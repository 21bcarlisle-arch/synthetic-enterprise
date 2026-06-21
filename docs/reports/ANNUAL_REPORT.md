# Annual Report — The Synthetic Enterprise

## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £29,846.19
- Final treasury: £11,131.18
  (£-18,715.01 net change)
- Customer bills (all-in): £143,671.95
  VAT remitted to HMRC: (£11,786.84) | Revenue (ex-VAT): £131,885.11
  Non-commodity pass-through: (£42,887.46)
- Gross margin: £-7,089.58
- Capital costs: £1,227.63
- Net margin: £-8,317.21
- Capital cost ratio: -17.3% of gross
- Net margin as % of revenue: -6.3%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 323
- Bills issued: 1117, average clarity 0.872,
  service quality score 0.921
- Enterprise value (CLV sum across 10 billing accounts): £-20,661.90
- Cost to serve (whole portfolio): £6,081.82, net margin after cost to serve: £-14,399.03
- Hedge effectiveness (whole window): hedging cost £1,656.28 vs. a fully unhedged book (commodity-only: actual net £-18,715.01 vs. naked net £-17,058.73)

- **2021** (crisis year): net margin £-3,069.53, 21 risk committee wake-up(s).
- **2022** (crisis year): net margin £-5,582.79, 71 risk committee wake-up(s).

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

The figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run (Phase 9a): gross £-7,089.58, capital £1,227.63, net £-8,317.21. Old-model run (commodity-only, pre-Phase-9a): gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: -7.0% (commodity basis, comparable to old model) / -17.3% (Phase 9a all-in gross) under the new mandate vs. 41.0% (commodity-only) under the old reactive model.
- **2021 net margin**: £-3,069.53 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run -6.3%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run, Phase 9a): £-8,317.21
- Old reactive model (actual, commodity-only): £26,779.56
- Fully naked (this run's counterfactual, commodity-only): £-17,058.73
- Fully naked (old run's counterfactual, commodity-only): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.

_Note: old reactive model figures are commodity-only (pre-Phase-9a). Naked counterfactuals are commodity-only since non-commodity pass-through is not affected by hedging decisions._
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £1,656.28 vs. a fully unhedged book (commodity-only: actual net £-18,715.01 vs. naked net £-17,058.73)
- **Best hedging decision of the run**: C6, term starting
  2021-03-31 (hedge fraction 0.95) -- hedging
  protected £2,367.75 vs. going naked.
- **Worst hedging decision of the run**: C4g, term
  starting 2022-09-30 (hedge fraction 1.00) --
  over-hedging cost £2,864.96 vs. going
  naked.

## Segment Margin Trend

Net margin (£) by segment, by year:

| Year | SME electricity | resi electricity | resi gas | Total |
|---|---|---|---|---|
| 2016 | £-451.81 | £-449.71 | £76.23 | £-825.28 |
| 2017 | £-867.00 | £-1,036.00 | £99.61 | £-1,803.39 |
| 2018 | £-716.77 | £-857.37 | £95.72 | £-1,478.42 |
| 2019 | £-354.55 | £-354.29 | £155.28 | £-553.56 |
| 2020 | £-362.93 | £-411.92 | £92.50 | £-682.36 |
| 2021 | £-1,210.03 | £-1,666.63 | £-192.87 | £-3,069.53 |
| 2022 | £-1,647.41 | £-3,539.35 | £-396.03 | £-5,582.79 |
| 2023 | £-603.91 | £-2,527.64 | £-434.80 | £-3,566.34 |
| 2024 | £32.45 | £-534.90 | £49.52 | £-452.92 |
| 2025 | £0.00 | £-700.42 | £0.00 | £-700.42 |

## Customer Lifecycle Events

Renewal decisions rolled at each annual renewal point across the simulation window.
Retained: **43** renewals.  Lost (churned): **6** accounts.

Accounts lost before end of window: C1, C2, C3, C4, C5, C6

| Account | Date | Outcome | p(churn) | p(win-back) | p(retain) | Roll |
|---------|------|---------|----------|-------------|-----------|------|
| C1 | 2016-12-31 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.1646 |
| C5 | 2016-12-31 | renewed | 0.2900 | 0.3500 | 0.8115 | 0.2812 |
| C7 | 2016-12-31 | renewed | 0.2900 | 0.5500 | 0.8695 | 0.1050 |
| C1 | 2017-12-31 | renewed | 0.1100 | 0.5500 | 0.9505 | 0.6188 |
| C5 | 2017-12-31 | renewed | 0.2900 | 0.3500 | 0.8115 | 0.4449 |
| C7 | 2017-12-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.8255 |
| C1 | 2018-12-31 | renewed | 0.1400 | 0.5500 | 0.9370 | 0.0480 |
| C5 | 2018-12-31 | renewed | 0.4100 | 0.3500 | 0.7335 | 0.3096 |
| C7 | 2018-12-31 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.6312 |
| C1 | 2019-12-31 | renewed | 0.1400 | 0.5500 | 0.9370 | 0.2972 |
| C5 | 2019-12-31 | renewed | 0.3800 | 0.3500 | 0.7530 | 0.4302 |
| C7 | 2019-12-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.7670 |
| C2 | 2020-03-31 | renewed | 0.1100 | 0.5500 | 0.9505 | 0.8936 |
| C6 | 2020-03-31 | renewed | 0.3800 | 0.3500 | 0.7530 | 0.4643 |
| C8 | 2020-03-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1066 |
| C3 | 2020-06-30 | churned **CHURNED** | 0.1400 | 0.5500 | 0.9370 | 0.9704 |
| C9 | 2020-06-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.5378 |
| C4 | 2020-09-30 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.2845 |
| C1 | 2020-12-30 | renewed | 0.2300 | 0.5500 | 0.8965 | 0.8047 |
| C5 | 2020-12-30 | renewed | 0.3800 | 0.3500 | 0.7530 | 0.7480 |
| C7 | 2020-12-30 | renewed | 0.3200 | 0.5500 | 0.8560 | 0.4829 |
| C2 | 2021-03-31 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.6102 |
| C6 | 2021-03-31 | renewed | 0.3800 | 0.3500 | 0.7530 | 0.5431 |
| C8 | 2021-03-31 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.4901 |
| C9 | 2021-06-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.5305 |
| C4 | 2021-09-30 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.4564 |
| C1 | 2021-12-30 | churned **CHURNED** | 0.1400 | 0.5500 | 0.9370 | 0.9691 |
| C5 | 2021-12-30 | churned **CHURNED** | 0.3500 | 0.3500 | 0.7725 | 0.8247 |
| C7 | 2021-12-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1963 |
| C2 | 2022-03-31 | churned **CHURNED** | 0.1700 | 0.5500 | 0.9235 | 0.9547 |
| C6 | 2022-03-31 | renewed | 0.3500 | 0.3500 | 0.7725 | 0.1058 |
| C8 | 2022-03-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.5712 |
| C9 | 2022-06-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.5875 |
| C4 | 2022-09-30 | renewed | 0.2300 | 0.5500 | 0.8965 | 0.8552 |
| C7 | 2022-12-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.0637 |
| C2_2 | 2023-03-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.0093 |
| C6 | 2023-03-31 | renewed | 0.2600 | 0.3500 | 0.8310 | 0.5155 |
| C8 | 2023-03-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.3785 |
| C9 | 2023-06-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.0307 |
| C4 | 2023-09-30 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.6095 |
| C7 | 2023-12-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1905 |
| C2_2 | 2024-03-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.6064 |
| C6 | 2024-03-30 | churned **CHURNED** | 0.3800 | 0.3500 | 0.7530 | 0.9632 |
| C8 | 2024-03-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.0592 |
| C9 | 2024-06-29 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.0025 |
| C4 | 2024-09-29 | churned **CHURNED** | 0.2300 | 0.5500 | 0.8965 | 0.9018 |
| C7 | 2024-12-29 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.4099 |
| C2_2 | 2025-03-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4434 |
| C8 | 2025-03-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4808 |

## Churn Prediction Basis Risk

At each renewal the company estimated churn risk from observable signals (rate change %, customer tenure). The SIM used its bill-shock model (actual bill amount relative to customer-specific thresholds). The gap is epistemic: in crisis years the company sees a rate % while the SIM sees the household-level financial shock — the same failure mode that surprised real suppliers in 2021-22.

- **Average absolute error:** 154.8%
- **Average signed error:** +53.5% (over-estimates vs SIM)
- **Renewal events with estimates:** 49

| Year | Renewals | Avg error (signed) | Avg abs error |
|------|----------|--------------------|---------------|
| 2016 | 3 | +146.4% | 153.4% |
| 2017 | 3 | -54.5% | 54.5% |
| 2018 | 3 | +14.6% | 54.9% |
| 2019 | 3 | -100.0% | 100.0% |
| 2020 | 9 | -76.5% | 76.5% |
| 2021 | 8 | +405.9% | 405.9% |
| 2022 | 6 | +197.6% | 224.0% |
| 2023 | 6 | -100.0% | 100.0% |
| 2024 | 6 | -96.7% | 96.7% |
| 2025 | 2 | +19.2% | 19.2% |

Positive error = company over-estimated churn vs SIM. Negative error = company under-estimated (more dangerous — expected retentions that were actually at risk).

## Company Model Divergence

Not available in current run output (see REPORTING_BACKLOG.md)

## Company CRM — Event Log

Dated artefacts of customer lifecycle events as seen by the company layer.
Total events: **7** (6 churn, 1 acquisition)

| Date | Event | Customer | Detail |
|------|-------|----------|--------|
| 2020-06-30 | CHURN | C3 | SIM p=0.14, company est=0.00 |
| 2021-12-30 | CHURN | C1 | SIM p=0.14, company est=0.95 |
| 2021-12-30 | CHURN | C5 | SIM p=0.35, company est=0.95 |
| 2022-03-31 | CHURN | C2 | SIM p=0.17, company est=0.95 |
| 2022-03-31 | ACQUISITION | C2_2 | home-move-win (predecessor: C2) |
| 2024-03-30 | CHURN | C6 | SIM p=0.38, company est=0.00 |
| 2024-09-29 | CHURN | C4 | SIM p=0.23, company est=0.00 |

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
| 2024-12-31 | 6 accounts | 1 active | yes |
| 2025-12-31 | 6 accounts | 1 active | yes |


## Retention Strategy P&L

### Aggregate (2016-2025)

| Metric | Value |
|--------|-------|
| Offers made | 2 |
| Retained | 2 (100%) |
| Churned despite offer | 0 |
| Total offer cost (foregone margin) | £93.34 |
| Margin saved (retained customers' terms) | £96.20 |
| Wasted offer cost (churned anyway) | £0.00 |
| **Net ROI of retention strategy** | **£2.85** |

Missed opportunities (churns with no offer): **6** (£398.24 expected margin lost without offer)
- **Blocked — uneconomical** (churn estimate above threshold but margin < discount cost): 3 (£146.72 margin foregone)
- **Below threshold** (churn estimate under 30%): 3 (£251.51 margin lost)

### Year-by-Year Breakdown

| Year | Offers | Retained | Offer Cost | Margin Saved | Net ROI | Missed Margin |
|------|--------|----------|-----------|-------------|---------|---------------|
| 2020 | 0 | 0 | £0.00 | £0.00 | £0.00 | £7.57 |
| 2021 | 0 | 0 | £0.00 | £0.00 | £0.00 | £129.63 |
| 2022 | 0 | 0 | £0.00 | £0.00 | £0.00 | £17.10 |
| 2024 | 0 | 0 | £0.00 | £0.00 | £0.00 | £243.94 |
| 2025 | 2 | 2 | £93.34 | £96.20 | £2.85 | £0.00 |

### Per-Offer Detail

| Date | Customer | Est. churn | Offer Cost | Expected Margin | Net | Outcome |
|------|----------|-----------|-----------|----------------|-----|---------|
| 2025-03-30 | C2_2 | 0.45 | £21.31 | £21.96 | £0.65 | retained |
| 2025-03-30 | C8 | 0.45 | £72.03 | £74.23 | £2.20 | retained |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C2 | C2_2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £-371.02 | — | — | — | — | £-1,629.75 | — | £-1,054.30 | — | — |
| 2017 | £-728.09 | £-1,681.70 | — | £-610.68 | £-675.79 | £-3,051.09 | £-4,003.76 | £-2,118.38 | £-2,704.69 | £-1,838.22 |
| 2018 | £-727.42 | £-1,624.05 | — | £-456.81 | £-557.85 | £-2,680.73 | £-3,357.67 | £-1,434.67 | £-1,987.18 | £-1,772.98 |
| 2019 | £-444.07 | £-1,138.87 | — | £-317.84 | £-459.64 | £-1,659.28 | £-3,119.38 | £-1,050.89 | £-1,705.96 | £-1,054.53 |
| 2020 | £-399.79 | £-878.56 | — | £-214.39 | £-414.52 | £-1,758.28 | £-2,510.61 | £-920.50 | £-1,410.63 | £-926.83 |
| 2021 | £-482.81 | £-1,026.89 | — | £-209.82 | £-909.09 | £-1,934.20 | £-2,736.95 | £-1,024.71 | £-1,567.28 | £-1,017.38 |
| 2022 | £-464.64 | £-861.75 | £-535.12 | £-235.86 | £-1,831.59 | £-1,759.96 | £-3,670.54 | £-1,498.60 | £-2,189.77 | £-1,151.65 |
| 2023 | £-409.74 | £-859.68 | £-595.29 | £-197.49 | £-2,319.57 | £-1,766.93 | £-3,275.65 | £-1,994.87 | £-2,046.77 | £-1,093.40 |
| 2024 | £-407.50 | £-909.45 | £-566.89 | £-186.73 | £-1,767.12 | £-1,601.78 | £-2,984.07 | £-1,764.69 | £-1,719.65 | £-918.67 |
| 2025 | £-350.15 | £-820.58 | £-521.29 | £-216.74 | £-1,723.89 | £-1,573.31 | £-2,683.48 | £-1,839.54 | £-1,733.10 | £-940.38 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £434.42, range £25.22–£1,106.23.

- C1: cost to serve £355.60, net margin after CTS £-629.50 — **NET_NEGATIVE** (tariff uplift needed: +49.0%)
- C1g: cost to serve £34.20, net margin after CTS £62.09
- C2: cost to serve £379.50, net margin after CTS £-1,219.75 — **NET_NEGATIVE** (tariff uplift needed: +49.2%)
- C2_2: cost to serve £284.35, net margin after CTS £-1,234.69 — **NET_NEGATIVE** (tariff uplift needed: +22.7%)
- C2g: cost to serve £42.30, net margin after CTS £-2.61 — **NET_NEGATIVE** (tariff uplift needed: +0.1%)
- C3: cost to serve £238.31, net margin after CTS £-356.29 — **NET_NEGATIVE** (tariff uplift needed: +38.8%)
- C3g: cost to serve £25.22, net margin after CTS £158.67
- C4: cost to serve £549.89, net margin after CTS £-2,467.61 — **NET_NEGATIVE** (tariff uplift needed: +44.9%)
- C4g: cost to serve £155.39, net margin after CTS £-862.06 — **NET_NEGATIVE** (tariff uplift needed: +11.8%)
- C5: cost to serve £782.19, net margin after CTS £-2,134.26 — **NET_NEGATIVE** (tariff uplift needed: +34.2%)
- C6: cost to serve £1,106.23, net margin after CTS £-5,489.86 — **NET_NEGATIVE** (tariff uplift needed: +37.5%)
- C7: cost to serve £756.35, net margin after CTS £-3,919.20 — **NET_NEGATIVE** (tariff uplift needed: +33.0%)
- C8: cost to serve £708.75, net margin after CTS £-3,541.34 — **NET_NEGATIVE** (tariff uplift needed: +34.8%)
- C9: cost to serve £663.55, net margin after CTS £-1,932.79 — **NET_NEGATIVE** (tariff uplift needed: +22.5%)

**Activity-Based Pricing Actions**

The following 12 customer(s) are loss-making after cost-to-serve and require immediate tariff review:
  - C1: net margin after CTS £-629.50 on revenue £1,283.40 — raise tariff by ≥49.0% to break even
  - C2: net margin after CTS £-1,219.75 on revenue £2,478.08 — raise tariff by ≥49.2% to break even
  - C2_2: net margin after CTS £-1,234.69 on revenue £5,442.49 — raise tariff by ≥22.7% to break even
  - C2g: net margin after CTS £-2.61 on revenue £1,771.43 — raise tariff by ≥0.1% to break even
  - C3: net margin after CTS £-356.29 on revenue £917.77 — raise tariff by ≥38.8% to break even
  - C4: net margin after CTS £-2,467.61 on revenue £5,500.02 — raise tariff by ≥44.9% to break even
  - C4g: net margin after CTS £-862.06 on revenue £7,311.12 — raise tariff by ≥11.8% to break even
  - C5: net margin after CTS £-2,134.26 on revenue £6,234.04 — raise tariff by ≥34.2% to break even
  - C6: net margin after CTS £-5,489.86 on revenue £14,645.34 — raise tariff by ≥37.5% to break even
  - C7: net margin after CTS £-3,919.20 on revenue £11,860.60 — raise tariff by ≥33.0% to break even
  - C8: net margin after CTS £-3,541.34 on revenue £10,165.87 — raise tariff by ≥34.8% to break even
  - C9: net margin after CTS £-1,932.79 on revenue £8,591.50 — raise tariff by ≥22.5% to break even

## Transaction Log

Total events: 2,238,162

| Event type | Count |
|------------|-------|
| acquisition_spend_event | 5 |
| bad_debt_event | 1,117 |
| billing_event | 1,117 |
| capital_charge_event | 1,019,177 |
| fixed_cost_event | 114 |
| non_commodity_cost_event | 1,117 |
| payment_received_event | 1,117 |
| settlement_event | 1,213,281 |
| vat_remittance_event | 1,117 |

**Cash-flow waterfall (from ledger)**

| Flow | Amount |
|------|--------|
| Customer bills (all-in) | £143,671.95 |
|   Less: VAT remitted to HMRC | (£11,786.84) |
| = Revenue (ex-VAT) | £131,885.11 |
| Less: non-commodity pass-through | (£42,887.46) |
| Wholesale cost (settlement events) | (£96,087.24) |
| Gross margin | £-7,089.58 |
| Capital charges | (£1,227.63) |
| Net margin | £-8,317.21 |

_Cash reconciliation: of £143,671.95 billed, bad debt of £2,820.74 was written off, leaving £140,851.21 cash collected (gross of VAT). After operating costs, net cash position before VAT remittance: £648.89._

| Acquisition spend | (£1,250.00) |
| Fixed overhead | (£5,700.00) |
| Operating net margin | £-15,267.21 |

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
**Operating net margin** (energy margin less acquisition spend & fixed costs): £-15,267.21

## 2016

**Trading & Risk**

- Net margin: £-825.28 (gross £-631.54, capital £193.74)
  - Electricity: gross £-714.10, capital £187.42, net £-901.52
  - Gas: gross £82.56, capital £6.32, net £76.23
- Treasury at year end: £29,365.63
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.90), C1g 0.85 (avg 0.85), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 0.85 (avg 0.85), C4 0.85 (avg 0.85), C4g 0.85 (avg 0.85), C5 0.85 (avg 0.90), C6 0.85 (avg 0.85), C7 0.85 (avg 0.90), C8 0.85 (avg 0.85), C9 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 81
  - 2016-01-01: treasury £29,846.19, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-01-31: treasury £29,842.15, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-03-01: treasury £29,838.21, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-03-31: treasury £29,834.26, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-04-30: treasury £29,831.13, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-05-30: treasury £29,828.32, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-06-29: treasury £29,825.32, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-07-29: treasury £29,822.49, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-08-28: treasury £29,819.76, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-09-27: treasury £29,816.45, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-10-27: treasury £29,812.86, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-11-26: treasury £29,807.09, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-12-26: treasury £29,802.68, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-01-18: treasury £29,815.91, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-02-17: treasury £29,790.65, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-03-18: treasury £29,763.87, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-04-17: treasury £29,743.59, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-05-17: treasury £29,725.24, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-06-16: treasury £29,711.27, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-07-16: treasury £29,698.42, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-08-15: treasury £29,686.36, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-09-14: treasury £29,672.73, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-10-14: treasury £29,656.22, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-11-13: treasury £29,628.90, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-12-13: treasury £29,598.07, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-01-13: treasury £29,575.12, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-02-12: treasury £29,557.22, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-03-13: treasury £29,537.43, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-04-12: treasury £29,523.20, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-05-12: treasury £29,510.15, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-06-11: treasury £29,501.87, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-07-11: treasury £29,494.82, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-08-10: treasury £29,488.32, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-09-09: treasury £29,481.47, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-10-09: treasury £29,472.94, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-11-08: treasury £29,457.57, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-12-08: treasury £29,434.49, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-04-08: treasury £29,419.78, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-05-08: treasury £29,414.13, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-06-07: treasury £29,409.07, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-07-07: treasury £29,403.65, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-08-06: treasury £29,398.54, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-09-05: treasury £29,393.54, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-10-05: treasury £29,387.76, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-11-04: treasury £29,381.12, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-12-04: treasury £29,372.25, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-08-05: treasury £29,349.29, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-04-26: treasury £29,337.19, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-05-26: treasury £29,317.75, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-06-25: treasury £29,301.73, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-07-25: treasury £29,286.35, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-08-24: treasury £29,272.55, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-09-23: treasury £29,256.41, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-10-23: treasury £29,235.56, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-11-22: treasury £29,199.51, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-12-22: treasury £29,168.40, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-04-21: treasury £29,057.24, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-05-21: treasury £29,045.81, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-06-20: treasury £29,039.32, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-07-20: treasury £29,033.63, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-08-19: treasury £29,029.11, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-09-18: treasury £29,024.05, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-10-18: treasury £29,014.31, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-11-17: treasury £28,995.89, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-12-17: treasury £28,973.20, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-07-16: treasury £28,905.76, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-08-15: treasury £28,904.11, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-09-14: treasury £28,902.06, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-10-14: treasury £28,899.76, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-11-13: treasury £28,896.22, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-12-13: treasury £28,892.23, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-07-03: treasury £28,913.55, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-08-02: treasury £28,910.09, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-09-01: treasury £28,907.02, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-10-01: treasury £28,902.81, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-10-31: treasury £28,895.07, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-11-30: treasury £28,876.97, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-12-30: treasury £28,866.87, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-10-28: treasury £28,809.57, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2016-11-27: treasury £28,801.77, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2016-12-27: treasury £28,795.81, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 3.03
- Worst single period: C8 on 2016-11-08 period 40, net margin £-0.49

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2016): £-1,018.36
  - By billing account: C1 £-371.02, C5 £-1,629.75, C7 £-1,054.30
- Bill shock events (>=20%): 18 -- C5 2016-05-31 (26%); C5 2016-10-31 (40%); C5 2016-11-30 (42%); C7 2016-05-31 (35%); C7 2016-06-30 (28%); C7 2016-10-31 (71%); C7 2016-11-30 (48%); C6 2016-05-31 (25%); C6 2016-06-30 (22%); C6 2016-10-31 (39%); C6 2016-11-30 (44%); C8 2016-05-31 (40%); C8 2016-06-30 (41%); C8 2016-09-30 (22%); C8 2016-10-31 (100%); C8 2016-11-30 (65%); C9 2016-10-31 (75%); C9 2016-11-30 (55%)
- Churn risk (accounts renewing in 2016): 2 at risk (≥20% churn prob): C5 29%, C7 29%

**Pricing & Margin**

- C1 (electricity): tariff £47.25-£58.16/MWh, net margin £-44.93 -- **net-negative**
- C1g (gas): tariff £15.71-£16.64/MWh, net margin £29.02
- C2 (electricity): tariff £44.01/MWh, net margin £-55.48 -- **net-negative**
- C2g (gas): tariff £16.44/MWh, net margin £11.89
- C3 (electricity): tariff £42.25/MWh, net margin £-16.21 -- **net-negative**
- C3g (gas): tariff £14.52/MWh, net margin £21.30
- C4 (electricity): tariff £43.69/MWh, net margin £-19.26 -- **net-negative**
- C4g (gas): tariff £14.85/MWh, net margin £14.03
- C5 (electricity): tariff £47.25-£58.16/MWh, net margin £-252.47 -- **net-negative**
- C6 (electricity): tariff £44.01/MWh, net margin £-199.34 -- **net-negative**
- C7 (electricity): tariff £47.25-£58.16/MWh, net margin £-163.57 -- **net-negative**
- C8 (electricity): tariff £44.01/MWh, net margin £-102.86 -- **net-negative**
- C9 (electricity): tariff £42.25/MWh, net margin £-47.39 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -30.7% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 108, average clarity 0.895, average bill shock 12.9%, bad debt provision £198.00, avg complaint probability 3.5%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-2,141.72 vs. naked (unhedged) net margin: £-2,120.87
- hedging cost £20.85 vs. a fully unhedged book (commodity-only: actual net £-2,141.72 vs. naked net £-2,120.87)
  - C1: actual £-162.40 vs. naked £-50.48 -- hedging cost £111.92
  - C1g: actual £41.27 vs. naked £35.86 -- hedging added £5.41
  - C2: actual £-77.64 vs. naked £-19.85 -- hedging cost £57.79
  - C2g: actual £13.53 vs. naked £42.07 -- hedging cost £28.54
  - C3: actual £-32.13 vs. naked £-47.40 -- hedging added £15.27
  - C3g: actual £39.40 vs. naked £8.15 -- hedging added £31.25
  - C4: actual £-66.81 vs. naked £-52.45 -- hedging cost £14.36
  - C4g: actual £49.84 vs. naked £-1.83 -- hedging added £51.67
  - C5: actual £-831.01 vs. naked £-703.96 -- hedging cost £127.05
  - C6: actual £-290.59 vs. naked £-603.98 -- hedging added £313.38
  - C7: actual £-565.53 vs. naked £-288.36 -- hedging cost £277.16
  - C8: actual £-159.79 vs. naked £-224.60 -- hedging added £64.81
  - C9: actual £-99.85 vs. naked £-214.02 -- hedging added £114.17

**Year narrative:** 2016 produced a net loss of £-825.28 across 13 accounts. The risk committee intervened 81 time(s), raising hedge fractions in response to elevated VaR. 18 customer(s) experienced a bill shock of >=20%.

## 2017

**Trading & Risk**

- Net margin: £-1,803.39 (gross £-1,673.31, capital £130.07)
  - Electricity: gross £-1,782.89, capital £120.11, net £-1,903.00
  - Gas: gross £109.57, capital £9.96, net £99.61
- Treasury at year end: £27,642.93
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 0.95 (avg 0.95), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.95 (avg 0.95), C3g 0.95 (avg 0.95), C4 0.85 (avg 0.85), C4g 0.95 (avg 0.95), C5 0.85 (avg 0.85), C6 0.95 (avg 0.95), C7 0.85 (avg 0.85), C8 0.95 (avg 0.95), C9 0.95 (avg 0.95)
- Risk committee (Context Handshake) interventions: 42
  - 2017-01-03: treasury £29,365.00, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2017-02-02: treasury £29,356.90, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2017-03-04: treasury £29,349.47, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2017-01-21: treasury £29,135.48, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2017-02-20: treasury £29,101.20, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2017-03-22: treasury £29,074.58, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2017-01-16: treasury £28,952.44, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2017-02-15: treasury £28,929.38, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2017-03-17: treasury £28,913.61, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2017-01-12: treasury £28,889.17, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-02-11: treasury £28,885.38, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-03-13: treasury £28,882.45, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-04-12: treasury £28,880.33, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-05-12: treasury £28,878.01, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-06-11: treasury £28,875.71, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-01-29: treasury £28,853.28, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-02-28: treasury £28,841.58, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-03-30: treasury £28,831.90, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-04-29: treasury £28,824.55, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-05-29: treasury £28,818.11, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-06-28: treasury £28,814.36, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-01-26: treasury £28,789.09, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-02-25: treasury £28,782.69, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-03-27: treasury £28,777.00, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-04-26: treasury £28,772.48, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-05-26: treasury £28,766.99, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-06-25: treasury £28,762.59, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-07-25: treasury £28,758.28, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-08-24: treasury £28,753.79, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-09-23: treasury £28,748.58, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-01-15: treasury £28,791.10, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-02-14: treasury £28,779.50, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-03-16: treasury £28,768.18, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-04-15: treasury £28,758.57, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-05-15: treasury £28,749.70, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-06-14: treasury £28,741.67, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-07-14: treasury £28,733.66, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-08-13: treasury £28,725.76, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-09-12: treasury £28,717.51, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-10-12: treasury £28,708.35, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-11-11: treasury £28,698.27, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-12-11: treasury £28,686.74, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.72
- Worst single period: C5 on 2017-01-23 period 19, net margin £-0.19

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2017): £-1,934.71
  - By billing account: C1 £-728.09, C2 £-1,681.70, C3 £-610.68, C4 £-675.79, C5 £-3,051.09, C6 £-4,003.76, C7 £-2,118.38, C8 £-2,704.69, C9 £-1,838.22
