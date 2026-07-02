# Annual Report — The Synthetic Enterprise


## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £2,466,636.22
- Final treasury: £3,910,173.54
  (£1,443,537.32 net change)
- Solvency signal (final year): £630,575/customer (6 customers, OK; Ofgem floor £130/customer)
- Customer bills (all-in): £15,979,164.61
  VAT remitted to HMRC: (£771,071.11) | Revenue (ex-VAT): £15,208,093.50
  Non-commodity pass-through: (£3,897,378.65)
- Gross margin: £5,422,401.40
- Capital costs: £40,289.20
- Net margin: £5,382,112.20
- Capital cost ratio: 0.7% of gross
- Net margin as % of revenue: 35.4%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 38
- Bills issued: 1383, average clarity 0.812,
  service quality score 0.904
- Enterprise value (CLV sum across 13 billing accounts): £5,256,728.12
- Cost to serve (whole portfolio): £75,383.51, net margin after cost to serve: £5,306,728.68
- Hedge effectiveness (whole window): hedging cost £2,946,170.81 vs. a fully unhedged book (commodity-only: actual net £1,443,537.32 vs. naked net £4,389,708.13)

- **2021** (crisis year): net margin £87,129.50, 0 risk committee wake-up(s).
- **2022** (crisis year): net margin £304,766.07, 9 risk committee wake-up(s).

## Board Risk Summary

Synthesised risk indicators across portfolio, capital, operations and pricing.
RAG: RED = immediate board action, AMBER = monitor closely, GREEN = on track.

| Risk Indicator | Value | RAG | Implication |
|----------------|-------|-----|-------------|
| Revenue concentration | HHI 2388, I&C 99% | **AMBER** | Single I&C departure removes 14-29%% of margin |
| Gas segment ROC | 159.2x (net £30,910.99 on £194.14 capital) | **GREEN** | Gas legs destroy capital; electricity cross-subsidises |
| Churn blind miss rate | 4/7 departures (57%) | **RED** | Company did not forecast these churns |
| Demand estimation error | Peak mean 4.0%, max 15.6% | **RED** | EAC drift from asset acquisitions; smart meters eliminate |
| Pricing basis risk (worst year) | 2025: +33.1% mean over-estimate | **RED** | Over-priced contracts help margin but create churn risk |
| Net margin % of revenue | 35.4% (benchmark: 2-5%) | **GREEN** | Within/above industry range |

**Board Action Required:** Churn blind miss rate, Demand estimation error, Pricing basis risk (worst year) — RED rating(s) require immediate attention.

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £5,422,401.40, capital £40,289.20, net £5,382,112.20. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 0.7% (commodity basis, comparable to old model) / 0.7% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £87,129.50 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 35.4%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £5,382,112.20
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £4,389,708.13
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £2,946,170.81 vs. a fully unhedged book (commodity-only: actual net £1,443,537.32 vs. naked net £4,389,708.13)
- **Best hedging decision of the run**: C_IC1, term starting
  2021-04-30 (hedge fraction 0.92) -- hedging
  protected £99,546.73 vs. going naked.
- **Worst hedging decision of the run**: C_IC3, term
  starting 2019-01-01 (hedge fraction 0.96) --
  over-hedging cost £288,582.30 vs. going
  naked.

## Segment Margin Trend

Net margin (£) by segment, by year:

| Year | I&C electricity | I&C gas | SME electricity | resi electricity | resi gas | Total |
|---|---|---|---|---|---|---|
| 2016 | £0.00 | £0.00 | £254.88 | £626.84 | £296.53 | £1,178.25 |
| 2017 | £29,047.38 | £0.00 | £233.41 | £821.92 | £463.34 | £30,566.05 |
| 2018 | £99,071.38 | £0.00 | £-244.55 | £504.67 | £374.66 | £99,706.17 |
| 2019 | £217,183.69 | £9,326.63 | £213.88 | £720.65 | £427.56 | £227,872.41 |
| 2020 | £142,198.64 | £9,435.16 | £335.22 | £753.59 | £309.78 | £153,032.39 |
| 2021 | £78,579.41 | £8,520.22 | £223.65 | £119.18 | £-312.96 | £87,129.50 |
| 2022 | £303,451.97 | £4,122.01 | £987.68 | £-2,511.06 | £-1,284.53 | £304,766.07 |
| 2023 | £247,545.00 | £0.00 | £1,515.26 | £-397.05 | £-1,164.32 | £247,498.90 |
| 2024 | £195,724.90 | £0.00 | £581.94 | £1,530.91 | £396.91 | £198,234.67 |
| 2025 | £93,339.34 | £0.00 | £0.00 | £213.60 | £0.00 | £93,552.93 |

## Customer Lifecycle Events

Renewal decisions rolled at each annual renewal point across the simulation window.
Retained: **42** renewals.  Lost (churned): **7** accounts.

Accounts lost before end of window: C1, C2, C3, C4, C5, C6, C_IC3

| Account | Date | Outcome | p(churn) | p(win-back) | p(retain) | Roll |
|---------|------|---------|----------|-------------|-----------|------|
| C1 | 2016-12-31 | renewed | 0.2900 | 0.5500 | 0.8695 | 0.1646 |
| C5 | 2016-12-31 | renewed | 0.2900 | 0.3500 | 0.8115 | 0.2812 |
| C7 | 2016-12-31 | renewed | 0.2900 | 0.5500 | 0.8695 | 0.1050 |
| C1 | 2017-12-31 | renewed | 0.3200 | 0.5500 | 0.8560 | 0.6188 |
| C5 | 2017-12-31 | renewed | 0.3200 | 0.3500 | 0.7920 | 0.4449 |
| C7 | 2017-12-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.8255 |
| C_IC1 | 2018-01-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.3902 |
| C1 | 2018-12-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.0480 |
| C5 | 2018-12-31 | renewed | 0.3500 | 0.3500 | 0.7725 | 0.3096 |
| C7 | 2018-12-31 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.6312 |
| C_IC2 | 2019-01-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.3710 |
| C1 | 2019-12-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.2972 |
| C5 | 2019-12-31 | renewed | 0.3800 | 0.3500 | 0.7530 | 0.4302 |
| C7 | 2019-12-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.7670 |
| C2 | 2020-03-31 | churned **CHURNED** | 0.3200 | 0.5500 | 0.8560 | 0.8936 |
| C6 | 2020-03-31 | renewed | 0.3200 | 0.3500 | 0.7920 | 0.4643 |
| C8 | 2020-03-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1066 |
| C3 | 2020-06-30 | churned **CHURNED** | 0.3200 | 0.5500 | 0.8560 | 0.9704 |
| C9 | 2020-06-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.5378 |
| C4 | 2020-09-30 | renewed | 0.3200 | 0.5500 | 0.8560 | 0.2845 |
| C1 | 2020-12-30 | renewed | 0.2900 | 0.5500 | 0.8695 | 0.8047 |
| C5 | 2020-12-30 | renewed | 0.3500 | 0.3500 | 0.7725 | 0.7480 |
| C7 | 2020-12-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.4829 |
| C_IC3 | 2020-12-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.5941 |
| C6 | 2021-03-31 | renewed | 0.3500 | 0.3500 | 0.7725 | 0.5431 |
| C8 | 2021-03-31 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.4901 |
| C9 | 2021-06-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.5305 |
| C4 | 2021-09-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.4564 |
| C1 | 2021-12-30 | churned **CHURNED** | 0.3200 | 0.5500 | 0.8560 | 0.9691 |
| C5 | 2021-12-30 | churned **CHURNED** | 0.3500 | 0.3500 | 0.7725 | 0.8247 |
| C7 | 2021-12-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.1963 |
| C_IC3 | 2021-12-31 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.5838 |
| C6 | 2022-03-31 | renewed | 0.3200 | 0.3500 | 0.7920 | 0.1058 |
| C8 | 2022-03-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.5712 |
| C9 | 2022-06-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.5875 |
| C4 | 2022-09-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.8552 |
| C7 | 2022-12-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.0637 |
| C_IC3 | 2022-12-31 | churned **CHURNED** | 0.2300 | 0.5500 | 0.8965 | 0.8723 |
| C6 | 2023-03-31 | renewed | 0.2900 | 0.3500 | 0.8115 | 0.5155 |
| C8 | 2023-03-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.3785 |
| C9 | 2023-06-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.0307 |
| C4 | 2023-09-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.6095 |
| C7 | 2023-12-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1905 |
| C6 | 2024-03-30 | churned **CHURNED** | 0.3800 | 0.3500 | 0.7530 | 0.9632 |
| C8 | 2024-03-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.0592 |
| C9 | 2024-06-29 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.0025 |
| C4 | 2024-09-29 | churned **CHURNED** | 0.3200 | 0.5500 | 0.8560 | 0.9018 |
| C7 | 2024-12-29 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.4099 |
| C8 | 2025-03-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4808 |

## Churn Prediction Basis Risk

At each renewal the company estimated churn risk from observable signals (rate change %, customer tenure). The SIM used its bill-shock model (actual bill amount relative to customer-specific thresholds). The gap is epistemic: in crisis years the company sees a rate % while the SIM sees the household-level financial shock — the same failure mode that surprised real suppliers in 2021-22.

- **Average absolute error:** 211.6%
- **Average signed error:** +82.1% (over-estimates vs SIM)
- **Renewal events with estimates:** 49

| Year | Renewals | Avg error (signed) | Avg abs error |
|------|----------|--------------------|---------------|
| 2016 | 3 | -82.1% | 82.1% |
| 2017 | 3 | -93.7% | 93.7% |
| 2018 | 4 | +450.1% | 515.7% |
| 2019 | 4 | +380.7% | 519.3% |
| 2020 | 10 | +168.8% | 281.8% |
| 2021 | 8 | +31.5% | 140.7% |
| 2022 | 6 | -14.6% | 118.9% |
| 2023 | 5 | -64.5% | 95.5% |
| 2024 | 5 | -40.5% | 93.2% |
| 2025 | 1 | -100.0% | 100.0% |

Positive error = company over-estimated churn vs SIM. Negative error = company under-estimated (more dangerous — expected retentions that were actually at risk).

## Active vs Passive Renewal Split (Phase 33a)

~35% of domestic/SME customers actively choose a new fixed deal at term end. ~65% roll to SVT by inaction — they are inert: low rate sensitivity, ~5% churn base. Crisis years (2022) force all renewals passive (no fixed deals available).

- **Total renewal events:** 49
- **Active renewers:** 15 (31%) — mean company estimate 70.2%, abs error 354.1%
- **Passive SVT-rollers:** 34 (69%) — mean company estimate 8.1%, abs error 148.7%

| Year | Active | Passive | Active est | Passive est | Active abs err | Passive abs err |
|------|--------|---------|-----------|------------|---------------|----------------|
| 2016 | 0 | 3 | 0.0% | 5.2% | 0.0% | 82.1% |
| 2017 | 0 | 3 | 0.0% | 2.1% | 0.0% | 93.7% |
| 2018 | 2 | 2 | 57.9% | 49.9% | 88.4% | 943.1% |
| 2019 | 2 | 2 | 51.5% | 0.0% | 938.6% | 100.0% |
| 2020 | 5 | 5 | 77.6% | 0.5% | 465.1% | 98.6% |
| 2021 | 3 | 5 | 91.6% | 4.4% | 229.6% | 87.3% |
| 2022 | 0 | 6 | 0.0% | 21.6% | 0.0% | 118.9% |
| 2023 | 1 | 4 | 51.5% | 0.0% | 77.5% | 100.0% |
| 2024 | 2 | 3 | 60.0% | 0.0% | 83.1% | 100.0% |
| 2025 | 0 | 1 | 0.0% | 0.0% | 0.0% | 100.0% |

Passive renewers should show lower company estimates and lower SIM churn — high abs error for passive renewers indicates the passive model needs recalibration.

## SVT Comparative Pricing — Passive Renewers (Phase 39a)

Passive renewers roll to a new fixed deal by inaction. A rate above SVT creates latent churn risk: once the customer notices they're paying more than the cap, they switch. A rate below SVT signals loyalty value — the company is rewarding inertia.

- **Passive renewal events with SVT data:** 34
- **Above SVT (at-risk):** 6 (18%)
- **Below/at SVT (protected):** 28 (82%)
- **Mean rate vs SVT premium:** -11.2%

| Year | Passive Renewals | Above SVT | Avg Premium | Avg Fixed Rate (£/MWh) | Avg SVT (£/MWh) |
|------|-----------------|-----------|-------------|----------------------|----------------|
| 2016 | 3 | 0 (0%) | -6.3% | 131.1 | 140.0 |
| 2017 | 3 | 0 (0%) | -14.3% | 119.9 | 140.0 |
| 2018 | 2 | 1 (50%) | +0.2% | 152.9 | 152.5 |
| 2019 | 2 | 0 (0%) | -29.1% | 126.5 | 178.5 |
| 2020 | 5 | 0 (0%) | -26.4% | 130.0 | 176.9 |
| 2021 | 5 | 2 (40%) | +0.1% | 185.1 | 186.2 |
| 2022 | 6 | 3 (50%) | +6.4% | 294.4 | 336.8 |
| 2023 | 4 | 0 (0%) | -26.8% | 250.9 | 386.5 |
| 2024 | 3 | 0 (0%) | -12.5% | 207.8 | 237.9 |
| 2025 | 1 | 0 (0%) | -23.6% | 190.0 | 248.6 |

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
| 2020 | 21 | 11.8% | 33.8% |
| 2021 | 15 | 11.8% | 44.5% |
| 2022 | 12 | 10.4% | 23.2% |
| 2023 | 11 | 15.8% | 38.4% |
| 2024 | 10 | 7.5% | 18.0% |
| 2025 | 1 | 33.1% | 33.1% |

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
| 2016 | 3 | 0.82× | 0.82× |
| 2017 | 3 | 0.94× | 0.94× |
| 2018 | 4 | 5.16× ⚠ | 18.00× |
| 2019 | 4 | 5.19× ⚠ | 18.00× |
| 2020 | 10 | 2.82× ⚠ | 18.00× |
| 2021 | 8 | 1.41× | 3.75× |
| 2022 | 6 | 1.19× | 3.13× |
| 2023 | 5 | 0.95× | 1.00× |
| 2024 | 5 | 0.93× | 1.32× |
| 2025 | 1 | 1.00× | 1.00× |

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
| 2021 | 10 | 1.19% | 4.24% | MODERATE — asset adoption visible |
| 2022 | 8 | 2.34% | 7.47% | MODERATE — asset adoption visible |
| 2023 | 7 | 3.28% | 8.47% | HIGH drift — EV/asset cohort growing |
| 2024 | 7 | 4.05% | 15.56% | HIGH drift — EV/asset cohort growing |
| 2025 | 1 | 0.77% | 0.77% | Low — stable portfolio |

**Trend:** demand estimation error grew from **0.07%** in 2016 to **4.05%** mean / **15.56%** max in 2024. Root cause: new asset acquisitions (Phase B life events) create a temporary estimation gap until the company observes a full billing cycle.
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
| 2021 | 10 | 1.2% | 4.2% |
| 2022 | 8 | 2.3% | 7.5% |
| 2023 | 7 | 3.3% | 8.5% |
| 2024 | 7 | 4.0% | 15.6% |
| 2025 | 1 | 0.8% | 0.8% |

**79** of **79** renewals used prior billing records; **0** used SIM oracle fallback (first term, no billing history).

## EAC Drift Snapshot (Phase AI)

Per-customer consumption drift from company billing history (first renewal → latest renewal).
Drift > +15%: EV/ASHP acquisition. Drift < −15%: solar installation or efficiency upgrade.

**1 significant** (≥15%) | **1 moderate** (5–15%) | **10 stable** (<5%)

| Customer | Baseline kWh | Current kWh | Drift | Likely Cause |
|----------|-------------|-------------|-------|--------------|
| C4 | 4,131 | 3,365 | -19% | likely solar installation or significant efficiency upgrade |
| C7 | 13,179 | 12,155 | -8% | efficiency improvement or reduced occupancy |

**Portfolio demand trend:** 3 customers increasing / 9 decreasing (mean drift: -2.8%)

## Company CRM — Event Log

Dated artefacts of customer lifecycle events as seen by the company layer.
Total events: **7** (7 churn, 0 acquisition)

| Date | Event | Customer | Detail |
|------|-------|----------|--------|
| 2020-03-31 | CHURN | C2 | SIM p=0.32, company est=0.00 |
| 2020-06-30 | CHURN | C3 | SIM p=0.32, company est=0.00 |
| 2021-12-30 | CHURN | C1 | SIM p=0.32, company est=0.04 |
| 2021-12-30 | CHURN | C5 | SIM p=0.35, company est=0.85 |
| 2022-12-31 | CHURN | C_IC3 | SIM p=0.23, company est=0.95 |
| 2024-03-30 | CHURN | C6 | SIM p=0.38, company est=0.25 |
| 2024-09-29 | CHURN | C4 | SIM p=0.32, company est=0.00 |

**SIM ground truth vs company CRM reconciliation (year-end snapshots):**

| Year-end | SIM churned (cumulative) | CRM active | Match |
|----------|--------------------------|------------|-------|
| 2016-12-31 | 0 accounts | 0 active | yes |
| 2017-12-31 | 0 accounts | 0 active | yes |
| 2018-12-31 | 0 accounts | 0 active | yes |
| 2019-12-31 | 0 accounts | 0 active | yes |
| 2020-12-31 | 2 accounts | 0 active | yes |
| 2021-12-31 | 4 accounts | 0 active | yes |
| 2022-12-31 | 5 accounts | 0 active | yes |
| 2023-12-31 | 5 accounts | 0 active | yes |
| 2024-12-31 | 7 accounts | 0 active | yes |
| 2025-12-31 | 7 accounts | 0 active | yes |

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
| 2020 | 238,546 | 35,378 | 69,454 | 56,528 | 69,997 | 0 | 469,903 |  |
| 2021 | 246,433 | 14,993 | 71,336 | 49,618 | 62,765 | 41,382 | 486,527 |  |
| 2022 | 255,491 | -49,599 | 70,842 | 36,579 | 68,914 | 99,197 | 481,425 | ⬇ CfD REBATE |
| 2023 | 163,224 | 38,874 | 43,007 | 30,656 | 45,087 | 8,253 | 329,101 |  |
| 2024 | 184,667 | 65,949 | 43,659 | 41,265 | 49,554 | 1,199 | 386,292 |  |
| 2025 | 80,356 | 27,796 | 18,436 | 18,371 | 21,403 | 505 | 166,867 |  |
| **Total** | **1,437,172** | **174,333** | **387,982** | **276,351** | **389,551** | **150,537** | **2,815,925** | |

