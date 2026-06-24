# Annual Report — The Synthetic Enterprise


## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £2,466,636.22
- Final treasury: £2,924,334.40
  (£457,698.18 net change)
- Solvency signal (final year): £325,077/customer (9 customers, OK; Ofgem floor £130/customer)
- Customer bills (all-in): £18,015,200.40
  VAT remitted to HMRC: (£866,315.84) | Revenue (ex-VAT): £17,148,884.56
  Non-commodity pass-through: (£4,015,867.35)
- Gross margin: £5,264,464.71
- Capital costs: £65,967.24
- Net margin: £5,198,497.46
- Capital cost ratio: 1.3% of gross
- Net margin as % of revenue: 30.3%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 38
- Bills issued: 1587, average clarity 0.867,
  service quality score 0.922
- Enterprise value (CLV sum across 13 billing accounts): £5,611,912.44
- Cost to serve (whole portfolio): £86,100.84, net margin after cost to serve: £5,112,396.62
- Hedge effectiveness (whole window): hedging cost £3,771,329.22 vs. a fully unhedged book (commodity-only: actual net £457,698.18 vs. naked net £4,229,027.40)

- **2021** (crisis year): net margin £43,574.72, 0 risk committee wake-up(s).
- **2022** (crisis year): net margin £-13,732.88, 9 risk committee wake-up(s).

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £5,264,464.71, capital £65,967.24, net £5,198,497.46. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 1.3% (commodity basis, comparable to old model) / 1.3% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £43,574.72 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 30.3%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £5,198,497.46
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £4,229,027.40
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £3,771,329.22 vs. a fully unhedged book (commodity-only: actual net £457,698.18 vs. naked net £4,229,027.40)
- **Best hedging decision of the run**: C_IC1, term starting
  2021-04-30 (hedge fraction 0.92) -- hedging
  protected £122,292.35 vs. going naked.
- **Worst hedging decision of the run**: C_IC3, term
  starting 2022-12-31 (hedge fraction 0.96) --
  over-hedging cost £604,090.40 vs. going
  naked.

## Segment Margin Trend

Net margin (£) by segment, by year:

| Year | I&C electricity | I&C gas | SME electricity | resi electricity | resi gas | Total |
|---|---|---|---|---|---|---|
| 2016 | £0.00 | £0.00 | £17.45 | £345.60 | £114.26 | £477.31 |
| 2017 | £37,113.69 | £0.00 | £172.74 | £560.41 | £108.19 | £37,955.03 |
| 2018 | £76,352.41 | £0.00 | £-250.79 | £381.69 | £63.89 | £76,547.19 |
| 2019 | £216,195.94 | £-36,112.79 | £224.06 | £760.52 | £173.51 | £181,241.24 |
| 2020 | £-32,709.61 | £-5,116.89 | £279.32 | £856.66 | £216.23 | £-36,474.28 |
| 2021 | £-82,016.45 | £125,577.06 | £32.69 | £354.51 | £-373.09 | £43,574.72 |
| 2022 | £-54,759.62 | £43,790.89 | £412.80 | £-1,959.93 | £-1,217.02 | £-13,732.88 |
| 2023 | £364,154.35 | £-253,415.10 | £1,360.29 | £26.64 | £-910.38 | £111,215.80 |
| 2024 | £94,489.40 | £-17,341.82 | £641.03 | £1,240.05 | £553.93 | £79,582.59 |
| 2025 | £-19,037.32 | £-3,756.29 | £0.00 | £108.76 | £-3.69 | £-22,688.54 |

## Customer Lifecycle Events

Renewal decisions rolled at each annual renewal point across the simulation window.
Retained: **52** renewals.  Lost (churned): **4** accounts.

Accounts lost before end of window: C1, C3, C5, C6

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
| C3 | 2020-06-30 | churned **CHURNED** | 0.1100 | 0.5500 | 0.9505 | 0.9704 |
| C9 | 2020-06-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.5378 |
| C4 | 2020-09-30 | renewed | 0.1400 | 0.5500 | 0.9370 | 0.2845 |
| C1 | 2020-12-30 | renewed | 0.2900 | 0.5500 | 0.8695 | 0.8047 |
| C5 | 2020-12-30 | renewed | 0.3500 | 0.3500 | 0.7725 | 0.7480 |
| C7 | 2020-12-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4829 |
| C_IC3 | 2020-12-31 | renewed | 0.0800 | 0.5500 | 0.9640 | 0.5941 |
| C2 | 2021-03-31 | renewed | 0.1100 | 0.5500 | 0.9505 | 0.6102 |
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
| C4 | 2022-09-30 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.8552 |
| C7 | 2022-12-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.0637 |
| C_IC3 | 2022-12-31 | renewed | 0.2900 | 0.5500 | 0.8695 | 0.8723 |
| C2 | 2023-03-31 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.6357 |
| C6 | 2023-03-31 | renewed | 0.2900 | 0.3500 | 0.8115 | 0.5155 |
| C8 | 2023-03-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.3785 |
| C9 | 2023-06-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.0307 |
| C4 | 2023-09-30 | renewed | 0.1700 | 0.5500 | 0.9235 | 0.6095 |
| C7 | 2023-12-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1905 |
| C_IC3 | 2023-12-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.7019 |
| C2 | 2024-03-30 | renewed | 0.1400 | 0.5500 | 0.9370 | 0.8119 |
| C6 | 2024-03-30 | churned **CHURNED** | 0.4100 | 0.3500 | 0.7335 | 0.9632 |
| C8 | 2024-03-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.0592 |
| C9 | 2024-06-29 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.0025 |
| C4 | 2024-09-29 | renewed | 0.0800 | 0.5500 | 0.9640 | 0.9018 |
| C7 | 2024-12-29 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.4099 |
| C_IC3 | 2024-12-30 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.3751 |
| C2 | 2025-03-30 | renewed | 0.1700 | 0.5500 | 0.9235 | 0.1514 |
| C8 | 2025-03-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4808 |

## Churn Prediction Basis Risk

At each renewal the company estimated churn risk from observable signals (rate change %, customer tenure). The SIM used its bill-shock model (actual bill amount relative to customer-specific thresholds). The gap is epistemic: in crisis years the company sees a rate % while the SIM sees the household-level financial shock — the same failure mode that surprised real suppliers in 2021-22.

- **Average absolute error:** 197.9%
- **Average signed error:** +59.3% (over-estimates vs SIM)
- **Renewal events with estimates:** 56

| Year | Renewals | Avg error (signed) | Avg abs error |
|------|----------|--------------------|---------------|
| 2016 | 3 | -60.8% | 60.8% |
| 2017 | 3 | -90.1% | 90.1% |
| 2018 | 4 | +436.5% | 511.2% |
| 2019 | 4 | +375.0% | 525.0% |
| 2020 | 10 | -14.0% | 148.0% |
| 2021 | 9 | -14.2% | 106.6% |
| 2022 | 7 | -16.3% | 91.5% |
| 2023 | 7 | +190.4% | 333.3% |
| 2024 | 7 | -32.3% | 124.8% |
| 2025 | 2 | -99.5% | 99.5% |

Positive error = company over-estimated churn vs SIM. Negative error = company under-estimated (more dangerous — expected retentions that were actually at risk).

## Active vs Passive Renewal Split (Phase 33a)

~35% of domestic/SME customers actively choose a new fixed deal at term end. ~65% roll to SVT by inaction — they are inert: low rate sensitivity, ~5% churn base. Crisis years (2022) force all renewals passive (no fixed deals available).

- **Total renewal events:** 56
- **Active renewers:** 17 (30%) — mean company estimate 30.9%, abs error 242.6%
- **Passive SVT-rollers:** 39 (70%) — mean company estimate 9.8%, abs error 178.4%

| Year | Active | Passive | Active est | Passive est | Active abs err | Passive abs err |
|------|--------|---------|-----------|------------|---------------|----------------|
| 2016 | 0 | 3 | 0.0% | 6.1% | 0.0% | 60.8% |
| 2017 | 0 | 3 | 0.0% | 2.4% | 0.0% | 90.1% |
| 2018 | 2 | 2 | 18.6% | 49.8% | 78.5% | 943.9% |
| 2019 | 2 | 2 | 47.5% | 0.0% | 950.0% | 100.0% |
| 2020 | 5 | 5 | 17.4% | 0.4% | 199.2% | 96.8% |
| 2021 | 3 | 6 | 53.9% | 3.3% | 155.2% | 82.3% |
| 2022 | 0 | 7 | 0.0% | 20.2% | 0.0% | 91.5% |
| 2023 | 1 | 6 | 38.5% | 15.8% | 32.8% | 383.3% |
| 2024 | 3 | 4 | 35.1% | 0.0% | 158.0% | 100.0% |
| 2025 | 1 | 1 | 0.2% | 0.0% | 99.1% | 100.0% |

Passive renewers should show lower company estimates and lower SIM churn — high abs error for passive renewers indicates the passive model needs recalibration.

## SVT Comparative Pricing — Passive Renewers (Phase 39a)

Passive renewers roll to a new fixed deal by inaction. A rate above SVT creates latent churn risk: once the customer notices they're paying more than the cap, they switch. A rate below SVT signals loyalty value — the company is rewarding inertia.

- **Passive renewal events with SVT data:** 39
- **Above SVT (at-risk):** 9 (23%)
- **Below/at SVT (protected):** 30 (77%)
- **Mean rate vs SVT premium:** -11.5%

| Year | Passive Renewals | Above SVT | Avg Premium | Avg Fixed Rate (£/MWh) | Avg SVT (£/MWh) |
|------|-----------------|-----------|-------------|----------------------|----------------|
| 2016 | 3 | 0 (0%) | -3.8% | 134.7 | 140.0 |
| 2017 | 3 | 0 (0%) | -9.7% | 126.5 | 140.0 |
| 2018 | 2 | 1 (50%) | -3.2% | 147.6 | 152.5 |
| 2019 | 2 | 0 (0%) | -26.2% | 131.6 | 178.5 |
| 2020 | 5 | 0 (0%) | -23.8% | 134.7 | 176.9 |
| 2021 | 6 | 3 (50%) | -2.5% | 178.1 | 183.8 |
| 2022 | 7 | 5 (71%) | +14.7% | 310.8 | 318.4 |
| 2023 | 6 | 0 (0%) | -39.3% | 226.3 | 415.0 |
| 2024 | 4 | 0 (0%) | -14.5% | 210.0 | 246.9 |
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
| 2016 | 17 | 11.5% | 30.8% |
| 2017 | 14 | 11.1% | 22.6% |
| 2018 | 16 | 9.7% | 20.3% |
| 2019 | 19 | 15.3% | 46.7% |
| 2020 | 22 | 19.0% | 47.8% |
| 2021 | 17 | 17.7% | 41.3% |
| 2022 | 15 | 14.0% | 52.4% |
| 2023 | 15 | 31.8% | 131.8% |
| 2024 | 15 | 11.6% | 50.2% |
| 2025 | 3 | 3.9% | 11.5% |

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
| 2021 | 9 | 1.07× | 3.75× |
| 2022 | 7 | 0.92× | 2.28× |
| 2023 | 7 | 3.33× ⚠ | 18.00× |
| 2024 | 7 | 1.25× | 3.24× |
| 2025 | 2 | 1.00× | 1.00× |

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
Total events: **4** (4 churn, 0 acquisition)

| Date | Event | Customer | Detail |
|------|-------|----------|--------|
| 2020-06-30 | CHURN | C3 | SIM p=0.11, company est=0.00 |
| 2021-12-30 | CHURN | C1 | SIM p=0.17, company est=0.03 |
| 2021-12-30 | CHURN | C5 | SIM p=0.35, company est=0.49 |
| 2024-03-30 | CHURN | C6 | SIM p=0.41, company est=0.21 |

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
| 2024-12-31 | 4 accounts | 0 active | yes |
| 2025-12-31 | 4 accounts | 0 active | yes |

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
| 2024 | 310,610 | 111,019 | 73,601 | 69,365 | 83,367 | 647,963 |  |
| 2025 | 137,705 | 47,634 | 31,649 | 31,482 | 36,678 | 285,148 |  |
| **Total** | **1,739,142** | **265,386** | **462,576** | **339,605** | **471,328** | **3,278,037** | |

Total policy cost: £3,278,037 across all years. Net margin is after deducting this. Revenue side: tariff pass-through at term-start year's levy rate — basis risk arises when cross-year terms meet a different actual levy (notably 2022 CfD rebate).

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
| 2024 | 144,288 |  |
| 2025 | 61,962 |  |
| **Total** | **885,914** | |

Total network cost: £885,914 across all years. Pass-through: tariff unit rate includes network cost at term-start year's rate; settlement deducts it — basis risk near-zero for annual contracts.

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
| 2024 | 37,573 | 76,371 | 113,944 |
| 2025 | 16,774 | 31,180 | 47,954 |
| **Total** | **171,121** | **391,537** | **562,659** |

Gas policy pass-through in tariff unit rate (CCL + GGL at term start); gas network pass-through likewise. Net basis risk near-zero for annual contracts.


## Gas Book P&L — Year by Year (Phase 32a)

Revenue = billing at fixed tariff unit rate. Wholesale = hedged + unhedged NBP cost.
Policy = gas CCL + GGL. Network = GDN + NTS. Net = gross − policy − network − capital.

| Year | Revenue £ | Wholesale £ | Gross £ | Policy £ | Network £ | Capital £ | Net £ | Net % |
|------|-----------|-------------|---------|----------|-----------|-----------|-------|-------|
| 2016 | 902 | 426 | 475 | 0 | 356 | 5 | 114 | +12.7% |
| 2017 | 1,590 | 848 | 742 | 0 | 624 | 10 | 108 | +6.8% |
| 2018 | 1,889 | 1,201 | 688 | 0 | 609 | 15 | 64 | +3.4% |
| 2019 | 135,992 | 105,132 | 30,860 | 15,273 | 50,131 | 1,395 | -35,939 | -26.4% |
| 2020 | 119,716 | 57,391 | 62,324 | 19,520 | 46,890 | 814 | -4,901 | -4.1% |
| 2021 | 296,537 | 97,288 | 199,249 | 22,523 | 50,386 | 1,136 | 125,204 | +42.2% |
| 2022 | 594,855 | 468,121 | 126,734 | 27,136 | 54,538 | 2,486 | 42,574 | +7.2% |
| 2023 | 296,651 | 437,786 | -141,135 | 32,320 | 80,454 | 416 | -254,325 | -85.7% |
| 2024 | 271,370 | 169,388 | 101,983 | 37,573 | 76,371 | 4,827 | -16,788 | -6.2% |
| 2025 | 129,120 | 81,409 | 47,711 | 16,774 | 31,180 | 3,517 | -3,760 | -2.9% |
| **Total** | **1,848,621** | **1,418,989** | **429,632** | **171,121** | **391,537** | **14,623** | **-147,649** | **-8.0%** |

Gas book net margin negative over the simulation period. Network charges (GDN + NTS, £9–18/MWh) dominate the gas non-commodity cost stack.

## Solvency Signal — Net Assets per Customer (Phase 21b)

Treasury balance ÷ active billing accounts at each year-end.
Ofgem licence floor: £0/account (positive net assets required to hold a supply licence).
Capital adequacy target: £130/dual-fuel billing account.

| Year | Treasury £ | Billing Accounts | Net Assets/Account £ | vs Floor | vs £130 Target |
|------|-----------|-----------------|----------------------|----------|----------------|
| 2016 | 2,466,899 | 9 | 274,100 | OK | OK |
| 2017 | 2,504,700 | 10 | 250,470 | OK | OK |
| 2018 | 2,496,471 | 11 | 226,952 | OK | OK |
| 2019 | 2,601,642 | 12 | 216,804 | OK | OK |
| 2020 | 2,672,581 | 13 | 205,583 | OK | OK |
| 2021 | 2,690,009 | 12 | 224,167 | OK | OK |
| 2022 | 2,547,751 | 10 | 254,775 | OK | OK |
| 2023 | 2,631,974 | 10 | 263,197 | OK | OK |
| 2024 | 2,873,173 | 10 | 287,317 | OK | OK |
| 2025 | 2,925,695 | 9 | 325,077 | OK | OK |

End-state (2025): **£325,077/account** across 9 billing accounts — above Ofgem £130 target.




## Time-of-Use Tariff Utilization (C7-C9 HH Customers)

Peak windows: 07:00–11:00 and 16:00–20:00 weekdays (periods 15-22, 33-40).
Peak rate = 1.5× flat; off-peak = 0.786× flat (revenue-neutral at 30/70 split).
ToU Premium: actual revenue vs flat-rate equivalent — positive when actual peak % > 30% design.

| Customer | Total kWh | Peak kWh | Peak % | Peak Revenue | Off-peak Revenue | Avg Peak Rate | Avg Off-peak Rate | ToU Premium |
|----------|-----------|----------|--------|-------------|-----------------|--------------|------------------|-------------|
| C7 | 120,842 | 40,643 | 33.6% | £10,313.65 | £10,685.36 | £253.76/MWh | £133.24/MWh | +2.7% |
| C8 | 106,723 | 46,761 | 43.8% | £12,646.91 | £8,506.73 | £270.46/MWh | £141.87/MWh | +9.9% |
| C9 | 109,388 | 46,156 | 42.2% | £11,812.54 | £8,474.74 | £255.93/MWh | £134.03/MWh | +8.7% |

Total HH revenue: £62,439.93 vs flat equivalent £58,349.98 (+7.0% ToU premium)

## Bill Shock Summary (2016-2025)

Month-on-month billing increase ≥20%. Bill shocks elevate SIM churn probability
via the bill-shock history model. Crisis years (2021-22) see the largest spikes.

| Year | Events | Max Spike | Worst Customer |
|------|--------|-----------|----------------|
| 2016 | 21 | 110% | C8 (2016-10-31) |
| 2017 | 27 | 85% | C8 (2017-11-30) |
| 2018 | 34 | 57% | C8 (2018-10-31) |
| 2019 | 36 | 123% | C_IC1 (2019-03-31) |
| 2020 | 32 | 132% | C_IC2 (2020-03-31) |
| 2021 | 38 | 85% | C8 (2021-11-30) |
| 2022 | 50 | 121% | C2g (2022-04-30) |
| 2023 | 33 | 134% | C_IC2 (2023-06-30) |
| 2024 | 25 | 119% | C_IC2 (2024-07-31) |
| 2025 | 23 | 81% | C_IC4 (2025-06-07) |

Total: **319** bill shock events across 10 years

**Top 10 worst single-period bill spikes:**

| Date | Customer | Spike | Eventually Churned? |
|------|----------|-------|---------------------|
| 2023-06-30 | C_IC2 | +134% | no |
| 2020-03-31 | C_IC2 | +132% | no |
| 2019-03-31 | C_IC1 | +123% | no |
| 2022-04-30 | C2g | +121% | no |
| 2022-10-31 | C4g | +121% | no |
| 2024-07-31 | C_IC2 | +119% | no |
| 2016-10-31 | C8 | +110% | no |
| 2023-07-31 | C_IC1 | +105% | no |
| 2022-12-31 | C_IC4 | +102% | no |
| 2023-10-31 | C8 | +101% | no |

## Gas Renewal Pressure (Dual-Fuel Portfolio)

Company gas churn estimates at each gas leg renewal (Phase 14b).
Threshold for elevated risk: >20% company gas churn estimate.

| Year | Renewals | Mean Est | Max Est | Elevated Risk |
|------|----------|----------|---------|---------------|
| 2016 | 1 | 9% | 9% | 0 |
| 2017 | 4 | 15% | 23% | 1 ⚠ |
| 2018 | 4 | 19% | 21% | 1 ⚠ |
| 2019 | 4 | 0% | 0% | 0 |
| 2020 | 5 | 1% | 2% | 0 |
| 2021 | 3 | 66% | 95% | 3 ⚠ |
| 2022 | 3 | 83% | 95% | 3 ⚠ |
| 2023 | 3 | 0% | 0% | 0 |
| 2024 | 3 | 0% | 0% | 0 |
| 2025 | 1 | 0% | 0% | 0 |

**Top elevated gas renewals (>20% estimated churn):**

| Date | Customer | Old Rate (£/MWh) | New Rate (£/MWh) | Est Churn |
|------|----------|-----------------|-----------------|-----------|
| 2021-12-31 | C_IC3g | £14.6 | £82.2 (+463%) | 95% |
| 2022-03-31 | C2g | £30.6 | £95.0 (+211%) | 95% |
| 2022-09-30 | C4g | £35.0 | £95.0 (+171%) | 95% |
| 2021-09-30 | C4g | £15.2 | £35.0 (+130%) | 81% |
| 2022-12-31 | C_IC3g | £82.2 | £156.7 (+91%) | 58% |

