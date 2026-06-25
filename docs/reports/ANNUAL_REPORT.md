# Annual Report — The Synthetic Enterprise


## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £2,466,636.22
- Final treasury: £2,749,580.80
  (£282,944.58 net change)
- Solvency signal (final year): £301,406/customer (9 customers, OK; Ofgem floor £130/customer)
- Customer bills (all-in): £18,059,162.00
  VAT remitted to HMRC: (£868,507.85) | Revenue (ex-VAT): £17,190,654.15
  Non-commodity pass-through: (£4,015,878.29)
- Gross margin: £5,506,327.73
- Capital costs: £237,296.40
- Net margin: £5,269,031.32
- Capital cost ratio: 4.3% of gross
- Net margin as % of revenue: 30.7%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 43
- Bills issued: 1549, average clarity 0.859,
  service quality score 0.919
- Enterprise value (CLV sum across 14 billing accounts): £6,024,925.91
- Cost to serve (whole portfolio): £86,310.79, net margin after cost to serve: £5,182,720.53
- Hedge effectiveness (whole window): hedging cost £4,036,593.59 vs. a fully unhedged book (commodity-only: actual net £282,944.58 vs. naked net £4,319,538.16)

- **2021** (crisis year): net margin £-103,914.72, 0 risk committee wake-up(s).
- **2022** (crisis year): net margin £85,096.77, 9 risk committee wake-up(s).

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £5,506,327.73, capital £237,296.40, net £5,269,031.32. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 4.3% (commodity basis, comparable to old model) / 4.3% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £-103,914.72 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 30.7%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £5,269,031.32
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £4,319,538.16
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £4,036,593.59 vs. a fully unhedged book (commodity-only: actual net £282,944.58 vs. naked net £4,319,538.16)
- **Best hedging decision of the run**: C_IC1, term starting
  2021-04-30 (hedge fraction 0.91) -- hedging
  protected £102,951.64 vs. going naked.
- **Worst hedging decision of the run**: C_IC3, term
  starting 2022-12-31 (hedge fraction 0.96) --
  over-hedging cost £618,207.73 vs. going
  naked.

## Segment Margin Trend

Net margin (£) by segment, by year:

| Year | I&C electricity | I&C gas | SME electricity | resi electricity | resi gas | Total |
|---|---|---|---|---|---|---|
| 2016 | £0.00 | £0.00 | £42.66 | £217.57 | £81.90 | £342.13 |
| 2017 | £29,240.89 | £0.00 | £172.91 | £380.52 | £177.77 | £29,972.08 |
| 2018 | £106,153.13 | £0.00 | £-362.03 | £153.71 | £128.23 | £106,073.04 |
| 2019 | £225,799.79 | £126.70 | £219.54 | £362.05 | £135.02 | £226,643.10 |
| 2020 | £-46,597.11 | £4,057.40 | £119.24 | £460.01 | £157.02 | £-41,803.43 |
| 2021 | £-101,710.80 | £-1,687.60 | £-1.46 | £-180.84 | £-334.02 | £-103,914.72 |
| 2022 | £136,617.41 | £-47,795.53 | £629.93 | £-3,248.45 | £-1,106.59 | £85,096.77 |
| 2023 | £-89,115.77 | £-30,761.54 | £1,206.12 | £-651.74 | £-1,099.91 | £-120,422.84 |
| 2024 | £129,188.31 | £-37,202.62 | £506.00 | £1,550.33 | £315.71 | £94,357.74 |
| 2025 | £25,987.87 | £-19,599.93 | £0.00 | £160.79 | £51.96 | £6,600.70 |

## Customer Lifecycle Events

Renewal decisions rolled at each annual renewal point across the simulation window.
Retained: **51** renewals.  Lost (churned): **5** accounts.

Accounts lost before end of window: C1, C2, C3, C5, C6

| Account | Date | Outcome | p(churn) | p(win-back) | p(retain) | Roll |
|---------|------|---------|----------|-------------|-----------|------|
| C1 | 2016-12-31 | renewed | 0.0800 | 0.5500 | 0.9640 | 0.1646 |
| C5 | 2016-12-31 | renewed | 0.2900 | 0.3500 | 0.8115 | 0.2812 |
| C7 | 2016-12-31 | renewed | 0.2900 | 0.5500 | 0.8695 | 0.1050 |
| C1 | 2017-12-31 | renewed | 0.1700 | 0.5500 | 0.9235 | 0.6188 |
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
| C1 | 2020-12-30 | renewed | 0.2600 | 0.5500 | 0.8830 | 0.8047 |
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
| C7 | 2022-12-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.0637 |
| C_IC3 | 2022-12-31 | renewed | 0.2600 | 0.5500 | 0.8830 | 0.8723 |
| C2_2 | 2023-03-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.0093 |
| C6 | 2023-03-31 | renewed | 0.2900 | 0.3500 | 0.8115 | 0.5155 |
| C8 | 2023-03-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.3785 |
| C9 | 2023-06-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.0307 |
| C4 | 2023-09-30 | renewed | 0.1700 | 0.5500 | 0.9235 | 0.6095 |
| C7 | 2023-12-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1905 |
| C_IC3 | 2023-12-31 | renewed | 0.1700 | 0.5500 | 0.9235 | 0.7019 |
| C2_2 | 2024-03-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.6064 |
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

- **Average absolute error:** 193.2%
- **Average signed error:** +54.0% (over-estimates vs SIM)
- **Renewal events with estimates:** 56

| Year | Renewals | Avg error (signed) | Avg abs error |
|------|----------|--------------------|---------------|
| 2016 | 3 | -62.5% | 62.5% |
| 2017 | 3 | -92.5% | 92.5% |
| 2018 | 4 | +471.1% | 544.8% |
| 2019 | 4 | +375.0% | 525.0% |
| 2020 | 10 | -15.3% | 146.4% |
| 2021 | 9 | +5.6% | 125.7% |
| 2022 | 7 | -23.2% | 99.0% |
| 2023 | 7 | +3.2% | 136.5% |
| 2024 | 7 | +76.2% | 234.5% |
| 2025 | 2 | -94.4% | 94.4% |

Positive error = company over-estimated churn vs SIM. Negative error = company under-estimated (more dangerous — expected retentions that were actually at risk).

## Active vs Passive Renewal Split (Phase 33a)

~35% of domestic/SME customers actively choose a new fixed deal at term end. ~65% roll to SVT by inaction — they are inert: low rate sensitivity, ~5% churn base. Crisis years (2022) force all renewals passive (no fixed deals available).

- **Total renewal events:** 56
- **Active renewers:** 17 (30%) — mean company estimate 34.1%, abs error 302.8%
- **Passive SVT-rollers:** 39 (70%) — mean company estimate 9.9%, abs error 145.4%

| Year | Active | Passive | Active est | Passive est | Active abs err | Passive abs err |
|------|--------|---------|-----------|------------|---------------|----------------|
| 2016 | 0 | 3 | 0.0% | 5.8% | 0.0% | 62.5% |
| 2017 | 0 | 3 | 0.0% | 2.1% | 0.0% | 92.5% |
| 2018 | 2 | 2 | 21.2% | 50.2% | 146.7% | 943.0% |
| 2019 | 2 | 2 | 47.5% | 0.0% | 950.0% | 100.0% |
| 2020 | 5 | 5 | 17.3% | 0.5% | 195.2% | 97.6% |
| 2021 | 3 | 6 | 64.7% | 4.0% | 213.3% | 82.0% |
| 2022 | 0 | 7 | 0.0% | 19.5% | 0.0% | 99.0% |
| 2023 | 2 | 5 | 24.7% | 19.0% | 48.2% | 171.8% |
| 2024 | 3 | 4 | 37.5% | 0.0% | 413.8% | 100.0% |
| 2025 | 0 | 2 | 0.0% | 2.1% | 0.0% | 94.4% |

Passive renewers should show lower company estimates and lower SIM churn — high abs error for passive renewers indicates the passive model needs recalibration.

## SVT Comparative Pricing — Passive Renewers (Phase 39a)

Passive renewers roll to a new fixed deal by inaction. A rate above SVT creates latent churn risk: once the customer notices they're paying more than the cap, they switch. A rate below SVT signals loyalty value — the company is rewarding inertia.

- **Passive renewal events with SVT data:** 39
- **Above SVT (at-risk):** 10 (26%)
- **Below/at SVT (protected):** 29 (74%)
- **Mean rate vs SVT premium:** -7.7%

| Year | Passive Renewals | Above SVT | Avg Premium | Avg Fixed Rate (£/MWh) | Avg SVT (£/MWh) |
|------|-----------------|-----------|-------------|----------------------|----------------|
| 2016 | 3 | 0 (0%) | -1.5% | 137.8 | 140.0 |
| 2017 | 3 | 0 (0%) | -10.9% | 124.8 | 140.0 |
| 2018 | 2 | 2 (100%) | +5.2% | 160.4 | 152.5 |
| 2019 | 2 | 0 (0%) | -26.5% | 131.3 | 178.5 |
| 2020 | 5 | 0 (0%) | -24.3% | 133.8 | 176.9 |
| 2021 | 6 | 3 (50%) | +1.8% | 185.9 | 183.8 |
| 2022 | 7 | 4 (57%) | +12.7% | 297.7 | 318.4 |
| 2023 | 5 | 0 (0%) | -30.5% | 230.8 | 364.0 |
| 2024 | 4 | 0 (0%) | -13.3% | 213.7 | 246.9 |
| 2025 | 2 | 1 (50%) | +4.1% | 258.8 | 248.6 |

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
| 2018 | 4 | 5.45× ⚠ | 18.00× |
| 2019 | 4 | 5.25× ⚠ | 18.00× |
| 2020 | 10 | 1.46× | 6.55× |
| 2021 | 9 | 1.26× | 4.59× |
| 2022 | 7 | 0.99× | 2.65× |
| 2023 | 7 | 1.36× | 4.59× |
| 2024 | 7 | 2.34× ⚠ | 10.88× |
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
| 2021-12-30 | CHURN | C5 | SIM p=0.35, company est=0.81 |
| 2022-03-31 | CHURN | C2 | SIM p=0.11, company est=0.07 |
| 2022-03-31 | ACQUISITION | C2_2 | home-move-win (predecessor: C2) |
| 2024-03-30 | CHURN | C6 | SIM p=0.38, company est=0.18 |

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
| 2016 | 887 | 426 | 461 | 0 | 356 | 5 | 82 | +9.2% |
| 2017 | 1,693 | 848 | 846 | 0 | 624 | 10 | 178 | +10.5% |
| 2018 | 1,993 | 1,201 | 792 | 0 | 609 | 15 | 128 | +6.4% |
| 2019 | 135,992 | 60,399 | 75,593 | 15,273 | 50,131 | 9,218 | 262 | +0.2% |
| 2020 | 119,682 | 43,054 | 76,628 | 19,520 | 46,890 | 5,385 | 4,214 | +3.5% |
| 2021 | 296,626 | 213,989 | 82,637 | 22,523 | 50,386 | 10,223 | -2,022 | -0.7% |
| 2022 | 593,793 | 503,227 | 90,567 | 27,135 | 54,413 | 51,897 | -48,902 | -8.2% |
| 2023 | 295,491 | 173,919 | 121,572 | 32,320 | 80,214 | 39,335 | -31,861 | -10.8% |
| 2024 | 270,499 | 146,371 | 124,128 | 37,573 | 76,143 | 45,912 | -36,887 | -13.6% |
| 2025 | 128,880 | 76,615 | 52,265 | 16,774 | 31,087 | 23,300 | -19,548 | -15.2% |
| **Total** | **1,845,538** | **1,220,049** | **625,489** | **171,119** | **390,853** | **185,301** | **-134,356** | **-7.3%** |

Gas book net margin negative over the simulation period. Network charges (GDN + NTS, £9–18/MWh) dominate the gas non-commodity cost stack.

## Solvency Signal — Net Assets per Customer (Phase 21b/55)

Treasury ÷ active accounts. Ofgem MCR floor: £130/dual-fuel account.
Watch < 2×, STRESS < 1× (account balance below regulatory floor).

| Year | Treasury £ | Accounts | Net Assets/Account £ | Solvency Ratio | Status |
|------|-----------|----------|----------------------|----------------|--------|
| 2016 | 2,466,968 | 9 | 274,108 | 2108.52× | OK |
| 2017 | 2,496,551 | 10 | 249,655 | 1920.42× | OK |
| 2018 | 2,484,426 | 11 | 225,857 | 1737.36× | OK |
| 2019 | 2,611,674 | 12 | 217,640 | 1674.15× | OK |
| 2020 | 2,748,696 | 13 | 211,438 | 1626.45× | OK |
| 2021 | 2,604,267 | 12 | 217,022 | 1669.40× | OK |
| 2022 | 2,582,037 | 11 | 234,731 | 1805.62× | OK |
| 2023 | 2,517,349 | 10 | 251,735 | 1936.42× | OK |
| 2024 | 2,657,841 | 10 | 265,784 | 2044.49× | OK |
| 2025 | 2,712,652 | 9 | 301,406 | 2318.51× | OK |

End-state (2025): **£301,406/account** across 9 billing accounts — OK.

## BSC Credit Cover — Working Capital Requirement (Phase 53)

Elexon BSC credit cover: max daily electricity wholesale charge × 28-day window × 1.2 buffer.
Below 5× coverage ratio (treasury / credit cover) flags working capital stress.

| Year | Peak Daily £ | Credit Cover £ | Treasury £ | Coverage Ratio | Status |
|------|-------------|---------------|-----------|----------------|--------|
| 2016 | 23 | 28 | 2,466,968 | 88074.5× | OK |
| 2017 | 466 | 559 | 2,496,551 | 4463.9× | OK |
| 2018 | 852 | 1,022 | 2,484,426 | 2430.0× | OK |
| 2019 | 1,543 | 1,851 | 2,611,674 | 1410.7× | OK |
| 2020 | 1,981 | 2,377 | 2,748,696 | 1156.5× | OK |
| 2021 | 4,420 | 5,305 | 2,604,267 | 491.0× | OK |
| 2022 | 8,509 | 10,211 | 2,582,037 | 252.9× | OK |
| 2023 | 5,609 | 6,731 | 2,517,349 | 374.0× | OK |
| 2024 | 2,739 | 3,287 | 2,657,841 | 808.7× | OK |
| 2025 | 4,216 | 5,060 | 2,712,652 | 536.1× | OK |




## Time-of-Use Tariff Utilization (C7-C9 HH Customers)

Peak windows: 07:00–11:00 and 16:00–20:00 weekdays (periods 15-22, 33-40).
Peak rate = 1.5× flat; off-peak = 0.786× flat (revenue-neutral at 30/70 split).
ToU Premium: actual revenue vs flat-rate equivalent — positive when actual peak % > 30% design.