- Bill shock events (>=20%): 21 -- C5 2017-01-31 (28%); C5 2017-02-28 (22%); C5 2017-06-30 (21%); C5 2017-11-30 (54%); C7 2017-01-31 (33%); C7 2017-02-28 (27%); C7 2017-05-31 (29%); C7 2017-06-30 (29%); C7 2017-09-30 (24%); C7 2017-11-30 (69%); C6 2017-05-31 (21%); C6 2017-11-30 (48%); C8 2017-05-31 (39%); C8 2017-06-30 (35%); C8 2017-09-30 (43%); C8 2017-11-30 (81%); C8 2017-12-31 (22%); C9 2017-05-31 (32%); C9 2017-06-30 (25%); C9 2017-09-30 (28%); C9 2017-11-30 (67%)
- Churn risk (accounts renewing in 2017): 5 at risk (≥20% churn prob): C5 29%, C6 35%, C7 35%, C8 35%, C9 29%

**Pricing & Margin**

- C1 (electricity): tariff £58.16-£58.79/MWh, net margin £-117.77 -- **net-negative**
- C1g (gas): tariff £15.71-£22.07/MWh, net margin £12.23
- C2 (electricity): tariff £44.01-£55.61/MWh, net margin £-83.70 -- **net-negative**
- C2g (gas): tariff £16.44-£19.42/MWh, net margin £0.74
- C3 (electricity): tariff £42.25-£48.46/MWh, net margin £-54.52 -- **net-negative**
- C3g (gas): tariff £14.52-£17.55/MWh, net margin £40.53
- C4 (electricity): tariff £43.69-£48.09/MWh, net margin £-60.36 -- **net-negative**
- C4g (gas): tariff £14.85-£18.82/MWh, net margin £46.11
- C5 (electricity): tariff £58.16-£58.79/MWh, net margin £-580.90 -- **net-negative**
- C6 (electricity): tariff £44.01-£55.61/MWh, net margin £-286.10 -- **net-negative**
- C7 (electricity): tariff £58.16-£58.79/MWh, net margin £-403.20 -- **net-negative**
- C8 (electricity): tariff £44.01-£55.61/MWh, net margin £-163.75 -- **net-negative**
- C9 (electricity): tariff £42.25-£48.46/MWh, net margin £-152.70 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -7.8% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.899, average bill shock 10.8%, bad debt provision £297.53, avg complaint probability 3.4%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-1,085.61 vs. naked (unhedged) net margin: £-1,570.78
- hedging added £485.17 vs. a fully unhedged book (commodity-only: actual net £-1,085.61 vs. naked net £-1,570.78)
  - C1: actual £-24.35 vs. naked £-30.10 -- hedging added £5.75
  - C1g: actual £19.29 vs. naked £-10.00 -- hedging added £29.29
  - C2: actual £-88.30 vs. naked £15.10 -- hedging cost £103.40
  - C2g: actual £-4.09 vs. naked £18.28 -- hedging cost £22.37
  - C3: actual £-78.70 vs. naked £-55.48 -- hedging cost £23.21
  - C3g: actual £43.19 vs. naked £-23.97 -- hedging added £67.15
  - C4: actual £-52.93 vs. naked £-90.36 -- hedging added £37.43
  - C4g: actual £38.22 vs. naked £-56.70 -- hedging added £94.92
  - C5: actual £-134.87 vs. naked £-258.29 -- hedging added £123.43
  - C6: actual £-301.72 vs. naked £-543.73 -- hedging added £242.01
  - C7: actual £-86.40 vs. naked £-123.46 -- hedging added £37.06
  - C8: actual £-182.71 vs. naked £-156.59 -- hedging cost £26.12
  - C9: actual £-232.25 vs. naked £-255.49 -- hedging added £23.24

