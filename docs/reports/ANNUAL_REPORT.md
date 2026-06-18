# Annual Report — The Synthetic Enterprise

## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £29,846.19
- Final treasury: £33,406.60
  (£3,560.41 net change)
- Revenue: £100,875.28
- Gross margin: £4,788.04
- Capital costs: £1,227.63
- Net margin: £3,560.41
- Capital cost ratio: 25.6% of gross
- Net margin as % of revenue: 3.5%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 160
- Bills issued: 1117, average clarity 0.862,
  service quality score 0.914
- Enterprise value (CLV sum across 10 billing accounts): £-1,635.32
- Cost to serve (whole portfolio): £6,460.24, net margin after cost to serve: £-1,672.19
- Hedge effectiveness (whole window): hedging cost £1,656.28 vs. a fully unhedged book (actual net £3,560.41 vs. naked net £5,216.69)

- **2021** (crisis year): net margin £-343.62, 4 risk committee wake-up(s).
- **2022** (crisis year): net margin £361.19, 30 risk committee wake-up(s).

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

**Note:** the figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run: gross £4,788.04, capital £1,227.63, net £3,560.41. Old-model run: gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 25.6% under the new mandate vs. 41.0% under the old reactive model.
- **2021 net margin**: £-343.62 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 3.5%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run): £3,560.41
- Old reactive model (actual): £26,779.56
- Fully naked (this run's counterfactual): £5,216.69
- Fully naked (old run's counterfactual): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.
## Administration Events

None — business survived the full simulation window.

## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £1,656.28 vs. a fully unhedged book (actual net £3,560.41 vs. naked net £5,216.69)
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
| 2016 | £22.90 | £94.49 | £84.20 | £201.59 |
| 2017 | £98.27 | £198.49 | £124.12 | £420.88 |
| 2018 | £86.55 | £224.78 | £137.61 | £448.93 |
| 2019 | £147.62 | £304.64 | £164.65 | £616.92 |
| 2020 | £110.22 | £224.48 | £139.04 | £473.74 |
| 2021 | £-196.16 | £-131.89 | £-15.56 | £-343.62 |
| 2022 | £49.28 | £290.15 | £21.76 | £361.19 |
| 2023 | £151.65 | £554.16 | £82.67 | £788.48 |
| 2024 | £56.56 | £418.53 | £47.96 | £523.05 |
| 2025 | £0.00 | £69.25 | £0.00 | £69.25 |

## Customer Lifecycle Events

Renewal decisions rolled at each annual renewal point across the simulation window.
Retained: **43** renewals.  Lost (churned): **6** accounts.

Accounts lost before end of window: C1, C2, C3, C4, C5, C6

| Account | Date | Outcome | p(churn) | p(win-back) | p(retain) | Roll |
|---------|------|---------|----------|-------------|-----------|------|
| C1 | 2016-12-31 | renewed | 0.0800 | 0.5500 | 0.9640 | 0.1646 |
| C5 | 2016-12-31 | renewed | 0.2900 | 0.3500 | 0.8115 | 0.2812 |
| C7 | 2016-12-31 | renewed | 0.2900 | 0.5500 | 0.8695 | 0.1050 |
| C1 | 2017-12-31 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.6188 |
| C5 | 2017-12-31 | renewed | 0.3200 | 0.3500 | 0.7920 | 0.4449 |
| C7 | 2017-12-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.8255 |
| C1 | 2018-12-31 | renewed | 0.0800 | 0.5500 | 0.9640 | 0.0480 |
| C5 | 2018-12-31 | renewed | 0.3200 | 0.3500 | 0.7920 | 0.3096 |
| C7 | 2018-12-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.6312 |
| C1 | 2019-12-31 | renewed | 0.1100 | 0.5500 | 0.9505 | 0.2972 |
| C5 | 2019-12-31 | renewed | 0.3500 | 0.3500 | 0.7725 | 0.4302 |
| C7 | 2019-12-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.7670 |
| C2 | 2020-03-31 | renewed | 0.1700 | 0.5500 | 0.9235 | 0.8936 |
| C6 | 2020-03-31 | renewed | 0.3800 | 0.3500 | 0.7530 | 0.4643 |
| C8 | 2020-03-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1066 |
| C3 | 2020-06-30 | churned **CHURNED** | 0.1400 | 0.5500 | 0.9370 | 0.9704 |
| C9 | 2020-06-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.5378 |
| C4 | 2020-09-30 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.2845 |
| C1 | 2020-12-30 | renewed | 0.2300 | 0.5500 | 0.8965 | 0.8047 |
| C5 | 2020-12-30 | renewed | 0.3200 | 0.3500 | 0.7920 | 0.7480 |
| C7 | 2020-12-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.4829 |
| C2 | 2021-03-31 | renewed | 0.2000 | 0.5500 | 0.9100 | 0.6102 |
| C6 | 2021-03-31 | renewed | 0.3800 | 0.3500 | 0.7530 | 0.5431 |
| C8 | 2021-03-31 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.4901 |
| C9 | 2021-06-30 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.5305 |
| C4 | 2021-09-30 | renewed | 0.0500 | 0.5500 | 0.9775 | 0.4564 |
| C1 | 2021-12-30 | churned **CHURNED** | 0.1700 | 0.5500 | 0.9235 | 0.9691 |
| C5 | 2021-12-30 | churned **CHURNED** | 0.3500 | 0.3500 | 0.7725 | 0.8247 |
| C7 | 2021-12-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1963 |
| C2 | 2022-03-31 | churned **CHURNED** | 0.2000 | 0.5500 | 0.9100 | 0.9547 |
| C6 | 2022-03-31 | renewed | 0.3500 | 0.3500 | 0.7725 | 0.1058 |
| C8 | 2022-03-31 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.5712 |
| C9 | 2022-06-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.5875 |
| C4 | 2022-09-30 | renewed | 0.2300 | 0.5500 | 0.8965 | 0.8552 |
| C7 | 2022-12-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.0637 |
| C2_2 | 2023-03-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.0093 |
| C6 | 2023-03-31 | renewed | 0.2600 | 0.3500 | 0.8310 | 0.5155 |
| C8 | 2023-03-31 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.3785 |
| C9 | 2023-06-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.0307 |
| C4 | 2023-09-30 | renewed | 0.1700 | 0.5500 | 0.9235 | 0.6095 |
| C7 | 2023-12-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.1905 |
| C2_2 | 2024-03-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.6064 |
| C6 | 2024-03-30 | churned **CHURNED** | 0.3800 | 0.3500 | 0.7530 | 0.9632 |
| C8 | 2024-03-30 | renewed | 0.4100 | 0.5500 | 0.8155 | 0.0592 |
| C9 | 2024-06-29 | renewed | 0.3500 | 0.5500 | 0.8425 | 0.0025 |
| C4 | 2024-09-29 | churned **CHURNED** | 0.2300 | 0.5500 | 0.8965 | 0.9018 |
| C7 | 2024-12-29 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4099 |
| C2_2 | 2025-03-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4434 |
| C8 | 2025-03-30 | renewed | 0.3800 | 0.5500 | 0.8290 | 0.4808 |

## CLV Trajectory

Point-in-Time Customer Lifetime Value per billing account at each year-end.
CLV is computed from churn renewal history and net margins accumulated up to that date only (Point-in-Time Blindfold). '—' = no renewal points yet.

| Year | C1 | C2 | C2_2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 |
|------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| 2016 | £-74.07 | — | — | — | — | £-177.31 | — | £-18.76 | — | — |
| 2017 | £-124.70 | £135.97 | — | £-186.20 | £2.26 | £-242.72 | £-671.10 | £-45.22 | £-307.56 | £-305.89 |
| 2018 | £-134.87 | £141.18 | — | £-163.18 | £-23.27 | £-271.19 | £-524.99 | £-73.54 | £-118.16 | £-239.74 |
| 2019 | £-120.70 | £170.31 | — | £-103.49 | £-6.81 | £-291.82 | £-382.99 | £-76.13 | £-30.01 | £-208.68 |
| 2020 | £-107.66 | £156.27 | — | £-74.96 | £14.82 | £-277.17 | £-290.28 | £-64.59 | £-25.80 | £-188.11 |
| 2021 | £-171.04 | £70.91 | — | £-73.89 | £-71.90 | £-438.00 | £-335.26 | £-157.89 | £-88.91 | £-212.44 |
| 2022 | £-176.61 | £23.82 | £48.13 | £-83.46 | £-104.60 | £-382.11 | £-362.25 | £-142.26 | £-114.46 | £-223.80 |
| 2023 | £-151.46 | £25.55 | £161.78 | £-66.39 | £-97.75 | £-407.88 | £-321.01 | £-156.66 | £-76.67 | £-187.33 |
| 2024 | £-133.91 | £21.89 | £161.85 | £-77.18 | £-51.58 | £-337.88 | £-259.32 | £-126.15 | £-32.70 | £-164.65 |
| 2025 | £-125.43 | £23.75 | £132.25 | £-70.69 | £-54.49 | £-357.18 | £-230.20 | £-97.59 | £-35.23 | £-160.76 |

## Cost to Serve & Pricing Actions

Whole-run totals (cumulative across all settlement periods). Average: £461.45, range £24.03–£1,156.79.

- C1: cost to serve £362.40, net margin after CTS £-296.15 — **NET_NEGATIVE** (tariff uplift needed: +18.2%)
- C1g: cost to serve £34.70, net margin after CTS £86.56
- C2: cost to serve £401.28, net margin after CTS £-152.22 — **NET_NEGATIVE** (tariff uplift needed: +4.3%)
- C2_2: cost to serve £315.64, net margin after CTS £298.43
- C2g: cost to serve £46.14, net margin after CTS £185.53
- C3: cost to serve £242.14, net margin after CTS £-168.29 — **NET_NEGATIVE** (tariff uplift needed: +15.2%)
- C3g: cost to serve £24.03, net margin after CTS £100.18
- C4: cost to serve £594.00, net margin after CTS £-306.22 — **NET_NEGATIVE** (tariff uplift needed: +4.0%)
- C4g: cost to serve £177.07, net margin after CTS £200.28
- C5: cost to serve £798.72, net margin after CTS £-498.01 — **NET_NEGATIVE** (tariff uplift needed: +6.3%)
- C6: cost to serve £1,156.79, net margin after CTS £-484.37 — **NET_NEGATIVE** (tariff uplift needed: +2.5%)
- C7: cost to serve £831.90, net margin after CTS £-217.02 — **NET_NEGATIVE** (tariff uplift needed: +1.4%)
- C8: cost to serve £779.32, net margin after CTS £-83.19 — **NET_NEGATIVE** (tariff uplift needed: +0.6%)
- C9: cost to serve £696.10, net margin after CTS £-337.72 — **NET_NEGATIVE** (tariff uplift needed: +3.3%)

**Activity-Based Pricing Actions**

The following 9 customer(s) are loss-making after cost-to-serve and require immediate tariff review:
  - C1: net margin after CTS £-296.15 on revenue £1,623.56 — raise tariff by ≥18.2% to break even
  - C2: net margin after CTS £-152.22 on revenue £3,567.40 — raise tariff by ≥4.3% to break even
  - C3: net margin after CTS £-168.29 on revenue £1,109.62 — raise tariff by ≥15.2% to break even
  - C4: net margin after CTS £-306.22 on revenue £7,705.52 — raise tariff by ≥4.0% to break even
  - C5: net margin after CTS £-498.01 on revenue £7,886.83 — raise tariff by ≥6.3% to break even
  - C6: net margin after CTS £-484.37 on revenue £19,701.39 — raise tariff by ≥2.5% to break even
  - C7: net margin after CTS £-217.02 on revenue £15,638.34 — raise tariff by ≥1.4% to break even
  - C8: net margin after CTS £-83.19 on revenue £13,694.60 — raise tariff by ≥0.6% to break even
  - C9: net margin after CTS £-337.72 on revenue £10,219.12 — raise tariff by ≥3.3% to break even

## Transaction Log

Total events: 2,235,809

| Event type | Count |
|------------|-------|
| bad_debt_event | 1,117 |
| billing_event | 1,117 |
| capital_charge_event | 1,019,177 |
| payment_received_event | 1,117 |
| settlement_event | 1,213,281 |

**Cash-flow waterfall (from ledger)**

| Flow | Amount |
|------|--------|
| Revenue billed (billing events) | £100,875.28 |
|   Less: bad debt written off | (£1,944.15) |
| = Cash collected | £98,931.13 |
| Wholesale cost (settlement events) | (£96,087.24) |
| Gross margin | £4,788.04 |
| Capital charges | (£1,227.63) |
| Net margin | £3,560.41 |
| Net margin (cash) | £1,616.26 |

Ledger P&L vs simulation direct: ✓ agrees with simulation

## 2016

**Trading & Risk**

- Net margin: £201.59 (gross £395.33, capital £193.74)
  - Electricity: gross £304.81, capital £187.42, net £117.39
  - Gas: gross £90.52, capital £6.32, net £84.20
- Treasury at year end: £29,976.48
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.90), C1g 0.85 (avg 0.85), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 0.85 (avg 0.85), C4 0.85 (avg 0.85), C4g 0.85 (avg 0.85), C5 0.85 (avg 0.90), C6 0.85 (avg 0.85), C7 0.85 (avg 0.90), C8 0.85 (avg 0.85), C9 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 81
  - 2016-01-01: treasury £29,846.19, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-01-31: treasury £29,847.61, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-03-01: treasury £29,849.16, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-03-31: treasury £29,850.51, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-04-30: treasury £29,851.64, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-05-30: treasury £29,852.89, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-06-29: treasury £29,853.74, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-07-29: treasury £29,854.76, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-08-28: treasury £29,855.86, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-09-27: treasury £29,856.78, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-10-27: treasury £29,857.55, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-11-26: treasury £29,857.13, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-12-26: treasury £29,858.21, C1->0.95, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-01-18: treasury £29,891.13, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-02-17: treasury £29,897.62, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-03-18: treasury £29,904.53, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-04-17: treasury £29,910.63, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-05-17: treasury £29,914.70, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-06-16: treasury £29,916.45, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-07-16: treasury £29,917.26, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-08-15: treasury £29,917.87, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-09-14: treasury £29,917.35, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-10-14: treasury £29,917.69, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-11-13: treasury £29,915.08, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-12-13: treasury £29,914.56, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-01-13: treasury £29,919.74, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-02-12: treasury £29,925.69, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-03-13: treasury £29,932.15, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-04-12: treasury £29,938.76, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-05-12: treasury £29,942.57, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-06-11: treasury £29,945.09, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-07-11: treasury £29,945.94, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-08-10: treasury £29,947.02, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-09-09: treasury £29,947.70, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-10-09: treasury £29,948.89, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-11-08: treasury £29,950.49, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-12-08: treasury £29,950.59, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-04-08: treasury £29,954.66, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-05-08: treasury £29,957.42, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-06-07: treasury £29,960.37, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-07-07: treasury £29,962.87, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-08-06: treasury £29,965.66, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-09-05: treasury £29,968.54, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-10-05: treasury £29,971.26, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-11-04: treasury £29,973.34, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-12-04: treasury £29,974.22, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-08-05: treasury £29,997.59, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-04-26: treasury £30,023.91, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-05-26: treasury £30,026.69, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-06-25: treasury £30,025.96, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-07-25: treasury £30,025.21, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-08-24: treasury £30,024.78, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-09-23: treasury £30,022.88, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-10-23: treasury £30,022.21, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-11-22: treasury £30,015.03, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-12-22: treasury £30,015.77, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-04-21: treasury £30,020.85, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-05-21: treasury £30,024.49, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-06-20: treasury £30,025.76, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-07-20: treasury £30,026.40, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-08-19: treasury £30,026.87, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-09-18: treasury £30,026.81, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-10-18: treasury £30,027.83, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-11-17: treasury £30,027.88, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-12-17: treasury £30,028.12, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-07-16: treasury £30,039.02, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-08-15: treasury £30,040.22, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-09-14: treasury £30,041.11, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-10-14: treasury £30,041.98, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-11-13: treasury £30,041.97, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-12-13: treasury £30,041.94, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-07-03: treasury £30,072.08, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-08-02: treasury £30,072.91, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-09-01: treasury £30,073.73, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-10-01: treasury £30,074.53, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-10-31: treasury £30,075.65, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-11-30: treasury £30,072.14, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-12-30: treasury £30,074.33, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-10-28: treasury £30,085.29, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2016-11-27: treasury £30,085.48, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2016-12-27: treasury £30,087.55, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 3.03
- Worst single period: C8 on 2016-11-08 period 40, net margin £-0.44

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2016): £-90.05
  - By billing account: C1 £-74.07, C5 £-177.31, C7 £-18.76