| Customer | Total kWh | Peak kWh | Peak % | Peak Revenue | Off-peak Revenue | Avg Peak Rate | Avg Off-peak Rate | ToU Premium |
|----------|-----------|----------|--------|-------------|-----------------|--------------|------------------|-------------|
| C7 | 120,839 | 36,249 | 30.0% | £9,430.84 | £11,563.39 | £260.17/MWh | £136.70/MWh | +0.2% |
| C8 | 106,722 | 43,948 | 41.2% | £11,778.47 | £8,826.08 | £268.01/MWh | £140.60/MWh | +8.1% |
| C9 | 109,387 | 43,689 | 39.9% | £10,859.60 | £8,555.42 | £248.57/MWh | £130.22/MWh | +7.1% |

Total HH revenue: £61,013.80 vs flat equivalent £58,154.33 (+4.9% ToU premium)

## Bill Shock Summary (2016-2025)

Month-on-month billing increase ≥20%. Bill shocks elevate SIM churn probability
via the bill-shock history model. Crisis years (2021-22) see the largest spikes.

| Year | Events | Max Spike | Worst Customer |
|------|--------|-----------|----------------|
| 2016 | 21 | 109% | C8 (2016-10-31) |
| 2017 | 28 | 85% | C8 (2017-11-30) |
| 2018 | 34 | 61% | C_IC1 (2018-02-28) |
| 2019 | 38 | 129% | C_IC1 (2019-03-31) |
| 2020 | 32 | 123% | C_IC2 (2020-03-31) |
| 2021 | 38 | 92% | C_IC2 (2021-04-30) |
| 2022 | 54 | 1712% | C2_2 (2022-04-30) |
| 2023 | 35 | 117% | C_IC2 (2023-06-30) |
| 2024 | 29 | 122% | C_IC2 (2024-07-31) |
| 2025 | 23 | 81% | C_IC4 (2025-06-07) |

Total: **332** bill shock events across 10 years

**Top 10 worst single-period bill spikes:**

| Date | Customer | Spike | Eventually Churned? |
|------|----------|-------|---------------------|
| 2022-04-30 | C2_2 | +1712% | no |
| 2019-03-31 | C_IC1 | +129% | no |
| 2020-03-31 | C_IC2 | +123% | no |
| 2024-07-31 | C_IC2 | +122% | no |
| 2022-10-31 | C4g | +121% | no |
| 2023-06-30 | C_IC2 | +117% | no |
| 2016-10-31 | C8 | +109% | no |
| 2022-01-31 | C_IC3 | +105% | no |
| 2022-12-31 | C_IC4 | +102% | no |
| 2023-10-31 | C8 | +101% | no |

## Gas Renewal Pressure (Dual-Fuel Portfolio)

Company gas churn estimates at each gas leg renewal (Phase 14b).
Threshold for elevated risk: >20% company gas churn estimate.

| Year | Renewals | Mean Est | Max Est | Elevated Risk |
|------|----------|----------|---------|---------------|
| 2016 | 1 | 15% | 15% | 0 |
| 2017 | 4 | 18% | 24% | 2 ⚠ |
| 2018 | 4 | 17% | 23% | 2 ⚠ |
| 2019 | 4 | 0% | 0% | 0 |
| 2020 | 5 | 5% | 26% | 1 ⚠ |
| 2021 | 3 | 67% | 95% | 3 ⚠ |
| 2022 | 2 | 48% | 95% | 1 ⚠ |
| 2023 | 2 | 0% | 0% | 0 |
| 2024 | 2 | 0% | 0% | 0 |

**Top elevated gas renewals (>20% estimated churn):**

| Date | Customer | Old Rate (£/MWh) | New Rate (£/MWh) | Est Churn |
|------|----------|-----------------|-----------------|-----------|
| 2021-12-31 | C_IC3g | £21.5 | £125.9 (+484%) | 95% |
| 2022-09-30 | C4g | £35.0 | £95.0 (+171%) | 95% |
| 2021-09-30 | C4g | £16.6 | £35.0 (+111%) | 70% |
| 2021-03-31 | C2g | £22.5 | £35.0 (+56%) | 36% |
| 2020-12-31 | C_IC3g | £16.1 | £21.5 (+34%) | 26% |

## Retention Strategy P&L

### Aggregate (2016-2025)