## Retention Strategy P&L

### Aggregate (2016-2025)

| Metric | Value |
|--------|-------|
| Offers made | 20 |
| Retained | 19 (95%) |
| Churned despite offer | 1 |
| Total offer cost (foregone margin) | £474,048.19 |
| Margin saved (retained customers' terms) | £2,411,063.13 |
| Wasted offer cost (churned anyway) | £150.29 |
| **Net ROI of retention strategy** | **£1,937,014.94** |
| Acquisition cost avoided (retained customers) | £3,100.00 |
| **Full economic ROI (margin + acq savings)** | **£1,940,114.94** |

Missed opportunities (churns with no offer): **3** (£3,392.63 expected margin lost without offer)
- **Below threshold** (churn estimate under 30%): 3 (£3,392.63 margin lost) — Phase 13c bill burden signal reduces this for high-spend SME customers

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2018 | 1 | 1 | £21746.79 | £157840.90 | £136094.11 | £0.00 |
| 2019 | 2 | 2 | £41007.73 | £296884.49 | £255876.76 | £0.00 |
| 2020 | 4 | 4 | £32078.60 | £273770.82 | £241692.21 | £386.28 |
| 2021 | 4 | 3 | £92062.78 | £381314.39 | £289251.60 | £95.45 |
| 2022 | 3 | 3 | £159070.80 | £440402.36 | £281331.56 | £0.00 |
| 2023 | 3 | 3 | £59350.60 | £426257.92 | £366907.32 | £0.00 |
| 2024 | 3 | 3 | £68730.88 | £434592.26 | £365861.38 | £2910.90 |

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
| 2021-12-30 | C5 | 0.49 | 3% | £150.29 | £2061.87 | £400 | £-150.29 | churned_despite_offer |
| 2021-12-31 | C_IC3 | 0.95 | 8% | £60514.40 | £124910.09 | £150 | £64395.70 | retained |
| 2022-04-30 | C_IC2 | 0.95 | 8% | £24305.80 | £78128.37 | £150 | £53822.57 | retained |
| 2022-05-30 | C_IC1 | 0.95 | 8% | £48718.47 | £203804.57 | £150 | £155086.10 | retained |
| 2022-12-31 | C_IC3 | 0.95 | 8% | £86046.54 | £158469.43 | £150 | £72422.89 | retained |
| 2023-03-31 | C6 | 0.39 | 3% | £210.46 | £3088.43 | £400 | £2877.97 | retained |
| 2023-05-30 | C_IC2 | 0.67 | 5% | £13170.02 | £139453.49 | £150 | £126283.46 | retained |
| 2023-06-29 | C_IC1 | 0.95 | 8% | £45970.12 | £283716.01 | £150 | £237745.89 | retained |
| 2024-06-28 | C_IC2 | 0.49 | 3% | £6076.68 | £135644.45 | £150 | £129567.77 | retained |
| 2024-07-28 | C_IC1 | 0.95 | 8% | £31705.79 | £267552.93 | £150 | £235847.14 | retained |
| 2024-12-30 | C_IC3 | 0.85 | 8% | £30948.41 | £31394.88 | £150 | £446.47 | retained |

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

**Full-history EV:** £5,611,912.44 — anchored to all 10 years including crisis losses
**3yr-trailing EV:** £182,103.61 — based on last 3 years (2023, 2024, 2025), reflecting current earning power

The gap between the two is the weight of unrecovered crisis losses in the CLV anchor.
When trailing EV > full-history EV, the company's recent performance is better than its
cumulative history suggests — a recovery signal.

**Portfolio net margin by year:**

| Year | Net margin |
|------|----------:|
| 2016 | £477.31 |
| 2017 | £37,955.03 |
| 2018 | £76,547.19 |
| 2019 | £181,241.24 |
| 2020 | £-36,474.28 |
| 2021 | £43,574.72 |
| 2022 | £-13,732.88 |
| 2023 | £111,215.80 | ← trailing
| 2024 | £79,582.59 | ← trailing
| 2025 | £-22,688.54 | ← trailing

**CLV by billing account:**

| Account | Full-history CLV | 3yr-trailing CLV |
|---------|----------------:|----------------:|
| C1 | £2,646.15 | — |
| C2 | £6,198.55 | £179.74 |
| C3 | £3,137.84 | — |
| C4 | £3,111.98 | £-901.28 |
| C5 | £9,273.41 | — |
| C6 | £14,308.70 | £3,232.63 |
| C7 | £7,339.07 | £-178.63 |
| C8 | £8,127.85 | £409.15 |
| C9 | £10,260.78 | £1,584.35 |
| C_IC1 | £1,793,670.45 | £541,317.17 |
| C_IC2 | £1,003,970.97 | £239,338.25 |
| C_IC3 | £2,720,297.39 | £-39,884.07 |
| C_IC4 | £29,569.32 | £-562,993.69 |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C_IC1 | C_IC2 | C_IC3 | C_IC4 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £1,726.49 | — | — | — | £5,007.86 | — | £4,168.20 | — | — | — | — | — | — |
| 2017 | £1,918.54 | £5,666.34 | £2,581.88 | £3,402.39 | £6,817.61 | £10,541.48 | £4,505.21 | £7,878.31 | £5,891.28 | — | — | — | — |
| 2018 | £1,934.31 | £4,672.57 | £2,558.66 | £2,906.60 | £5,951.75 | £7,706.43 | £4,492.88 | £6,334.54 | £5,832.06 | £1,462,228.40 | — | — | — |
| 2019 | £1,814.63 | £3,845.63 | £2,466.63 | £3,138.89 | £6,288.69 | £8,662.24 | £5,476.25 | £5,878.56 | £6,199.81 | £1,311,380.66 | £868,520.16 | — | — |
| 2020 | £1,951.58 | £4,638.66 | £2,072.15 | £2,741.45 | £6,963.68 | £8,536.75 | £4,633.89 | £5,875.89 | £5,871.51 | £855,227.01 | £511,287.01 | £1,511,183.86 | £24,868.19 |
| 2021 | £1,753.36 | £4,342.75 | £2,018.40 | £2,274.10 | £6,333.28 | £8,021.28 | £4,566.55 | £5,805.45 | £4,749.60 | £793,311.11 | £425,326.81 | £1,596,536.36 | £19,845.53 |
| 2022 | £1,700.15 | £3,608.10 | £1,947.47 | £1,361.56 | £5,690.63 | £8,172.50 | £3,552.78 | £5,592.11 | £5,359.92 | £966,887.64 | £450,132.08 | £1,268,893.34 | £14,838.48 |
| 2023 | £1,728.28 | £3,682.40 | £2,015.64 | £947.01 | £5,859.49 | £9,166.72 | £3,785.43 | £5,584.19 | £5,875.99 | £994,238.86 | £506,917.05 | £1,243,618.11 | £17,605.47 |
| 2024 | £1,695.21 | £4,148.85 | £2,078.58 | £1,700.28 | £6,015.20 | £8,969.23 | £4,080.78 | £5,854.73 | £5,940.97 | £1,048,489.96 | £507,492.57 | £1,509,734.50 | £17,974.37 |
| 2025 | £1,706.99 | £3,690.03 | £1,984.40 | £1,816.87 | £5,786.47 | £8,671.67 | £4,453.68 | £5,502.70 | £6,008.32 | £1,127,922.82 | £570,813.78 | £1,464,274.17 | £19,558.27 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £4,783.38, range £34.51–£26,062.65.

- C1: cost to serve £389.84, net margin after CTS £1,411.04
- C1g: cost to serve £47.16, net margin after CTS £811.23
- C2: cost to serve £746.87, net margin after CTS £5,623.53
- C2g: cost to serve £131.14, net margin after CTS £1,881.54
- C3: cost to serve £263.70, net margin after CTS £1,122.03
- C3g: cost to serve £34.51, net margin after CTS £668.44
- C4: cost to serve £644.76, net margin after CTS £3,180.88
- C4g: cost to serve £162.91, net margin after CTS £240.71
- C5: cost to serve £867.62, net margin after CTS £8,084.86
- C6: cost to serve £1,266.06, net margin after CTS £16,129.33
- C7: cost to serve £939.11, net margin after CTS £9,018.48
- C8: cost to serve £928.50, net margin after CTS £10,953.01
- C9: cost to serve £897.47, net margin after CTS £11,819.92
- C_IC1: cost to serve £20,820.15, net margin after CTS £2,030,681.67
- C_IC2: cost to serve £11,502.02, net margin after CTS £918,870.50
- C_IC3: cost to serve £26,062.65, net margin after CTS £1,705,894.89
- C_IC3g: cost to serve £9,224.23, net margin after CTS £416,430.41
- C_IC4: cost to serve £11,172.13, net margin after CTS £21,351.71 — MARGIN_SQUEEZE (below 2% benchmark)

**Activity-Based Pricing Actions**

The following 1 customer(s) are profitable but below the 2% net-margin benchmark (MARGIN_SQUEEZE): C_IC4


## Margin Recovery Surcharges (Phase 16c + 19a)

Company applied 34 recovery surcharge(s) at renewal based on prior-term losses (8 gas). Avg surcharge: 13.7%.

| Customer | Commodity | Term start | Prior margin | Prior revenue | Surcharge | Rate before | Rate after |
|----------|-----------|------------|-------------|--------------|-----------|------------|-----------|
| C4 | electricity | 2017-10-01 | £-29.11 | £562.14 | +0.2% | £113.33/MWh | £113.67/MWh |
| C_IC1 | electricity | 2018-01-31 | £-5,694.56 | £10,901.23 | +20.0% | £99.09/MWh | £132.90/MWh |
| C1 | electricity | 2018-12-31 | £-35.37 | £461.69 | +2.7% | £148.23/MWh | £154.56/MWh |
| C5 | electricity | 2018-12-31 | £-207.59 | £2,298.54 | +4.0% | £148.23/MWh | £156.24/MWh |
| C_IC2 | electricity | 2019-01-31 | £-3,300.82 | £6,376.41 | +20.0% | £123.82/MWh | £170.88/MWh |
| C_IC1 | electricity | 2019-03-02 | £-7,218.30 | £10,243.03 | +20.0% | £121.46/MWh | £165.97/MWh |
| C_IC3g | gas | 2020-01-01 | £-36,112.79 | £134,045.32 | +20.0% | £13.42/MWh | £15.58/MWh |
| C_IC2 | electricity | 2020-03-01 | £-3,904.90 | £3,444.18 | +20.0% | £96.22/MWh | £132.78/MWh |
| C_IC1 | electricity | 2020-03-31 | £-8,041.06 | £6,326.95 | +20.0% | £96.89/MWh | £110.45/MWh |
| C_IC2 | electricity | 2021-03-31 | £-3,729.85 | £5,726.15 | +20.0% | £120.96/MWh | £154.46/MWh |
| C_IC1 | electricity | 2021-04-30 | £-7,006.00 | £14,511.74 | +20.0% | £115.47/MWh | £143.78/MWh |
| C4 | electricity | 2021-09-30 | £-122.30 | £622.95 | +14.6% | £181.67/MWh | £218.11/MWh |
| C4g | gas | 2021-09-30 | £-125.76 | £334.71 | +20.0% | £43.19/MWh | £56.02/MWh |
| C1 | electricity | 2021-12-30 | £-35.37 | £523.21 | +1.8% | £247.72/MWh | £260.55/MWh |
| C5 | electricity | 2021-12-30 | £-227.33 | £2,695.44 | +3.4% | £247.72/MWh | £264.83/MWh |
| C2g | gas | 2022-03-31 | £-58.20 | £458.69 | +7.7% | £103.60/MWh | £125.16/MWh |
| C_IC2 | electricity | 2022-04-30 | £-1,292.09 | £17,661.75 | +2.3% | £273.88/MWh | £299.20/MWh |
| C_IC1 | electricity | 2022-05-30 | £-4,406.97 | £22,384.38 | +14.7% | £252.29/MWh | £302.36/MWh |
| C9 | electricity | 2022-06-30 | £-170.27 | £1,951.48 | +3.7% | £296.06/MWh | £305.85/MWh |
| C4 | electricity | 2022-09-30 | £-380.92 | £1,021.16 | +20.0% | £321.02/MWh | £371.82/MWh |
| C4g | gas | 2022-09-30 | £-791.90 | £770.00 | +20.0% | £136.87/MWh | £188.88/MWh |
| C7 | electricity | 2022-12-30 | £-1,640.56 | £2,294.28 | +20.0% | £331.55/MWh | £390.17/MWh |
| C_IC3 | electricity | 2022-12-31 | £-150,778.91 | £931,297.72 | +11.2% | £233.88/MWh | £265.64/MWh |
| C2 | electricity | 2023-03-31 | £-263.78 | £2,176.45 | +7.1% | £340.83/MWh | £419.86/MWh |
| C2g | gas | 2023-03-31 | £-222.05 | £1,425.00 | +10.6% | £117.34/MWh | £149.22/MWh |
| C_IC2 | electricity | 2023-05-30 | £-4,193.41 | £7,055.33 | +20.0% | £190.87/MWh | £259.02/MWh |
| C_IC1 | electricity | 2023-06-29 | £-8,414.36 | £17,979.18 | +20.0% | £213.85/MWh | £284.31/MWh |
| C4 | electricity | 2023-09-30 | £-545.96 | £1,701.85 | +20.0% | £216.87/MWh | £247.24/MWh |
| C4g | gas | 2023-09-30 | £-1,481.14 | £2,090.00 | +20.0% | £50.20/MWh | £69.27/MWh |
| C7 | electricity | 2023-12-30 | £-248.02 | £3,896.40 | +1.4% | £223.86/MWh | £215.57/MWh |
| C_IC3g | gas | 2023-12-31 | £-252,917.30 | £294,338.38 | +20.0% | £40.88/MWh | £56.41/MWh |
| C_IC2 | electricity | 2024-06-28 | £-5,916.03 | £7,659.10 | +20.0% | £143.32/MWh | £197.78/MWh |
| C_IC1 | electricity | 2024-07-28 | £-10,612.90 | £14,454.77 | +20.0% | £141.21/MWh | £194.87/MWh |
| C_IC3g | gas | 2024-12-30 | £-17,160.47 | £268,215.17 | +1.4% | £41.46/MWh | £41.59/MWh |


## Portfolio Learning Premium (Phase 17a + 19a)

Company applied portfolio premium adjustments at 117 renewal(s) (31 gas) based on recent portfolio-wide margin rates: 88 surcharge(s), 29 discount(s).

| Customer | Commodity | Term start | Mean recent margin | Portfolio premium | Rate before | Rate after |
|----------|-----------|------------|-------------------|-------------------|------------|-----------|
| C1 | electricity | 2016-12-31 | 2.2% | +2.9% | £130.93/MWh | £134.71/MWh |
| C1g | gas | 2016-12-31 | 10.4% | -1.2% | £25.47/MWh | £25.16/MWh |
| C5 | electricity | 2016-12-31 | 1.3% | +3.3% | £130.93/MWh | £135.30/MWh |
| C7 | electricity | 2016-12-31 | 3.4% | +2.3% | £130.93/MWh | £133.95/MWh |
| C2 | electricity | 2017-04-01 | 10.3% | -1.2% | £129.36/MWh | £127.87/MWh |
| C2g | gas | 2017-04-01 | 9.7% | -0.8% | £28.85/MWh | £28.61/MWh |
| C6 | electricity | 2017-04-01 | 9.6% | -0.8% | £129.36/MWh | £128.35/MWh |
| C8 | electricity | 2017-04-01 | 9.2% | -0.6% | £129.36/MWh | £128.60/MWh |
| C3 | electricity | 2017-07-01 | 10.1% | -1.0% | £116.98/MWh | £115.76/MWh |
| C3g | gas | 2017-07-01 | 7.3% | +0.3% | £25.97/MWh | £26.06/MWh |
| C9 | electricity | 2017-07-01 | 6.7% | +0.6% | £116.98/MWh | £117.73/MWh |
| C4 | electricity | 2017-10-01 | 7.8% | +0.1% | £113.33/MWh | £113.47/MWh |
| C4g | gas | 2017-10-01 | 6.7% | +0.7% | £25.27/MWh | £25.44/MWh |
| C1 | electricity | 2017-12-31 | 6.0% | +1.0% | £121.45/MWh | £122.65/MWh |
| C1g | gas | 2017-12-31 | 4.6% | +1.7% | £31.71/MWh | £32.24/MWh |
| C5 | electricity | 2017-12-31 | 0.5% | +3.7% | £121.45/MWh | £126.00/MWh |
| C7 | electricity | 2017-12-31 | -2.5% | +5.2% | £121.45/MWh | £127.81/MWh |
| C_IC1 | electricity | 2018-01-31 | -15.5% | +11.8% | £99.09/MWh | £110.75/MWh |
| C2 | electricity | 2018-04-01 | -5.7% | +6.9% | £136.23/MWh | £145.59/MWh |
| C2g | gas | 2018-04-01 | 5.5% | +1.3% | £34.79/MWh | £35.23/MWh |
| C6 | electricity | 2018-04-01 | -6.4% | +7.2% | £136.23/MWh | £146.05/MWh |
| C8 | electricity | 2018-04-01 | 5.4% | +1.3% | £136.23/MWh | £137.99/MWh |
| C3 | electricity | 2018-07-01 | 7.3% | +0.4% | £136.06/MWh | £136.57/MWh |
| C3g | gas | 2018-07-01 | 5.0% | +1.5% | £30.93/MWh | £31.39/MWh |
| C9 | electricity | 2018-07-01 | 0.7% | +3.7% | £136.06/MWh | £141.03/MWh |
| C4 | electricity | 2018-10-01 | 4.3% | +1.8% | £134.83/MWh | £137.30/MWh |
| C4g | gas | 2018-10-01 | 4.5% | +1.7% | £31.37/MWh | £31.92/MWh |
| C1 | electricity | 2018-12-31 | 4.9% | +1.6% | £148.23/MWh | £150.56/MWh |
| C1g | gas | 2018-12-31 | 4.7% | +1.7% | £38.38/MWh | £39.02/MWh |
| C5 | electricity | 2018-12-31 | 5.4% | +1.3% | £148.23/MWh | £150.18/MWh |
| C7 | electricity | 2018-12-31 | 5.3% | +1.3% | £148.23/MWh | £150.20/MWh |
| C_IC2 | electricity | 2019-01-31 | -28.1% | +15.0% | £123.82/MWh | £142.40/MWh |
| C_IC1 | electricity | 2019-03-02 | -19.7% | +13.9% | £121.46/MWh | £138.31/MWh |
| C2 | electricity | 2019-04-01 | 3.5% | +2.3% | £155.73/MWh | £159.26/MWh |
| C2g | gas | 2019-04-01 | -1.6% | +4.8% | £35.46/MWh | £37.16/MWh |
| C6 | electricity | 2019-04-01 | 6.2% | +0.9% | £155.73/MWh | £157.17/MWh |
| C8 | electricity | 2019-04-01 | 25.9% | -5.0% | £155.73/MWh | £147.94/MWh |
| C3 | electricity | 2019-07-01 | 19.8% | -5.0% | £133.43/MWh | £126.76/MWh |
| C3g | gas | 2019-07-01 | -1.7% | +4.8% | £27.26/MWh | £28.58/MWh |
| C9 | electricity | 2019-07-01 | 9.4% | -0.7% | £133.43/MWh | £132.49/MWh |
| C4 | electricity | 2019-10-01 | 9.4% | -0.7% | £128.04/MWh | £127.16/MWh |
| C4g | gas | 2019-10-01 | 4.6% | +1.7% | £22.67/MWh | £23.05/MWh |
| C1 | electricity | 2019-12-31 | 8.8% | -0.4% | £129.65/MWh | £129.11/MWh |
| C1g | gas | 2019-12-31 | 4.6% | +1.7% | £23.39/MWh | £23.79/MWh |
| C5 | electricity | 2019-12-31 | 5.2% | +1.4% | £129.65/MWh | £131.47/MWh |
| C7 | electricity | 2019-12-31 | 4.7% | +1.7% | £129.65/MWh | £131.82/MWh |
| C_IC3 | electricity | 2020-01-01 | 2.6% | +2.7% | £45.89/MWh | £47.13/MWh |
| C_IC3g | gas | 2020-01-01 | 14.6% | -3.3% | £13.42/MWh | £12.98/MWh |
| C_IC2 | electricity | 2020-03-01 | -97.9% | +15.0% | £96.22/MWh | £110.65/MWh |
| C2 | electricity | 2020-03-31 | -89.2% | +15.0% | £130.89/MWh | £150.52/MWh |
| C2g | gas | 2020-03-31 | 12.6% | -2.3% | £24.08/MWh | £23.52/MWh |
| C6 | electricity | 2020-03-31 | -46.1% | +15.0% | £130.89/MWh | £150.52/MWh |
| C8 | electricity | 2020-03-31 | -14.7% | +11.3% | £130.89/MWh | £145.72/MWh |
| C_IC1 | electricity | 2020-03-31 | 22.6% | -5.0% | £96.89/MWh | £92.05/MWh |
| C3 | electricity | 2020-06-30 | 19.9% | -5.0% | £120.23/MWh | £114.22/MWh |
| C9 | electricity | 2020-06-30 | 19.9% | -5.0% | £120.23/MWh | £114.22/MWh |
| C4 | electricity | 2020-09-30 | 16.5% | -4.3% | £116.26/MWh | £111.32/MWh |
| C4g | gas | 2020-09-30 | 13.4% | -2.7% | £15.64/MWh | £15.21/MWh |
| C1 | electricity | 2020-12-30 | 8.5% | -0.3% | £136.59/MWh | £136.24/MWh |
| C1g | gas | 2020-12-30 | -1.1% | +4.5% | £22.29/MWh | £23.30/MWh |
| C5 | electricity | 2020-12-30 | 1.4% | +3.3% | £136.59/MWh | £141.11/MWh |
| C7 | electricity | 2020-12-30 | -7.6% | +7.8% | £136.59/MWh | £147.24/MWh |
| C_IC3 | electricity | 2020-12-31 | -8.2% | +8.1% | £50.53/MWh | £54.64/MWh |
| C_IC3g | gas | 2020-12-31 | -10.6% | +9.3% | £13.35/MWh | £14.60/MWh |
| C2 | electricity | 2021-03-31 | -28.8% | +15.0% | £157.96/MWh | £181.66/MWh |
| C2g | gas | 2021-03-31 | 1.2% | +3.4% | £29.57/MWh | £30.58/MWh |
| C6 | electricity | 2021-03-31 | -26.8% | +15.0% | £157.96/MWh | £181.66/MWh |
| C8 | electricity | 2021-03-31 | -24.7% | +15.0% | £157.96/MWh | £181.66/MWh |
| C_IC2 | electricity | 2021-03-31 | -4.8% | +6.4% | £120.96/MWh | £128.71/MWh |
| C_IC1 | electricity | 2021-04-30 | 0.5% | +3.8% | £115.47/MWh | £119.82/MWh |
| C9 | electricity | 2021-06-30 | 4.6% | +1.7% | £154.99/MWh | £157.64/MWh |
| C4 | electricity | 2021-09-30 | -1.5% | +4.7% | £181.67/MWh | £190.27/MWh |
| C4g | gas | 2021-09-30 | -8.2% | +8.1% | £43.19/MWh | £46.68/MWh |
| C1 | electricity | 2021-12-30 | 1.3% | +3.4% | £247.72/MWh | £256.04/MWh |
| C5 | electricity | 2021-12-30 | 1.3% | +3.4% | £247.72/MWh | £256.04/MWh |
| C7 | electricity | 2021-12-30 | 1.3% | +3.4% | £247.72/MWh | £256.04/MWh |
| C_IC3 | electricity | 2021-12-31 | -24.3% | +15.0% | £161.66/MWh | £185.91/MWh |
| C_IC3g | gas | 2021-12-31 | -24.5% | +15.0% | £71.47/MWh | £82.19/MWh |
| C2 | electricity | 2022-03-31 | -37.4% | +15.0% | £329.80/MWh | £379.27/MWh |
| C2g | gas | 2022-03-31 | -16.4% | +12.2% | £103.60/MWh | £116.22/MWh |
| C6 | electricity | 2022-03-31 | -31.1% | +15.0% | £329.80/MWh | £379.27/MWh |
| C8 | electricity | 2022-03-31 | -11.2% | +9.6% | £329.80/MWh | £361.42/MWh |
| C_IC2 | electricity | 2022-04-30 | -5.5% | +6.8% | £273.88/MWh | £292.43/MWh |
| C_IC1 | electricity | 2022-05-30 | -1.0% | +4.5% | £252.29/MWh | £263.64/MWh |
| C9 | electricity | 2022-06-30 | 8.8% | -0.4% | £296.06/MWh | £294.86/MWh |
| C4 | electricity | 2022-09-30 | 15.0% | -3.5% | £321.02/MWh | £309.85/MWh |
| C4g | gas | 2022-09-30 | -30.9% | +15.0% | £136.87/MWh | £157.40/MWh |
| C7 | electricity | 2022-12-30 | 11.9% | -1.9% | £331.55/MWh | £325.14/MWh |
| C_IC3 | electricity | 2022-12-31 | 3.7% | +2.1% | £233.88/MWh | £238.90/MWh |
| C_IC3g | gas | 2022-12-31 | -45.5% | +15.0% | £136.28/MWh | £156.73/MWh |
| C2 | electricity | 2023-03-31 | -22.6% | +15.0% | £340.83/MWh | £391.95/MWh |
| C2g | gas | 2023-03-31 | -41.3% | +15.0% | £117.34/MWh | £134.94/MWh |
| C6 | electricity | 2023-03-31 | -15.1% | +11.6% | £340.83/MWh | £380.21/MWh |
| C8 | electricity | 2023-03-31 | -6.8% | +7.4% | £340.83/MWh | £366.05/MWh |
| C_IC2 | electricity | 2023-05-30 | -18.2% | +13.1% | £190.87/MWh | £215.85/MWh |
| C_IC1 | electricity | 2023-06-29 | -13.6% | +10.8% | £213.85/MWh | £236.93/MWh |
| C9 | electricity | 2023-06-30 | -3.0% | +5.5% | £275.32/MWh | £290.52/MWh |
| C4 | electricity | 2023-09-30 | 18.1% | -5.0% | £216.87/MWh | £206.03/MWh |
| C4g | gas | 2023-09-30 | -39.7% | +15.0% | £50.20/MWh | £57.73/MWh |
| C7 | electricity | 2023-12-30 | 34.1% | -5.0% | £223.86/MWh | £212.67/MWh |
| C_IC3 | electricity | 2023-12-31 | 24.0% | -5.0% | £101.84/MWh | £96.75/MWh |
| C_IC3g | gas | 2023-12-31 | -27.9% | +15.0% | £40.88/MWh | £47.01/MWh |
| C2 | electricity | 2024-03-30 | -19.1% | +13.6% | £213.76/MWh | £242.72/MWh |
| C2g | gas | 2024-03-30 | -11.8% | +9.9% | £56.57/MWh | £62.17/MWh |
| C6 | electricity | 2024-03-30 | -22.7% | +15.0% | £213.76/MWh | £245.82/MWh |
| C8 | electricity | 2024-03-30 | -22.7% | +15.0% | £213.76/MWh | £245.82/MWh |
| C_IC2 | electricity | 2024-06-28 | -34.2% | +15.0% | £143.32/MWh | £164.82/MWh |
| C9 | electricity | 2024-06-29 | -27.0% | +15.0% | £198.22/MWh | £227.96/MWh |
| C_IC1 | electricity | 2024-07-28 | -27.3% | +15.0% | £141.21/MWh | £162.39/MWh |
| C4 | electricity | 2024-09-29 | -0.9% | +4.5% | £203.72/MWh | £212.84/MWh |
| C4g | gas | 2024-09-29 | 16.4% | -4.2% | £45.47/MWh | £43.57/MWh |
| C7 | electricity | 2024-12-29 | 17.8% | -4.9% | £220.98/MWh | £210.18/MWh |
| C_IC3 | electricity | 2024-12-30 | 9.0% | -0.5% | £93.81/MWh | £93.35/MWh |
| C_IC3g | gas | 2024-12-30 | 10.1% | -1.1% | £41.46/MWh | £41.01/MWh |
| C2 | electricity | 2025-03-30 | -22.1% | +15.0% | £246.37/MWh | £283.33/MWh |
| C2g | gas | 2025-03-30 | 1.4% | +3.3% | £61.26/MWh | £63.29/MWh |
| C8 | electricity | 2025-03-30 | -29.3% | +15.0% | £246.37/MWh | £283.33/MWh |

## Churn Avoidability Analysis (Phase 17b)

Total no-offer churns: **3** | Blind misses: **3** | Deliberate passes (uneconomical): **0**

- Blind misses: company estimated churn < 30% → no offer made. Of these, 1 had SIM p ≥ 30% (detectable with a better model).
- Deliberate passes: company estimated churn ≥ 30% but the retention offer was uneconomical (margin + acq cost < offer cost).

**Estimated margin at stake** — blind: £3,392.63 | deliberate: £0.00 | total: £3,392.63

| Customer | Date | Reason | Co. est | SIM p | Detectable? | Margin at stake |
|----------|------|--------|---------|-------|-------------|----------------|
| C3 | 2020-06-30 | Blind miss | 0.00 | 0.11 | No | £386.28 |
| C1 | 2021-12-30 | Blind miss | 0.03 | 0.17 | No | £95.45 |
| C6 | 2024-03-30 | Blind miss | 0.21 | 0.41 | Yes | £2,910.90 |

## Dual-Fuel Account P&L (Phase 17d)

5 dual-fuel account pair(s): electricity leg + gas leg combined.

| Account | Elec net | Gas net | Combined net | Gas accretive? |
|---------|----------|---------|-------------|---------------|
| C2+C2g | £238.38 | £359.34 | £597.71 | Yes |
| C1+C1g | £45.94 | £140.13 | £186.07 | Yes |
| C3+C3g | £24.34 | £144.69 | £169.03 | Yes |
| C4+C4g | £-819.18 | £-1,918.33 | £-2,737.51 | No |
| C_IC3+C_IC3g | £93,714.76 | £-146,374.94 | £-52,660.18 | No |

Gas accretive in 3/5 dual-fuel accounts. Total gas net margin: £-147,649.11.

## Customer P&L Ranking (Phase 17c)

Lifetime net margin: £457,698.18 across 18 billing accounts. Revenue: £13,118,827.52.

| # | Customer | Tariff | Revenue | Gross margin | Capital | Net margin | Net margin % |
|---|----------|--------|---------|-------------|---------|------------|-------------|
| 1 | C_IC1 | fixed | £3,320,404.77 | £2,051,501.82 | £18,437.84 | £1,044,109.06 | 31.4% |
| 2 | C_IC2 | fixed | £1,556,767.97 | £930,372.52 | £8,676.07 | £466,829.11 | 30.0% |
| 3 | C_IC3 | pass_through | £4,568,865.13 | £1,731,957.54 | £23,338.59 | £93,714.76 | 2.1% |
| 4 | C6 | fixed | £30,629.03 | £17,395.39 | £218.32 | £3,109.56 | 10.2% |
| 5 | C9 | fixed | £20,287.28 | £12,717.38 | £123.03 | £2,446.07 | 12.1% |
| 6 | C8 | fixed | £21,153.64 | £11,881.51 | £141.63 | £1,916.87 | 9.1% |
| 7 | C2g | fixed | £6,030.55 | £2,012.68 | £84.61 | £359.34 | 6.0% |
| 8 | C2 | fixed | £12,071.97 | £6,370.40 | £84.77 | £238.38 | 2.0% |
| 9 | C3g | fixed | £1,496.50 | £702.95 | £9.77 | £144.69 | 9.7% |
| 10 | C1g | fixed | £2,014.25 | £858.39 | £14.90 | £140.13 | 7.0% |
| 11 | C1 | fixed | £2,995.33 | £1,800.88 | £15.65 | £45.94 | 1.5% |
| 12 | C3 | fixed | £2,187.60 | £1,385.73 | £9.45 | £24.34 | 1.1% |
| 13 | C5 | fixed | £14,777.21 | £8,952.48 | £79.54 | £-219.97 | -1.5% |
| 14 | C4 | fixed | £8,344.99 | £3,825.63 | £71.22 | £-819.18 | -9.8% |
| 15 | C7 | fixed | £20,999.01 | £9,957.60 | £148.53 | £-1,177.51 | -5.6% |
| 16 | C4g | fixed | £7,647.74 | £403.62 | £132.04 | £-1,918.33 | -25.1% |
| 17 | C_IC3g | pass_through | £1,831,432.12 | £425,654.64 | £14,381.28 | £-146,374.94 | -8.0% |
| 18 | C_IC4 | flex | £1,690,722.42 | £32,523.85 | £0.00 | £-1,004,870.14 | -59.4% |

## Revenue & Margin Sanity Check

### Portfolio P&L Waterfall
| Line | £ | % Revenue |
|------|---|-----------|
| Supply Revenue (ex-VAT, ex-policy passthrough) | £13,118,828 | 100.0% |
| Wholesale cost | -£7,868,552 | 60.0% |
| **Gross supply margin** | **£5,250,275** | **40.0%** |
| Policy + Network costs | -£4,726,610 | 36.0% |
| Capital cost | -£65,967 | 0.5% |
| **Net supply margin** | **£457,698** | **3.5%** |

> *The ledger's `net_margin_gbp` (£5,198,497) is gross − capital only, not final net.*

### Segment Net Margin vs Benchmark
| Segment | Revenue | Gross% | Net% | Benchmark | Status |
|---------|---------|--------|------|-----------|--------|
| I&C/elec | £11,136,760 | 42.6% | 5.4% | large spread -20% to +15% (crisis) | ✓ |
| I&C/gas | £1,831,432 | 23.2% | -8.0% | commodity 2-6%, pass-through ≈0 | ✓ |
| SME/elec | £45,406 | 58.0% | 6.4% | CMA 3-8% | ✓ |
| resi/elec | £88,040 | 54.5% | 3.0% | Ofgem CMA 2-5% | ✓ |
| resi/gas | £17,189 | 23.1% | -7.4% | Ofgem CMA 2-4% | ⚠ ANOMALY |

### Per-Customer Net Margin Flags
No individual customers outside ±40.0/80.0 thresholds.

**SANITY CHECK: ANOMALIES DETECTED**
- Segment resi/gas net -7.4% (benchmark Ofgem CMA 2-4%)
## Transaction Log

Total events: 3,324,230

| Event type | Count |
|------------|-------|
| acquisition_spend_event | 4 |
| bad_debt_event | 1,587 |
| billing_event | 1,587 |
| capital_charge_event | 1,600,920 |
| fixed_cost_event | 114 |
| non_commodity_cost_event | 1,587 |
| payment_received_event | 1,587 |
| settlement_event | 1,715,257 |
| vat_remittance_event | 1,587 |

**Cash-flow waterfall (from ledger)**

| Flow | Amount |
|------|--------|
| Customer bills (all-in) | £18,015,200.40 |
|   Less: VAT remitted to HMRC | (£866,315.84) |
| = Revenue (ex-VAT) | £17,148,884.56 |
| Less: non-commodity pass-through | (£4,015,867.35) |
| Wholesale cost (settlement events) | (£7,868,552.50) |
| Gross margin | £5,264,464.71 |
| Capital charges | (£65,967.24) |
| Net margin | £5,198,497.46 |

_Cash reconciliation: of £18,015,200.40 billed, bad debt of £360,265.65 was written off, leaving £17,654,934.74 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £5,704,547.65._

| Acquisition spend | (£1,100.00) |
| Fixed overhead | (£5,700.00) |
| Operating net margin | £5,191,697.46 |

## Growth & Acquisition

**Mandate:** `flat`  **Acquisition cost:** resi £150 / SME £400  **Fixed overhead:** £50/month

**Acquisition activity by year**

| Year | Attempts | Wins | Win Rate | Spend |
|------|----------|------|----------|-------|
| 2020 | 1 | 0 | 0% | £150.00 |
| 2021 | 2 | 0 | 0% | £550.00 |
| 2024 | 1 | 0 | 0% | £400.00 |

**Total:** 4 attempts, 0 wins (0% win rate), £1,100.00 total spend

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £5,191,697.46

## 2016

**Trading & Risk**

- Net margin: £477.31 (gross £5,559.88, capital £75.61)
  - Electricity: gross £5,084.43, capital £70.20, net £363.05
  - Gas: gross £475.45, capital £5.42, net £114.26
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
  - 2016-12-26: treasury £2,466,664.06, (none), VaR (current £23.72 / stressed £7.29) ratio 3.25
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 3.25
- Worst single period: C9 on 2016-11-20 period 36, net margin £-0.34

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2016): £3,634.19
  - By billing account: C1 £1,726.49, C5 £5,007.86, C7 £4,168.20