Total policy cost: £2,815,925 across all years. Net margin is after deducting this. Revenue side: tariff pass-through at term-start year's levy rate — basis risk arises when cross-year terms meet a different actual levy (notably 2022 CfD rebate).

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
| 2020 | 124,410 |  |
| 2021 | 123,233 |  |
| 2022 | 132,259 | BSUoS 100% demand-side from Apr 2022 |
| 2023 | 84,556 | RIIO-ED2 from Apr 2023 |
| 2024 | 86,427 |  |
| 2025 | 36,403 |  |
| **Total** | **743,608** | |

Total network cost: £743,608 across all years. Pass-through: tariff unit rate includes network cost at term-start year's rate; settlement deducts it — basis risk near-zero for annual contracts.

## Gas Policy Costs and Network Charges (Phase 30b)

Gas CCL: non-domestic only (domestic gas exempt). Gas network (GDN + NTS): all on unit rate.
GGL (Green Gas Levy): per-meter, from Nov 2021; tiny in £/MWh terms.

| Year | Gas Policy (CCL + GGL) £ | Gas Network £ | Total Gas Non-Commodity £ |
|------|--------------------------|---------------|--------------------------|
| 2016 | 0 | 479 | 479 |
| 2017 | 0 | 898 | 898 |
| 2018 | 0 | 905 | 905 |
| 2019 | 15,155 | 50,388 | 65,543 |
| 2020 | 19,468 | 47,112 | 66,580 |
| 2021 | 22,472 | 50,256 | 72,728 |
| 2022 | 26,961 | 54,204 | 81,165 |
| 2023 | 1 | 412 | 413 |
| 2024 | 0 | 302 | 302 |
| **Total** | **84,056** | **204,956** | **289,013** |

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
| 2020 | 120,808 | 43,845 | 76,963 | 19,468 | 47,112 | 9 | 9,745 | +8.1% |
| 2021 | 297,195 | 214,718 | 82,477 | 22,472 | 50,256 | 12 | 8,207 | +2.8% |
| 2022 | 586,414 | 496,405 | 90,009 | 26,961 | 54,204 | 33 | 2,837 | +0.5% |
| 2023 | 2,467 | 3,043 | -575 | 1 | 412 | 52 | -1,164 | -47.2% |
| 2024 | 1,322 | 560 | 762 | 0 | 302 | 23 | 397 | +30.0% |
| **Total** | **1,153,135** | **823,842** | **329,293** | **84,056** | **204,956** | **194** | **30,911** | **+2.7%** |

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
| 2021 | 2,983,493 | 11 | 271,227 | 2086.36× | OK |
| 2022 | 3,190,740 | 9 | 354,527 | 2727.13× | OK |
| 2023 | 3,492,184 | 8 | 436,523 | 3357.87× | OK |
| 2024 | 3,733,774 | 8 | 466,722 | 3590.17× | OK |
| 2025 | 3,783,451 | 6 | 630,575 | 4850.58× | OK |

End-state (2025): **£630,575/account** across 6 billing accounts — OK.

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
| 2021 | 4,362 | 5,235 | 2,983,493 | 569.9× | OK |
| 2022 | 8,498 | 10,197 | 3,190,740 | 312.9× | OK |
| 2023 | 3,196 | 3,835 | 3,492,184 | 910.6× | OK |
| 2024 | 1,721 | 2,065 | 3,733,774 | 1808.2× | OK |
| 2025 | 2,520 | 3,024 | 3,783,451 | 1251.2× | OK |




## Time-of-Use Tariff Utilization (C7-C9 HH Customers)

Peak windows: 07:00–11:00 and 16:00–20:00 weekdays (periods 15-22, 33-40).
Peak rate = 1.5× flat; off-peak = 0.786× flat (revenue-neutral at 30/70 split).
ToU Premium: actual revenue vs flat-rate equivalent — positive when actual peak % > 30% design.

| Customer | Total kWh | Peak kWh | Peak % | Peak Revenue | Off-peak Revenue | Avg Peak Rate | Avg Off-peak Rate | ToU Premium |
|----------|-----------|----------|--------|-------------|-----------------|--------------|------------------|-------------|
| C7 | 120,839 | 36,249 | 30.0% | £9,522.54 | £12,265.37 | £262.70/MWh | £145.00/MWh | +3.0% |
| C8 | 106,722 | 43,948 | 41.2% | £11,961.40 | £9,684.35 | £272.17/MWh | £154.27/MWh | +11.8% |
| C9 | 109,387 | 43,689 | 39.9% | £10,921.49 | £9,301.28 | £249.98/MWh | £141.58/MWh | +10.9% |

Total HH revenue: £63,656.43 vs flat equivalent £58,756.95 (+8.3% ToU premium)

## Bill Shock Summary (2016-2025)

Month-on-month billing increase ≥20%. Bill shocks elevate SIM churn probability
via the bill-shock history model. Crisis years (2021-22) see the largest spikes.

| Year | Events | Max Spike | Worst Customer |
|------|--------|-----------|----------------|
| 2016 | 31 | 100% | C8 (2016-10-31) |
| 2017 | 50 | 81% | C8 (2017-11-30) |
| 2018 | 60 | 85% | C4g (2018-10-31) |
| 2019 | 66 | 130% | C_IC1 (2019-03-31) |
| 2020 | 47 | 118% | C_IC2 (2020-03-31) |
| 2021 | 47 | 113% | C4g (2021-10-31) |
| 2022 | 55 | 134% | C4g (2022-10-31) |
| 2023 | 38 | 100% | C_IC2 (2023-06-30) |
| 2024 | 26 | 107% | C_IC2 (2024-07-31) |
| 2025 | 14 | 80% | C7 (2025-06-07) |

Total: **434** bill shock events across 10 years

**Top 10 worst single-period bill spikes:**

| Date | Customer | Spike | Eventually Churned? |
|------|----------|-------|---------------------|
| 2022-10-31 | C4g | +134% | no |
| 2019-03-31 | C_IC1 | +130% | no |
| 2020-03-31 | C_IC2 | +118% | no |
| 2021-10-31 | C4g | +113% | no |
| 2022-01-31 | C_IC3 | +108% | yes |
| 2024-07-31 | C_IC2 | +107% | no |
| 2016-10-31 | C8 | +100% | no |
| 2023-06-30 | C_IC2 | +100% | no |
| 2021-04-30 | C_IC2 | +93% | no |
| 2023-10-31 | C8 | +92% | no |

## Gas Renewal Pressure (Dual-Fuel Portfolio)

Company gas churn estimates at each gas leg renewal (Phase 14b).
Threshold for elevated risk: >20% company gas churn estimate.

| Year | Renewals | Mean Est | Max Est | Elevated Risk |
|------|----------|----------|---------|---------------|
| 2016 | 1 | 11% | 11% | 0 |
| 2017 | 4 | 16% | 23% | 2 ⚠ |
| 2018 | 4 | 17% | 23% | 2 ⚠ |
| 2019 | 4 | 0% | 0% | 0 |
| 2020 | 4 | 6% | 24% | 1 ⚠ |
| 2021 | 2 | 84% | 95% | 2 ⚠ |
| 2022 | 1 | 95% | 95% | 1 ⚠ |
| 2023 | 1 | 0% | 0% | 0 |

**Top elevated gas renewals (>20% estimated churn):**

| Date | Customer | Old Rate (£/MWh) | New Rate (£/MWh) | Est Churn |
|------|----------|-----------------|-----------------|-----------|
| 2021-12-31 | C_IC3g | £20.0 | £125.9 (+530%) | 95% |
| 2022-09-30 | C4g | £35.0 | £95.0 (+171%) | 95% |
| 2021-09-30 | C4g | £16.1 | £35.0 (+118%) | 74% |
| 2020-12-31 | C_IC3g | £15.4 | £20.0 (+29%) | 24% |
| 2018-10-01 | C4g | £26.1 | £33.6 (+29%) | 23% |

## Retention Strategy P&L

### Aggregate (2016-2025)

