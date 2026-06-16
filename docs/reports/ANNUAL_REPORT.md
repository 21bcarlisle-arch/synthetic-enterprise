# Annual Report — The Synthetic Enterprise

## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £29,846.19
- Final treasury: £34,295.80
  (£4,449.61 net change)
- Revenue: £132,448.73
- Gross margin: £5,912.20
- Capital costs: £1,462.59
- Net margin: £4,449.61
- Capital cost ratio: 24.7% of gross
- Net margin as % of revenue: 3.4%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 195
- Bills issued: 1434, average clarity 0.878,
  service quality score 0.919
- Enterprise value (CLV sum across 9 billing accounts): £-1,420.49
- Cost to serve (whole portfolio): £7,990.64, net margin after cost to serve: £-2,078.44
- Hedge effectiveness (whole window): hedging cost £2,212.11 vs. a fully unhedged book (actual net £4,449.61 vs. naked net £6,661.72)

- **2021** (crisis year): net margin £-355.59, 2 risk committee wake-up(s).
- **2022** (crisis year): net margin £499.09, 48 risk committee wake-up(s).

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

**Note:** the figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run: gross £5,912.20, capital £1,462.59, net £4,449.61. Old-model run: gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 24.7% under the new mandate vs. 41.0% under the old reactive model.
- **2021 net margin**: £-355.59 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 3.4%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run): £4,449.61
- Old reactive model (actual): £26,779.56
- Fully naked (this run's counterfactual): £6,661.72
- Fully naked (old run's counterfactual): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.
## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £2,212.11 vs. a fully unhedged book (actual net £4,449.61 vs. naked net £6,661.72)
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
| 2016 | £24.60 | £95.31 | £84.20 | £204.10 |
| 2017 | £84.33 | £183.61 | £124.12 | £392.07 |
| 2018 | £93.68 | £226.89 | £137.61 | £458.18 |
| 2019 | £130.92 | £290.51 | £164.65 | £586.09 |
| 2020 | £104.48 | £219.99 | £148.16 | £472.63 |
| 2021 | £-201.07 | £-140.38 | £-14.14 | £-355.59 |
| 2022 | £121.80 | £262.87 | £114.42 | £499.09 |
| 2023 | £252.92 | £496.00 | £243.70 | £992.62 |
| 2024 | £243.99 | £448.03 | £199.79 | £891.81 |
| 2025 | £121.76 | £109.99 | £76.86 | £308.61 |

## Customer Lifecycle Events

Not available in current run output (see REPORTING_BACKLOG.md)

## 2016

**Trading & Risk**

- Net margin: £204.10 (gross £395.05, capital £190.95)
  - Electricity: gross £304.53, capital £184.62, net £119.90
  - Gas: gross £90.52, capital £6.32, net £84.20
- Treasury at year end: £29,976.48
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.90), C1g 0.85 (avg 0.85), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 0.85 (avg 0.85), C4 0.85 (avg 0.85), C4g 0.85 (avg 0.85), C5 0.85 (avg 0.93), C6 0.85 (avg 0.85), C7 0.85 (avg 0.93), C8 0.85 (avg 0.85), C9 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 66
  - 2016-01-01: treasury £29,846.19, C1->1.00, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-01-31: treasury £29,847.61, C1->1.00, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-03-01: treasury £29,849.16, C1->1.00, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-03-31: treasury £29,850.51, C1->1.00, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-04-30: treasury £29,851.64, C1->1.00, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-05-30: treasury £29,852.89, C1->1.00, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-06-29: treasury £29,853.74, C1->1.00, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-07-29: treasury £29,854.76, C1->1.00, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-08-28: treasury £29,855.86, C1->1.00, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-09-27: treasury £29,856.78, C1->1.00, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-10-27: treasury £29,857.55, C1->1.00, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-11-26: treasury £29,857.13, C1->1.00, VaR (current £66.93 / stressed £20.56) ratio 3.25
  - 2016-01-18: treasury £29,891.13, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-02-17: treasury £29,897.62, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-03-18: treasury £29,904.53, C1->1.00, C5->1.00, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-05-17: treasury £29,914.70, C1->1.00, C5->1.00, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-06-16: treasury £29,916.45, C1->1.00, C5->1.00, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-07-16: treasury £29,917.26, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-08-15: treasury £29,917.87, C1->0.95, C5->0.95, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-09-14: treasury £29,917.35, C1->1.00, C5->1.00, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-10-14: treasury £29,917.69, C1->1.00, C5->1.00, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-11-13: treasury £29,915.08, C1->1.00, C5->1.00, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-12-13: treasury £29,914.56, C1->1.00, C5->1.00, VaR (current £664.48 / stressed £204.14) ratio 3.25
  - 2016-01-13: treasury £29,919.74, C1->1.00, C5->1.00, C7->1.00, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-02-12: treasury £29,925.69, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-03-13: treasury £29,932.15, C1->1.00, C5->1.00, C7->1.00, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-04-12: treasury £29,938.76, C1->1.00, C5->1.00, C7->1.00, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-05-12: treasury £29,942.57, C1->1.00, C5->1.00, C7->1.00, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-06-11: treasury £29,945.09, C1->1.00, C5->1.00, C7->1.00, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-07-11: treasury £29,945.94, C1->1.00, C5->1.00, C7->1.00, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-08-10: treasury £29,947.02, C1->1.00, C5->1.00, C7->1.00, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-09-09: treasury £29,947.70, C1->1.00, C5->1.00, C7->1.00, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-10-09: treasury £29,948.89, C1->0.95, C5->0.95, C7->0.95, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-12-08: treasury £29,950.59, C1->1.00, C5->1.00, C7->1.00, VaR (current £970.47 / stressed £298.15) ratio 3.25
  - 2016-04-08: treasury £29,954.66, C1->1.00, C5->1.00, C7->1.00, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-05-08: treasury £29,957.42, C1->1.00, C5->1.00, C7->1.00, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-06-07: treasury £29,960.37, C1->1.00, C5->1.00, C7->1.00, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-07-07: treasury £29,962.87, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-08-06: treasury £29,965.66, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-09-05: treasury £29,968.54, C1->1.00, C5->1.00, C7->1.00, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-10-05: treasury £29,971.26, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-12-04: treasury £29,974.22, C1->1.00, C5->1.00, C7->1.00, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-08-05: treasury £29,997.59, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2016-04-26: treasury £30,023.91, C1->1.00, C5->1.00, C7->1.00, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-05-26: treasury £30,026.69, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-08-24: treasury £30,024.78, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-09-23: treasury £30,022.88, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-10-23: treasury £30,022.21, C1->1.00, C5->1.00, C7->1.00, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-12-22: treasury £30,015.77, C1->1.00, C5->1.00, C7->1.00, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2016-07-20: treasury £30,026.40, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-08-19: treasury £30,026.87, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-09-18: treasury £30,026.81, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-10-18: treasury £30,027.83, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2016-07-16: treasury £30,039.02, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-08-15: treasury £30,040.22, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-10-14: treasury £30,041.98, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-11-13: treasury £30,041.97, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-12-13: treasury £30,041.94, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2016-07-03: treasury £30,072.08, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-08-02: treasury £30,072.91, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-09-01: treasury £30,073.73, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-10-01: treasury £30,074.53, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-11-30: treasury £30,072.14, C1->1.00, C5->1.00, C7->1.00, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-12-30: treasury £30,074.33, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2016-10-28: treasury £30,085.29, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2016-11-27: treasury £30,085.48, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 3.07
- Worst single period: C8 on 2016-11-08 period 40, net margin £-0.44

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £-157.83
- Highest CLV: C2 (£220.05); Lowest CLV: C5 (£-422.39)
- Bill shock events (>=20%): 23 -- C1 2016-04-30 (21%); C5 2016-04-30 (21%); C5 2016-05-31 (30%); C5 2016-06-30 (22%); C5 2016-10-31 (47%); C5 2016-11-30 (49%); C7 2016-04-30 (20%); C7 2016-05-31 (38%); C7 2016-06-30 (31%); C7 2016-10-31 (81%); C7 2016-11-30 (52%); C6 2016-05-31 (28%); C6 2016-06-30 (25%); C6 2016-10-31 (46%); C6 2016-11-30 (51%); C8 2016-05-31 (42%); C8 2016-06-30 (45%); C8 2016-09-30 (29%); C8 2016-10-31 (118%); C8 2016-11-30 (71%); C9 2016-09-30 (22%); C9 2016-10-31 (86%); C9 2016-11-30 (60%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £62.25-£94.12/MWh, net margin £11.92
- C1g (gas): tariff £16.55-£16.64/MWh, net margin £29.04
- C2 (electricity): tariff £59.02/MWh, net margin £22.64
- C2g (gas): tariff £18.07/MWh, net margin £30.30
- C3 (electricity): tariff £51.42/MWh, net margin £4.15
- C3g (gas): tariff £13.45/MWh, net margin £13.76
- C4 (electricity): tariff £56.07/MWh, net margin £4.39
- C4g (gas): tariff £14.32/MWh, net margin £11.09
- C5 (electricity): tariff £62.25-£94.12/MWh, net margin £29.95
- C6 (electricity): tariff £59.02/MWh, net margin £-5.36 -- **net-negative**
- C7 (electricity): tariff £62.25-£94.12/MWh, net margin £36.84
- C8 (electricity): tariff £59.02/MWh, net margin £12.77
- C9 (electricity): tariff £51.42/MWh, net margin £2.60
- Cost to serve per customer (whole-run total, average £614.66, range £88.06-£1,355.82):
  - C1: cost to serve £612.43, net margin after cost to serve £-430.59 -- **net-negative**
  - C1g: cost to serve £103.25, net margin after cost to serve £171.33
  - C2: cost to serve £676.87, net margin after cost to serve £-30.15 -- **net-negative**
  - C2g: cost to serve £121.48, net margin after cost to serve £333.75
  - C3: cost to serve £567.98, net margin after cost to serve £-398.27 -- **net-negative**
  - C3g: cost to serve £88.06, net margin after cost to serve £191.96
  - C4: cost to serve £642.68, net margin after cost to serve £-317.96 -- **net-negative**
  - C4g: cost to serve £189.40, net margin after cost to serve £237.83
  - C5: cost to serve £1,355.82, net margin after cost to serve £-620.85 -- **net-negative**
  - C6: cost to serve £1,325.34, net margin after cost to serve £-520.06 -- **net-negative**
  - C7: cost to serve £831.90, net margin after cost to serve £-274.53 -- **net-negative**
  - C8: cost to serve £779.32, net margin after cost to serve £-83.19 -- **net-negative**
  - C9: cost to serve £696.10, net margin after cost to serve £-337.72 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 48.3% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 108, average clarity 0.888, average bill shock 14.6%, bad debt provision £98.25, avg complaint probability 3.7%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £432.50 vs. naked (unhedged) net margin: £480.69
- hedging cost £48.19 vs. a fully unhedged book (actual net £432.50 vs. naked net £480.69)
  - C1: actual £29.16 vs. naked £141.08 -- hedging cost £111.92
  - C1g: actual £51.31 vs. naked £45.90 -- hedging added £5.41
  - C2: actual £29.42 vs. naked £87.21 -- hedging cost £57.79
  - C2g: actual £37.97 vs. naked £66.51 -- hedging cost £28.54
  - C3: actual £8.97 vs. naked £-6.29 -- hedging added £15.27
  - C3g: actual £24.44 vs. naked £-6.81 -- hedging added £31.25
  - C4: actual £21.50 vs. naked £35.86 -- hedging cost £14.36
  - C4g: actual £38.18 vs. naked £-13.49 -- hedging added £51.67
  - C5: actual £86.37 vs. naked £226.37 -- hedging cost £140.00
  - C6: actual £-3.82 vs. naked £-317.20 -- hedging added £313.38
  - C7: actual £76.52 vs. naked £368.08 -- hedging cost £291.56
  - C8: actual £21.02 vs. naked £-43.79 -- hedging added £64.81
  - C9: actual £11.44 vs. naked £-102.73 -- hedging added £114.17

**Year narrative:** 2016 produced a net gain of £204.10 across 13 accounts. The risk committee intervened 66 time(s), raising hedge fractions in response to elevated VaR. 23 customer(s) experienced a bill shock of >=20%.

## 2017

**Trading & Risk**

- Net margin: £392.07 (gross £487.42, capital £95.35)
  - Electricity: gross £353.34, capital £85.39, net £267.94
  - Gas: gross £134.08, capital £9.96, net £124.12
- Treasury at year end: £30,309.89
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 0.95 (avg 0.95), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.95 (avg 0.95), C3g 0.95 (avg 0.95), C4 0.85 (avg 0.85), C4g 0.95 (avg 0.95), C5 0.90 (avg 0.90), C6 0.95 (avg 0.95), C7 0.90 (avg 0.90), C8 0.95 (avg 0.95), C9 0.95 (avg 0.95)
- Risk committee (Context Handshake) interventions: 34
  - 2017-01-03: treasury £29,976.71, C1->1.00, C5->1.00, C7->1.00, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2017-03-04: treasury £29,980.65, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,028.87 / stressed £322.47) ratio 3.19
  - 2017-01-21: treasury £30,015.61, C1->1.00, C5->1.00, C7->1.00, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2017-02-20: treasury £30,014.18, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2017-03-22: treasury £30,016.97, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,779.68 / stressed £635.16) ratio 2.80
  - 2017-01-16: treasury £30,031.28, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2017-03-17: treasury £30,036.96, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,977.06 / stressed £717.36) ratio 2.76
  - 2017-01-12: treasury £30,042.81, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-02-11: treasury £30,042.97, C1->1.00, C5->1.00, C7->1.00, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-04-12: treasury £30,045.35, C1->1.00, C5->1.00, C7->1.00, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-05-12: treasury £30,046.17, C1->1.00, C5->1.00, C7->1.00, VaR (current £2,018.13 / stressed £736.64) ratio 2.74
  - 2017-01-29: treasury £30,074.40, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-02-28: treasury £30,076.28, C1->1.00, C5->1.00, C7->1.00, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-05-29: treasury £30,082.07, C1->1.00, C5->1.00, C7->1.00, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-06-28: treasury £30,083.17, C1->1.00, C5->1.00, C7->1.00, VaR (current £2,176.93 / stressed £811.14) ratio 2.68
  - 2017-02-25: treasury £30,090.49, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-03-27: treasury £30,092.79, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-04-26: treasury £30,095.20, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-05-26: treasury £30,096.46, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-06-25: treasury £30,098.61, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-07-25: treasury £30,100.82, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-08-24: treasury £30,102.83, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,252.15 / stressed £847.39) ratio 2.66
  - 2017-01-15: treasury £30,143.58, C5->1.00, C7->1.00, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-02-14: treasury £30,145.10, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-03-16: treasury £30,146.87, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-04-15: treasury £30,148.45, C5->1.00, C7->1.00, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-05-15: treasury £30,149.76, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-06-14: treasury £30,150.94, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-07-14: treasury £30,152.20, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-08-13: treasury £30,153.45, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-09-12: treasury £30,154.69, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-10-12: treasury £30,155.98, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-11-11: treasury £30,157.51, C5->0.95, C7->0.95, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
  - 2017-12-11: treasury £30,159.10, C5->1.00, C7->1.00, VaR (current £2,210.07 / stressed £837.30) ratio 2.64
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.71
- Worst single period: C9 on 2017-05-17 period 34, net margin £-0.17

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £-157.83
- Highest CLV: C2 (£220.05); Lowest CLV: C5 (£-422.39)
- Bill shock events (>=20%): 32 -- C1 2017-01-31 (49%); C1 2017-04-30 (21%); C5 2017-01-31 (73%); C5 2017-02-28 (23%); C5 2017-05-31 (22%); C5 2017-06-30 (23%); C5 2017-11-30 (62%); C7 2017-01-31 (82%); C7 2017-02-28 (28%); C7 2017-05-31 (31%); C7 2017-06-30 (31%); C7 2017-09-30 (28%); C7 2017-10-31 (20%); C7 2017-11-30 (76%); C6 2017-05-31 (24%); C6 2017-06-30 (21%); C6 2017-11-30 (55%); C8 2017-05-31 (42%); C8 2017-06-30 (38%); C8 2017-09-30 (52%); C8 2017-10-31 (22%); C8 2017-11-30 (89%); C8 2017-12-31 (23%); C3 2017-07-31 (39%); C3g 2017-07-31 (26%); C9 2017-05-31 (35%); C9 2017-06-30 (27%); C9 2017-07-31 (24%); C9 2017-09-30 (33%); C9 2017-10-31 (22%); C9 2017-11-30 (74%); C4g 2017-10-31 (38%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £67.79-£94.12/MWh, net margin £17.05
- C1g (gas): tariff £16.55-£22.59/MWh, net margin £22.26
- C2 (electricity): tariff £59.02-£73.42/MWh, net margin £37.98
- C2g (gas): tariff £18.07-£22.20/MWh, net margin £38.20
- C3 (electricity): tariff £51.42-£69.10/MWh, net margin £12.17
- C3g (gas): tariff £13.45-£16.39/MWh, net margin £24.92
- C4 (electricity): tariff £56.07-£57.26/MWh, net margin £21.85
- C4g (gas): tariff £14.32-£19.06/MWh, net margin £38.75
- C5 (electricity): tariff £67.79-£94.12/MWh, net margin £55.11
- C6 (electricity): tariff £59.02-£73.42/MWh, net margin £29.22
- C7 (electricity): tariff £67.79-£94.12/MWh, net margin £39.12
- C8 (electricity): tariff £59.02-£73.42/MWh, net margin £30.53
- C9 (electricity): tariff £51.42-£69.10/MWh, net margin £24.91
- Cost to serve per customer (whole-run total, average £614.66, range £88.06-£1,355.82):
  - C1: cost to serve £612.43, net margin after cost to serve £-430.59 -- **net-negative**
  - C1g: cost to serve £103.25, net margin after cost to serve £171.33
  - C2: cost to serve £676.87, net margin after cost to serve £-30.15 -- **net-negative**
  - C2g: cost to serve £121.48, net margin after cost to serve £333.75
  - C3: cost to serve £567.98, net margin after cost to serve £-398.27 -- **net-negative**
  - C3g: cost to serve £88.06, net margin after cost to serve £191.96
  - C4: cost to serve £642.68, net margin after cost to serve £-317.96 -- **net-negative**
  - C4g: cost to serve £189.40, net margin after cost to serve £237.83
  - C5: cost to serve £1,355.82, net margin after cost to serve £-620.85 -- **net-negative**
  - C6: cost to serve £1,325.34, net margin after cost to serve £-520.06 -- **net-negative**
  - C7: cost to serve £831.90, net margin after cost to serve £-274.53 -- **net-negative**
  - C8: cost to serve £779.32, net margin after cost to serve £-83.19 -- **net-negative**
  - C9: cost to serve £696.10, net margin after cost to serve £-337.72 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 19.6% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.886, average bill shock 13.3%, bad debt provision £170.76, avg complaint probability 3.8%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £391.34 vs. naked (unhedged) net margin: £-103.28
- hedging added £494.61 vs. a fully unhedged book (actual net £391.34 vs. naked net £-103.28)
  - C1: actual £9.53 vs. naked £3.78 -- hedging added £5.75
  - C1g: actual £25.47 vs. naked £-3.82 -- hedging added £29.29
  - C2: actual £38.72 vs. naked £142.12 -- hedging cost £103.40
  - C2g: actual £37.64 vs. naked £60.01 -- hedging cost £22.37
  - C3: actual £13.86 vs. naked £37.07 -- hedging cost £23.21
  - C3g: actual £26.92 vs. naked £-40.23 -- hedging added £67.15
  - C4: actual £12.46 vs. naked £-24.96 -- hedging added £37.43
  - C4g: actual £43.58 vs. naked £-51.34 -- hedging added £94.92
  - C5: actual £36.59 vs. naked £-94.10 -- hedging added £130.69
  - C6: actual £42.79 vs. naked £-199.22 -- hedging added £242.01
  - C7: actual £31.74 vs. naked £-7.50 -- hedging added £39.24
  - C8: actual £36.74 vs. naked £62.86 -- hedging cost £26.12
  - C9: actual £35.30 vs. naked £12.06 -- hedging added £23.24

**Year narrative:** 2017 produced a net gain of £392.07 across 13 accounts. The risk committee intervened 34 time(s), raising hedge fractions in response to elevated VaR. 32 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £458.18 (gross £544.37, capital £86.19)
  - Electricity: gross £399.60, capital £79.03, net £320.57
  - Gas: gross £144.77, capital £7.16, net £137.61
- Treasury at year end: £30,722.31
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.95 (avg 0.95), C1g 1.00 (avg 1.00), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 1.00 (avg 1.00), C4 0.95 (avg 0.95), C4g 1.00 (avg 1.00), C5 1.00 (avg 1.00), C6 1.00 (avg 1.00), C7 1.00 (avg 1.00), C8 0.85 (avg 0.85), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C5 on 2018-03-01 period 34, net margin £-0.18

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £-157.83
- Highest CLV: C2 (£220.05); Lowest CLV: C5 (£-422.39)
- Bill shock events (>=20%): 39 -- C1 2018-01-31 (27%); C1 2018-04-30 (20%); C1g 2018-01-31 (35%); C5 2018-01-31 (29%); C5 2018-04-30 (34%); C5 2018-05-31 (20%); C5 2018-06-30 (23%); C5 2018-10-31 (35%); C5 2018-11-30 (30%); C7 2018-01-31 (31%); C7 2018-04-30 (38%); C7 2018-05-31 (29%); C7 2018-06-30 (30%); C7 2018-09-30 (30%); C7 2018-10-31 (44%); C7 2018-11-30 (31%); C2 2018-04-30 (31%); C2g 2018-04-30 (26%); C6 2018-05-31 (23%); C6 2018-06-30 (24%); C6 2018-10-31 (33%); C6 2018-11-30 (23%); C8 2018-05-31 (41%); C8 2018-06-30 (44%); C8 2018-08-31 (27%); C8 2018-09-30 (60%); C8 2018-10-31 (56%); C8 2018-11-30 (30%); C3g 2018-07-31 (48%); C9 2018-04-30 (32%); C9 2018-05-31 (37%); C9 2018-06-30 (34%); C9 2018-07-31 (29%); C9 2018-08-31 (44%); C9 2018-09-30 (49%); C9 2018-10-31 (40%); C9 2018-12-31 (22%); C4 2018-10-31 (41%); C4g 2018-10-31 (55%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £67.79-£77.97/MWh, net margin £9.69
- C1g (gas): tariff £22.59-£26.30/MWh, net margin £25.55
- C2 (electricity): tariff £73.42-£111.24/MWh, net margin £59.80
- C2g (gas): tariff £22.20-£28.87/MWh, net margin £38.59
- C3 (electricity): tariff £67.49-£69.10/MWh, net margin £11.81
- C3g (gas): tariff £16.39-£23.49/MWh, net margin £28.64
- C4 (electricity): tariff £57.26-£76.50/MWh, net margin £13.99
- C4g (gas): tariff £19.06-£28.58/MWh, net margin £44.82
- C5 (electricity): tariff £67.79-£77.97/MWh, net margin £38.11
- C6 (electricity): tariff £73.42-£111.24/MWh, net margin £55.56
- C7 (electricity): tariff £67.79-£77.97/MWh, net margin £32.44
- C8 (electricity): tariff £73.42-£111.24/MWh, net margin £65.07
- C9 (electricity): tariff £67.49-£69.10/MWh, net margin £34.09
- Cost to serve per customer (whole-run total, average £614.66, range £88.06-£1,355.82):
  - C1: cost to serve £612.43, net margin after cost to serve £-430.59 -- **net-negative**
  - C1g: cost to serve £103.25, net margin after cost to serve £171.33
  - C2: cost to serve £676.87, net margin after cost to serve £-30.15 -- **net-negative**
  - C2g: cost to serve £121.48, net margin after cost to serve £333.75
  - C3: cost to serve £567.98, net margin after cost to serve £-398.27 -- **net-negative**
  - C3g: cost to serve £88.06, net margin after cost to serve £191.96
  - C4: cost to serve £642.68, net margin after cost to serve £-317.96 -- **net-negative**
  - C4g: cost to serve £189.40, net margin after cost to serve £237.83
  - C5: cost to serve £1,355.82, net margin after cost to serve £-620.85 -- **net-negative**
  - C6: cost to serve £1,325.34, net margin after cost to serve £-520.06 -- **net-negative**
  - C7: cost to serve £831.90, net margin after cost to serve £-274.53 -- **net-negative**
  - C8: cost to serve £779.32, net margin after cost to serve £-83.19 -- **net-negative**
  - C9: cost to serve £696.10, net margin after cost to serve £-337.72 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 15.8% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.889, average bill shock 12.6%, bad debt provision £190.39, avg complaint probability 3.7%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £568.33 vs. naked (unhedged) net margin: £2,695.46
- hedging cost £2,127.14 vs. a fully unhedged book (actual net £568.33 vs. naked net £2,695.46)
  - C1: actual £15.62 vs. naked £102.35 -- hedging cost £86.72
  - C1g: actual £27.55 vs. naked £147.39 -- hedging cost £119.84
  - C2: actual £73.60 vs. naked £355.64 -- hedging cost £282.05
  - C2g: actual £44.54 vs. naked £99.07 -- hedging cost £54.54
  - C3: actual £15.75 vs. naked £33.63 -- hedging cost £17.87
  - C3g: actual £31.67 vs. naked £51.89 -- hedging cost £20.23
  - C4: actual £28.31 vs. naked £171.10 -- hedging cost £142.79
  - C4g: actual £51.13 vs. naked £259.71 -- hedging cost £208.58
  - C5: actual £53.72 vs. naked £384.93 -- hedging cost £331.20
  - C6: actual £61.39 vs. naked £333.15 -- hedging cost £271.76
  - C7: actual £37.92 vs. naked £319.15 -- hedging cost £281.23
  - C8: actual £92.99 vs. naked £406.73 -- hedging cost £313.74
  - C9: actual £34.14 vs. naked £30.72 -- hedging added £3.42

**Year narrative:** 2018 produced a net gain of £458.18 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 39 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £586.09 (gross £638.38, capital £52.29)
  - Electricity: gross £468.10, capital £46.66, net £421.44
  - Gas: gross £170.28, capital £5.63, net £164.65
- Treasury at year end: £31,279.80
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 0.90 (avg 0.90), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 0.90 (avg 0.90), C4 0.85 (avg 0.85), C4g 0.90 (avg 0.90), C5 0.90 (avg 0.90), C6 0.90 (avg 0.90), C7 0.90 (avg 0.90), C8 0.85 (avg 0.85), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C1g on 2019-12-31 period 1, net margin £-0.03

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £-157.83
- Highest CLV: C2 (£220.05); Lowest CLV: C5 (£-422.39)
- Bill shock events (>=20%): 38 -- C1 2019-04-30 (24%); C5 2019-01-31 (38%); C5 2019-02-28 (22%); C5 2019-06-30 (28%); C5 2019-10-31 (48%); C5 2019-11-30 (39%); C7 2019-01-31 (43%); C7 2019-02-28 (25%); C7 2019-05-31 (23%); C7 2019-06-30 (34%); C7 2019-10-31 (67%); C7 2019-11-30 (45%); C2 2019-04-30 (42%); C6 2019-02-28 (21%); C6 2019-04-30 (45%); C6 2019-06-30 (26%); C6 2019-09-30 (22%); C6 2019-10-31 (45%); C6 2019-11-30 (29%); C8 2019-01-31 (24%); C8 2019-02-28 (26%); C8 2019-04-30 (49%); C8 2019-06-30 (40%); C8 2019-07-31 (38%); C8 2019-09-30 (67%); C8 2019-10-31 (87%); C8 2019-11-30 (40%); C3 2019-04-30 (22%); C3g 2019-07-31 (29%); C9 2019-02-28 (25%); C9 2019-04-30 (25%); C9 2019-06-30 (37%); C9 2019-07-31 (42%); C9 2019-09-30 (56%); C9 2019-10-31 (74%); C9 2019-11-30 (40%); C4 2019-10-31 (29%); C4g 2019-10-31 (56%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £56.59-£77.97/MWh, net margin £15.54
- C1g (gas): tariff £15.70-£26.30/MWh, net margin £27.45
- C2 (electricity): tariff £77.43-£111.24/MWh, net margin £62.76
- C2g (gas): tariff £24.14-£28.87/MWh, net margin £55.13
- C3 (electricity): tariff £58.84-£67.49/MWh, net margin £20.69
- C3g (gas): tariff £16.11-£23.49/MWh, net margin £33.07
- C4 (electricity): tariff £51.35-£76.50/MWh, net margin £29.00
- C4g (gas): tariff £12.10-£28.58/MWh, net margin £49.01
- C5 (electricity): tariff £56.59-£77.97/MWh, net margin £52.84
- C6 (electricity): tariff £77.43-£111.24/MWh, net margin £78.08
- C7 (electricity): tariff £56.59-£77.97/MWh, net margin £37.50
- C8 (electricity): tariff £77.43-£111.24/MWh, net margin £90.67
- C9 (electricity): tariff £58.84-£67.49/MWh, net margin £34.36
- Cost to serve per customer (whole-run total, average £614.66, range £88.06-£1,355.82):
  - C1: cost to serve £612.43, net margin after cost to serve £-430.59 -- **net-negative**
  - C1g: cost to serve £103.25, net margin after cost to serve £171.33
  - C2: cost to serve £676.87, net margin after cost to serve £-30.15 -- **net-negative**
  - C2g: cost to serve £121.48, net margin after cost to serve £333.75
  - C3: cost to serve £567.98, net margin after cost to serve £-398.27 -- **net-negative**
  - C3g: cost to serve £88.06, net margin after cost to serve £191.96
  - C4: cost to serve £642.68, net margin after cost to serve £-317.96 -- **net-negative**
  - C4g: cost to serve £189.40, net margin after cost to serve £237.83
  - C5: cost to serve £1,355.82, net margin after cost to serve £-620.85 -- **net-negative**
  - C6: cost to serve £1,325.34, net margin after cost to serve £-520.06 -- **net-negative**
  - C7: cost to serve £831.90, net margin after cost to serve £-274.53 -- **net-negative**
  - C8: cost to serve £779.32, net margin after cost to serve £-83.19 -- **net-negative**
  - C9: cost to serve £696.10, net margin after cost to serve £-337.72 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 8.2% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.884, average bill shock 14.2%, bad debt provision £189.50, avg complaint probability 3.9%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £612.66 vs. naked (unhedged) net margin: £2,212.02
- hedging cost £1,599.36 vs. a fully unhedged book (actual net £612.66 vs. naked net £2,212.02)
  - C1: actual £16.05 vs. naked £49.84 -- hedging cost £33.79
  - C1g: actual £30.66 vs. naked £72.58 -- hedging cost £41.92
  - C2: actual £58.48 vs. naked £271.55 -- hedging cost £213.07
  - C2g: actual £56.94 vs. naked £186.65 -- hedging cost £129.71
  - C3: actual £23.81 vs. naked £89.95 -- hedging cost £66.14
  - C3g: actual £36.80 vs. naked £94.38 -- hedging cost £57.58
  - C4: actual £32.35 vs. naked £110.24 -- hedging cost £77.89
  - C4g: actual £49.74 vs. naked £76.99 -- hedging cost £27.25
  - C5: actual £57.90 vs. naked £153.31 -- hedging cost £95.41
  - C6: actual £91.19 vs. naked £412.22 -- hedging cost £321.03
  - C7: actual £44.59 vs. naked £150.17 -- hedging cost £105.59
  - C8: actual £81.02 vs. naked £342.81 -- hedging cost £261.79
  - C9: actual £33.12 vs. naked £201.32 -- hedging cost £168.20

**Year narrative:** 2019 produced a net gain of £586.09 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 38 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £472.63 (gross £583.74, capital £111.11)
  - Electricity: gross £427.65, capital £103.18, net £324.47
  - Gas: gross £156.09, capital £7.93, net £148.16
- Treasury at year end: £31,877.13
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 0.85 (avg 0.85), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 0.85 (avg 0.85), C4 0.85 (avg 0.85), C4g 0.85 (avg 0.85), C5 0.85 (avg 0.85), C6 0.85 (avg 0.85), C7 0.85 (avg 0.85), C8 0.85 (avg 0.85), C9 0.90 (avg 0.90)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C8 on 2020-03-04 period 37, net margin £-0.92

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £-157.83
- Highest CLV: C2 (£220.05); Lowest CLV: C5 (£-422.39)
- Bill shock events (>=20%): 36 -- C1 2020-01-31 (27%); C1 2020-04-30 (23%); C1g 2020-01-31 (40%); C5 2020-01-31 (27%); C5 2020-04-30 (31%); C5 2020-10-31 (42%); C5 2020-11-30 (21%); C5 2020-12-31 (29%); C7 2020-01-31 (28%); C7 2020-04-30 (35%); C7 2020-06-30 (27%); C7 2020-10-31 (60%); C7 2020-11-30 (22%); C7 2020-12-31 (36%); C2 2020-04-30 (37%); C2g 2020-04-30 (47%); C6 2020-04-30 (46%); C6 2020-09-30 (23%); C6 2020-10-31 (37%); C6 2020-12-31 (27%); C8 2020-04-30 (53%); C8 2020-05-31 (25%); C8 2020-06-30 (35%); C8 2020-09-30 (57%); C8 2020-10-31 (69%); C8 2020-12-31 (42%); C3 2020-04-30 (21%); C3 2020-07-31 (28%); C3g 2020-07-31 (49%); C9 2020-04-30 (29%); C9 2020-05-31 (25%); C9 2020-06-30 (38%); C9 2020-07-31 (23%); C9 2020-09-30 (47%); C9 2020-10-31 (52%); C9 2020-12-31 (35%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £56.59-£72.32/MWh, net margin £15.72
- C1g (gas): tariff £15.70-£18.18/MWh, net margin £30.65
- C2 (electricity): tariff £57.53-£77.43/MWh, net margin £43.15
- C2g (gas): tariff £13.14-£24.14/MWh, net margin £41.65
- C3 (electricity): tariff £40.71-£58.84/MWh, net margin £15.16
- C3g (gas): tariff £7.79-£16.11/MWh, net margin £28.56
- C4 (electricity): tariff £51.35-£55.16/MWh, net margin £30.26
- C4g (gas): tariff £12.10-£12.67/MWh, net margin £47.31
- C5 (electricity): tariff £56.59-£72.32/MWh, net margin £54.86
- C6 (electricity): tariff £57.53-£77.43/MWh, net margin £49.62
- C7 (electricity): tariff £56.59-£72.32/MWh, net margin £42.89
- C8 (electricity): tariff £57.53-£77.43/MWh, net margin £51.88
- C9 (electricity): tariff £40.71-£58.84/MWh, net margin £20.92
- Cost to serve per customer (whole-run total, average £614.66, range £88.06-£1,355.82):
  - C1: cost to serve £612.43, net margin after cost to serve £-430.59 -- **net-negative**
  - C1g: cost to serve £103.25, net margin after cost to serve £171.33
  - C2: cost to serve £676.87, net margin after cost to serve £-30.15 -- **net-negative**
  - C2g: cost to serve £121.48, net margin after cost to serve £333.75
  - C3: cost to serve £567.98, net margin after cost to serve £-398.27 -- **net-negative**
  - C3g: cost to serve £88.06, net margin after cost to serve £191.96
  - C4: cost to serve £642.68, net margin after cost to serve £-317.96 -- **net-negative**
  - C4g: cost to serve £189.40, net margin after cost to serve £237.83
  - C5: cost to serve £1,355.82, net margin after cost to serve £-620.85 -- **net-negative**
  - C6: cost to serve £1,325.34, net margin after cost to serve £-520.06 -- **net-negative**
  - C7: cost to serve £831.90, net margin after cost to serve £-274.53 -- **net-negative**
  - C8: cost to serve £779.32, net margin after cost to serve £-83.19 -- **net-negative**
  - C9: cost to serve £696.10, net margin after cost to serve £-337.72 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 19.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.887, average bill shock 12.7%, bad debt provision £133.31, avg complaint probability 3.7%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £-244.40 vs. naked (unhedged) net margin: £-4,058.91
- hedging added £3,814.51 vs. a fully unhedged book (actual net £-244.40 vs. naked net £-4,058.91)
  - C1: actual £-25.49 vs. naked £-230.78 -- hedging added £205.29
  - C1g: actual £-23.27 vs. naked £-304.56 -- hedging added £281.29
  - C2: actual £27.89 vs. naked £77.45 -- hedging cost £49.56
  - C2g: actual £30.50 vs. naked £21.81 -- hedging added £8.69
  - C3: actual £-5.70 vs. naked £-101.10 -- hedging added £95.39
  - C3g: actual £7.55 vs. naked £-113.93 -- hedging added £121.48
  - C4: actual £-11.39 vs. naked £-183.25 -- hedging added £171.86
  - C4g: actual £-2.98 vs. naked £-285.42 -- hedging added £282.44
  - C5: actual £-152.32 vs. naked £-1,318.30 -- hedging added £1,165.98
  - C6: actual £0.41 vs. naked £-286.82 -- hedging added £287.23
  - C7: actual £-86.01 vs. naked £-789.03 -- hedging added £703.03
  - C8: actual £10.91 vs. naked £-109.17 -- hedging added £120.08
  - C9: actual £-14.49 vs. naked £-435.80 -- hedging added £421.31

**Year narrative:** 2020 produced a net gain of £472.63 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 36 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £-355.59 (gross £-146.88, capital £208.71)
  - Electricity: gross £-142.82, capital £198.63, net £-341.45
  - Gas: gross £-4.06, capital £10.08, net £-14.14
- Treasury at year end: £31,602.91
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.95 (avg 0.95), C1g 0.95 (avg 0.95), C2 0.85 (avg 0.85), C2g 0.95 (avg 0.95), C3 0.95 (avg 0.95), C3g 0.95 (avg 0.95), C4 0.95 (avg 0.95), C4g 0.95 (avg 0.95), C5 0.95 (avg 0.95), C6 0.95 (avg 0.95), C7 0.95 (avg 0.95), C8 0.95 (avg 0.95), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 2
  - 2021-11-29: treasury £31,554.01, C2->0.95, C3->1.00, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,918.19 / stressed £745.38) ratio 2.57
  - 2021-12-29: treasury £31,556.67, C2->0.95, C3->1.00, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,918.19 / stressed £745.38) ratio 2.57
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.57
- Worst single period: C5 on 2021-01-08 period 39, net margin £-2.12

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £-157.83
- Highest CLV: C2 (£220.05); Lowest CLV: C5 (£-422.39)
- Bill shock events (>=20%): 42 -- C1 2021-01-31 (26%); C1 2021-04-30 (22%); C1 2021-12-31 (23%); C1g 2021-12-31 (35%); C5 2021-01-31 (35%); C5 2021-05-31 (24%); C5 2021-06-30 (34%); C5 2021-10-31 (33%); C5 2021-11-30 (55%); C5 2021-12-31 (21%); C7 2021-01-31 (42%); C7 2021-05-31 (29%); C7 2021-06-30 (47%); C7 2021-10-31 (56%); C7 2021-11-30 (60%); C2 2021-04-30 (73%); C2g 2021-04-30 (75%); C6 2021-04-30 (87%); C6 2021-06-30 (37%); C6 2021-10-31 (29%); C6 2021-11-30 (53%); C8 2021-02-28 (21%); C8 2021-04-30 (96%); C8 2021-05-31 (28%); C8 2021-06-30 (63%); C8 2021-09-30 (24%); C8 2021-10-31 (78%); C8 2021-11-30 (81%); C3 2021-04-30 (21%); C3 2021-07-31 (179%); C3g 2021-07-31 (277%); C9 2021-02-28 (23%); C9 2021-05-31 (24%); C9 2021-06-30 (51%); C9 2021-07-31 (95%); C9 2021-08-31 (23%); C9 2021-09-30 (21%); C9 2021-10-31 (68%); C9 2021-11-30 (48%); C9 2021-12-31 (23%); C4 2021-10-31 (339%); C4g 2021-10-31 (352%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £72.32-£287.43/MWh, net margin £-25.42 -- **net-negative**
- C1g (gas): tariff £18.18-£105.38/MWh, net margin £-23.54 -- **net-negative**
- C2 (electricity): tariff £57.53-£120.87/MWh, net margin £-1.93 -- **net-negative**
- C2g (gas): tariff £13.14-£24.47/MWh, net margin £12.22
- C3 (electricity): tariff £40.71-£117.05/MWh, net margin £-8.13 -- **net-negative**
- C3g (gas): tariff £7.79-£31.30/MWh, net margin £1.73
- C4 (electricity): tariff £55.16-£258.73/MWh, net margin £-5.73 -- **net-negative**
- C4g (gas): tariff £12.67-£62.80/MWh, net margin £-4.56 -- **net-negative**
- C5 (electricity): tariff £72.32-£287.43/MWh, net margin £-153.52 -- **net-negative**
- C6 (electricity): tariff £57.53-£120.87/MWh, net margin £-47.55 -- **net-negative**
- C7 (electricity): tariff £72.32-£287.43/MWh, net margin £-86.46 -- **net-negative**
- C8 (electricity): tariff £57.53-£120.87/MWh, net margin £-11.98 -- **net-negative**
- C9 (electricity): tariff £40.71-£117.05/MWh, net margin £-0.73 -- **net-negative**
- Cost to serve per customer (whole-run total, average £614.66, range £88.06-£1,355.82):
  - C1: cost to serve £612.43, net margin after cost to serve £-430.59 -- **net-negative**
  - C1g: cost to serve £103.25, net margin after cost to serve £171.33
  - C2: cost to serve £676.87, net margin after cost to serve £-30.15 -- **net-negative**
  - C2g: cost to serve £121.48, net margin after cost to serve £333.75
  - C3: cost to serve £567.98, net margin after cost to serve £-398.27 -- **net-negative**
  - C3g: cost to serve £88.06, net margin after cost to serve £191.96
  - C4: cost to serve £642.68, net margin after cost to serve £-317.96 -- **net-negative**
  - C4g: cost to serve £189.40, net margin after cost to serve £237.83
  - C5: cost to serve £1,355.82, net margin after cost to serve £-620.85 -- **net-negative**
  - C6: cost to serve £1,325.34, net margin after cost to serve £-520.06 -- **net-negative**
  - C7: cost to serve £831.90, net margin after cost to serve £-274.53 -- **net-negative**
  - C8: cost to serve £779.32, net margin after cost to serve £-83.19 -- **net-negative**
  - C9: cost to serve £696.10, net margin after cost to serve £-337.72 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: -142.1% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.866, average bill shock 22.6%, bad debt provision £201.33, avg complaint probability 4.5%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £175.19 vs. naked (unhedged) net margin: £-7,995.20
- hedging added £8,170.39 vs. a fully unhedged book (actual net £175.19 vs. naked net £-7,995.20)
  - C1: actual £24.25 vs. naked £92.59 -- hedging cost £68.34
  - C1g: actual £33.21 vs. naked £-79.05 -- hedging added £112.26
  - C2: actual £-22.66 vs. naked £-290.46 -- hedging added £267.80
  - C2g: actual £4.80 vs. naked £-552.00 -- hedging added £556.81
  - C3: actual £-3.22 vs. naked £-354.09 -- hedging added £350.87
  - C3g: actual £-0.30 vs. naked £-632.96 -- hedging added £632.67
  - C4: actual £36.75 vs. naked £39.38 -- hedging cost £2.63
  - C4g: actual £7.71 vs. naked £-991.43 -- hedging added £999.15
  - C5: actual £66.99 vs. naked £-500.49 -- hedging added £567.48
  - C6: actual £-60.28 vs. naked £-2,428.03 -- hedging added £2,367.75
  - C7: actual £66.05 vs. naked £41.07 -- hedging added £24.98
  - C8: actual £-17.03 vs. naked £-1,097.25 -- hedging added £1,080.21
  - C9: actual £38.91 vs. naked £-1,242.48 -- hedging added £1,281.39

**Year narrative:** 2021 (flagged crisis year) produced a net loss of £-355.59 across 13 accounts. The risk committee intervened 2 time(s), raising hedge fractions in response to elevated VaR. 42 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £499.09 (gross £684.53, capital £185.44)
  - Electricity: gross £558.16, capital £173.48, net £384.67
  - Gas: gross £126.37, capital £11.96, net £114.42
- Treasury at year end: £31,845.25
- Hedge fraction at first renewal this year (avg across year's terms): C1 1.00 (avg 1.00), C1g 1.00 (avg 1.00), C2 0.95 (avg 0.95), C2g 1.00 (avg 1.00), C3 1.00 (avg 1.00), C3g 1.00 (avg 1.00), C4 1.00 (avg 1.00), C4g 1.00 (avg 1.00), C5 1.00 (avg 1.00), C6 1.00 (avg 1.00), C7 1.00 (avg 1.00), C8 1.00 (avg 1.00), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 48
  - 2022-03-29: treasury £31,568.32, C2->0.95, C3->1.00, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,918.19 / stressed £745.38) ratio 2.57
  - 2022-04-28: treasury £31,571.71, C2->0.95, C3->1.00, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,918.19 / stressed £745.38) ratio 2.57
  - 2022-05-16: treasury £31,602.13, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,953.78 / stressed £753.86) ratio 2.59
  - 2022-08-14: treasury £31,607.00, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,953.78 / stressed £753.86) ratio 2.59
  - 2022-09-13: treasury £31,606.75, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C6->1.00, C8->1.00, VaR (current £1,953.78 / stressed £753.86) ratio 2.59
  - 2022-01-04: treasury £31,645.57, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C8->1.00, VaR (current £2,271.58 / stressed £829.50) ratio 2.74
  - 2022-02-03: treasury £31,656.11, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C8->1.00, VaR (current £2,271.58 / stressed £829.50) ratio 2.74
  - 2022-03-05: treasury £31,669.16, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C8->1.00, VaR (current £2,271.58 / stressed £829.50) ratio 2.74
  - 2022-05-04: treasury £31,685.38, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C8->1.00, VaR (current £2,271.58 / stressed £829.50) ratio 2.74
  - 2022-07-03: treasury £31,697.00, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C8->1.00, VaR (current £2,271.58 / stressed £829.50) ratio 2.74
  - 2022-08-02: treasury £31,696.99, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C8->1.00, VaR (current £2,271.58 / stressed £829.50) ratio 2.74
  - 2022-01-29: treasury £31,724.09, C1->1.00, C2->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,434.31 / stressed £868.23) ratio 2.80
  - 2022-02-28: treasury £31,736.71, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,434.31 / stressed £868.23) ratio 2.80
  - 2022-10-26: treasury £31,766.25, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,434.31 / stressed £868.23) ratio 2.80
  - 2022-12-25: treasury £31,779.37, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,434.31 / stressed £868.23) ratio 2.80
  - 2022-06-24: treasury £31,803.42, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,396.06 / stressed £867.49) ratio 2.76
  - 2022-07-24: treasury £31,809.48, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,396.06 / stressed £867.49) ratio 2.76
  - 2022-08-23: treasury £31,813.28, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,396.06 / stressed £867.49) ratio 2.76
  - 2022-10-22: treasury £31,825.09, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,396.06 / stressed £867.49) ratio 2.76
  - 2022-11-21: treasury £31,836.10, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,396.06 / stressed £867.49) ratio 2.76
  - 2022-12-21: treasury £31,841.48, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,396.06 / stressed £867.49) ratio 2.76
  - 2022-04-12: treasury £31,933.02, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C7->1.00, C8->1.00, VaR (current £1,746.81 / stressed £650.20) ratio 2.69
  - 2022-05-12: treasury £31,941.74, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C7->1.00, C8->1.00, VaR (current £1,746.81 / stressed £650.20) ratio 2.69
  - 2022-06-11: treasury £31,948.68, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C7->1.00, C8->1.00, VaR (current £1,746.81 / stressed £650.20) ratio 2.69
  - 2022-07-11: treasury £31,954.52, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C7->1.00, C8->1.00, VaR (current £1,746.81 / stressed £650.20) ratio 2.69
  - 2022-09-09: treasury £31,965.51, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C7->1.00, C8->1.00, VaR (current £1,746.81 / stressed £650.20) ratio 2.69
  - 2022-10-09: treasury £31,972.99, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C7->1.00, C8->1.00, VaR (current £1,746.81 / stressed £650.20) ratio 2.69
  - 2022-11-08: treasury £31,981.57, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C7->1.00, C8->1.00, VaR (current £1,746.81 / stressed £650.20) ratio 2.69
  - 2022-12-08: treasury £31,993.96, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C7->1.00, C8->1.00, VaR (current £1,746.81 / stressed £650.20) ratio 2.69
  - 2022-04-08: treasury £32,046.20, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C7->1.00, VaR (current £1,576.14 / stressed £593.07) ratio 2.66
  - 2022-06-07: treasury £32,055.55, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C7->1.00, VaR (current £1,576.14 / stressed £593.07) ratio 2.66
  - 2022-07-07: treasury £32,057.85, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C7->1.00, VaR (current £1,576.14 / stressed £593.07) ratio 2.66
  - 2022-08-06: treasury £32,059.75, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C7->1.00, VaR (current £1,576.14 / stressed £593.07) ratio 2.66
  - 2022-09-05: treasury £32,061.59, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C7->1.00, VaR (current £1,576.14 / stressed £593.07) ratio 2.66
  - 2022-12-04: treasury £32,077.32, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C7->1.00, VaR (current £1,576.14 / stressed £593.07) ratio 2.66
  - 2022-09-01: treasury £32,118.07, C1->1.00, C4->1.00, C5->1.00, C7->1.00, VaR (current £1,536.66 / stressed £578.12) ratio 2.66
  - 2022-10-01: treasury £32,119.66, C1->1.00, C4->1.00, C5->1.00, C7->1.00, VaR (current £1,536.66 / stressed £578.12) ratio 2.66
  - 2022-11-30: treasury £32,123.31, C1->1.00, C4->1.00, C5->1.00, C7->1.00, VaR (current £1,536.66 / stressed £578.12) ratio 2.66
  - 2022-12-30: treasury £32,125.31, C1->1.00, C4->1.00, C5->1.00, C7->1.00, VaR (current £1,536.66 / stressed £578.12) ratio 2.66
  - 2022-07-21: treasury £32,181.52, C1->1.00, C4->1.00, C5->1.00, C7->1.00, VaR (current £1,536.66 / stressed £578.12) ratio 2.66
  - 2022-08-20: treasury £32,183.28, C1->1.00, C4->1.00, C5->1.00, C7->1.00, VaR (current £1,536.66 / stressed £578.12) ratio 2.66
  - 2022-09-19: treasury £32,185.55, C1->1.00, C4->1.00, C5->1.00, C7->1.00, VaR (current £1,536.66 / stressed £578.12) ratio 2.66
  - 2022-10-19: treasury £32,189.30, C1->1.00, C4->1.00, C5->1.00, C7->1.00, VaR (current £1,536.66 / stressed £578.12) ratio 2.66
  - 2022-11-18: treasury £32,193.42, C1->1.00, C4->1.00, C5->1.00, C7->1.00, VaR (current £1,536.66 / stressed £578.12) ratio 2.66
  - 2022-12-18: treasury £32,201.19, C1->1.00, C4->1.00, C5->1.00, C7->1.00, VaR (current £1,536.66 / stressed £578.12) ratio 2.66
  - 2022-10-16: treasury £32,237.00, C1->1.00, C5->1.00, C7->1.00, VaR (current £1,354.42 / stressed £520.76) ratio 2.60
  - 2022-11-15: treasury £32,241.28, C1->1.00, C5->1.00, C7->1.00, VaR (current £1,354.42 / stressed £520.76) ratio 2.60
  - 2022-12-15: treasury £32,245.81, C1->1.00, C5->1.00, C7->1.00, VaR (current £1,354.42 / stressed £520.76) ratio 2.60
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.69
- Worst single period: C6 on 2022-01-24 period 34, net margin £-0.82

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £-157.83
- Highest CLV: C2 (£220.05); Lowest CLV: C5 (£-422.39)
- Bill shock events (>=20%): 45 -- C1 2022-01-31 (235%); C1 2022-04-30 (21%); C1g 2022-01-31 (343%); C5 2022-01-31 (291%); C5 2022-02-28 (21%); C5 2022-04-30 (21%); C5 2022-05-31 (27%); C5 2022-11-30 (52%); C5 2022-12-31 (38%); C7 2022-01-31 (329%); C7 2022-02-28 (26%); C7 2022-04-30 (21%); C7 2022-05-31 (35%); C7 2022-06-30 (26%); C7 2022-09-30 (31%); C7 2022-11-30 (58%); C7 2022-12-31 (53%); C2 2022-04-30 (137%); C2g 2022-03-31 (26%); C2g 2022-04-30 (345%); C6 2022-04-30 (121%); C6 2022-05-31 (24%); C6 2022-09-30 (27%); C6 2022-11-30 (45%); C6 2022-12-31 (34%); C8 2022-02-28 (22%); C8 2022-04-30 (114%); C8 2022-05-31 (40%); C8 2022-06-30 (34%); C8 2022-07-31 (21%); C8 2022-09-30 (83%); C8 2022-10-31 (20%); C8 2022-11-30 (67%); C8 2022-12-31 (58%); C3 2022-07-31 (90%); C3g 2022-07-31 (200%); C9 2022-05-31 (31%); C9 2022-06-30 (29%); C9 2022-07-31 (44%); C9 2022-09-30 (49%); C9 2022-10-31 (33%); C9 2022-11-30 (41%); C9 2022-12-31 (54%); C4 2022-10-31 (64%); C4g 2022-10-31 (202%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £287.43-£329.46/MWh, net margin £24.75
- C1g (gas): tariff £102.05-£105.38/MWh, net margin £33.74
- C2 (electricity): tariff £120.87-£353.40/MWh, net margin £44.49
- C2g (gas): tariff £24.47-£127.96/MWh, net margin £36.40
- C3 (electricity): tariff £117.05-£220.84/MWh, net margin £8.04
- C3g (gas): tariff £31.30-£97.22/MWh, net margin £18.82
- C4 (electricity): tariff £258.73-£411.48/MWh, net margin £39.72
- C4g (gas): tariff £62.80-£196.77/MWh, net margin £25.46
- C5 (electricity): tariff £287.43-£329.46/MWh, net margin £72.52
- C6 (electricity): tariff £120.87-£353.40/MWh, net margin £49.28
- C7 (electricity): tariff £287.43-£329.46/MWh, net margin £68.92
- C8 (electricity): tariff £120.87-£353.40/MWh, net margin £30.48
- C9 (electricity): tariff £117.05-£220.84/MWh, net margin £46.47
- Cost to serve per customer (whole-run total, average £614.66, range £88.06-£1,355.82):
  - C1: cost to serve £612.43, net margin after cost to serve £-430.59 -- **net-negative**
  - C1g: cost to serve £103.25, net margin after cost to serve £171.33
  - C2: cost to serve £676.87, net margin after cost to serve £-30.15 -- **net-negative**
  - C2g: cost to serve £121.48, net margin after cost to serve £333.75
  - C3: cost to serve £567.98, net margin after cost to serve £-398.27 -- **net-negative**
  - C3g: cost to serve £88.06, net margin after cost to serve £191.96
  - C4: cost to serve £642.68, net margin after cost to serve £-317.96 -- **net-negative**
  - C4g: cost to serve £189.40, net margin after cost to serve £237.83
  - C5: cost to serve £1,355.82, net margin after cost to serve £-620.85 -- **net-negative**
  - C6: cost to serve £1,325.34, net margin after cost to serve £-520.06 -- **net-negative**
  - C7: cost to serve £831.90, net margin after cost to serve £-274.53 -- **net-negative**
  - C8: cost to serve £779.32, net margin after cost to serve £-83.19 -- **net-negative**
  - C9: cost to serve £696.10, net margin after cost to serve £-337.72 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 27.1% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.858, average bill shock 27.7%, bad debt provision £606.91, avg complaint probability 4.7%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £841.91 vs. naked (unhedged) net margin: £13,474.01
- hedging cost £12,632.10 vs. a fully unhedged book (actual net £841.91 vs. naked net £13,474.01)
  - C1: actual £22.52 vs. naked £719.05 -- hedging cost £696.53
  - C1g: actual £38.63 vs. naked £703.43 -- hedging cost £664.80
  - C2: actual £93.13 vs. naked £1,010.78 -- hedging cost £917.65
  - C2g: actual £53.03 vs. naked £399.40 -- hedging cost £346.38
  - C3: actual £20.92 vs. naked £88.50 -- hedging cost £67.58
  - C3g: actual £44.25 vs. naked £161.76 -- hedging cost £117.51
  - C4: actual £49.85 vs. naked £1,800.08 -- hedging cost £1,750.23
  - C4g: actual £96.22 vs. naked £2,961.18 -- hedging cost £2,864.96
  - C5: actual £106.95 vs. naked £2,818.57 -- hedging cost £2,711.62
  - C6: actual £115.92 vs. naked £-252.45 -- hedging added £368.37
  - C7: actual £74.70 vs. naked £2,169.04 -- hedging cost £2,094.34
  - C8: actual £71.13 vs. naked £903.27 -- hedging cost £832.14
  - C9: actual £54.65 vs. naked £-8.59 -- hedging added £63.24

**Year narrative:** 2022 (flagged crisis year) produced a net gain of £499.09 across 13 accounts. The risk committee intervened 48 time(s), raising hedge fractions in response to elevated VaR. 45 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £992.62 (gross £1,119.11, capital £126.49)
  - Electricity: gross £841.31, capital £92.39, net £748.92
  - Gas: gross £277.80, capital £34.10, net £243.70
- Treasury at year end: £32,741.59
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.90 (avg 0.90), C1g 0.90 (avg 0.90), C2 0.85 (avg 0.85), C2g 0.90 (avg 0.90), C3 0.90 (avg 0.90), C3g 0.90 (avg 0.90), C4 0.90 (avg 0.90), C4g 0.90 (avg 0.90), C5 0.90 (avg 0.90), C6 1.00 (avg 1.00), C7 0.90 (avg 0.90), C8 0.90 (avg 0.90), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 45
  - 2023-02-19: treasury £31,861.74, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,396.06 / stressed £867.49) ratio 2.76
  - 2023-03-21: treasury £31,871.61, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C6->1.00, C7->1.00, C8->1.00, VaR (current £2,396.06 / stressed £867.49) ratio 2.76
  - 2023-01-07: treasury £32,007.87, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C7->1.00, C8->1.00, VaR (current £1,746.81 / stressed £650.20) ratio 2.69
  - 2023-02-07: treasury £32,021.81, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C7->1.00, C8->1.00, VaR (current £1,746.81 / stressed £650.20) ratio 2.69
  - 2023-03-09: treasury £32,035.21, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C7->1.00, C8->1.00, VaR (current £1,746.81 / stressed £650.20) ratio 2.69
  - 2023-01-03: treasury £32,088.29, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C7->1.00, VaR (current £1,576.14 / stressed £593.07) ratio 2.66
  - 2023-02-02: treasury £32,098.22, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C7->1.00, VaR (current £1,576.14 / stressed £593.07) ratio 2.66
  - 2023-03-04: treasury £32,107.32, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C7->1.00, VaR (current £1,576.14 / stressed £593.07) ratio 2.66
  - 2023-01-29: treasury £32,127.32, C1->1.00, C4->1.00, C5->1.00, C7->1.00, VaR (current £1,536.66 / stressed £578.12) ratio 2.66
  - 2023-03-30: treasury £32,131.28, C1->1.00, C4->1.00, C5->1.00, C7->1.00, VaR (current £1,536.66 / stressed £578.12) ratio 2.66
  - 2023-06-28: treasury £32,135.86, C1->1.00, C4->1.00, C5->1.00, C7->1.00, VaR (current £1,536.66 / stressed £578.12) ratio 2.66
  - 2023-01-17: treasury £32,208.08, C1->1.00, C4->1.00, C5->1.00, C7->1.00, VaR (current £1,536.66 / stressed £578.12) ratio 2.66
  - 2023-02-16: treasury £32,214.77, C1->1.00, C4->1.00, C5->1.00, C7->1.00, VaR (current £1,536.66 / stressed £578.12) ratio 2.66
  - 2023-04-17: treasury £32,227.36, C1->1.00, C4->1.00, C5->1.00, C7->1.00, VaR (current £1,536.66 / stressed £578.12) ratio 2.66
  - 2023-06-16: treasury £32,234.09, C1->1.00, C4->1.00, C5->1.00, C7->1.00, VaR (current £1,536.66 / stressed £578.12) ratio 2.66
  - 2023-01-14: treasury £32,250.34, C1->1.00, C5->1.00, C7->1.00, VaR (current £1,354.42 / stressed £520.76) ratio 2.60
  - 2023-02-13: treasury £32,254.89, C1->1.00, C5->1.00, C7->1.00, VaR (current £1,354.42 / stressed £520.76) ratio 2.60
  - 2023-04-14: treasury £32,263.56, C1->1.00, C5->1.00, C7->1.00, VaR (current £1,354.42 / stressed £520.76) ratio 2.60
  - 2023-06-13: treasury £32,271.15, C1->1.00, C5->1.00, C7->1.00, VaR (current £1,354.42 / stressed £520.76) ratio 2.60
  - 2023-09-11: treasury £32,282.26, C1->1.00, C5->1.00, C7->1.00, VaR (current £1,354.42 / stressed £520.76) ratio 2.60
  - 2023-01-02: treasury £32,381.18, C5->1.00, C7->1.00, VaR (current £1,268.82 / stressed £488.29) ratio 2.60
  - 2023-02-01: treasury £32,383.37, C5->1.00, C7->1.00, VaR (current £1,268.82 / stressed £488.29) ratio 2.60
  - 2023-03-03: treasury £32,385.55, C5->1.00, C7->1.00, VaR (current £1,268.82 / stressed £488.29) ratio 2.60
  - 2023-04-02: treasury £32,387.62, C5->1.00, C7->1.00, VaR (current £1,268.82 / stressed £488.29) ratio 2.60
  - 2023-05-02: treasury £32,389.32, C5->1.00, C7->1.00, VaR (current £1,268.82 / stressed £488.29) ratio 2.60
  - 2023-06-01: treasury £32,390.91, C5->1.00, C7->1.00, VaR (current £1,268.82 / stressed £488.29) ratio 2.60
  - 2023-07-01: treasury £32,392.45, C5->1.00, C7->1.00, VaR (current £1,268.82 / stressed £488.29) ratio 2.60
  - 2023-07-31: treasury £32,393.98, C5->1.00, C7->1.00, VaR (current £1,268.82 / stressed £488.29) ratio 2.60
  - 2023-08-30: treasury £32,395.50, C5->1.00, C7->1.00, VaR (current £1,268.82 / stressed £488.29) ratio 2.60
  - 2023-09-29: treasury £32,397.23, C5->1.00, C7->1.00, VaR (current £1,268.82 / stressed £488.29) ratio 2.60
  - 2023-10-29: treasury £32,398.99, C5->1.00, C7->1.00, VaR (current £1,268.82 / stressed £488.29) ratio 2.60
  - 2023-11-28: treasury £32,401.17, C5->1.00, C7->1.00, VaR (current £1,268.82 / stressed £488.29) ratio 2.60
  - 2023-12-28: treasury £32,403.35, C5->1.00, C7->1.00, VaR (current £1,268.82 / stressed £488.29) ratio 2.60
  - 2023-01-20: treasury £32,450.56, C7->1.00, VaR (current £504.58 / stressed £198.40) ratio 2.54
  - 2023-02-19: treasury £32,463.82, C7->1.00, VaR (current £504.58 / stressed £198.40) ratio 2.54
  - 2023-03-21: treasury £32,476.29, C7->1.00, VaR (current £504.58 / stressed £198.40) ratio 2.54
  - 2023-04-20: treasury £32,486.22, C7->1.00, VaR (current £504.58 / stressed £198.40) ratio 2.54
  - 2023-05-20: treasury £32,494.44, C7->1.00, VaR (current £504.58 / stressed £198.40) ratio 2.54
  - 2023-06-19: treasury £32,500.39, C7->1.00, VaR (current £504.58 / stressed £198.40) ratio 2.54
  - 2023-07-19: treasury £32,505.70, C7->1.00, VaR (current £504.58 / stressed £198.40) ratio 2.54
  - 2023-08-18: treasury £32,510.84, C7->1.00, VaR (current £504.58 / stressed £198.40) ratio 2.54
  - 2023-09-17: treasury £32,516.08, C7->1.00, VaR (current £504.58 / stressed £198.40) ratio 2.54
  - 2023-10-17: treasury £32,522.26, C7->1.00, VaR (current £504.58 / stressed £198.40) ratio 2.54
  - 2023-11-16: treasury £32,531.85, C7->1.00, VaR (current £504.58 / stressed £198.40) ratio 2.54
  - 2023-12-16: treasury £32,544.38, C7->1.00, VaR (current £504.58 / stressed £198.40) ratio 2.54
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.61
- Worst single period: C2g on 2023-03-31 period 1, net margin £-1.69

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £-157.83
- Highest CLV: C2 (£220.05); Lowest CLV: C5 (£-422.39)
- Bill shock events (>=20%): 33 -- C1 2023-04-30 (21%); C5 2023-05-31 (23%); C5 2023-06-30 (26%); C5 2023-10-31 (33%); C5 2023-11-30 (55%); C7 2023-05-31 (32%); C7 2023-06-30 (35%); C7 2023-10-31 (52%); C7 2023-11-30 (65%); C2 2023-04-30 (50%); C2g 2023-04-30 (47%); C6 2023-04-30 (53%); C6 2023-05-31 (24%); C6 2023-06-30 (24%); C6 2023-10-31 (41%); C6 2023-11-30 (46%); C8 2023-04-30 (54%); C8 2023-05-31 (43%); C8 2023-06-30 (44%); C8 2023-10-31 (101%); C8 2023-11-30 (69%); C3 2023-07-31 (39%); C3g 2023-07-31 (56%); C9 2023-02-28 (20%); C9 2023-04-30 (25%); C9 2023-05-31 (34%); C9 2023-06-30 (46%); C9 2023-07-31 (32%); C9 2023-09-30 (23%); C9 2023-10-31 (76%); C9 2023-11-30 (53%); C4 2023-10-31 (70%); C4g 2023-10-31 (81%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £131.28-£329.46/MWh, net margin £22.00
- C1g (gas): tariff £42.92-£102.05/MWh, net margin £37.74
- C2 (electricity): tariff £204.90-£353.40/MWh, net margin £147.56
- C2g (gas): tariff £68.57-£127.96/MWh, net margin £80.61
- C3 (electricity): tariff £128.17-£220.84/MWh, net margin £27.90
- C3g (gas): tariff £40.69-£97.22/MWh, net margin £42.68
- C4 (electricity): tariff £112.80-£411.48/MWh, net margin £48.38
- C4g (gas): tariff £35.29-£196.77/MWh, net margin £82.67
- C5 (electricity): tariff £131.28-£329.46/MWh, net margin £101.27
- C6 (electricity): tariff £204.90-£353.40/MWh, net margin £151.65
- C7 (electricity): tariff £131.28-£329.46/MWh, net margin £72.31
- C8 (electricity): tariff £204.90-£353.40/MWh, net margin £112.53
- C9 (electricity): tariff £128.17-£220.84/MWh, net margin £65.33
- Cost to serve per customer (whole-run total, average £614.66, range £88.06-£1,355.82):
  - C1: cost to serve £612.43, net margin after cost to serve £-430.59 -- **net-negative**
  - C1g: cost to serve £103.25, net margin after cost to serve £171.33
  - C2: cost to serve £676.87, net margin after cost to serve £-30.15 -- **net-negative**
  - C2g: cost to serve £121.48, net margin after cost to serve £333.75
  - C3: cost to serve £567.98, net margin after cost to serve £-398.27 -- **net-negative**
  - C3g: cost to serve £88.06, net margin after cost to serve £191.96
  - C4: cost to serve £642.68, net margin after cost to serve £-317.96 -- **net-negative**
  - C4g: cost to serve £189.40, net margin after cost to serve £237.83
  - C5: cost to serve £1,355.82, net margin after cost to serve £-620.85 -- **net-negative**
  - C6: cost to serve £1,325.34, net margin after cost to serve £-520.06 -- **net-negative**
  - C7: cost to serve £831.90, net margin after cost to serve £-274.53 -- **net-negative**
  - C8: cost to serve £779.32, net margin after cost to serve £-83.19 -- **net-negative**
  - C9: cost to serve £696.10, net margin after cost to serve £-337.72 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 11.3% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.883, average bill shock 13.9%, bad debt provision £647.01, avg complaint probability 3.9%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £1,152.51 vs. naked (unhedged) net margin: £2,561.31
- hedging cost £1,408.80 vs. a fully unhedged book (actual net £1,152.51 vs. naked net £2,561.31)
  - C1: actual £33.32 vs. naked £108.38 -- hedging cost £75.06
  - C1g: actual £41.41 vs. naked £40.40 -- hedging added £1.01
  - C2: actual £167.40 vs. naked £741.54 -- hedging cost £574.14
  - C2g: actual £92.71 vs. naked £336.31 -- hedging cost £243.60
  - C3: actual £39.65 vs. naked £132.91 -- hedging cost £93.26
  - C3g: actual £46.31 vs. naked £37.04 -- hedging added £9.26
  - C4: actual £54.48 vs. naked £161.46 -- hedging cost £106.98
  - C4g: actual £58.93 vs. naked £-41.99 -- hedging added £100.92
  - C5: actual £112.08 vs. naked £78.77 -- hedging added £33.31
  - C6: actual £169.47 vs. naked £-143.50 -- hedging added £312.97
  - C7: actual £96.33 vs. naked £242.33 -- hedging cost £146.00
  - C8: actual £162.03 vs. naked £691.39 -- hedging cost £529.36
  - C9: actual £78.40 vs. naked £176.27 -- hedging cost £97.86

**Year narrative:** 2023 produced a net gain of £992.62 across 13 accounts. The risk committee intervened 45 time(s), raising hedge fractions in response to elevated VaR. 33 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £891.81 (gross £1,186.48, capital £294.67)
  - Electricity: gross £934.98, capital £242.95, net £692.02
  - Gas: gross £251.50, capital £51.72, net £199.79
- Treasury at year end: £33,815.10
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 0.90 (avg 0.90), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 1.00 (avg 1.00), C4 0.85 (avg 0.85), C4g 1.00 (avg 1.00), C5 1.00 (avg 1.00), C6 1.00 (avg 1.00), C7 0.85 (avg 0.85), C8 0.85 (avg 0.85), C9 0.90 (avg 0.90)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C2g on 2024-03-30 period 1, net margin £-0.51

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £-157.83
- Highest CLV: C2 (£220.05); Lowest CLV: C5 (£-422.39)
- Bill shock events (>=20%): 37 -- C1 2024-01-31 (59%); C1 2024-04-30 (24%); C1g 2024-01-31 (56%); C5 2024-01-31 (52%); C5 2024-02-29 (22%); C5 2024-05-31 (27%); C5 2024-09-30 (20%); C5 2024-10-31 (28%); C5 2024-11-30 (38%); C7 2024-01-31 (51%); C7 2024-02-29 (26%); C7 2024-04-30 (21%); C7 2024-05-31 (36%); C7 2024-09-30 (33%); C7 2024-10-31 (35%); C7 2024-11-30 (46%); C2 2024-04-30 (57%); C2g 2024-04-30 (53%); C6 2024-04-30 (58%); C6 2024-05-31 (30%); C6 2024-09-30 (26%); C6 2024-10-31 (24%); C6 2024-11-30 (39%); C8 2024-02-29 (23%); C8 2024-04-30 (60%); C8 2024-05-31 (51%); C8 2024-07-31 (29%); C8 2024-09-30 (78%); C8 2024-10-31 (38%); C8 2024-11-30 (62%); C3 2024-04-30 (22%); C9 2024-04-30 (22%); C9 2024-05-31 (50%); C9 2024-07-31 (40%); C9 2024-09-30 (56%); C9 2024-10-31 (24%); C9 2024-11-30 (48%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £128.48-£131.28/MWh, net margin £33.11
- C1g (gas): tariff £42.73-£42.92/MWh, net margin £41.49
- C2 (electricity): tariff £102.60-£204.90/MWh, net margin £88.41
- C2g (gas): tariff £32.50-£68.57/MWh, net margin £44.02
- C3 (electricity): tariff £99.91-£128.17/MWh, net margin £31.88
- C3g (gas): tariff £33.40-£40.69/MWh, net margin £47.70
- C4 (electricity): tariff £104.35-£112.80/MWh, net margin £51.23
- C4g (gas): tariff £35.29-£37.99/MWh, net margin £66.57
- C5 (electricity): tariff £128.48-£131.28/MWh, net margin £118.36
- C6 (electricity): tariff £102.60-£204.90/MWh, net margin £125.63
- C7 (electricity): tariff £128.48-£131.28/MWh, net margin £95.38
- C8 (electricity): tariff £102.60-£204.90/MWh, net margin £91.03
- C9 (electricity): tariff £99.91-£128.17/MWh, net margin £57.00
- Cost to serve per customer (whole-run total, average £614.66, range £88.06-£1,355.82):
  - C1: cost to serve £612.43, net margin after cost to serve £-430.59 -- **net-negative**
  - C1g: cost to serve £103.25, net margin after cost to serve £171.33
  - C2: cost to serve £676.87, net margin after cost to serve £-30.15 -- **net-negative**
  - C2g: cost to serve £121.48, net margin after cost to serve £333.75
  - C3: cost to serve £567.98, net margin after cost to serve £-398.27 -- **net-negative**
  - C3g: cost to serve £88.06, net margin after cost to serve £191.96
  - C4: cost to serve £642.68, net margin after cost to serve £-317.96 -- **net-negative**
  - C4g: cost to serve £189.40, net margin after cost to serve £237.83
  - C5: cost to serve £1,355.82, net margin after cost to serve £-620.85 -- **net-negative**
  - C6: cost to serve £1,325.34, net margin after cost to serve £-520.06 -- **net-negative**
  - C7: cost to serve £831.90, net margin after cost to serve £-274.53 -- **net-negative**
  - C8: cost to serve £779.32, net margin after cost to serve £-83.19 -- **net-negative**
  - C9: cost to serve £696.10, net margin after cost to serve £-337.72 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 24.8% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.883, average bill shock 13.6%, bad debt provision £303.59, avg complaint probability 3.8%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £436.47 vs. naked (unhedged) net margin: £-2,374.85
- hedging added £2,811.32 vs. a fully unhedged book (actual net £436.47 vs. naked net £-2,374.85)
  - C1: actual £9.53 vs. naked £-0.79 -- hedging added £10.32
  - C1g: actual £13.61 vs. naked £-28.42 -- hedging added £42.03
  - C2: actual £44.25 vs. naked £68.30 -- hedging cost £24.05
  - C2g: actual £21.17 vs. naked £-121.41 -- hedging added £142.58
  - C3: actual £14.43 vs. naked £-37.20 -- hedging added £51.64
  - C3g: actual £41.17 vs. naked £-122.07 -- hedging added £163.24
  - C4: actual £20.20 vs. naked £-29.81 -- hedging added £50.01
  - C4g: actual £49.89 vs. naked £-118.06 -- hedging added £167.96
  - C5: actual £59.20 vs. naked £-234.02 -- hedging added £293.22
  - C6: actual £104.69 vs. naked £-1,043.27 -- hedging added £1,147.96
  - C7: actual £24.38 vs. naked £-78.79 -- hedging added £103.17
  - C8: actual £9.59 vs. naked £-303.83 -- hedging added £313.42
  - C9: actual £24.35 vs. naked £-325.47 -- hedging added £349.82

**Year narrative:** 2024 produced a net gain of £891.81 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 37 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £308.61 (gross £420.00, capital £111.39)
  - Electricity: gross £330.29, capital £98.55, net £231.75
  - Gas: gross £89.71, capital £12.84, net £76.86
- Treasury at year end: £33,970.35
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.85 (avg 0.85), C2g 0.95 (avg 0.95), C6 1.00 (avg 1.00), C8 0.95 (avg 0.95)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C8 on 2025-01-08 period 36, net margin £-1.66

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £-157.83
- Highest CLV: C2 (£220.05); Lowest CLV: C5 (£-422.39)
- Bill shock events (>=20%): 32 -- C1 2025-04-30 (23%); C1 2025-06-07 (78%); C1g 2025-06-07 (77%); C5 2025-04-30 (31%); C5 2025-06-07 (79%); C7 2025-01-31 (23%); C7 2025-04-30 (37%); C7 2025-05-31 (22%); C7 2025-06-07 (80%); C2 2025-04-30 (71%); C2 2025-06-07 (78%); C2g 2025-04-30 (48%); C2g 2025-06-07 (77%); C6 2025-01-31 (25%); C6 2025-02-28 (20%); C6 2025-04-30 (48%); C6 2025-05-31 (21%); C6 2025-06-07 (76%); C8 2025-01-31 (39%); C8 2025-02-28 (24%); C8 2025-04-30 (25%); C8 2025-05-31 (38%); C8 2025-06-07 (73%); C3 2025-04-30 (22%); C3 2025-06-07 (78%); C3g 2025-06-07 (77%); C9 2025-01-31 (22%); C9 2025-04-30 (26%); C9 2025-05-31 (34%); C9 2025-06-07 (71%); C4 2025-06-07 (78%); C4g 2025-06-07 (77%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £128.48/MWh, net margin £10.12
- C1g (gas): tariff £42.73/MWh, net margin £14.21
- C2 (electricity): tariff £102.60-£222.51/MWh, net margin £35.72
- C2g (gas): tariff £32.50-£51.55/MWh, net margin £12.46
- C3 (electricity): tariff £99.91/MWh, net margin £4.82
- C3g (gas): tariff £33.40/MWh, net margin £18.91
- C4 (electricity): tariff £104.35/MWh, net margin £11.44
- C4g (gas): tariff £37.99/MWh, net margin £31.28
- C5 (electricity): tariff £128.48/MWh, net margin £57.98
- C6 (electricity): tariff £102.60-£222.51/MWh, net margin £63.78
- C7 (electricity): tariff £128.48/MWh, net margin £27.30
- C8 (electricity): tariff £102.60-£222.51/MWh, net margin £9.73
- C9 (electricity): tariff £99.91/MWh, net margin £10.86
- Cost to serve per customer (whole-run total, average £614.66, range £88.06-£1,355.82):
  - C1: cost to serve £612.43, net margin after cost to serve £-430.59 -- **net-negative**
  - C1g: cost to serve £103.25, net margin after cost to serve £171.33
  - C2: cost to serve £676.87, net margin after cost to serve £-30.15 -- **net-negative**
  - C2g: cost to serve £121.48, net margin after cost to serve £333.75
  - C3: cost to serve £567.98, net margin after cost to serve £-398.27 -- **net-negative**
  - C3g: cost to serve £88.06, net margin after cost to serve £191.96
  - C4: cost to serve £642.68, net margin after cost to serve £-317.96 -- **net-negative**
  - C4g: cost to serve £189.40, net margin after cost to serve £237.83
  - C5: cost to serve £1,355.82, net margin after cost to serve £-620.85 -- **net-negative**
  - C6: cost to serve £1,325.34, net margin after cost to serve £-520.06 -- **net-negative**
  - C7: cost to serve £831.90, net margin after cost to serve £-274.53 -- **net-negative**
  - C8: cost to serve £779.32, net margin after cost to serve £-83.19 -- **net-negative**
  - C9: cost to serve £696.10, net margin after cost to serve £-337.72 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 26.5% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 78, average clarity 0.831, average bill shock 24.8%, bad debt provision £143.10, avg complaint probability 5.6%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £83.11 vs. naked (unhedged) net margin: £-229.53
- hedging added £312.64 vs. a fully unhedged book (actual net £83.11 vs. naked net £-229.53)
  - C2: actual £30.36 vs. naked £131.09 -- hedging cost £100.73
  - C2g: actual £10.27 vs. naked £-0.48 -- hedging added £10.76
  - C6: actual £28.17 vs. naked £-365.86 -- hedging added £394.03
  - C8: actual £14.31 vs. naked £5.72 -- hedging added £8.59

**Year narrative:** 2025 produced a net gain of £308.61 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 32 customer(s) experienced a bill shock of >=20%.