- Bill shock events (>=20%): 21 -- C5 2016-05-31 (28%); C5 2016-06-30 (21%); C5 2016-10-31 (43%); C5 2016-11-30 (45%); C7 2016-04-30 (22%); C7 2016-05-31 (38%); C7 2016-06-30 (31%); C7 2016-10-31 (83%); C7 2016-11-30 (54%); C6 2016-05-31 (26%); C6 2016-06-30 (23%); C6 2016-10-31 (42%); C6 2016-11-30 (47%); C8 2016-05-31 (41%); C8 2016-06-30 (42%); C8 2016-09-30 (25%); C8 2016-10-31 (110%); C8 2016-11-30 (72%); C9 2016-09-30 (20%); C9 2016-10-31 (80%); C9 2016-11-30 (61%)
- Churn risk (accounts renewing in 2016): 2 at risk (≥20% churn prob): C5 29%, C7 29%

**Pricing & Margin**

- C1 (electricity): tariff £111.70-£134.71/MWh, net margin £28.18
- C1g (gas): tariff £24.34-£25.16/MWh, net margin £25.14
- C2 (electricity): tariff £110.95/MWh, net margin £33.68
- C2g (gas): tariff £28.13/MWh, net margin £67.31
- C3 (electricity): tariff £101.48/MWh, net margin £-2.29 -- **net-negative**
- C3g (gas): tariff £23.44/MWh, net margin £15.41
- C4 (electricity): tariff £100.64/MWh, net margin £-3.49 -- **net-negative**
- C4g (gas): tariff £22.66/MWh, net margin £6.40
- C5 (electricity): tariff £111.70-£135.30/MWh, net margin £33.52
- C6 (electricity): tariff £110.95/MWh, net margin £-16.07 -- **net-negative**
- C7 (electricity): tariff £87.77-£167.55/MWh, net margin £140.56
- C8 (electricity): tariff £87.18-£166.43/MWh, net margin £116.25
- C9 (electricity): tariff £79.73-£152.22/MWh, net margin £32.71

**Portfolio Health**

- Capital cost ratio: 1.4% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 108, average clarity 0.890, average bill shock 14.0%, bad debt provision £313.53, avg complaint probability 3.6%
- Solvency signal: £274,100/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £949.93 vs. naked (unhedged) net margin: £8,633.95
- hedging cost £7,684.02 vs. a fully unhedged book (commodity-only: actual net £949.93 vs. naked net £8,633.95)
  - C1: actual £73.16 vs. naked £508.76 -- hedging cost £435.59
  - C1g: actual £42.49 vs. naked £244.91 -- hedging cost £202.43
  - C2: actual £40.93 vs. naked £468.27 -- hedging cost £427.34
  - C2g: actual £87.10 vs. naked £221.80 -- hedging cost £134.70
  - C3: actual £-13.65 vs. naked £224.37 -- hedging cost £238.02
  - C3g: actual £27.71 vs. naked £133.26 -- hedging cost £105.55
  - C4: actual £-29.11 vs. naked £284.13 -- hedging cost £313.24
  - C4g: actual £19.57 vs. naked £171.36 -- hedging cost £151.78
  - C5: actual £163.00 vs. naked £2,399.57 -- hedging cost £2,236.57
  - C6: actual £-36.24 vs. naked £811.83 -- hedging cost £848.07
  - C7: actual £329.99 vs. naked £1,780.10 -- hedging cost £1,450.11
  - C8: actual £183.93 vs. naked £750.51 -- hedging cost £566.57
  - C9: actual £61.05 vs. naked £635.09 -- hedging cost £574.04

**Year narrative:** 2016 produced a net gain of £477.31 across 13 accounts. The risk committee intervened 13 time(s), raising hedge fractions in response to elevated VaR. 21 customer(s) experienced a bill shock of >=20%.

