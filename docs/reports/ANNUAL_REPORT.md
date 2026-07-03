# Annual Report — The Synthetic Enterprise


## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £2,466,636.22
- Final treasury: £3,903,585.29
  (£1,436,949.07 net change)
- Solvency signal (final year): £417,084/customer (9 customers, OK; Ofgem floor £130/customer)
- Customer bills (all-in): £19,797,278.86
  VAT remitted to HMRC: (£956,088.16) | Revenue (ex-VAT): £18,841,190.70
  Non-commodity pass-through: (£4,784,583.10)
- Gross margin: £6,453,707.51
- Capital costs: £51,305.83
- Net margin: £6,402,401.68
- Capital cost ratio: 0.8% of gross
- Net margin as % of revenue: 34.0%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 38
- Bills issued: 1574, average clarity 0.815,
  service quality score 0.904
- Enterprise value (CLV sum across 15 billing accounts): £8,087,302.19
- Cost to serve (whole portfolio): £91,342.93, net margin after cost to serve: £6,311,058.75
- Hedge effectiveness (whole window): hedging cost £4,227,921.44 vs. a fully unhedged book (commodity-only: actual net £1,436,949.07 vs. naked net £5,664,870.51)

- **2021** (crisis year): net margin £66,746.46, 0 risk committee wake-up(s).
- **2022** (crisis year): net margin £303,003.48, 9 risk committee wake-up(s).

## Board Risk Summary

Synthesised risk indicators across portfolio, capital, operations and pricing.
RAG: RED = immediate board action, AMBER = monitor closely, GREEN = on track.

| Risk Indicator | Value | RAG | Implication |
|----------------|-------|-----|-------------|
| Revenue concentration | HHI 2246, I&C 99% | **AMBER** | Single I&C departure removes 14-29%% of margin |
| Gas segment ROC | 259.7x (net £52,112.93 on £200.69 capital) | **GREEN** | Gas legs destroy capital; electricity cross-subsidises |
| Churn blind miss rate | 5/6 departures (83%) | **RED** | Company did not forecast these churns |
| Demand estimation error | Peak mean 3.0%, max 15.6% | **AMBER** | EAC drift from asset acquisitions; smart meters eliminate |
| Pricing basis risk (worst year) | 2025: +33.1% mean over-estimate | **RED** | Over-priced contracts help margin but create churn risk |
| Net margin % of revenue | 34.0% (benchmark: 2-5%) | **GREEN** | Within/above industry range |

**Board Action Required:** Churn blind miss rate, Pricing basis risk (worst year) — RED rating(s) require immediate attention.

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £6,453,707.51, capital £51,305.83, net £6,402,401.68. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 0.8% (commodity basis, comparable to old model) / 0.8% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £66,746.46 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 34.0%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £6,402,401.68
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £5,664,870.51
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £4,227,921.44 vs. a fully unhedged book (commodity-only: actual net £1,436,949.07 vs. naked net £5,664,870.51)
- **Best hedging decision of the run**: C_IC1, term starting
  2021-04-30 (hedge fraction 0.92) -- hedging
  protected £99,383.14 vs. going naked.
- **Worst hedging decision of the run**: C_IC3, term
  starting 2022-12-31 (hedge fraction 0.96) --
  over-hedging cost £612,915.06 vs. going
  naked.

## Segment Margin Trend

Net margin (£) by segment, by year:

| Year | I&C electricity | I&C gas | SME electricity | resi electricity | resi gas | Total |
|---|---|---|---|---|---|---|
| 2016 | £0.00 | £0.00 | £254.88 | £626.84 | £296.53 | £1,178.25 |
| 2017 | £29,047.38 | £0.00 | £233.41 | £821.92 | £463.34 | £30,566.05 |
| 2018 | £99,071.38 | £0.00 | £-244.55 | £504.67 | £374.66 | £99,706.17 |
| 2019 | £217,183.69 | £9,326.63 | £213.88 | £720.65 | £427.56 | £227,872.41 |
| 2020 | £111,150.85 | £9,435.16 | £335.48 | £875.65 | £417.70 | £122,214.83 |
| 2021 | £57,974.67 | £8,520.22 | £189.56 | £275.14 | £-213.12 | £66,746.46 |
| 2022 | £301,702.91 | £4,134.82 | £931.94 | £-2,464.34 | £-1,301.85 | £303,003.48 |
| 2023 | £124,225.91 | £8,526.27 | £151.01 | £106.58 | £-1,164.32 | £131,845.43 |
| 2024 | £324,422.67 | £8,684.92 | £1,680.08 | £2,009.47 | £396.91 | £337,194.05 |
| 2025 | £112,184.31 | £3,787.52 | £298.65 | £351.47 | £0.00 | £116,621.95 |

## Customer Lifecycle Events

Renewal decisions rolled at each annual renewal point across the simulation window.
Retained: **53** renewals.  Lost (churned): **6** accounts.

Accounts lost before end of window: C1, C2, C3, C4, C5, C6

| Account | Date | Outcome | p(churn) | p(win-back) | p(retain) | Roll |
|---------|------|---------|----------|-------------|-----------|------|
| C1 | 2016-12-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.1646 |
| C5 | 2016-12-31 | renewed | 0.0500 | 0.3500 | 0.9675 | 0.2812 |
| C7 | 2016-12-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.1050 |
| C1 | 2017-12-31 | renewed | 0.1100 | 0.5500 | 0.9505 | 0.6188 |
| C5 | 2017-12-31 | renewed | 0.1100 | 0.3500 | 0.9285 | 0.4449 |
| C7 | 2017-12-31 | renewed | 0.1100 | 0.5500 | 0.9505 | 0.8255 |
| C_IC1 | 2018-01-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.3902 |
| C1 | 2018-12-31 | renewed | 0.1100 | 0.5500 | 0.9505 | 0.0480 |
| C5 | 2018-12-31 | renewed | 0.1100 | 0.3500 | 0.9285 | 0.3096 |
| C7 | 2018-12-31 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.6312 |
| C_IC2 | 2019-01-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.3710 |
| C1 | 2019-12-31 | renewed | 0.2900 | 0.5500 | 0.8695 | 0.2972 |
| C5 | 2019-12-31 | renewed | 0.3500 | 0.3500 | 0.7725 | 0.4302 |
| C7 | 2019-12-31 | renewed | 0.2900 | 0.5500 | 0.8695 | 0.7670 |
| C2 | 2020-03-31 | renewed | 0.0800 | 0.5500 | 0.9640 | 0.8936 |
| C6 | 2020-03-31 | renewed | 0.1100 | 0.3500 | 0.9285 | 0.4643 |
| C8 | 2020-03-31 | renewed | 0.2300 | 0.5500 | 0.8965 | 0.1066 |
| C3 | 2020-06-30 | churned **CHURNED** | 0.1100 | 0.5500 | 0.9505 | 0.9704 |
| C9 | 2020-06-30 | renewed | 0.2300 | 0.5500 | 0.8965 | 0.5378 |
| C4 | 2020-09-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.2845 |
| C1 | 2020-12-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.8047 |
| C5 | 2020-12-30 | renewed | 0.3200 | 0.3500 | 0.7920 | 0.7480 |
| C7 | 2020-12-30 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.4829 |
| C_IC3 | 2020-12-31 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.5941 |
| C2 | 2021-03-31 | renewed | 0.0800 | 0.5500 | 0.9640 | 0.6102 |
| C6 | 2021-03-31 | renewed | 0.0800 | 0.3500 | 0.9480 | 0.5431 |
| C8 | 2021-03-31 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.4901 |
| C9 | 2021-06-30 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.5305 |
| C4 | 2021-09-30 | renewed | 0.1100 | 0.5500 | 0.9505 | 0.4564 |
| C1 | 2021-12-30 | churned **CHURNED** | 0.1100 | 0.5500 | 0.9505 | 0.9691 |
| C5 | 2021-12-30 | renewed | 0.1700 | 0.3500 | 0.8895 | 0.8247 |
| C7 | 2021-12-30 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.1963 |
| C_IC3 | 2021-12-31 | renewed | 0.3200 | 0.5500 | 0.8560 | 0.5838 |
| C2 | 2022-03-31 | churned **CHURNED** | 0.3800 | 0.5500 | 0.8290 | 0.9547 |
| C6 | 2022-03-31 | renewed | 0.3500 | 0.3500 | 0.7725 | 0.1058 |
| C8 | 2022-03-31 | renewed | 0.2600 | 0.5500 | 0.8830 | 0.5712 |
| C9 | 2022-06-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.5875 |
| C4 | 2022-09-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.8552 |
| C5 | 2022-12-30 | churned **CHURNED** | 0.3800 | 0.3500 | 0.7530 | 0.9650 |
| C7 | 2022-12-30 | renewed | 0.2300 | 0.5500 | 0.8965 | 0.0637 |
| C_IC3 | 2022-12-31 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.8723 |
| C2_2 | 2023-03-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.0093 |
| C6 | 2023-03-31 | renewed | 0.4100 | 0.3500 | 0.7335 | 0.5155 |
| C8 | 2023-03-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.3785 |
| C9 | 2023-06-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.0307 |
| C4 | 2023-09-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.6095 |
| C5_2 | 2023-12-30 | renewed | 0.0500 | 0.3500 | 0.9675 | 0.6875 |
| C7 | 2023-12-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.1905 |
| C_IC3 | 2023-12-31 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.7019 |
| C2_2 | 2024-03-30 | renewed | 0.2300 | 0.5500 | 0.8965 | 0.6064 |
| C6 | 2024-03-30 | churned **CHURNED** | 0.2600 | 0.3500 | 0.8310 | 0.9632 |
| C8 | 2024-03-30 | renewed | 0.1700 | 0.5500 | 0.9235 | 0.0592 |
| C9 | 2024-06-29 | renewed | 0.1700 | 0.5500 | 0.9235 | 0.0025 |
| C4 | 2024-09-29 | churned **CHURNED** | 0.3800 | 0.5500 | 0.8290 | 0.9018 |
| C5_2 | 2024-12-29 | renewed | 0.0800 | 0.3500 | 0.9480 | 0.4422 |
| C7 | 2024-12-29 | renewed | 0.2900 | 0.5500 | 0.8695 | 0.4099 |
| C_IC3 | 2024-12-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.3751 |
| C2_2 | 2025-03-30 | renewed | 0.3200 | 0.5500 | 0.8560 | 0.4434 |
| C8 | 2025-03-30 | renewed | 0.3200 | 0.5500 | 0.8560 | 0.4808 |

## Churn Prediction Basis Risk

At each renewal the company estimated churn risk from observable signals (rate change %, customer tenure). The SIM used its bill-shock model (actual bill amount relative to customer-specific thresholds). The gap is epistemic: in crisis years the company sees a rate % while the SIM sees the household-level financial shock — the same failure mode that surprised real suppliers in 2021-22.

- **Average absolute error:** 132.5%
- **Average signed error:** +28.9% (over-estimates vs SIM)
- **Renewal events with estimates:** 59

| Year | Renewals | Avg error (signed) | Avg abs error |
|------|----------|--------------------|---------------|
| 2016 | 3 | +3.6% | 3.6% |
| 2017 | 3 | -54.5% | 54.5% |
| 2018 | 4 | +399.8% | 433.8% |
| 2019 | 4 | +389.8% | 510.2% |
| 2020 | 10 | -53.0% | 63.7% |
| 2021 | 9 | +28.6% | 101.5% |
| 2022 | 8 | -78.4% | 78.4% |
| 2023 | 8 | +27.4% | 133.3% |
| 2024 | 8 | -56.6% | 56.6% |
| 2025 | 2 | -84.4% | 84.4% |

Positive error = company over-estimated churn vs SIM. Negative error = company under-estimated (more dangerous — expected retentions that were actually at risk).

## Active vs Passive Renewal Split (Phase 33a)

~35% of domestic/SME customers actively choose a new fixed deal at term end. ~65% roll to SVT by inaction — they are inert: low rate sensitivity, ~5% churn base. Crisis years (2022) force all renewals passive (no fixed deals available).

- **Total renewal events:** 59
- **Active renewers:** 18 (31%) — mean company estimate 30.1%, abs error 201.0%
- **Passive SVT-rollers:** 41 (69%) — mean company estimate 7.5%, abs error 102.4%

| Year | Active | Passive | Active est | Passive est | Active abs err | Passive abs err |
|------|--------|---------|-----------|------------|---------------|----------------|
| 2016 | 0 | 3 | 0.0% | 5.2% | 0.0% | 3.6% |
| 2017 | 0 | 3 | 0.0% | 5.0% | 0.0% | 54.5% |
| 2018 | 2 | 2 | 19.1% | 44.4% | 51.5% | 816.1% |
| 2019 | 2 | 2 | 51.5% | 5.0% | 936.2% | 84.2% |
| 2020 | 5 | 5 | 12.6% | 5.0% | 63.7% | 63.8% |
| 2021 | 3 | 6 | 66.0% | 5.2% | 195.2% | 54.6% |
| 2022 | 0 | 8 | 0.0% | 7.2% | 0.0% | 78.4% |
| 2023 | 3 | 5 | 30.1% | 6.2% | 214.3% | 84.7% |
| 2024 | 3 | 5 | 16.5% | 5.0% | 32.2% | 71.2% |
| 2025 | 0 | 2 | 0.0% | 5.0% | 0.0% | 84.4% |

Passive renewers should show lower company estimates and lower SIM churn — high abs error for passive renewers indicates the passive model needs recalibration.

## SVT Comparative Pricing — Passive Renewers (Phase 39a)

Passive renewers roll to a new fixed deal by inaction. A rate above SVT creates latent churn risk: once the customer notices they're paying more than the cap, they switch. A rate below SVT signals loyalty value — the company is rewarding inertia.

- **Passive renewal events with SVT data:** 41
- **Above SVT (at-risk):** 10 (24%)
- **Below/at SVT (protected):** 31 (76%)
- **Mean rate vs SVT premium:** -10.7%

| Year | Passive Renewals | Above SVT | Avg Premium | Avg Fixed Rate (£/MWh) | Avg SVT (£/MWh) |
|------|-----------------|-----------|-------------|----------------------|----------------|
| 2016 | 3 | 0 (0%) | -6.3% | 131.1 | 140.0 |
| 2017 | 3 | 0 (0%) | -14.3% | 119.9 | 140.0 |
| 2018 | 2 | 1 (50%) | +0.2% | 152.9 | 152.5 |
| 2019 | 2 | 0 (0%) | -29.1% | 126.5 | 178.5 |
| 2020 | 5 | 0 (0%) | -25.9% | 130.9 | 176.9 |
| 2021 | 6 | 3 (50%) | +0.9% | 184.2 | 183.8 |
| 2022 | 8 | 4 (50%) | +4.3% | 292.4 | 343.4 |
| 2023 | 5 | 0 (0%) | -32.5% | 225.1 | 364.0 |
| 2024 | 5 | 1 (20%) | -12.2% | 215.5 | 246.5 |
| 2025 | 2 | 1 (50%) | -3.4% | 240.1 | 248.6 |

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
| 2020 | 22 | 12.5% | 33.8% |
| 2021 | 17 | 14.5% | 44.5% |
| 2022 | 17 | 11.8% | 23.2% |
| 2023 | 15 | 21.3% | 40.0% |
| 2024 | 14 | 10.3% | 22.6% |
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
| 2016 | 3 | 0.04× | 0.05× |
| 2017 | 3 | 0.55× | 0.55× |
| 2018 | 4 | 4.34× ⚠ | 15.78× |
| 2019 | 4 | 5.10× ⚠ | 18.00× |
| 2020 | 10 | 0.64× | 0.88× |
| 2021 | 9 | 1.01× | 3.87× |
| 2022 | 8 | 0.78× | 0.87× |
| 2023 | 8 | 1.33× | 5.43× |
| 2024 | 8 | 0.57× | 0.87× |
| 2025 | 2 | 0.84× | 0.84× |

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
| 2021 | 11 | 1.10% | 4.24% | MODERATE — asset adoption visible |
| 2022 | 10 | 2.20% | 7.47% | MODERATE — asset adoption visible |
| 2023 | 10 | 2.35% | 8.47% | MODERATE — asset adoption visible |
| 2024 | 10 | 2.95% | 15.56% | HIGH drift — EV/asset cohort growing |
| 2025 | 2 | 1.42% | 2.07% | MODERATE — asset adoption visible |

**Trend:** demand estimation error grew from **0.07%** in 2016 to **2.95%** mean / **15.56%** max in 2024. Root cause: new asset acquisitions (Phase B life events) create a temporary estimation gap until the company observes a full billing cycle.
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
| 2022 | 10 | 2.2% | 7.5% |
| 2023 | 10 | 2.3% | 8.5% |
| 2024 | 10 | 3.0% | 15.6% |
| 2025 | 2 | 1.4% | 2.1% |

**89** of **89** renewals used prior billing records; **0** used SIM oracle fallback (first term, no billing history).

## EAC Drift Snapshot (Phase AI)

Per-customer consumption drift from company billing history (first renewal → latest renewal).
Drift > +15%: EV/ASHP acquisition. Drift < −15%: solar installation or efficiency upgrade.

**1 significant** (≥15%) | **1 moderate** (5–15%) | **12 stable** (<5%)

| Customer | Baseline kWh | Current kWh | Drift | Likely Cause |
|----------|-------------|-------------|-------|--------------|
| C4 | 4,131 | 3,365 | -19% | likely solar installation or significant efficiency upgrade |
| C7 | 13,179 | 12,155 | -8% | efficiency improvement or reduced occupancy |

**Portfolio demand trend:** 2 customers increasing / 11 decreasing (mean drift: -2.7%)

## Company CRM — Event Log

Dated artefacts of customer lifecycle events as seen by the company layer.
Total events: **8** (6 churn, 2 acquisition)

| Date | Event | Customer | Detail |
|------|-------|----------|--------|
| 2020-06-30 | CHURN | C3 | SIM p=0.11, company est=0.05 |
| 2021-12-30 | CHURN | C1 | SIM p=0.11, company est=0.05 |
| 2022-03-31 | CHURN | C2 | SIM p=0.38, company est=0.07 |
| 2022-03-31 | ACQUISITION | C2_2 | home-move-win (predecessor: C2) |
| 2022-12-30 | CHURN | C5 | SIM p=0.38, company est=0.05 |
| 2022-12-30 | ACQUISITION | C5_2 | home-move-win (predecessor: C5) |
| 2024-03-30 | CHURN | C6 | SIM p=0.26, company est=0.25 |
| 2024-09-29 | CHURN | C4 | SIM p=0.38, company est=0.05 |

**SIM ground truth vs company CRM reconciliation (year-end snapshots):**

| Year-end | SIM churned (cumulative) | CRM active | Match |
|----------|--------------------------|------------|-------|
| 2016-12-31 | 0 accounts | 0 active | yes |
| 2017-12-31 | 0 accounts | 0 active | yes |
| 2018-12-31 | 0 accounts | 0 active | yes |
| 2019-12-31 | 0 accounts | 0 active | yes |
| 2020-12-31 | 1 accounts | 0 active | yes |
| 2021-12-31 | 2 accounts | 0 active | yes |
| 2022-12-31 | 4 accounts | 2 active | yes |
| 2023-12-31 | 4 accounts | 2 active | yes |
| 2024-12-31 | 6 accounts | 2 active | yes |
| 2025-12-31 | 6 accounts | 2 active | yes |

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
| 2020 | 238,636 | 35,391 | 69,454 | 56,550 | 70,024 | 0 | 470,055 |  |
| 2021 | 246,565 | 15,001 | 71,336 | 49,645 | 62,799 | 41,404 | 486,751 |  |
| 2022 | 256,427 | -49,780 | 71,047 | 36,712 | 69,167 | 99,560 | 483,133 | ⬇ CfD REBATE |
| 2023 | 272,110 | 64,827 | 71,831 | 51,008 | 75,168 | 13,763 | 548,706 |  |
| 2024 | 307,883 | 110,026 | 72,944 | 68,765 | 82,632 | 2,000 | 644,249 |  |
| 2025 | 135,847 | 46,991 | 31,221 | 31,057 | 36,183 | 854 | 282,153 |  |
| **Total** | **1,725,922** | **263,398** | **459,082** | **337,069** | **467,805** | **157,583** | **3,410,858** | |

Total policy cost: £3,410,858 across all years. Net margin is after deducting this. Revenue side: tariff pass-through at term-start year's levy rate — basis risk arises when cross-year terms meet a different actual levy (notably 2022 CfD rebate).

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
| 2020 | 124,585 |  |
| 2021 | 123,496 |  |
| 2022 | 134,078 | BSUoS 100% demand-side from Apr 2022 |
| 2023 | 140,176 | RIIO-ED2 from Apr 2023 |
| 2024 | 144,050 |  |
| 2025 | 61,623 |  |
| **Total** | **884,328** | |

Total network cost: £884,328 across all years. Pass-through: tariff unit rate includes network cost at term-start year's rate; settlement deducts it — basis risk near-zero for annual contracts.

## Gas Policy Costs and Network Charges (Phase 30b)

Gas CCL: non-domestic only (domestic gas exempt). Gas network (GDN + NTS): all on unit rate.
GGL (Green Gas Levy): per-meter, from Nov 2021; tiny in £/MWh terms.

| Year | Gas Policy (CCL + GGL) £ | Gas Network £ | Total Gas Non-Commodity £ |
|------|--------------------------|---------------|--------------------------|
| 2016 | 0 | 479 | 479 |
| 2017 | 0 | 898 | 898 |
| 2018 | 0 | 905 | 905 |
| 2019 | 15,155 | 50,388 | 65,543 |
| 2020 | 19,468 | 47,215 | 66,683 |
| 2021 | 22,472 | 50,441 | 72,913 |
| 2022 | 27,045 | 54,433 | 81,478 |
| 2023 | 32,229 | 79,700 | 111,929 |
| 2024 | 37,494 | 76,429 | 113,923 |
| 2025 | 17,243 | 31,816 | 49,059 |
| **Total** | **171,106** | **392,704** | **563,810** |

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
| 2020 | 121,125 | 43,943 | 77,182 | 19,468 | 47,215 | 11 | 9,853 | +8.1% |
| 2021 | 297,852 | 215,060 | 82,792 | 22,472 | 50,441 | 16 | 8,307 | +2.8% |
| 2022 | 588,330 | 497,974 | 90,356 | 27,045 | 54,433 | 34 | 2,833 | +0.5% |
| 2023 | 297,198 | 176,258 | 120,940 | 32,229 | 79,700 | 52 | 7,362 | +2.5% |
| 2024 | 270,491 | 146,077 | 124,414 | 37,494 | 76,429 | 23 | 9,082 | +3.4% |
| 2025 | 132,454 | 78,945 | 53,509 | 17,243 | 31,816 | 0 | 3,788 | +2.9% |
| **Total** | **1,852,377** | **1,223,528** | **628,849** | **171,106** | **392,704** | **201** | **52,113** | **+2.8%** |

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
| 2020 | 2,914,253 | 13 | 224,173 | 1724.41× | OK |
| 2021 | 2,942,148 | 12 | 245,179 | 1885.99× | OK |
| 2022 | 3,137,595 | 13 | 241,353 | 1856.57× | OK |
| 2023 | 3,322,341 | 11 | 302,031 | 2323.32× | OK |
| 2024 | 3,703,825 | 11 | 336,711 | 2590.09× | OK |
| 2025 | 3,753,752 | 9 | 417,084 | 3208.34× | OK |

End-state (2025): **£417,084/account** across 9 billing accounts — OK.

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
| 2021 | 4,340 | 5,208 | 2,942,148 | 564.9× | OK |
| 2022 | 8,507 | 10,209 | 3,137,595 | 307.3× | OK |
| 2023 | 5,620 | 6,744 | 3,322,341 | 492.7× | OK |
| 2024 | 2,661 | 3,194 | 3,703,825 | 1159.8× | OK |
| 2025 | 3,888 | 4,666 | 3,753,752 | 804.5× | OK |




## Time-of-Use Tariff Utilization (C7-C9 HH Customers)

Peak windows: 07:00–11:00 and 16:00–20:00 weekdays (periods 15-22, 33-40).
Peak rate = 1.5× flat; off-peak = 0.786× flat (revenue-neutral at 30/70 split).
ToU Premium: actual revenue vs flat-rate equivalent — positive when actual peak % > 30% design.

| Customer | Total kWh | Peak kWh | Peak % | Peak Revenue | Off-peak Revenue | Avg Peak Rate | Avg Off-peak Rate | ToU Premium |
|----------|-----------|----------|--------|-------------|-----------------|--------------|------------------|-------------|
| C7 | 120,839 | 36,249 | 30.0% | £9,518.21 | £12,260.14 | £262.58/MWh | £144.94/MWh | +3.0% |
| C8 | 106,722 | 43,948 | 41.2% | £11,984.61 | £9,701.70 | £272.70/MWh | £154.55/MWh | +11.8% |
| C9 | 109,387 | 43,689 | 39.9% | £10,933.13 | £9,310.55 | £250.25/MWh | £141.72/MWh | +10.9% |

Total HH revenue: £63,708.34 vs flat equivalent £58,804.68 (+8.3% ToU premium)

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
| 2021 | 51 | 113% | C4g (2021-10-31) |
| 2022 | 68 | 1735% | C2_2 (2022-04-30) |
| 2023 | 49 | 2059% | C5_2 (2023-01-31) |
| 2024 | 37 | 107% | C_IC2 (2024-07-31) |
| 2025 | 22 | 80% | C7 (2025-06-07) |

Total: **487** bill shock events across 10 years

**Top 10 worst single-period bill spikes:**

| Date | Customer | Spike | Eventually Churned? |
|------|----------|-------|---------------------|
| 2023-01-31 | C5_2 | +2059% | no |
| 2022-04-30 | C2_2 | +1735% | no |
| 2022-10-31 | C4g | +134% | no |
| 2019-03-31 | C_IC1 | +130% | no |
| 2022-01-31 | C5 | +123% | yes |
| 2020-03-31 | C_IC2 | +118% | no |
| 2021-10-31 | C4g | +113% | no |
| 2022-01-31 | C_IC3 | +109% | no |
| 2024-07-31 | C_IC2 | +107% | no |
| 2023-06-30 | C_IC2 | +101% | no |

## Gas Renewal Pressure (Dual-Fuel Portfolio)

Company gas churn estimates at each gas leg renewal (Phase 14b).
Threshold for elevated risk: >20% company gas churn estimate.

| Year | Renewals | Mean Est | Max Est | Elevated Risk |
|------|----------|----------|---------|---------------|
| 2016 | 1 | 11% | 11% | 0 |
| 2017 | 4 | 16% | 23% | 2 ⚠ |
| 2018 | 4 | 17% | 23% | 2 ⚠ |
| 2019 | 4 | 0% | 0% | 0 |
| 2020 | 5 | 5% | 24% | 1 ⚠ |
| 2021 | 3 | 69% | 95% | 3 ⚠ |
| 2022 | 2 | 48% | 95% | 1 ⚠ |
| 2023 | 2 | 0% | 0% | 0 |
| 2024 | 1 | 1% | 1% | 0 |

**Top elevated gas renewals (>20% estimated churn):**

| Date | Customer | Old Rate (£/MWh) | New Rate (£/MWh) | Est Churn |
|------|----------|-----------------|-----------------|-----------|
| 2021-12-31 | C_IC3g | £20.1 | £123.8 (+517%) | 95% |
| 2022-09-30 | C4g | £35.0 | £95.0 (+171%) | 95% |
| 2021-09-30 | C4g | £16.1 | £35.0 (+118%) | 74% |
| 2021-03-31 | C2g | £21.7 | £35.0 (+62%) | 40% |
| 2020-12-31 | C_IC3g | £15.4 | £20.1 (+30%) | 24% |

## Retention Strategy P&L

### Aggregate (2016-2025)

| Metric | Value |
|--------|-------|
| Offers made | 12 |
| Retained | 12 (100%) |
| Churned despite offer | 0 |
| Total offer cost (foregone margin) | £236,164.03 |
| Margin saved (retained customers' terms) | £1,233,584.57 |
| Wasted offer cost (churned anyway) | £0.00 |
| **Net ROI of retention strategy** | **£997,420.54** |
| Acquisition cost avoided (retained customers) | £2,550.00 |
| **Full economic ROI (margin + acq savings)** | **£999,970.54** |

Missed opportunities (churns with no offer): **6** (£5,747.66 expected margin lost without offer)
- **Below threshold** (churn estimate under 30%): 6 (£5,747.66 margin lost) — Phase 13c bill burden signal reduces this for high-spend SME customers

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2018 | 1 | 1 | £24227.89 | £163704.65 | £139476.77 | £0.00 |
| 2019 | 2 | 2 | £25323.43 | £296612.44 | £271289.01 | £0.00 |
| 2020 | 1 | 1 | £6467.97 | £22900.05 | £16432.07 | £585.39 |
| 2021 | 4 | 4 | £106277.84 | £416501.51 | £310223.66 | £-178.13 |
| 2022 | 2 | 2 | £73492.71 | £327846.57 | £254353.86 | £2011.38 |
| 2023 | 2 | 2 | £374.19 | £6019.36 | £5645.17 | £0.00 |
| 2024 | 0 | 0 | £0.00 | £0.00 | £0.00 | £3329.02 |

### Per-Offer Detail

| Date | Customer | Est. churn | Discount | Offer Cost | Expected Margin | Acq Saved | Net | Outcome |
|------|----------|-----------|---------|-----------|----------------|-----------|-----|---------|
| 2018-01-31 | C_IC1 | 0.84 | 8% | £24227.89 | £163704.65 | £150 | £139476.77 | retained |
| 2019-01-31 | C_IC2 | 0.95 | 8% | £14841.81 | £101641.16 | £150 | £86799.35 | retained |
| 2019-03-02 | C_IC1 | 0.46 | 3% | £10481.62 | £194971.28 | £150 | £184489.66 | retained |
| 2020-12-31 | C_IC3 | 0.31 | 3% | £6467.97 | £22900.05 | £150 | £16432.07 | retained |
| 2021-03-31 | C_IC2 | 0.68 | 5% | £8850.68 | £91309.23 | £150 | £82458.56 | retained |
| 2021-04-30 | C_IC1 | 0.66 | 5% | £14077.11 | £158242.30 | £150 | £144165.19 | retained |
| 2021-12-30 | C5 | 0.83 | 8% | £509.78 | £2240.09 | £400 | £1730.31 | retained |
| 2021-12-31 | C_IC3 | 0.95 | 8% | £82840.28 | £164709.89 | £150 | £81869.61 | retained |
| 2022-04-30 | C_IC2 | 0.95 | 8% | £25114.25 | £96248.86 | £150 | £71134.61 | retained |
| 2022-05-30 | C_IC1 | 0.95 | 8% | £48378.45 | £231597.71 | £150 | £183219.25 | retained |
| 2023-03-31 | C6 | 0.49 | 3% | £229.94 | £3237.47 | £400 | £3007.53 | retained |
| 2023-12-30 | C5_2 | 0.32 | 3% | £144.25 | £2781.89 | £400 | £2637.64 | retained |

## Retention Durability

Post-retention survival: how long did retained customers stay before churning or reaching the simulation end?

| Customer | First retained | End of tenure | Post-retention months | Outcome |
|----------|---------------|--------------|----------------------|---------|
| C_IC1 | 2018-01-31 | (window end) | 95 | active |
| C_IC2 | 2019-01-31 | (window end) | 83 | active |
| C_IC3 | 2020-12-31 | (window end) | 60 | active |
| C5 | 2021-12-30 | 2022-12-30 | 12 | churned |
| C6 | 2023-03-31 | 2024-03-30 | 12 | churned |
| C5_2 | 2023-12-30 | (window end) | 24 | active |

**Eventually churned (2/6)**: C5, C6 — avg 12 months post-retention before final churn.
**Still active (4/6)**: C_IC1, C_IC2, C_IC3, C5_2 — survived to simulation end.

## Enterprise Value Analysis (Phase 22a)

**Full-history EV:** £8,087,302.19 — anchored to all 10 years including crisis losses
**3yr-trailing EV:** £700,587.57 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

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
| 2020 | £122,214.83 |
| 2021 | £66,746.46 |
| 2022 | £303,003.48 |
| 2023 | £131,845.43 | ← trailing
| 2024 | £337,194.05 | ← trailing
| 2025 | £116,621.95 | ← trailing

**CLV by billing account:**

| Account | Full-history CLV | 3yr-trailing CLV |
|---------|----------------:|----------------:|
| C1 | £4,898.21 | — |
| C2 | £6,944.28 | — |
| C2_2 | — | £1,241.81 |
| C3 | £7,451.08 | — |
| C4 | £4,194.50 | £-1,077.37 |
| C5 | £12,391.04 | — |
| C5_2 | — | £467.97 |
| C6 | £21,164.75 | £3,115.83 |
| C7 | £9,351.58 | £30.25 |
| C8 | £10,514.09 | £304.56 |
| C9 | £10,251.81 | £1,173.38 |
| C_IC1 | £1,846,699.19 | £413,300.07 |
| C_IC2 | £1,026,154.51 | £218,687.82 |
| C_IC3 | £3,309,102.77 | £53,069.46 |
| C_IC4 | £1,808,130.25 | £10,273.79 |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C2 | C2_2 | C3 | C4 | C5 | C5_2 | C6 | C7 | C8 | C9 | C_IC1 | C_IC2 | C_IC3 | C_IC4 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £6,228.45 | — | — | — | — | £14,109.80 | — | — | £10,200.00 | — | — | — | — | — | — |
| 2017 | £5,410.82 | £10,738.97 | — | £9,207.62 | £8,478.73 | £11,894.95 | — | £23,763.64 | £8,490.63 | £13,366.53 | £10,905.94 | — | — | — | — |
| 2018 | £5,600.28 | £9,078.04 | — | £8,930.17 | £7,414.78 | £11,521.58 | — | £19,884.32 | £8,460.10 | £11,877.30 | £10,261.59 | £2,879,139.19 | — | — | — |
| 2019 | £5,505.79 | £9,483.53 | — | £9,064.57 | £6,975.57 | £13,910.73 | — | £19,922.01 | £8,641.40 | £9,849.92 | £10,280.61 | £2,654,978.23 | £1,650,161.34 | — | — |
| 2020 | £5,848.48 | £7,950.91 | — | £8,072.18 | £6,824.11 | £10,518.32 | — | £18,914.03 | £9,763.37 | £9,858.32 | £9,713.68 | £1,576,265.01 | £837,234.64 | £2,659,040.22 | £1,534,392.97 |
| 2021 | £4,887.47 | £7,367.63 | — | £6,247.95 | £5,553.45 | £11,191.81 | — | £23,484.59 | £8,333.63 | £9,244.33 | £8,062.70 | £1,295,540.92 | £851,995.02 | £2,738,166.82 | £1,691,420.24 |
| 2022 | £4,394.39 | £6,200.81 | £939.08 | £5,935.80 | £3,381.15 | £12,309.64 | £7.13 | £19,803.98 | £6,004.58 | £7,721.44 | £9,354.39 | £1,286,271.35 | £820,608.72 | £2,639,400.54 | £1,287,454.00 |
| 2023 | £4,370.57 | £5,798.46 | £2,383.65 | £4,991.69 | £2,252.21 | £13,128.54 | £928.38 | £19,993.31 | £5,532.47 | £7,688.24 | £9,495.66 | £1,387,074.87 | £819,700.52 | £2,124,132.12 | £1,191,876.38 |
| 2024 | £4,503.71 | £4,686.91 | £2,966.09 | £4,871.42 | £3,295.44 | £10,452.79 | £2,987.03 | £16,599.24 | £5,957.33 | £7,915.19 | £8,233.32 | £1,409,766.99 | £664,180.47 | £2,166,612.23 | £1,186,971.47 |
| 2025 | £3,648.63 | £4,920.67 | £3,633.45 | £6,450.25 | £2,793.07 | £8,246.68 | £4,012.33 | £19,237.70 | £6,276.77 | £7,413.75 | £7,428.99 | £1,313,809.29 | £675,304.74 | £2,319,680.12 | £1,411,959.90 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £4,567.15, range £58.25–£26,368.63.

- C1: cost to serve £414.44, net margin after CTS £2,319.83
- C1g: cost to serve £64.75, net margin after CTS £1,475.88
- C2: cost to serve £432.22, net margin after CTS £2,978.09
- C2_2: cost to serve £381.60, net margin after CTS £5,115.36
- C2g: cost to serve £83.87, net margin after CTS £1,935.34
- C3: cost to serve £292.52, net margin after CTS £2,096.31
- C3g: cost to serve £58.25, net margin after CTS £1,240.28
- C4: cost to serve £565.38, net margin after CTS £2,749.41
- C4g: cost to serve £216.57, net margin after CTS £1,127.40
- C5: cost to serve £1,054.48, net margin after CTS £10,703.12
- C5_2: cost to serve £418.31, net margin after CTS £6,106.01
- C6: cost to serve £1,349.14, net margin after CTS £21,101.25
- C7: cost to serve £954.70, net margin after CTS £9,846.82
- C8: cost to serve £939.16, net margin after CTS £11,527.29
- C9: cost to serve £896.59, net margin after CTS £11,811.57
- C_IC1: cost to serve £19,836.09, net margin after CTS £1,854,821.05
- C_IC2: cost to serve £11,344.54, net margin after CTS £898,486.46
- C_IC3: cost to serve £26,368.63, net margin after CTS £1,798,804.30
- C_IC3g: cost to serve £9,229.97, net margin after CTS £613,417.06
- C_IC4: cost to serve £16,441.72, net margin after CTS £1,090,243.56


## Margin Recovery Surcharges (Phase 16c + 19a)

Company applied 27 recovery surcharge(s) at renewal based on prior-term losses (3 gas). Avg surcharge: 14.9%.

| Customer | Commodity | Term start | Prior margin | Prior revenue | Surcharge | Rate before | Rate after |
|----------|-----------|------------|-------------|--------------|-----------|------------|-----------|
| C_IC1 | electricity | 2018-01-31 | £-5,651.81 | £10,420.08 | +20.0% | £112.24/MWh | £152.31/MWh |
| C5 | electricity | 2018-12-31 | £-204.31 | £2,322.51 | +3.8% | £148.68/MWh | £153.39/MWh |
| C_IC2 | electricity | 2019-01-31 | £-3,283.71 | £6,187.80 | +20.0% | £134.57/MWh | £185.71/MWh |
| C_IC1 | electricity | 2019-03-02 | £-7,215.97 | £10,069.00 | +20.0% | £128.22/MWh | £175.80/MWh |
| C_IC2 | electricity | 2020-03-01 | £-3,915.21 | £3,421.95 | +20.0% | £92.92/MWh | £128.22/MWh |
| C_IC1 | electricity | 2020-03-31 | £-8,072.70 | £6,326.95 | +20.0% | £91.12/MWh | £103.88/MWh |
| C_IC2 | electricity | 2021-03-31 | £-4,097.33 | £5,726.15 | +20.0% | £138.90/MWh | £177.17/MWh |
| C_IC1 | electricity | 2021-04-30 | £-7,770.53 | £14,511.74 | +20.0% | £113.97/MWh | £141.62/MWh |
| C4g | gas | 2021-09-30 | £-75.14 | £687.61 | +5.9% | £53.99/MWh | £59.25/MWh |
| C5 | electricity | 2021-12-30 | £-339.41 | £2,699.34 | +7.6% | £311.83/MWh | £340.69/MWh |
| C7 | electricity | 2021-12-30 | £-122.68 | £1,986.24 | +1.2% | £311.83/MWh | £333.31/MWh |
| C_IC3 | electricity | 2021-12-31 | £-27,609.28 | £443,011.72 | +1.2% | £224.03/MWh | £260.80/MWh |
| C_IC2 | electricity | 2022-04-30 | £-2,287.21 | £17,661.75 | +8.0% | £269.81/MWh | £317.95/MWh |
| C_IC1 | electricity | 2022-05-30 | £-6,202.10 | £22,384.38 | +20.0% | £239.42/MWh | £308.66/MWh |
| C4 | electricity | 2022-09-30 | £-220.41 | £906.59 | +19.3% | £404.86/MWh | £484.82/MWh |
| C4g | gas | 2022-09-30 | £-901.21 | £1,040.11 | +20.0% | £183.79/MWh | £250.54/MWh |
| C7 | electricity | 2022-12-30 | £-1,829.78 | £2,404.50 | +20.0% | £266.73/MWh | £337.58/MWh |
| C8 | electricity | 2023-03-31 | £-481.87 | £3,898.74 | +7.4% | £319.17/MWh | £344.47/MWh |
| C_IC2 | electricity | 2023-05-30 | £-4,337.22 | £7,055.33 | +20.0% | £171.46/MWh | £236.61/MWh |
| C_IC1 | electricity | 2023-06-29 | £-8,734.92 | £17,979.18 | +20.0% | £163.19/MWh | £220.46/MWh |
| C4 | electricity | 2023-09-30 | £-277.33 | £1,324.46 | +15.9% | £216.77/MWh | £249.30/MWh |
| C4g | gas | 2023-09-30 | £-1,950.48 | £2,732.11 | +20.0% | £47.83/MWh | £66.00/MWh |
| C5_2 | electricity | 2023-12-30 | £-1,113.67 | £5,051.61 | +17.1% | £242.22/MWh | £269.33/MWh |
| C7 | electricity | 2023-12-30 | £-445.92 | £3,990.91 | +6.2% | £242.22/MWh | £244.32/MWh |
| C_IC3 | electricity | 2023-12-31 | £-124,836.88 | £971,625.50 | +7.8% | £118.95/MWh | £121.87/MWh |
| C_IC2 | electricity | 2024-06-28 | £-5,972.33 | £7,659.10 | +20.0% | £148.64/MWh | £205.12/MWh |
| C_IC1 | electricity | 2024-07-28 | £-10,717.78 | £14,454.77 | +20.0% | £154.38/MWh | £213.04/MWh |



## Portfolio Intelligence Pack (Phase AH)

Board-level synthesis of CRM and flexibility intelligence derived from observable operational data.

### 1. Retention Intelligence

- **Retention offers made:** 12
- **Offer acceptance rate:** 100% (12 retained / 0 churned despite offer)
- **Estimated margin protected:** £1,233,584.57
- **No-offer churns:** 6 total (0 blind miss / 0 deliberate pass)
- **Retention coverage rate:** 67% of at-risk renewals received an offer

### 2. Flexibility Revenue Intelligence

- No flexibility revenue data available.

### 3. Churn Pattern Analysis

- **Total lifetime churn events:** 6
- **Peak churn year:** 2022 (2 events)
- **Net book movement:** 2 acquisitions − 6 churns = -4
- **Portfolio trend:** shrinking

### 4. Board Recommendations

1. **Crisis-year churn:** 3 churn events in 2021–2022. Maintain minimum hedge floor pre-crisis to preserve pricing stability and limit bill-shock churn.

## CRM Intelligence: Risk Triage (Final Year)

Latest renewal record per account. Risk bands: CRITICAL>=50% | HIGH>=30% | MEDIUM>=15% | LOW<15%.

| Account | Seg | Risk Band | Sim Churn | Co. Est. | Rate vs SVT | Lifetime Margin |
|---------|-----|-----------|-----------|----------|-------------|-----------------|
| C_IC3 | I&C | HIGH | 41% | 11% | -53.9% [competitive] | £1,798,804.30 |
| C5 | SME | HIGH | 38% | 5% | -48.8% [competitive] | £10,703.12 |
| C2 | resi | HIGH | 38% | 7% | +46.6% [overpriced] | £2,978.09 |
| C4 | resi | HIGH | 38% | 5% | -9.0% | £2,749.41 |
| C8 | resi | HIGH | 32% | 5% | -23.6% [competitive] | £11,527.29 |
| C2_2 | resi | HIGH | 32% | 5% | +16.8% [overpriced] | £5,115.36 |
| C7 | resi | MEDIUM | 29% | 5% | -14.3% | £9,846.82 |
| C6 | SME | MEDIUM | 26% | 25% | -24.8% [competitive] | £21,101.25 |
| C9 | resi | MEDIUM | 17% | 5% | -14.3% | £11,811.57 |
| C1 | resi | LOW | 11% | 5% | -12.0% | £2,319.83 |
| C3 | resi | LOW | 11% | 5% | -39.0% [competitive] | £2,096.31 |
| C5_2 | SME | LOW | 8% | 5% | +3.3% | £6,106.01 |
| C_IC1 | I&C | LOW | 5% | 84% | -0.1% | £1,854,821.05 |
| C_IC2 | I&C | LOW | 5% | 95% | +12.4% [overpriced] | £898,486.46 |

**Risk Band Summary (latest renewal):**
- CRITICAL (>=50%): 0 accounts
- HIGH (>=30%): 6 accounts
- MEDIUM (>=15%): 3 accounts
- LOW (<15%): 5 accounts
- Lifetime margin at risk (CRITICAL+HIGH): £1,831,877.56
- Overpriced vs SVT within HIGH/CRITICAL band: 2 account(s) -- rate shock risk compounds churn probability

**Company blind spot:** 5 HIGH/CRITICAL account(s) where company churn estimate was <10%.
  - C5: sim 38%, company est 5%
  - C2: sim 38%, company est 7%
  - C4: sim 38%, company est 5%
  - C8: sim 32%, company est 5%
  - C2_2: sim 32%, company est 5%

## Churn Root Cause Attribution

Per-churned-account analysis: pricing journey, rate-vs-SVT positioning, and company vs SIM churn estimate at the point of departure.

| Account | Seg | Churn Date | Tenure | Last Rate Shock | Rate vs SVT | Sim Risk | Co. Est. | Margin Lost |
|---------|-----|------------|--------|-----------------|-------------|----------|----------|-------------|
| C3 | resi | 2020-06-30 | 4.0yr | -4.3% | -39.0% | 11% | 5% | £2,096.31 |
| C1 | resi | 2021-12-30 | 6.0yr | +1.6% | -12.0% | 11% | 5% | £2,319.83 |
| C2 | resi | 2022-03-31 | 6.0yr | +12.3% | +46.6% | 38% | 7% | £2,978.09 |
| C5 | SME | 2022-12-30 | 7.0yr | -0.5% | -48.8% | 38% | 5% | £10,703.12 |
| C6 | SME | 2024-03-30 | 8.0yr | -0.8% | -24.8% | 26% | 25% | £21,101.25 |
| C4 | resi | 2024-09-29 | 8.0yr | +3.8% | -9.0% | 38% | 5% | £2,749.41 |

**Root Cause Summary:**
- Total churned accounts: 6
- Lifetime margin lost: £41,948.01
- Average tenure at departure: 6.5 years
- Company blind misses (sim >=30%, co. est. <10%): 3 -- C2, C5, C4
- Company-warned churns (co. est. >=20%): 1 -- C6
- Crisis-era churns (2021-22): 3 -- absolute crisis price level, not rate-change delta, was the driver
- Overpriced vs SVT at departure: 1 account(s) -- rate shock risk was observable but unactioned

## Counterfactual Retention Value

What would company-initiated retention offers have been worth for the 6 accounts that churned without an offer? Calibrated from 12 actual offers (observed retention rate 100%).

| Account | Seg | Churn Date | Co. Est. | Term Margin | Disc Rate | Retention Cost | CF Net Benefit | Assessment |
|---------|-----|------------|----------|-------------|-----------|----------------|----------------|------------|
| C3 | resi | 2020-06-30 | 5% | £585.39 | 5% | £29.27 | £556.12 | MISSED OPP. |
| C1 | resi | 2021-12-30 | 5% | £-178.13 | 5% | £0.00 | n/a | CORRECT PASS |
| C2 | resi | 2022-03-31 | 7% | £236.63 | 5% | £11.83 | £224.80 | MISSED OPP. |
| C5 | SME | 2022-12-30 | 5% | £1,774.75 | 8% | £141.98 | £1,632.77 | MISSED OPP. |
| C6 | SME | 2024-03-30 | 25% | £2,860.15 | 8% | £228.81 | £2,631.34 | MISSED OPP. |
| C4 | resi | 2024-09-29 | 5% | £468.87 | 5% | £23.44 | £445.43 | MISSED OPP. |

**Counterfactual Summary:**
- No-offer churns assessed: 6
- Correct no-offer (net-neg ETM): 1 (C1)
- Missed opportunities (positive ETM, below detection): 5
- Total term margin foregone: £5,925.79
- Total retention cost (counterfactual): £435.34
- Net counterfactual benefit: £5,490.45 (at 100% retention probability)
- Root cause: company churn detection below threshold for all missed cases -- churn model underestimated bill-shock risk

## Pricing Basis Risk Attribution

Forward curve accuracy at each contract term. tariff_error_pct = (company_fwd - sim_fwd) / sim_fwd: positive = company over-estimated costs (higher than market); negative = company under-estimated (margin-at-risk).
Portfolio-wide mean error: +6.1%

| Year | Contracts | Mean Error | Max Abs | Over-priced | Under-priced | Assessment |
|------|-----------|------------|---------|-------------|--------------|------------|
| 2016 | 17 | +8.9% | 29.1% | 9 | 4 | moderate over |
| 2017 | 14 | +5.4% | 46.6% | 8 | 5 | moderate over |
| 2018 | 16 | -2.9% | 27.7% | 6 | 8 | on target |
| 2019 | 19 | +8.3% | 37.2% | 9 | 3 | moderate over |
| 2020 | 22 | +0.7% | 33.8% | 10 | 7 | on target |
| 2021 | 17 | +8.5% | 44.5% | 6 | 3 | moderate over |
| 2022 | 17 | -2.1% | 23.2% | 7 | 5 | on target |
| 2023 | 15 | +19.8% | 40.0% | 10 | 1 | HIGH OVER-PRICE |
| 2024 | 14 | +7.9% | 22.6% | 8 | 1 | moderate over |
| 2025 | 2 | +33.1% | 33.1% | 2 | 0 | HIGH OVER-PRICE |

**Basis Risk Summary:**
- Portfolio mean tariff error: +6.1%
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
| 2021 | £5,208 | £4,340 | 0.30% |
| 2022 | £10,209 | £8,507 | 0.30% |
| 2023 | £6,744 | £5,620 | 0.26% |
| 2024 | £3,194 | £2,661 | 0.15% |
| 2025 | £4,666 | £3,888 | 0.48% << |

<< BSC credit above 0.4% of revenue (elevated operational cash tie-up)

**Peak BSC credit requirement:** 2022 at £10,209 (portfolio growth and 2021-22 price surge)
## Operational Unit Economics

Revenue, gross margin, and net margin per active customer account. The dramatic rise in 2022-23 reflects wholesale price crisis inflating all revenue and cost metrics simultaneously.

| Year | Active | Rev/cust | Gross/cust | Net/cust | Net % |
|------|--------|----------|------------|----------|-------|
| 2016 | 13 | £801 | £524 | £91 | 11.3% |
| 2017 | 14 | £16,735 | £8,803 | £2,183 | 13.0% |
| 2018 | 15 | £29,022 | £17,502 | £6,647 | 22.9% |
| 2019 | 17 | £70,486 | £41,296 | £13,404 | 19.0% |
| 2020 | 18 | £67,965 | £43,989 | £6,790 | 10.0% |
| 2021 | 16 | £108,594 | £47,791 | £4,172 | 3.8% << |
| 2022 | 16 | £215,070 | £65,673 | £18,938 | 8.8% |
| 2023 | 13 | £199,793 | £73,608 | £10,142 | 5.1% |
| 2024 | 13 | £168,617 | £96,955 | £25,938 | 15.4% |
| 2025 | 10 | £97,254 | £52,011 | £11,662 | 12.0% |

<< Net margin below 5% (below Ofgem FRA comfort threshold)

**Best year per customer:** 2024 at £25,938 net/customer
**Worst year per customer:** 2016 at £91 net/customer
## Customer Lifetime P&L by Commodity

Lifetime net margin per customer, split by electricity and gas. Loss-making accounts (marked *) warrant repricing review or exit.

| Customer | Elec net | Gas net | Total |
|----------|----------|---------|-------|
| C1 | £423 | — | £423 |
| C1g | — | £643 | £643 |
| C2 | £690 | — | £690 |
| C2_2 | £1,068 | — | £1,068 |
| C2g | — | £802 | £802 |
| C3 | £206 | — | £206 |
| C3g | — | £283 | £283 |
| C4 | £139 | — | £139 |
| C4g | — | £-2,030 | £-2,030 * |
| C5 | £81 | — | £81 |
| C5_2 | £384 | — | £384 |
| C6 | £3,579 | — | £3,579 |
| C7 | £-1,458 | — | £-1,458 * |
| C8 | £1,268 | — | £1,268 |
| C9 | £1,493 | — | £1,493 |
| C_IC1 | £828,201 | — | £828,201 |
| C_IC2 | £426,672 | — | £426,672 |
| C_IC3 | £107,507 | — | £107,507 |
| C_IC3g | — | £52,416 | £52,416 |
| C_IC4 | £14,584 | — | £14,584 |
| **Total** | **£1,384,836** | **£52,113** | **£1,436,949** |

Loss-making accounts: C4g (£-2,030), C7 (£-1,458)
Gas loss-making: C4g (£-2,030)
Gas portfolio net: £52,113 (3.6% of total)

## Hedge Value-Add Analysis

Actual hedged net margin vs hypothetical spot-only (naked) net margin. Negative value-add indicates forward prices exceeded spot outturn — consistent with UK market backwardation in 2016-2021 and partial hedging in the crisis years.

| Year | Actual net | Naked net | Hedge value-add |
|------|-----------|-----------|-----------------|
| 2016 | £2,034 | £10,920 | £-8,885 |
| 2017 | £30,081 | £112,495 | £-82,414 |
| 2018 | £109,583 | £246,455 | £-136,872 |
| 2019 | £252,590 | £836,842 | £-584,252 |
| 2020 | £85,198 | £963,111 | £-877,913 |
| 2021 | £191,444 | £457,552 | £-266,107 |
| 2022 | £184,272 | £1,208,910 | £-1,024,637 |
| 2023 | £381,883 | £1,222,570 | £-840,687 |
| 2024 | £199,801 | £605,667 | £-405,865 |
| 2025 | £63 | £346 | £-283 |
| **Total** | **£1,436,949** | **£5,664,871** | **£-4,227,921** |

Largest hedging cost: **2022** (£1,024,637 vs naked)
Smallest hedging cost: **2025** (£283 vs naked)
Conclusion: systematic forward hedging cost £4,227,921 over 10 years vs spot purchasing.

## Customer Service Quality

Ofgem benchmarks: bill clarity >0.82 (GREEN) / >0.80 (AMBER) / ≤0.80 (RED); complaint probability <5% (GREEN) / <6% (RED); bill shock <0.20% (GREEN) / <0.30% (AMBER) / ≥0.30% (RED).

| Year | Clarity | Complaint% | Shock% | Shock events | Bills | RAG |
|------|---------|------------|--------|--------------|-------|-----|
| 2016 | 0.829 G | 4.7% | 0.20% | 31 | 108 | GREEN |
| 2017 | 0.818 A | 4.7% | 0.17% | 50 | 168 | AMBER |
| 2018 | 0.810 A | 4.7% | 0.16% | 60 | 180 | AMBER |
| 2019 | 0.824 G | 4.7% | 0.17% | 66 | 204 | GREEN |
| 2020 | 0.830 G | 4.3% | 0.14% | 53 | 204 | GREEN |
| 2021 | 0.829 G | 4.5% | 0.16% | 51 | 192 | GREEN |
| 2022 | 0.790 R | 5.6% | 0.33% | 68 | 161 | RED ! |
| 2023 | 0.805 A | 4.9% | 0.30% | 49 | 156 | RED ! |
| 2024 | 0.812 A | 4.7% | 0.16% | 37 | 141 | AMBER |
| 2025 | 0.775 R | 5.9% | 0.24% | 22 | 60 | RED ! |

Worst clarity year: **2025** (0.775)
Highest complaint probability: **2025** (5.9%)
Worst bill shock: **2022** (0.33%)
RED years: 2022, 2023, 2025
AMBER years: 2017, 2018, 2024
Trend (last 2 years): DECLINING

## Portfolio VaR Trajectory and Treasury Evolution

Annual VaR ratio (committee trigger = 3.0) and year-end treasury balance.

| Year | VaR Ratio | Status | Treasury £ | Net Margin £ |
|------|-----------|--------|-----------|-------------|
| 2016 | 3.25 | ALERT | £2,467,424 | £1,178 |
| 2017 | 2.69 | WATCH | £2,497,718 | £30,566 |
| 2018 | — | — | £2,486,407 | £99,706 |
| 2019 | — | — | £2,606,406 | £227,872 |
| 2020 | — | — | £2,914,253 | £122,215 |
| 2021 | — | — | £2,942,148 | £66,746 |
| 2022 | 2.70 | WATCH | £3,137,595 | £303,003 |
| 2023 | 2.73 | WATCH | £3,322,341 | £131,845 |
| 2024 | — | — | £3,703,825 | £337,194 |
| 2025 | — | — | £3,753,752 | £116,622 |

**Peak VaR year: 2016 (ratio 3.25)**
**Treasury peak: 2025 (£3,753,752)**
**Treasury growth: £2,467,424 → £3,753,752 (+£1,286,328)**

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
| C3 | 2020-06 | 5.0% | £585 | below threshold |
| C1 | 2021-12 | 5.0% | -£178 | below threshold |
| C2 | 2022-03 | 6.7% | £237 | below threshold |
| C5 | 2022-12 | 5.0% | £1,775 | below threshold |
| C6 | 2024-03 | 24.6% | £2,860 | below threshold ⚑ |
| C4 | 2024-09 | 5.0% | £469 | below threshold |

**High-risk no-offer events (≥10% churn): 1** — £2,860 margin at risk.

### Gas Renewal Risk — High-Churn Reprice Events (≥15% estimate)

| Customer | Term Start | Old Rate p/therm | New Rate p/therm | Churn Est |
|----------|-----------|-----------------|-----------------|----------|
| C2g | 2017-04 | 26.92 | 32.81 | 20.1% |
| C1g | 2017-12 | 26.25 | 33.49 | 22.6% |
| C3g | 2018-07 | 23.11 | 28.80 | 20.8% |
| C4g | 2018-10 | 26.10 | 33.61 | 23.3% |
| C_IC3g | 2020-12 | 15.44 | 20.08 | 24.0% |
| C2g | 2021-03 | 21.66 | 35.00 | 39.9% |
| C4g | 2021-09 | 16.09 | 35.00 | 73.5% |
| C_IC3g | 2021-12 | 20.08 | 123.80 | 95.0% |

**High-risk gas reprices: 9**

> ⚑ = customers with ≥15% churn estimate who received no retention offer.

## Retention Decision Economics

Per-offer cost, expected margin protected, and ROI for each retention intervention.

| Customer | Period | Retention Cost £ | Margin Protected £ | ROI | Discount % | Outcome |
|----------|--------|-----------------|-------------------|-----|------------|---------|
| C_IC1 | 2018-01 | £24,228 | £163,705 | 6.8× | 8% | retained |
| C_IC2 | 2019-01 | £14,842 | £101,641 | 6.8× | 8% | retained |
| C_IC1 | 2019-03 | £10,482 | £194,971 | 18.6× | 3% | retained |
| C_IC3 | 2020-12 | £6,468 | £22,900 | 3.5× | 3% | retained |
| C_IC2 | 2021-03 | £8,851 | £91,309 | 10.3× | 5% | retained |
| C_IC1 | 2021-04 | £14,077 | £158,242 | 11.2× | 5% | retained |
| C5 | 2021-12 | £510 | £2,240 | 4.4× | 8% | retained |
| C_IC3 | 2021-12 | £82,840 | £164,710 | 2.0× | 8% | retained |
| C_IC2 | 2022-04 | £25,114 | £96,249 | 3.8× | 8% | retained |
| C_IC1 | 2022-05 | £48,378 | £231,598 | 4.8× | 8% | retained |
| C6 | 2023-03 | £230 | £3,237 | 14.1× | 3% | retained |
| C5_2 | 2023-12 | £144 | £2,782 | 19.3× | 3% | retained |

**Total retention spend: £236,164** | **Total margin protected: £1,233,585**
**Portfolio retention ROI: 5.2×** | **Retained: 12/12**
**Best ROI intervention: C5_2 2023-12 (19.3×)**

> ROI = expected remaining-term margin ÷ retention cost (discount given).
> Churn probability weighted; 95% churn estimate used for I&C renewal trigger.

## Gas Exit Decision Analysis

Three-scenario P&L impact for the board (dual-fuel portfolio lifetime figures).

| Scenario | Net Margin £ | vs Status Quo |
|----------|-------------|--------------|
| Status Quo (hold gas) | £161,077 | — |
| Exit Gas (with churn risk) | £65,670 | -£95,407 |
| Reprice to Breakeven | £163,107 | +£2,030 |

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
| 2020 | 81.8% | 0.0% | 96.0% | 1 | 15 |
| 2021 | 84.4% | 0.0% | 97.0% | 1 | 13 |
| 2022 | 86.4% | 0.0% | 97.4% | 1 | 12 |
| 2023 | 83.7% | 0.0% | 96.1% | 1 | 12 |
| 2024 | 80.1% | 0.0% | 94.4% | 1 | 9 |
| 2025 | 87.2% | 85.0% | 89.4% | — | 2 |

**Lowest portfolio hedge fraction: 2024 (80.1%)** — risk erosion from regime-change blindness.
**Naked positions first appear in 2019** — unhedged accounts expose portfolio to spot price swings.

> Regime-change blindness: the sim converged toward lower hedging during calm 2016-2020,
> mirroring the strategy that destroyed real UK suppliers entering the 2021-22 crisis.

## Risk Committee Intervention Pattern

Annual risk committee wake-ups (triggered when portfolio VaR exceeds threshold).

| Year | Wake-ups | Customer Adjustments | Avg Customers/Event | Max VaR Stressed £ |
|------|----------|---------------------|--------------------|--------------------|
| 2016 | 13 | 13 | 1.0 | £9 |
| 2017 | 12 | 33 | 2.8 | £401 |
| 2022 | 9 | 62 | 6.9 | £20,663 |
| 2023 | 4 | 36 | 9.0 | £49,007 |

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
| 2020 | £2,375 | £56,550 | — | £69,454 | £47,215 |
| 2021 | £5,208 | £49,645 | £41,404 | £71,336 | £50,441 |
| 2022 | £10,209 | £36,712 | £99,560 | £71,047 | £54,433 |
| 2023 | £6,744 | £51,008 | £13,763 | £71,831 | £79,700 |
| 2024 | £3,194 | £68,765 | £2,000 | £72,944 | £76,429 |
| 2025 | £4,666 | £31,057 | £854 | £31,221 | £31,816 |

**Peak BSC credit obligation: 2022 (£10,209)** — driven by portfolio volume growth and crisis price levels.
**Mutualization levy first appeared in 2016** — reflects supplier failure costs passed to remaining suppliers via BSC.

> BSC credit = Elexon-mandated deposit against settlement exposure. Scales with volume × price.
> Mutualization = recoverable defaults from failed suppliers in settlement.

## Customer Cohort Revenue Analysis

Lifetime P&L by year-of-acquisition cohort (all years to simulation end).

| Cohort | Customers | Total Revenue £ | Gross Margin £ | Net Margin £ | Rev/Customer £ |
|--------|-----------|----------------|---------------|-------------|----------------|
| 2016 | 15 | £186,004 | £100,256 | £7,570 | £12,400 |
| 2017 | 1 | £3,123,595 | £1,874,657 | £828,201 | £3,123,595 |
| 2018 | 1 | £1,525,272 | £909,831 | £426,672 | £1,525,272 |
| 2019 | 2 | £6,462,641 | £2,447,820 | £159,923 | £3,231,320 |
| 2020 | 1 | £2,744,639 | £1,106,685 | £14,584 | £2,744,639 |

**Best revenue/customer cohort: 2019 (£3,231,320/customer)**
**Best net margin cohort: 2017 (£828,201)**

> Note: Gas customer legs excluded from electricity metrics; cohort = year of first contract.

## CfD Levy, Bad Debt & Treasury Drawdowns

Contracts for Difference levy (negative = credit to supplier in high-price periods).

| Year | CfD Levy £ | RO Levy £ | Bad Debt £ | Treasury Drawdowns | Bills |
|------|-----------|----------|-----------|-------------------|-------|
| 2016 | +£7 | £1,162 | £167 | — | 108 |
| 2017 | +£2,707 | £37,159 | £1,375 | — | 168 |
| 2018 | +£9,875 | £65,510 | £2,385 | — | 180 |
| 2019 | +£28,353 | £164,625 | £6,207 | — | 204 |
| 2020 | +£35,391 | £238,636 | £6,295 | — | 204 |
| 2021 | +£15,001 | £246,565 | £9,125 | — | 192 |
| 2022 | -£49,780 CREDIT | £256,427 | £35,785 | 1 | 161 |
| 2023 | +£64,827 | £272,110 | £14,209 | 47 | 156 |
| 2024 | +£110,026 | £307,883 | £11,463 | 4271 | 141 |
| 2025 | +£46,991 | £135,847 | £4,989 | — | 60 |

**CfD turned CREDIT in 2022: -£49,780 (high wholesale → CfD generators repay system)**
**Treasury drawdown years: 2022, 2023, 2024** (credit facility used)
**Peak bad debt year: 2022 (£35,785)**

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
| 2020 | £5,681 | £1,210 | £4,236 | £704,698 | £75,972 | £791,796 |
| 2021 | £5,364 | £537 | £4,502 | £672,004 | £82,255 | £764,661 |
| 2022 | £3,756 | -£762 | £6,118 | £950,531 | £91,118 | £1,050,761 |
| 2023 | £7,209 | -£575 | £5,799 | £822,951 | £121,515 | £956,898 |
| 2024 | £8,571 | £762 | £5,142 | £1,122,285 | £123,652 | £1,260,411 |
| 2025 | £3,636 | £0 | £1,550 | £461,417 | £53,509 | £520,112 |

**Best gross margin year: 2024 (£1,260,411)** | **Worst: 2016 (£6,814)**
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
| 2020 | 10 | -30.0% | 0/10 | -68.7% | +-18.0% |
| 2021 | 9 | +9.1% | 5/9 | -12.0% | +63.8% |
| 2022 | 8 | +4.3% | 4/8 | -64.0% | +95.6% |
| 2023 | 8 | -32.8% | 0/8 | -60.5% | +-1.7% |
| 2024 | 8 | -20.5% | 1/8 | -53.9% | +3.3% |
| 2025 | 2 | -3.4% | 1/2 | -23.6% | +16.8% |

**Best headroom year: 2023 (avg 32.8% below SVT)**
**Largest above-SVT year: 2021** (5/9 terms above — note: I&C customers exempt from SVT cap)

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
| 2021 | £2,942,148 | AMBER | AMBER | GREEN | AMBER | RED |
| 2022 | £3,137,595 | AMBER | AMBER | GREEN | AMBER | RED |
| 2023 | £3,322,341 | AMBER | AMBER | GREEN | AMBER | RED |
| 2024 | £3,703,825 | AMBER | AMBER | GREEN | AMBER | RED |
| 2025 | £3,753,752 | AMBER | AMBER | GREEN | AMBER | RED |

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
| 2020 | 18 | 40.5% | £103,171 | £44,089 | 2.06% |
| 2021 | 16 | 29.5% | £151,220 | £47,891 | 1.95% |
| 2022 | 16 | 22.5% | £265,265 | £65,763 | 1.98% |
| 2023 | 13 | 25.1% | £267,411 | £73,703 | 2.20% |
| 2024 | 13 | 39.5% | £231,040 | £96,993 | 2.14% |
| 2025 | 10 | 38.9% | £123,010 | £52,058 | 2.98% |

**Best EBIT%: 2016 (45.2%)** | **Worst EBIT%: 2022 (22.5%)**
**Peak revenue/customer: 2023 (£267,411)**

> Note: Revenue/customer driven by customer mix (I&C customers 10-100× resi volumes).

## Plausibility vs Industry

Key metrics vs UK retail energy norms (Ofgem/Cornwall Insight). OK = within range | ~ = amber | ! = outside expected range.

| Year | Net margin% | Gross margin% | Bad debt% | Churn% |
|------|-------------|---------------|-----------|--------|
| 2016 | !45.2% | !51.2% | OK1.53% | ~0% |
| 2017 | !33.5% | !35.8% | OK1.80% | ~0% |
| 2018 | !41.6% | !44.0% | OK1.97% | ~0% |
| 2019 | !40.7% | !42.8% | OK1.87% | ~0% |
| 2020 | !40.5% | !42.7% | OK2.06% | OK6% |
| 2021 | !29.5% | !31.7% | OK1.95% | OK6% |
| 2022 | !22.5% | ~24.8% | OK1.98% | OK12% |
| 2023 | !25.1% | ~27.6% | OK2.20% | ~0% |
| 2024 | !39.5% | !42.0% | OK2.14% | OK15% |
| 2025 | !38.9% | !42.3% | OK2.98% | ~0% |

**Benchmark ranges:** Net margin %: −5 to +8% green | Gross margin %: 0–20% green | Bad debt %: 0–5% green | Annual churn %: 3–35% green.
**RED — review required: 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025**

## Churn Prediction Calibration

How well the company estimated churn probability versus actual simulation outcomes.

| Customer | Date | Sim Probability | Company Estimate | Delta | Verdict |
|----------|------|----------------|-----------------|-------|---------|
| C3 | 2020-06 | 11.0% | 5.0% | -6.0pp | ACCURATE |
| C1 | 2021-12 | 11.0% | 5.0% | -6.0pp | ACCURATE |
| C2 | 2022-03 | 38.0% | 6.7% | -31.3pp | UNDERESTIMATED |
| C5 | 2022-12 | 38.0% | 5.0% | -33.0pp | UNDERESTIMATED |
| C6 | 2024-03 | 26.0% | 24.6% | -1.4pp | ACCURATE |
| C4 | 2024-09 | 38.0% | 5.0% | -33.0pp | UNDERESTIMATED |

**Outcomes: 3 underestimated / 3 accurate / 0 overestimated**
**Mean absolute error: 18.4pp**
**Systematic bias: company consistently UNDER-predicted churn risk.**

> Company churn estimates derived from company-observable signals (bill shock,
> margin feedback, renewal history) without access to the simulation's internal
> churn parameters — epistemic gap is expected and realistic for a small supplier.

## Counterfactual Retention & Threshold Optimisation

**Current threshold:** 30% | F1=0.000
**Optimal threshold:** 0% | F1=0.185

**RAG [!]:** RED — 5 unrecoverable high-value miss(es) — model underestimates churn: optimal threshold below current

**Missed retention opportunities:** 6 no-offer churns
  Value at stake: £5,748
  Counterfactually recoverable (with offer): 0/6
  Net value recoverable (after offer cost): £0

### Per-miss detail

| Year | Customer | Est | SIM p | Recoverable? | Margin | Net value |
|------|----------|-----|-------|-------------|--------|----------|
| 2020 | C3 | 5% | 11% | No | £585 | £-50 |
| 2021 | C1 | 5% | 11% | No | £-178 | £-50 |
| 2022 | C2 | 7% | 38% | No | £237 | £-50 |
| 2022 | C5 | 5% | 38% | No | £1,775 | £-50 |
| 2024 | C6 | 25% | 26% | No | £2,860 | £-50 |
| 2024 | C4 | 5% | 38% | No | £469 | £-50 |

### Threshold sensitivity curve

| Threshold | Recall | Precision | F1 |
|-----------|--------|-----------|----|
| 0% | 1.000 | 0.102 | 0.185 ← optimal |
| 5% | 1.000 | 0.102 | 0.185 |
| 10% | 0.167 | 0.059 | 0.087 |
| 15% | 0.167 | 0.091 | 0.118 |
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
| False Positives (FP) | 7 | Churn predicted BUT customer renewed |
| False Negatives (FN) | 6 | Churn NOT predicted BUT happened (blind miss) |
| True Negatives (TN) | 46 | No churn predicted AND customer renewed |
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
| 2018 | 0 | 1 | 0 | 3 | 0% | 0% |
| 2019 | 0 | 1 | 0 | 3 | 0% | 0% |
| 2020 | 0 | 1 | 1 | 8 | 0% | 0% |
| 2021 | 0 | 2 | 1 | 6 | 0% | 0% |
| 2022 | 0 | 0 | 2 | 6 | 0% | 0% |
| 2023 | 0 | 2 | 0 | 6 | 0% | 0% |
| 2024 | 0 | 0 | 2 | 6 | 0% | 0% |
| 2025 | 0 | 0 | 0 | 2 | 0% | 0% |

## Credit Risk & Capital Stress (Phase NR)

**Ofgem FRA stress multiplier:** 2.5x (empirical: 2021-22 crisis, industry bad debt 1% → 2.5% revenue)

| Year | Revenue £ | Bad Debt £ | Bad Debt % | Crisis Stress £ |
|------|-----------|------------|------------|-----------------|

**Total bad debt (all years):** £91,999
**Crisis stress incremental:** £137,999

**RAG [~]:** AMBER — Credit stress material but below 1% revenue

## Tariff Estimation Accuracy

Mean and maximum absolute error between company tariff estimates and actual outturn.

| Year | Observations | Mean Abs Error | Max Abs Error | Accuracy |
|------|-------------|---------------|--------------|----------|
| 2016 | 17 | 15.1% | 29.1% | POOR |
| 2017 | 14 | 16.6% | 46.6% | POOR |
| 2018 | 16 | 12.1% | 27.7% | MODERATE |
| 2019 | 19 | 11.0% | 37.2% | MODERATE |
| 2020 | 22 | 12.5% | 33.8% | MODERATE |
| 2021 | 17 | 14.5% | 44.5% | MODERATE |
| 2022 | 17 | 11.8% | 23.2% | MODERATE |
| 2023 | 15 | 21.3% | 40.0% | POOR |
| 2024 | 14 | 10.3% | 22.6% | MODERATE |
| 2025 | 2 | 33.1% | 33.1% | POOR |

**Best accuracy year (n≥5): 2024 (10.3% mean error)**
**Worst accuracy year (n≥5): 2023 (21.3% mean error)**

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
| 2020 | 18 | +3.3 | 9 | 9 | 2 |
| 2021 | 14 | +12.2 | 14 | 0 | 6 |
| 2022 | 12 | +17.9 | 11 | 1 | 5 |
| 2023 | 12 | +7.7 | 8 | 4 | 8 |
| 2024 | 11 | +6.5 | 6 | 5 | 2 |
| 2025 | 2 | +3.7 | 2 | 0 | 0 |

**Total adjustments 2016-2025: 115** | **Peak avg adjustment: 2022 (+17.9 £/MWh)**
**Emergency reprices: 27 total** (8 in 2023)

> Emergency reprices triggered when recent margin dropped below cost floor.
> Normal adjustments from rolling margin feedback; £/MWh delta versus prior contracted rate.

## Portfolio CLV Evolution

Estimated forward lifetime value of active billing accounts at each year-end.

| Year | Accounts | Total CLV £ | Avg CLV £ | Δ CLV £ |
|------|----------|-------------|-----------|---------|
| 2016 | 3 | £30,538 | £10,179 | — |
| 2017 | 9 | £102,258 | £11,362 | +£71,720 |
| 2018 | 10 | £2,972,167 | £297,217 | +£2,869,910 |
| 2019 | 11 | £4,398,774 | £399,889 | +£1,426,606 |
| 2020 | 13 | £6,694,396 | £514,954 | +£2,295,623 |
| 2021 | 13 | £6,661,497 | £512,423 | £-32,900 |
| 2022 | 15 | £6,109,787 | £407,319 | £-551,710 |
| 2023 | 15 | £5,599,347 | £373,290 | £-510,440 |
| 2024 | 15 | £5,500,000 | £366,667 | £-99,347 |
| 2025 | 15 | £5,794,816 | £386,321 | +£294,817 |

**Peak portfolio CLV: 2020 (£6,694,396)** | **Earliest/lowest: 2016 (£30,538)**
**Largest YoY gain: 2018 (+£2,869,910)**
**Largest YoY fall: 2022 (£-551,710)**

> Note: CLV snapshots are forward estimates at year-end based on remaining contract tenure and expected margins at that point in time.

## Gross Margin Bridge (Year-over-Year Attribution)

Annual change in gross margin decomposed into revenue and cost drivers.

| Year | Revenue £ | Wholesale £ | Non-Commodity £ | Gross Margin £ | GM% | ΔRevenue £ | ΔWholesale £ | ΔNon-Comm £ | ΔGM £ |
|------|-----------|-------------|-----------------|----------------|-----|------------|--------------|-------------|-------|
| 2016 | £15,354.61 | £3,596.53 | £3,892.24 | £7,865.84 | 51.2% | — | — | — | — |
| 2017 | £348,630.52 | £111,056.98 | £112,782.23 | £124,791.30 | 35.8% | +£333,275.90 | +£107,460.46 | +£108,889.99 | +£116,925.46 |
| 2018 | £600,953.01 | £172,802.28 | £163,976.80 | £264,173.93 | 44.0% | +£252,322.49 | +£61,745.30 | +£51,194.57 | +£139,382.63 |
| 2019 | £1,645,452.10 | £496,239.95 | £445,337.04 | £703,875.12 | 42.8% | +£1,044,499.09 | +£323,437.66 | +£281,360.24 | +£439,701.19 |
| 2020 | £1,857,080.58 | £431,625.18 | £631,858.33 | £793,597.07 | 42.7% | +£211,628.48 | £-64,614.77 | +£186,521.29 | +£89,721.95 |
| 2021 | £2,419,523.89 | £973,000.60 | £680,260.90 | £766,262.39 | 31.7% | +£562,443.31 | +£541,375.42 | +£48,402.57 | £-27,334.68 |
| 2022 | £4,244,235.13 | £2,390,418.55 | £801,612.92 | £1,052,203.66 | 24.8% | +£1,824,711.24 | +£1,417,417.95 | +£121,352.02 | +£285,941.27 |
| 2023 | £3,476,339.14 | £1,640,650.78 | £877,552.25 | £958,136.11 | 27.6% | £-767,895.99 | £-749,767.77 | +£75,939.33 | £-94,067.55 |
| 2024 | £3,003,518.02 | £932,392.51 | £810,222.09 | £1,260,903.42 | 42.0% | £-472,821.12 | £-708,258.27 | £-67,330.16 | +£302,767.32 |
| 2025 | £1,230,103.68 | £452,432.70 | £257,088.30 | £520,582.67 | 42.3% | £-1,773,414.35 | £-479,959.81 | £-553,133.80 | £-740,320.75 |

**Best GM year: 2016 (51.2%)** | **Worst GM year: 2022 (24.8%)**

> Note: Non-commodity costs include network (DUoS/TNUoS), policy levies (RO/CfD/CCL/CM/FiT), and mutualization.

## Risk Committee Activity (2016-2025)

Committee wake-up sessions: triggered when VaR stress ratio exceeds mandate threshold.

| Year | Sessions | Peak VaR (current) £ | Peak VaR (stressed) £ | Accounts touched |
|------|----------|----------------------|----------------------|-----------------|
| 2016 | 13 | £28 | £9 | 1 |
| 2017 | 12 | £1,005 | £401 | 3 |
| 2022 | 9 | £55,850 | £20,663 | 8 |
| 2023 | 4 | £128,638 | £49,007 | 10 |

**Total sessions 2016-2025: 38** | Busiest year: 2016 (13 sessions)
Peak VaR observed: 2023 at £128,638 | Unique accounts ever adjusted: 11

**Most frequently adjusted accounts:**
- C1: 22 sessions
- C5: 19 sessions
- C7: 16 sessions
- C2: 13 sessions
- C6: 12 sessions

> Risk committee wake-ups are documented in `docs/observability/run_history.json`.

## Customer Strategic Value Matrix

2x2 matrix: CLV (above/below median) × Churn probability (above/below median).
Median CLV: £10,514.09 | Median churn: 29% | Total portfolio CLV: £8,077,248.04

### PROTECT (High CLV, Low Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C_IC4 | £1,808,130.25 | 20% | 18.6 periods |
| C6 | £21,164.75 | 26% | 17.0 periods |

Quadrant CLV: £1,829,294.99 (23% of portfolio)

### CRITICAL (High CLV, High Churn — priority intervention)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C_IC3 | £3,309,102.77 | 41% | 18.2 periods |
| C_IC1 | £1,846,699.19 | 29% | 16.7 periods |
| C_IC2 | £1,026,154.51 | 32% | 16.9 periods |
| C5 | £12,391.04 | 38% | 17.5 periods |
| C8 | £10,514.09 | 32% | 18.0 periods |

Quadrant CLV: £6,204,861.59 (77% of portfolio)

### MONITOR (Low CLV, Low Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C9 | £10,251.81 | 26% | 15.9 periods |
| C3 | £7,451.08 | 11% | 23.5 periods |
| C1 | £4,898.21 | 11% | 15.6 periods |

Quadrant CLV: £22,601.10 (0% of portfolio)

### EXIT (Low CLV, High Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C7 | £9,351.58 | 29% | 20.2 periods |
| C2 | £6,944.28 | 38% | 19.8 periods |
| C4 | £4,194.50 | 38% | 21.1 periods |

Quadrant CLV: £20,490.36 (0% of portfolio)

**Board action: CRITICAL quadrant has 5 account(s). High CLV at risk from elevated churn probability. Immediate retention offers recommended.**

## Customer Experience & Service Quality

| Year | Billing Clarity | Complaint Prob | Acq Attempts | Acq Wins | Flag |
|------|----------------|---------------|-------------|---------|------|
| 2016 | 0.829 | 0.047 | 0 | 0 |  |
| 2017 | 0.818 | 0.047 | 0 | 0 |  |
| 2018 | 0.810 | 0.047 | 0 | 0 |  |
| 2019 | 0.824 | 0.047 | 0 | 0 |  |
| 2020 | 0.830 | 0.043 | 1 | 0 |  |
| 2021 | 0.829 | 0.045 | 1 | 0 |  |
| 2022 | 0.790 | 0.056 | 0 | 0 | **LOW CLARITY** |
| 2023 | 0.805 | 0.049 | 0 | 0 |  |
| 2024 | 0.812 | 0.047 | 2 | 0 |  |
| 2025 | 0.775 | 0.059 | 0 | 0 | **LOW CLARITY** |

**Overall service quality:** 90.4% | **Average billing clarity:** 0.815 | **Average complaint probability:** 0.048

**Acquisition performance:** 4 attempts, 0 wins (0% win rate). No new customers acquired — cap-constrained gate blocked resi acquisition 2021-2023 (negative projected margin).

**Lowest clarity: 2025** (0.775) — crisis complexity (multiple tariff changes, bill shock events) degraded statement clarity.

## Bill Shock Analysis

Bill shock events occur when a customer's bill increases >20% vs the prior bill.
Regulatory context: Ofgem monitors bill shock as a consumer harm indicator.

| Year | Avg Shock % | Events | Bills | Shock Rate | Flag |
|------|------------|--------|-------|------------|------|
| 2016 | 19.7% | 31 | 108 | 29% |  |
| 2017 | 16.5% | 50 | 168 | 30% |  |
| 2018 | 16.0% | 60 | 180 | 33% |  |
| 2019 | 17.1% | 66 | 204 | 32% |  |
| 2020 | 14.5% | 53 | 204 | 26% |  |
| 2021 | 15.9% | 51 | 192 | 27% |  |
| 2022 | 33.4% | 68 | 161 | 42% | **HIGH** |
| 2023 | 30.4% | 49 | 156 | 31% | **HIGH** |
| 2024 | 16.1% | 37 | 141 | 26% |  |
| 2025 | 24.1% | 22 | 60 | 37% | ELEVATED |

**Crisis peak: 2022** — 33.4% average shock. Energy crisis drove wholesale costs above locked tariff rates,
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
| 2020 | £238,635.82 | £35,390.91 | £69,454.47 | £56,549.79 | £70,023.55 | £470,054.54 | £124,584.59 |
| 2021 | £246,564.67 | £15,001.46 | £71,336.24 | £49,645.20 | £62,799.39 | £486,750.98 | £123,495.85 |
| 2022 | £256,426.70 | **£-49,780.25** | £71,047.02 | £36,711.67 | £69,167.42 | £483,133.05 | £134,078.42 |
| 2023 | £272,109.55 | £64,826.56 | £71,830.95 | £51,007.54 | £75,168.46 | £548,706.24 | £140,176.39 |
| 2024 | £307,882.62 | £110,025.84 | £72,943.93 | £68,764.54 | £82,631.76 | £644,249.16 | £144,049.76 |
| 2025 | £135,846.75 | £46,991.01 | £31,221.29 | £31,056.79 | £36,183.08 | £282,153.30 | £61,622.63 |

**CfD rebate in 2022:** Contracts for Difference (CfD) generators are paid
the difference between strike price and reference price. When spot > strike (2022 crisis),
the mechanism reverses — generators pay back, creating a negative levy for suppliers.

Policy costs: £1,701.01 (2016) → £282,153.30 (2025). CAGR: 76.5%.

## Electricity vs Gas P&L Split

Year-by-year net margin by fuel. Gas became structurally loss-making from 2021.

| Year | Elec Net | Gas Net | Elec Rev | Gas Rev | Gas Share of Rev | Gas Profitable |
|------|----------|---------|----------|---------|-----------------|---------------|
| 2016 | £881.72 | £296.53 | £9,021.95 | £1,388.28 | 13.3% | YES |
| 2017 | £30,102.71 | £463.34 | £231,632.96 | £2,660.42 | 1.1% | YES |
| 2018 | £99,331.51 | £374.66 | £432,208.83 | £3,113.94 | 0.7% | YES |
| 2019 | £218,118.22 | £9,754.19 | £1,060,498.38 | £137,766.14 | 11.5% | YES |
| 2020 | £112,361.98 | £9,852.86 | £1,102,239.07 | £121,124.94 | 9.9% | YES |
| 2021 | £58,439.36 | £8,307.09 | £1,439,653.14 | £297,851.59 | 17.1% | YES |
| 2022 | £300,170.51 | £2,832.97 | £2,852,791.94 | £588,329.77 | 17.1% | YES |
| 2023 | £124,483.49 | £7,361.94 | £2,300,110.86 | £297,197.78 | 11.4% | YES |
| 2024 | £328,112.21 | £9,081.83 | £1,921,524.24 | £270,490.62 | 12.3% | YES |
| 2025 | £112,834.43 | £3,787.52 | £840,090.83 | £132,453.71 | 13.6% | YES |

**Gas supply has been profitable throughout** (10 years).

## Gas Supply Exit Decision Analysis (Phase AR/AS)

Models three strategic scenarios for the board regarding gas supply legs.
Inputs: company billing records (per_cid_comm_pnl). Gas capital = hedge cost applied to gas leg.

### Scenario Comparison (Dual-Fuel Portfolio Only)

| Scenario | Portfolio Net | vs Status Quo | Action |
|----------|--------------|---------------|--------|
| STATUS_QUO | £161,077.15 | — | Current strategy |
| EXIT_GAS | £65,669.96 | £-95,407.18 | Remove gas; model elec churn risk |
| REPRICE_GAS | £163,107.00 | £2,029.86 | Raise gas tariff to break-even |

**Recommended action: REPRICE_GAS**

### Loss-Making Gas Accounts

| Account | Gas Net | Gas ROC | Revenue Uplift Needed |
|---------|---------|---------|----------------------|
| C4g | £-2,029.86 | -14.02x | +19.6% |

**Accretive gas accounts:** C1g (£642.69), C2g (£801.77), C3g (£282.80), C_IC3g (£52,415.53) — these gas legs support customer retention without capital destruction.

**Board Decision:**
- Exit gas: I&C customers at 40% electricity churn risk when gas removed (relationship loss)
- Reprice gas: increases customer cost but eliminates capital destruction
- Status quo: unsustainable — gas legs destroying £52113 in net value

## Segment Capital Efficiency (Return-on-Capital)

Lifetime net margin and capital deployed per segment.
ROC = lifetime net / lifetime capital. ROC < 0 = capital destroyer.

| Segment | Lifetime Gross | Capital Deployed | Lifetime Net | ROC | Signal |
|---------|---------------|------------------|--------------|-----|--------|
| I&C electricity | £5,716,346.34 | £50,049.96 | £1,376,963.76 | 27.5x | Strong |
| I&C gas | £622,647.03 | £0.00 | £52,415.53 | 0.0x | Low return |
| SME electricity | £40,732.31 | £484.92 | £4,044.33 | 8.3x | Moderate |
| resi electricity | £53,321.29 | £570.26 | £3,828.04 | 6.7x | Moderate |
| resi gas | £6,202.34 | £200.69 | £-302.60 | -1.5x | CAPITAL DESTROYER |

## Portfolio Concentration Risk

Revenue concentration analysis across 20 margin-positive accounts. Herfindahl-Hirschman Index (HHI): **2246** — MODERATE (1,500-2,500).

**Segment Margin Share:**
- I&C: £6,255,772.42 (98.5% of total positive margin)
- resi: £54,223.57 (0.9% of total positive margin)
- SME: £37,910.38 (0.6% of total positive margin)

**Top 5 Accounts by Margin Contribution:**

| Account | Segment | Lifetime Margin | Share | Latest Churn Risk | Margin at Risk |
|---------|---------|-----------------|-------|-------------------|----------------|
| C_IC1 | I&C | £1,854,821.05 | 29.2% | 5% | £92,741.05 |
| C_IC3 | I&C | £1,798,804.30 | 28.3% | 41% | £737,509.76 |
| C_IC4 | I&C | £1,090,243.56 | 17.2% | 0% | £0.00 |
| C_IC2 | I&C | £898,486.46 | 14.2% | 5% | £44,924.32 |
| C_IC3g | I&C | £613,417.06 | 9.7% | 0% | £0.00 |

**Concentration Risk Warning:**
- I&C segment accounts for 98.5% of total portfolio margin
- Resi and SME segments are effectively margin-neutral at portfolio scale
- A single large I&C departure would remove 14-29% of all margin
- Board action: diversify acquisition pipeline toward profitable resi/SME to reduce I&C dependency

## Portfolio Learning Premium (Phase 17a + 19a)

Company applied portfolio premium adjustments at 115 renewal(s) (26 gas) based on recent portfolio-wide margin rates: 63 surcharge(s), 52 discount(s).

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
| C1g | gas | 2020-12-30 | 14.7% | -3.3% | £28.99/MWh | £28.02/MWh |
| C5 | electricity | 2020-12-30 | 4.6% | +1.7% | £133.55/MWh | £135.84/MWh |
| C7 | electricity | 2020-12-30 | -3.1% | +5.5% | £133.55/MWh | £140.94/MWh |
| C_IC3 | electricity | 2020-12-31 | -4.3% | +6.2% | £50.65/MWh | £53.77/MWh |
| C_IC3g | gas | 2020-12-31 | 7.7% | +0.1% | £20.05/MWh | £20.08/MWh |
| C2 | electricity | 2021-03-31 | -20.8% | +14.4% | £175.90/MWh | £201.25/MWh |
| C2g | gas | 2021-03-31 | 6.5% | +0.8% | £36.20/MWh | £36.48/MWh |
| C6 | electricity | 2021-03-31 | -16.1% | +12.1% | £175.90/MWh | £197.12/MWh |
| C8 | electricity | 2021-03-31 | -11.9% | +9.9% | £175.90/MWh | £193.39/MWh |
| C_IC2 | electricity | 2021-03-31 | -4.6% | +6.3% | £138.90/MWh | £147.64/MWh |
| C_IC1 | electricity | 2021-04-30 | 0.9% | +3.5% | £113.97/MWh | £118.02/MWh |
| C9 | electricity | 2021-06-30 | 1.1% | +3.5% | £170.38/MWh | £176.29/MWh |
| C4 | electricity | 2021-09-30 | -2.4% | +5.2% | £205.15/MWh | £215.85/MWh |
| C4g | gas | 2021-09-30 | 0.8% | +3.6% | £53.99/MWh | £55.94/MWh |
| C1 | electricity | 2021-12-30 | 4.9% | +1.6% | £311.83/MWh | £316.70/MWh |
| C5 | electricity | 2021-12-30 | 4.9% | +1.6% | £311.83/MWh | £316.70/MWh |
| C7 | electricity | 2021-12-30 | -3.3% | +5.7% | £311.83/MWh | £329.43/MWh |
| C_IC3 | electricity | 2021-12-31 | -25.2% | +15.0% | £224.03/MWh | £257.63/MWh |
| C_IC3g | gas | 2021-12-31 | -18.2% | +13.1% | £109.48/MWh | £123.80/MWh |
| C2 | electricity | 2022-03-31 | -16.6% | +12.3% | £361.95/MWh | £406.41/MWh |
| C6 | electricity | 2022-03-31 | -16.8% | +12.4% | £361.95/MWh | £406.89/MWh |
| C8 | electricity | 2022-03-31 | 5.1% | +1.4% | £361.95/MWh | £367.17/MWh |
| C_IC2 | electricity | 2022-04-30 | -10.3% | +9.2% | £269.81/MWh | £294.54/MWh |
| C_IC1 | electricity | 2022-05-30 | -6.9% | +7.4% | £239.42/MWh | £257.21/MWh |
| C9 | electricity | 2022-06-30 | 4.4% | +1.8% | £255.09/MWh | £259.70/MWh |
| C4 | electricity | 2022-09-30 | 7.3% | +0.4% | £404.86/MWh | £406.35/MWh |
| C4g | gas | 2022-09-30 | -19.2% | +13.6% | £183.79/MWh | £208.78/MWh |
| C5 | electricity | 2022-12-30 | 9.0% | -0.5% | £266.73/MWh | £265.45/MWh |
| C7 | electricity | 2022-12-30 | -2.9% | +5.5% | £266.73/MWh | £281.32/MWh |
| C_IC3 | electricity | 2022-12-31 | -13.9% | +10.9% | £168.36/MWh | £186.79/MWh |
| C_IC3g | gas | 2022-12-31 | -37.8% | +15.0% | £101.23/MWh | £116.42/MWh |
| C2_2 | electricity | 2023-03-31 | -11.3% | +9.7% | £319.17/MWh | £350.04/MWh |
| C6 | electricity | 2023-03-31 | -0.2% | +4.1% | £319.17/MWh | £332.32/MWh |
| C8 | electricity | 2023-03-31 | 7.0% | +0.5% | £319.17/MWh | £320.85/MWh |
| C_IC2 | electricity | 2023-05-30 | -22.1% | +15.0% | £171.46/MWh | £197.18/MWh |
| C_IC1 | electricity | 2023-06-29 | -17.2% | +12.6% | £163.19/MWh | £183.71/MWh |
| C9 | electricity | 2023-06-30 | -10.4% | +9.2% | £224.44/MWh | £245.09/MWh |
| C4 | electricity | 2023-09-30 | 9.6% | -0.8% | £216.77/MWh | £215.02/MWh |
| C4g | gas | 2023-09-30 | -38.6% | +15.0% | £47.83/MWh | £55.00/MWh |
| C5_2 | electricity | 2023-12-30 | 29.2% | -5.0% | £242.22/MWh | £230.11/MWh |
| C7 | electricity | 2023-12-30 | 25.8% | -5.0% | £242.22/MWh | £230.11/MWh |
| C_IC3 | electricity | 2023-12-31 | 21.9% | -5.0% | £118.95/MWh | £113.00/MWh |
| C_IC3g | gas | 2023-12-31 | -10.0% | +9.0% | £51.89/MWh | £56.57/MWh |
| C2_2 | electricity | 2024-03-30 | 14.2% | -3.1% | £207.71/MWh | £201.26/MWh |
| C6 | electricity | 2024-03-30 | 9.5% | -0.8% | £207.71/MWh | £206.12/MWh |
| C8 | electricity | 2024-03-30 | 9.5% | -0.8% | £207.71/MWh | £206.12/MWh |
| C_IC2 | electricity | 2024-06-28 | -34.0% | +15.0% | £148.64/MWh | £170.93/MWh |
| C9 | electricity | 2024-06-29 | -27.5% | +15.0% | £203.92/MWh | £234.50/MWh |
| C_IC1 | electricity | 2024-07-28 | -26.9% | +15.0% | £154.38/MWh | £177.53/MWh |
| C4 | electricity | 2024-09-29 | 0.4% | +3.8% | £195.97/MWh | £203.38/MWh |
| C5_2 | electricity | 2024-12-29 | 0.4% | +3.8% | £243.79/MWh | £253.01/MWh |
| C7 | electricity | 2024-12-29 | 22.1% | -5.0% | £243.79/MWh | £231.60/MWh |
| C_IC3 | electricity | 2024-12-30 | 13.8% | -2.9% | £116.37/MWh | £112.99/MWh |
| C_IC3g | gas | 2024-12-30 | -9.4% | +8.7% | £50.47/MWh | £54.85/MWh |
| C2_2 | electricity | 2025-03-30 | 4.2% | +1.9% | £284.89/MWh | £290.27/MWh |
| C8 | electricity | 2025-03-30 | 6.5% | +0.7% | £284.89/MWh | £286.98/MWh |

## Churn Avoidability Analysis (Phase 17b)

Total no-offer churns: **6** | Blind misses: **6** | Deliberate passes (uneconomical): **0**

- Blind misses: company estimated churn < 30% → no offer made. Of these, 3 had SIM p ≥ 30% (detectable with a better model).
- Deliberate passes: company estimated churn ≥ 30% but the retention offer was uneconomical (margin + acq cost < offer cost).

**Estimated margin at stake** — blind: £5,747.66 | deliberate: £0.00 | total: £5,747.66

| Customer | Date | Reason | Co. est | SIM p | Detectable? | Margin at stake |
|----------|------|--------|---------|-------|-------------|----------------|
| C3 | 2020-06-30 | Blind miss | 0.05 | 0.11 | No | £585.39 |
| C1 | 2021-12-30 | Blind miss | 0.05 | 0.11 | No | £-178.13 |
| C2 | 2022-03-31 | Blind miss | 0.07 | 0.38 | Yes | £236.63 |
| C5 | 2022-12-30 | Blind miss | 0.05 | 0.38 | Yes | £1,774.75 |
| C6 | 2024-03-30 | Blind miss | 0.25 | 0.26 | No | £2,860.15 |
| C4 | 2024-09-29 | Blind miss | 0.05 | 0.38 | Yes | £468.87 |

## Dual-Fuel Account P&L (Phase 17d)

5 dual-fuel account pair(s): electricity leg + gas leg combined.

| Account | Elec net | Gas net | Combined net | Gas accretive? |
|---------|----------|---------|-------------|---------------|
| C_IC3+C_IC3g | £107,507.04 | £52,415.53 | £159,922.58 | Yes |
| C2+C2g | £689.87 | £801.77 | £1,491.64 | Yes |
| C1+C1g | £422.71 | £642.69 | £1,065.40 | Yes |
| C3+C3g | £205.99 | £282.80 | £488.79 | Yes |
| C4+C4g | £138.61 | £-2,029.86 | £-1,891.25 | No |

Gas accretive in 4/5 dual-fuel accounts. Total gas net margin: £52,112.93.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £1,436,949.07 across 20 billing accounts. Revenue: £14,042,149.39.

| # | Customer | Tariff | Revenue | Gross margin | Capital | Net margin | Net margin % |
|---|----------|--------|---------|-------------|---------|------------|-------------|
| 1 | C_IC1 | fixed | £3,123,594.54 | £1,874,657.14 | £18,414.17 | £828,200.85 | 26.5% |
| 2 | C_IC2 | fixed | £1,525,271.51 | £909,831.00 | £8,527.57 | £426,672.07 | 28.0% |
| 3 | C_IC3 | pass_through | £4,630,060.86 | £1,825,172.93 | £23,108.22 | £107,507.04 | 2.3% |
| 4 | C_IC3g | pass_through | £1,832,579.91 | £622,647.03 | £0.00 | £52,415.53 | 2.9% |
| 5 | C_IC4 | flex | £2,744,638.87 | £1,106,685.27 | £0.00 | £14,583.80 | 0.5% |
| 6 | C6 | fixed | £38,936.89 | £22,450.40 | £264.31 | £3,578.84 | 9.2% |
| 7 | C9 | fixed | £20,243.67 | £12,708.16 | £131.43 | £1,492.51 | 7.4% |
| 8 | C8 | fixed | £21,686.32 | £12,466.45 | £134.89 | £1,268.02 | 5.8% |
| 9 | C2_2 | fixed | £10,304.95 | £5,496.96 | £67.94 | £1,067.87 | 10.4% |
| 10 | C2g | fixed | £3,849.77 | £2,019.21 | £21.85 | £801.77 | 20.8% |
| 11 | C2 | fixed | £5,114.40 | £3,410.31 | £24.74 | £689.87 | 13.5% |
| 12 | C1g | fixed | £2,893.90 | £1,540.63 | £18.80 | £642.69 | 22.2% |
| 13 | C1 | fixed | £4,225.33 | £2,734.27 | £19.17 | £422.71 | 10.0% |
| 14 | C5_2 | fixed | £12,546.51 | £6,524.32 | £88.86 | £384.25 | 3.1% |
| 15 | C3g | fixed | £2,683.32 | £1,298.53 | £15.29 | £282.80 | 10.5% |
| 16 | C3 | fixed | £3,628.72 | £2,388.84 | £14.77 | £205.99 | 5.7% |
| 17 | C4 | fixed | £6,274.43 | £3,314.79 | £37.48 | £138.61 | 2.2% |
| 18 | C5 | fixed | £21,466.86 | £11,757.59 | £131.75 | £81.23 | 0.4% |
| 19 | C7 | fixed | £21,778.35 | £10,801.52 | £139.83 | £-1,457.52 | -6.7% |
| 20 | C4g | fixed | £10,370.30 | £1,343.97 | £144.75 | £-2,029.86 | -19.6% |

## Revenue & Margin Sanity Check

### Portfolio P&L Waterfall
| Line | £ | % Revenue |
|------|---|-----------|
| Supply Revenue (ex-VAT, ex-policy passthrough) | £14,042,149 | 100.0% |
| Wholesale cost | -£7,602,900 | 54.1% |
| **Gross supply margin** | **£6,439,249** | **45.9%** |
| Policy + Network costs | -£4,950,994 | 35.3% |
| Capital cost | -£51,306 | 0.4% |
| **Net supply margin** | **£1,436,949** | **10.2%** |

> *The ledger's `net_margin_gbp` (£6,402,402) is gross − capital only, not final net.*

### Segment Net Margin vs Benchmark
| Segment | Revenue | Gross% | Net% | Benchmark | Status |
|---------|---------|--------|------|-----------|--------|
| I&C/elec | £12,023,566 | 47.5% | 11.5% | large spread -20% to +15% (crisis) | ✓ |
| I&C/gas | £1,832,580 | 34.0% | 2.9% | commodity 2-6%, pass-through ≈0 | ✓ |
| SME/elec | £60,404 | 56.6% | 6.1% | CMA 3-8% | ✓ |
| resi/elec | £82,951 | 57.7% | 3.3% | Ofgem CMA 2-5% | ✓ |
| resi/gas | £19,797 | 31.3% | -1.5% | Ofgem CMA 2-4% | ✓ |

### Per-Customer Net Margin Flags
No individual customers outside ±40.0/80.0 thresholds.

**SANITY CHECK: PASS** — all segments within benchmarks.
## Transaction Log

Total events: 3,415,698

| Event type | Count |
|------------|-------|
| acquisition_gate_event | 1 |
| acquisition_spend_event | 3 |
| bad_debt_event | 1,574 |
| billing_event | 1,574 |
| capital_charge_event | 1,645,694 |
| fixed_cost_event | 114 |
| non_commodity_cost_event | 1,574 |
| payment_received_event | 1,574 |
| settlement_event | 1,762,016 |
| vat_remittance_event | 1,574 |

**Cash-flow waterfall (from ledger)**

| Flow | Amount |
|------|--------|
| Customer bills (all-in) | £19,797,278.86 |
|   Less: VAT remitted to HMRC | (£956,088.16) |
| = Revenue (ex-VAT) | £18,841,190.70 |
| Less: non-commodity pass-through | (£4,784,583.10) |
| Wholesale cost (settlement events) | (£7,602,900.09) |
| Gross margin | £6,453,707.51 |
| Capital charges | (£51,305.83) |
| Net margin | £6,402,401.68 |

_Cash reconciliation: of £19,797,278.86 billed, bad debt of £396,051.15 was written off, leaving £19,401,227.71 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £6,962,438.70._

| Acquisition spend | (£700.00) |
| Fixed overhead | (£5,700.00) |
| Operating net margin | £6,396,001.68 |

## Annual Management Accounts

Year-by-year income statement from company accounting records. All figures £.

| Year | Revenue | Wholesale | Non-Commod | Gross Margin | Bad Debt | OpEx | Net Margin |
|------|---------|-----------|-----------|--------------|----------|------|------------|
| 2016 | £15,354.61 | £3,596.53 | £3,892.24 | £7,865.84 | £234.62 | £834.62 | £6,944.88 (45.2%) |
| 2017 | £348,630.52 | £111,056.98 | £112,782.23 | £124,791.30 | £6,260.72 | £6,860.72 | £116,657.37 (33.5%) |
| 2018 | £600,953.01 | £172,802.28 | £163,976.80 | £264,173.93 | £11,823.00 | £12,423.00 | £250,222.87 (41.6%) |
| 2019 | £1,645,452.10 | £496,239.95 | £445,337.04 | £703,875.12 | £30,746.61 | £31,346.61 | £670,219.20 (40.7%) |
| 2020 | £1,857,080.58 | £431,625.18 | £631,858.33 | £793,597.07 | £38,269.56 | £39,019.56 | £752,612.52 (40.5%) |
| 2021 | £2,419,523.89 | £973,000.60 | £680,260.90 | £766,262.39 | £47,128.93 | £47,728.93 | £712,903.71 (29.5%) |
| 2022 | £4,244,235.13 | £2,390,418.55 | £801,612.92 | £1,052,203.66 | £84,225.82 | £84,825.82 | £954,095.04 (22.5%) |
| 2023 | £3,476,339.14 | £1,640,650.78 | £877,552.25 | £958,136.11 | £76,503.88 | £77,103.88 | £870,999.48 (25.1%) |
| 2024 | £3,003,518.02 | £932,392.51 | £810,222.09 | £1,260,903.42 | £64,224.08 | £65,374.08 | £1,185,996.65 (39.5%) |
| 2025 | £1,230,103.68 | £452,432.70 | £257,088.30 | £520,582.67 | £36,633.94 | £36,933.94 | £477,982.80 (38.9%) |
| **Total** | **£18,841,190.70** | | | | | | **£5,998,634.54 (31.8%)** |

**Best year:** 2024 — net £1,185,996.65 (39.5% margin)
**Worst year:** 2016 — net £6,944.88 (45.2% margin)

### Balance Sheet (Year End 2025)

| Item | Value |
|------|-------|
| Cash | £8,465,270.77 |
| Trade Receivables | £0.00 |
| **Total Assets** | **£8,465,270.77** |
| Opening Capital | £2,466,636.22 |
| Current Period Profit | £5,998,634.54 |

## Budget vs Actual

Annual plan compared to management account actuals. RAG: GREEN <5%, AMBER 5-15%, RED >=15% variance (either direction).

| Year | Bud Revenue | Act Revenue | Rev% | Bud Net | Act Net | Net% | RAG |
|------|-------------|-------------|------|---------|---------|------|-----|
| 2016 | £14,671.69 | £15,354.61 | +4.7% | £6,592.99 | £6,944.88 | +5.3% | AMBER |
| 2017 | £16,138.86 | £348,630.52 | +2060.2% | £7,252.29 | £116,657.37 | +1508.6% | RED |
| 2018 | £386,623.75 | £600,953.01 | +55.4% | £128,424.00 | £250,222.87 | +94.8% | RED |
| 2019 | £675,851.95 | £1,645,452.10 | +143.5% | £281,335.50 | £670,219.20 | +138.2% | RED |
| 2020 | £1,816,630.04 | £1,857,080.58 | +2.2% | £736,963.94 | £752,612.52 | +2.1% | GREEN |
| 2021 | £2,028,952.42 | £2,419,523.89 | +19.2% | £833,649.22 | £712,903.71 | -14.5% | AMBER |
| 2022 | £2,607,611.88 | £4,244,235.13 | +62.8% | £790,935.58 | £954,095.04 | +20.6% | RED |
| 2023 | £4,508,414.67 | £3,476,339.14 | -22.9% | £1,029,561.00 | £870,999.48 | -15.4% | RED |
| 2024 | £3,512,844.39 | £3,003,518.02 | -14.5% | £893,105.75 | £1,185,996.65 | +32.8% | RED |
| 2025 | £3,145,356.42 | £1,230,103.68 | -60.9% | £1,315,150.33 | £477,982.80 | -63.7% | RED |

## Growth & Acquisition

**Mandate:** `flat`  **Acquisition cost:** resi £150 / SME £400  **Fixed overhead:** £50/month

**Acquisition activity by year**

| Year | Attempts | Wins | Win Rate | Spend |
|------|----------|------|----------|-------|
| 2020 | 1 | 0 | 0% | £150.00 |
| 2021 | 1 | 0 | 0% | £0.00 |
| 2024 | 2 | 0 | 0% | £550.00 |

**Total:** 4 attempts, 0 wins (0% win rate), £700.00 total spend

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £6,396,001.68

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
- Average CLV (Point-in-Time, year-end 2017): £11,361.98
  - By billing account: C1 £5,410.82, C2 £10,738.97, C3 £9,207.62, C4 £8,478.73, C5 £11,894.95, C6 £23,763.64, C7 £8,490.63, C8 £13,366.53, C9 £10,905.94
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
- Average CLV (Point-in-Time, year-end 2018): £297,216.73
  - By billing account: C1 £5,600.28, C2 £9,078.04, C3 £8,930.17, C4 £7,414.78, C5 £11,521.58, C6 £19,884.32, C7 £8,460.10, C8 £11,877.30, C9 £10,261.59, C_IC1 £2,879,139.19
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
- Average CLV (Point-in-Time, year-end 2019): £399,888.52
  - By billing account: C1 £5,505.79, C2 £9,483.53, C3 £9,064.57, C4 £6,975.57, C5 £13,910.73, C6 £19,922.01, C7 £8,641.40, C8 £9,849.92, C9 £10,280.61, C_IC1 £2,654,978.23, C_IC2 £1,650,161.34
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

- Net margin: £122,214.83 (gross £791,796.48, capital £1,964.99)
  - Electricity: gross £714,614.63, capital £1,954.47, net £112,361.98
  - Gas: gross £77,181.85, capital £10.52, net £9,852.86
- Treasury at year end: £2,914,252.99
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.89 (avg 0.89), C1g 0.85 (avg 0.85), C2 0.86 (avg 0.86), C2g 0.85 (avg 0.85), C4 0.88 (avg 0.88), C4g 0.85 (avg 0.85), C5 0.89 (avg 0.89), C6 0.86 (avg 0.86), C7 0.89 (avg 0.89), C8 0.87 (avg 0.87), C9 0.85 (avg 0.85), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.87), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2020-03-16 period 20, net margin £-18.66

**Customer Book**

- Active accounts: 18 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC4
- Losses (churn) during year: C3
  - Renewals (retained): 9 accounts
- Average CLV (Point-in-Time, year-end 2020): £514,953.56
  - By billing account: C1 £5,848.48, C2 £7,950.91, C3 £8,072.18, C4 £6,824.11, C5 £10,518.32, C6 £18,914.03, C7 £9,763.37, C8 £9,858.32, C9 £9,713.68, C_IC1 £1,576,265.01, C_IC2 £837,234.64, C_IC3 £2,659,040.22, C_IC4 £1,534,392.97
- Bill shock events (>=20%): 53 -- C1g 2020-01-31 (21%); C1g 2020-04-30 (32%); C1g 2020-06-30 (25%); C1g 2020-10-31 (56%); C1g 2020-12-31 (35%); C5 2020-04-30 (28%); C5 2020-10-31 (36%); C5 2020-12-31 (25%); C7 2020-04-30 (34%); C7 2020-05-31 (20%); C7 2020-06-30 (27%); C7 2020-10-31 (58%); C7 2020-11-30 (23%); C7 2020-12-31 (34%); C2 2020-04-30 (23%); C2g 2020-04-30 (36%); C2g 2020-06-30 (25%); C2g 2020-09-30 (27%); C2g 2020-10-31 (48%); C2g 2020-12-31 (38%); C6 2020-04-30 (29%); C6 2020-09-30 (20%); C6 2020-10-31 (33%); C6 2020-12-31 (26%); C8 2020-04-30 (36%); C8 2020-05-31 (24%); C8 2020-06-30 (32%); C8 2020-09-30 (51%); C8 2020-10-31 (64%); C8 2020-12-31 (42%); C3g 2020-04-30 (24%); C3g 2020-05-31 (21%); C3g 2020-06-29 (34%); C9 2020-04-30 (27%); C9 2020-05-31 (25%); C9 2020-06-30 (34%); C9 2020-09-30 (42%); C9 2020-10-31 (49%); C9 2020-12-31 (36%); C4 2020-04-30 (30%); C4 2020-09-30 (20%); C4 2020-10-31 (22%); C4 2020-11-30 (24%); C4g 2020-04-30 (35%); C4g 2020-05-31 (20%); C4g 2020-06-30 (26%); C4g 2020-09-30 (30%); C4g 2020-10-31 (49%); C4g 2020-12-31 (35%); C_IC1 2020-03-31 (57%); C_IC1 2020-04-30 (72%); C_IC2 2020-02-29 (66%); C_IC2 2020-03-31 (118%)
- Churn risk (accounts renewing in 2020): 9 at risk (≥20% churn prob): C1 38%, C4 41%, C5 32%, C7 20%, C8 23%, C9 23%, C_IC1 41%, C_IC2 41%, C_IC3 20%

**Pricing & Margin**

- C1 (electricity): tariff £125.83-£132.43/MWh, net margin £75.01
- C1g (gas): tariff £25.00-£25.33/MWh, net margin £137.20
- C2 (electricity): tariff £143.89-£151.90/MWh, net margin £182.92
- C2g (gas): tariff £21.66-£26.00/MWh, net margin £133.50
- C3 (electricity): tariff £120.68/MWh, net margin £16.44
- C3g (gas): tariff £23.00/MWh, net margin £75.08
- C4 (electricity): tariff £122.47-£126.76/MWh, net margin £87.27
- C4g (gas): tariff £16.09-£19.47/MWh, net margin £71.92
- C5 (electricity): tariff £126.10-£135.84/MWh, net margin £-30.65 -- **net-negative**
- C6 (electricity): tariff £143.89-£148.72/MWh, net margin £366.13
- C7 (electricity): tariff £99.69-£211.41/MWh, net margin £58.18
- C8 (electricity): tariff £110.24-£211.40/MWh, net margin £338.60
- C9 (electricity): tariff £85.33-£188.63/MWh, net margin £117.22
- C_IC1 (electricity): tariff £-73.45-£2690.77/MWh, net margin £52,028.29
- C_IC2 (electricity): tariff £-79.50-£278.56/MWh, net margin £43,546.80
- C_IC3 (electricity): tariff £37.49-£80.66/MWh, net margin £11,005.48
- C_IC3g (gas): tariff £15.44-£20.08/MWh, net margin £9,435.16
- C_IC4 (electricity): tariff £77.17-£132.42/MWh, net margin £4,570.28

**Portfolio Health**

- Capital cost ratio: 0.2% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.830, average bill shock 14.5%, bad debt provision £6,294.75, avg complaint probability 4.3%
- Solvency signal: £224,173/customer (13 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £85,197.78 vs. naked (unhedged) net margin: £963,111.14
- hedging cost £877,913.36 vs. a fully unhedged book (commodity-only: actual net £85,197.78 vs. naked net £963,111.14)
  - C1: actual £-18.85 vs. naked £97.59 -- hedging cost £116.44
  - C1g: actual £22.28 vs. naked £-68.18 -- hedging added £90.47
  - C2: actual £175.35 vs. naked £570.69 -- hedging cost £395.33
  - C2g: actual £144.84 vs. naked £324.27 -- hedging cost £179.43
  - C4: actual £25.02 vs. naked £235.46 -- hedging cost £210.45
  - C4g: actual £-75.14 vs. naked £117.15 -- hedging cost £192.29
  - C5: actual £-339.41 vs. naked £173.58 -- hedging cost £512.99
  - C6: actual £355.75 vs. naked £2,175.57 -- hedging cost £1,819.82
  - C7: actual £-122.68 vs. naked £315.75 -- hedging cost £438.43
  - C8: actual £341.71 vs. naked £1,170.27 -- hedging cost £828.57
  - C9: actual £-18.70 vs. naked £697.66 -- hedging cost £716.35
  - C_IC1: actual £33,034.60 vs. naked £128,260.98 -- hedging cost £95,226.38
  - C_IC2: actual £42,303.73 vs. naked £96,422.44 -- hedging cost £54,118.71
  - C_IC3: actual £-16,452.24 vs. naked £220,540.02 -- hedging cost £236,992.27
  - C_IC3g: actual £17,934.51 vs. naked £159,245.07 -- hedging cost £141,310.56
  - C_IC4: actual £7,886.99 vs. naked £352,832.81 -- hedging cost £344,945.82

**Year narrative:** 2020 produced a net gain of £122,214.83 across 18 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 53 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £66,746.46 (gross £764,661.12, capital £5,629.75)
  - Electricity: gross £681,869.24, capital £5,613.98, net £58,439.36
  - Gas: gross £82,791.88, capital £15.77, net £8,307.09
- Treasury at year end: £2,942,147.83
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C4 0.94 (avg 0.94), C4g 0.85 (avg 0.85), C5 0.94 (avg 0.94), C6 0.92 (avg 0.92), C7 0.97 (avg 0.97), C8 0.92 (avg 0.92), C9 0.92 (avg 0.92), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.89), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2021-11-24 period 30, net margin £-74.84

**Customer Book**

- Active accounts: 16 (C1, C1g, C2, C2g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: C1
  - Renewals (retained): 8 accounts
- Average CLV (Point-in-Time, year-end 2021): £512,422.81
  - By billing account: C1 £4,887.47, C2 £7,367.63, C3 £6,247.95, C4 £5,553.45, C5 £11,191.81, C6 £23,484.59, C7 £8,333.63, C8 £9,244.33, C9 £8,062.70, C_IC1 £1,295,540.92, C_IC2 £851,995.02, C_IC3 £2,738,166.82, C_IC4 £1,691,420.24
- Bill shock events (>=20%): 51 -- C1g 2021-05-31 (28%); C1g 2021-06-30 (45%); C1g 2021-10-31 (55%); C1g 2021-11-30 (53%); C5 2021-05-31 (22%); C5 2021-06-30 (31%); C5 2021-10-31 (28%); C5 2021-11-30 (48%); C7 2021-01-31 (21%); C7 2021-05-31 (29%); C7 2021-06-30 (46%); C7 2021-10-31 (52%); C7 2021-11-30 (63%); C2g 2021-04-30 (32%); C2g 2021-05-31 (24%); C2g 2021-06-30 (53%); C2g 2021-10-31 (57%); C2g 2021-11-30 (58%); C6 2021-06-30 (35%); C6 2021-10-31 (27%); C6 2021-11-30 (49%); C8 2021-05-31 (28%); C8 2021-06-30 (60%); C8 2021-09-30 (23%); C8 2021-10-31 (65%); C8 2021-11-30 (80%); C9 2021-02-28 (21%); C9 2021-05-31 (24%); C9 2021-06-30 (49%); C9 2021-08-31 (20%); C9 2021-09-30 (21%); C9 2021-10-31 (59%); C9 2021-11-30 (48%); C9 2021-12-31 (23%); C4 2021-04-30 (30%); C4 2021-09-30 (23%); C4 2021-10-31 (48%); C4 2021-11-30 (31%); C4g 2021-05-31 (22%); C4g 2021-06-30 (53%); C4g 2021-10-31 (113%); C4g 2021-11-30 (56%); C_IC1 2021-05-31 (40%); C_IC2 2021-03-31 (23%); C_IC2 2021-04-30 (83%); C_IC3g 2021-09-30 (33%); C_IC3g 2021-10-31 (23%); C_IC3g 2021-12-31 (33%); C_IC4 2021-02-28 (21%); C_IC4 2021-09-30 (27%); C_IC4 2021-12-31 (23%)
- Churn risk (accounts renewing in 2021): 7 at risk (≥20% churn prob): C7 20%, C8 20%, C9 20%, C_IC1 41%, C_IC2 41%, C_IC3 32%, C_IC4 38%

**Pricing & Margin**

- C1 (electricity): tariff £132.43/MWh, net margin £-18.56 -- **net-negative**
- C1g (gas): tariff £25.00/MWh, net margin £21.95
- C2 (electricity): tariff £143.89-£183.00/MWh, net margin £157.33
- C2g (gas): tariff £21.66-£35.00/MWh, net margin £99.84
- C4 (electricity): tariff £122.47-£183.00/MWh, net margin £-59.19 -- **net-negative**
- C4g (gas): tariff £16.09-£35.00/MWh, net margin £-334.91 -- **net-negative**
- C5 (electricity): tariff £135.84-£340.69/MWh, net margin £-336.48 -- **net-negative**
- C6 (electricity): tariff £143.89-£197.12/MWh, net margin £526.04
- C7 (electricity): tariff £110.74-£274.50/MWh, net margin £-132.28 -- **net-negative**
- C8 (electricity): tariff £110.24-£274.50/MWh, net margin £341.36
- C9 (electricity): tariff £85.33-£264.43/MWh, net margin £-13.51 -- **net-negative**
- C_IC1 (electricity): tariff £-54.00-£2365.91/MWh, net margin £26,737.23
- C_IC2 (electricity): tariff £-73.20-£1080.00/MWh, net margin £55,499.76
- C_IC3 (electricity): tariff £42.25-£391.21/MWh, net margin £-27,586.98 -- **net-negative**
- C_IC3g (gas): tariff £20.08-£123.80/MWh, net margin £8,520.22
- C_IC4 (electricity): tariff £103.84-£397.26/MWh, net margin £3,324.66

**Portfolio Health**

- Capital cost ratio: 0.7% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 192, average clarity 0.829, average bill shock 15.9%, bad debt provision £9,125.22, avg complaint probability 4.5%
- Solvency signal: £245,179/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £191,444.48 vs. naked (unhedged) net margin: £457,552.33
- hedging cost £266,107.85 vs. a fully unhedged book (commodity-only: actual net £191,444.48 vs. naked net £457,552.33)
  - C2: actual £136.64 vs. naked £124.72 -- hedging added £11.92
  - C2g: actual £45.59 vs. naked £-190.70 -- hedging added £236.29
  - C4: actual £-220.41 vs. naked £-170.34 -- hedging cost £50.07
  - C4g: actual £-901.21 vs. naked £-1,344.38 -- hedging added £443.17
  - C5: actual £116.32 vs. naked £1,380.93 -- hedging cost £1,264.61
  - C6: actual £512.91 vs. naked £268.24 -- hedging added £244.67
  - C7: actual £-1,829.78 vs. naked £-869.22 -- hedging cost £960.56
  - C8: actual £285.02 vs. naked £107.75 -- hedging added £177.27
  - C9: actual £-48.55 vs. naked £-184.09 -- hedging added £135.55
  - C_IC1: actual £27,315.38 vs. naked £-61,910.67 -- hedging added £89,226.05
  - C_IC2: actual £63,558.59 vs. naked £22,119.88 -- hedging added £41,438.71
  - C_IC3: actual £100,234.37 vs. naked £234,716.59 -- hedging cost £134,482.23
  - C_IC3g: actual £4,142.87 vs. naked £85,199.40 -- hedging cost £81,056.52
  - C_IC4: actual £-1,903.26 vs. naked £178,304.23 -- hedging cost £180,207.49

**Year narrative:** 2021 (flagged crisis year) produced a net gain of £66,746.46 across 16 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 51 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £303,003.48 (gross £1,050,760.94, capital £13,282.80)
  - Electricity: gross £960,405.02, capital £13,248.96, net £300,170.51
  - Gas: gross £90,355.92, capital £33.84, net £2,832.97
- Treasury at year end: £3,137,594.83
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.95 (avg 0.95), C4 0.96 (avg 0.96), C4g 0.85 (avg 0.85), C5_2 0.94 (avg 0.94), C6 0.94 (avg 0.94), C7 0.93 (avg 0.93), C8 0.96 (avg 0.96), C9 0.94 (avg 0.94), C_IC1 1.00 (avg 0.97), C_IC2 1.00 (avg 0.97), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 9
  - 2022-04-29: treasury £3,037,811.81, C2->1.00, C6->1.00, C8->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,356.45 / stressed £20,517.58) ratio 2.70
  - 2022-05-29: treasury £3,037,932.16, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,466.25 / stressed £20,546.78) ratio 2.70
  - 2022-06-28: treasury £3,037,926.92, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,466.25 / stressed £20,546.78) ratio 2.70
  - 2022-07-28: treasury £3,037,734.29, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,527.66 / stressed £20,559.02) ratio 2.70
  - 2022-08-27: treasury £3,037,724.69, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,527.66 / stressed £20,559.02) ratio 2.70
  - 2022-09-26: treasury £3,037,709.24, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,527.66 / stressed £20,559.02) ratio 2.70
  - 2022-10-26: treasury £3,036,911.46, C2->1.00, C4->1.00, C5->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,849.59 / stressed £20,662.97) ratio 2.70
  - 2022-11-25: treasury £3,036,928.98, C2->1.00, C4->1.00, C5->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,849.59 / stressed £20,662.97) ratio 2.70
  - 2022-12-25: treasury £3,036,918.98, C2->1.00, C4->1.00, C5->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £55,849.59 / stressed £20,662.97) ratio 2.70
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.70
- Worst single period: C_IC1 on 2022-01-24 period 26, net margin £-89.06

**Customer Book**

- Active accounts: 16 (C2, C2_2, C2g, C4, C4g, C5, C5_2, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 3, gas (dual-fuel): 3
- New acquisitions this year: C2_2, C5_2
- Losses (churn) during year: C2, C5
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2022): £407,319.13
  - By billing account: C1 £4,394.39, C2 £6,200.81, C2_2 £939.08, C3 £5,935.80, C4 £3,381.15, C5 £12,309.64, C5_2 £7.13, C6 £19,803.98, C7 £6,004.58, C8 £7,721.44, C9 £9,354.39, C_IC1 £1,286,271.35, C_IC2 £820,608.72, C_IC3 £2,639,400.54, C_IC4 £1,287,454.00
- Bill shock events (>=20%): 68 -- C5 2022-01-31 (123%); C5 2022-02-28 (21%); C5 2022-05-31 (25%); C5 2022-11-30 (48%); C5 2022-12-29 (29%); C7 2022-01-31 (49%); C7 2022-02-28 (26%); C7 2022-04-30 (22%); C7 2022-05-31 (34%); C7 2022-06-30 (25%); C7 2022-09-30 (30%); C7 2022-11-30 (58%); C7 2022-12-31 (54%); C2g 2022-02-28 (22%); C6 2022-04-30 (42%); C6 2022-05-31 (23%); C6 2022-09-30 (25%); C6 2022-11-30 (43%); C6 2022-12-31 (33%); C8 2022-02-28 (22%); C8 2022-05-31 (38%); C8 2022-06-30 (33%); C8 2022-09-30 (76%); C8 2022-11-30 (68%); C8 2022-12-31 (56%); C9 2022-04-30 (20%); C9 2022-05-31 (28%); C9 2022-06-30 (29%); C9 2022-09-30 (45%); C9 2022-10-31 (30%); C9 2022-11-30 (43%); C9 2022-12-31 (51%); C4 2022-04-30 (28%); C4 2022-09-30 (25%); C4 2022-10-31 (62%); C4 2022-11-30 (31%); C4g 2022-01-31 (25%); C4g 2022-02-28 (24%); C4g 2022-05-31 (34%); C4g 2022-06-30 (28%); C4g 2022-07-31 (22%); C4g 2022-09-30 (63%); C4g 2022-10-31 (134%); C4g 2022-11-30 (57%); C4g 2022-12-31 (56%); C_IC1 2022-03-31 (21%); C_IC1 2022-06-30 (77%); C_IC2 2022-03-31 (24%); C_IC2 2022-05-31 (57%); C_IC3 2022-01-31 (109%); C_IC3g 2022-03-31 (38%); C_IC3g 2022-04-30 (22%); C_IC3g 2022-07-31 (40%); C_IC3g 2022-08-31 (30%); C_IC3g 2022-10-31 (51%); C_IC3g 2022-11-30 (31%); C_IC3g 2022-12-31 (22%); C_IC4 2022-03-31 (41%); C_IC4 2022-07-31 (29%); C_IC4 2022-08-31 (33%); C_IC4 2022-10-31 (31%); C_IC4 2022-12-31 (68%); C2_2 2022-04-30 (1735%); C2_2 2022-05-31 (38%); C2_2 2022-06-30 (32%); C2_2 2022-09-30 (70%); C2_2 2022-11-30 (62%); C2_2 2022-12-31 (56%)
- Churn risk (accounts renewing in 2022): 11 at risk (≥20% churn prob): C2 38%, C4 38%, C5 38%, C6 35%, C7 23%, C8 26%, C9 35%, C_IC1 38%, C_IC2 38%, C_IC3 41%, C_IC4 38%

**Pricing & Margin**

- C2 (electricity): tariff £183.00/MWh, net margin £13.07
- C2_2 (electricity): tariff £361.95/MWh, net margin £28.76
- C2g (gas): tariff £35.00/MWh, net margin £-17.33 -- **net-negative**
- C4 (electricity): tariff £183.00-£305.00/MWh, net margin £-276.94 -- **net-negative**
- C4g (gas): tariff £35.00-£95.00/MWh, net margin £-1,284.53 -- **net-negative**
- C5 (electricity): tariff £340.69/MWh, net margin £117.16
- C5_2 (electricity): tariff £266.73/MWh, net margin £-7.33 -- **net-negative**
- C6 (electricity): tariff £197.12-£406.89/MWh, net margin £822.10
- C7 (electricity): tariff £143.79-£457.50/MWh, net margin £-1,827.01 -- **net-negative**
- C8 (electricity): tariff £143.79-£457.50/MWh, net margin £-285.40 -- **net-negative**
- C9 (electricity): tariff £138.51-£389.54/MWh, net margin £-116.82 -- **net-negative**
- C_IC1 (electricity): tariff £-83.39-£462.98/MWh, net margin £131,248.84
- C_IC2 (electricity): tariff £-80.56-£593.08/MWh, net margin £73,037.60
- C_IC3 (electricity): tariff £146.76-£391.21/MWh, net margin £99,324.40
- C_IC3g (gas): tariff £116.42-£123.80/MWh, net margin £4,134.82
- C_IC4 (electricity): tariff £133.29-£531.77/MWh, net margin £-1,907.93 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 1.3% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £3,438,525.51 -> £3,035,092.09 (11.7%)
- Bills issued: 161, average clarity 0.790, average bill shock 33.4%, bad debt provision £35,784.81, avg complaint probability 5.6%
- Solvency signal: £241,353/customer (13 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £184,272.42 vs. naked (unhedged) net margin: £1,208,910.20
- hedging cost £1,024,637.77 vs. a fully unhedged book (commodity-only: actual net £184,272.42 vs. naked net £1,208,910.20)
  - C2_2: actual £30.18 vs. naked £1,645.15 -- hedging cost £1,614.97
  - C4: actual £-277.33 vs. naked £595.36 -- hedging cost £872.70
  - C4g: actual £-1,950.48 vs. naked £1,336.80 -- hedging cost £3,287.28
  - C5_2: actual £-1,113.67 vs. naked £2,632.27 -- hedging cost £3,745.94
  - C6: actual £1,128.51 vs. naked £3,996.58 -- hedging cost £2,868.07
  - C7: actual £-445.92 vs. naked £2,281.71 -- hedging cost £2,727.63
  - C8: actual £-481.87 vs. naked £1,102.92 -- hedging cost £1,584.78
  - C9: actual £-49.37 vs. naked £1,012.21 -- hedging cost £1,061.58
  - C_IC1: actual £212,769.51 vs. naked £251,051.40 -- hedging cost £38,281.89
  - C_IC2: actual £87,513.15 vs. naked £126,819.69 -- hedging cost £39,306.54
  - C_IC3: actual £-124,836.88 vs. naked £488,078.18 -- hedging cost £612,915.06
  - C_IC3g: actual £8,513.79 vs. naked £123,301.26 -- hedging cost £114,787.47
  - C_IC4: actual £3,472.81 vs. naked £205,056.67 -- hedging cost £201,583.86

**Year narrative:** 2022 (flagged crisis year) produced a net gain of £303,003.48 across 16 accounts. The risk committee intervened 9 time(s), raising hedge fractions in response to elevated VaR. 68 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £131,845.43 (gross £956,898.30, capital £10,032.75)
  - Electricity: gross £835,958.20, capital £9,980.32, net £124,483.49
  - Gas: gross £120,940.11, capital £52.42, net £7,361.94
- Treasury at year end: £3,322,341.29
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.93 (avg 0.93), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C5_2 0.91 (avg 0.91), C6 0.94 (avg 0.94), C7 0.92 (avg 0.92), C8 0.95 (avg 0.95), C9 0.91 (avg 0.91), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 4
  - 2023-01-24: treasury £3,137,594.49, C2->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,604.59 / stressed £44,049.81) ratio 2.76
  - 2023-02-23: treasury £3,137,594.84, C2->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,604.59 / stressed £44,049.81) ratio 2.76
  - 2023-03-25: treasury £3,137,595.14, C2->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £121,604.59 / stressed £44,049.81) ratio 2.76
  - 2023-04-24: treasury £3,217,814.18, C2->1.00, C4->1.00, C5->1.00, C7->1.00, C9->1.00, C_IC3->1.00, VaR (current £128,637.86 / stressed £49,006.78) ratio 2.62
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.73
- Worst single period: C_IC1 on 2023-06-16 period 22, net margin £-21.69

**Customer Book**

- Active accounts: 13 (C2_2, C4, C4g, C5_2, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 2, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 8 accounts
- Average CLV (Point-in-Time, year-end 2023): £373,289.81
  - By billing account: C1 £4,370.57, C2 £5,798.46, C2_2 £2,383.65, C3 £4,991.69, C4 £2,252.21, C5 £13,128.54, C5_2 £928.38, C6 £19,993.31, C7 £5,532.47, C8 £7,688.24, C9 £9,495.66, C_IC1 £1,387,074.87, C_IC2 £819,700.52, C_IC3 £2,124,132.12, C_IC4 £1,191,876.38
- Bill shock events (>=20%): 49 -- C7 2023-01-31 (40%); C7 2023-05-31 (31%); C7 2023-06-30 (35%); C7 2023-10-31 (53%); C7 2023-11-30 (69%); C6 2023-04-30 (32%); C6 2023-05-31 (23%); C6 2023-06-30 (22%); C6 2023-10-31 (38%); C6 2023-11-30 (43%); C8 2023-04-30 (30%); C8 2023-05-31 (39%); C8 2023-06-30 (42%); C8 2023-10-31 (92%); C8 2023-11-30 (66%); C9 2023-02-28 (21%); C9 2023-03-31 (20%); C9 2023-04-30 (26%); C9 2023-05-31 (32%); C9 2023-06-30 (43%); C9 2023-09-30 (20%); C9 2023-10-31 (71%); C9 2023-11-30 (52%); C4 2023-02-28 (25%); C4 2023-04-30 (29%); C4 2023-09-30 (24%); C4 2023-11-30 (27%); C4g 2023-05-31 (36%); C4g 2023-06-30 (45%); C4g 2023-10-31 (46%); C4g 2023-11-30 (63%); C_IC1 2023-03-31 (21%); C_IC1 2023-06-30 (53%); C_IC1 2023-07-31 (60%); C_IC2 2023-03-31 (22%); C_IC2 2023-05-31 (53%); C_IC2 2023-06-30 (101%); C_IC3g 2023-01-31 (31%); C_IC4 2023-01-31 (35%); C2_2 2023-04-30 (23%); C2_2 2023-05-31 (40%); C2_2 2023-06-30 (40%); C2_2 2023-10-31 (89%); C2_2 2023-11-30 (64%); C5_2 2023-01-31 (2059%); C5_2 2023-05-31 (21%); C5_2 2023-06-30 (24%); C5_2 2023-10-31 (30%); C5_2 2023-11-30 (50%)
- Churn risk (accounts renewing in 2023): 9 at risk (≥20% churn prob): C4 41%, C6 41%, C7 41%, C8 38%, C9 41%, C_IC1 41%, C_IC2 41%, C_IC3 41%, C_IC4 35%

**Pricing & Margin**

- C2_2 (electricity): tariff £350.04-£361.95/MWh, net margin £504.22
- C4 (electricity): tariff £249.30-£305.00/MWh, net margin £-68.72 -- **net-negative**
- C4g (gas): tariff £66.00-£95.00/MWh, net margin £-1,164.32 -- **net-negative**
- C5_2 (electricity): tariff £266.73-£269.33/MWh, net margin £-1,102.27 -- **net-negative**
- C6 (electricity): tariff £332.32-£406.89/MWh, net margin £1,253.27
- C7 (electricity): tariff £191.96-£457.50/MWh, net margin £-443.76 -- **net-negative**
- C8 (electricity): tariff £208.21-£457.50/MWh, net margin £-111.16 -- **net-negative**
- C9 (electricity): tariff £192.57-£389.54/MWh, net margin £226.00
- C_IC1 (electricity): tariff £-60.00-£462.98/MWh, net margin £159,949.80
- C_IC2 (electricity): tariff £-186.24-£476.93/MWh, net margin £84,688.50
- C_IC3 (electricity): tariff £95.75-£280.19/MWh, net margin £-123,892.64 -- **net-negative**
- C_IC3g (gas): tariff £56.57-£116.42/MWh, net margin £8,526.27
- C_IC4 (electricity): tariff £106.05-£234.49/MWh, net margin £3,480.25

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): 47 -- £3,700,029.75 -> £3,322,337.96 (10.2%); £3,700,029.90 -> £3,322,337.98 (10.2%); £3,700,030.05 -> £3,322,337.99 (10.2%); £3,700,030.20 -> £3,322,338.01 (10.2%); £3,700,030.36 -> £3,322,338.03 (10.2%); £3,700,030.51 -> £3,322,338.04 (10.2%); £3,700,030.66 -> £3,322,338.05 (10.2%); £3,700,030.82 -> £3,322,338.07 (10.2%); £3,700,030.97 -> £3,322,338.08 (10.2%); £3,700,031.13 -> £3,322,338.10 (10.2%); £3,700,031.29 -> £3,322,338.11 (10.2%); £3,700,031.44 -> £3,322,338.25 (10.2%); £3,700,031.60 -> £3,322,338.39 (10.2%); £3,700,031.77 -> £3,322,338.52 (10.2%); £3,700,031.96 -> £3,322,338.65 (10.2%); £3,700,032.17 -> £3,322,338.79 (10.2%); £3,700,032.39 -> £3,322,338.94 (10.2%); £3,700,032.63 -> £3,322,339.09 (10.2%); £3,700,032.90 -> £3,322,339.23 (10.2%); £3,700,033.15 -> £3,322,339.26 (10.2%); £3,700,033.41 -> £3,322,339.29 (10.2%); £3,700,033.66 -> £3,322,339.31 (10.2%); £3,700,033.93 -> £3,322,339.34 (10.2%); £3,700,034.19 -> £3,322,339.37 (10.2%); £3,700,034.45 -> £3,322,339.39 (10.2%); £3,700,034.72 -> £3,322,339.42 (10.2%); £3,700,034.98 -> £3,322,339.44 (10.2%); £3,700,035.24 -> £3,322,339.47 (10.2%); £3,700,035.50 -> £3,322,339.49 (10.2%); £3,700,035.75 -> £3,322,339.52 (10.2%); £3,700,036.01 -> £3,322,339.54 (10.2%); £3,700,036.26 -> £3,322,339.57 (10.2%); £3,700,036.52 -> £3,322,339.71 (10.2%); £3,700,036.78 -> £3,322,339.86 (10.2%); £3,700,037.04 -> £3,322,340.01 (10.2%); £3,700,037.30 -> £3,322,340.17 (10.2%); £3,700,037.56 -> £3,322,340.32 (10.2%); £3,700,037.82 -> £3,322,340.47 (10.2%); £3,700,038.09 -> £3,322,340.63 (10.2%); £3,700,038.35 -> £3,322,340.78 (10.2%); £3,700,038.61 -> £3,322,340.92 (10.2%); £3,700,038.87 -> £3,322,341.06 (10.2%); £3,700,039.13 -> £3,322,341.20 (10.2%); £3,700,039.39 -> £3,322,341.23 (10.2%); £3,700,039.65 -> £3,322,341.25 (10.2%); £3,700,039.89 -> £3,322,341.27 (10.2%); £3,700,040.11 -> £3,322,341.29 (10.2%)
- Bills issued: 156, average clarity 0.805, average bill shock 30.4%, bad debt provision £14,208.77, avg complaint probability 4.9%
- Solvency signal: £302,031/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £381,882.85 vs. naked (unhedged) net margin: £1,222,570.40
- hedging cost £840,687.55 vs. a fully unhedged book (commodity-only: actual net £381,882.85 vs. naked net £1,222,570.40)
  - C2_2: actual £828.99 vs. naked £2,421.10 -- hedging cost £1,592.11
  - C4: actual £313.86 vs. naked £700.05 -- hedging cost £386.18
  - C4g: actual £529.39 vs. naked £1,048.79 -- hedging cost £519.40
  - C5_2: actual £1,196.47 vs. naked £3,270.66 -- hedging cost £2,074.19
  - C6: actual £1,390.21 vs. naked £5,058.21 -- hedging cost £3,668.00
  - C7: actual £493.58 vs. naked £1,989.47 -- hedging cost £1,495.89
  - C8: actual £140.61 vs. naked £1,972.23 -- hedging cost £1,831.62
  - C9: actual £626.00 vs. naked £2,129.64 -- hedging cost £1,503.64
  - C_IC1: actual £141,576.45 vs. naked £284,450.26 -- hedging cost £142,873.81
  - C_IC2: actual £94,108.05 vs. naked £162,159.80 -- hedging cost £68,051.75
  - C_IC3: actual £128,327.22 vs. naked £402,135.26 -- hedging cost £273,808.05
  - C_IC3g: actual £8,660.26 vs. naked £123,107.25 -- hedging cost £114,446.99
  - C_IC4: actual £3,691.75 vs. naked £232,127.67 -- hedging cost £228,435.92

**Year narrative:** 2023 produced a net gain of £131,845.43 across 13 accounts. The risk committee intervened 4 time(s), raising hedge fractions in response to elevated VaR. 49 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £337,194.05 (gross £1,260,411.49, capital £9,532.69)
  - Electricity: gross £1,135,997.61, capital £9,509.29, net £328,112.21
  - Gas: gross £124,413.88, capital £23.40, net £9,081.83
- Treasury at year end: £3,703,825.02
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.91 (avg 0.91), C5_2 0.87 (avg 0.87), C7 0.90 (avg 0.90), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89), C_IC1 0.85 (avg 0.87), C_IC2 0.85 (avg 0.87), C_IC3 0.94 (avg 0.94), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2024-06-28 period 31, net margin £-26.25

**Customer Book**

- Active accounts: 13 (C2_2, C4, C4g, C5_2, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 2, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: C6, C4
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2024): £366,666.64
  - By billing account: C1 £4,503.71, C2 £4,686.91, C2_2 £2,966.09, C3 £4,871.42, C4 £3,295.44, C5 £10,452.79, C5_2 £2,987.03, C6 £16,599.24, C7 £5,957.33, C8 £7,915.19, C9 £8,233.32, C_IC1 £1,409,766.99, C_IC2 £664,180.47, C_IC3 £2,166,612.23, C_IC4 £1,186,971.47
- Bill shock events (>=20%): 37 -- C7 2024-02-29 (26%); C7 2024-05-31 (36%); C7 2024-09-30 (32%); C7 2024-10-31 (36%); C7 2024-11-30 (47%); C8 2024-02-29 (23%); C8 2024-04-30 (33%); C8 2024-05-31 (48%); C8 2024-07-31 (25%); C8 2024-09-30 (67%); C8 2024-10-31 (34%); C8 2024-11-30 (59%); C9 2024-05-31 (48%); C9 2024-07-31 (28%); C9 2024-09-30 (52%); C9 2024-10-31 (22%); C9 2024-11-30 (46%); C4 2024-04-30 (30%); C4g 2024-02-29 (27%); C4g 2024-05-31 (39%); C4g 2024-07-31 (24%); C4g 2024-09-28 (45%); C_IC1 2024-07-31 (33%); C_IC1 2024-08-31 (65%); C_IC2 2024-06-30 (49%); C_IC2 2024-07-31 (107%); C2_2 2024-02-29 (22%); C2_2 2024-04-30 (47%); C2_2 2024-05-31 (46%); C2_2 2024-07-31 (24%); C2_2 2024-09-30 (59%); C2_2 2024-10-31 (33%); C2_2 2024-11-30 (55%); C5_2 2024-02-29 (21%); C5_2 2024-05-31 (24%); C5_2 2024-10-31 (25%); C5_2 2024-11-30 (34%)
- Churn risk (accounts renewing in 2024): 8 at risk (≥20% churn prob): C2_2 23%, C4 38%, C6 26%, C7 29%, C_IC1 29%, C_IC2 32%, C_IC3 41%, C_IC4 20%

**Pricing & Margin**

- C2_2 (electricity): tariff £201.26-£350.04/MWh, net margin £429.86
- C4 (electricity): tariff £249.30/MWh, net margin £235.12
- C4g (gas): tariff £66.00/MWh, net margin £396.91
- C5_2 (electricity): tariff £253.01-£269.33/MWh, net margin £1,195.20
- C6 (electricity): tariff £332.32/MWh, net margin £484.88
- C7 (electricity): tariff £165.00-£366.47/MWh, net margin £492.80
- C8 (electricity): tariff £161.95-£397.50/MWh, net margin £291.33
- C9 (electricity): tariff £165.00-£367.64/MWh, net margin £560.36
- C_IC1 (electricity): tariff £-98.58-£330.68/MWh, net margin £123,481.08
- C_IC2 (electricity): tariff £-106.92-£354.92/MWh, net margin £68,786.62
- C_IC3 (electricity): tariff £88.78-£182.80/MWh, net margin £128,455.85
- C_IC3g (gas): tariff £54.85-£56.57/MWh, net margin £8,684.92
- C_IC4 (electricity): tariff £104.06-£193.21/MWh, net margin £3,699.12

**Portfolio Health**

- Capital cost ratio: 0.8% of gross
- Treasury drawdown events (>=10% threshold): 4271 -- £3,700,040.49 -> £3,322,341.33 (10.2%); £3,700,040.66 -> £3,322,341.35 (10.2%); £3,700,040.83 -> £3,322,341.37 (10.2%); £3,700,041.01 -> £3,322,341.38 (10.2%); £3,700,041.18 -> £3,322,341.40 (10.2%); £3,700,041.35 -> £3,322,341.41 (10.2%); £3,700,041.53 -> £3,322,341.43 (10.2%); £3,700,041.70 -> £3,322,341.45 (10.2%); £3,700,041.87 -> £3,322,341.46 (10.2%); £3,700,042.05 -> £3,322,341.48 (10.2%); £3,700,042.22 -> £3,322,341.50 (10.2%); £3,700,042.40 -> £3,322,341.64 (10.2%); £3,700,042.56 -> £3,322,341.79 (10.2%); £3,700,042.76 -> £3,322,341.95 (10.2%); £3,700,042.96 -> £3,322,342.10 (10.2%); £3,700,043.19 -> £3,322,342.27 (10.2%); £3,700,043.43 -> £3,322,342.43 (10.2%); £3,700,043.69 -> £3,322,342.58 (10.2%); £3,700,043.98 -> £3,322,342.73 (10.2%); £3,700,044.26 -> £3,322,342.76 (10.2%); £3,700,044.55 -> £3,322,342.78 (10.2%); £3,700,044.84 -> £3,322,342.80 (10.2%); £3,700,045.14 -> £3,322,342.83 (10.2%); £3,700,045.42 -> £3,322,342.85 (10.2%); £3,700,045.71 -> £3,322,342.88 (10.2%); £3,700,046.00 -> £3,322,342.90 (10.2%); £3,700,046.28 -> £3,322,342.92 (10.2%); £3,700,046.56 -> £3,322,342.95 (10.2%); £3,700,046.83 -> £3,322,342.97 (10.2%); £3,700,047.11 -> £3,322,342.99 (10.2%); £3,700,047.40 -> £3,322,343.02 (10.2%); £3,700,047.69 -> £3,322,343.05 (10.2%); £3,700,047.97 -> £3,322,343.22 (10.2%); £3,700,048.25 -> £3,322,343.38 (10.2%); £3,700,048.47 -> £3,322,343.54 (10.2%); £3,700,048.69 -> £3,322,343.71 (10.2%); £3,700,048.91 -> £3,322,343.88 (10.2%); £3,700,049.21 -> £3,322,344.06 (10.2%); £3,700,049.50 -> £3,322,344.23 (10.2%); £3,700,049.78 -> £3,322,344.40 (10.2%); £3,700,050.07 -> £3,322,344.57 (10.2%); £3,700,050.35 -> £3,322,344.74 (10.2%); £3,700,050.65 -> £3,322,344.91 (10.2%); £3,700,050.94 -> £3,322,344.94 (10.2%); £3,700,051.23 -> £3,322,344.97 (10.2%); £3,700,051.49 -> £3,322,344.99 (10.2%); £3,700,051.73 -> £3,322,345.02 (10.2%); £3,700,051.95 -> £3,322,345.04 (10.2%); £3,700,052.13 -> £3,322,345.06 (10.2%); £3,700,052.30 -> £3,322,345.08 (10.2%); £3,700,052.47 -> £3,322,345.09 (10.2%); £3,700,052.63 -> £3,322,345.11 (10.2%); £3,700,052.81 -> £3,322,345.13 (10.2%); £3,700,052.97 -> £3,322,345.15 (10.2%); £3,700,053.15 -> £3,322,345.16 (10.2%); £3,700,053.32 -> £3,322,345.18 (10.2%); £3,700,053.49 -> £3,322,345.20 (10.2%); £3,700,053.66 -> £3,322,345.21 (10.2%); £3,700,053.83 -> £3,322,345.23 (10.2%); £3,700,054.00 -> £3,322,345.36 (10.2%); £3,700,054.17 -> £3,322,345.48 (10.2%); £3,700,054.35 -> £3,322,345.61 (10.2%); £3,700,054.56 -> £3,322,345.75 (10.2%); £3,700,054.78 -> £3,322,345.88 (10.2%); £3,700,055.02 -> £3,322,346.02 (10.2%); £3,700,055.27 -> £3,322,346.15 (10.2%); £3,700,055.55 -> £3,322,346.28 (10.2%); £3,700,055.83 -> £3,322,346.31 (10.2%); £3,700,056.11 -> £3,322,346.33 (10.2%); £3,700,056.39 -> £3,322,346.36 (10.2%); £3,700,056.68 -> £3,322,346.38 (10.2%); £3,700,056.96 -> £3,322,346.41 (10.2%); £3,700,057.23 -> £3,322,346.43 (10.2%); £3,700,057.51 -> £3,322,346.45 (10.2%); £3,700,057.79 -> £3,322,346.48 (10.2%); £3,700,058.07 -> £3,322,346.50 (10.2%); £3,700,058.34 -> £3,322,346.52 (10.2%); £3,700,058.62 -> £3,322,346.55 (10.2%); £3,700,058.89 -> £3,322,346.57 (10.2%); £3,700,059.18 -> £3,322,346.60 (10.2%); £3,700,059.38 -> £3,322,346.73 (10.2%); £3,700,059.60 -> £3,322,346.87 (10.2%); £3,700,059.81 -> £3,322,347.00 (10.2%); £3,700,060.02 -> £3,322,347.14 (10.2%); £3,700,060.24 -> £3,322,347.28 (10.2%); £3,700,060.45 -> £3,322,347.41 (10.2%); £3,700,060.66 -> £3,322,347.55 (10.2%); £3,700,060.94 -> £3,322,347.68 (10.2%); £3,700,061.23 -> £3,322,347.82 (10.2%); £3,700,061.50 -> £3,322,347.96 (10.2%); £3,700,061.79 -> £3,322,348.09 (10.2%); £3,700,062.07 -> £3,322,348.12 (10.2%); £3,700,062.36 -> £3,322,348.15 (10.2%); £3,700,062.62 -> £3,322,348.17 (10.2%); £3,700,062.85 -> £3,322,348.20 (10.2%); £3,700,063.07 -> £3,322,348.22 (10.2%); £3,700,063.24 -> £3,322,348.23 (10.2%); £3,700,063.41 -> £3,322,348.25 (10.2%); £3,700,063.58 -> £3,322,348.27 (10.2%); £3,700,063.75 -> £3,322,348.29 (10.2%); £3,700,063.92 -> £3,322,348.30 (10.2%); £3,700,064.09 -> £3,322,348.32 (10.2%); £3,700,064.26 -> £3,322,348.34 (10.2%); £3,700,064.42 -> £3,322,348.35 (10.2%); £3,700,064.59 -> £3,322,348.37 (10.2%); £3,700,064.76 -> £3,322,348.39 (10.2%); £3,700,064.94 -> £3,322,348.40 (10.2%); £3,700,065.11 -> £3,322,348.55 (10.2%); £3,700,065.28 -> £3,322,348.70 (10.2%); £3,700,065.46 -> £3,322,348.85 (10.2%); £3,700,065.67 -> £3,322,349.02 (10.2%); £3,700,065.90 -> £3,322,349.18 (10.2%); £3,700,066.14 -> £3,322,349.33 (10.2%); £3,700,066.41 -> £3,322,349.47 (10.2%); £3,700,066.69 -> £3,322,349.61 (10.2%); £3,700,066.97 -> £3,322,349.64 (10.2%); £3,700,067.25 -> £3,322,349.66 (10.2%); £3,700,067.53 -> £3,322,349.69 (10.2%); £3,700,067.82 -> £3,322,349.71 (10.2%); £3,700,068.11 -> £3,322,349.73 (10.2%); £3,700,068.41 -> £3,322,349.76 (10.2%); £3,700,068.69 -> £3,322,349.78 (10.2%); £3,700,068.98 -> £3,322,349.80 (10.2%); £3,700,069.25 -> £3,322,349.83 (10.2%); £3,700,069.53 -> £3,322,349.85 (10.2%); £3,700,069.82 -> £3,322,349.87 (10.2%); £3,700,070.09 -> £3,322,349.90 (10.2%); £3,700,070.37 -> £3,322,349.93 (10.2%); £3,700,070.65 -> £3,322,350.08 (10.2%); £3,700,070.87 -> £3,322,350.25 (10.2%); £3,700,071.15 -> £3,322,350.40 (10.2%); £3,700,071.36 -> £3,322,350.56 (10.2%); £3,700,071.57 -> £3,322,350.72 (10.2%); £3,700,071.78 -> £3,322,350.87 (10.2%); £3,700,072.00 -> £3,322,351.03 (10.2%); £3,700,072.28 -> £3,322,351.19 (10.2%); £3,700,072.55 -> £3,322,351.35 (10.2%); £3,700,072.84 -> £3,322,351.51 (10.2%); £3,700,073.11 -> £3,322,351.66 (10.2%); £3,700,073.40 -> £3,322,351.69 (10.2%); £3,700,073.69 -> £3,322,351.72 (10.2%); £3,700,073.94 -> £3,322,351.74 (10.2%); £3,700,074.18 -> £3,322,351.76 (10.2%); £3,700,074.40 -> £3,322,351.78 (10.2%); £3,700,074.56 -> £3,322,351.80 (10.2%); £3,700,074.73 -> £3,322,351.82 (10.2%); £3,700,074.89 -> £3,322,351.84 (10.2%); £3,700,075.06 -> £3,322,351.85 (10.2%); £3,700,075.23 -> £3,322,351.87 (10.2%); £3,700,075.40 -> £3,322,351.89 (10.2%); £3,700,075.57 -> £3,322,351.90 (10.2%); £3,700,075.73 -> £3,322,351.92 (10.2%); £3,700,075.90 -> £3,322,351.94 (10.2%); £3,700,076.07 -> £3,322,351.95 (10.2%); £3,700,076.24 -> £3,322,351.97 (10.2%); £3,700,076.41 -> £3,322,352.14 (10.2%); £3,700,076.58 -> £3,322,352.31 (10.2%); £3,700,076.77 -> £3,322,352.48 (10.2%); £3,700,076.97 -> £3,322,352.66 (10.2%); £3,700,077.19 -> £3,322,352.83 (10.2%); £3,700,077.43 -> £3,322,353.00 (10.2%); £3,700,077.69 -> £3,322,353.18 (10.2%); £3,700,077.97 -> £3,322,353.35 (10.2%); £3,700,078.24 -> £3,322,353.37 (10.2%); £3,700,078.53 -> £3,322,353.40 (10.2%); £3,700,078.80 -> £3,322,353.42 (10.2%); £3,700,079.08 -> £3,322,353.45 (10.2%); £3,700,079.36 -> £3,322,353.47 (10.2%); £3,700,079.63 -> £3,322,353.49 (10.2%); £3,700,079.91 -> £3,322,353.52 (10.2%); £3,700,080.19 -> £3,322,353.54 (10.2%); £3,700,080.47 -> £3,322,353.56 (10.2%); £3,700,080.74 -> £3,322,353.59 (10.2%); £3,700,081.03 -> £3,322,353.61 (10.2%); £3,700,081.30 -> £3,322,353.64 (10.2%); £3,700,081.58 -> £3,322,353.66 (10.2%); £3,700,081.79 -> £3,322,353.84 (10.2%); £3,700,082.06 -> £3,322,354.02 (10.2%); £3,700,082.34 -> £3,322,354.19 (10.2%); £3,700,082.54 -> £3,322,354.37 (10.2%); £3,700,082.81 -> £3,322,354.55 (10.2%); £3,700,083.09 -> £3,322,354.72 (10.2%); £3,700,083.31 -> £3,322,354.89 (10.2%); £3,700,083.59 -> £3,322,355.06 (10.2%); £3,700,083.86 -> £3,322,355.24 (10.2%); £3,700,084.15 -> £3,322,355.40 (10.2%); £3,700,084.42 -> £3,322,355.58 (10.2%); £3,700,084.71 -> £3,322,355.60 (10.2%); £3,700,084.98 -> £3,322,355.63 (10.2%); £3,700,085.24 -> £3,322,355.66 (10.2%); £3,700,085.47 -> £3,322,355.68 (10.2%); £3,700,085.69 -> £3,322,355.70 (10.2%); £3,700,085.85 -> £3,322,355.72 (10.2%); £3,700,086.01 -> £3,322,355.73 (10.2%); £3,700,086.18 -> £3,322,355.75 (10.2%); £3,700,086.34 -> £3,322,355.77 (10.2%); £3,700,086.49 -> £3,322,355.78 (10.2%); £3,700,086.65 -> £3,322,355.80 (10.2%); £3,700,086.82 -> £3,322,355.82 (10.2%); £3,700,086.97 -> £3,322,355.83 (10.2%); £3,700,087.14 -> £3,322,355.85 (10.2%); £3,700,087.31 -> £3,322,355.87 (10.2%); £3,700,087.47 -> £3,322,355.89 (10.2%); £3,700,087.63 -> £3,322,356.07 (10.2%); £3,700,087.79 -> £3,322,356.25 (10.2%); £3,700,087.97 -> £3,322,356.44 (10.2%); £3,700,088.17 -> £3,322,356.64 (10.2%); £3,700,088.38 -> £3,322,356.83 (10.2%); £3,700,088.61 -> £3,322,357.02 (10.2%); £3,700,088.87 -> £3,322,357.20 (10.2%); £3,700,089.14 -> £3,322,357.38 (10.2%); £3,700,089.42 -> £3,322,357.41 (10.2%); £3,700,089.68 -> £3,322,357.43 (10.2%); £3,700,089.95 -> £3,322,357.46 (10.2%); £3,700,090.22 -> £3,322,357.48 (10.2%); £3,700,090.49 -> £3,322,357.50 (10.2%); £3,700,090.76 -> £3,322,357.53 (10.2%); £3,700,091.04 -> £3,322,357.55 (10.2%); £3,700,091.31 -> £3,322,357.58 (10.2%); £3,700,091.57 -> £3,322,357.60 (10.2%); £3,700,091.83 -> £3,322,357.62 (10.2%); £3,700,092.10 -> £3,322,357.65 (10.2%); £3,700,092.36 -> £3,322,357.67 (10.2%); £3,700,092.64 -> £3,322,357.70 (10.2%); £3,700,092.84 -> £3,322,357.88 (10.2%); £3,700,093.04 -> £3,322,358.07 (10.2%); £3,700,093.25 -> £3,322,358.26 (10.2%); £3,700,093.45 -> £3,322,358.46 (10.2%); £3,700,093.72 -> £3,322,358.64 (10.2%); £3,700,093.92 -> £3,322,358.83 (10.2%); £3,700,094.12 -> £3,322,359.02 (10.2%); £3,700,094.39 -> £3,322,359.20 (10.2%); £3,700,094.66 -> £3,322,359.39 (10.2%); £3,700,094.92 -> £3,322,359.58 (10.2%); £3,700,095.19 -> £3,322,359.77 (10.2%); £3,700,095.45 -> £3,322,359.80 (10.2%); £3,700,095.72 -> £3,322,359.83 (10.2%); £3,700,095.98 -> £3,322,359.85 (10.2%); £3,700,096.21 -> £3,322,359.87 (10.2%); £3,700,096.42 -> £3,322,359.89 (10.2%); £3,700,096.56 -> £3,322,359.91 (10.2%); £3,700,096.71 -> £3,322,359.93 (10.2%); £3,700,096.85 -> £3,322,359.95 (10.2%); £3,700,097.00 -> £3,322,359.97 (10.2%); £3,700,097.15 -> £3,322,359.98 (10.2%); £3,700,097.29 -> £3,322,360.00 (10.2%); £3,700,097.42 -> £3,322,360.02 (10.2%); £3,700,097.56 -> £3,322,360.03 (10.2%); £3,700,097.70 -> £3,322,360.05 (10.2%); £3,700,097.84 -> £3,322,360.07 (10.2%); £3,700,097.98 -> £3,322,360.09 (10.2%); £3,700,098.12 -> £3,322,360.31 (10.2%); £3,700,098.26 -> £3,322,360.53 (10.2%); £3,700,098.42 -> £3,322,360.76 (10.2%); £3,700,098.59 -> £3,322,360.99 (10.2%); £3,700,098.78 -> £3,322,361.22 (10.2%); £3,700,098.99 -> £3,322,361.46 (10.2%); £3,700,099.21 -> £3,322,361.69 (10.2%); £3,700,099.44 -> £3,322,361.93 (10.2%); £3,700,099.67 -> £3,322,361.95 (10.2%); £3,700,099.91 -> £3,322,361.98 (10.2%); £3,700,100.14 -> £3,322,362.01 (10.2%); £3,700,100.38 -> £3,322,362.03 (10.2%); £3,700,100.62 -> £3,322,362.06 (10.2%); £3,700,100.86 -> £3,322,362.09 (10.2%); £3,700,101.08 -> £3,322,362.11 (10.2%); £3,700,101.33 -> £3,322,362.14 (10.2%); £3,700,101.57 -> £3,322,362.16 (10.2%); £3,700,101.81 -> £3,322,362.19 (10.2%); £3,700,102.05 -> £3,322,362.21 (10.2%); £3,700,102.29 -> £3,322,362.24 (10.2%); £3,700,102.53 -> £3,322,362.27 (10.2%); £3,700,102.75 -> £3,322,362.48 (10.2%); £3,700,102.93 -> £3,322,362.70 (10.2%); £3,700,103.10 -> £3,322,362.93 (10.2%); £3,700,103.28 -> £3,322,363.15 (10.2%); £3,700,103.45 -> £3,322,363.38 (10.2%); £3,700,103.63 -> £3,322,363.60 (10.2%); £3,700,103.81 -> £3,322,363.83 (10.2%); £3,700,104.04 -> £3,322,364.06 (10.2%); £3,700,104.27 -> £3,322,364.29 (10.2%); £3,700,104.50 -> £3,322,364.51 (10.2%); £3,700,104.74 -> £3,322,364.74 (10.2%); £3,700,104.97 -> £3,322,364.77 (10.2%); £3,700,105.20 -> £3,322,364.79 (10.2%); £3,700,105.42 -> £3,322,364.82 (10.2%); £3,700,105.62 -> £3,322,364.84 (10.2%); £3,700,105.81 -> £3,322,364.86 (10.2%); £3,700,105.94 -> £3,322,364.88 (10.2%); £3,700,106.08 -> £3,322,364.90 (10.2%); £3,700,106.23 -> £3,322,364.92 (10.2%); £3,700,106.37 -> £3,322,364.94 (10.2%); £3,700,106.51 -> £3,322,364.96 (10.2%); £3,700,106.64 -> £3,322,364.97 (10.2%); £3,700,106.78 -> £3,322,364.99 (10.2%); £3,700,106.93 -> £3,322,365.01 (10.2%); £3,700,107.07 -> £3,322,365.02 (10.2%); £3,700,107.20 -> £3,322,365.04 (10.2%); £3,700,107.34 -> £3,322,365.06 (10.2%); £3,700,107.48 -> £3,322,365.27 (10.2%); £3,700,107.62 -> £3,322,365.49 (10.2%); £3,700,107.77 -> £3,322,365.71 (10.2%); £3,700,107.95 -> £3,322,365.93 (10.2%); £3,700,108.14 -> £3,322,366.15 (10.2%); £3,700,108.34 -> £3,322,366.37 (10.2%); £3,700,108.56 -> £3,322,366.59 (10.2%); £3,700,108.79 -> £3,322,366.81 (10.2%); £3,700,109.04 -> £3,322,366.84 (10.2%); £3,700,109.26 -> £3,322,366.87 (10.2%); £3,700,109.50 -> £3,322,366.90 (10.2%); £3,700,109.72 -> £3,322,366.93 (10.2%); £3,700,109.95 -> £3,322,366.96 (10.2%); £3,700,110.18 -> £3,322,367.00 (10.2%); £3,700,110.41 -> £3,322,367.03 (10.2%); £3,700,110.64 -> £3,322,367.06 (10.2%); £3,700,110.87 -> £3,322,367.08 (10.2%); £3,700,111.11 -> £3,322,367.11 (10.2%); £3,700,111.34 -> £3,322,367.14 (10.2%); £3,700,111.57 -> £3,322,367.17 (10.2%); £3,700,111.80 -> £3,322,367.20 (10.2%); £3,700,111.98 -> £3,322,367.41 (10.2%); £3,700,112.15 -> £3,322,367.63 (10.2%); £3,700,112.32 -> £3,322,367.85 (10.2%); £3,700,112.49 -> £3,322,368.08 (10.2%); £3,700,112.73 -> £3,322,368.30 (10.2%); £3,700,112.91 -> £3,322,368.52 (10.2%); £3,700,113.08 -> £3,322,368.75 (10.2%); £3,700,113.32 -> £3,322,368.97 (10.2%); £3,700,113.55 -> £3,322,369.20 (10.2%); £3,700,113.79 -> £3,322,369.41 (10.2%); £3,700,114.02 -> £3,322,369.64 (10.2%); £3,700,114.25 -> £3,322,369.67 (10.2%); £3,700,114.48 -> £3,322,369.69 (10.2%); £3,700,114.69 -> £3,322,369.72 (10.2%); £3,700,114.89 -> £3,322,369.74 (10.2%); £3,700,115.08 -> £3,322,369.76 (10.2%); £3,700,115.24 -> £3,322,369.78 (10.2%); £3,700,115.39 -> £3,322,369.80 (10.2%); £3,700,115.54 -> £3,322,369.81 (10.2%); £3,700,115.69 -> £3,322,369.83 (10.2%); £3,700,115.84 -> £3,322,369.85 (10.2%); £3,700,116.00 -> £3,322,369.86 (10.2%); £3,700,116.15 -> £3,322,369.88 (10.2%); £3,700,116.31 -> £3,322,369.90 (10.2%); £3,700,116.46 -> £3,322,369.91 (10.2%); £3,700,116.62 -> £3,322,369.93 (10.2%); £3,700,116.77 -> £3,322,369.95 (10.2%); £3,700,116.92 -> £3,322,370.15 (10.2%); £3,700,117.08 -> £3,322,370.37 (10.2%); £3,700,117.25 -> £3,322,370.58 (10.2%); £3,700,117.43 -> £3,322,370.79 (10.2%); £3,700,117.64 -> £3,322,371.02 (10.2%); £3,700,117.86 -> £3,322,371.24 (10.2%); £3,700,118.09 -> £3,322,371.46 (10.2%); £3,700,118.34 -> £3,322,371.67 (10.2%); £3,700,118.59 -> £3,322,371.70 (10.2%); £3,700,118.84 -> £3,322,371.72 (10.2%); £3,700,119.11 -> £3,322,371.75 (10.2%); £3,700,119.36 -> £3,322,371.77 (10.2%); £3,700,119.61 -> £3,322,371.79 (10.2%); £3,700,119.87 -> £3,322,371.82 (10.2%); £3,700,120.13 -> £3,322,371.84 (10.2%); £3,700,120.40 -> £3,322,371.86 (10.2%); £3,700,120.65 -> £3,322,371.89 (10.2%); £3,700,120.91 -> £3,322,371.91 (10.2%); £3,700,121.17 -> £3,322,371.93 (10.2%); £3,700,121.42 -> £3,322,371.96 (10.2%); £3,700,121.68 -> £3,322,371.99 (10.2%); £3,700,121.95 -> £3,322,372.21 (10.2%); £3,700,122.21 -> £3,322,372.43 (10.2%); £3,700,122.46 -> £3,322,372.65 (10.2%); £3,700,122.71 -> £3,322,372.88 (10.2%); £3,700,122.96 -> £3,322,373.10 (10.2%); £3,700,123.21 -> £3,322,373.32 (10.2%); £3,700,123.40 -> £3,322,373.54 (10.2%); £3,700,123.65 -> £3,322,373.76 (10.2%); £3,700,123.90 -> £3,322,373.98 (10.2%); £3,700,124.15 -> £3,322,374.20 (10.2%); £3,700,124.41 -> £3,322,374.42 (10.2%); £3,700,124.66 -> £3,322,374.45 (10.2%); £3,700,124.92 -> £3,322,374.47 (10.2%); £3,700,125.15 -> £3,322,374.50 (10.2%); £3,700,125.37 -> £3,322,374.52 (10.2%); £3,700,125.58 -> £3,322,374.54 (10.2%); £3,700,125.73 -> £3,322,374.56 (10.2%); £3,700,125.88 -> £3,322,374.58 (10.2%); £3,700,126.03 -> £3,322,374.59 (10.2%); £3,700,126.18 -> £3,322,374.61 (10.2%); £3,700,126.34 -> £3,322,374.63 (10.2%); £3,700,126.49 -> £3,322,374.64 (10.2%); £3,700,126.64 -> £3,322,374.66 (10.2%); £3,700,126.79 -> £3,322,374.68 (10.2%); £3,700,126.95 -> £3,322,374.69 (10.2%); £3,700,127.10 -> £3,322,374.71 (10.2%); £3,700,127.26 -> £3,322,374.73 (10.2%); £3,700,127.41 -> £3,322,374.93 (10.2%); £3,700,127.56 -> £3,322,375.14 (10.2%); £3,700,127.72 -> £3,322,375.35 (10.2%); £3,700,127.90 -> £3,322,375.57 (10.2%); £3,700,128.11 -> £3,322,375.78 (10.2%); £3,700,128.33 -> £3,322,376.00 (10.2%); £3,700,128.56 -> £3,322,376.21 (10.2%); £3,700,128.81 -> £3,322,376.42 (10.2%); £3,700,129.06 -> £3,322,376.45 (10.2%); £3,700,129.31 -> £3,322,376.47 (10.2%); £3,700,129.57 -> £3,322,376.49 (10.2%); £3,700,129.83 -> £3,322,376.52 (10.2%); £3,700,130.09 -> £3,322,376.54 (10.2%); £3,700,130.35 -> £3,322,376.57 (10.2%); £3,700,130.60 -> £3,322,376.59 (10.2%); £3,700,130.86 -> £3,322,376.61 (10.2%); £3,700,131.11 -> £3,322,376.64 (10.2%); £3,700,131.37 -> £3,322,376.66 (10.2%); £3,700,131.63 -> £3,322,376.68 (10.2%); £3,700,131.88 -> £3,322,376.71 (10.2%); £3,700,132.13 -> £3,322,376.74 (10.2%); £3,700,132.31 -> £3,322,376.94 (10.2%); £3,700,132.50 -> £3,322,377.16 (10.2%); £3,700,132.75 -> £3,322,377.37 (10.2%); £3,700,132.94 -> £3,322,377.58 (10.2%); £3,700,133.13 -> £3,322,377.80 (10.2%); £3,700,133.39 -> £3,322,378.01 (10.2%); £3,700,133.64 -> £3,322,378.23 (10.2%); £3,700,133.90 -> £3,322,378.44 (10.2%); £3,700,134.16 -> £3,322,378.65 (10.2%); £3,700,134.41 -> £3,322,378.86 (10.2%); £3,700,134.67 -> £3,322,379.07 (10.2%); £3,700,134.92 -> £3,322,379.10 (10.2%); £3,700,135.17 -> £3,322,379.13 (10.2%); £3,700,135.41 -> £3,322,379.15 (10.2%); £3,700,135.62 -> £3,322,379.18 (10.2%); £3,700,135.82 -> £3,322,379.20 (10.2%); £3,700,135.97 -> £3,322,379.22 (10.2%); £3,700,136.12 -> £3,322,379.23 (10.2%); £3,700,136.27 -> £3,322,379.25 (10.2%); £3,700,136.43 -> £3,322,379.27 (10.2%); £3,700,136.58 -> £3,322,379.28 (10.2%); £3,700,136.73 -> £3,322,379.30 (10.2%); £3,700,136.88 -> £3,322,379.32 (10.2%); £3,700,137.03 -> £3,322,379.33 (10.2%); £3,700,137.18 -> £3,322,379.35 (10.2%); £3,700,137.33 -> £3,322,379.37 (10.2%); £3,700,137.48 -> £3,322,379.39 (10.2%); £3,700,137.63 -> £3,322,379.57 (10.2%); £3,700,137.79 -> £3,322,379.74 (10.2%); £3,700,137.95 -> £3,322,379.92 (10.2%); £3,700,138.14 -> £3,322,380.10 (10.2%); £3,700,138.33 -> £3,322,380.28 (10.2%); £3,700,138.56 -> £3,322,380.46 (10.2%); £3,700,138.80 -> £3,322,380.64 (10.2%); £3,700,139.04 -> £3,322,380.81 (10.2%); £3,700,139.30 -> £3,322,380.84 (10.2%); £3,700,139.54 -> £3,322,380.86 (10.2%); £3,700,139.80 -> £3,322,380.89 (10.2%); £3,700,140.05 -> £3,322,380.91 (10.2%); £3,700,140.30 -> £3,322,380.93 (10.2%); £3,700,140.55 -> £3,322,380.96 (10.2%); £3,700,140.82 -> £3,322,380.98 (10.2%); £3,700,141.07 -> £3,322,381.00 (10.2%); £3,700,141.32 -> £3,322,381.03 (10.2%); £3,700,141.58 -> £3,322,381.05 (10.2%); £3,700,141.83 -> £3,322,381.07 (10.2%); £3,700,142.08 -> £3,322,381.10 (10.2%); £3,700,142.32 -> £3,322,381.13 (10.2%); £3,700,142.58 -> £3,322,381.31 (10.2%); £3,700,142.76 -> £3,322,381.50 (10.2%); £3,700,143.02 -> £3,322,381.70 (10.2%); £3,700,143.27 -> £3,322,381.88 (10.2%); £3,700,143.47 -> £3,322,382.08 (10.2%); £3,700,143.71 -> £3,322,382.27 (10.2%); £3,700,143.89 -> £3,322,382.45 (10.2%); £3,700,144.15 -> £3,322,382.64 (10.2%); £3,700,144.40 -> £3,322,382.83 (10.2%); £3,700,144.65 -> £3,322,383.03 (10.2%); £3,700,144.90 -> £3,322,383.21 (10.2%); £3,700,145.15 -> £3,322,383.24 (10.2%); £3,700,145.39 -> £3,322,383.27 (10.2%); £3,700,145.63 -> £3,322,383.29 (10.2%); £3,700,145.84 -> £3,322,383.32 (10.2%); £3,700,146.04 -> £3,322,383.34 (10.2%); £3,700,146.19 -> £3,322,383.36 (10.2%); £3,700,146.34 -> £3,322,383.37 (10.2%); £3,700,146.48 -> £3,322,383.39 (10.2%); £3,700,146.64 -> £3,322,383.41 (10.2%); £3,700,146.78 -> £3,322,383.42 (10.2%); £3,700,146.94 -> £3,322,383.44 (10.2%); £3,700,147.09 -> £3,322,383.46 (10.2%); £3,700,147.24 -> £3,322,383.47 (10.2%); £3,700,147.39 -> £3,322,383.49 (10.2%); £3,700,147.53 -> £3,322,383.51 (10.2%); £3,700,147.69 -> £3,322,383.53 (10.2%); £3,700,147.84 -> £3,322,383.69 (10.2%); £3,700,147.98 -> £3,322,383.85 (10.2%); £3,700,148.15 -> £3,322,384.01 (10.2%); £3,700,148.33 -> £3,322,384.17 (10.2%); £3,700,148.53 -> £3,322,384.34 (10.2%); £3,700,148.74 -> £3,322,384.51 (10.2%); £3,700,148.97 -> £3,322,384.67 (10.2%); £3,700,149.22 -> £3,322,384.83 (10.2%); £3,700,149.48 -> £3,322,384.86 (10.2%); £3,700,149.72 -> £3,322,384.88 (10.2%); £3,700,149.97 -> £3,322,384.90 (10.2%); £3,700,150.23 -> £3,322,384.93 (10.2%); £3,700,150.47 -> £3,322,384.95 (10.2%); £3,700,150.72 -> £3,322,384.98 (10.2%); £3,700,150.96 -> £3,322,385.00 (10.2%); £3,700,151.20 -> £3,322,385.02 (10.2%); £3,700,151.45 -> £3,322,385.05 (10.2%); £3,700,151.70 -> £3,322,385.07 (10.2%); £3,700,151.95 -> £3,322,385.09 (10.2%); £3,700,152.20 -> £3,322,385.12 (10.2%); £3,700,152.45 -> £3,322,385.15 (10.2%); £3,700,152.64 -> £3,322,385.31 (10.2%); £3,700,152.82 -> £3,322,385.49 (10.2%); £3,700,153.01 -> £3,322,385.66 (10.2%); £3,700,153.19 -> £3,322,385.83 (10.2%); £3,700,153.38 -> £3,322,386.01 (10.2%); £3,700,153.56 -> £3,322,386.18 (10.2%); £3,700,153.75 -> £3,322,386.35 (10.2%); £3,700,153.99 -> £3,322,386.52 (10.2%); £3,700,154.24 -> £3,322,386.70 (10.2%); £3,700,154.50 -> £3,322,386.87 (10.2%); £3,700,154.75 -> £3,322,387.04 (10.2%); £3,700,155.00 -> £3,322,387.07 (10.2%); £3,700,155.24 -> £3,322,387.09 (10.2%); £3,700,155.47 -> £3,322,387.12 (10.2%); £3,700,155.68 -> £3,322,387.14 (10.2%); £3,700,155.87 -> £3,322,387.16 (10.2%); £3,700,156.02 -> £3,322,387.18 (10.2%); £3,700,156.18 -> £3,322,387.20 (10.2%); £3,700,156.32 -> £3,322,387.21 (10.2%); £3,700,156.47 -> £3,322,387.23 (10.2%); £3,700,156.61 -> £3,322,387.25 (10.2%); £3,700,156.76 -> £3,322,387.26 (10.2%); £3,700,156.91 -> £3,322,387.28 (10.2%); £3,700,157.05 -> £3,322,387.30 (10.2%); £3,700,157.20 -> £3,322,387.31 (10.2%); £3,700,157.35 -> £3,322,387.33 (10.2%); £3,700,157.50 -> £3,322,387.35 (10.2%); £3,700,157.65 -> £3,322,387.53 (10.2%); £3,700,157.80 -> £3,322,387.71 (10.2%); £3,700,157.96 -> £3,322,387.89 (10.2%); £3,700,158.14 -> £3,322,388.08 (10.2%); £3,700,158.34 -> £3,322,388.27 (10.2%); £3,700,158.55 -> £3,322,388.45 (10.2%); £3,700,158.78 -> £3,322,388.64 (10.2%); £3,700,159.03 -> £3,322,388.82 (10.2%); £3,700,159.26 -> £3,322,388.84 (10.2%); £3,700,159.50 -> £3,322,388.86 (10.2%); £3,700,159.75 -> £3,322,388.89 (10.2%); £3,700,160.00 -> £3,322,388.91 (10.2%); £3,700,160.24 -> £3,322,388.93 (10.2%); £3,700,160.50 -> £3,322,388.96 (10.2%); £3,700,160.74 -> £3,322,388.98 (10.2%); £3,700,160.98 -> £3,322,389.00 (10.2%); £3,700,161.22 -> £3,322,389.03 (10.2%); £3,700,161.46 -> £3,322,389.05 (10.2%); £3,700,161.71 -> £3,322,389.07 (10.2%); £3,700,161.95 -> £3,322,389.10 (10.2%); £3,700,162.19 -> £3,322,389.13 (10.2%); £3,700,162.38 -> £3,322,389.31 (10.2%); £3,700,162.56 -> £3,322,389.50 (10.2%); £3,700,162.75 -> £3,322,389.69 (10.2%); £3,700,162.93 -> £3,322,389.88 (10.2%); £3,700,163.11 -> £3,322,390.07 (10.2%); £3,700,163.29 -> £3,322,390.26 (10.2%); £3,700,163.48 -> £3,322,390.45 (10.2%); £3,700,163.72 -> £3,322,390.64 (10.2%); £3,700,163.97 -> £3,322,390.83 (10.2%); £3,700,164.22 -> £3,322,391.02 (10.2%); £3,700,164.46 -> £3,322,391.21 (10.2%); £3,700,164.71 -> £3,322,391.23 (10.2%); £3,700,164.96 -> £3,322,391.26 (10.2%); £3,700,165.19 -> £3,322,391.29 (10.2%); £3,700,165.40 -> £3,322,391.31 (10.2%); £3,700,165.60 -> £3,322,391.33 (10.2%); £3,700,165.72 -> £3,322,391.35 (10.2%); £3,700,165.86 -> £3,322,391.37 (10.2%); £3,700,165.98 -> £3,322,391.38 (10.2%); £3,700,166.11 -> £3,322,391.40 (10.2%); £3,700,166.24 -> £3,322,391.42 (10.2%); £3,700,166.37 -> £3,322,391.44 (10.2%); £3,700,166.50 -> £3,322,391.45 (10.2%); £3,700,166.63 -> £3,322,391.47 (10.2%); £3,700,166.75 -> £3,322,391.49 (10.2%); £3,700,166.88 -> £3,322,391.50 (10.2%); £3,700,167.01 -> £3,322,391.52 (10.2%); £3,700,167.14 -> £3,322,391.69 (10.2%); £3,700,167.27 -> £3,322,391.86 (10.2%); £3,700,167.41 -> £3,322,392.04 (10.2%); £3,700,167.57 -> £3,322,392.21 (10.2%); £3,700,167.74 -> £3,322,392.40 (10.2%); £3,700,167.92 -> £3,322,392.57 (10.2%); £3,700,168.12 -> £3,322,392.75 (10.2%); £3,700,168.33 -> £3,322,392.93 (10.2%); £3,700,168.54 -> £3,322,392.96 (10.2%); £3,700,168.75 -> £3,322,392.98 (10.2%); £3,700,168.96 -> £3,322,393.01 (10.2%); £3,700,169.17 -> £3,322,393.04 (10.2%); £3,700,169.38 -> £3,322,393.06 (10.2%); £3,700,169.60 -> £3,322,393.09 (10.2%); £3,700,169.81 -> £3,322,393.12 (10.2%); £3,700,170.02 -> £3,322,393.14 (10.2%); £3,700,170.24 -> £3,322,393.17 (10.2%); £3,700,170.45 -> £3,322,393.19 (10.2%); £3,700,170.66 -> £3,322,393.22 (10.2%); £3,700,170.87 -> £3,322,393.24 (10.2%); £3,700,171.09 -> £3,322,393.27 (10.2%); £3,700,171.25 -> £3,322,393.45 (10.2%); £3,700,171.41 -> £3,322,393.62 (10.2%); £3,700,171.57 -> £3,322,393.81 (10.2%); £3,700,171.73 -> £3,322,393.99 (10.2%); £3,700,171.89 -> £3,322,394.17 (10.2%); £3,700,172.04 -> £3,322,394.36 (10.2%); £3,700,172.25 -> £3,322,394.55 (10.2%); £3,700,172.47 -> £3,322,394.72 (10.2%); £3,700,172.69 -> £3,322,394.91 (10.2%); £3,700,172.90 -> £3,322,395.09 (10.2%); £3,700,173.11 -> £3,322,395.27 (10.2%); £3,700,173.32 -> £3,322,395.30 (10.2%); £3,700,173.54 -> £3,322,395.32 (10.2%); £3,700,173.73 -> £3,322,395.35 (10.2%); £3,700,173.91 -> £3,322,395.37 (10.2%); £3,700,174.07 -> £3,322,395.40 (10.2%); £3,700,174.20 -> £3,322,395.42 (10.2%); £3,700,174.33 -> £3,322,395.43 (10.2%); £3,700,174.45 -> £3,322,395.45 (10.2%); £3,700,174.57 -> £3,322,395.47 (10.2%); £3,700,174.70 -> £3,322,395.49 (10.2%); £3,700,174.83 -> £3,322,395.51 (10.2%); £3,700,174.96 -> £3,322,395.52 (10.2%); £3,700,175.08 -> £3,322,395.54 (10.2%); £3,700,175.21 -> £3,322,395.55 (10.2%); £3,700,175.34 -> £3,322,395.57 (10.2%); £3,700,175.46 -> £3,322,395.59 (10.2%); £3,700,175.59 -> £3,322,395.80 (10.2%); £3,700,175.71 -> £3,322,396.02 (10.2%); £3,700,175.86 -> £3,322,396.23 (10.2%); £3,700,176.01 -> £3,322,396.45 (10.2%); £3,700,176.19 -> £3,322,396.67 (10.2%); £3,700,176.37 -> £3,322,396.89 (10.2%); £3,700,176.57 -> £3,322,397.11 (10.2%); £3,700,176.77 -> £3,322,397.33 (10.2%); £3,700,176.99 -> £3,322,397.36 (10.2%); £3,700,177.19 -> £3,322,397.39 (10.2%); £3,700,177.40 -> £3,322,397.42 (10.2%); £3,700,177.62 -> £3,322,397.45 (10.2%); £3,700,177.84 -> £3,322,397.48 (10.2%); £3,700,178.04 -> £3,322,397.52 (10.2%); £3,700,178.25 -> £3,322,397.55 (10.2%); £3,700,178.46 -> £3,322,397.58 (10.2%); £3,700,178.68 -> £3,322,397.60 (10.2%); £3,700,178.88 -> £3,322,397.63 (10.2%); £3,700,179.09 -> £3,322,397.66 (10.2%); £3,700,179.30 -> £3,322,397.69 (10.2%); £3,700,179.51 -> £3,322,397.72 (10.2%); £3,700,179.67 -> £3,322,397.93 (10.2%); £3,700,179.83 -> £3,322,398.15 (10.2%); £3,700,180.00 -> £3,322,398.37 (10.2%); £3,700,180.15 -> £3,322,398.59 (10.2%); £3,700,180.31 -> £3,322,398.81 (10.2%); £3,700,180.48 -> £3,322,399.03 (10.2%); £3,700,180.63 -> £3,322,399.25 (10.2%); £3,700,180.85 -> £3,322,399.46 (10.2%); £3,700,181.07 -> £3,322,399.69 (10.2%); £3,700,181.27 -> £3,322,399.91 (10.2%); £3,700,181.49 -> £3,322,400.13 (10.2%); £3,700,181.70 -> £3,322,400.16 (10.2%); £3,700,181.90 -> £3,322,400.19 (10.2%); £3,700,182.10 -> £3,322,400.21 (10.2%); £3,700,182.28 -> £3,322,400.23 (10.2%); £3,700,182.45 -> £3,322,400.25 (10.2%); £3,700,182.60 -> £3,322,400.27 (10.2%); £3,700,182.74 -> £3,322,400.29 (10.2%); £3,700,182.89 -> £3,322,400.31 (10.2%); £3,700,183.04 -> £3,322,400.32 (10.2%); £3,700,183.18 -> £3,322,400.34 (10.2%); £3,700,183.33 -> £3,322,400.36 (10.2%); £3,700,183.47 -> £3,322,400.37 (10.2%); £3,700,183.62 -> £3,322,400.39 (10.2%); £3,700,183.77 -> £3,322,400.41 (10.2%); £3,700,183.91 -> £3,322,400.42 (10.2%); £3,700,184.05 -> £3,322,400.44 (10.2%); £3,700,184.20 -> £3,322,400.69 (10.2%); £3,700,184.34 -> £3,322,400.94 (10.2%); £3,700,184.50 -> £3,322,401.20 (10.2%); £3,700,184.68 -> £3,322,401.46 (10.2%); £3,700,184.86 -> £3,322,401.71 (10.2%); £3,700,185.07 -> £3,322,401.97 (10.2%); £3,700,185.29 -> £3,322,402.22 (10.2%); £3,700,185.53 -> £3,322,402.48 (10.2%); £3,700,185.77 -> £3,322,402.50 (10.2%); £3,700,186.02 -> £3,322,402.53 (10.2%); £3,700,186.26 -> £3,322,402.55 (10.2%); £3,700,186.51 -> £3,322,402.57 (10.2%); £3,700,186.75 -> £3,322,402.60 (10.2%); £3,700,186.99 -> £3,322,402.62 (10.2%); £3,700,187.23 -> £3,322,402.65 (10.2%); £3,700,187.47 -> £3,322,402.67 (10.2%); £3,700,187.71 -> £3,322,402.69 (10.2%); £3,700,187.96 -> £3,322,402.72 (10.2%); £3,700,188.20 -> £3,322,402.74 (10.2%); £3,700,188.45 -> £3,322,402.77 (10.2%); £3,700,188.68 -> £3,322,402.79 (10.2%); £3,700,188.87 -> £3,322,403.04 (10.2%); £3,700,189.05 -> £3,322,403.29 (10.2%); £3,700,189.24 -> £3,322,403.54 (10.2%); £3,700,189.42 -> £3,322,403.79 (10.2%); £3,700,189.60 -> £3,322,404.05 (10.2%); £3,700,189.78 -> £3,322,404.30 (10.2%); £3,700,189.95 -> £3,322,404.56 (10.2%); £3,700,190.20 -> £3,322,404.81 (10.2%); £3,700,190.43 -> £3,322,405.07 (10.2%); £3,700,190.67 -> £3,322,405.33 (10.2%); £3,700,190.91 -> £3,322,405.58 (10.2%); £3,700,191.16 -> £3,322,405.61 (10.2%); £3,700,191.40 -> £3,322,405.64 (10.2%); £3,700,191.62 -> £3,322,405.66 (10.2%); £3,700,191.83 -> £3,322,405.69 (10.2%); £3,700,192.02 -> £3,322,405.71 (10.2%); £3,700,192.16 -> £3,322,405.72 (10.2%); £3,700,192.31 -> £3,322,405.74 (10.2%); £3,700,192.45 -> £3,322,405.76 (10.2%); £3,700,192.59 -> £3,322,405.78 (10.2%); £3,700,192.73 -> £3,322,405.79 (10.2%); £3,700,192.88 -> £3,322,405.81 (10.2%); £3,700,193.01 -> £3,322,405.83 (10.2%); £3,700,193.15 -> £3,322,405.84 (10.2%); £3,700,193.30 -> £3,322,405.86 (10.2%); £3,700,193.44 -> £3,322,405.88 (10.2%); £3,700,193.59 -> £3,322,405.89 (10.2%); £3,700,193.73 -> £3,322,406.12 (10.2%); £3,700,193.88 -> £3,322,406.35 (10.2%); £3,700,194.04 -> £3,322,406.57 (10.2%); £3,700,194.22 -> £3,322,406.79 (10.2%); £3,700,194.40 -> £3,322,407.02 (10.2%); £3,700,194.62 -> £3,322,407.24 (10.2%); £3,700,194.84 -> £3,322,407.47 (10.2%); £3,700,195.09 -> £3,322,407.69 (10.2%); £3,700,195.33 -> £3,322,407.71 (10.2%); £3,700,195.56 -> £3,322,407.74 (10.2%); £3,700,195.80 -> £3,322,407.76 (10.2%); £3,700,196.04 -> £3,322,407.78 (10.2%); £3,700,196.27 -> £3,322,407.81 (10.2%); £3,700,196.52 -> £3,322,407.83 (10.2%); £3,700,196.75 -> £3,322,407.86 (10.2%); £3,700,196.98 -> £3,322,407.88 (10.2%); £3,700,197.22 -> £3,322,407.90 (10.2%); £3,700,197.46 -> £3,322,407.93 (10.2%); £3,700,197.69 -> £3,322,407.95 (10.2%); £3,700,197.93 -> £3,322,407.98 (10.2%); £3,700,198.17 -> £3,322,408.00 (10.2%); £3,700,198.35 -> £3,322,408.23 (10.2%); £3,700,198.53 -> £3,322,408.46 (10.2%); £3,700,198.72 -> £3,322,408.70 (10.2%); £3,700,198.97 -> £3,322,408.94 (10.2%); £3,700,199.21 -> £3,322,409.18 (10.2%); £3,700,199.46 -> £3,322,409.42 (10.2%); £3,700,199.64 -> £3,322,409.65 (10.2%); £3,700,199.88 -> £3,322,409.88 (10.2%); £3,700,200.12 -> £3,322,410.11 (10.2%); £3,700,200.36 -> £3,322,410.33 (10.2%); £3,700,200.60 -> £3,322,410.56 (10.2%); £3,700,200.85 -> £3,322,410.58 (10.2%); £3,700,201.09 -> £3,322,410.61 (10.2%); £3,700,201.31 -> £3,322,410.64 (10.2%); £3,700,201.51 -> £3,322,410.66 (10.2%); £3,700,201.70 -> £3,322,410.68 (10.2%); £3,700,201.84 -> £3,322,410.70 (10.2%); £3,700,201.98 -> £3,322,410.72 (10.2%); £3,700,202.11 -> £3,322,410.73 (10.2%); £3,700,202.25 -> £3,322,410.75 (10.2%); £3,700,202.40 -> £3,322,410.77 (10.2%); £3,700,202.54 -> £3,322,410.78 (10.2%); £3,700,202.68 -> £3,322,410.80 (10.2%); £3,700,202.82 -> £3,322,410.82 (10.2%); £3,700,202.97 -> £3,322,410.83 (10.2%); £3,700,203.11 -> £3,322,410.85 (10.2%); £3,700,203.25 -> £3,322,410.87 (10.2%); £3,700,203.39 -> £3,322,411.11 (10.2%); £3,700,203.53 -> £3,322,411.36 (10.2%); £3,700,203.69 -> £3,322,411.61 (10.2%); £3,700,203.86 -> £3,322,411.86 (10.2%); £3,700,204.05 -> £3,322,412.10 (10.2%); £3,700,204.25 -> £3,322,412.35 (10.2%); £3,700,204.47 -> £3,322,412.61 (10.2%); £3,700,204.71 -> £3,322,412.86 (10.2%); £3,700,204.95 -> £3,322,412.88 (10.2%); £3,700,205.18 -> £3,322,412.90 (10.2%); £3,700,205.42 -> £3,322,412.93 (10.2%); £3,700,205.66 -> £3,322,412.95 (10.2%); £3,700,205.89 -> £3,322,412.98 (10.2%); £3,700,206.13 -> £3,322,413.00 (10.2%); £3,700,206.37 -> £3,322,413.02 (10.2%); £3,700,206.61 -> £3,322,413.05 (10.2%); £3,700,206.84 -> £3,322,413.07 (10.2%); £3,700,207.09 -> £3,322,413.09 (10.2%); £3,700,207.33 -> £3,322,413.12 (10.2%); £3,700,207.56 -> £3,322,413.14 (10.2%); £3,700,207.80 -> £3,322,413.17 (10.2%); £3,700,207.97 -> £3,322,413.40 (10.2%); £3,700,208.15 -> £3,322,413.66 (10.2%); £3,700,208.39 -> £3,322,413.91 (10.2%); £3,700,208.63 -> £3,322,414.16 (10.2%); £3,700,208.87 -> £3,322,414.42 (10.2%); £3,700,209.11 -> £3,322,414.67 (10.2%); £3,700,209.35 -> £3,322,414.92 (10.2%); £3,700,209.59 -> £3,322,415.17 (10.2%); £3,700,209.83 -> £3,322,415.42 (10.2%); £3,700,210.06 -> £3,322,415.65 (10.2%); £3,700,210.30 -> £3,322,415.89 (10.2%); £3,700,210.53 -> £3,322,415.92 (10.2%); £3,700,210.76 -> £3,322,415.94 (10.2%); £3,700,210.97 -> £3,322,415.97 (10.2%); £3,700,211.17 -> £3,322,415.99 (10.2%); £3,700,211.35 -> £3,322,416.01 (10.2%); £3,700,211.49 -> £3,322,416.03 (10.2%); £3,700,211.63 -> £3,322,416.05 (10.2%); £3,700,211.78 -> £3,322,416.07 (10.2%); £3,700,211.92 -> £3,322,416.08 (10.2%); £3,700,212.06 -> £3,322,416.10 (10.2%); £3,700,212.20 -> £3,322,416.12 (10.2%); £3,700,212.34 -> £3,322,416.13 (10.2%); £3,700,212.48 -> £3,322,416.15 (10.2%); £3,700,212.63 -> £3,322,416.16 (10.2%); £3,700,212.77 -> £3,322,416.18 (10.2%); £3,700,212.92 -> £3,322,416.20 (10.2%); £3,700,213.06 -> £3,322,416.46 (10.2%); £3,700,213.20 -> £3,322,416.73 (10.2%); £3,700,213.36 -> £3,322,417.00 (10.2%); £3,700,213.53 -> £3,322,417.28 (10.2%); £3,700,213.72 -> £3,322,417.55 (10.2%); £3,700,213.93 -> £3,322,417.82 (10.2%); £3,700,214.15 -> £3,322,418.10 (10.2%); £3,700,214.38 -> £3,322,418.37 (10.2%); £3,700,214.62 -> £3,322,418.39 (10.2%); £3,700,214.85 -> £3,322,418.41 (10.2%); £3,700,215.08 -> £3,322,418.44 (10.2%); £3,700,215.31 -> £3,322,418.46 (10.2%); £3,700,215.54 -> £3,322,418.49 (10.2%); £3,700,215.78 -> £3,322,418.51 (10.2%); £3,700,216.02 -> £3,322,418.53 (10.2%); £3,700,216.26 -> £3,322,418.56 (10.2%); £3,700,216.50 -> £3,322,418.58 (10.2%); £3,700,216.73 -> £3,322,418.60 (10.2%); £3,700,216.96 -> £3,322,418.63 (10.2%); £3,700,217.20 -> £3,322,418.65 (10.2%); £3,700,217.44 -> £3,322,418.68 (10.2%); £3,700,217.62 -> £3,322,418.95 (10.2%); £3,700,217.80 -> £3,322,419.22 (10.2%); £3,700,217.98 -> £3,322,419.50 (10.2%); £3,700,218.15 -> £3,322,419.78 (10.2%); £3,700,218.33 -> £3,322,420.05 (10.2%); £3,700,218.50 -> £3,322,420.33 (10.2%); £3,700,218.68 -> £3,322,420.60 (10.2%); £3,700,218.91 -> £3,322,420.87 (10.2%); £3,700,219.14 -> £3,322,421.13 (10.2%); £3,700,219.38 -> £3,322,421.41 (10.2%); £3,700,219.60 -> £3,322,421.69 (10.2%); £3,700,219.84 -> £3,322,421.72 (10.2%); £3,700,220.08 -> £3,322,421.74 (10.2%); £3,700,220.30 -> £3,322,421.77 (10.2%); £3,700,220.51 -> £3,322,421.79 (10.2%); £3,700,220.70 -> £3,322,421.81 (10.2%); £3,700,220.84 -> £3,322,421.83 (10.2%); £3,700,220.98 -> £3,322,421.85 (10.2%); £3,700,221.13 -> £3,322,421.86 (10.2%); £3,700,221.27 -> £3,322,421.88 (10.2%); £3,700,221.41 -> £3,322,421.90 (10.2%); £3,700,221.56 -> £3,322,421.92 (10.2%); £3,700,221.70 -> £3,322,421.93 (10.2%); £3,700,221.85 -> £3,322,421.95 (10.2%); £3,700,221.98 -> £3,322,421.96 (10.2%); £3,700,222.13 -> £3,322,421.98 (10.2%); £3,700,222.28 -> £3,322,422.00 (10.2%); £3,700,222.42 -> £3,322,422.22 (10.2%); £3,700,222.56 -> £3,322,422.45 (10.2%); £3,700,222.72 -> £3,322,422.68 (10.2%); £3,700,222.90 -> £3,322,422.92 (10.2%); £3,700,223.09 -> £3,322,423.15 (10.2%); £3,700,223.29 -> £3,322,423.39 (10.2%); £3,700,223.51 -> £3,322,423.62 (10.2%); £3,700,223.75 -> £3,322,423.85 (10.2%); £3,700,223.98 -> £3,322,423.87 (10.2%); £3,700,224.22 -> £3,322,423.90 (10.2%); £3,700,224.45 -> £3,322,423.92 (10.2%); £3,700,224.70 -> £3,322,423.94 (10.2%); £3,700,224.94 -> £3,322,423.97 (10.2%); £3,700,225.18 -> £3,322,423.99 (10.2%); £3,700,225.42 -> £3,322,424.02 (10.2%); £3,700,225.66 -> £3,322,424.04 (10.2%); £3,700,225.88 -> £3,322,424.06 (10.2%); £3,700,226.12 -> £3,322,424.09 (10.2%); £3,700,226.36 -> £3,322,424.11 (10.2%); £3,700,226.60 -> £3,322,424.14 (10.2%); £3,700,226.84 -> £3,322,424.16 (10.2%); £3,700,227.07 -> £3,322,424.39 (10.2%); £3,700,227.25 -> £3,322,424.63 (10.2%); £3,700,227.42 -> £3,322,424.86 (10.2%); £3,700,227.61 -> £3,322,425.10 (10.2%); £3,700,227.78 -> £3,322,425.34 (10.2%); £3,700,228.03 -> £3,322,425.58 (10.2%); £3,700,228.27 -> £3,322,425.82 (10.2%); £3,700,228.52 -> £3,322,426.06 (10.2%); £3,700,228.76 -> £3,322,426.29 (10.2%); £3,700,229.00 -> £3,322,426.52 (10.2%); £3,700,229.24 -> £3,322,426.75 (10.2%); £3,700,229.49 -> £3,322,426.78 (10.2%); £3,700,229.73 -> £3,322,426.81 (10.2%); £3,700,229.95 -> £3,322,426.83 (10.2%); £3,700,230.15 -> £3,322,426.85 (10.2%); £3,700,230.34 -> £3,322,426.88 (10.2%); £3,700,230.47 -> £3,322,426.90 (10.2%); £3,700,230.60 -> £3,322,426.91 (10.2%); £3,700,230.72 -> £3,322,426.93 (10.2%); £3,700,230.85 -> £3,322,426.95 (10.2%); £3,700,230.98 -> £3,322,426.97 (10.2%); £3,700,231.11 -> £3,322,426.98 (10.2%); £3,700,231.24 -> £3,322,427.00 (10.2%); £3,700,231.37 -> £3,322,427.02 (10.2%); £3,700,231.49 -> £3,322,427.03 (10.2%); £3,700,231.62 -> £3,322,427.05 (10.2%); £3,700,231.75 -> £3,322,427.07 (10.2%); £3,700,231.88 -> £3,322,427.24 (10.2%); £3,700,232.01 -> £3,322,427.42 (10.2%); £3,700,232.15 -> £3,322,427.60 (10.2%); £3,700,232.31 -> £3,322,427.78 (10.2%); £3,700,232.48 -> £3,322,427.97 (10.2%); £3,700,232.67 -> £3,322,428.15 (10.2%); £3,700,232.88 -> £3,322,428.34 (10.2%); £3,700,233.09 -> £3,322,428.52 (10.2%); £3,700,233.30 -> £3,322,428.55 (10.2%); £3,700,233.52 -> £3,322,428.58 (10.2%); £3,700,233.73 -> £3,322,428.60 (10.2%); £3,700,233.94 -> £3,322,428.63 (10.2%); £3,700,234.16 -> £3,322,428.66 (10.2%); £3,700,234.37 -> £3,322,428.68 (10.2%); £3,700,234.58 -> £3,322,428.71 (10.2%); £3,700,234.80 -> £3,322,428.74 (10.2%); £3,700,235.02 -> £3,322,428.76 (10.2%); £3,700,235.23 -> £3,322,428.79 (10.2%); £3,700,235.45 -> £3,322,428.81 (10.2%); £3,700,235.65 -> £3,322,428.84 (10.2%); £3,700,235.87 -> £3,322,428.86 (10.2%); £3,700,236.04 -> £3,322,429.05 (10.2%); £3,700,236.20 -> £3,322,429.23 (10.2%); £3,700,236.36 -> £3,322,429.42 (10.2%); £3,700,236.52 -> £3,322,429.61 (10.2%); £3,700,236.68 -> £3,322,429.80 (10.2%); £3,700,236.85 -> £3,322,429.99 (10.2%); £3,700,237.01 -> £3,322,430.18 (10.2%); £3,700,237.22 -> £3,322,430.36 (10.2%); £3,700,237.44 -> £3,322,430.55 (10.2%); £3,700,237.65 -> £3,322,430.73 (10.2%); £3,700,237.87 -> £3,322,430.92 (10.2%); £3,700,238.08 -> £3,322,430.94 (10.2%); £3,700,238.29 -> £3,322,430.97 (10.2%); £3,700,238.50 -> £3,322,431.00 (10.2%); £3,700,238.68 -> £3,322,431.02 (10.2%); £3,700,238.84 -> £3,322,431.04 (10.2%); £3,700,238.97 -> £3,322,431.06 (10.2%); £3,700,239.10 -> £3,322,431.08 (10.2%); £3,700,239.23 -> £3,322,431.10 (10.2%); £3,700,239.36 -> £3,322,431.12 (10.2%); £3,700,239.49 -> £3,322,431.13 (10.2%); £3,700,239.62 -> £3,322,431.15 (10.2%); £3,700,239.75 -> £3,322,431.17 (10.2%); £3,700,239.87 -> £3,322,431.18 (10.2%); £3,700,240.00 -> £3,322,431.20 (10.2%); £3,700,240.13 -> £3,322,431.22 (10.2%); £3,700,240.26 -> £3,322,431.23 (10.2%); £3,700,240.39 -> £3,322,431.35 (10.2%); £3,700,240.52 -> £3,322,431.46 (10.2%); £3,700,240.66 -> £3,322,431.57 (10.2%); £3,700,240.82 -> £3,322,431.69 (10.2%); £3,700,240.99 -> £3,322,431.81 (10.2%); £3,700,241.18 -> £3,322,431.93 (10.2%); £3,700,241.38 -> £3,322,432.06 (10.2%); £3,700,241.60 -> £3,322,432.18 (10.2%); £3,700,241.82 -> £3,322,432.21 (10.2%); £3,700,242.03 -> £3,322,432.24 (10.2%); £3,700,242.25 -> £3,322,432.27 (10.2%); £3,700,242.46 -> £3,322,432.30 (10.2%); £3,700,242.67 -> £3,322,432.34 (10.2%); £3,700,242.89 -> £3,322,432.37 (10.2%); £3,700,243.10 -> £3,322,432.40 (10.2%); £3,700,243.32 -> £3,322,432.43 (10.2%); £3,700,243.53 -> £3,322,432.46 (10.2%); £3,700,243.74 -> £3,322,432.49 (10.2%); £3,700,243.96 -> £3,322,432.51 (10.2%); £3,700,244.18 -> £3,322,432.54 (10.2%); £3,700,244.40 -> £3,322,432.57 (10.2%); £3,700,244.56 -> £3,322,432.70 (10.2%); £3,700,244.72 -> £3,322,432.83 (10.2%); £3,700,244.88 -> £3,322,432.96 (10.2%); £3,700,245.03 -> £3,322,433.10 (10.2%); £3,700,245.20 -> £3,322,433.23 (10.2%); £3,700,245.36 -> £3,322,433.36 (10.2%); £3,700,245.51 -> £3,322,433.49 (10.2%); £3,700,245.73 -> £3,322,433.62 (10.2%); £3,700,245.94 -> £3,322,433.75 (10.2%); £3,700,246.17 -> £3,322,433.88 (10.2%); £3,700,246.38 -> £3,322,434.00 (10.2%); £3,700,246.59 -> £3,322,434.03 (10.2%); £3,700,246.81 -> £3,322,434.06 (10.2%); £3,700,247.00 -> £3,322,434.08 (10.2%); £3,700,247.18 -> £3,322,434.10 (10.2%); £3,700,247.34 -> £3,322,434.12 (10.2%); £3,700,247.49 -> £3,322,434.14 (10.2%); £3,700,247.64 -> £3,322,434.16 (10.2%); £3,700,247.78 -> £3,322,434.18 (10.2%); £3,700,247.93 -> £3,322,434.19 (10.2%); £3,700,248.07 -> £3,322,434.21 (10.2%); £3,700,248.22 -> £3,322,434.23 (10.2%); £3,700,248.37 -> £3,322,434.24 (10.2%); £3,700,248.52 -> £3,322,434.26 (10.2%); £3,700,248.66 -> £3,322,434.28 (10.2%); £3,700,248.80 -> £3,322,434.29 (10.2%); £3,700,248.95 -> £3,322,434.31 (10.2%); £3,700,249.10 -> £3,322,434.44 (10.2%); £3,700,249.24 -> £3,322,434.57 (10.2%); £3,700,249.40 -> £3,322,434.71 (10.2%); £3,700,249.58 -> £3,322,434.85 (10.2%); £3,700,249.78 -> £3,322,434.99 (10.2%); £3,700,250.00 -> £3,322,435.13 (10.2%); £3,700,250.23 -> £3,322,435.26 (10.2%); £3,700,250.48 -> £3,322,435.40 (10.2%); £3,700,250.73 -> £3,322,435.42 (10.2%); £3,700,250.97 -> £3,322,435.44 (10.2%); £3,700,251.23 -> £3,322,435.47 (10.2%); £3,700,251.46 -> £3,322,435.49 (10.2%); £3,700,251.71 -> £3,322,435.52 (10.2%); £3,700,251.97 -> £3,322,435.54 (10.2%); £3,700,252.21 -> £3,322,435.56 (10.2%); £3,700,252.46 -> £3,322,435.59 (10.2%); £3,700,252.72 -> £3,322,435.61 (10.2%); £3,700,252.96 -> £3,322,435.63 (10.2%); £3,700,253.21 -> £3,322,435.66 (10.2%); £3,700,253.46 -> £3,322,435.68 (10.2%); £3,700,253.71 -> £3,322,435.71 (10.2%); £3,700,253.96 -> £3,322,435.86 (10.2%); £3,700,254.14 -> £3,322,436.00 (10.2%); £3,700,254.32 -> £3,322,436.15 (10.2%); £3,700,254.51 -> £3,322,436.30 (10.2%); £3,700,254.68 -> £3,322,436.45 (10.2%); £3,700,254.87 -> £3,322,436.60 (10.2%); £3,700,255.05 -> £3,322,436.75 (10.2%); £3,700,255.29 -> £3,322,436.89 (10.2%); £3,700,255.53 -> £3,322,437.04 (10.2%); £3,700,255.78 -> £3,322,437.18 (10.2%); £3,700,256.03 -> £3,322,437.33 (10.2%); £3,700,256.27 -> £3,322,437.36 (10.2%); £3,700,256.52 -> £3,322,437.39 (10.2%); £3,700,256.75 -> £3,322,437.41 (10.2%); £3,700,256.96 -> £3,322,437.43 (10.2%); £3,700,257.15 -> £3,322,437.45 (10.2%); £3,700,257.30 -> £3,322,437.47 (10.2%); £3,700,257.45 -> £3,322,437.49 (10.2%); £3,700,257.59 -> £3,322,437.51 (10.2%); £3,700,257.73 -> £3,322,437.53 (10.2%); £3,700,257.89 -> £3,322,437.54 (10.2%); £3,700,258.04 -> £3,322,437.56 (10.2%); £3,700,258.18 -> £3,322,437.58 (10.2%); £3,700,258.33 -> £3,322,437.59 (10.2%); £3,700,258.48 -> £3,322,437.61 (10.2%); £3,700,258.62 -> £3,322,437.63 (10.2%); £3,700,258.77 -> £3,322,437.64 (10.2%); £3,700,258.92 -> £3,322,437.76 (10.2%); £3,700,259.07 -> £3,322,437.88 (10.2%); £3,700,259.24 -> £3,322,438.01 (10.2%); £3,700,259.42 -> £3,322,438.14 (10.2%); £3,700,259.62 -> £3,322,438.27 (10.2%); £3,700,259.83 -> £3,322,438.40 (10.2%); £3,700,260.07 -> £3,322,438.53 (10.2%); £3,700,260.31 -> £3,322,438.65 (10.2%); £3,700,260.56 -> £3,322,438.67 (10.2%); £3,700,260.80 -> £3,322,438.70 (10.2%); £3,700,261.05 -> £3,322,438.72 (10.2%); £3,700,261.29 -> £3,322,438.75 (10.2%); £3,700,261.55 -> £3,322,438.77 (10.2%); £3,700,261.79 -> £3,322,438.80 (10.2%); £3,700,262.04 -> £3,322,438.82 (10.2%); £3,700,262.28 -> £3,322,438.84 (10.2%); £3,700,262.53 -> £3,322,438.87 (10.2%); £3,700,262.77 -> £3,322,438.89 (10.2%); £3,700,263.01 -> £3,322,438.91 (10.2%); £3,700,263.26 -> £3,322,438.94 (10.2%); £3,700,263.51 -> £3,322,438.97 (10.2%); £3,700,263.69 -> £3,322,439.10 (10.2%); £3,700,263.88 -> £3,322,439.24 (10.2%); £3,700,264.14 -> £3,322,439.39 (10.2%); £3,700,264.38 -> £3,322,439.53 (10.2%); £3,700,264.62 -> £3,322,439.67 (10.2%); £3,700,264.87 -> £3,322,439.81 (10.2%); £3,700,265.06 -> £3,322,439.95 (10.2%); £3,700,265.31 -> £3,322,440.08 (10.2%); £3,700,265.56 -> £3,322,440.22 (10.2%); £3,700,265.81 -> £3,322,440.35 (10.2%); £3,700,266.06 -> £3,322,440.48 (10.2%); £3,700,266.31 -> £3,322,440.51 (10.2%); £3,700,266.56 -> £3,322,440.54 (10.2%); £3,700,266.79 -> £3,322,440.56 (10.2%); £3,700,266.99 -> £3,322,440.59 (10.2%); £3,700,267.19 -> £3,322,440.61 (10.2%); £3,700,267.33 -> £3,322,440.62 (10.2%); £3,700,267.48 -> £3,322,440.64 (10.2%); £3,700,267.63 -> £3,322,440.66 (10.2%); £3,700,267.78 -> £3,322,440.68 (10.2%); £3,700,267.93 -> £3,322,440.69 (10.2%); £3,700,268.08 -> £3,322,440.71 (10.2%); £3,700,268.22 -> £3,322,440.73 (10.2%); £3,700,268.37 -> £3,322,440.75 (10.2%); £3,700,268.52 -> £3,322,440.76 (10.2%); £3,700,268.67 -> £3,322,440.78 (10.2%); £3,700,268.82 -> £3,322,440.80 (10.2%); £3,700,268.98 -> £3,322,440.92 (10.2%); £3,700,269.13 -> £3,322,441.05 (10.2%); £3,700,269.30 -> £3,322,441.18 (10.2%); £3,700,269.48 -> £3,322,441.31 (10.2%); £3,700,269.68 -> £3,322,441.45 (10.2%); £3,700,269.89 -> £3,322,441.58 (10.2%); £3,700,270.13 -> £3,322,441.71 (10.2%); £3,700,270.38 -> £3,322,441.85 (10.2%); £3,700,270.63 -> £3,322,441.87 (10.2%); £3,700,270.88 -> £3,322,441.89 (10.2%); £3,700,271.13 -> £3,322,441.92 (10.2%); £3,700,271.39 -> £3,322,441.94 (10.2%); £3,700,271.63 -> £3,322,441.97 (10.2%); £3,700,271.88 -> £3,322,441.99 (10.2%); £3,700,272.13 -> £3,322,442.02 (10.2%); £3,700,272.39 -> £3,322,442.04 (10.2%); £3,700,272.65 -> £3,322,442.06 (10.2%); £3,700,272.90 -> £3,322,442.09 (10.2%); £3,700,273.16 -> £3,322,442.11 (10.2%); £3,700,273.41 -> £3,322,442.14 (10.2%); £3,700,273.66 -> £3,322,442.17 (10.2%); £3,700,273.91 -> £3,322,442.31 (10.2%); £3,700,274.09 -> £3,322,442.45 (10.2%); £3,700,274.28 -> £3,322,442.60 (10.2%); £3,700,274.53 -> £3,322,442.75 (10.2%); £3,700,274.78 -> £3,322,442.91 (10.2%); £3,700,275.04 -> £3,322,443.05 (10.2%); £3,700,275.23 -> £3,322,443.20 (10.2%); £3,700,275.48 -> £3,322,443.34 (10.2%); £3,700,275.74 -> £3,322,443.49 (10.2%); £3,700,275.99 -> £3,322,443.63 (10.2%); £3,700,276.24 -> £3,322,443.77 (10.2%); £3,700,276.49 -> £3,322,443.80 (10.2%); £3,700,276.74 -> £3,322,443.83 (10.2%); £3,700,276.98 -> £3,322,443.85 (10.2%); £3,700,277.20 -> £3,322,443.87 (10.2%); £3,700,277.39 -> £3,322,443.89 (10.2%); £3,700,277.54 -> £3,322,443.91 (10.2%); £3,700,277.70 -> £3,322,443.93 (10.2%); £3,700,277.85 -> £3,322,443.95 (10.2%); £3,700,278.01 -> £3,322,443.97 (10.2%); £3,700,278.16 -> £3,322,443.98 (10.2%); £3,700,278.32 -> £3,322,444.00 (10.2%); £3,700,278.47 -> £3,322,444.02 (10.2%); £3,700,278.63 -> £3,322,444.03 (10.2%); £3,700,278.78 -> £3,322,444.05 (10.2%); £3,700,278.93 -> £3,322,444.07 (10.2%); £3,700,279.09 -> £3,322,444.08 (10.2%); £3,700,279.24 -> £3,322,444.20 (10.2%); £3,700,279.40 -> £3,322,444.31 (10.2%); £3,700,279.57 -> £3,322,444.44 (10.2%); £3,700,279.75 -> £3,322,444.56 (10.2%); £3,700,279.96 -> £3,322,444.69 (10.2%); £3,700,280.17 -> £3,322,444.81 (10.2%); £3,700,280.41 -> £3,322,444.94 (10.2%); £3,700,280.66 -> £3,322,445.06 (10.2%); £3,700,280.92 -> £3,322,445.09 (10.2%); £3,700,281.18 -> £3,322,445.11 (10.2%); £3,700,281.42 -> £3,322,445.14 (10.2%); £3,700,281.68 -> £3,322,445.16 (10.2%); £3,700,281.93 -> £3,322,445.18 (10.2%); £3,700,282.19 -> £3,322,445.21 (10.2%); £3,700,282.45 -> £3,322,445.23 (10.2%); £3,700,282.70 -> £3,322,445.26 (10.2%); £3,700,282.96 -> £3,322,445.28 (10.2%); £3,700,283.22 -> £3,322,445.30 (10.2%); £3,700,283.47 -> £3,322,445.33 (10.2%); £3,700,283.72 -> £3,322,445.35 (10.2%); £3,700,283.99 -> £3,322,445.38 (10.2%); £3,700,284.18 -> £3,322,445.51 (10.2%); £3,700,284.37 -> £3,322,445.65 (10.2%); £3,700,284.55 -> £3,322,445.79 (10.2%); £3,700,284.74 -> £3,322,445.92 (10.2%); £3,700,285.00 -> £3,322,446.06 (10.2%); £3,700,285.25 -> £3,322,446.20 (10.2%); £3,700,285.45 -> £3,322,446.33 (10.2%); £3,700,285.71 -> £3,322,446.46 (10.2%); £3,700,285.97 -> £3,322,446.59 (10.2%); £3,700,286.23 -> £3,322,446.72 (10.2%); £3,700,286.48 -> £3,322,446.85 (10.2%); £3,700,286.73 -> £3,322,446.88 (10.2%); £3,700,286.99 -> £3,322,446.91 (10.2%); £3,700,287.22 -> £3,322,446.94 (10.2%); £3,700,287.44 -> £3,322,446.96 (10.2%); £3,700,287.64 -> £3,322,446.98 (10.2%); £3,700,287.80 -> £3,322,447.00 (10.2%); £3,700,287.95 -> £3,322,447.01 (10.2%); £3,700,288.10 -> £3,322,447.03 (10.2%); £3,700,288.25 -> £3,322,447.05 (10.2%); £3,700,288.40 -> £3,322,447.07 (10.2%); £3,700,288.55 -> £3,322,447.08 (10.2%); £3,700,288.71 -> £3,322,447.10 (10.2%); £3,700,288.86 -> £3,322,447.12 (10.2%); £3,700,289.02 -> £3,322,447.13 (10.2%); £3,700,289.17 -> £3,322,447.15 (10.2%); £3,700,289.32 -> £3,322,447.17 (10.2%); £3,700,289.47 -> £3,322,447.30 (10.2%); £3,700,289.63 -> £3,322,447.43 (10.2%); £3,700,289.80 -> £3,322,447.57 (10.2%); £3,700,289.99 -> £3,322,447.72 (10.2%); £3,700,290.19 -> £3,322,447.86 (10.2%); £3,700,290.42 -> £3,322,448.00 (10.2%); £3,700,290.66 -> £3,322,448.14 (10.2%); £3,700,290.92 -> £3,322,448.28 (10.2%); £3,700,291.19 -> £3,322,448.31 (10.2%); £3,700,291.45 -> £3,322,448.33 (10.2%); £3,700,291.71 -> £3,322,448.36 (10.2%); £3,700,291.97 -> £3,322,448.38 (10.2%); £3,700,292.22 -> £3,322,448.41 (10.2%); £3,700,292.46 -> £3,322,448.43 (10.2%); £3,700,292.72 -> £3,322,448.46 (10.2%); £3,700,292.97 -> £3,322,448.48 (10.2%); £3,700,293.24 -> £3,322,448.51 (10.2%); £3,700,293.50 -> £3,322,448.53 (10.2%); £3,700,293.74 -> £3,322,448.56 (10.2%); £3,700,293.99 -> £3,322,448.58 (10.2%); £3,700,294.25 -> £3,322,448.61 (10.2%); £3,700,294.45 -> £3,322,448.75 (10.2%); £3,700,294.64 -> £3,322,448.91 (10.2%); £3,700,294.84 -> £3,322,449.06 (10.2%); £3,700,295.03 -> £3,322,449.21 (10.2%); £3,700,295.23 -> £3,322,449.36 (10.2%); £3,700,295.42 -> £3,322,449.51 (10.2%); £3,700,295.61 -> £3,322,449.67 (10.2%); £3,700,295.87 -> £3,322,449.82 (10.2%); £3,700,296.13 -> £3,322,449.97 (10.2%); £3,700,296.38 -> £3,322,450.13 (10.2%); £3,700,296.64 -> £3,322,450.27 (10.2%); £3,700,296.89 -> £3,322,450.30 (10.2%); £3,700,297.15 -> £3,322,450.33 (10.2%); £3,700,297.38 -> £3,322,450.35 (10.2%); £3,700,297.60 -> £3,322,450.38 (10.2%); £3,700,297.80 -> £3,322,450.40 (10.2%); £3,700,297.94 -> £3,322,450.42 (10.2%); £3,700,298.08 -> £3,322,450.44 (10.2%); £3,700,298.22 -> £3,322,450.46 (10.2%); £3,700,298.36 -> £3,322,450.47 (10.2%); £3,700,298.50 -> £3,322,450.49 (10.2%); £3,700,298.65 -> £3,322,450.51 (10.2%); £3,700,298.79 -> £3,322,450.52 (10.2%); £3,700,298.93 -> £3,322,450.54 (10.2%); £3,700,299.06 -> £3,322,450.56 (10.2%); £3,700,299.20 -> £3,322,450.58 (10.2%); £3,700,299.33 -> £3,322,450.59 (10.2%); £3,700,299.47 -> £3,322,450.75 (10.2%); £3,700,299.62 -> £3,322,450.91 (10.2%); £3,700,299.77 -> £3,322,451.07 (10.2%); £3,700,299.94 -> £3,322,451.23 (10.2%); £3,700,300.13 -> £3,322,451.39 (10.2%); £3,700,300.33 -> £3,322,451.56 (10.2%); £3,700,300.55 -> £3,322,451.72 (10.2%); £3,700,300.78 -> £3,322,451.89 (10.2%); £3,700,301.01 -> £3,322,451.92 (10.2%); £3,700,301.25 -> £3,322,451.94 (10.2%); £3,700,301.48 -> £3,322,451.97 (10.2%); £3,700,301.71 -> £3,322,452.00 (10.2%); £3,700,301.94 -> £3,322,452.03 (10.2%); £3,700,302.16 -> £3,322,452.05 (10.2%); £3,700,302.40 -> £3,322,452.08 (10.2%); £3,700,302.64 -> £3,322,452.11 (10.2%); £3,700,302.87 -> £3,322,452.14 (10.2%); £3,700,303.10 -> £3,322,452.16 (10.2%); £3,700,303.33 -> £3,322,452.19 (10.2%); £3,700,303.56 -> £3,322,452.21 (10.2%); £3,700,303.78 -> £3,322,452.24 (10.2%); £3,700,303.96 -> £3,322,452.40 (10.2%); £3,700,304.14 -> £3,322,452.57 (10.2%); £3,700,304.31 -> £3,322,452.74 (10.2%); £3,700,304.48 -> £3,322,452.91 (10.2%); £3,700,304.65 -> £3,322,453.09 (10.2%); £3,700,304.89 -> £3,322,453.26 (10.2%); £3,700,305.12 -> £3,322,453.43 (10.2%); £3,700,305.35 -> £3,322,453.60 (10.2%); £3,700,305.58 -> £3,322,453.77 (10.2%); £3,700,305.81 -> £3,322,453.94 (10.2%); £3,700,306.04 -> £3,322,454.11 (10.2%); £3,700,306.27 -> £3,322,454.14 (10.2%); £3,700,306.50 -> £3,322,454.17 (10.2%); £3,700,306.71 -> £3,322,454.19 (10.2%); £3,700,306.90 -> £3,322,454.22 (10.2%); £3,700,307.08 -> £3,322,454.24 (10.2%); £3,700,307.21 -> £3,322,454.26 (10.2%); £3,700,307.36 -> £3,322,454.28 (10.2%); £3,700,307.50 -> £3,322,454.30 (10.2%); £3,700,307.64 -> £3,322,454.31 (10.2%); £3,700,307.78 -> £3,322,454.33 (10.2%); £3,700,307.92 -> £3,322,454.35 (10.2%); £3,700,308.06 -> £3,322,454.37 (10.2%); £3,700,308.21 -> £3,322,454.38 (10.2%); £3,700,308.34 -> £3,322,454.40 (10.2%); £3,700,308.48 -> £3,322,454.42 (10.2%); £3,700,308.61 -> £3,322,454.43 (10.2%); £3,700,308.75 -> £3,322,454.57 (10.2%); £3,700,308.89 -> £3,322,454.70 (10.2%); £3,700,309.05 -> £3,322,454.83 (10.2%); £3,700,309.23 -> £3,322,454.96 (10.2%); £3,700,309.41 -> £3,322,455.09 (10.2%); £3,700,309.62 -> £3,322,455.23 (10.2%); £3,700,309.84 -> £3,322,455.36 (10.2%); £3,700,310.07 -> £3,322,455.50 (10.2%); £3,700,310.30 -> £3,322,455.54 (10.2%); £3,700,310.54 -> £3,322,455.57 (10.2%); £3,700,310.77 -> £3,322,455.60 (10.2%); £3,700,311.01 -> £3,322,455.63 (10.2%); £3,700,311.24 -> £3,322,455.66 (10.2%); £3,700,311.47 -> £3,322,455.69 (10.2%); £3,700,311.69 -> £3,322,455.72 (10.2%); £3,700,311.92 -> £3,322,455.75 (10.2%); £3,700,312.16 -> £3,322,455.78 (10.2%); £3,700,312.39 -> £3,322,455.81 (10.2%); £3,700,312.63 -> £3,322,455.84 (10.2%); £3,700,312.86 -> £3,322,455.87 (10.2%); £3,700,313.08 -> £3,322,455.90 (10.2%); £3,700,313.26 -> £3,322,456.04 (10.2%); £3,700,313.43 -> £3,322,456.18 (10.2%); £3,700,313.60 -> £3,322,456.33 (10.2%); £3,700,313.78 -> £3,322,456.48 (10.2%); £3,700,314.01 -> £3,322,456.63 (10.2%); £3,700,314.24 -> £3,322,456.78 (10.2%); £3,700,314.42 -> £3,322,456.92 (10.2%); £3,700,314.65 -> £3,322,457.06 (10.2%); £3,700,314.89 -> £3,322,457.20 (10.2%); £3,700,315.12 -> £3,322,457.34 (10.2%); £3,700,315.36 -> £3,322,457.48 (10.2%); £3,700,315.60 -> £3,322,457.51 (10.2%); £3,700,315.83 -> £3,322,457.54 (10.2%); £3,700,316.04 -> £3,322,457.56 (10.2%); £3,700,316.24 -> £3,322,457.59 (10.2%); £3,700,316.41 -> £3,322,457.61 (10.2%); £3,700,316.57 -> £3,322,457.62 (10.2%); £3,700,316.73 -> £3,322,457.64 (10.2%); £3,700,316.89 -> £3,322,457.66 (10.2%); £3,700,317.05 -> £3,322,457.68 (10.2%); £3,700,317.21 -> £3,322,457.69 (10.2%); £3,700,317.37 -> £3,322,457.71 (10.2%); £3,700,317.53 -> £3,322,457.73 (10.2%); £3,700,317.69 -> £3,322,457.74 (10.2%); £3,700,317.85 -> £3,322,457.76 (10.2%); £3,700,318.01 -> £3,322,457.78 (10.2%); £3,700,318.18 -> £3,322,457.79 (10.2%); £3,700,318.34 -> £3,322,457.88 (10.2%); £3,700,318.50 -> £3,322,457.97 (10.2%); £3,700,318.68 -> £3,322,458.07 (10.2%); £3,700,318.88 -> £3,322,458.18 (10.2%); £3,700,319.09 -> £3,322,458.28 (10.2%); £3,700,319.33 -> £3,322,458.38 (10.2%); £3,700,319.58 -> £3,322,458.48 (10.2%); £3,700,319.86 -> £3,322,458.57 (10.2%); £3,700,320.12 -> £3,322,458.60 (10.2%); £3,700,320.39 -> £3,322,458.62 (10.2%); £3,700,320.67 -> £3,322,458.65 (10.2%); £3,700,320.93 -> £3,322,458.67 (10.2%); £3,700,321.19 -> £3,322,458.69 (10.2%); £3,700,321.46 -> £3,322,458.72 (10.2%); £3,700,321.72 -> £3,322,458.74 (10.2%); £3,700,321.97 -> £3,322,458.76 (10.2%); £3,700,322.24 -> £3,322,458.79 (10.2%); £3,700,322.50 -> £3,322,458.81 (10.2%); £3,700,322.77 -> £3,322,458.83 (10.2%); £3,700,323.04 -> £3,322,458.86 (10.2%); £3,700,323.31 -> £3,322,458.89 (10.2%); £3,700,323.58 -> £3,322,459.00 (10.2%); £3,700,323.85 -> £3,322,459.12 (10.2%); £3,700,324.13 -> £3,322,459.24 (10.2%); £3,700,324.40 -> £3,322,459.35 (10.2%); £3,700,324.67 -> £3,322,459.47 (10.2%); £3,700,324.94 -> £3,322,459.58 (10.2%); £3,700,325.14 -> £3,322,459.70 (10.2%); £3,700,325.41 -> £3,322,459.81 (10.2%); £3,700,325.68 -> £3,322,459.92 (10.2%); £3,700,325.95 -> £3,322,460.03 (10.2%); £3,700,326.21 -> £3,322,460.13 (10.2%); £3,700,326.47 -> £3,322,460.16 (10.2%); £3,700,326.75 -> £3,322,460.19 (10.2%); £3,700,326.99 -> £3,322,460.21 (10.2%); £3,700,327.23 -> £3,322,460.24 (10.2%); £3,700,327.43 -> £3,322,460.26 (10.2%); £3,700,327.59 -> £3,322,460.27 (10.2%); £3,700,327.75 -> £3,322,460.29 (10.2%); £3,700,327.91 -> £3,322,460.31 (10.2%); £3,700,328.07 -> £3,322,460.33 (10.2%); £3,700,328.22 -> £3,322,460.34 (10.2%); £3,700,328.39 -> £3,322,460.36 (10.2%); £3,700,328.54 -> £3,322,460.38 (10.2%); £3,700,328.70 -> £3,322,460.39 (10.2%); £3,700,328.86 -> £3,322,460.41 (10.2%); £3,700,329.02 -> £3,322,460.43 (10.2%); £3,700,329.18 -> £3,322,460.45 (10.2%); £3,700,329.33 -> £3,322,460.60 (10.2%); £3,700,329.49 -> £3,322,460.76 (10.2%); £3,700,329.67 -> £3,322,460.92 (10.2%); £3,700,329.86 -> £3,322,461.08 (10.2%); £3,700,330.07 -> £3,322,461.24 (10.2%); £3,700,330.30 -> £3,322,461.40 (10.2%); £3,700,330.55 -> £3,322,461.57 (10.2%); £3,700,330.82 -> £3,322,461.73 (10.2%); £3,700,331.09 -> £3,322,461.75 (10.2%); £3,700,331.36 -> £3,322,461.77 (10.2%); £3,700,331.62 -> £3,322,461.80 (10.2%); £3,700,331.89 -> £3,322,461.82 (10.2%); £3,700,332.15 -> £3,322,461.85 (10.2%); £3,700,332.41 -> £3,322,461.87 (10.2%); £3,700,332.68 -> £3,322,461.90 (10.2%); £3,700,332.94 -> £3,322,461.92 (10.2%); £3,700,333.21 -> £3,322,461.94 (10.2%); £3,700,333.49 -> £3,322,461.97 (10.2%); £3,700,333.74 -> £3,322,461.99 (10.2%); £3,700,334.01 -> £3,322,462.01 (10.2%); £3,700,334.28 -> £3,322,462.04 (10.2%); £3,700,334.48 -> £3,322,462.20 (10.2%); £3,700,334.67 -> £3,322,462.37 (10.2%); £3,700,334.94 -> £3,322,462.55 (10.2%); £3,700,335.21 -> £3,322,462.71 (10.2%); £3,700,335.41 -> £3,322,462.88 (10.2%); £3,700,335.61 -> £3,322,463.05 (10.2%); £3,700,335.80 -> £3,322,463.21 (10.2%); £3,700,336.07 -> £3,322,463.37 (10.2%); £3,700,336.33 -> £3,322,463.54 (10.2%); £3,700,336.59 -> £3,322,463.71 (10.2%); £3,700,336.84 -> £3,322,463.87 (10.2%); £3,700,337.10 -> £3,322,463.90 (10.2%); £3,700,337.38 -> £3,322,463.93 (10.2%); £3,700,337.62 -> £3,322,463.95 (10.2%); £3,700,337.83 -> £3,322,463.97 (10.2%); £3,700,338.04 -> £3,322,463.99 (10.2%); £3,700,338.20 -> £3,322,464.01 (10.2%); £3,700,338.36 -> £3,322,464.03 (10.2%); £3,700,338.52 -> £3,322,464.05 (10.2%); £3,700,338.68 -> £3,322,464.06 (10.2%); £3,700,338.84 -> £3,322,464.08 (10.2%); £3,700,339.00 -> £3,322,464.10 (10.2%); £3,700,339.15 -> £3,322,464.11 (10.2%); £3,700,339.32 -> £3,322,464.13 (10.2%); £3,700,339.47 -> £3,322,464.15 (10.2%); £3,700,339.64 -> £3,322,464.17 (10.2%); £3,700,339.79 -> £3,322,464.18 (10.2%); £3,700,339.95 -> £3,322,464.35 (10.2%); £3,700,340.11 -> £3,322,464.52 (10.2%); £3,700,340.28 -> £3,322,464.70 (10.2%); £3,700,340.48 -> £3,322,464.88 (10.2%); £3,700,340.68 -> £3,322,465.06 (10.2%); £3,700,340.91 -> £3,322,465.23 (10.2%); £3,700,341.17 -> £3,322,465.41 (10.2%); £3,700,341.44 -> £3,322,465.58 (10.2%); £3,700,341.70 -> £3,322,465.60 (10.2%); £3,700,341.97 -> £3,322,465.63 (10.2%); £3,700,342.24 -> £3,322,465.65 (10.2%); £3,700,342.51 -> £3,322,465.68 (10.2%); £3,700,342.77 -> £3,322,465.70 (10.2%); £3,700,343.03 -> £3,322,465.73 (10.2%); £3,700,343.29 -> £3,322,465.75 (10.2%); £3,700,343.55 -> £3,322,465.77 (10.2%); £3,700,343.82 -> £3,322,465.80 (10.2%); £3,700,344.08 -> £3,322,465.82 (10.2%); £3,700,344.35 -> £3,322,465.84 (10.2%); £3,700,344.61 -> £3,322,465.87 (10.2%); £3,700,344.88 -> £3,322,465.90 (10.2%); £3,700,345.14 -> £3,322,466.07 (10.2%); £3,700,345.40 -> £3,322,466.25 (10.2%); £3,700,345.61 -> £3,322,466.44 (10.2%); £3,700,345.80 -> £3,322,466.62 (10.2%); £3,700,346.01 -> £3,322,466.80 (10.2%); £3,700,346.28 -> £3,322,466.99 (10.2%); £3,700,346.54 -> £3,322,467.16 (10.2%); £3,700,346.81 -> £3,322,467.34 (10.2%); £3,700,347.07 -> £3,322,467.52 (10.2%); £3,700,347.34 -> £3,322,467.69 (10.2%); £3,700,347.60 -> £3,322,467.87 (10.2%); £3,700,347.87 -> £3,322,467.90 (10.2%); £3,700,348.14 -> £3,322,467.93 (10.2%); £3,700,348.38 -> £3,322,467.95 (10.2%); £3,700,348.60 -> £3,322,467.98 (10.2%); £3,700,348.81 -> £3,322,468.00 (10.2%); £3,700,348.97 -> £3,322,468.01 (10.2%); £3,700,349.13 -> £3,322,468.03 (10.2%); £3,700,349.29 -> £3,322,468.05 (10.2%); £3,700,349.45 -> £3,322,468.07 (10.2%); £3,700,349.60 -> £3,322,468.08 (10.2%); £3,700,349.76 -> £3,322,468.10 (10.2%); £3,700,349.92 -> £3,322,468.12 (10.2%); £3,700,350.08 -> £3,322,468.13 (10.2%); £3,700,350.24 -> £3,322,468.15 (10.2%); £3,700,350.40 -> £3,322,468.17 (10.2%); £3,700,350.56 -> £3,322,468.19 (10.2%); £3,700,350.73 -> £3,322,468.36 (10.2%); £3,700,350.89 -> £3,322,468.52 (10.2%); £3,700,351.06 -> £3,322,468.69 (10.2%); £3,700,351.25 -> £3,322,468.86 (10.2%); £3,700,351.46 -> £3,322,469.03 (10.2%); £3,700,351.68 -> £3,322,469.20 (10.2%); £3,700,351.92 -> £3,322,469.37 (10.2%); £3,700,352.19 -> £3,322,469.54 (10.2%); £3,700,352.45 -> £3,322,469.57 (10.2%); £3,700,352.72 -> £3,322,469.59 (10.2%); £3,700,352.97 -> £3,322,469.62 (10.2%); £3,700,353.24 -> £3,322,469.64 (10.2%); £3,700,353.50 -> £3,322,469.67 (10.2%); £3,700,353.77 -> £3,322,469.69 (10.2%); £3,700,354.03 -> £3,322,469.71 (10.2%); £3,700,354.31 -> £3,322,469.74 (10.2%); £3,700,354.56 -> £3,322,469.76 (10.2%); £3,700,354.83 -> £3,322,469.78 (10.2%); £3,700,355.10 -> £3,322,469.81 (10.2%); £3,700,355.37 -> £3,322,469.83 (10.2%); £3,700,355.64 -> £3,322,469.86 (10.2%); £3,700,355.90 -> £3,322,470.03 (10.2%); £3,700,356.10 -> £3,322,470.21 (10.2%); £3,700,356.30 -> £3,322,470.38 (10.2%); £3,700,356.49 -> £3,322,470.56 (10.2%); £3,700,356.69 -> £3,322,470.74 (10.2%); £3,700,356.89 -> £3,322,470.91 (10.2%); £3,700,357.16 -> £3,322,471.09 (10.2%); £3,700,357.42 -> £3,322,471.27 (10.2%); £3,700,357.68 -> £3,322,471.44 (10.2%); £3,700,357.95 -> £3,322,471.62 (10.2%); £3,700,358.21 -> £3,322,471.79 (10.2%); £3,700,358.47 -> £3,322,471.82 (10.2%); £3,700,358.75 -> £3,322,471.84 (10.2%); £3,700,358.99 -> £3,322,471.87 (10.2%); £3,700,359.21 -> £3,322,471.89 (10.2%); £3,700,359.41 -> £3,322,471.91 (10.2%); £3,700,359.57 -> £3,322,471.93 (10.2%); £3,700,359.73 -> £3,322,471.95 (10.2%); £3,700,359.89 -> £3,322,471.96 (10.2%); £3,700,360.05 -> £3,322,471.98 (10.2%); £3,700,360.20 -> £3,322,472.00 (10.2%); £3,700,360.36 -> £3,322,472.01 (10.2%); £3,700,360.52 -> £3,322,472.03 (10.2%); £3,700,360.68 -> £3,322,472.05 (10.2%); £3,700,360.85 -> £3,322,472.06 (10.2%); £3,700,361.00 -> £3,322,472.08 (10.2%); £3,700,361.16 -> £3,322,472.10 (10.2%); £3,700,361.32 -> £3,322,472.20 (10.2%); £3,700,361.48 -> £3,322,472.31 (10.2%); £3,700,361.65 -> £3,322,472.43 (10.2%); £3,700,361.85 -> £3,322,472.54 (10.2%); £3,700,362.06 -> £3,322,472.66 (10.2%); £3,700,362.29 -> £3,322,472.78 (10.2%); £3,700,362.53 -> £3,322,472.89 (10.2%); £3,700,362.81 -> £3,322,473.00 (10.2%); £3,700,363.08 -> £3,322,473.03 (10.2%); £3,700,363.36 -> £3,322,473.05 (10.2%); £3,700,363.62 -> £3,322,473.08 (10.2%); £3,700,363.89 -> £3,322,473.10 (10.2%); £3,700,364.15 -> £3,322,473.13 (10.2%); £3,700,364.42 -> £3,322,473.15 (10.2%); £3,700,364.68 -> £3,322,473.17 (10.2%); £3,700,364.95 -> £3,322,473.20 (10.2%); £3,700,365.22 -> £3,322,473.22 (10.2%); £3,700,365.48 -> £3,322,473.25 (10.2%); £3,700,365.75 -> £3,322,473.27 (10.2%); £3,700,366.00 -> £3,322,473.30 (10.2%); £3,700,366.28 -> £3,322,473.32 (10.2%); £3,700,366.55 -> £3,322,473.45 (10.2%); £3,700,366.82 -> £3,322,473.58 (10.2%); £3,700,367.08 -> £3,322,473.71 (10.2%); £3,700,367.34 -> £3,322,473.84 (10.2%); £3,700,367.60 -> £3,322,473.97 (10.2%); £3,700,367.87 -> £3,322,474.10 (10.2%); £3,700,368.13 -> £3,322,474.23 (10.2%); £3,700,368.40 -> £3,322,474.35 (10.2%); £3,700,368.67 -> £3,322,474.48 (10.2%); £3,700,368.93 -> £3,322,474.60 (10.2%); £3,700,369.19 -> £3,322,474.72 (10.2%); £3,700,369.46 -> £3,322,474.75 (10.2%); £3,700,369.73 -> £3,322,474.78 (10.2%); £3,700,369.98 -> £3,322,474.80 (10.2%); £3,700,370.21 -> £3,322,474.83 (10.2%); £3,700,370.42 -> £3,322,474.85 (10.2%); £3,700,370.55 -> £3,322,474.87 (10.2%); £3,700,370.69 -> £3,322,474.89 (10.2%); £3,700,370.83 -> £3,322,474.91 (10.2%); £3,700,370.97 -> £3,322,474.93 (10.2%); £3,700,371.11 -> £3,322,474.94 (10.2%); £3,700,371.25 -> £3,322,474.96 (10.2%); £3,700,371.39 -> £3,322,474.98 (10.2%); £3,700,371.53 -> £3,322,474.99 (10.2%); £3,700,371.67 -> £3,322,475.01 (10.2%); £3,700,371.81 -> £3,322,475.03 (10.2%); £3,700,371.95 -> £3,322,475.04 (10.2%); £3,700,372.09 -> £3,322,475.15 (10.2%); £3,700,372.23 -> £3,322,475.26 (10.2%); £3,700,372.39 -> £3,322,475.38 (10.2%); £3,700,372.56 -> £3,322,475.49 (10.2%); £3,700,372.74 -> £3,322,475.60 (10.2%); £3,700,372.94 -> £3,322,475.71 (10.2%); £3,700,373.16 -> £3,322,475.83 (10.2%); £3,700,373.39 -> £3,322,475.94 (10.2%); £3,700,373.62 -> £3,322,475.97 (10.2%); £3,700,373.86 -> £3,322,475.99 (10.2%); £3,700,374.09 -> £3,322,476.02 (10.2%); £3,700,374.32 -> £3,322,476.05 (10.2%); £3,700,374.55 -> £3,322,476.07 (10.2%); £3,700,374.79 -> £3,322,476.10 (10.2%); £3,700,375.02 -> £3,322,476.13 (10.2%); £3,700,375.26 -> £3,322,476.15 (10.2%); £3,700,375.48 -> £3,322,476.18 (10.2%); £3,700,375.71 -> £3,322,476.20 (10.2%); £3,700,375.94 -> £3,322,476.23 (10.2%); £3,700,376.18 -> £3,322,476.26 (10.2%); £3,700,376.41 -> £3,322,476.29 (10.2%); £3,700,376.64 -> £3,322,476.40 (10.2%); £3,700,376.83 -> £3,322,476.52 (10.2%); £3,700,377.06 -> £3,322,476.65 (10.2%); £3,700,377.23 -> £3,322,476.77 (10.2%); £3,700,377.40 -> £3,322,476.89 (10.2%); £3,700,377.58 -> £3,322,477.01 (10.2%); £3,700,377.76 -> £3,322,477.14 (10.2%); £3,700,377.99 -> £3,322,477.27 (10.2%); £3,700,378.22 -> £3,322,477.39 (10.2%); £3,700,378.45 -> £3,322,477.51 (10.2%); £3,700,378.67 -> £3,322,477.63 (10.2%); £3,700,378.90 -> £3,322,477.66 (10.2%); £3,700,379.14 -> £3,322,477.69 (10.2%); £3,700,379.35 -> £3,322,477.71 (10.2%); £3,700,379.54 -> £3,322,477.74 (10.2%); £3,700,379.72 -> £3,322,477.76 (10.2%); £3,700,379.86 -> £3,322,477.78 (10.2%); £3,700,380.00 -> £3,322,477.80 (10.2%); £3,700,380.14 -> £3,322,477.82 (10.2%); £3,700,380.28 -> £3,322,477.84 (10.2%); £3,700,380.42 -> £3,322,477.85 (10.2%); £3,700,380.56 -> £3,322,477.87 (10.2%); £3,700,380.70 -> £3,322,477.89 (10.2%); £3,700,380.84 -> £3,322,477.91 (10.2%); £3,700,380.98 -> £3,322,477.92 (10.2%); £3,700,381.12 -> £3,322,477.94 (10.2%); £3,700,381.26 -> £3,322,477.96 (10.2%); £3,700,381.41 -> £3,322,478.06 (10.2%); £3,700,381.55 -> £3,322,478.16 (10.2%); £3,700,381.71 -> £3,322,478.26 (10.2%); £3,700,381.87 -> £3,322,478.37 (10.2%); £3,700,382.05 -> £3,322,478.47 (10.2%); £3,700,382.25 -> £3,322,478.58 (10.2%); £3,700,382.48 -> £3,322,478.70 (10.2%); £3,700,382.71 -> £3,322,478.81 (10.2%); £3,700,382.94 -> £3,322,478.84 (10.2%); £3,700,383.18 -> £3,322,478.87 (10.2%); £3,700,383.41 -> £3,322,478.90 (10.2%); £3,700,383.65 -> £3,322,478.94 (10.2%); £3,700,383.88 -> £3,322,478.97 (10.2%); £3,700,384.12 -> £3,322,479.00 (10.2%); £3,700,384.36 -> £3,322,479.03 (10.2%); £3,700,384.60 -> £3,322,479.06 (10.2%); £3,700,384.83 -> £3,322,479.09 (10.2%); £3,700,385.07 -> £3,322,479.12 (10.2%); £3,700,385.31 -> £3,322,479.15 (10.2%); £3,700,385.54 -> £3,322,479.18 (10.2%); £3,700,385.78 -> £3,322,479.21 (10.2%); £3,700,386.01 -> £3,322,479.32 (10.2%); £3,700,386.24 -> £3,322,479.44 (10.2%); £3,700,386.41 -> £3,322,479.56 (10.2%); £3,700,386.59 -> £3,322,479.68 (10.2%); £3,700,386.77 -> £3,322,479.80 (10.2%); £3,700,386.94 -> £3,322,479.92 (10.2%); £3,700,387.12 -> £3,322,480.03 (10.2%); £3,700,387.36 -> £3,322,480.15 (10.2%); £3,700,387.59 -> £3,322,480.26 (10.2%); £3,700,387.83 -> £3,322,480.38 (10.2%); £3,700,388.06 -> £3,322,480.50 (10.2%); £3,700,388.29 -> £3,322,480.53 (10.2%); £3,700,388.53 -> £3,322,480.56 (10.2%); £3,700,388.75 -> £3,322,480.58 (10.2%); £3,700,388.95 -> £3,322,480.61 (10.2%); £3,700,389.13 -> £3,322,480.63 (10.2%); £3,700,389.29 -> £3,322,480.65 (10.2%); £3,700,389.45 -> £3,322,480.66 (10.2%); £3,700,389.62 -> £3,322,480.68 (10.2%); £3,700,389.78 -> £3,322,480.70 (10.2%); £3,700,389.94 -> £3,322,480.72 (10.2%); £3,700,390.10 -> £3,322,480.73 (10.2%); £3,700,390.27 -> £3,322,480.75 (10.2%); £3,700,390.43 -> £3,322,480.77 (10.2%); £3,700,390.60 -> £3,322,480.78 (10.2%); £3,700,390.76 -> £3,322,480.80 (10.2%); £3,700,390.92 -> £3,322,480.82 (10.2%); £3,700,391.09 -> £3,322,480.93 (10.2%); £3,700,391.25 -> £3,322,481.04 (10.2%); £3,700,391.43 -> £3,322,481.15 (10.2%); £3,700,391.64 -> £3,322,481.26 (10.2%); £3,700,391.86 -> £3,322,481.38 (10.2%); £3,700,392.10 -> £3,322,481.49 (10.2%); £3,700,392.35 -> £3,322,481.61 (10.2%); £3,700,392.61 -> £3,322,481.72 (10.2%); £3,700,392.89 -> £3,322,481.75 (10.2%); £3,700,393.17 -> £3,322,481.77 (10.2%); £3,700,393.44 -> £3,322,481.79 (10.2%); £3,700,393.71 -> £3,322,481.82 (10.2%); £3,700,393.98 -> £3,322,481.84 (10.2%); £3,700,394.25 -> £3,322,481.87 (10.2%); £3,700,394.52 -> £3,322,481.89 (10.2%); £3,700,394.78 -> £3,322,481.91 (10.2%); £3,700,395.05 -> £3,322,481.93 (10.2%); £3,700,395.32 -> £3,322,481.96 (10.2%); £3,700,395.59 -> £3,322,481.98 (10.2%); £3,700,395.87 -> £3,322,482.01 (10.2%); £3,700,396.13 -> £3,322,482.03 (10.2%); £3,700,396.34 -> £3,322,482.15 (10.2%); £3,700,396.54 -> £3,322,482.28 (10.2%); £3,700,396.74 -> £3,322,482.40 (10.2%); £3,700,396.94 -> £3,322,482.53 (10.2%); £3,700,397.16 -> £3,322,482.66 (10.2%); £3,700,397.43 -> £3,322,482.79 (10.2%); £3,700,397.71 -> £3,322,482.92 (10.2%); £3,700,397.99 -> £3,322,483.04 (10.2%); £3,700,398.26 -> £3,322,483.17 (10.2%); £3,700,398.53 -> £3,322,483.29 (10.2%); £3,700,398.80 -> £3,322,483.41 (10.2%); £3,700,399.07 -> £3,322,483.44 (10.2%); £3,700,399.34 -> £3,322,483.46 (10.2%); £3,700,399.59 -> £3,322,483.49 (10.2%); £3,700,399.82 -> £3,322,483.51 (10.2%); £3,700,400.04 -> £3,322,483.53 (10.2%); £3,700,400.21 -> £3,322,483.55 (10.2%); £3,700,400.37 -> £3,322,483.57 (10.2%); £3,700,400.54 -> £3,322,483.59 (10.2%); £3,700,400.71 -> £3,322,483.60 (10.2%); £3,700,400.88 -> £3,322,483.62 (10.2%); £3,700,401.04 -> £3,322,483.64 (10.2%); £3,700,401.21 -> £3,322,483.65 (10.2%); £3,700,401.37 -> £3,322,483.67 (10.2%); £3,700,401.53 -> £3,322,483.69 (10.2%); £3,700,401.70 -> £3,322,483.70 (10.2%); £3,700,401.87 -> £3,322,483.72 (10.2%); £3,700,402.03 -> £3,322,483.85 (10.2%); £3,700,402.20 -> £3,322,483.98 (10.2%); £3,700,402.39 -> £3,322,484.11 (10.2%); £3,700,402.59 -> £3,322,484.25 (10.2%); £3,700,402.81 -> £3,322,484.38 (10.2%); £3,700,403.04 -> £3,322,484.51 (10.2%); £3,700,403.30 -> £3,322,484.64 (10.2%); £3,700,403.57 -> £3,322,484.77 (10.2%); £3,700,403.84 -> £3,322,484.80 (10.2%); £3,700,404.12 -> £3,322,484.82 (10.2%); £3,700,404.40 -> £3,322,484.85 (10.2%); £3,700,404.68 -> £3,322,484.87 (10.2%); £3,700,404.95 -> £3,322,484.89 (10.2%); £3,700,405.23 -> £3,322,484.92 (10.2%); £3,700,405.49 -> £3,322,484.94 (10.2%); £3,700,405.77 -> £3,322,484.97 (10.2%); £3,700,406.04 -> £3,322,484.99 (10.2%); £3,700,406.32 -> £3,322,485.01 (10.2%); £3,700,406.58 -> £3,322,485.04 (10.2%); £3,700,406.85 -> £3,322,485.06 (10.2%); £3,700,407.13 -> £3,322,485.09 (10.2%); £3,700,407.33 -> £3,322,485.22 (10.2%); £3,700,407.54 -> £3,322,485.36 (10.2%); £3,700,407.75 -> £3,322,485.50 (10.2%); £3,700,407.95 -> £3,322,485.63 (10.2%); £3,700,408.15 -> £3,322,485.77 (10.2%); £3,700,408.36 -> £3,322,485.90 (10.2%); £3,700,408.57 -> £3,322,486.04 (10.2%); £3,700,408.84 -> £3,322,486.17 (10.2%); £3,700,409.12 -> £3,322,486.30 (10.2%); £3,700,409.38 -> £3,322,486.43 (10.2%); £3,700,409.66 -> £3,322,486.57 (10.2%); £3,700,409.94 -> £3,322,486.59 (10.2%); £3,700,410.21 -> £3,322,486.62 (10.2%); £3,700,410.46 -> £3,322,486.65 (10.2%); £3,700,410.69 -> £3,322,486.67 (10.2%); £3,700,410.89 -> £3,322,486.69 (10.2%); £3,700,411.06 -> £3,322,486.71 (10.2%); £3,700,411.23 -> £3,322,486.73 (10.2%); £3,700,411.39 -> £3,322,486.74 (10.2%); £3,700,411.55 -> £3,322,486.76 (10.2%); £3,700,411.72 -> £3,322,486.78 (10.2%); £3,700,411.89 -> £3,322,486.79 (10.2%); £3,700,412.05 -> £3,322,486.81 (10.2%); £3,700,412.22 -> £3,322,486.83 (10.2%); £3,700,412.38 -> £3,322,486.84 (10.2%); £3,700,412.55 -> £3,322,486.86 (10.2%); £3,700,412.71 -> £3,322,486.88 (10.2%); £3,700,412.88 -> £3,322,487.07 (10.2%); £3,700,413.04 -> £3,322,487.26 (10.2%); £3,700,413.23 -> £3,322,487.47 (10.2%); £3,700,413.43 -> £3,322,487.67 (10.2%); £3,700,413.66 -> £3,322,487.87 (10.2%); £3,700,413.90 -> £3,322,488.07 (10.2%); £3,700,414.15 -> £3,322,488.27 (10.2%); £3,700,414.44 -> £3,322,488.46 (10.2%); £3,700,414.72 -> £3,322,488.48 (10.2%); £3,700,415.00 -> £3,322,488.51 (10.2%); £3,700,415.28 -> £3,322,488.53 (10.2%); £3,700,415.56 -> £3,322,488.56 (10.2%); £3,700,415.83 -> £3,322,488.58 (10.2%); £3,700,416.11 -> £3,322,488.60 (10.2%); £3,700,416.38 -> £3,322,488.63 (10.2%); £3,700,416.65 -> £3,322,488.65 (10.2%); £3,700,416.92 -> £3,322,488.67 (10.2%); £3,700,417.21 -> £3,322,488.70 (10.2%); £3,700,417.48 -> £3,322,488.72 (10.2%); £3,700,417.75 -> £3,322,488.75 (10.2%); £3,700,418.03 -> £3,322,488.78 (10.2%); £3,700,418.24 -> £3,322,488.97 (10.2%); £3,700,418.44 -> £3,322,489.18 (10.2%); £3,700,418.72 -> £3,322,489.37 (10.2%); £3,700,418.93 -> £3,322,489.58 (10.2%); £3,700,419.12 -> £3,322,489.77 (10.2%); £3,700,419.33 -> £3,322,489.98 (10.2%); £3,700,419.60 -> £3,322,490.19 (10.2%); £3,700,419.88 -> £3,322,490.39 (10.2%); £3,700,420.14 -> £3,322,490.60 (10.2%); £3,700,420.42 -> £3,322,490.80 (10.2%); £3,700,420.69 -> £3,322,490.99 (10.2%); £3,700,420.97 -> £3,322,491.02 (10.2%); £3,700,421.25 -> £3,322,491.04 (10.2%); £3,700,421.51 -> £3,322,491.07 (10.2%); £3,700,421.75 -> £3,322,491.09 (10.2%); £3,700,421.96 -> £3,322,491.11 (10.2%); £3,700,422.13 -> £3,322,491.13 (10.2%); £3,700,422.29 -> £3,322,491.15 (10.2%); £3,700,422.46 -> £3,322,491.16 (10.2%); £3,700,422.62 -> £3,322,491.18 (10.2%); £3,700,422.79 -> £3,322,491.20 (10.2%); £3,700,422.96 -> £3,322,491.22 (10.2%); £3,700,423.12 -> £3,322,491.23 (10.2%); £3,700,423.29 -> £3,322,491.25 (10.2%); £3,700,423.45 -> £3,322,491.26 (10.2%); £3,700,423.61 -> £3,322,491.28 (10.2%); £3,700,423.77 -> £3,322,491.30 (10.2%); £3,700,423.94 -> £3,322,491.50 (10.2%); £3,700,424.10 -> £3,322,491.70 (10.2%); £3,700,424.29 -> £3,322,491.91 (10.2%); £3,700,424.49 -> £3,322,492.13 (10.2%); £3,700,424.71 -> £3,322,492.35 (10.2%); £3,700,424.95 -> £3,322,492.57 (10.2%); £3,700,425.21 -> £3,322,492.78 (10.2%); £3,700,425.49 -> £3,322,492.99 (10.2%); £3,700,425.76 -> £3,322,493.01 (10.2%); £3,700,426.04 -> £3,322,493.03 (10.2%); £3,700,426.32 -> £3,322,493.06 (10.2%); £3,700,426.59 -> £3,322,493.08 (10.2%); £3,700,426.87 -> £3,322,493.11 (10.2%); £3,700,427.13 -> £3,322,493.13 (10.2%); £3,700,427.41 -> £3,322,493.15 (10.2%); £3,700,427.69 -> £3,322,493.18 (10.2%); £3,700,427.96 -> £3,322,493.20 (10.2%); £3,700,428.23 -> £3,322,493.22 (10.2%); £3,700,428.51 -> £3,322,493.25 (10.2%); £3,700,428.78 -> £3,322,493.27 (10.2%); £3,700,429.05 -> £3,322,493.30 (10.2%); £3,700,429.25 -> £3,322,493.51 (10.2%); £3,700,429.54 -> £3,322,493.73 (10.2%); £3,700,429.74 -> £3,322,493.95 (10.2%); £3,700,430.01 -> £3,322,494.17 (10.2%); £3,700,430.28 -> £3,322,494.39 (10.2%); £3,700,430.55 -> £3,322,494.61 (10.2%); £3,700,430.82 -> £3,322,494.83 (10.2%); £3,700,431.10 -> £3,322,495.04 (10.2%); £3,700,431.38 -> £3,322,495.25 (10.2%); £3,700,431.66 -> £3,322,495.46 (10.2%); £3,700,431.93 -> £3,322,495.68 (10.2%); £3,700,432.22 -> £3,322,495.70 (10.2%); £3,700,432.49 -> £3,322,495.73 (10.2%); £3,700,432.74 -> £3,322,495.76 (10.2%); £3,700,432.98 -> £3,322,495.78 (10.2%); £3,700,433.19 -> £3,322,495.80 (10.2%); £3,700,433.36 -> £3,322,495.82 (10.2%); £3,700,433.52 -> £3,322,495.83 (10.2%); £3,700,433.69 -> £3,322,495.85 (10.2%); £3,700,433.85 -> £3,322,495.87 (10.2%); £3,700,434.01 -> £3,322,495.89 (10.2%); £3,700,434.18 -> £3,322,495.90 (10.2%); £3,700,434.34 -> £3,322,495.92 (10.2%); £3,700,434.50 -> £3,322,495.93 (10.2%); £3,700,434.67 -> £3,322,495.95 (10.2%); £3,700,434.83 -> £3,322,495.97 (10.2%); £3,700,434.99 -> £3,322,495.99 (10.2%); £3,700,435.17 -> £3,322,496.14 (10.2%); £3,700,435.33 -> £3,322,496.30 (10.2%); £3,700,435.51 -> £3,322,496.46 (10.2%); £3,700,435.71 -> £3,322,496.63 (10.2%); £3,700,435.93 -> £3,322,496.79 (10.2%); £3,700,436.15 -> £3,322,496.96 (10.2%); £3,700,436.41 -> £3,322,497.12 (10.2%); £3,700,436.68 -> £3,322,497.29 (10.2%); £3,700,436.95 -> £3,322,497.31 (10.2%); £3,700,437.23 -> £3,322,497.34 (10.2%); £3,700,437.49 -> £3,322,497.36 (10.2%); £3,700,437.77 -> £3,322,497.39 (10.2%); £3,700,438.03 -> £3,322,497.41 (10.2%); £3,700,438.29 -> £3,322,497.44 (10.2%); £3,700,438.56 -> £3,322,497.46 (10.2%); £3,700,438.82 -> £3,322,497.49 (10.2%); £3,700,439.10 -> £3,322,497.51 (10.2%); £3,700,439.39 -> £3,322,497.54 (10.2%); £3,700,439.65 -> £3,322,497.56 (10.2%); £3,700,439.93 -> £3,322,497.58 (10.2%); £3,700,440.19 -> £3,322,497.61 (10.2%); £3,700,440.46 -> £3,322,497.78 (10.2%); £3,700,440.73 -> £3,322,497.96 (10.2%); £3,700,441.01 -> £3,322,498.13 (10.2%); £3,700,441.29 -> £3,322,498.31 (10.2%); £3,700,441.56 -> £3,322,498.48 (10.2%); £3,700,441.76 -> £3,322,498.65 (10.2%); £3,700,441.97 -> £3,322,498.82 (10.2%); £3,700,442.24 -> £3,322,498.99 (10.2%); £3,700,442.51 -> £3,322,499.16 (10.2%); £3,700,442.78 -> £3,322,499.33 (10.2%); £3,700,443.05 -> £3,322,499.49 (10.2%); £3,700,443.32 -> £3,322,499.52 (10.2%); £3,700,443.59 -> £3,322,499.55 (10.2%); £3,700,443.84 -> £3,322,499.57 (10.2%); £3,700,444.07 -> £3,322,499.59 (10.2%); £3,700,444.28 -> £3,322,499.62 (10.2%); £3,700,444.43 -> £3,322,499.64 (10.2%); £3,700,444.57 -> £3,322,499.65 (10.2%); £3,700,444.72 -> £3,322,499.67 (10.2%); £3,700,444.86 -> £3,322,499.69 (10.2%); £3,700,445.00 -> £3,322,499.71 (10.2%); £3,700,445.14 -> £3,322,499.72 (10.2%); £3,700,445.28 -> £3,322,499.74 (10.2%); £3,700,445.42 -> £3,322,499.76 (10.2%); £3,700,445.56 -> £3,322,499.77 (10.2%); £3,700,445.71 -> £3,322,499.79 (10.2%); £3,700,445.85 -> £3,322,499.81 (10.2%); £3,700,445.99 -> £3,322,499.95 (10.2%); £3,700,446.14 -> £3,322,500.10 (10.2%); £3,700,446.30 -> £3,322,500.26 (10.2%); £3,700,446.48 -> £3,322,500.41 (10.2%); £3,700,446.67 -> £3,322,500.57 (10.2%); £3,700,446.88 -> £3,322,500.74 (10.2%); £3,700,447.10 -> £3,322,500.90 (10.2%); £3,700,447.33 -> £3,322,501.06 (10.2%); £3,700,447.57 -> £3,322,501.09 (10.2%); £3,700,447.81 -> £3,322,501.12 (10.2%); £3,700,448.05 -> £3,322,501.14 (10.2%); £3,700,448.30 -> £3,322,501.17 (10.2%); £3,700,448.53 -> £3,322,501.20 (10.2%); £3,700,448.76 -> £3,322,501.22 (10.2%); £3,700,449.00 -> £3,322,501.25 (10.2%); £3,700,449.24 -> £3,322,501.28 (10.2%); £3,700,449.48 -> £3,322,501.30 (10.2%); £3,700,449.72 -> £3,322,501.33 (10.2%); £3,700,449.96 -> £3,322,501.35 (10.2%); £3,700,450.20 -> £3,322,501.38 (10.2%); £3,700,450.44 -> £3,322,501.41 (10.2%); £3,700,450.68 -> £3,322,501.57 (10.2%); £3,700,450.92 -> £3,322,501.74 (10.2%); £3,700,451.15 -> £3,322,501.90 (10.2%); £3,700,451.33 -> £3,322,502.08 (10.2%); £3,700,451.56 -> £3,322,502.24 (10.2%); £3,700,451.74 -> £3,322,502.41 (10.2%); £3,700,451.92 -> £3,322,502.58 (10.2%); £3,700,452.17 -> £3,322,502.74 (10.2%); £3,700,452.41 -> £3,322,502.91 (10.2%); £3,700,452.65 -> £3,322,503.08 (10.2%); £3,700,452.89 -> £3,322,503.24 (10.2%); £3,700,453.13 -> £3,322,503.27 (10.2%); £3,700,453.37 -> £3,322,503.29 (10.2%); £3,700,453.59 -> £3,322,503.32 (10.2%); £3,700,453.80 -> £3,322,503.34 (10.2%); £3,700,453.99 -> £3,322,503.36 (10.2%); £3,700,454.13 -> £3,322,503.38 (10.2%); £3,700,454.27 -> £3,322,503.40 (10.2%); £3,700,454.41 -> £3,322,503.42 (10.2%); £3,700,454.54 -> £3,322,503.44 (10.2%); £3,700,454.68 -> £3,322,503.46 (10.2%); £3,700,454.83 -> £3,322,503.47 (10.2%); £3,700,454.97 -> £3,322,503.49 (10.2%); £3,700,455.11 -> £3,322,503.51 (10.2%); £3,700,455.25 -> £3,322,503.52 (10.2%); £3,700,455.39 -> £3,322,503.54 (10.2%); £3,700,455.53 -> £3,322,503.56 (10.2%); £3,700,455.67 -> £3,322,503.72 (10.2%); £3,700,455.80 -> £3,322,503.88 (10.2%); £3,700,455.96 -> £3,322,504.03 (10.2%); £3,700,456.12 -> £3,322,504.19 (10.2%); £3,700,456.31 -> £3,322,504.36 (10.2%); £3,700,456.52 -> £3,322,504.53 (10.2%); £3,700,456.74 -> £3,322,504.70 (10.2%); £3,700,456.98 -> £3,322,504.87 (10.2%); £3,700,457.21 -> £3,322,504.90 (10.2%); £3,700,457.45 -> £3,322,504.93 (10.2%); £3,700,457.68 -> £3,322,504.97 (10.2%); £3,700,457.92 -> £3,322,505.00 (10.2%); £3,700,458.15 -> £3,322,505.03 (10.2%); £3,700,458.39 -> £3,322,505.06 (10.2%); £3,700,458.62 -> £3,322,505.09 (10.2%); £3,700,458.86 -> £3,322,505.12 (10.2%); £3,700,459.09 -> £3,322,505.15 (10.2%); £3,700,459.33 -> £3,322,505.18 (10.2%); £3,700,459.56 -> £3,322,505.21 (10.2%); £3,700,459.79 -> £3,322,505.24 (10.2%); £3,700,460.02 -> £3,322,505.27 (10.2%); £3,700,460.26 -> £3,322,505.44 (10.2%); £3,700,460.49 -> £3,322,505.61 (10.2%); £3,700,460.67 -> £3,322,505.79 (10.2%); £3,700,460.84 -> £3,322,505.96 (10.2%); £3,700,461.02 -> £3,322,506.13 (10.2%); £3,700,461.20 -> £3,322,506.30 (10.2%); £3,700,461.38 -> £3,322,506.48 (10.2%); £3,700,461.61 -> £3,322,506.65 (10.2%); £3,700,461.84 -> £3,322,506.83 (10.2%); £3,700,462.08 -> £3,322,507.00 (10.2%); £3,700,462.31 -> £3,322,507.17 (10.2%); £3,700,462.54 -> £3,322,507.19 (10.2%); £3,700,462.78 -> £3,322,507.22 (10.2%); £3,700,463.00 -> £3,322,507.24 (10.2%); £3,700,463.20 -> £3,322,507.27 (10.2%); £3,700,463.38 -> £3,322,507.29 (10.2%); £3,700,463.54 -> £3,322,507.31 (10.2%); £3,700,463.69 -> £3,322,507.32 (10.2%); £3,700,463.85 -> £3,322,507.34 (10.2%); £3,700,464.00 -> £3,322,507.36 (10.2%); £3,700,464.16 -> £3,322,507.37 (10.2%); £3,700,464.32 -> £3,322,507.39 (10.2%); £3,700,464.47 -> £3,322,507.41 (10.2%); £3,700,464.63 -> £3,322,507.42 (10.2%); £3,700,464.78 -> £3,322,507.44 (10.2%); £3,700,464.93 -> £3,322,507.46 (10.2%); £3,700,465.09 -> £3,322,507.47 (10.2%); £3,700,465.24 -> £3,322,507.65 (10.2%); £3,700,465.40 -> £3,322,507.83 (10.2%); £3,700,465.57 -> £3,322,508.01 (10.2%); £3,700,465.76 -> £3,322,508.19 (10.2%); £3,700,465.98 -> £3,322,508.37 (10.2%); £3,700,466.20 -> £3,322,508.56 (10.2%); £3,700,466.44 -> £3,322,508.74 (10.2%); £3,700,466.70 -> £3,322,508.92 (10.2%); £3,700,466.96 -> £3,322,508.95 (10.2%); £3,700,467.21 -> £3,322,508.97 (10.2%); £3,700,467.47 -> £3,322,509.00 (10.2%); £3,700,467.73 -> £3,322,509.02 (10.2%); £3,700,467.99 -> £3,322,509.04 (10.2%); £3,700,468.25 -> £3,322,509.07 (10.2%); £3,700,468.51 -> £3,322,509.09 (10.2%); £3,700,468.77 -> £3,322,509.12 (10.2%); £3,700,469.03 -> £3,322,509.14 (10.2%); £3,700,469.29 -> £3,322,509.16 (10.2%); £3,700,469.54 -> £3,322,509.19 (10.2%); £3,700,469.81 -> £3,322,509.21 (10.2%); £3,700,470.07 -> £3,322,509.24 (10.2%); £3,700,470.27 -> £3,322,509.42 (10.2%); £3,700,470.46 -> £3,322,509.61 (10.2%); £3,700,470.65 -> £3,322,509.79 (10.2%); £3,700,470.84 -> £3,322,509.98 (10.2%); £3,700,471.04 -> £3,322,510.16 (10.2%); £3,700,471.23 -> £3,322,510.35 (10.2%); £3,700,471.43 -> £3,322,510.53 (10.2%); £3,700,471.69 -> £3,322,510.71 (10.2%); £3,700,471.94 -> £3,322,510.90 (10.2%); £3,700,472.20 -> £3,322,511.08 (10.2%); £3,700,472.46 -> £3,322,511.26 (10.2%); £3,700,472.72 -> £3,322,511.29 (10.2%); £3,700,472.98 -> £3,322,511.32 (10.2%); £3,700,473.22 -> £3,322,511.34 (10.2%); £3,700,473.44 -> £3,322,511.37 (10.2%); £3,700,473.64 -> £3,322,511.39 (10.2%); £3,700,473.80 -> £3,322,511.41 (10.2%); £3,700,473.96 -> £3,322,511.42 (10.2%); £3,700,474.12 -> £3,322,511.44 (10.2%); £3,700,474.28 -> £3,322,511.46 (10.2%); £3,700,474.44 -> £3,322,511.47 (10.2%); £3,700,474.59 -> £3,322,511.49 (10.2%); £3,700,474.74 -> £3,322,511.51 (10.2%); £3,700,474.89 -> £3,322,511.52 (10.2%); £3,700,475.05 -> £3,322,511.54 (10.2%); £3,700,475.21 -> £3,322,511.56 (10.2%); £3,700,475.36 -> £3,322,511.57 (10.2%); £3,700,475.52 -> £3,322,511.72 (10.2%); £3,700,475.68 -> £3,322,511.87 (10.2%); £3,700,475.85 -> £3,322,512.02 (10.2%); £3,700,476.04 -> £3,322,512.18 (10.2%); £3,700,476.26 -> £3,322,512.34 (10.2%); £3,700,476.49 -> £3,322,512.49 (10.2%); £3,700,476.72 -> £3,322,512.65 (10.2%); £3,700,476.98 -> £3,322,512.80 (10.2%); £3,700,477.24 -> £3,322,512.82 (10.2%); £3,700,477.49 -> £3,322,512.85 (10.2%); £3,700,477.75 -> £3,322,512.87 (10.2%); £3,700,478.01 -> £3,322,512.89 (10.2%); £3,700,478.27 -> £3,322,512.92 (10.2%); £3,700,478.54 -> £3,322,512.94 (10.2%); £3,700,478.79 -> £3,322,512.97 (10.2%); £3,700,479.06 -> £3,322,512.99 (10.2%); £3,700,479.32 -> £3,322,513.01 (10.2%); £3,700,479.58 -> £3,322,513.04 (10.2%); £3,700,479.84 -> £3,322,513.06 (10.2%); £3,700,480.09 -> £3,322,513.09 (10.2%); £3,700,480.35 -> £3,322,513.12 (10.2%); £3,700,480.60 -> £3,322,513.28 (10.2%); £3,700,480.87 -> £3,322,513.45 (10.2%); £3,700,481.12 -> £3,322,513.61 (10.2%); £3,700,481.39 -> £3,322,513.78 (10.2%); £3,700,481.64 -> £3,322,513.95 (10.2%); £3,700,481.89 -> £3,322,514.12 (10.2%); £3,700,482.15 -> £3,322,514.28 (10.2%); £3,700,482.41 -> £3,322,514.45 (10.2%); £3,700,482.67 -> £3,322,514.61 (10.2%); £3,700,482.93 -> £3,322,514.77 (10.2%); £3,700,483.19 -> £3,322,514.92 (10.2%); £3,700,483.46 -> £3,322,514.95 (10.2%); £3,700,483.72 -> £3,322,514.98 (10.2%); £3,700,483.96 -> £3,322,515.00 (10.2%); £3,700,484.18 -> £3,322,515.02 (10.2%); £3,700,484.38 -> £3,322,515.04 (10.2%); £3,700,484.54 -> £3,322,515.06 (10.2%); £3,700,484.69 -> £3,322,515.08 (10.2%); £3,700,484.85 -> £3,322,515.10 (10.2%); £3,700,485.00 -> £3,322,515.12 (10.2%); £3,700,485.15 -> £3,322,515.13 (10.2%); £3,700,485.30 -> £3,322,515.15 (10.2%); £3,700,485.46 -> £3,322,515.17 (10.2%); £3,700,485.61 -> £3,322,515.18 (10.2%); £3,700,485.77 -> £3,322,515.20 (10.2%); £3,700,485.93 -> £3,322,515.22 (10.2%); £3,700,486.08 -> £3,322,515.23 (10.2%); £3,700,486.24 -> £3,322,515.32 (10.2%); £3,700,486.40 -> £3,322,515.41 (10.2%); £3,700,486.58 -> £3,322,515.51 (10.2%); £3,700,486.77 -> £3,322,515.61 (10.2%); £3,700,486.98 -> £3,322,515.71 (10.2%); £3,700,487.20 -> £3,322,515.81 (10.2%); £3,700,487.44 -> £3,322,515.90 (10.2%); £3,700,487.70 -> £3,322,515.99 (10.2%); £3,700,487.96 -> £3,322,516.02 (10.2%); £3,700,488.22 -> £3,322,516.04 (10.2%); £3,700,488.48 -> £3,322,516.07 (10.2%); £3,700,488.74 -> £3,322,516.09 (10.2%); £3,700,489.00 -> £3,322,516.12 (10.2%); £3,700,489.24 -> £3,322,516.14 (10.2%); £3,700,489.49 -> £3,322,516.16 (10.2%); £3,700,489.76 -> £3,322,516.19 (10.2%); £3,700,490.02 -> £3,322,516.21 (10.2%); £3,700,490.28 -> £3,322,516.23 (10.2%); £3,700,490.54 -> £3,322,516.26 (10.2%); £3,700,490.80 -> £3,322,516.28 (10.2%); £3,700,491.07 -> £3,322,516.31 (10.2%); £3,700,491.32 -> £3,322,516.42 (10.2%); £3,700,491.52 -> £3,322,516.52 (10.2%); £3,700,491.71 -> £3,322,516.63 (10.2%); £3,700,491.90 -> £3,322,516.75 (10.2%); £3,700,492.16 -> £3,322,516.86 (10.2%); £3,700,492.41 -> £3,322,516.97 (10.2%); £3,700,492.67 -> £3,322,517.08 (10.2%); £3,700,492.93 -> £3,322,517.19 (10.2%); £3,700,493.20 -> £3,322,517.30 (10.2%); £3,700,493.46 -> £3,322,517.41 (10.2%); £3,700,493.72 -> £3,322,517.51 (10.2%); £3,700,493.97 -> £3,322,517.54 (10.2%); £3,700,494.23 -> £3,322,517.57 (10.2%); £3,700,494.47 -> £3,322,517.59 (10.2%); £3,700,494.69 -> £3,322,517.62 (10.2%); £3,700,494.89 -> £3,322,517.64 (10.2%); £3,700,495.05 -> £3,322,517.65 (10.2%); £3,700,495.20 -> £3,322,517.67 (10.2%); £3,700,495.36 -> £3,322,517.69 (10.2%); £3,700,495.51 -> £3,322,517.71 (10.2%); £3,700,495.67 -> £3,322,517.72 (10.2%); £3,700,495.82 -> £3,322,517.74 (10.2%); £3,700,495.98 -> £3,322,517.76 (10.2%); £3,700,496.15 -> £3,322,517.77 (10.2%); £3,700,496.31 -> £3,322,517.79 (10.2%); £3,700,496.47 -> £3,322,517.81 (10.2%); £3,700,496.62 -> £3,322,517.82 (10.2%); £3,700,496.78 -> £3,322,517.89 (10.2%); £3,700,496.93 -> £3,322,517.95 (10.2%); £3,700,497.10 -> £3,322,518.02 (10.2%); £3,700,497.29 -> £3,322,518.10 (10.2%); £3,700,497.51 -> £3,322,518.17 (10.2%); £3,700,497.73 -> £3,322,518.25 (10.2%); £3,700,497.98 -> £3,322,518.32 (10.2%); £3,700,498.24 -> £3,322,518.39 (10.2%); £3,700,498.51 -> £3,322,518.41 (10.2%); £3,700,498.77 -> £3,322,518.44 (10.2%); £3,700,499.04 -> £3,322,518.46 (10.2%); £3,700,499.30 -> £3,322,518.48 (10.2%); £3,700,499.56 -> £3,322,518.51 (10.2%); £3,700,499.82 -> £3,322,518.53 (10.2%); £3,700,500.09 -> £3,322,518.56 (10.2%); £3,700,500.35 -> £3,322,518.58 (10.2%); £3,700,500.61 -> £3,322,518.60 (10.2%); £3,700,500.86 -> £3,322,518.63 (10.2%); £3,700,501.11 -> £3,322,518.65 (10.2%); £3,700,501.38 -> £3,322,518.68 (10.2%); £3,700,501.64 -> £3,322,518.71 (10.2%); £3,700,501.89 -> £3,322,518.79 (10.2%); £3,700,502.16 -> £3,322,518.88 (10.2%); £3,700,502.42 -> £3,322,518.97 (10.2%); £3,700,502.67 -> £3,322,519.06 (10.2%); £3,700,502.94 -> £3,322,519.15 (10.2%); £3,700,503.20 -> £3,322,519.24 (10.2%); £3,700,503.47 -> £3,322,519.33 (10.2%); £3,700,503.72 -> £3,322,519.41 (10.2%); £3,700,503.98 -> £3,322,519.50 (10.2%); £3,700,504.23 -> £3,322,519.58 (10.2%); £3,700,504.49 -> £3,322,519.66 (10.2%); £3,700,504.74 -> £3,322,519.69 (10.2%); £3,700,505.00 -> £3,322,519.72 (10.2%); £3,700,505.24 -> £3,322,519.74 (10.2%); £3,700,505.46 -> £3,322,519.76 (10.2%); £3,700,505.67 -> £3,322,519.78 (10.2%); £3,700,505.82 -> £3,322,519.80 (10.2%); £3,700,505.98 -> £3,322,519.82 (10.2%); £3,700,506.13 -> £3,322,519.84 (10.2%); £3,700,506.29 -> £3,322,519.85 (10.2%); £3,700,506.45 -> £3,322,519.87 (10.2%); £3,700,506.61 -> £3,322,519.89 (10.2%); £3,700,506.77 -> £3,322,519.90 (10.2%); £3,700,506.93 -> £3,322,519.92 (10.2%); £3,700,507.08 -> £3,322,519.94 (10.2%); £3,700,507.25 -> £3,322,519.95 (10.2%); £3,700,507.40 -> £3,322,519.97 (10.2%); £3,700,507.56 -> £3,322,520.07 (10.2%); £3,700,507.72 -> £3,322,520.18 (10.2%); £3,700,507.90 -> £3,322,520.29 (10.2%); £3,700,508.09 -> £3,322,520.41 (10.2%); £3,700,508.31 -> £3,322,520.52 (10.2%); £3,700,508.53 -> £3,322,520.63 (10.2%); £3,700,508.78 -> £3,322,520.73 (10.2%); £3,700,509.05 -> £3,322,520.84 (10.2%); £3,700,509.31 -> £3,322,520.87 (10.2%); £3,700,509.58 -> £3,322,520.89 (10.2%); £3,700,509.83 -> £3,322,520.91 (10.2%); £3,700,510.08 -> £3,322,520.94 (10.2%); £3,700,510.35 -> £3,322,520.96 (10.2%); £3,700,510.61 -> £3,322,520.99 (10.2%); £3,700,510.86 -> £3,322,521.01 (10.2%); £3,700,511.12 -> £3,322,521.03 (10.2%); £3,700,511.38 -> £3,322,521.06 (10.2%); £3,700,511.64 -> £3,322,521.08 (10.2%); £3,700,511.90 -> £3,322,521.10 (10.2%); £3,700,512.17 -> £3,322,521.13 (10.2%); £3,700,512.43 -> £3,322,521.16 (10.2%); £3,700,512.62 -> £3,322,521.27 (10.2%); £3,700,512.90 -> £3,322,521.40 (10.2%); £3,700,513.09 -> £3,322,521.52 (10.2%); £3,700,513.28 -> £3,322,521.64 (10.2%); £3,700,513.48 -> £3,322,521.76 (10.2%); £3,700,513.67 -> £3,322,521.88 (10.2%); £3,700,513.86 -> £3,322,522.00 (10.2%); £3,700,514.12 -> £3,322,522.12 (10.2%); £3,700,514.38 -> £3,322,522.23 (10.2%); £3,700,514.64 -> £3,322,522.35 (10.2%); £3,700,514.91 -> £3,322,522.47 (10.2%); £3,700,515.18 -> £3,322,522.50 (10.2%); £3,700,515.45 -> £3,322,522.53 (10.2%); £3,700,515.69 -> £3,322,522.55 (10.2%); £3,700,515.91 -> £3,322,522.57 (10.2%); £3,700,516.11 -> £3,322,522.60 (10.2%); £3,700,516.25 -> £3,322,522.62 (10.2%); £3,700,516.39 -> £3,322,522.63 (10.2%); £3,700,516.52 -> £3,322,522.65 (10.2%); £3,700,516.66 -> £3,322,522.67 (10.2%); £3,700,516.80 -> £3,322,522.69 (10.2%); £3,700,516.94 -> £3,322,522.70 (10.2%); £3,700,517.08 -> £3,322,522.72 (10.2%); £3,700,517.22 -> £3,322,522.74 (10.2%); £3,700,517.35 -> £3,322,522.75 (10.2%); £3,700,517.49 -> £3,322,522.77 (10.2%); £3,700,517.63 -> £3,322,522.79 (10.2%); £3,700,517.77 -> £3,322,522.88 (10.2%); £3,700,517.90 -> £3,322,522.97 (10.2%); £3,700,518.06 -> £3,322,523.06 (10.2%); £3,700,518.23 -> £3,322,523.15 (10.2%); £3,700,518.41 -> £3,322,523.25 (10.2%); £3,700,518.61 -> £3,322,523.34 (10.2%); £3,700,518.82 -> £3,322,523.44 (10.2%); £3,700,519.04 -> £3,322,523.54 (10.2%); £3,700,519.27 -> £3,322,523.57 (10.2%); £3,700,519.49 -> £3,322,523.60 (10.2%); £3,700,519.71 -> £3,322,523.62 (10.2%); £3,700,519.94 -> £3,322,523.65 (10.2%); £3,700,520.18 -> £3,322,523.68 (10.2%); £3,700,520.41 -> £3,322,523.71 (10.2%); £3,700,520.64 -> £3,322,523.73 (10.2%); £3,700,520.86 -> £3,322,523.76 (10.2%); £3,700,521.08 -> £3,322,523.78 (10.2%); £3,700,521.31 -> £3,322,523.81 (10.2%); £3,700,521.54 -> £3,322,523.83 (10.2%); £3,700,521.77 -> £3,322,523.86 (10.2%); £3,700,521.99 -> £3,322,523.89 (10.2%); £3,700,522.17 -> £3,322,523.99 (10.2%); £3,700,522.34 -> £3,322,524.10 (10.2%); £3,700,522.51 -> £3,322,524.21 (10.2%); £3,700,522.68 -> £3,322,524.32 (10.2%); £3,700,522.85 -> £3,322,524.43 (10.2%); £3,700,523.03 -> £3,322,524.54 (10.2%); £3,700,523.19 -> £3,322,524.65 (10.2%); £3,700,523.42 -> £3,322,524.76 (10.2%); £3,700,523.65 -> £3,322,524.87 (10.2%); £3,700,523.89 -> £3,322,524.97 (10.2%); £3,700,524.11 -> £3,322,525.08 (10.2%); £3,700,524.33 -> £3,322,525.10 (10.2%); £3,700,524.57 -> £3,322,525.13 (10.2%); £3,700,524.78 -> £3,322,525.16 (10.2%); £3,700,524.97 -> £3,322,525.18 (10.2%); £3,700,525.14 -> £3,322,525.20 (10.2%); £3,700,525.28 -> £3,322,525.22 (10.2%); £3,700,525.42 -> £3,322,525.24 (10.2%); £3,700,525.56 -> £3,322,525.26 (10.2%); £3,700,525.70 -> £3,322,525.28 (10.2%); £3,700,525.84 -> £3,322,525.29 (10.2%); £3,700,525.97 -> £3,322,525.31 (10.2%); £3,700,526.11 -> £3,322,525.33 (10.2%); £3,700,526.25 -> £3,322,525.34 (10.2%); £3,700,526.39 -> £3,322,525.36 (10.2%); £3,700,526.53 -> £3,322,525.38 (10.2%); £3,700,526.66 -> £3,322,525.40 (10.2%); £3,700,526.80 -> £3,322,525.49 (10.2%); £3,700,526.94 -> £3,322,525.58 (10.2%); £3,700,527.10 -> £3,322,525.67 (10.2%); £3,700,527.26 -> £3,322,525.76 (10.2%); £3,700,527.45 -> £3,322,525.85 (10.2%); £3,700,527.64 -> £3,322,525.95 (10.2%); £3,700,527.86 -> £3,322,526.05 (10.2%); £3,700,528.09 -> £3,322,526.16 (10.2%); £3,700,528.32 -> £3,322,526.19 (10.2%); £3,700,528.55 -> £3,322,526.22 (10.2%); £3,700,528.78 -> £3,322,526.25 (10.2%); £3,700,529.01 -> £3,322,526.28 (10.2%); £3,700,529.24 -> £3,322,526.31 (10.2%); £3,700,529.46 -> £3,322,526.34 (10.2%); £3,700,529.70 -> £3,322,526.38 (10.2%); £3,700,529.92 -> £3,322,526.41 (10.2%); £3,700,530.15 -> £3,322,526.44 (10.2%); £3,700,530.38 -> £3,322,526.46 (10.2%); £3,700,530.62 -> £3,322,526.49 (10.2%); £3,700,530.85 -> £3,322,526.52 (10.2%); £3,700,531.08 -> £3,322,526.55 (10.2%); £3,700,531.31 -> £3,322,526.67 (10.2%); £3,700,531.55 -> £3,322,526.78 (10.2%); £3,700,531.78 -> £3,322,526.89 (10.2%); £3,700,531.94 -> £3,322,527.01 (10.2%); £3,700,532.17 -> £3,322,527.12 (10.2%); £3,700,532.34 -> £3,322,527.23 (10.2%); £3,700,532.51 -> £3,322,527.35 (10.2%); £3,700,532.74 -> £3,322,527.46 (10.2%); £3,700,532.98 -> £3,322,527.57 (10.2%); £3,700,533.21 -> £3,322,527.69 (10.2%); £3,700,533.43 -> £3,322,527.79 (10.2%); £3,700,533.66 -> £3,322,527.82 (10.2%); £3,700,533.88 -> £3,322,527.85 (10.2%); £3,700,534.09 -> £3,322,527.88 (10.2%); £3,700,534.28 -> £3,322,527.90 (10.2%); £3,700,534.46 -> £3,322,527.92 (10.2%); £3,700,534.62 -> £3,322,527.94 (10.2%); £3,700,534.78 -> £3,322,527.96 (10.2%); £3,700,534.94 -> £3,322,527.98 (10.2%); £3,700,535.10 -> £3,322,527.99 (10.2%); £3,700,535.27 -> £3,322,528.01 (10.2%); £3,700,535.42 -> £3,322,528.03 (10.2%); £3,700,535.58 -> £3,322,528.04 (10.2%); £3,700,535.74 -> £3,322,528.06 (10.2%); £3,700,535.90 -> £3,322,528.08 (10.2%); £3,700,536.05 -> £3,322,528.09 (10.2%); £3,700,536.22 -> £3,322,528.11 (10.2%); £3,700,536.38 -> £3,322,528.23 (10.2%); £3,700,536.54 -> £3,322,528.36 (10.2%); £3,700,536.71 -> £3,322,528.49 (10.2%); £3,700,536.91 -> £3,322,528.62 (10.2%); £3,700,537.11 -> £3,322,528.75 (10.2%); £3,700,537.34 -> £3,322,528.88 (10.2%); £3,700,537.59 -> £3,322,529.01 (10.2%); £3,700,537.85 -> £3,322,529.13 (10.2%); £3,700,538.11 -> £3,322,529.16 (10.2%); £3,700,538.37 -> £3,322,529.18 (10.2%); £3,700,538.63 -> £3,322,529.21 (10.2%); £3,700,538.90 -> £3,322,529.23 (10.2%); £3,700,539.17 -> £3,322,529.25 (10.2%); £3,700,539.43 -> £3,322,529.28 (10.2%); £3,700,539.70 -> £3,322,529.30 (10.2%); £3,700,539.96 -> £3,322,529.33 (10.2%); £3,700,540.24 -> £3,322,529.35 (10.2%); £3,700,540.50 -> £3,322,529.37 (10.2%); £3,700,540.76 -> £3,322,529.40 (10.2%); £3,700,541.02 -> £3,322,529.42 (10.2%); £3,700,541.28 -> £3,322,529.45 (10.2%); £3,700,541.54 -> £3,322,529.59 (10.2%); £3,700,541.74 -> £3,322,529.73 (10.2%); £3,700,541.93 -> £3,322,529.87 (10.2%); £3,700,542.13 -> £3,322,530.01 (10.2%); £3,700,542.39 -> £3,322,530.16 (10.2%); £3,700,542.65 -> £3,322,530.30 (10.2%); £3,700,542.91 -> £3,322,530.44 (10.2%); £3,700,543.18 -> £3,322,530.58 (10.2%); £3,700,543.44 -> £3,322,530.72 (10.2%); £3,700,543.71 -> £3,322,530.86 (10.2%); £3,700,543.97 -> £3,322,530.99 (10.2%); £3,700,544.24 -> £3,322,531.02 (10.2%); £3,700,544.51 -> £3,322,531.05 (10.2%); £3,700,544.76 -> £3,322,531.07 (10.2%); £3,700,544.98 -> £3,322,531.10 (10.2%); £3,700,545.18 -> £3,322,531.12 (10.2%); £3,700,545.34 -> £3,322,531.13 (10.2%); £3,700,545.50 -> £3,322,531.15 (10.2%); £3,700,545.66 -> £3,322,531.17 (10.2%); £3,700,545.82 -> £3,322,531.19 (10.2%); £3,700,545.98 -> £3,322,531.20 (10.2%); £3,700,546.14 -> £3,322,531.22 (10.2%); £3,700,546.30 -> £3,322,531.24 (10.2%); £3,700,546.46 -> £3,322,531.25 (10.2%); £3,700,546.61 -> £3,322,531.27 (10.2%); £3,700,546.77 -> £3,322,531.29 (10.2%); £3,700,546.93 -> £3,322,531.30 (10.2%); £3,700,547.08 -> £3,322,531.42 (10.2%); £3,700,547.24 -> £3,322,531.53 (10.2%); £3,700,547.42 -> £3,322,531.66 (10.2%); £3,700,547.61 -> £3,322,531.78 (10.2%); £3,700,547.82 -> £3,322,531.91 (10.2%); £3,700,548.05 -> £3,322,532.03 (10.2%); £3,700,548.30 -> £3,322,532.15 (10.2%); £3,700,548.57 -> £3,322,532.27 (10.2%); £3,700,548.83 -> £3,322,532.29 (10.2%); £3,700,549.09 -> £3,322,532.32 (10.2%); £3,700,549.37 -> £3,322,532.34 (10.2%); £3,700,549.63 -> £3,322,532.37 (10.2%); £3,700,549.89 -> £3,322,532.39 (10.2%); £3,700,550.15 -> £3,322,532.42 (10.2%); £3,700,550.42 -> £3,322,532.44 (10.2%); £3,700,550.68 -> £3,322,532.47 (10.2%); £3,700,550.94 -> £3,322,532.49 (10.2%); £3,700,551.20 -> £3,322,532.51 (10.2%); £3,700,551.47 -> £3,322,532.54 (10.2%); £3,700,551.74 -> £3,322,532.56 (10.2%); £3,700,552.00 -> £3,322,532.59 (10.2%); £3,700,552.27 -> £3,322,532.72 (10.2%); £3,700,552.53 -> £3,322,532.86 (10.2%); £3,700,552.80 -> £3,322,533.00 (10.2%); £3,700,553.06 -> £3,322,533.14 (10.2%); £3,700,553.32 -> £3,322,533.28 (10.2%); £3,700,553.60 -> £3,322,533.41 (10.2%); £3,700,553.79 -> £3,322,533.54 (10.2%); £3,700,554.05 -> £3,322,533.67 (10.2%); £3,700,554.30 -> £3,322,533.80 (10.2%); £3,700,554.57 -> £3,322,533.94 (10.2%); £3,700,554.84 -> £3,322,534.07 (10.2%); £3,700,555.10 -> £3,322,534.10 (10.2%); £3,700,555.36 -> £3,322,534.12 (10.2%); £3,700,555.61 -> £3,322,534.15 (10.2%); £3,700,555.84 -> £3,322,534.17 (10.2%); £3,700,556.04 -> £3,322,534.19 (10.2%); £3,700,556.21 -> £3,322,534.21 (10.2%); £3,700,556.36 -> £3,322,534.23 (10.2%); £3,700,556.52 -> £3,322,534.24 (10.2%); £3,700,556.69 -> £3,322,534.26 (10.2%); £3,700,556.85 -> £3,322,534.28 (10.2%); £3,700,557.01 -> £3,322,534.29 (10.2%); £3,700,557.17 -> £3,322,534.31 (10.2%); £3,700,557.33 -> £3,322,534.33 (10.2%); £3,700,557.49 -> £3,322,534.34 (10.2%); £3,700,557.65 -> £3,322,534.36 (10.2%); £3,700,557.81 -> £3,322,534.38 (10.2%); £3,700,557.97 -> £3,322,534.49 (10.2%); £3,700,558.13 -> £3,322,534.60 (10.2%); £3,700,558.31 -> £3,322,534.71 (10.2%); £3,700,558.51 -> £3,322,534.83 (10.2%); £3,700,558.72 -> £3,322,534.95 (10.2%); £3,700,558.94 -> £3,322,535.07 (10.2%); £3,700,559.19 -> £3,322,535.18 (10.2%); £3,700,559.47 -> £3,322,535.29 (10.2%); £3,700,559.74 -> £3,322,535.32 (10.2%); £3,700,560.00 -> £3,322,535.34 (10.2%); £3,700,560.27 -> £3,322,535.37 (10.2%); £3,700,560.53 -> £3,322,535.39 (10.2%); £3,700,560.80 -> £3,322,535.41 (10.2%); £3,700,561.06 -> £3,322,535.44 (10.2%); £3,700,561.33 -> £3,322,535.46 (10.2%); £3,700,561.60 -> £3,322,535.49 (10.2%); £3,700,561.87 -> £3,322,535.51 (10.2%); £3,700,562.13 -> £3,322,535.53 (10.2%); £3,700,562.40 -> £3,322,535.56 (10.2%); £3,700,562.67 -> £3,322,535.58 (10.2%); £3,700,562.94 -> £3,322,535.61 (10.2%); £3,700,563.20 -> £3,322,535.73 (10.2%); £3,700,563.47 -> £3,322,535.86 (10.2%); £3,700,563.73 -> £3,322,535.99 (10.2%); £3,700,564.00 -> £3,322,536.12 (10.2%); £3,700,564.20 -> £3,322,536.25 (10.2%); £3,700,564.40 -> £3,322,536.37 (10.2%); £3,700,564.67 -> £3,322,536.50 (10.2%); £3,700,564.93 -> £3,322,536.63 (10.2%); £3,700,565.19 -> £3,322,536.75 (10.2%); £3,700,565.46 -> £3,322,536.87 (10.2%); £3,700,565.74 -> £3,322,537.00 (10.2%); £3,700,566.00 -> £3,322,537.03 (10.2%); £3,700,566.27 -> £3,322,537.06 (10.2%); £3,700,566.52 -> £3,322,537.09 (10.2%); £3,700,566.74 -> £3,322,537.11 (10.2%); £3,700,566.95 -> £3,322,537.13 (10.2%); £3,700,567.10 -> £3,322,537.15 (10.2%); £3,700,567.26 -> £3,322,537.17 (10.2%); £3,700,567.42 -> £3,322,537.18 (10.2%); £3,700,567.58 -> £3,322,537.20 (10.2%); £3,700,567.74 -> £3,322,537.22 (10.2%); £3,700,567.90 -> £3,322,537.23 (10.2%); £3,700,568.07 -> £3,322,537.25 (10.2%); £3,700,568.23 -> £3,322,537.27 (10.2%); £3,700,568.39 -> £3,322,537.28 (10.2%); £3,700,568.55 -> £3,322,537.30 (10.2%); £3,700,568.71 -> £3,322,537.32 (10.2%); £3,700,568.87 -> £3,322,537.47 (10.2%); £3,700,569.03 -> £3,322,537.61 (10.2%); £3,700,569.21 -> £3,322,537.77 (10.2%); £3,700,569.41 -> £3,322,537.92 (10.2%); £3,700,569.62 -> £3,322,538.07 (10.2%); £3,700,569.86 -> £3,322,538.23 (10.2%); £3,700,570.11 -> £3,322,538.38 (10.2%); £3,700,570.38 -> £3,322,538.53 (10.2%); £3,700,570.64 -> £3,322,538.55 (10.2%); £3,700,570.91 -> £3,322,538.57 (10.2%); £3,700,571.18 -> £3,322,538.60 (10.2%); £3,700,571.44 -> £3,322,538.62 (10.2%); £3,700,571.70 -> £3,322,538.65 (10.2%); £3,700,571.97 -> £3,322,538.67 (10.2%); £3,700,572.25 -> £3,322,538.69 (10.2%); £3,700,572.52 -> £3,322,538.72 (10.2%); £3,700,572.78 -> £3,322,538.74 (10.2%); £3,700,573.05 -> £3,322,538.76 (10.2%); £3,700,573.31 -> £3,322,538.78 (10.2%); £3,700,573.58 -> £3,322,538.81 (10.2%); £3,700,573.85 -> £3,322,538.84 (10.2%); £3,700,574.12 -> £3,322,539.00 (10.2%); £3,700,574.39 -> £3,322,539.17 (10.2%); £3,700,574.67 -> £3,322,539.34 (10.2%); £3,700,574.93 -> £3,322,539.50 (10.2%); £3,700,575.13 -> £3,322,539.67 (10.2%); £3,700,575.40 -> £3,322,539.84 (10.2%); £3,700,575.68 -> £3,322,540.00 (10.2%); £3,700,575.94 -> £3,322,540.17 (10.2%); £3,700,576.22 -> £3,322,540.33 (10.2%); £3,700,576.49 -> £3,322,540.48 (10.2%); £3,700,576.75 -> £3,322,540.64 (10.2%); £3,700,577.02 -> £3,322,540.67 (10.2%); £3,700,577.29 -> £3,322,540.69 (10.2%); £3,700,577.53 -> £3,322,540.72 (10.2%); £3,700,577.75 -> £3,322,540.74 (10.2%); £3,700,577.96 -> £3,322,540.76 (10.2%); £3,700,578.13 -> £3,322,540.78 (10.2%); £3,700,578.29 -> £3,322,540.80 (10.2%); £3,700,578.45 -> £3,322,540.81 (10.2%); £3,700,578.60 -> £3,322,540.83 (10.2%); £3,700,578.76 -> £3,322,540.85 (10.2%); £3,700,578.92 -> £3,322,540.87 (10.2%); £3,700,579.08 -> £3,322,540.88 (10.2%); £3,700,579.24 -> £3,322,540.90 (10.2%); £3,700,579.41 -> £3,322,540.92 (10.2%); £3,700,579.57 -> £3,322,540.93 (10.2%); £3,700,579.73 -> £3,322,540.95 (10.2%); £3,700,579.89 -> £3,322,541.13 (10.2%); £3,700,580.04 -> £3,322,541.33 (10.2%); £3,700,580.22 -> £3,322,541.53 (10.2%); £3,700,580.42 -> £3,322,541.73 (10.2%); £3,700,580.63 -> £3,322,541.93 (10.2%); £3,700,580.86 -> £3,322,542.13 (10.2%); £3,700,581.11 -> £3,322,542.32 (10.2%); £3,700,581.39 -> £3,322,542.52 (10.2%); £3,700,581.65 -> £3,322,542.55 (10.2%); £3,700,581.91 -> £3,322,542.57 (10.2%); £3,700,582.16 -> £3,322,542.59 (10.2%); £3,700,582.42 -> £3,322,542.62 (10.2%); £3,700,582.68 -> £3,322,542.64 (10.2%); £3,700,582.95 -> £3,322,542.67 (10.2%); £3,700,583.21 -> £3,322,542.69 (10.2%); £3,700,583.49 -> £3,322,542.71 (10.2%); £3,700,583.76 -> £3,322,542.74 (10.2%); £3,700,584.02 -> £3,322,542.76 (10.2%); £3,700,584.28 -> £3,322,542.78 (10.2%); £3,700,584.55 -> £3,322,542.81 (10.2%); £3,700,584.81 -> £3,322,542.84 (10.2%); £3,700,585.08 -> £3,322,543.04 (10.2%); £3,700,585.33 -> £3,322,543.24 (10.2%); £3,700,585.53 -> £3,322,543.44 (10.2%); £3,700,585.74 -> £3,322,543.64 (10.2%); £3,700,585.93 -> £3,322,543.83 (10.2%); £3,700,586.13 -> £3,322,544.03 (10.2%); £3,700,586.34 -> £3,322,544.23 (10.2%); £3,700,586.60 -> £3,322,544.42 (10.2%); £3,700,586.86 -> £3,322,544.61 (10.2%); £3,700,587.14 -> £3,322,544.81 (10.2%); £3,700,587.40 -> £3,322,545.00 (10.2%); £3,700,587.67 -> £3,322,545.03 (10.2%); £3,700,587.93 -> £3,322,545.06 (10.2%); £3,700,588.17 -> £3,322,545.08 (10.2%); £3,700,588.39 -> £3,322,545.11 (10.2%); £3,700,588.59 -> £3,322,545.13 (10.2%); £3,700,588.74 -> £3,322,545.15 (10.2%); £3,700,588.87 -> £3,322,545.17 (10.2%); £3,700,589.02 -> £3,322,545.18 (10.2%); £3,700,589.16 -> £3,322,545.20 (10.2%); £3,700,589.30 -> £3,322,545.22 (10.2%); £3,700,589.44 -> £3,322,545.23 (10.2%); £3,700,589.58 -> £3,322,545.25 (10.2%); £3,700,589.72 -> £3,322,545.27 (10.2%); £3,700,589.86 -> £3,322,545.28 (10.2%); £3,700,590.00 -> £3,322,545.30 (10.2%); £3,700,590.14 -> £3,322,545.32 (10.2%); £3,700,590.28 -> £3,322,545.52 (10.2%); £3,700,590.42 -> £3,322,545.72 (10.2%); £3,700,590.58 -> £3,322,545.93 (10.2%); £3,700,590.75 -> £3,322,546.13 (10.2%); £3,700,590.94 -> £3,322,546.34 (10.2%); £3,700,591.14 -> £3,322,546.55 (10.2%); £3,700,591.37 -> £3,322,546.76 (10.2%); £3,700,591.61 -> £3,322,546.96 (10.2%); £3,700,591.84 -> £3,322,546.99 (10.2%); £3,700,592.07 -> £3,322,547.02 (10.2%); £3,700,592.31 -> £3,322,547.04 (10.2%); £3,700,592.54 -> £3,322,547.07 (10.2%); £3,700,592.77 -> £3,322,547.10 (10.2%); £3,700,593.01 -> £3,322,547.12 (10.2%); £3,700,593.24 -> £3,322,547.15 (10.2%); £3,700,593.47 -> £3,322,547.18 (10.2%); £3,700,593.71 -> £3,322,547.20 (10.2%); £3,700,593.94 -> £3,322,547.23 (10.2%); £3,700,594.18 -> £3,322,547.25 (10.2%); £3,700,594.43 -> £3,322,547.28 (10.2%); £3,700,594.67 -> £3,322,547.31 (10.2%); £3,700,594.84 -> £3,322,547.51 (10.2%); £3,700,595.01 -> £3,322,547.72 (10.2%); £3,700,595.19 -> £3,322,547.92 (10.2%); £3,700,595.36 -> £3,322,548.13 (10.2%); £3,700,595.54 -> £3,322,548.34 (10.2%); £3,700,595.71 -> £3,322,548.55 (10.2%); £3,700,595.89 -> £3,322,548.76 (10.2%); £3,700,596.13 -> £3,322,548.96 (10.2%); £3,700,596.37 -> £3,322,549.16 (10.2%); £3,700,596.61 -> £3,322,549.37 (10.2%); £3,700,596.84 -> £3,322,549.57 (10.2%); £3,700,597.08 -> £3,322,549.60 (10.2%); £3,700,597.31 -> £3,322,549.62 (10.2%); £3,700,597.53 -> £3,322,549.65 (10.2%); £3,700,597.72 -> £3,322,549.67 (10.2%); £3,700,597.91 -> £3,322,549.69 (10.2%); £3,700,598.05 -> £3,322,549.71 (10.2%); £3,700,598.20 -> £3,322,549.73 (10.2%); £3,700,598.34 -> £3,322,549.75 (10.2%); £3,700,598.48 -> £3,322,549.77 (10.2%); £3,700,598.61 -> £3,322,549.79 (10.2%); £3,700,598.75 -> £3,322,549.80 (10.2%); £3,700,598.89 -> £3,322,549.82 (10.2%); £3,700,599.03 -> £3,322,549.84 (10.2%); £3,700,599.17 -> £3,322,549.85 (10.2%); £3,700,599.31 -> £3,322,549.87 (10.2%); £3,700,599.45 -> £3,322,549.89 (10.2%); £3,700,599.59 -> £3,322,550.07 (10.2%); £3,700,599.73 -> £3,322,550.25 (10.2%); £3,700,599.89 -> £3,322,550.44 (10.2%); £3,700,600.06 -> £3,322,550.63 (10.2%); £3,700,600.25 -> £3,322,550.82 (10.2%); £3,700,600.45 -> £3,322,551.01 (10.2%); £3,700,600.66 -> £3,322,551.21 (10.2%); £3,700,600.90 -> £3,322,551.41 (10.2%); £3,700,601.14 -> £3,322,551.44 (10.2%); £3,700,601.38 -> £3,322,551.47 (10.2%); £3,700,601.62 -> £3,322,551.50 (10.2%); £3,700,601.85 -> £3,322,551.53 (10.2%); £3,700,602.08 -> £3,322,551.56 (10.2%); £3,700,602.31 -> £3,322,551.60 (10.2%); £3,700,602.54 -> £3,322,551.63 (10.2%); £3,700,602.79 -> £3,322,551.66 (10.2%); £3,700,603.02 -> £3,322,551.69 (10.2%); £3,700,603.25 -> £3,322,551.71 (10.2%); £3,700,603.48 -> £3,322,551.74 (10.2%); £3,700,603.72 -> £3,322,551.77 (10.2%); £3,700,603.95 -> £3,322,551.80 (10.2%); £3,700,604.13 -> £3,322,551.99 (10.2%); £3,700,604.30 -> £3,322,552.19 (10.2%); £3,700,604.48 -> £3,322,552.38 (10.2%); £3,700,604.66 -> £3,322,552.58 (10.2%); £3,700,604.89 -> £3,322,552.78 (10.2%); £3,700,605.12 -> £3,322,552.98 (10.2%); £3,700,605.30 -> £3,322,553.18 (10.2%); £3,700,605.54 -> £3,322,553.38 (10.2%); £3,700,605.77 -> £3,322,553.57 (10.2%); £3,700,606.00 -> £3,322,553.77 (10.2%); £3,700,606.23 -> £3,322,553.96 (10.2%); £3,700,606.46 -> £3,322,553.99 (10.2%); £3,700,606.70 -> £3,322,554.02 (10.2%); £3,700,606.91 -> £3,322,554.05 (10.2%); £3,700,607.11 -> £3,322,554.07 (10.2%); £3,700,607.29 -> £3,322,554.09 (10.2%); £3,700,607.45 -> £3,322,554.11 (10.2%); £3,700,607.61 -> £3,322,554.13 (10.2%); £3,700,607.77 -> £3,322,554.14 (10.2%); £3,700,607.92 -> £3,322,554.16 (10.2%); £3,700,608.09 -> £3,322,554.18 (10.2%); £3,700,608.25 -> £3,322,554.20 (10.2%); £3,700,608.41 -> £3,322,554.21 (10.2%); £3,700,608.57 -> £3,322,554.23 (10.2%); £3,700,608.73 -> £3,322,554.24 (10.2%); £3,700,608.89 -> £3,322,554.26 (10.2%); £3,700,609.05 -> £3,322,554.28 (10.2%); £3,700,609.21 -> £3,322,554.45 (10.2%); £3,700,609.37 -> £3,322,554.62 (10.2%); £3,700,609.54 -> £3,322,554.79 (10.2%); £3,700,609.74 -> £3,322,554.96 (10.2%); £3,700,609.96 -> £3,322,555.14 (10.2%); £3,700,610.18 -> £3,322,555.32 (10.2%); £3,700,610.42 -> £3,322,555.49 (10.2%); £3,700,610.69 -> £3,322,555.66 (10.2%); £3,700,610.95 -> £3,322,555.69 (10.2%); £3,700,611.22 -> £3,322,555.71 (10.2%); £3,700,611.48 -> £3,322,555.73 (10.2%); £3,700,611.75 -> £3,322,555.76 (10.2%); £3,700,612.02 -> £3,322,555.78 (10.2%); £3,700,612.27 -> £3,322,555.81 (10.2%); £3,700,612.53 -> £3,322,555.83 (10.2%); £3,700,612.80 -> £3,322,555.85 (10.2%); £3,700,613.07 -> £3,322,555.88 (10.2%); £3,700,613.33 -> £3,322,555.90 (10.2%); £3,700,613.60 -> £3,322,555.93 (10.2%); £3,700,613.86 -> £3,322,555.95 (10.2%); £3,700,614.12 -> £3,322,555.98 (10.2%); £3,700,614.38 -> £3,322,556.16 (10.2%); £3,700,614.66 -> £3,322,556.35 (10.2%); £3,700,614.92 -> £3,322,556.53 (10.2%); £3,700,615.18 -> £3,322,556.72 (10.2%); £3,700,615.44 -> £3,322,556.90 (10.2%); £3,700,615.70 -> £3,322,557.08 (10.2%); £3,700,615.90 -> £3,322,557.26 (10.2%); £3,700,616.16 -> £3,322,557.44 (10.2%); £3,700,616.42 -> £3,322,557.62 (10.2%); £3,700,616.68 -> £3,322,557.80 (10.2%); £3,700,616.93 -> £3,322,557.98 (10.2%); £3,700,617.19 -> £3,322,558.01 (10.2%); £3,700,617.45 -> £3,322,558.03 (10.2%); £3,700,617.70 -> £3,322,558.06 (10.2%); £3,700,617.92 -> £3,322,558.08 (10.2%); £3,700,618.13 -> £3,322,558.10 (10.2%); £3,700,618.29 -> £3,322,558.12 (10.2%); £3,700,618.45 -> £3,322,558.14 (10.2%); £3,700,618.60 -> £3,322,558.16 (10.2%); £3,700,618.76 -> £3,322,558.17 (10.2%); £3,700,618.92 -> £3,322,558.19 (10.2%); £3,700,619.07 -> £3,322,558.21 (10.2%); £3,700,619.23 -> £3,322,558.22 (10.2%); £3,700,619.39 -> £3,322,558.24 (10.2%); £3,700,619.55 -> £3,322,558.26 (10.2%); £3,700,619.70 -> £3,322,558.27 (10.2%); £3,700,619.85 -> £3,322,558.29 (10.2%); £3,700,620.01 -> £3,322,558.48 (10.2%); £3,700,620.17 -> £3,322,558.68 (10.2%); £3,700,620.35 -> £3,322,558.88 (10.2%); £3,700,620.53 -> £3,322,559.08 (10.2%); £3,700,620.75 -> £3,322,559.28 (10.2%); £3,700,620.98 -> £3,322,559.48 (10.2%); £3,700,621.23 -> £3,322,559.67 (10.2%); £3,700,621.49 -> £3,322,559.87 (10.2%); £3,700,621.74 -> £3,322,559.89 (10.2%); £3,700,622.00 -> £3,322,559.92 (10.2%); £3,700,622.25 -> £3,322,559.94 (10.2%); £3,700,622.51 -> £3,322,559.97 (10.2%); £3,700,622.77 -> £3,322,559.99 (10.2%); £3,700,623.03 -> £3,322,560.02 (10.2%); £3,700,623.29 -> £3,322,560.04 (10.2%); £3,700,623.56 -> £3,322,560.06 (10.2%); £3,700,623.81 -> £3,322,560.09 (10.2%); £3,700,624.08 -> £3,322,560.11 (10.2%); £3,700,624.33 -> £3,322,560.13 (10.2%); £3,700,624.59 -> £3,322,560.16 (10.2%); £3,700,624.86 -> £3,322,560.19 (10.2%); £3,700,625.13 -> £3,322,560.39 (10.2%); £3,700,625.39 -> £3,322,560.59 (10.2%); £3,700,625.57 -> £3,322,560.79 (10.2%); £3,700,625.78 -> £3,322,560.99 (10.2%); £3,700,625.98 -> £3,322,561.19 (10.2%); £3,700,626.18 -> £3,322,561.39 (10.2%); £3,700,626.43 -> £3,322,561.59 (10.2%); £3,700,626.69 -> £3,322,561.79 (10.2%); £3,700,626.96 -> £3,322,561.99 (10.2%); £3,700,627.23 -> £3,322,562.19 (10.2%); £3,700,627.48 -> £3,322,562.39 (10.2%); £3,700,627.74 -> £3,322,562.42 (10.2%); £3,700,628.01 -> £3,322,562.44 (10.2%); £3,700,628.25 -> £3,322,562.47 (10.2%); £3,700,628.48 -> £3,322,562.49 (10.2%); £3,700,628.68 -> £3,322,562.51 (10.2%); £3,700,628.84 -> £3,322,562.53 (10.2%); £3,700,629.00 -> £3,322,562.55 (10.2%); £3,700,629.15 -> £3,322,562.56 (10.2%); £3,700,629.31 -> £3,322,562.58 (10.2%); £3,700,629.46 -> £3,322,562.60 (10.2%); £3,700,629.62 -> £3,322,562.61 (10.2%); £3,700,629.78 -> £3,322,562.63 (10.2%); £3,700,629.94 -> £3,322,562.65 (10.2%); £3,700,630.10 -> £3,322,562.66 (10.2%); £3,700,630.25 -> £3,322,562.68 (10.2%); £3,700,630.41 -> £3,322,562.70 (10.2%); £3,700,630.57 -> £3,322,562.85 (10.2%); £3,700,630.72 -> £3,322,563.00 (10.2%); £3,700,630.90 -> £3,322,563.15 (10.2%); £3,700,631.10 -> £3,322,563.31 (10.2%); £3,700,631.30 -> £3,322,563.47 (10.2%); £3,700,631.53 -> £3,322,563.62 (10.2%); £3,700,631.77 -> £3,322,563.78 (10.2%); £3,700,632.02 -> £3,322,563.93 (10.2%); £3,700,632.28 -> £3,322,563.96 (10.2%); £3,700,632.54 -> £3,322,563.98 (10.2%); £3,700,632.79 -> £3,322,564.01 (10.2%); £3,700,633.06 -> £3,322,564.03 (10.2%); £3,700,633.32 -> £3,322,564.06 (10.2%); £3,700,633.58 -> £3,322,564.08 (10.2%); £3,700,633.85 -> £3,322,564.11 (10.2%); £3,700,634.11 -> £3,322,564.13 (10.2%); £3,700,634.37 -> £3,322,564.15 (10.2%); £3,700,634.64 -> £3,322,564.18 (10.2%); £3,700,634.90 -> £3,322,564.20 (10.2%); £3,700,635.16 -> £3,322,564.22 (10.2%); £3,700,635.42 -> £3,322,564.25 (10.2%); £3,700,635.62 -> £3,322,564.42 (10.2%); £3,700,635.88 -> £3,322,564.58 (10.2%); £3,700,636.08 -> £3,322,564.75 (10.2%); £3,700,636.28 -> £3,322,564.92 (10.2%); £3,700,636.55 -> £3,322,565.08 (10.2%); £3,700,636.81 -> £3,322,565.25 (10.2%); £3,700,637.00 -> £3,322,565.41 (10.2%); £3,700,637.27 -> £3,322,565.57 (10.2%); £3,700,637.52 -> £3,322,565.73 (10.2%); £3,700,637.79 -> £3,322,565.89 (10.2%); £3,700,638.05 -> £3,322,566.05 (10.2%); £3,700,638.32 -> £3,322,566.08 (10.2%); £3,700,638.59 -> £3,322,566.11 (10.2%); £3,700,638.83 -> £3,322,566.13 (10.2%); £3,700,639.06 -> £3,322,566.16 (10.2%); £3,700,639.26 -> £3,322,566.18 (10.2%); £3,700,639.42 -> £3,322,566.19 (10.2%); £3,700,639.57 -> £3,322,566.21 (10.2%); £3,700,639.72 -> £3,322,566.23 (10.2%); £3,700,639.88 -> £3,322,566.25 (10.2%); £3,700,640.03 -> £3,322,566.26 (10.2%); £3,700,640.19 -> £3,322,566.28 (10.2%); £3,700,640.34 -> £3,322,566.30 (10.2%); £3,700,640.50 -> £3,322,566.31 (10.2%); £3,700,640.65 -> £3,322,566.33 (10.2%); £3,700,640.81 -> £3,322,566.35 (10.2%); £3,700,640.96 -> £3,322,566.36 (10.2%); £3,700,641.12 -> £3,322,566.50 (10.2%); £3,700,641.27 -> £3,322,566.63 (10.2%); £3,700,641.44 -> £3,322,566.77 (10.2%); £3,700,641.63 -> £3,322,566.90 (10.2%); £3,700,641.83 -> £3,322,567.05 (10.2%); £3,700,642.06 -> £3,322,567.18 (10.2%); £3,700,642.30 -> £3,322,567.31 (10.2%); £3,700,642.56 -> £3,322,567.44 (10.2%); £3,700,642.82 -> £3,322,567.47 (10.2%); £3,700,643.08 -> £3,322,567.49 (10.2%); £3,700,643.34 -> £3,322,567.51 (10.2%); £3,700,643.59 -> £3,322,567.54 (10.2%); £3,700,643.85 -> £3,322,567.56 (10.2%); £3,700,644.10 -> £3,322,567.59 (10.2%); £3,700,644.36 -> £3,322,567.61 (10.2%); £3,700,644.62 -> £3,322,567.63 (10.2%); £3,700,644.88 -> £3,322,567.66 (10.2%); £3,700,645.14 -> £3,322,567.68 (10.2%); £3,700,645.39 -> £3,322,567.70 (10.2%); £3,700,645.63 -> £3,322,567.73 (10.2%); £3,700,645.90 -> £3,322,567.76 (10.2%); £3,700,646.15 -> £3,322,567.90 (10.2%); £3,700,646.41 -> £3,322,568.05 (10.2%); £3,700,646.67 -> £3,322,568.20 (10.2%); £3,700,646.86 -> £3,322,568.34 (10.2%); £3,700,647.05 -> £3,322,568.49 (10.2%); £3,700,647.31 -> £3,322,568.63 (10.2%); £3,700,647.51 -> £3,322,568.77 (10.2%); £3,700,647.76 -> £3,322,568.91 (10.2%); £3,700,648.01 -> £3,322,569.05 (10.2%); £3,700,648.28 -> £3,322,569.19 (10.2%); £3,700,648.53 -> £3,322,569.33 (10.2%); £3,700,648.80 -> £3,322,569.36 (10.2%); £3,700,649.06 -> £3,322,569.38 (10.2%); £3,700,649.30 -> £3,322,569.41 (10.2%); £3,700,649.52 -> £3,322,569.43 (10.2%); £3,700,649.72 -> £3,322,569.45 (10.2%); £3,700,649.88 -> £3,322,569.47 (10.2%); £3,700,650.03 -> £3,322,569.49 (10.2%); £3,700,650.19 -> £3,322,569.50 (10.2%); £3,700,650.34 -> £3,322,569.52 (10.2%); £3,700,650.50 -> £3,322,569.54 (10.2%); £3,700,650.66 -> £3,322,569.56 (10.2%); £3,700,650.82 -> £3,322,569.57 (10.2%); £3,700,650.97 -> £3,322,569.59 (10.2%); £3,700,651.13 -> £3,322,569.60 (10.2%); £3,700,651.28 -> £3,322,569.62 (10.2%); £3,700,651.43 -> £3,322,569.64 (10.2%); £3,700,651.59 -> £3,322,569.83 (10.2%); £3,700,651.74 -> £3,322,570.02 (10.2%); £3,700,651.92 -> £3,322,570.21 (10.2%); £3,700,652.10 -> £3,322,570.41 (10.2%); £3,700,652.31 -> £3,322,570.61 (10.2%); £3,700,652.53 -> £3,322,570.81 (10.2%); £3,700,652.76 -> £3,322,571.00 (10.2%); £3,700,653.02 -> £3,322,571.20 (10.2%); £3,700,653.28 -> £3,322,571.22 (10.2%); £3,700,653.54 -> £3,322,571.25 (10.2%); £3,700,653.80 -> £3,322,571.27 (10.2%); £3,700,654.06 -> £3,322,571.30 (10.2%); £3,700,654.33 -> £3,322,571.32 (10.2%); £3,700,654.59 -> £3,322,571.34 (10.2%); £3,700,654.85 -> £3,322,571.37 (10.2%); £3,700,655.11 -> £3,322,571.39 (10.2%); £3,700,655.38 -> £3,322,571.41 (10.2%); £3,700,655.64 -> £3,322,571.44 (10.2%); £3,700,655.90 -> £3,322,571.46 (10.2%); £3,700,656.16 -> £3,322,571.49 (10.2%); £3,700,656.42 -> £3,322,571.51 (10.2%); £3,700,656.67 -> £3,322,571.71 (10.2%); £3,700,656.93 -> £3,322,571.91 (10.2%); £3,700,657.19 -> £3,322,572.12 (10.2%); £3,700,657.46 -> £3,322,572.31 (10.2%); £3,700,657.73 -> £3,322,572.51 (10.2%); £3,700,657.99 -> £3,322,572.72 (10.2%); £3,700,658.26 -> £3,322,572.92 (10.2%); £3,700,658.51 -> £3,322,573.12 (10.2%); £3,700,658.78 -> £3,322,573.32 (10.2%); £3,700,659.04 -> £3,322,573.52 (10.2%); £3,700,659.30 -> £3,322,573.72 (10.2%); £3,700,659.57 -> £3,322,573.75 (10.2%); £3,700,659.83 -> £3,322,573.77 (10.2%); £3,700,660.07 -> £3,322,573.80 (10.2%); £3,700,660.29 -> £3,322,573.82 (10.2%); £3,700,660.49 -> £3,322,573.84 (10.2%); £3,700,660.63 -> £3,322,573.86 (10.2%); £3,700,660.76 -> £3,322,573.88 (10.2%); £3,700,660.89 -> £3,322,573.90 (10.2%); £3,700,661.03 -> £3,322,573.91 (10.2%); £3,700,661.17 -> £3,322,573.93 (10.2%); £3,700,661.30 -> £3,322,573.95 (10.2%); £3,700,661.44 -> £3,322,573.96 (10.2%); £3,700,661.57 -> £3,322,573.98 (10.2%); £3,700,661.71 -> £3,322,574.00 (10.2%); £3,700,661.85 -> £3,322,574.01 (10.2%); £3,700,661.99 -> £3,322,574.03 (10.2%); £3,700,662.13 -> £3,322,574.23 (10.2%); £3,700,662.26 -> £3,322,574.43 (10.2%); £3,700,662.42 -> £3,322,574.63 (10.2%); £3,700,662.58 -> £3,322,574.84 (10.2%); £3,700,662.76 -> £3,322,575.04 (10.2%); £3,700,662.96 -> £3,322,575.24 (10.2%); £3,700,663.17 -> £3,322,575.44 (10.2%); £3,700,663.40 -> £3,322,575.64 (10.2%); £3,700,663.63 -> £3,322,575.67 (10.2%); £3,700,663.85 -> £3,322,575.70 (10.2%); £3,700,664.07 -> £3,322,575.72 (10.2%); £3,700,664.29 -> £3,322,575.75 (10.2%); £3,700,664.52 -> £3,322,575.78 (10.2%); £3,700,664.74 -> £3,322,575.80 (10.2%); £3,700,664.97 -> £3,322,575.83 (10.2%); £3,700,665.20 -> £3,322,575.86 (10.2%); £3,700,665.44 -> £3,322,575.88 (10.2%); £3,700,665.67 -> £3,322,575.91 (10.2%); £3,700,665.89 -> £3,322,575.93 (10.2%); £3,700,666.12 -> £3,322,575.96 (10.2%); £3,700,666.35 -> £3,322,575.99 (10.2%); £3,700,666.57 -> £3,322,576.19 (10.2%); £3,700,666.80 -> £3,322,576.40 (10.2%); £3,700,667.02 -> £3,322,576.61 (10.2%); £3,700,667.25 -> £3,322,576.82 (10.2%); £3,700,667.47 -> £3,322,577.02 (10.2%); £3,700,667.70 -> £3,322,577.24 (10.2%); £3,700,667.93 -> £3,322,577.45 (10.2%); £3,700,668.16 -> £3,322,577.66 (10.2%); £3,700,668.39 -> £3,322,577.86 (10.2%); £3,700,668.61 -> £3,322,578.07 (10.2%); £3,700,668.84 -> £3,322,578.27 (10.2%); £3,700,669.07 -> £3,322,578.30 (10.2%); £3,700,669.28 -> £3,322,578.33 (10.2%); £3,700,669.50 -> £3,322,578.35 (10.2%); £3,700,669.69 -> £3,322,578.38 (10.2%); £3,700,669.87 -> £3,322,578.40 (10.2%); £3,700,670.00 -> £3,322,578.42 (10.2%); £3,700,670.14 -> £3,322,578.44 (10.2%); £3,700,670.27 -> £3,322,578.46 (10.2%); £3,700,670.40 -> £3,322,578.47 (10.2%); £3,700,670.54 -> £3,322,578.49 (10.2%); £3,700,670.68 -> £3,322,578.51 (10.2%); £3,700,670.81 -> £3,322,578.53 (10.2%); £3,700,670.94 -> £3,322,578.54 (10.2%); £3,700,671.08 -> £3,322,578.56 (10.2%); £3,700,671.22 -> £3,322,578.58 (10.2%); £3,700,671.36 -> £3,322,578.59 (10.2%); £3,700,671.49 -> £3,322,578.78 (10.2%); £3,700,671.63 -> £3,322,578.96 (10.2%); £3,700,671.78 -> £3,322,579.15 (10.2%); £3,700,671.94 -> £3,322,579.35 (10.2%); £3,700,672.12 -> £3,322,579.54 (10.2%); £3,700,672.32 -> £3,322,579.74 (10.2%); £3,700,672.53 -> £3,322,579.95 (10.2%); £3,700,672.75 -> £3,322,580.15 (10.2%); £3,700,672.98 -> £3,322,580.18 (10.2%); £3,700,673.21 -> £3,322,580.21 (10.2%); £3,700,673.44 -> £3,322,580.24 (10.2%); £3,700,673.66 -> £3,322,580.27 (10.2%); £3,700,673.87 -> £3,322,580.31 (10.2%); £3,700,674.10 -> £3,322,580.34 (10.2%); £3,700,674.33 -> £3,322,580.37 (10.2%); £3,700,674.56 -> £3,322,580.40 (10.2%); £3,700,674.78 -> £3,322,580.43 (10.2%); £3,700,675.01 -> £3,322,580.46 (10.2%); £3,700,675.23 -> £3,322,580.48 (10.2%); £3,700,675.46 -> £3,322,580.51 (10.2%); £3,700,675.70 -> £3,322,580.54 (10.2%); £3,700,675.93 -> £3,322,580.74 (10.2%); £3,700,676.15 -> £3,322,580.95 (10.2%); £3,700,676.38 -> £3,322,581.15 (10.2%); £3,700,676.61 -> £3,322,581.35 (10.2%); £3,700,676.83 -> £3,322,581.55 (10.2%); £3,700,677.05 -> £3,322,581.75 (10.2%); £3,700,677.28 -> £3,322,581.96 (10.2%); £3,700,677.49 -> £3,322,582.16 (10.2%); £3,700,677.72 -> £3,322,582.37 (10.2%); £3,700,677.95 -> £3,322,582.56 (10.2%); £3,700,678.19 -> £3,322,582.76 (10.2%); £3,700,678.41 -> £3,322,582.79 (10.2%); £3,700,678.64 -> £3,322,582.82 (10.2%); £3,700,678.85 -> £3,322,582.84 (10.2%); £3,700,679.04 -> £3,322,582.87 (10.2%); £3,700,679.22 -> £3,322,582.89 (10.2%); £3,700,679.37 -> £3,322,582.90 (10.2%); £3,700,679.53 -> £3,322,582.92 (10.2%); £3,700,679.68 -> £3,322,582.94 (10.2%); £3,700,679.84 -> £3,322,582.96 (10.2%); £3,700,679.99 -> £3,322,582.97 (10.2%); £3,700,680.15 -> £3,322,582.99 (10.2%); £3,700,680.30 -> £3,322,583.01 (10.2%); £3,700,680.46 -> £3,322,583.02 (10.2%); £3,700,680.61 -> £3,322,583.04 (10.2%); £3,700,680.76 -> £3,322,583.06 (10.2%); £3,700,680.92 -> £3,322,583.07 (10.2%); £3,700,681.08 -> £3,322,583.24 (10.2%); £3,700,681.23 -> £3,322,583.41 (10.2%); £3,700,681.40 -> £3,322,583.59 (10.2%); £3,700,681.59 -> £3,322,583.77 (10.2%); £3,700,681.79 -> £3,322,583.95 (10.2%); £3,700,682.02 -> £3,322,584.13 (10.2%); £3,700,682.26 -> £3,322,584.31 (10.2%); £3,700,682.52 -> £3,322,584.49 (10.2%); £3,700,682.78 -> £3,322,584.51 (10.2%); £3,700,683.05 -> £3,322,584.54 (10.2%); £3,700,683.31 -> £3,322,584.56 (10.2%); £3,700,683.56 -> £3,322,584.58 (10.2%); £3,700,683.82 -> £3,322,584.61 (10.2%); £3,700,684.08 -> £3,322,584.63 (10.2%); £3,700,684.34 -> £3,322,584.66 (10.2%); £3,700,684.60 -> £3,322,584.68 (10.2%); £3,700,684.86 -> £3,322,584.70 (10.2%); £3,700,685.12 -> £3,322,584.73 (10.2%); £3,700,685.37 -> £3,322,584.75 (10.2%); £3,700,685.64 -> £3,322,584.78 (10.2%); £3,700,685.90 -> £3,322,584.81 (10.2%); £3,700,686.14 -> £3,322,584.99 (10.2%); £3,700,686.40 -> £3,322,585.17 (10.2%); £3,700,686.65 -> £3,322,585.36 (10.2%); £3,700,686.90 -> £3,322,585.54 (10.2%); £3,700,687.16 -> £3,322,585.73 (10.2%); £3,700,687.41 -> £3,322,585.91 (10.2%); £3,700,687.67 -> £3,322,586.10 (10.2%); £3,700,687.93 -> £3,322,586.28 (10.2%); £3,700,688.19 -> £3,322,586.47 (10.2%); £3,700,688.44 -> £3,322,586.65 (10.2%); £3,700,688.71 -> £3,322,586.83 (10.2%); £3,700,688.96 -> £3,322,586.86 (10.2%); £3,700,689.22 -> £3,322,586.89 (10.2%); £3,700,689.46 -> £3,322,586.91 (10.2%); £3,700,689.68 -> £3,322,586.93 (10.2%); £3,700,689.88 -> £3,322,586.95 (10.2%); £3,700,690.03 -> £3,322,586.97 (10.2%); £3,700,690.18 -> £3,322,586.99 (10.2%); £3,700,690.34 -> £3,322,587.01 (10.2%); £3,700,690.50 -> £3,322,587.02 (10.2%); £3,700,690.65 -> £3,322,587.04 (10.2%); £3,700,690.81 -> £3,322,587.06 (10.2%); £3,700,690.96 -> £3,322,587.07 (10.2%); £3,700,691.10 -> £3,322,587.09 (10.2%); £3,700,691.25 -> £3,322,587.11 (10.2%); £3,700,691.41 -> £3,322,587.12 (10.2%); £3,700,691.56 -> £3,322,587.14 (10.2%); £3,700,691.71 -> £3,322,587.28 (10.2%); £3,700,691.87 -> £3,322,587.43 (10.2%); £3,700,692.04 -> £3,322,587.57 (10.2%); £3,700,692.23 -> £3,322,587.73 (10.2%); £3,700,692.43 -> £3,322,587.88 (10.2%); £3,700,692.66 -> £3,322,588.03 (10.2%); £3,700,692.89 -> £3,322,588.18 (10.2%); £3,700,693.15 -> £3,322,588.32 (10.2%); £3,700,693.40 -> £3,322,588.35 (10.2%); £3,700,693.66 -> £3,322,588.37 (10.2%); £3,700,693.92 -> £3,322,588.40 (10.2%); £3,700,694.18 -> £3,322,588.42 (10.2%); £3,700,694.43 -> £3,322,588.44 (10.2%); £3,700,694.68 -> £3,322,588.47 (10.2%); £3,700,694.95 -> £3,322,588.49 (10.2%); £3,700,695.20 -> £3,322,588.52 (10.2%); £3,700,695.45 -> £3,322,588.54 (10.2%); £3,700,695.71 -> £3,322,588.56 (10.2%); £3,700,695.96 -> £3,322,588.59 (10.2%); £3,700,696.23 -> £3,322,588.61 (10.2%); £3,700,696.48 -> £3,322,588.64 (10.2%); £3,700,696.75 -> £3,322,588.80 (10.2%); £3,700,697.01 -> £3,322,588.96 (10.2%); £3,700,697.26 -> £3,322,589.12 (10.2%); £3,700,697.51 -> £3,322,589.27 (10.2%); £3,700,697.77 -> £3,322,589.43 (10.2%); £3,700,698.03 -> £3,322,589.59 (10.2%); £3,700,698.29 -> £3,322,589.74 (10.2%); £3,700,698.54 -> £3,322,589.90 (10.2%); £3,700,698.80 -> £3,322,590.06 (10.2%); £3,700,699.05 -> £3,322,590.21 (10.2%); £3,700,699.31 -> £3,322,590.36 (10.2%); £3,700,699.57 -> £3,322,590.39 (10.2%); £3,700,699.83 -> £3,322,590.42 (10.2%); £3,700,700.07 -> £3,322,590.44 (10.2%); £3,700,700.28 -> £3,322,590.47 (10.2%); £3,700,700.48 -> £3,322,590.49 (10.2%); £3,700,700.63 -> £3,322,590.51 (10.2%); £3,700,700.78 -> £3,322,590.52 (10.2%); £3,700,700.93 -> £3,322,590.54 (10.2%); £3,700,701.07 -> £3,322,590.56 (10.2%); £3,700,701.22 -> £3,322,590.57 (10.2%); £3,700,701.38 -> £3,322,590.59 (10.2%); £3,700,701.53 -> £3,322,590.61 (10.2%); £3,700,701.69 -> £3,322,590.62 (10.2%); £3,700,701.83 -> £3,322,590.64 (10.2%); £3,700,701.99 -> £3,322,590.66 (10.2%); £3,700,702.14 -> £3,322,590.67 (10.2%); £3,700,702.29 -> £3,322,590.84 (10.2%); £3,700,702.45 -> £3,322,591.01 (10.2%); £3,700,702.62 -> £3,322,591.18 (10.2%); £3,700,702.81 -> £3,322,591.35 (10.2%); £3,700,703.02 -> £3,322,591.53 (10.2%); £3,700,703.23 -> £3,322,591.70 (10.2%); £3,700,703.47 -> £3,322,591.88 (10.2%); £3,700,703.73 -> £3,322,592.06 (10.2%); £3,700,703.98 -> £3,322,592.08 (10.2%); £3,700,704.23 -> £3,322,592.11 (10.2%); £3,700,704.48 -> £3,322,592.13 (10.2%); £3,700,704.74 -> £3,322,592.16 (10.2%); £3,700,705.01 -> £3,322,592.18 (10.2%); £3,700,705.27 -> £3,322,592.20 (10.2%); £3,700,705.52 -> £3,322,592.23 (10.2%); £3,700,705.79 -> £3,322,592.25 (10.2%); £3,700,706.05 -> £3,322,592.27 (10.2%); £3,700,706.29 -> £3,322,592.30 (10.2%); £3,700,706.55 -> £3,322,592.32 (10.2%); £3,700,706.80 -> £3,322,592.35 (10.2%); £3,700,707.06 -> £3,322,592.38 (10.2%); £3,700,707.32 -> £3,322,592.56 (10.2%); £3,700,707.58 -> £3,322,592.74 (10.2%); £3,700,707.84 -> £3,322,592.92 (10.2%); £3,700,708.10 -> £3,322,593.10 (10.2%); £3,700,708.35 -> £3,322,593.28 (10.2%); £3,700,708.61 -> £3,322,593.46 (10.2%); £3,700,708.86 -> £3,322,593.65 (10.2%); £3,700,709.12 -> £3,322,593.82 (10.2%); £3,700,709.37 -> £3,322,594.00 (10.2%); £3,700,709.63 -> £3,322,594.19 (10.2%); £3,700,709.89 -> £3,322,594.37 (10.2%); £3,700,710.14 -> £3,322,594.40 (10.2%); £3,700,710.39 -> £3,322,594.43 (10.2%); £3,700,710.63 -> £3,322,594.45 (10.2%); £3,700,710.85 -> £3,322,594.47 (10.2%); £3,700,711.04 -> £3,322,594.49 (10.2%); £3,700,711.20 -> £3,322,594.51 (10.2%); £3,700,711.35 -> £3,322,594.53 (10.2%); £3,700,711.51 -> £3,322,594.55 (10.2%); £3,700,711.65 -> £3,322,594.56 (10.2%); £3,700,711.80 -> £3,322,594.58 (10.2%); £3,700,711.96 -> £3,322,594.60 (10.2%); £3,700,712.11 -> £3,322,594.61 (10.2%); £3,700,712.26 -> £3,322,594.63 (10.2%); £3,700,712.42 -> £3,322,594.65 (10.2%); £3,700,712.57 -> £3,322,594.66 (10.2%); £3,700,712.72 -> £3,322,594.68 (10.2%); £3,700,712.88 -> £3,322,594.83 (10.2%); £3,700,713.03 -> £3,322,594.98 (10.2%); £3,700,713.19 -> £3,322,595.14 (10.2%); £3,700,713.38 -> £3,322,595.30 (10.2%); £3,700,713.58 -> £3,322,595.46 (10.2%); £3,700,713.79 -> £3,322,595.62 (10.2%); £3,700,714.04 -> £3,322,595.77 (10.2%); £3,700,714.30 -> £3,322,595.93 (10.2%); £3,700,714.56 -> £3,322,595.95 (10.2%); £3,700,714.82 -> £3,322,595.98 (10.2%); £3,700,715.07 -> £3,322,596.00 (10.2%); £3,700,715.32 -> £3,322,596.02 (10.2%); £3,700,715.57 -> £3,322,596.05 (10.2%); £3,700,715.82 -> £3,322,596.07 (10.2%); £3,700,716.08 -> £3,322,596.10 (10.2%); £3,700,716.33 -> £3,322,596.12 (10.2%); £3,700,716.59 -> £3,322,596.14 (10.2%); £3,700,716.84 -> £3,322,596.16 (10.2%); £3,700,717.10 -> £3,322,596.19 (10.2%); £3,700,717.36 -> £3,322,596.21 (10.2%); £3,700,717.61 -> £3,322,596.24 (10.2%); £3,700,717.87 -> £3,322,596.40 (10.2%); £3,700,718.13 -> £3,322,596.57 (10.2%); £3,700,718.38 -> £3,322,596.74 (10.2%); £3,700,718.64 -> £3,322,596.91 (10.2%); £3,700,718.89 -> £3,322,597.09 (10.2%); £3,700,719.15 -> £3,322,597.26 (10.2%); £3,700,719.41 -> £3,322,597.43 (10.2%); £3,700,719.66 -> £3,322,597.59 (10.2%); £3,700,719.92 -> £3,322,597.76 (10.2%); £3,700,720.18 -> £3,322,597.93 (10.2%); £3,700,720.43 -> £3,322,598.09 (10.2%); £3,700,720.68 -> £3,322,598.12 (10.2%); £3,700,720.93 -> £3,322,598.15 (10.2%); £3,700,721.17 -> £3,322,598.17 (10.2%); £3,700,721.38 -> £3,322,598.19 (10.2%); £3,700,721.59 -> £3,322,598.21 (10.2%); £3,700,721.73 -> £3,322,598.23 (10.2%); £3,700,721.89 -> £3,322,598.25 (10.2%); £3,700,722.04 -> £3,322,598.27 (10.2%); £3,700,722.19 -> £3,322,598.28 (10.2%); £3,700,722.34 -> £3,322,598.30 (10.2%); £3,700,722.50 -> £3,322,598.32 (10.2%); £3,700,722.65 -> £3,322,598.33 (10.2%); £3,700,722.80 -> £3,322,598.35 (10.2%); £3,700,722.96 -> £3,322,598.37 (10.2%); £3,700,723.11 -> £3,322,598.38 (10.2%); £3,700,723.26 -> £3,322,598.40 (10.2%); £3,700,723.41 -> £3,322,598.56 (10.2%); £3,700,723.57 -> £3,322,598.71 (10.2%); £3,700,723.74 -> £3,322,598.87 (10.2%); £3,700,723.93 -> £3,322,599.04 (10.2%); £3,700,724.13 -> £3,322,599.20 (10.2%); £3,700,724.34 -> £3,322,599.36 (10.2%); £3,700,724.59 -> £3,322,599.52 (10.2%); £3,700,724.85 -> £3,322,599.68 (10.2%); £3,700,725.11 -> £3,322,599.70 (10.2%); £3,700,725.37 -> £3,322,599.73 (10.2%); £3,700,725.62 -> £3,322,599.75 (10.2%); £3,700,725.88 -> £3,322,599.77 (10.2%); £3,700,726.14 -> £3,322,599.80 (10.2%); £3,700,726.39 -> £3,322,599.82 (10.2%); £3,700,726.65 -> £3,322,599.85 (10.2%); £3,700,726.90 -> £3,322,599.87 (10.2%); £3,700,727.16 -> £3,322,599.89 (10.2%); £3,700,727.41 -> £3,322,599.92 (10.2%); £3,700,727.67 -> £3,322,599.94 (10.2%); £3,700,727.92 -> £3,322,599.97 (10.2%); £3,700,728.18 -> £3,322,599.99 (10.2%); £3,700,728.44 -> £3,322,600.16 (10.2%); £3,700,728.68 -> £3,322,600.33 (10.2%); £3,700,728.94 -> £3,322,600.50 (10.2%); £3,700,729.19 -> £3,322,600.67 (10.2%); £3,700,729.45 -> £3,322,600.83 (10.2%); £3,700,729.70 -> £3,322,601.00 (10.2%); £3,700,729.95 -> £3,322,601.17 (10.2%); £3,700,730.21 -> £3,322,601.33 (10.2%); £3,700,730.47 -> £3,322,601.50 (10.2%); £3,700,730.72 -> £3,322,601.66 (10.2%); £3,700,730.96 -> £3,322,601.82 (10.2%); £3,700,731.23 -> £3,322,601.85 (10.2%); £3,700,731.48 -> £3,322,601.88 (10.2%); £3,700,731.72 -> £3,322,601.90 (10.2%); £3,700,731.93 -> £3,322,601.93 (10.2%); £3,700,732.13 -> £3,322,601.95 (10.2%); £3,700,732.26 -> £3,322,601.97 (10.2%); £3,700,732.39 -> £3,322,601.98 (10.2%); £3,700,732.52 -> £3,322,602.00 (10.2%); £3,700,732.66 -> £3,322,602.02 (10.2%); £3,700,732.79 -> £3,322,602.04 (10.2%); £3,700,732.93 -> £3,322,602.05 (10.2%); £3,700,733.06 -> £3,322,602.07 (10.2%); £3,700,733.20 -> £3,322,602.09 (10.2%); £3,700,733.33 -> £3,322,602.10 (10.2%); £3,700,733.46 -> £3,322,602.12 (10.2%); £3,700,733.60 -> £3,322,602.14 (10.2%); £3,700,733.73 -> £3,322,602.28 (10.2%); £3,700,733.87 -> £3,322,602.42 (10.2%); £3,700,734.02 -> £3,322,602.57 (10.2%); £3,700,734.18 -> £3,322,602.72 (10.2%); £3,700,734.36 -> £3,322,602.87 (10.2%); £3,700,734.56 -> £3,322,603.02 (10.2%); £3,700,734.77 -> £3,322,603.18 (10.2%); £3,700,735.00 -> £3,322,603.33 (10.2%); £3,700,735.22 -> £3,322,603.35 (10.2%); £3,700,735.44 -> £3,322,603.38 (10.2%); £3,700,735.66 -> £3,322,603.41 (10.2%); £3,700,735.88 -> £3,322,603.43 (10.2%); £3,700,736.11 -> £3,322,603.46 (10.2%); £3,700,736.34 -> £3,322,603.49 (10.2%); £3,700,736.56 -> £3,322,603.51 (10.2%); £3,700,736.78 -> £3,322,603.54 (10.2%); £3,700,737.01 -> £3,322,603.56 (10.2%); £3,700,737.24 -> £3,322,603.59 (10.2%); £3,700,737.47 -> £3,322,603.61 (10.2%); £3,700,737.70 -> £3,322,603.64 (10.2%); £3,700,737.92 -> £3,322,603.67 (10.2%); £3,700,738.15 -> £3,322,603.83 (10.2%); £3,700,738.37 -> £3,322,603.99 (10.2%); £3,700,738.60 -> £3,322,604.15 (10.2%); £3,700,738.83 -> £3,322,604.31 (10.2%); £3,700,739.05 -> £3,322,604.47 (10.2%); £3,700,739.27 -> £3,322,604.63 (10.2%); £3,700,739.49 -> £3,322,604.80 (10.2%); £3,700,739.72 -> £3,322,604.96 (10.2%); £3,700,739.93 -> £3,322,605.12 (10.2%); £3,700,740.16 -> £3,322,605.28 (10.2%); £3,700,740.38 -> £3,322,605.43 (10.2%); £3,700,740.60 -> £3,322,605.46 (10.2%); £3,700,740.82 -> £3,322,605.48 (10.2%); £3,700,741.03 -> £3,322,605.51 (10.2%); £3,700,741.22 -> £3,322,605.53 (10.2%); £3,700,741.40 -> £3,322,605.55 (10.2%); £3,700,741.53 -> £3,322,605.57 (10.2%); £3,700,741.66 -> £3,322,605.59 (10.2%); £3,700,741.80 -> £3,322,605.61 (10.2%); £3,700,741.94 -> £3,322,605.63 (10.2%); £3,700,742.07 -> £3,322,605.65 (10.2%); £3,700,742.20 -> £3,322,605.67 (10.2%); £3,700,742.34 -> £3,322,605.68 (10.2%); £3,700,742.48 -> £3,322,605.70 (10.2%); £3,700,742.61 -> £3,322,605.72 (10.2%); £3,700,742.75 -> £3,322,605.73 (10.2%); £3,700,742.88 -> £3,322,605.75 (10.2%); £3,700,743.02 -> £3,322,605.89 (10.2%); £3,700,743.16 -> £3,322,606.02 (10.2%); £3,700,743.30 -> £3,322,606.16 (10.2%); £3,700,743.47 -> £3,322,606.30 (10.2%); £3,700,743.65 -> £3,322,606.44 (10.2%); £3,700,743.85 -> £3,322,606.58 (10.2%); £3,700,744.05 -> £3,322,606.73 (10.2%); £3,700,744.28 -> £3,322,606.88 (10.2%); £3,700,744.51 -> £3,322,606.91 (10.2%); £3,700,744.73 -> £3,322,606.94 (10.2%); £3,700,744.96 -> £3,322,606.97 (10.2%); £3,700,745.18 -> £3,322,607.00 (10.2%); £3,700,745.41 -> £3,322,607.03 (10.2%); £3,700,745.63 -> £3,322,607.06 (10.2%); £3,700,745.85 -> £3,322,607.09 (10.2%); £3,700,746.07 -> £3,322,607.12 (10.2%); £3,700,746.29 -> £3,322,607.15 (10.2%); £3,700,746.52 -> £3,322,607.18 (10.2%); £3,700,746.75 -> £3,322,607.21 (10.2%); £3,700,746.97 -> £3,322,607.24 (10.2%); £3,700,747.19 -> £3,322,607.27 (10.2%); £3,700,747.42 -> £3,322,607.42 (10.2%); £3,700,747.64 -> £3,322,607.58 (10.2%); £3,700,747.87 -> £3,322,607.74 (10.2%); £3,700,748.10 -> £3,322,607.89 (10.2%); £3,700,748.32 -> £3,322,608.05 (10.2%); £3,700,748.53 -> £3,322,608.20 (10.2%); £3,700,748.75 -> £3,322,608.35 (10.2%); £3,700,748.97 -> £3,322,608.50 (10.2%); £3,700,749.19 -> £3,322,608.65 (10.2%); £3,700,749.42 -> £3,322,608.80 (10.2%); £3,700,749.64 -> £3,322,608.95 (10.2%); £3,700,749.87 -> £3,322,608.98 (10.2%); £3,700,750.09 -> £3,322,609.01 (10.2%); £3,700,750.30 -> £3,322,609.04 (10.2%); £3,700,750.49 -> £3,322,609.06 (10.2%); £3,700,750.67 -> £3,322,609.08 (10.2%); £3,700,750.82 -> £3,322,609.10 (10.2%); £3,700,750.97 -> £3,322,609.11 (10.2%); £3,700,751.12 -> £3,322,609.13 (10.2%); £3,700,751.28 -> £3,322,609.15 (10.2%); £3,700,751.43 -> £3,322,609.17 (10.2%); £3,700,751.58 -> £3,322,609.18 (10.2%); £3,700,751.73 -> £3,322,609.20 (10.2%); £3,700,751.89 -> £3,322,609.21 (10.2%); £3,700,752.04 -> £3,322,609.23 (10.2%); £3,700,752.19 -> £3,322,609.25 (10.2%); £3,700,752.34 -> £3,322,609.27 (10.2%); £3,700,752.49 -> £3,322,609.41 (10.2%); £3,700,752.63 -> £3,322,609.56 (10.2%); £3,700,752.80 -> £3,322,609.70 (10.2%); £3,700,752.99 -> £3,322,609.85 (10.2%); £3,700,753.20 -> £3,322,610.00 (10.2%); £3,700,753.42 -> £3,322,610.14 (10.2%); £3,700,753.66 -> £3,322,610.29 (10.2%); £3,700,753.91 -> £3,322,610.43 (10.2%); £3,700,754.16 -> £3,322,610.46 (10.2%); £3,700,754.41 -> £3,322,610.48 (10.2%); £3,700,754.67 -> £3,322,610.50 (10.2%); £3,700,754.93 -> £3,322,610.53 (10.2%); £3,700,755.17 -> £3,322,610.55 (10.2%); £3,700,755.44 -> £3,322,610.57 (10.2%); £3,700,755.68 -> £3,322,610.60 (10.2%); £3,700,755.93 -> £3,322,610.62 (10.2%); £3,700,756.18 -> £3,322,610.64 (10.2%); £3,700,756.44 -> £3,322,610.67 (10.2%); £3,700,756.69 -> £3,322,610.69 (10.2%); £3,700,756.95 -> £3,322,610.72 (10.2%); £3,700,757.20 -> £3,322,610.74 (10.2%); £3,700,757.45 -> £3,322,610.89 (10.2%); £3,700,757.70 -> £3,322,611.04 (10.2%); £3,700,757.96 -> £3,322,611.19 (10.2%); £3,700,758.22 -> £3,322,611.34 (10.2%); £3,700,758.47 -> £3,322,611.49 (10.2%); £3,700,758.73 -> £3,322,611.65 (10.2%); £3,700,758.97 -> £3,322,611.81 (10.2%); £3,700,759.22 -> £3,322,611.97 (10.2%); £3,700,759.47 -> £3,322,612.13 (10.2%); £3,700,759.73 -> £3,322,612.28 (10.2%); £3,700,759.99 -> £3,322,612.43 (10.2%); £3,700,760.24 -> £3,322,612.46 (10.2%); £3,700,760.50 -> £3,322,612.49 (10.2%); £3,700,760.73 -> £3,322,612.51 (10.2%); £3,700,760.94 -> £3,322,612.54 (10.2%); £3,700,761.13 -> £3,322,612.56 (10.2%); £3,700,761.28 -> £3,322,612.57 (10.2%); £3,700,761.43 -> £3,322,612.59 (10.2%); £3,700,761.58 -> £3,322,612.61 (10.2%); £3,700,761.73 -> £3,322,612.63 (10.2%); £3,700,761.88 -> £3,322,612.64 (10.2%); £3,700,762.03 -> £3,322,612.66 (10.2%); £3,700,762.18 -> £3,322,612.68 (10.2%); £3,700,762.34 -> £3,322,612.69 (10.2%); £3,700,762.48 -> £3,322,612.71 (10.2%); £3,700,762.63 -> £3,322,612.73 (10.2%); £3,700,762.78 -> £3,322,612.74 (10.2%); £3,700,762.92 -> £3,322,612.85 (10.2%); £3,700,763.08 -> £3,322,612.96 (10.2%); £3,700,763.25 -> £3,322,613.07 (10.2%); £3,700,763.44 -> £3,322,613.19 (10.2%); £3,700,763.64 -> £3,322,613.31 (10.2%); £3,700,763.85 -> £3,322,613.43 (10.2%); £3,700,764.09 -> £3,322,613.55 (10.2%); £3,700,764.34 -> £3,322,613.66 (10.2%); £3,700,764.59 -> £3,322,613.68 (10.2%); £3,700,764.84 -> £3,322,613.71 (10.2%); £3,700,765.09 -> £3,322,613.73 (10.2%); £3,700,765.35 -> £3,322,613.75 (10.2%); £3,700,765.60 -> £3,322,613.78 (10.2%); £3,700,765.85 -> £3,322,613.80 (10.2%); £3,700,766.10 -> £3,322,613.83 (10.2%); £3,700,766.35 -> £3,322,613.85 (10.2%); £3,700,766.60 -> £3,322,613.87 (10.2%); £3,700,766.86 -> £3,322,613.90 (10.2%); £3,700,767.11 -> £3,322,613.92 (10.2%); £3,700,767.36 -> £3,322,613.95 (10.2%); £3,700,767.62 -> £3,322,613.97 (10.2%); £3,700,767.87 -> £3,322,614.10 (10.2%); £3,700,768.13 -> £3,322,614.22 (10.2%); £3,700,768.38 -> £3,322,614.35 (10.2%); £3,700,768.65 -> £3,322,614.48 (10.2%); £3,700,768.90 -> £3,322,614.60 (10.2%); £3,700,769.16 -> £3,322,614.73 (10.2%); £3,700,769.41 -> £3,322,614.86 (10.2%); £3,700,769.66 -> £3,322,614.99 (10.2%); £3,700,769.90 -> £3,322,615.11 (10.2%); £3,700,770.14 -> £3,322,615.23 (10.2%); £3,700,770.39 -> £3,322,615.35 (10.2%); £3,700,770.64 -> £3,322,615.37 (10.2%); £3,700,770.89 -> £3,322,615.40 (10.2%); £3,700,771.13 -> £3,322,615.43 (10.2%); £3,700,771.35 -> £3,322,615.45 (10.2%); £3,700,771.54 -> £3,322,615.47 (10.2%); £3,700,771.69 -> £3,322,615.49 (10.2%); £3,700,771.84 -> £3,322,615.50 (10.2%); £3,700,772.00 -> £3,322,615.52 (10.2%); £3,700,772.15 -> £3,322,615.54 (10.2%); £3,700,772.30 -> £3,322,615.56 (10.2%); £3,700,772.45 -> £3,322,615.57 (10.2%); £3,700,772.60 -> £3,322,615.59 (10.2%); £3,700,772.75 -> £3,322,615.61 (10.2%); £3,700,772.91 -> £3,322,615.62 (10.2%); £3,700,773.05 -> £3,322,615.64 (10.2%); £3,700,773.21 -> £3,322,615.66 (10.2%); £3,700,773.36 -> £3,322,615.73 (10.2%); £3,700,773.51 -> £3,322,615.81 (10.2%); £3,700,773.68 -> £3,322,615.89 (10.2%); £3,700,773.86 -> £3,322,615.98 (10.2%); £3,700,774.05 -> £3,322,616.07 (10.2%); £3,700,774.27 -> £3,322,616.16 (10.2%); £3,700,774.51 -> £3,322,616.24 (10.2%); £3,700,774.76 -> £3,322,616.33 (10.2%); £3,700,775.01 -> £3,322,616.35 (10.2%); £3,700,775.26 -> £3,322,616.38 (10.2%); £3,700,775.52 -> £3,322,616.40 (10.2%); £3,700,775.77 -> £3,322,616.42 (10.2%); £3,700,776.02 -> £3,322,616.45 (10.2%); £3,700,776.27 -> £3,322,616.47 (10.2%); £3,700,776.52 -> £3,322,616.50 (10.2%); £3,700,776.78 -> £3,322,616.52 (10.2%); £3,700,777.03 -> £3,322,616.54 (10.2%); £3,700,777.27 -> £3,322,616.57 (10.2%); £3,700,777.52 -> £3,322,616.59 (10.2%); £3,700,777.77 -> £3,322,616.62 (10.2%); £3,700,778.01 -> £3,322,616.64 (10.2%); £3,700,778.26 -> £3,322,616.74 (10.2%); £3,700,778.52 -> £3,322,616.84 (10.2%); £3,700,778.76 -> £3,322,616.94 (10.2%); £3,700,779.01 -> £3,322,617.04 (10.2%); £3,700,779.26 -> £3,322,617.14 (10.2%); £3,700,779.51 -> £3,322,617.24 (10.2%); £3,700,779.75 -> £3,322,617.33 (10.2%); £3,700,780.01 -> £3,322,617.43 (10.2%); £3,700,780.25 -> £3,322,617.53 (10.2%); £3,700,780.50 -> £3,322,617.62 (10.2%); £3,700,780.75 -> £3,322,617.72 (10.2%); £3,700,780.99 -> £3,322,617.75 (10.2%); £3,700,781.25 -> £3,322,617.77 (10.2%); £3,700,781.49 -> £3,322,617.80 (10.2%); £3,700,781.70 -> £3,322,617.82 (10.2%); £3,700,781.89 -> £3,322,617.84 (10.2%); £3,700,782.04 -> £3,322,617.86 (10.2%); £3,700,782.19 -> £3,322,617.88 (10.2%); £3,700,782.35 -> £3,322,617.89 (10.2%); £3,700,782.50 -> £3,322,617.91 (10.2%); £3,700,782.65 -> £3,322,617.93 (10.2%); £3,700,782.80 -> £3,322,617.94 (10.2%); £3,700,782.95 -> £3,322,617.96 (10.2%); £3,700,783.10 -> £3,322,617.98 (10.2%); £3,700,783.25 -> £3,322,617.99 (10.2%); £3,700,783.41 -> £3,322,618.01 (10.2%); £3,700,783.56 -> £3,322,618.03 (10.2%); £3,700,783.71 -> £3,322,618.10 (10.2%); £3,700,783.86 -> £3,322,618.18 (10.2%); £3,700,784.02 -> £3,322,618.26 (10.2%); £3,700,784.20 -> £3,322,618.34 (10.2%); £3,700,784.40 -> £3,322,618.43 (10.2%); £3,700,784.62 -> £3,322,618.51 (10.2%); £3,700,784.85 -> £3,322,618.60 (10.2%); £3,700,785.10 -> £3,322,618.68 (10.2%); £3,700,785.36 -> £3,322,618.70 (10.2%); £3,700,785.61 -> £3,322,618.73 (10.2%); £3,700,785.86 -> £3,322,618.75 (10.2%); £3,700,786.11 -> £3,322,618.77 (10.2%); £3,700,786.37 -> £3,322,618.80 (10.2%); £3,700,786.62 -> £3,322,618.82 (10.2%); £3,700,786.87 -> £3,322,618.85 (10.2%); £3,700,787.12 -> £3,322,618.87 (10.2%); £3,700,787.37 -> £3,322,618.89 (10.2%); £3,700,787.62 -> £3,322,618.91 (10.2%); £3,700,787.88 -> £3,322,618.94 (10.2%); £3,700,788.13 -> £3,322,618.96 (10.2%); £3,700,788.39 -> £3,322,618.99 (10.2%); £3,700,788.64 -> £3,322,619.08 (10.2%); £3,700,788.90 -> £3,322,619.18 (10.2%); £3,700,789.15 -> £3,322,619.28 (10.2%); £3,700,789.41 -> £3,322,619.37 (10.2%); £3,700,789.67 -> £3,322,619.47 (10.2%); £3,700,789.92 -> £3,322,619.57 (10.2%); £3,700,790.16 -> £3,322,619.66 (10.2%); £3,700,790.42 -> £3,322,619.76 (10.2%); £3,700,790.67 -> £3,322,619.85 (10.2%); £3,700,790.92 -> £3,322,619.95 (10.2%); £3,700,791.17 -> £3,322,620.04 (10.2%); £3,700,791.42 -> £3,322,620.07 (10.2%); £3,700,791.68 -> £3,322,620.09 (10.2%); £3,700,791.90 -> £3,322,620.12 (10.2%); £3,700,792.12 -> £3,322,620.14 (10.2%); £3,700,792.32 -> £3,322,620.16 (10.2%); £3,700,792.47 -> £3,322,620.18 (10.2%); £3,700,792.62 -> £3,322,620.20 (10.2%); £3,700,792.77 -> £3,322,620.22 (10.2%); £3,700,792.92 -> £3,322,620.23 (10.2%); £3,700,793.07 -> £3,322,620.25 (10.2%); £3,700,793.22 -> £3,322,620.27 (10.2%); £3,700,793.38 -> £3,322,620.28 (10.2%); £3,700,793.53 -> £3,322,620.30 (10.2%); £3,700,793.68 -> £3,322,620.32 (10.2%); £3,700,793.83 -> £3,322,620.33 (10.2%); £3,700,793.98 -> £3,322,620.35 (10.2%); £3,700,794.13 -> £3,322,620.46 (10.2%); £3,700,794.28 -> £3,322,620.57 (10.2%); £3,700,794.45 -> £3,322,620.69 (10.2%); £3,700,794.64 -> £3,322,620.81 (10.2%); £3,700,794.84 -> £3,322,620.93 (10.2%); £3,700,795.06 -> £3,322,621.04 (10.2%); £3,700,795.29 -> £3,322,621.15 (10.2%); £3,700,795.55 -> £3,322,621.26 (10.2%); £3,700,795.81 -> £3,322,621.28 (10.2%); £3,700,796.05 -> £3,322,621.31 (10.2%); £3,700,796.30 -> £3,322,621.33 (10.2%); £3,700,796.55 -> £3,322,621.35 (10.2%); £3,700,796.80 -> £3,322,621.38 (10.2%); £3,700,797.05 -> £3,322,621.40 (10.2%); £3,700,797.30 -> £3,322,621.43 (10.2%); £3,700,797.55 -> £3,322,621.45 (10.2%); £3,700,797.81 -> £3,322,621.48 (10.2%); £3,700,798.06 -> £3,322,621.50 (10.2%); £3,700,798.31 -> £3,322,621.53 (10.2%); £3,700,798.56 -> £3,322,621.55 (10.2%); £3,700,798.81 -> £3,322,621.58 (10.2%); £3,700,799.07 -> £3,322,621.70 (10.2%); £3,700,799.32 -> £3,322,621.82 (10.2%); £3,700,799.57 -> £3,322,621.94 (10.2%); £3,700,799.82 -> £3,322,622.07 (10.2%); £3,700,800.07 -> £3,322,622.19 (10.2%); £3,700,800.32 -> £3,322,622.31 (10.2%); £3,700,800.57 -> £3,322,622.43 (10.2%); £3,700,800.82 -> £3,322,622.55 (10.2%); £3,700,801.08 -> £3,322,622.66 (10.2%); £3,700,801.33 -> £3,322,622.78 (10.2%); £3,700,801.59 -> £3,322,622.90 (10.2%); £3,700,801.84 -> £3,322,622.93 (10.2%); £3,700,802.09 -> £3,322,622.96 (10.2%); £3,700,802.32 -> £3,322,622.98 (10.2%); £3,700,802.53 -> £3,322,623.00 (10.2%); £3,700,802.72 -> £3,322,623.02 (10.2%); £3,700,802.86 -> £3,322,623.04 (10.2%); £3,700,802.99 -> £3,322,623.06 (10.2%); £3,700,803.13 -> £3,322,623.08 (10.2%); £3,700,803.26 -> £3,322,623.10 (10.2%); £3,700,803.40 -> £3,322,623.11 (10.2%); £3,700,803.53 -> £3,322,623.13 (10.2%); £3,700,803.67 -> £3,322,623.15 (10.2%); £3,700,803.81 -> £3,322,623.16 (10.2%); £3,700,803.94 -> £3,322,623.18 (10.2%); £3,700,804.08 -> £3,322,623.20 (10.2%); £3,700,804.21 -> £3,322,623.21 (10.2%); £3,700,804.35 -> £3,322,623.35 (10.2%); £3,700,804.49 -> £3,322,623.50 (10.2%); £3,700,804.63 -> £3,322,623.64 (10.2%); £3,700,804.80 -> £3,322,623.79 (10.2%); £3,700,804.98 -> £3,322,623.94 (10.2%); £3,700,805.18 -> £3,322,624.10 (10.2%); £3,700,805.39 -> £3,322,624.25 (10.2%); £3,700,805.61 -> £3,322,624.40 (10.2%); £3,700,805.84 -> £3,322,624.43 (10.2%); £3,700,806.06 -> £3,322,624.46 (10.2%); £3,700,806.28 -> £3,322,624.48 (10.2%); £3,700,806.51 -> £3,322,624.51 (10.2%); £3,700,806.74 -> £3,322,624.53 (10.2%); £3,700,806.96 -> £3,322,624.56 (10.2%); £3,700,807.18 -> £3,322,624.59 (10.2%); £3,700,807.41 -> £3,322,624.61 (10.2%); £3,700,807.62 -> £3,322,624.64 (10.2%); £3,700,807.84 -> £3,322,624.66 (10.2%); £3,700,808.06 -> £3,322,624.69 (10.2%); £3,700,808.28 -> £3,322,624.72 (10.2%); £3,700,808.49 -> £3,322,624.74 (10.2%); £3,700,808.72 -> £3,322,624.89 (10.2%); £3,700,808.95 -> £3,322,625.05 (10.2%); £3,700,809.17 -> £3,322,625.20 (10.2%); £3,700,809.40 -> £3,322,625.36 (10.2%); £3,700,809.62 -> £3,322,625.52 (10.2%); £3,700,809.86 -> £3,322,625.68 (10.2%); £3,700,810.07 -> £3,322,625.83 (10.2%); £3,700,810.30 -> £3,322,625.99 (10.2%); £3,700,810.52 -> £3,322,626.14 (10.2%); £3,700,810.75 -> £3,322,626.29 (10.2%); £3,700,810.97 -> £3,322,626.45 (10.2%); £3,700,811.19 -> £3,322,626.48 (10.2%); £3,700,811.41 -> £3,322,626.51 (10.2%); £3,700,811.61 -> £3,322,626.53 (10.2%); £3,700,811.80 -> £3,322,626.56 (10.2%); £3,700,811.98 -> £3,322,626.58 (10.2%); £3,700,812.12 -> £3,322,626.60 (10.2%); £3,700,812.25 -> £3,322,626.62 (10.2%); £3,700,812.38 -> £3,322,626.64 (10.2%); £3,700,812.51 -> £3,322,626.66 (10.2%); £3,700,812.65 -> £3,322,626.67 (10.2%); £3,700,812.79 -> £3,322,626.69 (10.2%); £3,700,812.92 -> £3,322,626.71 (10.2%); £3,700,813.05 -> £3,322,626.72 (10.2%); £3,700,813.19 -> £3,322,626.74 (10.2%); £3,700,813.34 -> £3,322,626.76 (10.2%); £3,700,813.47 -> £3,322,626.77 (10.2%); £3,700,813.61 -> £3,322,626.85 (10.2%); £3,700,813.74 -> £3,322,626.93 (10.2%); £3,700,813.89 -> £3,322,627.00 (10.2%); £3,700,814.06 -> £3,322,627.08 (10.2%); £3,700,814.24 -> £3,322,627.16 (10.2%); £3,700,814.44 -> £3,322,627.25 (10.2%); £3,700,814.65 -> £3,322,627.33 (10.2%); £3,700,814.88 -> £3,322,627.42 (10.2%); £3,700,815.11 -> £3,322,627.45 (10.2%); £3,700,815.33 -> £3,322,627.47 (10.2%); £3,700,815.55 -> £3,322,627.51 (10.2%); £3,700,815.78 -> £3,322,627.54 (10.2%); £3,700,816.00 -> £3,322,627.57 (10.2%); £3,700,816.23 -> £3,322,627.60 (10.2%); £3,700,816.46 -> £3,322,627.63 (10.2%); £3,700,816.69 -> £3,322,627.66 (10.2%); £3,700,816.91 -> £3,322,627.69 (10.2%); £3,700,817.14 -> £3,322,627.72 (10.2%); £3,700,817.37 -> £3,322,627.75 (10.2%); £3,700,817.60 -> £3,322,627.78 (10.2%); £3,700,817.83 -> £3,322,627.81 (10.2%); £3,700,818.05 -> £3,322,627.90 (10.2%); £3,700,818.27 -> £3,322,628.00 (10.2%); £3,700,818.50 -> £3,322,628.10 (10.2%); £3,700,818.73 -> £3,322,628.20 (10.2%); £3,700,818.96 -> £3,322,628.30 (10.2%); £3,700,819.18 -> £3,322,628.40 (10.2%); £3,700,819.40 -> £3,322,628.50 (10.2%); £3,700,819.63 -> £3,322,628.60 (10.2%); £3,700,819.85 -> £3,322,628.69 (10.2%); £3,700,820.07 -> £3,322,628.79 (10.2%); £3,700,820.30 -> £3,322,628.88 (10.2%); £3,700,820.53 -> £3,322,628.91 (10.2%); £3,700,820.76 -> £3,322,628.94 (10.2%); £3,700,820.97 -> £3,322,628.96 (10.2%); £3,700,821.17 -> £3,322,628.99 (10.2%); £3,700,821.34 -> £3,322,629.01 (10.2%); £3,700,821.50 -> £3,322,629.02 (10.2%); £3,700,821.65 -> £3,322,629.04 (10.2%); £3,700,821.81 -> £3,322,629.06 (10.2%); £3,700,821.96 -> £3,322,629.08 (10.2%); £3,700,822.11 -> £3,322,629.09 (10.2%); £3,700,822.26 -> £3,322,629.11 (10.2%); £3,700,822.42 -> £3,322,629.13 (10.2%); £3,700,822.57 -> £3,322,629.14 (10.2%); £3,700,822.72 -> £3,322,629.16 (10.2%); £3,700,822.87 -> £3,322,629.18 (10.2%); £3,700,823.03 -> £3,322,629.19 (10.2%); £3,700,823.18 -> £3,322,629.29 (10.2%); £3,700,823.34 -> £3,322,629.39 (10.2%); £3,700,823.51 -> £3,322,629.49 (10.2%); £3,700,823.70 -> £3,322,629.60 (10.2%); £3,700,823.90 -> £3,322,629.71 (10.2%); £3,700,824.13 -> £3,322,629.82 (10.2%); £3,700,824.37 -> £3,322,629.92 (10.2%); £3,700,824.63 -> £3,322,630.03 (10.2%); £3,700,824.88 -> £3,322,630.06 (10.2%); £3,700,825.14 -> £3,322,630.08 (10.2%); £3,700,825.39 -> £3,322,630.10 (10.2%); £3,700,825.64 -> £3,322,630.13 (10.2%); £3,700,825.89 -> £3,322,630.15 (10.2%); £3,700,826.14 -> £3,322,630.18 (10.2%); £3,700,826.39 -> £3,322,630.20 (10.2%); £3,700,826.65 -> £3,322,630.22 (10.2%); £3,700,826.92 -> £3,322,630.25 (10.2%); £3,700,827.18 -> £3,322,630.27 (10.2%); £3,700,827.43 -> £3,322,630.29 (10.2%); £3,700,827.69 -> £3,322,630.32 (10.2%); £3,700,827.95 -> £3,322,630.35 (10.2%); £3,700,828.21 -> £3,322,630.47 (10.2%); £3,700,828.47 -> £3,322,630.59 (10.2%); £3,700,828.73 -> £3,322,630.71 (10.2%); £3,700,828.98 -> £3,322,630.83 (10.2%); £3,700,829.24 -> £3,322,630.95 (10.2%); £3,700,829.50 -> £3,322,631.07 (10.2%); £3,700,829.75 -> £3,322,631.19 (10.2%); £3,700,830.01 -> £3,322,631.30 (10.2%); £3,700,830.26 -> £3,322,631.42 (10.2%); £3,700,830.52 -> £3,322,631.54 (10.2%); £3,700,830.77 -> £3,322,631.66 (10.2%); £3,700,831.03 -> £3,322,631.69 (10.2%); £3,700,831.29 -> £3,322,631.71 (10.2%); £3,700,831.52 -> £3,322,631.74 (10.2%); £3,700,831.74 -> £3,322,631.76 (10.2%); £3,700,831.94 -> £3,322,631.78 (10.2%); £3,700,832.09 -> £3,322,631.80 (10.2%); £3,700,832.25 -> £3,322,631.82 (10.2%); £3,700,832.41 -> £3,322,631.84 (10.2%); £3,700,832.56 -> £3,322,631.85 (10.2%); £3,700,832.71 -> £3,322,631.87 (10.2%); £3,700,832.86 -> £3,322,631.89 (10.2%); £3,700,833.02 -> £3,322,631.90 (10.2%); £3,700,833.18 -> £3,322,631.92 (10.2%); £3,700,833.33 -> £3,322,631.94 (10.2%); £3,700,833.48 -> £3,322,631.95 (10.2%); £3,700,833.64 -> £3,322,631.97 (10.2%); £3,700,833.80 -> £3,322,632.05 (10.2%); £3,700,833.95 -> £3,322,632.14 (10.2%); £3,700,834.12 -> £3,322,632.22 (10.2%); £3,700,834.32 -> £3,322,632.31 (10.2%); £3,700,834.53 -> £3,322,632.41 (10.2%); £3,700,834.75 -> £3,322,632.50 (10.2%); £3,700,834.99 -> £3,322,632.60 (10.2%); £3,700,835.25 -> £3,322,632.69 (10.2%); £3,700,835.50 -> £3,322,632.71 (10.2%); £3,700,835.76 -> £3,322,632.73 (10.2%); £3,700,836.01 -> £3,322,632.76 (10.2%); £3,700,836.27 -> £3,322,632.78 (10.2%); £3,700,836.52 -> £3,322,632.81 (10.2%); £3,700,836.78 -> £3,322,632.83 (10.2%); £3,700,837.05 -> £3,322,632.86 (10.2%); £3,700,837.31 -> £3,322,632.88 (10.2%); £3,700,837.58 -> £3,322,632.90 (10.2%); £3,700,837.84 -> £3,322,632.92 (10.2%); £3,700,838.10 -> £3,322,632.95 (10.2%); £3,700,838.36 -> £3,322,632.97 (10.2%); £3,700,838.61 -> £3,322,633.00 (10.2%); £3,700,838.86 -> £3,322,633.10 (10.2%); £3,700,839.12 -> £3,322,633.20 (10.2%); £3,700,839.38 -> £3,322,633.30 (10.2%); £3,700,839.64 -> £3,322,633.40 (10.2%); £3,700,839.89 -> £3,322,633.50 (10.2%); £3,700,840.15 -> £3,322,633.60 (10.2%); £3,700,840.41 -> £3,322,633.70 (10.2%); £3,700,840.68 -> £3,322,633.81 (10.2%); £3,700,840.93 -> £3,322,633.91 (10.2%); £3,700,841.18 -> £3,322,634.00 (10.2%); £3,700,841.44 -> £3,322,634.10 (10.2%); £3,700,841.70 -> £3,322,634.13 (10.2%); £3,700,841.95 -> £3,322,634.15 (10.2%); £3,700,842.19 -> £3,322,634.18 (10.2%); £3,700,842.41 -> £3,322,634.20 (10.2%); £3,700,842.60 -> £3,322,634.22 (10.2%); £3,700,842.76 -> £3,322,634.24 (10.2%); £3,700,842.92 -> £3,322,634.26 (10.2%); £3,700,843.07 -> £3,322,634.27 (10.2%); £3,700,843.22 -> £3,322,634.29 (10.2%); £3,700,843.37 -> £3,322,634.31 (10.2%); £3,700,843.53 -> £3,322,634.32 (10.2%); £3,700,843.68 -> £3,322,634.34 (10.2%); £3,700,843.84 -> £3,322,634.36 (10.2%); £3,700,843.99 -> £3,322,634.37 (10.2%); £3,700,844.15 -> £3,322,634.39 (10.2%); £3,700,844.31 -> £3,322,634.41 (10.2%); £3,700,844.47 -> £3,322,634.51 (10.2%); £3,700,844.62 -> £3,322,634.61 (10.2%); £3,700,844.79 -> £3,322,634.72 (10.2%); £3,700,844.98 -> £3,322,634.83 (10.2%); £3,700,845.19 -> £3,322,634.94 (10.2%); £3,700,845.42 -> £3,322,635.05 (10.2%); £3,700,845.66 -> £3,322,635.15 (10.2%); £3,700,845.92 -> £3,322,635.26 (10.2%); £3,700,846.18 -> £3,322,635.28 (10.2%); £3,700,846.44 -> £3,322,635.31 (10.2%); £3,700,846.68 -> £3,322,635.33 (10.2%); £3,700,846.94 -> £3,322,635.36 (10.2%); £3,700,847.20 -> £3,322,635.38 (10.2%); £3,700,847.46 -> £3,322,635.40 (10.2%); £3,700,847.71 -> £3,322,635.43 (10.2%); £3,700,847.96 -> £3,322,635.45 (10.2%); £3,700,848.21 -> £3,322,635.47 (10.2%); £3,700,848.47 -> £3,322,635.50 (10.2%); £3,700,848.73 -> £3,322,635.52 (10.2%); £3,700,848.98 -> £3,322,635.55 (10.2%); £3,700,849.25 -> £3,322,635.57 (10.2%); £3,700,849.50 -> £3,322,635.69 (10.2%); £3,700,849.76 -> £3,322,635.82 (10.2%); £3,700,850.02 -> £3,322,635.93 (10.2%); £3,700,850.28 -> £3,322,636.05 (10.2%); £3,700,850.53 -> £3,322,636.16 (10.2%); £3,700,850.80 -> £3,322,636.28 (10.2%); £3,700,851.05 -> £3,322,636.39 (10.2%); £3,700,851.31 -> £3,322,636.51 (10.2%); £3,700,851.56 -> £3,322,636.63 (10.2%); £3,700,851.83 -> £3,322,636.75 (10.2%); £3,700,852.07 -> £3,322,636.86 (10.2%); £3,700,852.33 -> £3,322,636.89 (10.2%); £3,700,852.58 -> £3,322,636.92 (10.2%); £3,700,852.83 -> £3,322,636.94 (10.2%); £3,700,853.05 -> £3,322,636.96 (10.2%); £3,700,853.25 -> £3,322,636.98 (10.2%); £3,700,853.41 -> £3,322,637.00 (10.2%); £3,700,853.56 -> £3,322,637.02 (10.2%); £3,700,853.71 -> £3,322,637.04 (10.2%); £3,700,853.86 -> £3,322,637.06 (10.2%); £3,700,854.02 -> £3,322,637.07 (10.2%); £3,700,854.17 -> £3,322,637.09 (10.2%); £3,700,854.32 -> £3,322,637.11 (10.2%); £3,700,854.47 -> £3,322,637.12 (10.2%); £3,700,854.62 -> £3,322,637.14 (10.2%); £3,700,854.78 -> £3,322,637.16 (10.2%); £3,700,854.93 -> £3,322,637.17 (10.2%); £3,700,855.08 -> £3,322,637.29 (10.2%); £3,700,855.24 -> £3,322,637.40 (10.2%); £3,700,855.41 -> £3,322,637.53 (10.2%); £3,700,855.59 -> £3,322,637.65 (10.2%); £3,700,855.80 -> £3,322,637.77 (10.2%); £3,700,856.02 -> £3,322,637.90 (10.2%); £3,700,856.26 -> £3,322,638.02 (10.2%); £3,700,856.51 -> £3,322,638.14 (10.2%); £3,700,856.77 -> £3,322,638.16 (10.2%); £3,700,857.03 -> £3,322,638.19 (10.2%); £3,700,857.28 -> £3,322,638.21 (10.2%); £3,700,857.54 -> £3,322,638.23 (10.2%); £3,700,857.80 -> £3,322,638.26 (10.2%); £3,700,858.05 -> £3,322,638.28 (10.2%); £3,700,858.31 -> £3,322,638.31 (10.2%); £3,700,858.56 -> £3,322,638.33 (10.2%); £3,700,858.81 -> £3,322,638.35 (10.2%); £3,700,859.07 -> £3,322,638.38 (10.2%); £3,700,859.33 -> £3,322,638.40 (10.2%); £3,700,859.58 -> £3,322,638.43 (10.2%); £3,700,859.84 -> £3,322,638.45 (10.2%); £3,700,860.10 -> £3,322,638.59 (10.2%); £3,700,860.34 -> £3,322,638.72 (10.2%); £3,700,860.60 -> £3,322,638.86 (10.2%); £3,700,860.86 -> £3,322,638.99 (10.2%); £3,700,861.12 -> £3,322,639.13 (10.2%); £3,700,861.38 -> £3,322,639.27 (10.2%); £3,700,861.63 -> £3,322,639.40 (10.2%); £3,700,861.89 -> £3,322,639.53 (10.2%); £3,700,862.14 -> £3,322,639.66 (10.2%); £3,700,862.39 -> £3,322,639.80 (10.2%); £3,700,862.65 -> £3,322,639.93 (10.2%); £3,700,862.90 -> £3,322,639.96 (10.2%); £3,700,863.15 -> £3,322,639.98 (10.2%); £3,700,863.39 -> £3,322,640.01 (10.2%); £3,700,863.61 -> £3,322,640.03 (10.2%); £3,700,863.81 -> £3,322,640.05 (10.2%); £3,700,863.97 -> £3,322,640.07 (10.2%); £3,700,864.12 -> £3,322,640.09 (10.2%); £3,700,864.27 -> £3,322,640.11 (10.2%); £3,700,864.43 -> £3,322,640.12 (10.2%); £3,700,864.58 -> £3,322,640.14 (10.2%); £3,700,864.73 -> £3,322,640.16 (10.2%); £3,700,864.88 -> £3,322,640.18 (10.2%); £3,700,865.04 -> £3,322,640.19 (10.2%); £3,700,865.18 -> £3,322,640.21 (10.2%); £3,700,865.33 -> £3,322,640.23 (10.2%); £3,700,865.49 -> £3,322,640.24 (10.2%); £3,700,865.64 -> £3,322,640.36 (10.2%); £3,700,865.80 -> £3,322,640.48 (10.2%); £3,700,865.97 -> £3,322,640.61 (10.2%); £3,700,866.16 -> £3,322,640.74 (10.2%); £3,700,866.37 -> £3,322,640.87 (10.2%); £3,700,866.59 -> £3,322,641.00 (10.2%); £3,700,866.83 -> £3,322,641.13 (10.2%); £3,700,867.09 -> £3,322,641.26 (10.2%); £3,700,867.35 -> £3,322,641.28 (10.2%); £3,700,867.62 -> £3,322,641.30 (10.2%); £3,700,867.87 -> £3,322,641.33 (10.2%); £3,700,868.13 -> £3,322,641.35 (10.2%); £3,700,868.39 -> £3,322,641.38 (10.2%); £3,700,868.65 -> £3,322,641.40 (10.2%); £3,700,868.91 -> £3,322,641.43 (10.2%); £3,700,869.16 -> £3,322,641.45 (10.2%); £3,700,869.42 -> £3,322,641.47 (10.2%); £3,700,869.67 -> £3,322,641.50 (10.2%); £3,700,869.93 -> £3,322,641.52 (10.2%); £3,700,870.19 -> £3,322,641.55 (10.2%); £3,700,870.45 -> £3,322,641.58 (10.2%); £3,700,870.70 -> £3,322,641.71 (10.2%); £3,700,870.96 -> £3,322,641.85 (10.2%); £3,700,871.22 -> £3,322,641.99 (10.2%); £3,700,871.48 -> £3,322,642.13 (10.2%); £3,700,871.73 -> £3,322,642.26 (10.2%); £3,700,871.99 -> £3,322,642.40 (10.2%); £3,700,872.25 -> £3,322,642.53 (10.2%); £3,700,872.51 -> £3,322,642.67 (10.2%); £3,700,872.77 -> £3,322,642.80 (10.2%); £3,700,873.03 -> £3,322,642.94 (10.2%); £3,700,873.28 -> £3,322,643.07 (10.2%); £3,700,873.54 -> £3,322,643.10 (10.2%); £3,700,873.80 -> £3,322,643.13 (10.2%); £3,700,874.04 -> £3,322,643.16 (10.2%); £3,700,874.26 -> £3,322,643.18 (10.2%); £3,700,874.46 -> £3,322,643.20 (10.2%); £3,700,874.60 -> £3,322,643.22 (10.2%); £3,700,874.73 -> £3,322,643.24 (10.2%); £3,700,874.87 -> £3,322,643.26 (10.2%); £3,700,875.01 -> £3,322,643.28 (10.2%); £3,700,875.14 -> £3,322,643.29 (10.2%); £3,700,875.28 -> £3,322,643.31 (10.2%); £3,700,875.42 -> £3,322,643.33 (10.2%); £3,700,875.56 -> £3,322,643.34 (10.2%); £3,700,875.69 -> £3,322,643.36 (10.2%); £3,700,875.83 -> £3,322,643.38 (10.2%); £3,700,875.96 -> £3,322,643.40 (10.2%); £3,700,876.10 -> £3,322,643.56 (10.2%); £3,700,876.23 -> £3,322,643.73 (10.2%); £3,700,876.38 -> £3,322,643.90 (10.2%); £3,700,876.54 -> £3,322,644.08 (10.2%); £3,700,876.73 -> £3,322,644.26 (10.2%); £3,700,876.93 -> £3,322,644.45 (10.2%); £3,700,877.14 -> £3,322,644.63 (10.2%); £3,700,877.37 -> £3,322,644.81 (10.2%); £3,700,877.60 -> £3,322,644.84 (10.2%); £3,700,877.82 -> £3,322,644.87 (10.2%); £3,700,878.05 -> £3,322,644.90 (10.2%); £3,700,878.27 -> £3,322,644.92 (10.2%); £3,700,878.50 -> £3,322,644.95 (10.2%); £3,700,878.73 -> £3,322,644.98 (10.2%); £3,700,878.96 -> £3,322,645.01 (10.2%); £3,700,879.19 -> £3,322,645.03 (10.2%); £3,700,879.41 -> £3,322,645.06 (10.2%); £3,700,879.64 -> £3,322,645.09 (10.2%); £3,700,879.85 -> £3,322,645.11 (10.2%); £3,700,880.08 -> £3,322,645.14 (10.2%); £3,700,880.30 -> £3,322,645.17 (10.2%); £3,700,880.53 -> £3,322,645.34 (10.2%); £3,700,880.77 -> £3,322,645.52 (10.2%); £3,700,880.99 -> £3,322,645.69 (10.2%); £3,700,881.23 -> £3,322,645.87 (10.2%); £3,700,881.46 -> £3,322,646.04 (10.2%); £3,700,881.68 -> £3,322,646.21 (10.2%); £3,700,881.91 -> £3,322,646.39 (10.2%); £3,700,882.13 -> £3,322,646.57 (10.2%); £3,700,882.36 -> £3,322,646.75 (10.2%); £3,700,882.59 -> £3,322,646.92 (10.2%); £3,700,882.81 -> £3,322,647.10 (10.2%); £3,700,883.04 -> £3,322,647.13 (10.2%); £3,700,883.26 -> £3,322,647.15 (10.2%); £3,700,883.48 -> £3,322,647.18 (10.2%); £3,700,883.66 -> £3,322,647.21 (10.2%); £3,700,883.83 -> £3,322,647.23 (10.2%); £3,700,883.98 -> £3,322,647.25 (10.2%); £3,700,884.12 -> £3,322,647.27 (10.2%); £3,700,884.26 -> £3,322,647.29 (10.2%); £3,700,884.40 -> £3,322,647.31 (10.2%); £3,700,884.54 -> £3,322,647.32 (10.2%); £3,700,884.68 -> £3,322,647.34 (10.2%); £3,700,884.82 -> £3,322,647.36 (10.2%); £3,700,884.96 -> £3,322,647.37 (10.2%); £3,700,885.11 -> £3,322,647.39 (10.2%); £3,700,885.24 -> £3,322,647.41 (10.2%); £3,700,885.39 -> £3,322,647.43 (10.2%); £3,700,885.53 -> £3,322,647.57 (10.2%); £3,700,885.68 -> £3,322,647.72 (10.2%); £3,700,885.83 -> £3,322,647.87 (10.2%); £3,700,886.00 -> £3,322,648.02 (10.2%); £3,700,886.19 -> £3,322,648.17 (10.2%); £3,700,886.39 -> £3,322,648.33 (10.2%); £3,700,886.60 -> £3,322,648.49 (10.2%); £3,700,886.83 -> £3,322,648.65 (10.2%); £3,700,887.07 -> £3,322,648.68 (10.2%); £3,700,887.31 -> £3,322,648.71 (10.2%); £3,700,887.54 -> £3,322,648.74 (10.2%); £3,700,887.77 -> £3,322,648.77 (10.2%); £3,700,887.99 -> £3,322,648.81 (10.2%); £3,700,888.23 -> £3,322,648.84 (10.2%); £3,700,888.46 -> £3,322,648.87 (10.2%); £3,700,888.70 -> £3,322,648.90 (10.2%); £3,700,888.92 -> £3,322,648.93 (10.2%); £3,700,889.15 -> £3,322,648.96 (10.2%); £3,700,889.39 -> £3,322,648.99 (10.2%); £3,700,889.62 -> £3,322,649.01 (10.2%); £3,700,889.85 -> £3,322,649.05 (10.2%); £3,700,890.09 -> £3,322,649.20 (10.2%); £3,700,890.32 -> £3,322,649.35 (10.2%); £3,700,890.55 -> £3,322,649.50 (10.2%); £3,700,890.78 -> £3,322,649.66 (10.2%); £3,700,891.02 -> £3,322,649.81 (10.2%); £3,700,891.25 -> £3,322,649.96 (10.2%); £3,700,891.48 -> £3,322,650.12 (10.2%); £3,700,891.72 -> £3,322,650.27 (10.2%); £3,700,891.96 -> £3,322,650.42 (10.2%); £3,700,892.20 -> £3,322,650.57 (10.2%); £3,700,892.44 -> £3,322,650.72 (10.2%); £3,700,892.67 -> £3,322,650.75 (10.2%); £3,700,892.90 -> £3,322,650.78 (10.2%); £3,700,893.13 -> £3,322,650.81 (10.2%); £3,700,893.33 -> £3,322,650.83 (10.2%); £3,700,893.50 -> £3,322,650.85 (10.2%); £3,700,893.67 -> £3,322,650.87 (10.2%); £3,700,893.83 -> £3,322,650.88 (10.2%); £3,700,893.98 -> £3,322,650.90 (10.2%); £3,700,894.15 -> £3,322,650.92 (10.2%); £3,700,894.31 -> £3,322,650.94 (10.2%); £3,700,894.47 -> £3,322,650.95 (10.2%); £3,700,894.63 -> £3,322,650.97 (10.2%); £3,700,894.80 -> £3,322,650.99 (10.2%); £3,700,894.96 -> £3,322,651.00 (10.2%); £3,700,895.12 -> £3,322,651.02 (10.2%); £3,700,895.28 -> £3,322,651.04 (10.2%); £3,700,895.44 -> £3,322,651.18 (10.2%); £3,700,895.60 -> £3,322,651.32 (10.2%); £3,700,895.78 -> £3,322,651.46 (10.2%); £3,700,895.98 -> £3,322,651.61 (10.2%); £3,700,896.20 -> £3,322,651.77 (10.2%); £3,700,896.43 -> £3,322,651.92 (10.2%); £3,700,896.68 -> £3,322,652.06 (10.2%); £3,700,896.96 -> £3,322,652.21 (10.2%); £3,700,897.22 -> £3,322,652.24 (10.2%); £3,700,897.51 -> £3,322,652.26 (10.2%); £3,700,897.78 -> £3,322,652.28 (10.2%); £3,700,898.05 -> £3,322,652.31 (10.2%); £3,700,898.31 -> £3,322,652.33 (10.2%); £3,700,898.59 -> £3,322,652.36 (10.2%); £3,700,898.85 -> £3,322,652.38 (10.2%); £3,700,899.12 -> £3,322,652.40 (10.2%); £3,700,899.40 -> £3,322,652.43 (10.2%); £3,700,899.67 -> £3,322,652.45 (10.2%); £3,700,899.94 -> £3,322,652.48 (10.2%); £3,700,900.22 -> £3,322,652.50 (10.2%); £3,700,900.49 -> £3,322,652.53 (10.2%); £3,700,900.76 -> £3,322,652.67 (10.2%); £3,700,901.02 -> £3,322,652.82 (10.2%); £3,700,901.29 -> £3,322,652.97 (10.2%); £3,700,901.55 -> £3,322,653.12 (10.2%); £3,700,901.81 -> £3,322,653.27 (10.2%); £3,700,902.08 -> £3,322,653.43 (10.2%); £3,700,902.35 -> £3,322,653.58 (10.2%); £3,700,902.61 -> £3,322,653.73 (10.2%); £3,700,902.88 -> £3,322,653.88 (10.2%); £3,700,903.15 -> £3,322,654.02 (10.2%); £3,700,903.41 -> £3,322,654.17 (10.2%); £3,700,903.68 -> £3,322,654.20 (10.2%); £3,700,903.95 -> £3,322,654.23 (10.2%); £3,700,904.19 -> £3,322,654.25 (10.2%); £3,700,904.41 -> £3,322,654.27 (10.2%); £3,700,904.63 -> £3,322,654.29 (10.2%); £3,700,904.79 -> £3,322,654.31 (10.2%); £3,700,904.95 -> £3,322,654.33 (10.2%); £3,700,905.12 -> £3,322,654.35 (10.2%); £3,700,905.28 -> £3,322,654.36 (10.2%); £3,700,905.45 -> £3,322,654.38 (10.2%); £3,700,905.61 -> £3,322,654.40 (10.2%); £3,700,905.77 -> £3,322,654.41 (10.2%); £3,700,905.93 -> £3,322,654.43 (10.2%); £3,700,906.10 -> £3,322,654.45 (10.2%); £3,700,906.26 -> £3,322,654.46 (10.2%); £3,700,906.42 -> £3,322,654.48 (10.2%); £3,700,906.58 -> £3,322,654.59 (10.2%); £3,700,906.74 -> £3,322,654.71 (10.2%); £3,700,906.92 -> £3,322,654.83 (10.2%); £3,700,907.12 -> £3,322,654.96 (10.2%); £3,700,907.34 -> £3,322,655.09 (10.2%); £3,700,907.57 -> £3,322,655.21 (10.2%); £3,700,907.82 -> £3,322,655.34 (10.2%); £3,700,908.09 -> £3,322,655.46 (10.2%); £3,700,908.37 -> £3,322,655.48 (10.2%); £3,700,908.65 -> £3,322,655.51 (10.2%); £3,700,908.91 -> £3,322,655.53 (10.2%); £3,700,909.17 -> £3,322,655.56 (10.2%); £3,700,909.43 -> £3,322,655.58 (10.2%); £3,700,909.70 -> £3,322,655.61 (10.2%); £3,700,909.97 -> £3,322,655.63 (10.2%); £3,700,910.24 -> £3,322,655.65 (10.2%); £3,700,910.50 -> £3,322,655.68 (10.2%); £3,700,910.76 -> £3,322,655.70 (10.2%); £3,700,911.04 -> £3,322,655.72 (10.2%); £3,700,911.31 -> £3,322,655.75 (10.2%); £3,700,911.58 -> £3,322,655.78 (10.2%); £3,700,911.86 -> £3,322,655.90 (10.2%); £3,700,912.12 -> £3,322,656.04 (10.2%); £3,700,912.39 -> £3,322,656.17 (10.2%); £3,700,912.66 -> £3,322,656.30 (10.2%); £3,700,912.93 -> £3,322,656.43 (10.2%); £3,700,913.19 -> £3,322,656.56 (10.2%); £3,700,913.46 -> £3,322,656.69 (10.2%); £3,700,913.72 -> £3,322,656.82 (10.2%); £3,700,913.98 -> £3,322,656.96 (10.2%); £3,700,914.26 -> £3,322,657.09 (10.2%); £3,700,914.53 -> £3,322,657.22 (10.2%); £3,700,914.80 -> £3,322,657.25 (10.2%); £3,700,915.07 -> £3,322,657.27 (10.2%); £3,700,915.32 -> £3,322,657.30 (10.2%); £3,700,915.55 -> £3,322,657.32 (10.2%); £3,700,915.76 -> £3,322,657.34 (10.2%); £3,700,915.93 -> £3,322,657.36 (10.2%); £3,700,916.09 -> £3,322,657.38 (10.2%); £3,700,916.24 -> £3,322,657.39 (10.2%); £3,700,916.40 -> £3,322,657.41 (10.2%); £3,700,916.56 -> £3,322,657.43 (10.2%); £3,700,916.72 -> £3,322,657.44 (10.2%); £3,700,916.88 -> £3,322,657.46 (10.2%); £3,700,917.04 -> £3,322,657.48 (10.2%); £3,700,917.19 -> £3,322,657.49 (10.2%); £3,700,917.35 -> £3,322,657.51 (10.2%); £3,700,917.52 -> £3,322,657.53 (10.2%); £3,700,917.67 -> £3,322,657.67 (10.2%); £3,700,917.83 -> £3,322,657.81 (10.2%); £3,700,918.01 -> £3,322,657.96 (10.2%); £3,700,918.21 -> £3,322,658.11 (10.2%); £3,700,918.43 -> £3,322,658.26 (10.2%); £3,700,918.66 -> £3,322,658.41 (10.2%); £3,700,918.91 -> £3,322,658.55 (10.2%); £3,700,919.18 -> £3,322,658.70 (10.2%); £3,700,919.45 -> £3,322,658.72 (10.2%); £3,700,919.71 -> £3,322,658.75 (10.2%); £3,700,919.99 -> £3,322,658.77 (10.2%); £3,700,920.25 -> £3,322,658.80 (10.2%); £3,700,920.52 -> £3,322,658.82 (10.2%); £3,700,920.79 -> £3,322,658.84 (10.2%); £3,700,921.06 -> £3,322,658.87 (10.2%); £3,700,921.34 -> £3,322,658.89 (10.2%); £3,700,921.62 -> £3,322,658.91 (10.2%); £3,700,921.88 -> £3,322,658.94 (10.2%); £3,700,922.15 -> £3,322,658.96 (10.2%); £3,700,922.42 -> £3,322,658.99 (10.2%); £3,700,922.69 -> £3,322,659.02 (10.2%); £3,700,922.96 -> £3,322,659.18 (10.2%); £3,700,923.23 -> £3,322,659.34 (10.2%); £3,700,923.50 -> £3,322,659.50 (10.2%); £3,700,923.77 -> £3,322,659.67 (10.2%); £3,700,924.04 -> £3,322,659.82 (10.2%); £3,700,924.31 -> £3,322,659.98 (10.2%); £3,700,924.58 -> £3,322,660.13 (10.2%); £3,700,924.84 -> £3,322,660.28 (10.2%); £3,700,925.11 -> £3,322,660.44 (10.2%); £3,700,925.38 -> £3,322,660.59 (10.2%); £3,700,925.65 -> £3,322,660.74 (10.2%); £3,700,925.92 -> £3,322,660.77 (10.2%); £3,700,926.20 -> £3,322,660.79 (10.2%); £3,700,926.45 -> £3,322,660.82 (10.2%); £3,700,926.67 -> £3,322,660.84 (10.2%); £3,700,926.88 -> £3,322,660.86 (10.2%); £3,700,927.04 -> £3,322,660.88 (10.2%); £3,700,927.20 -> £3,322,660.89 (10.2%); £3,700,927.36 -> £3,322,660.91 (10.2%); £3,700,927.53 -> £3,322,660.93 (10.2%); £3,700,927.68 -> £3,322,660.95 (10.2%); £3,700,927.85 -> £3,322,660.96 (10.2%); £3,700,928.00 -> £3,322,660.98 (10.2%); £3,700,928.16 -> £3,322,661.00 (10.2%); £3,700,928.32 -> £3,322,661.01 (10.2%); £3,700,928.48 -> £3,322,661.03 (10.2%); £3,700,928.65 -> £3,322,661.05 (10.2%); £3,700,928.81 -> £3,322,661.19 (10.2%); £3,700,928.97 -> £3,322,661.33 (10.2%); £3,700,929.16 -> £3,322,661.49 (10.2%); £3,700,929.36 -> £3,322,661.63 (10.2%); £3,700,929.58 -> £3,322,661.78 (10.2%); £3,700,929.81 -> £3,322,661.93 (10.2%); £3,700,930.06 -> £3,322,662.07 (10.2%); £3,700,930.33 -> £3,322,662.21 (10.2%); £3,700,930.60 -> £3,322,662.24 (10.2%); £3,700,930.87 -> £3,322,662.26 (10.2%); £3,700,931.14 -> £3,322,662.28 (10.2%); £3,700,931.41 -> £3,322,662.31 (10.2%); £3,700,931.69 -> £3,322,662.33 (10.2%); £3,700,931.96 -> £3,322,662.35 (10.2%); £3,700,932.23 -> £3,322,662.38 (10.2%); £3,700,932.50 -> £3,322,662.40 (10.2%); £3,700,932.78 -> £3,322,662.42 (10.2%); £3,700,933.05 -> £3,322,662.45 (10.2%); £3,700,933.32 -> £3,322,662.47 (10.2%); £3,700,933.59 -> £3,322,662.50 (10.2%); £3,700,933.86 -> £3,322,662.53 (10.2%); £3,700,934.15 -> £3,322,662.67 (10.2%); £3,700,934.42 -> £3,322,662.83 (10.2%); £3,700,934.69 -> £3,322,662.98 (10.2%); £3,700,934.95 -> £3,322,663.13 (10.2%); £3,700,935.22 -> £3,322,663.28 (10.2%); £3,700,935.50 -> £3,322,663.43 (10.2%); £3,700,935.78 -> £3,322,663.58 (10.2%); £3,700,936.05 -> £3,322,663.73 (10.2%); £3,700,936.33 -> £3,322,663.88 (10.2%); £3,700,936.60 -> £3,322,664.03 (10.2%); £3,700,936.87 -> £3,322,664.17 (10.2%); £3,700,937.15 -> £3,322,664.20 (10.2%); £3,700,937.42 -> £3,322,664.23 (10.2%); £3,700,937.67 -> £3,322,664.25 (10.2%); £3,700,937.91 -> £3,322,664.27 (10.2%); £3,700,938.13 -> £3,322,664.29 (10.2%); £3,700,938.28 -> £3,322,664.31 (10.2%); £3,700,938.45 -> £3,322,664.33 (10.2%); £3,700,938.61 -> £3,322,664.34 (10.2%); £3,700,938.78 -> £3,322,664.36 (10.2%); £3,700,938.93 -> £3,322,664.38 (10.2%); £3,700,939.10 -> £3,322,664.39 (10.2%); £3,700,939.26 -> £3,322,664.41 (10.2%); £3,700,939.43 -> £3,322,664.43 (10.2%); £3,700,939.59 -> £3,322,664.44 (10.2%); £3,700,939.75 -> £3,322,664.46 (10.2%); £3,700,939.91 -> £3,322,664.48 (10.2%); £3,700,940.07 -> £3,322,664.60 (10.2%); £3,700,940.23 -> £3,322,664.73 (10.2%); £3,700,940.41 -> £3,322,664.86 (10.2%); £3,700,940.61 -> £3,322,664.99 (10.2%); £3,700,940.82 -> £3,322,665.12 (10.2%); £3,700,941.06 -> £3,322,665.25 (10.2%); £3,700,941.31 -> £3,322,665.38 (10.2%); £3,700,941.57 -> £3,322,665.51 (10.2%); £3,700,941.85 -> £3,322,665.54 (10.2%); £3,700,942.11 -> £3,322,665.56 (10.2%); £3,700,942.38 -> £3,322,665.59 (10.2%); £3,700,942.65 -> £3,322,665.61 (10.2%); £3,700,942.92 -> £3,322,665.64 (10.2%); £3,700,943.19 -> £3,322,665.66 (10.2%); £3,700,943.48 -> £3,322,665.68 (10.2%); £3,700,943.75 -> £3,322,665.71 (10.2%); £3,700,944.01 -> £3,322,665.73 (10.2%); £3,700,944.29 -> £3,322,665.75 (10.2%); £3,700,944.55 -> £3,322,665.78 (10.2%); £3,700,944.82 -> £3,322,665.80 (10.2%); £3,700,945.09 -> £3,322,665.83 (10.2%); £3,700,945.35 -> £3,322,665.97 (10.2%); £3,700,945.63 -> £3,322,666.11 (10.2%); £3,700,945.90 -> £3,322,666.25 (10.2%); £3,700,946.17 -> £3,322,666.39 (10.2%); £3,700,946.44 -> £3,322,666.53 (10.2%); £3,700,946.71 -> £3,322,666.67 (10.2%); £3,700,946.99 -> £3,322,666.81 (10.2%); £3,700,947.25 -> £3,322,666.96 (10.2%); £3,700,947.52 -> £3,322,667.10 (10.2%); £3,700,947.80 -> £3,322,667.24 (10.2%); £3,700,948.07 -> £3,322,667.38 (10.2%); £3,700,948.34 -> £3,322,667.41 (10.2%); £3,700,948.61 -> £3,322,667.43 (10.2%); £3,700,948.86 -> £3,322,667.46 (10.2%); £3,700,949.10 -> £3,322,667.48 (10.2%)
- Bills issued: 141, average clarity 0.812, average bill shock 16.1%, bad debt provision £11,462.70, avg complaint probability 4.7%
- Solvency signal: £336,711/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £199,800.99 vs. naked (unhedged) net margin: £605,666.93
- hedging cost £405,865.94 vs. a fully unhedged book (commodity-only: actual net £199,800.99 vs. naked net £605,666.93)
  - C2_2: actual £115.65 vs. naked £1,054.69 -- hedging cost £939.04
  - C5_2: actual £301.45 vs. naked £1,247.57 -- hedging cost £946.11
  - C7: actual £-27.34 vs. naked £653.82 -- hedging cost £681.16
  - C8: actual £310.30 vs. naked £1,424.17 -- hedging cost £1,113.87
  - C9: actual £373.18 vs. naked £1,427.71 -- hedging cost £1,054.53
  - C_IC1: actual £114,253.44 vs. naked £208,996.78 -- hedging cost £94,743.34
  - C_IC2: actual £60,322.70 vs. naked £111,508.78 -- hedging cost £51,186.08
  - C_IC3: actual £18,878.62 vs. naked £119,696.87 -- hedging cost £100,818.25
  - C_IC3g: actual £3,837.46 vs. naked £56,934.03 -- hedging cost £53,096.57
  - C_IC4: actual £1,435.52 vs. naked £102,722.50 -- hedging cost £101,286.98

**Year narrative:** 2024 produced a net gain of £337,194.05 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 37 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £116,621.95 (gross £520,111.83, capital £5,665.93)
  - Electricity: gross £466,603.05, capital £5,665.93, net £112,834.43
  - Gas: gross £53,508.78, capital £0.00, net £3,787.52
- Treasury at year end: £3,753,752.21
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C8 0.89 (avg 0.89)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2025-01-08 period 31, net margin £-81.23

**Customer Book**

- Active accounts: 10 (C2_2, C5_2, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 4, SME electricity: 1, gas (dual-fuel): 1
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 2 accounts
- Average CLV (Point-in-Time, year-end 2025): £386,321.09
  - By billing account: C1 £3,648.63, C2 £4,920.67, C2_2 £3,633.45, C3 £6,450.25, C4 £2,793.07, C5 £8,246.68, C5_2 £4,012.33, C6 £19,237.70, C7 £6,276.77, C8 £7,413.75, C9 £7,428.99, C_IC1 £1,313,809.29, C_IC2 £675,304.74, C_IC3 £2,319,680.12, C_IC4 £1,411,959.90
- Bill shock events (>=20%): 22 -- C7 2025-04-30 (36%); C7 2025-05-31 (22%); C7 2025-06-07 (80%); C8 2025-01-31 (30%); C8 2025-02-28 (24%); C8 2025-04-30 (39%); C8 2025-05-31 (35%); C8 2025-06-07 (73%); C9 2025-04-30 (24%); C9 2025-05-31 (32%); C9 2025-06-07 (72%); C_IC1 2025-06-07 (77%); C_IC2 2025-06-07 (75%); C_IC3 2025-06-07 (78%); C_IC3g 2025-06-07 (77%); C_IC4 2025-06-07 (79%); C2_2 2025-01-31 (28%); C2_2 2025-02-28 (23%); C2_2 2025-05-31 (34%); C2_2 2025-06-07 (73%); C5_2 2025-04-30 (29%); C5_2 2025-06-07 (79%)
- Churn risk (accounts renewing in 2025): 3 at risk (≥20% churn prob): C2_2 32%, C8 32%, C9 26%

**Pricing & Margin**

- C2_2 (electricity): tariff £201.26-£290.27/MWh, net margin £105.03
- C5_2 (electricity): tariff £253.01/MWh, net margin £298.65
- C7 (electricity): tariff £165.00-£315.00/MWh, net margin £-23.72 -- **net-negative**
- C8 (electricity): tariff £149.29-£309.18/MWh, net margin £74.68
- C9 (electricity): tariff £165.00-£315.00/MWh, net margin £195.49
- C_IC1 (electricity): tariff £167.39-£319.56/MWh, net margin £62,405.83
- C_IC2 (electricity): tariff £161.16-£307.68/MWh, net margin £29,516.09
- C_IC3 (electricity): tariff £88.78-£169.49/MWh, net margin £18,844.97
- C_IC3g (gas): tariff £54.85/MWh, net margin £3,787.52
- C_IC4 (electricity): tariff £123.20-£273.78/MWh, net margin £1,417.43

**Portfolio Health**

- Capital cost ratio: 1.1% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 60, average clarity 0.775, average bill shock 24.1%, bad debt provision £4,989.04, avg complaint probability 5.9%
- Solvency signal: £417,084/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £62.96 vs. naked (unhedged) net margin: £346.44
- hedging cost £283.47 vs. a fully unhedged book (commodity-only: actual net £62.96 vs. naked net £346.44)
  - C2_2: actual £93.05 vs. naked £227.54 -- hedging cost £134.49
  - C8: actual £-30.08 vs. naked £118.90 -- hedging cost £148.98

**Year narrative:** 2025 produced a net gain of £116,621.95 across 10 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 22 customer(s) experienced a bill shock of >=20%.