| Metric | Value |
|--------|-------|
| Offers made | 26 |
| Retained | 25 (96%) |
| Churned despite offer | 1 |
| Total offer cost (foregone margin) | £413,699.02 |
| Margin saved (retained customers' terms) | £2,282,815.45 |
| Wasted offer cost (churned anyway) | £512.78 |
| **Net ROI of retention strategy** | **£1,869,116.43** |
| Acquisition cost avoided (retained customers) | £4,000.00 |
| **Full economic ROI (margin + acq savings)** | **£1,873,116.43** |

Missed opportunities (churns with no offer): **6** (£47,477.00 expected margin lost without offer)
- **Blocked — uneconomical** (churn estimate above threshold but margin + acq_cost < discount cost): 1 (£43,346.20 margin foregone)
- **Below threshold** (churn estimate under 30%): 5 (£4,130.81 margin lost) — Phase 13c bill burden signal reduces this for high-spend SME customers

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2017 | 1 | 1 | £122.71 | £867.92 | £745.20 | £0.00 |
| 2018 | 3 | 3 | £24511.82 | £165693.15 | £141181.34 | £0.00 |
| 2019 | 4 | 4 | £43042.88 | £298543.40 | £255500.52 | £0.00 |
| 2020 | 6 | 6 | £47598.87 | £284072.45 | £236473.57 | £1139.33 |
| 2021 | 4 | 3 | £120893.47 | £424960.89 | £304067.42 | £-178.13 |
| 2022 | 2 | 2 | £73447.76 | £327284.70 | £253836.94 | £43346.20 |
| 2023 | 3 | 3 | £53775.05 | £377246.31 | £323471.26 | £0.00 |
| 2024 | 3 | 3 | £50306.47 | £404146.63 | £353840.17 | £3169.61 |

### Per-Offer Detail

| Date | Customer | Est. churn | Discount | Offer Cost | Expected Margin | Acq Saved | Net | Outcome |
|------|----------|-----------|---------|-----------|----------------|-----------|-----|---------|
| 2017-04-01 | C8 | 0.95 | 8% | £122.71 | £867.92 | £150 | £745.20 | retained |
| 2018-01-31 | C_IC1 | 0.95 | 8% | £24227.89 | £163704.65 | £150 | £139476.77 | retained |
| 2018-04-01 | C8 | 0.95 | 8% | £131.88 | £977.60 | £150 | £845.72 | retained |
| 2018-12-31 | C7 | 0.95 | 8% | £152.05 | £1010.90 | £150 | £858.85 | retained |
| 2019-01-31 | C_IC2 | 0.95 | 8% | £14841.81 | £101641.16 | £150 | £86799.35 | retained |
| 2019-03-02 | C_IC1 | 0.95 | 8% | £27950.99 | £194971.28 | £150 | £167020.29 | retained |
| 2019-04-01 | C8 | 0.95 | 8% | £127.34 | £893.79 | £150 | £766.44 | retained |
| 2019-07-01 | C9 | 0.95 | 8% | £122.74 | £1037.18 | £150 | £914.44 | retained |
| 2020-03-01 | C_IC2 | 0.95 | 8% | £10298.77 | £88443.61 | £150 | £78144.84 | retained |
| 2020-03-31 | C8 | 0.95 | 8% | £137.77 | £1263.03 | £150 | £1125.26 | retained |
| 2020-03-31 | C_IC1 | 0.95 | 8% | £19604.63 | £168458.66 | £150 | £148854.03 | retained |
| 2020-06-30 | C9 | 0.95 | 8% | £106.17 | £1018.47 | £150 | £912.30 | retained |
| 2020-12-30 | C7 | 0.95 | 8% | £140.30 | £1197.37 | £150 | £1057.07 | retained |
| 2020-12-31 | C_IC3 | 0.95 | 8% | £17311.23 | £23691.31 | £150 | £6380.08 | retained |
| 2021-03-31 | C_IC2 | 0.95 | 8% | £15320.99 | £105808.01 | £150 | £90487.02 | retained |
| 2021-04-30 | C_IC1 | 0.95 | 8% | £22356.55 | £156157.03 | £150 | £133800.48 | retained |
| 2021-12-30 | C5 | 0.85 | 8% | £512.78 | £2277.57 | £400 | £-512.78 | churned_despite_offer |
| 2021-12-31 | C_IC3 | 0.95 | 8% | £82703.16 | £162995.85 | £150 | £80292.69 | retained |
| 2022-04-30 | C_IC2 | 0.95 | 8% | £25060.47 | £95576.59 | £150 | £70516.12 | retained |
| 2022-05-30 | C_IC1 | 0.95 | 8% | £48387.28 | £231708.10 | £150 | £183320.82 | retained |
| 2023-03-31 | C6 | 0.51 | 5% | £397.90 | £3530.84 | £400 | £3132.94 | retained |
| 2023-05-30 | C_IC2 | 0.95 | 8% | £18664.02 | £129902.25 | £150 | £111238.22 | retained |
| 2023-06-29 | C_IC1 | 0.95 | 8% | £34713.13 | £243813.23 | £150 | £209100.10 | retained |
| 2024-03-30 | C8 | 0.95 | 8% | £178.37 | £1315.37 | £150 | £1137.00 | retained |
| 2024-06-28 | C_IC2 | 0.95 | 8% | £16369.46 | £133340.97 | £150 | £116971.50 | retained |
| 2024-07-28 | C_IC1 | 0.95 | 8% | £33758.63 | £269490.30 | £150 | £235731.67 | retained |

## Retention Durability

Post-retention survival: how long did retained customers stay before churning or reaching the simulation end?

| Customer | First retained | End of tenure | Post-retention months | Outcome |
|----------|---------------|--------------|----------------------|---------|
| C8 | 2017-04-01 | (window end) | 105 | active |
| C_IC1 | 2018-01-31 | (window end) | 95 | active |
| C7 | 2018-12-31 | (window end) | 84 | active |
| C_IC2 | 2019-01-31 | (window end) | 83 | active |
| C9 | 2019-07-01 | (window end) | 78 | active |
| C_IC3 | 2020-12-31 | 2022-12-31 | 24 | churned |
| C5 | 2021-12-30 | 2021-12-30 | 0 | churned |
| C6 | 2023-03-31 | 2024-03-30 | 12 | churned |

**Eventually churned (3/8)**: C_IC3, C5, C6 — avg 12 months post-retention before final churn.
**Still active (5/8)**: C8, C_IC1, C7, C_IC2, C9 — survived to simulation end.

## Enterprise Value Analysis (Phase 22a)

**Full-history EV:** £5,256,728.12 — anchored to all 10 years including crisis losses
**3yr-trailing EV:** £495,835.61 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

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
| 2020 | £153,032.39 |
| 2021 | £87,129.50 |
| 2022 | £304,766.07 |
| 2023 | £247,498.90 | ← trailing
| 2024 | £198,234.67 | ← trailing
| 2025 | £93,552.93 | ← trailing

**CLV by billing account:**

| Account | Full-history CLV | 3yr-trailing CLV |
|---------|----------------:|----------------:|
| C1 | £3,500.48 | — |
| C2 | £4,284.18 | — |
| C3 | £4,429.11 | — |
| C4 | £2,777.33 | £-827.53 |
| C5 | £7,657.72 | — |
| C6 | £14,735.14 | £2,888.34 |
| C7 | £6,234.13 | £23.24 |
| C8 | £6,866.87 | £158.75 |
| C9 | £7,204.17 | £902.27 |
| C_IC1 | £1,243,799.99 | £317,660.21 |
| C_IC2 | £762,079.25 | £167,137.14 |
| C_IC3 | £2,012,685.81 | — |
| C_IC4 | £1,180,473.94 | £7,893.19 |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C_IC1 | C_IC2 | C_IC3 | C_IC4 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £2,259.66 | — | — | — | £5,096.01 | — | £4,189.02 | — | — | — | — | — | — |
| 2017 | £1,866.40 | £3,448.52 | £3,029.81 | £2,742.22 | £3,908.13 | £7,630.18 | £2,786.39 | £4,112.60 | £3,653.20 | — | — | — | — |
| 2018 | £1,719.42 | £3,117.96 | £2,735.70 | £2,244.33 | £3,848.31 | £5,861.07 | £2,579.63 | £3,446.77 | £3,434.55 | £909,624.79 | — | — | — |
| 2019 | £1,697.80 | £2,636.08 | £2,692.56 | £2,508.16 | £4,077.50 | £6,421.57 | £2,893.06 | £3,508.69 | £3,243.91 | £815,715.03 | £542,363.74 | — | — |
| 2020 | £2,034.59 | £2,294.14 | £2,586.03 | £2,582.20 | £4,517.94 | £7,623.25 | £3,145.02 | £4,073.66 | £3,787.92 | £576,736.84 | £293,544.83 | £1,010,362.98 | £538,445.61 |
| 2021 | £2,042.23 | £2,356.99 | £2,458.40 | £2,267.90 | £4,261.36 | £7,289.32 | £3,423.59 | £4,066.88 | £3,661.53 | £532,150.82 | £314,544.40 | £970,054.62 | £561,837.14 |
| 2022 | £2,033.60 | £2,343.14 | £2,442.45 | £1,528.55 | £4,247.85 | £7,927.26 | £2,724.09 | £3,997.66 | £3,698.51 | £564,101.48 | £335,668.74 | £1,074,180.04 | £559,776.91 |
| 2023 | £1,954.13 | £2,269.64 | £2,559.82 | £1,168.62 | £4,442.82 | £9,613.75 | £2,703.63 | £4,225.35 | £4,056.59 | £631,410.35 | £364,308.54 | £1,096,950.89 | £561,852.97 |
| 2024 | £2,104.15 | £2,399.61 | £2,672.11 | £1,522.41 | £4,369.47 | £9,448.74 | £3,052.51 | £4,466.75 | £4,029.62 | £716,502.10 | £387,798.07 | £988,673.17 | £607,907.37 |
| 2025 | £2,042.23 | £2,611.51 | £2,588.30 | £1,534.18 | £4,473.71 | £8,893.04 | £3,249.86 | £4,156.97 | £3,811.24 | £714,425.52 | £417,525.43 | £1,045,832.66 | £679,568.52 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £4,187.97, range £57.03–£20,032.99.

- C1: cost to serve £414.25, net margin after CTS £2,311.07
- C1g: cost to serve £64.75, net margin after CTS £1,475.88
- C2: cost to serve £283.32, net margin after CTS £1,762.99
- C2g: cost to serve £57.03, net margin after CTS £1,356.44
- C3: cost to serve £292.52, net margin after CTS £2,096.31
- C3g: cost to serve £58.25, net margin after CTS £1,240.28
- C4: cost to serve £565.21, net margin after CTS £2,741.48
- C4g: cost to serve £216.57, net margin after CTS £1,127.40
- C5: cost to serve £871.49, net margin after CTS £8,478.91
- C6: cost to serve £1,355.14, net margin after CTS £21,695.98
- C7: cost to serve £954.89, net margin after CTS £9,855.71
- C8: cost to serve £938.35, net margin after CTS £11,487.59
- C9: cost to serve £896.17, net margin after CTS £11,791.58
- C_IC1: cost to serve £20,032.99, net margin after CTS £1,893,623.73
- C_IC2: cost to serve £11,417.43, net margin after CTS £912,368.86
- C_IC3: cost to serve £14,808.92, net margin after CTS £1,042,785.72
- C_IC3g: cost to serve £5,714.49, net margin after CTS £317,981.74
- C_IC4: cost to serve £16,441.72, net margin after CTS £1,090,243.56


## Margin Recovery Surcharges (Phase 16c + 19a)

Company applied 25 recovery surcharge(s) at renewal based on prior-term losses (3 gas). Avg surcharge: 15.1%.

| Customer | Commodity | Term start | Prior margin | Prior revenue | Surcharge | Rate before | Rate after |
|----------|-----------|------------|-------------|--------------|-----------|------------|-----------|
| C_IC1 | electricity | 2018-01-31 | £-5,651.81 | £10,420.08 | +20.0% | £112.24/MWh | £152.31/MWh |
| C5 | electricity | 2018-12-31 | £-204.31 | £2,322.51 | +3.8% | £148.68/MWh | £153.39/MWh |
| C_IC2 | electricity | 2019-01-31 | £-3,283.71 | £6,187.80 | +20.0% | £134.57/MWh | £185.71/MWh |
| C_IC1 | electricity | 2019-03-02 | £-7,215.97 | £10,069.00 | +20.0% | £128.22/MWh | £175.80/MWh |
| C_IC2 | electricity | 2020-03-01 | £-3,915.21 | £3,421.95 | +20.0% | £92.92/MWh | £128.22/MWh |
| C_IC1 | electricity | 2020-03-31 | £-8,072.70 | £6,326.95 | +20.0% | £91.12/MWh | £122.71/MWh |
| C_IC2 | electricity | 2021-03-31 | £-4,097.33 | £5,726.15 | +20.0% | £138.90/MWh | £191.68/MWh |
| C_IC1 | electricity | 2021-04-30 | £-7,770.53 | £14,511.74 | +20.0% | £113.97/MWh | £140.57/MWh |
| C4g | gas | 2021-09-30 | £-75.14 | £687.61 | +5.9% | £53.99/MWh | £59.13/MWh |
| C5 | electricity | 2021-12-30 | £-365.46 | £2,671.00 | +8.7% | £311.83/MWh | £342.69/MWh |
| C7 | electricity | 2021-12-30 | £-114.05 | £1,995.80 | +0.7% | £311.83/MWh | £317.57/MWh |
| C_IC3 | electricity | 2021-12-31 | £-26,911.89 | £443,752.95 | +1.1% | £224.03/MWh | £260.37/MWh |
| C_IC2 | electricity | 2022-04-30 | £-2,287.21 | £17,661.75 | +8.0% | £269.81/MWh | £317.27/MWh |
| C_IC1 | electricity | 2022-05-30 | £-6,202.10 | £22,384.38 | +20.0% | £239.42/MWh | £308.71/MWh |
| C4 | electricity | 2022-09-30 | £-220.41 | £906.59 | +19.3% | £404.86/MWh | £484.90/MWh |
| C4g | gas | 2022-09-30 | £-901.21 | £1,040.11 | +20.0% | £183.79/MWh | £250.92/MWh |
| C7 | electricity | 2022-12-30 | £-1,829.78 | £2,404.50 | +20.0% | £266.73/MWh | £318.59/MWh |
| C8 | electricity | 2023-03-31 | £-481.87 | £3,898.74 | +7.4% | £319.17/MWh | £361.07/MWh |
| C_IC2 | electricity | 2023-05-30 | £-4,337.22 | £7,055.33 | +20.0% | £171.46/MWh | £235.96/MWh |
| C_IC1 | electricity | 2023-06-29 | £-8,734.92 | £17,979.18 | +20.0% | £163.19/MWh | £220.50/MWh |
| C4 | electricity | 2023-09-30 | £-277.33 | £1,324.46 | +15.9% | £216.77/MWh | £249.34/MWh |
| C4g | gas | 2023-09-30 | £-1,950.48 | £2,732.11 | +20.0% | £47.83/MWh | £66.00/MWh |
| C7 | electricity | 2023-12-30 | £-445.92 | £3,990.91 | +6.2% | £242.22/MWh | £244.32/MWh |
| C_IC2 | electricity | 2024-06-28 | £-5,972.33 | £7,659.10 | +20.0% | £148.64/MWh | £205.12/MWh |
| C_IC1 | electricity | 2024-07-28 | £-10,717.78 | £14,454.77 | +20.0% | £154.38/MWh | £213.04/MWh |



## Portfolio Intelligence Pack (Phase AH)

Board-level synthesis of CRM and flexibility intelligence derived from observable operational data.

### 1. Retention Intelligence

- **Retention offers made:** 26
- **Offer acceptance rate:** 96% (25 retained / 1 churned despite offer)
- **Estimated margin protected:** £2,282,815.45
- **No-offer churns:** 6 total (0 blind miss / 1 deliberate pass)
- **Retention coverage rate:** 81% of at-risk renewals received an offer

### 2. Flexibility Revenue Intelligence

- No flexibility revenue data available.

### 3. Churn Pattern Analysis

- **Total lifetime churn events:** 7
- **Peak churn year:** 2020 (2 events)

### 4. Board Recommendations

1. **Crisis-year churn:** 3 churn events in 2021–2022. Maintain minimum hedge floor pre-crisis to preserve pricing stability and limit bill-shock churn.

## CRM Intelligence: Risk Triage (Final Year)

Latest renewal record per account. Risk bands: CRITICAL>=50% | HIGH>=30% | MEDIUM>=15% | LOW<15%.

| Account | Seg | Risk Band | Sim Churn | Co. Est. | Rate vs SVT | Lifetime Margin |
|---------|-----|-----------|-----------|----------|-------------|-----------------|
| C6 | SME | HIGH | 38% | 25% | -27.3% [competitive] | £21,695.98 |
| C8 | resi | HIGH | 38% | 0% | -23.6% [competitive] | £11,487.59 |
| C9 | resi | HIGH | 38% | 0% | -14.3% | £11,791.58 |
| C5 | SME | HIGH | 35% | 85% | +64.8% [overpriced] | £8,478.91 |
| C7 | resi | HIGH | 35% | 0% | -14.3% | £9,855.71 |
| C1 | resi | HIGH | 32% | 4% | -12.0% | £2,311.07 |
| C2 | resi | HIGH | 32% | 0% | -19.2% | £1,762.99 |
| C3 | resi | HIGH | 32% | 0% | -39.5% [competitive] | £2,096.31 |
| C4 | resi | HIGH | 32% | 0% | -9.0% | £2,741.48 |
| C_IC3 | I&C | MEDIUM | 23% | 95% | -66.2% [competitive] | £1,042,785.72 |
| C_IC1 | I&C | LOW | 5% | 95% | -0.1% | £1,893,623.73 |
| C_IC2 | I&C | LOW | 5% | 95% | +12.4% [overpriced] | £912,368.86 |

**Risk Band Summary (latest renewal):**
- CRITICAL (>=50%): 0 accounts
- HIGH (>=30%): 9 accounts
- MEDIUM (>=15%): 1 accounts
- LOW (<15%): 2 accounts
- Lifetime margin at risk (CRITICAL+HIGH): £72,221.62
- Overpriced vs SVT within HIGH/CRITICAL band: 1 account(s) -- rate shock risk compounds churn probability

**Company blind spot:** 7 HIGH/CRITICAL account(s) where company churn estimate was <10%.
  - C8: sim 38%, company est 0%
  - C9: sim 38%, company est 0%
  - C7: sim 35%, company est 0%
  - C1: sim 32%, company est 4%
  - C2: sim 32%, company est 0%

## Churn Root Cause Attribution

Per-churned-account analysis: pricing journey, rate-vs-SVT positioning, and company vs SIM churn estimate at the point of departure.

| Account | Seg | Churn Date | Tenure | Last Rate Shock | Rate vs SVT | Sim Risk | Co. Est. | Margin Lost |
|---------|-----|------------|--------|-----------------|-------------|----------|----------|-------------|
| C2 | resi | 2020-03-31 | 4.0yr | +15.0% | -19.2% | 32% | 0% | £1,762.99 |
| C3 | resi | 2020-06-30 | 4.0yr | -5.0% | -39.5% | 32% | 0% | £2,096.31 |
| C1 | resi | 2021-12-30 | 6.0yr | +1.1% | -12.0% | 32% | 4% | £2,311.07 |
| C5 | SME | 2021-12-30 | 6.0yr | +1.1% | +64.8% | 35% | 85% | £8,478.91 |
| C_IC3 | I&C | 2022-12-31 | 4.0yr | +4.1% | -66.2% | 23% | 95% | £1,042,785.72 |
| C6 | SME | 2024-03-30 | 8.0yr | -4.1% | -27.3% | 38% | 25% | £21,695.98 |
| C4 | resi | 2024-09-29 | 8.0yr | +3.8% | -9.0% | 32% | 0% | £2,741.48 |

**Root Cause Summary:**
- Total churned accounts: 7
- Lifetime margin lost: £1,081,872.47
- Average tenure at departure: 5.7 years
- Company blind misses (sim >=30%, co. est. <10%): 4 -- C2, C3, C1, C4
- Company-warned churns (co. est. >=20%): 3 -- C5, C_IC3, C6
- Crisis-era churns (2021-22): 3 -- absolute crisis price level, not rate-change delta, was the driver
- Overpriced vs SVT at departure: 1 account(s) -- rate shock risk was observable but unactioned

## Counterfactual Retention Value

What would company-initiated retention offers have been worth for the 6 accounts that churned without an offer? Calibrated from 26 actual offers (observed retention rate 96%).

| Account | Seg | Churn Date | Co. Est. | Term Margin | Disc Rate | Retention Cost | CF Net Benefit | Assessment |
|---------|-----|------------|----------|-------------|-----------|----------------|----------------|------------|
| C2 | resi | 2020-03-31 | 0% | £559.82 | 5% | £27.99 | £510.29 | MISSED OPP. |
| C3 | resi | 2020-06-30 | 0% | £579.51 | 5% | £28.98 | £528.25 | MISSED OPP. |
| C1 | resi | 2021-12-30 | 4% | £-178.13 | 5% | £0.00 | n/a | CORRECT PASS |
| C_IC3 | I&C | 2022-12-31 | 95% | £43,346.20 | 8% | £3,467.70 | £38,211.34 | MISSED OPP. |
| C6 | SME | 2024-03-30 | 25% | £2,700.74 | 8% | £216.06 | £2,380.80 | MISSED OPP. |
| C4 | resi | 2024-09-29 | 0% | £468.87 | 5% | £23.44 | £427.39 | MISSED OPP. |

**Counterfactual Summary:**
- No-offer churns assessed: 6
- Correct no-offer (net-neg ETM): 1 (C1)
- Missed opportunities (positive ETM, below detection): 5
- Total term margin foregone: £47,655.14
- Total retention cost (counterfactual): £3,764.16
- Net counterfactual benefit: £42,058.08 (at 96% retention probability)
- Root cause: company churn detection below threshold for all missed cases -- churn model underestimated bill-shock risk

## Pricing Basis Risk Attribution

Forward curve accuracy at each contract term. tariff_error_pct = (company_fwd - sim_fwd) / sim_fwd: positive = company over-estimated costs (higher than market); negative = company under-estimated (margin-at-risk).
Portfolio-wide mean error: +4.5%

| Year | Contracts | Mean Error | Max Abs | Over-priced | Under-priced | Assessment |
|------|-----------|------------|---------|-------------|--------------|------------|
| 2016 | 17 | +8.9% | 29.1% | 9 | 4 | moderate over |
| 2017 | 14 | +5.4% | 46.6% | 8 | 5 | moderate over |
| 2018 | 16 | -2.9% | 27.7% | 6 | 8 | on target |
| 2019 | 19 | +8.3% | 37.2% | 9 | 3 | moderate over |
| 2020 | 21 | -0.6% | 33.8% | 9 | 7 | on target |
| 2021 | 15 | +4.8% | 44.5% | 4 | 3 | on target |
| 2022 | 12 | -1.6% | 23.2% | 4 | 3 | on target |
| 2023 | 11 | +13.8% | 38.4% | 6 | 1 | moderate over |
| 2024 | 10 | +4.2% | 18.0% | 4 | 1 | on target |
| 2025 | 1 | +33.1% | 33.1% | 1 | 0 | HIGH OVER-PRICE |

**Basis Risk Summary:**
- Portfolio mean tariff error: +4.5%
- Worst over-pricing year: 2025 (+33.1%) -- company forward curve above settled market
- Post-crisis over-pricing years (2025): company locked in expensive crisis-era forwards after prices normalised -- mechanism that eroded real suppliers' margins 2022-24

## BSC Settlement Exposure

Elexon's Balancing and Settlement Code (BSC) requires suppliers to post credit cover to fund potential imbalance charges. Credit requirements track portfolio size and wholesale price levels. Peak daily settlement is the largest single-day settlement amount seen in that year.

| Year | BSC Credit Required | Peak Daily | % of Revenue |
|------|---------------------|------------|--------------|
| 2016 | £30 | £25 | 0.29% |
| 2017 | £559 | £466 | 0.24% |
| 2018 | £1,019 | £849 | 0.23% |
| 2019 | £1,851 | £1,543 | 0.15% |
| 2020 | £2,375 | £1,979 | 0.19% |
| 2021 | £5,235 | £4,362 | 0.30% |
| 2022 | £10,197 | £8,498 | 0.30% |
| 2023 | £3,835 | £3,196 | 0.29% |
| 2024 | £2,065 | £1,721 | 0.18% |
| 2025 | £3,024 | £2,520 | 0.59% << |

<< BSC credit above 0.4% of revenue (elevated operational cash tie-up)

**Peak BSC credit requirement:** 2022 at £10,197 (portfolio growth and 2021-22 price surge)
## Operational Unit Economics

Revenue, gross margin, and net margin per active customer account. The dramatic rise in 2022-23 reflects wholesale price crisis inflating all revenue and cost metrics simultaneously.

| Year | Active | Rev/cust | Gross/cust | Net/cust | Net % |
|------|--------|----------|------------|----------|-------|
| 2016 | 13 | £801 | £524 | £91 | 11.3% |
| 2017 | 14 | £16,735 | £8,803 | £2,183 | 13.0% |
| 2018 | 15 | £29,022 | £17,502 | £6,647 | 22.9% |
| 2019 | 17 | £70,486 | £41,296 | £13,404 | 19.0% |
| 2020 | 18 | £69,666 | £45,692 | £8,502 | 12.2% |
| 2021 | 14 | £125,522 | £56,036 | £6,224 | 5.0% << |
| 2022 | 11 | £311,730 | £95,256 | £27,706 | 8.9% |
| 2023 | 9 | £146,922 | £74,961 | £27,500 | 18.7% |
| 2024 | 9 | £127,131 | £75,919 | £22,026 | 17.3% |
| 2025 | 6 | £85,505 | £50,418 | £15,592 | 18.2% |

<< Net margin below 5% (below Ofgem FRA comfort threshold)

**Best year per customer:** 2022 at £27,706 net/customer
**Worst year per customer:** 2016 at £91 net/customer
## Customer Lifetime P&L by Commodity

Lifetime net margin per customer, split by electricity and gas. Loss-making accounts (marked *) warrant repricing review or exit.

| Customer | Elec net | Gas net | Total |
|----------|----------|---------|-------|
| C1 | £414 | — | £414 |
| C1g | — | £643 | £643 |
| C2 | £378 | — | £378 |
| C2g | — | £611 | £611 |
| C3 | £206 | — | £206 |
| C3g | — | £283 | £283 |
| C4 | £131 | — | £131 |
| C4g | — | £-2,030 | £-2,030 * |
| C5 | £-61 | — | £-61 * |
| C6 | £4,163 | — | £4,163 |
| C7 | £-1,449 | — | £-1,449 * |
| C8 | £1,230 | — | £1,230 |
| C9 | £1,473 | — | £1,473 |
| C_IC1 | £866,862 | — | £866,862 |
| C_IC2 | £440,451 | — | £440,451 |
| C_IC3 | £84,245 | — | £84,245 |
| C_IC3g | — | £31,404 | £31,404 |
| C_IC4 | £14,584 | — | £14,584 |
| **Total** | **£1,412,626** | **£30,911** | **£1,443,537** |

Loss-making accounts: C4g (£-2,030), C7 (£-1,449), C5 (£-61)
Gas loss-making: C4g (£-2,030)
Gas portfolio net: £30,911 (2.1% of total)

## Hedge Value-Add Analysis

Actual hedged net margin vs hypothetical spot-only (naked) net margin. Negative value-add indicates forward prices exceeded spot outturn — consistent with UK market backwardation in 2016-2021 and partial hedging in the crisis years.

| Year | Actual net | Naked net | Hedge value-add |
|------|-----------|-----------|-----------------|
| 2016 | £2,034 | £10,920 | £-8,885 |
| 2017 | £30,081 | £112,495 | £-82,414 |
| 2018 | £109,583 | £246,455 | £-136,872 |
| 2019 | £252,590 | £836,842 | £-584,252 |
| 2020 | £126,136 | £1,004,397 | £-878,260 |
| 2021 | £202,761 | £468,486 | £-265,724 |
| 2022 | £301,267 | £592,490 | £-291,222 |
| 2023 | £242,530 | £691,021 | £-448,490 |
| 2024 | £176,586 | £426,483 | £-249,897 |
| 2025 | £-30 | £119 | £-148 |
| **Total** | **£1,443,537** | **£4,389,708** | **£-2,946,170** |

Largest hedging cost: **2020** (£878,260 vs naked)
Smallest hedging cost: **2025** (£148 vs naked)
Conclusion: systematic forward hedging cost £2,946,170 over 10 years vs spot purchasing.

## Customer Service Quality

Ofgem benchmarks: bill clarity >0.82 (GREEN) / >0.80 (AMBER) / ≤0.80 (RED); complaint probability <5% (GREEN) / <6% (RED); bill shock <0.20% (GREEN) / <0.30% (AMBER) / ≥0.30% (RED).

| Year | Clarity | Complaint% | Shock% | Shock events | Bills | RAG |
|------|---------|------------|--------|--------------|-------|-----|
| 2016 | 0.829 G | 4.7% | 0.20% | 31 | 108 | GREEN |
| 2017 | 0.818 A | 4.7% | 0.17% | 50 | 168 | AMBER |
| 2018 | 0.810 A | 4.7% | 0.16% | 60 | 180 | AMBER |
| 2019 | 0.824 G | 4.7% | 0.17% | 66 | 204 | GREEN |
| 2020 | 0.830 G | 4.3% | 0.14% | 47 | 186 | GREEN |
| 2021 | 0.826 G | 4.6% | 0.16% | 47 | 168 | GREEN |
| 2022 | 0.794 R | 5.5% | 0.22% | 55 | 132 | RED ! |
| 2023 | 0.782 R | 5.2% | 0.19% | 38 | 108 | RED ! |
| 2024 | 0.783 R | 5.1% | 0.18% | 26 | 93 | RED ! |
| 2025 | 0.742 R | 6.3% | 0.25% | 14 | 36 | RED ! |

Worst clarity year: **2025** (0.742)
Highest complaint probability: **2025** (6.3%)
Worst bill shock: **2025** (0.25%)
RED years: 2022, 2023, 2024, 2025
AMBER years: 2017, 2018
Trend (last 2 years): DECLINING

## Portfolio VaR Trajectory and Treasury Evolution

Annual VaR ratio (committee trigger = 3.0) and year-end treasury balance.

| Year | VaR Ratio | Status | Treasury £ | Net Margin £ |
|------|-----------|--------|-----------|-------------|
| 2016 | 3.25 | ALERT | £2,467,424 | £1,178 |
| 2017 | 2.69 | WATCH | £2,497,718 | £30,566 |
| 2018 | — | — | £2,486,407 | £99,706 |
| 2019 | — | — | £2,606,406 | £227,872 |
| 2020 | — | — | £2,914,253 | £153,032 |
| 2021 | — | — | £2,983,493 | £87,129 |
| 2022 | 2.70 | WATCH | £3,190,740 | £304,766 |
| 2023 | 2.72 | WATCH | £3,492,184 | £247,499 |
| 2024 | — | — | £3,733,774 | £198,235 |
| 2025 | — | — | £3,783,451 | £93,553 |

**Peak VaR year: 2016 (ratio 3.25)**
**Treasury peak: 2025 (£3,783,451)**
**Treasury growth: £2,467,424 → £3,783,451 (+£1,316,027)**

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
| C2 | 2020-03 | 0.5% | £560 | below threshold |
| C3 | 2020-06 | 0.0% | £580 | below threshold |
| C1 | 2021-12 | 4.0% | -£178 | below threshold |
| C_IC3 | 2022-12 | 95.0% | £43,346 | uneconomical ⚑ |
| C6 | 2024-03 | 24.9% | £2,701 | below threshold ⚑ |
| C4 | 2024-09 | 0.0% | £469 | below threshold |

**High-risk no-offer events (≥10% churn): 2** — £46,047 margin at risk.

### Gas Renewal Risk — High-Churn Reprice Events (≥15% estimate)

| Customer | Term Start | Old Rate p/therm | New Rate p/therm | Churn Est |
|----------|-----------|-----------------|-----------------|----------|
| C2g | 2017-04 | 26.92 | 32.81 | 20.1% |
| C1g | 2017-12 | 26.25 | 33.49 | 22.6% |
| C3g | 2018-07 | 23.11 | 28.80 | 20.8% |
| C4g | 2018-10 | 26.10 | 33.61 | 23.3% |
| C_IC3g | 2020-12 | 15.44 | 19.98 | 23.7% |
| C4g | 2021-09 | 16.09 | 35.00 | 73.5% |
| C_IC3g | 2021-12 | 19.98 | 125.90 | 95.0% |
| C4g | 2022-09 | 35.00 | 95.00 | 95.0% |

**High-risk gas reprices: 8**

> ⚑ = customers with ≥15% churn estimate who received no retention offer.

## Retention Decision Economics

Per-offer cost, expected margin protected, and ROI for each retention intervention.

| Customer | Period | Retention Cost £ | Margin Protected £ | ROI | Discount % | Outcome |
|----------|--------|-----------------|-------------------|-----|------------|---------|
| C8 | 2017-04 | £123 | £868 | 7.1× | 8% | retained |
| C_IC1 | 2018-01 | £24,228 | £163,705 | 6.8× | 8% | retained |
| C8 | 2018-04 | £132 | £978 | 7.4× | 8% | retained |
| C7 | 2018-12 | £152 | £1,011 | 6.6× | 8% | retained |
| C_IC2 | 2019-01 | £14,842 | £101,641 | 6.8× | 8% | retained |
| C_IC1 | 2019-03 | £27,951 | £194,971 | 7.0× | 8% | retained |
| C8 | 2019-04 | £127 | £894 | 7.0× | 8% | retained |
| C9 | 2019-07 | £123 | £1,037 | 8.5× | 8% | retained |
| C_IC2 | 2020-03 | £10,299 | £88,444 | 8.6× | 8% | retained |
| C8 | 2020-03 | £138 | £1,263 | 9.2× | 8% | retained |
| C_IC1 | 2020-03 | £19,605 | £168,459 | 8.6× | 8% | retained |
| C9 | 2020-06 | £106 | £1,018 | 9.6× | 8% | retained |
| C7 | 2020-12 | £140 | £1,197 | 8.5× | 8% | retained |
| C_IC3 | 2020-12 | £17,311 | £23,691 | 1.4× | 8% | retained |
| C_IC2 | 2021-03 | £15,321 | £105,808 | 6.9× | 8% | retained |
| C_IC1 | 2021-04 | £22,357 | £156,157 | 7.0× | 8% | retained |
| C5 | 2021-12 | £513 | £2,278 | 4.4× | 8% | churned_despite_offer |
| C_IC3 | 2021-12 | £82,703 | £162,996 | 2.0× | 8% | retained |
| C_IC2 | 2022-04 | £25,060 | £95,577 | 3.8× | 8% | retained |
| C_IC1 | 2022-05 | £48,387 | £231,708 | 4.8× | 8% | retained |
| C6 | 2023-03 | £398 | £3,531 | 8.9× | 5% | retained |
| C_IC2 | 2023-05 | £18,664 | £129,902 | 7.0× | 8% | retained |
| C_IC1 | 2023-06 | £34,713 | £243,813 | 7.0× | 8% | retained |
| C8 | 2024-03 | £178 | £1,315 | 7.4× | 8% | retained |
| C_IC2 | 2024-06 | £16,369 | £133,341 | 8.1× | 8% | retained |
| C_IC1 | 2024-07 | £33,759 | £269,490 | 8.0× | 8% | retained |

**Total retention spend: £413,699** | **Total margin protected: £2,285,093**
**Portfolio retention ROI: 5.5×** | **Retained: 25/26**
**Best ROI intervention: C9 2020-06 (9.6×)**

> ROI = expected remaining-term margin ÷ retention cost (discount given).
> Churn probability weighted; 95% churn estimate used for I&C renewal trigger.

## Gas Exit Decision Analysis

Three-scenario P&L impact for the board (dual-fuel portfolio lifetime figures).

| Scenario | Net Margin £ | vs Status Quo |
|----------|-------------|--------------|
| Status Quo (hold gas) | £116,285 | — |
| Exit Gas (with churn risk) | £51,450 | -£64,835 |
| Reprice to Breakeven | £118,314 | +£2,030 |

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
| 2020 | 81.2% | 0.0% | 96.0% | 1 | 13 |
| 2021 | 82.7% | 0.0% | 97.0% | 1 | 10 |
| 2022 | 93.1% | 85.0% | 97.4% | — | 9 |
| 2023 | 89.8% | 85.0% | 95.0% | — | 9 |
| 2024 | 88.1% | 85.0% | 91.1% | — | 6 |
| 2025 | 89.4% | 89.4% | 89.4% | — | 1 |

**Lowest portfolio hedge fraction: 2020 (81.2%)** — risk erosion from regime-change blindness.
**Naked positions first appear in 2019** — unhedged accounts expose portfolio to spot price swings.

> Regime-change blindness: the sim converged toward lower hedging during calm 2016-2020,
> mirroring the strategy that destroyed real UK suppliers entering the 2021-22 crisis.

## Risk Committee Intervention Pattern

Annual risk committee wake-ups (triggered when portfolio VaR exceeds threshold).

| Year | Wake-ups | Customer Adjustments | Avg Customers/Event | Max VaR Stressed £ |
|------|----------|---------------------|--------------------|--------------------|
| 2016 | 13 | 13 | 1.0 | £9 |
| 2017 | 12 | 33 | 2.8 | £401 |
| 2022 | 9 | 52 | 5.8 | £20,830 |
| 2023 | 4 | 25 | 6.2 | £48,770 |

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
| 2020 | £2,375 | £56,528 | — | £69,454 | £47,112 |
| 2021 | £5,235 | £49,618 | £41,382 | £71,336 | £50,256 |
| 2022 | £10,197 | £36,579 | £99,197 | £70,842 | £54,204 |
| 2023 | £3,835 | £30,656 | £8,253 | £43,007 | £412 |
| 2024 | £2,065 | £41,265 | £1,199 | £43,659 | £302 |
| 2025 | £3,024 | £18,371 | £505 | £18,436 | £0 |

**Peak BSC credit obligation: 2022 (£10,197)** — driven by portfolio volume growth and crisis price levels.
**Mutualization levy first appeared in 2016** — reflects supplier failure costs passed to remaining suppliers via BSC.

> BSC credit = Elexon-mandated deposit against settlement exposure. Scales with volume × price.
> Mutualization = recoverable defaults from failed suppliers in settlement.

## Customer Cohort Revenue Analysis

Lifetime P&L by year-of-acquisition cohort (all years to simulation end).

| Cohort | Customers | Total Revenue £ | Gross Margin £ | Net Margin £ | Rev/Customer £ |
|--------|-----------|----------------|---------------|-------------|----------------|
| 2016 | 13 | £154,206 | £84,390 | £5,992 | £11,862 |
| 2017 | 1 | £3,162,975 | £1,913,657 | £866,862 | £3,162,975 |
| 2018 | 1 | £1,539,850 | £923,786 | £440,451 | £1,539,850 |
| 2019 | 2 | £3,696,452 | £1,381,291 | £115,649 | £1,848,226 |
| 2020 | 1 | £2,744,639 | £1,106,685 | £14,584 | £2,744,639 |

**Best revenue/customer cohort: 2017 (£3,162,975/customer)**
**Best net margin cohort: 2017 (£866,862)**

> Note: Gas customer legs excluded from electricity metrics; cohort = year of first contract.

## CfD Levy, Bad Debt & Treasury Drawdowns

Contracts for Difference levy (negative = credit to supplier in high-price periods).

| Year | CfD Levy £ | RO Levy £ | Bad Debt £ | Treasury Drawdowns | Bills |
|------|-----------|----------|-----------|-------------------|-------|
| 2016 | +£7 | £1,162 | £167 | — | 108 |
| 2017 | +£2,707 | £37,159 | £1,375 | — | 168 |
| 2018 | +£9,875 | £65,510 | £2,385 | — | 180 |
| 2019 | +£28,353 | £164,625 | £6,207 | — | 204 |
| 2020 | +£35,378 | £238,546 | £6,434 | — | 186 |
| 2021 | +£14,993 | £246,433 | £9,166 | — | 168 |
| 2022 | -£49,599 CREDIT | £255,491 | £35,335 | 1 | 132 |
| 2023 | +£38,874 | £163,224 | £7,592 | — | 108 |
| 2024 | +£65,949 | £184,667 | £6,116 | — | 93 |
| 2025 | +£27,796 | £80,356 | £2,659 | — | 36 |

**CfD turned CREDIT in 2022: -£49,599 (high wholesale → CfD generators repay system)**
**Treasury drawdown years: 2022** (credit facility used)
**Peak bad debt year: 2022 (£35,335)**

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
| 2020 | £5,218 | £990 | £4,236 | £736,031 | £75,972 | £822,448 |
| 2021 | £4,684 | £222 | £4,522 | £692,818 | £82,255 | £784,501 |
| 2022 | £2,652 | -£834 | £3,916 | £951,242 | £90,843 | £1,047,819 |
| 2023 | £5,259 | -£575 | £4,731 | £665,237 | £0 | £674,652 |
| 2024 | £6,718 | £762 | £1,611 | £674,181 | £0 | £683,272 |
| 2025 | £2,755 | £0 | £0 | £299,752 | £0 | £302,508 |

**Best gross margin year: 2022 (£1,047,819)** | **Worst: 2016 (£6,814)**
**Loss-making: resi gas in 2022 (£-834)**
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
| 2020 | 10 | -30.1% | 0/10 | -68.6% | +-17.6% |
| 2021 | 8 | +9.8% | 4/8 | -12.0% | +64.8% |
| 2022 | 6 | +6.4% | 3/6 | -66.2% | +100.1% |
| 2023 | 5 | -31.1% | 0/5 | -60.5% | +-10.8% |
| 2024 | 5 | -18.4% | 0/5 | -27.3% | +-9.0% |
| 2025 | 1 | -23.6% | 0/1 | -23.6% | +-23.6% |

**Best headroom year: 2023 (avg 31.1% below SVT)**
**Largest above-SVT year: 2021** (4/8 terms above — note: I&C customers exempt from SVT cap)

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
| 2021 | £2,983,493 | AMBER | AMBER | GREEN | AMBER | RED |
| 2022 | £3,190,740 | AMBER | AMBER | GREEN | AMBER | RED |
| 2023 | £3,492,184 | AMBER | AMBER | GREEN | AMBER | RED |
| 2024 | £3,733,774 | AMBER | AMBER | GREEN | AMBER | RED |
| 2025 | £3,783,451 | AMBER | AMBER | GREEN | AMBER | RED |

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
| 2020 | 18 | 41.5% | £104,845 | £45,784 | 2.05% |
| 2021 | 14 | 30.0% | £174,184 | £56,137 | 1.95% |
| 2022 | 11 | 22.5% | £384,468 | £95,358 | 1.99% |
| 2023 | 9 | 34.5% | £200,193 | £75,044 | 2.62% |
| 2024 | 9 | 40.4% | £176,528 | £75,918 | 2.12% |
| 2025 | 6 | 43.0% | £108,711 | £50,461 | 2.96% |

**Best EBIT%: 2016 (45.2%)** | **Worst EBIT%: 2022 (22.5%)**
**Peak revenue/customer: 2022 (£384,468)**

> Note: Revenue/customer driven by customer mix (I&C customers 10-100× resi volumes).

## Churn Prediction Calibration

How well the company estimated churn probability versus actual simulation outcomes.

| Customer | Date | Sim Probability | Company Estimate | Delta | Verdict |
|----------|------|----------------|-----------------|-------|---------|
| C2 | 2020-03 | 32.0% | 0.5% | -31.5pp | UNDERESTIMATED |
| C3 | 2020-06 | 32.0% | 0.0% | -32.0pp | UNDERESTIMATED |
| C1 | 2021-12 | 32.0% | 4.0% | -28.0pp | UNDERESTIMATED |
| C5 | 2021-12 | 35.0% | 84.9% | +49.9pp | OVERESTIMATED |
| C_IC3 | 2022-12 | 23.0% | 95.0% | +72.0pp | OVERESTIMATED |
| C6 | 2024-03 | 38.0% | 24.9% | -13.1pp | UNDERESTIMATED |
| C4 | 2024-09 | 32.0% | 0.0% | -32.0pp | UNDERESTIMATED |

**Outcomes: 5 underestimated / 0 accurate / 2 overestimated**
**Mean absolute error: 36.9pp**
**Systematic bias: company consistently UNDER-predicted churn risk.**

> Company churn estimates derived from company-observable signals (bill shock,
> margin feedback, renewal history) without access to the simulation's internal
> churn parameters — epistemic gap is expected and realistic for a small supplier.

## Tariff Estimation Accuracy

Mean and maximum absolute error between company tariff estimates and actual outturn.

| Year | Observations | Mean Abs Error | Max Abs Error | Accuracy |
|------|-------------|---------------|--------------|----------|
| 2016 | 17 | 15.1% | 29.1% | POOR |
| 2017 | 14 | 16.6% | 46.6% | POOR |
| 2018 | 16 | 12.1% | 27.7% | MODERATE |
| 2019 | 19 | 11.0% | 37.2% | MODERATE |
| 2020 | 21 | 11.8% | 33.8% | MODERATE |
| 2021 | 15 | 11.8% | 44.5% | MODERATE |
| 2022 | 12 | 10.4% | 23.2% | MODERATE |
| 2023 | 11 | 15.8% | 38.4% | POOR |
| 2024 | 10 | 7.5% | 18.0% | GOOD |
| 2025 | 1 | 33.1% | 33.1% | POOR |

**Best accuracy year (n≥5): 2024 (7.5% mean error)**
**Worst accuracy year (n≥5): 2017 (16.6% mean error)**

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
| 2020 | 17 | +4.3 | 9 | 8 | 2 |
| 2021 | 12 | +12.3 | 12 | 0 | 6 |
| 2022 | 9 | +19.2 | 8 | 1 | 5 |
| 2023 | 8 | +12.8 | 6 | 2 | 6 |
| 2024 | 7 | +10.8 | 5 | 2 | 2 |
| 2025 | 1 | -4.1 | 0 | 1 | 0 |

**Total adjustments 2016-2025: 100** | **Peak avg adjustment: 2022 (+19.2 £/MWh)**
**Emergency reprices: 25 total** (6 in 2021)

> Emergency reprices triggered when recent margin dropped below cost floor.
> Normal adjustments from rolling margin feedback; £/MWh delta versus prior contracted rate.

## Portfolio CLV Evolution

Estimated forward lifetime value of active billing accounts at each year-end.

| Year | Accounts | Total CLV £ | Avg CLV £ | Δ CLV £ |
|------|----------|-------------|-----------|---------|
| 2016 | 3 | £11,545 | £3,848 | — |
| 2017 | 9 | £33,177 | £3,686 | +£21,633 |
| 2018 | 10 | £938,613 | £93,861 | +£905,435 |
| 2019 | 11 | £1,387,758 | £126,160 | +£449,146 |
| 2020 | 13 | £2,451,735 | £188,595 | +£1,063,977 |
| 2021 | 13 | £2,410,415 | £185,417 | £-41,320 |
| 2022 | 13 | £2,564,670 | £197,282 | +£154,255 |
| 2023 | 13 | £2,687,517 | £206,732 | +£122,847 |
| 2024 | 13 | £2,734,946 | £210,380 | +£47,429 |
| 2025 | 13 | £2,890,713 | £222,363 | +£155,767 |

**Peak portfolio CLV: 2025 (£2,890,713)** | **Earliest/lowest: 2016 (£11,545)**
**Largest YoY gain: 2020 (+£1,063,977)**
**Largest YoY fall: 2021 (£-41,320)**

> Note: CLV snapshots are forward estimates at year-end based on remaining contract tenure and expected margins at that point in time.

## Gross Margin Bridge (Year-over-Year Attribution)

Annual change in gross margin decomposed into revenue and cost drivers.

| Year | Revenue £ | Wholesale £ | Non-Commodity £ | Gross Margin £ | GM% | ΔRevenue £ | ΔWholesale £ | ΔNon-Comm £ | ΔGM £ |
|------|-----------|-------------|-----------------|----------------|-----|------------|--------------|-------------|-------|
| 2016 | £15,354.61 | £3,596.53 | £3,892.24 | £7,865.84 | 51.2% | — | — | — | — |
| 2017 | £348,630.52 | £111,056.98 | £112,782.23 | £124,791.30 | 35.8% | +£333,275.90 | +£107,460.46 | +£108,889.99 | +£116,925.46 |
| 2018 | £600,953.01 | £172,802.28 | £163,976.80 | £264,173.93 | 44.0% | +£252,322.49 | +£61,745.30 | +£51,194.57 | +£139,382.63 |
| 2019 | £1,645,452.10 | £496,239.95 | £445,337.04 | £703,875.12 | 42.8% | +£1,044,499.09 | +£323,437.66 | +£281,360.24 | +£439,701.19 |
| 2020 | £1,887,212.43 | £431,591.09 | £631,516.48 | £824,104.87 | 43.7% | +£241,760.32 | £-64,648.86 | +£186,179.44 | +£120,229.75 |
| 2021 | £2,438,581.89 | £972,966.99 | £679,703.43 | £785,911.46 | 32.2% | +£551,369.46 | +£541,375.91 | +£48,186.96 | £-38,193.41 |
| 2022 | £4,229,152.66 | £2,381,271.82 | £798,941.22 | £1,048,939.63 | 24.8% | +£1,790,570.78 | +£1,408,304.83 | +£119,237.79 | +£263,028.17 |
| 2023 | £1,801,739.61 | £647,884.02 | £478,461.98 | £675,393.61 | 37.5% | £-2,427,413.06 | £-1,733,387.79 | £-320,479.24 | £-373,546.02 |
| 2024 | £1,588,749.06 | £461,696.61 | £443,786.27 | £683,266.18 | 43.0% | £-212,990.54 | £-186,187.41 | £-34,675.71 | +£7,872.58 |
| 2025 | £652,267.61 | £210,523.16 | £138,980.98 | £302,763.47 | 46.4% | £-936,481.46 | £-251,173.45 | £-304,805.29 | £-380,502.72 |

**Best GM year: 2016 (51.2%)** | **Worst GM year: 2022 (24.8%)**

> Note: Non-commodity costs include network (DUoS/TNUoS), policy levies (RO/CfD/CCL/CM/FiT), and mutualization.

## Risk Committee Activity (2016-2025)

Committee wake-up sessions: triggered when VaR stress ratio exceeds mandate threshold.

| Year | Sessions | Peak VaR (current) £ | Peak VaR (stressed) £ | Accounts touched |
|------|----------|----------------------|----------------------|-----------------|
| 2016 | 13 | £28 | £9 | 1 |
| 2017 | 12 | £1,005 | £401 | 3 |
| 2022 | 9 | £56,293 | £20,830 | 7 |
| 2023 | 4 | £127,898 | £48,770 | 7 |

**Total sessions 2016-2025: 38** | Busiest year: 2016 (13 sessions)
Peak VaR observed: 2023 at £127,898 | Unique accounts ever adjusted: 10

**Most frequently adjusted accounts:**
- C1: 22 sessions
- C7: 19 sessions
- C5: 12 sessions
- C8: 12 sessions
- C_IC1: 12 sessions

> Risk committee wake-ups are documented in `docs/observability/run_history.json`.

## Customer Strategic Value Matrix

2x2 matrix: CLV (above/below median) × Churn probability (above/below median).
Median CLV: £7,204.17 | Median churn: 32% | Total portfolio CLV: £5,256,728.12

### PROTECT (High CLV, Low Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C_IC3 | £2,012,685.81 | 23% | 9.4 periods |
| C_IC1 | £1,243,799.99 | 8% | 7.8 periods |
| C_IC4 | £1,180,473.94 | 14% | 8.2 periods |
| C_IC2 | £762,079.25 | 11% | 9.2 periods |

Quadrant CLV: £5,199,038.98 (99% of portfolio)

### CRITICAL (High CLV, High Churn — priority intervention)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C6 | £14,735.14 | 38% | 8.2 periods |
| C5 | £7,657.72 | 35% | 8.2 periods |
| C9 | £7,204.17 | 38% | 8.4 periods |

Quadrant CLV: £29,597.03 (1% of portfolio)

### EXIT (Low CLV, High Churn)

| Account | CLV | Churn Prob | Expected Life |
|---------|-----|------------|--------------|
| C8 | £6,866.87 | 38% | 8.1 periods |
| C7 | £6,234.13 | 35% | 8.8 periods |
| C3 | £4,429.11 | 32% | 7.9 periods |
| C2 | £4,284.18 | 32% | 8.4 periods |
| C1 | £3,500.48 | 32% | 8.5 periods |
| C4 | £2,777.33 | 32% | 9.0 periods |

Quadrant CLV: £28,092.11 (1% of portfolio)

**Board action: CRITICAL quadrant has 3 account(s). High CLV at risk from elevated churn probability. Immediate retention offers recommended.**

## Customer Experience & Service Quality

| Year | Billing Clarity | Complaint Prob | Acq Attempts | Acq Wins | Flag |
|------|----------------|---------------|-------------|---------|------|
| 2016 | 0.829 | 0.047 | 0 | 0 |  |
| 2017 | 0.818 | 0.047 | 0 | 0 |  |
| 2018 | 0.810 | 0.047 | 0 | 0 |  |
| 2019 | 0.824 | 0.047 | 0 | 0 |  |
| 2020 | 0.830 | 0.043 | 2 | 0 |  |
| 2021 | 0.826 | 0.046 | 2 | 0 |  |
| 2022 | 0.794 | 0.055 | 0 | 0 | **LOW CLARITY** |
| 2023 | 0.782 | 0.052 | 0 | 0 | **LOW CLARITY** |
| 2024 | 0.783 | 0.051 | 2 | 0 | **LOW CLARITY** |
| 2025 | 0.742 | 0.063 | 0 | 0 | **LOW CLARITY** |

**Overall service quality:** 90.4% | **Average billing clarity:** 0.812 | **Average complaint probability:** 0.048

**Acquisition performance:** 6 attempts, 0 wins (0% win rate). No new customers acquired — cap-constrained gate blocked resi acquisition 2021-2023 (negative projected margin).

**Lowest clarity: 2025** (0.742) — crisis complexity (multiple tariff changes, bill shock events) degraded statement clarity.

## Bill Shock Analysis

Bill shock events occur when a customer's bill increases >20% vs the prior bill.
Regulatory context: Ofgem monitors bill shock as a consumer harm indicator.

| Year | Avg Shock % | Events | Bills | Shock Rate | Flag |
|------|------------|--------|-------|------------|------|
| 2016 | 19.7% | 31 | 108 | 29% |  |
| 2017 | 16.5% | 50 | 168 | 30% |  |
| 2018 | 16.0% | 60 | 180 | 33% |  |
| 2019 | 17.1% | 66 | 204 | 32% |  |
| 2020 | 14.4% | 47 | 186 | 25% |  |
| 2021 | 16.1% | 47 | 168 | 28% |  |
| 2022 | 22.0% | 55 | 132 | 42% | ELEVATED |
| 2023 | 18.8% | 38 | 108 | 35% |  |
| 2024 | 17.6% | 26 | 93 | 28% |  |
| 2025 | 24.6% | 14 | 36 | 39% | ELEVATED |

**Crisis peak: 2025** — 24.6% average shock. Energy crisis drove wholesale costs above locked tariff rates,
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
| 2020 | £238,546.49 | £35,377.66 | £69,454.47 | £56,527.62 | £69,996.68 | £469,902.92 | £124,410.46 |
| 2021 | £246,432.58 | £14,993.40 | £71,335.52 | £49,618.32 | £62,765.47 | £486,527.09 | £123,232.78 |
| 2022 | £255,490.50 | **£-49,598.74** | £70,842.27 | £36,579.42 | £68,913.70 | £481,424.63 | £132,258.75 |
| 2023 | £163,223.52 | £38,873.74 | £43,007.33 | £30,656.28 | £45,086.73 | £329,100.80 | £84,555.60 |
| 2024 | £184,666.63 | £65,948.54 | £43,658.65 | £41,265.13 | £49,554.26 | £386,292.28 | £86,427.11 |
| 2025 | £80,356.27 | £27,796.20 | £18,435.76 | £18,370.76 | £21,403.07 | £166,867.44 | £36,403.32 |

**CfD rebate in 2022:** Contracts for Difference (CfD) generators are paid
the difference between strike price and reference price. When spot > strike (2022 crisis),
the mechanism reverses — generators pay back, creating a negative levy for suppliers.

Policy costs: £1,701.01 (2016) → £166,867.44 (2025). CAGR: 66.5%.

## Electricity vs Gas P&L Split

Year-by-year net margin by fuel. Gas became structurally loss-making from 2021.

| Year | Elec Net | Gas Net | Elec Rev | Gas Rev | Gas Share of Rev | Gas Profitable |
|------|----------|---------|----------|---------|-----------------|---------------|
| 2016 | £881.72 | £296.53 | £9,021.95 | £1,388.28 | 13.3% | YES |
| 2017 | £30,102.71 | £463.34 | £231,632.96 | £2,660.42 | 1.1% | YES |
| 2018 | £99,331.51 | £374.66 | £432,208.83 | £3,113.94 | 0.7% | YES |
| 2019 | £218,118.22 | £9,754.19 | £1,060,498.38 | £137,766.14 | 11.5% | YES |
| 2020 | £143,287.45 | £9,744.94 | £1,133,173.61 | £120,807.62 | 9.6% | YES |
| 2021 | £78,922.24 | £8,207.26 | £1,460,116.20 | £297,194.89 | 16.9% | YES |
| 2022 | £301,928.59 | £2,837.49 | £2,842,619.37 | £586,413.67 | 17.1% | YES |
| 2023 | £248,663.22 | £-1,164.32 | £1,319,828.45 | £2,467.34 | 0.2% | **NO** |
| 2024 | £197,837.75 | £396.91 | £1,142,857.09 | £1,322.40 | 0.1% | YES |
| 2025 | £93,552.93 | £0.00 | £513,030.67 | £0.00 | 0.0% | YES |

**Gas has been loss-making since 2023** (1 consecutive years). Electricity cross-subsidises gas supply.

## Gas Supply Exit Decision Analysis (Phase AR/AS)

Models three strategic scenarios for the board regarding gas supply legs.
Inputs: company billing records (per_cid_comm_pnl). Gas capital = hedge cost applied to gas leg.

### Scenario Comparison (Dual-Fuel Portfolio Only)

| Scenario | Portfolio Net | vs Status Quo | Action |
|----------|--------------|---------------|--------|
| STATUS_QUO | £116,284.54 | — | Current strategy |
| EXIT_GAS | £51,449.91 | £-64,834.63 | Remove gas; model elec churn risk |
| REPRICE_GAS | £118,314.39 | £2,029.86 | Raise gas tariff to break-even |

**Recommended action: REPRICE_GAS**

### Loss-Making Gas Accounts

| Account | Gas Net | Gas ROC | Revenue Uplift Needed |
|---------|---------|---------|----------------------|
| C4g | £-2,029.86 | -14.02x | +19.6% |

**Accretive gas accounts:** C1g (£642.69), C2g (£611.34), C3g (£282.80), C_IC3g (£31,404.02) — these gas legs support customer retention without capital destruction.

**Board Decision:**
- Exit gas: I&C customers at 40% electricity churn risk when gas removed (relationship loss)
- Reprice gas: increases customer cost but eliminates capital destruction
- Status quo: unsustainable — gas legs destroying £30911 in net value

## Segment Capital Efficiency (Return-on-Capital)

Lifetime net margin and capital deployed per segment.
ROC = lifetime net / lifetime capital. ROC < 0 = capital destroyer.

| Segment | Lifetime Gross | Capital Deployed | Lifetime Net | ROC | Signal |
|---------|---------------|------------------|--------------|-----|--------|
| I&C electricity | £5,001,722.94 | £39,258.39 | £1,406,141.71 | 35.8x | Strong |
| I&C gas | £323,696.23 | £0.00 | £31,404.02 | 0.0x | Low return |
| SME electricity | £32,401.52 | £345.83 | £4,101.38 | 11.9x | Moderate |
| resi electricity | £46,391.45 | £490.84 | £2,383.25 | 4.9x | Low return |
| resi gas | £5,596.61 | £194.14 | £-493.03 | -2.5x | CAPITAL DESTROYER |

## Portfolio Concentration Risk

Revenue concentration analysis across 18 margin-positive accounts. Herfindahl-Hirschman Index (HHI): **2388** — MODERATE (1,500-2,500).

**Segment Margin Share:**
- I&C: £5,257,003.62 (98.5% of total positive margin)
- resi: £47,246.73 (0.9% of total positive margin)
- SME: £30,174.89 (0.6% of total positive margin)

**Top 5 Accounts by Margin Contribution:**

| Account | Segment | Lifetime Margin | Share | Latest Churn Risk | Margin at Risk |
|---------|---------|-----------------|-------|-------------------|----------------|
| C_IC1 | I&C | £1,893,623.73 | 35.5% | 5% | £94,681.19 |
| C_IC4 | I&C | £1,090,243.56 | 20.4% | 0% | £0.00 |
| C_IC3 | I&C | £1,042,785.72 | 19.5% | 23% | £239,840.72 |
| C_IC2 | I&C | £912,368.86 | 17.1% | 5% | £45,618.44 |
| C_IC3g | I&C | £317,981.74 | 6.0% | 0% | £0.00 |

**Concentration Risk Warning:**
- I&C segment accounts for 98.5% of total portfolio margin
- Resi and SME segments are effectively margin-neutral at portfolio scale
- A single large I&C departure would remove 14-29% of all margin
- Board action: diversify acquisition pipeline toward profitable resi/SME to reduce I&C dependency

## Portfolio Learning Premium (Phase 17a + 19a)

Company applied portfolio premium adjustments at 100 renewal(s) (21 gas) based on recent portfolio-wide margin rates: 53 surcharge(s), 47 discount(s).

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
| C6 | electricity | 2020-03-31 | -52.0% | +15.0% | £125.12/MWh | £143.89/MWh |
| C8 | electricity | 2020-03-31 | -50.0% | +15.0% | £125.12/MWh | £143.89/MWh |
| C_IC1 | electricity | 2020-03-31 | -16.4% | +12.2% | £91.12/MWh | £102.26/MWh |
| C3 | electricity | 2020-06-30 | 23.0% | -5.0% | £113.43/MWh | £107.76/MWh |
| C9 | electricity | 2020-06-30 | 23.0% | -5.0% | £113.43/MWh | £107.76/MWh |
| C4 | electricity | 2020-09-30 | 14.5% | -3.2% | £124.42/MWh | £120.39/MWh |
| C4g | gas | 2020-09-30 | 18.7% | -5.0% | £16.94/MWh | £16.09/MWh |
| C1 | electricity | 2020-12-30 | 12.7% | -2.4% | £133.55/MWh | £130.41/MWh |
| C1g | gas | 2020-12-30 | 10.7% | -1.4% | £28.99/MWh | £28.60/MWh |
| C5 | electricity | 2020-12-30 | 6.9% | +0.6% | £133.55/MWh | £134.32/MWh |
| C7 | electricity | 2020-12-30 | -4.1% | +6.1% | £133.55/MWh | £141.65/MWh |
| C_IC3 | electricity | 2020-12-31 | -5.1% | +6.5% | £50.65/MWh | £53.97/MWh |
| C_IC3g | gas | 2020-12-31 | 8.6% | -0.3% | £20.05/MWh | £19.98/MWh |
| C6 | electricity | 2021-03-31 | -20.7% | +14.3% | £175.90/MWh | £201.11/MWh |
| C8 | electricity | 2021-03-31 | -16.2% | +12.1% | £175.90/MWh | £197.15/MWh |
| C_IC2 | electricity | 2021-03-31 | -25.2% | +15.0% | £138.90/MWh | £159.73/MWh |
| C_IC1 | electricity | 2021-04-30 | 2.4% | +2.8% | £113.97/MWh | £117.15/MWh |
| C9 | electricity | 2021-06-30 | 2.1% | +3.0% | £170.38/MWh | £175.44/MWh |
| C4 | electricity | 2021-09-30 | -1.5% | +4.8% | £205.15/MWh | £214.94/MWh |
| C4g | gas | 2021-09-30 | 1.2% | +3.4% | £53.99/MWh | £55.83/MWh |
| C1 | electricity | 2021-12-30 | 5.8% | +1.1% | £311.83/MWh | £315.32/MWh |
| C5 | electricity | 2021-12-30 | 5.8% | +1.1% | £311.83/MWh | £315.32/MWh |
| C7 | electricity | 2021-12-30 | 5.8% | +1.1% | £311.83/MWh | £315.32/MWh |
| C_IC3 | electricity | 2021-12-31 | -23.0% | +15.0% | £224.03/MWh | £257.63/MWh |
| C_IC3g | gas | 2021-12-31 | -22.4% | +15.0% | £109.48/MWh | £125.90/MWh |
| C6 | electricity | 2022-03-31 | -23.1% | +15.0% | £361.95/MWh | £416.24/MWh |
| C8 | electricity | 2022-03-31 | -13.7% | +10.8% | £361.95/MWh | £401.16/MWh |
| C_IC2 | electricity | 2022-04-30 | -9.9% | +8.9% | £269.81/MWh | £293.91/MWh |
| C_IC1 | electricity | 2022-05-30 | -6.9% | +7.5% | £239.42/MWh | £257.26/MWh |
| C9 | electricity | 2022-06-30 | 4.3% | +1.8% | £255.09/MWh | £259.74/MWh |
| C4 | electricity | 2022-09-30 | 7.2% | +0.4% | £404.86/MWh | £406.41/MWh |
| C4g | gas | 2022-09-30 | -19.5% | +13.8% | £183.79/MWh | £209.10/MWh |
| C7 | electricity | 2022-12-30 | 8.9% | -0.5% | £266.73/MWh | £265.49/MWh |
| C_IC3 | electricity | 2022-12-31 | -0.2% | +4.1% | £168.36/MWh | £175.27/MWh |
| C6 | electricity | 2023-03-31 | -8.2% | +8.1% | £319.17/MWh | £345.04/MWh |
| C8 | electricity | 2023-03-31 | -2.7% | +5.4% | £319.17/MWh | £336.31/MWh |
| C_IC2 | electricity | 2023-05-30 | -21.4% | +14.7% | £171.46/MWh | £196.64/MWh |
| C_IC1 | electricity | 2023-06-29 | -17.2% | +12.6% | £163.19/MWh | £183.75/MWh |
| C9 | electricity | 2023-06-30 | -10.4% | +9.2% | £224.44/MWh | £245.14/MWh |
| C4 | electricity | 2023-09-30 | 9.6% | -0.8% | £216.77/MWh | £215.06/MWh |
| C4g | gas | 2023-09-30 | -38.6% | +15.0% | £47.83/MWh | £55.00/MWh |
| C7 | electricity | 2023-12-30 | 29.2% | -5.0% | £242.22/MWh | £230.11/MWh |
| C6 | electricity | 2024-03-30 | 16.2% | -4.1% | £207.71/MWh | £199.18/MWh |
| C8 | electricity | 2024-03-30 | 16.2% | -4.1% | £207.71/MWh | £199.18/MWh |
| C_IC2 | electricity | 2024-06-28 | -35.7% | +15.0% | £148.64/MWh | £170.93/MWh |
| C9 | electricity | 2024-06-29 | -28.1% | +15.0% | £203.92/MWh | £234.50/MWh |
| C_IC1 | electricity | 2024-07-28 | -26.9% | +15.0% | £154.38/MWh | £177.53/MWh |
| C4 | electricity | 2024-09-29 | 0.4% | +3.8% | £195.97/MWh | £203.38/MWh |
| C7 | electricity | 2024-12-29 | 0.4% | +3.8% | £243.79/MWh | £253.01/MWh |
| C8 | electricity | 2025-03-30 | 10.9% | -1.4% | £284.89/MWh | £280.77/MWh |

## Churn Avoidability Analysis (Phase 17b)

Total no-offer churns: **6** | Blind misses: **5** | Deliberate passes (uneconomical): **1**

- Blind misses: company estimated churn < 30% → no offer made. Of these, 5 had SIM p ≥ 30% (detectable with a better model).
- Deliberate passes: company estimated churn ≥ 30% but the retention offer was uneconomical (margin + acq cost < offer cost).

**Estimated margin at stake** — blind: £4,130.81 | deliberate: £43,346.20 | total: £47,477.00

| Customer | Date | Reason | Co. est | SIM p | Detectable? | Margin at stake |
|----------|------|--------|---------|-------|-------------|----------------|
| C2 | 2020-03-31 | Blind miss | 0.00 | 0.32 | Yes | £559.82 |
| C3 | 2020-06-30 | Blind miss | 0.00 | 0.32 | Yes | £579.51 |
| C1 | 2021-12-30 | Blind miss | 0.04 | 0.32 | Yes | £-178.13 |
| C_IC3 | 2022-12-31 | Uneconomical | 0.95 | 0.23 | No | £43,346.20 |
| C6 | 2024-03-30 | Blind miss | 0.25 | 0.38 | Yes | £2,700.74 |
| C4 | 2024-09-29 | Blind miss | 0.00 | 0.32 | Yes | £468.87 |

## Dual-Fuel Account P&L (Phase 17d)

5 dual-fuel account pair(s): electricity leg + gas leg combined.

| Account | Elec net | Gas net | Combined net | Gas accretive? |
|---------|----------|---------|-------------|---------------|
| C_IC3+C_IC3g | £84,244.63 | £31,404.02 | £115,648.65 | Yes |
| C1+C1g | £414.20 | £642.69 | £1,056.90 | Yes |
| C2+C2g | £377.87 | £611.34 | £989.21 | Yes |
| C3+C3g | £205.99 | £282.80 | £488.79 | Yes |
| C4+C4g | £130.84 | £-2,029.86 | £-1,899.01 | No |

Gas accretive in 4/5 dual-fuel accounts. Total gas net margin: £30,910.99.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £1,443,537.32 across 18 billing accounts. Revenue: £11,298,122.20.

| # | Customer | Tariff | Revenue | Gross margin | Capital | Net margin | Net margin % |
|---|----------|--------|---------|-------------|---------|------------|-------------|
| 1 | C_IC1 | fixed | £3,162,974.57 | £1,913,656.73 | £18,558.52 | £866,862.49 | 27.4% |
| 2 | C_IC2 | fixed | £1,539,850.37 | £923,786.29 | £8,615.41 | £440,450.78 | 28.6% |
| 3 | C_IC3 | pass_through | £2,561,887.42 | £1,057,594.65 | £12,084.46 | £84,244.63 | 3.3% |
| 4 | C_IC3g | pass_through | £1,134,564.64 | £323,696.23 | £0.00 | £31,404.02 | 2.8% |
| 5 | C_IC4 | flex | £2,744,638.87 | £1,106,685.27 | £0.00 | £14,583.80 | 0.5% |
| 6 | C6 | fixed | £39,537.05 | £23,051.13 | £268.73 | £4,162.51 | 10.5% |
| 7 | C9 | fixed | £20,222.77 | £12,687.75 | £131.35 | £1,473.15 | 7.3% |
| 8 | C8 | fixed | £21,645.75 | £12,425.94 | £134.42 | £1,230.08 | 5.7% |
| 9 | C1g | fixed | £2,893.90 | £1,540.63 | £18.80 | £642.69 | 22.2% |
| 10 | C2g | fixed | £2,622.54 | £1,413.47 | £15.30 | £611.34 | 23.3% |
| 11 | C1 | fixed | £4,215.83 | £2,725.31 | £19.09 | £414.20 | 9.8% |
| 12 | C2 | fixed | £3,168.45 | £2,046.31 | £13.89 | £377.87 | 11.9% |
| 13 | C3g | fixed | £2,683.32 | £1,298.53 | £15.29 | £282.80 | 10.5% |
| 14 | C3 | fixed | £3,628.72 | £2,388.84 | £14.77 | £205.99 | 5.7% |
| 15 | C4 | fixed | £6,265.96 | £3,306.69 | £37.42 | £130.84 | 2.1% |
| 16 | C5 | fixed | £15,163.84 | £9,350.39 | £77.10 | £-61.13 | -0.4% |
| 17 | C7 | fixed | £21,787.91 | £10,810.60 | £139.90 | £-1,448.90 | -6.7% |
| 18 | C4g | fixed | £10,370.30 | £1,343.97 | £144.75 | £-2,029.86 | -19.6% |

## Revenue & Margin Sanity Check

### Portfolio P&L Waterfall
| Line | £ | % Revenue |
|------|---|-----------|
| Supply Revenue (ex-VAT, ex-policy passthrough) | £11,298,122 | 100.0% |
| Wholesale cost | -£5,888,313 | 52.1% |
| **Gross supply margin** | **£5,409,809** | **47.9%** |
| Policy + Network costs | -£3,925,982 | 34.7% |
| Capital cost | -£40,289 | 0.4% |
| **Net supply margin** | **£1,443,537** | **12.8%** |

> *The ledger's `net_margin_gbp` (£5,382,112) is gross − capital only, not final net.*

### Segment Net Margin vs Benchmark
| Segment | Revenue | Gross% | Net% | Benchmark | Status |
|---------|---------|--------|------|-----------|--------|
| I&C/elec | £10,009,351 | 50.0% | 14.0% | large spread -20% to +15% (crisis) | ✓ |
| I&C/gas | £1,134,565 | 28.5% | 2.8% | commodity 2-6%, pass-through ≈0 | ✓ |
| SME/elec | £54,701 | 59.2% | 7.5% | CMA 3-8% | ✓ |
| resi/elec | £80,935 | 57.3% | 2.9% | Ofgem CMA 2-5% | ✓ |
| resi/gas | £18,570 | 30.1% | -2.7% | Ofgem CMA 2-4% | ⚠ ANOMALY |

### Per-Customer Net Margin Flags
No individual customers outside ±40.0/80.0 thresholds.

**SANITY CHECK: ANOMALIES DETECTED**
- Segment resi/gas net -2.7% (benchmark Ofgem CMA 2-4%)
## Transaction Log

Total events: 3,024,561

| Event type | Count |
|------------|-------|
| acquisition_gate_event | 1 |
| acquisition_spend_event | 5 |
| bad_debt_event | 1,383 |
| billing_event | 1,383 |
| capital_charge_event | 1,451,047 |
| fixed_cost_event | 114 |
| non_commodity_cost_event | 1,383 |
| payment_received_event | 1,383 |
| settlement_event | 1,566,479 |
| vat_remittance_event | 1,383 |

**Cash-flow waterfall (from ledger)**

| Flow | Amount |
|------|--------|
| Customer bills (all-in) | £15,979,164.61 |
|   Less: VAT remitted to HMRC | (£771,071.11) |
| = Revenue (ex-VAT) | £15,208,093.50 |
| Less: non-commodity pass-through | (£3,897,378.65) |
| Wholesale cost (settlement events) | (£5,888,313.45) |
| Gross margin | £5,422,401.40 |
| Capital charges | (£40,289.20) |
| Net margin | £5,382,112.20 |

_Cash reconciliation: of £15,979,164.61 billed, bad debt of £319,689.15 was written off, leaving £15,659,475.46 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £5,833,494.15._

| Acquisition spend | (£1,250.00) |
| Fixed overhead | (£5,700.00) |
| Operating net margin | £5,375,162.20 |

## Annual Management Accounts

Year-by-year income statement from company accounting records. All figures £.

| Year | Revenue | Wholesale | Non-Commod | Gross Margin | Bad Debt | OpEx | Net Margin |
|------|---------|-----------|-----------|--------------|----------|------|------------|
| 2016 | £15,354.61 | £3,596.53 | £3,892.24 | £7,865.84 | £234.62 | £834.62 | £6,944.88 (45.2%) |
| 2017 | £348,630.52 | £111,056.98 | £112,782.23 | £124,791.30 | £6,260.72 | £6,860.72 | £116,657.37 (33.5%) |
| 2018 | £600,953.01 | £172,802.28 | £163,976.80 | £264,173.93 | £11,823.00 | £12,423.00 | £250,222.87 (41.6%) |
| 2019 | £1,645,452.10 | £496,239.95 | £445,337.04 | £703,875.12 | £30,746.61 | £31,346.61 | £670,219.20 (40.7%) |
| 2020 | £1,887,212.43 | £431,591.09 | £631,516.48 | £824,104.87 | £38,766.02 | £39,666.02 | £782,350.45 (41.5%) |
| 2021 | £2,438,581.89 | £972,966.99 | £679,703.43 | £785,911.46 | £47,629.10 | £48,629.10 | £731,564.68 (30.0%) |
| 2022 | £4,229,152.66 | £2,381,271.82 | £798,941.22 | £1,048,939.63 | £84,099.64 | £84,699.64 | £951,370.07 (22.5%) |
| 2023 | £1,801,739.61 | £647,884.02 | £478,461.98 | £675,393.61 | £47,214.13 | £47,814.13 | £622,087.80 (34.5%) |
| 2024 | £1,588,749.06 | £461,696.61 | £443,786.27 | £683,266.18 | £33,638.14 | £34,788.14 | £642,578.33 (40.4%) |
| 2025 | £652,267.61 | £210,523.16 | £138,980.98 | £302,763.47 | £19,277.17 | £19,577.17 | £280,161.40 (43.0%) |
| **Total** | **£15,208,093.50** | | | | | | **£5,054,157.06 (33.2%)** |

**Best year:** 2022 — net £951,370.07 (22.5% margin)
**Worst year:** 2016 — net £6,944.88 (45.2% margin)

### Balance Sheet (Year End 2025)

| Item | Value |
|------|-------|
| Cash | £7,520,793.28 |
| Trade Receivables | £0.00 |
| **Total Assets** | **£7,520,793.28** |
| Opening Capital | £2,466,636.22 |
| Current Period Profit | £5,054,157.06 |

## Budget vs Actual

Annual plan compared to management account actuals. RAG: GREEN <5%, AMBER 5-15%, RED >=15% variance (either direction).

| Year | Bud Revenue | Act Revenue | Rev% | Bud Net | Act Net | Net% | RAG |
|------|-------------|-------------|------|---------|---------|------|-----|
| 2016 | £14,671.69 | £15,354.61 | +4.7% | £6,592.99 | £6,944.88 | +5.3% | AMBER |
| 2017 | £16,138.86 | £348,630.52 | +2060.2% | £7,252.29 | £116,657.37 | +1508.6% | RED |
| 2018 | £386,623.75 | £600,953.01 | +55.4% | £128,424.00 | £250,222.87 | +94.8% | RED |
| 2019 | £675,851.95 | £1,645,452.10 | +143.5% | £281,335.50 | £670,219.20 | +138.2% | RED |
| 2020 | £1,816,630.04 | £1,887,212.43 | +3.9% | £736,963.94 | £782,350.45 | +6.2% | AMBER |
| 2021 | £2,028,952.42 | £2,438,581.89 | +20.2% | £833,649.22 | £731,564.68 | -12.2% | AMBER |
| 2022 | £2,607,611.88 | £4,229,152.66 | +62.2% | £790,935.58 | £951,370.07 | +20.3% | RED |
| 2023 | £4,508,414.67 | £1,801,739.61 | -60.0% | £1,029,561.00 | £622,087.80 | -39.6% | RED |
| 2024 | £3,512,844.39 | £1,588,749.06 | -54.8% | £893,105.75 | £642,578.33 | -28.1% | RED |
| 2025 | £3,145,356.42 | £652,267.61 | -79.3% | £1,315,150.33 | £280,161.40 | -78.7% | RED |

## Growth & Acquisition

**Mandate:** `flat`  **Acquisition cost:** resi £150 / SME £400  **Fixed overhead:** £50/month

**Acquisition activity by year**

| Year | Attempts | Wins | Win Rate | Spend |
|------|----------|------|----------|-------|
| 2020 | 2 | 0 | 0% | £300.00 |
| 2021 | 2 | 0 | 0% | £400.00 |
| 2024 | 2 | 0 | 0% | £550.00 |

**Total:** 6 attempts, 0 wins (0% win rate), £1,250.00 total spend

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £5,375,162.20

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
- Average CLV (Point-in-Time, year-end 2016): £3,848.23
  - By billing account: C1 £2,259.66, C5 £5,096.01, C7 £4,189.02
- Bill shock events (>=20%): 31 -- C1g 2016-05-31 (37%); C1g 2016-06-30 (29%); C1g 2016-10-31 (79%); C1g 2016-11-30 (46%); C5 2016-05-31 (27%); C5 2016-10-31 (40%); C5 2016-11-30 (43%); C7 2016-04-30 (21%); C7 2016-05-31 (37%); C7 2016-06-30 (30%); C7 2016-10-31 (77%); C7 2016-11-30 (52%); C2g 2016-05-31 (36%); C2g 2016-06-30 (34%); C2g 2016-10-31 (82%); C2g 2016-11-30 (53%); C6 2016-05-31 (25%); C6 2016-06-30 (23%); C6 2016-10-31 (40%); C6 2016-11-30 (46%); C8 2016-05-31 (40%); C8 2016-06-30 (40%); C8 2016-09-30 (22%); C8 2016-10-31 (100%); C8 2016-11-30 (68%); C3g 2016-10-31 (70%); C3g 2016-11-30 (48%); C9 2016-10-31 (74%); C9 2016-11-30 (58%); C4 2016-11-30 (28%); C4g 2016-11-30 (47%)
- Churn risk (accounts renewing in 2016): 3 at risk (≥20% churn prob): C1 29%, C5 29%, C7 29%

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
- Average CLV (Point-in-Time, year-end 2017): £3,686.38
  - By billing account: C1 £1,866.40, C2 £3,448.52, C3 £3,029.81, C4 £2,742.22, C5 £3,908.13, C6 £7,630.18, C7 £2,786.39, C8 £4,112.60, C9 £3,653.20
- Bill shock events (>=20%): 50 -- C1g 2017-01-31 (31%); C1g 2017-02-28 (28%); C1g 2017-05-31 (30%); C1g 2017-06-30 (30%); C1g 2017-09-30 (21%); C1g 2017-11-30 (70%); C5 2017-01-31 (25%); C5 2017-02-28 (23%); C5 2017-06-30 (21%); C5 2017-11-30 (55%); C7 2017-01-31 (33%); C7 2017-02-28 (28%); C7 2017-05-31 (30%); C7 2017-06-30 (31%); C7 2017-09-30 (25%); C7 2017-10-31 (21%); C7 2017-11-30 (74%); C2g 2017-05-31 (34%); C2g 2017-06-30 (29%); C2g 2017-09-30 (27%); C2g 2017-11-30 (66%); C2g 2017-12-31 (22%); C6 2017-05-31 (22%); C6 2017-11-30 (49%); C8 2017-05-31 (39%); C8 2017-06-30 (35%); C8 2017-09-30 (43%); C8 2017-10-31 (22%); C8 2017-11-30 (81%); C8 2017-12-31 (21%); C3g 2017-05-31 (30%); C3g 2017-06-30 (23%); C3g 2017-09-30 (21%); C3g 2017-11-30 (59%); C9 2017-05-31 (32%); C9 2017-06-30 (26%); C9 2017-09-30 (29%); C9 2017-10-31 (21%); C9 2017-11-30 (69%); C4 2017-04-30 (28%); C4 2017-09-30 (21%); C4 2017-10-31 (25%); C4 2017-11-30 (26%); C4g 2017-01-31 (23%); C4g 2017-02-28 (22%); C4g 2017-05-31 (33%); C4g 2017-06-30 (35%); C4g 2017-09-30 (36%); C4g 2017-10-31 (22%); C4g 2017-11-30 (69%)
- Churn risk (accounts renewing in 2017): 9 at risk (≥20% churn prob): C1 32%, C2 29%, C3 23%, C4 29%, C5 32%, C6 35%, C7 38%, C8 35%, C9 29%

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
- Average CLV (Point-in-Time, year-end 2018): £93,861.25
  - By billing account: C1 £1,719.42, C2 £3,117.96, C3 £2,735.70, C4 £2,244.33, C5 £3,848.31, C6 £5,861.07, C7 £2,579.63, C8 £3,446.77, C9 £3,434.55, C_IC1 £909,624.79
- Bill shock events (>=20%): 60 -- C1g 2018-04-30 (37%); C1g 2018-05-31 (29%); C1g 2018-06-30 (30%); C1g 2018-09-30 (25%); C1g 2018-10-31 (46%); C1g 2018-11-30 (27%); C5 2018-04-30 (31%); C5 2018-06-30 (20%); C5 2018-10-31 (31%); C5 2018-11-30 (26%); C7 2018-04-30 (38%); C7 2018-05-31 (28%); C7 2018-06-30 (30%); C7 2018-09-30 (27%); C7 2018-10-31 (45%); C7 2018-11-30 (31%); C2g 2018-04-30 (28%); C2g 2018-05-31 (34%); C2g 2018-06-30 (34%); C2g 2018-09-30 (33%); C2g 2018-10-31 (45%); C6 2018-04-30 (23%); C6 2018-05-31 (21%); C6 2018-06-30 (22%); C6 2018-10-31 (30%); C6 2018-11-30 (21%); C8 2018-04-30 (35%); C8 2018-05-31 (37%); C8 2018-06-30 (42%); C8 2018-08-31 (23%); C8 2018-09-30 (49%); C8 2018-10-31 (53%); C8 2018-11-30 (29%); C3g 2018-04-30 (28%); C3g 2018-05-31 (32%); C3g 2018-06-30 (29%); C3g 2018-08-31 (34%); C3g 2018-09-30 (34%); C3g 2018-10-31 (35%); C3g 2018-12-31 (22%); C9 2018-04-30 (31%); C9 2018-05-31 (34%); C9 2018-06-30 (33%); C9 2018-07-31 (21%); C9 2018-08-31 (39%); C9 2018-09-30 (42%); C9 2018-10-31 (39%); C4 2018-04-30 (28%); C4 2018-09-30 (23%); C4 2018-10-31 (41%); C4 2018-11-30 (28%); C4g 2018-04-30 (36%); C4g 2018-05-31 (33%); C4g 2018-06-30 (36%); C4g 2018-09-30 (39%); C4g 2018-10-31 (85%); C4g 2018-11-30 (24%); C_IC1 2018-01-31 (22%); C_IC1 2018-02-28 (63%); C_IC2 2018-09-30 (20%)
- Churn risk (accounts renewing in 2018): 9 at risk (≥20% churn prob): C1 38%, C2 32%, C3 32%, C4 38%, C5 35%, C6 32%, C7 41%, C8 35%, C9 38%

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
- Average CLV (Point-in-Time, year-end 2019): £126,159.83
  - By billing account: C1 £1,697.80, C2 £2,636.08, C3 £2,692.56, C4 £2,508.16, C5 £4,077.50, C6 £6,421.57, C7 £2,893.06, C8 £3,508.69, C9 £3,243.91, C_IC1 £815,715.03, C_IC2 £542,363.74
- Bill shock events (>=20%): 66 -- C1 2019-04-30 (21%); C1g 2019-01-31 (36%); C1g 2019-02-28 (26%); C1g 2019-05-31 (23%); C1g 2019-06-30 (35%); C1g 2019-10-31 (74%); C1g 2019-11-30 (43%); C5 2019-01-31 (42%); C5 2019-02-28 (21%); C5 2019-06-30 (25%); C5 2019-10-31 (42%); C5 2019-11-30 (35%); C7 2019-01-31 (44%); C7 2019-02-28 (26%); C7 2019-05-31 (23%); C7 2019-06-30 (34%); C7 2019-10-31 (68%); C7 2019-11-30 (44%); C2g 2019-01-31 (25%); C2g 2019-02-28 (26%); C2g 2019-04-30 (35%); C2g 2019-06-30 (32%); C2g 2019-07-31 (25%); C2g 2019-09-30 (30%); C2g 2019-10-31 (64%); C2g 2019-11-30 (28%); C6 2019-02-28 (21%); C6 2019-06-30 (24%); C6 2019-10-31 (41%); C6 2019-11-30 (26%); C8 2019-01-31 (27%); C8 2019-02-28 (27%); C8 2019-04-30 (21%); C8 2019-06-30 (38%); C8 2019-07-31 (33%); C8 2019-09-30 (55%); C8 2019-10-31 (83%); C8 2019-11-30 (36%); C3 2019-04-30 (20%); C3g 2019-02-28 (26%); C3g 2019-06-30 (33%); C3g 2019-07-31 (35%); C3g 2019-09-30 (35%); C3g 2019-10-31 (64%); C3g 2019-11-30 (31%); C9 2019-02-28 (26%); C9 2019-04-30 (22%); C9 2019-06-30 (35%); C9 2019-07-31 (32%); C9 2019-09-30 (48%); C9 2019-10-31 (71%); C9 2019-11-30 (36%); C4 2019-04-30 (31%); C4 2019-09-30 (25%); C4 2019-11-30 (26%); C4g 2019-01-31 (30%); C4g 2019-02-28 (25%); C4g 2019-05-31 (21%); C4g 2019-06-30 (33%); C4g 2019-07-31 (37%); C4g 2019-09-30 (31%); C4g 2019-10-31 (34%); C4g 2019-11-30 (35%); C_IC1 2019-02-28 (54%); C_IC1 2019-03-31 (130%); C_IC2 2019-02-28 (69%)
- Churn risk (accounts renewing in 2019): 10 at risk (≥20% churn prob): C1 35%, C2 29%, C3 32%, C4 38%, C5 38%, C6 29%, C7 35%, C8 38%, C9 32%, C_IC1 23%

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

- Net margin: £153,032.39 (gross £822,447.79, capital £2,088.40)
  - Electricity: gross £745,485.04, capital £2,079.49, net £143,287.45
  - Gas: gross £76,962.75, capital £8.92, net £9,744.94
- Treasury at year end: £2,914,252.99
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.89 (avg 0.89), C1g 0.85 (avg 0.85), C4 0.88 (avg 0.88), C4g 0.85 (avg 0.85), C5 0.89 (avg 0.89), C6 0.86 (avg 0.86), C7 0.88 (avg 0.88), C8 0.86 (avg 0.86), C9 0.85 (avg 0.85), C_IC1 0.85 (avg 0.87), C_IC2 0.85 (avg 0.87), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2020-03-16 period 20, net margin £-18.66

**Customer Book**

- Active accounts: 18 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 5
- New acquisitions this year: C_IC4
- Losses (churn) during year: C2, C3
  - Renewals (retained): 8 accounts
- Average CLV (Point-in-Time, year-end 2020): £188,595.00
  - By billing account: C1 £2,034.59, C2 £2,294.14, C3 £2,586.03, C4 £2,582.20, C5 £4,517.94, C6 £7,623.25, C7 £3,145.02, C8 £4,073.66, C9 £3,787.92, C_IC1 £576,736.84, C_IC2 £293,544.83, C_IC3 £1,010,362.98, C_IC4 £538,445.61
- Bill shock events (>=20%): 47 -- C1g 2020-01-31 (21%); C1g 2020-04-30 (32%); C1g 2020-06-30 (25%); C1g 2020-10-31 (56%); C1g 2020-12-31 (35%); C5 2020-04-30 (28%); C5 2020-10-31 (36%); C5 2020-12-31 (25%); C7 2020-04-30 (34%); C7 2020-05-31 (20%); C7 2020-06-30 (27%); C7 2020-10-31 (58%); C7 2020-11-30 (23%); C7 2020-12-31 (34%); C6 2020-04-30 (29%); C6 2020-09-30 (20%); C6 2020-10-31 (33%); C6 2020-12-31 (26%); C8 2020-04-30 (35%); C8 2020-05-31 (24%); C8 2020-06-30 (32%); C8 2020-09-30 (51%); C8 2020-10-31 (64%); C8 2020-12-31 (42%); C3g 2020-04-30 (24%); C3g 2020-05-31 (21%); C3g 2020-06-29 (34%); C9 2020-04-30 (27%); C9 2020-05-31 (25%); C9 2020-06-30 (34%); C9 2020-09-30 (42%); C9 2020-10-31 (48%); C9 2020-12-31 (36%); C4 2020-04-30 (30%); C4 2020-09-30 (20%); C4 2020-10-31 (21%); C4 2020-11-30 (24%); C4g 2020-04-30 (35%); C4g 2020-05-31 (20%); C4g 2020-06-30 (26%); C4g 2020-09-30 (30%); C4g 2020-10-31 (49%); C4g 2020-12-31 (35%); C_IC1 2020-03-31 (57%); C_IC1 2020-04-30 (91%); C_IC2 2020-02-29 (66%); C_IC2 2020-03-31 (118%)
- Churn risk (accounts renewing in 2020): 10 at risk (≥20% churn prob): C1 29%, C2 32%, C3 32%, C4 32%, C5 35%, C6 32%, C7 35%, C8 38%, C9 41%, C_IC2 20%

**Pricing & Margin**

- C1 (electricity): tariff £125.83-£130.41/MWh, net margin £74.96
- C1g (gas): tariff £25.00-£25.33/MWh, net margin £137.20
- C2 (electricity): tariff £151.90/MWh, net margin £41.32
- C2g (gas): tariff £26.00/MWh, net margin £25.58
- C3 (electricity): tariff £120.68/MWh, net margin £16.44
- C3g (gas): tariff £23.00/MWh, net margin £75.08
- C4 (electricity): tariff £120.39-£126.76/MWh, net margin £84.40
- C4g (gas): tariff £16.09-£19.47/MWh, net margin £71.92
- C5 (electricity): tariff £126.10-£134.32/MWh, net margin £-30.91 -- **net-negative**
- C6 (electricity): tariff £143.89-£148.72/MWh, net margin £366.13
- C7 (electricity): tariff £99.69-£212.48/MWh, net margin £58.29
- C8 (electricity): tariff £110.73-£215.83/MWh, net margin £365.81
- C9 (electricity): tariff £84.67-£188.63/MWh, net margin £112.35
- C_IC1 (electricity): tariff £-73.45-£2690.77/MWh, net margin £83,074.42
- C_IC2 (electricity): tariff £-79.50-£278.56/MWh, net margin £43,546.80
- C_IC3 (electricity): tariff £37.49-£80.95/MWh, net margin £11,007.15
- C_IC3g (gas): tariff £15.44-£19.98/MWh, net margin £9,435.16
- C_IC4 (electricity): tariff £77.17-£132.42/MWh, net margin £4,570.28

**Portfolio Health**

- Capital cost ratio: 0.3% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 186, average clarity 0.830, average bill shock 14.4%, bad debt provision £6,434.09, avg complaint probability 4.3%
- Solvency signal: £224,173/customer (13 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £126,136.42 vs. naked (unhedged) net margin: £1,004,396.90
- hedging cost £878,260.48 vs. a fully unhedged book (commodity-only: actual net £126,136.42 vs. naked net £1,004,396.90)
  - C1: actual £-27.35 vs. naked £88.09 -- hedging cost £115.44
  - C1g: actual £22.28 vs. naked £-68.18 -- hedging added £90.47
  - C4: actual £17.11 vs. naked £226.84 -- hedging cost £209.73
  - C4g: actual £-75.14 vs. naked £117.15 -- hedging cost £192.29
  - C5: actual £-365.46 vs. naked £145.23 -- hedging cost £510.69
  - C6: actual £355.75 vs. naked £2,175.57 -- hedging cost £1,819.82
  - C7: actual £-114.05 vs. naked £325.31 -- hedging cost £439.36
  - C8: actual £385.72 vs. naked £1,216.68 -- hedging cost £830.96
  - C9: actual £-30.07 vs. naked £685.91 -- hedging cost £715.98
  - C_IC1: actual £73,597.25 vs. naked £169,702.73 -- hedging cost £96,105.47
  - C_IC2: actual £42,303.73 vs. naked £96,422.44 -- hedging cost £54,118.71
  - C_IC3: actual £-15,754.85 vs. naked £221,281.26 -- hedging cost £237,036.11
  - C_IC3g: actual £17,934.51 vs. naked £159,245.07 -- hedging cost £141,310.56
  - C_IC4: actual £7,886.99 vs. naked £352,832.81 -- hedging cost £344,945.82

**Year narrative:** 2020 produced a net gain of £153,032.39 across 18 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 47 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £87,129.50 (gross £784,501.09, capital £5,717.68)
  - Electricity: gross £702,023.97, capital £5,705.82, net £78,922.24
  - Gas: gross £82,477.12, capital £11.86, net £8,207.26
- Treasury at year end: £2,983,493.32
- Hedge fraction at first renewal this year (avg across year's terms): C4 0.94 (avg 0.94), C4g 0.85 (avg 0.85), C6 0.91 (avg 0.91), C7 0.97 (avg 0.97), C8 0.92 (avg 0.92), C9 0.92 (avg 0.92), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.00 (avg 0.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2021-11-24 period 30, net margin £-74.55

**Customer Book**

- Active accounts: 14 (C1, C1g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 2, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: C1, C5
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2021): £185,416.55
  - By billing account: C1 £2,042.23, C2 £2,356.99, C3 £2,458.40, C4 £2,267.90, C5 £4,261.36, C6 £7,289.32, C7 £3,423.59, C8 £4,066.88, C9 £3,661.53, C_IC1 £532,150.82, C_IC2 £314,544.40, C_IC3 £970,054.62, C_IC4 £561,837.14
- Bill shock events (>=20%): 47 -- C1g 2021-05-31 (28%); C1g 2021-06-30 (45%); C1g 2021-10-31 (55%); C1g 2021-11-30 (53%); C5 2021-05-31 (22%); C5 2021-06-30 (31%); C5 2021-10-31 (28%); C5 2021-11-30 (48%); C7 2021-01-31 (21%); C7 2021-05-31 (29%); C7 2021-06-30 (46%); C7 2021-10-31 (52%); C7 2021-11-30 (63%); C6 2021-06-30 (35%); C6 2021-10-31 (27%); C6 2021-11-30 (49%); C8 2021-05-31 (28%); C8 2021-06-30 (60%); C8 2021-09-30 (23%); C8 2021-10-31 (65%); C8 2021-11-30 (80%); C9 2021-02-28 (21%); C9 2021-05-31 (24%); C9 2021-06-30 (49%); C9 2021-08-31 (20%); C9 2021-09-30 (21%); C9 2021-10-31 (59%); C9 2021-11-30 (48%); C9 2021-12-31 (23%); C4 2021-04-30 (30%); C4 2021-09-30 (22%); C4 2021-10-31 (49%); C4 2021-11-30 (31%); C4g 2021-05-31 (22%); C4g 2021-06-30 (53%); C4g 2021-10-31 (113%); C4g 2021-11-30 (56%); C_IC1 2021-04-30 (25%); C_IC1 2021-05-31 (39%); C_IC2 2021-03-31 (22%); C_IC2 2021-04-30 (93%); C_IC3g 2021-09-30 (33%); C_IC3g 2021-10-31 (23%); C_IC3g 2021-12-31 (33%); C_IC4 2021-02-28 (21%); C_IC4 2021-09-30 (27%); C_IC4 2021-12-31 (23%)
- Churn risk (accounts renewing in 2021): 10 at risk (≥20% churn prob): C1 32%, C4 35%, C5 35%, C6 35%, C7 35%, C8 41%, C9 35%, C_IC2 23%, C_IC3 20%, C_IC4 29%

**Pricing & Margin**

- C1 (electricity): tariff £130.41/MWh, net margin £-27.01 -- **net-negative**
- C1g (gas): tariff £25.00/MWh, net margin £21.95
- C4 (electricity): tariff £120.39-£183.00/MWh, net margin £-64.23 -- **net-negative**
- C4g (gas): tariff £16.09-£35.00/MWh, net margin £-334.91 -- **net-negative**
- C5 (electricity): tariff £134.32/MWh, net margin £-361.42 -- **net-negative**
- C6 (electricity): tariff £143.89-£201.11/MWh, net margin £585.08
- C7 (electricity): tariff £111.30-£274.50/MWh, net margin £-123.77 -- **net-negative**
- C8 (electricity): tariff £113.06-£274.50/MWh, net margin £358.15
- C9 (electricity): tariff £84.67-£263.17/MWh, net margin £-23.96 -- **net-negative**
- C_IC1 (electricity): tariff £-54.00-£2365.91/MWh, net margin £34,804.69
- C_IC2 (electricity): tariff £-73.20-£1080.00/MWh, net margin £67,345.13
- C_IC3 (electricity): tariff £42.40-£390.56/MWh, net margin £-26,895.06 -- **net-negative**
- C_IC3g (gas): tariff £19.98-£125.90/MWh, net margin £8,520.22
- C_IC4 (electricity): tariff £103.84-£397.26/MWh, net margin £3,324.66

**Portfolio Health**

- Capital cost ratio: 0.7% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 168, average clarity 0.826, average bill shock 16.1%, bad debt provision £9,165.93, avg complaint probability 4.6%
- Solvency signal: £271,227/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £202,760.86 vs. naked (unhedged) net margin: £468,485.56
- hedging cost £265,724.70 vs. a fully unhedged book (commodity-only: actual net £202,760.86 vs. naked net £468,485.56)
  - C4: actual £-220.41 vs. naked £-170.34 -- hedging cost £50.07
  - C4g: actual £-901.21 vs. naked £-1,344.38 -- hedging added £443.17
  - C6: actual £599.03 vs. naked £361.28 -- hedging added £237.75
  - C7: actual £-1,829.78 vs. naked £-869.22 -- hedging cost £960.56
  - C8: actual £285.02 vs. naked £107.75 -- hedging added £177.27
  - C9: actual £-57.61 vs. naked £-194.40 -- hedging added £136.78
  - C_IC1: actual £25,203.57 vs. naked £-64,186.08 -- hedging added £89,389.65
  - C_IC2: actual £78,799.11 vs. naked £38,176.83 -- hedging added £40,622.29
  - C_IC3: actual £98,643.53 vs. naked £233,100.50 -- hedging cost £134,456.97
  - C_IC3g: actual £4,142.87 vs. naked £85,199.40 -- hedging cost £81,056.52
  - C_IC4: actual £-1,903.26 vs. naked £178,304.23 -- hedging cost £180,207.49

**Year narrative:** 2021 (flagged crisis year) produced a net gain of £87,129.50 across 14 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 47 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £304,766.07 (gross £1,047,819.00, capital £12,869.92)
  - Electricity: gross £957,809.94, capital £12,837.11, net £301,928.59
  - Gas: gross £90,009.06, capital £32.81, net £2,837.49
- Treasury at year end: £3,190,740.16
- Hedge fraction at first renewal this year (avg across year's terms): C4 0.96 (avg 0.96), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.93 (avg 0.93), C8 0.96 (avg 0.96), C9 0.94 (avg 0.94), C_IC1 1.00 (avg 0.97), C_IC2 1.00 (avg 0.97), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 9
  - 2022-04-29: treasury £3,091,790.81, C6->1.00, C8->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,060.50 / stressed £20,778.40) ratio 2.70
  - 2022-05-29: treasury £3,091,894.79, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,169.42 / stressed £20,807.27) ratio 2.70
  - 2022-06-28: treasury £3,091,889.12, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,169.42 / stressed £20,807.27) ratio 2.70
  - 2022-07-28: treasury £3,091,696.47, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, VaR (current £56,231.40 / stressed £20,819.81) ratio 2.70
  - 2022-08-27: treasury £3,091,686.87, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,231.40 / stressed £20,819.81) ratio 2.70
  - 2022-09-26: treasury £3,091,671.42, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,231.40 / stressed £20,819.81) ratio 2.70
  - 2022-10-26: treasury £3,089,385.48, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,292.84 / stressed £20,829.96) ratio 2.70
  - 2022-11-25: treasury £3,089,235.07, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,292.84 / stressed £20,829.96) ratio 2.70
  - 2022-12-25: treasury £3,088,968.88, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £56,292.84 / stressed £20,829.96) ratio 2.70
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.70
- Worst single period: C_IC1 on 2022-01-24 period 26, net margin £-88.66