## 2017

**Trading & Risk**

- Net margin: £37,955.03 (gross £129,065.46, capital £1,258.39)
  - Electricity: gross £128,323.13, capital £1,247.96, net £37,846.84
  - Gas: gross £742.32, capital £10.43, net £108.19
- Treasury at year end: £2,504,699.84
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.91 (avg 0.91), C1g 0.85 (avg 0.85), C2 0.92 (avg 0.92), C2g 0.85 (avg 0.85), C3 0.90 (avg 0.90), C3g 0.85 (avg 0.85), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C5 0.91 (avg 0.91), C6 0.92 (avg 0.92), C7 0.90 (avg 0.90), C8 0.92 (avg 0.92), C9 0.90 (avg 0.90), C_IC1 0.94 (avg 0.94)
- Risk committee (Context Handshake) interventions: 12
  - 2017-01-25: treasury £2,466,900.99, C1->1.00, C5->1.00, C7->1.00, VaR (current £312.92 / stressed £98.91) ratio 3.16
  - 2017-02-24: treasury £2,466,903.27, C1->1.00, C5->1.00, C7->1.00, VaR (current £312.92 / stressed £98.91) ratio 3.16
  - 2017-03-26: treasury £2,466,905.98, C1->1.00, C5->1.00, C7->1.00, VaR (current £312.92 / stressed £98.91) ratio 3.16
  - 2017-04-25: treasury £2,467,132.95, C1->1.00, C5->1.00, C7->1.00, VaR (current £747.19 / stressed £280.93) ratio 2.66
  - 2017-05-25: treasury £2,467,130.22, C1->1.00, C5->1.00, C7->1.00, VaR (current £747.19 / stressed £280.93) ratio 2.66
  - 2017-06-24: treasury £2,467,128.06, C1->1.00, C5->1.00, C7->1.00, VaR (current £747.19 / stressed £280.93) ratio 2.66
  - 2017-07-24: treasury £2,467,194.92, C1->1.00, C5->1.00, C7->1.00, VaR (current £869.28 / stressed £338.68) ratio 2.57
  - 2017-08-23: treasury £2,467,191.94, C1->1.00, C5->1.00, C7->1.00, VaR (current £869.28 / stressed £338.68) ratio 2.57
  - 2017-09-22: treasury £2,467,188.41, C1->1.00, C5->1.00, C7->1.00, VaR (current £869.28 / stressed £338.68) ratio 2.57
  - 2017-10-22: treasury £2,467,243.16, C5->1.00, C7->1.00, VaR (current £875.36 / stressed £343.96) ratio 2.54
  - 2017-11-21: treasury £2,467,246.96, C5->1.00, C7->1.00, VaR (current £875.36 / stressed £343.96) ratio 2.54
  - 2017-12-21: treasury £2,467,250.57, C5->1.00, C7->1.00, VaR (current £875.36 / stressed £343.96) ratio 2.54
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.73
- Worst single period: C_IC1 on 2017-05-17 period 32, net margin £-23.56

**Customer Book**

- Active accounts: 14 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9, C_IC1)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C_IC1
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2017): £5,467.00
  - By billing account: C1 £1,918.54, C2 £5,666.34, C3 £2,581.88, C4 £3,402.39, C5 £6,817.61, C6 £10,541.48, C7 £4,505.21, C8 £7,878.31, C9 £5,891.28
- Bill shock events (>=20%): 27 -- C5 2017-01-31 (32%); C5 2017-02-28 (23%); C5 2017-05-31 (20%); C5 2017-06-30 (22%); C5 2017-11-30 (58%); C7 2017-01-31 (39%); C7 2017-02-28 (29%); C7 2017-05-31 (32%); C7 2017-06-30 (33%); C7 2017-09-30 (28%); C7 2017-10-31 (23%); C7 2017-11-30 (79%); C6 2017-05-31 (22%); C6 2017-06-30 (20%); C6 2017-11-30 (51%); C8 2017-05-31 (40%); C8 2017-06-30 (37%); C8 2017-09-30 (48%); C8 2017-10-31 (23%); C8 2017-11-30 (85%); C8 2017-12-31 (22%); C9 2017-05-31 (33%); C9 2017-06-30 (27%); C9 2017-09-30 (31%); C9 2017-10-31 (22%); C9 2017-11-30 (72%); C4 2017-10-31 (22%)
- Churn risk (accounts renewing in 2017): 5 at risk (≥20% churn prob): C5 32%, C6 35%, C7 38%, C8 35%, C9 32%

**Pricing & Margin**

- C1 (electricity): tariff £122.65-£134.71/MWh, net margin £44.77
- C1g (gas): tariff £25.16-£32.24/MWh, net margin £17.22
- C2 (electricity): tariff £110.95-£127.87/MWh, net margin £47.77
- C2g (gas): tariff £28.13-£28.61/MWh, net margin £58.10
- C3 (electricity): tariff £101.48-£118.76/MWh, net margin £0.53
- C3g (gas): tariff £23.44-£26.06/MWh, net margin £24.57
- C4 (electricity): tariff £100.64-£116.67/MWh, net margin £-26.22 -- **net-negative**
- C4g (gas): tariff £22.66-£25.44/MWh, net margin £8.30
- C5 (electricity): tariff £126.00-£135.30/MWh, net margin £128.44
- C6 (electricity): tariff £110.95-£131.35/MWh, net margin £44.30
- C7 (electricity): tariff £102.78-£200.93/MWh, net margin £187.95
- C8 (electricity): tariff £87.18-£192.90/MWh, net margin £205.65
- C9 (electricity): tariff £79.73-£176.59/MWh, net margin £99.97
- C_IC1 (electricity): tariff £79.23-£151.25/MWh, net margin £37,113.69

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 168, average clarity 0.884, average bill shock 11.4%, bad debt provision £7,542.10, avg complaint probability 3.5%
- Solvency signal: £250,470/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £37,545.02 vs. naked (unhedged) net margin: £116,563.01
- hedging cost £79,017.99 vs. a fully unhedged book (commodity-only: actual net £37,545.02 vs. naked net £116,563.01)
  - C1: actual £-35.37 vs. naked £206.65 -- hedging cost £242.02
  - C1g: actual £35.19 vs. naked £113.40 -- hedging cost £78.21
  - C2: actual £53.52 vs. naked £510.58 -- hedging cost £457.06
  - C2g: actual £47.98 vs. naked £162.13 -- hedging cost £114.15
  - C3: actual £15.53 vs. naked £264.18 -- hedging cost £248.65
  - C3g: actual £21.42 vs. naked £95.50 -- hedging cost £74.08
  - C4: actual £-20.73 vs. naked £311.90 -- hedging cost £332.63
  - C4g: actual £-23.96 vs. naked £90.47 -- hedging cost £114.43
  - C5: actual £-207.59 vs. naked £1,043.39 -- hedging cost £1,250.98
  - C6: actual £94.83 vs. naked £1,328.09 -- hedging cost £1,233.26
  - C7: actual £34.27 vs. naked £859.88 -- hedging cost £825.61
  - C8: actual £250.03 vs. naked £942.76 -- hedging cost £692.73
  - C9: actual £166.21 vs. naked £836.58 -- hedging cost £670.37
  - C_IC1: actual £37,113.69 vs. naked £109,797.51 -- hedging cost £72,683.81

**Year narrative:** 2017 produced a net gain of £37,955.03 across 14 accounts. The risk committee intervened 12 time(s), raising hedge fractions in response to elevated VaR. 27 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £76,547.19 (gross £237,353.43, capital £1,619.08)
  - Electricity: gross £236,665.29, capital £1,604.28, net £76,483.31
  - Gas: gross £688.14, capital £14.80, net £63.89
- Treasury at year end: £2,496,471.41
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
- Average CLV (Point-in-Time, year-end 2018): £150,461.82
  - By billing account: C1 £1,934.31, C2 £4,672.57, C3 £2,558.66, C4 £2,906.60, C5 £5,951.75, C6 £7,706.43, C7 £4,492.88, C8 £6,334.54, C9 £5,832.06, C_IC1 £1,462,228.40
- Bill shock events (>=20%): 34 -- C5 2018-04-30 (32%); C5 2018-06-30 (21%); C5 2018-10-31 (32%); C5 2018-11-30 (28%); C7 2018-04-30 (39%); C7 2018-05-31 (29%); C7 2018-06-30 (32%); C7 2018-09-30 (30%); C7 2018-10-31 (48%); C7 2018-11-30 (33%); C6 2018-04-30 (24%); C6 2018-05-31 (22%); C6 2018-06-30 (22%); C6 2018-10-31 (31%); C6 2018-11-30 (22%); C8 2018-04-30 (34%); C8 2018-05-31 (38%); C8 2018-06-30 (44%); C8 2018-08-31 (26%); C8 2018-09-30 (55%); C8 2018-10-31 (57%); C8 2018-11-30 (30%); C9 2018-04-30 (32%); C9 2018-05-31 (35%); C9 2018-06-30 (35%); C9 2018-08-31 (44%); C9 2018-09-30 (46%); C9 2018-10-31 (41%); C9 2018-12-31 (20%); C4 2018-10-31 (26%); C4g 2018-10-31 (20%); C_IC1 2018-01-31 (22%); C_IC1 2018-02-28 (48%); C_IC2 2018-09-30 (20%)
- Churn risk (accounts renewing in 2018): 6 at risk (≥20% churn prob): C4 20%, C5 38%, C6 32%, C7 41%, C8 35%, C9 38%

**Pricing & Margin**

- C1 (electricity): tariff £122.65-£157.56/MWh, net margin £-35.10 -- **net-negative**
- C1g (gas): tariff £32.24-£39.02/MWh, net margin £35.28
- C2 (electricity): tariff £127.87-£145.59/MWh, net margin £12.21
- C2g (gas): tariff £28.61-£35.23/MWh, net margin £45.27
- C3 (electricity): tariff £118.76-£139.57/MWh, net margin £19.99
- C3g (gas): tariff £26.06-£31.39/MWh, net margin £14.14
- C4 (electricity): tariff £116.67-£140.30/MWh, net margin £-21.79 -- **net-negative**
- C4g (gas): tariff £25.44-£31.92/MWh, net margin £-30.80 -- **net-negative**
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
- Bills issued: 180, average clarity 0.872, average bill shock 11.2%, bad debt provision £12,302.64, avg complaint probability 3.6%
- Solvency signal: £226,952/customer (11 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £84,339.49 vs. naked (unhedged) net margin: £216,906.85
- hedging cost £132,567.36 vs. a fully unhedged book (commodity-only: actual net £84,339.49 vs. naked net £216,906.85)
  - C1: actual £38.83 vs. naked £399.69 -- hedging cost £360.86
  - C1g: actual £96.06 vs. naked £301.78 -- hedging cost £205.72
  - C2: actual £-7.31 vs. naked £586.42 -- hedging cost £593.73
  - C2g: actual £50.01 vs. naked £199.63 -- hedging cost £149.62
  - C3: actual £24.24 vs. naked £354.58 -- hedging cost £330.34
  - C3g: actual £17.17 vs. naked £163.26 -- hedging cost £146.10
  - C4: actual £-21.79 vs. naked £485.11 -- hedging cost £506.90
  - C4g: actual £-26.79 vs. naked £336.16 -- hedging cost £362.95
  - C5: actual £109.51 vs. naked £1,941.31 -- hedging cost £1,831.81
  - C6: actual £-131.73 vs. naked £1,423.17 -- hedging cost £1,554.90
  - C7: actual £138.07 vs. naked £1,364.66 -- hedging cost £1,226.59
  - C8: actual £78.48 vs. naked £951.07 -- hedging cost £872.59
  - C9: actual £264.24 vs. naked £1,124.82 -- hedging cost £860.57
  - C_IC1: actual £86,675.68 vs. naked £170,942.41 -- hedging cost £84,266.73
  - C_IC2: actual £-2,965.19 vs. naked £36,332.77 -- hedging cost £39,297.96

**Year narrative:** 2018 produced a net gain of £76,547.19 across 15 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 34 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £181,241.24 (gross £650,965.41, capital £3,549.29)
  - Electricity: gross £620,105.31, capital £2,153.83, net £217,180.52
  - Gas: gross £30,860.10, capital £1,395.46, net £-35,939.28
- Treasury at year end: £2,601,642.24
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
- Average CLV (Point-in-Time, year-end 2019): £202,152.01
  - By billing account: C1 £1,814.63, C2 £3,845.63, C3 £2,466.63, C4 £3,138.89, C5 £6,288.69, C6 £8,662.24, C7 £5,476.25, C8 £5,878.56, C9 £6,199.81, C_IC1 £1,311,380.66, C_IC2 £868,520.16
- Bill shock events (>=20%): 36 -- C1 2019-04-30 (22%); C5 2019-01-31 (41%); C5 2019-02-28 (22%); C5 2019-06-30 (26%); C5 2019-10-31 (44%); C5 2019-11-30 (36%); C7 2019-01-31 (42%); C7 2019-02-28 (27%); C7 2019-05-31 (24%); C7 2019-06-30 (36%); C7 2019-10-31 (73%); C7 2019-11-30 (46%); C2g 2019-04-30 (21%); C6 2019-02-28 (21%); C6 2019-06-30 (25%); C6 2019-10-31 (42%); C6 2019-11-30 (27%); C8 2019-01-31 (27%); C8 2019-02-28 (28%); C8 2019-04-30 (22%); C8 2019-06-30 (40%); C8 2019-07-31 (36%); C8 2019-09-30 (62%); C8 2019-10-31 (89%); C8 2019-11-30 (38%); C3 2019-04-30 (21%); C9 2019-02-28 (27%); C9 2019-04-30 (23%); C9 2019-06-30 (37%); C9 2019-07-31 (36%); C9 2019-09-30 (53%); C9 2019-10-31 (76%); C9 2019-11-30 (38%); C_IC1 2019-02-28 (51%); C_IC1 2019-03-31 (123%); C_IC2 2019-02-28 (62%)
- Churn risk (accounts renewing in 2019): 8 at risk (≥20% churn prob): C1 20%, C4 20%, C5 38%, C6 32%, C7 35%, C8 38%, C9 32%, C_IC1 20%

**Pricing & Margin**

- C1 (electricity): tariff £129.11-£157.56/MWh, net margin £38.69
- C1g (gas): tariff £23.79-£39.02/MWh, net margin £96.02
- C2 (electricity): tariff £145.59-£159.26/MWh, net margin £108.68
- C2g (gas): tariff £26.00-£35.23/MWh, net margin £23.67
- C3 (electricity): tariff £126.76-£139.57/MWh, net margin £7.42
- C3g (gas): tariff £26.00-£31.39/MWh, net margin £48.17
- C4 (electricity): tariff £130.16-£140.30/MWh, net margin £-5.58 -- **net-negative**
- C4g (gas): tariff £23.05-£31.92/MWh, net margin £5.65
- C5 (electricity): tariff £131.47-£159.23/MWh, net margin £108.70
- C6 (electricity): tariff £146.05-£157.17/MWh, net margin £115.36
- C7 (electricity): tariff £103.57-£229.80/MWh, net margin £137.86
- C8 (electricity): tariff £110.78-£221.91/MWh, net margin £217.52
- C9 (electricity): tariff £106.45-£216.05/MWh, net margin £255.93
- C_IC1 (electricity): tariff £0.00-£253.45/MWh, net margin £130,126.32
- C_IC2 (electricity): tariff £-60.00-£260.81/MWh, net margin £70,597.21
- C_IC3 (electricity): tariff £56.10-£107.11/MWh, net margin £15,472.41
- C_IC3g (gas): tariff £28.80/MWh, net margin £-36,112.79 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.5% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.878, average bill shock 12.4%, bad debt provision £34,390.69, avg complaint probability 3.7%
- Solvency signal: £216,804/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £206,570.86 vs. naked (unhedged) net margin: £821,697.32
- hedging cost £615,126.46 vs. a fully unhedged book (commodity-only: actual net £206,570.86 vs. naked net £821,697.32)
  - C1: actual £4.69 vs. naked £323.49 -- hedging cost £318.80
  - C1g: actual £36.70 vs. naked £171.45 -- hedging cost £134.75
  - C2: actual £158.02 vs. naked £846.38 -- hedging cost £688.36
  - C2g: actual £13.39 vs. naked £222.05 -- hedging cost £208.65
  - C3: actual £-1.78 vs. naked £395.08 -- hedging cost £396.85
  - C3g: actual £78.39 vs. naked £236.36 -- hedging cost £157.97
  - C4: actual £46.46 vs. naked £524.98 -- hedging cost £478.52
  - C4g: actual £103.65 vs. naked £319.85 -- hedging cost £216.20
  - C5: actual £-57.55 vs. naked £1,537.50 -- hedging cost £1,595.05
  - C6: actual £255.96 vs. naked £2,122.13 -- hedging cost £1,866.17
  - C7: actual £91.74 vs. naked £1,132.43 -- hedging cost £1,040.70
  - C8: actual £302.43 vs. naked £1,386.90 -- hedging cost £1,084.48
  - C9: actual £249.44 vs. naked £1,307.14 -- hedging cost £1,057.70
  - C_IC1: actual £148,717.82 vs. naked £286,943.07 -- hedging cost £138,225.25
  - C_IC2: actual £77,211.89 vs. naked £151,825.79 -- hedging cost £74,613.91
  - C_IC3: actual £15,472.41 vs. naked £306,825.65 -- hedging cost £291,353.23
  - C_IC3g: actual £-36,112.79 vs. naked £65,577.06 -- hedging cost £101,689.86

**Year narrative:** 2019 produced a net gain of £181,241.24 across 17 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 36 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £-36,474.28 (gross £628,291.52, capital £2,757.84)
  - Electricity: gross £565,967.33, capital £1,943.67, net £-31,573.63
  - Gas: gross £62,324.19, capital £814.17, net £-4,900.65
- Treasury at year end: £2,672,581.32
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
- Average CLV (Point-in-Time, year-end 2020): £226,603.97
  - By billing account: C1 £1,951.58, C2 £4,638.66, C3 £2,072.15, C4 £2,741.45, C5 £6,963.68, C6 £8,536.75, C7 £4,633.89, C8 £5,875.89, C9 £5,871.51, C_IC1 £855,227.01, C_IC2 £511,287.01, C_IC3 £1,511,183.86, C_IC4 £24,868.19
- Bill shock events (>=20%): 32 -- C1 2020-04-30 (21%); C1g 2020-01-31 (26%); C5 2020-04-30 (29%); C5 2020-10-31 (39%); C5 2020-12-31 (26%); C7 2020-04-30 (35%); C7 2020-05-31 (22%); C7 2020-06-30 (28%); C7 2020-10-31 (63%); C7 2020-11-30 (24%); C7 2020-12-31 (36%); C6 2020-04-30 (30%); C6 2020-09-30 (21%); C6 2020-10-31 (34%); C6 2020-12-31 (26%); C8 2020-04-30 (37%); C8 2020-05-31 (26%); C8 2020-06-30 (33%); C8 2020-09-30 (57%); C8 2020-10-31 (68%); C8 2020-12-31 (44%); C9 2020-04-30 (28%); C9 2020-05-31 (26%); C9 2020-06-30 (36%); C9 2020-09-30 (47%); C9 2020-10-31 (52%); C9 2020-12-31 (37%); C_IC1 2020-03-31 (57%); C_IC1 2020-04-30 (86%); C_IC2 2020-02-29 (65%); C_IC2 2020-03-31 (132%); C_IC4 2020-12-31 (21%)
- Churn risk (accounts renewing in 2020): 7 at risk (≥20% churn prob): C1 29%, C5 35%, C6 32%, C7 38%, C8 38%, C9 41%, C_IC4 23%

**Pricing & Margin**

- C1 (electricity): tariff £129.11-£139.24/MWh, net margin £4.35
- C1g (gas): tariff £23.30-£23.79/MWh, net margin £36.55
- C2 (electricity): tariff £150.52-£159.26/MWh, net margin £191.56
- C2g (gas): tariff £23.52-£26.00/MWh, net margin £73.63
- C3 (electricity): tariff £126.76/MWh, net margin £-1.31 -- **net-negative**
- C3g (gas): tariff £26.00/MWh, net margin £42.39
- C4 (electricity): tariff £111.32-£130.16/MWh, net margin £2.51
- C4g (gas): tariff £15.21-£23.05/MWh, net margin £63.66
- C5 (electricity): tariff £131.47-£144.11/MWh, net margin £-59.67 -- **net-negative**
- C6 (electricity): tariff £150.52-£157.17/MWh, net margin £338.99
- C7 (electricity): tariff £103.57-£220.86/MWh, net margin £94.33
- C8 (electricity): tariff £114.49-£221.91/MWh, net margin £384.68
- C9 (electricity): tariff £89.74-£203.23/MWh, net margin £180.56
- C_IC1 (electricity): tariff £-73.45-£2690.77/MWh, net margin £71,628.80
- C_IC2 (electricity): tariff £-79.50-£260.81/MWh, net margin £53,243.76
- C_IC3 (electricity): tariff £37.03-£81.96/MWh, net margin £12,398.03
- C_IC3g (gas): tariff £14.60-£15.58/MWh, net margin £-5,116.89 -- **net-negative**
- C_IC4 (electricity): tariff £18.53-£73.19/MWh, net margin £-169,980.21 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 0.4% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 204, average clarity 0.877, average bill shock 11.5%, bad debt provision £35,386.82, avg complaint probability 3.6%
- Solvency signal: £205,583/customer (13 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-102,418.07 vs. naked (unhedged) net margin: £591,688.85
- hedging cost £694,106.92 vs. a fully unhedged book (commodity-only: actual net £-102,418.07 vs. naked net £591,688.85)
  - C1: actual £-35.37 vs. naked £18.95 -- hedging cost £54.32
  - C1g: actual £-70.31 vs. naked £-241.92 -- hedging added £171.61
  - C2: actual £194.80 vs. naked £733.60 -- hedging cost £538.80
  - C2g: actual £87.00 vs. naked £181.16 -- hedging cost £94.16
  - C4: actual £-122.30 vs. naked £183.46 -- hedging cost £305.76
  - C4g: actual £-125.76 vs. naked £-226.03 -- hedging added £100.27
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

**Year narrative:** 2020 produced a net loss of £-36,474.28 across 18 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 32 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £43,574.72 (gross £697,702.31, capital £6,951.30)
  - Electricity: gross £498,453.16, capital £5,815.02, net £-81,629.25
  - Gas: gross £199,249.15, capital £1,136.28, net £125,203.97
- Treasury at year end: £2,690,008.76
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.90 (avg 0.90), C2g 0.85 (avg 0.85), C4 0.93 (avg 0.93), C4g 0.85 (avg 0.85), C6 0.90 (avg 0.90), C7 0.96 (avg 0.96), C8 0.90 (avg 0.90), C9 0.91 (avg 0.91), C_IC1 0.85 (avg 0.88), C_IC2 0.85 (avg 0.88), C_IC3 0.96 (avg 0.96), C_IC3g 0.95 (avg 0.95), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2021-12-31 period 1, net margin £-85.79

**Customer Book**

- Active accounts: 16 (C1, C1g, C2, C2g, C4, C4g, C5, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 6, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: C1, C5
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2021): £221,144.97
  - By billing account: C1 £1,753.36, C2 £4,342.75, C3 £2,018.40, C4 £2,274.10, C5 £6,333.28, C6 £8,021.28, C7 £4,566.55, C8 £5,805.45, C9 £4,749.60, C_IC1 £793,311.11, C_IC2 £425,326.81, C_IC3 £1,596,536.36, C_IC4 £19,845.53
- Bill shock events (>=20%): 38 -- C1 2021-04-30 (20%); C5 2021-05-31 (23%); C5 2021-06-30 (32%); C5 2021-10-31 (30%); C5 2021-11-30 (51%); C7 2021-05-31 (31%); C7 2021-06-30 (48%); C7 2021-10-31 (56%); C7 2021-11-30 (67%); C6 2021-06-30 (36%); C6 2021-10-31 (27%); C6 2021-11-30 (50%); C8 2021-05-31 (29%); C8 2021-06-30 (62%); C8 2021-09-30 (26%); C8 2021-10-31 (69%); C8 2021-11-30 (85%); C9 2021-02-28 (21%); C9 2021-05-31 (25%); C9 2021-06-30 (52%); C9 2021-08-31 (22%); C9 2021-09-30 (23%); C9 2021-10-31 (62%); C9 2021-11-30 (50%); C9 2021-12-31 (24%); C4 2021-10-31 (52%); C4g 2021-10-31 (69%); C_IC1 2021-04-30 (22%); C_IC1 2021-05-31 (47%); C_IC2 2021-03-31 (30%); C_IC2 2021-04-30 (75%); C_IC3g 2021-09-30 (23%); C_IC3g 2021-10-31 (28%); C_IC3g 2021-12-31 (31%); C_IC4 2021-02-28 (28%); C_IC4 2021-07-31 (22%); C_IC4 2021-09-30 (40%); C_IC4 2021-12-31 (29%)
- Churn risk (accounts renewing in 2021): 9 at risk (≥20% churn prob): C5 35%, C6 35%, C7 35%, C8 41%, C9 35%, C_IC1 20%, C_IC2 23%, C_IC3 20%, C_IC4 32%

**Pricing & Margin**

- C1 (electricity): tariff £139.24/MWh, net margin £-34.95 -- **net-negative**
- C1g (gas): tariff £23.30/MWh, net margin £-70.08 -- **net-negative**
- C2 (electricity): tariff £150.52-£181.66/MWh, net margin £161.23
- C2g (gas): tariff £23.52-£30.58/MWh, net margin £-11.53 -- **net-negative**
- C4 (electricity): tariff £111.32-£183.00/MWh, net margin £-191.59 -- **net-negative**
- C4g (gas): tariff £15.21-£35.00/MWh, net margin £-291.49 -- **net-negative**
- C5 (electricity): tariff £144.11/MWh, net margin £-224.58 -- **net-negative**
- C6 (electricity): tariff £150.52-£181.66/MWh, net margin £257.27
- C7 (electricity): tariff £115.69-£274.50/MWh, net margin £25.03
- C8 (electricity): tariff £114.49-£272.49/MWh, net margin £412.73
- C9 (electricity): tariff £89.74-£236.46/MWh, net margin £-17.94 -- **net-negative**
- C_IC1 (electricity): tariff £-54.00-£2365.91/MWh, net margin £54,831.14
- C_IC2 (electricity): tariff £-73.20-£1080.00/MWh, net margin £48,116.84
- C_IC3 (electricity): tariff £42.93-£283.37/MWh, net margin £-21,405.16 -- **net-negative**
- C_IC3g (gas): tariff £14.60-£82.19/MWh, net margin £125,577.06
- C_IC4 (electricity): tariff £42.47-£336.77/MWh, net margin £-163,559.27 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 1.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 192, average clarity 0.869, average bill shock 12.9%, bad debt provision £45,594.73, avg complaint probability 3.8%
- Solvency signal: £224,167/customer (12 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-145,703.17 vs. naked (unhedged) net margin: £-152,066.49
- hedging added £6,363.32 vs. a fully unhedged book (commodity-only: actual net £-145,703.17 vs. naked net £-152,066.49)
  - C2: actual £125.94 vs. naked £127.93 -- hedging cost £2.00
  - C2g: actual £-58.20 vs. naked £-454.26 -- hedging added £396.07
  - C4: actual £-380.92 vs. naked £-303.64 -- hedging cost £77.28
  - C4g: actual £-791.90 vs. naked £-1,586.23 -- hedging added £794.33
  - C6: actual £130.62 vs. naked £-219.78 -- hedging added £350.39
  - C7: actual £-1,640.56 vs. naked £-1,041.64 -- hedging cost £598.93
  - C8: actual £355.92 vs. naked £-27.38 -- hedging added £383.30
  - C9: actual £-170.27 vs. naked £-548.68 -- hedging added £378.41
  - C_IC1: actual £60,250.07 vs. naked £-52,649.80 -- hedging added £112,899.86
  - C_IC2: actual £52,270.49 vs. naked £-508.76 -- hedging added £52,779.25
  - C_IC3: actual £-150,778.91 vs. naked £-73,354.89 -- hedging cost £77,424.02
  - C_IC3g: actual £43,578.41 vs. naked £38,284.45 -- hedging added £5,293.96
  - C_IC4: actual £-148,593.86 vs. naked £-59,783.81 -- hedging cost £88,810.05

**Year narrative:** 2021 (flagged crisis year) produced a net gain of £43,574.72 across 16 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 38 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £-13,732.88 (gross £605,768.96, capital £15,742.16)
  - Electricity: gross £479,034.67, capital £13,255.78, net £-56,306.75
  - Gas: gross £126,734.29, capital £2,486.38, net £42,573.87
- Treasury at year end: £2,547,750.88
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.95 (avg 0.95), C2g 0.85 (avg 0.85), C4 0.95 (avg 0.95), C4g 0.85 (avg 0.85), C6 0.94 (avg 0.94), C7 0.95 (avg 0.95), C8 0.95 (avg 0.95), C9 0.94 (avg 0.94), C_IC1 1.00 (avg 0.97), C_IC2 1.00 (avg 0.98), C_IC3 0.96 (avg 0.96), C_IC3g 1.00 (avg 1.00), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 9
  - 2022-04-29: treasury £2,806,393.41, C2->1.00, C6->1.00, C8->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £57,745.51 / stressed £21,353.04) ratio 2.70
  - 2022-05-29: treasury £2,806,542.71, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £57,882.93 / stressed £21,394.25) ratio 2.71
  - 2022-06-28: treasury £2,806,528.41, C2->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £57,882.93 / stressed £21,394.25) ratio 2.71
  - 2022-07-28: treasury £2,806,214.08, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £57,990.23 / stressed £21,416.75) ratio 2.71
  - 2022-08-27: treasury £2,806,183.44, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £57,990.23 / stressed £21,416.75) ratio 2.71
  - 2022-09-26: treasury £2,806,151.26, C2->1.00, C4->1.00, C6->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £57,990.23 / stressed £21,416.75) ratio 2.71
  - 2022-10-26: treasury £2,804,101.95, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £58,132.56 / stressed £21,457.90) ratio 2.71
  - 2022-11-25: treasury £2,803,969.55, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £58,132.56 / stressed £21,457.90) ratio 2.71
  - 2022-12-25: treasury £2,803,740.53, C2->1.00, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, VaR (current £58,132.56 / stressed £21,457.90) ratio 2.71
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.71
- Worst single period: C_IC3g on 2022-10-01 period 1, net margin £-463.03