- Bill shock events (>=20%): 23 -- C1 2016-04-30 (21%); C5 2016-04-30 (21%); C5 2016-05-31 (30%); C5 2016-06-30 (22%); C5 2016-10-31 (47%); C5 2016-11-30 (49%); C7 2016-04-30 (20%); C7 2016-05-31 (38%); C7 2016-06-30 (31%); C7 2016-10-31 (81%); C7 2016-11-30 (52%); C6 2016-05-31 (28%); C6 2016-06-30 (25%); C6 2016-10-31 (46%); C6 2016-11-30 (51%); C8 2016-05-31 (42%); C8 2016-06-30 (45%); C8 2016-09-30 (29%); C8 2016-10-31 (118%); C8 2016-11-30 (71%); C9 2016-09-30 (22%); C9 2016-10-31 (86%); C9 2016-11-30 (60%)
- Churn risk (accounts renewing in 2016): 2 at risk (≥20% churn prob): C5 29%, C7 29%

**Pricing & Margin**

- C1 (electricity): tariff £62.25-£94.12/MWh, net margin £11.92
- C1g (gas): tariff £16.55-£16.64/MWh, net margin £29.04
- C2 (electricity): tariff £59.02/MWh, net margin £22.64
- C2g (gas): tariff £18.07/MWh, net margin £30.30
- C3 (electricity): tariff £51.42/MWh, net margin £4.15
- C3g (gas): tariff £13.45/MWh, net margin £13.76
- C4 (electricity): tariff £56.07/MWh, net margin £4.39
- C4g (gas): tariff £14.32/MWh, net margin £11.09
- C5 (electricity): tariff £62.25-£94.12/MWh, net margin £28.25
- C6 (electricity): tariff £59.02/MWh, net margin £-5.36 -- **net-negative**
- C7 (electricity): tariff £62.25-£94.12/MWh, net margin £36.03
- C8 (electricity): tariff £59.02/MWh, net margin £12.77
- C9 (electricity): tariff £51.42/MWh, net margin £2.60