**Customer Book**

- Active accounts: 11 (C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 4, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: none
- Losses (churn) during year: C_IC3
  - Renewals (retained): 5 accounts
- Average CLV (Point-in-Time, year-end 2022): £197,282.33
  - By billing account: C1 £2,033.60, C2 £2,343.14, C3 £2,442.45, C4 £1,528.55, C5 £4,247.85, C6 £7,927.26, C7 £2,724.09, C8 £3,997.66, C9 £3,698.51, C_IC1 £564,101.48, C_IC2 £335,668.74, C_IC3 £1,074,180.04, C_IC4 £559,776.91
- Bill shock events (>=20%): 55 -- C7 2022-01-31 (49%); C7 2022-02-28 (26%); C7 2022-04-30 (22%); C7 2022-05-31 (34%); C7 2022-06-30 (25%); C7 2022-09-30 (30%); C7 2022-11-30 (58%); C7 2022-12-31 (54%); C6 2022-04-30 (42%); C6 2022-05-31 (23%); C6 2022-09-30 (25%); C6 2022-11-30 (43%); C6 2022-12-31 (33%); C8 2022-02-28 (22%); C8 2022-05-31 (38%); C8 2022-06-30 (33%); C8 2022-09-30 (76%); C8 2022-11-30 (68%); C8 2022-12-31 (56%); C9 2022-04-30 (20%); C9 2022-05-31 (28%); C9 2022-06-30 (29%); C9 2022-09-30 (45%); C9 2022-10-31 (30%); C9 2022-11-30 (43%); C9 2022-12-31 (51%); C4 2022-04-30 (28%); C4 2022-09-30 (25%); C4 2022-10-31 (62%); C4 2022-11-30 (31%); C4g 2022-01-31 (25%); C4g 2022-02-28 (24%); C4g 2022-05-31 (34%); C4g 2022-06-30 (28%); C4g 2022-07-31 (22%); C4g 2022-09-30 (63%); C4g 2022-10-31 (134%); C4g 2022-11-30 (57%); C4g 2022-12-31 (56%); C_IC1 2022-03-31 (21%); C_IC1 2022-06-30 (77%); C_IC2 2022-03-31 (24%); C_IC2 2022-05-31 (56%); C_IC3 2022-01-31 (108%); C_IC3g 2022-03-31 (38%); C_IC3g 2022-04-30 (22%); C_IC3g 2022-07-31 (40%); C_IC3g 2022-08-31 (30%); C_IC3g 2022-10-31 (51%); C_IC3g 2022-11-30 (31%); C_IC4 2022-03-31 (41%); C_IC4 2022-07-31 (29%); C_IC4 2022-08-31 (33%); C_IC4 2022-10-31 (31%); C_IC4 2022-12-31 (68%)
- Churn risk (accounts renewing in 2022): 8 at risk (≥20% churn prob): C4 38%, C6 32%, C7 35%, C8 35%, C9 38%, C_IC1 20%, C_IC3 23%, C_IC4 32%

**Pricing & Margin**

- C4 (electricity): tariff £183.00-£305.00/MWh, net margin £-276.94 -- **net-negative**
- C4g (gas): tariff £35.00-£95.00/MWh, net margin £-1,284.53 -- **net-negative**
- C6 (electricity): tariff £201.11-£416.24/MWh, net margin £987.68
- C7 (electricity): tariff £143.79-£457.50/MWh, net margin £-1,827.01 -- **net-negative**
- C8 (electricity): tariff £143.79-£457.50/MWh, net margin £-285.40 -- **net-negative**
- C9 (electricity): tariff £137.85-£389.61/MWh, net margin £-121.71 -- **net-negative**
- C_IC1 (electricity): tariff £-83.39-£463.07/MWh, net margin £130,656.99
- C_IC2 (electricity): tariff £-80.56-£593.08/MWh, net margin £75,926.31
- C_IC3 (electricity): tariff £204.58-£390.56/MWh, net margin £98,776.60
- C_IC3g (gas): tariff £125.90/MWh, net margin £4,122.01
- C_IC4 (electricity): tariff £133.29-£531.77/MWh, net margin £-1,907.93 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 1.2% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £3,490,337.78 -> £3,088,937.96 (11.5%)
- Bills issued: 132, average clarity 0.794, average bill shock 22.0%, bad debt provision £35,334.71, avg complaint probability 5.5%
- Solvency signal: £354,527/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £301,266.96 vs. naked (unhedged) net margin: £592,489.70
- hedging cost £291,222.73 vs. a fully unhedged book (commodity-only: actual net £301,266.96 vs. naked net £592,489.70)
  - C4: actual £-277.33 vs. naked £595.36 -- hedging cost £872.70
  - C4g: actual £-1,950.48 vs. naked £1,336.80 -- hedging cost £3,287.28
  - C6: actual £1,338.15 vs. naked £4,212.15 -- hedging cost £2,874.00
  - C7: actual £-445.92 vs. naked £2,281.71 -- hedging cost £2,727.63
  - C8: actual £-481.87 vs. naked £1,102.92 -- hedging cost £1,584.78
  - C9: actual £-48.83 vs. naked £1,012.79 -- hedging cost £1,061.62
  - C_IC1: actual £212,889.80 vs. naked £251,173.84 -- hedging cost £38,284.04
  - C_IC2: actual £86,770.64 vs. naked £126,067.12 -- hedging cost £39,296.49
  - C_IC4: actual £3,472.81 vs. naked £204,707.00 -- hedging cost £201,234.19

**Year narrative:** 2022 (flagged crisis year) produced a net gain of £304,766.07 across 11 accounts. The risk committee intervened 9 time(s), raising hedge fractions in response to elevated VaR. 55 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £247,498.90 (gross £674,652.20, capital £5,491.67)
  - Electricity: gross £675,227.54, capital £5,439.25, net £248,663.22
  - Gas: gross £-575.33, capital £52.42, net £-1,164.32
- Treasury at year end: £3,492,184.23
- Hedge fraction at first renewal this year (avg across year's terms): C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C6 0.93 (avg 0.93), C7 0.92 (avg 0.92), C8 0.95 (avg 0.95), C9 0.91 (avg 0.91), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 4
  - 2023-01-24: treasury £3,190,852.51, C4->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £122,074.63 / stressed £44,286.67) ratio 2.76
  - 2023-02-23: treasury £3,190,992.42, C4->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £122,074.63 / stressed £44,286.67) ratio 2.76
  - 2023-03-25: treasury £3,191,134.86, C4->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £122,074.63 / stressed £44,286.67) ratio 2.76
  - 2023-04-24: treasury £3,269,520.42, C4->1.00, C7->1.00, C9->1.00, C_IC3->1.00, VaR (current £127,898.24 / stressed £48,770.20) ratio 2.62
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.72
- Worst single period: C_IC1 on 2023-06-16 period 22, net margin £-21.69