**Year narrative:** 2017 produced a net loss of £-1,803.39 across 13 accounts. The risk committee intervened 42 time(s), raising hedge fractions in response to elevated VaR. 21 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £-1,478.42 (gross £-1,377.05, capital £101.37)
  - Electricity: gross £-1,479.93, capital £94.21, net £-1,574.14
  - Gas: gross £102.88, capital £7.16, net £95.72
- Treasury at year end: £26,449.34
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.95 (avg 0.95), C1g 1.00 (avg 1.00), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 1.00 (avg 1.00), C4 0.95 (avg 0.95), C4g 1.00 (avg 1.00), C5 0.95 (avg 0.95), C6 1.00 (avg 1.00), C7 0.95 (avg 0.95), C8 0.85 (avg 0.85), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C5 on 2018-03-01 period 34, net margin £-0.32

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2018): £-1,622.15
  - By billing account: C1 £-727.42, C2 £-1,624.05, C3 £-456.81, C4 £-557.85, C5 £-2,680.73, C6 £-3,357.67, C7 £-1,434.67, C8 £-1,987.18, C9 £-1,772.98
- Bill shock events (>=20%): 32 -- C5 2018-04-30 (32%); C5 2018-06-30 (20%); C5 2018-10-31 (31%); C5 2018-11-30 (26%); C7 2018-04-30 (37%); C7 2018-05-31 (27%); C7 2018-06-30 (27%); C7 2018-09-30 (26%); C7 2018-10-31 (41%); C7 2018-11-30 (29%); C6 2018-04-30 (20%); C6 2018-05-31 (21%); C6 2018-06-30 (22%); C6 2018-10-31 (29%); C6 2018-11-30 (21%); C8 2018-04-30 (30%); C8 2018-05-31 (38%); C8 2018-06-30 (40%); C8 2018-08-31 (22%); C8 2018-09-30 (51%); C8 2018-10-31 (51%); C8 2018-11-30 (27%); C3g 2018-07-31 (28%); C9 2018-04-30 (31%); C9 2018-05-31 (34%); C9 2018-06-30 (31%); C9 2018-08-31 (36%); C9 2018-09-30 (43%); C9 2018-10-31 (37%); C9 2018-12-31 (21%); C4 2018-10-31 (24%); C4g 2018-10-31 (30%)
- Churn risk (accounts renewing in 2018): 5 at risk (≥20% churn prob): C5 41%, C6 32%, C7 41%, C8 35%, C9 38%

**Pricing & Margin**

- C1 (electricity): tariff £58.79-£74.67/MWh, net margin £-24.11 -- **net-negative**
- C1g (gas): tariff £22.07-£28.52/MWh, net margin £19.46
- C2 (electricity): tariff £55.61-£68.65/MWh, net margin £-196.28 -- **net-negative**
- C2g (gas): tariff £19.42-£25.45/MWh, net margin £-10.37 -- **net-negative**
- C3 (electricity): tariff £48.46-£62.97/MWh, net margin £-44.87 -- **net-negative**
- C3g (gas): tariff £17.55-£25.69/MWh, net margin £52.24
- C4 (electricity): tariff £48.09-£68.79/MWh, net margin £-48.61 -- **net-negative**
- C4g (gas): tariff £18.82-£27.43/MWh, net margin £34.39
- C5 (electricity): tariff £58.79-£74.67/MWh, net margin £-133.11 -- **net-negative**
- C6 (electricity): tariff £55.61-£68.65/MWh, net margin £-583.66 -- **net-negative**
- C7 (electricity): tariff £58.79-£74.67/MWh, net margin £-85.45 -- **net-negative**
- C8 (electricity): tariff £55.61-£68.65/MWh, net margin £-316.86 -- **net-negative**
- C9 (electricity): tariff £48.46-£62.97/MWh, net margin £-141.18 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -7.4% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.899, average bill shock 10.6%, bad debt provision £325.31, avg complaint probability 3.3%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-1,237.40 vs. naked (unhedged) net margin: £859.11
- hedging cost £2,096.51 vs. a fully unhedged book (commodity-only: actual net £-1,237.40 vs. naked net £859.11)
  - C1: actual £3.14 vs. naked £89.86 -- hedging cost £86.72
  - C1g: actual £54.18 vs. naked £174.02 -- hedging cost £119.84
  - C2: actual £-230.95 vs. naked £51.10 -- hedging cost £282.05
  - C2g: actual £-6.80 vs. naked £47.74 -- hedging cost £54.54
  - C3: actual £-4.62 vs. naked £13.26 -- hedging cost £17.87
  - C3g: actual £62.48 vs. naked £82.70 -- hedging cost £20.22
  - C4: actual £-26.80 vs. naked £115.99 -- hedging cost £142.79
  - C4g: actual £25.66 vs. naked £234.24 -- hedging cost £208.58
  - C5: actual £9.63 vs. naked £324.27 -- hedging cost £314.64
  - C6: actual £-723.45 vs. naked £-451.69 -- hedging cost £271.76
  - C7: actual £9.17 vs. naked £276.34 -- hedging cost £267.17
  - C8: actual £-387.97 vs. naked £-74.22 -- hedging cost £313.74
  - C9: actual £-21.06 vs. naked £-24.48 -- hedging added £3.42

**Year narrative:** 2018 produced a net loss of £-1,478.42 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 32 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £-553.56 (gross £-488.14, capital £65.42)
  - Electricity: gross £-649.05, capital £59.79, net £-708.84
  - Gas: gross £160.91, capital £5.63, net £155.28
- Treasury at year end: £25,352.46
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 0.90 (avg 0.90), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 0.90 (avg 0.90), C4 0.85 (avg 0.85), C4g 0.90 (avg 0.90), C5 0.85 (avg 0.85), C6 0.90 (avg 0.90), C7 0.85 (avg 0.85), C8 0.85 (avg 0.85), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C6 on 2019-01-23 period 20, net margin £-0.19

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2019): £-1,216.72
  - By billing account: C1 £-444.07, C2 £-1,138.87, C3 £-317.84, C4 £-459.64, C5 £-1,659.28, C6 £-3,119.38, C7 £-1,050.89, C8 £-1,705.96, C9 £-1,054.53
- Bill shock events (>=20%): 34 -- C1 2019-04-30 (21%); C5 2019-01-31 (35%); C5 2019-02-28 (21%); C5 2019-06-30 (25%); C5 2019-10-31 (42%); C5 2019-11-30 (35%); C7 2019-01-31 (40%); C7 2019-02-28 (24%); C7 2019-05-31 (22%); C7 2019-06-30 (32%); C7 2019-10-31 (61%); C7 2019-11-30 (43%); C6 2019-02-28 (21%); C6 2019-04-30 (23%); C6 2019-06-30 (24%); C6 2019-10-31 (40%); C6 2019-11-30 (26%); C8 2019-01-31 (23%); C8 2019-02-28 (26%); C8 2019-04-30 (28%); C8 2019-06-30 (37%); C8 2019-07-31 (33%); C8 2019-09-30 (54%); C8 2019-10-31 (78%); C8 2019-11-30 (37%); C3g 2019-07-31 (21%); C9 2019-02-28 (25%); C9 2019-04-30 (24%); C9 2019-06-30 (35%); C9 2019-07-31 (36%); C9 2019-09-30 (46%); C9 2019-10-31 (67%); C9 2019-11-30 (37%); C4g 2019-10-31 (34%)
- Churn risk (accounts renewing in 2019): 6 at risk (≥20% churn prob): C3 23%, C5 38%, C6 29%, C7 38%, C8 32%, C9 32%