**Portfolio Health**

- Capital cost ratio: 49.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 108, average clarity 0.888, average bill shock 14.6%, bad debt provision £98.25, avg complaint probability 3.7%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £459.84 vs. naked (unhedged) net margin: £480.69
- hedging cost £20.85 vs. a fully unhedged book (actual net £459.84 vs. naked net £480.69)
  - C1: actual £29.16 vs. naked £141.08 -- hedging cost £111.92
  - C1g: actual £51.31 vs. naked £45.90 -- hedging added £5.41
  - C2: actual £29.42 vs. naked £87.21 -- hedging cost £57.79
  - C2g: actual £37.97 vs. naked £66.51 -- hedging cost £28.54
  - C3: actual £8.97 vs. naked £-6.29 -- hedging added £15.27
  - C3g: actual £24.44 vs. naked £-6.81 -- hedging added £31.25
  - C4: actual £21.50 vs. naked £35.86 -- hedging cost £14.36
  - C4g: actual £38.18 vs. naked £-13.49 -- hedging added £51.67
  - C5: actual £99.32 vs. naked £226.37 -- hedging cost £127.05
  - C6: actual £-3.82 vs. naked £-317.20 -- hedging added £313.38
  - C7: actual £90.91 vs. naked £368.08 -- hedging cost £277.16
  - C8: actual £21.02 vs. naked £-43.79 -- hedging added £64.81
  - C9: actual £11.44 vs. naked £-102.73 -- hedging added £114.17

**Year narrative:** 2016 produced a net gain of £201.59 across 13 accounts. The risk committee intervened 81 time(s), raising hedge fractions in response to elevated VaR. 23 customer(s) experienced a bill shock of >=20%.

## 2017

**Trading & Risk**

- Net margin: £420.88 (gross £550.95, capital £130.07)
  - Electricity: gross £416.87, capital £120.11, net £296.76
  - Gas: gross £134.08, capital £9.96, net £124.12
- Treasury at year end: £30,337.23
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 0.95 (avg 0.95), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.95 (avg 0.95), C3g 0.95 (avg 0.95), C4 0.85 (avg 0.85), C4g 0.95 (avg 0.95), C5 0.85 (avg 0.85), C6 0.95 (avg 0.95), C7 0.85 (avg 0.85), C8 0.95 (avg 0.95), C9 0.95 (avg 0.95)
- Risk committee (Context Handshake) interventions: 42
  - 2017-01-03: treasury £29,976.71, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2017-02-02: treasury £29,978.34, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2017-03-04: treasury £29,980.65, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2017-01-21: treasury £30,015.61, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2017-02-20: treasury £30,014.18, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2017-03-22: treasury £30,016.97, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2017-01-16: treasury £30,031.28, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2017-02-15: treasury £30,032.92, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2017-03-17: treasury £30,036.96, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2017-01-12: treasury £30,042.81, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-02-11: treasury £30,042.97, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-03-13: treasury £30,043.99, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-04-12: treasury £30,045.35, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-05-12: treasury £30,046.17, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-06-11: treasury £30,046.74, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-01-29: treasury £30,074.40, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-02-28: treasury £30,076.28, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-03-30: treasury £30,078.85, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-04-29: treasury £30,081.78, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-05-29: treasury £30,082.07, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-06-28: treasury £30,083.17, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-01-26: treasury £30,088.86, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-02-25: treasury £30,090.49, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-03-27: treasury £30,092.79, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-04-26: treasury £30,095.20, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-05-26: treasury £30,096.46, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-06-25: treasury £30,098.61, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-07-25: treasury £30,100.82, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-08-24: treasury £30,102.83, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-09-23: treasury £30,104.44, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-01-15: treasury £30,143.58, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-02-14: treasury £30,145.10, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-03-16: treasury £30,146.87, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-04-15: treasury £30,148.45, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-05-15: treasury £30,149.76, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-06-14: treasury £30,150.94, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-07-14: treasury £30,152.20, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-08-13: treasury £30,153.45, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-09-12: treasury £30,154.69, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-10-12: treasury £30,155.98, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-11-11: treasury £30,157.51, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-12-11: treasury £30,159.10, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.72
- Worst single period: C9 on 2017-05-17 period 34, net margin £-0.17

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2017): £-193.91
  - By billing account: C1 £-124.70, C2 £135.97, C3 £-186.20, C4 £2.26, C5 £-242.72, C6 £-671.10, C7 £-45.22, C8 £-307.56, C9 £-305.89
- Bill shock events (>=20%): 32 -- C1 2017-01-31 (49%); C1 2017-04-30 (21%); C5 2017-01-31 (73%); C5 2017-02-28 (23%); C5 2017-05-31 (22%); C5 2017-06-30 (23%); C5 2017-11-30 (62%); C7 2017-01-31 (82%); C7 2017-02-28 (28%); C7 2017-05-31 (31%); C7 2017-06-30 (31%); C7 2017-09-30 (28%); C7 2017-10-31 (20%); C7 2017-11-30 (76%); C6 2017-05-31 (24%); C6 2017-06-30 (21%); C6 2017-11-30 (55%); C8 2017-05-31 (42%); C8 2017-06-30 (38%); C8 2017-09-30 (52%); C8 2017-10-31 (22%); C8 2017-11-30 (89%); C8 2017-12-31 (23%); C3 2017-07-31 (39%); C3g 2017-07-31 (26%); C9 2017-05-31 (35%); C9 2017-06-30 (27%); C9 2017-07-31 (24%); C9 2017-09-30 (33%); C9 2017-10-31 (22%); C9 2017-11-30 (74%); C4g 2017-10-31 (38%)
- Churn risk (accounts renewing in 2017): 6 at risk (≥20% churn prob): C1 20%, C5 32%, C6 35%, C7 35%, C8 35%, C9 29%