**Customer Book**

- Active accounts: 13 (C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2022): £210,595.14
  - By billing account: C1 £1,700.15, C2 £3,608.10, C3 £1,947.47, C4 £1,361.56, C5 £5,690.63, C6 £8,172.50, C7 £3,552.78, C8 £5,592.11, C9 £5,359.92, C_IC1 £966,887.64, C_IC2 £450,132.08, C_IC3 £1,268,893.34, C_IC4 £14,838.48
- Bill shock events (>=20%): 50 -- C7 2022-01-31 (40%); C7 2022-02-28 (27%); C7 2022-04-30 (23%); C7 2022-05-31 (36%); C7 2022-06-30 (27%); C7 2022-09-30 (34%); C7 2022-11-30 (64%); C7 2022-12-31 (56%); C2 2022-04-30 (27%); C2g 2022-04-30 (121%); C6 2022-04-30 (47%); C6 2022-05-31 (23%); C6 2022-09-30 (26%); C6 2022-11-30 (44%); C6 2022-12-31 (34%); C8 2022-02-28 (22%); C8 2022-05-31 (39%); C8 2022-06-30 (35%); C8 2022-07-31 (22%); C8 2022-09-30 (85%); C8 2022-11-30 (73%); C8 2022-12-31 (57%); C9 2022-04-30 (21%); C9 2022-05-31 (30%); C9 2022-06-30 (30%); C9 2022-07-31 (25%); C9 2022-09-30 (51%); C9 2022-10-31 (31%); C9 2022-11-30 (46%); C9 2022-12-31 (53%); C4 2022-10-31 (62%); C4g 2022-10-31 (121%); C_IC1 2022-06-30 (85%); C_IC2 2022-05-31 (56%); C_IC3 2022-01-31 (69%); C_IC3g 2022-03-31 (55%); C_IC3g 2022-04-30 (20%); C_IC3g 2022-07-31 (46%); C_IC3g 2022-08-31 (30%); C_IC3g 2022-09-30 (21%); C_IC3g 2022-10-31 (51%); C_IC3g 2022-11-30 (21%); C_IC3g 2022-12-31 (21%); C_IC4 2022-02-28 (21%); C_IC4 2022-03-31 (44%); C_IC4 2022-05-31 (21%); C_IC4 2022-07-31 (38%); C_IC4 2022-08-31 (41%); C_IC4 2022-10-31 (39%); C_IC4 2022-12-31 (102%)
- Churn risk (accounts renewing in 2022): 8 at risk (≥20% churn prob): C4 20%, C6 32%, C7 38%, C8 38%, C9 41%, C_IC1 20%, C_IC3 29%, C_IC4 38%

**Pricing & Margin**