| Metric | Value |
|--------|-------|
| Offers made | 19 |
| Retained | 18 (95%) |
| Churned despite offer | 1 |
| Total offer cost (foregone margin) | £486,168.24 |
| Margin saved (retained customers' terms) | £2,375,169.94 |
| Wasted offer cost (churned anyway) | £532.48 |
| **Net ROI of retention strategy** | **£1,889,001.71** |
| Acquisition cost avoided (retained customers) | £2,950.00 |
| **Full economic ROI (margin + acq savings)** | **£1,891,951.71** |

Missed opportunities (churns with no offer): **4** (£3,355.89 expected margin lost without offer)
- **Below threshold** (churn estimate under 30%): 4 (£3,355.89 margin lost) — Phase 13c bill burden signal reduces this for high-spend SME customers

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2018 | 1 | 1 | £24900.79 | £171286.28 | £146385.49 | £0.00 |
| 2019 | 2 | 2 | £43702.07 | £306529.83 | £262827.76 | £0.00 |
| 2020 | 3 | 3 | £27922.70 | £187648.66 | £159725.97 | £400.12 |
| 2021 | 4 | 3 | £122000.90 | £429902.10 | £307901.20 | £-142.51 |
| 2022 | 3 | 3 | £133418.12 | £408320.16 | £274902.04 | £320.54 |
| 2023 | 4 | 4 | £89108.83 | £455095.24 | £365986.42 | £0.00 |
| 2024 | 2 | 2 | £45114.83 | £416387.67 | £371272.84 | £2777.74 |

### Per-Offer Detail

| Date | Customer | Est. churn | Discount | Offer Cost | Expected Margin | Acq Saved | Net | Outcome |
|------|----------|-----------|---------|-----------|----------------|-----------|-----|---------|
| 2018-01-31 | C_IC1 | 0.95 | 8% | £24900.79 | £171286.28 | £150 | £146385.49 | retained |
| 2019-01-31 | C_IC2 | 0.95 | 8% | £15172.47 | £105268.85 | £150 | £90096.38 | retained |
| 2019-03-02 | C_IC1 | 0.95 | 8% | £28529.60 | £201260.98 | £150 | £172731.38 | retained |
| 2020-01-01 | C_IC3 | 0.39 | 3% | £5943.93 | £17839.58 | £150 | £11895.65 | retained |
| 2020-03-31 | C_IC1 | 0.53 | 5% | £10785.97 | £138983.49 | £150 | £128197.53 | retained |
| 2020-12-31 | C_IC3 | 0.60 | 5% | £11192.80 | £30825.59 | £150 | £19632.79 | retained |
| 2021-03-31 | C_IC2 | 0.86 | 8% | £14742.32 | £98053.49 | £150 | £83311.17 | retained |
| 2021-04-30 | C_IC1 | 0.95 | 8% | £23238.44 | £166439.02 | £150 | £143200.58 | retained |
| 2021-12-30 | C5 | 0.81 | 8% | £532.48 | £2523.90 | £400 | £-532.48 | churned_despite_offer |
| 2021-12-31 | C_IC3 | 0.95 | 8% | £83487.65 | £165409.59 | £150 | £81921.94 | retained |
| 2022-04-30 | C_IC2 | 0.95 | 8% | £25854.31 | £101527.80 | £150 | £75673.49 | retained |
| 2022-05-30 | C_IC1 | 0.95 | 8% | £49754.32 | £242114.63 | £150 | £192360.31 | retained |
| 2022-12-31 | C_IC3 | 0.95 | 8% | £57809.49 | £64677.73 | £150 | £6868.24 | retained |
| 2023-03-31 | C6 | 0.38 | 3% | £200.66 | £3147.06 | £400 | £2946.40 | retained |
| 2023-05-30 | C_IC2 | 0.59 | 5% | £12043.52 | £135743.51 | £150 | £123699.99 | retained |
| 2023-06-29 | C_IC1 | 0.95 | 8% | £35861.02 | £255060.25 | £150 | £219199.23 | retained |
| 2023-12-31 | C_IC3 | 0.95 | 8% | £41003.63 | £61144.42 | £150 | £20140.79 | retained |
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

**Full-history EV:** £6,024,925.91 — anchored to all 10 years including crisis losses
**3yr-trailing EV:** £-20,391.29 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

The gap between the two is the weight of unrecovered crisis losses in the CLV anchor.
When trailing EV > full-history EV, the company's recent performance is better than its
cumulative history suggests — a recovery signal.

**Portfolio net margin by year:**

| Year | Net margin |
|------|----------:|
| 2016 | £342.13 |
| 2017 | £29,972.08 |
| 2018 | £106,073.04 |
| 2019 | £226,643.10 |
| 2020 | £-41,803.43 |
| 2021 | £-103,914.72 |
| 2022 | £85,096.77 |
| 2023 | £-120,422.84 | ← trailing
| 2024 | £94,357.74 | ← trailing
| 2025 | £6,600.70 | ← trailing

**CLV by billing account:**

| Account | Full-history CLV | 3yr-trailing CLV |
|---------|----------------:|----------------:|
| C1 | £2,732.13 | — |
| C2 | £5,764.92 | — |
| C2_2 | — | £1,169.79 |
| C3 | £3,073.92 | — |
| C4 | £3,432.13 | £-1,088.44 |
| C5 | £10,180.08 | — |
| C6 | £16,095.38 | £2,814.26 |
| C7 | £7,682.37 | £-222.96 |
| C8 | £8,311.36 | £-56.34 |
| C9 | £8,324.10 | £556.44 |
| C_IC1 | £1,692,243.47 | £406,809.21 |
| C_IC2 | £1,065,692.95 | £214,069.49 |
| C_IC3 | £3,164,648.00 | £-62,635.08 |
| C_IC4 | £32,411.05 | £-581,807.65 |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C2 | C2_2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C_IC1 | C_IC2 | C_IC3 | C_IC4 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £1,830.80 | — | — | — | — | £5,444.81 | — | £4,336.09 | — | — | — | — | — | — |
| 2017 | £2,570.36 | £6,817.26 | — | £3,091.12 | £4,105.10 | £7,456.75 | £13,185.27 | £5,239.64 | £7,868.97 | £6,429.77 | — | — | — | — |
| 2018 | £2,193.25 | £5,946.35 | — | £3,264.59 | £3,851.56 | £9,130.25 | £11,560.48 | £5,252.49 | £6,618.54 | £6,076.04 | £2,012,473.11 | — | — | — |
| 2019 | £2,313.97 | £5,016.97 | — | £2,822.87 | £3,714.44 | £7,870.95 | £11,452.36 | £4,947.93 | £6,930.48 | £6,538.82 | £1,671,916.15 | £1,056,288.50 | — | — |
| 2020 | £2,131.34 | £5,504.03 | — | £2,241.16 | £3,550.64 | £7,953.89 | £8,236.99 | £5,066.95 | £6,642.92 | £5,947.97 | £1,043,920.08 | £536,317.03 | £1,761,972.82 | £25,030.09 |
| 2021 | £2,032.95 | £4,756.71 | — | £1,990.17 | £2,582.03 | £7,403.04 | £8,905.47 | £4,671.22 | £5,860.37 | £5,755.43 | £881,756.59 | £571,856.72 | £1,688,960.11 | £22,674.60 |
| 2022 | £2,125.93 | £3,916.21 | £522.38 | £1,925.16 | £1,754.78 | £6,323.82 | £9,374.73 | £3,651.74 | £5,545.82 | £5,272.96 | £969,632.13 | £540,763.13 | £1,832,589.75 | £18,555.44 |
| 2023 | £2,162.80 | £3,640.43 | £1,615.86 | £1,913.10 | £1,146.48 | £6,109.56 | £10,033.16 | £3,715.64 | £5,321.30 | £5,354.64 | £1,027,112.98 | £602,276.01 | £1,579,976.33 | £18,128.49 |
| 2024 | £2,188.95 | £3,755.63 | £2,426.76 | £1,901.91 | £1,939.78 | £6,032.93 | £9,741.42 | £4,375.44 | £5,669.77 | £5,777.80 | £1,064,580.25 | £641,230.30 | £1,753,092.04 | £18,961.40 |
| 2025 | £2,117.55 | £3,459.85 | £2,559.22 | £1,817.05 | £2,056.66 | £6,035.77 | £9,858.67 | £4,698.36 | £5,237.29 | £5,558.58 | £1,111,889.72 | £670,622.87 | £1,898,212.73 | £20,474.26 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £4,542.67, range £32.52–£26,707.73.

- C1: cost to serve £391.15, net margin after CTS £1,474.21
- C1g: cost to serve £48.91, net margin after CTS £896.77
- C2: cost to serve £452.29, net margin after CTS £3,383.86
- C2_2: cost to serve £379.85, net margin after CTS £5,018.90
- C2g: cost to serve £61.74, net margin after CTS £1,226.15
- C3: cost to serve £263.39, net margin after CTS £1,107.24
- C3g: cost to serve £32.52, net margin after CTS £570.73
- C4: cost to serve £648.54, net margin after CTS £3,358.55
- C4g: cost to serve £167.24, net margin after CTS £452.84
- C5: cost to serve £869.83, net margin after CTS £8,295.59
- C6: cost to serve £1,270.76, net margin after CTS £16,617.06
- C7: cost to serve £939.02, net margin after CTS £9,054.00
- C8: cost to serve £917.52, net margin after CTS £10,448.44
- C9: cost to serve £880.02, net margin after CTS £10,981.98
- C_IC1: cost to serve £20,305.19, net margin after CTS £1,929,615.74
- C_IC2: cost to serve £11,578.71, net margin after CTS £935,559.92
- C_IC3: cost to serve £26,707.73, net margin after CTS £1,833,897.18
- C_IC3g: cost to serve £9,224.23, net margin after CTS £612,807.63
- C_IC4: cost to serve £11,172.13, net margin after CTS £21,351.71 — MARGIN_SQUEEZE (below 2% benchmark)

**Activity-Based Pricing Actions**

The following 1 customer(s) are profitable but below the 2% net-margin benchmark (MARGIN_SQUEEZE): C_IC4


## Margin Recovery Surcharges (Phase 16c + 19a)

Company applied 39 recovery surcharge(s) at renewal based on prior-term losses (6 gas). Avg surcharge: 12.1%.

| Customer | Commodity | Term start | Prior margin | Prior revenue | Surcharge | Rate before | Rate after |
|----------|-----------|------------|-------------|--------------|-----------|------------|-----------|
| C6 | electricity | 2017-04-01 | £-122.69 | £2,055.98 | +1.0% | £127.97/MWh | £129.39/MWh |
| C3 | electricity | 2017-07-01 | £-37.54 | £440.29 | +3.5% | £122.23/MWh | £126.70/MWh |
| C4 | electricity | 2017-10-01 | £-52.77 | £549.78 | +4.6% | £111.62/MWh | £116.13/MWh |
| C_IC1 | electricity | 2018-01-31 | £-5,749.07 | £10,901.23 | +20.0% | £112.24/MWh | £152.62/MWh |
| C1 | electricity | 2018-12-31 | £-52.78 | £453.38 | +6.6% | £148.68/MWh | £163.66/MWh |
| C5 | electricity | 2018-12-31 | £-269.89 | £2,259.07 | +7.0% | £148.68/MWh | £162.11/MWh |
| C_IC2 | electricity | 2019-01-31 | £-3,332.71 | £6,376.41 | +20.0% | £134.57/MWh | £185.71/MWh |
| C_IC1 | electricity | 2019-03-02 | £-7,269.51 | £10,243.03 | +20.0% | £128.22/MWh | £175.35/MWh |
| C6 | electricity | 2019-04-01 | £-202.92 | £2,646.95 | +2.7% | £148.35/MWh | £154.13/MWh |
| C3 | electricity | 2019-07-01 | £-33.41 | £582.68 | +0.7% | £127.03/MWh | £122.89/MWh |
| C_IC2 | electricity | 2020-03-01 | £-3,922.12 | £3,444.18 | +20.0% | £92.92/MWh | £128.22/MWh |
| C_IC1 | electricity | 2020-03-31 | £-8,072.70 | £6,326.95 | +20.0% | £91.12/MWh | £104.83/MWh |
| C_IC2 | electricity | 2021-03-31 | £-4,097.33 | £5,726.15 | +20.0% | £138.90/MWh | £180.32/MWh |
| C_IC1 | electricity | 2021-04-30 | £-7,770.53 | £14,511.74 | +20.0% | £113.97/MWh | £142.25/MWh |
| C9 | electricity | 2021-06-30 | £-91.70 | £1,549.18 | +0.9% | £170.38/MWh | £177.93/MWh |
| C4 | electricity | 2021-09-30 | £-87.63 | £693.35 | +7.6% | £205.15/MWh | £232.16/MWh |
| C4g | gas | 2021-09-30 | £-108.63 | £364.57 | +20.0% | £53.99/MWh | £71.69/MWh |
| C1 | electricity | 2021-12-30 | £-74.31 | £522.66 | +9.2% | £311.83/MWh | £355.68/MWh |
| C5 | electricity | 2021-12-30 | £-359.38 | £2,691.13 | +8.3% | £311.83/MWh | £352.86/MWh |
| C7 | electricity | 2021-12-30 | £-157.50 | £1,955.96 | +3.0% | £311.83/MWh | £335.60/MWh |
| C_IC2 | electricity | 2022-04-30 | £-2,287.21 | £17,661.75 | +8.0% | £269.81/MWh | £318.46/MWh |
| C_IC1 | electricity | 2022-05-30 | £-6,202.10 | £22,384.38 | +20.0% | £239.42/MWh | £308.85/MWh |
| C9 | electricity | 2022-06-30 | £-128.20 | £2,206.80 | +0.8% | £255.09/MWh | £261.24/MWh |
| C4 | electricity | 2022-09-30 | £-489.61 | £1,021.16 | +20.0% | £404.86/MWh | £488.79/MWh |
| C4g | gas | 2022-09-30 | £-845.65 | £770.00 | +20.0% | £183.79/MWh | £253.63/MWh |
| C7 | electricity | 2022-12-30 | £-1,989.53 | £2,236.99 | +20.0% | £266.73/MWh | £326.89/MWh |
| C_IC3g | gas | 2022-12-31 | £-48,879.18 | £592,608.29 | +3.2% | £101.23/MWh | £120.20/MWh |
| C8 | electricity | 2023-03-31 | £-515.43 | £3,724.74 | +8.8% | £319.17/MWh | £379.18/MWh |
| C_IC2 | electricity | 2023-05-30 | £-4,337.22 | £7,055.33 | +20.0% | £171.46/MWh | £236.61/MWh |
| C_IC1 | electricity | 2023-06-29 | £-8,734.92 | £17,979.18 | +20.0% | £163.19/MWh | £221.13/MWh |
| C9 | electricity | 2023-06-30 | £-169.21 | £3,313.41 | +0.1% | £224.44/MWh | £244.79/MWh |
| C4 | electricity | 2023-09-30 | £-678.78 | £1,701.85 | +20.0% | £216.77/MWh | £259.08/MWh |
| C4g | gas | 2023-09-30 | £-1,601.62 | £2,090.00 | +20.0% | £47.83/MWh | £66.00/MWh |
| C7 | electricity | 2023-12-30 | £-534.71 | £3,797.69 | +9.1% | £242.22/MWh | £251.00/MWh |
| C_IC3 | electricity | 2023-12-31 | £-150,190.48 | £958,893.79 | +10.7% | £118.95/MWh | £125.05/MWh |
| C_IC3g | gas | 2023-12-31 | £-30,255.66 | £294,338.38 | +5.3% | £51.89/MWh | £61.62/MWh |
| C_IC2 | electricity | 2024-06-28 | £-5,972.33 | £7,659.10 | +20.0% | £148.64/MWh | £205.12/MWh |
| C_IC1 | electricity | 2024-07-28 | £-10,717.78 | £14,454.77 | +20.0% | £154.38/MWh | £213.04/MWh |
| C_IC3g | gas | 2024-12-30 | £-36,844.69 | £268,215.17 | +8.7% | £50.47/MWh | £56.37/MWh |


## Portfolio Learning Premium (Phase 17a + 19a)

Company applied portfolio premium adjustments at 113 renewal(s) (27 gas) based on recent portfolio-wide margin rates: 93 surcharge(s), 20 discount(s).

| Customer | Commodity | Term start | Mean recent margin | Portfolio premium | Rate before | Rate after |
|----------|-----------|------------|-------------------|-------------------|------------|-----------|
| C1 | electricity | 2016-12-31 | -3.5% | +5.8% | £131.49/MWh | £139.04/MWh |
| C1g | gas | 2016-12-31 | 7.7% | +0.2% | £27.63/MWh | £27.68/MWh |
| C5 | electricity | 2016-12-31 | -2.6% | +5.3% | £131.49/MWh | £138.48/MWh |
| C7 | electricity | 2016-12-31 | 1.1% | +3.5% | £131.49/MWh | £136.02/MWh |
| C2 | electricity | 2017-04-01 | 9.3% | -0.7% | £127.97/MWh | £127.12/MWh |
| C2g | gas | 2017-04-01 | 9.1% | -0.5% | £34.54/MWh | £34.35/MWh |
| C6 | electricity | 2017-04-01 | 7.7% | +0.1% | £127.97/MWh | £128.15/MWh |
| C8 | electricity | 2017-04-01 | 7.0% | +0.5% | £127.97/MWh | £128.62/MWh |
| C3 | electricity | 2017-07-01 | 7.7% | +0.1% | £122.23/MWh | £122.38/MWh |
| C3g | gas | 2017-07-01 | 11.3% | -1.7% | £24.33/MWh | £23.92/MWh |
| C9 | electricity | 2017-07-01 | 6.7% | +0.7% | £122.23/MWh | £123.02/MWh |
| C4 | electricity | 2017-10-01 | 9.1% | -0.5% | £111.62/MWh | £111.03/MWh |
| C4g | gas | 2017-10-01 | 10.1% | -1.1% | £27.48/MWh | £27.18/MWh |
| C1 | electricity | 2017-12-31 | 7.4% | +0.3% | £120.10/MWh | £120.45/MWh |
| C1g | gas | 2017-12-31 | 8.1% | -0.0% | £34.79/MWh | £34.78/MWh |
| C5 | electricity | 2017-12-31 | 1.8% | +3.1% | £120.10/MWh | £123.83/MWh |
| C7 | electricity | 2017-12-31 | -3.5% | +5.7% | £120.10/MWh | £127.00/MWh |
| C_IC1 | electricity | 2018-01-31 | -18.6% | +13.3% | £112.24/MWh | £127.18/MWh |
| C2 | electricity | 2018-04-01 | -6.3% | +7.1% | £133.89/MWh | £143.44/MWh |
| C2g | gas | 2018-04-01 | 8.4% | -0.2% | £38.21/MWh | £38.13/MWh |
| C6 | electricity | 2018-04-01 | -6.5% | +7.3% | £133.89/MWh | £143.62/MWh |
| C8 | electricity | 2018-04-01 | 4.7% | +1.6% | £133.89/MWh | £136.08/MWh |
| C3 | electricity | 2018-07-01 | 6.3% | +0.9% | £128.29/MWh | £129.40/MWh |
| C3g | gas | 2018-07-01 | 6.0% | +1.0% | £29.63/MWh | £29.92/MWh |
| C9 | electricity | 2018-07-01 | -4.5% | +6.3% | £128.29/MWh | £136.32/MWh |
| C4 | electricity | 2018-10-01 | -1.6% | +4.8% | £145.00/MWh | £151.94/MWh |
| C4g | gas | 2018-10-01 | 6.4% | +0.8% | £34.60/MWh | £34.87/MWh |
| C1 | electricity | 2018-12-31 | 1.6% | +3.2% | £148.68/MWh | £153.47/MWh |
| C1g | gas | 2018-12-31 | 7.1% | +0.5% | £37.15/MWh | £37.33/MWh |
| C5 | electricity | 2018-12-31 | 4.1% | +1.9% | £148.68/MWh | £151.58/MWh |
| C7 | electricity | 2018-12-31 | 7.1% | +0.5% | £148.68/MWh | £149.37/MWh |
| C_IC2 | electricity | 2019-01-31 | -30.3% | +15.0% | £134.57/MWh | £154.76/MWh |
| C_IC1 | electricity | 2019-03-02 | -19.9% | +14.0% | £128.22/MWh | £146.12/MWh |
| C2 | electricity | 2019-04-01 | 3.8% | +2.1% | £148.35/MWh | £151.47/MWh |
| C2g | gas | 2019-04-01 | 3.8% | +2.1% | £32.94/MWh | £33.63/MWh |
| C6 | electricity | 2019-04-01 | 5.6% | +1.2% | £148.35/MWh | £150.13/MWh |
| C8 | electricity | 2019-04-01 | 24.8% | -5.0% | £148.35/MWh | £140.93/MWh |
| C3 | electricity | 2019-07-01 | 15.9% | -4.0% | £127.03/MWh | £121.99/MWh |
| C3g | gas | 2019-07-01 | 4.9% | +1.6% | £23.62/MWh | £23.99/MWh |
| C9 | electricity | 2019-07-01 | 4.5% | +1.7% | £127.03/MWh | £129.23/MWh |
| C4 | electricity | 2019-10-01 | 4.8% | +1.6% | £126.72/MWh | £128.77/MWh |
| C4g | gas | 2019-10-01 | 7.3% | +0.3% | £20.41/MWh | £20.47/MWh |
| C1 | electricity | 2019-12-31 | 4.2% | +1.9% | £127.44/MWh | £129.89/MWh |
| C1g | gas | 2019-12-31 | 5.7% | +1.1% | £26.17/MWh | £26.46/MWh |
| C5 | electricity | 2019-12-31 | 2.1% | +3.0% | £127.44/MWh | £131.21/MWh |
| C7 | electricity | 2019-12-31 | 1.9% | +3.0% | £127.44/MWh | £131.32/MWh |
| C_IC3 | electricity | 2020-01-01 | 0.0% | +4.0% | £47.59/MWh | £49.49/MWh |
| C_IC3g | gas | 2020-01-01 | 10.3% | -1.1% | £16.25/MWh | £16.06/MWh |
| C_IC2 | electricity | 2020-03-01 | -98.0% | +15.0% | £92.92/MWh | £106.85/MWh |
| C2 | electricity | 2020-03-31 | -90.6% | +15.0% | £125.12/MWh | £143.89/MWh |
| C2g | gas | 2020-03-31 | 10.9% | -1.4% | £22.80/MWh | £22.48/MWh |
| C6 | electricity | 2020-03-31 | -49.2% | +15.0% | £125.12/MWh | £143.89/MWh |
| C8 | electricity | 2020-03-31 | -19.2% | +13.6% | £125.12/MWh | £142.17/MWh |
| C_IC1 | electricity | 2020-03-31 | 16.3% | -4.1% | £91.12/MWh | £87.36/MWh |
| C3 | electricity | 2020-06-30 | 13.1% | -2.5% | £113.43/MWh | £110.56/MWh |
| C9 | electricity | 2020-06-30 | 13.1% | -2.5% | £113.43/MWh | £110.56/MWh |
| C4 | electricity | 2020-09-30 | 8.8% | -0.4% | £124.42/MWh | £123.89/MWh |
| C4g | gas | 2020-09-30 | 12.3% | -2.1% | £16.94/MWh | £16.57/MWh |
| C1 | electricity | 2020-12-30 | 4.2% | +1.9% | £133.55/MWh | £136.10/MWh |
| C1g | gas | 2020-12-30 | 2.8% | +2.6% | £28.99/MWh | £29.75/MWh |
| C5 | electricity | 2020-12-30 | -3.0% | +5.5% | £133.55/MWh | £140.88/MWh |
| C7 | electricity | 2020-12-30 | -11.5% | +9.8% | £133.55/MWh | £146.60/MWh |
| C_IC3 | electricity | 2020-12-31 | -12.1% | +10.0% | £50.65/MWh | £55.74/MWh |
| C_IC3g | gas | 2020-12-31 | -7.0% | +7.5% | £20.05/MWh | £21.55/MWh |
| C2 | electricity | 2021-03-31 | -33.9% | +15.0% | £175.90/MWh | £202.28/MWh |
| C2g | gas | 2021-03-31 | -7.8% | +7.9% | £36.20/MWh | £39.06/MWh |
| C6 | electricity | 2021-03-31 | -31.0% | +15.0% | £175.90/MWh | £202.28/MWh |
| C8 | electricity | 2021-03-31 | -27.5% | +15.0% | £175.90/MWh | £202.28/MWh |
| C_IC2 | electricity | 2021-03-31 | -8.4% | +8.2% | £138.90/MWh | £150.27/MWh |
| C_IC1 | electricity | 2021-04-30 | -0.0% | +4.0% | £113.97/MWh | £118.54/MWh |
| C9 | electricity | 2021-06-30 | 1.0% | +3.5% | £170.38/MWh | £176.31/MWh |
| C4 | electricity | 2021-09-30 | -2.3% | +5.1% | £205.15/MWh | £215.69/MWh |
| C4g | gas | 2021-09-30 | -13.3% | +10.7% | £53.99/MWh | £59.74/MWh |
| C1 | electricity | 2021-12-30 | -0.9% | +4.4% | £311.83/MWh | £325.66/MWh |
| C5 | electricity | 2021-12-30 | -0.9% | +4.4% | £311.83/MWh | £325.66/MWh |
| C7 | electricity | 2021-12-30 | -0.9% | +4.4% | £311.83/MWh | £325.66/MWh |
| C_IC3 | electricity | 2021-12-31 | -32.3% | +15.0% | £224.03/MWh | £257.63/MWh |
| C_IC3g | gas | 2021-12-31 | -33.3% | +15.0% | £109.48/MWh | £125.90/MWh |
| C2 | electricity | 2022-03-31 | -39.7% | +15.0% | £361.95/MWh | £416.24/MWh |
| C6 | electricity | 2022-03-31 | -28.7% | +15.0% | £361.95/MWh | £416.24/MWh |
| C8 | electricity | 2022-03-31 | -3.5% | +5.8% | £361.95/MWh | £382.75/MWh |
| C_IC2 | electricity | 2022-04-30 | -10.7% | +9.3% | £269.81/MWh | £295.01/MWh |
| C_IC1 | electricity | 2022-05-30 | -7.0% | +7.5% | £239.42/MWh | £257.38/MWh |
| C9 | electricity | 2022-06-30 | 4.8% | +1.6% | £255.09/MWh | £259.14/MWh |
| C4 | electricity | 2022-09-30 | 6.8% | +0.6% | £404.86/MWh | £407.32/MWh |
| C4g | gas | 2022-09-30 | -30.2% | +15.0% | £183.79/MWh | £211.36/MWh |
| C7 | electricity | 2022-12-30 | 3.7% | +2.1% | £266.73/MWh | £272.41/MWh |
| C_IC3 | electricity | 2022-12-31 | -6.4% | +7.2% | £168.36/MWh | £180.48/MWh |
| C_IC3g | gas | 2022-12-31 | -49.5% | +15.0% | £101.23/MWh | £116.42/MWh |
| C2_2 | electricity | 2023-03-31 | -34.7% | +15.0% | £319.17/MWh | £367.05/MWh |
| C6 | electricity | 2023-03-31 | -19.1% | +13.6% | £319.17/MWh | £362.51/MWh |
| C8 | electricity | 2023-03-31 | -10.3% | +9.2% | £319.17/MWh | £348.39/MWh |
| C_IC2 | electricity | 2023-05-30 | -22.1% | +15.0% | £171.46/MWh | £197.18/MWh |
| C_IC1 | electricity | 2023-06-29 | -17.8% | +12.9% | £163.19/MWh | £184.28/MWh |
| C9 | electricity | 2023-06-30 | -9.9% | +8.9% | £224.44/MWh | £244.53/MWh |
| C4 | electricity | 2023-09-30 | 8.8% | -0.4% | £216.77/MWh | £215.90/MWh |
| C4g | gas | 2023-09-30 | -51.2% | +15.0% | £47.83/MWh | £55.00/MWh |
| C7 | electricity | 2023-12-30 | 25.2% | -5.0% | £242.22/MWh | £230.11/MWh |
| C_IC3 | electricity | 2023-12-31 | 19.3% | -5.0% | £118.95/MWh | £113.00/MWh |
| C_IC3g | gas | 2023-12-31 | -17.6% | +12.8% | £51.89/MWh | £58.53/MWh |
| C2_2 | electricity | 2024-03-30 | -13.7% | +10.9% | £207.71/MWh | £230.29/MWh |
| C6 | electricity | 2024-03-30 | -16.1% | +12.1% | £207.71/MWh | £232.75/MWh |
| C8 | electricity | 2024-03-30 | -16.1% | +12.1% | £207.71/MWh | £232.75/MWh |
| C_IC2 | electricity | 2024-06-28 | -34.4% | +15.0% | £148.64/MWh | £170.93/MWh |
| C9 | electricity | 2024-06-29 | -28.3% | +15.0% | £203.92/MWh | £234.50/MWh |
| C_IC1 | electricity | 2024-07-28 | -28.4% | +15.0% | £154.38/MWh | £177.53/MWh |
| C4 | electricity | 2024-09-29 | -0.7% | +4.4% | £195.97/MWh | £204.52/MWh |
| C4g | gas | 2024-09-29 | -19.0% | +13.5% | £50.11/MWh | £56.87/MWh |
| C7 | electricity | 2024-12-29 | 16.8% | -4.4% | £243.79/MWh | £233.01/MWh |
| C_IC3 | electricity | 2024-12-30 | 6.8% | +0.6% | £116.37/MWh | £117.07/MWh |
| C_IC3g | gas | 2024-12-30 | 2.5% | +2.7% | £50.47/MWh | £51.84/MWh |
| C2_2 | electricity | 2025-03-30 | -22.3% | +15.0% | £284.89/MWh | £327.63/MWh |
| C8 | electricity | 2025-03-30 | -15.7% | +11.8% | £284.89/MWh | £318.63/MWh |

## Churn Avoidability Analysis (Phase 17b)

Total no-offer churns: **4** | Blind misses: **4** | Deliberate passes (uneconomical): **0**

- Blind misses: company estimated churn < 30% → no offer made. Of these, 1 had SIM p ≥ 30% (detectable with a better model).
- Deliberate passes: company estimated churn ≥ 30% but the retention offer was uneconomical (margin + acq cost < offer cost).

**Estimated margin at stake** — blind: £3,355.89 | deliberate: £0.00 | total: £3,355.89

| Customer | Date | Reason | Co. est | SIM p | Detectable? | Margin at stake |
|----------|------|--------|---------|-------|-------------|----------------|
| C3 | 2020-06-30 | Blind miss | 0.00 | 0.11 | No | £400.12 |
| C1 | 2021-12-30 | Blind miss | 0.03 | 0.17 | No | £-142.51 |
| C2 | 2022-03-31 | Blind miss | 0.07 | 0.11 | No | £320.54 |
| C6 | 2024-03-30 | Blind miss | 0.18 | 0.38 | Yes | £2,777.74 |

## Dual-Fuel Account P&L (Phase 17d)

5 dual-fuel account pair(s): electricity leg + gas leg combined.

| Account | Elec net | Gas net | Combined net | Gas accretive? |
|---------|----------|---------|-------------|---------------|
| C2+C2g | £224.16 | £317.26 | £541.42 | Yes |
| C1+C1g | £22.95 | £179.41 | £202.37 | Yes |
| C3+C3g | £-34.66 | £17.05 | £-17.61 | Yes |
| C4+C4g | £-1,043.19 | £-2,006.64 | £-3,049.84 | No |
| C_IC3+C_IC3g | £129,429.23 | £-132,863.11 | £-3,433.89 | No |

Gas accretive in 3/5 dual-fuel accounts. Total gas net margin: £-134,356.03.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £282,944.58 across 19 billing accounts. Revenue: £13,160,877.42.

| # | Customer | Tariff | Revenue | Gross margin | Capital | Net margin | Net margin % |
|---|----------|--------|---------|-------------|---------|------------|-------------|
| 1 | C_IC1 | fixed | £3,217,414.20 | £1,949,920.93 | £18,966.00 | £891,661.05 | 27.7% |
| 2 | C_IC2 | fixed | £1,572,107.09 | £947,138.64 | £8,786.28 | £458,195.14 | 29.1% |
| 3 | C_IC3 | pass_through | £4,697,882.45 | £1,860,604.91 | £23,336.77 | £129,429.23 | 2.8% |
| 4 | C6 | fixed | £31,098.24 | £17,887.82 | £219.51 | £2,781.34 | 8.9% |
| 5 | C2_2 | fixed | £10,217.83 | £5,398.75 | £72.21 | £976.47 | 9.6% |
| 6 | C9 | fixed | £19,415.02 | £11,862.00 | £131.28 | £678.15 | 3.5% |
| 7 | C8 | fixed | £20,604.55 | £11,365.96 | £136.15 | £453.21 | 2.2% |
| 8 | C2g | fixed | £2,743.06 | £1,287.88 | £17.31 | £317.26 | 11.6% |
| 9 | C2 | fixed | £6,117.73 | £3,836.15 | £31.75 | £224.16 | 3.7% |
| 10 | C1g | fixed | £2,101.53 | £945.68 | £14.90 | £179.41 | 8.5% |
| 11 | C1 | fixed | £3,061.15 | £1,865.36 | £16.06 | £22.95 | 0.7% |
| 12 | C3g | fixed | £1,396.80 | £603.25 | £9.77 | £17.05 | 1.2% |
| 13 | C3 | fixed | £2,172.22 | £1,370.63 | £9.91 | £-34.66 | -1.6% |
| 14 | C5 | fixed | £14,998.17 | £9,165.43 | £80.98 | £-248.42 | -1.7% |
| 15 | C4 | fixed | £8,534.39 | £4,007.09 | £65.84 | £-1,043.19 | -12.2% |
| 16 | C4g | fixed | £7,864.21 | £620.09 | £132.04 | £-2,006.64 | -25.5% |
| 17 | C7 | fixed | £20,994.23 | £9,993.02 | £142.92 | £-2,073.14 | -9.9% |
| 18 | C_IC3g | pass_through | £1,831,432.12 | £622,031.85 | £185,126.72 | £-132,863.11 | -7.3% |
| 19 | C_IC4 | flex | £1,690,722.42 | £32,523.85 | £0.00 | £-1,063,721.69 | -62.9% |

## Revenue & Margin Sanity Check

### Portfolio P&L Waterfall
| Line | £ | % Revenue |
|------|---|-----------|
| Supply Revenue (ex-VAT, ex-policy passthrough) | £13,160,877 | 100.0% |
| Wholesale cost | -£7,668,448 | 58.3% |
| **Gross supply margin** | **£5,492,429** | **41.7%** |
| Policy + Network costs | -£4,972,188 | 37.8% |
| Capital cost | -£237,296 | 1.8% |
| **Net supply margin** | **£282,945** | **2.1%** |

> *The ledger's `net_margin_gbp` (£5,269,031) is gross − capital only, not final net.*

### Segment Net Margin vs Benchmark
| Segment | Revenue | Gross% | Net% | Benchmark | Status |
|---------|---------|--------|------|-----------|--------|
| I&C/elec | £11,178,126 | 42.9% | 3.7% | large spread -20% to +15% (crisis) | ✓ |
| I&C/gas | £1,831,432 | 34.0% | -7.3% | commodity 2-6%, pass-through ≈0 | ✓ |
| SME/elec | £46,096 | 58.7% | 5.5% | CMA 3-8% | ✓ |
| resi/elec | £80,899 | 54.8% | -2.2% | Ofgem CMA 2-5% | ⚠ ANOMALY |
| resi/gas | £14,106 | 24.5% | -10.6% | Ofgem CMA 2-4% | ⚠ ANOMALY |

### Per-Customer Net Margin Flags
No individual customers outside ±40.0/80.0 thresholds.

**SANITY CHECK: ANOMALIES DETECTED**
- Segment resi/elec net -2.2% (benchmark Ofgem CMA 2-5%)
- Segment resi/gas net -10.6% (benchmark Ofgem CMA 2-4%)
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
| Customer bills (all-in) | £18,059,162.00 |
|   Less: VAT remitted to HMRC | (£868,507.85) |
| = Revenue (ex-VAT) | £17,190,654.15 |
| Less: non-commodity pass-through | (£4,015,878.29) |
| Wholesale cost (settlement events) | (£7,668,448.13) |
| Gross margin | £5,506,327.73 |
| Capital charges | (£237,296.40) |
| Net margin | £5,269,031.32 |

_Cash reconciliation: of £18,059,162.00 billed, bad debt of £361,139.90 was written off, leaving £17,698,022.10 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £5,776,399.27._

| Acquisition spend | (£950.00) |
| Fixed overhead | (£5,700.00) |
| Operating net margin | £5,262,381.32 |

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £5,262,381.32

## 2016

**Trading & Risk**

- Net margin: £342.13 (gross £5,566.29, capital £75.74)
  - Electricity: gross £5,105.45, capital £70.32, net £260.23
  - Gas: gross £460.84, capital £5.42, net £81.90
- Treasury at year end: £2,466,967.68
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.92 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.89 (avg 0.89), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.92 (avg 0.92), C6 0.91 (avg 0.91), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89)
- Risk committee (Context Handshake) interventions: 13
  - 2016-01-01: treasury £2,466,636.22, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-01-31: treasury £2,466,640.28, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-03-01: treasury £2,466,644.42, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-03-31: treasury £2,466,648.34, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-04-30: treasury £2,466,651.56, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-05-30: treasury £2,466,654.70, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-06-29: treasury £2,466,657.51, (none), VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-07-29: treasury £2,466,660.42, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-08-28: treasury £2,466,663.35, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-09-27: treasury £2,466,666.42, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-10-27: treasury £2,466,669.48, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-11-26: treasury £2,466,672.46, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
  - 2016-12-26: treasury £2,466,676.33, C1->1.00, VaR (current £22.23 / stressed £6.83) ratio 3.25
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 3.25
- Worst single period: C9 on 2016-11-20 period 36, net margin £-0.31

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2016): £3,870.57
  - By billing account: C1 £1,830.80, C5 £5,444.81, C7 £4,336.09