**Pricing & Margin**

- C1 (electricity): tariff £46.27-£74.67/MWh, net margin £2.97
- C1g (gas): tariff £13.99-£28.52/MWh, net margin £53.94
- C2 (electricity): tariff £63.91-£68.65/MWh, net margin £-90.44 -- **net-negative**
- C2g (gas): tariff £22.37-£25.45/MWh, net margin £22.43
- C3 (electricity): tariff £50.45-£62.97/MWh, net margin £-8.31 -- **net-negative**
- C3g (gas): tariff £15.94-£25.69/MWh, net margin £47.16
- C4 (electricity): tariff £45.81-£68.79/MWh, net margin £-21.98 -- **net-negative**
- C4g (gas): tariff £12.42-£27.43/MWh, net margin £31.75
- C5 (electricity): tariff £46.27-£74.67/MWh, net margin £8.34
- C6 (electricity): tariff £63.91-£68.65/MWh, net margin £-362.89 -- **net-negative**
- C7 (electricity): tariff £46.27-£74.67/MWh, net margin £8.43
- C8 (electricity): tariff £63.91-£68.65/MWh, net margin £-201.17 -- **net-negative**
- C9 (electricity): tariff £50.45-£62.97/MWh, net margin £-43.79 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -13.4% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.894, average bill shock 12.3%, bad debt provision £342.86, avg complaint probability 3.6%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-463.13 vs. naked (unhedged) net margin: £1,125.07
- hedging cost £1,588.19 vs. a fully unhedged book (commodity-only: actual net £-463.13 vs. naked net £1,125.07)
  - C1: actual £-22.97 vs. naked £10.82 -- hedging cost £33.79
  - C1g: actual £10.19 vs. naked £52.10 -- hedging cost £41.92
  - C2: actual £-38.19 vs. naked £174.88 -- hedging cost £213.07
  - C2g: actual £30.34 vs. naked £160.05 -- hedging cost £129.71
  - C3: actual £-14.00 vs. naked £52.14 -- hedging cost £66.14
  - C3g: actual £34.45 vs. naked £92.03 -- hedging cost £57.58
  - C4: actual £-7.27 vs. naked £70.62 -- hedging cost £77.89
  - C4g: actual £56.83 vs. naked £84.08 -- hedging cost £27.25
  - C5: actual £-119.77 vs. naked £-29.66 -- hedging cost £90.11
  - C6: actual £-165.86 vs. naked £155.17 -- hedging cost £321.03
  - C7: actual £-76.65 vs. naked £23.07 -- hedging cost £99.72
  - C8: actual £-80.20 vs. naked £181.59 -- hedging cost £261.79
  - C9: actual £-70.02 vs. naked £98.17 -- hedging cost £168.20

**Year narrative:** 2019 produced a net loss of £-553.56 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 34 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £-682.36 (gross £-564.36, capital £118.00)
  - Electricity: gross £-664.21, capital £110.64, net £-774.85
  - Gas: gross £99.85, capital £7.35, net £92.50
- Treasury at year end: £24,859.71
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 0.85 (avg 0.85), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C4 0.85 (avg 0.85), C4g 0.85 (avg 0.85), C5 0.85 (avg 0.85), C6 0.85 (avg 0.85), C7 0.85 (avg 0.85), C8 0.85 (avg 0.85), C9 0.90 (avg 0.90)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C5 on 2020-03-04 period 37, net margin £-1.01

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: C3
  - Renewals (retained): 8 accounts
- Average CLV (Point-in-Time, year-end 2020): £-1,048.23
  - By billing account: C1 £-399.79, C2 £-878.56, C3 £-214.39, C4 £-414.52, C5 £-1,758.28, C6 £-2,510.61, C7 £-920.50, C8 £-1,410.63, C9 £-926.83
- Bill shock events (>=20%): 28 -- C1g 2020-01-31 (31%); C5 2020-01-31 (23%); C5 2020-04-30 (28%); C5 2020-10-31 (36%); C5 2020-12-31 (25%); C7 2020-01-31 (22%); C7 2020-04-30 (34%); C7 2020-06-30 (25%); C7 2020-10-31 (53%); C7 2020-11-30 (20%); C7 2020-12-31 (32%); C2 2020-04-30 (28%); C2g 2020-04-30 (27%); C6 2020-04-30 (40%); C6 2020-10-31 (32%); C6 2020-12-31 (25%); C8 2020-04-30 (47%); C8 2020-05-31 (22%); C8 2020-06-30 (32%); C8 2020-09-30 (46%); C8 2020-10-31 (61%); C8 2020-12-31 (39%); C9 2020-04-30 (28%); C9 2020-05-31 (23%); C9 2020-06-30 (35%); C9 2020-09-30 (38%); C9 2020-10-31 (46%); C9 2020-12-31 (32%)
- Churn risk (accounts renewing in 2020): 7 at risk (≥20% churn prob): C1 23%, C4 20%, C5 38%, C6 38%, C7 32%, C8 38%, C9 41%

**Pricing & Margin**

- C1 (electricity): tariff £46.27-£55.50/MWh, net margin £-23.58 -- **net-negative**
- C1g (gas): tariff £13.99-£16.93/MWh, net margin £10.15
- C2 (electricity): tariff £41.35-£63.91/MWh, net margin £-67.82 -- **net-negative**
- C2g (gas): tariff £12.61-£22.37/MWh, net margin £29.04
- C3 (electricity): tariff £50.45/MWh, net margin £-5.53 -- **net-negative**
- C3g (gas): tariff £15.94/MWh, net margin £18.27
- C4 (electricity): tariff £40.59-£45.81/MWh, net margin £-27.05 -- **net-negative**
- C4g (gas): tariff £9.54-£12.42/MWh, net margin £35.04
- C5 (electricity): tariff £46.27-£55.50/MWh, net margin £-124.80 -- **net-negative**
- C6 (electricity): tariff £41.35-£63.91/MWh, net margin £-238.13 -- **net-negative**
- C7 (electricity): tariff £46.27-£55.50/MWh, net margin £-80.03 -- **net-negative**
- C8 (electricity): tariff £41.35-£63.91/MWh, net margin £-124.75 -- **net-negative**
- C9 (electricity): tariff £32.11-£50.45/MWh, net margin £-83.17 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -20.9% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 144, average clarity 0.892, average bill shock 11.1%, bad debt provision £254.91, avg complaint probability 3.5%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-1,775.52 vs. naked (unhedged) net margin: £-5,373.16
- hedging added £3,597.64 vs. a fully unhedged book (commodity-only: actual net £-1,775.52 vs. naked net £-5,373.16)
  - C1: actual £-88.70 vs. naked £-293.99 -- hedging added £205.29
  - C1g: actual £-38.18 vs. naked £-319.47 -- hedging added £281.29
  - C2: actual £-87.86 vs. naked £-38.30 -- hedging cost £49.56
  - C2g: actual £22.51 vs. naked £13.81 -- hedging added £8.69
  - C4: actual £-115.62 vs. naked £-287.48 -- hedging added £171.86
  - C4g: actual £-71.97 vs. naked £-354.41 -- hedging added £282.44
  - C5: actual £-466.95 vs. naked £-1,632.93 -- hedging added £1,165.98
  - C6: actual £-308.54 vs. naked £-595.77 -- hedging added £287.23
  - C7: actual £-310.09 vs. naked £-1,013.11 -- hedging added £703.03
  - C8: actual £-183.17 vs. naked £-303.25 -- hedging added £120.08
  - C9: actual £-126.95 vs. naked £-548.26 -- hedging added £421.31

**Year narrative:** 2020 produced a net loss of £-682.36 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 28 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £-3,069.53 (gross £-2,873.58, capital £195.95)
  - Electricity: gross £-2,688.79, capital £187.87, net £-2,876.66
  - Gas: gross £-184.79, capital £8.08, net £-192.87
- Treasury at year end: £22,891.57
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.85 (avg 0.85), C2g 0.95 (avg 0.95), C4 0.95 (avg 0.95), C4g 0.95 (avg 0.95), C6 0.95 (avg 0.95), C7 0.95 (avg 0.95), C8 0.95 (avg 0.95), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 21
  - 2021-10-15: treasury £22,367.64, C2->0.95, C6->1.00, VaR (current £1,813.45 / stressed £792.72) ratio 2.29
  - 2021-11-14: treasury £22,289.43, C2->0.95, C6->1.00, VaR (current £1,813.45 / stressed £792.72) ratio 2.29
  - 2021-12-14: treasury £22,181.58, C2->0.95, C6->1.00, VaR (current £1,813.45 / stressed £792.72) ratio 2.29
  - 2021-04-13: treasury £21,770.69, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2021-05-13: treasury £21,720.70, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2021-06-12: treasury £21,693.26, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2021-07-12: treasury £21,676.88, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2021-08-11: treasury £21,662.19, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2021-09-10: treasury £21,645.34, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2021-10-10: treasury £21,620.13, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2021-11-09: treasury £21,575.97, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2021-12-09: treasury £21,505.23, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2021-07-08: treasury £21,234.06, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2021-08-07: treasury £21,223.92, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2021-09-06: treasury £21,211.27, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2021-10-06: treasury £21,193.16, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2021-11-05: treasury £21,166.54, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2021-12-05: treasury £21,127.27, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2021-10-03: treasury £20,878.65, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2021-11-02: treasury £20,812.11, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2021-12-02: treasury £20,735.61, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.42
- Worst single period: C5 on 2021-01-08 period 39, net margin £-2.18

**Customer Book**

- Active accounts: 11 (C1, C1g, C2, C2g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 6, SME electricity: 2, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: C1, C5
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2021): £-1,212.12
  - By billing account: C1 £-482.81, C2 £-1,026.89, C3 £-209.82, C4 £-909.09, C5 £-1,934.20, C6 £-2,736.95, C7 £-1,024.71, C8 £-1,567.28, C9 £-1,017.38