- C2 (electricity): tariff £181.66-£305.00/MWh, net margin £-158.62 -- **net-negative**
- C2g (gas): tariff £30.58-£95.00/MWh, net margin £-222.17 -- **net-negative**
- C4 (electricity): tariff £183.00-£305.00/MWh, net margin £-421.23 -- **net-negative**
- C4g (gas): tariff £35.00-£95.00/MWh, net margin £-994.85 -- **net-negative**
- C6 (electricity): tariff £181.66-£382.27/MWh, net margin £412.80
- C7 (electricity): tariff £143.79-£457.50/MWh, net margin £-1,634.41 -- **net-negative**
- C8 (electricity): tariff £142.73-£457.50/MWh, net margin £42.81
- C9 (electricity): tariff £123.86-£457.50/MWh, net margin £211.50
- C_IC1 (electricity): tariff £-83.39-£458.04/MWh, net margin £168,397.32
- C_IC2 (electricity): tariff £-80.56-£593.08/MWh, net margin £75,575.04
- C_IC3 (electricity): tariff £148.43-£283.37/MWh, net margin £-150,225.40 -- **net-negative**
- C_IC3g (gas): tariff £82.19-£156.73/MWh, net margin £43,790.89
- C_IC4 (electricity): tariff £71.50-£469.98/MWh, net margin £-148,506.58 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 2.6% of gross
- Treasury drawdown events (>=10% threshold): 720 -- £2,881,383.01 -> £2,547,581.70 (11.6%); £2,881,383.03 -> £2,547,582.01 (11.6%); £2,881,383.12 -> £2,547,582.04 (11.6%); £2,881,383.13 -> £2,547,582.07 (11.6%); £2,881,383.15 -> £2,547,582.12 (11.6%); £2,881,383.15 -> £2,547,582.62 (11.6%); £2,881,383.23 -> £2,547,582.65 (11.6%); £2,881,383.31 -> £2,547,582.68 (11.6%); £2,881,383.39 -> £2,547,582.71 (11.6%); £2,881,383.40 -> £2,547,583.03 (11.6%); £2,881,383.53 -> £2,547,583.08 (11.6%); £2,881,383.67 -> £2,547,583.13 (11.6%); £2,881,383.80 -> £2,547,583.16 (11.6%); £2,881,383.85 -> £2,547,583.21 (11.6%); £2,881,383.89 -> £2,547,583.24 (11.6%); £2,881,384.01 -> £2,547,583.75 (11.6%); £2,881,384.14 -> £2,547,583.79 (11.6%); £2,881,384.27 -> £2,547,583.83 (11.6%); £2,881,384.40 -> £2,547,583.85 (11.6%); £2,881,384.52 -> £2,547,583.88 (11.6%); £2,881,384.64 -> £2,547,583.91 (11.6%); £2,881,384.75 -> £2,547,583.94 (11.6%); £2,881,384.78 -> £2,547,586.35 (11.6%); £2,881,384.82 -> £2,547,586.39 (11.6%); £2,881,384.87 -> £2,547,586.44 (11.6%); £2,881,384.87 -> £2,547,586.95 (11.6%); £2,881,385.02 -> £2,547,587.01 (11.6%); £2,881,385.17 -> £2,547,587.05 (11.6%); £2,881,385.32 -> £2,547,587.09 (11.6%); £2,881,385.46 -> £2,547,587.13 (11.6%); £2,881,385.61 -> £2,547,587.16 (11.6%); £2,881,385.75 -> £2,547,587.20 (11.6%); £2,881,385.89 -> £2,547,587.23 (11.6%); £2,881,385.97 -> £2,547,587.53 (11.6%); £2,881,386.08 -> £2,547,587.56 (11.6%); £2,881,386.20 -> £2,547,587.61 (11.6%); £2,881,386.31 -> £2,547,587.66 (11.6%); £2,881,386.42 -> £2,547,587.69 (11.6%); £2,881,386.46 -> £2,547,587.72 (11.6%); £2,881,386.50 -> £2,547,587.75 (11.6%); £2,881,386.59 -> £2,547,588.18 (11.6%); £2,881,386.69 -> £2,547,588.20 (11.6%); £2,881,386.80 -> £2,547,588.23 (11.6%); £2,881,386.90 -> £2,547,588.25 (11.6%); £2,881,387.01 -> £2,547,588.27 (11.6%); £2,881,387.11 -> £2,547,588.29 (11.6%); £2,881,387.20 -> £2,547,588.30 (11.6%); £2,881,387.29 -> £2,547,588.55 (11.6%); £2,881,387.37 -> £2,547,588.59 (11.6%); £2,881,387.45 -> £2,547,588.64 (11.6%); £2,881,387.54 -> £2,547,588.67 (11.6%); £2,881,387.58 -> £2,547,588.71 (11.6%); £2,881,387.62 -> £2,547,588.75 (11.6%); £2,881,387.70 -> £2,547,589.24 (11.6%); £2,881,387.79 -> £2,547,589.28 (11.6%); £2,881,387.89 -> £2,547,589.31 (11.6%); £2,881,387.98 -> £2,547,589.34 (11.6%); £2,881,388.07 -> £2,547,589.36 (11.6%); £2,881,388.15 -> £2,547,589.38 (11.6%); £2,881,388.23 -> £2,547,589.40 (11.6%); £2,881,388.25 -> £2,547,589.70 (11.6%); £2,881,388.29 -> £2,547,589.74 (11.6%); £2,881,388.33 -> £2,547,589.79 (11.6%); £2,881,388.37 -> £2,547,589.83 (11.6%); £2,881,388.42 -> £2,547,589.88 (11.6%); £2,881,388.46 -> £2,547,589.92 (11.6%); £2,881,388.51 -> £2,547,590.44 (11.6%); £2,881,388.57 -> £2,547,590.47 (11.6%); £2,881,388.63 -> £2,547,590.49 (11.6%); £2,881,388.68 -> £2,547,590.51 (11.6%); £2,881,388.74 -> £2,547,590.53 (11.6%); £2,881,388.79 -> £2,547,590.55 (11.6%); £2,881,388.84 -> £2,547,590.56 (11.6%); £2,881,388.87 -> £2,547,590.79 (11.6%); £2,881,388.96 -> £2,547,590.83 (11.6%); £2,881,389.04 -> £2,547,590.86 (11.6%); £2,881,389.12 -> £2,547,590.92 (11.6%); £2,881,389.20 -> £2,547,590.97 (11.6%); £2,881,389.24 -> £2,547,591.00 (11.6%); £2,881,389.29 -> £2,547,591.03 (11.6%); £2,881,389.37 -> £2,547,591.54 (11.6%); £2,881,389.45 -> £2,547,591.57 (11.6%); £2,881,389.54 -> £2,547,591.59 (11.6%); £2,881,389.62 -> £2,547,591.61 (11.6%); £2,881,389.70 -> £2,547,591.62 (11.6%); £2,881,389.78 -> £2,547,591.64 (11.6%); £2,881,389.85 -> £2,547,591.66 (11.6%); £2,881,389.89 -> £2,547,594.33 (11.6%); £2,881,389.93 -> £2,547,594.36 (11.6%); £2,881,389.97 -> £2,547,594.39 (11.6%); £2,881,390.01 -> £2,547,594.42 (11.6%); £2,881,390.03 -> £2,547,594.73 (11.6%); £2,881,390.08 -> £2,547,594.75 (11.6%); £2,881,390.14 -> £2,547,594.76 (11.6%); £2,881,390.19 -> £2,547,594.78 (11.6%); £2,881,390.24 -> £2,547,594.79 (11.6%); £2,881,390.29 -> £2,547,594.80 (11.6%); £2,881,390.33 -> £2,547,592.42 (11.6%); £2,881,390.40 -> £2,547,595.02 (11.6%); £2,881,390.50 -> £2,547,595.04 (11.6%); £2,881,390.60 -> £2,547,595.08 (11.6%); £2,881,390.70 -> £2,547,595.12 (11.6%); £2,881,390.81 -> £2,547,595.16 (11.6%); £2,881,390.85 -> £2,547,595.20 (11.6%); £2,881,390.89 -> £2,547,595.25 (11.6%); £2,881,390.98 -> £2,547,595.74 (11.6%); £2,881,391.09 -> £2,547,595.78 (11.6%); £2,881,391.20 -> £2,547,595.81 (11.6%); £2,881,391.30 -> £2,547,595.83 (11.6%); £2,881,391.41 -> £2,547,595.86 (11.6%); £2,881,391.51 -> £2,547,595.88 (11.6%); £2,881,391.60 -> £2,547,591.53 (11.6%); £2,881,391.67 -> £2,547,596.16 (11.6%); £2,881,391.79 -> £2,547,596.20 (11.6%); £2,881,391.91 -> £2,547,596.25 (11.6%); £2,881,392.03 -> £2,547,596.31 (11.6%); £2,881,392.14 -> £2,547,596.35 (11.6%); £2,881,392.18 -> £2,547,596.39 (11.6%); £2,881,392.23 -> £2,547,596.44 (11.6%); £2,881,392.33 -> £2,547,596.96 (11.6%); £2,881,392.44 -> £2,547,596.99 (11.6%); £2,881,392.56 -> £2,547,597.03 (11.6%); £2,881,392.67 -> £2,547,597.06 (11.6%); £2,881,392.78 -> £2,547,597.09 (11.6%); £2,881,392.89 -> £2,547,597.11 (11.6%); £2,881,392.99 -> £2,547,590.64 (11.6%); £2,881,393.01 -> £2,547,597.46 (11.6%); £2,881,393.07 -> £2,547,597.52 (11.6%); £2,881,393.13 -> £2,547,597.58 (11.6%); £2,881,393.18 -> £2,547,597.62 (11.6%); £2,881,393.22 -> £2,547,597.67 (11.6%); £2,881,393.27 -> £2,547,597.71 (11.6%); £2,881,393.33 -> £2,547,598.24 (11.6%); £2,881,393.40 -> £2,547,598.28 (11.6%); £2,881,393.47 -> £2,547,598.31 (11.6%); £2,881,393.53 -> £2,547,598.34 (11.6%); £2,881,393.60 -> £2,547,598.38 (11.6%); £2,881,393.66 -> £2,547,598.41 (11.6%); £2,881,393.72 -> £2,547,587.09 (11.6%); £2,881,393.74 -> £2,547,601.31 (11.6%); £2,881,393.78 -> £2,547,601.34 (11.6%); £2,881,393.82 -> £2,547,601.37 (11.6%); £2,881,393.86 -> £2,547,601.40 (11.6%); £2,881,393.90 -> £2,547,601.43 (11.6%); £2,881,393.91 -> £2,547,601.81 (11.6%); £2,881,393.97 -> £2,547,601.82 (11.6%); £2,881,394.02 -> £2,547,601.82 (11.6%); £2,881,394.07 -> £2,547,601.82 (11.6%); £2,881,394.12 -> £2,547,601.83 (11.6%); £2,881,394.16 -> £2,547,601.83 (11.6%); £2,881,394.20 -> £2,547,586.21 (11.6%); £2,881,394.21 -> £2,547,602.12 (11.6%); £2,881,394.26 -> £2,547,602.17 (11.6%); £2,881,394.30 -> £2,547,602.23 (11.6%); £2,881,394.34 -> £2,547,602.28 (11.6%); £2,881,394.39 -> £2,547,602.32 (11.6%); £2,881,394.43 -> £2,547,602.37 (11.6%); £2,881,394.48 -> £2,547,602.84 (11.6%); £2,881,394.53 -> £2,547,602.87 (11.6%); £2,881,394.59 -> £2,547,602.91 (11.6%); £2,881,394.65 -> £2,547,602.93 (11.6%); £2,881,394.71 -> £2,547,602.96 (11.6%); £2,881,394.76 -> £2,547,602.98 (11.6%); £2,881,394.81 -> £2,547,585.32 (11.6%); £2,881,394.85 -> £2,547,603.32 (11.6%); £2,881,394.89 -> £2,547,603.38 (11.6%); £2,881,394.93 -> £2,547,603.44 (11.6%); £2,881,394.97 -> £2,547,603.46 (11.6%); £2,881,395.01 -> £2,547,603.49 (11.6%); £2,881,395.05 -> £2,547,603.54 (11.6%); £2,881,395.09 -> £2,547,603.97 (11.6%); £2,881,395.15 -> £2,547,604.01 (11.6%); £2,881,395.21 -> £2,547,604.04 (11.6%); £2,881,395.27 -> £2,547,604.07 (11.6%); £2,881,395.33 -> £2,547,604.10 (11.6%); £2,881,395.38 -> £2,547,604.12 (11.6%); £2,881,395.43 -> £2,547,584.43 (11.6%); £2,881,395.44 -> £2,547,604.41 (11.6%); £2,881,395.50 -> £2,547,604.44 (11.6%); £2,881,395.56 -> £2,547,604.48 (11.6%); £2,881,395.62 -> £2,547,604.52 (11.6%); £2,881,395.67 -> £2,547,604.56 (11.6%); £2,881,395.72 -> £2,547,604.60 (11.6%); £2,881,395.76 -> £2,547,604.64 (11.6%); £2,881,395.81 -> £2,547,605.07 (11.6%); £2,881,395.88 -> £2,547,605.09 (11.6%); £2,881,395.94 -> £2,547,605.11 (11.6%); £2,881,396.01 -> £2,547,605.13 (11.6%); £2,881,396.07 -> £2,547,605.15 (11.6%); £2,881,396.13 -> £2,547,605.17 (11.6%); £2,881,396.19 -> £2,547,580.88 (11.6%); £2,881,396.25 -> £2,547,607.77 (11.6%); £2,881,396.37 -> £2,547,607.80 (11.6%); £2,881,396.48 -> £2,547,607.83 (11.6%); £2,881,396.59 -> £2,547,607.87 (11.6%); £2,881,396.71 -> £2,547,607.91 (11.6%); £2,881,396.75 -> £2,547,607.95 (11.6%); £2,881,396.80 -> £2,547,607.96 (11.6%); £2,881,396.90 -> £2,547,608.45 (11.6%); £2,881,397.01 -> £2,547,608.48 (11.6%); £2,881,397.12 -> £2,547,608.52 (11.6%); £2,881,397.23 -> £2,547,608.54 (11.6%); £2,881,397.34 -> £2,547,608.56 (11.6%); £2,881,397.44 -> £2,547,608.57 (11.6%); £2,881,397.53 -> £2,547,579.99 (11.6%); £2,881,397.62 -> £2,547,608.83 (11.6%); £2,881,397.75 -> £2,547,608.87 (11.6%); £2,881,397.88 -> £2,547,608.91 (11.6%); £2,881,398.01 -> £2,547,608.94 (11.6%); £2,881,398.13 -> £2,547,608.98 (11.6%); £2,881,398.18 -> £2,547,609.02 (11.6%); £2,881,398.22 -> £2,547,609.06 (11.6%); £2,881,398.33 -> £2,547,609.51 (11.6%); £2,881,398.45 -> £2,547,609.55 (11.6%); £2,881,398.57 -> £2,547,609.58 (11.6%); £2,881,398.69 -> £2,547,609.60 (11.6%); £2,881,398.81 -> £2,547,609.63 (11.6%); £2,881,398.92 -> £2,547,609.65 (11.6%); £2,881,399.04 -> £2,547,579.11 (11.6%); £2,881,399.07 -> £2,547,609.89 (11.6%); £2,881,399.17 -> £2,547,609.91 (11.6%); £2,881,399.27 -> £2,547,609.96 (11.6%); £2,881,399.38 -> £2,547,610.01 (11.6%); £2,881,399.49 -> £2,547,610.05 (11.6%); £2,881,399.53 -> £2,547,610.09 (11.6%); £2,881,399.58 -> £2,547,610.13 (11.6%); £2,881,399.66 -> £2,547,610.58 (11.6%); £2,881,399.77 -> £2,547,610.61 (11.6%); £2,881,399.87 -> £2,547,610.64 (11.6%); £2,881,399.97 -> £2,547,610.66 (11.6%); £2,881,400.07 -> £2,547,610.69 (11.6%); £2,881,400.17 -> £2,547,610.70 (11.6%); £2,881,400.26 -> £2,547,578.22 (11.6%); £2,881,400.28 -> £2,547,610.99 (11.6%); £2,881,400.32 -> £2,547,611.01 (11.6%); £2,881,400.37 -> £2,547,611.05 (11.6%); £2,881,400.41 -> £2,547,611.09 (11.6%); £2,881,400.44 -> £2,547,611.45 (11.6%); £2,881,400.49 -> £2,547,611.48 (11.6%); £2,881,400.54 -> £2,547,611.49 (11.6%); £2,881,400.59 -> £2,547,611.51 (11.6%); £2,881,400.64 -> £2,547,611.52 (11.6%); £2,881,400.69 -> £2,547,611.54 (11.6%); £2,881,400.73 -> £2,547,575.25 (11.6%); £2,881,400.78 -> £2,547,613.70 (11.6%); £2,881,400.87 -> £2,547,613.71 (11.6%); £2,881,400.96 -> £2,547,613.73 (11.6%); £2,881,401.05 -> £2,547,613.74 (11.6%); £2,881,401.13 -> £2,547,574.05 (11.6%); £2,881,401.15 -> £2,547,614.06 (11.6%); £2,881,401.19 -> £2,547,614.11 (11.6%); £2,881,401.23 -> £2,547,614.14 (11.6%); £2,881,401.28 -> £2,547,614.18 (11.6%); £2,881,401.32 -> £2,547,614.21 (11.6%); £2,881,401.36 -> £2,547,614.68 (11.6%); £2,881,401.42 -> £2,547,614.71 (11.6%); £2,881,401.48 -> £2,547,614.74 (11.6%); £2,881,401.53 -> £2,547,614.76 (11.6%); £2,881,401.58 -> £2,547,614.78 (11.6%); £2,881,401.63 -> £2,547,614.80 (11.6%); £2,881,401.68 -> £2,547,572.85 (11.6%); £2,881,401.69 -> £2,547,615.08 (11.6%); £2,881,401.74 -> £2,547,615.12 (11.6%); £2,881,401.78 -> £2,547,615.17 (11.6%); £2,881,401.83 -> £2,547,615.20 (11.6%); £2,881,401.87 -> £2,547,615.23 (11.6%); £2,881,401.91 -> £2,547,615.27 (11.6%); £2,881,401.94 -> £2,547,615.63 (11.6%); £2,881,402.00 -> £2,547,615.65 (11.6%); £2,881,402.05 -> £2,547,615.67 (11.6%); £2,881,402.10 -> £2,547,615.68 (11.6%); £2,881,402.15 -> £2,547,615.69 (11.6%); £2,881,402.20 -> £2,547,615.70 (11.6%); £2,881,402.25 -> £2,547,571.66 (11.6%); £2,881,402.34 -> £2,547,615.91 (11.6%); £2,881,402.47 -> £2,547,615.93 (11.6%); £2,881,402.60 -> £2,547,615.97 (11.6%); £2,881,402.74 -> £2,547,616.02 (11.6%); £2,881,402.88 -> £2,547,616.05 (11.6%); £2,881,402.92 -> £2,547,616.09 (11.6%); £2,881,402.97 -> £2,547,616.12 (11.6%); £2,881,403.07 -> £2,547,616.57 (11.6%); £2,881,403.19 -> £2,547,616.61 (11.6%); £2,881,403.32 -> £2,547,616.64 (11.6%); £2,881,403.44 -> £2,547,616.65 (11.6%); £2,881,403.56 -> £2,547,616.67 (11.6%); £2,881,403.68 -> £2,547,616.68 (11.6%); £2,881,403.79 -> £2,547,570.46 (11.6%); £2,881,403.90 -> £2,547,616.97 (11.6%); £2,881,404.08 -> £2,547,617.01 (11.6%); £2,881,404.25 -> £2,547,617.08 (11.6%); £2,881,404.43 -> £2,547,617.15 (11.6%); £2,881,404.61 -> £2,547,617.19 (11.6%); £2,881,404.65 -> £2,547,617.22 (11.6%); £2,881,404.70 -> £2,547,617.26 (11.6%); £2,881,404.84 -> £2,547,617.75 (11.6%); £2,881,404.99 -> £2,547,617.80 (11.6%); £2,881,405.15 -> £2,547,617.84 (11.6%); £2,881,405.30 -> £2,547,617.87 (11.6%); £2,881,405.45 -> £2,547,617.90 (11.6%); £2,881,405.59 -> £2,547,617.93 (11.6%); £2,881,405.73 -> £2,547,565.67 (11.6%); £2,881,405.75 -> £2,547,620.93 (11.6%); £2,881,405.79 -> £2,547,621.38 (11.6%); £2,881,405.84 -> £2,547,621.41 (11.6%); £2,881,405.89 -> £2,547,621.43 (11.6%); £2,881,405.95 -> £2,547,621.44 (11.6%); £2,881,406.00 -> £2,547,621.46 (11.6%); £2,881,406.04 -> £2,547,621.47 (11.6%); £2,881,406.09 -> £2,547,564.47 (11.6%); £2,881,406.12 -> £2,547,621.77 (11.6%); £2,881,406.16 -> £2,547,621.82 (11.6%); £2,881,406.20 -> £2,547,621.85 (11.6%); £2,881,406.25 -> £2,547,621.89 (11.6%); £2,881,406.29 -> £2,547,621.93 (11.6%); £2,881,406.33 -> £2,547,622.33 (11.6%); £2,881,406.38 -> £2,547,622.35 (11.6%); £2,881,406.43 -> £2,547,622.37 (11.6%); £2,881,406.48 -> £2,547,622.38 (11.6%); £2,881,406.53 -> £2,547,622.39 (11.6%); £2,881,406.57 -> £2,547,622.40 (11.6%); £2,881,406.62 -> £2,547,563.28 (11.6%); £2,881,406.63 -> £2,547,622.63 (11.6%); £2,881,406.67 -> £2,547,622.67 (11.6%); £2,881,406.71 -> £2,547,622.69 (11.6%); £2,881,406.75 -> £2,547,622.72 (11.6%); £2,881,406.79 -> £2,547,622.75 (11.6%); £2,881,406.81 -> £2,547,623.10 (11.6%); £2,881,406.86 -> £2,547,623.11 (11.6%); £2,881,406.91 -> £2,547,623.12 (11.6%); £2,881,406.96 -> £2,547,623.12 (11.6%); £2,881,407.01 -> £2,547,623.12 (11.6%); £2,881,407.05 -> £2,547,623.13 (11.6%); £2,881,407.09 -> £2,547,562.08 (11.6%); £2,881,407.13 -> £2,547,623.41 (11.6%); £2,881,407.17 -> £2,547,623.44 (11.6%); £2,881,407.21 -> £2,547,623.47 (11.6%); £2,881,407.26 -> £2,547,623.50 (11.6%); £2,881,407.29 -> £2,547,623.94 (11.6%); £2,881,407.35 -> £2,547,623.98 (11.6%); £2,881,407.40 -> £2,547,623.99 (11.6%); £2,881,407.45 -> £2,547,624.01 (11.6%); £2,881,407.50 -> £2,547,624.02 (11.6%); £2,881,407.55 -> £2,547,624.04 (11.6%); £2,881,407.59 -> £2,547,557.29 (11.6%); £2,881,407.60 -> £2,547,626.40 (11.6%); £2,881,407.65 -> £2,547,626.41 (11.6%); £2,881,407.71 -> £2,547,626.42 (11.6%); £2,881,407.76 -> £2,547,626.42 (11.6%); £2,881,407.81 -> £2,547,626.43 (11.6%); £2,881,407.86 -> £2,547,556.09 (11.6%); £2,881,407.92 -> £2,547,626.67 (11.6%); £2,881,408.03 -> £2,547,626.71 (11.6%); £2,881,408.14 -> £2,547,626.75 (11.6%); £2,881,408.25 -> £2,547,626.77 (11.6%); £2,881,408.35 -> £2,547,626.79 (11.6%); £2,881,408.39 -> £2,547,626.81 (11.6%); £2,881,408.43 -> £2,547,626.83 (11.6%); £2,881,408.47 -> £2,547,627.05 (11.6%); £2,881,408.57 -> £2,547,627.06 (11.6%); £2,881,408.66 -> £2,547,627.07 (11.6%); £2,881,408.75 -> £2,547,627.08 (11.6%); £2,881,408.84 -> £2,547,627.10 (11.6%); £2,881,408.94 -> £2,547,627.12 (11.6%); £2,881,409.03 -> £2,547,554.90 (11.6%); £2,881,409.06 -> £2,547,627.34 (11.6%); £2,881,409.11 -> £2,547,627.37 (11.6%); £2,881,409.15 -> £2,547,627.39 (11.6%); £2,881,409.20 -> £2,547,627.43 (11.6%); £2,881,409.23 -> £2,547,627.82 (11.6%); £2,881,409.29 -> £2,547,627.85 (11.6%); £2,881,409.35 -> £2,547,627.88 (11.6%); £2,881,409.41 -> £2,547,627.90 (11.6%); £2,881,409.47 -> £2,547,627.92 (11.6%); £2,881,409.52 -> £2,547,627.94 (11.6%); £2,881,409.58 -> £2,547,553.70 (11.6%); £2,881,409.61 -> £2,547,628.13 (11.6%); £2,881,409.72 -> £2,547,628.15 (11.6%); £2,881,409.82 -> £2,547,628.17 (11.6%); £2,881,409.93 -> £2,547,628.22 (11.6%); £2,881,410.04 -> £2,547,628.25 (11.6%); £2,881,410.09 -> £2,547,628.29 (11.6%); £2,881,410.13 -> £2,547,628.32 (11.6%); £2,881,410.22 -> £2,547,628.75 (11.6%); £2,881,410.33 -> £2,547,628.77 (11.6%); £2,881,410.43 -> £2,547,628.80 (11.6%); £2,881,410.53 -> £2,547,628.82 (11.6%); £2,881,410.64 -> £2,547,628.84 (11.6%); £2,881,410.74 -> £2,547,628.86 (11.6%); £2,881,410.84 -> £2,547,550.11 (11.6%); £2,881,410.92 -> £2,547,630.82 (11.6%); £2,881,411.02 -> £2,547,548.91 (11.6%); £2,881,411.02 -> £2,547,631.04 (11.6%); £2,881,411.06 -> £2,547,631.05 (11.6%); £2,881,411.10 -> £2,547,631.08 (11.6%); £2,881,411.14 -> £2,547,631.10 (11.6%); £2,881,411.19 -> £2,547,631.33 (11.6%); £2,881,411.24 -> £2,547,631.33 (11.6%); £2,881,411.28 -> £2,547,631.34 (11.6%); £2,881,411.33 -> £2,547,631.34 (11.6%); £2,881,411.37 -> £2,547,631.34 (11.6%); £2,881,411.41 -> £2,547,547.72 (11.6%); £2,881,411.42 -> £2,547,631.50 (11.6%); £2,881,411.45 -> £2,547,631.53 (11.6%); £2,881,411.50 -> £2,547,631.56 (11.6%); £2,881,411.54 -> £2,547,631.59 (11.6%); £2,881,411.56 -> £2,547,631.93 (11.6%); £2,881,411.61 -> £2,547,631.93 (11.6%); £2,881,411.66 -> £2,547,631.93 (11.6%); £2,881,411.70 -> £2,547,631.93 (11.6%); £2,881,411.75 -> £2,547,631.94 (11.6%); £2,881,411.79 -> £2,547,631.94 (11.6%); £2,881,411.83 -> £2,547,546.52 (11.6%); £2,881,411.84 -> £2,547,632.02 (11.6%); £2,881,411.92 -> £2,547,632.03 (11.6%); £2,881,412.00 -> £2,547,632.07 (11.6%); £2,881,412.09 -> £2,547,632.07 (11.6%); £2,881,412.12 -> £2,547,632.08 (11.6%); £2,881,412.16 -> £2,547,632.06 (11.6%); £2,881,412.17 -> £2,547,632.24 (11.6%); £2,881,412.26 -> £2,547,632.26 (11.6%); £2,881,412.34 -> £2,547,632.29 (11.6%); £2,881,412.43 -> £2,547,632.30 (11.6%); £2,881,412.52 -> £2,547,632.32 (11.6%); £2,881,412.60 -> £2,547,632.34 (11.6%); £2,881,412.68 -> £2,547,545.32 (11.6%); £2,881,412.73 -> £2,547,632.46 (11.6%); £2,881,412.83 -> £2,547,632.50 (11.6%); £2,881,412.94 -> £2,547,632.53 (11.6%); £2,881,413.04 -> £2,547,632.56 (11.6%); £2,881,413.09 -> £2,547,632.59 (11.6%); £2,881,413.13 -> £2,547,632.60 (11.6%); £2,881,413.14 -> £2,547,632.75 (11.6%); £2,881,413.24 -> £2,547,632.76 (11.6%); £2,881,413.34 -> £2,547,632.78 (11.6%); £2,881,413.44 -> £2,547,632.80 (11.6%); £2,881,413.54 -> £2,547,632.81 (11.6%); £2,881,413.62 -> £2,547,632.82 (11.6%); £2,881,413.71 -> £2,547,540.53 (11.6%); £2,881,413.73 -> £2,547,635.14 (11.6%); £2,881,413.82 -> £2,547,635.17 (11.6%); £2,881,413.92 -> £2,547,635.18 (11.6%); £2,881,414.00 -> £2,547,635.21 (11.6%); £2,881,414.09 -> £2,547,635.23 (11.6%); £2,881,414.18 -> £2,547,635.25 (11.6%); £2,881,414.27 -> £2,547,539.34 (11.6%); £2,881,414.39 -> £2,547,635.46 (11.6%); £2,881,414.54 -> £2,547,635.48 (11.6%); £2,881,414.69 -> £2,547,635.53 (11.6%); £2,881,414.85 -> £2,547,635.58 (11.6%); £2,881,415.02 -> £2,547,635.62 (11.6%); £2,881,415.06 -> £2,547,635.65 (11.6%); £2,881,415.11 -> £2,547,635.69 (11.6%); £2,881,415.22 -> £2,547,636.09 (11.6%); £2,881,415.35 -> £2,547,636.10 (11.6%); £2,881,415.48 -> £2,547,636.13 (11.6%); £2,881,415.63 -> £2,547,636.16 (11.6%); £2,881,415.77 -> £2,547,636.17 (11.6%); £2,881,415.89 -> £2,547,636.19 (11.6%); £2,881,416.03 -> £2,547,538.38 (11.6%); £2,881,416.13 -> £2,547,636.48 (11.6%); £2,881,416.26 -> £2,547,636.49 (11.6%); £2,881,416.38 -> £2,547,636.51 (11.6%); £2,881,416.50 -> £2,547,636.54 (11.6%); £2,881,416.62 -> £2,547,636.56 (11.6%); £2,881,416.66 -> £2,547,636.58 (11.6%); £2,881,416.70 -> £2,547,636.61 (11.6%); £2,881,416.78 -> £2,547,636.92 (11.6%); £2,881,416.88 -> £2,547,636.93 (11.6%); £2,881,416.99 -> £2,547,636.93 (11.6%); £2,881,417.09 -> £2,547,636.94 (11.6%); £2,881,417.19 -> £2,547,636.95 (11.6%); £2,881,417.29 -> £2,547,636.96 (11.6%); £2,881,417.40 -> £2,547,537.43 (11.6%); £2,881,417.44 -> £2,547,637.15 (11.6%); £2,881,417.50 -> £2,547,637.17 (11.6%); £2,881,417.56 -> £2,547,637.19 (11.6%); £2,881,417.60 -> £2,547,637.20 (11.6%); £2,881,417.64 -> £2,547,637.22 (11.6%); £2,881,417.68 -> £2,547,637.56 (11.6%); £2,881,417.75 -> £2,547,637.59 (11.6%); £2,881,417.83 -> £2,547,637.61 (11.6%); £2,881,417.89 -> £2,547,637.63 (11.6%); £2,881,417.97 -> £2,547,637.65 (11.6%); £2,881,418.04 -> £2,547,637.68 (11.6%); £2,881,418.11 -> £2,547,534.56 (11.6%); £2,881,418.15 -> £2,547,533.61 (11.6%); £2,881,418.16 -> £2,547,640.22 (11.6%); £2,881,418.21 -> £2,547,640.27 (11.6%); £2,881,418.25 -> £2,547,640.33 (11.6%); £2,881,418.30 -> £2,547,640.38 (11.6%); £2,881,418.34 -> £2,547,640.42 (11.6%); £2,881,418.39 -> £2,547,640.47 (11.6%); £2,881,418.44 -> £2,547,640.98 (11.6%); £2,881,418.50 -> £2,547,641.00 (11.6%); £2,881,418.56 -> £2,547,641.01 (11.6%); £2,881,418.63 -> £2,547,641.04 (11.6%); £2,881,418.70 -> £2,547,641.06 (11.6%); £2,881,418.77 -> £2,547,641.08 (11.6%); £2,881,418.84 -> £2,547,532.65 (11.6%); £2,881,418.88 -> £2,547,641.44 (11.6%); £2,881,418.92 -> £2,547,641.50 (11.6%); £2,881,418.97 -> £2,547,641.57 (11.6%); £2,881,419.02 -> £2,547,641.62 (11.6%); £2,881,419.06 -> £2,547,641.67 (11.6%); £2,881,419.11 -> £2,547,641.72 (11.6%); £2,881,419.12 -> £2,547,642.24 (11.6%); £2,881,419.18 -> £2,547,642.30 (11.6%); £2,881,419.24 -> £2,547,642.34 (11.6%); £2,881,419.31 -> £2,547,642.36 (11.6%); £2,881,419.37 -> £2,547,642.37 (11.6%); £2,881,419.44 -> £2,547,642.38 (11.6%); £2,881,419.50 -> £2,547,642.39 (11.6%); £2,881,419.57 -> £2,547,531.69 (11.6%); £2,881,419.59 -> £2,547,642.65 (11.6%); £2,881,419.65 -> £2,547,642.68 (11.6%); £2,881,419.69 -> £2,547,642.74 (11.6%); £2,881,419.75 -> £2,547,642.76 (11.6%); £2,881,419.79 -> £2,547,642.79 (11.6%); £2,881,419.83 -> £2,547,642.84 (11.6%); £2,881,419.88 -> £2,547,643.30 (11.6%); £2,881,419.95 -> £2,547,643.34 (11.6%); £2,881,420.02 -> £2,547,643.37 (11.6%); £2,881,420.10 -> £2,547,643.40 (11.6%); £2,881,420.18 -> £2,547,643.43 (11.6%); £2,881,420.26 -> £2,547,643.45 (11.6%); £2,881,420.33 -> £2,547,530.74 (11.6%); £2,881,420.34 -> £2,547,643.71 (11.6%); £2,881,420.41 -> £2,547,643.74 (11.6%); £2,881,420.47 -> £2,547,643.79 (11.6%); £2,881,420.54 -> £2,547,643.85 (11.6%); £2,881,420.61 -> £2,547,643.89 (11.6%); £2,881,420.66 -> £2,547,643.94 (11.6%); £2,881,420.70 -> £2,547,643.99 (11.6%); £2,881,420.77 -> £2,547,644.49 (11.6%); £2,881,420.85 -> £2,547,644.53 (11.6%); £2,881,420.94 -> £2,547,644.56 (11.6%); £2,881,421.02 -> £2,547,644.57 (11.6%); £2,881,421.11 -> £2,547,644.60 (11.6%); £2,881,421.20 -> £2,547,644.62 (11.6%); £2,881,421.28 -> £2,547,527.87 (11.6%); £2,881,421.35 -> £2,547,526.92 (11.6%); £2,881,421.46 -> £2,547,647.01 (11.6%); £2,881,421.62 -> £2,547,647.07 (11.6%); £2,881,421.76 -> £2,547,647.14 (11.6%); £2,881,421.91 -> £2,547,647.21 (11.6%); £2,881,422.05 -> £2,547,647.25 (11.6%); £2,881,422.10 -> £2,547,647.30 (11.6%); £2,881,422.15 -> £2,547,647.34 (11.6%); £2,881,422.26 -> £2,547,647.82 (11.6%); £2,881,422.40 -> £2,547,647.85 (11.6%); £2,881,422.52 -> £2,547,647.88 (11.6%); £2,881,422.65 -> £2,547,647.90 (11.6%); £2,881,422.79 -> £2,547,647.94 (11.6%); £2,881,422.93 -> £2,547,647.98 (11.6%); £2,881,423.08 -> £2,547,525.96 (11.6%); £2,881,423.20 -> £2,547,648.31 (11.6%); £2,881,423.36 -> £2,547,648.34 (11.6%); £2,881,423.52 -> £2,547,648.37 (11.6%); £2,881,423.68 -> £2,547,648.41 (11.6%); £2,881,423.84 -> £2,547,648.43 (11.6%); £2,881,423.89 -> £2,547,648.45 (11.6%); £2,881,423.93 -> £2,547,648.48 (11.6%); £2,881,424.04 -> £2,547,648.87 (11.6%); £2,881,424.19 -> £2,547,648.90 (11.6%); £2,881,424.34 -> £2,547,648.92 (11.6%); £2,881,424.49 -> £2,547,648.94 (11.6%); £2,881,424.64 -> £2,547,648.99 (11.6%); £2,881,424.81 -> £2,547,649.01 (11.6%); £2,881,424.97 -> £2,547,525.01 (11.6%); £2,881,424.97 -> £2,547,649.34 (11.6%); £2,881,425.20 -> £2,547,649.37 (11.6%); £2,881,425.43 -> £2,547,649.41 (11.6%); £2,881,425.65 -> £2,547,649.45 (11.6%); £2,881,425.87 -> £2,547,649.51 (11.6%); £2,881,426.11 -> £2,547,649.55 (11.6%); £2,881,426.15 -> £2,547,649.60 (11.6%); £2,881,426.20 -> £2,547,649.64 (11.6%); £2,881,426.38 -> £2,547,650.12 (11.6%); £2,881,426.58 -> £2,547,650.16 (11.6%); £2,881,426.77 -> £2,547,650.19 (11.6%); £2,881,426.97 -> £2,547,650.23 (11.6%); £2,881,427.18 -> £2,547,650.27 (11.6%); £2,881,427.40 -> £2,547,650.31 (11.6%); £2,881,427.61 -> £2,547,524.05 (11.6%); £2,881,427.62 -> £2,547,650.70 (11.6%); £2,881,427.90 -> £2,547,650.76 (11.6%); £2,881,428.20 -> £2,547,650.83 (11.6%); £2,881,428.48 -> £2,547,650.92 (11.6%); £2,881,428.78 -> £2,547,651.02 (11.6%); £2,881,429.08 -> £2,547,651.07 (11.6%); £2,881,429.13 -> £2,547,651.11 (11.6%); £2,881,429.17 -> £2,547,651.16 (11.6%); £2,881,429.41 -> £2,547,651.76 (11.6%); £2,881,429.67 -> £2,547,651.84 (11.6%); £2,881,429.92 -> £2,547,651.90 (11.6%); £2,881,430.16 -> £2,547,651.95 (11.6%); £2,881,430.41 -> £2,547,652.01 (11.6%); £2,881,430.66 -> £2,547,652.06 (11.6%); £2,881,430.91 -> £2,547,521.19 (11.6%); £2,881,430.94 -> £2,547,655.69 (11.6%); £2,881,430.98 -> £2,547,655.74 (11.6%); £2,881,431.13 -> £2,547,656.19 (11.6%); £2,881,431.31 -> £2,547,656.23 (11.6%); £2,881,431.48 -> £2,547,656.27 (11.6%); £2,881,431.65 -> £2,547,656.30 (11.6%); £2,881,431.83 -> £2,547,656.35 (11.6%); £2,881,432.03 -> £2,547,656.40 (11.6%); £2,881,432.22 -> £2,547,520.23 (11.6%); £2,881,432.32 -> £2,547,656.89 (11.6%); £2,881,432.45 -> £2,547,656.93 (11.6%); £2,881,432.58 -> £2,547,656.98 (11.6%); £2,881,432.71 -> £2,547,657.04 (11.6%); £2,881,432.83 -> £2,547,657.07 (11.6%); £2,881,432.88 -> £2,547,657.11 (11.6%); £2,881,432.92 -> £2,547,657.14 (11.6%); £2,881,433.04 -> £2,547,657.69 (11.6%); £2,881,433.17 -> £2,547,657.73 (11.6%); £2,881,433.29 -> £2,547,657.78 (11.6%); £2,881,433.42 -> £2,547,657.80 (11.6%); £2,881,433.55 -> £2,547,657.85 (11.6%); £2,881,433.69 -> £2,547,657.90 (11.6%); £2,881,433.83 -> £2,547,519.27 (11.6%); £2,881,433.88 -> £2,547,658.32 (11.6%); £2,881,433.98 -> £2,547,658.36 (11.6%); £2,881,434.07 -> £2,547,658.40 (11.6%); £2,881,434.16 -> £2,547,658.44 (11.6%); £2,881,434.25 -> £2,547,658.47 (11.6%); £2,881,434.30 -> £2,547,658.50 (11.6%); £2,881,434.34 -> £2,547,658.53 (11.6%); £2,881,434.43 -> £2,547,659.08 (11.6%); £2,881,434.53 -> £2,547,659.12 (11.6%); £2,881,434.63 -> £2,547,659.15 (11.6%); £2,881,434.73 -> £2,547,659.18 (11.6%); £2,881,434.84 -> £2,547,659.20 (11.6%); £2,881,434.94 -> £2,547,659.23 (11.6%); £2,881,435.05 -> £2,547,518.32 (11.6%); £2,881,435.10 -> £2,547,659.57 (11.6%); £2,881,435.21 -> £2,547,659.63 (11.6%); £2,881,435.33 -> £2,547,659.68 (11.6%); £2,881,435.43 -> £2,547,659.73 (11.6%); £2,881,435.53 -> £2,547,659.77 (11.6%); £2,881,435.58 -> £2,547,659.81 (11.6%); £2,881,435.62 -> £2,547,659.84 (11.6%); £2,881,435.69 -> £2,547,660.21 (11.6%); £2,881,435.79 -> £2,547,660.23 (11.6%); £2,881,435.89 -> £2,547,660.24 (11.6%); £2,881,435.99 -> £2,547,660.25 (11.6%); £2,881,436.09 -> £2,547,660.27 (11.6%); £2,881,436.20 -> £2,547,660.29 (11.6%); £2,881,436.31 -> £2,547,517.36 (11.6%); £2,881,436.52 -> £2,547,660.60 (11.6%); £2,881,436.74 -> £2,547,660.63 (11.6%); £2,881,436.95 -> £2,547,660.67 (11.6%); £2,881,437.17 -> £2,547,660.72 (11.6%); £2,881,437.38 -> £2,547,660.74 (11.6%); £2,881,437.43 -> £2,547,660.77 (11.6%); £2,881,437.47 -> £2,547,660.80 (11.6%); £2,881,437.66 -> £2,547,661.36 (11.6%); £2,881,437.86 -> £2,547,661.42 (11.6%); £2,881,438.07 -> £2,547,661.47 (11.6%); £2,881,438.28 -> £2,547,661.52 (11.6%); £2,881,438.49 -> £2,547,661.57 (11.6%); £2,881,438.70 -> £2,547,661.62 (11.6%); £2,881,438.91 -> £2,547,514.50 (11.6%); £2,881,438.96 -> £2,547,665.15 (11.6%); £2,881,439.01 -> £2,547,665.20 (11.6%); £2,881,439.06 -> £2,547,665.25 (11.6%); £2,881,439.28 -> £2,547,665.83 (11.6%); £2,881,439.51 -> £2,547,665.88 (11.6%); £2,881,439.73 -> £2,547,665.93 (11.6%); £2,881,439.95 -> £2,547,665.98 (11.6%); £2,881,440.18 -> £2,547,666.02 (11.6%); £2,881,440.41 -> £2,547,666.06 (11.6%); £2,881,440.63 -> £2,547,513.54 (11.6%); £2,881,440.73 -> £2,547,666.63 (11.6%); £2,881,441.05 -> £2,547,666.71 (11.6%); £2,881,441.37 -> £2,547,666.79 (11.6%); £2,881,441.69 -> £2,547,666.87 (11.6%); £2,881,441.99 -> £2,547,666.96 (11.6%); £2,881,442.30 -> £2,547,667.00 (11.6%); £2,881,442.34 -> £2,547,667.04 (11.6%); £2,881,442.39 -> £2,547,667.07 (11.6%); £2,881,442.61 -> £2,547,667.57 (11.6%); £2,881,442.86 -> £2,547,667.61 (11.6%); £2,881,443.10 -> £2,547,667.65 (11.6%); £2,881,443.34 -> £2,547,667.69 (11.6%); £2,881,443.60 -> £2,547,667.74 (11.6%); £2,881,443.85 -> £2,547,667.79 (11.6%); £2,881,444.10 -> £2,547,512.59 (11.6%); £2,881,444.28 -> £2,547,668.29 (11.6%); £2,881,444.55 -> £2,547,668.38 (11.6%); £2,881,444.84 -> £2,547,668.46 (11.6%); £2,881,445.11 -> £2,547,668.56 (11.6%); £2,881,445.39 -> £2,547,668.59 (11.6%); £2,881,445.43 -> £2,547,668.62 (11.6%); £2,881,445.47 -> £2,547,668.67 (11.6%); £2,881,445.69 -> £2,547,669.24 (11.6%); £2,881,445.93 -> £2,547,669.29 (11.6%); £2,881,446.14 -> £2,547,669.31 (11.6%); £2,881,446.35 -> £2,547,669.33 (11.6%); £2,881,446.56 -> £2,547,669.37 (11.6%); £2,881,446.78 -> £2,547,669.40 (11.6%); £2,881,447.00 -> £2,547,511.63 (11.6%); £2,881,447.12 -> £2,547,669.90 (11.6%); £2,881,447.30 -> £2,547,669.95 (11.6%); £2,881,447.49 -> £2,547,670.01 (11.6%); £2,881,447.67 -> £2,547,670.08 (11.6%); £2,881,447.85 -> £2,547,670.11 (11.6%); £2,881,447.90 -> £2,547,670.14 (11.6%); £2,881,447.94 -> £2,547,670.18 (11.6%); £2,881,448.09 -> £2,547,670.70 (11.6%); £2,881,448.26 -> £2,547,670.76 (11.6%); £2,881,448.43 -> £2,547,670.81 (11.6%); £2,881,448.60 -> £2,547,670.87 (11.6%); £2,881,448.78 -> £2,547,670.91 (11.6%); £2,881,448.96 -> £2,547,670.96 (11.6%); £2,881,449.14 -> £2,547,510.68 (11.6%); £2,882,054.24 -> £2,547,463.49 (11.6%); £3,080,208.20 -> £2,547,750.88 (17.3%)
- Bills issued: 156, average clarity 0.835, average bill shock 18.7%, bad debt provision £75,448.55, avg complaint probability 4.8%
- Solvency signal: £254,775/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £84,088.44 vs. naked (unhedged) net margin: £1,232,082.10
- hedging cost £1,147,993.66 vs. a fully unhedged book (commodity-only: actual net £84,088.44 vs. naked net £1,232,082.10)
  - C2: actual £-263.78 vs. naked £565.72 -- hedging cost £829.50
  - C2g: actual £-222.05 vs. naked £-60.48 -- hedging cost £161.57
  - C4: actual £-545.96 vs. naked £811.29 -- hedging cost £1,357.25
  - C4g: actual £-1,481.14 vs. naked £778.72 -- hedging cost £2,259.86
  - C6: actual £567.65 vs. naked £2,532.35 -- hedging cost £1,964.70
  - C7: actual £-248.02 vs. naked £2,154.89 -- hedging cost £2,402.91
  - C8: actual £-122.41 vs. naked £962.48 -- hedging cost £1,084.89
  - C9: actual £671.31 vs. naked £1,430.81 -- hedging cost £759.50
  - C_IC1: actual £243,570.41 vs. naked £257,385.20 -- hedging cost £13,814.78
  - C_IC2: actual £89,932.95 vs. naked £116,316.98 -- hedging cost £26,384.03
  - C_IC3: actual £200,302.28 vs. naked £804,392.68 -- hedging cost £604,090.40
  - C_IC3g: actual £-252,917.30 vs. naked £83,300.79 -- hedging cost £336,218.09
  - C_IC4: actual £-195,155.50 vs. naked £-38,489.32 -- hedging cost £156,666.18