- Bill shock events (>=20%): 21 -- C5 2016-05-31 (28%); C5 2016-06-30 (21%); C5 2016-10-31 (43%); C5 2016-11-30 (45%); C7 2016-04-30 (22%); C7 2016-05-31 (38%); C7 2016-06-30 (31%); C7 2016-10-31 (82%); C7 2016-11-30 (54%); C6 2016-05-31 (26%); C6 2016-06-30 (23%); C6 2016-10-31 (42%); C6 2016-11-30 (47%); C8 2016-05-31 (41%); C8 2016-06-30 (42%); C8 2016-09-30 (25%); C8 2016-10-31 (109%); C8 2016-11-30 (72%); C9 2016-09-30 (20%); C9 2016-10-31 (80%); C9 2016-11-30 (61%)
- Churn risk (accounts renewing in 2016): 2 at risk (≥20% churn prob): C5 29%, C7 29%

**Pricing & Margin**

- C1 (electricity): tariff £117.30-£139.04/MWh, net margin £40.67
- C1g (gas): tariff £24.34-£27.68/MWh, net margin £19.36
- C2 (electricity): tariff £107.62/MWh, net margin £5.07
- C2g (gas): tariff £26.92/MWh, net margin £47.53
- C3 (electricity): tariff £98.21/MWh, net margin £-14.14 -- **net-negative**
- C3g (gas): tariff £21.93/MWh, net margin £1.66
- C4 (electricity): tariff £98.43/MWh, net margin £-10.46 -- **net-negative**
- C4g (gas): tariff £24.40/MWh, net margin £13.35
- C5 (electricity): tariff £117.30-£138.48/MWh, net margin £117.24
- C6 (electricity): tariff £107.62/MWh, net margin £-74.58 -- **net-negative**
- C7 (electricity): tariff £92.16-£175.95/MWh, net margin £147.33
- C8 (electricity): tariff £84.56-£161.43/MWh, net margin £55.50
- C9 (electricity): tariff £77.16-£147.31/MWh, net margin £-6.40 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 1.4% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 108, average clarity 0.890, average bill shock 14.0%, bad debt provision £141.48, avg complaint probability 3.6%
- Solvency signal: £274,108/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £673.74 vs. naked (unhedged) net margin: £8,691.94
- hedging cost £8,018.20 vs. a fully unhedged book (commodity-only: actual net £673.74 vs. naked net £8,691.94)
  - C1: actual £91.45 vs. naked £546.11 -- hedging cost £454.66
  - C1g: actual £60.27 vs. naked £275.18 -- hedging cost £214.91
  - C2: actual £1.67 vs. naked £444.49 -- hedging cost £442.82
  - C2g: actual £60.84 vs. naked £203.62 -- hedging cost £142.78
  - C3: actual £-37.54 vs. naked £209.70 -- hedging cost £247.24
  - C3g: actual £0.44 vs. naked £112.13 -- hedging cost £111.69
  - C4: actual £-52.77 vs. naked £271.77 -- hedging cost £324.54
  - C4g: actual £47.15 vs. naked £209.67 -- hedging cost £162.52
  - C5: actual £278.91 vs. naked £2,561.03 -- hedging cost £2,282.12
  - C6: actual £-122.69 vs. naked £748.13 -- hedging cost £870.82
  - C7: actual £285.36 vs. naked £1,829.98 -- hedging cost £1,544.62
  - C8: actual £87.74 vs. naked £695.71 -- hedging cost £607.98
  - C9: actual £-27.09 vs. naked £584.41 -- hedging cost £611.50