- Bill shock events (>=20%): 28 -- C5 2021-05-31 (22%); C5 2021-06-30 (31%); C5 2021-10-31 (28%); C5 2021-11-30 (48%); C7 2021-01-31 (22%); C7 2021-05-31 (27%); C7 2021-06-30 (44%); C7 2021-10-31 (50%); C7 2021-11-30 (55%); C2g 2021-04-30 (26%); C6 2021-04-30 (22%); C6 2021-06-30 (34%); C6 2021-10-31 (26%); C6 2021-11-30 (48%); C8 2021-02-28 (20%); C8 2021-04-30 (24%); C8 2021-05-31 (27%); C8 2021-06-30 (59%); C8 2021-10-31 (68%); C8 2021-11-30 (74%); C9 2021-02-28 (22%); C9 2021-05-31 (22%); C9 2021-06-30 (48%); C9 2021-10-31 (61%); C9 2021-11-30 (44%); C9 2021-12-31 (22%); C4 2021-10-31 (90%); C4g 2021-10-31 (160%)
- Churn risk (accounts renewing in 2021): 6 at risk (≥20% churn prob): C2 20%, C5 35%, C6 38%, C7 38%, C8 41%, C9 35%

**Pricing & Margin**

- C1 (electricity): tariff £55.50/MWh, net margin £-87.86 -- **net-negative**
- C1g (gas): tariff £16.93/MWh, net margin £-38.05 -- **net-negative**
- C2 (electricity): tariff £41.35-£73.44/MWh, net margin £-280.48 -- **net-negative**
- C2g (gas): tariff £12.61-£21.81/MWh, net margin £-19.89 -- **net-negative**
- C4 (electricity): tariff £40.59-£134.66/MWh, net margin £-320.62 -- **net-negative**
- C4g (gas): tariff £9.54-£48.71/MWh, net margin £-134.93 -- **net-negative**
- C5 (electricity): tariff £55.50/MWh, net margin £-460.04 -- **net-negative**
- C6 (electricity): tariff £41.35-£73.44/MWh, net margin £-749.99 -- **net-negative**
- C7 (electricity): tariff £55.50-£220.50/MWh, net margin £-311.76 -- **net-negative**
- C8 (electricity): tariff £41.35-£73.44/MWh, net margin £-434.65 -- **net-negative**
- C9 (electricity): tariff £32.11-£83.14/MWh, net margin £-231.26 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -6.8% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £24,859.69 -> £19,730.94 (20.6%)
- Bills issued: 132, average clarity 0.880, average bill shock 14.2%, bad debt provision £258.24, avg complaint probability 3.9%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-4,162.77 vs. naked (unhedged) net margin: £-10,738.23
- hedging added £6,575.46 vs. a fully unhedged book (commodity-only: actual net £-4,162.77 vs. naked net £-10,738.23)
  - C2: actual £-360.93 vs. naked £-628.72 -- hedging added £267.80
  - C2g: actual £-35.08 vs. naked £-591.89 -- hedging added £556.81
  - C4: actual £-848.86 vs. naked £-846.23 -- hedging cost £2.63
  - C4g: actual £-302.21 vs. naked £-1,301.36 -- hedging added £999.15
  - C6: actual £-945.06 vs. naked £-3,312.81 -- hedging added £2,367.75
  - C7: actual £-756.97 vs. naked £-781.95 -- hedging added £24.98
  - C8: actual £-564.66 vs. naked £-1,644.87 -- hedging added £1,080.21
  - C9: actual £-349.00 vs. naked £-1,630.39 -- hedging added £1,281.39

**Year narrative:** 2021 (flagged crisis year) produced a net loss of £-3,069.53 across 11 accounts. The risk committee intervened 21 time(s), raising hedge fractions in response to elevated VaR. 28 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £-5,582.79 (gross £-5,472.74, capital £110.05)
  - Electricity: gross £-5,081.36, capital £105.40, net £-5,186.76
  - Gas: gross £-391.38, capital £4.65, net £-396.03
- Treasury at year end: £18,387.15
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C4 1.00 (avg 1.00), C4g 1.00 (avg 1.00), C6 1.00 (avg 1.00), C7 1.00 (avg 1.00), C8 1.00 (avg 1.00), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 71
  - 2022-01-13: treasury £22,073.97, C2->0.95, C6->1.00, VaR (current £1,813.45 / stressed £792.72) ratio 2.29
  - 2022-02-12: treasury £21,959.87, C2->0.95, C6->1.00, VaR (current £1,813.45 / stressed £792.72) ratio 2.29
  - 2022-03-14: treasury £21,854.26, C2->0.95, C6->1.00, VaR (current £1,813.45 / stressed £792.72) ratio 2.29
  - 2022-01-08: treasury £21,434.03, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2022-02-07: treasury £21,352.86, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2022-03-09: treasury £21,278.82, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,854.75 / stressed £769.78) ratio 2.41
  - 2022-01-04: treasury £21,083.39, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2022-02-03: treasury £21,040.11, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2022-03-05: treasury £20,994.94, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2022-04-04: treasury £20,954.98, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2022-05-04: treasury £20,923.76, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2022-06-03: treasury £20,901.90, C2->0.95, C6->1.00, C8->1.00, VaR (current £1,784.03 / stressed £730.87) ratio 2.44
  - 2022-01-01: treasury £20,658.29, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-01-31: treasury £20,581.48, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-03-02: treasury £20,505.78, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-04-01: treasury £20,429.72, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-05-01: treasury £20,363.95, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-05-31: treasury £20,301.72, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-06-30: treasury £20,240.10, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-07-30: treasury £20,176.36, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-08-29: treasury £20,109.84, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-09-28: treasury £20,042.28, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-01-19: treasury £19,666.90, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-02-18: treasury £19,574.89, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-03-20: treasury £19,486.61, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-04-20: treasury £19,413.96, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-05-20: treasury £19,366.45, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-06-19: treasury £19,329.96, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-07-19: treasury £19,297.76, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-08-18: treasury £19,263.92, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-09-17: treasury £19,227.79, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-10-17: treasury £19,178.44, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-11-16: treasury £19,132.03, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-12-16: treasury £19,021.51, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-04-16: treasury £18,922.46, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-05-16: treasury £18,865.00, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-06-15: treasury £18,824.15, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-07-15: treasury £18,794.68, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-08-14: treasury £18,765.43, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-09-13: treasury £18,733.32, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-10-13: treasury £18,672.12, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-11-12: treasury £18,619.48, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-12-12: treasury £18,487.52, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-04-11: treasury £17,987.82, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2022-05-11: treasury £17,836.95, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2022-06-10: treasury £17,713.15, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2022-07-10: treasury £17,611.64, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2022-08-09: treasury £17,517.14, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2022-09-08: treasury £17,423.73, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2022-10-08: treasury £17,294.32, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2022-11-07: treasury £17,149.93, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2022-12-07: treasury £16,943.22, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2022-04-06: treasury £16,031.48, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-05-06: treasury £15,930.11, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-06-05: treasury £15,867.17, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-07-05: treasury £15,825.18, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-08-04: treasury £15,793.01, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-09-03: treasury £15,760.57, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-10-03: treasury £15,696.16, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-11-02: treasury £15,622.98, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-12-02: treasury £15,496.12, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-07-01: treasury £14,836.20, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-07-31: treasury £14,830.69, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-08-30: treasury £14,825.20, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-09-29: treasury £14,816.67, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-10-29: treasury £14,805.62, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-11-28: treasury £14,790.14, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-12-28: treasury £14,766.00, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2022-10-27: treasury £14,614.54, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2022-11-26: treasury £14,542.73, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2022-12-26: treasury £14,469.93, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.48
- Worst single period: C4g on 2022-09-30 period 1, net margin £-1.64

**Customer Book**

- Active accounts: 9 (C2, C2_2, C2g, C4, C4g, C6, C7, C8, C9)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: C2_2
- Losses (churn) during year: C2
  - Renewals (retained): 5 accounts
- Average CLV (Point-in-Time, year-end 2022): £-1,419.95
  - By billing account: C1 £-464.64, C2 £-861.75, C2_2 £-535.12, C3 £-235.86, C4 £-1,831.59, C5 £-1,759.96, C6 £-3,670.54, C7 £-1,498.60, C8 £-2,189.77, C9 £-1,151.65
- Bill shock events (>=20%): 35 -- C7 2022-01-31 (175%); C7 2022-02-28 (25%); C7 2022-04-30 (20%); C7 2022-05-31 (34%); C7 2022-06-30 (25%); C7 2022-09-30 (29%); C7 2022-11-30 (55%); C7 2022-12-31 (52%); C6 2022-04-30 (82%); C6 2022-05-31 (23%); C6 2022-09-30 (25%); C6 2022-11-30 (43%); C6 2022-12-31 (33%); C8 2022-02-28 (22%); C8 2022-04-30 (69%); C8 2022-05-31 (39%); C8 2022-06-30 (33%); C8 2022-09-30 (76%); C8 2022-11-30 (65%); C8 2022-12-31 (57%); C9 2022-05-31 (29%); C9 2022-06-30 (27%); C9 2022-07-31 (38%); C9 2022-09-30 (45%); C9 2022-10-31 (32%); C9 2022-11-30 (40%); C9 2022-12-31 (53%); C4 2022-10-31 (82%); C4g 2022-10-31 (178%); C2_2 2022-04-30 (1719%); C2_2 2022-05-31 (39%); C2_2 2022-06-30 (33%); C2_2 2022-09-30 (76%); C2_2 2022-11-30 (64%); C2_2 2022-12-31 (57%)
- Churn risk (accounts renewing in 2022): 5 at risk (≥20% churn prob): C4 23%, C6 35%, C7 38%, C8 35%, C9 38%

**Pricing & Margin**