**Pricing & Margin**

- C1 (electricity): tariff £67.79-£94.12/MWh, net margin £17.05
- C1g (gas): tariff £16.55-£22.59/MWh, net margin £22.26
- C2 (electricity): tariff £59.02-£73.42/MWh, net margin £37.98
- C2g (gas): tariff £18.07-£22.20/MWh, net margin £38.20
- C3 (electricity): tariff £51.42-£69.10/MWh, net margin £12.17
- C3g (gas): tariff £13.45-£16.39/MWh, net margin £24.92
- C4 (electricity): tariff £56.07-£57.26/MWh, net margin £21.85
- C4g (gas): tariff £14.32-£19.06/MWh, net margin £38.75
- C5 (electricity): tariff £67.79-£94.12/MWh, net margin £69.05
- C6 (electricity): tariff £59.02-£73.42/MWh, net margin £29.22
- C7 (electricity): tariff £67.79-£94.12/MWh, net margin £53.99
- C8 (electricity): tariff £59.02-£73.42/MWh, net margin £30.53
- C9 (electricity): tariff £51.42-£69.10/MWh, net margin £24.91

**Portfolio Health**

- Capital cost ratio: 23.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.886, average bill shock 13.3%, bad debt provision £170.76, avg complaint probability 3.8%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £381.90 vs. naked (unhedged) net margin: £-103.28
- hedging added £485.17 vs. a fully unhedged book (actual net £381.90 vs. naked net £-103.28)
  - C1: actual £9.53 vs. naked £3.78 -- hedging added £5.75
  - C1g: actual £25.47 vs. naked £-3.82 -- hedging added £29.29
  - C2: actual £38.72 vs. naked £142.12 -- hedging cost £103.40
  - C2g: actual £37.64 vs. naked £60.01 -- hedging cost £22.37
  - C3: actual £13.86 vs. naked £37.07 -- hedging cost £23.21
  - C3g: actual £26.92 vs. naked £-40.23 -- hedging added £67.15
  - C4: actual £12.46 vs. naked £-24.96 -- hedging added £37.43
  - C4g: actual £43.58 vs. naked £-51.34 -- hedging added £94.92
  - C5: actual £29.33 vs. naked £-94.10 -- hedging added £123.43
  - C6: actual £42.79 vs. naked £-199.22 -- hedging added £242.01
  - C7: actual £29.56 vs. naked £-7.50 -- hedging added £37.06
  - C8: actual £36.74 vs. naked £62.86 -- hedging cost £26.12
  - C9: actual £35.30 vs. naked £12.06 -- hedging added £23.24

**Year narrative:** 2017 produced a net gain of £420.88 across 13 accounts. The risk committee intervened 42 time(s), raising hedge fractions in response to elevated VaR. 32 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £448.93 (gross £550.31, capital £101.37)
  - Electricity: gross £405.54, capital £94.21, net £311.33
  - Gas: gross £144.77, capital £7.16, net £137.61
- Treasury at year end: £30,740.21
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.95 (avg 0.95), C1g 1.00 (avg 1.00), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 1.00 (avg 1.00), C4 0.95 (avg 0.95), C4g 1.00 (avg 1.00), C5 0.95 (avg 0.95), C6 1.00 (avg 1.00), C7 0.95 (avg 0.95), C8 0.85 (avg 0.85), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C5 on 2018-03-01 period 34, net margin £-0.27

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2018): £-156.42
  - By billing account: C1 £-134.87, C2 £141.18, C3 £-163.18, C4 £-23.27, C5 £-271.19, C6 £-524.99, C7 £-73.54, C8 £-118.16, C9 £-239.74
- Bill shock events (>=20%): 39 -- C1 2018-01-31 (27%); C1 2018-04-30 (20%); C1g 2018-01-31 (35%); C5 2018-01-31 (29%); C5 2018-04-30 (34%); C5 2018-05-31 (20%); C5 2018-06-30 (23%); C5 2018-10-31 (35%); C5 2018-11-30 (30%); C7 2018-01-31 (31%); C7 2018-04-30 (38%); C7 2018-05-31 (29%); C7 2018-06-30 (30%); C7 2018-09-30 (30%); C7 2018-10-31 (44%); C7 2018-11-30 (31%); C2 2018-04-30 (31%); C2g 2018-04-30 (26%); C6 2018-05-31 (23%); C6 2018-06-30 (24%); C6 2018-10-31 (33%); C6 2018-11-30 (23%); C8 2018-05-31 (41%); C8 2018-06-30 (44%); C8 2018-08-31 (27%); C8 2018-09-30 (60%); C8 2018-10-31 (56%); C8 2018-11-30 (30%); C3g 2018-07-31 (48%); C9 2018-04-30 (32%); C9 2018-05-31 (37%); C9 2018-06-30 (34%); C9 2018-07-31 (29%); C9 2018-08-31 (44%); C9 2018-09-30 (49%); C9 2018-10-31 (40%); C9 2018-12-31 (22%); C4 2018-10-31 (41%); C4g 2018-10-31 (55%)
- Churn risk (accounts renewing in 2018): 6 at risk (≥20% churn prob): C3 23%, C5 32%, C6 32%, C7 38%, C8 35%, C9 38%

**Pricing & Margin**

- C1 (electricity): tariff £67.79-£77.97/MWh, net margin £9.69
- C1g (gas): tariff £22.59-£26.30/MWh, net margin £25.55
- C2 (electricity): tariff £73.42-£111.24/MWh, net margin £59.80
- C2g (gas): tariff £22.20-£28.87/MWh, net margin £38.59
- C3 (electricity): tariff £67.49-£69.10/MWh, net margin £11.81
- C3g (gas): tariff £16.39-£23.49/MWh, net margin £28.64
- C4 (electricity): tariff £57.26-£76.50/MWh, net margin £13.99
- C4g (gas): tariff £19.06-£28.58/MWh, net margin £44.82
- C5 (electricity): tariff £67.79-£77.97/MWh, net margin £30.98
- C6 (electricity): tariff £73.42-£111.24/MWh, net margin £55.56
- C7 (electricity): tariff £67.79-£77.97/MWh, net margin £30.32
- C8 (electricity): tariff £73.42-£111.24/MWh, net margin £65.07
- C9 (electricity): tariff £67.49-£69.10/MWh, net margin £34.09

**Portfolio Health**

- Capital cost ratio: 18.4% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.889, average bill shock 12.6%, bad debt provision £190.39, avg complaint probability 3.7%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £598.95 vs. naked (unhedged) net margin: £2,695.46
- hedging cost £2,096.51 vs. a fully unhedged book (actual net £598.95 vs. naked net £2,695.46)
  - C1: actual £15.62 vs. naked £102.35 -- hedging cost £86.72
  - C1g: actual £27.55 vs. naked £147.39 -- hedging cost £119.84
  - C2: actual £73.60 vs. naked £355.64 -- hedging cost £282.05
  - C2g: actual £44.54 vs. naked £99.07 -- hedging cost £54.54
  - C3: actual £15.75 vs. naked £33.63 -- hedging cost £17.87
  - C3g: actual £31.67 vs. naked £51.89 -- hedging cost £20.23
  - C4: actual £28.31 vs. naked £171.10 -- hedging cost £142.79
  - C4g: actual £51.13 vs. naked £259.71 -- hedging cost £208.58
  - C5: actual £70.28 vs. naked £384.93 -- hedging cost £314.64
  - C6: actual £61.39 vs. naked £333.15 -- hedging cost £271.76
  - C7: actual £51.98 vs. naked £319.15 -- hedging cost £267.17
  - C8: actual £92.99 vs. naked £406.73 -- hedging cost £313.74
  - C9: actual £34.14 vs. naked £30.72 -- hedging added £3.42