**Year narrative:** 2016 produced a net gain of £342.13 across 13 accounts. The risk committee intervened 13 time(s), raising hedge fractions in response to elevated VaR. 21 customer(s) experienced a bill shock of >=20%.

## 2017

**Trading & Risk**

- Net margin: £29,972.08 (gross £122,417.71, capital £1,267.89)
  - Electricity: gross £121,571.94, capital £1,257.46, net £29,794.32
  - Gas: gross £845.77, capital £10.43, net £177.77
- Treasury at year end: £2,496,550.85
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.91 (avg 0.91), C1g 0.85 (avg 0.85), C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C3 0.90 (avg 0.90), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.90 (avg 0.90), C6 0.91 (avg 0.91), C7 0.90 (avg 0.90), C8 0.92 (avg 0.92), C9 0.91 (avg 0.91), C_IC1 0.94 (avg 0.94)
- Risk committee (Context Handshake) interventions: 12
  - 2017-01-25: treasury £2,466,966.55, C1->1.00, C5->1.00, C7->1.00, VaR (current £296.00 / stressed £93.84) ratio 3.15
  - 2017-02-24: treasury £2,466,965.24, C1->1.00, C5->1.00, C7->1.00, VaR (current £296.00 / stressed £93.84) ratio 3.15
  - 2017-03-26: treasury £2,466,964.39, C1->1.00, C5->1.00, C7->1.00, VaR (current £296.00 / stressed £93.84) ratio 3.15
  - 2017-04-25: treasury £2,466,961.77, C1->1.00, C5->1.00, C7->1.00, VaR (current £750.80 / stressed £284.48) ratio 2.64
  - 2017-05-25: treasury £2,466,957.27, C1->1.00, C5->1.00, C7->1.00, VaR (current £750.80 / stressed £284.48) ratio 2.64
  - 2017-06-24: treasury £2,466,953.46, C1->1.00, C5->1.00, C7->1.00, VaR (current £750.80 / stressed £284.48) ratio 2.64
  - 2017-07-24: treasury £2,466,884.76, C1->1.00, C5->1.00, C7->1.00, VaR (current £879.93 / stressed £345.56) ratio 2.55
  - 2017-08-23: treasury £2,466,880.20, C1->1.00, C5->1.00, C7->1.00, VaR (current £879.93 / stressed £345.56) ratio 2.55
  - 2017-09-22: treasury £2,466,874.92, C1->1.00, C5->1.00, C7->1.00, VaR (current £879.93 / stressed £345.56) ratio 2.55
  - 2017-10-22: treasury £2,466,961.21, C5->1.00, C7->1.00, VaR (current £888.20 / stressed £351.59) ratio 2.53
  - 2017-11-21: treasury £2,466,965.55, C5->1.00, C7->1.00, VaR (current £888.20 / stressed £351.59) ratio 2.53
  - 2017-12-21: treasury £2,466,969.72, C5->1.00, C7->1.00, VaR (current £888.20 / stressed £351.59) ratio 2.53
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.72
- Worst single period: C_IC1 on 2017-05-17 period 32, net margin £-20.46

**Customer Book**

- Active accounts: 14 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC1
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2017): £6,307.14
  - By billing account: C1 £2,570.36, C2 £6,817.26, C3 £3,091.12, C4 £4,105.10, C5 £7,456.75, C6 £13,185.27, C7 £5,239.64, C8 £7,868.97, C9 £6,429.77
- Bill shock events (>=20%): 28 -- C5 2017-01-31 (30%); C5 2017-02-28 (23%); C5 2017-05-31 (20%); C5 2017-06-30 (22%); C5 2017-11-30 (58%); C7 2017-01-31 (36%); C7 2017-02-28 (28%); C7 2017-05-31 (31%); C7 2017-06-30 (33%); C7 2017-09-30 (27%); C7 2017-10-31 (22%); C7 2017-11-30 (78%); C6 2017-05-31 (22%); C6 2017-06-30 (20%); C6 2017-11-30 (51%); C8 2017-05-31 (40%); C8 2017-06-30 (37%); C8 2017-09-30 (48%); C8 2017-10-31 (23%); C8 2017-11-30 (85%); C8 2017-12-31 (22%); C3 2017-07-31 (22%); C9 2017-05-31 (33%); C9 2017-06-30 (27%); C9 2017-09-30 (31%); C9 2017-10-31 (22%); C9 2017-11-30 (72%); C4 2017-10-31 (25%)
- Churn risk (accounts renewing in 2017): 5 at risk (≥20% churn prob): C5 32%, C6 35%, C7 38%, C8 35%, C9 32%

**Pricing & Margin**

- C1 (electricity): tariff £120.45-£139.04/MWh, net margin £50.50
- C1g (gas): tariff £27.68-£34.78/MWh, net margin £40.84
- C2 (electricity): tariff £107.62-£127.12/MWh, net margin £19.99
- C2g (gas): tariff £26.92-£34.35/MWh, net margin £108.74
- C3 (electricity): tariff £98.21-£129.70/MWh, net margin £7.12
- C3g (gas): tariff £21.93-£23.92/MWh, net margin £-7.40 -- **net-negative**
- C4 (electricity): tariff £98.43-£119.13/MWh, net margin £-42.88 -- **net-negative**
- C4g (gas): tariff £24.40-£27.18/MWh, net margin £35.59
- C5 (electricity): tariff £123.83-£138.48/MWh, net margin £160.49
- C6 (electricity): tariff £107.62-£132.39/MWh, net margin £12.42
- C7 (electricity): tariff £102.14-£204.03/MWh, net margin £136.45
- C8 (electricity): tariff £84.56-£192.94/MWh, net margin £133.55
- C9 (electricity): tariff £77.16-£189.03/MWh, net margin £75.78
- C_IC1 (electricity): tariff £78.24-£149.38/MWh, net margin £29,240.89

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 168, average clarity 0.884, average bill shock 11.5%, bad debt provision £1,325.92, avg complaint probability 3.6%
- Solvency signal: £249,655/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £29,595.76 vs. naked (unhedged) net margin: £111,070.71
- hedging cost £81,474.95 vs. a fully unhedged book (commodity-only: actual net £29,595.76 vs. naked net £111,070.71)
  - C1: actual £-52.78 vs. naked £198.34 -- hedging cost £251.12
  - C1g: actual £57.23 vs. naked £143.80 -- hedging cost £86.56
  - C2: actual £30.02 vs. naked £505.28 -- hedging cost £475.26
  - C2g: actual £123.78 vs. naked £248.23 -- hedging cost £124.45
  - C3: actual £53.11 vs. naked £313.22 -- hedging cost £260.11
  - C3g: actual £-15.18 vs. naked £65.60 -- hedging cost £80.78
  - C4: actual £-20.83 vs. naked £325.63 -- hedging cost £346.46
  - C4g: actual £2.49 vs. naked £128.88 -- hedging cost £126.39
  - C5: actual £-269.89 vs. naked £1,003.91 -- hedging cost £1,273.79
  - C6: actual £88.54 vs. naked £1,348.10 -- hedging cost £1,259.56
  - C7: actual £-52.05 vs. naked £819.27 -- hedging cost £871.32
  - C8: actual £186.72 vs. naked £922.23 -- hedging cost £735.52
  - C9: actual £223.71 vs. naked £935.08 -- hedging cost £711.37
  - C_IC1: actual £29,240.89 vs. naked £104,113.14 -- hedging cost £74,872.25

**Year narrative:** 2017 produced a net gain of £29,972.08 across 14 accounts. The risk committee intervened 12 time(s), raising hedge fractions in response to elevated VaR. 28 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £106,073.04 (gross £269,203.83, capital £1,551.61)
  - Electricity: gross £268,411.48, capital £1,536.81, net £105,944.82
  - Gas: gross £792.35, capital £14.80, net £128.23
- Treasury at year end: £2,484,425.75
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.91 (avg 0.91), C1g 0.85 (avg 0.85), C2 0.90 (avg 0.90), C2g 0.85 (avg 0.85), C3 0.90 (avg 0.90), C3g 0.85 (avg 0.85), C4 0.91 (avg 0.91), C4g 0.85 (avg 0.85), C5 0.91 (avg 0.91), C6 0.90 (avg 0.90), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.90 (avg 0.90), C_IC1 0.85 (avg 0.88), C_IC2 0.93 (avg 0.93)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2018-03-01 period 27, net margin £-14.84

**Customer Book**

- Active accounts: 15 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC2
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2018): £206,636.67
  - By billing account: C1 £2,193.25, C2 £5,946.35, C3 £3,264.59, C4 £3,851.56, C5 £9,130.25, C6 £11,560.48, C7 £5,252.49, C8 £6,618.54, C9 £6,076.04, C_IC1 £2,012,473.11
- Bill shock events (>=20%): 34 -- C5 2018-04-30 (32%); C5 2018-06-30 (21%); C5 2018-10-31 (32%); C5 2018-11-30 (28%); C7 2018-04-30 (39%); C7 2018-05-31 (29%); C7 2018-06-30 (31%); C7 2018-09-30 (30%); C7 2018-10-31 (48%); C7 2018-11-30 (33%); C6 2018-04-30 (25%); C6 2018-05-31 (22%); C6 2018-06-30 (22%); C6 2018-10-31 (31%); C6 2018-11-30 (22%); C8 2018-04-30 (35%); C8 2018-05-31 (38%); C8 2018-06-30 (44%); C8 2018-08-31 (26%); C8 2018-09-30 (55%); C8 2018-10-31 (56%); C8 2018-11-30 (30%); C9 2018-04-30 (32%); C9 2018-05-31 (35%); C9 2018-06-30 (35%); C9 2018-07-31 (22%); C9 2018-08-31 (44%); C9 2018-09-30 (46%); C9 2018-10-31 (41%); C9 2018-12-31 (20%); C4 2018-10-31 (32%); C4g 2018-10-31 (23%); C_IC1 2018-02-28 (61%); C_IC2 2018-09-30 (20%)
- Churn risk (accounts renewing in 2018): 6 at risk (≥20% churn prob): C4 20%, C5 38%, C6 32%, C7 41%, C8 35%, C9 38%

**Pricing & Margin**

- C1 (electricity): tariff £120.45-£166.66/MWh, net margin £-52.39 -- **net-negative**
- C1g (gas): tariff £34.78-£37.33/MWh, net margin £57.18
- C2 (electricity): tariff £127.12-£143.44/MWh, net margin £-20.27 -- **net-negative**
- C2g (gas): tariff £34.35-£38.13/MWh, net margin £88.12
- C3 (electricity): tariff £129.40-£129.70/MWh, net margin £10.30
- C3g (gas): tariff £23.92-£29.92/MWh, net margin £-18.58 -- **net-negative**
- C4 (electricity): tariff £119.13-£154.94/MWh, net margin £-2.97 -- **net-negative**
- C4g (gas): tariff £27.18-£34.87/MWh, net margin £1.50
- C5 (electricity): tariff £123.83-£165.11/MWh, net margin £-268.27 -- **net-negative**
- C6 (electricity): tariff £132.39-£143.62/MWh, net margin £-93.76 -- **net-negative**
- C7 (electricity): tariff £102.14-£228.55/MWh, net margin £-49.67 -- **net-negative**
- C8 (electricity): tariff £101.06-£208.62/MWh, net margin £78.91
- C9 (electricity): tariff £99.01-£208.98/MWh, net margin £189.80
- C_IC1 (electricity): tariff £-82.12-£233.42/MWh, net margin £112,884.03
- C_IC2 (electricity): tariff £70.26-£134.14/MWh, net margin £-6,730.90 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 180, average clarity 0.872, average bill shock 11.3%, bad debt provision £2,387.69, avg complaint probability 3.6%
- Solvency signal: £225,857/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £116,917.84 vs. naked (unhedged) net margin: £253,297.11
- hedging cost £136,379.27 vs. a fully unhedged book (commodity-only: actual net £116,917.84 vs. naked net £253,297.11)
  - C1: actual £60.84 vs. naked £434.06 -- hedging cost £373.23
  - C1g: actual £66.76 vs. naked £281.44 -- hedging cost £214.68
  - C2: actual £-43.12 vs. naked £571.03 -- hedging cost £614.14
  - C2g: actual £82.09 vs. naked £243.14 -- hedging cost £161.06
  - C3: actual £-33.41 vs. naked £308.78 -- hedging cost £342.19
  - C3g: actual £-11.73 vs. naked £142.75 -- hedging cost £154.47
  - C4: actual £42.30 vs. naked £566.88 -- hedging cost £524.58
  - C4g: actual £22.85 vs. naked £401.13 -- hedging cost £378.29
  - C5: actual £187.71 vs. naked £2,049.26 -- hedging cost £1,861.56
  - C6: actual £-202.92 vs. naked £1,378.42 -- hedging cost £1,581.35
  - C7: actual £35.93 vs. naked £1,312.27 -- hedging cost £1,276.34
  - C8: actual £-7.91 vs. naked £905.09 -- hedging cost £913.00
  - C9: actual £137.50 vs. naked £1,041.46 -- hedging cost £903.97
  - C_IC1: actual £123,311.85 vs. naked £210,085.45 -- hedging cost £86,773.60
  - C_IC2: actual £-6,730.90 vs. naked £33,575.93 -- hedging cost £40,306.83