**Year narrative:** 2022 (flagged crisis year) produced a net loss of £-13,732.88 across 13 accounts. The risk committee intervened 9 time(s), raising hedge fractions in response to elevated VaR. 50 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £111,215.80 (gross £913,513.33, capital £10,111.66)
  - Electricity: gross £1,054,648.26, capital £9,695.48, net £365,541.28
  - Gas: gross £-141,134.93, capital £416.18, net £-254,325.48
- Treasury at year end: £2,631,973.76
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.95 (avg 0.95), C2g 0.85 (avg 0.85), C4 0.90 (avg 0.90), C4g 0.85 (avg 0.85), C6 0.93 (avg 0.93), C7 0.92 (avg 0.92), C8 0.95 (avg 0.95), C9 0.93 (avg 0.93), C_IC1 0.85 (avg 0.89), C_IC2 0.85 (avg 0.89), C_IC3 0.96 (avg 0.96), C_IC3g 0.90 (avg 0.90), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 4
  - 2023-01-24: treasury £2,547,726.38, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £124,979.84 / stressed £45,252.01) ratio 2.76
  - 2023-02-23: treasury £2,547,694.04, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £124,979.84 / stressed £45,252.01) ratio 2.76
  - 2023-03-25: treasury £2,547,661.97, C4->1.00, C6->1.00, C7->1.00, C8->1.00, C9->1.00, C_IC1->1.00, C_IC2->1.00, C_IC3->1.00, VaR (current £124,979.84 / stressed £45,252.01) ratio 2.76
  - 2023-04-24: treasury £2,631,825.89, C4->1.00, C7->1.00, C9->1.00, C_IC3->1.00, VaR (current £129,684.71 / stressed £49,304.48) ratio 2.63
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.73
- Worst single period: C_IC3g on 2023-07-01 period 1, net margin £-813.88