**Year narrative:** 2018 produced a net gain of £448.93 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 39 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £616.92 (gross £682.33, capital £65.42)
  - Electricity: gross £512.05, capital £59.79, net £452.26
  - Gas: gross £170.28, capital £5.63, net £164.65
- Treasury at year end: £31,328.32
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 0.90 (avg 0.90), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 0.90 (avg 0.90), C4 0.85 (avg 0.85), C4g 0.90 (avg 0.90), C5 0.85 (avg 0.85), C6 0.90 (avg 0.90), C7 0.85 (avg 0.85), C8 0.85 (avg 0.85), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C1g on 2019-12-31 period 1, net margin £-0.03

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 3 accounts
- Average CLV (Point-in-Time, year-end 2019): £-116.70
  - By billing account: C1 £-120.70, C2 £170.31, C3 £-103.49, C4 £-6.81, C5 £-291.82, C6 £-382.99, C7 £-76.13, C8 £-30.01, C9 £-208.68
- Bill shock events (>=20%): 38 -- C1 2019-04-30 (24%); C5 2019-01-31 (38%); C5 2019-02-28 (22%); C5 2019-06-30 (28%); C5 2019-10-31 (48%); C5 2019-11-30 (39%); C7 2019-01-31 (43%); C7 2019-02-28 (25%); C7 2019-05-31 (23%); C7 2019-06-30 (34%); C7 2019-10-31 (67%); C7 2019-11-30 (45%); C2 2019-04-30 (42%); C6 2019-02-28 (21%); C6 2019-04-30 (45%); C6 2019-06-30 (26%); C6 2019-09-30 (22%); C6 2019-10-31 (45%); C6 2019-11-30 (29%); C8 2019-01-31 (24%); C8 2019-02-28 (26%); C8 2019-04-30 (49%); C8 2019-06-30 (40%); C8 2019-07-31 (38%); C8 2019-09-30 (67%); C8 2019-10-31 (87%); C8 2019-11-30 (40%); C3 2019-04-30 (22%); C3g 2019-07-31 (29%); C9 2019-02-28 (25%); C9 2019-04-30 (25%); C9 2019-06-30 (37%); C9 2019-07-31 (42%); C9 2019-09-30 (56%); C9 2019-10-31 (74%); C9 2019-11-30 (40%); C4 2019-10-31 (29%); C4g 2019-10-31 (56%)
- Churn risk (accounts renewing in 2019): 5 at risk (≥20% churn prob): C5 35%, C6 32%, C7 35%, C8 32%, C9 32%

**Pricing & Margin**

- C1 (electricity): tariff £56.59-£77.97/MWh, net margin £15.54
- C1g (gas): tariff £15.70-£26.30/MWh, net margin £27.45
- C2 (electricity): tariff £77.43-£111.24/MWh, net margin £62.76
- C2g (gas): tariff £24.14-£28.87/MWh, net margin £55.13
- C3 (electricity): tariff £58.84-£67.49/MWh, net margin £20.69
- C3g (gas): tariff £16.11-£23.49/MWh, net margin £33.07
- C4 (electricity): tariff £51.35-£76.50/MWh, net margin £29.00
- C4g (gas): tariff £12.10-£28.58/MWh, net margin £49.01
- C5 (electricity): tariff £56.59-£77.97/MWh, net margin £69.54
- C6 (electricity): tariff £77.43-£111.24/MWh, net margin £78.08
- C7 (electricity): tariff £56.59-£77.97/MWh, net margin £51.62
- C8 (electricity): tariff £77.43-£111.24/MWh, net margin £90.67
- C9 (electricity): tariff £58.84-£67.49/MWh, net margin £34.36

**Portfolio Health**

- Capital cost ratio: 9.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.884, average bill shock 14.2%, bad debt provision £189.50, avg complaint probability 3.9%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £623.83 vs. naked (unhedged) net margin: £2,212.02
- hedging cost £1,588.19 vs. a fully unhedged book (actual net £623.83 vs. naked net £2,212.02)
  - C1: actual £16.05 vs. naked £49.84 -- hedging cost £33.79
  - C1g: actual £30.66 vs. naked £72.58 -- hedging cost £41.92
  - C2: actual £58.48 vs. naked £271.55 -- hedging cost £213.07
  - C2g: actual £56.94 vs. naked £186.65 -- hedging cost £129.71
  - C3: actual £23.81 vs. naked £89.95 -- hedging cost £66.14
  - C3g: actual £36.80 vs. naked £94.38 -- hedging cost £57.58
  - C4: actual £32.35 vs. naked £110.24 -- hedging cost £77.89
  - C4g: actual £49.74 vs. naked £76.99 -- hedging cost £27.25
  - C5: actual £63.20 vs. naked £153.31 -- hedging cost £90.11
  - C6: actual £91.19 vs. naked £412.22 -- hedging cost £321.03
  - C7: actual £50.45 vs. naked £150.17 -- hedging cost £99.72
  - C8: actual £81.02 vs. naked £342.81 -- hedging cost £261.79
  - C9: actual £33.12 vs. naked £201.32 -- hedging cost £168.20

**Year narrative:** 2019 produced a net gain of £616.92 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 38 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £473.74 (gross £591.74, capital £118.00)
  - Electricity: gross £445.35, capital £110.64, net £334.70
  - Gas: gross £146.39, capital £7.35, net £139.04
- Treasury at year end: £31,936.82
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 0.85 (avg 0.85), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C4 0.85 (avg 0.85), C4g 0.85 (avg 0.85), C5 0.85 (avg 0.85), C6 0.85 (avg 0.85), C7 0.85 (avg 0.85), C8 0.85 (avg 0.85), C9 0.90 (avg 0.90)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C5 on 2020-03-04 period 37, net margin £-0.98

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 7, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn) during year: C3
  - Renewals (retained): 8 accounts
- Average CLV (Point-in-Time, year-end 2020): £-95.28
  - By billing account: C1 £-107.66, C2 £156.27, C3 £-74.96, C4 £14.82, C5 £-277.17, C6 £-290.28, C7 £-64.59, C8 £-25.80, C9 £-188.11
- Bill shock events (>=20%): 34 -- C1 2020-01-31 (27%); C1 2020-04-30 (23%); C1g 2020-01-31 (40%); C5 2020-01-31 (27%); C5 2020-04-30 (31%); C5 2020-10-31 (42%); C5 2020-11-30 (21%); C5 2020-12-31 (29%); C7 2020-01-31 (28%); C7 2020-04-30 (35%); C7 2020-06-30 (27%); C7 2020-10-31 (60%); C7 2020-11-30 (22%); C7 2020-12-31 (36%); C2 2020-04-30 (37%); C2g 2020-04-30 (47%); C6 2020-04-30 (46%); C6 2020-09-30 (23%); C6 2020-10-31 (37%); C6 2020-12-31 (27%); C8 2020-04-30 (53%); C8 2020-05-31 (25%); C8 2020-06-30 (35%); C8 2020-09-30 (57%); C8 2020-10-31 (69%); C8 2020-12-31 (42%); C3 2020-04-30 (21%); C9 2020-04-30 (29%); C9 2020-05-31 (25%); C9 2020-06-30 (38%); C9 2020-07-31 (23%); C9 2020-09-30 (47%); C9 2020-10-31 (52%); C9 2020-12-31 (35%)
- Churn risk (accounts renewing in 2020): 7 at risk (≥20% churn prob): C1 23%, C4 20%, C5 32%, C6 38%, C7 35%, C8 38%, C9 41%

**Pricing & Margin**