**Year narrative:** 2018 produced a net gain of £106,073.04 across 15 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 34 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £226,643.10 (gross £710,361.89, capital £11,320.07)
  - Electricity: gross £634,769.00, capital £2,101.99, net £226,381.38
  - Gas: gross £75,592.89, capital £9,218.08, net £261.73
- Treasury at year end: £2,611,674.09
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.88 (avg 0.88), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.89 (avg 0.89), C3g 0.85 (avg 0.85), C4 0.88 (avg 0.88), C4g 0.85 (avg 0.85), C5 0.88 (avg 0.88), C6 0.91 (avg 0.91), C7 0.88 (avg 0.88), C8 0.92 (avg 0.92), C9 0.88 (avg 0.88), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2019-02-04 period 35, net margin £-14.60

**Customer Book**

- Active accounts: 17 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC3, C_IC3g
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2019): £252,710.31
  - By billing account: C1 £2,313.97, C2 £5,016.97, C3 £2,822.87, C4 £3,714.44, C5 £7,870.95, C6 £11,452.36, C7 £4,947.93, C8 £6,930.48, C9 £6,538.82, C_IC1 £1,671,916.15, C_IC2 £1,056,288.50
- Bill shock events (>=20%): 38 -- C1 2019-01-31 (22%); C1 2019-04-30 (22%); C5 2019-01-31 (46%); C5 2019-02-28 (22%); C5 2019-06-30 (26%); C5 2019-10-31 (44%); C5 2019-11-30 (36%); C7 2019-01-31 (42%); C7 2019-02-28 (26%); C7 2019-05-31 (24%); C7 2019-06-30 (35%); C7 2019-10-31 (73%); C7 2019-11-30 (46%); C2g 2019-04-30 (25%); C6 2019-02-28 (21%); C6 2019-06-30 (25%); C6 2019-10-31 (42%); C6 2019-11-30 (27%); C8 2019-01-31 (27%); C8 2019-02-28 (28%); C8 2019-04-30 (24%); C8 2019-06-30 (40%); C8 2019-07-31 (36%); C8 2019-09-30 (61%); C8 2019-10-31 (88%); C8 2019-11-30 (38%); C3 2019-04-30 (21%); C9 2019-02-28 (27%); C9 2019-04-30 (23%); C9 2019-06-30 (37%); C9 2019-07-31 (35%); C9 2019-09-30 (53%); C9 2019-10-31 (76%); C9 2019-11-30 (38%); C4g 2019-10-31 (27%); C_IC1 2019-02-28 (55%); C_IC1 2019-03-31 (129%); C_IC2 2019-02-28 (69%)
- Churn risk (accounts renewing in 2019): 8 at risk (≥20% churn prob): C1 20%, C4 20%, C5 38%, C6 32%, C7 35%, C8 38%, C9 32%, C_IC1 23%

**Pricing & Margin**

- C1 (electricity): tariff £129.89-£166.66/MWh, net margin £60.61
- C1g (gas): tariff £26.00-£37.33/MWh, net margin £66.86
- C2 (electricity): tariff £143.44-£151.47/MWh, net margin £42.88
- C2g (gas): tariff £26.00-£38.13/MWh, net margin £25.70
- C3 (electricity): tariff £125.89-£129.40/MWh, net margin £-29.18 -- **net-negative**
- C3g (gas): tariff £23.99-£29.92/MWh, net margin £16.26
- C4 (electricity): tariff £128.77-£154.94/MWh, net margin £33.03
- C4g (gas): tariff £20.47-£34.87/MWh, net margin £26.20
- C5 (electricity): tariff £131.21-£165.11/MWh, net margin £186.47
- C6 (electricity): tariff £143.62-£154.13/MWh, net margin £33.07
- C7 (electricity): tariff £103.18-£228.55/MWh, net margin £35.74
- C8 (electricity): tariff £109.28-£211.40/MWh, net margin £82.21
- C9 (electricity): tariff £103.89-£208.98/MWh, net margin £136.77
- C_IC1 (electricity): tariff £0.00-£267.52/MWh, net margin £143,120.71
- C_IC2 (electricity): tariff £-60.00-£283.06/MWh, net margin £81,495.84
- C_IC3 (electricity): tariff £54.22-£103.50/MWh, net margin £1,183.24
- C_IC3g (gas): tariff £27.53/MWh, net margin £126.70

**Portfolio Health**

- Capital cost ratio: 1.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.877, average bill shock 12.5%, bad debt provision £6,225.79, avg complaint probability 3.7%
- Solvency signal: £217,640/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £251,631.59 vs. naked (unhedged) net margin: £838,745.64
- hedging cost £587,114.06 vs. a fully unhedged book (commodity-only: actual net £251,631.59 vs. naked net £838,745.64)
  - C1: actual £-2.24 vs. naked £326.43 -- hedging cost £328.67
  - C1g: actual £57.00 vs. naked £198.00 -- hedging cost £140.99
  - C2: actual £81.10 vs. naked £790.62 -- hedging cost £709.51
  - C2g: actual £5.59 vs. naked £222.05 -- hedging cost £216.45
  - C3: actual £-16.82 vs. naked £391.13 -- hedging cost £407.95
  - C3g: actual £43.52 vs. naked £208.21 -- hedging cost £164.69
  - C4: actual £24.34 vs. naked £517.23 -- hedging cost £492.89
  - C4g: actual £37.94 vs. naked £263.15 -- hedging cost £225.21
  - C5: actual £-85.77 vs. naked £1,532.83 -- hedging cost £1,618.60
  - C6: actual £170.16 vs. naked £2,064.31 -- hedging cost £1,894.15
  - C7: actual £13.11 vs. naked £1,102.78 -- hedging cost £1,089.67
  - C8: actual £143.07 vs. naked £1,272.20 -- hedging cost £1,129.13
  - C9: actual £145.68 vs. naked £1,245.21 -- hedging cost £1,099.54
  - C_IC1: actual £160,623.08 vs. naked £301,777.75 -- hedging cost £141,154.67
  - C_IC2: actual £89,081.88 vs. naked £165,284.43 -- hedging cost £76,202.55
  - C_IC3: actual £1,183.24 vs. naked £295,972.25 -- hedging cost £294,789.01
  - C_IC3g: actual £126.70 vs. naked £65,577.06 -- hedging cost £65,450.36

**Year narrative:** 2019 produced a net gain of £226,643.10 across 17 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 38 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £-41,803.43 (gross £633,097.66, capital £7,410.82)
  - Electricity: gross £556,469.89, capital £2,025.44, net £-46,017.85
  - Gas: gross £76,627.77, capital £5,385.37, net £4,214.42
- Treasury at year end: £2,748,695.87
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.89 (avg 0.89), C1g 0.85 (avg 0.85), C2 0.86 (avg 0.86), C2g 0.85 (avg 0.85), C4 0.87 (avg 0.87), C4g 0.85 (avg 0.85), C5 0.88 (avg 0.88), C6 0.86 (avg 0.86), C7 0.88 (avg 0.88), C8 0.86 (avg 0.86), C9 0.85 (avg 0.85), C_IC1 0.85 (avg 0.87), C_IC2 0.85 (avg 0.87), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2020-12-31 period 1, net margin £-486.10

**Customer Book**

- Active accounts: 18 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC4
- Losses (churn) during year: C3
  - Renewals (retained): 9 accounts
- Average CLV (Point-in-Time, year-end 2020): £262,655.07
  - By billing account: C1 £2,131.34, C2 £5,504.03, C3 £2,241.16, C4 £3,550.64, C5 £7,953.89, C6 £8,236.99, C7 £5,066.95, C8 £6,642.92, C9 £5,947.97, C_IC1 £1,043,920.08, C_IC2 £536,317.03, C_IC3 £1,761,972.82, C_IC4 £25,030.09
- Bill shock events (>=20%): 32 -- C1 2020-04-30 (21%); C1g 2020-01-31 (20%); C5 2020-04-30 (29%); C5 2020-10-31 (39%); C5 2020-12-31 (26%); C7 2020-04-30 (35%); C7 2020-05-31 (21%); C7 2020-06-30 (28%); C7 2020-10-31 (62%); C7 2020-11-30 (24%); C7 2020-12-31 (36%); C6 2020-04-30 (31%); C6 2020-09-30 (21%); C6 2020-10-31 (34%); C6 2020-12-31 (26%); C8 2020-04-30 (36%); C8 2020-05-31 (26%); C8 2020-06-30 (33%); C8 2020-09-30 (57%); C8 2020-10-31 (68%); C8 2020-12-31 (44%); C9 2020-04-30 (28%); C9 2020-05-31 (26%); C9 2020-06-30 (36%); C9 2020-09-30 (47%); C9 2020-10-31 (51%); C9 2020-12-31 (37%); C_IC1 2020-03-31 (58%); C_IC1 2020-04-30 (78%); C_IC2 2020-02-29 (66%); C_IC2 2020-03-31 (123%); C_IC4 2020-12-31 (21%)
- Churn risk (accounts renewing in 2020): 7 at risk (≥20% churn prob): C1 26%, C5 35%, C6 32%, C7 38%, C8 38%, C9 41%, C_IC4 23%

**Pricing & Margin**

- C1 (electricity): tariff £129.89-£139.10/MWh, net margin £-2.64 -- **net-negative**
- C1g (gas): tariff £25.00-£26.00/MWh, net margin £56.87
- C2 (electricity): tariff £143.89-£151.47/MWh, net margin £120.59
- C2g (gas): tariff £22.48-£26.00/MWh, net margin £54.77
- C3 (electricity): tariff £125.89/MWh, net margin £-8.76 -- **net-negative**
- C3g (gas): tariff £23.99/MWh, net margin £25.10
- C4 (electricity): tariff £123.89-£128.77/MWh, net margin £4.12
- C4g (gas): tariff £16.57-£20.47/MWh, net margin £20.26
- C5 (electricity): tariff £131.21-£143.88/MWh, net margin £-88.20 -- **net-negative**
- C6 (electricity): tariff £143.89-£154.13/MWh, net margin £207.44
- C7 (electricity): tariff £103.18-£219.90/MWh, net margin £14.66
- C8 (electricity): tariff £110.73-£213.25/MWh, net margin £254.97
- C9 (electricity): tariff £86.87-£198.34/MWh, net margin £77.09
- C_IC1 (electricity): tariff £-73.45-£2690.77/MWh, net margin £59,662.94
- C_IC2 (electricity): tariff £-79.50-£283.06/MWh, net margin £46,781.50
- C_IC3 (electricity): tariff £38.88-£83.60/MWh, net margin £17,491.33
- C_IC3g (gas): tariff £16.06-£21.55/MWh, net margin £4,057.40
- C_IC4 (electricity): tariff £18.53-£73.19/MWh, net margin £-170,532.89 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 1.2% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.877, average bill shock 11.4%, bad debt provision £5,484.14, avg complaint probability 3.6%
- Solvency signal: £211,438/customer (13 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-257,161.28 vs. naked (unhedged) net margin: £600,642.27
- hedging cost £857,803.55 vs. a fully unhedged book (commodity-only: actual net £-257,161.28 vs. naked net £600,642.27)
  - C1: actual £-74.31 vs. naked £18.41 -- hedging cost £92.72
  - C1g: actual £-61.85 vs. naked £-221.49 -- hedging added £159.64
  - C2: actual £112.23 vs. naked £686.15 -- hedging cost £573.92
  - C2g: actual £62.96 vs. naked £165.50 -- hedging cost £102.54
  - C4: actual £-87.63 vs. naked £253.85 -- hedging cost £341.48
  - C4g: actual £-108.63 vs. naked £-196.17 -- hedging added £87.54
  - C5: actual £-359.38 vs. naked £164.99 -- hedging cost £524.36
  - C6: actual £164.32 vs. naked £1,619.88 -- hedging cost £1,455.56
  - C7: actual £-157.50 vs. naked £285.21 -- hedging cost £442.71
  - C8: actual £266.01 vs. naked £1,093.97 -- hedging cost £827.96
  - C9: actual £-91.70 vs. naked £622.96 -- hedging cost £714.66
  - C_IC1: actual £41,841.03 vs. naked £136,118.22 -- hedging cost £94,277.19
  - C_IC2: actual £45,917.01 vs. naked £98,961.61 -- hedging cost £53,044.61
  - C_IC3: actual £-3,268.31 vs. naked £231,155.16 -- hedging cost £234,423.46
  - C_IC3g: actual £6,424.32 vs. naked £146,590.86 -- hedging cost £140,166.55
  - C_IC4: actual £-347,739.85 vs. naked £-16,676.84 -- hedging cost £331,063.01

**Year narrative:** 2020 produced a net loss of £-41,803.43 across 18 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 32 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £-103,914.72 (gross £609,453.43, capital £16,023.03)
  - Electricity: gross £526,816.66, capital £5,800.27, net £-101,893.10
  - Gas: gross £82,636.76, capital £10,222.76, net £-2,021.62
- Treasury at year end: £2,604,267.23
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C4 0.94 (avg 0.94), C4g 0.85 (avg 0.85), C6 0.91 (avg 0.91), C7 0.97 (avg 0.97), C8 0.92 (avg 0.92), C9 0.92 (avg 0.92), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.89), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2021-12-31 period 1, net margin £-4,054.51

**Customer Book**

- Active accounts: 16 (C1, C1g, C2, C2g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: C1, C5
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2021): £246,861.95
  - By billing account: C1 £2,032.95, C2 £4,756.71, C3 £1,990.17, C4 £2,582.03, C5 £7,403.04, C6 £8,905.47, C7 £4,671.22, C8 £5,860.37, C9 £5,755.43, C_IC1 £881,756.59, C_IC2 £571,856.72, C_IC3 £1,688,960.11, C_IC4 £22,674.60