**Customer Book**

- Active accounts: 9 (C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC4)
  - Resi electricity: 4, SME electricity: 1, gas (dual-fuel): 1
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 5 accounts
- Average CLV (Point-in-Time, year-end 2023): £206,732.09
  - By billing account: C1 £1,954.13, C2 £2,269.64, C3 £2,559.82, C4 £1,168.62, C5 £4,442.82, C6 £9,613.75, C7 £2,703.63, C8 £4,225.35, C9 £4,056.59, C_IC1 £631,410.35, C_IC2 £364,308.54, C_IC3 £1,096,950.89, C_IC4 £561,852.97
- Bill shock events (>=20%): 38 -- C7 2023-01-31 (40%); C7 2023-05-31 (31%); C7 2023-06-30 (35%); C7 2023-10-31 (53%); C7 2023-11-30 (69%); C6 2023-04-30 (31%); C6 2023-05-31 (23%); C6 2023-06-30 (22%); C6 2023-10-31 (38%); C6 2023-11-30 (43%); C8 2023-04-30 (30%); C8 2023-05-31 (39%); C8 2023-06-30 (42%); C8 2023-10-31 (92%); C8 2023-11-30 (66%); C9 2023-02-28 (21%); C9 2023-03-31 (20%); C9 2023-04-30 (26%); C9 2023-05-31 (32%); C9 2023-06-30 (43%); C9 2023-09-30 (20%); C9 2023-10-31 (71%); C9 2023-11-30 (52%); C4 2023-02-28 (25%); C4 2023-04-30 (29%); C4 2023-09-30 (24%); C4 2023-11-30 (27%); C4g 2023-05-31 (36%); C4g 2023-06-30 (45%); C4g 2023-10-31 (46%); C4g 2023-11-30 (63%); C_IC1 2023-03-31 (21%); C_IC1 2023-06-30 (53%); C_IC1 2023-07-31 (60%); C_IC2 2023-03-31 (22%); C_IC2 2023-05-31 (52%); C_IC2 2023-06-30 (100%); C_IC4 2023-01-31 (35%)
- Churn risk (accounts renewing in 2023): 6 at risk (≥20% churn prob): C4 35%, C6 29%, C7 38%, C8 38%, C9 38%, C_IC4 26%