- C2 (electricity): tariff £73.44/MWh, net margin £-109.67 -- **net-negative**
- C2_2 (electricity): tariff £238.67/MWh, net margin £-592.90 -- **net-negative**
- C2g (gas): tariff £21.81/MWh, net margin £-13.42 -- **net-negative**
- C4 (electricity): tariff £134.66-£292.40/MWh, net margin £-836.57 -- **net-negative**
- C4g (gas): tariff £48.71-£165.18/MWh, net margin £-382.61 -- **net-negative**
- C6 (electricity): tariff £73.44-£238.67/MWh, net margin £-1,647.41 -- **net-negative**
- C7 (electricity): tariff £220.50-£228.32/MWh, net margin £-757.76 -- **net-negative**
- C8 (electricity): tariff £73.44-£238.67/MWh, net margin £-970.02 -- **net-negative**
- C9 (electricity): tariff £83.14-£202.15/MWh, net margin £-272.42 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -2.0% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £22,891.54 -> £13,267.24 (42.0%)
- Bills issued: 88, average clarity 0.808, average bill shock 44.3%, bad debt provision £383.85, avg complaint probability 5.6%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-6,892.36 vs. naked (unhedged) net margin: £1,275.26
- hedging cost £8,167.63 vs. a fully unhedged book (commodity-only: actual net £-6,892.36 vs. naked net £1,275.26)
  - C2_2: actual £-914.53 vs. naked £143.05 -- hedging cost £1,057.59
  - C4: actual £-799.38 vs. naked £950.85 -- hedging cost £1,750.23
  - C4g: actual £-598.89 vs. naked £2,266.06 -- hedging cost £2,864.96
  - C6: actual £-2,000.99 vs. naked £-2,369.36 -- hedging added £368.37
  - C7: actual £-1,186.42 vs. naked £907.92 -- hedging cost £2,094.34
  - C8: actual £-1,227.88 vs. naked £-395.75 -- hedging cost £832.14
  - C9: actual £-164.27 vs. naked £-227.51 -- hedging added £63.24

**Year narrative:** 2022 (flagged crisis year) produced a net loss of £-5,582.79 across 9 accounts. The risk committee intervened 71 time(s), raising hedge fractions in response to elevated VaR. 35 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £-3,566.34 (gross £-3,475.21, capital £91.13)
  - Electricity: gross £-3,046.22, capital £85.32, net £-3,131.54
  - Gas: gross £-428.99, capital £5.81, net £-434.80
- Treasury at year end: £12,191.98
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C4 0.90 (avg 0.90), C4g 0.90 (avg 0.90), C6 1.00 (avg 1.00), C7 0.90 (avg 0.90), C8 0.90 (avg 0.90), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 73
  - 2023-01-11: treasury £18,356.73, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2023-02-10: treasury £18,230.90, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2023-03-12: treasury £18,116.93, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2023-01-06: treasury £16,695.76, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2023-02-05: treasury £16,459.35, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2023-03-07: treasury £16,229.49, C2->0.95, C4->1.00, C7->1.00, C8->1.00, VaR (current £1,412.48 / stressed £574.03) ratio 2.46
  - 2023-01-01: treasury £15,306.63, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2023-01-31: treasury £15,133.41, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2023-03-02: treasury £14,978.49, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2023-01-27: treasury £14,744.41, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2023-02-26: treasury £14,725.79, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2023-03-29: treasury £14,704.79, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2023-04-28: treasury £14,689.21, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2023-05-28: treasury £14,678.70, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2023-06-27: treasury £14,672.95, C2->0.95, C4->1.00, C7->1.00, VaR (current £1,241.81 / stressed £516.91) ratio 2.40
  - 2023-01-25: treasury £14,397.06, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2023-02-24: treasury £14,324.36, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2023-03-26: treasury £14,251.66, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2023-04-25: treasury £14,188.88, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2023-05-25: treasury £14,127.64, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2023-06-24: treasury £14,068.52, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2023-07-24: treasury £14,009.37, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2023-08-23: treasury £13,950.55, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2023-09-22: treasury £13,888.87, C2->0.95, C7->1.00, VaR (current £1,059.57 / stressed £459.54) ratio 2.31
  - 2023-01-13: treasury £13,216.22, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-02-12: treasury £13,041.67, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-03-14: treasury £12,892.11, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-04-13: treasury £12,774.50, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-05-13: treasury £12,677.18, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-06-12: treasury £12,610.56, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-07-12: treasury £12,563.17, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-08-11: treasury £12,515.56, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-09-10: treasury £12,466.86, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-10-10: treasury £12,412.74, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-11-09: treasury £12,315.25, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-12-09: treasury £12,168.24, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-04-09: treasury £12,090.57, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-05-09: treasury £12,104.56, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-06-08: treasury £12,114.32, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-07-08: treasury £12,118.27, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-08-07: treasury £12,123.44, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-09-06: treasury £12,128.01, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-10-06: treasury £12,134.56, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-11-05: treasury £12,146.74, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-12-05: treasury £12,169.49, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-04-04: treasury £12,277.10, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-05-04: treasury £12,285.68, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-06-03: treasury £12,291.83, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-07-03: treasury £12,296.71, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-08-02: treasury £12,301.60, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-09-01: treasury £12,306.47, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-10-01: treasury £12,311.59, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-10-31: treasury £12,318.78, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-11-30: treasury £12,329.40, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-12-30: treasury £12,340.11, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2023-04-29: treasury £12,378.52, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-05-29: treasury £12,384.15, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-06-28: treasury £12,385.30, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-07-28: treasury £12,386.84, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-08-27: treasury £12,387.96, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-09-26: treasury £12,389.72, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-10-26: treasury £12,394.94, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-11-25: treasury £12,407.92, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-12-25: treasury £12,426.18, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-07-24: treasury £12,489.66, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-08-23: treasury £12,488.43, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-09-22: treasury £12,486.76, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-10-22: treasury £12,484.25, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-11-21: treasury £12,480.16, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-12-21: treasury £12,475.23, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2023-10-19: treasury £12,447.56, C2->0.95, VaR (current £1,013.09 / stressed £1,027.22) ratio 0.99
  - 2023-11-18: treasury £12,440.54, C2->0.95, VaR (current £1,013.09 / stressed £1,027.22) ratio 0.99
  - 2023-12-18: treasury £12,433.78, C2->0.95, VaR (current £1,013.09 / stressed £1,027.22) ratio 0.99
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 1.96
- Worst single period: C4g on 2023-01-01 period 1, net margin £-1.64

**Customer Book**

- Active accounts: 7 (C2_2, C4, C4g, C6, C7, C8, C9)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 1
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2023): £-1,455.94
  - By billing account: C1 £-409.74, C2 £-859.68, C2_2 £-595.29, C3 £-197.49, C4 £-2,319.57, C5 £-1,766.93, C6 £-3,275.65, C7 £-1,994.87, C8 £-2,046.77, C9 £-1,093.40
- Bill shock events (>=20%): 28 -- C7 2023-05-31 (31%); C7 2023-06-30 (33%); C7 2023-10-31 (49%); C7 2023-11-30 (63%); C6 2023-04-30 (30%); C6 2023-05-31 (23%); C6 2023-06-30 (23%); C6 2023-10-31 (38%); C6 2023-11-30 (44%); C8 2023-04-30 (31%); C8 2023-05-31 (41%); C8 2023-06-30 (42%); C8 2023-10-31 (94%); C8 2023-11-30 (66%); C9 2023-02-28 (20%); C9 2023-04-30 (25%); C9 2023-05-31 (33%); C9 2023-06-30 (44%); C9 2023-09-30 (21%); C9 2023-10-31 (70%); C9 2023-11-30 (50%); C4 2023-10-31 (51%); C4g 2023-10-31 (71%); C2_2 2023-04-30 (31%); C2_2 2023-05-31 (41%); C2_2 2023-06-30 (42%); C2_2 2023-10-31 (94%); C2_2 2023-11-30 (66%)
- Churn risk (accounts renewing in 2023): 6 at risk (≥20% churn prob): C2_2 35%, C4 20%, C6 26%, C7 38%, C8 35%, C9 35%

**Pricing & Margin**

- C2_2 (electricity): tariff £200.96-£238.67/MWh, net margin £-217.34 -- **net-negative**
- C4 (electricity): tariff £96.30-£292.40/MWh, net margin £-603.08 -- **net-negative**
- C4g (gas): tariff £35.38-£165.18/MWh, net margin £-434.80 -- **net-negative**
- C6 (electricity): tariff £200.96-£238.67/MWh, net margin £-603.91 -- **net-negative**
- C7 (electricity): tariff £101.20-£228.32/MWh, net margin £-1,184.14 -- **net-negative**
- C8 (electricity): tariff £200.96-£238.67/MWh, net margin £-414.37 -- **net-negative**
- C9 (electricity): tariff £118.46-£202.15/MWh, net margin £-108.71 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -2.6% of gross
- Treasury drawdown events (>=10% threshold): 1 -- £18,387.14 -> £12,086.07 (34.3%)
- Bills issued: 84, average clarity 0.818, average bill shock 19.1%, bad debt provision £455.21, avg complaint probability 5.0%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £94.14 vs. naked (unhedged) net margin: £1,324.67
- hedging cost £1,230.52 vs. a fully unhedged book (commodity-only: actual net £94.14 vs. naked net £1,324.67)
  - C2_2: actual £187.95 vs. naked £952.16 -- hedging cost £764.20
  - C4: actual £-63.51 vs. naked £43.46 -- hedging cost £106.98
  - C4g: actual £61.03 vs. naked £-39.89 -- hedging added £100.92
  - C6: actual £97.22 vs. naked £-215.75 -- hedging added £312.97
  - C7: actual £-267.89 vs. naked £-121.89 -- hedging cost £146.00
  - C8: actual £118.03 vs. naked £647.39 -- hedging cost £529.36
  - C9: actual £-38.68 vs. naked £59.19 -- hedging cost £97.86

**Year narrative:** 2023 produced a net loss of £-3,566.34 across 7 accounts. The risk committee intervened 73 time(s), raising hedge fractions in response to elevated VaR. 28 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £-452.92 (gross £-301.49, capital £151.43)
  - Electricity: gross £-364.09, capital £138.36, net £-502.45
  - Gas: gross £62.59, capital £13.07, net £49.52