**Customer Book**

- Active accounts: 13 (C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 7 accounts
- Average CLV (Point-in-Time, year-end 2023): £215,463.43
  - By billing account: C1 £1,728.28, C2 £3,682.40, C3 £2,015.64, C4 £947.01, C5 £5,859.49, C6 £9,166.72, C7 £3,785.43, C8 £5,584.19, C9 £5,875.99, C_IC1 £994,238.86, C_IC2 £506,917.05, C_IC3 £1,243,618.11, C_IC4 £17,605.47
- Bill shock events (>=20%): 33 -- C7 2023-01-31 (41%); C7 2023-05-31 (32%); C7 2023-06-30 (38%); C7 2023-10-31 (58%); C7 2023-11-30 (74%); C2 2023-04-30 (23%); C2g 2023-04-30 (24%); C6 2023-04-30 (20%); C6 2023-05-31 (24%); C6 2023-06-30 (23%); C6 2023-10-31 (39%); C6 2023-11-30 (45%); C8 2023-04-30 (31%); C8 2023-05-31 (41%); C8 2023-06-30 (44%); C8 2023-10-31 (101%); C8 2023-11-30 (70%); C9 2023-02-28 (21%); C9 2023-03-31 (21%); C9 2023-04-30 (27%); C9 2023-05-31 (33%); C9 2023-06-30 (46%); C9 2023-09-30 (23%); C9 2023-10-31 (77%); C9 2023-11-30 (55%); C4g 2023-10-31 (20%); C_IC1 2023-06-30 (55%); C_IC1 2023-07-31 (105%); C_IC2 2023-05-31 (54%); C_IC2 2023-06-30 (134%); C_IC3 2023-01-31 (29%); C_IC3g 2023-01-31 (34%); C_IC4 2023-01-31 (46%)
- Churn risk (accounts renewing in 2023): 6 at risk (≥20% churn prob): C2 20%, C6 29%, C7 38%, C8 38%, C9 41%, C_IC4 32%

**Pricing & Margin**

- C2 (electricity): tariff £265.00-£305.00/MWh, net margin £-129.34 -- **net-negative**
- C2g (gas): tariff £70.00-£95.00/MWh, net margin £74.80
- C4 (electricity): tariff £250.24-£305.00/MWh, net margin £-334.22 -- **net-negative**
- C4g (gas): tariff £69.27-£95.00/MWh, net margin £-985.18 -- **net-negative**
- C6 (electricity): tariff £380.21-£382.27/MWh, net margin £1,360.29
- C7 (electricity): tariff £169.38-£457.50/MWh, net margin £-250.76 -- **net-negative**
- C8 (electricity): tariff £208.21-£457.50/MWh, net margin £36.54
- C9 (electricity): tariff £208.21-£457.50/MWh, net margin £704.43
- C_IC1 (electricity): tariff £-60.00-£458.04/MWh, net margin £252,456.20
- C_IC2 (electricity): tariff £-186.24-£453.31/MWh, net margin £106,619.95
- C_IC3 (electricity): tariff £76.02-£402.96/MWh, net margin £200,354.17
- C_IC3g (gas): tariff £56.41-£156.73/MWh, net margin £-253,415.10 -- **net-negative**
- C_IC4 (electricity): tariff £36.40-£169.32/MWh, net margin £-195,275.98 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 1.1% of gross
- Treasury drawdown events (>=10% threshold): 64 -- £3,079,769.51 -> £2,547,434.44 (17.3%); £3,079,776.73 -> £2,631,973.99 (14.5%); £3,079,823.53 -> £2,631,973.98 (14.5%); £3,079,871.51 -> £2,631,973.98 (14.5%); £3,079,917.94 -> £2,631,973.97 (14.5%); £3,079,964.63 -> £2,631,973.97 (14.5%); £3,080,009.73 -> £2,631,973.97 (14.5%); £3,080,011.29 -> £2,631,973.96 (14.5%); £3,080,012.86 -> £2,631,973.96 (14.5%); £3,080,013.62 -> £2,631,973.96 (14.5%); £3,080,014.37 -> £2,631,973.95 (14.5%); £3,080,015.47 -> £2,631,973.95 (14.5%); £3,080,016.63 -> £2,631,973.95 (14.5%); £3,080,017.62 -> £2,631,973.95 (14.5%); £3,080,018.66 -> £2,631,973.95 (14.5%); £3,080,020.45 -> £2,631,973.94 (14.5%); £3,080,021.42 -> £2,631,973.94 (14.5%); £3,080,022.96 -> £2,631,973.93 (14.5%); £3,080,024.55 -> £2,631,973.93 (14.5%); £3,080,026.43 -> £2,631,973.93 (14.5%); £3,080,028.31 -> £2,631,973.93 (14.5%); £3,080,030.16 -> £2,631,973.92 (14.5%); £3,080,032.05 -> £2,631,973.92 (14.5%); £3,080,033.91 -> £2,631,973.92 (14.5%); £3,080,035.81 -> £2,631,973.92 (14.5%); £3,080,037.61 -> £2,631,973.92 (14.5%); £3,080,038.17 -> £2,631,973.92 (14.5%); £3,080,039.83 -> £2,631,973.92 (14.5%); £3,080,041.61 -> £2,631,973.92 (14.5%); £3,080,043.21 -> £2,631,973.91 (14.5%); £3,080,044.74 -> £2,631,973.91 (14.5%); £3,080,046.35 -> £2,631,973.91 (14.5%); £3,080,047.13 -> £2,631,973.91 (14.5%); £3,080,048.62 -> £2,631,973.91 (14.5%); £3,080,050.16 -> £2,631,973.91 (14.5%); £3,080,051.65 -> £2,631,973.90 (14.5%); £3,080,052.46 -> £2,631,973.90 (14.5%); £3,080,053.19 -> £2,631,973.90 (14.5%); £3,080,053.96 -> £2,631,973.90 (14.5%); £3,080,054.74 -> £2,631,973.90 (14.5%); £3,080,056.35 -> £2,631,973.89 (14.5%); £3,080,057.66 -> £2,631,973.89 (14.5%); £3,080,058.73 -> £2,631,973.89 (14.5%); £3,080,059.59 -> £2,631,973.89 (14.5%); £3,080,060.43 -> £2,631,973.89 (14.5%); £3,080,061.26 -> £2,631,973.89 (14.5%); £3,080,062.06 -> £2,631,973.88 (14.5%); £3,080,062.91 -> £2,631,973.88 (14.5%); £3,080,063.74 -> £2,631,973.88 (14.5%); £3,080,064.49 -> £2,631,973.87 (14.5%); £3,080,065.11 -> £2,631,973.87 (14.5%); £3,080,065.91 -> £2,631,973.86 (14.5%); £3,080,066.80 -> £2,631,973.86 (14.5%); £3,080,067.64 -> £2,631,973.86 (14.5%); £3,080,069.16 -> £2,631,973.85 (14.5%); £3,080,070.74 -> £2,631,973.85 (14.5%); £3,080,071.55 -> £2,631,973.85 (14.5%); £3,080,073.06 -> £2,631,973.85 (14.5%); £3,080,074.59 -> £2,631,973.84 (14.5%); £3,080,076.21 -> £2,631,973.84 (14.5%); £3,080,077.83 -> £2,631,973.84 (14.5%); £3,080,079.67 -> £2,631,973.84 (14.5%); £3,080,081.51 -> £2,631,973.84 (14.5%); £3,118,480.43 -> £2,631,973.76 (15.6%)
- Bills issued: 156, average clarity 0.855, average bill shock 14.2%, bad debt provision £72,135.14, avg complaint probability 4.1%
- Solvency signal: £263,197/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £241,127.77 vs. naked (unhedged) net margin: £997,856.14
- hedging cost £756,728.37 vs. a fully unhedged book (commodity-only: actual net £241,127.77 vs. naked net £997,856.14)
  - C2: actual £-42.87 vs. naked £1,067.28 -- hedging cost £1,110.15
  - C2g: actual £141.84 vs. naked £441.37 -- hedging cost £299.53
  - C4: actual £242.29 vs. naked £900.75 -- hedging cost £658.46
  - C4g: actual £483.47 vs. naked £715.92 -- hedging cost £232.45
  - C6: actual £1,873.05 vs. naked £4,682.54 -- hedging cost £2,809.48
  - C7: actual £132.52 vs. naked £1,465.63 -- hedging cost £1,333.11
  - C8: actual £216.68 vs. naked £1,813.97 -- hedging cost £1,597.29
  - C9: actual £867.16 vs. naked £2,218.27 -- hedging cost £1,351.11
  - C_IC1: actual £308,186.48 vs. naked £445,847.55 -- hedging cost £137,661.07
  - C_IC2: actual £132,423.31 vs. naked £197,653.50 -- hedging cost £65,230.19
  - C_IC3: actual £42,318.89 vs. naked £310,644.61 -- hedging cost £268,325.72
  - C_IC3g: actual £-17,160.47 vs. naked £77,607.60 -- hedging cost £94,768.08
  - C_IC4: actual £-228,554.58 vs. naked £-47,202.85 -- hedging cost £181,351.73

**Year narrative:** 2023 produced a net gain of £111,215.80 across 13 accounts. The risk committee intervened 4 time(s), raising hedge fractions in response to elevated VaR. 33 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £79,582.59 (gross £999,998.28, capital £14,220.76)
  - Electricity: gross £898,015.39, capital £9,393.95, net £96,370.48
  - Gas: gross £101,982.89, capital £4,826.81, net £-16,787.89
- Treasury at year end: £2,873,173.32
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.91 (avg 0.91), C2g 0.85 (avg 0.85), C4 0.87 (avg 0.87), C4g 0.85 (avg 0.85), C7 0.87 (avg 0.87), C8 0.91 (avg 0.91), C9 0.88 (avg 0.88), C_IC1 0.85 (avg 0.86), C_IC2 0.85 (avg 0.87), C_IC3 0.94 (avg 0.94), C_IC3g 0.85 (avg 0.85), C_IC4 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2024-12-30 period 1, net margin £-276.23

**Customer Book**

- Active accounts: 13 (C2, C2g, C4, C4g, C6, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: C6
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2024): £240,321.17
  - By billing account: C1 £1,695.21, C2 £4,148.85, C3 £2,078.58, C4 £1,700.28, C5 £6,015.20, C6 £8,969.23, C7 £4,080.78, C8 £5,854.73, C9 £5,940.97, C_IC1 £1,048,489.96, C_IC2 £507,492.57, C_IC3 £1,509,734.50, C_IC4 £17,974.37
- Bill shock events (>=20%): 25 -- C7 2024-02-29 (27%); C7 2024-05-31 (38%); C7 2024-09-30 (37%); C7 2024-10-31 (39%); C7 2024-11-30 (51%); C2 2024-04-30 (29%); C8 2024-02-29 (23%); C8 2024-04-30 (34%); C8 2024-05-31 (50%); C8 2024-07-31 (28%); C8 2024-09-30 (81%); C8 2024-10-31 (37%); C8 2024-11-30 (65%); C9 2024-05-31 (50%); C9 2024-07-31 (35%); C9 2024-09-30 (60%); C9 2024-10-31 (23%); C9 2024-11-30 (49%); C4g 2024-10-31 (27%); C_IC1 2024-07-31 (50%); C_IC1 2024-08-31 (66%); C_IC2 2024-06-30 (56%); C_IC2 2024-07-31 (119%); C_IC3 2024-01-31 (41%); C_IC4 2024-05-31 (25%)
- Churn risk (accounts renewing in 2024): 6 at risk (≥20% churn prob): C6 41%, C7 35%, C8 41%, C9 38%, C_IC3 20%, C_IC4 26%

**Pricing & Margin**

- C2 (electricity): tariff £210.00-£265.00/MWh, net margin £28.92
- C2g (gas): tariff £55.00-£70.00/MWh, net margin £207.50
- C4 (electricity): tariff £210.00-£250.24/MWh, net margin £176.40
- C4g (gas): tariff £43.57-£69.27/MWh, net margin £346.43
- C6 (electricity): tariff £380.21/MWh, net margin £641.03
- C7 (electricity): tariff £165.00-£323.36/MWh, net margin £133.12
- C8 (electricity): tariff £165.00-£397.50/MWh, net margin £280.99
- C9 (electricity): tariff £165.00-£397.50/MWh, net margin £620.62
- C_IC1 (electricity): tariff £-98.58-£430.97/MWh, net margin £196,500.83
- C_IC2 (electricity): tariff £-106.92-£393.03/MWh, net margin £85,056.90
- C_IC3 (electricity): tariff £75.71-£145.12/MWh, net margin £42,309.92
- C_IC3g (gas): tariff £41.59-£56.41/MWh, net margin £-17,341.82 -- **net-negative**
- C_IC4 (electricity): tariff £23.97-£113.12/MWh, net margin £-229,378.26 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 1.4% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £3,118,390.04 -> £2,631,965.85 (15.6%)
- Bills issued: 147, average clarity 0.862, average bill shock 12.9%, bad debt provision £53,972.65, avg complaint probability 3.9%
- Solvency signal: £287,317/customer (10 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £51,330.68 vs. naked (unhedged) net margin: £395,488.89
- hedging cost £344,158.21 vs. a fully unhedged book (commodity-only: actual net £51,330.68 vs. naked net £395,488.89)
  - C2: actual £45.20 vs. naked £785.98 -- hedging cost £740.78
  - C2g: actual £219.54 vs. naked £238.87 -- hedging cost £19.32
  - C4: actual £12.88 vs. naked £415.49 -- hedging cost £402.60
  - C4g: actual £-75.47 vs. naked £-22.56 -- hedging cost £52.90
  - C7: actual £-52.16 vs. naked £567.90 -- hedging cost £620.06
  - C8: actual £293.11 vs. naked £1,269.97 -- hedging cost £976.86
  - C9: actual £264.84 vs. naked £1,235.23 -- hedging cost £970.40
  - C_IC1: actual £97,289.46 vs. naked £188,337.69 -- hedging cost £91,048.23
  - C_IC2: actual £62,613.13 vs. naked £111,527.80 -- hedging cost £48,914.67
  - C_IC3: actual £-5,485.75 vs. naked £92,054.98 -- hedging cost £97,540.73
  - C_IC3g: actual £-4,308.75 vs. naked £25,544.36 -- hedging cost £29,853.11
  - C_IC4: actual £-99,485.34 vs. naked £-26,466.80 -- hedging cost £73,018.54

**Year narrative:** 2024 produced a net gain of £79,582.59 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 25 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £-22,688.54 (gross £382,056.44, capital £9,681.16)
  - Electricity: gross £334,345.76, capital £6,164.49, net £-18,928.56
  - Gas: gross £47,710.68, capital £3,516.68, net £-3,759.98
- Treasury at year end: £2,925,694.56
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.86 (avg 0.86), C2g 0.85 (avg 0.85), C8 0.86 (avg 0.86)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C_IC3g on 2025-06-01 period 1, net margin £-113.52

**Customer Book**

- Active accounts: 12 (C2, C2g, C4, C4g, C7, C8, C9, C_IC1, C_IC2, C_IC3, C_IC3g, C_IC4)
  - Resi electricity: 5, SME electricity: 0, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 2 accounts
- Average CLV (Point-in-Time, year-end 2025): £247,860.78
  - By billing account: C1 £1,706.99, C2 £3,690.03, C3 £1,984.40, C4 £1,816.87, C5 £5,786.47, C6 £8,671.67, C7 £4,453.68, C8 £5,502.70, C9 £6,008.32, C_IC1 £1,127,922.82, C_IC2 £570,813.78, C_IC3 £1,464,274.17, C_IC4 £19,558.27
- Bill shock events (>=20%): 23 -- C7 2025-01-31 (25%); C7 2025-04-30 (38%); C7 2025-05-31 (24%); C7 2025-06-07 (80%); C2 2025-04-30 (21%); C2 2025-06-07 (78%); C2g 2025-06-07 (77%); C8 2025-01-31 (40%); C8 2025-02-28 (24%); C8 2025-04-30 (42%); C8 2025-05-31 (38%); C8 2025-06-07 (73%); C9 2025-01-31 (22%); C9 2025-04-30 (25%); C9 2025-05-31 (34%); C9 2025-06-07 (71%); C4 2025-06-07 (78%); C4g 2025-06-07 (77%); C_IC1 2025-06-07 (77%); C_IC2 2025-06-07 (75%); C_IC3 2025-06-07 (78%); C_IC3g 2025-06-07 (77%); C_IC4 2025-06-07 (81%)
- Churn risk (accounts renewing in 2025): 2 at risk (≥20% churn prob): C8 38%, C9 38%

**Pricing & Margin**

- C2 (electricity): tariff £190.00-£210.00/MWh, net margin £-57.71 -- **net-negative**
- C2g (gas): tariff £52.00-£55.00/MWh, net margin £42.76
- C4 (electricity): tariff £210.00/MWh, net margin £6.04
- C4g (gas): tariff £43.57/MWh, net margin £-46.45 -- **net-negative**
- C7 (electricity): tariff £165.00-£315.00/MWh, net margin £-48.25 -- **net-negative**
- C8 (electricity): tariff £149.29-£315.00/MWh, net margin £62.42
- C9 (electricity): tariff £165.00-£315.00/MWh, net margin £146.25
- C_IC1 (electricity): tariff £155.47-£296.80/MWh, net margin £53,737.14
- C_IC2 (electricity): tariff £157.76-£301.17/MWh, net margin £30,584.61
- C_IC3 (electricity): tariff £75.71-£144.53/MWh, net margin £-5,189.23 -- **net-negative**
- C_IC3g (gas): tariff £41.59/MWh, net margin £-3,756.29 -- **net-negative**
- C_IC4 (electricity): tariff £43.11-£193.69/MWh, net margin £-98,169.84 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 2.5% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 72, average clarity 0.818, average bill shock 22.4%, bad debt provision £23,178.81, avg complaint probability 5.4%
- Solvency signal: £325,077/customer (9 customers) — OK (Ofgem floor £130/customer)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-132.77 vs. naked (unhedged) net margin: £176.78
- hedging cost £309.54 vs. a fully unhedged book (commodity-only: actual net £-132.77 vs. naked net £176.78)
  - C2: actual £-66.08 vs. naked £84.50 -- hedging cost £150.57
  - C2g: actual £-7.28 vs. naked £11.80 -- hedging cost £19.08
  - C8: actual £-59.41 vs. naked £80.48 -- hedging cost £139.89

**Year narrative:** 2025 produced a net loss of £-22,688.54 across 12 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 23 customer(s) experienced a bill shock of >=20%.