- C1 (electricity): tariff £56.59-£72.32/MWh, net margin £15.72
- C1g (gas): tariff £15.70-£18.18/MWh, net margin £30.65
- C2 (electricity): tariff £57.53-£77.43/MWh, net margin £43.15
- C2g (gas): tariff £13.14-£24.14/MWh, net margin £41.65
- C3 (electricity): tariff £58.84/MWh, net margin £13.58
- C3g (gas): tariff £16.11/MWh, net margin £19.44
- C4 (electricity): tariff £51.35-£55.16/MWh, net margin £30.26
- C4g (gas): tariff £12.10-£12.67/MWh, net margin £47.31
- C5 (electricity): tariff £56.59-£72.32/MWh, net margin £60.60
- C6 (electricity): tariff £57.53-£77.43/MWh, net margin £49.62
- C7 (electricity): tariff £56.59-£72.32/MWh, net margin £48.97
- C8 (electricity): tariff £57.53-£77.43/MWh, net margin £51.88
- C9 (electricity): tariff £40.71-£58.84/MWh, net margin £20.92

**Portfolio Health**

- Capital cost ratio: 19.9% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 144, average clarity 0.883, average bill shock 12.9%, bad debt provision £124.90, avg complaint probability 3.7%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-246.25 vs. naked (unhedged) net margin: £-3,843.88
- hedging added £3,597.64 vs. a fully unhedged book (actual net £-246.25 vs. naked net £-3,843.88)
  - C1: actual £-25.49 vs. naked £-230.78 -- hedging added £205.29
  - C1g: actual £-23.27 vs. naked £-304.56 -- hedging added £281.29
  - C2: actual £27.89 vs. naked £77.45 -- hedging cost £49.56
  - C2g: actual £30.50 vs. naked £21.81 -- hedging added £8.69
  - C4: actual £-11.39 vs. naked £-183.25 -- hedging added £171.86
  - C4g: actual £-2.98 vs. naked £-285.42 -- hedging added £282.44
  - C5: actual £-152.32 vs. naked £-1,318.30 -- hedging added £1,165.98
  - C6: actual £0.41 vs. naked £-286.82 -- hedging added £287.23
  - C7: actual £-86.01 vs. naked £-789.03 -- hedging added £703.03
  - C8: actual £10.91 vs. naked £-109.17 -- hedging added £120.08
  - C9: actual £-14.49 vs. naked £-435.80 -- hedging added £421.31

**Year narrative:** 2020 produced a net gain of £473.74 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 34 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £-343.62 (gross £-147.67, capital £195.95)
  - Electricity: gross £-140.19, capital £187.87, net £-328.06
  - Gas: gross £-7.48, capital £8.08, net £-15.56
- Treasury at year end: £31,660.75
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.85 (avg 0.85), C2g 0.95 (avg 0.95), C4 0.95 (avg 0.95), C4g 0.95 (avg 0.95), C6 0.95 (avg 0.95), C7 0.95 (avg 0.95), C8 0.95 (avg 0.95), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 4
  - 2021-09-30: treasury £31,608.17, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2021-10-30: treasury £31,611.05, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2021-11-29: treasury £31,615.37, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2021-12-29: treasury £31,618.03, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.52
- Worst single period: C5 on 2021-01-08 period 39, net margin £-2.12

**Customer Book**

- Active accounts: 11 (C1, C1g, C2, C2g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 6, SME electricity: 2, gas (dual-fuel): 3
- New acquisitions this year: none
- Losses (churn) during year: C1, C5
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2021): £-164.27
  - By billing account: C1 £-171.04, C2 £70.91, C3 £-73.89, C4 £-71.90, C5 £-438.00, C6 £-335.26, C7 £-157.89, C8 £-88.91, C9 £-212.44
- Bill shock events (>=20%): 36 -- C1 2021-01-31 (26%); C1 2021-04-30 (22%); C5 2021-01-31 (35%); C5 2021-05-31 (24%); C5 2021-06-30 (34%); C5 2021-10-31 (33%); C5 2021-11-30 (55%); C7 2021-01-31 (42%); C7 2021-05-31 (29%); C7 2021-06-30 (47%); C7 2021-10-31 (56%); C7 2021-11-30 (60%); C2 2021-04-30 (73%); C2g 2021-04-30 (75%); C6 2021-04-30 (87%); C6 2021-06-30 (37%); C6 2021-10-31 (29%); C6 2021-11-30 (53%); C8 2021-02-28 (21%); C8 2021-04-30 (96%); C8 2021-05-31 (28%); C8 2021-06-30 (63%); C8 2021-09-30 (24%); C8 2021-10-31 (78%); C8 2021-11-30 (81%); C9 2021-02-28 (23%); C9 2021-05-31 (24%); C9 2021-06-30 (51%); C9 2021-07-31 (95%); C9 2021-08-31 (23%); C9 2021-09-30 (21%); C9 2021-10-31 (68%); C9 2021-11-30 (48%); C9 2021-12-31 (23%); C4 2021-10-31 (339%); C4g 2021-10-31 (352%)
- Churn risk (accounts renewing in 2021): 6 at risk (≥20% churn prob): C2 20%, C5 35%, C6 38%, C7 38%, C8 41%, C9 35%

**Pricing & Margin**

- C1 (electricity): tariff £72.32/MWh, net margin £-25.06 -- **net-negative**
- C1g (gas): tariff £18.18/MWh, net margin £-23.23 -- **net-negative**
- C2 (electricity): tariff £57.53-£120.87/MWh, net margin £-1.93 -- **net-negative**
- C2g (gas): tariff £13.14-£24.47/MWh, net margin £12.22
- C4 (electricity): tariff £55.16-£258.73/MWh, net margin £-5.73 -- **net-negative**
- C4g (gas): tariff £12.67-£62.80/MWh, net margin £-4.56 -- **net-negative**
- C5 (electricity): tariff £72.32/MWh, net margin £-148.61 -- **net-negative**
- C6 (electricity): tariff £57.53-£120.87/MWh, net margin £-47.55 -- **net-negative**
- C7 (electricity): tariff £72.32-£287.43/MWh, net margin £-86.46 -- **net-negative**
- C8 (electricity): tariff £57.53-£120.87/MWh, net margin £-11.98 -- **net-negative**
- C9 (electricity): tariff £40.71-£117.05/MWh, net margin £-0.73 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -132.7% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 132, average clarity 0.858, average bill shock 21.8%, bad debt provision £166.85, avg complaint probability 4.6%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £54.25 vs. naked (unhedged) net margin: £-6,521.21
- hedging added £6,575.46 vs. a fully unhedged book (actual net £54.25 vs. naked net £-6,521.21)
  - C2: actual £-22.66 vs. naked £-290.46 -- hedging added £267.80
  - C2g: actual £4.80 vs. naked £-552.00 -- hedging added £556.81
  - C4: actual £36.75 vs. naked £39.38 -- hedging cost £2.63
  - C4g: actual £7.71 vs. naked £-991.43 -- hedging added £999.15
  - C6: actual £-60.28 vs. naked £-2,428.03 -- hedging added £2,367.75
  - C7: actual £66.05 vs. naked £41.07 -- hedging added £24.98
  - C8: actual £-17.03 vs. naked £-1,097.25 -- hedging added £1,080.21
  - C9: actual £38.91 vs. naked £-1,242.48 -- hedging added £1,281.39

**Year narrative:** 2021 (flagged crisis year) produced a net loss of £-343.62 across 11 accounts. The risk committee intervened 4 time(s), raising hedge fractions in response to elevated VaR. 36 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £361.19 (gross £471.24, capital £110.05)
  - Electricity: gross £444.82, capital £105.40, net £339.43
  - Gas: gross £26.41, capital £4.65, net £21.76