- Treasury at year end: £12,079.69
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C7 0.85 (avg 0.85), C8 0.85 (avg 0.85), C9 0.90 (avg 0.90)
- Risk committee (Context Handshake) interventions: 33
  - 2024-01-04: treasury £12,195.72, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2024-02-03: treasury £12,226.48, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2024-03-04: treasury £12,255.34, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2024-01-29: treasury £12,351.91, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2024-02-28: treasury £12,362.51, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2024-03-29: treasury £12,372.83, C2->0.95, VaR (current £668.23 / stressed £311.11) ratio 2.15
  - 2024-01-24: treasury £12,449.80, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2024-02-23: treasury £12,468.53, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2024-03-24: treasury £12,488.03, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2024-01-20: treasury £12,469.85, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2024-02-19: treasury £12,465.52, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2024-03-20: treasury £12,461.06, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2024-04-19: treasury £12,457.22, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2024-05-19: treasury £12,454.83, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2024-06-18: treasury £12,452.67, C2->0.95, VaR (current £932.26 / stressed £882.22) ratio 1.06
  - 2024-01-17: treasury £12,428.92, C2->0.95, VaR (current £1,013.09 / stressed £1,027.22) ratio 0.99
  - 2024-02-16: treasury £12,423.90, C2->0.95, VaR (current £1,013.09 / stressed £1,027.22) ratio 0.99
  - 2024-03-17: treasury £12,418.77, C2->0.95, VaR (current £1,013.09 / stressed £1,027.22) ratio 0.99
  - 2024-04-16: treasury £12,414.81, C2->0.95, VaR (current £1,013.09 / stressed £1,027.22) ratio 0.99
  - 2024-05-16: treasury £12,409.99, C2->0.95, VaR (current £1,013.09 / stressed £1,027.22) ratio 0.99
  - 2024-06-15: treasury £12,405.29, C2->0.95, VaR (current £1,013.09 / stressed £1,027.22) ratio 0.99
  - 2024-07-15: treasury £12,400.60, C2->0.95, VaR (current £1,013.09 / stressed £1,027.22) ratio 0.99
  - 2024-08-14: treasury £12,396.08, C2->0.95, VaR (current £1,013.09 / stressed £1,027.22) ratio 0.99
  - 2024-09-13: treasury £12,391.51, C2->0.95, VaR (current £1,013.09 / stressed £1,027.22) ratio 0.99
  - 2024-01-06: treasury £12,440.25, C2->0.95, VaR (current £1,189.59 / stressed £1,421.00) ratio 0.84
  - 2024-02-05: treasury £12,406.05, C2->0.95, VaR (current £1,189.59 / stressed £1,421.00) ratio 0.84
  - 2024-03-06: treasury £12,378.21, C2->0.95, VaR (current £1,189.59 / stressed £1,421.00) ratio 0.84
  - 2024-04-05: treasury £12,353.64, C2->0.95, VaR (current £1,189.59 / stressed £1,421.00) ratio 0.84
  - 2024-05-05: treasury £12,332.34, C2->0.95, VaR (current £1,189.59 / stressed £1,421.00) ratio 0.84
  - 2024-06-04: treasury £12,317.71, C2->0.95, VaR (current £1,189.59 / stressed £1,421.00) ratio 0.84
  - 2024-07-04: treasury £12,303.68, C2->0.95, VaR (current £1,189.59 / stressed £1,421.00) ratio 0.84
  - 2024-08-03: treasury £12,291.31, C2->0.95, VaR (current £1,189.59 / stressed £1,421.00) ratio 0.84
  - 2024-09-02: treasury £12,280.06, C2->0.95, VaR (current £1,189.59 / stressed £1,421.00) ratio 0.84
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 1.18
- Worst single period: C8 on 2024-12-12 period 34, net margin £-0.19

**Customer Book**

- Active accounts: 7 (C2_2, C4, C4g, C6, C7, C8, C9)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 1
- New acquisitions this year: none
- Losses (churn) during year: C6, C4
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2024): £-1,282.65
  - By billing account: C1 £-407.50, C2 £-909.45, C2_2 £-566.89, C3 £-186.73, C4 £-1,767.12, C5 £-1,601.78, C6 £-2,984.07, C7 £-1,764.69, C8 £-1,719.65, C9 £-918.67
- Bill shock events (>=20%): 27 -- C7 2024-01-31 (32%); C7 2024-02-29 (26%); C7 2024-04-30 (20%); C7 2024-05-31 (35%); C7 2024-09-30 (30%); C7 2024-10-31 (33%); C7 2024-11-30 (43%); C8 2024-02-29 (22%); C8 2024-04-30 (57%); C8 2024-05-31 (48%); C8 2024-07-31 (26%); C8 2024-09-30 (66%); C8 2024-10-31 (35%); C8 2024-11-30 (58%); C9 2024-04-30 (21%); C9 2024-05-31 (48%); C9 2024-07-31 (38%); C9 2024-09-30 (48%); C9 2024-10-31 (23%); C9 2024-11-30 (45%); C2_2 2024-02-29 (22%); C2_2 2024-04-30 (57%); C2_2 2024-05-31 (48%); C2_2 2024-07-31 (25%); C2_2 2024-09-30 (65%); C2_2 2024-10-31 (35%); C2_2 2024-11-30 (57%)
- Churn risk (accounts renewing in 2024): 6 at risk (≥20% churn prob): C2_2 41%, C4 23%, C6 38%, C7 35%, C8 41%, C9 35%

**Pricing & Margin**

- C2_2 (electricity): tariff £80.99-£200.96/MWh, net margin £-18.48 -- **net-negative**
- C4 (electricity): tariff £96.30/MWh, net margin £-43.64 -- **net-negative**
- C4g (gas): tariff £35.38/MWh, net margin £49.52
- C6 (electricity): tariff £200.96/MWh, net margin £32.45
- C7 (electricity): tariff £101.20-£103.55/MWh, net margin £-269.77 -- **net-negative**
- C8 (electricity): tariff £80.99-£200.96/MWh, net margin £-77.56 -- **net-negative**
- C9 (electricity): tariff £77.83-£118.46/MWh, net margin £-125.44 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -50.2% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 69, average clarity 0.810, average bill shock 19.4%, bad debt provision £227.33, avg complaint probability 5.1%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-798.32 vs. naked (unhedged) net margin: £-1,689.07
- hedging added £890.75 vs. a fully unhedged book (commodity-only: actual net £-798.32 vs. naked net £-1,689.07)
  - C2_2: actual £-188.73 vs. naked £-313.08 -- hedging added £124.35
  - C7: actual £-138.59 vs. naked £-241.76 -- hedging added £103.17
  - C8: actual £-241.28 vs. naked £-554.70 -- hedging added £313.42
  - C9: actual £-229.71 vs. naked £-579.53 -- hedging added £349.82

**Year narrative:** 2024 produced a net loss of £-452.92 across 7 accounts. The risk committee intervened 33 time(s), raising hedge fractions in response to elevated VaR. 27 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £-700.42 (gross £-629.95, capital £70.47)
  - Electricity: gross £-629.95, capital £70.47, net £-700.42
- Treasury at year end: £11,522.11
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.95 (avg 0.95), C8 0.95 (avg 0.95)
- Risk committee (Context Handshake) interventions: 2
  - 2025-04-21: treasury £11,207.32, C2->0.95, VaR (current £1,297.08 / stressed £1,632.52) ratio 0.79
  - 2025-05-21: treasury £11,159.70, C2->0.95, VaR (current £1,297.08 / stressed £1,632.52) ratio 0.79
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 0.79
- Worst single period: C8 on 2025-01-08 period 36, net margin £-1.75

**Customer Book**

- Active accounts: 4 (C2_2, C7, C8, C9)
  - Resi electricity: 4, SME electricity: 0, gas (dual-fuel): 0
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 2 accounts
- Average CLV (Point-in-Time, year-end 2025): £-1,240.25
  - By billing account: C1 £-350.15, C2 £-820.58, C2_2 £-521.29, C3 £-216.74, C4 £-1,723.89, C5 £-1,573.31, C6 £-2,683.48, C7 £-1,839.54, C8 £-1,733.10, C9 £-940.38
- Bill shock events (>=20%): 18 -- C7 2025-01-31 (26%); C7 2025-04-30 (36%); C7 2025-05-31 (21%); C7 2025-06-07 (80%); C8 2025-01-31 (38%); C8 2025-02-28 (24%); C8 2025-04-30 (21%); C8 2025-05-31 (36%); C8 2025-06-07 (73%); C9 2025-01-31 (21%); C9 2025-04-30 (25%); C9 2025-05-31 (32%); C9 2025-06-07 (72%); C2_2 2025-01-31 (38%); C2_2 2025-02-28 (24%); C2_2 2025-04-30 (21%); C2_2 2025-05-31 (36%); C2_2 2025-06-07 (73%)
- Churn risk (accounts renewing in 2025): 3 at risk (≥20% churn prob): C2_2 38%, C8 38%, C9 35%

**Pricing & Margin**

- C2_2 (electricity): tariff £80.99-£121.78/MWh, net margin £-202.56 -- **net-negative**
- C7 (electricity): tariff £103.55/MWh, net margin £-132.13 -- **net-negative**
- C8 (electricity): tariff £80.99-£121.78/MWh, net margin £-240.00 -- **net-negative**
- C9 (electricity): tariff £77.83/MWh, net margin £-125.73 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -11.2% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 24, average clarity 0.729, average bill shock 31.6%, bad debt provision £77.50, avg complaint probability 7.2%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-252.34 vs. naked (unhedged) net margin: £-150.74
- hedging cost £101.60 vs. a fully unhedged book (commodity-only: actual net £-252.34 vs. naked net £-150.74)
  - C2_2: actual £-115.97 vs. naked £-5.78 -- hedging cost £110.19
  - C8: actual £-136.37 vs. naked £-144.96 -- hedging added £8.59

**Year narrative:** 2025 produced a net loss of £-700.42 across 4 accounts. The risk committee intervened 2 time(s), raising hedge fractions in response to elevated VaR. 18 customer(s) experienced a bill shock of >=20%.