- Bill shock events (>=20%): 38 -- C1 2021-04-30 (20%); C5 2021-05-31 (23%); C5 2021-06-30 (32%); C5 2021-10-31 (30%); C5 2021-11-30 (51%); C7 2021-05-31 (30%); C7 2021-06-30 (48%); C7 2021-10-31 (56%); C7 2021-11-30 (66%); C2g 2021-04-30 (27%); C6 2021-06-30 (36%); C6 2021-10-31 (28%); C6 2021-11-30 (51%); C8 2021-05-31 (29%); C8 2021-06-30 (62%); C8 2021-09-30 (25%); C8 2021-10-31 (69%); C8 2021-11-30 (84%); C9 2021-02-28 (22%); C9 2021-05-31 (25%); C9 2021-06-30 (51%); C9 2021-08-31 (22%); C9 2021-09-30 (23%); C9 2021-10-31 (63%); C9 2021-11-30 (50%); C9 2021-12-31 (24%); C4 2021-10-31 (43%); C4g 2021-10-31 (62%); C_IC1 2021-05-31 (45%); C_IC2 2021-03-31 (27%); C_IC2 2021-04-30 (92%); C_IC3g 2021-09-30 (23%); C_IC3g 2021-10-31 (28%); C_IC3g 2021-12-31 (31%); C_IC4 2021-02-28 (28%); C_IC4 2021-07-31 (22%); C_IC4 2021-09-30 (40%); C_IC4 2021-12-31 (29%)
- Churn risk (accounts renewing in 2021): 8 at risk (≥20% churn prob): C5 35%, C6 35%, C7 35%, C8 41%, C9 35%, C_IC1 20%, C_IC2 23%, C_IC4 32%

**Pricing & Margin**

- C1 (electricity): tariff £139.10/MWh, net margin £-73.79 -- **net-negative**
- C1g (gas): tariff £25.00/MWh, net margin £-61.70 -- **net-negative**
- C2 (electricity): tariff £143.89-£183.00/MWh, net margin £84.36
- C2g (gas): tariff £22.48-£35.00/MWh, net margin £15.63
- C4 (electricity): tariff £123.89-£183.00/MWh, net margin £-191.28 -- **net-negative**
- C4g (gas): tariff £16.57-£35.00/MWh, net margin £-287.95 -- **net-negative**
- C5 (electricity): tariff £143.88/MWh, net margin £-356.16 -- **net-negative**
- C6 (electricity): tariff £143.89-£202.28/MWh, net margin £354.70
- C7 (electricity): tariff £115.18-£274.50/MWh, net margin £-168.01 -- **net-negative**
- C8 (electricity): tariff £111.70-£274.50/MWh, net margin £247.22
- C9 (electricity): tariff £86.87-£271.40/MWh, net margin £-79.33 -- **net-negative**
- C_IC1 (electricity): tariff £-54.00-£2365.91/MWh, net margin £34,682.23
- C_IC2 (electricity): tariff £-73.20-£1080.00/MWh, net margin £62,179.50
- C_IC3 (electricity): tariff £43.79-£390.95/MWh, net margin £-20,865.84 -- **net-negative**
- C_IC3g (gas): tariff £21.55-£125.90/MWh, net margin £-1,687.60 -- **net-negative**
- C_IC4 (electricity): tariff £42.47-£336.77/MWh, net margin £-177,706.70 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 2.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 192, average clarity 0.869, average bill shock 13.0%, bad debt provision £8,362.24, avg complaint probability 3.9%
- Solvency signal: £217,022/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-26,165.88 vs. naked (unhedged) net margin: £183,996.64
- hedging cost £210,162.52 vs. a fully unhedged book (commodity-only: actual net £-26,165.88 vs. naked net £183,996.64)
  - C2: actual £42.26 vs. naked £137.50 -- hedging cost £95.24
  - C2g: actual £-18.01 vs. naked £-387.95 -- hedging added £369.95
  - C4: actual £-489.61 vs. naked £-303.64 -- hedging cost £185.97
  - C4g: actual £-845.65 vs. naked £-1,586.23 -- hedging added £740.58
  - C6: actual £354.70 vs. naked £164.92 -- hedging added £189.77
  - C7: actual £-1,989.53 vs. naked £-1,038.19 -- hedging cost £951.34
  - C8: actual £169.02 vs. naked £-13.65 -- hedging added £182.67
  - C9: actual £-128.20 vs. naked £-264.40 -- hedging added £136.20
  - C_IC1: actual £36,073.09 vs. naked £-56,721.53 -- hedging added £92,794.62
  - C_IC2: actual £71,916.64 vs. naked £28,069.28 -- hedging added £43,847.35
  - C_IC3: actual £102,221.19 vs. naked £237,439.90 -- hedging cost £135,218.71
  - C_IC3g: actual £-48,879.18 vs. naked £38,284.45 -- hedging cost £87,163.63
  - C_IC4: actual £-184,592.59 vs. naked £-59,783.81 -- hedging cost £124,808.78

**Year narrative:** 2021 (flagged crisis year) produced a net loss of £-103,914.72 across 16 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 38 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £85,096.77 (gross £888,903.61, capital £65,310.02)
  - Electricity: gross £798,336.92, capital £13,413.27, net £133,998.89
  - Gas: gross £90,566.68, capital £51,896.75, net £-48,902.12
- Treasury at year end: £2,582,036.95
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.95 (avg 0.95), C4 0.96 (avg 0.96), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.93 (avg 0.93), C8 0.96 (avg 0.96), C9 0.94 (avg 0.94), C_IC1 1.00 (avg 0.97), C_IC2 1.00 (avg 0.97), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 9
  - 2022-04-29: treasury £2,716,641.83, C2->1.00, C6->1.00, C8->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £57,384.02 / stressed £21,272.82) ratio 2.70
  - 2022-05-29: treasury £2,716,719.50, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £57,498.85 / stressed £21,303.90) ratio 2.70
  - 2022-06-28: treasury £2,716,703.81, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £57,498.85 / stressed £21,303.90) ratio 2.70
  - 2022-07-28: treasury £2,716,299.58, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £57,581.26 / stressed £21,320.11) ratio 2.70
  - 2022-08-27: treasury £2,716,260.91, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £57,581.26 / stressed £21,320.11) ratio 2.70
  - 2022-09-26: treasury £2,716,219.27, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £57,581.26 / stressed £21,320.11) ratio 2.70
  - 2022-10-26: treasury £2,713,854.97, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £57,638.27 / stressed £21,328.10) ratio 2.70
  - 2022-11-25: treasury £2,713,691.39, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £57,638.27 / stressed £21,328.10) ratio 2.70
  - 2022-12-25: treasury £2,713,411.69, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £57,638.27 / stressed £21,328.10) ratio 2.70
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.70
- Worst single period: C_IC3g on 2022-12-31 period 1, net margin £-2,970.86

**Customer Book**

- Active accounts: 14 (C2, C2_2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: C2_2
- Losses (churn) during year: C2
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2022): £242,996.71
  - By billing account: C1 £2,125.93, C2 £3,916.21, C2_2 £522.38, C3 £1,925.16, C4 £1,754.78, C5 £6,323.82, C6 £9,374.73, C7 £3,651.74, C8 £5,545.82, C9 £5,272.96, C_IC1 £969,632.13, C_IC2 £540,763.13, C_IC3 £1,832,589.75, C_IC4 £18,555.44
- Bill shock events (>=20%): 54 -- C7 2022-01-31 (40%); C7 2022-02-28 (26%); C7 2022-04-30 (22%); C7 2022-05-31 (36%); C7 2022-06-30 (27%); C7 2022-09-30 (34%); C7 2022-11-30 (63%); C7 2022-12-31 (56%); C6 2022-04-30 (47%); C6 2022-05-31 (24%); C6 2022-09-30 (26%); C6 2022-11-30 (44%); C6 2022-12-31 (34%); C8 2022-02-28 (22%); C8 2022-05-31 (39%); C8 2022-06-30 (35%); C8 2022-07-31 (22%); C8 2022-09-30 (85%); C8 2022-11-30 (72%); C8 2022-12-31 (58%); C9 2022-04-30 (21%); C9 2022-05-31 (30%); C9 2022-06-30 (31%); C9 2022-09-30 (50%); C9 2022-10-31 (31%); C9 2022-11-30 (45%); C9 2022-12-31 (53%); C4 2022-10-31 (62%); C4g 2022-10-31 (121%); C_IC1 2022-06-30 (85%); C_IC2 2022-05-31 (62%); C_IC3 2022-01-31 (105%); C_IC3g 2022-03-31 (55%); C_IC3g 2022-04-30 (20%); C_IC3g 2022-07-31 (46%); C_IC3g 2022-08-31 (30%); C_IC3g 2022-09-30 (21%); C_IC3g 2022-10-31 (51%); C_IC3g 2022-11-30 (21%); C_IC3g 2022-12-31 (21%); C_IC4 2022-02-28 (21%); C_IC4 2022-03-31 (44%); C_IC4 2022-05-31 (21%); C_IC4 2022-07-31 (38%); C_IC4 2022-08-31 (41%); C_IC4 2022-10-31 (39%); C_IC4 2022-12-31 (102%); C2_2 2022-04-30 (1712%); C2_2 2022-05-31 (39%); C2_2 2022-06-30 (33%); C2_2 2022-07-31 (20%); C2_2 2022-09-30 (78%); C2_2 2022-11-30 (65%); C2_2 2022-12-31 (58%)
- Churn risk (accounts renewing in 2022): 8 at risk (≥20% churn prob): C4 20%, C6 32%, C7 38%, C8 38%, C9 38%, C_IC1 20%, C_IC3 26%, C_IC4 38%

**Pricing & Margin**

- C2 (electricity): tariff £183.00/MWh, net margin £-28.45 -- **net-negative**
- C2_2 (electricity): tariff £361.95/MWh, net margin £-91.03 -- **net-negative**
- C2g (gas): tariff £35.00/MWh, net margin £-23.24 -- **net-negative**
- C4 (electricity): tariff £183.00-£305.00/MWh, net margin £-571.71 -- **net-negative**
- C4g (gas): tariff £35.00-£95.00/MWh, net margin £-1,083.36 -- **net-negative**
- C6 (electricity): tariff £202.28-£419.24/MWh, net margin £629.93
- C7 (electricity): tariff £143.79-£457.50/MWh, net margin £-1,986.17 -- **net-negative**
- C8 (electricity): tariff £143.79-£457.50/MWh, net margin £-347.74 -- **net-negative**
- C9 (electricity): tariff £142.16-£396.36/MWh, net margin £-223.35 -- **net-negative**
- C_IC1 (electricity): tariff £-83.39-£467.78/MWh, net margin £140,831.02
- C_IC2 (electricity): tariff £-80.56-£593.08/MWh, net margin £79,117.19
- C_IC3 (electricity): tariff £141.81-£390.95/MWh, net margin £101,214.89
- C_IC3g (gas): tariff £120.20-£125.90/MWh, net margin £-47,795.53 -- **net-negative**
- C_IC4 (electricity): tariff £71.50-£469.98/MWh, net margin £-184,545.69 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 7.3% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £2,901,107.60 -> £2,582,036.95 (11.0%)
- Bills issued: 148, average clarity 0.811, average bill shock 32.3%, bad debt provision £34,109.66, avg complaint probability 5.3%
- Solvency signal: £234,731/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-65,258.42 vs. naked (unhedged) net margin: £919,928.19
- hedging cost £985,186.61 vs. a fully unhedged book (commodity-only: actual net £-65,258.42 vs. naked net £919,928.19)
  - C2_2: actual £-136.24 vs. naked £1,470.79 -- hedging cost £1,607.02
  - C4: actual £-678.78 vs. naked £811.29 -- hedging cost £1,490.07
  - C4g: actual £-1,601.62 vs. naked £778.72 -- hedging cost £2,380.34
  - C6: actual £912.31 vs. naked £3,214.36 -- hedging cost £2,302.04
  - C7: actual £-534.71 vs. naked £2,087.74 -- hedging cost £2,622.46
  - C8: actual £-515.43 vs. naked £927.73 -- hedging cost £1,443.16
  - C9: actual £-169.21 vs. naked £888.10 -- hedging cost £1,057.31
  - C_IC1: actual £224,964.23 vs. naked £263,325.39 -- hedging cost £38,361.16
  - C_IC2: actual £93,754.79 vs. naked £133,595.35 -- hedging cost £39,840.56
  - C_IC3: actual £-150,190.48 vs. naked £468,017.25 -- hedging cost £618,207.73
  - C_IC3g: actual £-30,255.66 vs. naked £83,300.79 -- hedging cost £113,556.45
  - C_IC4: actual £-200,807.61 vs. naked £-38,489.32 -- hedging cost £162,318.29

**Year narrative:** 2022 (flagged crisis year) produced a net gain of £85,096.77 across 14 accounts. The risk committee intervened 9 time(s), raising hedge fractions in response to elevated VaR. 54 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £-120,422.84 (gross £748,058.99, capital £49,388.73)
  - Electricity: gross £626,487.06, capital £10,053.47, net £-88,561.39
  - Gas: gross £121,571.93, capital £39,335.26, net £-31,861.45
- Treasury at year end: £2,517,349.36
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.93 (avg 0.93), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C6 0.93 (avg 0.93), C7 0.92 (avg 0.92), C8 0.95 (avg 0.95), C9 0.91 (avg 0.91), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 4
  - 2023-01-24: treasury £2,582,024.54, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £123,516.89 / stressed £44,713.04) ratio 2.76
  - 2023-02-23: treasury £2,582,009.16, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £123,516.89 / stressed £44,713.04) ratio 2.76
  - 2023-03-25: treasury £2,581,993.74, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £123,516.89 / stressed £44,713.04) ratio 2.76
  - 2023-04-24: treasury £2,668,136.11, C2->1.00, C4->1.00, C7->1.00, C9->1.00, C_IC3->1.00, VaR (current £130,588.42 / stressed £49,751.53) ratio 2.62
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.73
- Worst single period: C_IC3g on 2023-12-31 period 1, net margin £-3,476.75

**Customer Book**

- Active accounts: 12 (C2_2, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2023): £233,464.77
  - By billing account: C1 £2,162.80, C2 £3,640.43, C2_2 £1,615.86, C3 £1,913.10, C4 £1,146.48, C5 £6,109.56, C6 £10,033.16, C7 £3,715.64, C8 £5,321.30, C9 £5,354.64, C_IC1 £1,027,112.98, C_IC2 £602,276.01, C_IC3 £1,579,976.33, C_IC4 £18,128.49
- Bill shock events (>=20%): 35 -- C7 2023-01-31 (41%); C7 2023-05-31 (32%); C7 2023-06-30 (37%); C7 2023-10-31 (57%); C7 2023-11-30 (73%); C6 2023-04-30 (29%); C6 2023-05-31 (24%); C6 2023-06-30 (23%); C6 2023-10-31 (39%); C6 2023-11-30 (44%); C8 2023-04-30 (31%); C8 2023-05-31 (41%); C8 2023-06-30 (44%); C8 2023-10-31 (101%); C8 2023-11-30 (70%); C9 2023-02-28 (21%); C9 2023-03-31 (21%); C9 2023-04-30 (27%); C9 2023-05-31 (33%); C9 2023-06-30 (46%); C9 2023-09-30 (23%); C9 2023-10-31 (77%); C9 2023-11-30 (55%); C4g 2023-10-31 (23%); C_IC1 2023-06-30 (56%); C_IC1 2023-07-31 (71%); C_IC2 2023-05-31 (57%); C_IC2 2023-06-30 (117%); C_IC3g 2023-01-31 (34%); C_IC4 2023-01-31 (46%); C2_2 2023-04-30 (20%); C2_2 2023-05-31 (42%); C2_2 2023-06-30 (42%); C2_2 2023-10-31 (97%); C2_2 2023-11-30 (67%)
- Churn risk (accounts renewing in 2023): 6 at risk (≥20% churn prob): C2_2 35%, C6 29%, C7 38%, C8 38%, C9 38%, C_IC4 32%