- Treasury at year end: £31,842.22
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C4 1.00 (avg 1.00), C4g 1.00 (avg 1.00), C6 1.00 (avg 1.00), C7 1.00 (avg 1.00), C8 1.00 (avg 1.00), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 30
  - 2022-01-28: treasury £31,622.17, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-02-27: treasury £31,626.94, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-03-29: treasury £31,629.68, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-04-28: treasury £31,633.07, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-05-28: treasury £31,638.07, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-06-27: treasury £31,642.00, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-07-27: treasury £31,644.22, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-08-26: treasury £31,643.75, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-09-25: treasury £31,644.50, C2->0.95, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,899.00 / stressed £752.59) ratio 2.52
  - 2022-01-16: treasury £31,657.26, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-02-15: treasury £31,668.68, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-03-17: treasury £31,676.01, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-04-16: treasury £31,683.63, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-05-16: treasury £31,691.08, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-06-15: treasury £31,695.88, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-07-15: treasury £31,697.54, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-08-14: treasury £31,697.87, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-09-13: treasury £31,696.11, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-10-13: treasury £31,700.15, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-11-12: treasury £31,708.59, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-12-12: treasury £31,714.83, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-04-12: treasury £31,726.43, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-05-12: treasury £31,747.75, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-06-11: treasury £31,763.53, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-07-11: treasury £31,769.75, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-08-10: treasury £31,772.18, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-09-09: treasury £31,770.18, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-10-09: treasury £31,780.34, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-11-08: treasury £31,804.62, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2022-12-08: treasury £31,829.96, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.58
- Worst single period: C6 on 2022-01-24 period 34, net margin £-0.82

**Customer Book**

- Active accounts: 9 (C2, C2_2, C2g, C4, C4g, C6, C7, C8, C9)
  - Resi electricity: 6, SME electricity: 1, gas (dual-fuel): 2
- New acquisitions this year: C2_2
- Losses (churn) during year: C2
  - Renewals (retained): 5 accounts
- Average CLV (Point-in-Time, year-end 2022): £-151.76
  - By billing account: C1 £-176.61, C2 £23.82, C2_2 £48.13, C3 £-83.46, C4 £-104.60, C5 £-382.11, C6 £-362.25, C7 £-142.26, C8 £-114.46, C9 £-223.80
- Bill shock events (>=20%): 39 -- C7 2022-01-31 (329%); C7 2022-02-28 (26%); C7 2022-04-30 (21%); C7 2022-05-31 (35%); C7 2022-06-30 (26%); C7 2022-09-30 (31%); C7 2022-11-30 (58%); C7 2022-12-31 (53%); C6 2022-04-30 (121%); C6 2022-05-31 (24%); C6 2022-09-30 (27%); C6 2022-11-30 (45%); C6 2022-12-31 (34%); C8 2022-02-28 (22%); C8 2022-04-30 (114%); C8 2022-05-31 (40%); C8 2022-06-30 (34%); C8 2022-07-31 (21%); C8 2022-09-30 (83%); C8 2022-10-31 (20%); C8 2022-11-30 (67%); C8 2022-12-31 (58%); C9 2022-05-31 (31%); C9 2022-06-30 (29%); C9 2022-07-31 (44%); C9 2022-09-30 (49%); C9 2022-10-31 (33%); C9 2022-11-30 (41%); C9 2022-12-31 (54%); C4 2022-10-31 (64%); C4g 2022-10-31 (202%); C2_2 2022-04-30 (1698%); C2_2 2022-05-31 (40%); C2_2 2022-06-30 (34%); C2_2 2022-07-31 (21%); C2_2 2022-09-30 (84%); C2_2 2022-10-31 (20%); C2_2 2022-11-30 (68%); C2_2 2022-12-31 (59%)
- Churn risk (accounts renewing in 2022): 6 at risk (≥20% churn prob): C2 20%, C4 23%, C6 35%, C7 38%, C8 38%, C9 38%

**Pricing & Margin**

- C2 (electricity): tariff £120.87/MWh, net margin £-18.96 -- **net-negative**
- C2_2 (electricity): tariff £353.40/MWh, net margin £123.51
- C2g (gas): tariff £24.47/MWh, net margin £-3.70 -- **net-negative**
- C4 (electricity): tariff £258.73-£411.48/MWh, net margin £39.72
- C4g (gas): tariff £62.80-£196.77/MWh, net margin £25.46
- C6 (electricity): tariff £120.87-£353.40/MWh, net margin £49.28
- C7 (electricity): tariff £287.43-£329.46/MWh, net margin £68.92
- C8 (electricity): tariff £120.87-£353.40/MWh, net margin £30.48
- C9 (electricity): tariff £117.05-£220.84/MWh, net margin £46.47

**Portfolio Health**

- Capital cost ratio: 23.4% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 88, average clarity 0.801, average bill shock 47.8%, bad debt provision £373.96, avg complaint probability 5.9%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £712.91 vs. naked (unhedged) net margin: £8,880.54
- hedging cost £8,167.63 vs. a fully unhedged book (actual net £712.91 vs. naked net £8,880.54)
  - C2_2: actual £250.43 vs. naked £1,308.01 -- hedging cost £1,057.59
  - C4: actual £49.85 vs. naked £1,800.08 -- hedging cost £1,750.23
  - C4g: actual £96.22 vs. naked £2,961.18 -- hedging cost £2,864.96
  - C6: actual £115.92 vs. naked £-252.45 -- hedging added £368.37
  - C7: actual £74.70 vs. naked £2,169.04 -- hedging cost £2,094.34
  - C8: actual £71.13 vs. naked £903.27 -- hedging cost £832.14
  - C9: actual £54.65 vs. naked £-8.59 -- hedging added £63.24

**Year narrative:** 2022 (flagged crisis year) produced a net gain of £361.19 across 9 accounts. The risk committee intervened 30 time(s), raising hedge fractions in response to elevated VaR. 39 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £788.48 (gross £879.61, capital £91.13)
  - Electricity: gross £791.13, capital £85.32, net £705.80
  - Gas: gross £88.48, capital £5.81, net £82.67
- Treasury at year end: £32,560.32
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C4 0.90 (avg 0.90), C4g 0.90 (avg 0.90), C6 1.00 (avg 1.00), C7 0.90 (avg 0.90), C8 0.90 (avg 0.90), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 3
  - 2023-01-07: treasury £31,850.96, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2023-02-06: treasury £31,897.44, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
  - 2023-03-08: treasury £31,938.97, C2->0.95, C4->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,061.73 / stressed £791.33) ratio 2.61
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.61
- Worst single period: C4g on 2023-09-30 period 1, net margin £-1.25

**Customer Book**

- Active accounts: 7 (C2_2, C4, C4g, C6, C7, C8, C9)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 1
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 6 accounts
- Average CLV (Point-in-Time, year-end 2023): £-127.78
  - By billing account: C1 £-151.46, C2 £25.55, C2_2 £161.78, C3 £-66.39, C4 £-97.75, C5 £-407.88, C6 £-321.01, C7 £-156.66, C8 £-76.67, C9 £-187.33
- Bill shock events (>=20%): 29 -- C7 2023-05-31 (32%); C7 2023-06-30 (35%); C7 2023-10-31 (52%); C7 2023-11-30 (65%); C6 2023-04-30 (53%); C6 2023-05-31 (24%); C6 2023-06-30 (24%); C6 2023-10-31 (41%); C6 2023-11-30 (46%); C8 2023-04-30 (54%); C8 2023-05-31 (43%); C8 2023-06-30 (44%); C8 2023-10-31 (101%); C8 2023-11-30 (69%); C9 2023-02-28 (20%); C9 2023-04-30 (25%); C9 2023-05-31 (34%); C9 2023-06-30 (46%); C9 2023-07-31 (32%); C9 2023-09-30 (23%); C9 2023-10-31 (76%); C9 2023-11-30 (53%); C4 2023-10-31 (70%); C4g 2023-10-31 (81%); C2_2 2023-04-30 (54%); C2_2 2023-05-31 (43%); C2_2 2023-06-30 (44%); C2_2 2023-10-31 (102%); C2_2 2023-11-30 (69%)
- Churn risk (accounts renewing in 2023): 5 at risk (≥20% churn prob): C2_2 35%, C6 26%, C7 38%, C8 35%, C9 41%

**Pricing & Margin**

