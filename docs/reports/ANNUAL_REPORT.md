# Annual Report — The Synthetic Enterprise


## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £2,466,636.22
- Final treasury: £3,911,893.89
  (£1,445,257.67 net change)
- Solvency signal (final year): £376,060/customer (10 customers, OK; Ofgem floor £130/customer)
- Customer bills (all-in): £19,819,620.93
  VAT remitted to HMRC: (£957,157.22) | Revenue (ex-VAT): £18,862,463.71
  Non-commodity pass-through: (£4,787,181.64)
- Gross margin: £6,467,308.57
- Capital costs: £51,432.98
- Net margin: £6,415,875.59
- Capital cost ratio: 0.8% of gross
- Net margin as % of revenue: 34.0%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 38
- Bills issued: 1605, average clarity 0.811,
  service quality score 0.903
- Enterprise value (CLV sum across 16 billing accounts): £8,826,938.57
- Cost to serve (whole portfolio): £91,780.10, net margin after cost to serve: £6,324,095.49
- Hedge effectiveness (whole window): hedging cost £4,232,037.05 vs. a fully unhedged book (commodity-only: actual net £1,445,257.67 vs. naked net £5,677,294.72)

- **2021** (crisis year): net margin £67,928.67, 0 risk committee wake-up(s).
- **2022** (crisis year): net margin £300,205.86, 9 risk committee wake-up(s).

## Board Risk Summary

Synthesised risk indicators across portfolio, capital, operations and pricing.
RAG: RED = immediate board action, AMBER = monitor closely, GREEN = on track.

| Risk Indicator | Value | RAG | Implication |
|----------------|-------|-----|-------------|
| Revenue concentration | HHI 2244, I&C 98% | **AMBER** | Single I&C departure removes 14-29%% of margin |
| Gas segment ROC | 263.5x (net £52,090.65 on £197.67 capital) | **GREEN** | Gas legs destroy capital; electricity cross-subsidises |
| Churn blind miss rate | 5/6 departures (83%) | **RED** | Company did not forecast these churns |
| Demand estimation error | Peak mean 3.1%, max 15.6% | **RED** | EAC drift from asset acquisitions; smart meters eliminate |
| Pricing basis risk (worst year) | 2025: +33.1% mean over-estimate | **RED** | Over-priced contracts help margin but create churn risk |
| Net margin % of revenue | 34.0% (benchmark: 2-5%) | **GREEN** | Within/above industry range |

**Board Action Required:** Churn blind miss rate, Demand estimation error, Pricing basis risk (worst year) — RED rating(s) require immediate attention.

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £6,467,308.57, capital £51,432.98, net £6,415,875.59. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 0.8% (commodity basis, comparable to old model) / 0.8% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £67,928.67 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 34.0%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £6,415,875.59
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £5,677,294.72
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £4,232,037.05 vs. a fully unhedged book (commodity-only: actual net £1,445,257.67 vs. naked net £5,677,294.72)
- **Best hedging decision of the run**: C_IC1, term starting
  2021-04-30 (hedge fraction 0.92) -- hedging
  protected £99,382.46 vs. going naked.
- **Worst hedging decision of the run**: C_IC3, term
  starting 2022-12-31 (hedge fraction 0.96) --
  over-hedging cost £612,664.13 vs. going
  naked.

## Segment Margin Trend

Net margin (£) by segment, by year:

| Year | I&C electricity | I&C gas | SME electricity | resi electricity | resi gas | Total |
|---|---|---|---|---|---|---|
| 2016 | £0.00 | £0.00 | £254.88 | £626.84 | £296.53 | £1,178.25 |
| 2017 | £29,047.38 | £0.00 | £233.41 | £821.92 | £463.34 | £30,566.05 |
| 2018 | £99,071.38 | £0.00 | £-244.55 | £504.67 | £374.66 | £99,706.17 |
| 2019 | £217,183.69 | £9,326.63 | £213.88 | £720.65 | £427.56 | £227,872.41 |
| 2020 | £111,153.96 | £9,435.16 | £335.69 | £874.72 | £417.37 | £122,216.90 |
| 2021 | £59,275.26 | £8,520.22 | £210.66 | £157.61 | £-235.08 | £67,928.67 |
| 2022 | £298,776.33 | £4,134.82 | £1,145.42 | £-2,548.86 | £-1,301.85 | £300,205.86 |
| 2023 | £140,329.18 | £8,526.27 | £141.63 | £-479.10 | £-1,164.32 | £147,353.65 |
| 2024 | £316,713.64 | £8,684.92 | £1,671.29 | £2,693.52 | £396.91 | £330,160.28 |
| 2025 | £113,606.91 | £3,787.52 | £113.41 | £561.60 | £0.00 | £118,069.43 |

## Customer Lifecycle Events

Renewal decisions rolled at each annual renewal point across the simulation window.
Retained: **56** renewals.  Lost (churned): **6** accounts.

Accounts lost before end of window: C1, C2, C3, C4, C5, C6

| Account | Date | Outcome | p(churn) | p(win-back) | p(retain) | Roll |
|---------|------|---------|----------|-------------|-----------|------|
| C1 | 2016-12-31 | renewed | 0.0500 | 0.5500 | 0.9462 | 0.1646 |
| C5 | 2016-12-31 | renewed | 0.0500 | 0.3500 | 0.9223 | 0.2812 |
| C7 | 2016-12-31 | renewed | 0.0500 | 0.5500 | 0.9462 | 0.1050 |
| C1 | 2017-12-31 | renewed | 0.1100 | 0.5500 | 0.9113 | 0.6188 |
| C5 | 2017-12-31 | renewed | 0.1100 | 0.3500 | 0.8718 | 0.4449 |
| C7 | 2017-12-31 | renewed | 0.1100 | 0.5500 | 0.9113 | 0.8255 |
| C_IC1 | 2018-01-31 | renewed | 0.0500 | 0.5500 | 0.9677 | 0.3902 |
| C1 | 2018-12-31 | renewed | 0.1100 | 0.5500 | 0.9290 | 0.0480 |
| C5 | 2018-12-31 | renewed | 0.1100 | 0.3500 | 0.8718 | 0.3096 |
| C7 | 2018-12-31 | renewed | 0.2000 | 0.5500 | 0.8387 | 0.6312 |
| C_IC2 | 2019-01-31 | renewed | 0.0500 | 0.5500 | 0.9707 | 0.3710 |
| C1 | 2019-12-31 | renewed | 0.2900 | 0.5500 | 0.7873 | 0.2972 |
| C5 | 2019-12-31 | renewed | 0.3500 | 0.3500 | 0.8370 | 0.4302 |
| C7 | 2019-12-31 | renewed | 0.2900 | 0.5500 | 0.8370 | 0.7670 |
| C2 | 2020-03-31 | renewed | 0.0800 | 0.5500 | 0.9531 | 0.8936 |
| C6 | 2020-03-31 | renewed | 0.1100 | 0.3500 | 0.9068 | 0.4643 |
| C8 | 2020-03-31 | renewed | 0.2300 | 0.5500 | 0.8651 | 0.1066 |
| C3 | 2020-06-30 | churned **CHURNED** | 0.1100 | 0.5500 | 0.9355 | 0.9704 |
| C9 | 2020-06-30 | renewed | 0.2300 | 0.5500 | 0.8651 | 0.5378 |
| C4 | 2020-09-30 | renewed | 0.4100 | 0.5500 | 0.8696 | 0.2845 |
| C1 | 2020-12-30 | churned **CHURNED** | 0.3800 | 0.5500 | 0.7771 | 0.8047 |
| C5 | 2020-12-30 | renewed | 0.3200 | 0.3500 | 0.8696 | 0.7480 |
| C7 | 2020-12-30 | renewed | 0.2000 | 0.5500 | 0.8827 | 0.4829 |
| C_IC3 | 2020-12-31 | renewed | 0.2000 | 0.5500 | 0.8827 | 0.5941 |
| C2 | 2021-03-31 | renewed | 0.0800 | 0.5500 | 0.9707 | 0.6102 |
| C6 | 2021-03-31 | renewed | 0.0800 | 0.3500 | 0.9576 | 0.5431 |
| C8 | 2021-03-31 | renewed | 0.2000 | 0.5500 | 0.9267 | 0.4901 |
| C9 | 2021-06-30 | renewed | 0.2000 | 0.5500 | 0.9267 | 0.5305 |
| C4 | 2021-09-30 | renewed | 0.1100 | 0.5500 | 0.9597 | 0.4564 |
| C1_2 | 2021-12-30 | renewed | 0.0500 | 0.5500 | 0.9833 | 0.2977 |
| C5 | 2021-12-30 | renewed | 0.1700 | 0.3500 | 0.9280 | 0.8247 |
| C7 | 2021-12-30 | renewed | 0.2000 | 0.5500 | 0.9267 | 0.1963 |
| C_IC3 | 2021-12-31 | renewed | 0.3200 | 0.5500 | 0.9061 | 0.5838 |
| C2 | 2022-03-31 | churned **CHURNED** | 0.3800 | 0.5500 | 0.9511 | 0.9547 |
| C6 | 2022-03-31 | renewed | 0.3500 | 0.3500 | 0.9511 | 0.1058 |
| C8 | 2022-03-31 | renewed | 0.2600 | 0.5500 | 0.9511 | 0.5712 |
| C9 | 2022-06-30 | renewed | 0.3500 | 0.5500 | 0.9364 | 0.5875 |
| C4 | 2022-09-30 | renewed | 0.3800 | 0.5500 | 0.9364 | 0.8552 |
| C1_2 | 2022-12-30 | renewed | 0.4100 | 0.5500 | 0.9556 | 0.9433 |
| C5 | 2022-12-30 | churned **CHURNED** | 0.3800 | 0.3500 | 0.9511 | 0.9650 |
| C7 | 2022-12-30 | renewed | 0.2300 | 0.5500 | 0.9364 | 0.0637 |
| C_IC3 | 2022-12-31 | renewed | 0.4100 | 0.5500 | 0.9511 | 0.8723 |
| C2_2 | 2023-03-31 | renewed | 0.0500 | 0.5500 | 0.9802 | 0.0093 |
| C6 | 2023-03-31 | renewed | 0.4100 | 0.3500 | 0.7933 | 0.5155 |
| C8 | 2023-03-31 | renewed | 0.3800 | 0.5500 | 0.9251 | 0.3785 |
| C9 | 2023-06-30 | renewed | 0.4100 | 0.5500 | 0.8739 | 0.0307 |
| C4 | 2023-09-30 | renewed | 0.4100 | 0.5500 | 0.8739 | 0.6095 |
| C1_2 | 2023-12-30 | renewed | 0.1700 | 0.5500 | 0.9326 | 0.5453 |
| C5_2 | 2023-12-30 | renewed | 0.0500 | 0.3500 | 0.9714 | 0.6875 |
| C7 | 2023-12-30 | renewed | 0.4100 | 0.5500 | 0.9026 | 0.1905 |
| C_IC3 | 2023-12-31 | renewed | 0.4100 | 0.5500 | 0.9030 | 0.7019 |
| C2_2 | 2024-03-30 | renewed | 0.2300 | 0.5500 | 0.9000 | 0.6064 |
| C6 | 2024-03-30 | churned **CHURNED** | 0.2900 | 0.3500 | 0.7926 | 0.9632 |
| C8 | 2024-03-30 | renewed | 0.1700 | 0.5500 | 0.9350 | 0.0592 |
| C9 | 2024-06-29 | renewed | 0.1700 | 0.5500 | 0.8906 | 0.0025 |
| C4 | 2024-09-29 | churned **CHURNED** | 0.3800 | 0.5500 | 0.8570 | 0.9018 |
| C1_2 | 2024-12-29 | renewed | 0.1700 | 0.5500 | 0.9235 | 0.1722 |
| C5_2 | 2024-12-29 | renewed | 0.0800 | 0.3500 | 0.9480 | 0.4422 |
| C7 | 2024-12-29 | renewed | 0.2900 | 0.5500 | 0.8895 | 0.4099 |
| C_IC3 | 2024-12-30 | renewed | 0.4100 | 0.5500 | 0.7971 | 0.3751 |
| C2_2 | 2025-03-30 | renewed | 0.3200 | 0.5500 | 0.8889 | 0.4434 |
| C8 | 2025-03-30 | renewed | 0.3200 | 0.5500 | 0.9056 | 0.4808 |

## Churn Prediction Basis Risk

At each renewal the company estimated churn risk from observable signals (rate change %, customer tenure). The SIM used its bill-shock model (actual bill amount relative to customer-specific thresholds). The gap is epistemic: in crisis years the company sees a rate % while the SIM sees the household-level financial shock — the same failure mode that surprised real suppliers in 2021-22.

- **Average absolute error:** 159.2%
- **Average signed error:** +100.2% (over-estimates vs SIM)
- **Renewal events with estimates:** 62

| Year | Renewals | Avg error (signed) | Avg abs error |
|------|----------|--------------------|---------------|
| 2016 | 3 | +87.6% | 87.6% |
| 2017 | 3 | -4.9% | 12.9% |
| 2018 | 4 | +653.4% | 669.9% |
| 2019 | 4 | +582.5% | 661.8% |
| 2020 | 10 | -22.6% | 53.8% |
| 2021 | 9 | +103.0% | 142.5% |
| 2022 | 9 | -44.1% | 44.1% |
| 2023 | 9 | +102.2% | 164.2% |
| 2024 | 9 | -10.2% | 48.5% |
| 2025 | 2 | -54.4% | 54.4% |

Positive error = company over-estimated churn vs SIM. Negative error = company under-estimated (more dangerous — expected retentions that were actually at risk).

## Active vs Passive Renewal Split (Phase 33a)

~35% of domestic/SME customers actively choose a new fixed deal at term end. ~65% roll to SVT by inaction — they are inert: low rate sensitivity, ~5% churn base. Crisis years (2022) force all renewals passive (no fixed deals available).

- **Total renewal events:** 62
- **Active renewers:** 20 (32%) — mean company estimate 24.8%, abs error 276.5%
- **Passive SVT-rollers:** 42 (68%) — mean company estimate 7.3%, abs error 103.3%

| Year | Active | Passive | Active est | Passive est | Active abs err | Passive abs err |
|------|--------|---------|-----------|------------|---------------|----------------|
| 2016 | 0 | 3 | 0.0% | 11.2% | 0.0% | 87.6% |
| 2017 | 0 | 3 | 0.0% | 9.4% | 0.0% | 12.9% |
| 2018 | 2 | 2 | 32.8% | 51.8% | 194.6% | 1145.1% |
| 2019 | 2 | 2 | 53.2% | 7.1% | 1267.4% | 56.1% |
| 2020 | 5 | 5 | 12.2% | 4.8% | 66.9% | 40.8% |
| 2021 | 3 | 6 | 38.2% | 3.4% | 287.8% | 69.8% |
| 2022 | 0 | 9 | 0.0% | 2.9% | 0.0% | 44.1% |
| 2023 | 4 | 5 | 21.2% | 4.4% | 299.7% | 55.8% |
| 2024 | 4 | 5 | 15.7% | 5.0% | 52.2% | 45.6% |
| 2025 | 0 | 2 | 0.0% | 4.7% | 0.0% | 54.4% |

Passive renewers should show lower company estimates and lower SIM churn — high abs error for passive renewers indicates the passive model needs recalibration.

## SVT Comparative Pricing — Passive Renewers (Phase 39a)

Passive renewers roll to a new fixed deal by inaction. A rate above SVT creates latent churn risk: once the customer notices they're paying more than the cap, they switch. A rate below SVT signals loyalty value — the company is rewarding inertia.

- **Passive renewal events with SVT data:** 42
- **Above SVT (at-risk):** 10 (24%)
- **Below/at SVT (protected):** 32 (76%)
- **Mean rate vs SVT premium:** -10.0%

| Year | Passive Renewals | Above SVT | Avg Premium | Avg Fixed Rate (£/MWh) | Avg SVT (£/MWh) |
|------|-----------------|-----------|-------------|----------------------|----------------|
| 2016 | 3 | 0 (0%) | -6.3% | 131.1 | 140.0 |
| 2017 | 3 | 0 (0%) | -14.3% | 119.9 | 140.0 |
| 2018 | 2 | 1 (50%) | +0.2% | 152.9 | 152.5 |
| 2019 | 2 | 0 (0%) | -29.1% | 126.5 | 178.5 |
| 2020 | 5 | 0 (0%) | -25.8% | 131.2 | 176.9 |
| 2021 | 6 | 4 (67%) | +12.8% | 209.1 | 183.8 |
| 2022 | 9 | 4 (44%) | -1.2% | 291.6 | 362.9 |
| 2023 | 5 | 0 (0%) | -32.7% | 224.7 | 364.0 |
| 2024 | 5 | 0 (0%) | -13.9% | 211.3 | 246.5 |
| 2025 | 2 | 1 (50%) | -2.9% | 241.4 | 248.6 |

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
| 2016 | 17 | 15.1% | 29.1% |
| 2017 | 14 | 16.6% | 46.6% |
| 2018 | 16 | 12.1% | 27.7% |
| 2019 | 19 | 11.0% | 37.2% |
| 2020 | 22 | 12.4% | 33.8% |
| 2021 | 17 | 14.5% | 44.5% |
| 2022 | 18 | 12.4% | 23.2% |
| 2023 | 16 | 22.3% | 40.0% |
| 2024 | 15 | 10.8% | 22.6% |
| 2025 | 2 | 33.1% | 33.1% |

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
| 2016 | 3 | 0.88× | 1.11× |
| 2017 | 3 | 0.13× | 0.27× |
| 2018 | 4 | 6.70× ⚠ | 22.57× |
| 2019 | 4 | 6.62× ⚠ | 24.89× |
| 2020 | 10 | 0.54× | 1.55× |
| 2021 | 9 | 1.42× | 4.47× |
| 2022 | 9 | 0.44× | 0.65× |
| 2023 | 9 | 1.64× | 7.88× |
| 2024 | 9 | 0.48× | 0.84× |
| 2025 | 2 | 0.54× | 0.58× |

### Demand Estimation Error (Phase AO)

Company EAC estimate error vs SIM settled consumption — year-by-year trend.
Error grows as customers acquire EVs, solar, and heat pumps that the company
cannot directly observe. The first contract term after asset acquisition has
the highest error; subsequent terms self-correct from billing history.

| Year | Customers | Mean Abs Error | Max Abs Error | Signal |
|------|-----------|----------------|---------------|--------|
| 2016 | 3 | 0.07% | 0.07% | Low — stable portfolio |
| 2017 | 9 | 0.38% | 1.69% | Low — stable portfolio |
| 2018 | 10 | 0.64% | 3.21% | Low — stable portfolio |
| 2019 | 11 | 1.00% | 5.05% | MODERATE — asset adoption visible |
| 2020 | 13 | 0.81% | 3.50% | Low — stable portfolio |
| 2021 | 11 | 1.07% | 4.24% | MODERATE — asset adoption visible |
| 2022 | 11 | 2.47% | 7.47% | MODERATE — asset adoption visible |
| 2023 | 11 | 2.35% | 8.47% | MODERATE — asset adoption visible |
| 2024 | 11 | 3.07% | 15.56% | HIGH drift — EV/asset cohort growing |
| 2025 | 2 | 1.42% | 2.07% | MODERATE — asset adoption visible |

**Trend:** demand estimation error grew from **0.07%** in 2016 to **3.07%** mean / **15.56%** max in 2024. Root cause: new asset acquisitions (Phase B life events) create a temporary estimation gap until the company observes a full billing cycle.
Portfolio action: prioritise smart meter installation for high-EAC-drift accounts — interval data eliminates estimation error at renewal.

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
| 2020 | 13 | 0.8% | 3.5% |
| 2021 | 11 | 1.1% | 4.2% |
| 2022 | 11 | 2.5% | 7.5% |
| 2023 | 11 | 2.4% | 8.5% |
| 2024 | 11 | 3.1% | 15.6% |
| 2025 | 2 | 1.4% | 2.1% |

**92** of **92** renewals used prior billing records; **0** used SIM oracle fallback (first term, no billing history).

## EAC Drift Snapshot (Phase AI)

Per-customer consumption drift from company billing history (first renewal → latest renewal).
Drift > +15%: EV/ASHP acquisition. Drift < −15%: solar installation or efficiency upgrade.

**1 significant** (≥15%) | **2 moderate** (5–15%) | **12 stable** (<5%)

| Customer | Baseline kWh | Current kWh | Drift | Likely Cause |
|----------|-------------|-------------|-------|--------------|
| C4 | 4,131 | 3,365 | -19% | likely solar installation or significant efficiency upgrade |
| C1_2 | 10,401 | 9,227 | -11% | efficiency improvement or reduced occupancy |
| C7 | 13,179 | 12,155 | -8% | efficiency improvement or reduced occupancy |

**Portfolio demand trend:** 3 customers increasing / 11 decreasing (mean drift: -3.2%)

## Company CRM — Event Log

Dated artefacts of customer lifecycle events as seen by the company layer.
Total events: **9** (6 churn, 3 acquisition)

| Date | Event | Customer | Detail |
|------|-------|----------|--------|
| 2020-06-30 | CHURN | C3 | SIM p=0.06, company est=0.05 |
| 2020-12-30 | CHURN | C1 | SIM p=0.22, company est=0.07 |
| 2020-12-30 | ACQUISITION | C1_2 | home-move-win (predecessor: C1) |
| 2022-03-31 | CHURN | C2 | SIM p=0.05, company est=0.03 |
| 2022-03-31 | ACQUISITION | C2_2 | home-move-win (predecessor: C2) |
| 2022-12-30 | CHURN | C5 | SIM p=0.05, company est=0.02 |
| 2022-12-30 | ACQUISITION | C5_2 | home-move-win (predecessor: C5) |
| 2024-03-30 | CHURN | C6 | SIM p=0.21, company est=0.25 |
| 2024-09-29 | CHURN | C4 | SIM p=0.14, company est=0.05 |

**SIM ground truth vs company CRM reconciliation (year-end snapshots):**

| Year-end | SIM churned (cumulative) | CRM active | Match |
|----------|--------------------------|------------|-------|
| 2016-12-31 | 0 accounts | 0 active | yes |
| 2017-12-31 | 0 accounts | 0 active | yes |
| 2018-12-31 | 0 accounts | 0 active | yes |
| 2019-12-31 | 0 accounts | 0 active | yes |
| 2020-12-31 | 2 accounts | 1 active | yes |
| 2021-12-31 | 2 accounts | 1 active | yes |
| 2022-12-31 | 4 accounts | 3 active | yes |
| 2023-12-31 | 4 accounts | 3 active | yes |
| 2024-12-31 | 6 accounts | 3 active | yes |
| 2025-12-31 | 6 accounts | 3 active | yes |

## Policy Costs — RO + CfD + CCL + CM + FiT + Mutualization (Phase 21a/27b/30a/31a/54)

Electricity policy costs deducted from net_margin_gbp each year. 
CfD levy was NEGATIVE in 2022 (crisis rebate from LCCC). 
CCL applies to business (SME/I&C) only — resi exempt. 
CM (Capacity Market) and FiT (Feed-in Tariff) levies apply to ALL demand including domestic.

| Year | RO levy £ | CfD levy £ | CCL £ | CM levy £ | FiT levy £ | Mutualization £ | Total policy cost £ | Note |
|------|-----------|------------|-------|-----------|-----------------|---------------------|------|---------------------|
| 2016 | 1,162 | 7 | 189 | 37 | 305 | 0 | 1,701 |  |
| 2017 | 37,159 | 2,707 | 11,165 | 1,977 | 9,940 | 0 | 62,948 |  |
| 2018 | 65,510 | 9,875 | 17,434 | 9,350 | 17,284 | 0 | 119,453 |  |
| 2019 | 164,625 | 28,353 | 42,460 | 31,969 | 44,302 | 0 | 311,709 |  |
| 2020 | 238,638 | 35,391 | 69,454 | 56,550 | 70,024 | 0 | 470,058 |  |
| 2021 | 246,702 | 15,010 | 71,336 | 49,675 | 62,836 | 41,427 | 486,987 |  |
| 2022 | 256,667 | -49,827 | 71,047 | 36,748 | 69,231 | 99,654 | 483,520 | ⬇ CfD REBATE |
| 2023 | 272,368 | 64,889 | 71,831 | 51,053 | 75,240 | 13,776 | 549,157 |  |
| 2024 | 308,162 | 110,127 | 72,944 | 68,826 | 82,707 | 2,002 | 644,768 |  |
| 2025 | 136,010 | 47,047 | 31,221 | 31,094 | 36,227 | 855 | 282,455 |  |
| **Total** | **1,727,002** | **263,580** | **459,082** | **337,279** | **468,096** | **157,716** | **3,412,755** | |

Total policy cost: £3,412,755 across all years. Net margin is after deducting this. Revenue side: tariff pass-through at term-start year's levy rate — basis risk arises when cross-year terms meet a different actual levy (notably 2022 CfD rebate).

## Network Charges — DUoS + TNUoS (Phase 29a)

Electricity network charges deducted from net_margin_gbp each year. 
Resi/SME: combined DUoS + TNUoS unit rate (largest single non-commodity cost). 
I&C HV: DUoS only (Triad TNUoS is an annual lump tracked in the Triad section).

| Year | Network cost £ | Note |
|------|----------------|------|
| 2016 | 3,202 |  |
| 2017 | 26,176 |  |
| 2018 | 38,555 |  |
| 2019 | 88,387 |  |
| 2020 | 124,589 |  |
| 2021 | 123,772 |  |
| 2022 | 134,698 | BSUoS 100% demand-side from Apr 2022 |
| 2023 | 140,894 | RIIO-ED2 from Apr 2023 |
| 2024 | 144,687 |  |
| 2025 | 61,977 |  |
| **Total** | **886,938** | |

Total network cost: £886,938 across all years. Pass-through: tariff unit rate includes network cost at term-start year's rate; settlement deducts it — basis risk near-zero for annual contracts.

## Gas Policy Costs and Network Charges (Phase 30b)

Gas CCL: non-domestic only (domestic gas exempt). Gas network (GDN + NTS): all on unit rate.
GGL (Green Gas Levy): per-meter, from Nov 2021; tiny in £/MWh terms.

| Year | Gas Policy (CCL + GGL) £ | Gas Network £ | Total Gas Non-Commodity £ |
|------|--------------------------|---------------|--------------------------|
| 2016 | 0 | 479 | 479 |
| 2017 | 0 | 898 | 898 |
| 2018 | 0 | 905 | 905 |
| 2019 | 15,155 | 50,388 | 65,543 |
| 2020 | 19,468 | 47,213 | 66,681 |
| 2021 | 22,472 | 50,301 | 72,773 |
| 2022 | 27,045 | 54,433 | 81,478 |
| 2023 | 32,229 | 79,700 | 111,929 |
| 2024 | 37,494 | 76,429 | 113,923 |
| 2025 | 17,243 | 31,816 | 49,059 |
| **Total** | **171,106** | **392,562** | **563,668** |

Gas policy pass-through in tariff unit rate (CCL + GGL at term start); gas network pass-through likewise. Net basis risk near-zero for annual contracts.


## Gas Book P&L — Year by Year (Phase 32a)

Revenue = billing at fixed tariff unit rate. Wholesale = hedged + unhedged NBP cost.
Policy = gas CCL + GGL. Network = GDN + NTS. Net = gross − policy − network − capital.

| Year | Revenue £ | Wholesale £ | Gross £ | Policy £ | Network £ | Capital £ | Net £ | Net % |
|------|-----------|-------------|---------|----------|-----------|-----------|-------|-------|
| 2016 | 1,388 | 578 | 811 | 0 | 479 | 7 | 297 | +21.4% |
| 2017 | 2,660 | 1,231 | 1,430 | 0 | 898 | 15 | 463 | +17.4% |
| 2018 | 3,114 | 1,751 | 1,363 | 0 | 905 | 21 | 375 | +12.0% |
| 2019 | 137,766 | 61,712 | 76,054 | 15,155 | 50,388 | 21 | 9,754 | +7.1% |
| 2020 | 121,120 | 43,940 | 77,180 | 19,468 | 47,213 | 10 | 9,853 | +8.1% |
| 2021 | 297,399 | 214,790 | 82,609 | 22,472 | 50,301 | 13 | 8,285 | +2.8% |
| 2022 | 588,330 | 497,974 | 90,356 | 27,045 | 54,433 | 34 | 2,833 | +0.5% |
| 2023 | 297,198 | 176,258 | 120,940 | 32,229 | 79,700 | 52 | 7,362 | +2.5% |
| 2024 | 270,491 | 146,077 | 124,414 | 37,494 | 76,429 | 23 | 9,082 | +3.4% |
| 2025 | 132,454 | 78,945 | 53,509 | 17,243 | 31,816 | 0 | 3,788 | +2.9% |
| **Total** | **1,851,920** | **1,223,256** | **628,664** | **171,106** | **392,562** | **198** | **52,091** | **+2.8%** |

Gas book net margin positive over the simulation period. Network charges (GDN + NTS, £9–18/MWh) dominate the gas non-commodity cost stack.

## Solvency Signal — Net Assets per Customer (Phase 21b/55)

Treasury ÷ active accounts. Ofgem MCR floor: £130/dual-fuel account.
Watch < 2×, STRESS < 1× (account balance below regulatory floor).

| Year | Treasury £ | Accounts | Net Assets/Account £ | Solvency Ratio | Status |
|------|-----------|----------|----------------------|----------------|--------|
| 2016 | 2,467,424 | 9 | 274,158 | 2108.91× | OK |
| 2017 | 2,497,718 | 10 | 249,772 | 1921.32× | OK |
| 2018 | 2,486,407 | 11 | 226,037 | 1738.75× | OK |
| 2019 | 2,606,406 | 12 | 217,201 | 1670.77× | OK |
| 2020 | 2,914,253 | 14 | 208,161 | 1601.24× | OK |
| 2021 | 2,943,330 | 12 | 245,277 | 1886.75× | OK |
| 2022 | 3,135,961 | 14 | 223,997 | 1723.06× | OK |
| 2023 | 3,336,256 | 12 | 278,021 | 2138.63× | OK |
| 2024 | 3,710,669 | 12 | 309,222 | 2378.63× | OK |
| 2025 | 3,760,599 | 10 | 376,060 | 2892.77× | OK |

End-state (2025): **£376,060/account** across 10 billing accounts — OK.

## BSC Credit Cover — Working Capital Requirement (Phase 53)

Elexon BSC credit cover: max daily electricity wholesale charge × 28-day window × 1.2 buffer.
Below 5× coverage ratio (treasury / credit cover) flags working capital stress.

| Year | Peak Daily £ | Credit Cover £ | Treasury £ | Coverage Ratio | Status |
|------|-------------|---------------|-----------|----------------|--------|
| 2016 | 25 | 30 | 2,467,424 | 81947.0× | OK |
| 2017 | 466 | 559 | 2,497,718 | 4467.7× | OK |
| 2018 | 849 | 1,019 | 2,486,407 | 2439.7× | OK |
| 2019 | 1,543 | 1,851 | 2,606,406 | 1408.0× | OK |
| 2020 | 1,979 | 2,375 | 2,914,253 | 1227.2× | OK |
| 2021 | 4,342 | 5,211 | 2,943,330 | 564.9× | OK |
| 2022 | 8,509 | 10,211 | 3,135,961 | 307.1× | OK |
| 2023 | 5,630 | 6,755 | 3,336,256 | 493.9× | OK |
| 2024 | 2,667 | 3,200 | 3,710,669 | 1159.6× | OK |
| 2025 | 3,902 | 4,682 | 3,760,599 | 803.1× | OK |




## Time-of-Use Tariff Utilization (C7-C9 HH Customers)

Peak windows: 07:00–11:00 and 16:00–20:00 weekdays (periods 15-22, 33-40).
Peak rate = 1.5× flat; off-peak = 0.786× flat (revenue-neutral at 30/70 split).
ToU Premium: actual revenue vs flat-rate equivalent — positive when actual peak % > 30% design.

| Customer | Total kWh | Peak kWh | Peak % | Peak Revenue | Off-peak Revenue | Avg Peak Rate | Avg Off-peak Rate | ToU Premium |
|----------|-----------|----------|--------|-------------|-----------------|--------------|------------------|-------------|
| C7 | 120,839 | 36,249 | 30.0% | £9,524.77 | £12,268.08 | £262.76/MWh | £145.03/MWh | +3.0% |
| C8 | 106,722 | 43,948 | 41.2% | £11,986.02 | £9,702.76 | £272.73/MWh | £154.57/MWh | +11.8% |
| C9 | 109,387 | 43,689 | 39.9% | £10,933.12 | £9,310.54 | £250.25/MWh | £141.72/MWh | +10.9% |

Total HH revenue: £63,725.29 vs flat equivalent £58,821.31 (+8.3% ToU premium)

## Bill Shock Summary (2016-2025)

Month-on-month billing increase ≥20%. Bill shocks elevate SIM churn probability
via the bill-shock history model. Crisis years (2021-22) see the largest spikes.

| Year | Events | Max Spike | Worst Customer |
|------|--------|-----------|----------------|
| 2016 | 31 | 100% | C8 (2016-10-31) |
| 2017 | 50 | 81% | C8 (2017-11-30) |
| 2018 | 60 | 85% | C4g (2018-10-31) |
| 2019 | 66 | 130% | C_IC1 (2019-03-31) |
| 2020 | 53 | 118% | C_IC2 (2020-03-31) |
| 2021 | 52 | 1207% | C1_2 (2021-01-31) |
| 2022 | 76 | 1735% | C2_2 (2022-04-30) |
| 2023 | 53 | 2059% | C5_2 (2023-01-31) |
| 2024 | 45 | 107% | C_IC2 (2024-07-31) |
| 2025 | 25 | 80% | C1_2 (2025-06-07) |

Total: **511** bill shock events across 10 years

**Top 10 worst single-period bill spikes:**

| Date | Customer | Spike | Eventually Churned? |
|------|----------|-------|---------------------|
| 2023-01-31 | C5_2 | +2059% | no |
| 2022-04-30 | C2_2 | +1735% | no |
| 2021-01-31 | C1_2 | +1207% | no |
| 2022-01-31 | C1_2 | +141% | no |
| 2022-10-31 | C4g | +134% | no |
| 2019-03-31 | C_IC1 | +130% | no |
| 2022-01-31 | C5 | +128% | yes |
| 2020-03-31 | C_IC2 | +118% | no |
| 2021-10-31 | C4g | +113% | no |
| 2022-01-31 | C_IC3 | +108% | no |

## Gas Renewal Pressure (Dual-Fuel Portfolio)

Company gas churn estimates at each gas leg renewal (Phase 14b).
Threshold for elevated risk: >20% company gas churn estimate.

| Year | Renewals | Mean Est | Max Est | Elevated Risk |
|------|----------|----------|---------|---------------|
| 2016 | 1 | 11% | 11% | 0 |
| 2017 | 4 | 16% | 23% | 2 ⚠ |
| 2018 | 4 | 17% | 23% | 2 ⚠ |
| 2019 | 4 | 0% | 0% | 0 |
| 2020 | 4 | 5% | 21% | 1 ⚠ |
| 2021 | 3 | 69% | 95% | 3 ⚠ |
| 2022 | 2 | 48% | 95% | 1 ⚠ |
| 2023 | 2 | 0% | 0% | 0 |
| 2024 | 1 | 1% | 1% | 0 |

**Top elevated gas renewals (>20% estimated churn):**

| Date | Customer | Old Rate (£/MWh) | New Rate (£/MWh) | Est Churn |
|------|----------|-----------------|-----------------|-----------|
| 2021-12-31 | C_IC3g | £19.4 | £125.9 (+550%) | 95% |
| 2022-09-30 | C4g | £35.0 | £95.0 (+171%) | 95% |
| 2021-09-30 | C4g | £16.1 | £35.0 (+118%) | 74% |
| 2021-03-31 | C2g | £21.7 | £35.0 (+62%) | 40% |
| 2018-10-01 | C4g | £26.1 | £33.6 (+29%) | 23% |

## Retention Strategy P&L

### Aggregate (2016-2025)

| Metric | Value |
|--------|-------|
| Offers made | 14 |
| Retained | 14 (100%) |
| Churned despite offer | 0 |
| Total offer cost (foregone margin) | £150,009.81 |
| Margin saved (retained customers' terms) | £1,207,026.38 |
| Wasted offer cost (churned anyway) | £0.00 |
| **Net ROI of retention strategy** | **£1,057,016.57** |
| Acquisition cost avoided (retained customers) | £2,600.00 |
| **Full economic ROI (margin + acq savings)** | **£1,059,616.57** |

Missed opportunities (churns with no offer): **6** (£6,623.39 expected margin lost without offer)
- **Below threshold** (churn estimate under 30%): 6 (£6,623.39 margin lost) — Phase 13c bill burden signal reduces this for high-spend SME customers

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2017 | 2 | 2 | £71.20 | £1362.45 | £1291.25 | £0.00 |
| 2018 | 3 | 3 | £24267.43 | £164429.07 | £140161.64 | £0.00 |
| 2019 | 2 | 2 | £32311.18 | £296612.44 | £264301.26 | £0.00 |
| 2020 | 0 | 0 | £0.00 | £0.00 | £0.00 | £1000.56 |
| 2021 | 4 | 4 | £65570.96 | £413560.19 | £347989.23 | £0.00 |
| 2022 | 2 | 2 | £27559.58 | £327840.37 | £300280.79 | £2289.28 |
| 2023 | 1 | 1 | £229.47 | £3221.88 | £2992.40 | £0.00 |
| 2024 | 0 | 0 | £0.00 | £0.00 | £0.00 | £3333.54 |

### Per-Offer Detail

| Date | Customer | Est. churn | Discount | Offer Cost | Expected Margin | Acq Saved | Net | Outcome |
|------|----------|-----------|---------|-----------|----------------|-----------|-----|---------|
| 2017-04-01 | C8 | 0.34 | 3% | £46.02 | £867.92 | £150 | £821.90 | retained |
| 2017-07-01 | C3 | 0.39 | 3% | £25.18 | £494.53 | £150 | £469.35 | retained |
| 2018-01-31 | C_IC1 | 0.95 | 8% | £24227.89 | £163704.65 | £150 | £139476.77 | retained |
| 2018-10-01 | C4 | 0.45 | 3% | £18.42 | £345.06 | £150 | £326.64 | retained |
| 2018-12-31 | C1 | 0.36 | 3% | £21.13 | £379.36 | £150 | £358.23 | retained |
| 2019-01-31 | C_IC2 | 0.95 | 8% | £14841.81 | £101641.16 | £150 | £86799.35 | retained |
| 2019-03-02 | C_IC1 | 0.66 | 5% | £17469.37 | £194971.28 | £150 | £177501.91 | retained |
| 2021-03-31 | C_IC2 | 0.39 | 3% | £5310.58 | £91314.94 | £150 | £86004.36 | retained |
| 2021-04-30 | C_IC1 | 0.38 | 3% | £8446.52 | £158250.95 | £150 | £149804.43 | retained |
| 2021-12-30 | C5 | 0.49 | 3% | £198.22 | £2475.25 | £400 | £2277.03 | retained |
| 2021-12-31 | C_IC3 | 0.54 | 5% | £51615.63 | £161519.05 | £150 | £109903.42 | retained |
| 2022-04-30 | C_IC2 | 0.42 | 3% | £9417.62 | £96241.44 | £150 | £86823.82 | retained |
| 2022-05-30 | C_IC1 | 0.42 | 3% | £18141.96 | £231598.92 | £150 | £213456.97 | retained |
| 2023-03-31 | C6 | 0.39 | 3% | £229.47 | £3221.88 | £400 | £2992.40 | retained |

## Retention Durability

Post-retention survival: how long did retained customers stay before churning or reaching the simulation end?

| Customer | First retained | End of tenure | Post-retention months | Outcome |
|----------|---------------|--------------|----------------------|---------|
| C8 | 2017-04-01 | (window end) | 105 | active |
| C3 | 2017-07-01 | 2020-06-30 | 36 | churned |
| C_IC1 | 2018-01-31 | (window end) | 95 | active |
| C4 | 2018-10-01 | 2024-09-29 | 72 | churned |
| C1 | 2018-12-31 | 2020-12-30 | 24 | churned |
| C_IC2 | 2019-01-31 | (window end) | 83 | active |
| C5 | 2021-12-30 | 2022-12-30 | 12 | churned |
| C_IC3 | 2021-12-31 | (window end) | 48 | active |
| C6 | 2023-03-31 | 2024-03-30 | 12 | churned |

**Eventually churned (5/9)**: C3, C4, C1, C5, C6 — avg 31 months post-retention before final churn.
**Still active (4/9)**: C8, C_IC1, C_IC2, C_IC3 — survived to simulation end.

## Enterprise Value Analysis (Phase 22a)

**Full-history EV:** £8,826,938.57 — anchored to all 10 years including crisis losses
**3yr-trailing EV:** £729,896.20 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

The gap between the two is the weight of unrecovered crisis losses in the CLV anchor.
When trailing EV > full-history EV, the company's recent performance is better than its
cumulative history suggests — a recovery signal.

**Portfolio net margin by year:**

| Year | Net margin |
|------|----------:|
| 2016 | £1,178.25 |
| 2017 | £30,566.05 |
| 2018 | £99,706.17 |
| 2019 | £227,872.41 |
| 2020 | £122,216.90 |
| 2021 | £67,928.67 |
| 2022 | £300,205.86 |
| 2023 | £147,353.65 | ← trailing
| 2024 | £330,160.28 | ← trailing
| 2025 | £118,069.43 | ← trailing

**CLV by billing account:**

| Account | Full-history CLV | 3yr-trailing CLV |
|---------|----------------:|----------------:|
| C1 | £5,484.28 | — |
| C1_2 | — | £376.92 |
| C2 | £7,339.85 | — |
| C2_2 | — | £1,270.20 |
| C3 | £6,823.79 | — |
| C4 | £3,921.60 | £-1,103.78 |
| C5 | £14,409.65 | — |
| C5_2 | — | £248.19 |
| C6 | £22,350.07 | £3,165.49 |
| C7 | £9,218.57 | £30.99 |
| C8 | £10,789.22 | £314.87 |
| C9 | £12,017.28 | £1,202.14 |
| C_IC1 | £1,979,417.19 | £423,429.59 |
| C_IC2 | £1,141,168.85 | £224,044.08 |
| C_IC3 | £3,764,767.63 | £66,391.93 |
| C_IC4 | £1,834,396.57 | £10,525.58 |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C1_2 | C2 | C2_2 | C3 | C4 | C5 | C5_2 | C6 | C7 | C8 | C9 | C_IC1 | C_IC2 | C_IC3 | C_IC4 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £6,228.45 | — | — | — | — | — | £14,109.80 | — | — | £10,200.00 | — | — | — | — | — | — |
| 2017 | £5,470.70 | — | £10,821.00 | — | £9,473.64 | £8,371.99 | £11,735.66 | — | £23,920.37 | £8,667.92 | £13,323.56 | £10,874.42 | — | — | — | — |
| 2018 | £5,697.08 | — | £9,411.38 | — | £8,891.54 | £7,799.21 | £12,331.60 | — | £20,109.02 | £8,563.83 | £11,409.42 | £10,798.47 | £2,809,761.35 | — | — | — |
| 2019 | £6,046.01 | — | £9,483.53 | — | £9,318.53 | £7,754.22 | £13,910.73 | — | £20,752.15 | £9,842.14 | £11,020.84 | £10,646.87 | £2,649,003.90 | £1,764,083.33 | — | — |
| 2020 | £6,293.16 | £15.96 | £9,319.76 | — | £8,260.26 | £8,236.31 | £12,918.81 | — | £18,929.57 | £9,705.30 | £11,800.14 | £10,507.78 | £1,826,772.55 | £816,663.61 | £2,894,255.48 | £1,476,603.82 |
| 2021 | £5,295.46 | £1,215.38 | £7,182.87 | — | £6,963.40 | £5,891.46 | £12,404.05 | — | £21,264.35 | £8,502.43 | £11,083.85 | £11,184.62 | £1,613,852.65 | £946,833.37 | £2,594,930.48 | £1,678,673.09 |
| 2022 | £5,760.93 | £2,223.35 | £6,645.17 | £1,068.69 | £7,598.89 | £4,129.23 | £11,532.92 | £7.16 | £19,748.20 | £6,091.12 | £11,370.96 | £10,023.90 | £1,679,089.32 | £1,056,515.43 | £2,440,360.88 | £1,466,766.77 |
| 2023 | £6,142.89 | £1,992.91 | £6,136.90 | £3,717.08 | £6,214.40 | £2,912.30 | £10,629.41 | £912.14 | £19,004.78 | £6,681.84 | £8,929.80 | £9,648.06 | £1,543,308.03 | £824,338.30 | £2,389,942.94 | £1,408,103.70 |
| 2024 | £4,633.75 | £3,099.46 | £5,088.64 | £4,144.53 | £5,683.10 | £3,419.27 | £11,328.55 | £3,428.63 | £16,245.83 | £8,694.38 | £9,152.68 | £8,883.63 | £1,494,574.75 | £610,332.16 | £2,326,510.46 | £1,303,777.60 |
| 2025 | £4,338.09 | £3,856.07 | £5,911.85 | £3,493.53 | £5,747.90 | £2,772.74 | £9,675.09 | £4,275.95 | £15,200.05 | £7,594.48 | £7,947.09 | £8,801.76 | £1,355,811.81 | £849,459.41 | £2,158,651.79 | £1,349,750.16 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £4,370.48, range £54.46–£26,408.27.

- C1: cost to serve £344.89, net margin after CTS £1,948.84
- C1_2: cost to serve £476.66, net margin after CTS £5,179.59
- C1g: cost to serve £54.46, net margin after CTS £1,300.78
- C2: cost to serve £432.22, net margin after CTS £2,978.09
- C2_2: cost to serve £381.56, net margin after CTS £5,113.51
- C2g: cost to serve £83.87, net margin after CTS £1,935.34
- C3: cost to serve £292.52, net margin after CTS £2,096.31
- C3g: cost to serve £58.25, net margin after CTS £1,240.28
- C4: cost to serve £565.38, net margin after CTS £2,749.41
- C4g: cost to serve £216.57, net margin after CTS £1,127.40
- C5: cost to serve £1,056.93, net margin after CTS £10,944.62
- C5_2: cost to serve £416.37, net margin after CTS £5,914.60
- C6: cost to serve £1,349.00, net margin after CTS £21,086.52
- C7: cost to serve £954.99, net margin after CTS £9,860.29
- C8: cost to serve £939.21, net margin after CTS £11,529.68
- C9: cost to serve £896.59, net margin after CTS £11,811.56
- C_IC1: cost to serve £19,836.15, net margin after CTS £1,854,831.25
- C_IC2: cost to serve £11,344.53, net margin after CTS £898,484.24
- C_IC3: cost to serve £26,408.27, net margin after CTS £1,807,029.46
- C_IC3g: cost to serve £9,229.97, net margin after CTS £613,417.06
- C_IC4: cost to serve £16,441.72, net margin after CTS £1,090,243.56


## Margin Recovery Surcharges (Phase 16c + 19a)

Company applied 29 recovery surcharge(s) at renewal based on prior-term losses (3 gas). Avg surcharge: 14.5%.

| Customer | Commodity | Term start | Prior margin | Prior revenue | Surcharge | Rate before | Rate after |
|----------|-----------|------------|-------------|--------------|-----------|------------|-----------|
| C_IC1 | electricity | 2018-01-31 | £-5,651.81 | £10,420.08 | +20.0% | £112.24/MWh | £152.31/MWh |
| C5 | electricity | 2018-12-31 | £-204.31 | £2,322.51 | +3.8% | £148.68/MWh | £153.39/MWh |
| C_IC2 | electricity | 2019-01-31 | £-3,283.71 | £6,187.80 | +20.0% | £134.57/MWh | £185.71/MWh |
| C_IC1 | electricity | 2019-03-02 | £-7,215.97 | £10,069.00 | +20.0% | £128.22/MWh | £175.80/MWh |
| C_IC2 | electricity | 2020-03-01 | £-3,915.21 | £3,421.95 | +20.0% | £92.92/MWh | £128.22/MWh |
| C_IC1 | electricity | 2020-03-31 | £-8,072.70 | £6,326.95 | +20.0% | £91.12/MWh | £103.88/MWh |
| C_IC2 | electricity | 2021-03-31 | £-4,097.33 | £5,726.15 | +20.0% | £138.90/MWh | £177.17/MWh |
| C_IC1 | electricity | 2021-04-30 | £-7,770.53 | £14,511.74 | +20.0% | £113.97/MWh | £141.63/MWh |
| C4g | gas | 2021-09-30 | £-75.14 | £687.61 | +5.9% | £53.99/MWh | £57.53/MWh |
| C1_2 | electricity | 2021-12-30 | £-149.26 | £1,494.88 | +5.0% | £311.83/MWh | £332.49/MWh |
| C5 | electricity | 2021-12-30 | £-318.19 | £2,722.44 | +6.7% | £311.83/MWh | £353.26/MWh |
| C7 | electricity | 2021-12-30 | £-109.60 | £2,000.74 | +0.5% | £311.83/MWh | £335.19/MWh |
| C_IC3 | electricity | 2021-12-31 | £-26,309.16 | £444,393.58 | +0.9% | £224.03/MWh | £260.00/MWh |
| C_IC2 | electricity | 2022-04-30 | £-2,287.21 | £17,661.75 | +8.0% | £269.81/MWh | £317.95/MWh |
| C_IC1 | electricity | 2022-05-30 | £-6,202.10 | £22,384.38 | +20.0% | £239.42/MWh | £308.66/MWh |
| C4 | electricity | 2022-09-30 | £-220.41 | £906.59 | +19.3% | £404.86/MWh | £484.82/MWh |
| C4g | gas | 2022-09-30 | £-901.21 | £1,040.11 | +20.0% | £183.79/MWh | £250.54/MWh |
| C7 | electricity | 2022-12-30 | £-1,829.78 | £2,404.50 | +20.0% | £266.73/MWh | £359.29/MWh |
| C8 | electricity | 2023-03-31 | £-481.87 | £3,898.74 | +7.4% | £319.17/MWh | £343.81/MWh |
| C_IC2 | electricity | 2023-05-30 | £-4,337.22 | £7,055.33 | +20.0% | £171.46/MWh | £236.61/MWh |
| C_IC1 | electricity | 2023-06-29 | £-8,734.92 | £17,979.18 | +20.0% | £163.19/MWh | £220.46/MWh |
| C4 | electricity | 2023-09-30 | £-277.33 | £1,324.46 | +15.9% | £216.77/MWh | £249.30/MWh |
| C4g | gas | 2023-09-30 | £-1,950.48 | £2,732.11 | +20.0% | £47.83/MWh | £66.00/MWh |
| C1_2 | electricity | 2023-12-30 | £-589.08 | £2,728.19 | +16.6% | £242.22/MWh | £268.29/MWh |
| C5_2 | electricity | 2023-12-30 | £-1,113.67 | £5,051.61 | +17.1% | £242.22/MWh | £269.33/MWh |
| C7 | electricity | 2023-12-30 | £-445.92 | £3,990.91 | +6.2% | £242.22/MWh | £244.32/MWh |
| C_IC3 | electricity | 2023-12-31 | £-108,689.56 | £987,521.89 | +6.0% | £118.95/MWh | £119.79/MWh |
| C_IC2 | electricity | 2024-06-28 | £-5,972.33 | £7,659.10 | +20.0% | £148.64/MWh | £205.12/MWh |
| C_IC1 | electricity | 2024-07-28 | £-10,717.78 | £14,454.77 | +20.0% | £154.38/MWh | £213.04/MWh |


## Flexibility Revenue — DSR & Capacity Market (Phase AG/NX)

Two flexibility revenue streams: residential DSR (EV/ASHP/battery via FlexibilityRevenueBook) and I&C demand response (interruptible process load via ICFlexibilityRevenueBook).
- **Capacity Market (CM):** T-4 auction clearing prices (£6.44–£22.50/kW/yr by year, NESO); operational since 2014.
- **Demand Flexibility Service (DFS):** launched October 2022; £4.5/MWh × 20 events/yr.
- **I&C DSR aggregator fee:** 20% of gross CM/DFS revenue.

**Total 2016–2025:** £0.00  (Residential: £0.00 | I&C: £21,381.06)

### I&C Demand Response Revenue

| Year | Net Revenue | Enrolled | Flex kW |
|------|-------------|----------|---------|
| 2016 | £2,109.00 | 4 | 176 kW |
| 2017 | £1,406.00 | 4 | 176 kW |
| 2018 | £2,727.64 | 4 | 176 kW |
| 2019 | £2,530.80 | 4 | 176 kW |
| 2020 | £3,163.50 | 4 | 176 kW |
| 2021 | £1,181.04 | 4 | 176 kW |
| 2022 | £918.12 | 4 | 176 kW |
| 2023 | £2,258.04 | 4 | 176 kW |
| 2024 | £2,543.46 | 4 | 176 kW |
| 2025 | £2,543.46 | 4 | 176 kW |

## Portfolio Intelligence Pack (Phase AH)

Board-level synthesis of CRM and flexibility intelligence derived from observable operational data.

### 1. Retention Intelligence

- **Retention offers made:** 14
- **Offer acceptance rate:** 100% (14 retained / 0 churned despite offer)
- **Estimated margin protected:** £1,207,026.38
- **No-offer churns:** 6 total (0 blind miss / 0 deliberate pass)
- **Retention coverage rate:** 70% of at-risk renewals received an offer

### 2. Flexibility Revenue Intelligence

- No flexibility revenue data available.

### 3. Churn Pattern Analysis

- **Total lifetime churn events:** 6
- **Peak churn year:** 2020 (2 events)
- **Net book movement:** 3 acquisitions − 6 churns = -3
- **Portfolio trend:** shrinking

### 4. Board Recommendations

1. **Crisis-year churn:** 2 churn events in 2021–2022. Maintain minimum hedge floor pre-crisis to preserve pricing stability and limit bill-shock churn.

## CRM Intelligence: Risk Triage (Final Year)

Latest renewal record per account. Risk bands: CRITICAL>=50% | HIGH>=30% | MEDIUM>=15% | LOW<15%.

| Account | Seg | Risk Band | Sim Churn | Co. Est. | Rate vs SVT | Lifetime Margin |
|---------|-----|-----------|-----------|----------|-------------|-----------------|
| C1 | resi | MEDIUM | 22% | 7% | -23.0% [competitive] | £1,948.84 |
| C6 | SME | MEDIUM | 21% | 25% | -24.7% [competitive] | £21,086.52 |
| C_IC3 | I&C | MEDIUM | 20% | 13% | -53.5% [competitive] | £1,807,029.46 |
| C4 | resi | LOW | 14% | 5% | -9.0% | £2,749.41 |
| C2_2 | resi | LOW | 11% | 5% | +17.8% [overpriced] | £5,113.51 |
| C7 | resi | LOW | 11% | 5% | -14.3% | £9,860.29 |
| C9 | resi | LOW | 11% | 5% | -14.3% | £11,811.56 |
| C8 | resi | LOW | 9% | 5% | -23.6% [competitive] | £11,529.68 |
| C1_2 | resi | LOW | 8% | 14% | +3.3% | £5,179.59 |
| C3 | resi | LOW | 6% | 5% | -39.0% [competitive] | £2,096.31 |
| C5_2 | SME | LOW | 5% | 5% | -5.5% | £5,914.60 |
| C5 | SME | LOW | 5% | 2% | -45.8% [competitive] | £10,944.62 |
| C2 | resi | LOW | 5% | 3% | +46.6% [overpriced] | £2,978.09 |
| C_IC1 | I&C | LOW | 4% | 95% | -0.1% | £1,854,831.25 |
| C_IC2 | I&C | LOW | 4% | 95% | +12.4% [overpriced] | £898,484.24 |

**Risk Band Summary (latest renewal):**
- CRITICAL (>=50%): 0 accounts
- HIGH (>=30%): 0 accounts
- MEDIUM (>=15%): 3 accounts
- LOW (<15%): 12 accounts
- Lifetime margin at risk (CRITICAL+HIGH): £0.00

## Churn Root Cause Attribution

Per-churned-account analysis: pricing journey, rate-vs-SVT positioning, and company vs SIM churn estimate at the point of departure.

| Account | Seg | Churn Date | Tenure | Last Rate Shock | Rate vs SVT | Sim Risk | Co. Est. | Margin Lost |
|---------|-----|------------|--------|-----------------|-------------|----------|----------|-------------|
| C3 | resi | 2020-06-30 | 4.0yr | -4.3% | -39.0% | 6% | 5% | £2,096.31 |
| C1 | resi | 2020-12-30 | 5.0yr | -0.8% | -23.0% | 22% | 7% | £1,948.84 |
| C2 | resi | 2022-03-31 | 6.0yr | +11.9% | +46.6% | 5% | 3% | £2,978.09 |
| C5 | SME | 2022-12-30 | 7.0yr | +5.4% | -45.8% | 5% | 2% | £10,944.62 |
| C6 | SME | 2024-03-30 | 8.0yr | -0.7% | -24.7% | 21% | 25% | £21,086.52 |
| C4 | resi | 2024-09-29 | 8.0yr | +3.8% | -9.0% | 14% | 5% | £2,749.41 |

**Root Cause Summary:**
- Total churned accounts: 6
- Lifetime margin lost: £41,803.80
- Average tenure at departure: 6.3 years
- Company-warned churns (co. est. >=20%): 1 -- C6
- Crisis-era churns (2021-22): 2 -- absolute crisis price level, not rate-change delta, was the driver
- Overpriced vs SVT at departure: 1 account(s) -- rate shock risk was observable but unactioned

## Counterfactual Retention Value

What would company-initiated retention offers have been worth for the 6 accounts that churned without an offer? Calibrated from 14 actual offers (observed retention rate 100%).

| Account | Seg | Churn Date | Co. Est. | Term Margin | Disc Rate | Retention Cost | CF Net Benefit | Assessment |
|---------|-----|------------|----------|-------------|-----------|----------------|----------------|------------|
| C3 | resi | 2020-06-30 | 5% | £585.39 | 5% | £29.27 | £556.12 | MISSED OPP. |
| C1 | resi | 2020-12-30 | 7% | £415.17 | 5% | £20.76 | £394.42 | MISSED OPP. |
| C2 | resi | 2022-03-31 | 3% | £236.63 | 5% | £11.83 | £224.80 | MISSED OPP. |
| C5 | SME | 2022-12-30 | 2% | £2,052.65 | 8% | £164.21 | £1,888.44 | MISSED OPP. |
| C6 | SME | 2024-03-30 | 25% | £2,864.67 | 8% | £229.17 | £2,635.50 | MISSED OPP. |
| C4 | resi | 2024-09-29 | 5% | £468.87 | 5% | £23.44 | £445.43 | MISSED OPP. |

**Counterfactual Summary:**
- No-offer churns assessed: 6
- Correct no-offer (net-neg ETM): 0
- Missed opportunities (positive ETM, below detection): 6
- Total term margin foregone: £6,623.39
- Total retention cost (counterfactual): £478.69
- Net counterfactual benefit: £6,144.70 (at 100% retention probability)
- Root cause: company churn detection below threshold for all missed cases -- churn model underestimated bill-shock risk

## Pricing Basis Risk Attribution

Forward curve accuracy at each contract term. tariff_error_pct = (company_fwd - sim_fwd) / sim_fwd: positive = company over-estimated costs (higher than market); negative = company under-estimated (margin-at-risk).
Portfolio-wide mean error: +6.0%

| Year | Contracts | Mean Error | Max Abs | Over-priced | Under-priced | Assessment |
|------|-----------|------------|---------|-------------|--------------|------------|
| 2016 | 17 | +8.9% | 29.1% | 9 | 4 | moderate over |
| 2017 | 14 | +5.4% | 46.6% | 8 | 5 | moderate over |
| 2018 | 16 | -2.9% | 27.7% | 6 | 8 | on target |
| 2019 | 19 | +8.3% | 37.2% | 9 | 3 | moderate over |
| 2020 | 22 | -0.9% | 33.8% | 9 | 8 | on target |
| 2021 | 17 | +8.5% | 44.5% | 6 | 3 | moderate over |
| 2022 | 18 | -3.3% | 23.2% | 7 | 6 | on target |
| 2023 | 16 | +20.9% | 40.0% | 11 | 1 | HIGH OVER-PRICE |
| 2024 | 15 | +8.6% | 22.6% | 9 | 1 | moderate over |
| 2025 | 2 | +33.1% | 33.1% | 2 | 0 | HIGH OVER-PRICE |

**Basis Risk Summary:**
- Portfolio mean tariff error: +6.0%
- Worst over-pricing year: 2025 (+33.1%) -- company forward curve above settled market
- Post-crisis over-pricing years (2023, 2025): company locked in expensive crisis-era forwards after prices normalised -- mechanism that eroded real suppliers' margins 2022-24

## BSC Settlement Exposure

Elexon's Balancing and Settlement Code (BSC) requires suppliers to post credit cover to fund potential imbalance charges. Credit requirements track portfolio size and wholesale price levels. Peak daily settlement is the largest single-day settlement amount seen in that year.

| Year | BSC Credit Required | Peak Daily | % of Revenue |
|------|---------------------|------------|--------------|
| 2016 | £30 | £25 | 0.29% |
| 2017 | £559 | £466 | 0.24% |
| 2018 | £1,019 | £849 | 0.23% |
| 2019 | £1,851 | £1,543 | 0.15% |
| 2020 | £2,375 | £1,979 | 0.19% |
| 2021 | £5,211 | £4,342 | 0.30% |
| 2022 | £10,211 | £8,509 | 0.30% |
| 2023 | £6,755 | £5,630 | 0.26% |
| 2024 | £3,200 | £2,667 | 0.15% |
| 2025 | £4,682 | £3,902 | 0.48% << |

<< BSC credit above 0.4% of revenue (elevated operational cash tie-up)

**Peak BSC credit requirement:** 2022 at £10,211 (portfolio growth and 2021-22 price surge)
## Operational Unit Economics

Revenue, gross margin, and net margin per active customer account. The dramatic rise in 2022-23 reflects wholesale price crisis inflating all revenue and cost metrics simultaneously.

| Year | Active | Rev/cust | Gross/cust | Net/cust | Net % |
|------|--------|----------|------------|----------|-------|
| 2016 | 13 | £801 | £524 | £91 | 11.3% |
| 2017 | 14 | £16,735 | £8,803 | £2,183 | 13.0% |
| 2018 | 15 | £29,022 | £17,502 | £6,647 | 22.9% |
| 2019 | 17 | £70,486 | £41,296 | £13,404 | 19.0% |
| 2020 | 19 | £64,388 | £41,674 | £6,432 | 10.0% |
| 2021 | 15 | £115,949 | £51,083 | £4,529 | 3.9% << |
| 2022 | 17 | £202,451 | £61,719 | £17,659 | 8.7% |
| 2023 | 14 | £186,848 | £69,564 | £10,525 | 5.6% |
| 2024 | 14 | £156,210 | £89,610 | £23,583 | 15.1% |
| 2025 | 11 | £88,655 | £47,480 | £10,734 | 12.1% |

<< Net margin below 5% (below Ofgem FRA comfort threshold)

**Best year per customer:** 2024 at £23,583 net/customer
**Worst year per customer:** 2016 at £91 net/customer
## Customer Lifetime P&L by Commodity

Lifetime net margin per customer, split by electricity and gas. Loss-making accounts (marked *) warrant repricing review or exit.

| Customer | Elec net | Gas net | Total |
|----------|----------|---------|-------|
| C1 | £442 | — | £442 |
| C1_2 | £73 | — | £73 |
| C1g | — | £620 | £620 |
| C2 | £690 | — | £690 |
| C2_2 | £1,066 | — | £1,066 |
| C2g | — | £802 | £802 |
| C3 | £206 | — | £206 |
| C3g | — | £283 | £283 |
| C4 | £139 | — | £139 |
| C4g | — | £-2,030 | £-2,030 * |
| C5 | £316 | — | £316 |
| C5_2 | £195 | — | £195 |
| C6 | £3,564 | — | £3,564 |
| C7 | £-1,444 | — | £-1,444 * |
| C8 | £1,270 | — | £1,270 |
| C9 | £1,493 | — | £1,493 |
| C_IC1 | £828,211 | — | £828,211 |
| C_IC2 | £426,670 | — | £426,670 |
| C_IC3 | £115,693 | — | £115,693 |
| C_IC3g | — | £52,416 | £52,416 |
| C_IC4 | £14,584 | — | £14,584 |
| **Total** | **£1,393,167** | **£52,091** | **£1,445,258** |

Loss-making accounts: C4g (£-2,030), C7 (£-1,444)
Gas loss-making: C4g (£-2,030)
Gas portfolio net: £52,091 (3.6% of total)

## Hedge Value-Add Analysis

Actual hedged net margin vs hypothetical spot-only (naked) net margin. Negative value-add indicates forward prices exceeded spot outturn — consistent with UK market backwardation in 2016-2021 and partial hedging in the crisis years.

| Year | Actual net | Naked net | Hedge value-add |
|------|-----------|-----------|-----------------|
| 2016 | £2,034 | £10,920 | £-8,885 |
| 2017 | £30,081 | £112,495 | £-82,414 |
| 2018 | £109,583 | £246,455 | £-136,872 |
| 2019 | £252,590 | £836,842 | £-584,252 |
| 2020 | £86,380 | £964,655 | £-878,275 |
| 2021 | £188,629 | £455,365 | £-266,736 |
| 2022 | £199,826 | £1,226,097 | £-1,026,271 |
| 2023 | £374,806 | £1,216,465 | £-841,659 |
| 2024 | £201,264 | £607,649 | £-406,385 |
| 2025 | £66 | £350 | £-283 |
| **Total** | **£1,445,258** | **£5,677,295** | **£-4,232,037** |

Largest hedging cost: **2022** (£1,026,271 vs naked)
Smallest hedging cost: **2025** (£283 vs naked)
Conclusion: systematic forward hedging cost £4,232,037 over 10 years vs spot purchasing.

## Customer Service Quality

Ofgem benchmarks: bill clarity >0.82 (GREEN) / >0.80 (AMBER) / ≤0.80 (RED); complaint probability <5% (GREEN) / <6% (RED); bill shock <0.20% (GREEN) / <0.30% (AMBER) / ≥0.30% (RED).

| Year | Clarity | Complaint% | Shock% | Shock events | Bills | RAG |
|------|---------|------------|--------|--------------|-------|-----|
| 2016 | 0.829 G | 4.7% | 0.20% | 31 | 108 | GREEN |
| 2017 | 0.818 A | 4.7% | 0.17% | 50 | 168 | AMBER |
| 2018 | 0.810 A | 4.7% | 0.16% | 60 | 180 | AMBER |
| 2019 | 0.824 G | 4.7% | 0.17% | 66 | 204 | GREEN |
| 2020 | 0.831 G | 4.3% | 0.14% | 53 | 205 | GREEN |
| 2021 | 0.817 A | 4.8% | 0.24% | 52 | 180 | AMBER |
| 2022 | 0.783 R | 5.8% | 0.34% | 76 | 173 | RED ! |
| 2023 | 0.801 A | 5.0% | 0.30% | 53 | 168 | RED ! |
| 2024 | 0.806 A | 4.8% | 0.17% | 45 | 153 | AMBER |
| 2025 | 0.768 R | 6.1% | 0.25% | 25 | 66 | RED ! |

Worst clarity year: **2025** (0.768)
Highest complaint probability: **2025** (6.1%)
Worst bill shock: **2022** (0.34%)
RED years: 2022, 2023, 2025
AMBER years: 2017, 2018, 2021, 2024
Trend (last 2 years): DECLINING

## Portfolio VaR Trajectory and Treasury Evolution

Annual VaR ratio (committee trigger = 3.0) and year-end treasury balance.

| Year | VaR Ratio | Status | Treasury £ | Net Margin £ |
|------|-----------|--------|-----------|-------------|
| 2016 | 3.25 | ALERT | £2,467,424 | £1,178 |
| 2017 | 2.69 | WATCH | £2,497,718 | £30,566 |
| 2018 | — | — | £2,486,407 | £99,706 |
| 2019 | — | — | £2,606,406 | £227,872 |
| 2020 | — | — | £2,914,253 | £122,217 |
| 2021 | — | — | £2,943,330 | £67,929 |
| 2022 | 2.70 | WATCH | £3,135,961 | £300,206 |
| 2023 | 2.73 | WATCH | £3,336,256 | £147,354 |
| 2024 | — | — | £3,710,669 | £330,160 |
| 2025 | — | — | £3,760,599 | £118,069 |

**Peak VaR year: 2016 (ratio 3.25)**
**Treasury peak: 2025 (£3,760,599)**
**Treasury growth: £2,467,424 → £3,760,599 (+£1,293,175)**

> VaR ratio = portfolio stressed VaR ÷ treasury; ≥ 3.0 triggers committee review.
> Treasury funded from net margin accumulation, never falling to zero across run.

## UK Grid Fuel Mix Disclosure (Ofgem FMD)

Company's disclosed fuel mix per year (UK national grid average — Ofgem FMD requirement).

| Year | Renewable % | Nuclear % | Gas % | Coal % | Other % | Low-Carbon % |
|------|------------|----------|-------|--------|---------|-------------|
| 2016 | 24.6% | 20.9% | 42.6% | 9.0% | 2.9% | **45.5%** |
| 2017 | 29.3% | 20.4% | 40.7% | 7.0% | 2.6% | **49.7%** |
| 2018 | 33.0% | 19.3% | 39.4% | 5.1% | 3.2% | **52.3%** |
| 2019 | 36.9% | 17.4% | 38.3% | 2.1% | 5.3% | **54.3%** |
| 2020 | 42.2% | 16.7% | 35.8% | 1.8% | 3.5% | **58.9%** |
| 2021 | 39.8% | 14.5% | 38.3% | 2.5% | 4.9% | **54.3%** |
| 2022 | 40.5% | 14.5% | 37.8% | 1.7% | 5.5% | **55.0%** |
| 2023 | 47.8% | 14.6% | 31.5% | 1.3% | 4.8% | **62.4%** |
| 2024 | 51.4% | 14.1% | 28.6% | 0.4% | 5.5% | **65.5%** |
| 2025 | 55.0% | 13.5% | 26.0% | 0.1% | 5.4% | **68.5%** |

**Peak renewable share: 2025 (55.0%)**
**Renewable majority first achieved: 2024**

> UK grid fuel mix disclosed per Ofgem FMD regulations; published annually.
> Suppliers with 100% renewable tariffs must hold REGOs matching total supply.

## Missed Retention Opportunity Analysis

Customers who reached a renewal/churn trigger but received no retention offer.

### Electricity Customers — No Offer Made

| Customer | Date | Churn Estimate | Margin at Risk £ | Reason |
|----------|------|---------------|-----------------|--------|
| C3 | 2020-06 | 4.8% | £585 | below threshold |
| C1 | 2020-12 | 7.3% | £415 | below threshold |
| C2 | 2022-03 | 2.9% | £237 | below threshold |
| C5 | 2022-12 | 2.2% | £2,053 | below threshold |
| C6 | 2024-03 | 24.6% | £2,865 | below threshold ⚑ |
| C4 | 2024-09 | 5.0% | £469 | below threshold |

**High-risk no-offer events (≥10% churn): 1** — £2,865 margin at risk.

### Gas Renewal Risk — High-Churn Reprice Events (≥15% estimate)

| Customer | Term Start | Old Rate p/therm | New Rate p/therm | Churn Est |
|----------|-----------|-----------------|-----------------|----------|
| C2g | 2017-04 | 26.92 | 32.81 | 20.1% |
| C1g | 2017-12 | 26.25 | 33.49 | 22.6% |
| C3g | 2018-07 | 23.11 | 28.80 | 20.8% |
| C4g | 2018-10 | 26.10 | 33.61 | 23.3% |
| C_IC3g | 2020-12 | 15.44 | 19.38 | 21.3% |
| C2g | 2021-03 | 21.66 | 35.00 | 39.9% |
| C4g | 2021-09 | 16.09 | 35.00 | 73.5% |
| C_IC3g | 2021-12 | 19.38 | 125.90 | 95.0% |

**High-risk gas reprices: 9**

> ⚑ = customers with ≥15% churn estimate who received no retention offer.

## Retention Decision Economics

Per-offer cost, expected margin protected, and ROI for each retention intervention.

| Customer | Period | Retention Cost £ | Margin Protected £ | ROI | Discount % | Outcome |
|----------|--------|-----------------|-------------------|-----|------------|---------|
| C8 | 2017-04 | £46 | £868 | 18.9× | 3% | retained |
| C3 | 2017-07 | £25 | £495 | 19.6× | 3% | retained |
| C_IC1 | 2018-01 | £24,228 | £163,705 | 6.8× | 8% | retained |
| C4 | 2018-10 | £18 | £345 | 18.7× | 3% | retained |
| C1 | 2018-12 | £21 | £379 | 18.0× | 3% | retained |
| C_IC2 | 2019-01 | £14,842 | £101,641 | 6.8× | 8% | retained |
| C_IC1 | 2019-03 | £17,469 | £194,971 | 11.2× | 5% | retained |
| C_IC2 | 2021-03 | £5,311 | £91,315 | 17.2× | 3% | retained |
| C_IC1 | 2021-04 | £8,447 | £158,251 | 18.7× | 3% | retained |
| C5 | 2021-12 | £198 | £2,475 | 12.5× | 3% | retained |
| C_IC3 | 2021-12 | £51,616 | £161,519 | 3.1× | 5% | retained |
| C_IC2 | 2022-04 | £9,418 | £96,241 | 10.2× | 3% | retained |
| C_IC1 | 2022-05 | £18,142 | £231,599 | 12.8× | 3% | retained |
| C6 | 2023-03 | £229 | £3,222 | 14.0× | 3% | retained |

**Total retention spend: £150,010** | **Total margin protected: £1,207,026**
**Portfolio retention ROI: 8.0×** | **Retained: 14/14**
**Best ROI intervention: C3 2017-07 (19.6×)**

> ROI = expected remaining-term margin ÷ retention cost (discount given).
> Churn probability weighted; 95% churn estimate used for I&C renewal trigger.

## Gas Exit Decision Analysis

Three-scenario P&L impact for the board (dual-fuel portfolio lifetime figures).

| Scenario | Net Margin £ | vs Status Quo |
|----------|-------------|--------------|
| Status Quo (hold gas) | £169,260 | — |
| Exit Gas (with churn risk) | £70,597 | -£98,663 |
| Reprice to Breakeven | £171,290 | +£2,030 |

**Loss-making gas accounts: C4**
**Board recommendation: REPRICE GAS**

> Gas drag reduces dual-fuel net margin. Repricing to breakeven is preferable to exit
> because exiting gas risks losing the electricity contract (cross-product churn).

## Portfolio Hedge Fraction Evolution

Average hedge fraction (0=fully naked, 1=fully hedged) per year.

| Year | Portfolio Avg | Min HF | Max HF | Naked Accounts | Covered Accts |
|------|--------------|--------|--------|---------------|--------------|
| 2016 | 88.9% | 85.0% | 92.2% | — | 13 |
| 2017 | 89.5% | 85.0% | 94.3% | — | 14 |
| 2018 | 89.5% | 85.0% | 93.1% | — | 15 |
| 2019 | 83.5% | 0.0% | 96.2% | 1 | 16 |
| 2020 | 81.6% | 0.0% | 96.0% | 1 | 14 |
| 2021 | 85.0% | 0.0% | 97.0% | 1 | 14 |
| 2022 | 86.9% | 0.0% | 97.4% | 1 | 13 |
| 2023 | 84.3% | 0.0% | 96.1% | 1 | 13 |
| 2024 | 80.9% | 0.0% | 94.3% | 1 | 10 |
| 2025 | 87.2% | 85.0% | 89.4% | — | 2 |

**Lowest portfolio hedge fraction: 2024 (80.9%)** — risk erosion from regime-change blindness.
**Naked positions first appear in 2019** — unhedged accounts expose portfolio to spot price swings.

> Regime-change blindness: the sim converged toward lower hedging during calm 2016-2020,
> mirroring the strategy that destroyed real UK suppliers entering the 2021-22 crisis.

## Risk Committee Intervention Pattern

Annual risk committee wake-ups (triggered when portfolio VaR exceeds threshold).

| Year | Wake-ups | Customer Adjustments | Avg Customers/Event | Max VaR Stressed £ |
|------|----------|---------------------|--------------------|--------------------|
| 2016 | 13 | 13 | 1.0 | £9 |
| 2017 | 12 | 33 | 2.8 | £401 |
| 2022 | 9 | 59 | 6.6 | £20,607 |
| 2023 | 4 | 36 | 9.0 | £48,915 |

**Peak intervention year: 2016 (13 wake-ups)**
**Total committee events (all years): 38**

> Each wake-up adjusts hedge fractions upward for flagged customers. 2016-17 (early book).
> 2022-23 crisis years trigger most interventions on I&C anchor accounts.

## Worst Half-Hourly Settlement Period by Year

Most loss-making single 30-minute period per settlement year.

| Year | Date | SP | Customer | Net Margin £ |
|------|------|----|----------|-------------|
| 2016 | 2016-11-08 | 40 | C6 | -£0 |
| 2017 | 2017-05-17 | 32 | C_IC1 | -£20 |
| 2018 | 2018-03-01 | 27 | C_IC1 | -£15 |
| 2019 | 2019-02-04 | 35 | C_IC1 | -£15 |
| 2020 | 2020-03-16 | 20 | C_IC1 | -£19 |
| 2021 | 2021-11-24 | 30 | C_IC1 | -£75 |
| 2022 | 2022-01-24 | 26 | C_IC1 | -£89 |
| 2023 | 2023-06-16 | 22 | C_IC1 | -£22 |
| 2024 | 2024-06-28 | 31 | C_IC1 | -£26 |
| 2025 | 2025-01-08 | 31 | C_IC1 | -£81 |

**Single worst period: 2022 2022-01-24 SP26 (C_IC1, -£89)** — exposure from gas supply anchor at year-end pricing.

> SP = settlement period (1-48; SP1 = 00:00-00:30). Year-end gas exposure dominates from 2020 onward as C_IC3g position grows.

## BSC Credit Obligation and Regulatory Levy Breakdown

Elexon BSC credit posting requirement and annual levy costs.

| Year | BSC Credit £ | CM Levy £ | Mutualization £ | CCL £ | Gas Network £ |
|------|-------------|----------|----------------|-------|--------------|
| 2016 | £30 | £37 | — | £189 | £479 |
| 2017 | £559 | £1,977 | — | £11,165 | £898 |
| 2018 | £1,019 | £9,350 | — | £17,434 | £905 |
| 2019 | £1,851 | £31,969 | — | £42,460 | £50,388 |
| 2020 | £2,375 | £56,550 | — | £69,454 | £47,213 |
| 2021 | £5,211 | £49,675 | £41,427 | £71,336 | £50,301 |
| 2022 | £10,211 | £36,748 | £99,654 | £71,047 | £54,433 |
| 2023 | £6,755 | £51,053 | £13,776 | £71,831 | £79,700 |
| 2024 | £3,200 | £68,826 | £2,002 | £72,944 | £76,429 |
| 2025 | £4,682 | £31,094 | £855 | £31,221 | £31,816 |

**Peak BSC credit obligation: 2022 (£10,211)** — driven by portfolio volume growth and crisis price levels.
**Mutualization levy first appeared in 2016** — reflects supplier failure costs passed to remaining suppliers via BSC.

> BSC credit = Elexon-mandated deposit against settlement exposure. Scales with volume × price.
> Mutualization = recoverable defaults from failed suppliers in settlement.

## Customer Cohort Revenue Analysis

Lifetime P&L by year-of-acquisition cohort (all years to simulation end).

| Cohort | Customers | Total Revenue £ | Gross Margin £ | Net Margin £ | Rev/Customer £ |
|--------|-----------|----------------|---------------|-------------|----------------|
| 2016 | 16 | £196,493 | £105,336 | £7,684 | £12,281 |
| 2017 | 1 | £3,123,605 | £1,874,667 | £828,211 | £3,123,605 |
| 2018 | 1 | £1,525,270 | £909,829 | £426,670 | £1,525,270 |
| 2019 | 2 | £6,470,569 | £2,456,085 | £168,109 | £3,235,285 |
| 2020 | 1 | £2,744,639 | £1,106,685 | £14,584 | £2,744,639 |

**Best revenue/customer cohort: 2019 (£3,235,285/customer)**
**Best net margin cohort: 2017 (£828,211)**

> Note: Gas customer legs excluded from electricity metrics; cohort = year of first contract.

## CfD Levy, Bad Debt & Treasury Drawdowns

Contracts for Difference levy (negative = credit to supplier in high-price periods).

| Year | CfD Levy £ | RO Levy £ | Bad Debt £ | Treasury Drawdowns | Bills |
|------|-----------|----------|-----------|-------------------|-------|
| 2016 | +£7 | £1,162 | £167 | — | 108 |
| 2017 | +£2,707 | £37,159 | £1,375 | — | 168 |
| 2018 | +£9,875 | £65,510 | £2,385 | — | 180 |
| 2019 | +£28,353 | £164,625 | £6,207 | — | 204 |
| 2020 | +£35,391 | £238,638 | £6,295 | — | 205 |
| 2021 | +£15,010 | £246,702 | £9,146 | — | 180 |
| 2022 | -£49,827 CREDIT | £256,667 | £36,025 | 1 | 173 |
| 2023 | +£64,889 | £272,368 | £14,424 | — | 168 |
| 2024 | +£110,127 | £308,162 | £11,505 | 3714 | 153 |
| 2025 | +£47,047 | £136,010 | £5,022 | — | 66 |

**CfD turned CREDIT in 2022: -£49,827 (high wholesale → CfD generators repay system)**
**Treasury drawdown years: 2022, 2024** (credit facility used)
**Peak bad debt year: 2022 (£36,025)**

> CfD (Contracts for Difference): when wholesale > strike price, generators repay;
> the net credit is passed through as a negative levy on supplier bills.

## Segment Gross Margin Attribution

Gross margin (£) by customer segment and year.

| Year | resi electricity | resi gas | SME electricity | I&C electricity | I&C gas | Total |
|------|----------|----------|----------|----------|----------|-------|
| 2016 | £3,270 | £811 | £2,733 | £0 | £0 | £6,814 |
| 2017 | £4,994 | £1,430 | £3,395 | £113,418 | £0 | £123,236 |
| 2018 | £5,063 | £1,363 | £3,206 | £252,900 | £0 | £262,531 |
| 2019 | £5,779 | £1,428 | £4,051 | £616,144 | £74,626 | £702,028 |
| 2020 | £5,688 | £1,207 | £4,236 | £704,702 | £75,972 | £791,806 |
| 2021 | £5,790 | £354 | £4,524 | £673,320 | £82,255 | £766,242 |
| 2022 | £4,971 | -£762 | £6,340 | £947,557 | £91,118 | £1,049,224 |
| 2023 | £7,943 | -£575 | £5,789 | £839,225 | £121,515 | £973,897 |
| 2024 | £10,511 | £762 | £5,133 | £1,114,487 | £123,652 | £1,254,545 |
| 2025 | £4,543 | £0 | £1,361 | £462,867 | £53,509 | £522,280 |

**Best gross margin year: 2024 (£1,254,545)** | **Worst: 2016 (£6,814)**
**Loss-making: resi gas in 2022 (£-762)**
**Loss-making: resi gas in 2023 (£-575)**


## Price Cap Headroom (Tariff vs SVT)

Percentage difference between contracted unit rate and SVT (price cap) at term start.
Negative = below cap (headroom). Positive = above cap (I&C terms; SVT applies to resi only).

| Year | Terms | Avg vs SVT% | Above Cap | Min% | Max% |
|------|-------|-------------|-----------|------|------|
| 2016 | 3 | -6.3% | 0/3 | -6.7% | +-5.8% |
| 2017 | 3 | -14.3% | 0/3 | -16.0% | +-12.4% |
| 2018 | 4 | -1.2% | 1/4 | -3.3% | +0.6% |
| 2019 | 4 | -18.8% | 1/4 | -29.5% | +12.4% |
| 2020 | 10 | -29.8% | 0/10 | -68.5% | +-17.4% |
| 2021 | 9 | +17.8% | 6/9 | -12.0% | +69.8% |
| 2022 | 9 | -1.2% | 4/9 | -63.2% | +95.7% |
| 2023 | 9 | -29.5% | 0/9 | -60.5% | +-1.7% |
| 2024 | 9 | -18.8% | 1/9 | -53.5% | +3.3% |
| 2025 | 2 | -2.9% | 1/2 | -23.6% | +17.8% |

**Best headroom year: 2020 (avg 29.8% below SVT)**
**Largest above-SVT year: 2021** (6/9 terms above — note: I&C customers exempt from SVT cap)

> SVT (Standard Variable Tariff) = Ofgem price cap. Residential tariffs must not exceed SVT.
> I&C/SME terms above SVT are expected during crisis years when wholesale >cap.

## Portfolio Stress Test History

Retrospective RAG status: would year-end treasury have survived each scenario?
Credit facility: £2M. Weekly burn estimated at 1% of year-end treasury.

| Year | Treasury £ | Mkt Spike | Credit | Demand | Liquidity | Combined |
|------|-----------|----------|----------|----------|----------|----------|
| 2016 | £2,467,424 | AMBER | RED | GREEN | AMBER | RED |
| 2017 | £2,497,718 | AMBER | RED | GREEN | AMBER | RED |
| 2018 | £2,486,407 | AMBER | RED | GREEN | AMBER | RED |
| 2019 | £2,606,406 | AMBER | RED | GREEN | AMBER | RED |
| 2020 | £2,914,253 | AMBER | AMBER | GREEN | AMBER | RED |
| 2021 | £2,943,330 | AMBER | AMBER | GREEN | AMBER | RED |
| 2022 | £3,135,961 | AMBER | AMBER | GREEN | AMBER | RED |
| 2023 | £3,336,256 | AMBER | AMBER | GREEN | AMBER | RED |
| 2024 | £3,710,669 | AMBER | AMBER | GREEN | AMBER | RED |
| 2025 | £3,760,599 | AMBER | AMBER | GREEN | AMBER | RED |

**Most stressed year: 2016 (2 RED scenario(s))**

> GREEN = drawdown <25% | AMBER = 25-50% | RED = drawdown >50% (or failure).

## Financial Ratios

Key per-customer and margin metrics by year.

| Year | Customers | EBIT% | Revenue/Customer £ | GM/Customer £ | Bad Debt% |
|------|-----------|-------|--------------------|--------------|-----------|
| 2016 | 13 | 45.2% | £1,181 | £605 | 1.53% |
| 2017 | 14 | 33.5% | £24,902 | £8,914 | 1.80% |
| 2018 | 15 | 41.6% | £40,064 | £17,612 | 1.97% |
| 2019 | 17 | 40.7% | £96,791 | £41,404 | 1.87% |
| 2020 | 19 | 40.5% | £97,742 | £41,769 | 2.06% |
| 2021 | 15 | 29.5% | £161,423 | £51,184 | 1.95% |
| 2022 | 17 | 22.4% | £249,739 | £61,810 | 1.98% |
| 2023 | 14 | 25.4% | £249,697 | £69,660 | 2.20% |
| 2024 | 14 | 39.4% | £214,230 | £89,653 | 2.14% |
| 2025 | 11 | 38.9% | £112,099 | £47,527 | 2.98% |

**Best EBIT%: 2016 (45.2%)** | **Worst EBIT%: 2022 (22.4%)**
**Peak revenue/customer: 2022 (£249,739)**

> Note: Revenue/customer driven by customer mix (I&C customers 10-100× resi volumes).

## Population Anchoring -- Complaints & Arrears (Phase PS)

SIM aggregate complaint and arrears rates vs published UK benchmarks.
Complaints: Ofgem QoS survey, I&C adjusted (GREEN 2-6%, crisis 2-8%).
Arrears: DESNZ business energy debt (GREEN <8%, crisis <12%).

| Year | Complaint rate% | C.Bench hi | C.RAG | Arrears rate% | A.Bench hi | A.RAG |
|------|-----------------|-----------|-------|---------------|-----------|-------|
| 2016 | 4.70% | 6% | OK | 30.8% | 8% | ! |
| 2017 | 4.67% | 6% | OK | 21.4% | 8% | ! |
| 2018 | 4.66% | 6% | OK | 33.3% | 8% | ! |
| 2019 | 4.67% | 6% | OK | 23.5% | 8% | ! |
| 2020 | 4.29% | 6% | OK | 5.3% | 8% | OK |
| 2021 | 4.80% | 8% | OK | 20.0% | 12% | ! |
| 2022 | 5.81% | 8% | OK | 35.3% | 12% | ! |
| 2023 | 5.05% | 8% | OK | 21.4% | 12% | ! |
| 2024 | 4.82% | 6% | OK | 28.6% | 8% | ! |
| 2025 | 6.07% | 6% | ~ | 9.1% | 8% | ~ |

**Complaints:** 9 of 10 years GREEN (I&C baseline 2-6% normal, 2-8% crisis).
**Arrears:** 1 of 10 years GREEN (DESNZ I&C baseline <8% normal, <12% crisis).

## Plausibility vs Industry

Key metrics vs UK retail energy norms (Ofgem/Cornwall Insight). OK = within range | ~ = amber | ! = outside expected range.

| Year | Net margin% | Gross margin% | Bad debt% | Churn% |
|------|-------------|---------------|-----------|--------|
| 2016 | !45.2% | !51.2% | OK1.53% | ~0% |
| 2017 | !33.5% | !35.8% | OK1.80% | ~0% |
| 2018 | !41.6% | !44.0% | OK1.97% | ~0% |
| 2019 | !40.7% | !42.8% | OK1.87% | ~0% |
| 2020 | !40.5% | !42.7% | OK2.06% | OK11% |
| 2021 | !29.5% | !31.7% | OK1.95% | ~0% |
| 2022 | !22.4% | ~24.7% | OK1.98% | OK12% |
| 2023 | !25.4% | ~27.9% | OK2.20% | ~0% |
| 2024 | !39.4% | !41.8% | OK2.14% | OK14% |
| 2025 | !38.9% | !42.4% | OK2.98% | ~0% |

**Benchmark ranges:** Net margin %: −5 to +8% green | Gross margin %: 0–20% green | Bad debt %: 0–5% green | Annual churn %: 3–35% green.
**RED — review required: 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025**

## Churn Prediction Calibration

How well the company estimated churn probability versus actual simulation outcomes.

| Customer | Date | Sim Probability | Company Estimate | Delta | Verdict |
|----------|------|----------------|-----------------|-------|---------|
| C3 | 2020-06 | 6.5% | 4.8% | -1.7pp | ACCURATE |
| C1 | 2020-12 | 22.3% | 7.3% | -15.0pp | UNDERESTIMATED |
| C2 | 2022-03 | 4.9% | 2.9% | -2.0pp | ACCURATE |
| C5 | 2022-12 | 4.9% | 2.2% | -2.7pp | ACCURATE |
| C6 | 2024-03 | 20.7% | 24.6% | +3.9pp | ACCURATE |
| C4 | 2024-09 | 14.3% | 5.0% | -9.3pp | ACCURATE |

**Outcomes: 1 underestimated / 5 accurate / 0 overestimated**
**Mean absolute error: 5.8pp**
**Systematic bias: company consistently UNDER-predicted churn risk.**

> Company churn estimates derived from company-observable signals (bill shock,
> margin feedback, renewal history) without access to the simulation's internal
> churn parameters — epistemic gap is expected and realistic for a small supplier.

## Counterfactual Retention & Threshold Optimisation

**Current threshold:** 30% | F1=0.000
**Optimal threshold:** 0% | F1=0.176

**RAG [!]:** RED — 4 unrecoverable high-value miss(es) — model underestimates churn: optimal threshold below current

**Missed retention opportunities:** 6 no-offer churns
  Value at stake: £6,623
  Counterfactually recoverable (with offer): 2/6
  Net value recoverable (after offer cost): £552

### Per-miss detail

| Year | Customer | Est | SIM p | Recoverable? | Margin | Net value |
|------|----------|-----|-------|-------------|--------|----------|
| 2020 | C3 | 5% | 6% | No | £585 | £-50 |
| 2020 | C1 | 7% | 22% | Yes | £415 | £365 |
| 2022 | C2 | 3% | 5% | Yes | £237 | £187 |
| 2022 | C5 | 2% | 5% | No | £2,053 | £-50 |
| 2024 | C6 | 25% | 21% | No | £2,865 | £-50 |
| 2024 | C4 | 5% | 14% | No | £469 | £-50 |

### Threshold sensitivity curve

| Threshold | Recall | Precision | F1 |
|-----------|--------|-----------|----|
| 0% | 1.000 | 0.097 | 0.176 ← optimal |
| 5% | 0.500 | 0.081 | 0.140 |
| 10% | 0.167 | 0.050 | 0.077 |
| 15% | 0.167 | 0.100 | 0.125 |
| 20% | 0.167 | 0.100 | 0.125 |
| 25% | 0.000 | 0.000 | 0.000 |
| 30% | 0.000 | 0.000 | 0.000 |
| 35% | 0.000 | 0.000 | 0.000 |
| 40% | 0.000 | 0.000 | 0.000 |
| 45% | 0.000 | 0.000 | 0.000 |
| 50% | 0.000 | 0.000 | 0.000 |

## Churn Model Quality (Phase NK)

Company churn model performance: did the company predict churn before it happened?
Threshold: company_churn_estimate > 30% = predicted. Evaluated at each renewal event.

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Total churn events | 6 | Customers who actually churned |
| True Positives (TP) | 0 | Churn predicted AND happened |
| False Positives (FP) | 6 | Churn predicted BUT customer renewed |
| False Negatives (FN) | 6 | Churn NOT predicted BUT happened (blind miss) |
| True Negatives (TN) | 50 | No churn predicted AND customer renewed |
| **Recall** | **0.0%** | % of churners detected before departure |
| **Precision** | **0.0%** | % of retention offers to genuine churners |
| **F1 Score** | **0.00** | Harmonic mean of recall and precision |

**Model quality: RED**

> **Board Action Required:** F1 < 0.30 — churn model is failing to detect departures.
> Company is missing churning customers; retention spend may be misdirected.

> **Known limitation:** passive SVT-rollers (69% of renewals) churn at ~10% effective rate
> after passive_churn_cap, but the 30% retention threshold is calibrated for active renewers.
> Passive blind misses are a structural feature — these customers's seasonal bill variability
> (8-11 monthly shocks/year) inflates the SIM's base churn_probability to 29-38%, but
> effective churn after the passive cap is ~11%. A separate passive loyalty programme
> would be needed to recover these departures.

### Per-Year Model Performance

| Year | TP | FP | FN | TN | Recall | Precision |
|------|----|----|----|----|--------|-----------|
| 2016 | 0 | 0 | 0 | 3 | 0% | 0% |
| 2017 | 0 | 0 | 0 | 3 | 0% | 0% |
| 2018 | 0 | 2 | 0 | 2 | 0% | 0% |
| 2019 | 0 | 1 | 0 | 3 | 0% | 0% |
| 2020 | 0 | 0 | 2 | 8 | 0% | 0% |
| 2021 | 0 | 2 | 0 | 7 | 0% | 0% |
| 2022 | 0 | 0 | 2 | 7 | 0% | 0% |
| 2023 | 0 | 1 | 0 | 8 | 0% | 0% |
| 2024 | 0 | 0 | 2 | 7 | 0% | 0% |
| 2025 | 0 | 0 | 0 | 2 | 0% | 0% |

## Credit Risk & Capital Stress (Phase NR)

**Ofgem FRA stress multiplier:** 2.5x (empirical: 2021-22 crisis, industry bad debt 1% → 2.5% revenue)

| Year | Revenue £ | Bad Debt £ | Bad Debt % | Crisis Stress £ |
|------|-----------|------------|------------|-----------------|

**Total bad debt (all years):** £92,551
**Crisis stress incremental:** £138,826

**RAG [~]:** AMBER — Credit stress material but below 1% revenue

## Scenario Sensitivity Analysis (Phase PZ)

Live portfolio (11 active customers) under 12-month forward scenarios.
Generated: 2026-07-04T15:30:48Z

Closes CLAUDE.md known failure: regime-change blindness — board can now ask 'what if 2021-22 happened again?'

| Scenario | Elec Fwd (£/MWh) | Gas Fwd (£/MWh) | Hedge Rec | Renewing | Exposure Delta |
|----------|------------------|-----------------|-----------|----------|----------------|
| Base | 86.7 | 55.1 | INCREASE | 0 | — |
| Bull | 56.1 | 35.7 | INCREASE | 0 | £-398,252 |
| Bear | 147.9 | 93.8 | INCREASE | 0 | +£796,504 |
| Crisis | 217.3 | 110.2 | INCREASE | 0 | +£1,562,206 |

**Scenario labels:**
- **Base**: Base (normal OU, long-run mean start)
- **Bull**: Bull (prices below long-run mean — cheap energy)
- **Bear**: Bear (prices above long-run mean — expensive energy)
- **Crisis**: Crisis (high-vol regime forced — 2021-22 style shock)

**Exposure delta:** additional annual unhedged commodity cost vs base scenario.
Positive = more expensive under this scenario; negative = cheaper.

**Renewal flags under each scenario:**

## Tariff Estimation Accuracy

Mean and maximum absolute error between company tariff estimates and actual outturn.

| Year | Observations | Mean Abs Error | Max Abs Error | Accuracy |
|------|-------------|---------------|--------------|----------|
| 2016 | 17 | 15.1% | 29.1% | POOR |
| 2017 | 14 | 16.6% | 46.6% | POOR |
| 2018 | 16 | 12.1% | 27.7% | MODERATE |
| 2019 | 19 | 11.0% | 37.2% | MODERATE |
| 2020 | 22 | 12.4% | 33.8% | MODERATE |
| 2021 | 17 | 14.5% | 44.5% | MODERATE |
| 2022 | 18 | 12.4% | 23.2% | MODERATE |
| 2023 | 16 | 22.3% | 40.0% | POOR |
| 2024 | 15 | 10.8% | 22.6% | MODERATE |
| 2025 | 2 | 33.1% | 33.1% | POOR |

**Best accuracy year (n≥5): 2024 (10.8% mean error)**
**Worst accuracy year (n≥5): 2023 (22.3% mean error)**

> Errors reflect the company's information gap: forward curves are approximations;
> the company cannot observe simulation wholesale cost internals (epistemic blindfold).

## Dynamic Pricing Activity

Rate adjustments driven by the margin feedback loop and emergency reprice events.

| Year | Adjustments | Avg Delta £/MWh | Up | Down | Emergency |
|------|------------|-----------------|-----|------|-----------|
| 2016 | 4 | -0.6 | 1 | 3 | 0 |
| 2017 | 13 | -1.1 | 1 | 12 | 0 |
| 2018 | 14 | +2.5 | 6 | 8 | 2 |
| 2019 | 15 | +1.4 | 5 | 10 | 2 |
| 2020 | 17 | +3.6 | 8 | 9 | 2 |
| 2021 | 14 | +13.5 | 14 | 0 | 7 |
| 2022 | 13 | +19.3 | 12 | 1 | 5 |
| 2023 | 13 | +6.0 | 8 | 5 | 9 |
| 2024 | 12 | +5.3 | 6 | 6 | 2 |
| 2025 | 2 | +4.8 | 2 | 0 | 0 |

**Total adjustments 2016-2025: 117** | **Peak avg adjustment: 2022 (+19.3 £/MWh)**
**Emergency reprices: 29 total** (9 in 2023)

> Emergency reprices triggered when recent margin dropped below cost floor.
> Normal adjustments from rolling margin feedback; £/MWh delta versus prior contracted rate.

## Portfolio CLV Evolution

Estimated forward lifetime value of active billing accounts at each year-end.

| Year | Accounts | Total CLV £ | Avg CLV £ | Δ CLV £ |
|------|----------|-------------|-----------|---------|
| 2016 | 3 | £30,538 | £10,179 | — |
| 2017 | 9 | £102,659 | £11,407 | +£72,121 |
| 2018 | 10 | £2,904,773 | £290,477 | +£2,802,114 |
| 2019 | 11 | £4,511,862 | £410,169 | +£1,607,089 |
| 2020 | 14 | £7,110,282 | £507,877 | +£2,598,420 |
| 2021 | 14 | £6,925,277 | £494,663 | £-185,005 |
| 2022 | 16 | £6,728,933 | £420,558 | £-196,345 |
| 2023 | 16 | £6,248,615 | £390,538 | £-480,317 |
| 2024 | 16 | £5,818,997 | £363,687 | £-429,618 |
| 2025 | 16 | £5,793,288 | £362,080 | £-25,710 |

**Peak portfolio CLV: 2020 (£7,110,282)** | **Earliest/lowest: 2016 (£30,538)**
**Largest YoY gain: 2018 (+£2,802,114)**
**Largest YoY fall: 2023 (£-480,317)**

> Note: CLV snapshots are forward estimates at year-end based on remaining contract tenure and expected margins at that point in time.

## Gross Margin Bridge (Year-over-Year Attribution)

Annual change in gross margin decomposed into revenue and cost drivers.

| Year | Revenue £ | Wholesale £ | Non-Commodity £ | Gross Margin £ | GM% | ΔRevenue £ | ΔWholesale £ | ΔNon-Comm £ | ΔGM £ |
|------|-----------|-------------|-----------------|----------------|-----|------------|--------------|-------------|-------|
| 2016 | £15,354.61 | £3,596.53 | £3,892.24 | £7,865.84 | 51.2% | — | — | — | — |
| 2017 | £348,630.52 | £111,056.98 | £112,782.23 | £124,791.30 | 35.8% | +£333,275.90 | +£107,460.46 | +£108,889.99 | +£116,925.46 |
| 2018 | £600,953.01 | £172,802.28 | £163,976.80 | £264,173.93 | 44.0% | +£252,322.49 | +£61,745.30 | +£51,194.57 | +£139,382.63 |
| 2019 | £1,645,452.10 | £496,239.95 | £445,337.04 | £703,875.12 | 42.8% | +£1,044,499.09 | +£323,437.66 | +£281,360.24 | +£439,701.19 |
| 2020 | £1,857,096.31 | £431,628.21 | £631,861.95 | £793,606.15 | 42.7% | +£211,644.21 | £-64,611.74 | +£186,524.91 | +£89,731.04 |
| 2021 | £2,421,344.01 | £973,152.05 | £680,438.97 | £767,752.99 | 31.7% | +£564,247.70 | +£541,523.84 | +£48,577.02 | £-25,853.16 |
| 2022 | £4,245,565.53 | £2,392,501.35 | £802,298.72 | £1,050,765.46 | 24.7% | +£1,824,221.52 | +£1,419,349.30 | +£121,859.75 | +£283,012.47 |
| 2023 | £3,495,761.69 | £1,642,210.96 | £878,317.42 | £975,233.31 | 27.9% | £-749,803.83 | £-750,290.38 | +£76,018.70 | £-75,532.15 |
| 2024 | £2,999,221.95 | £933,180.92 | £810,905.76 | £1,255,135.26 | 41.8% | £-496,539.75 | £-709,030.04 | £-67,411.66 | +£279,901.95 |
| 2025 | £1,233,083.98 | £452,920.26 | £257,370.51 | £522,793.21 | 42.4% | £-1,766,137.97 | £-480,260.67 | £-553,535.25 | £-732,342.05 |

**Best GM year: 2016 (51.2%)** | **Worst GM year: 2022 (24.7%)**

> Note: Non-commodity costs include network (DUoS/TNUoS), policy levies (RO/CfD/CCL/CM/FiT), and mutualization.

## Net Margin Bridge (Year-on-Year Attribution)

Decomposes each year's net margin change into: gross margin movement, bad debt, capital costs, policy levies, network costs.

| Transition | Net Δ | Gross Δ | Bad Debt Δ | Capital Δ | Policy Δ | Network Δ | Portfolio | Driver | RAG |
|-----------|-------|---------|-----------|---------|---------|---------|---------|--------|-----|
| 2016→2017 | +£29,388 | +£116,423 | -£1,209 | -£1,187 | -£61,247 | -£23,393 | +1 | gross margin | GREEN |
| 2017→2018 | +£69,140 | +£139,295 | -£1,009 | -£255 | -£56,505 | -£12,385 | +1 | gross margin | GREEN |
| 2018→2019 | +£128,166 | +£439,496 | -£3,823 | -£781 | -£207,410 | -£99,316 | +2 | gross margin | GREEN |
| 2019→2020 | -£105,656 | +£89,778 | -£88 | +£344 | -£162,663 | -£33,027 | +2 | policy levies | RED |
| 2020→2021 | -£54,288 | -£25,564 | -£2,851 | -£3,670 | -£19,932 | -£2,271 | -4 | gross margin | RED |
| 2021→2022 | +£232,277 | +£282,982 | -£26,879 | -£7,660 | -£1,107 | -£15,058 | +2 | gross margin | GREEN |
| 2022→2023 | -£152,852 | -£75,327 | +£21,601 | +£3,156 | -£70,820 | -£31,462 | -3 | gross margin | RED |
| 2023→2024 | +£182,807 | +£280,648 | +£2,919 | +£639 | -£100,877 | -£522 | +0 | gross margin | GREEN |
| 2024→2025 | -£212,091 | -£732,265 | +£6,482 | +£3,803 | +£382,565 | +£127,323 | -3 | gross margin | RED |

**Most damaging transition: 2024→2025 (-£212,091)** | **Best transition: 2021→2022 (+£232,277)**

> Gross delta: revenue minus energy wholesale cost. Bad debt / capital / policy / network deltas: negative = costs rose (margin impact). Portfolio: active customer count change.

## Payment Portfolio Health (P2: Billing Infra)

Year-by-year bad debt rate and high-churn-risk customer concentration.

| Year | Bad Debt | Bad Debt Rate | At-Risk Customers | At-Risk % | Trend | RAG |
|------|----------|--------------|-----------------|----------|-------|-----|
| 2016 | £167 | 1.60% | 0/5 | 0% | — STABLE | RED |
| 2017 | £1,375 | 0.59% | 0/12 | 0% | ↓ IMPROVING | GREEN |
| 2018 | £2,385 | 0.55% | 1/13 | 8% | — STABLE | GREEN |
| 2019 | £6,207 | 0.52% | 3/14 | 21% | — STABLE | GREEN |
| 2020 | £6,295 | 0.51% | 5/16 | 31% | — STABLE | AMBER |
| 2021 | £9,146 | 0.53% | 4/14 | 29% | — STABLE | GREEN |
| 2022 | £36,025 | 1.05% | 10/14 | 71% | ↑ DETERIORATING | RED |
| 2023 | £14,424 | 0.55% | 9/12 | 75% | ↓ IMPROVING | RED |
| 2024 | £11,505 | 0.53% | 3/12 | 25% | — STABLE | GREEN |
| 2025 | £5,022 | 0.52% | 2/3 | 67% | — STABLE | RED |

**Worst bad debt year: 2016 (1.60%)** | **Peak at-risk concentration: 2023 (75% of customers)**

> At-risk = churn risk score >30% at year-end. Bad debt rate = written-off bad debt as % of annual revenue. RAG: GREEN <0.75% bad debt and <30% at-risk; RED >1.5% bad debt or >60% at-risk.

## Portfolio Composition (P3: Population Anchoring)

Gross margin share by segment and fuel type. Concentration RAG: GREEN <70% dominant, AMBER 70-90%, RED >90% (single-segment dependency).
Benchmark: balanced UK small supplier targets resi 40-70%, I&C 20-50%, elec 70-90% of gross.

| Year | Resi% | SME% | I&C% | Elec% | Gas% | Dominant | Concentration |
|------|-------|------|------|-------|------|---------|--------------|
| 2016 | 60% | 40% | 0% | 88% | 12% | Residential | GREEN |
| 2017 | 5% | 3% | 92% | 99% | 1% | I&C | RED |
| 2018 | 2% | 1% | 96% | 99% | 1% | I&C | RED |
| 2019 | 1% | 1% | 98% | 89% | 11% | I&C | RED |
| 2020 | 1% | 1% | 99% | 90% | 10% | I&C | RED |
| 2021 | 1% | 1% | 99% | 89% | 11% | I&C | RED |
| 2022 | 0% | 1% | 99% | 91% | 9% | I&C | RED |
| 2023 | 1% | 1% | 99% | 88% | 12% | I&C | RED |
| 2024 | 1% | 0% | 99% | 90% | 10% | I&C | RED |
| 2025 | 1% | 0% | 99% | 90% | 10% | I&C | RED |

> **Concentration alert:** I&C dominated gross margin in 2017–2025. Loss of a single large I&C customer has outsized P&L impact. Benchmark: a resilient mixed-book supplier targets no segment >70% of gross margin.

## Shadow Retention Strategy (P4: Shadow Ops)

Counterfactual: what if the company had offered retention to ALL renewal customers (not just those above the 30% threshold)?
Shadow discount: 8% off next term. Assumes P(accept) = (1 - churn\_estimate) x 90%.

| Year | No-Offer Churns | Margin Lost | Shadow Retained | Offer Cost | Shadow Net Gain |
|------|----------------|------------|----------------|-----------|----------------|
| 2020 | 2 | £1,001 | £780 | £68 | +£712 |
| 2022 | 2 | £2,289 | £1,852 | £161 | +£1,691 |
| 2024 | 2 | £3,334 | £2,157 | £188 | +£1,969 |

**Total opportunity cost vs actual: +£4,373 net** (gross £6,623 margin lost; £416 offer cost if all retained).

> The shadow strategy net gain is small because all no-offer churns were residential customers with low margins. I&C customers (large margins) already received retention offers — the current threshold strategy is near-optimal for the existing portfolio composition.

## Ofgem FRA Regulatory Capital Ratio (Phase NZ)

Equity / (annual revenue ÷ 12). Ofgem FRA minimum: ≥ 1x monthly revenue.
Sector best practice: ≥ 6x (GREEN). Early warning: < 3x (AMBER). Non-compliant: < 1x (RED).
Real-world context: Bulb 2021 collapse at ~-0.01x; Igloo 2021 ~0.07x.

| Year | Equity | Monthly Rev | FRA Ratio | RAG | Compliant |
|------|--------|-------------|-----------|-----|-----------|
| 2016 | £2,473,581.11 | £1,279.55 | 1933.2x | ✓ GREEN | Yes |
| 2017 | £2,590,238.47 | £29,052.54 | 89.2x | ✓ GREEN | Yes |
| 2018 | £2,840,461.34 | £50,079.42 | 56.7x | ✓ GREEN | Yes |
| 2019 | £3,510,680.54 | £137,121.01 | 25.6x | ✓ GREEN | Yes |
| 2020 | £4,263,301.67 | £154,758.03 | 27.6x | ✓ GREEN | Yes |
| 2021 | £4,977,644.98 | £201,778.67 | 24.7x | ✓ GREEN | Yes |
| 2022 | £5,930,261.96 | £353,797.13 | 16.8x | ✓ GREEN | Yes |
| 2023 | £6,817,903.47 | £291,313.47 | 23.4x | ✓ GREEN | Yes |
| 2024 | £7,998,172.05 | £249,935.16 | 32.0x | ✓ GREEN | Yes |
| 2025 | £8,478,280.23 | £102,757.00 | 82.5x | ✓ GREEN | Yes |

**Weakest year:** 2022 — 16.8x (equity £5,930,261.96 vs monthly revenue £353,797.13). RAG: GREEN.
**Strongest year:** 2016 — 1933.2x.

## I&C Broker / TPI Commission (Phase OA)

I&C customers procure electricity via energy brokers. Commission rate: £1.5/MWh (0.15p/kWh — standard for large I&C per Ofgem TPI register data).

| Year | Deals | Consumption (MWh) | Commission £ |
|------|-------|-------------------|--------------|
| 2016 | 0 | 0 | £0 |
| 2017 | 1 | 1,983 | £2,974 |
| 2018 | 2 | 2,986 | £4,478 |
| 2019 | 3 | 6,987 | £10,481 |
| 2020 | 4 | 10,016 | £15,024 |
| 2021 | 4 | 9,907 | £14,860 |
| 2022 | 4 | 9,868 | £14,802 |
| 2023 | 4 | 9,883 | £14,825 |
| 2024 | 4 | 9,929 | £14,894 |
| 2025 | 4 | 4,239 | £6,358 |
|------|-------|-------------------|--------------|
| **Total** | **30** | | **£98,698** |

**Total broker commission 2016–2025:** £98,698

_Note: This cost was previously unmodelled — I&C gross margin was overstated by this amount._
## Elexon Settlement Reconciliation Exposure (Phase OB)

UK electricity suppliers receive reconciliation adjustments via R1/R2/R3/RF runs (1, 3, 5, 28 months after delivery). 60% resolved at R1; 3% tail into RF.
HH meters (I&C): ±0.5% variance. Non-HH (resi/SME): ±4%. Portfolio: ~90% HH.
Zero-mean: adjustments go both ways. Crisis years bias toward supplier credit.

| Year | Revenue £ | Pool Outstanding £ | Max Adverse £ | RAG | Crisis |
|------|-----------|---------------------|---------------|-----|--------|
| 2016 | £15,354.61 | £5,706.80 | £48.51 | ✓ GREEN |  |
| 2017 | £348,630.52 | £129,574.34 | £1,101.38 | ✓ GREEN |  |
| 2018 | £600,953.01 | £223,354.20 | £1,898.51 | ✓ GREEN |  |
| 2019 | £1,645,452.10 | £611,559.70 | £5,198.26 | ✓ GREEN |  |
| 2020 | £1,857,096.31 | £690,220.80 | £5,866.88 | ✓ GREEN |  |
| 2021 | £2,421,344.01 | £899,932.86 | £7,649.43 | ✓ GREEN | CREDIT EXPECTED |
| 2022 | £4,245,565.53 | £1,577,935.19 | £13,412.45 | ✓ GREEN | CREDIT EXPECTED |
| 2023 | £3,495,761.69 | £1,299,258.10 | £11,043.69 | ✓ GREEN |  |
| 2024 | £2,999,221.95 | £1,114,710.82 | £9,475.04 | ✓ GREEN |  |
| 2025 | £1,233,083.98 | £458,296.21 | £3,895.52 | ✓ GREEN |  |

**Peak reconciliation exposure:** 2022 — max adverse £13,412 (4.5 months weighted tail).

_Note: Outstanding pool ≈ current-year revenue × (weighted outstanding months ÷ 12)._
_Max adverse = pool × blended variance rate (0.5% HH + 4% non-HH, portfolio-weighted)._
## Ofgem Supply Licence Health (Phase OC)

Annual licence health checks: customer base, net assets, liquidity, bad debt.
Breach triggers board escalation and Ofgem notification under SLC 0.
WATCH = within 20% of threshold. BREACH = threshold crossed.

| Year | Customers | Net Assets | Treasury | Cash Wks | Bad Debt % | Overall |
|------|-----------|------------|----------|----------|------------|---------|
| 2016 | 13 | £2,473,581.11 | £2,467,424.50 | 35675w | 1.60% | ✗ BREACH |
| 2017 | 14 | £2,590,238.47 | £2,497,718.04 | 1170w | 0.59% | ✗ BREACH |
| 2018 | 15 | £2,840,461.34 | £2,486,406.51 | 748w | 0.55% | ✗ BREACH |
| 2019 | 17 | £3,510,680.54 | £2,606,406.14 | 273w | 0.52% | ✗ BREACH |
| 2020 | 19 | £4,263,301.67 | £2,914,252.99 | 351w | 0.51% | ✗ BREACH |
| 2021 | 15 | £4,977,644.98 | £2,943,329.55 | 157w | 0.53% | ✗ BREACH |
| 2022 | 17 | £5,930,261.96 | £3,135,960.69 | 68w | 1.05% | ✗ BREACH |
| 2023 | 14 | £6,817,903.47 | £3,336,256.48 | 106w | 0.55% | ✗ BREACH |
| 2024 | 14 | £7,998,172.05 | £3,710,669.07 | 207w | 0.53% | ✗ BREACH |
| 2025 | 11 | £8,478,280.23 | £3,760,599.46 | 432w | 0.52% | ✗ BREACH |

**BREACH years:** 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025 — board escalation required.

_Note: Complaints from contact model avg_complaint_probability. Customer count <50 triggers Ofgem viability review — small-portfolio years will show WATCH._
## Ofgem SLC Compliance Scorecard (Phase OD)

10 compliance domains per year, derived from simulation outputs.
G = GREEN (compliant), A = AMBER (watch), R = RED (breach).

| Domain | SLC Ref | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|--------|---------|------|------|------|------|------|------|------|------|------|------|
| Governance | SLC 0-9 | G | G | G | G | G | G | G | G | G | G |
| Billing/Metering | SLC 10-14 | G | G | G | G | G | G | A | G | G | A |
| Payment/Debt | SLC 15-19 | A | G | G | G | G | G | A | G | G | G |
| Information | SLC 20-24 | G | G | G | G | G | G | G | G | G | G |
| Complaints | SLC 25-29 / Ofgem Time to Fix rules | A | A | A | A | A | A | R | R | A | R |
| Vulnerable Cust | SLC 30-35 / PSR | G | G | G | G | G | G | G | G | G | G |
| Tariff/Cap | SLC 36-40 / Default Tariff Cap | G | G | G | G | G | G | G | G | G | G |
| Environmental | SLC 41-50 / RO, CfD, EE obligation | G | G | G | G | G | G | G | G | G | G |
| Network/BSC | SLC 51-60 / BSC obligations | G | G | G | G | G | G | G | G | G | G |
| Financial Res. | SLC 4C / SFR Decision 2023 | G | G | G | G | G | G | G | G | G | G |
| **Overall** |  | A | A | A | A | A | A | R | R | A | R |

**Breach years (RED):** 2022, 2023, 2025
**Watch years (AMBER):** 2016, 2017, 2018, 2019, 2020, 2021, 2024

_Note: Vulnerable customers, tariff/cap, and environmental domains defaulted to GREEN_
_(these are modelled as compliant; detailed SLC breach simulation not yet implemented)._
## Ofgem Annual Supply Return (Phase OE)

UK suppliers must file annual supply returns to Ofgem. Filed by 31 March of the following year.

| Year | Submitted | Customers (R/SME/I&C) | Elec GWh | Gas GWh | Bad Debt/Cust |
|------|-----------|----------------------|----------|---------|---------------|
| 2016 | Yes | 13/13/13 | 0.1 | 0.0 | £13 |
| 2017 | Yes | 14/14/14 | 1.5 | 0.1 | £98 |
| 2018 | Yes | 15/15/15 | 2.9 | 0.1 | £159 |
| 2019 | Yes | 17/17/17 | 7.1 | 2.8 | £365 |
| 2020 | Yes | 19/19/19 | 7.3 | 2.4 | £331 |
| 2021 | Yes | 15/15/15 | 9.6 | 6.0 | £610 |
| 2022 | Yes | 17/17/17 | 19.0 | 11.8 | £2119 |
| 2023 | Yes | 14/14/14 | 15.5 | 5.9 | £1030 |
| 2024 | Yes | 14/14/14 | 12.8 | 5.4 | £822 |
| 2025 | Yes | 11/11/11 | 5.6 | 2.6 | £457 |

**All 10 annual returns filed** — full compliance 2016–2025.

_Note: WHD and GSOP metrics default to zero (not yet modelled in detail)._
_Volume GWh estimated from revenue at average unit rate proxies (£150/MWh elec, £50/MWh gas)._
## GSOP Obligations (Phase OF)

Guaranteed Standards of Performance — GBP 30 per breach (Ofgem-mandated).

No GSOP obligations triggered in 2016-2025 window.
_Small portfolio with low complaint and churn volumes falls below estimated trigger thresholds._
## Renewable Obligation (RO) Cost Observatory

UK suppliers must surrender ROCs (or pay buy-out price) by 1 September each year.
ROC buy-out cost is the maximum supplier exposure; ROC market purchases reduce actual cost.

| Year | Elec MWh | Obligation Level | ROCs Required | Buy-out Price | Buy-out Cost |
|------|----------|-----------------|--------------|--------------|-------------|
| 2016 | 74.5 | 0.317 ROC/MWh | 23.6 | £43.30 | £1,023 |
| 2017 | 2,082.1 | 0.334 ROC/MWh | 695.4 | £44.77 | £31,134 |
| 2018 | 3,086.0 | 0.342 ROC/MWh | 1,055.4 | £46.43 | £49,003 |
| 2019 | 7,088.2 | 0.351 ROC/MWh | 2,488.0 | £47.22 | £117,481 |
| 2020 | 10,111.8 | 0.358 ROC/MWh | 3,620.0 | £48.78 | £176,585 |
| 2021 | 10,006.6 | 0.364 ROC/MWh | 3,642.4 | £50.80 | £185,034 |
| 2022 | 9,965.4 | 0.370 ROC/MWh | 3,687.2 | £52.88 | £194,979 |
| 2023 | 9,982.9 | 0.376 ROC/MWh | 3,753.6 | £54.35 | £204,007 |
| 2024 | 10,011.6 | 0.382 ROC/MWh | 3,824.4 | £56.19 | £214,895 |
| 2025 | 4,277.0 | 0.389 ROC/MWh | 1,663.8 | £58.10 | £96,664 |
| **Total** | **66,686.1** | | | | **£1,270,805** |

RO cost as % of total revenue (2016-2025): **6.7%** (industry benchmark 5-10%)

> Note: actual RO cost depends on ROC market prices. Buy-out price is the regulatory ceiling.
## Feed-in Tariff (FiT) Levelisation Levy

Ofgem FiT levelisation redistributes FiT payment obligations across all licensed suppliers
(proportional to electricity supplied). FiT scheme closed to new applicants 2019-03-31.

| Year | Elec MWh | Levy Rate (GBP/MWh) | FiT Levy Cost |
|------|----------|---------------------|--------------|
| 2016 | 74.5 | GBP8.36 | GBP622.60 |
| 2017 | 2,082.1 | GBP9.19 | GBP19,134.80 |
| 2018 | 3,086.0 | GBP9.40 | GBP29,008.53 |
| 2019 | 7,088.2 | GBP9.45 | GBP66,983.17 |
| 2020 | 10,111.8 | GBP0.00 (scheme closed) | NIL |
| 2021 | 10,006.6 | GBP0.00 (scheme closed) | NIL |
| 2022 | 9,965.4 | GBP0.00 (scheme closed) | NIL |
| 2023 | 9,982.9 | GBP0.00 (scheme closed) | NIL |
| 2024 | 10,011.6 | GBP0.00 (scheme closed) | NIL |
| 2025 | 4,277.0 | GBP0.00 (scheme closed) | NIL |
| **Total** | | | **GBP115,749.10** |

FiT levy as % of total revenue (levy years 2016-2019): **0.6%** (industry benchmark ~1-2%)

> FiT levy ended 2019-20. Post-2019 cost is NIL as levelisation rates fell to zero.
## Climate Change Levy (CCL) Observatory

CCL is charged on business energy consumption and remitted to HMRC quarterly.
Residential customers are fully exempt. I&C customers pay at HMRC annual rates.
CCL is a pass-through: collected from customers, remitted to HMRC (no net P&L impact).

| Year | Elec kWh | Elec Rate (p/kWh) | CCL Elec | Gas kWh | Gas Rate | CCL Gas | Total CCL |
|------|----------|------------------|----------|---------|----------|---------|----------|
| 2016 | 0 | 0.554p | GBP0.00 | 0 | 0.195p | GBP0.00 | GBP0.00 |
| 2017 | 1,982,966 | 0.568p | GBP11,263.25 | 0 | 0.198p | GBP0.00 | GBP11,263.25 |
| 2018 | 2,985,506 | 0.583p | GBP17,405.50 | 0 | 0.203p | GBP0.00 | GBP17,405.50 |
| 2019 (*) | 6,987,285 | 0.847p | GBP59,182.30 | 4,999,959 | 0.339p | GBP16,949.86 | GBP76,132.16 |
| 2020 | 10,016,266 | 0.811p | GBP81,231.91 | 5,015,381 | 0.406p | GBP20,362.45 | GBP101,594.36 |
| 2021 | 9,906,804 | 0.775p | GBP76,777.73 | 4,999,959 | 0.465p | GBP23,249.81 | GBP100,027.54 |
| 2022 | 9,868,318 | 0.775p | GBP76,479.47 | 4,999,959 | 0.465p | GBP23,249.81 | GBP99,729.28 |
| 2023 | 9,883,290 | 0.775p | GBP76,595.50 | 4,999,959 | 0.465p | GBP23,249.81 | GBP99,845.31 |
| 2024 | 9,929,315 | 0.775p | GBP76,952.19 | 5,015,381 | 0.465p | GBP23,321.52 | GBP100,273.71 |
| 2025 | 4,238,894 | 0.775p | GBP32,851.43 | 2,224,893 | 0.465p | GBP10,345.75 | GBP43,197.18 |
| **Total** | | | | | | | **GBP649,468.29** |

(*) 2019: electricity CCL +45% (0.583->0.847p/kWh), gas +67% (0.203->0.339p/kWh) -- Budget 2018 carbon tax shift.

> Quarterly HMRC remittance obligation per CCLQuarterlyReturn. Pass-through: no net supplier P&L impact.
## Warm Home Discount (WHD) Liability Observatory

WHD is mandatory for suppliers with 150,000+ domestic customers.
Eligible customers receive a GBP 140-150 rebate applied to their electricity bill.

| Year | Domestic Customers | WHD Threshold | Status | Rebate/Customer | Liability |
|------|-------------------|--------------|--------|----------------|---------|
| 2016 | 13 | 150,000 | OK (exempt) | N/A | NIL |
| 2017 | 13 | 150,000 | OK (exempt) | N/A | NIL |
| 2018 | 13 | 150,000 | OK (exempt) | N/A | NIL |
| 2019 | 13 | 150,000 | OK (exempt) | N/A | NIL |
| 2020 | 14 | 150,000 | OK (exempt) | N/A | NIL |
| 2021 | 10 | 150,000 | OK (exempt) | N/A | NIL |
| 2022 | 12 | 150,000 | OK (exempt) | N/A | NIL |
| 2023 | 9 | 150,000 | OK (exempt) | N/A | NIL |
| 2024 | 9 | 150,000 | OK (exempt) | N/A | NIL |
| 2025 | 6 | 150,000 | OK (exempt) | N/A | NIL |

> Portfolio is primarily I&C. Domestic customer count is far below WHD threshold -- no obligation to participate.
> If domestic portfolio grows to 150,000+, WHD registration with Ofgem becomes mandatory.
## Energy Company Obligation (ECO) Observatory

ECO requires suppliers with 150,000+ domestic customers to fund home energy efficiency upgrades.
Phases: ECO2 (2015-2018, GBP3.20/MWh), ECO3 (2018-2022, GBP4.50/MWh), ECO4 (2022-2026, GBP6.80/MWh).

| Year | ECO Phase | Rate (GBP/MWh) | Domestic Cust | Status | Counterfactual Liability |
|------|----------|---------------|--------------|--------|------------------------|
| 2016 | ECO2 | GBP3.20 | 13 | OK (exempt) | GBP0 |
| 2017 | ECO2 | GBP3.20 | 13 | OK (exempt) | GBP7 |
| 2018 | ECO3 | GBP4.50 | 13 | OK (exempt) | GBP18 |
| 2019 | ECO3 | GBP4.50 | 13 | OK (exempt) | GBP49 |
| 2020 | ECO3 | GBP4.50 | 14 | OK (exempt) | GBP56 |
| 2021 | ECO3 | GBP4.50 | 10 | OK (exempt) | GBP73 |
| 2022 | ECO4 | GBP6.80 | 12 | OK (exempt) | GBP192 |
| 2023 | ECO4 | GBP6.80 | 9 | OK (exempt) | GBP158 |
| 2024 | ECO4 | GBP6.80 | 9 | OK (exempt) | GBP136 |
| 2025 | ECO4 | GBP6.80 | 6 | OK (exempt) | GBP56 |

Counterfactual total 2016-2025 (if 150k domestic): **GBP745**

> Actual ECO liability: NIL -- domestic customer count is far below threshold.
> Counterfactual shows obligation rate if portfolio scaled to 150,000 domestic customers.
## Carbon Emissions Reporting Observatory

Scope 2 emissions from customer electricity consumption (UK grid emission intensity).
Scope 1 emissions from gas supply (183g CO2/kWh). Source: DESNZ/National Grid annual fuel mix data.

| Year | Elec MWh | Grid Intensity | Elec CO2 (t) | Gas MWh | Gas CO2 (t) | Total CO2 (t) | Low Carbon % |
|------|----------|---------------|-------------|---------|------------|-------------|-------------|
| 2016 | 0 | 315g/kWh | 0.0 | 0 | 0.0 | 0.0 | 45% |
| 2017 | 2 | 290g/kWh | 0.7 | 0 | 0.0 | 0.7 | 49% |
| 2018 | 4 | 274g/kWh | 1.1 | 0 | 0.1 | 1.2 | 51% |
| 2019 | 11 | 244g/kWh | 2.7 | 1 | 0.2 | 2.9 | 57% |
| 2020 | 12 | 225g/kWh | 2.8 | 1 | 0.2 | 3.0 | 59% (decarbonising) |
| 2021 | 16 | 243g/kWh | 3.9 | 2 | 0.3 | 4.2 | 56% (decarbonising) |
| 2022 | 28 | 237g/kWh | 6.7 | 3 | 0.5 | 7.2 | 57% (decarbonising) |
| 2023 | 23 | 219g/kWh | 5.1 | 2 | 0.4 | 5.5 | 59% (decarbonising) |
| 2024 | 20 | 196g/kWh | 3.9 | 2 | 0.4 | 4.3 | 64% (decarbonising) |
| 2025 | 8 | 175g/kWh | 1.4 | 1 | 0.2 | 1.6 | 68% (decarbonising) |
| **Total** | | | | | | **30.6 t** | |

> Grid emission intensity declining: 2016 ~290g/kWh -> 2025 ~175g/kWh (40% reduction). Carbon disclosure per SECR/ESOS.
## Risk Committee Activity (2016-2025)

Committee wake-up sessions: triggered when VaR stress ratio exceeds mandate threshold.

| Year | Sessions | Peak VaR (current) £ | Peak VaR (stressed) £ | Accounts touched |
|------|----------|----------------------|----------------------|-----------------|
| 2016 | 13 | £28 | £9 | 1 |
| 2017 | 12 | £1,005 | £401 | 3 |
| 2022 | 9 | £55,609 | £20,607 | 7 |
| 2023 | 4 | £128,380 | £48,915 | 10 |

**Total sessions 2016-2025: 38** | Busiest year: 2016 (13 sessions)
Peak VaR observed: 2023 at £128,380 | Unique accounts ever adjusted: 11

**Most frequently adjusted accounts:**
- C1: 22 sessions
- C5: 16 sessions
- C7: 16 sessions
- C2: 13 sessions
- C6: 12 sessions

> Risk committee wake-ups are documented in `docs/observability/run_history.json`.

## Customer Strategic Value Matrix

2x2 matrix: CLV (above/below median) × Churn probability (above/below median).
Median CLV: £12,017.28 | Median churn: 32% | Total portfolio CLV: £8,812,104.53

### PROTECT (High CLV, Low Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C_IC1 | £1,979,417.19 | 29% | 20.2 periods |
| C_IC4 | £1,834,396.57 | 20% | 19.3 periods |
| C6 | £22,350.07 | 29% | 19.8 periods |
| C9 | £12,017.28 | 26% | 25.9 periods |

Quadrant CLV: £3,848,181.10 (44% of portfolio)

### CRITICAL (High CLV, High Churn — priority intervention)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C_IC3 | £3,764,767.63 | 41% | 28.4 periods |
| C_IC2 | £1,141,168.85 | 32% | 23.1 periods |
| C5 | £14,409.65 | 38% | 26.7 periods |

Quadrant CLV: £4,920,346.12 (56% of portfolio)

### MONITOR (Low CLV, Low Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C7 | £9,218.57 | 29% | 19.3 periods |
| C3 | £6,823.79 | 11% | 17.9 periods |

Quadrant CLV: £16,042.37 (0% of portfolio)

### EXIT (Low CLV, High Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C8 | £10,789.22 | 32% | 19.4 periods |
| C2 | £7,339.85 | 38% | 23.8 periods |
| C1 | £5,484.28 | 38% | 19.5 periods |
| C4 | £3,921.60 | 38% | 17.4 periods |

Quadrant CLV: £27,534.94 (0% of portfolio)

**Board action: CRITICAL quadrant has 3 account(s). High CLV at risk from elevated churn probability. Immediate retention offers recommended.**

## Customer Experience & Service Quality

| Year | Billing Clarity | Complaint Prob | Acq Attempts | Acq Wins | Flag |
|------|----------------|---------------|-------------|---------|------|
| 2016 | 0.829 | 0.047 | 0 | 0 |  |
| 2017 | 0.818 | 0.047 | 0 | 0 |  |
| 2018 | 0.810 | 0.047 | 0 | 0 |  |
| 2019 | 0.824 | 0.047 | 0 | 0 |  |
| 2020 | 0.831 | 0.043 | 1 | 0 |  |
| 2021 | 0.817 | 0.048 | 0 | 0 |  |
| 2022 | 0.783 | 0.058 | 0 | 0 | **LOW CLARITY** |
| 2023 | 0.801 | 0.050 | 0 | 0 |  |
| 2024 | 0.806 | 0.048 | 2 | 0 |  |
| 2025 | 0.768 | 0.061 | 0 | 0 | **LOW CLARITY** |

**Overall service quality:** 90.3% | **Average billing clarity:** 0.811 | **Average complaint probability:** 0.049

**Acquisition performance:** 3 attempts, 0 wins (0% win rate). No new customers acquired — cap-constrained gate blocked resi acquisition 2021-2023 (negative projected margin).

**Lowest clarity: 2025** (0.768) — crisis complexity (multiple tariff changes, bill shock events) degraded statement clarity.

## Bill Shock Analysis

Bill shock events occur when a customer's bill increases >20% vs the prior bill.
Regulatory context: Ofgem monitors bill shock as a consumer harm indicator.

| Year | Avg Shock % | Events | Bills | Shock Rate | Flag |
|------|------------|--------|-------|------------|------|
| 2016 | 19.7% | 31 | 108 | 29% |  |
| 2017 | 16.5% | 50 | 168 | 30% |  |
| 2018 | 16.0% | 60 | 180 | 33% |  |
| 2019 | 17.1% | 66 | 204 | 32% |  |
| 2020 | 14.4% | 53 | 205 | 26% |  |
| 2021 | 23.6% | 52 | 180 | 29% | ELEVATED |
| 2022 | 33.9% | 76 | 173 | 44% | **HIGH** |
| 2023 | 30.1% | 53 | 168 | 32% | **HIGH** |
| 2024 | 17.0% | 45 | 153 | 29% |  |
| 2025 | 24.7% | 25 | 66 | 38% | ELEVATED |

**Crisis peak: 2022** — 33.9% average shock. Energy crisis drove wholesale costs above locked tariff rates,
causing step-change increases at every renewal. SLC 21: suppliers must issue
renewal notice 42 days before contract end, giving customers time to switch.

## Policy Cost & Levy Breakdown

UK energy levies collected through supplier bills. Policy costs are non-commodity costs
passed through to customers. CfD levy went negative in 2022 (crisis: spot exceeded strike prices;
renewable generators repaid back via levy mechanism).

| Year | RO | CfD | CCL | CM | FiT | Total Policy | Network |
|------|----|-----|-----|----|-----|-------------|---------|
| 2016 | £1,161.79 | £7.45 | £189.19 | £37.24 | £305.34 | £1,701.01 | £3,202.38 |
| 2017 | £37,159.19 | £2,706.77 | £11,164.93 | £1,976.65 | £9,940.12 | £62,947.66 | £26,175.96 |
| 2018 | £65,510.23 | £9,875.24 | £17,433.71 | £9,349.95 | £17,283.87 | £119,453.00 | £38,554.65 |
| 2019 | £164,624.73 | £28,352.67 | £42,460.21 | £31,969.18 | £44,301.87 | £311,708.66 | £88,387.10 |
| 2020 | £238,638.15 | £35,391.25 | £69,454.47 | £56,550.37 | £70,024.25 | £470,058.49 | £124,589.13 |
| 2021 | £246,701.82 | £15,009.92 | £71,336.24 | £49,674.92 | £62,836.38 | £486,986.67 | £123,772.40 |
| 2022 | £256,667.15 | **£-49,827.22** | £71,047.02 | £36,748.27 | £69,230.82 | £483,520.48 | £134,698.46 |
| 2023 | £272,367.84 | £64,888.73 | £71,830.95 | £51,052.83 | £75,239.96 | £549,156.68 | £140,893.74 |
| 2024 | £308,161.53 | £110,127.47 | £72,943.93 | £68,825.93 | £82,706.97 | £644,768.14 | £144,687.24 |
| 2025 | £136,009.92 | £47,047.46 | £31,221.29 | £31,094.09 | £36,226.54 | £282,454.70 | £61,976.68 |

**CfD rebate in 2022:** Contracts for Difference (CfD) generators are paid
the difference between strike price and reference price. When spot > strike (2022 crisis),
the mechanism reverses — generators pay back, creating a negative levy for suppliers.

Policy costs: £1,701.01 (2016) → £282,454.70 (2025). CAGR: 76.5%.

## Electricity vs Gas P&L Split

Year-by-year net margin by fuel. Gas became structurally loss-making from 2021.

| Year | Elec Net | Gas Net | Elec Rev | Gas Rev | Gas Share of Rev | Gas Profitable |
|------|----------|---------|----------|---------|-----------------|---------------|
| 2016 | £881.72 | £296.53 | £9,021.95 | £1,388.28 | 13.3% | YES |
| 2017 | £30,102.71 | £463.34 | £231,632.96 | £2,660.42 | 1.1% | YES |
| 2018 | £99,331.51 | £374.66 | £432,208.83 | £3,113.94 | 0.7% | YES |
| 2019 | £218,118.22 | £9,754.19 | £1,060,498.38 | £137,766.14 | 11.5% | YES |
| 2020 | £112,364.37 | £9,852.53 | £1,102,256.74 | £121,119.88 | 9.9% | YES |
| 2021 | £59,643.53 | £8,285.14 | £1,441,837.83 | £297,399.17 | 17.1% | YES |
| 2022 | £297,372.89 | £2,832.97 | £2,853,337.99 | £588,329.77 | 17.1% | YES |
| 2023 | £139,991.71 | £7,361.94 | £2,318,669.69 | £297,197.78 | 11.4% | YES |
| 2024 | £321,078.45 | £9,081.83 | £1,916,445.67 | £270,490.62 | 12.4% | YES |
| 2025 | £114,281.92 | £3,787.52 | £842,746.26 | £132,453.71 | 13.6% | YES |

**Gas supply has been profitable throughout** (10 years).

## Gas Supply Exit Decision Analysis (Phase AR/AS)

Models three strategic scenarios for the board regarding gas supply legs.
Inputs: company billing records (per_cid_comm_pnl). Gas capital = hedge cost applied to gas leg.

### Scenario Comparison (Dual-Fuel Portfolio Only)

| Scenario | Portfolio Net | vs Status Quo | Action |
|----------|--------------|---------------|--------|
| STATUS_QUO | £169,259.78 | — | Current strategy |
| EXIT_GAS | £70,596.68 | £-98,663.10 | Remove gas; model elec churn risk |
| REPRICE_GAS | £171,289.63 | £2,029.86 | Raise gas tariff to break-even |

**Recommended action: REPRICE_GAS**

### Loss-Making Gas Accounts

| Account | Gas Net | Gas ROC | Revenue Uplift Needed |
|---------|---------|---------|----------------------|
| C4g | £-2,029.86 | -14.02x | +19.6% |

**Accretive gas accounts:** C1g (£620.41), C2g (£801.77), C3g (£282.80), C_IC3g (£52,415.53) — these gas legs support customer retention without capital destruction.

**Board Decision:**
- Exit gas: I&C customers at 40% electricity churn risk when gas removed (relationship loss)
- Reprice gas: increases customer cost but eliminates capital destruction
- Status quo: unsustainable — gas legs destroying £52091 in net value

## Segment Capital Efficiency (Return-on-Capital)

Lifetime net margin and capital deployed per segment.
ROC = lifetime net / lifetime capital. ROC < 0 = capital destroyer.

| Segment | Lifetime Gross | Capital Deployed | Lifetime Net | ROC | Signal |
|---------|---------------|------------------|--------------|-----|--------|
| I&C electricity | £5,724,619.17 | £50,103.96 | £1,385,157.72 | 27.6x | Strong |
| I&C gas | £622,647.03 | £0.00 | £52,415.53 | 0.0x | Low return |
| SME electricity | £40,768.05 | £484.47 | £4,075.71 | 8.4x | Moderate |
| resi electricity | £58,551.31 | £646.88 | £3,933.58 | 6.1x | Moderate |
| resi gas | £6,016.94 | £197.67 | £-324.89 | -1.6x | CAPITAL DESTROYER |

## Portfolio Concentration Risk

Revenue concentration analysis across 21 margin-positive accounts. Herfindahl-Hirschman Index (HHI): **2244** — MODERATE (1,500-2,500).

**Segment Margin Share:**
- I&C: £6,264,005.57 (98.5% of total positive margin)
- resi: £58,871.08 (0.9% of total positive margin)
- SME: £37,945.75 (0.6% of total positive margin)

**Top 5 Accounts by Margin Contribution:**

| Account | Segment | Lifetime Margin | Share | Latest Churn Risk | Margin at Risk |
|---------|---------|-----------------|-------|-------------------|----------------|
| C_IC1 | I&C | £1,854,831.25 | 29.2% | 4% | £74,749.70 |
| C_IC3 | I&C | £1,807,029.46 | 28.4% | 20% | £366,646.28 |
| C_IC4 | I&C | £1,090,243.56 | 17.1% | 0% | £0.00 |
| C_IC2 | I&C | £898,484.24 | 14.1% | 4% | £32,974.37 |
| C_IC3g | I&C | £613,417.06 | 9.6% | 0% | £0.00 |

**Concentration Risk Warning:**
- I&C segment accounts for 98.5% of total portfolio margin
- Resi and SME segments are effectively margin-neutral at portfolio scale
- A single large I&C departure would remove 14-29% of all margin
- Board action: diversify acquisition pipeline toward profitable resi/SME to reduce I&C dependency

## Portfolio Learning Premium (Phase 17a + 19a)

Company applied portfolio premium adjustments at 117 renewal(s) (25 gas) based on recent portfolio-wide margin rates: 63 surcharge(s), 54 discount(s).

| Customer | Commodity | Term start | Mean recent margin | Portfolio premium | Rate before | Rate after |
|----------|-----------|------------|-------------------|-------------------|------------|-----------|
| C1 | electricity | 2016-12-31 | 7.4% | +0.3% | £131.49/MWh | £131.86/MWh |
| C1g | gas | 2016-12-31 | 19.6% | -5.0% | £27.63/MWh | £26.25/MWh |
| C5 | electricity | 2016-12-31 | 8.7% | -0.4% | £131.49/MWh | £131.01/MWh |
| C7 | electricity | 2016-12-31 | 9.4% | -0.7% | £131.49/MWh | £130.56/MWh |
| C2 | electricity | 2017-04-01 | 11.5% | -1.7% | £127.97/MWh | £125.75/MWh |
| C2g | gas | 2017-04-01 | 19.8% | -5.0% | £34.54/MWh | £32.81/MWh |
| C6 | electricity | 2017-04-01 | 9.7% | -0.8% | £127.97/MWh | £126.89/MWh |
| C8 | electricity | 2017-04-01 | 9.0% | -0.5% | £127.97/MWh | £127.35/MWh |
| C3 | electricity | 2017-07-01 | 10.4% | -1.2% | £122.23/MWh | £120.78/MWh |
| C3g | gas | 2017-07-01 | 20.5% | -5.0% | £24.33/MWh | £23.11/MWh |
| C9 | electricity | 2017-07-01 | 10.1% | -1.1% | £122.23/MWh | £120.94/MWh |
| C4 | electricity | 2017-10-01 | 11.1% | -1.6% | £111.62/MWh | £109.87/MWh |
| C4g | gas | 2017-10-01 | 18.4% | -5.0% | £27.48/MWh | £26.10/MWh |
| C1 | electricity | 2017-12-31 | 12.1% | -2.0% | £120.10/MWh | £117.65/MWh |
| C1g | gas | 2017-12-31 | 15.4% | -3.7% | £34.79/MWh | £33.49/MWh |
| C5 | electricity | 2017-12-31 | 9.0% | -0.5% | £120.10/MWh | £119.51/MWh |
| C7 | electricity | 2017-12-31 | 3.7% | +2.1% | £120.10/MWh | £122.67/MWh |
| C_IC1 | electricity | 2018-01-31 | -18.2% | +13.1% | £112.24/MWh | £126.93/MWh |
| C2 | electricity | 2018-04-01 | -6.9% | +7.5% | £133.89/MWh | £143.89/MWh |
| C2g | gas | 2018-04-01 | 15.4% | -3.7% | £38.21/MWh | £36.79/MWh |
| C6 | electricity | 2018-04-01 | -4.4% | +6.2% | £133.89/MWh | £142.17/MWh |
| C8 | electricity | 2018-04-01 | 8.2% | -0.1% | £133.89/MWh | £133.79/MWh |
| C3 | electricity | 2018-07-01 | 10.2% | -1.1% | £128.29/MWh | £126.90/MWh |
| C3g | gas | 2018-07-01 | 13.6% | -2.8% | £29.63/MWh | £28.80/MWh |
| C9 | electricity | 2018-07-01 | 1.8% | +3.1% | £128.29/MWh | £132.25/MWh |
| C4 | electricity | 2018-10-01 | 2.0% | +3.0% | £145.00/MWh | £149.37/MWh |
| C4g | gas | 2018-10-01 | 13.7% | -2.8% | £34.60/MWh | £33.61/MWh |
| C1 | electricity | 2018-12-31 | 6.7% | +0.7% | £148.68/MWh | £149.68/MWh |
| C1g | gas | 2018-12-31 | 13.9% | -3.0% | £37.15/MWh | £36.05/MWh |
| C5 | electricity | 2018-12-31 | 9.2% | -0.6% | £148.68/MWh | £147.78/MWh |
| C7 | electricity | 2018-12-31 | 9.6% | -0.8% | £148.68/MWh | £147.52/MWh |
| C_IC2 | electricity | 2019-01-31 | -30.2% | +15.0% | £134.57/MWh | £154.76/MWh |
| C_IC1 | electricity | 2019-03-02 | -20.5% | +14.2% | £128.22/MWh | £146.50/MWh |
| C2 | electricity | 2019-04-01 | 3.2% | +2.4% | £148.35/MWh | £151.90/MWh |
| C2g | gas | 2019-04-01 | 10.4% | -1.2% | £32.94/MWh | £32.54/MWh |
| C6 | electricity | 2019-04-01 | 7.5% | +0.2% | £148.35/MWh | £148.72/MWh |
| C8 | electricity | 2019-04-01 | 27.0% | -5.0% | £148.35/MWh | £140.93/MWh |
| C3 | electricity | 2019-07-01 | 19.5% | -5.0% | £127.03/MWh | £120.68/MWh |
| C3g | gas | 2019-07-01 | 13.2% | -2.6% | £23.62/MWh | £23.00/MWh |
| C9 | electricity | 2019-07-01 | 10.0% | -1.0% | £127.03/MWh | £125.75/MWh |
| C4 | electricity | 2019-10-01 | 7.9% | +0.0% | £126.72/MWh | £126.76/MWh |
| C4g | gas | 2019-10-01 | 17.2% | -4.6% | £20.41/MWh | £19.47/MWh |
| C1 | electricity | 2019-12-31 | 10.5% | -1.3% | £127.44/MWh | £125.83/MWh |
| C1g | gas | 2019-12-31 | 14.4% | -3.2% | £26.17/MWh | £25.33/MWh |
| C5 | electricity | 2019-12-31 | 10.1% | -1.1% | £127.44/MWh | £126.10/MWh |
| C7 | electricity | 2019-12-31 | 8.9% | -0.4% | £127.44/MWh | £126.88/MWh |
| C_IC3 | electricity | 2020-01-01 | 7.5% | +0.3% | £47.59/MWh | £47.71/MWh |
| C_IC3g | gas | 2020-01-01 | 20.8% | -5.0% | £16.25/MWh | £15.44/MWh |
| C_IC2 | electricity | 2020-03-01 | -59.4% | +15.0% | £92.92/MWh | £106.85/MWh |
| C2 | electricity | 2020-03-31 | -52.0% | +15.0% | £125.12/MWh | £143.89/MWh |
| C2g | gas | 2020-03-31 | 18.7% | -5.0% | £22.80/MWh | £21.66/MWh |
| C6 | electricity | 2020-03-31 | -47.4% | +15.0% | £125.12/MWh | £143.89/MWh |
| C8 | electricity | 2020-03-31 | -16.3% | +12.1% | £125.12/MWh | £140.31/MWh |
| C_IC1 | electricity | 2020-03-31 | 20.1% | -5.0% | £91.12/MWh | £86.56/MWh |
| C3 | electricity | 2020-06-30 | 16.5% | -4.3% | £113.43/MWh | £108.60/MWh |
| C9 | electricity | 2020-06-30 | 16.5% | -4.3% | £113.43/MWh | £108.60/MWh |
| C4 | electricity | 2020-09-30 | 11.1% | -1.6% | £124.42/MWh | £122.47/MWh |
| C4g | gas | 2020-09-30 | 20.7% | -5.0% | £16.94/MWh | £16.09/MWh |
| C1 | electricity | 2020-12-30 | 9.7% | -0.8% | £133.55/MWh | £132.43/MWh |
| C5 | electricity | 2020-12-30 | 2.7% | +2.6% | £133.55/MWh | £137.07/MWh |
| C7 | electricity | 2020-12-30 | -4.7% | +6.3% | £133.55/MWh | £142.02/MWh |
| C_IC3 | electricity | 2020-12-31 | -5.8% | +6.9% | £50.65/MWh | £54.14/MWh |
| C_IC3g | gas | 2020-12-31 | 14.7% | -3.3% | £20.05/MWh | £19.38/MWh |
| C2 | electricity | 2021-03-31 | -20.6% | +14.3% | £175.90/MWh | £201.03/MWh |
| C2g | gas | 2021-03-31 | 7.2% | +0.4% | £36.20/MWh | £36.34/MWh |
| C6 | electricity | 2021-03-31 | -16.1% | +12.0% | £175.90/MWh | £197.06/MWh |
| C8 | electricity | 2021-03-31 | -11.9% | +9.9% | £175.90/MWh | £193.40/MWh |
| C_IC2 | electricity | 2021-03-31 | -4.6% | +6.3% | £138.90/MWh | £147.64/MWh |
| C_IC1 | electricity | 2021-04-30 | 0.9% | +3.6% | £113.97/MWh | £118.02/MWh |
| C9 | electricity | 2021-06-30 | 1.1% | +3.5% | £170.38/MWh | £176.29/MWh |
| C4 | electricity | 2021-09-30 | -2.4% | +5.2% | £205.15/MWh | £215.85/MWh |
| C4g | gas | 2021-09-30 | 6.8% | +0.6% | £53.99/MWh | £54.31/MWh |
| C1_2 | electricity | 2021-12-30 | 4.9% | +1.6% | £311.83/MWh | £316.70/MWh |
| C5 | electricity | 2021-12-30 | -4.4% | +6.2% | £311.83/MWh | £331.12/MWh |
| C7 | electricity | 2021-12-30 | -6.0% | +7.0% | £311.83/MWh | £333.59/MWh |
| C_IC3 | electricity | 2021-12-31 | -24.4% | +15.0% | £224.03/MWh | £257.63/MWh |
| C_IC3g | gas | 2021-12-31 | -22.1% | +15.0% | £109.48/MWh | £125.90/MWh |
| C2 | electricity | 2022-03-31 | -15.8% | +11.9% | £361.95/MWh | £405.05/MWh |
| C6 | electricity | 2022-03-31 | -16.9% | +12.4% | £361.95/MWh | £406.99/MWh |
| C8 | electricity | 2022-03-31 | 5.1% | +1.5% | £361.95/MWh | £367.26/MWh |
| C_IC2 | electricity | 2022-04-30 | -10.3% | +9.2% | £269.81/MWh | £294.53/MWh |
| C_IC1 | electricity | 2022-05-30 | -6.9% | +7.4% | £239.42/MWh | £257.21/MWh |
| C9 | electricity | 2022-06-30 | 4.4% | +1.8% | £255.09/MWh | £259.70/MWh |
| C4 | electricity | 2022-09-30 | 7.3% | +0.4% | £404.86/MWh | £406.35/MWh |
| C4g | gas | 2022-09-30 | -19.2% | +13.6% | £183.79/MWh | £208.78/MWh |
| C1_2 | electricity | 2022-12-30 | 9.0% | -0.5% | £266.73/MWh | £265.45/MWh |
| C5 | electricity | 2022-12-30 | -2.8% | +5.4% | £266.73/MWh | £281.17/MWh |
| C7 | electricity | 2022-12-30 | -16.5% | +12.2% | £266.73/MWh | £299.40/MWh |
| C_IC3 | electricity | 2022-12-31 | -18.9% | +13.5% | £168.36/MWh | £191.03/MWh |
| C_IC3g | gas | 2022-12-31 | -37.8% | +15.0% | £101.23/MWh | £116.42/MWh |
| C2_2 | electricity | 2023-03-31 | -10.9% | +9.4% | £319.17/MWh | £349.30/MWh |
| C6 | electricity | 2023-03-31 | 0.2% | +3.9% | £319.17/MWh | £331.64/MWh |
| C8 | electricity | 2023-03-31 | 7.3% | +0.3% | £319.17/MWh | £320.24/MWh |
| C_IC2 | electricity | 2023-05-30 | -22.1% | +15.0% | £171.46/MWh | £197.18/MWh |
| C_IC1 | electricity | 2023-06-29 | -17.2% | +12.6% | £163.19/MWh | £183.71/MWh |
| C9 | electricity | 2023-06-30 | -10.4% | +9.2% | £224.44/MWh | £245.09/MWh |
| C4 | electricity | 2023-09-30 | 9.6% | -0.8% | £216.77/MWh | £215.02/MWh |
| C4g | gas | 2023-09-30 | -38.6% | +15.0% | £47.83/MWh | £55.00/MWh |
| C1_2 | electricity | 2023-12-30 | 29.2% | -5.0% | £242.22/MWh | £230.11/MWh |
| C5_2 | electricity | 2023-12-30 | 26.3% | -5.0% | £242.22/MWh | £230.11/MWh |
| C7 | electricity | 2023-12-30 | 24.4% | -5.0% | £242.22/MWh | £230.11/MWh |
| C_IC3 | electricity | 2023-12-31 | 23.6% | -5.0% | £118.95/MWh | £113.00/MWh |
| C_IC3g | gas | 2023-12-31 | -10.0% | +9.0% | £51.89/MWh | £56.57/MWh |
| C2_2 | electricity | 2024-03-30 | 14.0% | -3.0% | £207.71/MWh | £201.48/MWh |
| C6 | electricity | 2024-03-30 | 9.3% | -0.7% | £207.71/MWh | £206.31/MWh |
| C8 | electricity | 2024-03-30 | 9.3% | -0.7% | £207.71/MWh | £206.31/MWh |
| C_IC2 | electricity | 2024-06-28 | -34.0% | +15.0% | £148.64/MWh | £170.93/MWh |
| C9 | electricity | 2024-06-29 | -27.5% | +15.0% | £203.92/MWh | £234.50/MWh |
| C_IC1 | electricity | 2024-07-28 | -26.9% | +15.0% | £154.38/MWh | £177.53/MWh |
| C4 | electricity | 2024-09-29 | 0.4% | +3.8% | £195.97/MWh | £203.38/MWh |
| C1_2 | electricity | 2024-12-29 | 0.4% | +3.8% | £243.79/MWh | £253.01/MWh |
| C5_2 | electricity | 2024-12-29 | 22.6% | -5.0% | £243.79/MWh | £231.60/MWh |
| C7 | electricity | 2024-12-29 | 16.1% | -4.0% | £243.79/MWh | £233.94/MWh |
| C_IC3 | electricity | 2024-12-30 | 12.3% | -2.1% | £116.37/MWh | £113.88/MWh |
| C_IC3g | gas | 2024-12-30 | -9.4% | +8.7% | £50.47/MWh | £54.85/MWh |
| C2_2 | electricity | 2025-03-30 | 2.5% | +2.8% | £284.89/MWh | £292.73/MWh |
| C8 | electricity | 2025-03-30 | 6.8% | +0.6% | £284.89/MWh | £286.63/MWh |

## Churn Avoidability Analysis (Phase 17b)

Total no-offer churns: **6** | Blind misses: **6** | Deliberate passes (uneconomical): **0**

- Blind misses: company estimated churn < 30% → no offer made. Of these, 0 had SIM p ≥ 30% (detectable with a better model).
- Deliberate passes: company estimated churn ≥ 30% but the retention offer was uneconomical (margin + acq cost < offer cost).

**Estimated margin at stake** — blind: £6,623.39 | deliberate: £0.00 | total: £6,623.39

| Customer | Date | Reason | Co. est | SIM p | Detectable? | Margin at stake |
|----------|------|--------|---------|-------|-------------|----------------|
| C3 | 2020-06-30 | Blind miss | 0.05 | 0.06 | No | £585.39 |
| C1 | 2020-12-30 | Blind miss | 0.07 | 0.22 | No | £415.17 |
| C2 | 2022-03-31 | Blind miss | 0.03 | 0.05 | No | £236.63 |
| C5 | 2022-12-30 | Blind miss | 0.02 | 0.05 | No | £2,052.65 |
| C6 | 2024-03-30 | Blind miss | 0.25 | 0.21 | No | £2,864.67 |
| C4 | 2024-09-29 | Blind miss | 0.05 | 0.14 | No | £468.87 |

## Dual-Fuel Account P&L (Phase 17d)

5 dual-fuel account pair(s): electricity leg + gas leg combined.

| Account | Elec net | Gas net | Combined net | Gas accretive? |
|---------|----------|---------|-------------|---------------|
| C_IC3+C_IC3g | £115,693.11 | £52,415.53 | £168,108.64 | Yes |
| C2+C2g | £689.87 | £801.77 | £1,491.64 | Yes |
| C1+C1g | £441.55 | £620.41 | £1,061.96 | Yes |
| C3+C3g | £205.99 | £282.80 | £488.79 | Yes |
| C4+C4g | £138.61 | £-2,029.86 | £-1,891.25 | No |

Gas accretive in 4/5 dual-fuel accounts. Total gas net margin: £52,090.65.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £1,445,257.67 across 21 billing accounts. Revenue: £14,060,576.00.

| # | Customer | Tariff | Revenue | Gross margin | Capital | Net margin | Net margin % |
|---|----------|--------|---------|-------------|---------|------------|-------------|
| 1 | C_IC1 | fixed | £3,123,605.33 | £1,874,667.40 | £18,414.27 | £828,210.94 | 26.5% |
| 2 | C_IC2 | fixed | £1,525,269.53 | £909,828.76 | £8,527.56 | £426,669.88 | 28.0% |
| 3 | C_IC3 | pass_through | £4,637,989.59 | £1,833,437.73 | £23,162.13 | £115,693.11 | 2.5% |
| 4 | C_IC3g | pass_through | £1,832,579.91 | £622,647.03 | £0.00 | £52,415.53 | 2.9% |
| 5 | C_IC4 | flex | £2,744,638.87 | £1,106,685.27 | £0.00 | £14,583.80 | 0.5% |
| 6 | C6 | fixed | £38,922.12 | £22,435.52 | £264.20 | £3,564.32 | 9.2% |
| 7 | C9 | fixed | £20,243.67 | £12,708.16 | £131.43 | £1,492.50 | 7.4% |
| 8 | C8 | fixed | £21,688.78 | £12,468.89 | £134.91 | £1,270.34 | 5.9% |
| 9 | C2_2 | fixed | £10,303.18 | £5,495.07 | £67.91 | £1,066.20 | 10.3% |
| 10 | C2g | fixed | £3,849.77 | £2,019.21 | £21.85 | £801.77 | 20.8% |
| 11 | C2 | fixed | £5,114.40 | £3,410.31 | £24.74 | £689.87 | 13.5% |
| 12 | C1g | fixed | £2,436.42 | £1,355.24 | £15.79 | £620.41 | 25.5% |
| 13 | C1 | fixed | £3,497.52 | £2,293.73 | £14.09 | £441.55 | 12.6% |
| 14 | C5 | fixed | £21,712.25 | £12,001.55 | £133.94 | £316.02 | 1.5% |
| 15 | C3g | fixed | £2,683.32 | £1,298.53 | £15.29 | £282.80 | 10.5% |
| 16 | C3 | fixed | £3,628.72 | £2,388.84 | £14.77 | £205.99 | 5.7% |
| 17 | C5_2 | fixed | £12,351.94 | £6,330.97 | £86.34 | £195.38 | 1.6% |
| 18 | C4 | fixed | £6,274.43 | £3,314.79 | £37.48 | £138.61 | 2.2% |
| 19 | C1_2 | fixed | £11,623.13 | £5,656.25 | £81.60 | £72.95 | 0.6% |
| 20 | C7 | fixed | £21,792.85 | £10,815.29 | £139.94 | £-1,444.44 | -6.6% |
| 21 | C4g | fixed | £10,370.30 | £1,343.97 | £144.75 | £-2,029.86 | -19.6% |

## Revenue & Margin Sanity Check

### Portfolio P&L Waterfall
| Line | £ | % Revenue |
|------|---|-----------|
| Supply Revenue (ex-VAT, ex-policy passthrough) | £14,060,576 | 100.0% |
| Wholesale cost | -£7,607,974 | 54.1% |
| **Gross supply margin** | **£6,452,602** | **45.9%** |
| Policy + Network costs | -£4,955,912 | 35.2% |
| Capital cost | -£51,433 | 0.4% |
| **Net supply margin** | **£1,445,258** | **10.3%** |

> *The ledger's `net_margin_gbp` (£6,415,876) is gross − capital only, not final net.*

### Segment Net Margin vs Benchmark
| Segment | Revenue | Gross% | Net% | Benchmark | Status |
|---------|---------|--------|------|-----------|--------|
| I&C/elec | £12,031,503 | 47.6% | 11.5% | large spread -20% to +15% (crisis) | ✓ |
| I&C/gas | £1,832,580 | 34.0% | 2.9% | commodity 2-6%, pass-through ≈0 | ✓ |
| SME/elec | £60,634 | 56.8% | 6.4% | CMA 3-8% | ✓ |
| resi/elec | £82,240 | 57.6% | 3.4% | Ofgem CMA 2-5% | ✓ |
| resi/gas | £19,340 | 31.1% | -1.7% | Ofgem CMA 2-4% | ✓ |

### Per-Customer Net Margin Flags
No individual customers outside ±40.0/80.0 thresholds.

**SANITY CHECK: PASS** — all segments within benchmarks.
## Transaction Log

Total events: 3,535,662

| Event type | Count |
|------------|-------|
| acquisition_spend_event | 3 |
| bad_debt_event | 1,605 |
| billing_event | 1,605 |
| capital_charge_event | 1,705,599 |
| fixed_cost_event | 114 |
| non_commodity_cost_event | 1,605 |
| payment_received_event | 1,605 |
| settlement_event | 1,821,921 |
| vat_remittance_event | 1,605 |

**Cash-flow waterfall (from ledger)**

| Flow | Amount |
|------|--------|
| Customer bills (all-in) | £19,819,620.93 |
|   Less: VAT remitted to HMRC | (£957,157.22) |
| = Revenue (ex-VAT) | £18,862,463.71 |
| Less: non-commodity pass-through | (£4,787,181.64) |
| Wholesale cost (settlement events) | (£7,607,973.51) |
| Gross margin | £6,467,308.57 |
| Capital charges | (£51,432.98) |
| Net margin | £6,415,875.59 |

_Cash reconciliation: of £19,819,620.93 billed, bad debt of £396,515.59 was written off, leaving £19,423,105.34 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £6,976,517.22._

| Acquisition spend | (£700.00) |
| Fixed overhead | (£5,700.00) |
| Operating net margin | £6,409,475.59 |

## Annual Management Accounts

Year-by-year income statement from company accounting records. All figures £.

| Year | Revenue | Wholesale | Non-Commod | Gross Margin | Bad Debt | OpEx | Net Margin |
|------|---------|-----------|-----------|--------------|----------|------|------------|
| 2016 | £15,354.61 | £3,596.53 | £3,892.24 | £7,865.84 | £234.62 | £834.62 | £6,944.88 (45.2%) |
| 2017 | £348,630.52 | £111,056.98 | £112,782.23 | £124,791.30 | £6,260.72 | £6,860.72 | £116,657.37 (33.5%) |
| 2018 | £600,953.01 | £172,802.28 | £163,976.80 | £264,173.93 | £11,823.00 | £12,423.00 | £250,222.87 (41.6%) |
| 2019 | £1,645,452.10 | £496,239.95 | £445,337.04 | £703,875.12 | £30,746.61 | £31,346.61 | £670,219.20 (40.7%) |
| 2020 | £1,857,096.31 | £431,628.21 | £631,861.95 | £793,606.15 | £38,269.56 | £39,019.56 | £752,621.12 (40.5%) |
| 2021 | £2,421,344.01 | £973,152.05 | £680,438.97 | £767,752.99 | £47,173.73 | £47,773.73 | £714,343.31 (29.5%) |
| 2022 | £4,245,565.53 | £2,392,501.35 | £802,298.72 | £1,050,765.46 | £84,252.31 | £84,852.31 | £952,616.98 (22.4%) |
| 2023 | £3,495,761.69 | £1,642,210.96 | £878,317.42 | £975,233.31 | £76,851.81 | £77,451.81 | £887,641.52 (25.4%) |
| 2024 | £2,999,221.95 | £933,180.92 | £810,905.76 | £1,255,135.26 | £64,215.74 | £65,365.74 | £1,180,268.58 (39.4%) |
| 2025 | £1,233,083.98 | £452,920.26 | £257,370.51 | £522,793.21 | £36,687.50 | £36,987.50 | £480,108.18 (38.9%) |
| **Total** | **£18,862,463.71** | | | | | | **£6,011,644.01 (31.9%)** |

**Best year:** 2024 — net £1,180,268.58 (39.4% margin)
**Worst year:** 2016 — net £6,944.88 (45.2% margin)

### Balance Sheet (Year End 2025)

| Item | Value |
|------|-------|
| Cash | £8,478,280.23 |
| Trade Receivables | £0.00 |
| **Total Assets** | **£8,478,280.23** |
| Opening Capital | £2,466,636.22 |
| Current Period Profit | £6,011,644.01 |

## Budget vs Actual

Annual plan compared to management account actuals. RAG: GREEN <5%, AMBER 5-15%, RED >=15% variance (either direction).

| Year | Bud Revenue | Act Revenue | Rev% | Bud Net | Act Net | Net% | RAG |
|------|-------------|-------------|------|---------|---------|------|-----|
| 2016 | £14,671.69 | £15,354.61 | +4.7% | £6,592.99 | £6,944.88 | +5.3% | AMBER |
| 2017 | £16,138.86 | £348,630.52 | +2060.2% | £7,252.29 | £116,657.37 | +1508.6% | RED |
| 2018 | £386,623.75 | £600,953.01 | +55.4% | £128,424.00 | £250,222.87 | +94.8% | RED |
| 2019 | £675,851.95 | £1,645,452.10 | +143.5% | £281,335.50 | £670,219.20 | +138.2% | RED |
| 2020 | £1,816,630.04 | £1,857,096.31 | +2.2% | £736,963.94 | £752,621.12 | +2.1% | GREEN |
| 2021 | £2,028,952.42 | £2,421,344.01 | +19.3% | £833,649.22 | £714,343.31 | -14.3% | AMBER |
| 2022 | £2,607,611.88 | £4,245,565.53 | +62.8% | £790,935.58 | £952,616.98 | +20.4% | RED |
| 2023 | £4,508,414.67 | £3,495,761.69 | -22.5% | £1,029,561.00 | £887,641.52 | -13.8% | AMBER |
| 2024 | £3,512,844.39 | £2,999,221.95 | -14.6% | £893,105.75 | £1,180,268.58 | +32.2% | RED |
| 2025 | £3,145,356.42 | £1,233,083.98 | -60.8% | £1,315,150.33 | £480,108.18 | -63.5% | RED |

## Growth & Acquisition

**Mandate:** `flat`  **Acquisition cost:** resi £150 / SME £400  **Fixed overhead:** £50/month

**Acquisition activity by year**

| Year | Attempts | Wins | Win Rate | Spend |
|------|----------|------|----------|-------|
| 2020 | 1 | 0 | 0% | £150.00 |
| 2024 | 2 | 0 | 0% | £550.00 |

**Total:** 3 attempts, 0 wins (0% win rate), £700.00 total spend

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £6,409,475.59

## 2016

**Trading & Risk**

- Net margin: £1,178.25 (gross £6,813.70, capital £86.34)
  - Electricity: gross £6,002.97, capital £78.97, net £881.72
  - Gas: gross £810.73, capital £7.36, net £296.53
- Treasury at year end: £2,467,424.50
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.92 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.89 (avg 0.89), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.92 (avg 0.92), C6 0.91 (avg 0.91), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89)
- Risk committee (Context Handshake) interventions: 13
  - 2016-01-01: treasury £2,466,636.23, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-01-31: treasury £2,466,648.39, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-03-01: treasury £2,466,660.65, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-03-31: treasury £2,466,672.63, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-04-30: treasury £2,466,683.74, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-05-30: treasury £2,466,694.75, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-06-29: treasury £2,466,705.34, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-07-29: treasury £2,466,716.06, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-08-28: treasury £2,466,726.80, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-09-27: treasury £2,466,737.73, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-10-27: treasury £2,466,748.64, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-11-26: treasury £2,466,759.45, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
  - 2016-12-26: treasury £2,466,771.39, C1->1.00, VaR (current £27.73 / stressed £8.52) ratio 3.25
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 3.25
- Worst single period: C6 on 2016-11-08 period 40, net margin £-0.36

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2016): £10,179.42
  - By billing account: C1 £6,228.45, C5 £14,109.80, C7 £10,200.00
- Bill shock events (>=20%): 31 -- C1g 2016-05-31 (37%); C1g 2016-06-30 (29%); C1g 2016-10-31 (79%); C1g 2016-11-30 (46%); C5 2016-05-31 (27%); C5 2016-10-31 (40%); C5 2016-11-30 (43%); C7 2016-04-30 (21%); C7 2016-05-31 (37%); C7 2016-06-30 (30%); C7 2016-10-31 (77%); C7 2016-11-30 (52%); C2g 2016-05-31 (36%); C2g 2016-06-30 (34%); C2g 2016-10-31 (82%); C2g 2016-11-30 (53%); C6 2016-05-31 (25%); C6 2016-06-30 (23%); C6 2016-10-31 (40%); C6 2016-11-30 (46%); C8 2016-05-31 (40%); C8 2016-06-30 (40%); C8 2016-09-30 (22%); C8 2016-10-31 (100%); C8 2016-11-30 (68%); C3g 2016-10-31 (70%); C3g 2016-11-30 (48%); C9 2016-10-31 (74%); C9 2016-11-30 (58%); C4 2016-11-30 (28%); C4g 2016-11-30 (47%)
- Churn risk (accounts renewing in 2016): none above 20% threshold

**Pricing & Margin**

- C1 (electricity): tariff £117.30-£131.86/MWh, net margin £137.18
- C1g (gas): tariff £24.46-£26.25/MWh, net margin £101.24
- C2 (electricity): tariff £107.62/MWh, net margin £65.40
- C2g (gas): tariff £26.92/MWh, net margin £108.55
- C3 (electricity): tariff £98.21/MWh, net margin £21.61
- C3g (gas): tariff £21.93/MWh, net margin £40.58
- C4 (electricity): tariff £98.43/MWh, net margin £11.43
- C4g (gas): tariff £24.40/MWh, net margin £46.16
- C5 (electricity): tariff £117.30-£131.01/MWh, net margin £248.76
- C6 (electricity): tariff £107.62/MWh, net margin £6.12
- C7 (electricity): tariff £92.16-£175.95/MWh, net margin £234.27
- C8 (electricity): tariff £84.56-£161.43/MWh, net margin £120.80
- C9 (electricity): tariff £77.16-£147.31/MWh, net margin £36.15

**Portfolio Health**

- Capital cost ratio: 1.3% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 108, average clarity 0.829, average bill shock 19.7%, bad debt provision £166.66, avg complaint probability 4.7%
- Solvency signal: £274,158/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £2,034.44 vs. naked (unhedged) net margin: £10,920.39
- hedging cost £8,885.95 vs. a fully unhedged book (commodity-only: actual net £2,034.44 vs. naked net £10,920.39)
  - C1: actual £257.43 vs. naked £827.86 -- hedging cost £570.43
  - C1g: actual £207.55 vs. naked £516.14 -- hedging cost £308.59
  - C2: actual £83.88 vs. naked £370.88 -- hedging cost £287.00
  - C2g: actual £152.39 vs. naked £385.71 -- hedging cost £233.32
  - C3: actual £29.93 vs. naked £414.50 -- hedging cost £384.57
  - C3g: actual £77.50 vs. naked £396.79 -- hedging cost £319.29
  - C4: actual £48.51 vs. naked £261.09 -- hedging cost £212.58
  - C4g: actual £153.10 vs. naked £606.05 -- hedging cost £452.95
  - C5: actual £414.43 vs. naked £2,694.63 -- hedging cost £2,280.21
  - C6: actual £-19.99 vs. naked £1,068.86 -- hedging cost £1,088.85
  - C7: actual £395.13 vs. naked £1,939.88 -- hedging cost £1,544.75
  - C8: actual £175.42 vs. naked £784.40 -- hedging cost £608.98
  - C9: actual £59.16 vs. naked £653.59 -- hedging cost £594.44

**Year narrative:** 2016 produced a net gain of £1,178.25 across 13 accounts. The risk committee intervened 13 time(s), raising hedge fractions in response to elevated VaR. 31 customer(s) experienced a bill shock of >=20%.

## 2017

**Trading & Risk**

- Net margin: £30,566.05 (gross £123,236.40, capital £1,273.22)
  - Electricity: gross £121,806.83, capital £1,258.37, net £30,102.71
  - Gas: gross £1,429.57, capital £14.85, net £463.34
- Treasury at year end: £2,497,718.04
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.91 (avg 0.91), C1g 0.85 (avg 0.85), C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C3 0.91 (avg 0.91), C3g 0.85 (avg 0.85), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C5 0.91 (avg 0.91), C6 0.92 (avg 0.92), C7 0.91 (avg 0.91), C8 0.92 (avg 0.92), C9 0.91 (avg 0.91), C_IC1 0.94 (avg 0.94)
- Risk committee (Context Handshake) interventions: 12
  - 2017-01-25: treasury £2,467,429.20, C1->1.00, C5->1.00, C7->1.00, VaR (current £307.55 / stressed £98.11) ratio 3.13
  - 2017-02-24: treasury £2,467,435.20, C1->1.00, C5->1.00, C7->1.00, VaR (current £307.55 / stressed £98.11) ratio 3.13
  - 2017-03-26: treasury £2,467,441.63, C1->1.00, C5->1.00, C7->1.00, VaR (current £307.55 / stressed £98.11) ratio 3.13
  - 2017-04-25: treasury £2,467,778.39, C1->1.00, C5->1.00, C7->1.00, VaR (current £859.42 / stressed £329.85) ratio 2.61
  - 2017-05-25: treasury £2,467,778.80, C1->1.00, C5->1.00, C7->1.00, VaR (current £859.42 / stressed £329.85) ratio 2.61
  - 2017-06-24: treasury £2,467,780.28, C1->1.00, C5->1.00, C7->1.00, VaR (current £859.42 / stressed £329.85) ratio 2.61
  - 2017-07-24: treasury £2,467,956.57, C1->1.00, C5->1.00, C7->1.00, VaR (current £996.73 / stressed £394.58) ratio 2.53
  - 2017-08-23: treasury £2,467,961.22, C1->1.00, C5->1.00, C7->1.00, VaR (current £996.73 / stressed £394.58) ratio 2.53
  - 2017-09-22: treasury £2,467,964.95, C1->1.00, C5->1.00, C7->1.00, VaR (current £996.73 / stressed £394.58) ratio 2.53
  - 2017-10-22: treasury £2,468,217.02, C5->1.00, C7->1.00, VaR (current £1,005.08 / stressed £401.28) ratio 2.50
  - 2017-11-21: treasury £2,468,226.78, C5->1.00, C7->1.00, VaR (current £1,005.08 / stressed £401.28) ratio 2.50
  - 2017-12-21: treasury £2,468,236.21, C5->1.00, C7->1.00, VaR (current £1,005.08 / stressed £401.28) ratio 2.50
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.69
- Worst single period: C_IC1 on 2017-05-17 period 32, net margin £-20.43

**Customer Book**

- Active accounts: 14 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC1
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2017): £11,406.58
  - By billing account: C1 £5,470.70, C2 £10,821.00, C3 £9,473.64, C4 £8,371.99, C5 £11,735.66, C6 £23,920.37, C7 £8,667.92, C8 £13,323.56, C9 £10,874.42
- Bill shock events (>=20%): 50 -- C1g 2017-01-31 (31%); C1g 2017-02-28 (28%); C1g 2017-05-31 (30%); C1g 2017-06-30 (30%); C1g 2017-09-30 (21%); C1g 2017-11-30 (70%); C5 2017-01-31 (25%); C5 2017-02-28 (23%); C5 2017-06-30 (21%); C5 2017-11-30 (55%); C7 2017-01-31 (33%); C7 2017-02-28 (28%); C7 2017-05-31 (30%); C7 2017-06-30 (31%); C7 2017-09-30 (25%); C7 2017-10-31 (21%); C7 2017-11-30 (74%); C2g 2017-05-31 (34%); C2g 2017-06-30 (29%); C2g 2017-09-30 (27%); C2g 2017-11-30 (66%); C2g 2017-12-31 (22%); C6 2017-05-31 (22%); C6 2017-11-30 (49%); C8 2017-05-31 (39%); C8 2017-06-30 (35%); C8 2017-09-30 (43%); C8 2017-10-31 (22%); C8 2017-11-30 (81%); C8 2017-12-31 (21%); C3g 2017-05-31 (30%); C3g 2017-06-30 (23%); C3g 2017-09-30 (21%); C3g 2017-11-30 (59%); C9 2017-05-31 (32%); C9 2017-06-30 (26%); C9 2017-09-30 (29%); C9 2017-10-31 (21%); C9 2017-11-30 (69%); C4 2017-04-30 (28%); C4 2017-09-30 (21%); C4 2017-10-31 (25%); C4 2017-11-30 (26%); C4g 2017-01-31 (23%); C4g 2017-02-28 (22%); C4g 2017-05-31 (33%); C4g 2017-06-30 (35%); C4g 2017-09-30 (36%); C4g 2017-10-31 (22%); C4g 2017-11-30 (69%)
- Churn risk (accounts renewing in 2017): none above 20% threshold

**Pricing & Margin**

- C1 (electricity): tariff £117.65-£131.86/MWh, net margin £120.11
- C1g (gas): tariff £26.25-£33.49/MWh, net margin £106.38
- C2 (electricity): tariff £107.62-£125.75/MWh, net margin £75.15
- C2g (gas): tariff £26.92-£32.81/MWh, net margin £181.68
- C3 (electricity): tariff £98.21-£120.78/MWh, net margin £71.13
- C3g (gas): tariff £21.93-£23.11/MWh, net margin £57.45
- C4 (electricity): tariff £98.43-£109.87/MWh, net margin £46.13
- C4g (gas): tariff £24.40-£26.10/MWh, net margin £117.83
- C5 (electricity): tariff £119.51-£131.01/MWh, net margin £164.74
- C6 (electricity): tariff £107.62-£126.89/MWh, net margin £68.67
- C7 (electricity): tariff £96.38-£195.85/MWh, net margin £159.34
- C8 (electricity): tariff £84.56-£191.02/MWh, net margin £214.39
- C9 (electricity): tariff £77.16-£181.41/MWh, net margin £135.66
- C_IC1 (electricity): tariff £78.24-£149.38/MWh, net margin £29,047.38

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 168, average clarity 0.818, average bill shock 16.5%, bad debt provision £1,375.34, avg complaint probability 4.7%
- Solvency signal: £249,772/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £30,080.50 vs. naked (unhedged) net margin: £112,495.31
- hedging cost £82,414.80 vs. a fully unhedged book (commodity-only: actual net £30,080.50 vs. naked net £112,495.31)
  - C1: actual £14.74 vs. naked £329.72 -- hedging cost £314.97
  - C1g: actual £131.41 vs. naked £272.27 -- hedging cost £140.86
  - C2: actual £74.11 vs. naked £438.14 -- hedging cost £364.04
  - C2g: actual £207.48 vs. naked £448.25 -- hedging cost £240.78
  - C3: actual £114.13 vs. naked £516.65 -- hedging cost £402.52
  - C3g: actual £30.62 vs. naked £394.35 -- hedging cost £363.73
  - C4: actual £40.58 vs. naked £274.45 -- hedging cost £233.87
  - C4g: actual £44.94 vs. naked £544.66 -- hedging cost £499.72
  - C5: actual £-204.31 vs. naked £1,067.62 -- hedging cost £1,271.94
  - C6: actual £119.34 vs. naked £1,690.80 -- hedging cost £1,571.46
  - C7: actual £-49.36 vs. naked £820.03 -- hedging cost £869.39
  - C8: actual £261.70 vs. naked £997.59 -- hedging cost £735.89
  - C9: actual £247.74 vs. naked £957.68 -- hedging cost £709.94
  - C_IC1: actual £29,047.38 vs. naked £103,743.08 -- hedging cost £74,695.71

**Year narrative:** 2017 produced a net gain of £30,566.05 across 14 accounts. The risk committee intervened 12 time(s), raising hedge fractions in response to elevated VaR. 50 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £99,706.17 (gross £262,531.43, capital £1,528.07)
  - Electricity: gross £261,168.63, capital £1,507.00, net £99,331.51
  - Gas: gross £1,362.80, capital £21.07, net £374.66
- Treasury at year end: £2,486,406.51
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.92 (avg 0.92), C1g 0.85 (avg 0.85), C2 0.90 (avg 0.90), C2g 0.85 (avg 0.85), C3 0.91 (avg 0.91), C3g 0.85 (avg 0.85), C4 0.92 (avg 0.92), C4g 0.85 (avg 0.85), C5 0.92 (avg 0.92), C6 0.90 (avg 0.90), C7 0.92 (avg 0.92), C8 0.91 (avg 0.91), C9 0.90 (avg 0.90), C_IC1 0.85 (avg 0.89), C_IC2 0.93 (avg 0.93)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2018-03-01 period 27, net margin £-15.07

**Customer Book**

- Active accounts: 15 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC2
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2018): £290,477.29
  - By billing account: C1 £5,697.08, C2 £9,411.38, C3 £8,891.54, C4 £7,799.21, C5 £12,331.60, C6 £20,109.02, C7 £8,563.83, C8 £11,409.42, C9 £10,798.47, C_IC1 £2,809,761.35
- Bill shock events (>=20%): 60 -- C1g 2018-04-30 (37%); C1g 2018-05-31 (29%); C1g 2018-06-30 (30%); C1g 2018-09-30 (25%); C1g 2018-10-31 (46%); C1g 2018-11-30 (27%); C5 2018-04-30 (31%); C5 2018-06-30 (20%); C5 2018-10-31 (31%); C5 2018-11-30 (26%); C7 2018-04-30 (38%); C7 2018-05-31 (28%); C7 2018-06-30 (30%); C7 2018-09-30 (27%); C7 2018-10-31 (45%); C7 2018-11-30 (31%); C2g 2018-04-30 (28%); C2g 2018-05-31 (34%); C2g 2018-06-30 (34%); C2g 2018-09-30 (33%); C2g 2018-10-31 (45%); C6 2018-04-30 (23%); C6 2018-05-31 (21%); C6 2018-06-30 (22%); C6 2018-10-31 (30%); C6 2018-11-30 (21%); C8 2018-04-30 (35%); C8 2018-05-31 (37%); C8 2018-06-30 (42%); C8 2018-08-31 (23%); C8 2018-09-30 (49%); C8 2018-10-31 (53%); C8 2018-11-30 (29%); C3g 2018-04-30 (28%); C3g 2018-05-31 (32%); C3g 2018-06-30 (29%); C3g 2018-08-31 (34%); C3g 2018-09-30 (34%); C3g 2018-10-31 (35%); C3g 2018-12-31 (22%); C9 2018-04-30 (31%); C9 2018-05-31 (34%); C9 2018-06-30 (33%); C9 2018-07-31 (21%); C9 2018-08-31 (39%); C9 2018-09-30 (42%); C9 2018-10-31 (39%); C4 2018-04-30 (28%); C4 2018-09-30 (23%); C4 2018-10-31 (41%); C4 2018-11-30 (28%); C4g 2018-04-30 (36%); C4g 2018-05-31 (33%); C4g 2018-06-30 (36%); C4g 2018-09-30 (39%); C4g 2018-10-31 (85%); C4g 2018-11-30 (24%); C_IC1 2018-01-31 (22%); C_IC1 2018-02-28 (63%); C_IC2 2018-09-30 (20%)
- Churn risk (accounts renewing in 2018): 6 at risk (≥20% churn prob): C2 23%, C3 23%, C6 23%, C7 20%, C8 23%, C9 32%

**Pricing & Margin**

- C1 (electricity): tariff £117.65-£149.68/MWh, net margin £15.05
- C1g (gas): tariff £33.49-£36.05/MWh, net margin £131.41
- C2 (electricity): tariff £125.75-£143.89/MWh, net margin £68.53
- C2g (gas): tariff £32.81-£36.79/MWh, net margin £174.16
- C3 (electricity): tariff £120.78-£126.90/MWh, net margin £71.12
- C3g (gas): tariff £23.11-£28.80/MWh, net margin £26.42
- C4 (electricity): tariff £109.87-£149.37/MWh, net margin £61.80
- C4g (gas): tariff £26.10-£33.61/MWh, net margin £42.67
- C5 (electricity): tariff £119.51-£153.39/MWh, net margin £-203.32 -- **net-negative**
- C6 (electricity): tariff £126.89-£142.17/MWh, net margin £-41.23 -- **net-negative**
- C7 (electricity): tariff £96.38-£221.28/MWh, net margin £-47.02 -- **net-negative**
- C8 (electricity): tariff £100.06-£200.68/MWh, net margin £128.59
- C9 (electricity): tariff £95.02-£198.38/MWh, net margin £206.61
- C_IC1 (electricity): tariff £-82.12-£228.47/MWh, net margin £105,764.22
- C_IC2 (electricity): tariff £70.26-£134.14/MWh, net margin £-6,692.84 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 180, average clarity 0.810, average bill shock 16.0%, bad debt provision £2,384.75, avg complaint probability 4.7%
- Solvency signal: £226,037/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £109,582.74 vs. naked (unhedged) net margin: £246,455.41
- hedging cost £136,872.67 vs. a fully unhedged book (commodity-only: actual net £109,582.74 vs. naked net £246,455.41)
  - C1: actual £94.01 vs. naked £560.96 -- hedging cost £466.94
  - C1g: actual £144.33 vs. naked £420.62 -- hedging cost £276.29
  - C2: actual £62.60 vs. naked £499.23 -- hedging cost £436.64
  - C2g: actual £158.01 vs. naked £399.99 -- hedging cost £241.98
  - C3: actual £26.68 vs. naked £557.91 -- hedging cost £531.24
  - C3g: actual £38.90 vs. naked £481.52 -- hedging cost £442.62
  - C4: actual £104.22 vs. naked £464.67 -- hedging cost £360.45
  - C4g: actual £68.19 vs. naked £870.63 -- hedging cost £802.44
  - C5: actual £121.83 vs. naked £1,981.96 -- hedging cost £1,860.13
  - C6: actual £-141.45 vs. naked £1,833.69 -- hedging cost £1,975.14
  - C7: actual £71.87 vs. naked £1,347.87 -- hedging cost £1,276.01
  - C8: actual £24.32 vs. naked £936.62 -- hedging cost £912.30
  - C9: actual £143.75 vs. naked £1,046.07 -- hedging cost £902.32
  - C_IC1: actual £115,358.32 vs. naked £201,607.35 -- hedging cost £86,249.03
  - C_IC2: actual £-6,692.84 vs. naked £33,446.32 -- hedging cost £40,139.15

**Year narrative:** 2018 produced a net gain of £99,706.17 across 15 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 60 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £227,872.41 (gross £702,027.61, capital £2,309.31)
  - Electricity: gross £625,973.77, capital £2,287.85, net £218,118.22
  - Gas: gross £76,053.84, capital £21.46, net £9,754.19
- Treasury at year end: £2,606,406.14
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.89 (avg 0.89), C1g 0.85 (avg 0.85), C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C3 0.89 (avg 0.89), C3g 0.85 (avg 0.85), C4 0.89 (avg 0.89), C4g 0.85 (avg 0.85), C5 0.89 (avg 0.89), C6 0.91 (avg 0.91), C7 0.89 (avg 0.89), C8 0.92 (avg 0.92), C9 0.89 (avg 0.89), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2019-02-04 period 35, net margin £-14.60

**Customer Book**

- Active accounts: 17 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC3, C_IC3g
- Losses (churn) during year: none
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2019): £410,169.30
  - By billing account: C1 £6,046.01, C2 £9,483.53, C3 £9,318.53, C4 £7,754.22, C5 £13,910.73, C6 £20,752.15, C7 £9,842.14, C8 £11,020.84, C9 £10,646.87, C_IC1 £2,649,003.90, C_IC2 £1,764,083.33
- Bill shock events (>=20%): 66 -- C1 2019-04-30 (21%); C1g 2019-01-31 (36%); C1g 2019-02-28 (26%); C1g 2019-05-31 (23%); C1g 2019-06-30 (35%); C1g 2019-10-31 (74%); C1g 2019-11-30 (43%); C5 2019-01-31 (42%); C5 2019-02-28 (21%); C5 2019-06-30 (25%); C5 2019-10-31 (42%); C5 2019-11-30 (35%); C7 2019-01-31 (44%); C7 2019-02-28 (26%); C7 2019-05-31 (23%); C7 2019-06-30 (34%); C7 2019-10-31 (68%); C7 2019-11-30 (44%); C2g 2019-01-31 (25%); C2g 2019-02-28 (26%); C2g 2019-04-30 (35%); C2g 2019-06-30 (32%); C2g 2019-07-31 (25%); C2g 2019-09-30 (30%); C2g 2019-10-31 (64%); C2g 2019-11-30 (28%); C6 2019-02-28 (21%); C6 2019-06-30 (24%); C6 2019-10-31 (41%); C6 2019-11-30 (26%); C8 2019-01-31 (27%); C8 2019-02-28 (27%); C8 2019-04-30 (21%); C8 2019-06-30 (38%); C8 2019-07-31 (33%); C8 2019-09-30 (55%); C8 2019-10-31 (83%); C8 2019-11-30 (36%); C3 2019-04-30 (20%); C3g 2019-02-28 (26%); C3g 2019-06-30 (33%); C3g 2019-07-31 (35%); C3g 2019-09-30 (35%); C3g 2019-10-31 (64%); C3g 2019-11-30 (31%); C9 2019-02-28 (26%); C9 2019-04-30 (22%); C9 2019-06-30 (35%); C9 2019-07-31 (32%); C9 2019-09-30 (48%); C9 2019-10-31 (71%); C9 2019-11-30 (36%); C4 2019-04-30 (31%); C4 2019-09-30 (25%); C4 2019-11-30 (26%); C4g 2019-01-31 (30%); C4g 2019-02-28 (25%); C4g 2019-05-31 (21%); C4g 2019-06-30 (33%); C4g 2019-07-31 (37%); C4g 2019-09-30 (31%); C4g 2019-10-31 (34%); C4g 2019-11-30 (35%); C_IC1 2019-02-28 (54%); C_IC1 2019-03-31 (130%); C_IC2 2019-02-28 (69%)
- Churn risk (accounts renewing in 2019): 6 at risk (≥20% churn prob): C1 29%, C4 35%, C5 35%, C7 29%, C9 23%, C_IC1 41%

**Pricing & Margin**

- C1 (electricity): tariff £125.83-£149.68/MWh, net margin £93.91
- C1g (gas): tariff £25.33-£36.05/MWh, net margin £144.51
- C2 (electricity): tariff £143.89-£151.90/MWh, net margin £127.48
- C2g (gas): tariff £26.00-£36.79/MWh, net margin £121.37
- C3 (electricity): tariff £120.68-£126.90/MWh, net margin £25.68
- C3g (gas): tariff £23.00-£28.80/MWh, net margin £83.28
- C4 (electricity): tariff £126.76-£149.37/MWh, net margin £101.72
- C4g (gas): tariff £19.47-£33.61/MWh, net margin £78.41
- C5 (electricity): tariff £126.10-£153.39/MWh, net margin £121.02
- C6 (electricity): tariff £142.17-£148.72/MWh, net margin £92.86
- C7 (electricity): tariff £99.69-£221.28/MWh, net margin £71.68
- C8 (electricity): tariff £105.12-£211.40/MWh, net margin £154.84
- C9 (electricity): tariff £98.80-£198.38/MWh, net margin £145.35
- C_IC1 (electricity): tariff £0.00-£263.70/MWh, net margin £137,538.19
- C_IC2 (electricity): tariff £-60.00-£278.56/MWh, net margin £78,289.55
- C_IC3 (electricity): tariff £54.22-£103.50/MWh, net margin £1,355.95
- C_IC3g (gas): tariff £27.53/MWh, net margin £9,326.63

**Portfolio Health**

- Capital cost ratio: 0.3% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.824, average bill shock 17.1%, bad debt provision £6,207.40, avg complaint probability 4.7%
- Solvency signal: £217,201/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £252,589.91 vs. naked (unhedged) net margin: £836,841.98
- hedging cost £584,252.07 vs. a fully unhedged book (commodity-only: actual net £252,589.91 vs. naked net £836,841.98)
  - C1: actual £75.37 vs. naked £487.42 -- hedging cost £412.06
  - C1g: actual £137.12 vs. naked £302.41 -- hedging cost £165.30
  - C2: actual £157.29 vs. naked £663.14 -- hedging cost £505.85
  - C2g: actual £93.46 vs. naked £403.54 -- hedging cost £310.08
  - C3: actual £35.26 vs. naked £668.43 -- hedging cost £633.17
  - C3g: actual £135.78 vs. naked £505.74 -- hedging cost £369.96
  - C4: actual £104.15 vs. naked £443.69 -- hedging cost £339.54
  - C4g: actual £101.34 vs. naked £573.92 -- hedging cost £472.58
  - C5: actual £-27.61 vs. naked £1,590.08 -- hedging cost £1,617.69
  - C6: actual £233.55 vs. naked £2,599.80 -- hedging cost £2,366.24
  - C7: actual £56.98 vs. naked £1,146.66 -- hedging cost £1,089.68
  - C8: actual £240.89 vs. naked £1,370.83 -- hedging cost £1,129.94
  - C9: actual £159.29 vs. naked £1,258.35 -- hedging cost £1,099.06
  - C_IC1: actual £154,845.76 vs. naked £297,973.82 -- hedging cost £143,128.05
  - C_IC2: actual £85,558.69 vs. naked £161,523.27 -- hedging cost £75,964.58
  - C_IC3: actual £1,355.95 vs. naked £289,938.26 -- hedging cost £288,582.30
  - C_IC3g: actual £9,326.63 vs. naked £75,392.62 -- hedging cost £66,066.00

**Year narrative:** 2019 produced a net gain of £227,872.41 across 17 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 66 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £122,216.90 (gross £791,806.06, capital £1,965.47)
  - Electricity: gross £714,626.51, capital £1,955.18, net £112,364.37
  - Gas: gross £77,179.55, capital £10.29, net £9,852.53
- Treasury at year end: £2,914,252.99
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.89 (avg 0.89), C2 0.86 (avg 0.86), C2g 0.85 (avg 0.85), C4 0.88 (avg 0.88), C4g 0.85 (avg 0.85), C5 0.89 (avg 0.89), C6 0.86 (avg 0.86), C7 0.88 (avg 0.88), C8 0.87 (avg 0.87), C9 0.85 (avg 0.85), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.87), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2020-03-16 period 20, net margin £-18.66

**Customer Book**

- Active accounts: 19 (C1, C1_2, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 8, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C1_2, C_IC4
- Losses (churn) during year: C3, C1
  - Renewals (retained): 8 accounts
- Average CLV (Point-in-Time, year-end 2020): £507,877.32
  - By billing account: C1 £6,293.16, C1_2 £15.96, C2 £9,319.76, C3 £8,260.26, C4 £8,236.31, C5 £12,918.81, C6 £18,929.57, C7 £9,705.30, C8 £11,800.14, C9 £10,507.78, C_IC1 £1,826,772.55, C_IC2 £816,663.61, C_IC3 £2,894,255.48, C_IC4 £1,476,603.82
- Bill shock events (>=20%): 53 -- C1g 2020-01-31 (21%); C1g 2020-04-30 (32%); C1g 2020-06-30 (25%); C1g 2020-10-31 (56%); C1g 2020-12-29 (23%); C5 2020-04-30 (28%); C5 2020-10-31 (36%); C5 2020-12-31 (25%); C7 2020-04-30 (34%); C7 2020-05-31 (20%); C7 2020-06-30 (27%); C7 2020-10-31 (58%); C7 2020-11-30 (23%); C7 2020-12-31 (34%); C2 2020-04-30 (23%); C2g 2020-04-30 (36%); C2g 2020-06-30 (25%); C2g 2020-09-30 (27%); C2g 2020-10-31 (48%); C2g 2020-12-31 (38%); C6 2020-04-30 (29%); C6 2020-09-30 (20%); C6 2020-10-31 (33%); C6 2020-12-31 (26%); C8 2020-04-30 (36%); C8 2020-05-31 (24%); C8 2020-06-30 (32%); C8 2020-09-30 (51%); C8 2020-10-31 (64%); C8 2020-12-31 (42%); C3g 2020-04-30 (24%); C3g 2020-05-31 (21%); C3g 2020-06-29 (34%); C9 2020-04-30 (27%); C9 2020-05-31 (25%); C9 2020-06-30 (34%); C9 2020-09-30 (42%); C9 2020-10-31 (49%); C9 2020-12-31 (36%); C4 2020-04-30 (30%); C4 2020-09-30 (20%); C4 2020-10-31 (22%); C4 2020-11-30 (24%); C4g 2020-04-30 (35%); C4g 2020-05-31 (20%); C4g 2020-06-30 (26%); C4g 2020-09-30 (30%); C4g 2020-10-31 (49%); C4g 2020-12-31 (35%); C_IC1 2020-03-31 (57%); C_IC1 2020-04-30 (72%); C_IC2 2020-02-29 (66%); C_IC2 2020-03-31 (118%)
- Churn risk (accounts renewing in 2020): 9 at risk (≥20% churn prob): C1 38%, C4 41%, C5 32%, C7 20%, C8 23%, C9 23%, C_IC1 41%, C_IC2 41%, C_IC3 20%

**Pricing & Margin**

- C1 (electricity): tariff £125.83/MWh, net margin £75.30
- C1_2 (electricity): tariff £133.55/MWh, net margin £-1.38 -- **net-negative**
- C1g (gas): tariff £25.33/MWh, net margin £136.87
- C2 (electricity): tariff £143.89-£151.90/MWh, net margin £182.92
- C2g (gas): tariff £21.66-£26.00/MWh, net margin £133.50
- C3 (electricity): tariff £120.68/MWh, net margin £16.44
- C3g (gas): tariff £23.00/MWh, net margin £75.08
- C4 (electricity): tariff £122.47-£126.76/MWh, net margin £87.27
- C4g (gas): tariff £16.09-£19.47/MWh, net margin £71.92
- C5 (electricity): tariff £126.10-£137.07/MWh, net margin £-30.43 -- **net-negative**
- C6 (electricity): tariff £143.89-£148.72/MWh, net margin £366.13
- C7 (electricity): tariff £99.69-£213.04/MWh, net margin £58.35
- C8 (electricity): tariff £110.24-£211.40/MWh, net margin £338.60
- C9 (electricity): tariff £85.33-£188.63/MWh, net margin £117.22
- C_IC1 (electricity): tariff £-73.45-£2690.77/MWh, net margin £52,028.29
- C_IC2 (electricity): tariff £-79.50-£278.56/MWh, net margin £43,546.80
- C_IC3 (electricity): tariff £37.49-£81.21/MWh, net margin £11,008.59
- C_IC3g (gas): tariff £15.44-£19.38/MWh, net margin £9,435.16
- C_IC4 (electricity): tariff £77.17-£132.42/MWh, net margin £4,570.28

**Portfolio Health**

- Capital cost ratio: 0.2% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 205, average clarity 0.831, average bill shock 14.4%, bad debt provision £6,294.94, avg complaint probability 4.3%
- Solvency signal: £208,161/customer (14 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £86,379.50 vs. naked (unhedged) net margin: £964,655.44
- hedging cost £878,275.93 vs. a fully unhedged book (commodity-only: actual net £86,379.50 vs. naked net £964,655.44)
  - C1_2: actual £-149.26 vs. naked £154.26 -- hedging cost £303.52
  - C2: actual £175.35 vs. naked £570.69 -- hedging cost £395.33
  - C2g: actual £144.84 vs. naked £324.27 -- hedging cost £179.43
  - C4: actual £25.02 vs. naked £235.46 -- hedging cost £210.45
  - C4g: actual £-75.14 vs. naked £117.15 -- hedging cost £192.29
  - C5: actual £-318.19 vs. naked £196.67 -- hedging cost £514.86
  - C6: actual £355.75 vs. naked £2,175.57 -- hedging cost £1,819.82
  - C7: actual £-109.60 vs. naked £330.25 -- hedging cost £439.85
  - C8: actual £341.71 vs. naked £1,170.27 -- hedging cost £828.57
  - C9: actual £-18.70 vs. naked £697.66 -- hedging cost £716.35
  - C_IC1: actual £33,034.60 vs. naked £128,260.98 -- hedging cost £95,226.38
  - C_IC2: actual £42,303.73 vs. naked £96,422.44 -- hedging cost £54,118.71
  - C_IC3: actual £-15,152.11 vs. naked £221,921.88 -- hedging cost £237,074.00
  - C_IC3g: actual £17,934.51 vs. naked £159,245.07 -- hedging cost £141,310.56
  - C_IC4: actual £7,886.99 vs. naked £352,832.81 -- hedging cost £344,945.82

**Year narrative:** 2020 produced a net gain of £122,216.90 across 19 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 53 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £67,928.67 (gross £766,241.93, capital £5,635.95)
  - Electricity: gross £683,633.14, capital £5,622.97, net £59,643.53
  - Gas: gross £82,608.79, capital £12.99, net £8,285.14
- Treasury at year end: £2,943,329.55
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.95 (avg 0.95), C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C4 0.94 (avg 0.94), C4g 0.85 (avg 0.85), C5 0.94 (avg 0.94), C6 0.92 (avg 0.92), C7 0.97 (avg 0.97), C8 0.92 (avg 0.92), C9 0.92 (avg 0.92), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.89), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2021-11-24 period 30, net margin £-74.84

**Customer Book**

- Active accounts: 15 (C1_2, C2, C2g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 2, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 9 accounts
- Average CLV (Point-in-Time, year-end 2021): £494,662.68
  - By billing account: C1 £5,295.46, C1_2 £1,215.38, C2 £7,182.87, C3 £6,963.40, C4 £5,891.46, C5 £12,404.05, C6 £21,264.35, C7 £8,502.43, C8 £11,083.85, C9 £11,184.62, C_IC1 £1,613,852.65, C_IC2 £946,833.37, C_IC3 £2,594,930.48, C_IC4 £1,678,673.09
- Bill shock events (>=20%): 52 -- C5 2021-05-31 (22%); C5 2021-06-30 (31%); C5 2021-10-31 (28%); C5 2021-11-30 (48%); C7 2021-01-31 (22%); C7 2021-05-31 (29%); C7 2021-06-30 (46%); C7 2021-10-31 (52%); C7 2021-11-30 (63%); C2g 2021-04-30 (32%); C2g 2021-05-31 (24%); C2g 2021-06-30 (53%); C2g 2021-10-31 (57%); C2g 2021-11-30 (58%); C6 2021-06-30 (35%); C6 2021-10-31 (27%); C6 2021-11-30 (49%); C8 2021-05-31 (28%); C8 2021-06-30 (60%); C8 2021-09-30 (23%); C8 2021-10-31 (65%); C8 2021-11-30 (80%); C9 2021-02-28 (21%); C9 2021-05-31 (24%); C9 2021-06-30 (49%); C9 2021-08-31 (20%); C9 2021-09-30 (21%); C9 2021-10-31 (59%); C9 2021-11-30 (48%); C9 2021-12-31 (23%); C4 2021-04-30 (30%); C4 2021-09-30 (23%); C4 2021-10-31 (48%); C4 2021-11-30 (31%); C4g 2021-05-31 (22%); C4g 2021-06-30 (53%); C4g 2021-10-31 (113%); C4g 2021-11-30 (56%); C_IC1 2021-05-31 (40%); C_IC2 2021-03-31 (23%); C_IC2 2021-04-30 (83%); C_IC3g 2021-09-30 (33%); C_IC3g 2021-10-31 (23%); C_IC3g 2021-12-31 (33%); C_IC4 2021-02-28 (21%); C_IC4 2021-09-30 (27%); C_IC4 2021-12-31 (23%); C1_2 2021-01-31 (1207%); C1_2 2021-05-31 (33%); C1_2 2021-06-30 (55%); C1_2 2021-10-31 (76%); C1_2 2021-11-30 (75%)
- Churn risk (accounts renewing in 2021): 7 at risk (≥20% churn prob): C7 20%, C8 20%, C9 20%, C_IC1 41%, C_IC2 41%, C_IC3 32%, C_IC4 38%

**Pricing & Margin**

- C1_2 (electricity): tariff £133.55-£332.49/MWh, net margin £-149.00 -- **net-negative**
- C2 (electricity): tariff £143.89-£183.00/MWh, net margin £157.33
- C2g (gas): tariff £21.66-£35.00/MWh, net margin £99.84
- C4 (electricity): tariff £122.47-£183.00/MWh, net margin £-59.19 -- **net-negative**
- C4g (gas): tariff £16.09-£35.00/MWh, net margin £-334.91 -- **net-negative**
- C5 (electricity): tariff £137.07-£353.26/MWh, net margin £-314.37 -- **net-negative**
- C6 (electricity): tariff £143.89-£197.06/MWh, net margin £525.02
- C7 (electricity): tariff £111.59-£274.50/MWh, net margin £-119.37 -- **net-negative**
- C8 (electricity): tariff £110.24-£274.50/MWh, net margin £341.36
- C9 (electricity): tariff £85.33-£264.43/MWh, net margin £-13.51 -- **net-negative**
- C_IC1 (electricity): tariff £-54.00-£2365.91/MWh, net margin £26,743.24
- C_IC2 (electricity): tariff £-73.20-£1080.00/MWh, net margin £55,504.42
- C_IC3 (electricity): tariff £42.54-£390.00/MWh, net margin £-26,297.06 -- **net-negative**
- C_IC3g (gas): tariff £19.38-£125.90/MWh, net margin £8,520.22
- C_IC4 (electricity): tariff £103.84-£397.26/MWh, net margin £3,324.66

**Portfolio Health**

- Capital cost ratio: 0.7% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 180, average clarity 0.817, average bill shock 23.6%, bad debt provision £9,145.63, avg complaint probability 4.8%
- Solvency signal: £245,277/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £188,628.62 vs. naked (unhedged) net margin: £455,364.94
- hedging cost £266,736.32 vs. a fully unhedged book (commodity-only: actual net £188,628.62 vs. naked net £455,364.94)
  - C1_2: actual £-81.21 vs. naked £584.66 -- hedging cost £665.87
  - C2: actual £136.64 vs. naked £124.72 -- hedging added £11.92
  - C2g: actual £45.59 vs. naked £-190.70 -- hedging added £236.29
  - C4: actual £-220.41 vs. naked £-170.34 -- hedging cost £50.07
  - C4g: actual £-901.21 vs. naked £-1,344.38 -- hedging added £443.17
  - C5: actual £329.88 vs. naked £1,603.22 -- hedging cost £1,273.34
  - C6: actual £511.43 vs. naked £266.64 -- hedging added £244.79
  - C7: actual £-1,829.78 vs. naked £-869.22 -- hedging cost £960.56
  - C8: actual £285.02 vs. naked £107.75 -- hedging added £177.27
  - C9: actual £-48.56 vs. naked £-184.11 -- hedging added £135.55
  - C_IC1: actual £27,324.15 vs. naked £-61,901.23 -- hedging added £89,225.37
  - C_IC2: actual £63,564.59 vs. naked £22,126.20 -- hedging added £41,438.39
  - C_IC3: actual £97,272.89 vs. naked £231,708.10 -- hedging cost £134,435.21
  - C_IC3g: actual £4,142.87 vs. naked £85,199.40 -- hedging cost £81,056.52
  - C_IC4: actual £-1,903.26 vs. naked £178,304.23 -- hedging cost £180,207.49

**Year narrative:** 2021 (flagged crisis year) produced a net gain of £67,928.67 across 15 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 52 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £300,205.86 (gross £1,049,224.19, capital £13,296.17)
  - Electricity: gross £958,868.27, capital £13,262.33, net £297,372.89
  - Gas: gross £90,355.92, capital £33.84, net £2,832.97
- Treasury at year end: £3,135,960.69
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.94 (avg 0.94), C2_2 0.95 (avg 0.95), C4 0.96 (avg 0.96), C4g 0.85 (avg 0.85), C5_2 0.94 (avg 0.94), C6 0.94 (avg 0.94), C7 0.93 (avg 0.93), C8 0.96 (avg 0.96), C9 0.94 (avg 0.94), C_IC1 1.00 (avg 0.97), C_IC2 1.00 (avg 0.97), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 9
  - 2022-04-29: treasury £3,039,006.78, C2->1.00, C6->1.00, C8->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,437.98 / stressed £20,565.19) ratio 2.70
  - 2022-05-29: treasury £3,039,127.16, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,547.78 / stressed £20,594.39) ratio 2.70
  - 2022-06-28: treasury £3,039,121.91, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,547.78 / stressed £20,594.39) ratio 2.70
  - 2022-07-28: treasury £3,038,929.29, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,609.19 / stressed £20,606.62) ratio 2.70
  - 2022-08-27: treasury £3,038,919.68, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,609.19 / stressed £20,606.62) ratio 2.70
  - 2022-09-26: treasury £3,038,904.24, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,609.19 / stressed £20,606.62) ratio 2.70
  - 2022-10-26: treasury £3,037,957.44, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,609.19 / stressed £20,606.62) ratio 2.70
  - 2022-11-25: treasury £3,037,954.46, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,609.19 / stressed £20,606.62) ratio 2.70
  - 2022-12-25: treasury £3,037,920.80, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,609.19 / stressed £20,606.62) ratio 2.70
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.70
- Worst single period: C_IC1 on 2022-01-24 period 26, net margin £-89.07

**Customer Book**

- Active accounts: 17 (C1_2, C2, C2_2, C2g, C4, C4g, C5, C5_2, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 7, SME electricity: 3, gas (dual-fuel): 3
- New acquisitions this year: C2_2, C5_2
- Losses (churn) during year: C2, C5
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2022): £420,558.31
  - By billing account: C1 £5,760.93, C1_2 £2,223.35, C2 £6,645.17, C2_2 £1,068.69, C3 £7,598.89, C4 £4,129.23, C5 £11,532.92, C5_2 £7.16, C6 £19,748.20, C7 £6,091.12, C8 £11,370.96, C9 £10,023.90, C_IC1 £1,679,089.32, C_IC2 £1,056,515.43, C_IC3 £2,440,360.88, C_IC4 £1,466,766.77
- Bill shock events (>=20%): 76 -- C5 2022-01-31 (128%); C5 2022-02-28 (21%); C5 2022-05-31 (25%); C5 2022-11-30 (48%); C5 2022-12-29 (29%); C7 2022-01-31 (49%); C7 2022-02-28 (26%); C7 2022-04-30 (22%); C7 2022-05-31 (34%); C7 2022-06-30 (25%); C7 2022-09-30 (30%); C7 2022-11-30 (58%); C7 2022-12-31 (54%); C2g 2022-02-28 (22%); C6 2022-04-30 (42%); C6 2022-05-31 (23%); C6 2022-09-30 (25%); C6 2022-11-30 (43%); C6 2022-12-31 (33%); C8 2022-02-28 (22%); C8 2022-05-31 (38%); C8 2022-06-30 (33%); C8 2022-09-30 (76%); C8 2022-11-30 (68%); C8 2022-12-31 (56%); C9 2022-04-30 (20%); C9 2022-05-31 (28%); C9 2022-06-30 (29%); C9 2022-09-30 (45%); C9 2022-10-31 (30%); C9 2022-11-30 (43%); C9 2022-12-31 (51%); C4 2022-04-30 (28%); C4 2022-09-30 (25%); C4 2022-10-31 (62%); C4 2022-11-30 (31%); C4g 2022-01-31 (25%); C4g 2022-02-28 (24%); C4g 2022-05-31 (34%); C4g 2022-06-30 (28%); C4g 2022-07-31 (22%); C4g 2022-09-30 (63%); C4g 2022-10-31 (134%); C4g 2022-11-30 (57%); C4g 2022-12-31 (56%); C_IC1 2022-03-31 (21%); C_IC1 2022-06-30 (77%); C_IC2 2022-03-31 (24%); C_IC2 2022-05-31 (57%); C_IC3 2022-01-31 (108%); C_IC3g 2022-03-31 (38%); C_IC3g 2022-04-30 (22%); C_IC3g 2022-07-31 (40%); C_IC3g 2022-08-31 (30%); C_IC3g 2022-10-31 (51%); C_IC3g 2022-11-30 (31%); C_IC3g 2022-12-31 (22%); C_IC4 2022-03-31 (41%); C_IC4 2022-07-31 (29%); C_IC4 2022-08-31 (33%); C_IC4 2022-10-31 (31%); C_IC4 2022-12-31 (68%); C1_2 2022-01-31 (141%); C1_2 2022-02-28 (28%); C1_2 2022-04-30 (23%); C1_2 2022-05-31 (43%); C1_2 2022-06-30 (34%); C1_2 2022-09-30 (51%); C1_2 2022-11-30 (79%); C1_2 2022-12-31 (61%); C2_2 2022-04-30 (1735%); C2_2 2022-05-31 (38%); C2_2 2022-06-30 (32%); C2_2 2022-09-30 (70%); C2_2 2022-11-30 (62%); C2_2 2022-12-31 (56%)
- Churn risk (accounts renewing in 2022): 12 at risk (≥20% churn prob): C1_2 41%, C2 38%, C4 38%, C5 38%, C6 35%, C7 23%, C8 26%, C9 35%, C_IC1 38%, C_IC2 38%, C_IC3 41%, C_IC4 38%

**Pricing & Margin**

- C1_2 (electricity): tariff £265.45-£332.49/MWh, net margin £-84.52 -- **net-negative**
- C2 (electricity): tariff £183.00/MWh, net margin £13.07
- C2_2 (electricity): tariff £361.95/MWh, net margin £28.76
- C2g (gas): tariff £35.00/MWh, net margin £-17.33 -- **net-negative**
- C4 (electricity): tariff £183.00-£305.00/MWh, net margin £-276.94 -- **net-negative**
- C4g (gas): tariff £35.00-£95.00/MWh, net margin £-1,284.53 -- **net-negative**
- C5 (electricity): tariff £353.26/MWh, net margin £329.61
- C5_2 (electricity): tariff £266.73/MWh, net margin £-7.33 -- **net-negative**
- C6 (electricity): tariff £197.06-£406.99/MWh, net margin £823.13
- C7 (electricity): tariff £143.79-£457.50/MWh, net margin £-1,827.01 -- **net-negative**
- C8 (electricity): tariff £143.79-£457.50/MWh, net margin £-285.40 -- **net-negative**
- C9 (electricity): tariff £138.51-£389.55/MWh, net margin £-116.82 -- **net-negative**
- C_IC1 (electricity): tariff £-83.39-£462.99/MWh, net margin £131,252.37
- C_IC2 (electricity): tariff £-80.56-£593.08/MWh, net margin £73,033.35
- C_IC3 (electricity): tariff £150.10-£390.00/MWh, net margin £96,398.54
- C_IC3g (gas): tariff £116.42-£125.90/MWh, net margin £4,134.82
- C_IC4 (electricity): tariff £133.29-£531.77/MWh, net margin £-1,907.93 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 1.3% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £3,436,886.77 -> £3,036,419.43 (11.7%)
- Bills issued: 173, average clarity 0.783, average bill shock 33.9%, bad debt provision £36,024.85, avg complaint probability 5.8%
- Solvency signal: £223,997/customer (14 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £199,826.07 vs. naked (unhedged) net margin: £1,226,097.34
- hedging cost £1,026,271.27 vs. a fully unhedged book (commodity-only: actual net £199,826.07 vs. naked net £1,226,097.34)
  - C1_2: actual £-589.08 vs. naked £1,295.38 -- hedging cost £1,884.46
  - C2_2: actual £30.18 vs. naked £1,645.15 -- hedging cost £1,614.97
  - C4: actual £-277.33 vs. naked £595.36 -- hedging cost £872.70
  - C4g: actual £-1,950.48 vs. naked £1,336.80 -- hedging cost £3,287.28
  - C5_2: actual £-1,113.67 vs. naked £2,632.27 -- hedging cost £3,745.94
  - C6: actual £1,130.77 vs. naked £3,998.91 -- hedging cost £2,868.14
  - C7: actual £-445.92 vs. naked £2,281.71 -- hedging cost £2,727.63
  - C8: actual £-481.87 vs. naked £1,102.92 -- hedging cost £1,584.78
  - C9: actual £-49.37 vs. naked £1,012.21 -- hedging cost £1,061.58
  - C_IC1: actual £212,770.84 vs. naked £251,052.75 -- hedging cost £38,281.91
  - C_IC2: actual £87,504.96 vs. naked £126,811.39 -- hedging cost £39,306.43
  - C_IC3: actual £-108,689.56 vs. naked £503,974.57 -- hedging cost £612,664.13
  - C_IC3g: actual £8,513.79 vs. naked £123,301.26 -- hedging cost £114,787.47
  - C_IC4: actual £3,472.81 vs. naked £205,056.67 -- hedging cost £201,583.86

**Year narrative:** 2022 (flagged crisis year) produced a net gain of £300,205.86 across 17 accounts. The risk committee intervened 9 time(s), raising hedge fractions in response to elevated VaR. 76 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £147,353.65 (gross £973,896.95, capital £10,139.98)
  - Electricity: gross £852,956.85, capital £10,087.56, net £139,991.71
  - Gas: gross £120,940.11, capital £52.42, net £7,361.94
- Treasury at year end: £3,336,256.48
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.91 (avg 0.91), C2_2 0.93 (avg 0.93), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C5_2 0.91 (avg 0.91), C6 0.94 (avg 0.94), C7 0.92 (avg 0.92), C8 0.95 (avg 0.95), C9 0.91 (avg 0.91), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 4
  - 2023-01-24: treasury £3,135,960.36, C2->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,347.43 / stressed £43,958.32) ratio 2.76
  - 2023-02-23: treasury £3,135,960.71, C2->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,347.43 / stressed £43,958.32) ratio 2.76
  - 2023-03-25: treasury £3,135,961.01, C2->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,347.43 / stressed £43,958.32) ratio 2.76
  - 2023-04-24: treasury £3,216,174.27, C2->1.00, C4->1.00, C5->1.00, C7->1.00, C9->1.00, C_IC3->1.00, VaR (current £128,380.19 / stressed £48,915.08) ratio 2.62
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.73
- Worst single period: C_IC1 on 2023-06-16 period 22, net margin £-21.69

**Customer Book**

- Active accounts: 14 (C1_2, C2_2, C4, C4g, C5_2, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 2, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 9 accounts
- Average CLV (Point-in-Time, year-end 2023): £390,538.47
  - By billing account: C1 £6,142.89, C1_2 £1,992.91, C2 £6,136.90, C2_2 £3,717.08, C3 £6,214.40, C4 £2,912.30, C5 £10,629.41, C5_2 £912.14, C6 £19,004.78, C7 £6,681.84, C8 £8,929.80, C9 £9,648.06, C_IC1 £1,543,308.03, C_IC2 £824,338.30, C_IC3 £2,389,942.94, C_IC4 £1,408,103.70
- Bill shock events (>=20%): 53 -- C7 2023-01-31 (40%); C7 2023-05-31 (31%); C7 2023-06-30 (35%); C7 2023-10-31 (53%); C7 2023-11-30 (69%); C6 2023-04-30 (32%); C6 2023-05-31 (23%); C6 2023-06-30 (22%); C6 2023-10-31 (38%); C6 2023-11-30 (43%); C8 2023-04-30 (30%); C8 2023-05-31 (39%); C8 2023-06-30 (42%); C8 2023-10-31 (92%); C8 2023-11-30 (66%); C9 2023-02-28 (21%); C9 2023-03-31 (20%); C9 2023-04-30 (26%); C9 2023-05-31 (32%); C9 2023-06-30 (43%); C9 2023-09-30 (20%); C9 2023-10-31 (71%); C9 2023-11-30 (52%); C4 2023-02-28 (25%); C4 2023-04-30 (29%); C4 2023-09-30 (24%); C4 2023-11-30 (27%); C4g 2023-05-31 (36%); C4g 2023-06-30 (45%); C4g 2023-10-31 (46%); C4g 2023-11-30 (63%); C_IC1 2023-03-31 (21%); C_IC1 2023-06-30 (53%); C_IC1 2023-07-31 (60%); C_IC2 2023-03-31 (22%); C_IC2 2023-05-31 (53%); C_IC2 2023-06-30 (101%); C_IC3g 2023-01-31 (31%); C_IC4 2023-01-31 (35%); C1_2 2023-05-31 (38%); C1_2 2023-06-30 (43%); C1_2 2023-10-31 (73%); C1_2 2023-11-30 (83%); C2_2 2023-04-30 (23%); C2_2 2023-05-31 (40%); C2_2 2023-06-30 (40%); C2_2 2023-10-31 (89%); C2_2 2023-11-30 (64%); C5_2 2023-01-31 (2059%); C5_2 2023-05-31 (21%); C5_2 2023-06-30 (24%); C5_2 2023-10-31 (30%); C5_2 2023-11-30 (50%)
- Churn risk (accounts renewing in 2023): 9 at risk (≥20% churn prob): C4 41%, C6 41%, C7 41%, C8 38%, C9 41%, C_IC1 41%, C_IC2 41%, C_IC3 41%, C_IC4 35%

**Pricing & Margin**

- C1_2 (electricity): tariff £265.45-£268.29/MWh, net margin £-581.35 -- **net-negative**
- C2_2 (electricity): tariff £349.30-£361.95/MWh, net margin £499.89
- C4 (electricity): tariff £249.30-£305.00/MWh, net margin £-68.72 -- **net-negative**
- C4g (gas): tariff £66.00-£95.00/MWh, net margin £-1,164.32 -- **net-negative**
- C5_2 (electricity): tariff £266.73-£269.33/MWh, net margin £-1,102.27 -- **net-negative**
- C6 (electricity): tariff £331.64-£406.99/MWh, net margin £1,243.90
- C7 (electricity): tariff £191.96-£457.50/MWh, net margin £-443.76 -- **net-negative**
- C8 (electricity): tariff £208.21-£457.50/MWh, net margin £-111.16 -- **net-negative**
- C9 (electricity): tariff £192.57-£389.55/MWh, net margin £226.00
- C_IC1 (electricity): tariff £-60.00-£462.99/MWh, net margin £159,950.35
- C_IC2 (electricity): tariff £-186.24-£476.92/MWh, net margin £84,685.89
- C_IC3 (electricity): tariff £94.12-£286.55/MWh, net margin £-107,787.31 -- **net-negative**
- C_IC3g (gas): tariff £56.57-£116.42/MWh, net margin £8,526.27
- C_IC4 (electricity): tariff £106.05-£234.49/MWh, net margin £3,480.25

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 168, average clarity 0.801, average bill shock 30.1%, bad debt provision £14,424.18, avg complaint probability 5.0%
- Solvency signal: £278,021/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £374,806.08 vs. naked (unhedged) net margin: £1,216,465.11
- hedging cost £841,659.04 vs. a fully unhedged book (commodity-only: actual net £374,806.08 vs. naked net £1,216,465.11)
  - C1_2: actual £684.84 vs. naked £1,724.56 -- hedging cost £1,039.72
  - C2_2: actual £821.91 vs. naked £2,413.74 -- hedging cost £1,591.83
  - C4: actual £313.86 vs. naked £700.05 -- hedging cost £386.18
  - C4g: actual £529.39 vs. naked £1,048.79 -- hedging cost £519.40
  - C5_2: actual £1,196.47 vs. naked £3,270.66 -- hedging cost £2,074.19
  - C6: actual £1,374.90 vs. naked £5,042.71 -- hedging cost £3,667.81
  - C7: actual £493.58 vs. naked £1,989.47 -- hedging cost £1,495.89
  - C8: actual £140.61 vs. naked £1,972.23 -- hedging cost £1,831.62
  - C9: actual £626.00 vs. naked £2,129.64 -- hedging cost £1,503.64
  - C_IC1: actual £141,576.45 vs. naked £284,450.26 -- hedging cost £142,873.81
  - C_IC2: actual £94,108.05 vs. naked £162,159.80 -- hedging cost £68,051.75
  - C_IC3: actual £120,587.99 vs. naked £394,328.28 -- hedging cost £273,740.29
  - C_IC3g: actual £8,660.26 vs. naked £123,107.25 -- hedging cost £114,446.99
  - C_IC4: actual £3,691.75 vs. naked £232,127.67 -- hedging cost £228,435.92

**Year narrative:** 2023 produced a net gain of £147,353.65 across 14 accounts. The risk committee intervened 4 time(s), raising hedge fractions in response to elevated VaR. 53 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £330,160.28 (gross £1,254,544.51, capital £9,500.95)
  - Electricity: gross £1,130,130.63, capital £9,477.55, net £321,078.45
  - Gas: gross £124,413.88, capital £23.40, net £9,081.83
- Treasury at year end: £3,710,669.07
- Hedge fraction at first renewal this year (avg across year's terms): C1_2 0.87 (avg 0.87), C2_2 0.91 (avg 0.91), C5_2 0.88 (avg 0.88), C7 0.90 (avg 0.90), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89), C_IC1 0.85 (avg 0.87), C_IC2 0.85 (avg 0.87), C_IC3 0.94 (avg 0.94), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2024-06-28 period 31, net margin £-26.25

**Customer Book**

- Active accounts: 14 (C1_2, C2_2, C4, C4g, C5_2, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 2, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: C6, C4
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2024): £363,687.34
  - By billing account: C1 £4,633.75, C1_2 £3,099.46, C2 £5,088.64, C2_2 £4,144.53, C3 £5,683.10, C4 £3,419.27, C5 £11,328.55, C5_2 £3,428.63, C6 £16,245.83, C7 £8,694.38, C8 £9,152.68, C9 £8,883.63, C_IC1 £1,494,574.75, C_IC2 £610,332.16, C_IC3 £2,326,510.46, C_IC4 £1,303,777.60
- Bill shock events (>=20%): 45 -- C7 2024-02-29 (26%); C7 2024-05-31 (36%); C7 2024-09-30 (32%); C7 2024-10-31 (36%); C7 2024-11-30 (47%); C8 2024-02-29 (23%); C8 2024-04-30 (33%); C8 2024-05-31 (48%); C8 2024-07-31 (25%); C8 2024-09-30 (67%); C8 2024-10-31 (34%); C8 2024-11-30 (59%); C9 2024-05-31 (48%); C9 2024-07-31 (28%); C9 2024-09-30 (52%); C9 2024-10-31 (22%); C9 2024-11-30 (46%); C4 2024-04-30 (30%); C4g 2024-02-29 (27%); C4g 2024-05-31 (39%); C4g 2024-07-31 (24%); C4g 2024-09-28 (45%); C_IC1 2024-07-31 (33%); C_IC1 2024-08-31 (65%); C_IC2 2024-06-30 (49%); C_IC2 2024-07-31 (107%); C_IC3 2024-01-31 (20%); C1_2 2024-01-31 (21%); C1_2 2024-02-29 (28%); C1_2 2024-04-30 (23%); C1_2 2024-05-31 (44%); C1_2 2024-09-30 (51%); C1_2 2024-10-31 (45%); C1_2 2024-11-30 (57%); C2_2 2024-02-29 (22%); C2_2 2024-04-30 (47%); C2_2 2024-05-31 (46%); C2_2 2024-07-31 (24%); C2_2 2024-09-30 (59%); C2_2 2024-10-31 (33%); C2_2 2024-11-30 (55%); C5_2 2024-02-29 (21%); C5_2 2024-05-31 (24%); C5_2 2024-10-31 (25%); C5_2 2024-11-30 (34%)
- Churn risk (accounts renewing in 2024): 8 at risk (≥20% churn prob): C2_2 23%, C4 38%, C6 29%, C7 29%, C_IC1 29%, C_IC2 32%, C_IC3 41%, C_IC4 20%

**Pricing & Margin**

- C1_2 (electricity): tariff £253.01-£268.29/MWh, net margin £684.09
- C2_2 (electricity): tariff £201.48-£349.30/MWh, net margin £428.43
- C4 (electricity): tariff £249.30/MWh, net margin £235.12
- C4g (gas): tariff £66.00/MWh, net margin £396.91
- C5_2 (electricity): tariff £231.60-£269.33/MWh, net margin £1,191.57
- C6 (electricity): tariff £331.64/MWh, net margin £479.72
- C7 (electricity): tariff £165.00-£366.47/MWh, net margin £492.80
- C8 (electricity): tariff £162.10-£397.50/MWh, net margin £292.72
- C9 (electricity): tariff £165.00-£367.64/MWh, net margin £560.36
- C_IC1 (electricity): tariff £-98.58-£330.68/MWh, net margin £123,481.08
- C_IC2 (electricity): tariff £-106.92-£354.92/MWh, net margin £68,786.62
- C_IC3 (electricity): tariff £89.47-£179.68/MWh, net margin £120,746.82
- C_IC3g (gas): tariff £54.85-£56.57/MWh, net margin £8,684.92
- C_IC4 (electricity): tariff £104.06-£193.21/MWh, net margin £3,699.12

**Portfolio Health**

- Capital cost ratio: 0.8% of gross
- Treasury drawdown events (>=10% threshold): 3714 -- £3,707,004.45 -> £3,336,303.85 (10.0%); £3,707,004.69 -> £3,336,303.87 (10.0%); £3,707,004.93 -> £3,336,303.90 (10.0%); £3,707,005.12 -> £3,336,304.08 (10.0%); £3,707,005.30 -> £3,336,304.26 (10.0%); £3,707,005.49 -> £3,336,304.45 (10.0%); £3,707,005.67 -> £3,336,304.64 (10.0%); £3,707,005.85 -> £3,336,304.83 (10.0%); £3,707,006.03 -> £3,336,305.02 (10.0%); £3,707,006.22 -> £3,336,305.21 (10.0%); £3,707,006.46 -> £3,336,305.40 (10.0%); £3,707,006.71 -> £3,336,305.58 (10.0%); £3,707,006.96 -> £3,336,305.77 (10.0%); £3,707,007.20 -> £3,336,305.96 (10.0%); £3,707,007.45 -> £3,336,305.99 (10.0%); £3,707,007.70 -> £3,336,306.01 (10.0%); £3,707,007.93 -> £3,336,306.04 (10.0%); £3,707,008.14 -> £3,336,306.06 (10.0%); £3,707,008.34 -> £3,336,306.08 (10.0%); £3,707,008.46 -> £3,336,306.10 (10.0%); £3,707,008.60 -> £3,336,306.12 (10.0%); £3,707,008.72 -> £3,336,306.14 (10.0%); £3,707,008.85 -> £3,336,306.15 (10.0%); £3,707,008.98 -> £3,336,306.17 (10.0%); £3,707,009.11 -> £3,336,306.19 (10.0%); £3,707,009.24 -> £3,336,306.20 (10.0%); £3,707,009.37 -> £3,336,306.22 (10.0%); £3,707,009.49 -> £3,336,306.24 (10.0%); £3,707,009.62 -> £3,336,306.25 (10.0%); £3,707,009.75 -> £3,336,306.27 (10.0%); £3,707,009.88 -> £3,336,306.44 (10.0%); £3,707,010.01 -> £3,336,306.61 (10.0%); £3,707,010.15 -> £3,336,306.79 (10.0%); £3,707,010.31 -> £3,336,306.96 (10.0%); £3,707,010.48 -> £3,336,307.14 (10.0%); £3,707,010.66 -> £3,336,307.31 (10.0%); £3,707,010.86 -> £3,336,307.49 (10.0%); £3,707,011.07 -> £3,336,307.67 (10.0%); £3,707,011.28 -> £3,336,307.70 (10.0%); £3,707,011.49 -> £3,336,307.72 (10.0%); £3,707,011.70 -> £3,336,307.75 (10.0%); £3,707,011.91 -> £3,336,307.77 (10.0%); £3,707,012.12 -> £3,336,307.80 (10.0%); £3,707,012.34 -> £3,336,307.83 (10.0%); £3,707,012.55 -> £3,336,307.85 (10.0%); £3,707,012.76 -> £3,336,307.88 (10.0%); £3,707,012.98 -> £3,336,307.90 (10.0%); £3,707,013.19 -> £3,336,307.93 (10.0%); £3,707,013.40 -> £3,336,307.95 (10.0%); £3,707,013.61 -> £3,336,307.98 (10.0%); £3,707,013.83 -> £3,336,308.01 (10.0%); £3,707,013.99 -> £3,336,308.18 (10.0%); £3,707,014.15 -> £3,336,308.36 (10.0%); £3,707,014.31 -> £3,336,308.54 (10.0%); £3,707,014.47 -> £3,336,308.72 (10.0%); £3,707,014.63 -> £3,336,308.90 (10.0%); £3,707,014.78 -> £3,336,309.09 (10.0%); £3,707,014.99 -> £3,336,309.27 (10.0%); £3,707,015.21 -> £3,336,309.45 (10.0%); £3,707,015.43 -> £3,336,309.63 (10.0%); £3,707,015.64 -> £3,336,309.81 (10.0%); £3,707,015.85 -> £3,336,309.99 (10.0%); £3,707,016.06 -> £3,336,310.01 (10.0%); £3,707,016.28 -> £3,336,310.04 (10.0%); £3,707,016.47 -> £3,336,310.07 (10.0%); £3,707,016.65 -> £3,336,310.09 (10.0%); £3,707,016.81 -> £3,336,310.11 (10.0%); £3,707,016.94 -> £3,336,310.13 (10.0%); £3,707,017.07 -> £3,336,310.15 (10.0%); £3,707,017.19 -> £3,336,310.17 (10.0%); £3,707,017.31 -> £3,336,310.19 (10.0%); £3,707,017.44 -> £3,336,310.20 (10.0%); £3,707,017.57 -> £3,336,310.22 (10.0%); £3,707,017.70 -> £3,336,310.24 (10.0%); £3,707,017.82 -> £3,336,310.25 (10.0%); £3,707,017.95 -> £3,336,310.27 (10.0%); £3,707,018.08 -> £3,336,310.29 (10.0%); £3,707,018.20 -> £3,336,310.30 (10.0%); £3,707,018.33 -> £3,336,310.52 (10.0%); £3,707,018.45 -> £3,336,310.73 (10.0%); £3,707,018.60 -> £3,336,310.94 (10.0%); £3,707,018.75 -> £3,336,311.16 (10.0%); £3,707,018.93 -> £3,336,311.37 (10.0%); £3,707,019.11 -> £3,336,311.60 (10.0%); £3,707,019.31 -> £3,336,311.81 (10.0%); £3,707,019.51 -> £3,336,312.03 (10.0%); £3,707,019.73 -> £3,336,312.06 (10.0%); £3,707,019.93 -> £3,336,312.09 (10.0%); £3,707,020.14 -> £3,336,312.12 (10.0%); £3,707,020.36 -> £3,336,312.15 (10.0%); £3,707,020.58 -> £3,336,312.18 (10.0%); £3,707,020.79 -> £3,336,312.21 (10.0%); £3,707,020.99 -> £3,336,312.24 (10.0%); £3,707,021.20 -> £3,336,312.27 (10.0%); £3,707,021.42 -> £3,336,312.30 (10.0%); £3,707,021.62 -> £3,336,312.33 (10.0%); £3,707,021.83 -> £3,336,312.36 (10.0%); £3,707,022.04 -> £3,336,312.39 (10.0%); £3,707,022.25 -> £3,336,312.42 (10.0%); £3,707,022.41 -> £3,336,312.63 (10.0%); £3,707,022.58 -> £3,336,312.84 (10.0%); £3,707,022.74 -> £3,336,313.06 (10.0%); £3,707,022.89 -> £3,336,313.28 (10.0%); £3,707,023.05 -> £3,336,313.50 (10.0%); £3,707,023.22 -> £3,336,313.71 (10.0%); £3,707,023.37 -> £3,336,313.93 (10.0%); £3,707,023.59 -> £3,336,314.14 (10.0%); £3,707,023.81 -> £3,336,314.36 (10.0%); £3,707,024.01 -> £3,336,314.59 (10.0%); £3,707,024.23 -> £3,336,314.81 (10.0%); £3,707,024.44 -> £3,336,314.84 (10.0%); £3,707,024.64 -> £3,336,314.86 (10.0%); £3,707,024.84 -> £3,336,314.89 (10.0%); £3,707,025.02 -> £3,336,314.91 (10.0%); £3,707,025.19 -> £3,336,314.93 (10.0%); £3,707,025.34 -> £3,336,314.95 (10.0%); £3,707,025.48 -> £3,336,314.96 (10.0%); £3,707,025.63 -> £3,336,314.98 (10.0%); £3,707,025.78 -> £3,336,315.00 (10.0%); £3,707,025.93 -> £3,336,315.01 (10.0%); £3,707,026.07 -> £3,336,315.03 (10.0%); £3,707,026.21 -> £3,336,315.05 (10.0%); £3,707,026.36 -> £3,336,315.06 (10.0%); £3,707,026.51 -> £3,336,315.08 (10.0%); £3,707,026.65 -> £3,336,315.10 (10.0%); £3,707,026.79 -> £3,336,315.12 (10.0%); £3,707,026.94 -> £3,336,315.36 (10.0%); £3,707,027.08 -> £3,336,315.61 (10.0%); £3,707,027.24 -> £3,336,315.86 (10.0%); £3,707,027.42 -> £3,336,316.12 (10.0%); £3,707,027.60 -> £3,336,316.38 (10.0%); £3,707,027.81 -> £3,336,316.63 (10.0%); £3,707,028.03 -> £3,336,316.88 (10.0%); £3,707,028.27 -> £3,336,317.13 (10.0%); £3,707,028.51 -> £3,336,317.16 (10.0%); £3,707,028.76 -> £3,336,317.18 (10.0%); £3,707,029.00 -> £3,336,317.20 (10.0%); £3,707,029.25 -> £3,336,317.23 (10.0%); £3,707,029.49 -> £3,336,317.25 (10.0%); £3,707,029.73 -> £3,336,317.28 (10.0%); £3,707,029.97 -> £3,336,317.30 (10.0%); £3,707,030.21 -> £3,336,317.32 (10.0%); £3,707,030.45 -> £3,336,317.35 (10.0%); £3,707,030.70 -> £3,336,317.37 (10.0%); £3,707,030.94 -> £3,336,317.39 (10.0%); £3,707,031.19 -> £3,336,317.42 (10.0%); £3,707,031.42 -> £3,336,317.45 (10.0%); £3,707,031.61 -> £3,336,317.69 (10.0%); £3,707,031.79 -> £3,336,317.94 (10.0%); £3,707,031.98 -> £3,336,318.19 (10.0%); £3,707,032.16 -> £3,336,318.43 (10.0%); £3,707,032.34 -> £3,336,318.69 (10.0%); £3,707,032.52 -> £3,336,318.94 (10.0%); £3,707,032.69 -> £3,336,319.20 (10.0%); £3,707,032.94 -> £3,336,319.44 (10.0%); £3,707,033.18 -> £3,336,319.70 (10.0%); £3,707,033.41 -> £3,336,319.95 (10.0%); £3,707,033.65 -> £3,336,320.21 (10.0%); £3,707,033.90 -> £3,336,320.24 (10.0%); £3,707,034.14 -> £3,336,320.26 (10.0%); £3,707,034.36 -> £3,336,320.29 (10.0%); £3,707,034.57 -> £3,336,320.31 (10.0%); £3,707,034.76 -> £3,336,320.33 (10.0%); £3,707,034.90 -> £3,336,320.35 (10.0%); £3,707,035.05 -> £3,336,320.37 (10.0%); £3,707,035.19 -> £3,336,320.38 (10.0%); £3,707,035.33 -> £3,336,320.40 (10.0%); £3,707,035.47 -> £3,336,320.42 (10.0%); £3,707,035.62 -> £3,336,320.43 (10.0%); £3,707,035.75 -> £3,336,320.45 (10.0%); £3,707,035.89 -> £3,336,320.47 (10.0%); £3,707,036.04 -> £3,336,320.48 (10.0%); £3,707,036.18 -> £3,336,320.50 (10.0%); £3,707,036.33 -> £3,336,320.52 (10.0%); £3,707,036.47 -> £3,336,320.75 (10.0%); £3,707,036.62 -> £3,336,320.96 (10.0%); £3,707,036.78 -> £3,336,321.19 (10.0%); £3,707,036.96 -> £3,336,321.41 (10.0%); £3,707,037.14 -> £3,336,321.63 (10.0%); £3,707,037.36 -> £3,336,321.85 (10.0%); £3,707,037.58 -> £3,336,322.08 (10.0%); £3,707,037.83 -> £3,336,322.30 (10.0%); £3,707,038.07 -> £3,336,322.32 (10.0%); £3,707,038.30 -> £3,336,322.34 (10.0%); £3,707,038.54 -> £3,336,322.37 (10.0%); £3,707,038.78 -> £3,336,322.39 (10.0%); £3,707,039.01 -> £3,336,322.41 (10.0%); £3,707,039.26 -> £3,336,322.44 (10.0%); £3,707,039.50 -> £3,336,322.46 (10.0%); £3,707,039.72 -> £3,336,322.49 (10.0%); £3,707,039.96 -> £3,336,322.51 (10.0%); £3,707,040.20 -> £3,336,322.53 (10.0%); £3,707,040.43 -> £3,336,322.55 (10.0%); £3,707,040.67 -> £3,336,322.58 (10.0%); £3,707,040.91 -> £3,336,322.61 (10.0%); £3,707,041.09 -> £3,336,322.83 (10.0%); £3,707,041.27 -> £3,336,323.06 (10.0%); £3,707,041.46 -> £3,336,323.30 (10.0%); £3,707,041.71 -> £3,336,323.54 (10.0%); £3,707,041.96 -> £3,336,323.78 (10.0%); £3,707,042.20 -> £3,336,324.01 (10.0%); £3,707,042.38 -> £3,336,324.24 (10.0%); £3,707,042.62 -> £3,336,324.47 (10.0%); £3,707,042.86 -> £3,336,324.70 (10.0%); £3,707,043.10 -> £3,336,324.91 (10.0%); £3,707,043.34 -> £3,336,325.14 (10.0%); £3,707,043.59 -> £3,336,325.16 (10.0%); £3,707,043.83 -> £3,336,325.19 (10.0%); £3,707,044.05 -> £3,336,325.22 (10.0%); £3,707,044.25 -> £3,336,325.24 (10.0%); £3,707,044.44 -> £3,336,325.26 (10.0%); £3,707,044.58 -> £3,336,325.28 (10.0%); £3,707,044.72 -> £3,336,325.29 (10.0%); £3,707,044.85 -> £3,336,325.31 (10.0%); £3,707,044.99 -> £3,336,325.33 (10.0%); £3,707,045.14 -> £3,336,325.35 (10.0%); £3,707,045.28 -> £3,336,325.36 (10.0%); £3,707,045.42 -> £3,336,325.38 (10.0%); £3,707,045.56 -> £3,336,325.40 (10.0%); £3,707,045.71 -> £3,336,325.41 (10.0%); £3,707,045.85 -> £3,336,325.43 (10.0%); £3,707,045.99 -> £3,336,325.45 (10.0%); £3,707,046.13 -> £3,336,325.69 (10.0%); £3,707,046.27 -> £3,336,325.93 (10.0%); £3,707,046.43 -> £3,336,326.18 (10.0%); £3,707,046.60 -> £3,336,326.43 (10.0%); £3,707,046.79 -> £3,336,326.67 (10.0%); £3,707,046.99 -> £3,336,326.92 (10.0%); £3,707,047.21 -> £3,336,327.17 (10.0%); £3,707,047.45 -> £3,336,327.42 (10.0%); £3,707,047.69 -> £3,336,327.44 (10.0%); £3,707,047.92 -> £3,336,327.46 (10.0%); £3,707,048.16 -> £3,336,327.49 (10.0%); £3,707,048.40 -> £3,336,327.51 (10.0%); £3,707,048.63 -> £3,336,327.54 (10.0%); £3,707,048.87 -> £3,336,327.56 (10.0%); £3,707,049.11 -> £3,336,327.58 (10.0%); £3,707,049.35 -> £3,336,327.61 (10.0%); £3,707,049.58 -> £3,336,327.63 (10.0%); £3,707,049.83 -> £3,336,327.65 (10.0%); £3,707,050.07 -> £3,336,327.67 (10.0%); £3,707,050.30 -> £3,336,327.70 (10.0%); £3,707,050.54 -> £3,336,327.73 (10.0%); £3,707,050.71 -> £3,336,327.96 (10.0%); £3,707,050.89 -> £3,336,328.21 (10.0%); £3,707,051.13 -> £3,336,328.46 (10.0%); £3,707,051.37 -> £3,336,328.71 (10.0%); £3,707,051.61 -> £3,336,328.96 (10.0%); £3,707,051.85 -> £3,336,329.21 (10.0%); £3,707,052.09 -> £3,336,329.46 (10.0%); £3,707,052.33 -> £3,336,329.71 (10.0%); £3,707,052.57 -> £3,336,329.95 (10.0%); £3,707,052.80 -> £3,336,330.19 (10.0%); £3,707,053.04 -> £3,336,330.42 (10.0%); £3,707,053.27 -> £3,336,330.45 (10.0%); £3,707,053.50 -> £3,336,330.48 (10.0%); £3,707,053.71 -> £3,336,330.50 (10.0%); £3,707,053.91 -> £3,336,330.52 (10.0%); £3,707,054.09 -> £3,336,330.54 (10.0%); £3,707,054.23 -> £3,336,330.56 (10.0%); £3,707,054.37 -> £3,336,330.58 (10.0%); £3,707,054.52 -> £3,336,330.60 (10.0%); £3,707,054.66 -> £3,336,330.62 (10.0%); £3,707,054.80 -> £3,336,330.63 (10.0%); £3,707,054.94 -> £3,336,330.65 (10.0%); £3,707,055.08 -> £3,336,330.66 (10.0%); £3,707,055.22 -> £3,336,330.68 (10.0%); £3,707,055.37 -> £3,336,330.70 (10.0%); £3,707,055.51 -> £3,336,330.71 (10.0%); £3,707,055.66 -> £3,336,330.73 (10.0%); £3,707,055.80 -> £3,336,330.99 (10.0%); £3,707,055.95 -> £3,336,331.26 (10.0%); £3,707,056.10 -> £3,336,331.53 (10.0%); £3,707,056.27 -> £3,336,331.80 (10.0%); £3,707,056.46 -> £3,336,332.07 (10.0%); £3,707,056.67 -> £3,336,332.34 (10.0%); £3,707,056.89 -> £3,336,332.61 (10.0%); £3,707,057.12 -> £3,336,332.88 (10.0%); £3,707,057.36 -> £3,336,332.90 (10.0%); £3,707,057.59 -> £3,336,332.92 (10.0%); £3,707,057.82 -> £3,336,332.95 (10.0%); £3,707,058.05 -> £3,336,332.97 (10.0%); £3,707,058.28 -> £3,336,333.00 (10.0%); £3,707,058.52 -> £3,336,333.02 (10.0%); £3,707,058.76 -> £3,336,333.04 (10.0%); £3,707,059.00 -> £3,336,333.07 (10.0%); £3,707,059.24 -> £3,336,333.09 (10.0%); £3,707,059.47 -> £3,336,333.11 (10.0%); £3,707,059.70 -> £3,336,333.14 (10.0%); £3,707,059.94 -> £3,336,333.16 (10.0%); £3,707,060.18 -> £3,336,333.19 (10.0%); £3,707,060.36 -> £3,336,333.46 (10.0%); £3,707,060.54 -> £3,336,333.73 (10.0%); £3,707,060.72 -> £3,336,334.00 (10.0%); £3,707,060.89 -> £3,336,334.27 (10.0%); £3,707,061.07 -> £3,336,334.55 (10.0%); £3,707,061.24 -> £3,336,334.82 (10.0%); £3,707,061.42 -> £3,336,335.09 (10.0%); £3,707,061.65 -> £3,336,335.35 (10.0%); £3,707,061.88 -> £3,336,335.62 (10.0%); £3,707,062.12 -> £3,336,335.89 (10.0%); £3,707,062.34 -> £3,336,336.17 (10.0%); £3,707,062.58 -> £3,336,336.20 (10.0%); £3,707,062.82 -> £3,336,336.22 (10.0%); £3,707,063.04 -> £3,336,336.25 (10.0%); £3,707,063.25 -> £3,336,336.27 (10.0%); £3,707,063.44 -> £3,336,336.29 (10.0%); £3,707,063.58 -> £3,336,336.31 (10.0%); £3,707,063.72 -> £3,336,336.33 (10.0%); £3,707,063.87 -> £3,336,336.34 (10.0%); £3,707,064.01 -> £3,336,336.36 (10.0%); £3,707,064.15 -> £3,336,336.38 (10.0%); £3,707,064.30 -> £3,336,336.39 (10.0%); £3,707,064.44 -> £3,336,336.41 (10.0%); £3,707,064.59 -> £3,336,336.43 (10.0%); £3,707,064.72 -> £3,336,336.44 (10.0%); £3,707,064.87 -> £3,336,336.46 (10.0%); £3,707,065.02 -> £3,336,336.48 (10.0%); £3,707,065.16 -> £3,336,336.70 (10.0%); £3,707,065.30 -> £3,336,336.93 (10.0%); £3,707,065.46 -> £3,336,337.16 (10.0%); £3,707,065.64 -> £3,336,337.39 (10.0%); £3,707,065.83 -> £3,336,337.62 (10.0%); £3,707,066.03 -> £3,336,337.85 (10.0%); £3,707,066.25 -> £3,336,338.08 (10.0%); £3,707,066.49 -> £3,336,338.31 (10.0%); £3,707,066.72 -> £3,336,338.33 (10.0%); £3,707,066.96 -> £3,336,338.36 (10.0%); £3,707,067.19 -> £3,336,338.38 (10.0%); £3,707,067.44 -> £3,336,338.40 (10.0%); £3,707,067.68 -> £3,336,338.43 (10.0%); £3,707,067.92 -> £3,336,338.45 (10.0%); £3,707,068.16 -> £3,336,338.48 (10.0%); £3,707,068.40 -> £3,336,338.50 (10.0%); £3,707,068.62 -> £3,336,338.52 (10.0%); £3,707,068.86 -> £3,336,338.55 (10.0%); £3,707,069.10 -> £3,336,338.57 (10.0%); £3,707,069.34 -> £3,336,338.60 (10.0%); £3,707,069.58 -> £3,336,338.62 (10.0%); £3,707,069.81 -> £3,336,338.85 (10.0%); £3,707,069.99 -> £3,336,339.08 (10.0%); £3,707,070.17 -> £3,336,339.32 (10.0%); £3,707,070.35 -> £3,336,339.55 (10.0%); £3,707,070.52 -> £3,336,339.79 (10.0%); £3,707,070.77 -> £3,336,340.03 (10.0%); £3,707,071.01 -> £3,336,340.26 (10.0%); £3,707,071.26 -> £3,336,340.50 (10.0%); £3,707,071.50 -> £3,336,340.73 (10.0%); £3,707,071.74 -> £3,336,340.96 (10.0%); £3,707,071.99 -> £3,336,341.19 (10.0%); £3,707,072.23 -> £3,336,341.22 (10.0%); £3,707,072.47 -> £3,336,341.24 (10.0%); £3,707,072.69 -> £3,336,341.27 (10.0%); £3,707,072.89 -> £3,336,341.29 (10.0%); £3,707,073.08 -> £3,336,341.31 (10.0%); £3,707,073.21 -> £3,336,341.33 (10.0%); £3,707,073.34 -> £3,336,341.35 (10.0%); £3,707,073.46 -> £3,336,341.37 (10.0%); £3,707,073.59 -> £3,336,341.38 (10.0%); £3,707,073.72 -> £3,336,341.40 (10.0%); £3,707,073.85 -> £3,336,341.42 (10.0%); £3,707,073.98 -> £3,336,341.43 (10.0%); £3,707,074.11 -> £3,336,341.45 (10.0%); £3,707,074.23 -> £3,336,341.47 (10.0%); £3,707,074.36 -> £3,336,341.49 (10.0%); £3,707,074.49 -> £3,336,341.50 (10.0%); £3,707,074.62 -> £3,336,341.68 (10.0%); £3,707,074.75 -> £3,336,341.85 (10.0%); £3,707,074.89 -> £3,336,342.03 (10.0%); £3,707,075.05 -> £3,336,342.21 (10.0%); £3,707,075.22 -> £3,336,342.40 (10.0%); £3,707,075.41 -> £3,336,342.58 (10.0%); £3,707,075.62 -> £3,336,342.76 (10.0%); £3,707,075.83 -> £3,336,342.94 (10.0%); £3,707,076.04 -> £3,336,342.97 (10.0%); £3,707,076.26 -> £3,336,343.00 (10.0%); £3,707,076.47 -> £3,336,343.02 (10.0%); £3,707,076.68 -> £3,336,343.05 (10.0%); £3,707,076.90 -> £3,336,343.08 (10.0%); £3,707,077.11 -> £3,336,343.10 (10.0%); £3,707,077.32 -> £3,336,343.13 (10.0%); £3,707,077.54 -> £3,336,343.15 (10.0%); £3,707,077.76 -> £3,336,343.18 (10.0%); £3,707,077.97 -> £3,336,343.20 (10.0%); £3,707,078.19 -> £3,336,343.23 (10.0%); £3,707,078.39 -> £3,336,343.26 (10.0%); £3,707,078.61 -> £3,336,343.28 (10.0%); £3,707,078.78 -> £3,336,343.46 (10.0%); £3,707,078.94 -> £3,336,343.65 (10.0%); £3,707,079.10 -> £3,336,343.84 (10.0%); £3,707,079.26 -> £3,336,344.02 (10.0%); £3,707,079.42 -> £3,336,344.21 (10.0%); £3,707,079.59 -> £3,336,344.40 (10.0%); £3,707,079.75 -> £3,336,344.58 (10.0%); £3,707,079.96 -> £3,336,344.77 (10.0%); £3,707,080.18 -> £3,336,344.95 (10.0%); £3,707,080.39 -> £3,336,345.13 (10.0%); £3,707,080.61 -> £3,336,345.31 (10.0%); £3,707,080.82 -> £3,336,345.34 (10.0%); £3,707,081.03 -> £3,336,345.37 (10.0%); £3,707,081.24 -> £3,336,345.39 (10.0%); £3,707,081.42 -> £3,336,345.42 (10.0%); £3,707,081.58 -> £3,336,345.44 (10.0%); £3,707,081.71 -> £3,336,345.46 (10.0%); £3,707,081.84 -> £3,336,345.48 (10.0%); £3,707,081.97 -> £3,336,345.50 (10.0%); £3,707,082.10 -> £3,336,345.52 (10.0%); £3,707,082.23 -> £3,336,345.53 (10.0%); £3,707,082.36 -> £3,336,345.55 (10.0%); £3,707,082.49 -> £3,336,345.57 (10.0%); £3,707,082.61 -> £3,336,345.58 (10.0%); £3,707,082.74 -> £3,336,345.60 (10.0%); £3,707,082.87 -> £3,336,345.62 (10.0%); £3,707,083.00 -> £3,336,345.63 (10.0%); £3,707,083.13 -> £3,336,345.75 (10.0%); £3,707,083.26 -> £3,336,345.86 (10.0%); £3,707,083.40 -> £3,336,345.97 (10.0%); £3,707,083.56 -> £3,336,346.08 (10.0%); £3,707,083.73 -> £3,336,346.21 (10.0%); £3,707,083.92 -> £3,336,346.33 (10.0%); £3,707,084.12 -> £3,336,346.45 (10.0%); £3,707,084.34 -> £3,336,346.57 (10.0%); £3,707,084.56 -> £3,336,346.60 (10.0%); £3,707,084.77 -> £3,336,346.63 (10.0%); £3,707,084.99 -> £3,336,346.66 (10.0%); £3,707,085.20 -> £3,336,346.69 (10.0%); £3,707,085.41 -> £3,336,346.73 (10.0%); £3,707,085.63 -> £3,336,346.76 (10.0%); £3,707,085.84 -> £3,336,346.79 (10.0%); £3,707,086.06 -> £3,336,346.82 (10.0%); £3,707,086.27 -> £3,336,346.85 (10.0%); £3,707,086.48 -> £3,336,346.87 (10.0%); £3,707,086.70 -> £3,336,346.90 (10.0%); £3,707,086.92 -> £3,336,346.93 (10.0%); £3,707,087.14 -> £3,336,346.96 (10.0%); £3,707,087.30 -> £3,336,347.09 (10.0%); £3,707,087.46 -> £3,336,347.22 (10.0%); £3,707,087.62 -> £3,336,347.35 (10.0%); £3,707,087.77 -> £3,336,347.48 (10.0%); £3,707,087.94 -> £3,336,347.61 (10.0%); £3,707,088.10 -> £3,336,347.74 (10.0%); £3,707,088.25 -> £3,336,347.87 (10.0%); £3,707,088.48 -> £3,336,348.00 (10.0%); £3,707,088.69 -> £3,336,348.12 (10.0%); £3,707,088.91 -> £3,336,348.25 (10.0%); £3,707,089.12 -> £3,336,348.37 (10.0%); £3,707,089.33 -> £3,336,348.40 (10.0%); £3,707,089.55 -> £3,336,348.43 (10.0%); £3,707,089.74 -> £3,336,348.45 (10.0%); £3,707,089.92 -> £3,336,348.48 (10.0%); £3,707,090.08 -> £3,336,348.50 (10.0%); £3,707,090.23 -> £3,336,348.51 (10.0%); £3,707,090.38 -> £3,336,348.53 (10.0%); £3,707,090.52 -> £3,336,348.55 (10.0%); £3,707,090.67 -> £3,336,348.57 (10.0%); £3,707,090.81 -> £3,336,348.58 (10.0%); £3,707,090.96 -> £3,336,348.60 (10.0%); £3,707,091.11 -> £3,336,348.62 (10.0%); £3,707,091.26 -> £3,336,348.63 (10.0%); £3,707,091.40 -> £3,336,348.65 (10.0%); £3,707,091.54 -> £3,336,348.67 (10.0%); £3,707,091.69 -> £3,336,348.68 (10.0%); £3,707,091.84 -> £3,336,348.81 (10.0%); £3,707,091.98 -> £3,336,348.94 (10.0%); £3,707,092.14 -> £3,336,349.08 (10.0%); £3,707,092.32 -> £3,336,349.22 (10.0%); £3,707,092.52 -> £3,336,349.35 (10.0%); £3,707,092.74 -> £3,336,349.49 (10.0%); £3,707,092.97 -> £3,336,349.62 (10.0%); £3,707,093.22 -> £3,336,349.76 (10.0%); £3,707,093.47 -> £3,336,349.78 (10.0%); £3,707,093.71 -> £3,336,349.81 (10.0%); £3,707,093.97 -> £3,336,349.83 (10.0%); £3,707,094.20 -> £3,336,349.85 (10.0%); £3,707,094.45 -> £3,336,349.88 (10.0%); £3,707,094.71 -> £3,336,349.90 (10.0%); £3,707,094.95 -> £3,336,349.93 (10.0%); £3,707,095.20 -> £3,336,349.95 (10.0%); £3,707,095.46 -> £3,336,349.97 (10.0%); £3,707,095.71 -> £3,336,350.00 (10.0%); £3,707,095.95 -> £3,336,350.02 (10.0%); £3,707,096.20 -> £3,336,350.05 (10.0%); £3,707,096.45 -> £3,336,350.07 (10.0%); £3,707,096.70 -> £3,336,350.22 (10.0%); £3,707,096.88 -> £3,336,350.36 (10.0%); £3,707,097.06 -> £3,336,350.51 (10.0%); £3,707,097.25 -> £3,336,350.66 (10.0%); £3,707,097.42 -> £3,336,350.81 (10.0%); £3,707,097.61 -> £3,336,350.95 (10.0%); £3,707,097.79 -> £3,336,351.10 (10.0%); £3,707,098.03 -> £3,336,351.24 (10.0%); £3,707,098.27 -> £3,336,351.39 (10.0%); £3,707,098.52 -> £3,336,351.53 (10.0%); £3,707,098.77 -> £3,336,351.67 (10.0%); £3,707,099.01 -> £3,336,351.70 (10.0%); £3,707,099.26 -> £3,336,351.73 (10.0%); £3,707,099.49 -> £3,336,351.76 (10.0%); £3,707,099.70 -> £3,336,351.78 (10.0%); £3,707,099.89 -> £3,336,351.80 (10.0%); £3,707,100.04 -> £3,336,351.82 (10.0%); £3,707,100.19 -> £3,336,351.84 (10.0%); £3,707,100.33 -> £3,336,351.85 (10.0%); £3,707,100.47 -> £3,336,351.87 (10.0%); £3,707,100.63 -> £3,336,351.89 (10.0%); £3,707,100.78 -> £3,336,351.90 (10.0%); £3,707,100.92 -> £3,336,351.92 (10.0%); £3,707,101.07 -> £3,336,351.94 (10.0%); £3,707,101.22 -> £3,336,351.95 (10.0%); £3,707,101.36 -> £3,336,351.97 (10.0%); £3,707,101.51 -> £3,336,351.99 (10.0%); £3,707,101.66 -> £3,336,352.11 (10.0%); £3,707,101.81 -> £3,336,352.23 (10.0%); £3,707,101.98 -> £3,336,352.35 (10.0%); £3,707,102.16 -> £3,336,352.48 (10.0%); £3,707,102.36 -> £3,336,352.61 (10.0%); £3,707,102.57 -> £3,336,352.74 (10.0%); £3,707,102.81 -> £3,336,352.86 (10.0%); £3,707,103.05 -> £3,336,352.99 (10.0%); £3,707,103.30 -> £3,336,353.01 (10.0%); £3,707,103.54 -> £3,336,353.03 (10.0%); £3,707,103.79 -> £3,336,353.06 (10.0%); £3,707,104.03 -> £3,336,353.08 (10.0%); £3,707,104.29 -> £3,336,353.11 (10.0%); £3,707,104.53 -> £3,336,353.13 (10.0%); £3,707,104.78 -> £3,336,353.16 (10.0%); £3,707,105.02 -> £3,336,353.18 (10.0%); £3,707,105.27 -> £3,336,353.20 (10.0%); £3,707,105.51 -> £3,336,353.23 (10.0%); £3,707,105.75 -> £3,336,353.25 (10.0%); £3,707,106.00 -> £3,336,353.27 (10.0%); £3,707,106.25 -> £3,336,353.30 (10.0%); £3,707,106.43 -> £3,336,353.43 (10.0%); £3,707,106.62 -> £3,336,353.58 (10.0%); £3,707,106.88 -> £3,336,353.72 (10.0%); £3,707,107.12 -> £3,336,353.86 (10.0%); £3,707,107.36 -> £3,336,354.00 (10.0%); £3,707,107.61 -> £3,336,354.14 (10.0%); £3,707,107.80 -> £3,336,354.27 (10.0%); £3,707,108.05 -> £3,336,354.40 (10.0%); £3,707,108.30 -> £3,336,354.54 (10.0%); £3,707,108.55 -> £3,336,354.67 (10.0%); £3,707,108.80 -> £3,336,354.80 (10.0%); £3,707,109.05 -> £3,336,354.83 (10.0%); £3,707,109.30 -> £3,336,354.86 (10.0%); £3,707,109.53 -> £3,336,354.88 (10.0%); £3,707,109.73 -> £3,336,354.91 (10.0%); £3,707,109.93 -> £3,336,354.93 (10.0%); £3,707,110.07 -> £3,336,354.94 (10.0%); £3,707,110.22 -> £3,336,354.96 (10.0%); £3,707,110.37 -> £3,336,354.98 (10.0%); £3,707,110.52 -> £3,336,355.00 (10.0%); £3,707,110.67 -> £3,336,355.01 (10.0%); £3,707,110.82 -> £3,336,355.03 (10.0%); £3,707,110.96 -> £3,336,355.05 (10.0%); £3,707,111.11 -> £3,336,355.07 (10.0%); £3,707,111.26 -> £3,336,355.08 (10.0%); £3,707,111.41 -> £3,336,355.10 (10.0%); £3,707,111.56 -> £3,336,355.12 (10.0%); £3,707,111.72 -> £3,336,355.24 (10.0%); £3,707,111.87 -> £3,336,355.37 (10.0%); £3,707,112.04 -> £3,336,355.50 (10.0%); £3,707,112.23 -> £3,336,355.63 (10.0%); £3,707,112.42 -> £3,336,355.76 (10.0%); £3,707,112.63 -> £3,336,355.89 (10.0%); £3,707,112.87 -> £3,336,356.02 (10.0%); £3,707,113.12 -> £3,336,356.16 (10.0%); £3,707,113.37 -> £3,336,356.18 (10.0%); £3,707,113.62 -> £3,336,356.20 (10.0%); £3,707,113.87 -> £3,336,356.23 (10.0%); £3,707,114.13 -> £3,336,356.25 (10.0%); £3,707,114.37 -> £3,336,356.28 (10.0%); £3,707,114.62 -> £3,336,356.30 (10.0%); £3,707,114.87 -> £3,336,356.33 (10.0%); £3,707,115.13 -> £3,336,356.35 (10.0%); £3,707,115.39 -> £3,336,356.37 (10.0%); £3,707,115.64 -> £3,336,356.40 (10.0%); £3,707,115.90 -> £3,336,356.42 (10.0%); £3,707,116.15 -> £3,336,356.45 (10.0%); £3,707,116.40 -> £3,336,356.48 (10.0%); £3,707,116.65 -> £3,336,356.61 (10.0%); £3,707,116.83 -> £3,336,356.76 (10.0%); £3,707,117.02 -> £3,336,356.91 (10.0%); £3,707,117.27 -> £3,336,357.06 (10.0%); £3,707,117.52 -> £3,336,357.21 (10.0%); £3,707,117.78 -> £3,336,357.35 (10.0%); £3,707,117.97 -> £3,336,357.49 (10.0%); £3,707,118.22 -> £3,336,357.64 (10.0%); £3,707,118.48 -> £3,336,357.78 (10.0%); £3,707,118.73 -> £3,336,357.93 (10.0%); £3,707,118.98 -> £3,336,358.07 (10.0%); £3,707,119.23 -> £3,336,358.09 (10.0%); £3,707,119.48 -> £3,336,358.12 (10.0%); £3,707,119.72 -> £3,336,358.14 (10.0%); £3,707,119.94 -> £3,336,358.17 (10.0%); £3,707,120.13 -> £3,336,358.19 (10.0%); £3,707,120.28 -> £3,336,358.21 (10.0%); £3,707,120.44 -> £3,336,358.22 (10.0%); £3,707,120.59 -> £3,336,358.24 (10.0%); £3,707,120.75 -> £3,336,358.26 (10.0%); £3,707,120.90 -> £3,336,358.27 (10.0%); £3,707,121.06 -> £3,336,358.29 (10.0%); £3,707,121.21 -> £3,336,358.31 (10.0%); £3,707,121.37 -> £3,336,358.32 (10.0%); £3,707,121.52 -> £3,336,358.34 (10.0%); £3,707,121.67 -> £3,336,358.36 (10.0%); £3,707,121.83 -> £3,336,358.38 (10.0%); £3,707,121.98 -> £3,336,358.49 (10.0%); £3,707,122.14 -> £3,336,358.61 (10.0%); £3,707,122.31 -> £3,336,358.73 (10.0%); £3,707,122.49 -> £3,336,358.85 (10.0%); £3,707,122.70 -> £3,336,358.98 (10.0%); £3,707,122.91 -> £3,336,359.10 (10.0%); £3,707,123.15 -> £3,336,359.22 (10.0%); £3,707,123.40 -> £3,336,359.35 (10.0%); £3,707,123.66 -> £3,336,359.37 (10.0%); £3,707,123.92 -> £3,336,359.39 (10.0%); £3,707,124.16 -> £3,336,359.42 (10.0%); £3,707,124.42 -> £3,336,359.44 (10.0%); £3,707,124.67 -> £3,336,359.47 (10.0%); £3,707,124.93 -> £3,336,359.49 (10.0%); £3,707,125.19 -> £3,336,359.52 (10.0%); £3,707,125.44 -> £3,336,359.54 (10.0%); £3,707,125.70 -> £3,336,359.56 (10.0%); £3,707,125.96 -> £3,336,359.59 (10.0%); £3,707,126.21 -> £3,336,359.61 (10.0%); £3,707,126.47 -> £3,336,359.64 (10.0%); £3,707,126.73 -> £3,336,359.66 (10.0%); £3,707,126.92 -> £3,336,359.79 (10.0%); £3,707,127.11 -> £3,336,359.93 (10.0%); £3,707,127.29 -> £3,336,360.06 (10.0%); £3,707,127.48 -> £3,336,360.20 (10.0%); £3,707,127.74 -> £3,336,360.34 (10.0%); £3,707,127.99 -> £3,336,360.47 (10.0%); £3,707,128.19 -> £3,336,360.60 (10.0%); £3,707,128.45 -> £3,336,360.73 (10.0%); £3,707,128.71 -> £3,336,360.86 (10.0%); £3,707,128.97 -> £3,336,360.99 (10.0%); £3,707,129.22 -> £3,336,361.12 (10.0%); £3,707,129.47 -> £3,336,361.15 (10.0%); £3,707,129.73 -> £3,336,361.18 (10.0%); £3,707,129.96 -> £3,336,361.20 (10.0%); £3,707,130.18 -> £3,336,361.23 (10.0%); £3,707,130.38 -> £3,336,361.25 (10.0%); £3,707,130.54 -> £3,336,361.26 (10.0%); £3,707,130.69 -> £3,336,361.28 (10.0%); £3,707,130.84 -> £3,336,361.30 (10.0%); £3,707,130.99 -> £3,336,361.32 (10.0%); £3,707,131.14 -> £3,336,361.33 (10.0%); £3,707,131.29 -> £3,336,361.35 (10.0%); £3,707,131.45 -> £3,336,361.37 (10.0%); £3,707,131.60 -> £3,336,361.38 (10.0%); £3,707,131.76 -> £3,336,361.40 (10.0%); £3,707,131.91 -> £3,336,361.42 (10.0%); £3,707,132.06 -> £3,336,361.43 (10.0%); £3,707,132.22 -> £3,336,361.57 (10.0%); £3,707,132.37 -> £3,336,361.70 (10.0%); £3,707,132.54 -> £3,336,361.84 (10.0%); £3,707,132.73 -> £3,336,361.98 (10.0%); £3,707,132.93 -> £3,336,362.12 (10.0%); £3,707,133.16 -> £3,336,362.26 (10.0%); £3,707,133.40 -> £3,336,362.40 (10.0%); £3,707,133.66 -> £3,336,362.54 (10.0%); £3,707,133.93 -> £3,336,362.56 (10.0%); £3,707,134.19 -> £3,336,362.59 (10.0%); £3,707,134.45 -> £3,336,362.61 (10.0%); £3,707,134.71 -> £3,336,362.64 (10.0%); £3,707,134.96 -> £3,336,362.66 (10.0%); £3,707,135.20 -> £3,336,362.69 (10.0%); £3,707,135.46 -> £3,336,362.72 (10.0%); £3,707,135.71 -> £3,336,362.74 (10.0%); £3,707,135.98 -> £3,336,362.76 (10.0%); £3,707,136.24 -> £3,336,362.79 (10.0%); £3,707,136.48 -> £3,336,362.81 (10.0%); £3,707,136.73 -> £3,336,362.84 (10.0%); £3,707,136.99 -> £3,336,362.86 (10.0%); £3,707,137.19 -> £3,336,363.01 (10.0%); £3,707,137.38 -> £3,336,363.16 (10.0%); £3,707,137.58 -> £3,336,363.31 (10.0%); £3,707,137.77 -> £3,336,363.46 (10.0%); £3,707,137.97 -> £3,336,363.61 (10.0%); £3,707,138.16 -> £3,336,363.76 (10.0%); £3,707,138.35 -> £3,336,363.91 (10.0%); £3,707,138.61 -> £3,336,364.06 (10.0%); £3,707,138.87 -> £3,336,364.22 (10.0%); £3,707,139.12 -> £3,336,364.37 (10.0%); £3,707,139.38 -> £3,336,364.51 (10.0%); £3,707,139.63 -> £3,336,364.54 (10.0%); £3,707,139.89 -> £3,336,364.57 (10.0%); £3,707,140.12 -> £3,336,364.59 (10.0%); £3,707,140.34 -> £3,336,364.62 (10.0%); £3,707,140.54 -> £3,336,364.64 (10.0%); £3,707,140.69 -> £3,336,364.66 (10.0%); £3,707,140.82 -> £3,336,364.68 (10.0%); £3,707,140.96 -> £3,336,364.70 (10.0%); £3,707,141.10 -> £3,336,364.71 (10.0%); £3,707,141.24 -> £3,336,364.73 (10.0%); £3,707,141.39 -> £3,336,364.75 (10.0%); £3,707,141.53 -> £3,336,364.76 (10.0%); £3,707,141.67 -> £3,336,364.78 (10.0%); £3,707,141.80 -> £3,336,364.80 (10.0%); £3,707,141.94 -> £3,336,364.81 (10.0%); £3,707,142.07 -> £3,336,364.83 (10.0%); £3,707,142.21 -> £3,336,364.99 (10.0%); £3,707,142.36 -> £3,336,365.14 (10.0%); £3,707,142.51 -> £3,336,365.30 (10.0%); £3,707,142.68 -> £3,336,365.46 (10.0%); £3,707,142.88 -> £3,336,365.63 (10.0%); £3,707,143.07 -> £3,336,365.79 (10.0%); £3,707,143.29 -> £3,336,365.95 (10.0%); £3,707,143.52 -> £3,336,366.12 (10.0%); £3,707,143.75 -> £3,336,366.14 (10.0%); £3,707,143.99 -> £3,336,366.17 (10.0%); £3,707,144.22 -> £3,336,366.20 (10.0%); £3,707,144.46 -> £3,336,366.22 (10.0%); £3,707,144.68 -> £3,336,366.25 (10.0%); £3,707,144.90 -> £3,336,366.28 (10.0%); £3,707,145.14 -> £3,336,366.31 (10.0%); £3,707,145.38 -> £3,336,366.33 (10.0%); £3,707,145.61 -> £3,336,366.36 (10.0%); £3,707,145.84 -> £3,336,366.39 (10.0%); £3,707,146.07 -> £3,336,366.41 (10.0%); £3,707,146.30 -> £3,336,366.44 (10.0%); £3,707,146.52 -> £3,336,366.47 (10.0%); £3,707,146.70 -> £3,336,366.63 (10.0%); £3,707,146.88 -> £3,336,366.79 (10.0%); £3,707,147.05 -> £3,336,366.96 (10.0%); £3,707,147.22 -> £3,336,367.13 (10.0%); £3,707,147.39 -> £3,336,367.31 (10.0%); £3,707,147.63 -> £3,336,367.48 (10.0%); £3,707,147.86 -> £3,336,367.65 (10.0%); £3,707,148.09 -> £3,336,367.82 (10.0%); £3,707,148.32 -> £3,336,367.98 (10.0%); £3,707,148.55 -> £3,336,368.15 (10.0%); £3,707,148.78 -> £3,336,368.32 (10.0%); £3,707,149.01 -> £3,336,368.35 (10.0%); £3,707,149.24 -> £3,336,368.37 (10.0%); £3,707,149.45 -> £3,336,368.40 (10.0%); £3,707,149.64 -> £3,336,368.42 (10.0%); £3,707,149.82 -> £3,336,368.44 (10.0%); £3,707,149.95 -> £3,336,368.47 (10.0%); £3,707,150.10 -> £3,336,368.48 (10.0%); £3,707,150.24 -> £3,336,368.50 (10.0%); £3,707,150.38 -> £3,336,368.52 (10.0%); £3,707,150.52 -> £3,336,368.54 (10.0%); £3,707,150.66 -> £3,336,368.56 (10.0%); £3,707,150.80 -> £3,336,368.57 (10.0%); £3,707,150.95 -> £3,336,368.59 (10.0%); £3,707,151.09 -> £3,336,368.61 (10.0%); £3,707,151.22 -> £3,336,368.62 (10.0%); £3,707,151.35 -> £3,336,368.64 (10.0%); £3,707,151.49 -> £3,336,368.77 (10.0%); £3,707,151.63 -> £3,336,368.90 (10.0%); £3,707,151.79 -> £3,336,369.03 (10.0%); £3,707,151.97 -> £3,336,369.16 (10.0%); £3,707,152.15 -> £3,336,369.29 (10.0%); £3,707,152.36 -> £3,336,369.43 (10.0%); £3,707,152.58 -> £3,336,369.56 (10.0%); £3,707,152.81 -> £3,336,369.70 (10.0%); £3,707,153.05 -> £3,336,369.73 (10.0%); £3,707,153.28 -> £3,336,369.76 (10.0%); £3,707,153.51 -> £3,336,369.79 (10.0%); £3,707,153.75 -> £3,336,369.82 (10.0%); £3,707,153.98 -> £3,336,369.86 (10.0%); £3,707,154.21 -> £3,336,369.89 (10.0%); £3,707,154.43 -> £3,336,369.92 (10.0%); £3,707,154.66 -> £3,336,369.95 (10.0%); £3,707,154.90 -> £3,336,369.98 (10.0%); £3,707,155.14 -> £3,336,370.00 (10.0%); £3,707,155.37 -> £3,336,370.03 (10.0%); £3,707,155.60 -> £3,336,370.06 (10.0%); £3,707,155.82 -> £3,336,370.09 (10.0%); £3,707,156.00 -> £3,336,370.23 (10.0%); £3,707,156.17 -> £3,336,370.37 (10.0%); £3,707,156.34 -> £3,336,370.52 (10.0%); £3,707,156.52 -> £3,336,370.67 (10.0%); £3,707,156.75 -> £3,336,370.82 (10.0%); £3,707,156.98 -> £3,336,370.96 (10.0%); £3,707,157.16 -> £3,336,371.11 (10.0%); £3,707,157.39 -> £3,336,371.25 (10.0%); £3,707,157.63 -> £3,336,371.39 (10.0%); £3,707,157.86 -> £3,336,371.52 (10.0%); £3,707,158.10 -> £3,336,371.66 (10.0%); £3,707,158.34 -> £3,336,371.69 (10.0%); £3,707,158.57 -> £3,336,371.72 (10.0%); £3,707,158.78 -> £3,336,371.74 (10.0%); £3,707,158.98 -> £3,336,371.77 (10.0%); £3,707,159.15 -> £3,336,371.79 (10.0%); £3,707,159.31 -> £3,336,371.80 (10.0%); £3,707,159.47 -> £3,336,371.82 (10.0%); £3,707,159.63 -> £3,336,371.84 (10.0%); £3,707,159.79 -> £3,336,371.85 (10.0%); £3,707,159.95 -> £3,336,371.87 (10.0%); £3,707,160.11 -> £3,336,371.89 (10.0%); £3,707,160.27 -> £3,336,371.90 (10.0%); £3,707,160.43 -> £3,336,371.92 (10.0%); £3,707,160.59 -> £3,336,371.94 (10.0%); £3,707,160.75 -> £3,336,371.95 (10.0%); £3,707,160.92 -> £3,336,371.97 (10.0%); £3,707,161.08 -> £3,336,372.06 (10.0%); £3,707,161.24 -> £3,336,372.15 (10.0%); £3,707,161.42 -> £3,336,372.25 (10.0%); £3,707,161.62 -> £3,336,372.35 (10.0%); £3,707,161.83 -> £3,336,372.45 (10.0%); £3,707,162.07 -> £3,336,372.55 (10.0%); £3,707,162.32 -> £3,336,372.65 (10.0%); £3,707,162.60 -> £3,336,372.75 (10.0%); £3,707,162.86 -> £3,336,372.77 (10.0%); £3,707,163.13 -> £3,336,372.79 (10.0%); £3,707,163.41 -> £3,336,372.82 (10.0%); £3,707,163.67 -> £3,336,372.84 (10.0%); £3,707,163.93 -> £3,336,372.86 (10.0%); £3,707,164.20 -> £3,336,372.89 (10.0%); £3,707,164.46 -> £3,336,372.91 (10.0%); £3,707,164.72 -> £3,336,372.93 (10.0%); £3,707,164.98 -> £3,336,372.96 (10.0%); £3,707,165.24 -> £3,336,372.98 (10.0%); £3,707,165.51 -> £3,336,373.00 (10.0%); £3,707,165.78 -> £3,336,373.03 (10.0%); £3,707,166.05 -> £3,336,373.06 (10.0%); £3,707,166.32 -> £3,336,373.17 (10.0%); £3,707,166.59 -> £3,336,373.28 (10.0%); £3,707,166.87 -> £3,336,373.40 (10.0%); £3,707,167.14 -> £3,336,373.52 (10.0%); £3,707,167.41 -> £3,336,373.64 (10.0%); £3,707,167.68 -> £3,336,373.75 (10.0%); £3,707,167.88 -> £3,336,373.86 (10.0%); £3,707,168.15 -> £3,336,373.97 (10.0%); £3,707,168.42 -> £3,336,374.08 (10.0%); £3,707,168.69 -> £3,336,374.19 (10.0%); £3,707,168.95 -> £3,336,374.29 (10.0%); £3,707,169.21 -> £3,336,374.32 (10.0%); £3,707,169.49 -> £3,336,374.35 (10.0%); £3,707,169.73 -> £3,336,374.37 (10.0%); £3,707,169.97 -> £3,336,374.39 (10.0%); £3,707,170.17 -> £3,336,374.41 (10.0%); £3,707,170.33 -> £3,336,374.43 (10.0%); £3,707,170.49 -> £3,336,374.45 (10.0%); £3,707,170.65 -> £3,336,374.47 (10.0%); £3,707,170.81 -> £3,336,374.48 (10.0%); £3,707,170.96 -> £3,336,374.50 (10.0%); £3,707,171.13 -> £3,336,374.52 (10.0%); £3,707,171.28 -> £3,336,374.53 (10.0%); £3,707,171.44 -> £3,336,374.55 (10.0%); £3,707,171.60 -> £3,336,374.57 (10.0%); £3,707,171.76 -> £3,336,374.58 (10.0%); £3,707,171.92 -> £3,336,374.60 (10.0%); £3,707,172.07 -> £3,336,374.75 (10.0%); £3,707,172.23 -> £3,336,374.91 (10.0%); £3,707,172.41 -> £3,336,375.07 (10.0%); £3,707,172.60 -> £3,336,375.23 (10.0%); £3,707,172.81 -> £3,336,375.39 (10.0%); £3,707,173.04 -> £3,336,375.55 (10.0%); £3,707,173.29 -> £3,336,375.71 (10.0%); £3,707,173.56 -> £3,336,375.87 (10.0%); £3,707,173.83 -> £3,336,375.90 (10.0%); £3,707,174.10 -> £3,336,375.92 (10.0%); £3,707,174.36 -> £3,336,375.94 (10.0%); £3,707,174.63 -> £3,336,375.97 (10.0%); £3,707,174.89 -> £3,336,375.99 (10.0%); £3,707,175.15 -> £3,336,376.02 (10.0%); £3,707,175.42 -> £3,336,376.04 (10.0%); £3,707,175.68 -> £3,336,376.06 (10.0%); £3,707,175.95 -> £3,336,376.09 (10.0%); £3,707,176.23 -> £3,336,376.11 (10.0%); £3,707,176.48 -> £3,336,376.13 (10.0%); £3,707,176.75 -> £3,336,376.16 (10.0%); £3,707,177.02 -> £3,336,376.19 (10.0%); £3,707,177.22 -> £3,336,376.35 (10.0%); £3,707,177.41 -> £3,336,376.52 (10.0%); £3,707,177.68 -> £3,336,376.69 (10.0%); £3,707,177.95 -> £3,336,376.85 (10.0%); £3,707,178.15 -> £3,336,377.02 (10.0%); £3,707,178.35 -> £3,336,377.18 (10.0%); £3,707,178.55 -> £3,336,377.34 (10.0%); £3,707,178.81 -> £3,336,377.51 (10.0%); £3,707,179.07 -> £3,336,377.67 (10.0%); £3,707,179.33 -> £3,336,377.83 (10.0%); £3,707,179.58 -> £3,336,378.00 (10.0%); £3,707,179.85 -> £3,336,378.03 (10.0%); £3,707,180.12 -> £3,336,378.05 (10.0%); £3,707,180.36 -> £3,336,378.08 (10.0%); £3,707,180.57 -> £3,336,378.10 (10.0%); £3,707,180.78 -> £3,336,378.12 (10.0%); £3,707,180.94 -> £3,336,378.14 (10.0%); £3,707,181.10 -> £3,336,378.16 (10.0%); £3,707,181.26 -> £3,336,378.17 (10.0%); £3,707,181.42 -> £3,336,378.19 (10.0%); £3,707,181.58 -> £3,336,378.21 (10.0%); £3,707,181.74 -> £3,336,378.22 (10.0%); £3,707,181.89 -> £3,336,378.24 (10.0%); £3,707,182.06 -> £3,336,378.26 (10.0%); £3,707,182.21 -> £3,336,378.27 (10.0%); £3,707,182.38 -> £3,336,378.29 (10.0%); £3,707,182.54 -> £3,336,378.31 (10.0%); £3,707,182.69 -> £3,336,378.47 (10.0%); £3,707,182.85 -> £3,336,378.64 (10.0%); £3,707,183.02 -> £3,336,378.82 (10.0%); £3,707,183.22 -> £3,336,379.00 (10.0%); £3,707,183.43 -> £3,336,379.18 (10.0%); £3,707,183.65 -> £3,336,379.35 (10.0%); £3,707,183.91 -> £3,336,379.53 (10.0%); £3,707,184.18 -> £3,336,379.69 (10.0%); £3,707,184.44 -> £3,336,379.72 (10.0%); £3,707,184.71 -> £3,336,379.74 (10.0%); £3,707,184.98 -> £3,336,379.77 (10.0%); £3,707,185.25 -> £3,336,379.79 (10.0%); £3,707,185.51 -> £3,336,379.81 (10.0%); £3,707,185.77 -> £3,336,379.84 (10.0%); £3,707,186.03 -> £3,336,379.86 (10.0%); £3,707,186.29 -> £3,336,379.89 (10.0%); £3,707,186.56 -> £3,336,379.91 (10.0%); £3,707,186.82 -> £3,336,379.93 (10.0%); £3,707,187.09 -> £3,336,379.96 (10.0%); £3,707,187.35 -> £3,336,379.98 (10.0%); £3,707,187.62 -> £3,336,380.01 (10.0%); £3,707,187.88 -> £3,336,380.18 (10.0%); £3,707,188.14 -> £3,336,380.36 (10.0%); £3,707,188.35 -> £3,336,380.54 (10.0%); £3,707,188.54 -> £3,336,380.72 (10.0%); £3,707,188.75 -> £3,336,380.91 (10.0%); £3,707,189.02 -> £3,336,381.09 (10.0%); £3,707,189.28 -> £3,336,381.26 (10.0%); £3,707,189.55 -> £3,336,381.44 (10.0%); £3,707,189.81 -> £3,336,381.62 (10.0%); £3,707,190.08 -> £3,336,381.79 (10.0%); £3,707,190.34 -> £3,336,381.96 (10.0%); £3,707,190.61 -> £3,336,381.99 (10.0%); £3,707,190.88 -> £3,336,382.02 (10.0%); £3,707,191.12 -> £3,336,382.05 (10.0%); £3,707,191.34 -> £3,336,382.07 (10.0%); £3,707,191.55 -> £3,336,382.09 (10.0%); £3,707,191.71 -> £3,336,382.11 (10.0%); £3,707,191.87 -> £3,336,382.13 (10.0%); £3,707,192.03 -> £3,336,382.14 (10.0%); £3,707,192.19 -> £3,336,382.16 (10.0%); £3,707,192.34 -> £3,336,382.18 (10.0%); £3,707,192.50 -> £3,336,382.19 (10.0%); £3,707,192.66 -> £3,336,382.21 (10.0%); £3,707,192.82 -> £3,336,382.23 (10.0%); £3,707,192.98 -> £3,336,382.24 (10.0%); £3,707,193.14 -> £3,336,382.26 (10.0%); £3,707,193.30 -> £3,336,382.28 (10.0%); £3,707,193.47 -> £3,336,382.45 (10.0%); £3,707,193.63 -> £3,336,382.61 (10.0%); £3,707,193.80 -> £3,336,382.78 (10.0%); £3,707,193.99 -> £3,336,382.95 (10.0%); £3,707,194.20 -> £3,336,383.12 (10.0%); £3,707,194.42 -> £3,336,383.28 (10.0%); £3,707,194.66 -> £3,336,383.45 (10.0%); £3,707,194.93 -> £3,336,383.62 (10.0%); £3,707,195.19 -> £3,336,383.65 (10.0%); £3,707,195.46 -> £3,336,383.67 (10.0%); £3,707,195.72 -> £3,336,383.70 (10.0%); £3,707,195.98 -> £3,336,383.72 (10.0%); £3,707,196.24 -> £3,336,383.74 (10.0%); £3,707,196.51 -> £3,336,383.77 (10.0%); £3,707,196.77 -> £3,336,383.79 (10.0%); £3,707,197.05 -> £3,336,383.82 (10.0%); £3,707,197.30 -> £3,336,383.84 (10.0%); £3,707,197.57 -> £3,336,383.86 (10.0%); £3,707,197.84 -> £3,336,383.89 (10.0%); £3,707,198.11 -> £3,336,383.91 (10.0%); £3,707,198.38 -> £3,336,383.94 (10.0%); £3,707,198.64 -> £3,336,384.11 (10.0%); £3,707,198.84 -> £3,336,384.28 (10.0%); £3,707,199.04 -> £3,336,384.46 (10.0%); £3,707,199.23 -> £3,336,384.63 (10.0%); £3,707,199.43 -> £3,336,384.81 (10.0%); £3,707,199.63 -> £3,336,384.98 (10.0%); £3,707,199.90 -> £3,336,385.16 (10.0%); £3,707,200.16 -> £3,336,385.33 (10.0%); £3,707,200.42 -> £3,336,385.51 (10.0%); £3,707,200.69 -> £3,336,385.68 (10.0%); £3,707,200.95 -> £3,336,385.85 (10.0%); £3,707,201.21 -> £3,336,385.88 (10.0%); £3,707,201.49 -> £3,336,385.90 (10.0%); £3,707,201.73 -> £3,336,385.93 (10.0%); £3,707,201.95 -> £3,336,385.95 (10.0%); £3,707,202.15 -> £3,336,385.97 (10.0%); £3,707,202.31 -> £3,336,385.99 (10.0%); £3,707,202.47 -> £3,336,386.01 (10.0%); £3,707,202.63 -> £3,336,386.02 (10.0%); £3,707,202.79 -> £3,336,386.04 (10.0%); £3,707,202.94 -> £3,336,386.06 (10.0%); £3,707,203.10 -> £3,336,386.07 (10.0%); £3,707,203.26 -> £3,336,386.09 (10.0%); £3,707,203.42 -> £3,336,386.11 (10.0%); £3,707,203.59 -> £3,336,386.12 (10.0%); £3,707,203.74 -> £3,336,386.14 (10.0%); £3,707,203.90 -> £3,336,386.16 (10.0%); £3,707,204.06 -> £3,336,386.26 (10.0%); £3,707,204.22 -> £3,336,386.37 (10.0%); £3,707,204.39 -> £3,336,386.48 (10.0%); £3,707,204.59 -> £3,336,386.60 (10.0%); £3,707,204.80 -> £3,336,386.72 (10.0%); £3,707,205.03 -> £3,336,386.83 (10.0%); £3,707,205.27 -> £3,336,386.94 (10.0%); £3,707,205.55 -> £3,336,387.05 (10.0%); £3,707,205.82 -> £3,336,387.08 (10.0%); £3,707,206.10 -> £3,336,387.10 (10.0%); £3,707,206.36 -> £3,336,387.13 (10.0%); £3,707,206.63 -> £3,336,387.15 (10.0%); £3,707,206.89 -> £3,336,387.18 (10.0%); £3,707,207.16 -> £3,336,387.20 (10.0%); £3,707,207.42 -> £3,336,387.22 (10.0%); £3,707,207.69 -> £3,336,387.25 (10.0%); £3,707,207.96 -> £3,336,387.27 (10.0%); £3,707,208.22 -> £3,336,387.30 (10.0%); £3,707,208.49 -> £3,336,387.32 (10.0%); £3,707,208.74 -> £3,336,387.34 (10.0%); £3,707,209.02 -> £3,336,387.37 (10.0%); £3,707,209.29 -> £3,336,387.50 (10.0%); £3,707,209.56 -> £3,336,387.62 (10.0%); £3,707,209.82 -> £3,336,387.75 (10.0%); £3,707,210.08 -> £3,336,387.88 (10.0%); £3,707,210.34 -> £3,336,388.01 (10.0%); £3,707,210.61 -> £3,336,388.14 (10.0%); £3,707,210.87 -> £3,336,388.27 (10.0%); £3,707,211.14 -> £3,336,388.39 (10.0%); £3,707,211.41 -> £3,336,388.51 (10.0%); £3,707,211.67 -> £3,336,388.64 (10.0%); £3,707,211.93 -> £3,336,388.76 (10.0%); £3,707,212.20 -> £3,336,388.79 (10.0%); £3,707,212.47 -> £3,336,388.82 (10.0%); £3,707,212.72 -> £3,336,388.84 (10.0%); £3,707,212.95 -> £3,336,388.86 (10.0%); £3,707,213.16 -> £3,336,388.89 (10.0%); £3,707,213.29 -> £3,336,388.91 (10.0%); £3,707,213.43 -> £3,336,388.93 (10.0%); £3,707,213.57 -> £3,336,388.94 (10.0%); £3,707,213.71 -> £3,336,388.96 (10.0%); £3,707,213.85 -> £3,336,388.98 (10.0%); £3,707,213.99 -> £3,336,388.99 (10.0%); £3,707,214.13 -> £3,336,389.01 (10.0%); £3,707,214.27 -> £3,336,389.03 (10.0%); £3,707,214.41 -> £3,336,389.05 (10.0%); £3,707,214.55 -> £3,336,389.06 (10.0%); £3,707,214.69 -> £3,336,389.08 (10.0%); £3,707,214.83 -> £3,336,389.19 (10.0%); £3,707,214.97 -> £3,336,389.30 (10.0%); £3,707,215.13 -> £3,336,389.41 (10.0%); £3,707,215.30 -> £3,336,389.52 (10.0%); £3,707,215.48 -> £3,336,389.63 (10.0%); £3,707,215.69 -> £3,336,389.74 (10.0%); £3,707,215.90 -> £3,336,389.85 (10.0%); £3,707,216.13 -> £3,336,389.97 (10.0%); £3,707,216.36 -> £3,336,389.99 (10.0%); £3,707,216.60 -> £3,336,390.02 (10.0%); £3,707,216.83 -> £3,336,390.05 (10.0%); £3,707,217.06 -> £3,336,390.07 (10.0%); £3,707,217.29 -> £3,336,390.10 (10.0%); £3,707,217.53 -> £3,336,390.13 (10.0%); £3,707,217.76 -> £3,336,390.15 (10.0%); £3,707,218.00 -> £3,336,390.18 (10.0%); £3,707,218.22 -> £3,336,390.20 (10.0%); £3,707,218.45 -> £3,336,390.23 (10.0%); £3,707,218.68 -> £3,336,390.26 (10.0%); £3,707,218.92 -> £3,336,390.28 (10.0%); £3,707,219.15 -> £3,336,390.31 (10.0%); £3,707,219.39 -> £3,336,390.43 (10.0%); £3,707,219.57 -> £3,336,390.55 (10.0%); £3,707,219.80 -> £3,336,390.67 (10.0%); £3,707,219.97 -> £3,336,390.79 (10.0%); £3,707,220.14 -> £3,336,390.91 (10.0%); £3,707,220.32 -> £3,336,391.03 (10.0%); £3,707,220.50 -> £3,336,391.16 (10.0%); £3,707,220.73 -> £3,336,391.28 (10.0%); £3,707,220.96 -> £3,336,391.41 (10.0%); £3,707,221.19 -> £3,336,391.52 (10.0%); £3,707,221.41 -> £3,336,391.64 (10.0%); £3,707,221.65 -> £3,336,391.67 (10.0%); £3,707,221.88 -> £3,336,391.70 (10.0%); £3,707,222.09 -> £3,336,391.73 (10.0%); £3,707,222.28 -> £3,336,391.75 (10.0%); £3,707,222.46 -> £3,336,391.77 (10.0%); £3,707,222.60 -> £3,336,391.79 (10.0%); £3,707,222.74 -> £3,336,391.81 (10.0%); £3,707,222.88 -> £3,336,391.83 (10.0%); £3,707,223.02 -> £3,336,391.85 (10.0%); £3,707,223.16 -> £3,336,391.87 (10.0%); £3,707,223.30 -> £3,336,391.88 (10.0%); £3,707,223.44 -> £3,336,391.90 (10.0%); £3,707,223.58 -> £3,336,391.92 (10.0%); £3,707,223.73 -> £3,336,391.94 (10.0%); £3,707,223.86 -> £3,336,391.95 (10.0%); £3,707,224.01 -> £3,336,391.97 (10.0%); £3,707,224.15 -> £3,336,392.07 (10.0%); £3,707,224.29 -> £3,336,392.17 (10.0%); £3,707,224.45 -> £3,336,392.27 (10.0%); £3,707,224.61 -> £3,336,392.38 (10.0%); £3,707,224.79 -> £3,336,392.48 (10.0%); £3,707,224.99 -> £3,336,392.59 (10.0%); £3,707,225.22 -> £3,336,392.70 (10.0%); £3,707,225.45 -> £3,336,392.81 (10.0%); £3,707,225.68 -> £3,336,392.85 (10.0%); £3,707,225.92 -> £3,336,392.88 (10.0%); £3,707,226.15 -> £3,336,392.91 (10.0%); £3,707,226.39 -> £3,336,392.94 (10.0%); £3,707,226.62 -> £3,336,392.97 (10.0%); £3,707,226.86 -> £3,336,393.01 (10.0%); £3,707,227.10 -> £3,336,393.04 (10.0%); £3,707,227.34 -> £3,336,393.07 (10.0%); £3,707,227.57 -> £3,336,393.09 (10.0%); £3,707,227.81 -> £3,336,393.12 (10.0%); £3,707,228.05 -> £3,336,393.15 (10.0%); £3,707,228.28 -> £3,336,393.18 (10.0%); £3,707,228.52 -> £3,336,393.21 (10.0%); £3,707,228.75 -> £3,336,393.33 (10.0%); £3,707,228.99 -> £3,336,393.44 (10.0%); £3,707,229.15 -> £3,336,393.56 (10.0%); £3,707,229.33 -> £3,336,393.68 (10.0%); £3,707,229.51 -> £3,336,393.80 (10.0%); £3,707,229.68 -> £3,336,393.91 (10.0%); £3,707,229.86 -> £3,336,394.03 (10.0%); £3,707,230.10 -> £3,336,394.14 (10.0%); £3,707,230.33 -> £3,336,394.26 (10.0%); £3,707,230.57 -> £3,336,394.37 (10.0%); £3,707,230.80 -> £3,336,394.49 (10.0%); £3,707,231.03 -> £3,336,394.52 (10.0%); £3,707,231.27 -> £3,336,394.55 (10.0%); £3,707,231.49 -> £3,336,394.57 (10.0%); £3,707,231.69 -> £3,336,394.60 (10.0%); £3,707,231.87 -> £3,336,394.62 (10.0%); £3,707,232.03 -> £3,336,394.64 (10.0%); £3,707,232.19 -> £3,336,394.65 (10.0%); £3,707,232.36 -> £3,336,394.67 (10.0%); £3,707,232.52 -> £3,336,394.69 (10.0%); £3,707,232.68 -> £3,336,394.71 (10.0%); £3,707,232.84 -> £3,336,394.72 (10.0%); £3,707,233.01 -> £3,336,394.74 (10.0%); £3,707,233.17 -> £3,336,394.76 (10.0%); £3,707,233.34 -> £3,336,394.77 (10.0%); £3,707,233.50 -> £3,336,394.79 (10.0%); £3,707,233.66 -> £3,336,394.81 (10.0%); £3,707,233.83 -> £3,336,394.92 (10.0%); £3,707,233.99 -> £3,336,395.02 (10.0%); £3,707,234.17 -> £3,336,395.13 (10.0%); £3,707,234.38 -> £3,336,395.25 (10.0%); £3,707,234.60 -> £3,336,395.36 (10.0%); £3,707,234.84 -> £3,336,395.47 (10.0%); £3,707,235.09 -> £3,336,395.59 (10.0%); £3,707,235.35 -> £3,336,395.70 (10.0%); £3,707,235.63 -> £3,336,395.73 (10.0%); £3,707,235.91 -> £3,336,395.75 (10.0%); £3,707,236.18 -> £3,336,395.77 (10.0%); £3,707,236.45 -> £3,336,395.80 (10.0%); £3,707,236.72 -> £3,336,395.82 (10.0%); £3,707,236.99 -> £3,336,395.85 (10.0%); £3,707,237.26 -> £3,336,395.87 (10.0%); £3,707,237.52 -> £3,336,395.89 (10.0%); £3,707,237.79 -> £3,336,395.92 (10.0%); £3,707,238.06 -> £3,336,395.94 (10.0%); £3,707,238.33 -> £3,336,395.96 (10.0%); £3,707,238.61 -> £3,336,395.99 (10.0%); £3,707,238.87 -> £3,336,396.01 (10.0%); £3,707,239.08 -> £3,336,396.13 (10.0%); £3,707,239.28 -> £3,336,396.26 (10.0%); £3,707,239.48 -> £3,336,396.38 (10.0%); £3,707,239.69 -> £3,336,396.50 (10.0%); £3,707,239.90 -> £3,336,396.63 (10.0%); £3,707,240.17 -> £3,336,396.76 (10.0%); £3,707,240.45 -> £3,336,396.89 (10.0%); £3,707,240.73 -> £3,336,397.01 (10.0%); £3,707,241.00 -> £3,336,397.14 (10.0%); £3,707,241.27 -> £3,336,397.25 (10.0%); £3,707,241.54 -> £3,336,397.37 (10.0%); £3,707,241.81 -> £3,336,397.40 (10.0%); £3,707,242.08 -> £3,336,397.43 (10.0%); £3,707,242.33 -> £3,336,397.46 (10.0%); £3,707,242.56 -> £3,336,397.48 (10.0%); £3,707,242.78 -> £3,336,397.50 (10.0%); £3,707,242.95 -> £3,336,397.52 (10.0%); £3,707,243.11 -> £3,336,397.54 (10.0%); £3,707,243.28 -> £3,336,397.55 (10.0%); £3,707,243.45 -> £3,336,397.57 (10.0%); £3,707,243.62 -> £3,336,397.59 (10.0%); £3,707,243.78 -> £3,336,397.60 (10.0%); £3,707,243.95 -> £3,336,397.62 (10.0%); £3,707,244.11 -> £3,336,397.64 (10.0%); £3,707,244.27 -> £3,336,397.65 (10.0%); £3,707,244.44 -> £3,336,397.67 (10.0%); £3,707,244.61 -> £3,336,397.69 (10.0%); £3,707,244.77 -> £3,336,397.82 (10.0%); £3,707,244.94 -> £3,336,397.94 (10.0%); £3,707,245.13 -> £3,336,398.07 (10.0%); £3,707,245.33 -> £3,336,398.21 (10.0%); £3,707,245.55 -> £3,336,398.34 (10.0%); £3,707,245.78 -> £3,336,398.47 (10.0%); £3,707,246.04 -> £3,336,398.60 (10.0%); £3,707,246.31 -> £3,336,398.73 (10.0%); £3,707,246.58 -> £3,336,398.75 (10.0%); £3,707,246.86 -> £3,336,398.78 (10.0%); £3,707,247.15 -> £3,336,398.80 (10.0%); £3,707,247.42 -> £3,336,398.83 (10.0%); £3,707,247.69 -> £3,336,398.85 (10.0%); £3,707,247.97 -> £3,336,398.88 (10.0%); £3,707,248.23 -> £3,336,398.90 (10.0%); £3,707,248.51 -> £3,336,398.92 (10.0%); £3,707,248.78 -> £3,336,398.94 (10.0%); £3,707,249.06 -> £3,336,398.97 (10.0%); £3,707,249.32 -> £3,336,398.99 (10.0%); £3,707,249.59 -> £3,336,399.02 (10.0%); £3,707,249.87 -> £3,336,399.04 (10.0%); £3,707,250.07 -> £3,336,399.18 (10.0%); £3,707,250.28 -> £3,336,399.31 (10.0%); £3,707,250.49 -> £3,336,399.45 (10.0%); £3,707,250.70 -> £3,336,399.58 (10.0%); £3,707,250.89 -> £3,336,399.72 (10.0%); £3,707,251.10 -> £3,336,399.85 (10.0%); £3,707,251.31 -> £3,336,399.99 (10.0%); £3,707,251.58 -> £3,336,400.12 (10.0%); £3,707,251.86 -> £3,336,400.25 (10.0%); £3,707,252.12 -> £3,336,400.38 (10.0%); £3,707,252.40 -> £3,336,400.51 (10.0%); £3,707,252.68 -> £3,336,400.54 (10.0%); £3,707,252.95 -> £3,336,400.56 (10.0%); £3,707,253.20 -> £3,336,400.59 (10.0%); £3,707,253.43 -> £3,336,400.61 (10.0%); £3,707,253.63 -> £3,336,400.63 (10.0%); £3,707,253.81 -> £3,336,400.65 (10.0%); £3,707,253.97 -> £3,336,400.67 (10.0%); £3,707,254.13 -> £3,336,400.68 (10.0%); £3,707,254.29 -> £3,336,400.70 (10.0%); £3,707,254.46 -> £3,336,400.72 (10.0%); £3,707,254.63 -> £3,336,400.73 (10.0%); £3,707,254.79 -> £3,336,400.75 (10.0%); £3,707,254.96 -> £3,336,400.77 (10.0%); £3,707,255.12 -> £3,336,400.78 (10.0%); £3,707,255.29 -> £3,336,400.80 (10.0%); £3,707,255.45 -> £3,336,400.82 (10.0%); £3,707,255.62 -> £3,336,401.00 (10.0%); £3,707,255.79 -> £3,336,401.20 (10.0%); £3,707,255.97 -> £3,336,401.40 (10.0%); £3,707,256.17 -> £3,336,401.60 (10.0%); £3,707,256.40 -> £3,336,401.80 (10.0%); £3,707,256.64 -> £3,336,402.00 (10.0%); £3,707,256.89 -> £3,336,402.19 (10.0%); £3,707,257.18 -> £3,336,402.39 (10.0%); £3,707,257.46 -> £3,336,402.41 (10.0%); £3,707,257.74 -> £3,336,402.43 (10.0%); £3,707,258.02 -> £3,336,402.46 (10.0%); £3,707,258.30 -> £3,336,402.48 (10.0%); £3,707,258.57 -> £3,336,402.50 (10.0%); £3,707,258.85 -> £3,336,402.53 (10.0%); £3,707,259.12 -> £3,336,402.55 (10.0%); £3,707,259.39 -> £3,336,402.58 (10.0%); £3,707,259.66 -> £3,336,402.60 (10.0%); £3,707,259.95 -> £3,336,402.62 (10.0%); £3,707,260.22 -> £3,336,402.65 (10.0%); £3,707,260.49 -> £3,336,402.67 (10.0%); £3,707,260.77 -> £3,336,402.70 (10.0%); £3,707,260.98 -> £3,336,402.89 (10.0%); £3,707,261.19 -> £3,336,403.10 (10.0%); £3,707,261.46 -> £3,336,403.29 (10.0%); £3,707,261.67 -> £3,336,403.49 (10.0%); £3,707,261.86 -> £3,336,403.69 (10.0%); £3,707,262.07 -> £3,336,403.89 (10.0%); £3,707,262.34 -> £3,336,404.10 (10.0%); £3,707,262.62 -> £3,336,404.30 (10.0%); £3,707,262.88 -> £3,336,404.50 (10.0%); £3,707,263.16 -> £3,336,404.70 (10.0%); £3,707,263.43 -> £3,336,404.89 (10.0%); £3,707,263.71 -> £3,336,404.92 (10.0%); £3,707,263.99 -> £3,336,404.95 (10.0%); £3,707,264.25 -> £3,336,404.97 (10.0%); £3,707,264.49 -> £3,336,404.99 (10.0%); £3,707,264.70 -> £3,336,405.01 (10.0%); £3,707,264.87 -> £3,336,405.03 (10.0%); £3,707,265.03 -> £3,336,405.05 (10.0%); £3,707,265.20 -> £3,336,405.07 (10.0%); £3,707,265.36 -> £3,336,405.08 (10.0%); £3,707,265.53 -> £3,336,405.10 (10.0%); £3,707,265.70 -> £3,336,405.12 (10.0%); £3,707,265.86 -> £3,336,405.13 (10.0%); £3,707,266.03 -> £3,336,405.15 (10.0%); £3,707,266.19 -> £3,336,405.17 (10.0%); £3,707,266.35 -> £3,336,405.18 (10.0%); £3,707,266.51 -> £3,336,405.20 (10.0%); £3,707,266.68 -> £3,336,405.40 (10.0%); £3,707,266.84 -> £3,336,405.60 (10.0%); £3,707,267.03 -> £3,336,405.81 (10.0%); £3,707,267.23 -> £3,336,406.02 (10.0%); £3,707,267.45 -> £3,336,406.24 (10.0%); £3,707,267.69 -> £3,336,406.46 (10.0%); £3,707,267.95 -> £3,336,406.67 (10.0%); £3,707,268.23 -> £3,336,406.87 (10.0%); £3,707,268.50 -> £3,336,406.90 (10.0%); £3,707,268.78 -> £3,336,406.92 (10.0%); £3,707,269.06 -> £3,336,406.94 (10.0%); £3,707,269.33 -> £3,336,406.97 (10.0%); £3,707,269.61 -> £3,336,406.99 (10.0%); £3,707,269.87 -> £3,336,407.02 (10.0%); £3,707,270.15 -> £3,336,407.04 (10.0%); £3,707,270.43 -> £3,336,407.06 (10.0%); £3,707,270.70 -> £3,336,407.08 (10.0%); £3,707,270.98 -> £3,336,407.11 (10.0%); £3,707,271.25 -> £3,336,407.13 (10.0%); £3,707,271.52 -> £3,336,407.16 (10.0%); £3,707,271.79 -> £3,336,407.18 (10.0%); £3,707,271.99 -> £3,336,407.40 (10.0%); £3,707,272.28 -> £3,336,407.61 (10.0%); £3,707,272.48 -> £3,336,407.83 (10.0%); £3,707,272.75 -> £3,336,408.05 (10.0%); £3,707,273.02 -> £3,336,408.27 (10.0%); £3,707,273.29 -> £3,336,408.48 (10.0%); £3,707,273.57 -> £3,336,408.70 (10.0%); £3,707,273.84 -> £3,336,408.91 (10.0%); £3,707,274.12 -> £3,336,409.12 (10.0%); £3,707,274.40 -> £3,336,409.33 (10.0%); £3,707,274.67 -> £3,336,409.54 (10.0%); £3,707,274.96 -> £3,336,409.57 (10.0%); £3,707,275.23 -> £3,336,409.59 (10.0%); £3,707,275.48 -> £3,336,409.62 (10.0%); £3,707,275.72 -> £3,336,409.64 (10.0%); £3,707,275.93 -> £3,336,409.66 (10.0%); £3,707,276.10 -> £3,336,409.68 (10.0%); £3,707,276.26 -> £3,336,409.70 (10.0%); £3,707,276.43 -> £3,336,409.71 (10.0%); £3,707,276.59 -> £3,336,409.73 (10.0%); £3,707,276.75 -> £3,336,409.75 (10.0%); £3,707,276.92 -> £3,336,409.76 (10.0%); £3,707,277.08 -> £3,336,409.78 (10.0%); £3,707,277.24 -> £3,336,409.80 (10.0%); £3,707,277.41 -> £3,336,409.81 (10.0%); £3,707,277.57 -> £3,336,409.83 (10.0%); £3,707,277.74 -> £3,336,409.85 (10.0%); £3,707,277.91 -> £3,336,410.00 (10.0%); £3,707,278.07 -> £3,336,410.16 (10.0%); £3,707,278.25 -> £3,336,410.32 (10.0%); £3,707,278.45 -> £3,336,410.48 (10.0%); £3,707,278.67 -> £3,336,410.65 (10.0%); £3,707,278.89 -> £3,336,410.81 (10.0%); £3,707,279.15 -> £3,336,410.97 (10.0%); £3,707,279.42 -> £3,336,411.14 (10.0%); £3,707,279.69 -> £3,336,411.16 (10.0%); £3,707,279.97 -> £3,336,411.19 (10.0%); £3,707,280.24 -> £3,336,411.21 (10.0%); £3,707,280.51 -> £3,336,411.24 (10.0%); £3,707,280.77 -> £3,336,411.26 (10.0%); £3,707,281.03 -> £3,336,411.29 (10.0%); £3,707,281.30 -> £3,336,411.31 (10.0%); £3,707,281.56 -> £3,336,411.34 (10.0%); £3,707,281.85 -> £3,336,411.36 (10.0%); £3,707,282.13 -> £3,336,411.38 (10.0%); £3,707,282.39 -> £3,336,411.41 (10.0%); £3,707,282.67 -> £3,336,411.43 (10.0%); £3,707,282.93 -> £3,336,411.46 (10.0%); £3,707,283.20 -> £3,336,411.63 (10.0%); £3,707,283.47 -> £3,336,411.80 (10.0%); £3,707,283.75 -> £3,336,411.98 (10.0%); £3,707,284.03 -> £3,336,412.15 (10.0%); £3,707,284.30 -> £3,336,412.32 (10.0%); £3,707,284.50 -> £3,336,412.49 (10.0%); £3,707,284.71 -> £3,336,412.66 (10.0%); £3,707,284.98 -> £3,336,412.82 (10.0%); £3,707,285.25 -> £3,336,412.99 (10.0%); £3,707,285.52 -> £3,336,413.16 (10.0%); £3,707,285.79 -> £3,336,413.32 (10.0%); £3,707,286.06 -> £3,336,413.35 (10.0%); £3,707,286.33 -> £3,336,413.38 (10.0%); £3,707,286.58 -> £3,336,413.40 (10.0%); £3,707,286.81 -> £3,336,413.42 (10.0%); £3,707,287.02 -> £3,336,413.45 (10.0%); £3,707,287.17 -> £3,336,413.47 (10.0%); £3,707,287.31 -> £3,336,413.48 (10.0%); £3,707,287.46 -> £3,336,413.50 (10.0%); £3,707,287.60 -> £3,336,413.52 (10.0%); £3,707,287.74 -> £3,336,413.54 (10.0%); £3,707,287.88 -> £3,336,413.55 (10.0%); £3,707,288.02 -> £3,336,413.57 (10.0%); £3,707,288.16 -> £3,336,413.58 (10.0%); £3,707,288.30 -> £3,336,413.60 (10.0%); £3,707,288.45 -> £3,336,413.62 (10.0%); £3,707,288.59 -> £3,336,413.63 (10.0%); £3,707,288.73 -> £3,336,413.78 (10.0%); £3,707,288.88 -> £3,336,413.93 (10.0%); £3,707,289.04 -> £3,336,414.08 (10.0%); £3,707,289.22 -> £3,336,414.23 (10.0%); £3,707,289.41 -> £3,336,414.39 (10.0%); £3,707,289.62 -> £3,336,414.56 (10.0%); £3,707,289.84 -> £3,336,414.72 (10.0%); £3,707,290.07 -> £3,336,414.88 (10.0%); £3,707,290.31 -> £3,336,414.91 (10.0%); £3,707,290.55 -> £3,336,414.93 (10.0%); £3,707,290.79 -> £3,336,414.96 (10.0%); £3,707,291.04 -> £3,336,414.99 (10.0%); £3,707,291.27 -> £3,336,415.01 (10.0%); £3,707,291.50 -> £3,336,415.04 (10.0%); £3,707,291.74 -> £3,336,415.07 (10.0%); £3,707,291.98 -> £3,336,415.09 (10.0%); £3,707,292.22 -> £3,336,415.12 (10.0%); £3,707,292.46 -> £3,336,415.14 (10.0%); £3,707,292.70 -> £3,336,415.17 (10.0%); £3,707,292.94 -> £3,336,415.19 (10.0%); £3,707,293.18 -> £3,336,415.22 (10.0%); £3,707,293.42 -> £3,336,415.39 (10.0%); £3,707,293.66 -> £3,336,415.55 (10.0%); £3,707,293.89 -> £3,336,415.72 (10.0%); £3,707,294.07 -> £3,336,415.89 (10.0%); £3,707,294.30 -> £3,336,416.05 (10.0%); £3,707,294.48 -> £3,336,416.21 (10.0%); £3,707,294.66 -> £3,336,416.38 (10.0%); £3,707,294.91 -> £3,336,416.55 (10.0%); £3,707,295.15 -> £3,336,416.71 (10.0%); £3,707,295.39 -> £3,336,416.88 (10.0%); £3,707,295.63 -> £3,336,417.04 (10.0%); £3,707,295.87 -> £3,336,417.07 (10.0%); £3,707,296.11 -> £3,336,417.09 (10.0%); £3,707,296.33 -> £3,336,417.12 (10.0%); £3,707,296.54 -> £3,336,417.14 (10.0%); £3,707,296.73 -> £3,336,417.16 (10.0%); £3,707,296.87 -> £3,336,417.18 (10.0%); £3,707,297.01 -> £3,336,417.20 (10.0%); £3,707,297.15 -> £3,336,417.22 (10.0%); £3,707,297.28 -> £3,336,417.24 (10.0%); £3,707,297.42 -> £3,336,417.25 (10.0%); £3,707,297.57 -> £3,336,417.27 (10.0%); £3,707,297.71 -> £3,336,417.29 (10.0%); £3,707,297.85 -> £3,336,417.30 (10.0%); £3,707,298.00 -> £3,336,417.32 (10.0%); £3,707,298.13 -> £3,336,417.34 (10.0%); £3,707,298.27 -> £3,336,417.36 (10.0%); £3,707,298.41 -> £3,336,417.51 (10.0%); £3,707,298.54 -> £3,336,417.67 (10.0%); £3,707,298.70 -> £3,336,417.83 (10.0%); £3,707,298.86 -> £3,336,417.99 (10.0%); £3,707,299.05 -> £3,336,418.15 (10.0%); £3,707,299.26 -> £3,336,418.32 (10.0%); £3,707,299.48 -> £3,336,418.49 (10.0%); £3,707,299.72 -> £3,336,418.66 (10.0%); £3,707,299.95 -> £3,336,418.69 (10.0%); £3,707,300.19 -> £3,336,418.72 (10.0%); £3,707,300.42 -> £3,336,418.75 (10.0%); £3,707,300.66 -> £3,336,418.78 (10.0%); £3,707,300.89 -> £3,336,418.81 (10.0%); £3,707,301.13 -> £3,336,418.85 (10.0%); £3,707,301.36 -> £3,336,418.88 (10.0%); £3,707,301.60 -> £3,336,418.90 (10.0%); £3,707,301.83 -> £3,336,418.93 (10.0%); £3,707,302.07 -> £3,336,418.96 (10.0%); £3,707,302.30 -> £3,336,418.99 (10.0%); £3,707,302.53 -> £3,336,419.02 (10.0%); £3,707,302.76 -> £3,336,419.05 (10.0%); £3,707,303.00 -> £3,336,419.22 (10.0%); £3,707,303.23 -> £3,336,419.39 (10.0%); £3,707,303.41 -> £3,336,419.56 (10.0%); £3,707,303.58 -> £3,336,419.74 (10.0%); £3,707,303.76 -> £3,336,419.91 (10.0%); £3,707,303.94 -> £3,336,420.08 (10.0%); £3,707,304.12 -> £3,336,420.25 (10.0%); £3,707,304.35 -> £3,336,420.42 (10.0%); £3,707,304.58 -> £3,336,420.60 (10.0%); £3,707,304.82 -> £3,336,420.77 (10.0%); £3,707,305.05 -> £3,336,420.93 (10.0%); £3,707,305.28 -> £3,336,420.96 (10.0%); £3,707,305.52 -> £3,336,420.98 (10.0%); £3,707,305.74 -> £3,336,421.01 (10.0%); £3,707,305.94 -> £3,336,421.03 (10.0%); £3,707,306.12 -> £3,336,421.05 (10.0%); £3,707,306.28 -> £3,336,421.07 (10.0%); £3,707,306.43 -> £3,336,421.09 (10.0%); £3,707,306.59 -> £3,336,421.11 (10.0%); £3,707,306.74 -> £3,336,421.12 (10.0%); £3,707,306.90 -> £3,336,421.14 (10.0%); £3,707,307.06 -> £3,336,421.16 (10.0%); £3,707,307.21 -> £3,336,421.17 (10.0%); £3,707,307.37 -> £3,336,421.19 (10.0%); £3,707,307.52 -> £3,336,421.20 (10.0%); £3,707,307.67 -> £3,336,421.22 (10.0%); £3,707,307.83 -> £3,336,421.24 (10.0%); £3,707,307.98 -> £3,336,421.41 (10.0%); £3,707,308.14 -> £3,336,421.59 (10.0%); £3,707,308.31 -> £3,336,421.77 (10.0%); £3,707,308.50 -> £3,336,421.95 (10.0%); £3,707,308.72 -> £3,336,422.13 (10.0%); £3,707,308.94 -> £3,336,422.31 (10.0%); £3,707,309.18 -> £3,336,422.49 (10.0%); £3,707,309.44 -> £3,336,422.67 (10.0%); £3,707,309.70 -> £3,336,422.70 (10.0%); £3,707,309.95 -> £3,336,422.72 (10.0%); £3,707,310.21 -> £3,336,422.75 (10.0%); £3,707,310.47 -> £3,336,422.77 (10.0%); £3,707,310.73 -> £3,336,422.79 (10.0%); £3,707,310.99 -> £3,336,422.82 (10.0%); £3,707,311.25 -> £3,336,422.84 (10.0%); £3,707,311.51 -> £3,336,422.87 (10.0%); £3,707,311.77 -> £3,336,422.89 (10.0%); £3,707,312.03 -> £3,336,422.91 (10.0%); £3,707,312.28 -> £3,336,422.94 (10.0%); £3,707,312.55 -> £3,336,422.96 (10.0%); £3,707,312.81 -> £3,336,422.99 (10.0%); £3,707,313.01 -> £3,336,423.17 (10.0%); £3,707,313.20 -> £3,336,423.35 (10.0%); £3,707,313.39 -> £3,336,423.54 (10.0%); £3,707,313.58 -> £3,336,423.72 (10.0%); £3,707,313.78 -> £3,336,423.91 (10.0%); £3,707,313.97 -> £3,336,424.09 (10.0%); £3,707,314.17 -> £3,336,424.27 (10.0%); £3,707,314.43 -> £3,336,424.45 (10.0%); £3,707,314.68 -> £3,336,424.63 (10.0%); £3,707,314.94 -> £3,336,424.81 (10.0%); £3,707,315.20 -> £3,336,424.99 (10.0%); £3,707,315.46 -> £3,336,425.02 (10.0%); £3,707,315.72 -> £3,336,425.05 (10.0%); £3,707,315.96 -> £3,336,425.07 (10.0%); £3,707,316.18 -> £3,336,425.10 (10.0%); £3,707,316.39 -> £3,336,425.12 (10.0%); £3,707,316.54 -> £3,336,425.13 (10.0%); £3,707,316.70 -> £3,336,425.15 (10.0%); £3,707,316.86 -> £3,336,425.17 (10.0%); £3,707,317.02 -> £3,336,425.19 (10.0%); £3,707,317.18 -> £3,336,425.20 (10.0%); £3,707,317.33 -> £3,336,425.22 (10.0%); £3,707,317.48 -> £3,336,425.24 (10.0%); £3,707,317.64 -> £3,336,425.25 (10.0%); £3,707,317.79 -> £3,336,425.27 (10.0%); £3,707,317.95 -> £3,336,425.28 (10.0%); £3,707,318.10 -> £3,336,425.30 (10.0%); £3,707,318.26 -> £3,336,425.45 (10.0%); £3,707,318.42 -> £3,336,425.60 (10.0%); £3,707,318.59 -> £3,336,425.75 (10.0%); £3,707,318.78 -> £3,336,425.90 (10.0%); £3,707,319.00 -> £3,336,426.06 (10.0%); £3,707,319.23 -> £3,336,426.21 (10.0%); £3,707,319.47 -> £3,336,426.37 (10.0%); £3,707,319.72 -> £3,336,426.52 (10.0%); £3,707,319.98 -> £3,336,426.54 (10.0%); £3,707,320.23 -> £3,336,426.56 (10.0%); £3,707,320.49 -> £3,336,426.59 (10.0%); £3,707,320.75 -> £3,336,426.61 (10.0%); £3,707,321.01 -> £3,336,426.64 (10.0%); £3,707,321.28 -> £3,336,426.66 (10.0%); £3,707,321.53 -> £3,336,426.68 (10.0%); £3,707,321.80 -> £3,336,426.71 (10.0%); £3,707,322.06 -> £3,336,426.73 (10.0%); £3,707,322.32 -> £3,336,426.75 (10.0%); £3,707,322.58 -> £3,336,426.78 (10.0%); £3,707,322.83 -> £3,336,426.80 (10.0%); £3,707,323.09 -> £3,336,426.83 (10.0%); £3,707,323.34 -> £3,336,426.99 (10.0%); £3,707,323.61 -> £3,336,427.16 (10.0%); £3,707,323.86 -> £3,336,427.33 (10.0%); £3,707,324.13 -> £3,336,427.49 (10.0%); £3,707,324.38 -> £3,336,427.66 (10.0%); £3,707,324.64 -> £3,336,427.82 (10.0%); £3,707,324.89 -> £3,336,427.99 (10.0%); £3,707,325.15 -> £3,336,428.15 (10.0%); £3,707,325.41 -> £3,336,428.31 (10.0%); £3,707,325.67 -> £3,336,428.47 (10.0%); £3,707,325.93 -> £3,336,428.62 (10.0%); £3,707,326.20 -> £3,336,428.65 (10.0%); £3,707,326.46 -> £3,336,428.68 (10.0%); £3,707,326.70 -> £3,336,428.70 (10.0%); £3,707,326.92 -> £3,336,428.72 (10.0%); £3,707,327.12 -> £3,336,428.74 (10.0%); £3,707,327.28 -> £3,336,428.76 (10.0%); £3,707,327.43 -> £3,336,428.78 (10.0%); £3,707,327.59 -> £3,336,428.80 (10.0%); £3,707,327.74 -> £3,336,428.81 (10.0%); £3,707,327.89 -> £3,336,428.83 (10.0%); £3,707,328.04 -> £3,336,428.85 (10.0%); £3,707,328.20 -> £3,336,428.86 (10.0%); £3,707,328.35 -> £3,336,428.88 (10.0%); £3,707,328.51 -> £3,336,428.90 (10.0%); £3,707,328.67 -> £3,336,428.91 (10.0%); £3,707,328.82 -> £3,336,428.93 (10.0%); £3,707,328.98 -> £3,336,429.02 (10.0%); £3,707,329.14 -> £3,336,429.11 (10.0%); £3,707,329.32 -> £3,336,429.20 (10.0%); £3,707,329.51 -> £3,336,429.30 (10.0%); £3,707,329.72 -> £3,336,429.40 (10.0%); £3,707,329.94 -> £3,336,429.50 (10.0%); £3,707,330.18 -> £3,336,429.59 (10.0%); £3,707,330.44 -> £3,336,429.69 (10.0%); £3,707,330.70 -> £3,336,429.71 (10.0%); £3,707,330.96 -> £3,336,429.73 (10.0%); £3,707,331.22 -> £3,336,429.76 (10.0%); £3,707,331.48 -> £3,336,429.78 (10.0%); £3,707,331.74 -> £3,336,429.81 (10.0%); £3,707,331.98 -> £3,336,429.83 (10.0%); £3,707,332.23 -> £3,336,429.85 (10.0%); £3,707,332.50 -> £3,336,429.88 (10.0%); £3,707,332.76 -> £3,336,429.90 (10.0%); £3,707,333.02 -> £3,336,429.92 (10.0%); £3,707,333.28 -> £3,336,429.95 (10.0%); £3,707,333.54 -> £3,336,429.97 (10.0%); £3,707,333.81 -> £3,336,430.00 (10.0%); £3,707,334.06 -> £3,336,430.11 (10.0%); £3,707,334.26 -> £3,336,430.21 (10.0%); £3,707,334.45 -> £3,336,430.32 (10.0%); £3,707,334.64 -> £3,336,430.43 (10.0%); £3,707,334.90 -> £3,336,430.54 (10.0%); £3,707,335.16 -> £3,336,430.66 (10.0%); £3,707,335.41 -> £3,336,430.76 (10.0%); £3,707,335.67 -> £3,336,430.87 (10.0%); £3,707,335.94 -> £3,336,430.98 (10.0%); £3,707,336.20 -> £3,336,431.09 (10.0%); £3,707,336.46 -> £3,336,431.19 (10.0%); £3,707,336.71 -> £3,336,431.22 (10.0%); £3,707,336.97 -> £3,336,431.25 (10.0%); £3,707,337.21 -> £3,336,431.27 (10.0%); £3,707,337.43 -> £3,336,431.29 (10.0%); £3,707,337.63 -> £3,336,431.31 (10.0%); £3,707,337.79 -> £3,336,431.33 (10.0%); £3,707,337.94 -> £3,336,431.35 (10.0%); £3,707,338.10 -> £3,336,431.37 (10.0%); £3,707,338.25 -> £3,336,431.38 (10.0%); £3,707,338.41 -> £3,336,431.40 (10.0%); £3,707,338.56 -> £3,336,431.42 (10.0%); £3,707,338.72 -> £3,336,431.43 (10.0%); £3,707,338.89 -> £3,336,431.45 (10.0%); £3,707,339.05 -> £3,336,431.47 (10.0%); £3,707,339.21 -> £3,336,431.48 (10.0%); £3,707,339.36 -> £3,336,431.50 (10.0%); £3,707,339.52 -> £3,336,431.56 (10.0%); £3,707,339.67 -> £3,336,431.63 (10.0%); £3,707,339.84 -> £3,336,431.70 (10.0%); £3,707,340.04 -> £3,336,431.77 (10.0%); £3,707,340.25 -> £3,336,431.85 (10.0%); £3,707,340.47 -> £3,336,431.92 (10.0%); £3,707,340.72 -> £3,336,431.99 (10.0%); £3,707,340.98 -> £3,336,432.06 (10.0%); £3,707,341.25 -> £3,336,432.09 (10.0%); £3,707,341.51 -> £3,336,432.11 (10.0%); £3,707,341.78 -> £3,336,432.13 (10.0%); £3,707,342.04 -> £3,336,432.16 (10.0%); £3,707,342.30 -> £3,336,432.18 (10.0%); £3,707,342.56 -> £3,336,432.21 (10.0%); £3,707,342.83 -> £3,336,432.23 (10.0%); £3,707,343.09 -> £3,336,432.25 (10.0%); £3,707,343.35 -> £3,336,432.28 (10.0%); £3,707,343.60 -> £3,336,432.30 (10.0%); £3,707,343.85 -> £3,336,432.32 (10.0%); £3,707,344.12 -> £3,336,432.35 (10.0%); £3,707,344.38 -> £3,336,432.38 (10.0%); £3,707,344.63 -> £3,336,432.46 (10.0%); £3,707,344.90 -> £3,336,432.55 (10.0%); £3,707,345.16 -> £3,336,432.64 (10.0%); £3,707,345.41 -> £3,336,432.73 (10.0%); £3,707,345.68 -> £3,336,432.82 (10.0%); £3,707,345.94 -> £3,336,432.91 (10.0%); £3,707,346.21 -> £3,336,432.99 (10.0%); £3,707,346.46 -> £3,336,433.08 (10.0%); £3,707,346.72 -> £3,336,433.16 (10.0%); £3,707,346.97 -> £3,336,433.25 (10.0%); £3,707,347.23 -> £3,336,433.32 (10.0%); £3,707,347.48 -> £3,336,433.35 (10.0%); £3,707,347.74 -> £3,336,433.38 (10.0%); £3,707,347.98 -> £3,336,433.40 (10.0%); £3,707,348.20 -> £3,336,433.43 (10.0%); £3,707,348.41 -> £3,336,433.45 (10.0%); £3,707,348.57 -> £3,336,433.46 (10.0%); £3,707,348.72 -> £3,336,433.48 (10.0%); £3,707,348.87 -> £3,336,433.50 (10.0%); £3,707,349.04 -> £3,336,433.52 (10.0%); £3,707,349.19 -> £3,336,433.53 (10.0%); £3,707,349.35 -> £3,336,433.55 (10.0%); £3,707,349.51 -> £3,336,433.57 (10.0%); £3,707,349.67 -> £3,336,433.58 (10.0%); £3,707,349.83 -> £3,336,433.60 (10.0%); £3,707,349.99 -> £3,336,433.62 (10.0%); £3,707,350.14 -> £3,336,433.63 (10.0%); £3,707,350.30 -> £3,336,433.74 (10.0%); £3,707,350.46 -> £3,336,433.84 (10.0%); £3,707,350.64 -> £3,336,433.95 (10.0%); £3,707,350.83 -> £3,336,434.06 (10.0%); £3,707,351.05 -> £3,336,434.17 (10.0%); £3,707,351.27 -> £3,336,434.28 (10.0%); £3,707,351.52 -> £3,336,434.39 (10.0%); £3,707,351.79 -> £3,336,434.50 (10.0%); £3,707,352.05 -> £3,336,434.52 (10.0%); £3,707,352.32 -> £3,336,434.54 (10.0%); £3,707,352.57 -> £3,336,434.57 (10.0%); £3,707,352.82 -> £3,336,434.59 (10.0%); £3,707,353.09 -> £3,336,434.62 (10.0%); £3,707,353.35 -> £3,336,434.64 (10.0%); £3,707,353.60 -> £3,336,434.66 (10.0%); £3,707,353.86 -> £3,336,434.69 (10.0%); £3,707,354.12 -> £3,336,434.71 (10.0%); £3,707,354.38 -> £3,336,434.73 (10.0%); £3,707,354.64 -> £3,336,434.76 (10.0%); £3,707,354.91 -> £3,336,434.78 (10.0%); £3,707,355.17 -> £3,336,434.81 (10.0%); £3,707,355.36 -> £3,336,434.93 (10.0%); £3,707,355.64 -> £3,336,435.05 (10.0%); £3,707,355.83 -> £3,336,435.17 (10.0%); £3,707,356.02 -> £3,336,435.29 (10.0%); £3,707,356.22 -> £3,336,435.41 (10.0%); £3,707,356.41 -> £3,336,435.53 (10.0%); £3,707,356.60 -> £3,336,435.64 (10.0%); £3,707,356.86 -> £3,336,435.76 (10.0%); £3,707,357.12 -> £3,336,435.88 (10.0%); £3,707,357.38 -> £3,336,435.99 (10.0%); £3,707,357.65 -> £3,336,436.11 (10.0%); £3,707,357.92 -> £3,336,436.14 (10.0%); £3,707,358.19 -> £3,336,436.17 (10.0%); £3,707,358.43 -> £3,336,436.19 (10.0%); £3,707,358.65 -> £3,336,436.21 (10.0%); £3,707,358.85 -> £3,336,436.24 (10.0%); £3,707,358.99 -> £3,336,436.26 (10.0%); £3,707,359.13 -> £3,336,436.27 (10.0%); £3,707,359.26 -> £3,336,436.29 (10.0%); £3,707,359.40 -> £3,336,436.31 (10.0%); £3,707,359.54 -> £3,336,436.33 (10.0%); £3,707,359.68 -> £3,336,436.34 (10.0%); £3,707,359.82 -> £3,336,436.36 (10.0%); £3,707,359.96 -> £3,336,436.38 (10.0%); £3,707,360.09 -> £3,336,436.39 (10.0%); £3,707,360.23 -> £3,336,436.41 (10.0%); £3,707,360.37 -> £3,336,436.43 (10.0%); £3,707,360.51 -> £3,336,436.52 (10.0%); £3,707,360.64 -> £3,336,436.60 (10.0%); £3,707,360.80 -> £3,336,436.70 (10.0%); £3,707,360.97 -> £3,336,436.79 (10.0%); £3,707,361.15 -> £3,336,436.88 (10.0%); £3,707,361.35 -> £3,336,436.98 (10.0%); £3,707,361.56 -> £3,336,437.08 (10.0%); £3,707,361.78 -> £3,336,437.18 (10.0%); £3,707,362.01 -> £3,336,437.20 (10.0%); £3,707,362.23 -> £3,336,437.23 (10.0%); £3,707,362.45 -> £3,336,437.26 (10.0%); £3,707,362.68 -> £3,336,437.28 (10.0%); £3,707,362.92 -> £3,336,437.31 (10.0%); £3,707,363.15 -> £3,336,437.34 (10.0%); £3,707,363.38 -> £3,336,437.37 (10.0%); £3,707,363.60 -> £3,336,437.39 (10.0%); £3,707,363.82 -> £3,336,437.42 (10.0%); £3,707,364.05 -> £3,336,437.44 (10.0%); £3,707,364.28 -> £3,336,437.47 (10.0%); £3,707,364.51 -> £3,336,437.49 (10.0%); £3,707,364.73 -> £3,336,437.52 (10.0%); £3,707,364.91 -> £3,336,437.62 (10.0%); £3,707,365.08 -> £3,336,437.73 (10.0%); £3,707,365.25 -> £3,336,437.84 (10.0%); £3,707,365.42 -> £3,336,437.95 (10.0%); £3,707,365.59 -> £3,336,438.06 (10.0%); £3,707,365.77 -> £3,336,438.17 (10.0%); £3,707,365.94 -> £3,336,438.28 (10.0%); £3,707,366.16 -> £3,336,438.38 (10.0%); £3,707,366.39 -> £3,336,438.49 (10.0%); £3,707,366.63 -> £3,336,438.60 (10.0%); £3,707,366.85 -> £3,336,438.70 (10.0%); £3,707,367.07 -> £3,336,438.72 (10.0%); £3,707,367.31 -> £3,336,438.75 (10.0%); £3,707,367.52 -> £3,336,438.78 (10.0%); £3,707,367.71 -> £3,336,438.80 (10.0%); £3,707,367.88 -> £3,336,438.82 (10.0%); £3,707,368.02 -> £3,336,438.84 (10.0%); £3,707,368.16 -> £3,336,438.86 (10.0%); £3,707,368.30 -> £3,336,438.88 (10.0%); £3,707,368.44 -> £3,336,438.90 (10.0%); £3,707,368.58 -> £3,336,438.91 (10.0%); £3,707,368.71 -> £3,336,438.93 (10.0%); £3,707,368.85 -> £3,336,438.95 (10.0%); £3,707,368.99 -> £3,336,438.96 (10.0%); £3,707,369.13 -> £3,336,438.98 (10.0%); £3,707,369.27 -> £3,336,439.00 (10.0%); £3,707,369.40 -> £3,336,439.01 (10.0%); £3,707,369.54 -> £3,336,439.11 (10.0%); £3,707,369.68 -> £3,336,439.19 (10.0%); £3,707,369.84 -> £3,336,439.28 (10.0%); £3,707,370.00 -> £3,336,439.37 (10.0%); £3,707,370.19 -> £3,336,439.47 (10.0%); £3,707,370.38 -> £3,336,439.57 (10.0%); £3,707,370.60 -> £3,336,439.67 (10.0%); £3,707,370.83 -> £3,336,439.77 (10.0%); £3,707,371.06 -> £3,336,439.80 (10.0%); £3,707,371.29 -> £3,336,439.83 (10.0%); £3,707,371.52 -> £3,336,439.86 (10.0%); £3,707,371.75 -> £3,336,439.89 (10.0%); £3,707,371.98 -> £3,336,439.92 (10.0%); £3,707,372.20 -> £3,336,439.96 (10.0%); £3,707,372.44 -> £3,336,439.99 (10.0%); £3,707,372.66 -> £3,336,440.02 (10.0%); £3,707,372.89 -> £3,336,440.05 (10.0%); £3,707,373.12 -> £3,336,440.08 (10.0%); £3,707,373.36 -> £3,336,440.10 (10.0%); £3,707,373.59 -> £3,336,440.13 (10.0%); £3,707,373.82 -> £3,336,440.16 (10.0%); £3,707,374.05 -> £3,336,440.28 (10.0%); £3,707,374.29 -> £3,336,440.39 (10.0%); £3,707,374.52 -> £3,336,440.50 (10.0%); £3,707,374.68 -> £3,336,440.62 (10.0%); £3,707,374.91 -> £3,336,440.73 (10.0%); £3,707,375.09 -> £3,336,440.84 (10.0%); £3,707,375.25 -> £3,336,440.95 (10.0%); £3,707,375.48 -> £3,336,441.06 (10.0%); £3,707,375.72 -> £3,336,441.18 (10.0%); £3,707,375.95 -> £3,336,441.29 (10.0%); £3,707,376.17 -> £3,336,441.39 (10.0%); £3,707,376.40 -> £3,336,441.42 (10.0%); £3,707,376.62 -> £3,336,441.45 (10.0%); £3,707,376.83 -> £3,336,441.48 (10.0%); £3,707,377.02 -> £3,336,441.50 (10.0%); £3,707,377.20 -> £3,336,441.52 (10.0%); £3,707,377.36 -> £3,336,441.54 (10.0%); £3,707,377.52 -> £3,336,441.56 (10.0%); £3,707,377.68 -> £3,336,441.57 (10.0%); £3,707,377.84 -> £3,336,441.59 (10.0%); £3,707,378.01 -> £3,336,441.61 (10.0%); £3,707,378.16 -> £3,336,441.62 (10.0%); £3,707,378.32 -> £3,336,441.64 (10.0%); £3,707,378.48 -> £3,336,441.66 (10.0%); £3,707,378.64 -> £3,336,441.67 (10.0%); £3,707,378.79 -> £3,336,441.69 (10.0%); £3,707,378.96 -> £3,336,441.71 (10.0%); £3,707,379.12 -> £3,336,441.83 (10.0%); £3,707,379.28 -> £3,336,441.95 (10.0%); £3,707,379.45 -> £3,336,442.08 (10.0%); £3,707,379.65 -> £3,336,442.21 (10.0%); £3,707,379.85 -> £3,336,442.34 (10.0%); £3,707,380.08 -> £3,336,442.47 (10.0%); £3,707,380.33 -> £3,336,442.60 (10.0%); £3,707,380.59 -> £3,336,442.72 (10.0%); £3,707,380.85 -> £3,336,442.75 (10.0%); £3,707,381.11 -> £3,336,442.77 (10.0%); £3,707,381.37 -> £3,336,442.79 (10.0%); £3,707,381.64 -> £3,336,442.82 (10.0%); £3,707,381.91 -> £3,336,442.84 (10.0%); £3,707,382.17 -> £3,336,442.87 (10.0%); £3,707,382.44 -> £3,336,442.89 (10.0%); £3,707,382.70 -> £3,336,442.91 (10.0%); £3,707,382.98 -> £3,336,442.94 (10.0%); £3,707,383.24 -> £3,336,442.96 (10.0%); £3,707,383.50 -> £3,336,442.99 (10.0%); £3,707,383.76 -> £3,336,443.01 (10.0%); £3,707,384.02 -> £3,336,443.04 (10.0%); £3,707,384.28 -> £3,336,443.17 (10.0%); £3,707,384.48 -> £3,336,443.31 (10.0%); £3,707,384.67 -> £3,336,443.45 (10.0%); £3,707,384.87 -> £3,336,443.59 (10.0%); £3,707,385.13 -> £3,336,443.74 (10.0%); £3,707,385.39 -> £3,336,443.88 (10.0%); £3,707,385.65 -> £3,336,444.02 (10.0%); £3,707,385.92 -> £3,336,444.16 (10.0%); £3,707,386.18 -> £3,336,444.29 (10.0%); £3,707,386.45 -> £3,336,444.43 (10.0%); £3,707,386.71 -> £3,336,444.57 (10.0%); £3,707,386.98 -> £3,336,444.60 (10.0%); £3,707,387.25 -> £3,336,444.62 (10.0%); £3,707,387.50 -> £3,336,444.65 (10.0%); £3,707,387.72 -> £3,336,444.67 (10.0%); £3,707,387.92 -> £3,336,444.69 (10.0%); £3,707,388.08 -> £3,336,444.71 (10.0%); £3,707,388.24 -> £3,336,444.73 (10.0%); £3,707,388.40 -> £3,336,444.74 (10.0%); £3,707,388.56 -> £3,336,444.76 (10.0%); £3,707,388.72 -> £3,336,444.78 (10.0%); £3,707,388.88 -> £3,336,444.79 (10.0%); £3,707,389.04 -> £3,336,444.81 (10.0%); £3,707,389.20 -> £3,336,444.83 (10.0%); £3,707,389.35 -> £3,336,444.84 (10.0%); £3,707,389.51 -> £3,336,444.86 (10.0%); £3,707,389.67 -> £3,336,444.88 (10.0%); £3,707,389.82 -> £3,336,444.99 (10.0%); £3,707,389.98 -> £3,336,445.10 (10.0%); £3,707,390.16 -> £3,336,445.22 (10.0%); £3,707,390.35 -> £3,336,445.35 (10.0%); £3,707,390.56 -> £3,336,445.47 (10.0%); £3,707,390.80 -> £3,336,445.59 (10.0%); £3,707,391.04 -> £3,336,445.71 (10.0%); £3,707,391.31 -> £3,336,445.83 (10.0%); £3,707,391.57 -> £3,336,445.86 (10.0%); £3,707,391.83 -> £3,336,445.88 (10.0%); £3,707,392.11 -> £3,336,445.91 (10.0%); £3,707,392.37 -> £3,336,445.93 (10.0%); £3,707,392.63 -> £3,336,445.96 (10.0%); £3,707,392.89 -> £3,336,445.98 (10.0%); £3,707,393.16 -> £3,336,446.00 (10.0%); £3,707,393.42 -> £3,336,446.03 (10.0%); £3,707,393.68 -> £3,336,446.05 (10.0%); £3,707,393.94 -> £3,336,446.08 (10.0%); £3,707,394.21 -> £3,336,446.10 (10.0%); £3,707,394.48 -> £3,336,446.13 (10.0%); £3,707,394.74 -> £3,336,446.15 (10.0%); £3,707,395.01 -> £3,336,446.29 (10.0%); £3,707,395.27 -> £3,336,446.42 (10.0%); £3,707,395.54 -> £3,336,446.56 (10.0%); £3,707,395.80 -> £3,336,446.70 (10.0%); £3,707,396.06 -> £3,336,446.83 (10.0%); £3,707,396.34 -> £3,336,446.96 (10.0%); £3,707,396.53 -> £3,336,447.09 (10.0%); £3,707,396.79 -> £3,336,447.23 (10.0%); £3,707,397.04 -> £3,336,447.36 (10.0%); £3,707,397.31 -> £3,336,447.49 (10.0%); £3,707,397.58 -> £3,336,447.61 (10.0%); £3,707,397.84 -> £3,336,447.64 (10.0%); £3,707,398.10 -> £3,336,447.67 (10.0%); £3,707,398.35 -> £3,336,447.70 (10.0%); £3,707,398.58 -> £3,336,447.72 (10.0%); £3,707,398.78 -> £3,336,447.74 (10.0%); £3,707,398.95 -> £3,336,447.76 (10.0%); £3,707,399.10 -> £3,336,447.77 (10.0%); £3,707,399.26 -> £3,336,447.79 (10.0%); £3,707,399.43 -> £3,336,447.81 (10.0%); £3,707,399.59 -> £3,336,447.83 (10.0%); £3,707,399.75 -> £3,336,447.84 (10.0%); £3,707,399.91 -> £3,336,447.86 (10.0%); £3,707,400.07 -> £3,336,447.88 (10.0%); £3,707,400.23 -> £3,336,447.89 (10.0%); £3,707,400.39 -> £3,336,447.91 (10.0%); £3,707,400.55 -> £3,336,447.93 (10.0%); £3,707,400.71 -> £3,336,448.04 (10.0%); £3,707,400.87 -> £3,336,448.15 (10.0%); £3,707,401.05 -> £3,336,448.26 (10.0%); £3,707,401.25 -> £3,336,448.38 (10.0%); £3,707,401.46 -> £3,336,448.49 (10.0%); £3,707,401.69 -> £3,336,448.61 (10.0%); £3,707,401.93 -> £3,336,448.72 (10.0%); £3,707,402.21 -> £3,336,448.83 (10.0%); £3,707,402.48 -> £3,336,448.86 (10.0%); £3,707,402.74 -> £3,336,448.88 (10.0%); £3,707,403.01 -> £3,336,448.91 (10.0%); £3,707,403.27 -> £3,336,448.93 (10.0%); £3,707,403.54 -> £3,336,448.95 (10.0%); £3,707,403.80 -> £3,336,448.98 (10.0%); £3,707,404.07 -> £3,336,449.00 (10.0%); £3,707,404.34 -> £3,336,449.02 (10.0%); £3,707,404.61 -> £3,336,449.05 (10.0%); £3,707,404.87 -> £3,336,449.07 (10.0%); £3,707,405.14 -> £3,336,449.10 (10.0%); £3,707,405.42 -> £3,336,449.12 (10.0%); £3,707,405.68 -> £3,336,449.15 (10.0%); £3,707,405.94 -> £3,336,449.27 (10.0%); £3,707,406.21 -> £3,336,449.40 (10.0%); £3,707,406.48 -> £3,336,449.52 (10.0%); £3,707,406.74 -> £3,336,449.65 (10.0%); £3,707,406.94 -> £3,336,449.78 (10.0%); £3,707,407.14 -> £3,336,449.90 (10.0%); £3,707,407.41 -> £3,336,450.03 (10.0%); £3,707,407.67 -> £3,336,450.16 (10.0%); £3,707,407.93 -> £3,336,450.28 (10.0%); £3,707,408.20 -> £3,336,450.40 (10.0%); £3,707,408.48 -> £3,336,450.53 (10.0%); £3,707,408.74 -> £3,336,450.56 (10.0%); £3,707,409.01 -> £3,336,450.59 (10.0%); £3,707,409.26 -> £3,336,450.61 (10.0%); £3,707,409.48 -> £3,336,450.63 (10.0%); £3,707,409.69 -> £3,336,450.65 (10.0%); £3,707,409.84 -> £3,336,450.67 (10.0%); £3,707,410.00 -> £3,336,450.69 (10.0%); £3,707,410.16 -> £3,336,450.71 (10.0%); £3,707,410.32 -> £3,336,450.73 (10.0%); £3,707,410.48 -> £3,336,450.74 (10.0%); £3,707,410.64 -> £3,336,450.76 (10.0%); £3,707,410.81 -> £3,336,450.78 (10.0%); £3,707,410.97 -> £3,336,450.79 (10.0%); £3,707,411.13 -> £3,336,450.81 (10.0%); £3,707,411.29 -> £3,336,450.83 (10.0%); £3,707,411.45 -> £3,336,450.84 (10.0%); £3,707,411.61 -> £3,336,450.99 (10.0%); £3,707,411.77 -> £3,336,451.14 (10.0%); £3,707,411.95 -> £3,336,451.29 (10.0%); £3,707,412.15 -> £3,336,451.44 (10.0%); £3,707,412.36 -> £3,336,451.59 (10.0%); £3,707,412.60 -> £3,336,451.74 (10.0%); £3,707,412.85 -> £3,336,451.89 (10.0%); £3,707,413.12 -> £3,336,452.04 (10.0%); £3,707,413.38 -> £3,336,452.06 (10.0%); £3,707,413.65 -> £3,336,452.09 (10.0%); £3,707,413.92 -> £3,336,452.11 (10.0%); £3,707,414.18 -> £3,336,452.13 (10.0%); £3,707,414.44 -> £3,336,452.16 (10.0%); £3,707,414.71 -> £3,336,452.18 (10.0%); £3,707,414.99 -> £3,336,452.20 (10.0%); £3,707,415.26 -> £3,336,452.23 (10.0%); £3,707,415.52 -> £3,336,452.25 (10.0%); £3,707,415.79 -> £3,336,452.27 (10.0%); £3,707,416.05 -> £3,336,452.30 (10.0%); £3,707,416.32 -> £3,336,452.32 (10.0%); £3,707,416.59 -> £3,336,452.35 (10.0%); £3,707,416.86 -> £3,336,452.51 (10.0%); £3,707,417.13 -> £3,336,452.68 (10.0%); £3,707,417.41 -> £3,336,452.85 (10.0%); £3,707,417.67 -> £3,336,453.01 (10.0%); £3,707,417.87 -> £3,336,453.17 (10.0%); £3,707,418.14 -> £3,336,453.34 (10.0%); £3,707,418.42 -> £3,336,453.50 (10.0%); £3,707,418.68 -> £3,336,453.66 (10.0%); £3,707,418.96 -> £3,336,453.83 (10.0%); £3,707,419.23 -> £3,336,453.98 (10.0%); £3,707,419.49 -> £3,336,454.13 (10.0%); £3,707,419.76 -> £3,336,454.16 (10.0%); £3,707,420.03 -> £3,336,454.19 (10.0%); £3,707,420.27 -> £3,336,454.21 (10.0%); £3,707,420.49 -> £3,336,454.24 (10.0%); £3,707,420.70 -> £3,336,454.26 (10.0%); £3,707,420.87 -> £3,336,454.27 (10.0%); £3,707,421.03 -> £3,336,454.29 (10.0%); £3,707,421.19 -> £3,336,454.31 (10.0%); £3,707,421.34 -> £3,336,454.33 (10.0%); £3,707,421.50 -> £3,336,454.34 (10.0%); £3,707,421.66 -> £3,336,454.36 (10.0%); £3,707,421.83 -> £3,336,454.38 (10.0%); £3,707,421.99 -> £3,336,454.39 (10.0%); £3,707,422.15 -> £3,336,454.41 (10.0%); £3,707,422.31 -> £3,336,454.43 (10.0%); £3,707,422.47 -> £3,336,454.44 (10.0%); £3,707,422.63 -> £3,336,454.63 (10.0%); £3,707,422.78 -> £3,336,454.82 (10.0%); £3,707,422.96 -> £3,336,455.02 (10.0%); £3,707,423.16 -> £3,336,455.22 (10.0%); £3,707,423.37 -> £3,336,455.41 (10.0%); £3,707,423.60 -> £3,336,455.61 (10.0%); £3,707,423.85 -> £3,336,455.81 (10.0%); £3,707,424.13 -> £3,336,456.00 (10.0%); £3,707,424.39 -> £3,336,456.02 (10.0%); £3,707,424.65 -> £3,336,456.05 (10.0%); £3,707,424.90 -> £3,336,456.07 (10.0%); £3,707,425.16 -> £3,336,456.10 (10.0%); £3,707,425.42 -> £3,336,456.12 (10.0%); £3,707,425.69 -> £3,336,456.14 (10.0%); £3,707,425.95 -> £3,336,456.17 (10.0%); £3,707,426.23 -> £3,336,456.19 (10.0%); £3,707,426.50 -> £3,336,456.21 (10.0%); £3,707,426.76 -> £3,336,456.24 (10.0%); £3,707,427.02 -> £3,336,456.26 (10.0%); £3,707,427.29 -> £3,336,456.29 (10.0%); £3,707,427.55 -> £3,336,456.32 (10.0%); £3,707,427.82 -> £3,336,456.51 (10.0%); £3,707,428.07 -> £3,336,456.71 (10.0%); £3,707,428.27 -> £3,336,456.91 (10.0%); £3,707,428.48 -> £3,336,457.11 (10.0%); £3,707,428.67 -> £3,336,457.30 (10.0%); £3,707,428.88 -> £3,336,457.50 (10.0%); £3,707,429.08 -> £3,336,457.69 (10.0%); £3,707,429.34 -> £3,336,457.88 (10.0%); £3,707,429.60 -> £3,336,458.07 (10.0%); £3,707,429.88 -> £3,336,458.27 (10.0%); £3,707,430.14 -> £3,336,458.46 (10.0%); £3,707,430.41 -> £3,336,458.49 (10.0%); £3,707,430.67 -> £3,336,458.52 (10.0%); £3,707,430.91 -> £3,336,458.54 (10.0%); £3,707,431.13 -> £3,336,458.56 (10.0%); £3,707,431.33 -> £3,336,458.58 (10.0%); £3,707,431.48 -> £3,336,458.60 (10.0%); £3,707,431.62 -> £3,336,458.62 (10.0%); £3,707,431.76 -> £3,336,458.64 (10.0%); £3,707,431.90 -> £3,336,458.66 (10.0%); £3,707,432.04 -> £3,336,458.67 (10.0%); £3,707,432.18 -> £3,336,458.69 (10.0%); £3,707,432.32 -> £3,336,458.71 (10.0%); £3,707,432.46 -> £3,336,458.72 (10.0%); £3,707,432.60 -> £3,336,458.74 (10.0%); £3,707,432.74 -> £3,336,458.76 (10.0%); £3,707,432.88 -> £3,336,458.77 (10.0%); £3,707,433.02 -> £3,336,458.97 (10.0%); £3,707,433.16 -> £3,336,459.17 (10.0%); £3,707,433.32 -> £3,336,459.38 (10.0%); £3,707,433.49 -> £3,336,459.58 (10.0%); £3,707,433.68 -> £3,336,459.79 (10.0%); £3,707,433.89 -> £3,336,459.99 (10.0%); £3,707,434.11 -> £3,336,460.20 (10.0%); £3,707,434.35 -> £3,336,460.40 (10.0%); £3,707,434.58 -> £3,336,460.43 (10.0%); £3,707,434.81 -> £3,336,460.46 (10.0%); £3,707,435.05 -> £3,336,460.48 (10.0%); £3,707,435.28 -> £3,336,460.51 (10.0%); £3,707,435.51 -> £3,336,460.54 (10.0%); £3,707,435.75 -> £3,336,460.56 (10.0%); £3,707,435.98 -> £3,336,460.59 (10.0%); £3,707,436.21 -> £3,336,460.62 (10.0%); £3,707,436.45 -> £3,336,460.64 (10.0%); £3,707,436.68 -> £3,336,460.67 (10.0%); £3,707,436.92 -> £3,336,460.69 (10.0%); £3,707,437.17 -> £3,336,460.72 (10.0%); £3,707,437.41 -> £3,336,460.75 (10.0%); £3,707,437.58 -> £3,336,460.95 (10.0%); £3,707,437.75 -> £3,336,461.15 (10.0%); £3,707,437.93 -> £3,336,461.36 (10.0%); £3,707,438.10 -> £3,336,461.56 (10.0%); £3,707,438.28 -> £3,336,461.77 (10.0%); £3,707,438.45 -> £3,336,461.98 (10.0%); £3,707,438.63 -> £3,336,462.18 (10.0%); £3,707,438.87 -> £3,336,462.38 (10.0%); £3,707,439.11 -> £3,336,462.59 (10.0%); £3,707,439.35 -> £3,336,462.79 (10.0%); £3,707,439.58 -> £3,336,462.99 (10.0%); £3,707,439.82 -> £3,336,463.01 (10.0%); £3,707,440.05 -> £3,336,463.04 (10.0%); £3,707,440.27 -> £3,336,463.07 (10.0%); £3,707,440.46 -> £3,336,463.09 (10.0%); £3,707,440.65 -> £3,336,463.11 (10.0%); £3,707,440.79 -> £3,336,463.13 (10.0%); £3,707,440.94 -> £3,336,463.15 (10.0%); £3,707,441.08 -> £3,336,463.17 (10.0%); £3,707,441.22 -> £3,336,463.19 (10.0%); £3,707,441.35 -> £3,336,463.20 (10.0%); £3,707,441.49 -> £3,336,463.22 (10.0%); £3,707,441.63 -> £3,336,463.24 (10.0%); £3,707,441.77 -> £3,336,463.25 (10.0%); £3,707,441.91 -> £3,336,463.27 (10.0%); £3,707,442.05 -> £3,336,463.29 (10.0%); £3,707,442.19 -> £3,336,463.30 (10.0%); £3,707,442.33 -> £3,336,463.48 (10.0%); £3,707,442.47 -> £3,336,463.66 (10.0%); £3,707,442.63 -> £3,336,463.85 (10.0%); £3,707,442.80 -> £3,336,464.04 (10.0%); £3,707,442.99 -> £3,336,464.23 (10.0%); £3,707,443.19 -> £3,336,464.42 (10.0%); £3,707,443.40 -> £3,336,464.61 (10.0%); £3,707,443.64 -> £3,336,464.81 (10.0%); £3,707,443.88 -> £3,336,464.84 (10.0%); £3,707,444.12 -> £3,336,464.87 (10.0%); £3,707,444.36 -> £3,336,464.90 (10.0%); £3,707,444.59 -> £3,336,464.93 (10.0%); £3,707,444.82 -> £3,336,464.97 (10.0%); £3,707,445.05 -> £3,336,465.00 (10.0%); £3,707,445.28 -> £3,336,465.03 (10.0%); £3,707,445.53 -> £3,336,465.06 (10.0%); £3,707,445.76 -> £3,336,465.09 (10.0%); £3,707,445.99 -> £3,336,465.11 (10.0%); £3,707,446.22 -> £3,336,465.14 (10.0%); £3,707,446.46 -> £3,336,465.17 (10.0%); £3,707,446.69 -> £3,336,465.20 (10.0%); £3,707,446.87 -> £3,336,465.39 (10.0%); £3,707,447.04 -> £3,336,465.58 (10.0%); £3,707,447.22 -> £3,336,465.78 (10.0%); £3,707,447.40 -> £3,336,465.97 (10.0%); £3,707,447.63 -> £3,336,466.17 (10.0%); £3,707,447.87 -> £3,336,466.37 (10.0%); £3,707,448.04 -> £3,336,466.56 (10.0%); £3,707,448.28 -> £3,336,466.76 (10.0%); £3,707,448.51 -> £3,336,466.96 (10.0%); £3,707,448.74 -> £3,336,467.15 (10.0%); £3,707,448.97 -> £3,336,467.34 (10.0%); £3,707,449.20 -> £3,336,467.37 (10.0%); £3,707,449.44 -> £3,336,467.40 (10.0%); £3,707,449.65 -> £3,336,467.43 (10.0%); £3,707,449.85 -> £3,336,467.45 (10.0%); £3,707,450.03 -> £3,336,467.47 (10.0%); £3,707,450.19 -> £3,336,467.49 (10.0%); £3,707,450.35 -> £3,336,467.51 (10.0%); £3,707,450.51 -> £3,336,467.52 (10.0%); £3,707,450.66 -> £3,336,467.54 (10.0%); £3,707,450.83 -> £3,336,467.56 (10.0%); £3,707,450.99 -> £3,336,467.57 (10.0%); £3,707,451.15 -> £3,336,467.59 (10.0%); £3,707,451.31 -> £3,336,467.61 (10.0%); £3,707,451.47 -> £3,336,467.62 (10.0%); £3,707,451.63 -> £3,336,467.64 (10.0%); £3,707,451.79 -> £3,336,467.66 (10.0%); £3,707,451.95 -> £3,336,467.82 (10.0%); £3,707,452.11 -> £3,336,467.99 (10.0%); £3,707,452.28 -> £3,336,468.16 (10.0%); £3,707,452.48 -> £3,336,468.33 (10.0%); £3,707,452.70 -> £3,336,468.51 (10.0%); £3,707,452.93 -> £3,336,468.69 (10.0%); £3,707,453.16 -> £3,336,468.86 (10.0%); £3,707,453.43 -> £3,336,469.03 (10.0%); £3,707,453.69 -> £3,336,469.05 (10.0%); £3,707,453.96 -> £3,336,469.08 (10.0%); £3,707,454.22 -> £3,336,469.10 (10.0%); £3,707,454.49 -> £3,336,469.12 (10.0%); £3,707,454.76 -> £3,336,469.15 (10.0%); £3,707,455.01 -> £3,336,469.17 (10.0%); £3,707,455.27 -> £3,336,469.20 (10.0%); £3,707,455.54 -> £3,336,469.22 (10.0%); £3,707,455.81 -> £3,336,469.24 (10.0%); £3,707,456.07 -> £3,336,469.27 (10.0%); £3,707,456.34 -> £3,336,469.29 (10.0%); £3,707,456.60 -> £3,336,469.32 (10.0%); £3,707,456.86 -> £3,336,469.34 (10.0%); £3,707,457.12 -> £3,336,469.52 (10.0%); £3,707,457.40 -> £3,336,469.71 (10.0%); £3,707,457.66 -> £3,336,469.89 (10.0%); £3,707,457.92 -> £3,336,470.07 (10.0%); £3,707,458.18 -> £3,336,470.25 (10.0%); £3,707,458.44 -> £3,336,470.43 (10.0%); £3,707,458.64 -> £3,336,470.61 (10.0%); £3,707,458.90 -> £3,336,470.79 (10.0%); £3,707,459.16 -> £3,336,470.97 (10.0%); £3,707,459.42 -> £3,336,471.15 (10.0%); £3,707,459.67 -> £3,336,471.32 (10.0%); £3,707,459.93 -> £3,336,471.35 (10.0%); £3,707,460.19 -> £3,336,471.38 (10.0%); £3,707,460.44 -> £3,336,471.40 (10.0%); £3,707,460.66 -> £3,336,471.43 (10.0%); £3,707,460.87 -> £3,336,471.45 (10.0%); £3,707,461.03 -> £3,336,471.46 (10.0%); £3,707,461.19 -> £3,336,471.48 (10.0%); £3,707,461.34 -> £3,336,471.50 (10.0%); £3,707,461.50 -> £3,336,471.52 (10.0%); £3,707,461.66 -> £3,336,471.53 (10.0%); £3,707,461.81 -> £3,336,471.55 (10.0%); £3,707,461.97 -> £3,336,471.57 (10.0%); £3,707,462.13 -> £3,336,471.58 (10.0%); £3,707,462.29 -> £3,336,471.60 (10.0%); £3,707,462.44 -> £3,336,471.62 (10.0%); £3,707,462.59 -> £3,336,471.63 (10.0%); £3,707,462.75 -> £3,336,471.82 (10.0%); £3,707,462.91 -> £3,336,472.02 (10.0%); £3,707,463.09 -> £3,336,472.22 (10.0%); £3,707,463.27 -> £3,336,472.41 (10.0%); £3,707,463.49 -> £3,336,472.62 (10.0%); £3,707,463.72 -> £3,336,472.81 (10.0%); £3,707,463.97 -> £3,336,473.01 (10.0%); £3,707,464.23 -> £3,336,473.20 (10.0%); £3,707,464.48 -> £3,336,473.22 (10.0%); £3,707,464.74 -> £3,336,473.25 (10.0%); £3,707,464.99 -> £3,336,473.27 (10.0%); £3,707,465.25 -> £3,336,473.30 (10.0%); £3,707,465.51 -> £3,336,473.32 (10.0%); £3,707,465.77 -> £3,336,473.35 (10.0%); £3,707,466.03 -> £3,336,473.37 (10.0%); £3,707,466.30 -> £3,336,473.39 (10.0%); £3,707,466.55 -> £3,336,473.42 (10.0%); £3,707,466.82 -> £3,336,473.44 (10.0%); £3,707,467.07 -> £3,336,473.46 (10.0%); £3,707,467.33 -> £3,336,473.49 (10.0%); £3,707,467.60 -> £3,336,473.52 (10.0%); £3,707,467.87 -> £3,336,473.71 (10.0%); £3,707,468.13 -> £3,336,473.91 (10.0%); £3,707,468.31 -> £3,336,474.11 (10.0%); £3,707,468.52 -> £3,336,474.31 (10.0%); £3,707,468.72 -> £3,336,474.50 (10.0%); £3,707,468.92 -> £3,336,474.71 (10.0%); £3,707,469.17 -> £3,336,474.90 (10.0%); £3,707,469.43 -> £3,336,475.10 (10.0%); £3,707,469.70 -> £3,336,475.30 (10.0%); £3,707,469.97 -> £3,336,475.50 (10.0%); £3,707,470.22 -> £3,336,475.69 (10.0%); £3,707,470.48 -> £3,336,475.72 (10.0%); £3,707,470.75 -> £3,336,475.75 (10.0%); £3,707,470.99 -> £3,336,475.77 (10.0%); £3,707,471.22 -> £3,336,475.80 (10.0%); £3,707,471.42 -> £3,336,475.82 (10.0%); £3,707,471.58 -> £3,336,475.84 (10.0%); £3,707,471.74 -> £3,336,475.85 (10.0%); £3,707,471.89 -> £3,336,475.87 (10.0%); £3,707,472.05 -> £3,336,475.89 (10.0%); £3,707,472.20 -> £3,336,475.90 (10.0%); £3,707,472.36 -> £3,336,475.92 (10.0%); £3,707,472.52 -> £3,336,475.94 (10.0%); £3,707,472.68 -> £3,336,475.95 (10.0%); £3,707,472.84 -> £3,336,475.97 (10.0%); £3,707,472.99 -> £3,336,475.99 (10.0%); £3,707,473.15 -> £3,336,476.00 (10.0%); £3,707,473.31 -> £3,336,476.15 (10.0%); £3,707,473.46 -> £3,336,476.30 (10.0%); £3,707,473.64 -> £3,336,476.45 (10.0%); £3,707,473.84 -> £3,336,476.61 (10.0%); £3,707,474.04 -> £3,336,476.77 (10.0%); £3,707,474.27 -> £3,336,476.92 (10.0%); £3,707,474.51 -> £3,336,477.08 (10.0%); £3,707,474.76 -> £3,336,477.23 (10.0%); £3,707,475.02 -> £3,336,477.25 (10.0%); £3,707,475.28 -> £3,336,477.28 (10.0%); £3,707,475.53 -> £3,336,477.30 (10.0%); £3,707,475.80 -> £3,336,477.33 (10.0%); £3,707,476.06 -> £3,336,477.35 (10.0%); £3,707,476.32 -> £3,336,477.38 (10.0%); £3,707,476.59 -> £3,336,477.40 (10.0%); £3,707,476.85 -> £3,336,477.42 (10.0%); £3,707,477.11 -> £3,336,477.45 (10.0%); £3,707,477.38 -> £3,336,477.47 (10.0%); £3,707,477.64 -> £3,336,477.49 (10.0%); £3,707,477.90 -> £3,336,477.52 (10.0%); £3,707,478.16 -> £3,336,477.55 (10.0%); £3,707,478.36 -> £3,336,477.71 (10.0%); £3,707,478.62 -> £3,336,477.87 (10.0%); £3,707,478.82 -> £3,336,478.04 (10.0%); £3,707,479.02 -> £3,336,478.20 (10.0%); £3,707,479.29 -> £3,336,478.37 (10.0%); £3,707,479.55 -> £3,336,478.53 (10.0%); £3,707,479.74 -> £3,336,478.69 (10.0%); £3,707,480.01 -> £3,336,478.85 (10.0%); £3,707,480.26 -> £3,336,479.01 (10.0%); £3,707,480.53 -> £3,336,479.17 (10.0%); £3,707,480.80 -> £3,336,479.33 (10.0%); £3,707,481.06 -> £3,336,479.36 (10.0%); £3,707,481.33 -> £3,336,479.38 (10.0%); £3,707,481.57 -> £3,336,479.41 (10.0%); £3,707,481.80 -> £3,336,479.43 (10.0%); £3,707,482.00 -> £3,336,479.45 (10.0%); £3,707,482.16 -> £3,336,479.47 (10.0%); £3,707,482.31 -> £3,336,479.49 (10.0%); £3,707,482.46 -> £3,336,479.50 (10.0%); £3,707,482.62 -> £3,336,479.52 (10.0%); £3,707,482.77 -> £3,336,479.54 (10.0%); £3,707,482.93 -> £3,336,479.55 (10.0%); £3,707,483.09 -> £3,336,479.57 (10.0%); £3,707,483.24 -> £3,336,479.59 (10.0%); £3,707,483.39 -> £3,336,479.60 (10.0%); £3,707,483.55 -> £3,336,479.62 (10.0%); £3,707,483.70 -> £3,336,479.64 (10.0%); £3,707,483.86 -> £3,336,479.77 (10.0%); £3,707,484.01 -> £3,336,479.90 (10.0%); £3,707,484.18 -> £3,336,480.04 (10.0%); £3,707,484.37 -> £3,336,480.17 (10.0%); £3,707,484.57 -> £3,336,480.31 (10.0%); £3,707,484.80 -> £3,336,480.45 (10.0%); £3,707,485.04 -> £3,336,480.58 (10.0%); £3,707,485.30 -> £3,336,480.71 (10.0%); £3,707,485.56 -> £3,336,480.73 (10.0%); £3,707,485.82 -> £3,336,480.76 (10.0%); £3,707,486.08 -> £3,336,480.78 (10.0%); £3,707,486.33 -> £3,336,480.80 (10.0%); £3,707,486.59 -> £3,336,480.83 (10.0%); £3,707,486.84 -> £3,336,480.85 (10.0%); £3,707,487.10 -> £3,336,480.88 (10.0%); £3,707,487.36 -> £3,336,480.90 (10.0%); £3,707,487.62 -> £3,336,480.92 (10.0%); £3,707,487.88 -> £3,336,480.94 (10.0%); £3,707,488.13 -> £3,336,480.97 (10.0%); £3,707,488.37 -> £3,336,480.99 (10.0%); £3,707,488.64 -> £3,336,481.02 (10.0%); £3,707,488.89 -> £3,336,481.16 (10.0%); £3,707,489.15 -> £3,336,481.31 (10.0%); £3,707,489.41 -> £3,336,481.45 (10.0%); £3,707,489.60 -> £3,336,481.60 (10.0%); £3,707,489.79 -> £3,336,481.75 (10.0%); £3,707,490.05 -> £3,336,481.89 (10.0%); £3,707,490.25 -> £3,336,482.03 (10.0%); £3,707,490.50 -> £3,336,482.17 (10.0%); £3,707,490.75 -> £3,336,482.30 (10.0%); £3,707,491.02 -> £3,336,482.44 (10.0%); £3,707,491.27 -> £3,336,482.58 (10.0%); £3,707,491.54 -> £3,336,482.61 (10.0%); £3,707,491.80 -> £3,336,482.63 (10.0%); £3,707,492.04 -> £3,336,482.66 (10.0%); £3,707,492.26 -> £3,336,482.68 (10.0%); £3,707,492.46 -> £3,336,482.70 (10.0%); £3,707,492.62 -> £3,336,482.72 (10.0%); £3,707,492.77 -> £3,336,482.74 (10.0%); £3,707,492.93 -> £3,336,482.75 (10.0%); £3,707,493.08 -> £3,336,482.77 (10.0%); £3,707,493.24 -> £3,336,482.79 (10.0%); £3,707,493.40 -> £3,336,482.80 (10.0%); £3,707,493.56 -> £3,336,482.82 (10.0%); £3,707,493.71 -> £3,336,482.84 (10.0%); £3,707,493.87 -> £3,336,482.85 (10.0%); £3,707,494.02 -> £3,336,482.87 (10.0%); £3,707,494.17 -> £3,336,482.89 (10.0%); £3,707,494.33 -> £3,336,483.07 (10.0%); £3,707,494.48 -> £3,336,483.26 (10.0%); £3,707,494.66 -> £3,336,483.45 (10.0%); £3,707,494.84 -> £3,336,483.65 (10.0%); £3,707,495.05 -> £3,336,483.85 (10.0%); £3,707,495.27 -> £3,336,484.04 (10.0%); £3,707,495.50 -> £3,336,484.24 (10.0%); £3,707,495.76 -> £3,336,484.43 (10.0%); £3,707,496.02 -> £3,336,484.46 (10.0%); £3,707,496.28 -> £3,336,484.48 (10.0%); £3,707,496.54 -> £3,336,484.50 (10.0%); £3,707,496.80 -> £3,336,484.53 (10.0%); £3,707,497.07 -> £3,336,484.55 (10.0%); £3,707,497.33 -> £3,336,484.58 (10.0%); £3,707,497.59 -> £3,336,484.60 (10.0%); £3,707,497.85 -> £3,336,484.62 (10.0%); £3,707,498.12 -> £3,336,484.65 (10.0%); £3,707,498.38 -> £3,336,484.67 (10.0%); £3,707,498.64 -> £3,336,484.69 (10.0%); £3,707,498.90 -> £3,336,484.72 (10.0%); £3,707,499.16 -> £3,336,484.75 (10.0%); £3,707,499.41 -> £3,336,484.94 (10.0%); £3,707,499.67 -> £3,336,485.14 (10.0%); £3,707,499.93 -> £3,336,485.34 (10.0%); £3,707,500.20 -> £3,336,485.54 (10.0%); £3,707,500.47 -> £3,336,485.73 (10.0%); £3,707,500.73 -> £3,336,485.94 (10.0%); £3,707,501.00 -> £3,336,486.14 (10.0%); £3,707,501.25 -> £3,336,486.34 (10.0%); £3,707,501.52 -> £3,336,486.53 (10.0%); £3,707,501.78 -> £3,336,486.74 (10.0%); £3,707,502.04 -> £3,336,486.93 (10.0%); £3,707,502.31 -> £3,336,486.96 (10.0%); £3,707,502.57 -> £3,336,486.98 (10.0%); £3,707,502.81 -> £3,336,487.01 (10.0%); £3,707,503.03 -> £3,336,487.03 (10.0%); £3,707,503.23 -> £3,336,487.05 (10.0%); £3,707,503.37 -> £3,336,487.07 (10.0%); £3,707,503.50 -> £3,336,487.09 (10.0%); £3,707,503.63 -> £3,336,487.11 (10.0%); £3,707,503.77 -> £3,336,487.12 (10.0%); £3,707,503.91 -> £3,336,487.14 (10.0%); £3,707,504.04 -> £3,336,487.16 (10.0%); £3,707,504.18 -> £3,336,487.17 (10.0%); £3,707,504.31 -> £3,336,487.19 (10.0%); £3,707,504.45 -> £3,336,487.21 (10.0%); £3,707,504.59 -> £3,336,487.22 (10.0%); £3,707,504.73 -> £3,336,487.24 (10.0%); £3,707,504.87 -> £3,336,487.44 (10.0%); £3,707,505.00 -> £3,336,487.64 (10.0%); £3,707,505.16 -> £3,336,487.84 (10.0%); £3,707,505.32 -> £3,336,488.04 (10.0%); £3,707,505.50 -> £3,336,488.24 (10.0%); £3,707,505.70 -> £3,336,488.44 (10.0%); £3,707,505.91 -> £3,336,488.64 (10.0%); £3,707,506.14 -> £3,336,488.84 (10.0%); £3,707,506.37 -> £3,336,488.86 (10.0%); £3,707,506.59 -> £3,336,488.89 (10.0%); £3,707,506.81 -> £3,336,488.92 (10.0%); £3,707,507.03 -> £3,336,488.94 (10.0%); £3,707,507.26 -> £3,336,488.97 (10.0%); £3,707,507.48 -> £3,336,489.00 (10.0%); £3,707,507.71 -> £3,336,489.02 (10.0%); £3,707,507.94 -> £3,336,489.05 (10.0%); £3,707,508.18 -> £3,336,489.07 (10.0%); £3,707,508.41 -> £3,336,489.10 (10.0%); £3,707,508.63 -> £3,336,489.13 (10.0%); £3,707,508.86 -> £3,336,489.15 (10.0%); £3,707,509.09 -> £3,336,489.18 (10.0%); £3,707,509.31 -> £3,336,489.38 (10.0%); £3,707,509.54 -> £3,336,489.59 (10.0%); £3,707,509.76 -> £3,336,489.79 (10.0%); £3,707,509.99 -> £3,336,490.00 (10.0%); £3,707,510.21 -> £3,336,490.21 (10.0%); £3,707,510.44 -> £3,336,490.42 (10.0%); £3,707,510.67 -> £3,336,490.62 (10.0%); £3,707,510.90 -> £3,336,490.83 (10.0%); £3,707,511.13 -> £3,336,491.04 (10.0%); £3,707,511.35 -> £3,336,491.24 (10.0%); £3,707,511.58 -> £3,336,491.44 (10.0%); £3,707,511.81 -> £3,336,491.47 (10.0%); £3,707,512.02 -> £3,336,491.50 (10.0%); £3,707,512.24 -> £3,336,491.52 (10.0%); £3,707,512.43 -> £3,336,491.55 (10.0%); £3,707,512.61 -> £3,336,491.57 (10.0%); £3,707,512.74 -> £3,336,491.59 (10.0%); £3,707,512.88 -> £3,336,491.61 (10.0%); £3,707,513.01 -> £3,336,491.63 (10.0%); £3,707,513.14 -> £3,336,491.65 (10.0%); £3,707,513.28 -> £3,336,491.66 (10.0%); £3,707,513.42 -> £3,336,491.68 (10.0%); £3,707,513.55 -> £3,336,491.70 (10.0%); £3,707,513.68 -> £3,336,491.71 (10.0%); £3,707,513.82 -> £3,336,491.73 (10.0%); £3,707,513.96 -> £3,336,491.75 (10.0%); £3,707,514.10 -> £3,336,491.76 (10.0%); £3,707,514.23 -> £3,336,491.95 (10.0%); £3,707,514.37 -> £3,336,492.13 (10.0%); £3,707,514.52 -> £3,336,492.32 (10.0%); £3,707,514.68 -> £3,336,492.51 (10.0%); £3,707,514.86 -> £3,336,492.70 (10.0%); £3,707,515.06 -> £3,336,492.90 (10.0%); £3,707,515.27 -> £3,336,493.10 (10.0%); £3,707,515.49 -> £3,336,493.30 (10.0%); £3,707,515.72 -> £3,336,493.33 (10.0%); £3,707,515.95 -> £3,336,493.36 (10.0%); £3,707,516.18 -> £3,336,493.39 (10.0%); £3,707,516.40 -> £3,336,493.43 (10.0%); £3,707,516.61 -> £3,336,493.46 (10.0%); £3,707,516.84 -> £3,336,493.49 (10.0%); £3,707,517.07 -> £3,336,493.52 (10.0%); £3,707,517.30 -> £3,336,493.55 (10.0%); £3,707,517.52 -> £3,336,493.58 (10.0%); £3,707,517.75 -> £3,336,493.61 (10.0%); £3,707,517.97 -> £3,336,493.64 (10.0%); £3,707,518.20 -> £3,336,493.67 (10.0%); £3,707,518.44 -> £3,336,493.70 (10.0%); £3,707,518.67 -> £3,336,493.89 (10.0%); £3,707,518.89 -> £3,336,494.09 (10.0%); £3,707,519.12 -> £3,336,494.29 (10.0%); £3,707,519.35 -> £3,336,494.49 (10.0%); £3,707,519.57 -> £3,336,494.69 (10.0%); £3,707,519.79 -> £3,336,494.90 (10.0%); £3,707,520.02 -> £3,336,495.10 (10.0%); £3,707,520.23 -> £3,336,495.30 (10.0%); £3,707,520.46 -> £3,336,495.50 (10.0%); £3,707,520.69 -> £3,336,495.70 (10.0%); £3,707,520.93 -> £3,336,495.89 (10.0%); £3,707,521.15 -> £3,336,495.92 (10.0%); £3,707,521.38 -> £3,336,495.95 (10.0%); £3,707,521.59 -> £3,336,495.97 (10.0%); £3,707,521.78 -> £3,336,496.00 (10.0%); £3,707,521.96 -> £3,336,496.02 (10.0%); £3,707,522.11 -> £3,336,496.04 (10.0%); £3,707,522.27 -> £3,336,496.05 (10.0%); £3,707,522.42 -> £3,336,496.07 (10.0%); £3,707,522.58 -> £3,336,496.09 (10.0%); £3,707,522.73 -> £3,336,496.10 (10.0%); £3,707,522.89 -> £3,336,496.12 (10.0%); £3,707,523.04 -> £3,336,496.14 (10.0%); £3,707,523.20 -> £3,336,496.15 (10.0%); £3,707,523.35 -> £3,336,496.17 (10.0%); £3,707,523.50 -> £3,336,496.19 (10.0%); £3,707,523.66 -> £3,336,496.20 (10.0%); £3,707,523.82 -> £3,336,496.37 (10.0%); £3,707,523.97 -> £3,336,496.54 (10.0%); £3,707,524.14 -> £3,336,496.71 (10.0%); £3,707,524.33 -> £3,336,496.89 (10.0%); £3,707,524.53 -> £3,336,497.07 (10.0%); £3,707,524.76 -> £3,336,497.25 (10.0%); £3,707,525.00 -> £3,336,497.43 (10.0%); £3,707,525.26 -> £3,336,497.61 (10.0%); £3,707,525.52 -> £3,336,497.63 (10.0%); £3,707,525.79 -> £3,336,497.65 (10.0%); £3,707,526.05 -> £3,336,497.68 (10.0%); £3,707,526.30 -> £3,336,497.70 (10.0%); £3,707,526.56 -> £3,336,497.73 (10.0%); £3,707,526.82 -> £3,336,497.75 (10.0%); £3,707,527.08 -> £3,336,497.77 (10.0%); £3,707,527.34 -> £3,336,497.80 (10.0%); £3,707,527.60 -> £3,336,497.82 (10.0%); £3,707,527.86 -> £3,336,497.84 (10.0%); £3,707,528.11 -> £3,336,497.87 (10.0%); £3,707,528.38 -> £3,336,497.89 (10.0%); £3,707,528.64 -> £3,336,497.92 (10.0%); £3,707,528.88 -> £3,336,498.10 (10.0%); £3,707,529.14 -> £3,336,498.29 (10.0%); £3,707,529.39 -> £3,336,498.47 (10.0%); £3,707,529.64 -> £3,336,498.65 (10.0%); £3,707,529.90 -> £3,336,498.84 (10.0%); £3,707,530.15 -> £3,336,499.02 (10.0%); £3,707,530.41 -> £3,336,499.20 (10.0%); £3,707,530.67 -> £3,336,499.39 (10.0%); £3,707,530.93 -> £3,336,499.57 (10.0%); £3,707,531.18 -> £3,336,499.75 (10.0%); £3,707,531.45 -> £3,336,499.93 (10.0%); £3,707,531.70 -> £3,336,499.96 (10.0%); £3,707,531.96 -> £3,336,499.98 (10.0%); £3,707,532.20 -> £3,336,500.01 (10.0%); £3,707,532.42 -> £3,336,500.03 (10.0%); £3,707,532.62 -> £3,336,500.05 (10.0%); £3,707,532.77 -> £3,336,500.07 (10.0%); £3,707,532.92 -> £3,336,500.09 (10.0%); £3,707,533.08 -> £3,336,500.10 (10.0%); £3,707,533.24 -> £3,336,500.12 (10.0%); £3,707,533.39 -> £3,336,500.14 (10.0%); £3,707,533.55 -> £3,336,500.15 (10.0%); £3,707,533.70 -> £3,336,500.17 (10.0%); £3,707,533.84 -> £3,336,500.19 (10.0%); £3,707,533.99 -> £3,336,500.20 (10.0%); £3,707,534.15 -> £3,336,500.22 (10.0%); £3,707,534.30 -> £3,336,500.24 (10.0%); £3,707,534.45 -> £3,336,500.38 (10.0%); £3,707,534.61 -> £3,336,500.52 (10.0%); £3,707,534.78 -> £3,336,500.67 (10.0%); £3,707,534.97 -> £3,336,500.82 (10.0%); £3,707,535.17 -> £3,336,500.97 (10.0%); £3,707,535.40 -> £3,336,501.12 (10.0%); £3,707,535.63 -> £3,336,501.26 (10.0%); £3,707,535.89 -> £3,336,501.41 (10.0%); £3,707,536.15 -> £3,336,501.43 (10.0%); £3,707,536.40 -> £3,336,501.46 (10.0%); £3,707,536.66 -> £3,336,501.48 (10.0%); £3,707,536.92 -> £3,336,501.50 (10.0%); £3,707,537.17 -> £3,336,501.53 (10.0%); £3,707,537.42 -> £3,336,501.55 (10.0%); £3,707,537.69 -> £3,336,501.58 (10.0%); £3,707,537.94 -> £3,336,501.60 (10.0%); £3,707,538.19 -> £3,336,501.62 (10.0%); £3,707,538.45 -> £3,336,501.65 (10.0%); £3,707,538.70 -> £3,336,501.67 (10.0%); £3,707,538.97 -> £3,336,501.70 (10.0%); £3,707,539.22 -> £3,336,501.73 (10.0%); £3,707,539.49 -> £3,336,501.88 (10.0%); £3,707,539.75 -> £3,336,502.04 (10.0%); £3,707,540.00 -> £3,336,502.20 (10.0%); £3,707,540.25 -> £3,336,502.35 (10.0%); £3,707,540.51 -> £3,336,502.51 (10.0%); £3,707,540.77 -> £3,336,502.66 (10.0%); £3,707,541.03 -> £3,336,502.82 (10.0%); £3,707,541.28 -> £3,336,502.97 (10.0%); £3,707,541.55 -> £3,336,503.13 (10.0%); £3,707,541.79 -> £3,336,503.28 (10.0%); £3,707,542.05 -> £3,336,503.43 (10.0%); £3,707,542.31 -> £3,336,503.46 (10.0%); £3,707,542.57 -> £3,336,503.49 (10.0%); £3,707,542.81 -> £3,336,503.51 (10.0%); £3,707,543.02 -> £3,336,503.53 (10.0%); £3,707,543.22 -> £3,336,503.55 (10.0%); £3,707,543.37 -> £3,336,503.57 (10.0%); £3,707,543.52 -> £3,336,503.59 (10.0%); £3,707,543.67 -> £3,336,503.61 (10.0%); £3,707,543.81 -> £3,336,503.62 (10.0%); £3,707,543.96 -> £3,336,503.64 (10.0%); £3,707,544.12 -> £3,336,503.66 (10.0%); £3,707,544.27 -> £3,336,503.67 (10.0%); £3,707,544.43 -> £3,336,503.69 (10.0%); £3,707,544.57 -> £3,336,503.71 (10.0%); £3,707,544.73 -> £3,336,503.72 (10.0%); £3,707,544.88 -> £3,336,503.74 (10.0%); £3,707,545.03 -> £3,336,503.90 (10.0%); £3,707,545.19 -> £3,336,504.07 (10.0%); £3,707,545.36 -> £3,336,504.24 (10.0%); £3,707,545.55 -> £3,336,504.41 (10.0%); £3,707,545.76 -> £3,336,504.59 (10.0%); £3,707,545.98 -> £3,336,504.76 (10.0%); £3,707,546.21 -> £3,336,504.94 (10.0%); £3,707,546.47 -> £3,336,505.11 (10.0%); £3,707,546.72 -> £3,336,505.14 (10.0%); £3,707,546.97 -> £3,336,505.16 (10.0%); £3,707,547.22 -> £3,336,505.18 (10.0%); £3,707,547.48 -> £3,336,505.21 (10.0%); £3,707,547.75 -> £3,336,505.23 (10.0%); £3,707,548.01 -> £3,336,505.26 (10.0%); £3,707,548.26 -> £3,336,505.28 (10.0%); £3,707,548.53 -> £3,336,505.30 (10.0%); £3,707,548.79 -> £3,336,505.33 (10.0%); £3,707,549.03 -> £3,336,505.35 (10.0%); £3,707,549.29 -> £3,336,505.37 (10.0%); £3,707,549.54 -> £3,336,505.40 (10.0%); £3,707,549.80 -> £3,336,505.43 (10.0%); £3,707,550.06 -> £3,336,505.61 (10.0%); £3,707,550.32 -> £3,336,505.79 (10.0%); £3,707,550.58 -> £3,336,505.97 (10.0%); £3,707,550.85 -> £3,336,506.15 (10.0%); £3,707,551.09 -> £3,336,506.33 (10.0%); £3,707,551.35 -> £3,336,506.50 (10.0%); £3,707,551.60 -> £3,336,506.69 (10.0%); £3,707,551.86 -> £3,336,506.86 (10.0%); £3,707,552.11 -> £3,336,507.04 (10.0%); £3,707,552.37 -> £3,336,507.22 (10.0%); £3,707,552.63 -> £3,336,507.40 (10.0%); £3,707,552.88 -> £3,336,507.43 (10.0%); £3,707,553.13 -> £3,336,507.46 (10.0%); £3,707,553.37 -> £3,336,507.48 (10.0%); £3,707,553.59 -> £3,336,507.51 (10.0%); £3,707,553.78 -> £3,336,507.53 (10.0%); £3,707,553.94 -> £3,336,507.55 (10.0%); £3,707,554.09 -> £3,336,507.56 (10.0%); £3,707,554.25 -> £3,336,507.58 (10.0%); £3,707,554.40 -> £3,336,507.60 (10.0%); £3,707,554.54 -> £3,336,507.61 (10.0%); £3,707,554.70 -> £3,336,507.63 (10.0%); £3,707,554.85 -> £3,336,507.65 (10.0%); £3,707,555.00 -> £3,336,507.66 (10.0%); £3,707,555.16 -> £3,336,507.68 (10.0%); £3,707,555.31 -> £3,336,507.70 (10.0%); £3,707,555.46 -> £3,336,507.71 (10.0%); £3,707,555.62 -> £3,336,507.87 (10.0%); £3,707,555.77 -> £3,336,508.01 (10.0%); £3,707,555.93 -> £3,336,508.17 (10.0%); £3,707,556.12 -> £3,336,508.32 (10.0%); £3,707,556.32 -> £3,336,508.49 (10.0%); £3,707,556.53 -> £3,336,508.64 (10.0%); £3,707,556.78 -> £3,336,508.80 (10.0%); £3,707,557.04 -> £3,336,508.95 (10.0%); £3,707,557.30 -> £3,336,508.97 (10.0%); £3,707,557.56 -> £3,336,509.00 (10.0%); £3,707,557.81 -> £3,336,509.02 (10.0%); £3,707,558.06 -> £3,336,509.04 (10.0%); £3,707,558.31 -> £3,336,509.07 (10.0%); £3,707,558.56 -> £3,336,509.09 (10.0%); £3,707,558.82 -> £3,336,509.12 (10.0%); £3,707,559.07 -> £3,336,509.14 (10.0%); £3,707,559.33 -> £3,336,509.16 (10.0%); £3,707,559.58 -> £3,336,509.18 (10.0%); £3,707,559.84 -> £3,336,509.21 (10.0%); £3,707,560.10 -> £3,336,509.23 (10.0%); £3,707,560.35 -> £3,336,509.26 (10.0%); £3,707,560.61 -> £3,336,509.42 (10.0%); £3,707,560.87 -> £3,336,509.59 (10.0%); £3,707,561.12 -> £3,336,509.76 (10.0%); £3,707,561.38 -> £3,336,509.93 (10.0%); £3,707,561.63 -> £3,336,510.10 (10.0%); £3,707,561.89 -> £3,336,510.27 (10.0%); £3,707,562.15 -> £3,336,510.43 (10.0%); £3,707,562.40 -> £3,336,510.60 (10.0%); £3,707,562.66 -> £3,336,510.76 (10.0%); £3,707,562.92 -> £3,336,510.93 (10.0%); £3,707,563.17 -> £3,336,511.09 (10.0%); £3,707,563.42 -> £3,336,511.12 (10.0%); £3,707,563.67 -> £3,336,511.15 (10.0%); £3,707,563.91 -> £3,336,511.17 (10.0%); £3,707,564.12 -> £3,336,511.19 (10.0%); £3,707,564.33 -> £3,336,511.21 (10.0%); £3,707,564.48 -> £3,336,511.23 (10.0%); £3,707,564.63 -> £3,336,511.25 (10.0%); £3,707,564.78 -> £3,336,511.27 (10.0%); £3,707,564.93 -> £3,336,511.28 (10.0%); £3,707,565.08 -> £3,336,511.30 (10.0%); £3,707,565.24 -> £3,336,511.32 (10.0%); £3,707,565.39 -> £3,336,511.33 (10.0%); £3,707,565.54 -> £3,336,511.35 (10.0%); £3,707,565.70 -> £3,336,511.37 (10.0%); £3,707,565.85 -> £3,336,511.38 (10.0%); £3,707,566.00 -> £3,336,511.40 (10.0%); £3,707,566.15 -> £3,336,511.56 (10.0%); £3,707,566.31 -> £3,336,511.71 (10.0%); £3,707,566.48 -> £3,336,511.87 (10.0%); £3,707,566.67 -> £3,336,512.03 (10.0%); £3,707,566.87 -> £3,336,512.19 (10.0%); £3,707,567.08 -> £3,336,512.35 (10.0%); £3,707,567.33 -> £3,336,512.51 (10.0%); £3,707,567.59 -> £3,336,512.67 (10.0%); £3,707,567.85 -> £3,336,512.69 (10.0%); £3,707,568.11 -> £3,336,512.72 (10.0%); £3,707,568.36 -> £3,336,512.74 (10.0%); £3,707,568.62 -> £3,336,512.76 (10.0%); £3,707,568.88 -> £3,336,512.79 (10.0%); £3,707,569.13 -> £3,336,512.81 (10.0%); £3,707,569.39 -> £3,336,512.83 (10.0%); £3,707,569.64 -> £3,336,512.86 (10.0%); £3,707,569.90 -> £3,336,512.88 (10.0%); £3,707,570.15 -> £3,336,512.91 (10.0%); £3,707,570.41 -> £3,336,512.93 (10.0%); £3,707,570.66 -> £3,336,512.95 (10.0%); £3,707,570.92 -> £3,336,512.98 (10.0%); £3,707,571.18 -> £3,336,513.14 (10.0%); £3,707,571.42 -> £3,336,513.31 (10.0%); £3,707,571.68 -> £3,336,513.48 (10.0%); £3,707,571.93 -> £3,336,513.65 (10.0%); £3,707,572.19 -> £3,336,513.81 (10.0%); £3,707,572.44 -> £3,336,513.98 (10.0%); £3,707,572.69 -> £3,336,514.14 (10.0%); £3,707,572.95 -> £3,336,514.31 (10.0%); £3,707,573.21 -> £3,336,514.47 (10.0%); £3,707,573.46 -> £3,336,514.63 (10.0%); £3,707,573.70 -> £3,336,514.79 (10.0%); £3,707,573.97 -> £3,336,514.82 (10.0%); £3,707,574.23 -> £3,336,514.85 (10.0%); £3,707,574.46 -> £3,336,514.87 (10.0%); £3,707,574.67 -> £3,336,514.90 (10.0%); £3,707,574.87 -> £3,336,514.92 (10.0%); £3,707,575.00 -> £3,336,514.94 (10.0%); £3,707,575.13 -> £3,336,514.95 (10.0%); £3,707,575.26 -> £3,336,514.97 (10.0%); £3,707,575.40 -> £3,336,514.99 (10.0%); £3,707,575.53 -> £3,336,515.01 (10.0%); £3,707,575.67 -> £3,336,515.02 (10.0%); £3,707,575.80 -> £3,336,515.04 (10.0%); £3,707,575.94 -> £3,336,515.06 (10.0%); £3,707,576.07 -> £3,336,515.07 (10.0%); £3,707,576.20 -> £3,336,515.09 (10.0%); £3,707,576.34 -> £3,336,515.11 (10.0%); £3,707,576.47 -> £3,336,515.25 (10.0%); £3,707,576.61 -> £3,336,515.39 (10.0%); £3,707,576.76 -> £3,336,515.53 (10.0%); £3,707,576.92 -> £3,336,515.68 (10.0%); £3,707,577.10 -> £3,336,515.84 (10.0%); £3,707,577.30 -> £3,336,515.99 (10.0%); £3,707,577.51 -> £3,336,516.14 (10.0%); £3,707,577.74 -> £3,336,516.28 (10.0%); £3,707,577.96 -> £3,336,516.31 (10.0%); £3,707,578.18 -> £3,336,516.34 (10.0%); £3,707,578.40 -> £3,336,516.36 (10.0%); £3,707,578.62 -> £3,336,516.39 (10.0%); £3,707,578.85 -> £3,336,516.42 (10.0%); £3,707,579.08 -> £3,336,516.44 (10.0%); £3,707,579.30 -> £3,336,516.47 (10.0%); £3,707,579.52 -> £3,336,516.49 (10.0%); £3,707,579.75 -> £3,336,516.52 (10.0%); £3,707,579.98 -> £3,336,516.54 (10.0%); £3,707,580.21 -> £3,336,516.57 (10.0%); £3,707,580.44 -> £3,336,516.59 (10.0%); £3,707,580.66 -> £3,336,516.62 (10.0%); £3,707,580.89 -> £3,336,516.78 (10.0%); £3,707,581.11 -> £3,336,516.94 (10.0%); £3,707,581.34 -> £3,336,517.10 (10.0%); £3,707,581.57 -> £3,336,517.26 (10.0%); £3,707,581.79 -> £3,336,517.42 (10.0%); £3,707,582.01 -> £3,336,517.58 (10.0%); £3,707,582.23 -> £3,336,517.74 (10.0%); £3,707,582.46 -> £3,336,517.90 (10.0%); £3,707,582.67 -> £3,336,518.06 (10.0%); £3,707,582.90 -> £3,336,518.22 (10.0%); £3,707,583.12 -> £3,336,518.37 (10.0%); £3,707,583.34 -> £3,336,518.40 (10.0%); £3,707,583.56 -> £3,336,518.42 (10.0%); £3,707,583.78 -> £3,336,518.45 (10.0%); £3,707,583.96 -> £3,336,518.47 (10.0%); £3,707,584.14 -> £3,336,518.49 (10.0%); £3,707,584.27 -> £3,336,518.51 (10.0%); £3,707,584.40 -> £3,336,518.53 (10.0%); £3,707,584.54 -> £3,336,518.55 (10.0%); £3,707,584.68 -> £3,336,518.57 (10.0%); £3,707,584.81 -> £3,336,518.59 (10.0%); £3,707,584.95 -> £3,336,518.60 (10.0%); £3,707,585.08 -> £3,336,518.62 (10.0%); £3,707,585.22 -> £3,336,518.64 (10.0%); £3,707,585.35 -> £3,336,518.66 (10.0%); £3,707,585.49 -> £3,336,518.67 (10.0%); £3,707,585.62 -> £3,336,518.69 (10.0%); £3,707,585.76 -> £3,336,518.82 (10.0%); £3,707,585.90 -> £3,336,518.96 (10.0%); £3,707,586.04 -> £3,336,519.09 (10.0%); £3,707,586.21 -> £3,336,519.23 (10.0%); £3,707,586.39 -> £3,336,519.37 (10.0%); £3,707,586.59 -> £3,336,519.51 (10.0%); £3,707,586.79 -> £3,336,519.66 (10.0%); £3,707,587.02 -> £3,336,519.81 (10.0%); £3,707,587.25 -> £3,336,519.84 (10.0%); £3,707,587.47 -> £3,336,519.87 (10.0%); £3,707,587.70 -> £3,336,519.90 (10.0%); £3,707,587.92 -> £3,336,519.93 (10.0%); £3,707,588.15 -> £3,336,519.96 (10.0%); £3,707,588.37 -> £3,336,519.99 (10.0%); £3,707,588.59 -> £3,336,520.02 (10.0%); £3,707,588.81 -> £3,336,520.05 (10.0%); £3,707,589.03 -> £3,336,520.08 (10.0%); £3,707,589.26 -> £3,336,520.11 (10.0%); £3,707,589.49 -> £3,336,520.13 (10.0%); £3,707,589.71 -> £3,336,520.16 (10.0%); £3,707,589.93 -> £3,336,520.19 (10.0%); £3,707,590.16 -> £3,336,520.35 (10.0%); £3,707,590.38 -> £3,336,520.51 (10.0%); £3,707,590.61 -> £3,336,520.66 (10.0%); £3,707,590.84 -> £3,336,520.81 (10.0%); £3,707,591.06 -> £3,336,520.97 (10.0%); £3,707,591.27 -> £3,336,521.12 (10.0%); £3,707,591.49 -> £3,336,521.27 (10.0%); £3,707,591.71 -> £3,336,521.42 (10.0%); £3,707,591.93 -> £3,336,521.57 (10.0%); £3,707,592.16 -> £3,336,521.71 (10.0%); £3,707,592.38 -> £3,336,521.86 (10.0%); £3,707,592.61 -> £3,336,521.89 (10.0%); £3,707,592.83 -> £3,336,521.92 (10.0%); £3,707,593.04 -> £3,336,521.95 (10.0%); £3,707,593.23 -> £3,336,521.97 (10.0%); £3,707,593.41 -> £3,336,521.99 (10.0%); £3,707,593.56 -> £3,336,522.01 (10.0%); £3,707,593.71 -> £3,336,522.02 (10.0%); £3,707,593.86 -> £3,336,522.04 (10.0%); £3,707,594.02 -> £3,336,522.06 (10.0%); £3,707,594.17 -> £3,336,522.07 (10.0%); £3,707,594.32 -> £3,336,522.09 (10.0%); £3,707,594.47 -> £3,336,522.11 (10.0%); £3,707,594.63 -> £3,336,522.12 (10.0%); £3,707,594.78 -> £3,336,522.14 (10.0%); £3,707,594.93 -> £3,336,522.16 (10.0%); £3,707,595.08 -> £3,336,522.17 (10.0%); £3,707,595.23 -> £3,336,522.32 (10.0%); £3,707,595.37 -> £3,336,522.46 (10.0%); £3,707,595.54 -> £3,336,522.61 (10.0%); £3,707,595.73 -> £3,336,522.75 (10.0%); £3,707,595.94 -> £3,336,522.90 (10.0%); £3,707,596.16 -> £3,336,523.04 (10.0%); £3,707,596.40 -> £3,336,523.19 (10.0%); £3,707,596.65 -> £3,336,523.33 (10.0%); £3,707,596.90 -> £3,336,523.35 (10.0%); £3,707,597.15 -> £3,336,523.38 (10.0%); £3,707,597.41 -> £3,336,523.40 (10.0%); £3,707,597.67 -> £3,336,523.42 (10.0%); £3,707,597.92 -> £3,336,523.45 (10.0%); £3,707,598.18 -> £3,336,523.47 (10.0%); £3,707,598.42 -> £3,336,523.50 (10.0%); £3,707,598.67 -> £3,336,523.52 (10.0%); £3,707,598.92 -> £3,336,523.54 (10.0%); £3,707,599.18 -> £3,336,523.56 (10.0%); £3,707,599.43 -> £3,336,523.59 (10.0%); £3,707,599.69 -> £3,336,523.61 (10.0%); £3,707,599.94 -> £3,336,523.64 (10.0%); £3,707,600.19 -> £3,336,523.78 (10.0%); £3,707,600.44 -> £3,336,523.93 (10.0%); £3,707,600.70 -> £3,336,524.08 (10.0%); £3,707,600.96 -> £3,336,524.23 (10.0%); £3,707,601.21 -> £3,336,524.38 (10.0%); £3,707,601.47 -> £3,336,524.54 (10.0%); £3,707,601.71 -> £3,336,524.70 (10.0%); £3,707,601.96 -> £3,336,524.86 (10.0%); £3,707,602.21 -> £3,336,525.01 (10.0%); £3,707,602.47 -> £3,336,525.16 (10.0%); £3,707,602.73 -> £3,336,525.31 (10.0%); £3,707,602.98 -> £3,336,525.34 (10.0%); £3,707,603.24 -> £3,336,525.37 (10.0%); £3,707,603.47 -> £3,336,525.39 (10.0%); £3,707,603.68 -> £3,336,525.42 (10.0%); £3,707,603.88 -> £3,336,525.44 (10.0%); £3,707,604.03 -> £3,336,525.45 (10.0%); £3,707,604.17 -> £3,336,525.47 (10.0%); £3,707,604.32 -> £3,336,525.49 (10.0%); £3,707,604.47 -> £3,336,525.51 (10.0%); £3,707,604.62 -> £3,336,525.52 (10.0%); £3,707,604.77 -> £3,336,525.54 (10.0%); £3,707,604.92 -> £3,336,525.56 (10.0%); £3,707,605.08 -> £3,336,525.57 (10.0%); £3,707,605.22 -> £3,336,525.59 (10.0%); £3,707,605.37 -> £3,336,525.61 (10.0%); £3,707,605.52 -> £3,336,525.62 (10.0%); £3,707,605.66 -> £3,336,525.73 (10.0%); £3,707,605.82 -> £3,336,525.84 (10.0%); £3,707,605.99 -> £3,336,525.95 (10.0%); £3,707,606.18 -> £3,336,526.07 (10.0%); £3,707,606.38 -> £3,336,526.19 (10.0%); £3,707,606.60 -> £3,336,526.31 (10.0%); £3,707,606.83 -> £3,336,526.42 (10.0%); £3,707,607.08 -> £3,336,526.53 (10.0%); £3,707,607.33 -> £3,336,526.55 (10.0%); £3,707,607.58 -> £3,336,526.58 (10.0%); £3,707,607.83 -> £3,336,526.60 (10.0%); £3,707,608.09 -> £3,336,526.63 (10.0%); £3,707,608.34 -> £3,336,526.65 (10.0%); £3,707,608.59 -> £3,336,526.67 (10.0%); £3,707,608.84 -> £3,336,526.70 (10.0%); £3,707,609.09 -> £3,336,526.72 (10.0%); £3,707,609.34 -> £3,336,526.74 (10.0%); £3,707,609.60 -> £3,336,526.77 (10.0%); £3,707,609.85 -> £3,336,526.79 (10.0%); £3,707,610.10 -> £3,336,526.82 (10.0%); £3,707,610.36 -> £3,336,526.84 (10.0%); £3,707,610.61 -> £3,336,526.97 (10.0%); £3,707,610.87 -> £3,336,527.09 (10.0%); £3,707,611.12 -> £3,336,527.22 (10.0%); £3,707,611.39 -> £3,336,527.34 (10.0%); £3,707,611.64 -> £3,336,527.47 (10.0%); £3,707,611.90 -> £3,336,527.60 (10.0%); £3,707,612.15 -> £3,336,527.72 (10.0%); £3,707,612.40 -> £3,336,527.85 (10.0%); £3,707,612.64 -> £3,336,527.97 (10.0%); £3,707,612.88 -> £3,336,528.09 (10.0%); £3,707,613.13 -> £3,336,528.20 (10.0%); £3,707,613.38 -> £3,336,528.23 (10.0%); £3,707,613.63 -> £3,336,528.26 (10.0%); £3,707,613.87 -> £3,336,528.28 (10.0%); £3,707,614.09 -> £3,336,528.31 (10.0%); £3,707,614.28 -> £3,336,528.33 (10.0%); £3,707,614.43 -> £3,336,528.34 (10.0%); £3,707,614.58 -> £3,336,528.36 (10.0%); £3,707,614.74 -> £3,336,528.38 (10.0%); £3,707,614.89 -> £3,336,528.40 (10.0%); £3,707,615.04 -> £3,336,528.41 (10.0%); £3,707,615.19 -> £3,336,528.43 (10.0%); £3,707,615.35 -> £3,336,528.45 (10.0%); £3,707,615.49 -> £3,336,528.46 (10.0%); £3,707,615.65 -> £3,336,528.48 (10.0%); £3,707,615.79 -> £3,336,528.50 (10.0%); £3,707,615.95 -> £3,336,528.51 (10.0%); £3,707,616.10 -> £3,336,528.59 (10.0%); £3,707,616.25 -> £3,336,528.67 (10.0%); £3,707,616.42 -> £3,336,528.75 (10.0%); £3,707,616.60 -> £3,336,528.83 (10.0%); £3,707,616.79 -> £3,336,528.92 (10.0%); £3,707,617.01 -> £3,336,529.01 (10.0%); £3,707,617.26 -> £3,336,529.10 (10.0%); £3,707,617.50 -> £3,336,529.18 (10.0%); £3,707,617.75 -> £3,336,529.20 (10.0%); £3,707,618.00 -> £3,336,529.23 (10.0%); £3,707,618.26 -> £3,336,529.25 (10.0%); £3,707,618.51 -> £3,336,529.27 (10.0%); £3,707,618.76 -> £3,336,529.30 (10.0%); £3,707,619.01 -> £3,336,529.32 (10.0%); £3,707,619.26 -> £3,336,529.35 (10.0%); £3,707,619.52 -> £3,336,529.37 (10.0%); £3,707,619.77 -> £3,336,529.39 (10.0%); £3,707,620.01 -> £3,336,529.42 (10.0%); £3,707,620.26 -> £3,336,529.44 (10.0%); £3,707,620.51 -> £3,336,529.47 (10.0%); £3,707,620.76 -> £3,336,529.49 (10.0%); £3,707,621.00 -> £3,336,529.59 (10.0%); £3,707,621.26 -> £3,336,529.69 (10.0%); £3,707,621.50 -> £3,336,529.78 (10.0%); £3,707,621.75 -> £3,336,529.88 (10.0%); £3,707,622.00 -> £3,336,529.98 (10.0%); £3,707,622.25 -> £3,336,530.08 (10.0%); £3,707,622.49 -> £3,336,530.18 (10.0%); £3,707,622.75 -> £3,336,530.27 (10.0%); £3,707,622.99 -> £3,336,530.37 (10.0%); £3,707,623.24 -> £3,336,530.46 (10.0%); £3,707,623.49 -> £3,336,530.56 (10.0%); £3,707,623.73 -> £3,336,530.59 (10.0%); £3,707,623.99 -> £3,336,530.61 (10.0%); £3,707,624.23 -> £3,336,530.64 (10.0%); £3,707,624.44 -> £3,336,530.66 (10.0%); £3,707,624.63 -> £3,336,530.68 (10.0%); £3,707,624.78 -> £3,336,530.70 (10.0%); £3,707,624.93 -> £3,336,530.71 (10.0%); £3,707,625.09 -> £3,336,530.73 (10.0%); £3,707,625.24 -> £3,336,530.75 (10.0%); £3,707,625.39 -> £3,336,530.77 (10.0%); £3,707,625.54 -> £3,336,530.78 (10.0%); £3,707,625.69 -> £3,336,530.80 (10.0%); £3,707,625.84 -> £3,336,530.82 (10.0%); £3,707,625.99 -> £3,336,530.83 (10.0%); £3,707,626.15 -> £3,336,530.85 (10.0%); £3,707,626.30 -> £3,336,530.87 (10.0%); £3,707,626.45 -> £3,336,530.94 (10.0%); £3,707,626.60 -> £3,336,531.01 (10.0%); £3,707,626.76 -> £3,336,531.10 (10.0%); £3,707,626.94 -> £3,336,531.18 (10.0%); £3,707,627.14 -> £3,336,531.27 (10.0%); £3,707,627.36 -> £3,336,531.35 (10.0%); £3,707,627.59 -> £3,336,531.43 (10.0%); £3,707,627.84 -> £3,336,531.51 (10.0%); £3,707,628.10 -> £3,336,531.54 (10.0%); £3,707,628.35 -> £3,336,531.56 (10.0%); £3,707,628.60 -> £3,336,531.58 (10.0%); £3,707,628.85 -> £3,336,531.61 (10.0%); £3,707,629.11 -> £3,336,531.63 (10.0%); £3,707,629.36 -> £3,336,531.65 (10.0%); £3,707,629.61 -> £3,336,531.68 (10.0%); £3,707,629.86 -> £3,336,531.70 (10.0%); £3,707,630.11 -> £3,336,531.72 (10.0%); £3,707,630.36 -> £3,336,531.75 (10.0%); £3,707,630.62 -> £3,336,531.77 (10.0%); £3,707,630.87 -> £3,336,531.79 (10.0%); £3,707,631.13 -> £3,336,531.82 (10.0%); £3,707,631.38 -> £3,336,531.91 (10.0%); £3,707,631.64 -> £3,336,532.01 (10.0%); £3,707,631.89 -> £3,336,532.10 (10.0%); £3,707,632.15 -> £3,336,532.20 (10.0%); £3,707,632.41 -> £3,336,532.30 (10.0%); £3,707,632.66 -> £3,336,532.40 (10.0%); £3,707,632.90 -> £3,336,532.49 (10.0%); £3,707,633.16 -> £3,336,532.58 (10.0%); £3,707,633.41 -> £3,336,532.67 (10.0%); £3,707,633.66 -> £3,336,532.77 (10.0%); £3,707,633.91 -> £3,336,532.86 (10.0%); £3,707,634.16 -> £3,336,532.89 (10.0%); £3,707,634.42 -> £3,336,532.92 (10.0%); £3,707,634.65 -> £3,336,532.94 (10.0%); £3,707,634.86 -> £3,336,532.96 (10.0%); £3,707,635.06 -> £3,336,532.98 (10.0%); £3,707,635.21 -> £3,336,533.00 (10.0%); £3,707,635.36 -> £3,336,533.02 (10.0%); £3,707,635.51 -> £3,336,533.04 (10.0%); £3,707,635.66 -> £3,336,533.05 (10.0%); £3,707,635.81 -> £3,336,533.07 (10.0%); £3,707,635.96 -> £3,336,533.09 (10.0%); £3,707,636.12 -> £3,336,533.10 (10.0%); £3,707,636.27 -> £3,336,533.12 (10.0%); £3,707,636.42 -> £3,336,533.14 (10.0%); £3,707,636.57 -> £3,336,533.15 (10.0%); £3,707,636.72 -> £3,336,533.17 (10.0%); £3,707,636.87 -> £3,336,533.28 (10.0%); £3,707,637.02 -> £3,336,533.39 (10.0%); £3,707,637.19 -> £3,336,533.50 (10.0%); £3,707,637.38 -> £3,336,533.62 (10.0%); £3,707,637.58 -> £3,336,533.74 (10.0%); £3,707,637.80 -> £3,336,533.85 (10.0%); £3,707,638.03 -> £3,336,533.96 (10.0%); £3,707,638.29 -> £3,336,534.07 (10.0%); £3,707,638.55 -> £3,336,534.09 (10.0%); £3,707,638.79 -> £3,336,534.12 (10.0%); £3,707,639.04 -> £3,336,534.14 (10.0%); £3,707,639.29 -> £3,336,534.17 (10.0%); £3,707,639.54 -> £3,336,534.19 (10.0%); £3,707,639.79 -> £3,336,534.22 (10.0%); £3,707,640.04 -> £3,336,534.24 (10.0%); £3,707,640.29 -> £3,336,534.26 (10.0%); £3,707,640.55 -> £3,336,534.29 (10.0%); £3,707,640.80 -> £3,336,534.31 (10.0%); £3,707,641.06 -> £3,336,534.34 (10.0%); £3,707,641.31 -> £3,336,534.36 (10.0%); £3,707,641.55 -> £3,336,534.39 (10.0%); £3,707,641.81 -> £3,336,534.51 (10.0%); £3,707,642.06 -> £3,336,534.63 (10.0%); £3,707,642.31 -> £3,336,534.75 (10.0%); £3,707,642.56 -> £3,336,534.87 (10.0%); £3,707,642.81 -> £3,336,535.00 (10.0%); £3,707,643.06 -> £3,336,535.12 (10.0%); £3,707,643.31 -> £3,336,535.24 (10.0%); £3,707,643.56 -> £3,336,535.35 (10.0%); £3,707,643.82 -> £3,336,535.47 (10.0%); £3,707,644.07 -> £3,336,535.58 (10.0%); £3,707,644.33 -> £3,336,535.70 (10.0%); £3,707,644.58 -> £3,336,535.73 (10.0%); £3,707,644.83 -> £3,336,535.75 (10.0%); £3,707,645.06 -> £3,336,535.78 (10.0%); £3,707,645.27 -> £3,336,535.80 (10.0%); £3,707,645.46 -> £3,336,535.82 (10.0%); £3,707,645.60 -> £3,336,535.84 (10.0%); £3,707,645.73 -> £3,336,535.86 (10.0%); £3,707,645.87 -> £3,336,535.88 (10.0%); £3,707,646.00 -> £3,336,535.89 (10.0%); £3,707,646.14 -> £3,336,535.91 (10.0%); £3,707,646.27 -> £3,336,535.93 (10.0%); £3,707,646.41 -> £3,336,535.94 (10.0%); £3,707,646.55 -> £3,336,535.96 (10.0%); £3,707,646.68 -> £3,336,535.98 (10.0%); £3,707,646.82 -> £3,336,535.99 (10.0%); £3,707,646.95 -> £3,336,536.01 (10.0%); £3,707,647.09 -> £3,336,536.15 (10.0%); £3,707,647.23 -> £3,336,536.29 (10.0%); £3,707,647.37 -> £3,336,536.44 (10.0%); £3,707,647.55 -> £3,336,536.58 (10.0%); £3,707,647.72 -> £3,336,536.73 (10.0%); £3,707,647.92 -> £3,336,536.89 (10.0%); £3,707,648.13 -> £3,336,537.04 (10.0%); £3,707,648.35 -> £3,336,537.19 (10.0%); £3,707,648.58 -> £3,336,537.22 (10.0%); £3,707,648.80 -> £3,336,537.24 (10.0%); £3,707,649.02 -> £3,336,537.27 (10.0%); £3,707,649.25 -> £3,336,537.29 (10.0%); £3,707,649.48 -> £3,336,537.32 (10.0%); £3,707,649.70 -> £3,336,537.35 (10.0%); £3,707,649.92 -> £3,336,537.37 (10.0%); £3,707,650.15 -> £3,336,537.40 (10.0%); £3,707,650.36 -> £3,336,537.42 (10.0%); £3,707,650.58 -> £3,336,537.45 (10.0%); £3,707,650.80 -> £3,336,537.48 (10.0%); £3,707,651.02 -> £3,336,537.50 (10.0%); £3,707,651.23 -> £3,336,537.53 (10.0%); £3,707,651.46 -> £3,336,537.68 (10.0%); £3,707,651.69 -> £3,336,537.83 (10.0%); £3,707,651.91 -> £3,336,537.98 (10.0%); £3,707,652.14 -> £3,336,538.14 (10.0%); £3,707,652.36 -> £3,336,538.29 (10.0%); £3,707,652.60 -> £3,336,538.45 (10.0%); £3,707,652.81 -> £3,336,538.61 (10.0%); £3,707,653.04 -> £3,336,538.76 (10.0%); £3,707,653.26 -> £3,336,538.91 (10.0%); £3,707,653.49 -> £3,336,539.06 (10.0%); £3,707,653.71 -> £3,336,539.22 (10.0%); £3,707,653.93 -> £3,336,539.25 (10.0%); £3,707,654.15 -> £3,336,539.28 (10.0%); £3,707,654.35 -> £3,336,539.30 (10.0%); £3,707,654.54 -> £3,336,539.33 (10.0%); £3,707,654.72 -> £3,336,539.35 (10.0%); £3,707,654.86 -> £3,336,539.37 (10.0%); £3,707,654.99 -> £3,336,539.39 (10.0%); £3,707,655.12 -> £3,336,539.41 (10.0%); £3,707,655.25 -> £3,336,539.43 (10.0%); £3,707,655.39 -> £3,336,539.44 (10.0%); £3,707,655.53 -> £3,336,539.46 (10.0%); £3,707,655.66 -> £3,336,539.48 (10.0%); £3,707,655.79 -> £3,336,539.49 (10.0%); £3,707,655.93 -> £3,336,539.51 (10.0%); £3,707,656.08 -> £3,336,539.53 (10.0%); £3,707,656.21 -> £3,336,539.54 (10.0%); £3,707,656.35 -> £3,336,539.62 (10.0%); £3,707,656.48 -> £3,336,539.69 (10.0%); £3,707,656.63 -> £3,336,539.77 (10.0%); £3,707,656.80 -> £3,336,539.85 (10.0%); £3,707,656.98 -> £3,336,539.93 (10.0%); £3,707,657.18 -> £3,336,540.01 (10.0%); £3,707,657.39 -> £3,336,540.09 (10.0%); £3,707,657.62 -> £3,336,540.18 (10.0%); £3,707,657.85 -> £3,336,540.21 (10.0%); £3,707,658.07 -> £3,336,540.24 (10.0%); £3,707,658.29 -> £3,336,540.27 (10.0%); £3,707,658.52 -> £3,336,540.30 (10.0%); £3,707,658.74 -> £3,336,540.33 (10.0%); £3,707,658.97 -> £3,336,540.36 (10.0%); £3,707,659.20 -> £3,336,540.39 (10.0%); £3,707,659.43 -> £3,336,540.42 (10.0%); £3,707,659.65 -> £3,336,540.45 (10.0%); £3,707,659.88 -> £3,336,540.48 (10.0%); £3,707,660.11 -> £3,336,540.51 (10.0%); £3,707,660.34 -> £3,336,540.54 (10.0%); £3,707,660.57 -> £3,336,540.57 (10.0%); £3,707,660.79 -> £3,336,540.66 (10.0%); £3,707,661.01 -> £3,336,540.76 (10.0%); £3,707,661.24 -> £3,336,540.86 (10.0%); £3,707,661.47 -> £3,336,540.96 (10.0%); £3,707,661.70 -> £3,336,541.06 (10.0%); £3,707,661.92 -> £3,336,541.16 (10.0%); £3,707,662.14 -> £3,336,541.25 (10.0%); £3,707,662.37 -> £3,336,541.35 (10.0%); £3,707,662.59 -> £3,336,541.44 (10.0%); £3,707,662.81 -> £3,336,541.54 (10.0%); £3,707,663.04 -> £3,336,541.63 (10.0%); £3,707,663.27 -> £3,336,541.66 (10.0%); £3,707,663.50 -> £3,336,541.69 (10.0%); £3,707,663.71 -> £3,336,541.71 (10.0%); £3,707,663.91 -> £3,336,541.74 (10.0%); £3,707,664.08 -> £3,336,541.76 (10.0%); £3,707,664.24 -> £3,336,541.77 (10.0%); £3,707,664.39 -> £3,336,541.79 (10.0%); £3,707,664.55 -> £3,336,541.81 (10.0%); £3,707,664.70 -> £3,336,541.83 (10.0%); £3,707,664.85 -> £3,336,541.84 (10.0%); £3,707,665.00 -> £3,336,541.86 (10.0%); £3,707,665.16 -> £3,336,541.88 (10.0%); £3,707,665.31 -> £3,336,541.89 (10.0%); £3,707,665.46 -> £3,336,541.91 (10.0%); £3,707,665.61 -> £3,336,541.93 (10.0%); £3,707,665.77 -> £3,336,541.94 (10.0%); £3,707,665.92 -> £3,336,542.04 (10.0%); £3,707,666.08 -> £3,336,542.14 (10.0%); £3,707,666.25 -> £3,336,542.24 (10.0%); £3,707,666.44 -> £3,336,542.34 (10.0%); £3,707,666.64 -> £3,336,542.45 (10.0%); £3,707,666.87 -> £3,336,542.56 (10.0%); £3,707,667.11 -> £3,336,542.67 (10.0%); £3,707,667.37 -> £3,336,542.77 (10.0%); £3,707,667.62 -> £3,336,542.80 (10.0%); £3,707,667.88 -> £3,336,542.82 (10.0%); £3,707,668.13 -> £3,336,542.84 (10.0%); £3,707,668.39 -> £3,336,542.87 (10.0%); £3,707,668.63 -> £3,336,542.89 (10.0%); £3,707,668.88 -> £3,336,542.92 (10.0%); £3,707,669.14 -> £3,336,542.94 (10.0%); £3,707,669.39 -> £3,336,542.96 (10.0%); £3,707,669.66 -> £3,336,542.99 (10.0%); £3,707,669.92 -> £3,336,543.01 (10.0%); £3,707,670.17 -> £3,336,543.03 (10.0%); £3,707,670.43 -> £3,336,543.06 (10.0%); £3,707,670.69 -> £3,336,543.09 (10.0%); £3,707,670.95 -> £3,336,543.21 (10.0%); £3,707,671.21 -> £3,336,543.33 (10.0%); £3,707,671.47 -> £3,336,543.45 (10.0%); £3,707,671.72 -> £3,336,543.57 (10.0%); £3,707,671.98 -> £3,336,543.68 (10.0%); £3,707,672.24 -> £3,336,543.81 (10.0%); £3,707,672.49 -> £3,336,543.92 (10.0%); £3,707,672.75 -> £3,336,544.04 (10.0%); £3,707,673.00 -> £3,336,544.15 (10.0%); £3,707,673.26 -> £3,336,544.27 (10.0%); £3,707,673.51 -> £3,336,544.39 (10.0%); £3,707,673.77 -> £3,336,544.41 (10.0%); £3,707,674.03 -> £3,336,544.44 (10.0%); £3,707,674.26 -> £3,336,544.47 (10.0%); £3,707,674.48 -> £3,336,544.49 (10.0%); £3,707,674.68 -> £3,336,544.51 (10.0%); £3,707,674.84 -> £3,336,544.53 (10.0%); £3,707,674.99 -> £3,336,544.55 (10.0%); £3,707,675.15 -> £3,336,544.56 (10.0%); £3,707,675.30 -> £3,336,544.58 (10.0%); £3,707,675.45 -> £3,336,544.60 (10.0%); £3,707,675.60 -> £3,336,544.61 (10.0%); £3,707,675.76 -> £3,336,544.63 (10.0%); £3,707,675.92 -> £3,336,544.65 (10.0%); £3,707,676.07 -> £3,336,544.66 (10.0%); £3,707,676.22 -> £3,336,544.68 (10.0%); £3,707,676.38 -> £3,336,544.70 (10.0%); £3,707,676.54 -> £3,336,544.78 (10.0%); £3,707,676.69 -> £3,336,544.86 (10.0%); £3,707,676.86 -> £3,336,544.95 (10.0%); £3,707,677.06 -> £3,336,545.04 (10.0%); £3,707,677.27 -> £3,336,545.13 (10.0%); £3,707,677.49 -> £3,336,545.23 (10.0%); £3,707,677.73 -> £3,336,545.32 (10.0%); £3,707,677.99 -> £3,336,545.41 (10.0%); £3,707,678.24 -> £3,336,545.43 (10.0%); £3,707,678.50 -> £3,336,545.46 (10.0%); £3,707,678.75 -> £3,336,545.48 (10.0%); £3,707,679.01 -> £3,336,545.50 (10.0%); £3,707,679.26 -> £3,336,545.53 (10.0%); £3,707,679.52 -> £3,336,545.55 (10.0%); £3,707,679.79 -> £3,336,545.58 (10.0%); £3,707,680.05 -> £3,336,545.60 (10.0%); £3,707,680.32 -> £3,336,545.62 (10.0%); £3,707,680.58 -> £3,336,545.64 (10.0%); £3,707,680.84 -> £3,336,545.67 (10.0%); £3,707,681.10 -> £3,336,545.69 (10.0%); £3,707,681.35 -> £3,336,545.72 (10.0%); £3,707,681.60 -> £3,336,545.82 (10.0%); £3,707,681.86 -> £3,336,545.92 (10.0%); £3,707,682.12 -> £3,336,546.02 (10.0%); £3,707,682.38 -> £3,336,546.11 (10.0%); £3,707,682.63 -> £3,336,546.21 (10.0%); £3,707,682.89 -> £3,336,546.32 (10.0%); £3,707,683.15 -> £3,336,546.42 (10.0%); £3,707,683.42 -> £3,336,546.52 (10.0%); £3,707,683.67 -> £3,336,546.62 (10.0%); £3,707,683.92 -> £3,336,546.71 (10.0%); £3,707,684.18 -> £3,336,546.81 (10.0%); £3,707,684.44 -> £3,336,546.84 (10.0%); £3,707,684.69 -> £3,336,546.86 (10.0%); £3,707,684.93 -> £3,336,546.89 (10.0%); £3,707,685.15 -> £3,336,546.91 (10.0%); £3,707,685.34 -> £3,336,546.93 (10.0%); £3,707,685.50 -> £3,336,546.95 (10.0%); £3,707,685.66 -> £3,336,546.97 (10.0%); £3,707,685.81 -> £3,336,546.98 (10.0%); £3,707,685.96 -> £3,336,547.00 (10.0%); £3,707,686.11 -> £3,336,547.02 (10.0%); £3,707,686.27 -> £3,336,547.03 (10.0%); £3,707,686.42 -> £3,336,547.05 (10.0%); £3,707,686.58 -> £3,336,547.07 (10.0%); £3,707,686.73 -> £3,336,547.08 (10.0%); £3,707,686.89 -> £3,336,547.10 (10.0%); £3,707,687.05 -> £3,336,547.12 (10.0%); £3,707,687.21 -> £3,336,547.21 (10.0%); £3,707,687.36 -> £3,336,547.31 (10.0%); £3,707,687.53 -> £3,336,547.42 (10.0%); £3,707,687.72 -> £3,336,547.53 (10.0%); £3,707,687.93 -> £3,336,547.64 (10.0%); £3,707,688.16 -> £3,336,547.75 (10.0%); £3,707,688.40 -> £3,336,547.86 (10.0%); £3,707,688.66 -> £3,336,547.96 (10.0%); £3,707,688.92 -> £3,336,547.98 (10.0%); £3,707,689.18 -> £3,336,548.01 (10.0%); £3,707,689.42 -> £3,336,548.03 (10.0%); £3,707,689.68 -> £3,336,548.06 (10.0%); £3,707,689.94 -> £3,336,548.08 (10.0%); £3,707,690.20 -> £3,336,548.10 (10.0%); £3,707,690.45 -> £3,336,548.13 (10.0%); £3,707,690.70 -> £3,336,548.15 (10.0%); £3,707,690.95 -> £3,336,548.17 (10.0%); £3,707,691.21 -> £3,336,548.20 (10.0%); £3,707,691.47 -> £3,336,548.22 (10.0%); £3,707,691.72 -> £3,336,548.24 (10.0%); £3,707,691.99 -> £3,336,548.27 (10.0%); £3,707,692.24 -> £3,336,548.39 (10.0%); £3,707,692.50 -> £3,336,548.52 (10.0%); £3,707,692.76 -> £3,336,548.63 (10.0%); £3,707,693.02 -> £3,336,548.74 (10.0%); £3,707,693.27 -> £3,336,548.85 (10.0%); £3,707,693.54 -> £3,336,548.97 (10.0%); £3,707,693.79 -> £3,336,549.08 (10.0%); £3,707,694.05 -> £3,336,549.20 (10.0%); £3,707,694.30 -> £3,336,549.32 (10.0%); £3,707,694.57 -> £3,336,549.43 (10.0%); £3,707,694.81 -> £3,336,549.55 (10.0%); £3,707,695.07 -> £3,336,549.58 (10.0%); £3,707,695.32 -> £3,336,549.61 (10.0%); £3,707,695.57 -> £3,336,549.63 (10.0%); £3,707,695.79 -> £3,336,549.65 (10.0%); £3,707,695.99 -> £3,336,549.67 (10.0%); £3,707,696.15 -> £3,336,549.69 (10.0%); £3,707,696.30 -> £3,336,549.71 (10.0%); £3,707,696.46 -> £3,336,549.73 (10.0%); £3,707,696.60 -> £3,336,549.74 (10.0%); £3,707,696.76 -> £3,336,549.76 (10.0%); £3,707,696.91 -> £3,336,549.78 (10.0%); £3,707,697.06 -> £3,336,549.79 (10.0%); £3,707,697.21 -> £3,336,549.81 (10.0%); £3,707,697.36 -> £3,336,549.82 (10.0%); £3,707,697.52 -> £3,336,549.84 (10.0%); £3,707,697.67 -> £3,336,549.86 (10.0%); £3,707,697.82 -> £3,336,549.97 (10.0%); £3,707,697.98 -> £3,336,550.09 (10.0%); £3,707,698.15 -> £3,336,550.21 (10.0%); £3,707,698.33 -> £3,336,550.33 (10.0%); £3,707,698.54 -> £3,336,550.46 (10.0%); £3,707,698.76 -> £3,336,550.58 (10.0%); £3,707,699.00 -> £3,336,550.70 (10.0%); £3,707,699.25 -> £3,336,550.81 (10.0%); £3,707,699.51 -> £3,336,550.84 (10.0%); £3,707,699.77 -> £3,336,550.86 (10.0%); £3,707,700.03 -> £3,336,550.89 (10.0%); £3,707,700.28 -> £3,336,550.91 (10.0%); £3,707,700.54 -> £3,336,550.94 (10.0%); £3,707,700.80 -> £3,336,550.96 (10.0%); £3,707,701.05 -> £3,336,550.98 (10.0%); £3,707,701.30 -> £3,336,551.01 (10.0%); £3,707,701.56 -> £3,336,551.03 (10.0%); £3,707,701.81 -> £3,336,551.05 (10.0%); £3,707,702.07 -> £3,336,551.08 (10.0%); £3,707,702.32 -> £3,336,551.10 (10.0%); £3,707,702.58 -> £3,336,551.13 (10.0%); £3,707,702.84 -> £3,336,551.26 (10.0%); £3,707,703.08 -> £3,336,551.39 (10.0%); £3,707,703.34 -> £3,336,551.53 (10.0%); £3,707,703.60 -> £3,336,551.66 (10.0%); £3,707,703.86 -> £3,336,551.80 (10.0%); £3,707,704.12 -> £3,336,551.93 (10.0%); £3,707,704.37 -> £3,336,552.07 (10.0%); £3,707,704.63 -> £3,336,552.20 (10.0%); £3,707,704.88 -> £3,336,552.33 (10.0%); £3,707,705.13 -> £3,336,552.46 (10.0%); £3,707,705.39 -> £3,336,552.59 (10.0%); £3,707,705.64 -> £3,336,552.62 (10.0%); £3,707,705.89 -> £3,336,552.65 (10.0%); £3,707,706.13 -> £3,336,552.67 (10.0%); £3,707,706.35 -> £3,336,552.69 (10.0%); £3,707,706.55 -> £3,336,552.71 (10.0%); £3,707,706.71 -> £3,336,552.73 (10.0%); £3,707,706.86 -> £3,336,552.75 (10.0%); £3,707,707.01 -> £3,336,552.77 (10.0%); £3,707,707.17 -> £3,336,552.79 (10.0%); £3,707,707.32 -> £3,336,552.80 (10.0%); £3,707,707.47 -> £3,336,552.82 (10.0%); £3,707,707.62 -> £3,336,552.84 (10.0%); £3,707,707.78 -> £3,336,552.85 (10.0%); £3,707,707.92 -> £3,336,552.87 (10.0%); £3,707,708.07 -> £3,336,552.89 (10.0%); £3,707,708.23 -> £3,336,552.90 (10.0%); £3,707,708.38 -> £3,336,553.02 (10.0%); £3,707,708.54 -> £3,336,553.14 (10.0%); £3,707,708.71 -> £3,336,553.27 (10.0%); £3,707,708.90 -> £3,336,553.40 (10.0%); £3,707,709.11 -> £3,336,553.53 (10.0%); £3,707,709.33 -> £3,336,553.65 (10.0%); £3,707,709.57 -> £3,336,553.78 (10.0%); £3,707,709.84 -> £3,336,553.91 (10.0%); £3,707,710.10 -> £3,336,553.93 (10.0%); £3,707,710.36 -> £3,336,553.96 (10.0%); £3,707,710.61 -> £3,336,553.98 (10.0%); £3,707,710.88 -> £3,336,554.01 (10.0%); £3,707,711.13 -> £3,336,554.03 (10.0%); £3,707,711.39 -> £3,336,554.05 (10.0%); £3,707,711.65 -> £3,336,554.08 (10.0%); £3,707,711.90 -> £3,336,554.10 (10.0%); £3,707,712.16 -> £3,336,554.12 (10.0%); £3,707,712.41 -> £3,336,554.15 (10.0%); £3,707,712.67 -> £3,336,554.17 (10.0%); £3,707,712.93 -> £3,336,554.20 (10.0%); £3,707,713.19 -> £3,336,554.23 (10.0%); £3,707,713.44 -> £3,336,554.36 (10.0%); £3,707,713.70 -> £3,336,554.50 (10.0%); £3,707,713.96 -> £3,336,554.64 (10.0%); £3,707,714.22 -> £3,336,554.77 (10.0%); £3,707,714.47 -> £3,336,554.91 (10.0%); £3,707,714.73 -> £3,336,555.04 (10.0%); £3,707,714.99 -> £3,336,555.18 (10.0%); £3,707,715.26 -> £3,336,555.31 (10.0%); £3,707,715.51 -> £3,336,555.44 (10.0%); £3,707,715.77 -> £3,336,555.58 (10.0%); £3,707,716.02 -> £3,336,555.71 (10.0%); £3,707,716.28 -> £3,336,555.74 (10.0%); £3,707,716.54 -> £3,336,555.77 (10.0%); £3,707,716.78 -> £3,336,555.79 (10.0%); £3,707,717.00 -> £3,336,555.81 (10.0%); £3,707,717.20 -> £3,336,555.84 (10.0%); £3,707,717.34 -> £3,336,555.86 (10.0%); £3,707,717.47 -> £3,336,555.88 (10.0%); £3,707,717.61 -> £3,336,555.89 (10.0%); £3,707,717.75 -> £3,336,555.91 (10.0%); £3,707,717.88 -> £3,336,555.93 (10.0%); £3,707,718.02 -> £3,336,555.95 (10.0%); £3,707,718.16 -> £3,336,555.96 (10.0%); £3,707,718.30 -> £3,336,555.98 (10.0%); £3,707,718.43 -> £3,336,556.00 (10.0%); £3,707,718.57 -> £3,336,556.01 (10.0%); £3,707,718.70 -> £3,336,556.03 (10.0%); £3,707,718.84 -> £3,336,556.20 (10.0%); £3,707,718.97 -> £3,336,556.36 (10.0%); £3,707,719.12 -> £3,336,556.53 (10.0%); £3,707,719.28 -> £3,336,556.71 (10.0%); £3,707,719.47 -> £3,336,556.89 (10.0%); £3,707,719.67 -> £3,336,557.08 (10.0%); £3,707,719.88 -> £3,336,557.26 (10.0%); £3,707,720.11 -> £3,336,557.44 (10.0%); £3,707,720.34 -> £3,336,557.46 (10.0%); £3,707,720.56 -> £3,336,557.49 (10.0%); £3,707,720.79 -> £3,336,557.52 (10.0%); £3,707,721.01 -> £3,336,557.55 (10.0%); £3,707,721.24 -> £3,336,557.57 (10.0%); £3,707,721.47 -> £3,336,557.60 (10.0%); £3,707,721.70 -> £3,336,557.63 (10.0%); £3,707,721.93 -> £3,336,557.66 (10.0%); £3,707,722.15 -> £3,336,557.68 (10.0%); £3,707,722.38 -> £3,336,557.71 (10.0%); £3,707,722.60 -> £3,336,557.73 (10.0%); £3,707,722.82 -> £3,336,557.76 (10.0%); £3,707,723.05 -> £3,336,557.79 (10.0%); £3,707,723.27 -> £3,336,557.96 (10.0%); £3,707,723.51 -> £3,336,558.14 (10.0%); £3,707,723.73 -> £3,336,558.31 (10.0%); £3,707,723.97 -> £3,336,558.48 (10.0%); £3,707,724.20 -> £3,336,558.65 (10.0%); £3,707,724.42 -> £3,336,558.83 (10.0%); £3,707,724.65 -> £3,336,559.00 (10.0%); £3,707,724.87 -> £3,336,559.18 (10.0%); £3,707,725.10 -> £3,336,559.36 (10.0%); £3,707,725.33 -> £3,336,559.53 (10.0%); £3,707,725.55 -> £3,336,559.70 (10.0%); £3,707,725.78 -> £3,336,559.73 (10.0%); £3,707,726.00 -> £3,336,559.76 (10.0%); £3,707,726.22 -> £3,336,559.78 (10.0%); £3,707,726.40 -> £3,336,559.81 (10.0%); £3,707,726.58 -> £3,336,559.83 (10.0%); £3,707,726.72 -> £3,336,559.85 (10.0%); £3,707,726.86 -> £3,336,559.87 (10.0%); £3,707,727.00 -> £3,336,559.89 (10.0%); £3,707,727.14 -> £3,336,559.91 (10.0%); £3,707,727.28 -> £3,336,559.93 (10.0%); £3,707,727.42 -> £3,336,559.94 (10.0%); £3,707,727.56 -> £3,336,559.96 (10.0%); £3,707,727.70 -> £3,336,559.98 (10.0%); £3,707,727.85 -> £3,336,559.99 (10.0%); £3,707,727.98 -> £3,336,560.01 (10.0%); £3,707,728.13 -> £3,336,560.03 (10.0%); £3,707,728.27 -> £3,336,560.17 (10.0%); £3,707,728.42 -> £3,336,560.32 (10.0%); £3,707,728.57 -> £3,336,560.47 (10.0%); £3,707,728.74 -> £3,336,560.62 (10.0%); £3,707,728.93 -> £3,336,560.77 (10.0%); £3,707,729.13 -> £3,336,560.93 (10.0%); £3,707,729.34 -> £3,336,561.09 (10.0%); £3,707,729.57 -> £3,336,561.24 (10.0%); £3,707,729.81 -> £3,336,561.27 (10.0%); £3,707,730.05 -> £3,336,561.30 (10.0%); £3,707,730.28 -> £3,336,561.33 (10.0%); £3,707,730.51 -> £3,336,561.36 (10.0%); £3,707,730.73 -> £3,336,561.40 (10.0%); £3,707,730.97 -> £3,336,561.43 (10.0%); £3,707,731.20 -> £3,336,561.46 (10.0%); £3,707,731.44 -> £3,336,561.49 (10.0%); £3,707,731.67 -> £3,336,561.52 (10.0%); £3,707,731.89 -> £3,336,561.55 (10.0%); £3,707,732.13 -> £3,336,561.58 (10.0%); £3,707,732.36 -> £3,336,561.60 (10.0%); £3,707,732.59 -> £3,336,561.64 (10.0%); £3,707,732.83 -> £3,336,561.78 (10.0%); £3,707,733.06 -> £3,336,561.94 (10.0%); £3,707,733.29 -> £3,336,562.09 (10.0%); £3,707,733.52 -> £3,336,562.24 (10.0%); £3,707,733.76 -> £3,336,562.39 (10.0%); £3,707,733.99 -> £3,336,562.54 (10.0%); £3,707,734.22 -> £3,336,562.70 (10.0%); £3,707,734.46 -> £3,336,562.85 (10.0%); £3,707,734.70 -> £3,336,562.99 (10.0%); £3,707,734.94 -> £3,336,563.15 (10.0%); £3,707,735.18 -> £3,336,563.30 (10.0%); £3,707,735.41 -> £3,336,563.33 (10.0%); £3,707,735.64 -> £3,336,563.36 (10.0%); £3,707,735.87 -> £3,336,563.38 (10.0%); £3,707,736.07 -> £3,336,563.40 (10.0%); £3,707,736.25 -> £3,336,563.42 (10.0%); £3,707,736.41 -> £3,336,563.44 (10.0%); £3,707,736.57 -> £3,336,563.46 (10.0%); £3,707,736.72 -> £3,336,563.48 (10.0%); £3,707,736.89 -> £3,336,563.49 (10.0%); £3,707,737.05 -> £3,336,563.51 (10.0%); £3,707,737.21 -> £3,336,563.53 (10.0%); £3,707,737.37 -> £3,336,563.54 (10.0%); £3,707,737.54 -> £3,336,563.56 (10.0%); £3,707,737.70 -> £3,336,563.57 (10.0%); £3,707,737.86 -> £3,336,563.59 (10.0%); £3,707,738.02 -> £3,336,563.61 (10.0%); £3,707,738.18 -> £3,336,563.75 (10.0%); £3,707,738.34 -> £3,336,563.89 (10.0%); £3,707,738.52 -> £3,336,564.03 (10.0%); £3,707,738.72 -> £3,336,564.18 (10.0%); £3,707,738.94 -> £3,336,564.33 (10.0%); £3,707,739.17 -> £3,336,564.48 (10.0%); £3,707,739.42 -> £3,336,564.63 (10.0%); £3,707,739.70 -> £3,336,564.77 (10.0%); £3,707,739.96 -> £3,336,564.80 (10.0%); £3,707,740.25 -> £3,336,564.82 (10.0%); £3,707,740.52 -> £3,336,564.85 (10.0%); £3,707,740.79 -> £3,336,564.87 (10.0%); £3,707,741.05 -> £3,336,564.89 (10.0%); £3,707,741.33 -> £3,336,564.92 (10.0%); £3,707,741.59 -> £3,336,564.94 (10.0%); £3,707,741.86 -> £3,336,564.97 (10.0%); £3,707,742.14 -> £3,336,564.99 (10.0%); £3,707,742.41 -> £3,336,565.01 (10.0%); £3,707,742.68 -> £3,336,565.04 (10.0%); £3,707,742.96 -> £3,336,565.06 (10.0%); £3,707,743.23 -> £3,336,565.09 (10.0%); £3,707,743.50 -> £3,336,565.23 (10.0%); £3,707,743.76 -> £3,336,565.38 (10.0%); £3,707,744.03 -> £3,336,565.53 (10.0%); £3,707,744.29 -> £3,336,565.68 (10.0%); £3,707,744.55 -> £3,336,565.83 (10.0%); £3,707,744.82 -> £3,336,565.98 (10.0%); £3,707,745.09 -> £3,336,566.13 (10.0%); £3,707,745.35 -> £3,336,566.28 (10.0%); £3,707,745.62 -> £3,336,566.42 (10.0%); £3,707,745.89 -> £3,336,566.57 (10.0%); £3,707,746.15 -> £3,336,566.72 (10.0%); £3,707,746.42 -> £3,336,566.74 (10.0%); £3,707,746.69 -> £3,336,566.77 (10.0%); £3,707,746.93 -> £3,336,566.80 (10.0%); £3,707,747.15 -> £3,336,566.82 (10.0%); £3,707,747.37 -> £3,336,566.84 (10.0%); £3,707,747.53 -> £3,336,566.86 (10.0%); £3,707,747.69 -> £3,336,566.87 (10.0%); £3,707,747.86 -> £3,336,566.89 (10.0%); £3,707,748.02 -> £3,336,566.91 (10.0%); £3,707,748.19 -> £3,336,566.92 (10.0%); £3,707,748.35 -> £3,336,566.94 (10.0%); £3,707,748.51 -> £3,336,566.96 (10.0%); £3,707,748.67 -> £3,336,566.97 (10.0%); £3,707,748.84 -> £3,336,566.99 (10.0%); £3,707,749.00 -> £3,336,567.01 (10.0%); £3,707,749.16 -> £3,336,567.02 (10.0%); £3,707,749.32 -> £3,336,567.14 (10.0%); £3,707,749.48 -> £3,336,567.25 (10.0%); £3,707,749.66 -> £3,336,567.37 (10.0%); £3,707,749.86 -> £3,336,567.50 (10.0%); £3,707,750.08 -> £3,336,567.62 (10.0%); £3,707,750.32 -> £3,336,567.75 (10.0%); £3,707,750.56 -> £3,336,567.87 (10.0%); £3,707,750.83 -> £3,336,567.99 (10.0%); £3,707,751.11 -> £3,336,568.02 (10.0%); £3,707,751.39 -> £3,336,568.04 (10.0%); £3,707,751.65 -> £3,336,568.07 (10.0%); £3,707,751.91 -> £3,336,568.09 (10.0%); £3,707,752.17 -> £3,336,568.12 (10.0%); £3,707,752.44 -> £3,336,568.14 (10.0%); £3,707,752.71 -> £3,336,568.16 (10.0%); £3,707,752.98 -> £3,336,568.19 (10.0%); £3,707,753.24 -> £3,336,568.21 (10.0%); £3,707,753.51 -> £3,336,568.23 (10.0%); £3,707,753.78 -> £3,336,568.26 (10.0%); £3,707,754.05 -> £3,336,568.28 (10.0%); £3,707,754.32 -> £3,336,568.31 (10.0%); £3,707,754.60 -> £3,336,568.44 (10.0%); £3,707,754.86 -> £3,336,568.57 (10.0%); £3,707,755.13 -> £3,336,568.70 (10.0%); £3,707,755.40 -> £3,336,568.83 (10.0%); £3,707,755.67 -> £3,336,568.96 (10.0%); £3,707,755.93 -> £3,336,569.09 (10.0%); £3,707,756.20 -> £3,336,569.22 (10.0%); £3,707,756.46 -> £3,336,569.35 (10.0%); £3,707,756.72 -> £3,336,569.48 (10.0%); £3,707,757.00 -> £3,336,569.61 (10.0%); £3,707,757.27 -> £3,336,569.74 (10.0%); £3,707,757.54 -> £3,336,569.77 (10.0%); £3,707,757.81 -> £3,336,569.79 (10.0%); £3,707,758.06 -> £3,336,569.82 (10.0%); £3,707,758.29 -> £3,336,569.84 (10.0%); £3,707,758.50 -> £3,336,569.86 (10.0%); £3,707,758.67 -> £3,336,569.88 (10.0%); £3,707,758.83 -> £3,336,569.90 (10.0%); £3,707,758.98 -> £3,336,569.91 (10.0%); £3,707,759.14 -> £3,336,569.93 (10.0%); £3,707,759.30 -> £3,336,569.95 (10.0%); £3,707,759.46 -> £3,336,569.96 (10.0%); £3,707,759.62 -> £3,336,569.98 (10.0%); £3,707,759.78 -> £3,336,570.00 (10.0%); £3,707,759.93 -> £3,336,570.01 (10.0%); £3,707,760.09 -> £3,336,570.03 (10.0%); £3,707,760.26 -> £3,336,570.05 (10.0%); £3,707,760.41 -> £3,336,570.19 (10.0%); £3,707,760.57 -> £3,336,570.33 (10.0%); £3,707,760.75 -> £3,336,570.48 (10.0%); £3,707,760.95 -> £3,336,570.63 (10.0%); £3,707,761.17 -> £3,336,570.77 (10.0%); £3,707,761.40 -> £3,336,570.92 (10.0%); £3,707,761.65 -> £3,336,571.06 (10.0%); £3,707,761.92 -> £3,336,571.21 (10.0%); £3,707,762.19 -> £3,336,571.23 (10.0%); £3,707,762.45 -> £3,336,571.26 (10.0%); £3,707,762.73 -> £3,336,571.28 (10.0%); £3,707,762.99 -> £3,336,571.30 (10.0%); £3,707,763.26 -> £3,336,571.33 (10.0%); £3,707,763.53 -> £3,336,571.35 (10.0%); £3,707,763.80 -> £3,336,571.38 (10.0%); £3,707,764.08 -> £3,336,571.40 (10.0%); £3,707,764.36 -> £3,336,571.42 (10.0%); £3,707,764.62 -> £3,336,571.45 (10.0%); £3,707,764.89 -> £3,336,571.47 (10.0%); £3,707,765.16 -> £3,336,571.50 (10.0%); £3,707,765.43 -> £3,336,571.53 (10.0%); £3,707,765.70 -> £3,336,571.68 (10.0%); £3,707,765.97 -> £3,336,571.84 (10.0%); £3,707,766.24 -> £3,336,572.00 (10.0%); £3,707,766.51 -> £3,336,572.17 (10.0%); £3,707,766.78 -> £3,336,572.32 (10.0%); £3,707,767.05 -> £3,336,572.48 (10.0%); £3,707,767.32 -> £3,336,572.63 (10.0%); £3,707,767.58 -> £3,336,572.78 (10.0%); £3,707,767.85 -> £3,336,572.93 (10.0%); £3,707,768.12 -> £3,336,573.08 (10.0%); £3,707,768.39 -> £3,336,573.23 (10.0%); £3,707,768.66 -> £3,336,573.26 (10.0%); £3,707,768.94 -> £3,336,573.28 (10.0%); £3,707,769.19 -> £3,336,573.31 (10.0%); £3,707,769.41 -> £3,336,573.33 (10.0%); £3,707,769.62 -> £3,336,573.35 (10.0%); £3,707,769.78 -> £3,336,573.37 (10.0%); £3,707,769.94 -> £3,336,573.38 (10.0%); £3,707,770.11 -> £3,336,573.40 (10.0%); £3,707,770.27 -> £3,336,573.42 (10.0%); £3,707,770.42 -> £3,336,573.44 (10.0%); £3,707,770.59 -> £3,336,573.45 (10.0%); £3,707,770.74 -> £3,336,573.47 (10.0%); £3,707,770.90 -> £3,336,573.49 (10.0%); £3,707,771.06 -> £3,336,573.50 (10.0%); £3,707,771.22 -> £3,336,573.52 (10.0%); £3,707,771.39 -> £3,336,573.54 (10.0%); £3,707,771.55 -> £3,336,573.68 (10.0%); £3,707,771.71 -> £3,336,573.82 (10.0%); £3,707,771.90 -> £3,336,573.97 (10.0%); £3,707,772.10 -> £3,336,574.12 (10.0%); £3,707,772.32 -> £3,336,574.26 (10.0%); £3,707,772.55 -> £3,336,574.41 (10.0%); £3,707,772.80 -> £3,336,574.55 (10.0%); £3,707,773.08 -> £3,336,574.69 (10.0%); £3,707,773.34 -> £3,336,574.71 (10.0%); £3,707,773.61 -> £3,336,574.74 (10.0%); £3,707,773.88 -> £3,336,574.76 (10.0%); £3,707,774.15 -> £3,336,574.78 (10.0%); £3,707,774.43 -> £3,336,574.81 (10.0%); £3,707,774.70 -> £3,336,574.83 (10.0%); £3,707,774.97 -> £3,336,574.86 (10.0%); £3,707,775.24 -> £3,336,574.88 (10.0%); £3,707,775.52 -> £3,336,574.90 (10.0%); £3,707,775.79 -> £3,336,574.93 (10.0%); £3,707,776.06 -> £3,336,574.95 (10.0%); £3,707,776.33 -> £3,336,574.97 (10.0%); £3,707,776.60 -> £3,336,575.00 (10.0%); £3,707,776.89 -> £3,336,575.15 (10.0%); £3,707,777.16 -> £3,336,575.30 (10.0%); £3,707,777.43 -> £3,336,575.45 (10.0%); £3,707,777.69 -> £3,336,575.60 (10.0%); £3,707,777.96 -> £3,336,575.75 (10.0%); £3,707,778.24 -> £3,336,575.90 (10.0%); £3,707,778.52 -> £3,336,576.05 (10.0%); £3,707,778.79 -> £3,336,576.20 (10.0%); £3,707,779.07 -> £3,336,576.34 (10.0%); £3,707,779.34 -> £3,336,576.49 (10.0%); £3,707,779.61 -> £3,336,576.63 (10.0%); £3,707,779.89 -> £3,336,576.66 (10.0%); £3,707,780.16 -> £3,336,576.69 (10.0%); £3,707,780.41 -> £3,336,576.71 (10.0%); £3,707,780.65 -> £3,336,576.73 (10.0%); £3,707,780.87 -> £3,336,576.75 (10.0%); £3,707,781.02 -> £3,336,576.77 (10.0%); £3,707,781.19 -> £3,336,576.79 (10.0%); £3,707,781.35 -> £3,336,576.80 (10.0%); £3,707,781.52 -> £3,336,576.82 (10.0%); £3,707,781.67 -> £3,336,576.84 (10.0%); £3,707,781.84 -> £3,336,576.85 (10.0%); £3,707,782.00 -> £3,336,576.87 (10.0%); £3,707,782.17 -> £3,336,576.89 (10.0%); £3,707,782.33 -> £3,336,576.90 (10.0%); £3,707,782.49 -> £3,336,576.92 (10.0%); £3,707,782.65 -> £3,336,576.94 (10.0%); £3,707,782.81 -> £3,336,577.06 (10.0%); £3,707,782.97 -> £3,336,577.18 (10.0%); £3,707,783.15 -> £3,336,577.31 (10.0%); £3,707,783.35 -> £3,336,577.45 (10.0%); £3,707,783.57 -> £3,336,577.58 (10.0%); £3,707,783.80 -> £3,336,577.71 (10.0%); £3,707,784.05 -> £3,336,577.84 (10.0%); £3,707,784.31 -> £3,336,577.96 (10.0%); £3,707,784.59 -> £3,336,577.99 (10.0%); £3,707,784.85 -> £3,336,578.01 (10.0%); £3,707,785.12 -> £3,336,578.04 (10.0%); £3,707,785.39 -> £3,336,578.06 (10.0%); £3,707,785.66 -> £3,336,578.09 (10.0%); £3,707,785.94 -> £3,336,578.11 (10.0%); £3,707,786.22 -> £3,336,578.13 (10.0%); £3,707,786.49 -> £3,336,578.16 (10.0%); £3,707,786.75 -> £3,336,578.18 (10.0%); £3,707,787.03 -> £3,336,578.20 (10.0%); £3,707,787.29 -> £3,336,578.22 (10.0%); £3,707,787.56 -> £3,336,578.25 (10.0%); £3,707,787.83 -> £3,336,578.28 (10.0%); £3,707,788.09 -> £3,336,578.41 (10.0%); £3,707,788.37 -> £3,336,578.55 (10.0%); £3,707,788.64 -> £3,336,578.69 (10.0%); £3,707,788.91 -> £3,336,578.84 (10.0%); £3,707,789.18 -> £3,336,578.98 (10.0%); £3,707,789.45 -> £3,336,579.12 (10.0%); £3,707,789.73 -> £3,336,579.25 (10.0%); £3,707,789.99 -> £3,336,579.40 (10.0%); £3,707,790.26 -> £3,336,579.54 (10.0%); £3,707,790.54 -> £3,336,579.68 (10.0%); £3,707,790.81 -> £3,336,579.81 (10.0%); £3,707,791.08 -> £3,336,579.84 (10.0%); £3,707,791.35 -> £3,336,579.87 (10.0%); £3,707,791.60 -> £3,336,579.89 (10.0%); £3,707,791.84 -> £3,336,579.91 (10.0%)
- Bills issued: 153, average clarity 0.806, average bill shock 17.0%, bad debt provision £11,504.77, avg complaint probability 4.8%
- Solvency signal: £309,222/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £201,263.61 vs. naked (unhedged) net margin: £607,649.06
- hedging cost £406,385.45 vs. a fully unhedged book (commodity-only: actual net £201,263.61 vs. naked net £607,649.06)
  - C1_2: actual £207.67 vs. naked £705.98 -- hedging cost £498.32
  - C2_2: actual £117.83 vs. naked £1,056.98 -- hedging cost £939.14
  - C5_2: actual £112.58 vs. naked £1,053.00 -- hedging cost £940.42
  - C7: actual £-27.34 vs. naked £653.82 -- hedging cost £681.16
  - C8: actual £312.62 vs. naked £1,426.63 -- hedging cost £1,114.01
  - C9: actual £373.18 vs. naked £1,427.71 -- hedging cost £1,054.53
  - C_IC1: actual £114,253.44 vs. naked £208,996.78 -- hedging cost £94,743.34
  - C_IC2: actual £60,322.70 vs. naked £111,508.78 -- hedging cost £51,186.08
  - C_IC3: actual £20,317.94 vs. naked £121,162.83 -- hedging cost £100,844.89
  - C_IC3g: actual £3,837.46 vs. naked £56,934.03 -- hedging cost £53,096.57
  - C_IC4: actual £1,435.52 vs. naked £102,722.50 -- hedging cost £101,286.98

**Year narrative:** 2024 produced a net gain of £330,160.28 across 14 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 45 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £118,069.43 (gross £522,279.71, capital £5,697.53)
  - Electricity: gross £468,770.93, capital £5,697.53, net £114,281.92
  - Gas: gross £53,508.78, capital £0.00, net £3,787.52
- Treasury at year end: £3,760,599.46
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C8 0.89 (avg 0.89)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2025-01-08 period 31, net margin £-81.23

**Customer Book**

- Active accounts: 11 (C1_2, C2_2, C5_2, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 1
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 2 accounts
- Average CLV (Point-in-Time, year-end 2025): £362,080.49
  - By billing account: C1 £4,338.09, C1_2 £3,856.07, C2 £5,911.85, C2_2 £3,493.53, C3 £5,747.90, C4 £2,772.74, C5 £9,675.09, C5_2 £4,275.95, C6 £15,200.05, C7 £7,594.48, C8 £7,947.09, C9 £8,801.76, C_IC1 £1,355,811.81, C_IC2 £849,459.41, C_IC3 £2,158,651.79, C_IC4 £1,349,750.16
- Bill shock events (>=20%): 25 -- C7 2025-04-30 (36%); C7 2025-05-31 (22%); C7 2025-06-07 (80%); C8 2025-01-31 (30%); C8 2025-02-28 (24%); C8 2025-04-30 (40%); C8 2025-05-31 (35%); C8 2025-06-07 (73%); C9 2025-04-30 (24%); C9 2025-05-31 (32%); C9 2025-06-07 (72%); C_IC1 2025-06-07 (77%); C_IC2 2025-06-07 (75%); C_IC3 2025-06-07 (78%); C_IC3g 2025-06-07 (77%); C_IC4 2025-06-07 (79%); C1_2 2025-04-30 (42%); C1_2 2025-05-31 (28%); C1_2 2025-06-07 (80%); C2_2 2025-01-31 (28%); C2_2 2025-02-28 (23%); C2_2 2025-05-31 (35%); C2_2 2025-06-07 (73%); C5_2 2025-04-30 (29%); C5_2 2025-06-07 (79%)
- Churn risk (accounts renewing in 2025): 3 at risk (≥20% churn prob): C2_2 32%, C8 32%, C9 26%

**Pricing & Margin**

- C1_2 (electricity): tariff £253.01/MWh, net margin £205.11
- C2_2 (electricity): tariff £201.48-£292.73/MWh, net margin £109.12
- C5_2 (electricity): tariff £231.60/MWh, net margin £113.41
- C7 (electricity): tariff £165.00-£315.00/MWh, net margin £-23.72 -- **net-negative**
- C8 (electricity): tariff £149.29-£309.47/MWh, net margin £75.61
- C9 (electricity): tariff £165.00-£315.00/MWh, net margin £195.49
- C_IC1 (electricity): tariff £167.39-£319.56/MWh, net margin £62,405.83
- C_IC2 (electricity): tariff £161.16-£307.68/MWh, net margin £29,516.09
- C_IC3 (electricity): tariff £89.47-£170.81/MWh, net margin £20,267.57
- C_IC3g (gas): tariff £54.85/MWh, net margin £3,787.52
- C_IC4 (electricity): tariff £123.20-£273.78/MWh, net margin £1,417.43

**Portfolio Health**

- Capital cost ratio: 1.1% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 66, average clarity 0.768, average bill shock 24.7%, bad debt provision £5,022.37, avg complaint probability 6.1%
- Solvency signal: £376,060/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £66.19 vs. naked (unhedged) net margin: £349.73
- hedging cost £283.54 vs. a fully unhedged book (commodity-only: actual net £66.19 vs. naked net £349.73)
  - C2_2: actual £96.28 vs. naked £230.84 -- hedging cost £134.56
  - C8: actual £-30.08 vs. naked £118.90 -- hedging cost £148.98

**Year narrative:** 2025 produced a net gain of £118,069.43 across 11 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 25 customer(s) experienced a bill shock of >=20%.