**Pricing & Margin**

- C2_2 (electricity): tariff £361.95-£370.05/MWh, net margin £434.59
- C4 (electricity): tariff £262.08-£305.00/MWh, net margin £-412.60 -- **net-negative**
- C4g (gas): tariff £66.00-£95.00/MWh, net margin £-1,099.91 -- **net-negative**
- C6 (electricity): tariff £362.51-£419.24/MWh, net margin £1,206.12
- C7 (electricity): tariff £199.57-£457.50/MWh, net margin £-532.56 -- **net-negative**
- C8 (electricity): tariff £208.21-£457.50/MWh, net margin £-209.06 -- **net-negative**
- C9 (electricity): tariff £192.33-£396.36/MWh, net margin £67.89
- C_IC1 (electricity): tariff £-60.00-£467.78/MWh, net margin £170,877.91
- C_IC2 (electricity): tariff £-186.24-£482.19/MWh, net margin £90,002.65
- C_IC3 (electricity): tariff £100.61-£270.72/MWh, net margin £-149,137.96 -- **net-negative**
- C_IC3g (gas): tariff £61.62-£120.20/MWh, net margin £-30,761.54 -- **net-negative**
- C_IC4 (electricity): tariff £36.40-£169.32/MWh, net margin £-200,858.37 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 6.6% of gross
- Treasury drawdown events (>=10% threshold): 20 -- £2,901,018.09 -> £2,582,034.81 (11.0%); £2,901,018.09 -> £2,582,034.80 (11.0%); £2,901,018.25 -> £2,582,034.79 (11.0%); £2,901,018.40 -> £2,582,034.78 (11.0%); £2,901,018.56 -> £2,582,034.76 (11.0%); £2,901,018.72 -> £2,582,034.75 (11.0%); £2,901,018.90 -> £2,514,820.55 (13.3%); £2,901,027.92 -> £2,514,812.68 (13.3%); £2,901,058.91 -> £2,514,806.45 (13.3%); £2,901,085.40 -> £2,514,801.86 (13.3%); £2,901,104.66 -> £2,514,799.69 (13.3%); £2,901,105.32 -> £2,514,798.17 (13.3%); £2,901,106.04 -> £2,514,796.55 (13.3%); £2,901,106.46 -> £2,514,795.57 (13.3%); £2,901,106.60 -> £2,514,795.07 (13.3%); £2,901,106.72 -> £2,514,794.75 (13.3%); £2,901,106.84 -> £2,514,794.41 (13.3%); £2,901,107.16 -> £2,514,794.17 (13.3%); £2,901,107.65 -> £2,506,042.98 (13.6%); £2,921,348.87 -> £2,517,345.68 (13.8%)
- Bills issued: 144, average clarity 0.827, average bill shock 16.4%, bad debt provision £12,914.21, avg complaint probability 4.6%
- Solvency signal: £251,735/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £140,858.41 vs. naked (unhedged) net margin: £936,495.46
- hedging cost £795,637.05 vs. a fully unhedged book (commodity-only: actual net £140,858.41 vs. naked net £936,495.46)
  - C2_2: actual £827.08 vs. naked £2,420.08 -- hedging cost £1,593.00
  - C4: actual £252.64 vs. naked £967.16 -- hedging cost £714.52
  - C4g: actual £360.46 vs. naked £643.87 -- hedging cost £283.41
  - C6: actual £1,416.93 vs. naked £4,357.94 -- hedging cost £2,941.02
  - C7: actual £435.97 vs. naked £1,883.02 -- hedging cost £1,447.05
  - C8: actual £17.48 vs. naked £1,770.70 -- hedging cost £1,753.21
  - C9: actual £420.40 vs. naked £1,917.27 -- hedging cost £1,496.87
  - C_IC1: actual £152,008.37 vs. naked £295,820.02 -- hedging cost £143,811.64
  - C_IC2: actual £98,975.16 vs. naked £167,487.89 -- hedging cost £68,512.73
  - C_IC3: actual £153,241.55 vs. naked £428,822.77 -- hedging cost £275,581.21
  - C_IC3g: actual £-36,844.69 vs. naked £77,607.60 -- hedging cost £114,452.30
  - C_IC4: actual £-230,252.95 vs. naked £-47,202.85 -- hedging cost £183,050.10

**Year narrative:** 2023 produced a net loss of £-120,422.84 across 12 accounts. The risk committee intervened 4 time(s), raising hedge fractions in response to elevated VaR. 35 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £94,357.74 (gross £1,068,921.48, capital £55,792.83)
  - Electricity: gross £944,793.11, capital £9,881.03, net £131,244.65
  - Gas: gross £124,128.37, capital £45,911.80, net £-36,886.91
- Treasury at year end: £2,657,841.10
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.90 (avg 0.90), C4 0.86 (avg 0.86), C4g 0.85 (avg 0.85), C7 0.90 (avg 0.90), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89), C_IC1 0.85 (avg 0.87), C_IC2 0.85 (avg 0.87), C_IC3 0.94 (avg 0.94), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 5
  - 2024-01-19: treasury £2,517,438.13, C2->1.00, VaR (current £93,161.41 / stressed £52,985.82) ratio 1.76
  - 2024-02-18: treasury £2,517,546.81, C2->1.00, VaR (current £93,161.41 / stressed £52,985.82) ratio 1.76
  - 2024-03-19: treasury £2,517,659.57, C2->1.00, VaR (current £93,161.41 / stressed £52,985.82) ratio 1.76
  - 2024-04-18: treasury £2,598,986.58, C2->1.00, VaR (current £84,105.61 / stressed £63,793.12) ratio 1.32
  - 2024-05-18: treasury £2,606,885.84, C2->1.00, VaR (current £84,105.61 / stressed £63,793.12) ratio 1.32
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 1.58
- Worst single period: C_IC3g on 2024-12-30 period 1, net margin £-1,917.34

**Customer Book**

- Active accounts: 12 (C2_2, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: C6
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2024): £251,548.17
  - By billing account: C1 £2,188.95, C2 £3,755.63, C2_2 £2,426.76, C3 £1,901.91, C4 £1,939.78, C5 £6,032.93, C6 £9,741.42, C7 £4,375.44, C8 £5,669.77, C9 £5,777.80, C_IC1 £1,064,580.25, C_IC2 £641,230.30, C_IC3 £1,753,092.04, C_IC4 £18,961.40
- Bill shock events (>=20%): 29 -- C7 2024-02-29 (27%); C7 2024-05-31 (38%); C7 2024-09-30 (37%); C7 2024-10-31 (39%); C7 2024-11-30 (51%); C8 2024-02-29 (23%); C8 2024-04-30 (34%); C8 2024-05-31 (50%); C8 2024-07-31 (28%); C8 2024-09-30 (81%); C8 2024-10-31 (37%); C8 2024-11-30 (64%); C9 2024-05-31 (50%); C9 2024-07-31 (31%); C9 2024-09-30 (59%); C9 2024-10-31 (23%); C9 2024-11-30 (49%); C_IC1 2024-07-31 (37%); C_IC1 2024-08-31 (74%); C_IC2 2024-06-30 (52%); C_IC2 2024-07-31 (122%); C_IC4 2024-05-31 (25%); C2_2 2024-02-29 (23%); C2_2 2024-04-30 (47%); C2_2 2024-05-31 (50%); C2_2 2024-07-31 (27%); C2_2 2024-09-30 (72%); C2_2 2024-10-31 (36%); C2_2 2024-11-30 (60%)
- Churn risk (accounts renewing in 2024): 6 at risk (≥20% churn prob): C2_2 38%, C6 38%, C7 35%, C8 41%, C9 38%, C_IC4 26%

**Pricing & Margin**

- C2_2 (electricity): tariff £230.29-£370.05/MWh, net margin £460.41
- C4 (electricity): tariff £204.52-£262.08/MWh, net margin £170.85
- C4g (gas): tariff £55.00-£66.00/MWh, net margin £315.71
- C6 (electricity): tariff £362.51/MWh, net margin £506.00
- C7 (electricity): tariff £165.00-£381.00/MWh, net margin £433.85
- C8 (electricity): tariff £165.00-£397.50/MWh, net margin £145.51
- C9 (electricity): tariff £165.00-£367.18/MWh, net margin £339.71
- C_IC1 (electricity): tariff £-98.58-£336.20/MWh, net margin £133,302.43
- C_IC2 (electricity): tariff £-106.92-£359.42/MWh, net margin £73,514.83
- C_IC3 (electricity): tariff £91.98-£192.07/MWh, net margin £153,447.57
- C_IC3g (gas): tariff £56.37-£61.62/MWh, net margin £-37,202.62 -- **net-negative**
- C_IC4 (electricity): tariff £23.97-£113.12/MWh, net margin £-231,076.52 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 5.2% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £2,921,259.81 -> £2,517,349.38 (13.8%)
- Bills issued: 135, average clarity 0.832, average bill shock 15.4%, bad debt provision £10,424.99, avg complaint probability 4.4%
- Solvency signal: £265,784/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £91,821.62 vs. naked (unhedged) net margin: £466,359.48
- hedging cost £374,537.86 vs. a fully unhedged book (commodity-only: actual net £91,821.62 vs. naked net £466,359.48)
  - C2_2: actual £185.64 vs. naked £1,133.92 -- hedging cost £948.29
  - C4: actual £-32.85 vs. naked £392.71 -- hedging cost £425.56
  - C4g: actual £78.37 vs. naked £151.09 -- hedging cost £72.73
  - C7: actual £-109.71 vs. naked £555.29 -- hedging cost £665.01
  - C8: actual £175.30 vs. naked £1,249.75 -- hedging cost £1,074.45
  - C9: actual £167.07 vs. naked £1,217.40 -- hedging cost £1,050.32
  - C_IC1: actual £123,598.52 vs. naked £218,723.34 -- hedging cost £95,124.82
  - C_IC2: actual £65,280.57 vs. naked £116,615.17 -- hedging cost £51,334.60
  - C_IC3: actual £26,242.03 vs. naked £127,243.27 -- hedging cost £101,001.23
  - C_IC3g: actual £-23,434.60 vs. naked £25,544.36 -- hedging cost £48,978.96
  - C_IC4: actual £-100,328.70 vs. naked £-26,466.80 -- hedging cost £73,861.89

**Year narrative:** 2024 produced a net gain of £94,357.74 across 12 accounts. The risk committee intervened 5 time(s), raising hedge fractions in response to elevated VaR. 29 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £6,600.70 (gross £436,444.40, capital £29,155.68)
  - Electricity: gross £384,179.02, capital £5,855.61, net £26,148.67
  - Gas: gross £52,265.38, capital £23,300.07, net £-19,547.97
- Treasury at year end: £2,712,651.70
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C8 0.89 (avg 0.89)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2025-06-01 period 1, net margin £-530.95

**Customer Book**

- Active accounts: 11 (C2_2, C4, C4g, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 0, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 2 accounts
- Average CLV (Point-in-Time, year-end 2025): £267,471.33
  - By billing account: C1 £2,117.55, C2 £3,459.85, C2_2 £2,559.22, C3 £1,817.05, C4 £2,056.66, C5 £6,035.77, C6 £9,858.67, C7 £4,698.36, C8 £5,237.29, C9 £5,558.58, C_IC1 £1,111,889.72, C_IC2 £670,622.87, C_IC3 £1,898,212.73, C_IC4 £20,474.26
- Bill shock events (>=20%): 23 -- C7 2025-04-30 (37%); C7 2025-05-31 (24%); C7 2025-06-07 (80%); C8 2025-01-31 (40%); C8 2025-02-28 (24%); C8 2025-04-30 (42%); C8 2025-05-31 (38%); C8 2025-06-07 (73%); C9 2025-01-31 (22%); C9 2025-04-30 (25%); C9 2025-05-31 (34%); C9 2025-06-07 (71%); C4 2025-06-07 (78%); C4g 2025-06-07 (77%); C_IC1 2025-06-07 (77%); C_IC2 2025-06-07 (75%); C_IC3 2025-06-07 (78%); C_IC3g 2025-06-07 (77%); C_IC4 2025-06-07 (81%); C2_2 2025-01-31 (39%); C2_2 2025-02-28 (24%); C2_2 2025-05-31 (37%); C2_2 2025-06-07 (73%)
- Churn risk (accounts renewing in 2025): 3 at risk (≥20% churn prob): C2_2 38%, C8 38%, C9 38%

**Pricing & Margin**

- C2_2 (electricity): tariff £230.29-£327.63/MWh, net margin £172.50
- C4 (electricity): tariff £204.52/MWh, net margin £-19.27 -- **net-negative**
- C4g (gas): tariff £55.00/MWh, net margin £51.96
- C7 (electricity): tariff £165.00-£315.00/MWh, net margin £-104.77 -- **net-negative**
- C8 (electricity): tariff £149.29-£315.00/MWh, net margin £12.14
- C9 (electricity): tariff £165.00-£315.00/MWh, net margin £100.19
- C_IC1 (electricity): tariff £169.74-£324.06/MWh, net margin £67,058.89
- C_IC2 (electricity): tariff £163.52-£312.18/MWh, net margin £31,834.52
- C_IC3 (electricity): tariff £91.98-£175.60/MWh, net margin £26,095.99
- C_IC3g (gas): tariff £56.37/MWh, net margin £-19,599.93 -- **net-negative**
- C_IC4 (electricity): tariff £43.11-£193.69/MWh, net margin £-99,001.53 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 6.7% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 66, average clarity 0.795, average bill shock 23.8%, bad debt provision £4,563.02, avg complaint probability 5.8%
- Solvency signal: £301,406/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £31.20 vs. naked (unhedged) net margin: £310.72
- hedging cost £279.52 vs. a fully unhedged book (commodity-only: actual net £31.20 vs. naked net £310.72)
  - C2_2: actual £99.99 vs. naked £234.73 -- hedging cost £134.74
  - C8: actual £-68.79 vs. naked £75.99 -- hedging cost £144.78

**Year narrative:** 2025 produced a net gain of £6,600.70 across 11 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 23 customer(s) experienced a bill shock of >=20%.