- C2_2 (electricity): tariff £204.90-£353.40/MWh, net margin £255.61
- C4 (electricity): tariff £112.80-£411.48/MWh, net margin £48.38
- C4g (gas): tariff £35.29-£196.77/MWh, net margin £82.67
- C6 (electricity): tariff £204.90-£353.40/MWh, net margin £151.65
- C7 (electricity): tariff £131.28-£329.46/MWh, net margin £72.31
- C8 (electricity): tariff £204.90-£353.40/MWh, net margin £112.53
- C9 (electricity): tariff £128.17-£220.84/MWh, net margin £65.33

**Portfolio Health**

- Capital cost ratio: 10.4% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 84, average clarity 0.808, average bill shock 21.3%, bad debt provision £410.52, avg complaint probability 5.3%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £847.04 vs. naked (unhedged) net margin: £2,077.56
- hedging cost £1,230.52 vs. a fully unhedged book (actual net £847.04 vs. naked net £2,077.56)
  - C2_2: actual £227.41 vs. naked £991.61 -- hedging cost £764.20
  - C4: actual £54.48 vs. naked £161.46 -- hedging cost £106.98
  - C4g: actual £58.93 vs. naked £-41.99 -- hedging added £100.92
  - C6: actual £169.47 vs. naked £-143.50 -- hedging added £312.97
  - C7: actual £96.33 vs. naked £242.33 -- hedging cost £146.00
  - C8: actual £162.03 vs. naked £691.39 -- hedging cost £529.36
  - C9: actual £78.40 vs. naked £176.27 -- hedging cost £97.86

**Year narrative:** 2023 produced a net gain of £788.48 across 7 accounts. The risk committee intervened 3 time(s), raising hedge fractions in response to elevated VaR. 29 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £523.05 (gross £674.48, capital £151.43)
  - Electricity: gross £613.45, capital £138.36, net £475.09
  - Gas: gross £61.03, capital £13.07, net £47.96
- Treasury at year end: £33,312.60
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.85 (avg 0.85), C7 0.85 (avg 0.85), C8 0.85 (avg 0.85), C9 0.90 (avg 0.90)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C8 on 2024-12-12 period 34, net margin £-0.14

**Customer Book**

- Active accounts: 7 (C2_2, C4, C4g, C6, C7, C8, C9)
  - Resi electricity: 5, SME electricity: 1, gas (dual-fuel): 1
- New acquisitions this year: none
- Losses (churn) during year: C6, C4
  - Renewals (retained): 4 accounts
- Average CLV (Point-in-Time, year-end 2024): £-99.96
  - By billing account: C1 £-133.91, C2 £21.89, C2_2 £161.85, C3 £-77.18, C4 £-51.58, C5 £-337.88, C6 £-259.32, C7 £-126.15, C8 £-32.70, C9 £-164.65
- Bill shock events (>=20%): 27 -- C7 2024-01-31 (51%); C7 2024-02-29 (26%); C7 2024-04-30 (21%); C7 2024-05-31 (36%); C7 2024-09-30 (33%); C7 2024-10-31 (35%); C7 2024-11-30 (46%); C8 2024-02-29 (23%); C8 2024-04-30 (60%); C8 2024-05-31 (51%); C8 2024-07-31 (29%); C8 2024-09-30 (78%); C8 2024-10-31 (38%); C8 2024-11-30 (62%); C9 2024-04-30 (22%); C9 2024-05-31 (50%); C9 2024-07-31 (40%); C9 2024-09-30 (56%); C9 2024-10-31 (24%); C9 2024-11-30 (48%); C2_2 2024-02-29 (23%); C2_2 2024-04-30 (60%); C2_2 2024-05-31 (51%); C2_2 2024-07-31 (29%); C2_2 2024-09-30 (79%); C2_2 2024-10-31 (38%); C2_2 2024-11-30 (62%)
- Churn risk (accounts renewing in 2024): 6 at risk (≥20% churn prob): C2_2 41%, C4 23%, C6 38%, C7 38%, C8 41%, C9 35%

**Pricing & Margin**

- C2_2 (electricity): tariff £102.60-£204.90/MWh, net margin £132.65
- C4 (electricity): tariff £112.80/MWh, net margin £42.47
- C4g (gas): tariff £35.29/MWh, net margin £47.96
- C6 (electricity): tariff £204.90/MWh, net margin £56.56
- C7 (electricity): tariff £128.48-£131.28/MWh, net margin £95.38
- C8 (electricity): tariff £102.60-£204.90/MWh, net margin £91.03
- C9 (electricity): tariff £99.91-£128.17/MWh, net margin £57.00

**Portfolio Health**

- Capital cost ratio: 22.5% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 69, average clarity 0.801, average bill shock 21.2%, bad debt provision £159.75, avg complaint probability 5.4%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £94.60 vs. naked (unhedged) net margin: £-796.16
- hedging added £890.75 vs. a fully unhedged book (actual net £94.60 vs. naked net £-796.16)
  - C2_2: actual £36.27 vs. naked £-88.08 -- hedging added £124.35
  - C7: actual £24.38 vs. naked £-78.79 -- hedging added £103.17
  - C8: actual £9.59 vs. naked £-303.83 -- hedging added £313.42
  - C9: actual £24.35 vs. naked £-325.47 -- hedging added £349.82

**Year narrative:** 2024 produced a net gain of £523.05 across 7 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 27 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £69.25 (gross £139.72, capital £70.47)
  - Electricity: gross £139.72, capital £70.47, net £69.25
- Treasury at year end: £33,348.88
- Hedge fraction at first renewal this year (avg across year's terms): C2_2 0.95 (avg 0.95), C8 0.95 (avg 0.95)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C8 on 2025-01-08 period 36, net margin £-1.66

**Customer Book**

- Active accounts: 4 (C2_2, C7, C8, C9)
  - Resi electricity: 4, SME electricity: 0, gas (dual-fuel): 0
- New acquisitions this year: none
- Losses (churn) during year: none
  - Renewals (retained): 2 accounts
- Average CLV (Point-in-Time, year-end 2025): £-97.56
  - By billing account: C1 £-125.43, C2 £23.75, C2_2 £132.25, C3 £-70.69, C4 £-54.49, C5 £-357.18, C6 £-230.20, C7 £-97.59, C8 £-35.23, C9 £-160.76
- Bill shock events (>=20%): 18 -- C7 2025-01-31 (23%); C7 2025-04-30 (37%); C7 2025-05-31 (22%); C7 2025-06-07 (80%); C8 2025-01-31 (39%); C8 2025-02-28 (24%); C8 2025-04-30 (25%); C8 2025-05-31 (38%); C8 2025-06-07 (73%); C9 2025-01-31 (22%); C9 2025-04-30 (26%); C9 2025-05-31 (34%); C9 2025-06-07 (71%); C2_2 2025-01-31 (40%); C2_2 2025-02-28 (24%); C2_2 2025-04-30 (25%); C2_2 2025-05-31 (39%); C2_2 2025-06-07 (73%)
- Churn risk (accounts renewing in 2025): 3 at risk (≥20% churn prob): C2_2 38%, C8 38%, C9 38%

**Pricing & Margin**

- C2_2 (electricity): tariff £102.60-£222.51/MWh, net margin £21.36
- C7 (electricity): tariff £128.48/MWh, net margin £27.30
- C8 (electricity): tariff £102.60-£222.51/MWh, net margin £9.73
- C9 (electricity): tariff £99.91/MWh, net margin £10.86

**Portfolio Health**

- Capital cost ratio: 50.4% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 24, average clarity 0.726, average bill shock 32.3%, bad debt provision £59.27, avg complaint probability 7.3%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £33.34 vs. naked (unhedged) net margin: £134.94
- hedging cost £101.60 vs. a fully unhedged book (actual net £33.34 vs. naked net £134.94)
  - C2_2: actual £19.03 vs. naked £129.21 -- hedging cost £110.19
  - C8: actual £14.31 vs. naked £5.72 -- hedging added £8.59

**Year narrative:** 2025 produced a net gain of £69.25 across 4 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 18 customer(s) experienced a bill shock of >=20%.