**Pricing & Margin**

- C4 (electricity): tariff £249.34-£305.00/MWh, net margin £-68.67 -- **net-negative**
- C4g (gas): tariff £66.00-£95.00/MWh, net margin £-1,164.32 -- **net-negative**
- C6 (electricity): tariff £345.04-£416.24/MWh, net margin £1,515.26
- C7 (electricity): tariff £191.96-£457.50/MWh, net margin £-443.76 -- **net-negative**
- C8 (electricity): tariff £208.21-£457.50/MWh, net margin £-111.16 -- **net-negative**
- C9 (electricity): tariff £192.61-£389.61/MWh, net margin £226.55
- C_IC1 (electricity): tariff £-60.00-£463.07/MWh, net margin £160,044.88
- C_IC2 (electricity): tariff £-186.24-£475.91/MWh, net margin £84,019.87
- C_IC4 (electricity): tariff £106.05-£234.49/MWh, net margin £3,480.25

**Portfolio Health**

- Capital cost ratio: 0.8% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 108, average clarity 0.782, average bill shock 18.8%, bad debt provision £7,592.04, avg complaint probability 5.2%
- Solvency signal: £436,523/customer (8 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £242,529.71 vs. naked (unhedged) net margin: £691,020.58
- hedging cost £448,490.87 vs. a fully unhedged book (commodity-only: actual net £242,529.71 vs. naked net £691,020.58)
  - C4: actual £314.01 vs. naked £700.20 -- hedging cost £386.19
  - C4g: actual £529.39 vs. naked £1,048.79 -- hedging cost £519.40
  - C6: actual £1,678.11 vs. naked £5,349.76 -- hedging cost £3,671.65
  - C7: actual £493.58 vs. naked £1,989.47 -- hedging cost £1,495.89
  - C8: actual £140.61 vs. naked £1,972.23 -- hedging cost £1,831.62
  - C9: actual £626.55 vs. naked £2,130.21 -- hedging cost £1,503.66
  - C_IC1: actual £141,666.97 vs. naked £284,541.50 -- hedging cost £142,874.54
  - C_IC2: actual £93,388.75 vs. naked £161,434.28 -- hedging cost £68,045.53
  - C_IC4: actual £3,691.75 vs. naked £231,854.14 -- hedging cost £228,162.39

**Year narrative:** 2023 produced a net gain of £247,498.90 across 9 accounts. The risk committee intervened 4 time(s), raising hedge fractions in response to elevated VaR. 38 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £198,234.67 (gross £683,272.01, capital £5,899.72)
  - Electricity: gross £682,509.72, capital £5,876.32, net £197,837.75
  - Gas: gross £762.29, capital £23.40, net £396.91
- Treasury at year end: £3,733,774.21
- Hedge fraction at first renewal this year (avg across year's terms): C7 0.90 (avg 0.90), C8 0.91 (avg 0.91), C9 0.89 (avg 0.89), C_IC1 0.85 (avg 0.87), C_IC2 0.85 (avg 0.87), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2024-06-28 period 31, net margin £-26.25

**Customer Book**

- Active accounts: 9 (C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC4)
  - Resi electricity: 4, SME electricity: 1, gas (dual-fuel): 1
- New acquisitions this year: none
- Losses (churn) during year: C6, C4
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2024): £210,380.47
  - By billing account: C1 £2,104.15, C2 £2,399.61, C3 £2,672.11, C4 £1,522.41, C5 £4,369.47, C6 £9,448.74, C7 £3,052.51, C8 £4,466.75, C9 £4,029.62, C_IC1 £716,502.10, C_IC2 £387,798.07, C_IC3 £988,673.17, C_IC4 £607,907.37
- Bill shock events (>=20%): 26 -- C7 2024-02-29 (26%); C7 2024-05-31 (36%); C7 2024-09-30 (32%); C7 2024-10-31 (36%); C7 2024-11-30 (47%); C8 2024-02-29 (23%); C8 2024-04-30 (35%); C8 2024-05-31 (47%); C8 2024-07-31 (25%); C8 2024-09-30 (67%); C8 2024-10-31 (34%); C8 2024-11-30 (59%); C9 2024-05-31 (48%); C9 2024-07-31 (28%); C9 2024-09-30 (52%); C9 2024-10-31 (22%); C9 2024-11-30 (46%); C4 2024-04-30 (30%); C4g 2024-02-29 (27%); C4g 2024-05-31 (39%); C4g 2024-07-31 (24%); C4g 2024-09-28 (45%); C_IC1 2024-07-31 (33%); C_IC1 2024-08-31 (65%); C_IC2 2024-06-30 (49%); C_IC2 2024-07-31 (107%)
- Churn risk (accounts renewing in 2024): 5 at risk (≥20% churn prob): C4 32%, C6 38%, C7 35%, C8 41%, C9 38%

**Pricing & Margin**

- C4 (electricity): tariff £249.34/MWh, net margin £235.22
- C4g (gas): tariff £66.00/MWh, net margin £396.91
- C6 (electricity): tariff £345.04/MWh, net margin £581.94
- C7 (electricity): tariff £165.00-£366.47/MWh, net margin £492.80
- C8 (electricity): tariff £156.50-£397.50/MWh, net margin £242.23
- C9 (electricity): tariff £165.00-£367.70/MWh, net margin £560.67
- C_IC1 (electricity): tariff £-98.58-£330.75/MWh, net margin £123,525.90
- C_IC2 (electricity): tariff £-106.92-£353.94/MWh, net margin £68,499.87
- C_IC4 (electricity): tariff £104.06-£193.21/MWh, net margin £3,699.12

**Portfolio Health**

- Capital cost ratio: 0.9% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 93, average clarity 0.783, average bill shock 17.6%, bad debt provision £6,115.94, avg complaint probability 5.1%
- Solvency signal: £466,722/customer (8 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £176,585.86 vs. naked (unhedged) net margin: £426,483.41
- hedging cost £249,897.55 vs. a fully unhedged book (commodity-only: actual net £176,585.86 vs. naked net £426,483.41)
  - C7: actual £-27.34 vs. naked £653.82 -- hedging cost £681.16
  - C8: actual £228.35 vs. naked £1,337.20 -- hedging cost £1,108.84
  - C9: actual £373.18 vs. naked £1,427.71 -- hedging cost £1,054.53
  - C_IC1: actual £114,253.44 vs. naked £208,996.78 -- hedging cost £94,743.34
  - C_IC2: actual £60,322.70 vs. naked £111,508.78 -- hedging cost £51,186.08
  - C_IC4: actual £1,435.52 vs. naked £102,559.12 -- hedging cost £101,123.60

**Year narrative:** 2024 produced a net gain of £198,234.67 across 9 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 26 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £93,552.93 (gross £302,507.51, capital £3,024.89)
  - Electricity: gross £302,507.51, capital £3,024.89, net £93,552.93
- Treasury at year end: £3,783,451.05
- Hedge fraction at first renewal this year (avg across year's terms): C8 0.89 (avg 0.89)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC1 on 2025-01-08 period 31, net margin £-81.23

**Customer Book**

- Active accounts: 6 (C7, C8, C9, C_IC1, C_IC2, C_IC4)
  - Resi electricity: 3, SME electricity: 0, gas (dual-fuel): 0
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 1 accounts
- Average CLV (Point-in-Time, year-end 2025): £222,362.55
  - By billing account: C1 £2,042.23, C2 £2,611.51, C3 £2,588.30, C4 £1,534.18, C5 £4,473.71, C6 £8,893.04, C7 £3,249.86, C8 £4,156.97, C9 £3,811.24, C_IC1 £714,425.52, C_IC2 £417,525.43, C_IC3 £1,045,832.66, C_IC4 £679,568.52
- Bill shock events (>=20%): 14 -- C7 2025-04-30 (36%); C7 2025-05-31 (22%); C7 2025-06-07 (80%); C8 2025-01-31 (29%); C8 2025-02-28 (24%); C8 2025-04-30 (38%); C8 2025-05-31 (35%); C8 2025-06-07 (73%); C9 2025-04-30 (24%); C9 2025-05-31 (32%); C9 2025-06-07 (72%); C_IC1 2025-06-07 (77%); C_IC2 2025-06-07 (75%); C_IC4 2025-06-07 (79%)
- Churn risk (accounts renewing in 2025): 2 at risk (≥20% churn prob): C8 38%, C9 38%

**Pricing & Margin**

- C7 (electricity): tariff £165.00-£315.00/MWh, net margin £-23.72 -- **net-negative**
- C8 (electricity): tariff £149.29-£298.77/MWh, net margin £41.83
- C9 (electricity): tariff £165.00-£315.00/MWh, net margin £195.49
- C_IC1 (electricity): tariff £167.39-£319.56/MWh, net margin £62,405.83
- C_IC2 (electricity): tariff £161.16-£307.68/MWh, net margin £29,516.09
- C_IC4 (electricity): tariff £123.20-£273.78/MWh, net margin £1,417.43

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 36, average clarity 0.742, average bill shock 24.6%, bad debt provision £2,658.91, avg complaint probability 6.3%
- Solvency signal: £630,575/customer (6 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-30.08 vs. naked (unhedged) net margin: £118.90
- hedging cost £148.98 vs. a fully unhedged book (commodity-only: actual net £-30.08 vs. naked net £118.90)
  - C8: actual £-30.08 vs. naked £118.90 -- hedging cost £148.98

**Year narrative:** 2025 produced a net gain of £93,552.93 across 6 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 14 customer(s) experienced a bill shock of >=20%.
