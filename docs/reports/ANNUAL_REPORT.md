# Annual Report — The Synthetic Enterprise

## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £21,829.17
- Final treasury: £37,953.15
  (£16,123.98 net change)
- Gross margin: £18,970.93
- Capital costs: £2,846.94
- Net margin: £16,123.98
- Capital cost ratio: 15.0% of gross
- Risk committee (Context Handshake) interventions: 99
- Bills issued: 1101, average clarity 0.918,
  service quality score 0.935
- Enterprise value (CLV sum across 6 billing accounts): £10,496.28
- Cost to serve (whole portfolio): £6,189.28, net margin after cost to serve: £12,781.64
- Hedge effectiveness (whole window): hedging cost £17,352.21 vs. a fully unhedged book (actual net £16,123.98 vs. naked net £33,476.19)

- **2021** (crisis year): net margin £632.78, 12 risk committee wake-up(s).
- **2022** (crisis year): net margin £2,530.50, 20 risk committee wake-up(s).

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

**Note:** the figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run: gross £18,970.93, capital £2,846.94, net £16,123.98. Old-model run: gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 15.0% under the new mandate vs. 41.0% under the old reactive model.
- **2021 net margin**: £632.78 under the new mandate vs. £-1,096.43 under the old reactive model.

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run): £16,123.98
- Old reactive model (actual): £26,779.56
- Fully naked (this run's counterfactual): £33,476.19
- Fully naked (old run's counterfactual): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.
## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £17,352.21 vs. a fully unhedged book (actual net £16,123.98 vs. naked net £33,476.19)
- **Best hedging decision of the run**: C6, term starting
  2021-03-31 (hedge fraction 0.85) -- hedging
  protected £1,497.22 vs. going naked.
- **Worst hedging decision of the run**: C5, term
  starting 2022-12-30 (hedge fraction 1.00) --
  over-hedging cost £3,360.13 vs. going
  naked.

## 2016

**Trading & Risk**

- Net margin: £713.99 (gross £952.44, capital £238.45)
  - Electricity: gross £826.92, capital £232.13, net £594.79
  - Gas: gross £125.53, capital £6.32, net £119.20
- Treasury at year end: £22,325.94
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.93), C1g 0.85 (avg 0.85), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 0.85 (avg 0.85), C4 0.85 (avg 0.85), C4g 0.85 (avg 0.85), C5 0.85 (avg 0.90), C6 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 36
  - 2016-01-31: treasury £21,836.72, C1->1.00, VaR (current £135.51 / stressed £41.63) ratio 3.25
  - 2016-03-31: treasury £21,851.63, C1->1.00, VaR (current £135.51 / stressed £41.63) ratio 3.25
  - 2016-04-30: treasury £21,857.41, C1->0.95, VaR (current £135.51 / stressed £41.63) ratio 3.25
  - 2016-05-30: treasury £21,863.06, C1->1.00, VaR (current £135.51 / stressed £41.63) ratio 3.25
  - 2016-06-29: treasury £21,868.03, C1->1.00, VaR (current £135.51 / stressed £41.63) ratio 3.25
  - 2016-08-28: treasury £21,878.42, C1->0.95, VaR (current £135.51 / stressed £41.63) ratio 3.25
  - 2016-10-27: treasury £21,889.48, C1->1.00, VaR (current £135.51 / stressed £41.63) ratio 3.25
  - 2016-11-26: treasury £21,895.04, C1->1.00, VaR (current £135.51 / stressed £41.63) ratio 3.25
  - 2016-12-26: treasury £21,902.23, C1->1.00, VaR (current £135.51 / stressed £41.63) ratio 3.25
  - 2016-01-18: treasury £21,968.37, C1->1.00, C5->1.00, VaR (current £1,345.40 / stressed £413.34) ratio 3.25
  - 2016-02-17: treasury £22,008.51, C1->1.00, C5->1.00, VaR (current £1,345.40 / stressed £413.34) ratio 3.25
  - 2016-06-16: treasury £22,127.13, C1->1.00, C5->1.00, VaR (current £1,345.40 / stressed £413.34) ratio 3.25
  - 2016-08-15: treasury £22,150.74, C1->1.00, C5->1.00, VaR (current £1,345.40 / stressed £413.34) ratio 3.25
  - 2016-09-14: treasury £22,161.23, C1->1.00, C5->1.00, VaR (current £1,345.40 / stressed £413.34) ratio 3.25
  - 2016-10-14: treasury £22,177.12, C1->1.00, C5->1.00, VaR (current £1,345.40 / stressed £413.34) ratio 3.25
  - 2016-11-13: treasury £22,199.69, C1->1.00, C5->1.00, VaR (current £1,345.40 / stressed £413.34) ratio 3.25
  - 2016-04-13: treasury £22,256.80, C1->0.95, C5->0.95, VaR (current £1,430.87 / stressed £448.93) ratio 3.19
  - 2016-05-13: treasury £22,264.86, C1->0.95, C5->0.95, VaR (current £1,430.87 / stressed £448.93) ratio 3.19
  - 2016-07-12: treasury £22,280.53, C1->1.00, C5->1.00, VaR (current £1,430.87 / stressed £448.93) ratio 3.19
  - 2016-08-11: treasury £22,288.52, C1->0.95, C5->0.95, VaR (current £1,430.87 / stressed £448.93) ratio 3.19
  - 2016-11-09: treasury £22,311.73, C1->0.95, C5->0.95, VaR (current £1,430.87 / stressed £448.93) ratio 3.19
  - 2016-12-09: treasury £22,319.34, C1->0.95, C5->0.95, VaR (current £1,430.87 / stressed £448.93) ratio 3.19
  - 2016-04-30: treasury £22,424.97, C1->0.95, C5->0.95, VaR (current £2,529.76 / stressed £906.58) ratio 2.79
  - 2016-05-30: treasury £22,437.57, C1->1.00, C5->1.00, VaR (current £2,529.76 / stressed £906.58) ratio 2.79
  - 2016-07-29: treasury £22,449.82, C1->0.95, C5->0.95, VaR (current £2,529.76 / stressed £906.58) ratio 2.79
  - 2016-08-28: treasury £22,454.85, C1->1.00, C5->1.00, VaR (current £2,529.76 / stressed £906.58) ratio 2.79
  - 2016-09-27: treasury £22,460.14, C1->1.00, C5->1.00, VaR (current £2,529.76 / stressed £906.58) ratio 2.79
  - 2016-10-27: treasury £22,470.99, C1->0.95, C5->0.95, VaR (current £2,529.76 / stressed £906.58) ratio 2.79
  - 2016-11-26: treasury £22,481.54, C1->1.00, C5->1.00, VaR (current £2,529.76 / stressed £906.58) ratio 2.79
  - 2016-07-26: treasury £22,561.25, C1->1.00, C5->1.00, VaR (current £2,587.66 / stressed £933.75) ratio 2.77
  - 2016-08-25: treasury £22,564.85, C1->1.00, C5->1.00, VaR (current £2,587.66 / stressed £933.75) ratio 2.77
  - 2016-10-24: treasury £22,571.85, C1->0.95, C5->0.95, VaR (current £2,587.66 / stressed £933.75) ratio 2.77
  - 2016-12-23: treasury £22,578.44, C1->0.95, C5->0.95, VaR (current £2,587.66 / stressed £933.75) ratio 2.77
  - 2016-10-13: treasury £22,640.29, C1->0.95, C5->0.95, VaR (current £2,699.03 / stressed £987.41) ratio 2.73
  - 2016-11-12: treasury £22,647.11, C1->1.00, C5->1.00, VaR (current £2,699.03 / stressed £987.41) ratio 2.73
  - 2016-12-12: treasury £22,654.09, C1->0.95, C5->0.95, VaR (current £2,699.03 / stressed £987.41) ratio 2.73
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 3.06
- Worst single period: C6 on 2016-11-08 period 40, net margin £-0.41

**Customer Book**

- Active accounts: 10 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £1,749.38
- Highest CLV: C6 (£3,450.46); Lowest CLV: C3 (£641.62)
- Bill shock events (>=20%): 10 -- C1 2016-04-30 (21%); C5 2016-04-30 (21%); C5 2016-05-31 (30%); C5 2016-06-30 (22%); C5 2016-10-31 (47%); C5 2016-11-30 (49%); C6 2016-05-31 (28%); C6 2016-06-30 (25%); C6 2016-10-31 (46%); C6 2016-11-30 (51%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £132.43-£166.09/MWh, net margin £74.29
- C1g (gas): tariff £17.55-£17.65/MWh, net margin £41.21
- C2 (electricity): tariff £91.21/MWh, net margin £72.66
- C2g (gas): tariff £19.18/MWh, net margin £42.85
- C3 (electricity): tariff £76.47/MWh, net margin £21.20
- C3g (gas): tariff £14.24/MWh, net margin £19.34
- C4 (electricity): tariff £87.58/MWh, net margin £22.00
- C4g (gas): tariff £15.17/MWh, net margin £15.81
- C5 (electricity): tariff £132.43-£166.09/MWh, net margin £306.86
- C6 (electricity): tariff £91.21/MWh, net margin £97.79
- Cost to serve per customer (whole-run total, average £618.93, range £95.63-£1,458.12):
  - C1: cost to serve £655.06, net margin after cost to serve £221.49
  - C1g: cost to serve £111.21, net margin after cost to serve £561.02
  - C2: cost to serve £772.86, net margin after cost to serve £1,626.62
  - C2g: cost to serve £133.02, net margin after cost to serve £899.18
  - C3: cost to serve £599.86, net margin after cost to serve £197.00
  - C3g: cost to serve £95.63, net margin after cost to serve £563.12
  - C4: cost to serve £709.09, net margin after cost to serve £803.85
  - C4g: cost to serve £204.67, net margin after cost to serve £986.14
  - C5: cost to serve £1,458.12, net margin after cost to serve £2,822.36
  - C6: cost to serve £1,449.78, net margin after cost to serve £4,100.88

**Portfolio Health**

- Capital cost ratio: 25.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 81, average clarity 0.931, average bill shock 8.6%, bad debt provision £111.63, avg complaint probability 2.7%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £1,354.95 vs. naked (unhedged) net margin: £3,557.86
- hedging cost £2,202.91 vs. a fully unhedged book (actual net £1,354.95 vs. naked net £3,557.86)
  - C1: actual £128.51 vs. naked £593.88 -- hedging cost £465.37
  - C1g: actual £75.50 vs. naked £70.08 -- hedging added £5.41
  - C2: actual £98.05 vs. naked £298.79 -- hedging cost £200.74
  - C2g: actual £54.62 vs. naked £83.16 -- hedging cost £28.54
  - C3: actual £43.41 vs. naked £94.80 -- hedging cost £51.39
  - C3g: actual £35.51 vs. naked £4.26 -- hedging added £31.25
  - C4: actual £87.04 vs. naked £236.52 -- hedging cost £149.48
  - C4g: actual £56.91 vs. naked £5.23 -- hedging added £51.67
  - C5: actual £622.95 vs. naked £2,105.31 -- hedging cost £1,482.36
  - C6: actual £152.45 vs. naked £65.82 -- hedging added £86.63

**Year narrative:** 2016 produced a net gain of £713.99 across 10 accounts. The risk committee intervened 36 time(s), raising hedge fractions in response to elevated VaR. 10 customer(s) experienced a bill shock of >=20%.

## 2017

**Trading & Risk**

- Net margin: £976.67 (gross £1,109.46, capital £132.80)
  - Electricity: gross £910.40, capital £122.83, net £787.56
  - Gas: gross £199.06, capital £9.96, net £189.10
- Treasury at year end: £23,264.48
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.90 (avg 0.90), C1g 0.95 (avg 0.95), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 0.95 (avg 0.95), C4 0.85 (avg 0.85), C4g 0.95 (avg 0.95), C5 0.85 (avg 0.85), C6 0.95 (avg 0.95)
- Risk committee (Context Handshake) interventions: 30
  - 2017-01-08: treasury £22,328.04, C1->1.00, C5->1.00, VaR (current £1,430.87 / stressed £448.93) ratio 3.19
  - 2017-02-07: treasury £22,335.97, C1->0.95, C5->0.95, VaR (current £1,430.87 / stressed £448.93) ratio 3.19
  - 2017-03-09: treasury £22,344.65, C1->0.95, C5->0.95, VaR (current £1,430.87 / stressed £448.93) ratio 3.19
  - 2017-01-25: treasury £22,519.19, C1->0.95, C5->0.95, VaR (current £2,529.76 / stressed £906.58) ratio 2.79
  - 2017-02-24: treasury £22,537.13, C1->0.95, C5->0.95, VaR (current £2,529.76 / stressed £906.58) ratio 2.79
  - 2017-03-27: treasury £22,556.31, C1->0.95, C5->0.95, VaR (current £2,529.76 / stressed £906.58) ratio 2.79
  - 2017-01-22: treasury £22,582.23, C1->1.00, C5->1.00, VaR (current £2,587.66 / stressed £933.75) ratio 2.77
  - 2017-02-21: treasury £22,585.96, C1->1.00, C5->1.00, VaR (current £2,587.66 / stressed £933.75) ratio 2.77
  - 2017-05-22: treasury £22,597.32, C1->0.95, C5->0.95, VaR (current £2,587.66 / stressed £933.75) ratio 2.77
  - 2017-06-21: treasury £22,600.70, C1->0.95, C5->0.95, VaR (current £2,587.66 / stressed £933.75) ratio 2.77
  - 2017-02-10: treasury £22,669.11, C1->1.00, C5->1.00, VaR (current £2,699.03 / stressed £987.41) ratio 2.73
  - 2017-03-12: treasury £22,677.23, C1->0.95, C5->0.95, VaR (current £2,699.03 / stressed £987.41) ratio 2.73
  - 2017-04-11: treasury £22,685.37, C1->0.95, C5->0.95, VaR (current £2,699.03 / stressed £987.41) ratio 2.73
  - 2017-05-11: treasury £22,692.30, C1->0.95, C5->0.95, VaR (current £2,699.03 / stressed £987.41) ratio 2.73
  - 2017-06-10: treasury £22,698.77, C1->0.95, C5->0.95, VaR (current £2,699.03 / stressed £987.41) ratio 2.73
  - 2017-07-10: treasury £22,705.75, C1->0.95, C5->0.95, VaR (current £2,699.03 / stressed £987.41) ratio 2.73
  - 2017-08-09: treasury £22,712.73, C1->0.95, C5->0.95, VaR (current £2,699.03 / stressed £987.41) ratio 2.73
  - 2017-09-08: treasury £22,719.40, C1->0.95, C5->0.95, VaR (current £2,699.03 / stressed £987.41) ratio 2.73
  - 2017-09-25: treasury £22,780.59, C1->1.00, C5->1.00, VaR (current £2,699.03 / stressed £987.41) ratio 2.73
  - 2017-01-29: treasury £22,786.54, C5->1.00, VaR (current £2,563.52 / stressed £945.78) ratio 2.71
  - 2017-02-28: treasury £22,791.81, C5->1.00, VaR (current £2,563.52 / stressed £945.78) ratio 2.71
  - 2017-03-30: treasury £22,796.89, C5->1.00, VaR (current £2,563.52 / stressed £945.78) ratio 2.71
  - 2017-04-29: treasury £22,801.02, C5->1.00, VaR (current £2,563.52 / stressed £945.78) ratio 2.71
  - 2017-05-29: treasury £22,804.91, C5->0.95, VaR (current £2,563.52 / stressed £945.78) ratio 2.71
  - 2017-06-28: treasury £22,808.64, C5->0.95, VaR (current £2,563.52 / stressed £945.78) ratio 2.71
  - 2017-07-28: treasury £22,812.34, C5->1.00, VaR (current £2,563.52 / stressed £945.78) ratio 2.71
  - 2017-08-27: treasury £22,816.02, C5->1.00, VaR (current £2,563.52 / stressed £945.78) ratio 2.71
  - 2017-09-26: treasury £22,820.10, C5->1.00, VaR (current £2,563.52 / stressed £945.78) ratio 2.71
  - 2017-10-26: treasury £22,824.31, C5->1.00, VaR (current £2,563.52 / stressed £945.78) ratio 2.71
  - 2017-11-25: treasury £22,829.51, C5->0.95, VaR (current £2,563.52 / stressed £945.78) ratio 2.71
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.78
- Worst single period: C6 on 2017-05-17 period 34, net margin £-0.10

**Customer Book**

- Active accounts: 10 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £1,749.38
- Highest CLV: C6 (£3,450.46); Lowest CLV: C3 (£641.62)
- Bill shock events (>=20%): 13 -- C1 2017-01-31 (25%); C1 2017-04-30 (21%); C5 2017-01-31 (45%); C5 2017-02-28 (23%); C5 2017-05-31 (22%); C5 2017-06-30 (23%); C5 2017-11-30 (62%); C6 2017-05-31 (24%); C6 2017-06-30 (21%); C6 2017-11-30 (55%); C3 2017-07-31 (49%); C3g 2017-07-31 (26%); C4g 2017-10-31 (38%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £88.75-£166.09/MWh, net margin £54.16
- C1g (gas): tariff £17.55-£24.01/MWh, net margin £34.33
- C2 (electricity): tariff £91.21-£100.69/MWh, net margin £105.75
- C2g (gas): tariff £19.18-£23.60/MWh, net margin £58.07
- C3 (electricity): tariff £76.47-£110.09/MWh, net margin £57.86
- C3g (gas): tariff £14.24-£17.38/MWh, net margin £37.42
- C4 (electricity): tariff £80.08-£87.58/MWh, net margin £84.24
- C4g (gas): tariff £15.17-£20.24/MWh, net margin £59.28
- C5 (electricity): tariff £88.75-£166.09/MWh, net margin £313.84
- C6 (electricity): tariff £91.21-£100.69/MWh, net margin £171.71
- Cost to serve per customer (whole-run total, average £618.93, range £95.63-£1,458.12):
  - C1: cost to serve £655.06, net margin after cost to serve £221.49
  - C1g: cost to serve £111.21, net margin after cost to serve £561.02
  - C2: cost to serve £772.86, net margin after cost to serve £1,626.62
  - C2g: cost to serve £133.02, net margin after cost to serve £899.18
  - C3: cost to serve £599.86, net margin after cost to serve £197.00
  - C3g: cost to serve £95.63, net margin after cost to serve £563.12
  - C4: cost to serve £709.09, net margin after cost to serve £803.85
  - C4g: cost to serve £204.67, net margin after cost to serve £986.14
  - C5: cost to serve £1,458.12, net margin after cost to serve £2,822.36
  - C6: cost to serve £1,449.78, net margin after cost to serve £4,100.88

**Portfolio Health**

- Capital cost ratio: 12.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 120, average clarity 0.929, average bill shock 8.8%, bad debt provision £172.79, avg complaint probability 2.9%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £841.51 vs. naked (unhedged) net margin: £1,163.80
- hedging cost £322.29 vs. a fully unhedged book (actual net £841.51 vs. naked net £1,163.80)
  - C1: actual £36.85 vs. naked £77.40 -- hedging cost £40.55
  - C1g: actual £42.53 vs. naked £13.24 -- hedging added £29.29
  - C2: actual £106.10 vs. naked £323.40 -- hedging cost £217.30
  - C2g: actual £58.57 vs. naked £80.93 -- hedging cost £22.37
  - C3: actual £69.00 vs. naked £200.46 -- hedging cost £131.46
  - C3g: actual £40.83 vs. naked £-26.32 -- hedging added £67.15
  - C4: actual £66.21 vs. naked £120.69 -- hedging cost £54.48
  - C4g: actual £69.50 vs. naked £-25.41 -- hedging added £94.92
  - C5: actual £169.41 vs. naked £241.07 -- hedging cost £71.65
  - C6: actual £182.50 vs. naked £158.35 -- hedging added £24.15

**Year narrative:** 2017 produced a net gain of £976.67 across 10 accounts. The risk committee intervened 30 time(s), raising hedge fractions in response to elevated VaR. 13 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £923.74 (gross £1,005.17, capital £81.43)
  - Electricity: gross £770.25, capital £74.27, net £695.99
  - Gas: gross £234.91, capital £7.16, net £227.75
- Treasury at year end: £24,141.85
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 1.00 (avg 1.00), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 1.00 (avg 1.00), C4 0.85 (avg 0.85), C4g 1.00 (avg 1.00), C5 0.85 (avg 0.85), C6 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C5 on 2018-03-01 period 36, net margin £-0.24

**Customer Book**

- Active accounts: 10 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £1,749.38
- Highest CLV: C6 (£3,450.46); Lowest CLV: C3 (£641.62)
- Bill shock events (>=20%): 18 -- C1 2018-01-31 (46%); C1 2018-04-30 (20%); C1g 2018-01-31 (35%); C5 2018-01-31 (47%); C5 2018-04-30 (34%); C5 2018-05-31 (20%); C5 2018-06-30 (23%); C5 2018-10-31 (35%); C5 2018-11-30 (30%); C2 2018-04-30 (22%); C2g 2018-04-30 (26%); C6 2018-05-31 (23%); C6 2018-06-30 (24%); C6 2018-10-31 (33%); C6 2018-11-30 (23%); C3g 2018-07-31 (48%); C4 2018-10-31 (33%); C4g 2018-10-31 (55%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £88.75-£105.29/MWh, net margin £36.83
- C1g (gas): tariff £24.01-£27.98/MWh, net margin £42.62
- C2 (electricity): tariff £100.69-£141.79/MWh, net margin £141.97
- C2g (gas): tariff £23.60-£30.72/MWh, net margin £64.72
- C3 (electricity): tariff £87.90-£110.09/MWh, net margin £55.97
- C3g (gas): tariff £17.38-£24.97/MWh, net margin £46.02
- C4 (electricity): tariff £80.08-£101.06/MWh, net margin £72.14
- C4g (gas): tariff £20.24-£30.42/MWh, net margin £74.39
- C5 (electricity): tariff £88.75-£105.29/MWh, net margin £170.30
- C6 (electricity): tariff £100.69-£141.79/MWh, net margin £218.79
- Cost to serve per customer (whole-run total, average £618.93, range £95.63-£1,458.12):
  - C1: cost to serve £655.06, net margin after cost to serve £221.49
  - C1g: cost to serve £111.21, net margin after cost to serve £561.02
  - C2: cost to serve £772.86, net margin after cost to serve £1,626.62
  - C2g: cost to serve £133.02, net margin after cost to serve £899.18
  - C3: cost to serve £599.86, net margin after cost to serve £197.00
  - C3g: cost to serve £95.63, net margin after cost to serve £563.12
  - C4: cost to serve £709.09, net margin after cost to serve £803.85
  - C4g: cost to serve £204.67, net margin after cost to serve £986.14
  - C5: cost to serve £1,458.12, net margin after cost to serve £2,822.36
  - C6: cost to serve £1,449.78, net margin after cost to serve £4,100.88

**Portfolio Health**

- Capital cost ratio: 8.1% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 120, average clarity 0.926, average bill shock 9.2%, bad debt provision £170.06, avg complaint probability 3.0%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £1,158.60 vs. naked (unhedged) net margin: £3,503.08
- hedging cost £2,344.48 vs. a fully unhedged book (actual net £1,158.60 vs. naked net £3,503.08)
  - C1: actual £61.67 vs. naked £200.20 -- hedging cost £138.52
  - C1g: actual £47.69 vs. naked £167.53 -- hedging cost £119.84
  - C2: actual £161.44 vs. naked £564.65 -- hedging cost £403.22
  - C2g: actual £72.37 vs. naked £126.91 -- hedging cost £54.54
  - C3: actual £50.76 vs. naked £120.80 -- hedging cost £70.04
  - C3g: actual £52.44 vs. naked £72.66 -- hedging cost £20.22
  - C4: actual £108.57 vs. naked £337.71 -- hedging cost £229.14
  - C4g: actual £91.52 vs. naked £300.10 -- hedging cost £208.58
  - C5: actual £279.48 vs. naked £838.34 -- hedging cost £558.86
  - C6: actual £232.66 vs. naked £774.18 -- hedging cost £541.52

**Year narrative:** 2018 produced a net gain of £923.74 across 10 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 18 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £1,128.75 (gross £1,211.17, capital £82.42)
  - Electricity: gross £945.38, capital £76.79, net £868.58
  - Gas: gross £265.80, capital £5.63, net £260.17
- Treasury at year end: £25,271.89
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 0.90 (avg 0.90), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 0.90 (avg 0.90), C4 0.85 (avg 0.85), C4g 0.90 (avg 0.90), C5 0.85 (avg 0.85), C6 0.90 (avg 0.90)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C5 on 2019-12-31 period 6, net margin £-0.04

**Customer Book**

- Active accounts: 10 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £1,749.38
- Highest CLV: C6 (£3,450.46); Lowest CLV: C3 (£641.62)
- Bill shock events (>=20%): 17 -- C1 2019-04-30 (24%); C5 2019-01-31 (42%); C5 2019-02-28 (22%); C5 2019-06-30 (28%); C5 2019-10-31 (48%); C5 2019-11-30 (39%); C2 2019-04-30 (41%); C6 2019-02-28 (21%); C6 2019-04-30 (44%); C6 2019-06-30 (26%); C6 2019-09-30 (22%); C6 2019-10-31 (45%); C6 2019-11-30 (29%); C3 2019-04-30 (22%); C3g 2019-07-31 (29%); C4 2019-10-31 (26%); C4g 2019-10-31 (57%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £79.54-£105.29/MWh, net margin £61.69
- C1g (gas): tariff £16.65-£27.98/MWh, net margin £47.56
- C2 (electricity): tariff £100.16-£141.79/MWh, net margin £132.88
- C2g (gas): tariff £25.67-£30.72/MWh, net margin £79.27
- C3 (electricity): tariff £78.50-£87.90/MWh, net margin £54.38
- C3g (gas): tariff £17.08-£24.97/MWh, net margin £50.25
- C4 (electricity): tariff £70.47-£101.06/MWh, net margin £103.14
- C4g (gas): tariff £12.80-£30.42/MWh, net margin £83.09
- C5 (electricity): tariff £79.54-£105.29/MWh, net margin £279.84
- C6 (electricity): tariff £100.16-£141.79/MWh, net margin £236.65
- Cost to serve per customer (whole-run total, average £618.93, range £95.63-£1,458.12):
  - C1: cost to serve £655.06, net margin after cost to serve £221.49
  - C1g: cost to serve £111.21, net margin after cost to serve £561.02
  - C2: cost to serve £772.86, net margin after cost to serve £1,626.62
  - C2g: cost to serve £133.02, net margin after cost to serve £899.18
  - C3: cost to serve £599.86, net margin after cost to serve £197.00
  - C3g: cost to serve £95.63, net margin after cost to serve £563.12
  - C4: cost to serve £709.09, net margin after cost to serve £803.85
  - C4g: cost to serve £204.67, net margin after cost to serve £986.14
  - C5: cost to serve £1,458.12, net margin after cost to serve £2,822.36
  - C6: cost to serve £1,449.78, net margin after cost to serve £4,100.88

**Portfolio Health**

- Capital cost ratio: 6.8% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 120, average clarity 0.925, average bill shock 9.7%, bad debt provision £165.51, avg complaint probability 3.0%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £977.69 vs. naked (unhedged) net margin: £2,772.99
- hedging cost £1,795.30 vs. a fully unhedged book (actual net £977.69 vs. naked net £2,772.99)
  - C1: actual £45.18 vs. naked £131.94 -- hedging cost £86.76
  - C1g: actual £42.01 vs. naked £83.93 -- hedging cost £41.92
  - C2: actual £121.93 vs. naked £429.46 -- hedging cost £307.52
  - C2g: actual £79.87 vs. naked £209.58 -- hedging cost £129.71
  - C3: actual £56.17 vs. naked £174.78 -- hedging cost £118.61
  - C3g: actual £50.44 vs. naked £108.02 -- hedging cost £57.58
  - C4: actual £79.86 vs. naked £240.36 -- hedging cost £160.50
  - C4g: actual £65.08 vs. naked £92.34 -- hedging cost £27.25
  - C5: actual £196.77 vs. naked £518.03 -- hedging cost £321.27
  - C6: actual £240.38 vs. naked £784.55 -- hedging cost £544.17

**Year narrative:** 2019 produced a net gain of £1,128.75 across 10 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 17 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £948.73 (gross £1,091.31, capital £142.59)
  - Electricity: gross £884.23, capital £134.66, net £749.57
  - Gas: gross £207.08, capital £7.93, net £199.15
- Treasury at year end: £26,263.66
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 0.85 (avg 0.85), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 0.85 (avg 0.85), C4 0.85 (avg 0.85), C4g 0.85 (avg 0.85), C5 0.85 (avg 0.85), C6 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C5 on 2020-03-04 period 37, net margin £-0.95

**Customer Book**

- Active accounts: 10 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £1,749.38
- Highest CLV: C6 (£3,450.46); Lowest CLV: C3 (£641.62)
- Bill shock events (>=20%): 15 -- C1 2020-01-31 (24%); C1 2020-04-30 (23%); C1g 2020-01-31 (40%); C5 2020-01-31 (24%); C5 2020-04-30 (31%); C5 2020-10-31 (42%); C5 2020-11-30 (21%); C5 2020-12-31 (31%); C2g 2020-04-30 (47%); C6 2020-09-30 (23%); C6 2020-10-31 (37%); C6 2020-12-31 (27%); C3 2020-04-30 (21%); C3 2020-07-31 (24%); C3g 2020-07-31 (50%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £79.54-£113.28/MWh, net margin £44.92
- C1g (gas): tariff £16.65-£19.29/MWh, net margin £42.04
- C2 (electricity): tariff £100.16-£113.28/MWh, net margin £136.01
- C2g (gas): tariff £13.91-£25.67/MWh, net margin £56.03
- C3 (electricity): tariff £57.17-£78.50/MWh, net margin £43.60
- C3g (gas): tariff £8.19-£17.08/MWh, net margin £38.16
- C4 (electricity): tariff £70.47-£76.39/MWh, net margin £78.76
- C4g (gas): tariff £12.80-£13.41/MWh, net margin £62.92
- C5 (electricity): tariff £79.54-£113.28/MWh, net margin £194.67
- C6 (electricity): tariff £100.16-£113.28/MWh, net margin £251.61
- Cost to serve per customer (whole-run total, average £618.93, range £95.63-£1,458.12):
  - C1: cost to serve £655.06, net margin after cost to serve £221.49
  - C1g: cost to serve £111.21, net margin after cost to serve £561.02
  - C2: cost to serve £772.86, net margin after cost to serve £1,626.62
  - C2g: cost to serve £133.02, net margin after cost to serve £899.18
  - C3: cost to serve £599.86, net margin after cost to serve £197.00
  - C3g: cost to serve £95.63, net margin after cost to serve £563.12
  - C4: cost to serve £709.09, net margin after cost to serve £803.85
  - C4g: cost to serve £204.67, net margin after cost to serve £986.14
  - C5: cost to serve £1,458.12, net margin after cost to serve £2,822.36
  - C6: cost to serve £1,449.78, net margin after cost to serve £4,100.88

**Portfolio Health**

- Capital cost ratio: 13.1% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 120, average clarity 0.929, average bill shock 8.5%, bad debt provision £132.24, avg complaint probability 2.8%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £567.28 vs. naked (unhedged) net margin: £-598.05
- hedging added £1,165.34 vs. a fully unhedged book (actual net £567.28 vs. naked net £-598.05)
  - C1: actual £19.27 vs. naked £-94.21 -- hedging added £113.48
  - C1g: actual £-9.87 vs. naked £-291.16 -- hedging added £281.29
  - C2: actual £131.37 vs. naked £451.98 -- hedging cost £320.61
  - C2g: actual £42.05 vs. naked £33.35 -- hedging added £8.69
  - C3: actual £18.66 vs. naked £-33.61 -- hedging added £52.27
  - C3g: actual £13.15 vs. naked £-108.33 -- hedging added £121.48
  - C4: actual £39.57 vs. naked £-46.41 -- hedging added £85.98
  - C4g: actual £13.23 vs. naked £-269.21 -- hedging added £282.44
  - C5: actual £60.20 vs. naked £-707.00 -- hedging added £767.20
  - C6: actual £239.66 vs. naked £466.54 -- hedging cost £226.88

**Year narrative:** 2020 produced a net gain of £948.73 across 10 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 15 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £632.78 (gross £1,110.17, capital £477.39)
  - Electricity: gross £1,027.27, capital £467.30, net £559.97
  - Gas: gross £82.89, capital £10.08, net £72.81
- Treasury at year end: £26,889.30
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.95 (avg 0.95), C1g 0.95 (avg 0.95), C2 0.85 (avg 0.85), C2g 0.95 (avg 0.95), C3 0.95 (avg 0.95), C3g 0.95 (avg 0.95), C4 0.95 (avg 0.95), C4g 0.95 (avg 0.95), C5 0.95 (avg 0.95), C6 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 12
  - 2021-03-31: treasury £26,958.60, C2->0.95, C6->0.95, VaR (current £4,916.52 / stressed £1,777.28) ratio 2.77
  - 2021-04-30: treasury £26,973.68, C2->0.95, C6->0.95, VaR (current £4,916.52 / stressed £1,777.28) ratio 2.77
  - 2021-06-29: treasury £27,016.44, C2->0.95, C6->0.95, VaR (current £4,916.52 / stressed £1,777.28) ratio 2.77
  - 2021-07-29: treasury £27,021.33, C2->0.95, C6->0.95, VaR (current £4,916.52 / stressed £1,777.28) ratio 2.77
  - 2021-08-28: treasury £27,024.73, C2->0.95, C6->0.95, VaR (current £4,916.52 / stressed £1,777.28) ratio 2.77
  - 2021-09-27: treasury £27,015.62, C2->0.95, C6->0.95, VaR (current £4,916.52 / stressed £1,777.28) ratio 2.77
  - 2021-10-27: treasury £27,021.87, C2->0.95, C6->0.95, VaR (current £4,916.52 / stressed £1,777.28) ratio 2.77
  - 2021-11-26: treasury £27,035.20, C2->1.00, C6->1.00, VaR (current £4,916.52 / stressed £1,777.28) ratio 2.77
  - 2021-12-26: treasury £27,041.25, C2->0.95, C6->0.95, VaR (current £4,916.52 / stressed £1,777.28) ratio 2.77
  - 2021-07-25: treasury £27,084.71, C2->0.95, C3->1.00, C6->0.95, VaR (current £4,938.87 / stressed £1,779.47) ratio 2.78
  - 2021-10-23: treasury £27,099.85, C2->0.95, C3->1.00, C6->0.95, VaR (current £4,938.87 / stressed £1,779.47) ratio 2.78
  - 2021-11-22: treasury £27,105.84, C2->0.95, C3->1.00, C6->0.95, VaR (current £4,938.87 / stressed £1,779.47) ratio 2.78
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.77
- Worst single period: C5 on 2021-01-08 period 39, net margin £-2.07

**Customer Book**

- Active accounts: 10 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £1,749.38
- Highest CLV: C6 (£3,450.46); Lowest CLV: C3 (£641.62)
- Bill shock events (>=20%): 21 -- C1 2021-01-31 (39%); C1 2021-04-30 (22%); C1 2021-12-31 (22%); C1g 2021-12-31 (36%); C5 2021-01-31 (49%); C5 2021-05-31 (24%); C5 2021-06-30 (34%); C5 2021-10-31 (33%); C5 2021-11-30 (55%); C5 2021-12-31 (21%); C2 2021-04-30 (80%); C2g 2021-04-30 (76%); C6 2021-04-30 (94%); C6 2021-06-30 (37%); C6 2021-10-31 (29%); C6 2021-11-30 (53%); C3 2021-04-30 (21%); C3 2021-07-31 (212%); C3g 2021-07-31 (281%); C4 2021-10-31 (394%); C4g 2021-10-31 (356%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £113.28-£430.44/MWh, net margin £19.79
- C1g (gas): tariff £19.29-£112.52/MWh, net margin £-9.74 -- **net-negative**
- C2 (electricity): tariff £113.28-£247.59/MWh, net margin £189.73
- C2g (gas): tariff £13.91-£26.02/MWh, net margin £32.64
- C3 (electricity): tariff £57.17-£185.57/MWh, net margin £37.18
- C3g (gas): tariff £8.19-£33.32/MWh, net margin £18.85
- C4 (electricity): tariff £76.39-£411.48/MWh, net margin £94.41
- C4g (gas): tariff £13.41-£66.99/MWh, net margin £31.06
- C5 (electricity): tariff £113.28-£430.44/MWh, net margin £59.31
- C6 (electricity): tariff £113.28-£247.59/MWh, net margin £159.55
- Cost to serve per customer (whole-run total, average £618.93, range £95.63-£1,458.12):
  - C1: cost to serve £655.06, net margin after cost to serve £221.49
  - C1g: cost to serve £111.21, net margin after cost to serve £561.02
  - C2: cost to serve £772.86, net margin after cost to serve £1,626.62
  - C2g: cost to serve £133.02, net margin after cost to serve £899.18
  - C3: cost to serve £599.86, net margin after cost to serve £197.00
  - C3g: cost to serve £95.63, net margin after cost to serve £563.12
  - C4: cost to serve £709.09, net margin after cost to serve £803.85
  - C4g: cost to serve £204.67, net margin after cost to serve £986.14
  - C5: cost to serve £1,458.12, net margin after cost to serve £2,822.36
  - C6: cost to serve £1,449.78, net margin after cost to serve £4,100.88

**Portfolio Health**

- Capital cost ratio: 43.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 120, average clarity 0.904, average bill shock 21.1%, bad debt provision £231.02, avg complaint probability 3.7%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £1,733.17 vs. naked (unhedged) net margin: £-128.58
- hedging added £1,861.75 vs. a fully unhedged book (actual net £1,733.17 vs. naked net £-128.58)
  - C1: actual £151.58 vs. naked £556.64 -- hedging cost £405.06
  - C1g: actual £118.89 vs. naked £6.63 -- hedging added £112.26
  - C2: actual £201.97 vs. naked £511.28 -- hedging cost £309.32
  - C2g: actual £28.08 vs. naked £-528.73 -- hedging added £556.81
  - C3: actual £63.48 vs. naked £-89.05 -- hedging added £152.52
  - C3g: actual £28.02 vs. naked £-604.64 -- hedging added £632.67
  - C4: actual £271.36 vs. naked £935.47 -- hedging cost £664.11
  - C4g: actual £100.08 vs. naked £-899.06 -- hedging added £999.15
  - C5: actual £648.43 vs. naked £1,358.80 -- hedging cost £710.38
  - C6: actual £121.28 vs. naked £-1,375.94 -- hedging added £1,497.22

**Year narrative:** 2021 (flagged crisis year) produced a net gain of £632.78 across 10 accounts. The risk committee intervened 12 time(s), raising hedge fractions in response to elevated VaR. 21 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £2,530.50 (gross £2,967.32, capital £436.82)
  - Electricity: gross £2,446.08, capital £424.86, net £2,021.22
  - Gas: gross £521.24, capital £11.96, net £509.28
- Treasury at year end: £28,740.84
- Hedge fraction at first renewal this year (avg across year's terms): C1 1.00 (avg 1.00), C1g 1.00 (avg 1.00), C2 0.95 (avg 0.95), C2g 1.00 (avg 1.00), C3 1.00 (avg 1.00), C3g 1.00 (avg 1.00), C4 1.00 (avg 1.00), C4g 1.00 (avg 1.00), C5 1.00 (avg 1.00), C6 0.95 (avg 0.95)
- Risk committee (Context Handshake) interventions: 20
  - 2022-01-25: treasury £27,055.65, C2->0.95, C6->0.95, VaR (current £4,916.52 / stressed £1,777.28) ratio 2.77
  - 2022-03-26: treasury £27,080.64, C2->0.95, C6->0.95, VaR (current £4,916.52 / stressed £1,777.28) ratio 2.77
  - 2022-01-21: treasury £27,116.78, C2->0.95, C3->1.00, C6->0.95, VaR (current £4,938.87 / stressed £1,779.47) ratio 2.78
  - 2022-04-21: treasury £27,132.33, C2->0.95, C3->1.00, C6->0.95, VaR (current £4,938.87 / stressed £1,779.47) ratio 2.78
  - 2022-05-21: treasury £27,137.78, C2->0.95, C3->1.00, C6->0.95, VaR (current £4,938.87 / stressed £1,779.47) ratio 2.78
  - 2022-06-20: treasury £27,142.67, C2->0.95, C3->1.00, C6->0.95, VaR (current £4,938.87 / stressed £1,779.47) ratio 2.78
  - 2022-03-11: treasury £27,304.09, C2->0.95, C3->1.00, C4->1.00, C6->0.95, VaR (current £5,122.71 / stressed £1,818.41) ratio 2.82
  - 2022-03-30: treasury £27,587.01, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C6->0.95, VaR (current £5,168.87 / stressed £1,828.48) ratio 2.83
  - 2022-06-28: treasury £27,621.62, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C6->0.95, VaR (current £5,168.87 / stressed £1,828.48) ratio 2.83
  - 2022-08-27: treasury £27,640.31, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C6->0.95, VaR (current £5,168.87 / stressed £1,828.48) ratio 2.83
  - 2022-11-25: treasury £27,679.15, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C6->0.95, VaR (current £5,168.87 / stressed £1,828.48) ratio 2.83
  - 2022-12-25: treasury £27,692.32, C1->1.00, C2->1.00, C3->1.00, C4->1.00, C6->1.00, VaR (current £5,168.87 / stressed £1,828.48) ratio 2.83
  - 2022-03-17: treasury £28,011.76, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C5->1.00, C6->0.95, VaR (current £5,581.02 / stressed £1,918.34) ratio 2.91
  - 2022-04-16: treasury £28,077.35, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C5->1.00, C6->0.95, VaR (current £5,581.02 / stressed £1,918.34) ratio 2.91
  - 2022-06-15: treasury £28,167.51, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C5->1.00, C6->0.95, VaR (current £5,581.02 / stressed £1,918.34) ratio 2.91
  - 2022-07-15: treasury £28,197.43, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C5->1.00, C6->0.95, VaR (current £5,581.02 / stressed £1,918.34) ratio 2.91
  - 2022-08-14: treasury £28,223.56, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C5->1.00, C6->0.95, VaR (current £5,581.02 / stressed £1,918.34) ratio 2.91
  - 2022-09-13: treasury £28,246.40, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C5->1.00, C6->0.95, VaR (current £5,581.02 / stressed £1,918.34) ratio 2.91
  - 2022-04-12: treasury £28,473.58, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C6->0.95, VaR (current £5,444.80 / stressed £1,889.43) ratio 2.88
  - 2022-11-08: treasury £28,679.45, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C6->0.95, VaR (current £5,444.80 / stressed £1,889.43) ratio 2.88
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.84
- Worst single period: C6 on 2022-01-24 period 34, net margin £-2.36

**Customer Book**

- Active accounts: 10 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £1,749.38
- Highest CLV: C6 (£3,450.46); Lowest CLV: C3 (£641.62)
- Bill shock events (>=20%): 21 -- C1 2022-01-31 (223%); C1 2022-04-30 (21%); C1g 2022-01-31 (345%); C5 2022-01-31 (276%); C5 2022-02-28 (21%); C5 2022-04-30 (21%); C5 2022-05-31 (27%); C5 2022-11-30 (52%); C5 2022-12-31 (36%); C2 2022-04-30 (75%); C2g 2022-03-31 (26%); C2g 2022-04-30 (347%); C6 2022-04-30 (64%); C6 2022-05-31 (24%); C6 2022-09-30 (27%); C6 2022-11-30 (45%); C6 2022-12-31 (34%); C3 2022-07-31 (52%); C3g 2022-07-31 (201%); C4 2022-10-31 (29%); C4g 2022-10-31 (203%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £400.33-£430.44/MWh, net margin £152.17
- C1g (gas): tariff £108.96-£112.52/MWh, net margin £119.40
- C2 (electricity): tariff £247.59-£521.36/MWh, net margin £320.33
- C2g (gas): tariff £26.02-£136.66/MWh, net margin £140.74
- C3 (electricity): tariff £185.57-£276.59/MWh, net margin £82.29
- C3g (gas): tariff £33.32-£103.79/MWh, net margin £79.45
- C4 (electricity): tariff £411.48-£506.37/MWh, net margin £275.70
- C4g (gas): tariff £66.99-£210.22/MWh, net margin £169.69
- C5 (electricity): tariff £400.33-£430.44/MWh, net margin £655.78
- C6 (electricity): tariff £247.59-£521.36/MWh, net margin £534.93
- Cost to serve per customer (whole-run total, average £618.93, range £95.63-£1,458.12):
  - C1: cost to serve £655.06, net margin after cost to serve £221.49
  - C1g: cost to serve £111.21, net margin after cost to serve £561.02
  - C2: cost to serve £772.86, net margin after cost to serve £1,626.62
  - C2g: cost to serve £133.02, net margin after cost to serve £899.18
  - C3: cost to serve £599.86, net margin after cost to serve £197.00
  - C3g: cost to serve £95.63, net margin after cost to serve £563.12
  - C4: cost to serve £709.09, net margin after cost to serve £803.85
  - C4g: cost to serve £204.67, net margin after cost to serve £986.14
  - C5: cost to serve £1,458.12, net margin after cost to serve £2,822.36
  - C6: cost to serve £1,449.78, net margin after cost to serve £4,100.88

**Portfolio Health**

- Capital cost ratio: 14.7% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 120, average clarity 0.902, average bill shock 22.5%, bad debt provision £605.58, avg complaint probability 3.8%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £3,116.95 vs. naked (unhedged) net margin: £16,237.70
- hedging cost £13,120.76 vs. a fully unhedged book (actual net £3,116.95 vs. naked net £16,237.70)
  - C1: actual £121.31 vs. naked £968.92 -- hedging cost £847.61
  - C1g: actual £121.55 vs. naked £786.35 -- hedging cost £664.80
  - C2: actual £386.91 vs. naked £2,115.46 -- hedging cost £1,728.55
  - C2g: actual £183.51 vs. naked £529.89 -- hedging cost £346.38
  - C3: actual £102.50 vs. naked £317.54 -- hedging cost £215.04
  - C3g: actual £136.30 vs. naked £253.82 -- hedging cost £117.51
  - C4: actual £287.64 vs. naked £2,432.33 -- hedging cost £2,144.69
  - C4g: actual £392.14 vs. naked £3,257.10 -- hedging cost £2,864.96
  - C5: actual £576.15 vs. naked £3,936.28 -- hedging cost £3,360.13
  - C6: actual £808.94 vs. naked £1,640.03 -- hedging cost £831.09

**Year narrative:** 2022 (flagged crisis year) produced a net gain of £2,530.50 across 10 accounts. The risk committee intervened 20 time(s), raising hedge fractions in response to elevated VaR. 21 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £3,667.51 (gross £4,178.76, capital £511.25)
  - Electricity: gross £3,274.23, capital £477.15, net £2,797.08
  - Gas: gross £904.52, capital £34.10, net £870.42
- Treasury at year end: £32,053.49
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.90 (avg 0.90), C1g 0.90 (avg 0.90), C2 0.85 (avg 0.85), C2g 0.90 (avg 0.90), C3 0.90 (avg 0.90), C3g 0.90 (avg 0.90), C4 0.90 (avg 0.90), C4g 0.90 (avg 0.90), C5 0.90 (avg 0.90), C6 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 1
  - 2023-03-08: treasury £28,822.56, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C6->0.95, VaR (current £5,444.80 / stressed £1,889.43) ratio 2.88
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.88
- Worst single period: C2g on 2023-03-31 period 1, net margin £-1.13

**Customer Book**

- Active accounts: 10 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £1,749.38
- Highest CLV: C6 (£3,450.46); Lowest CLV: C3 (£641.62)
- Bill shock events (>=20%): 16 -- C1 2023-04-30 (21%); C5 2023-05-31 (23%); C5 2023-06-30 (26%); C5 2023-10-31 (33%); C5 2023-11-30 (55%); C2 2023-04-30 (44%); C2g 2023-04-30 (41%); C6 2023-04-30 (48%); C6 2023-05-31 (24%); C6 2023-06-30 (24%); C6 2023-10-31 (41%); C6 2023-11-30 (46%); C3 2023-07-31 (28%); C3g 2023-07-31 (51%); C4 2023-10-31 (63%); C4g 2023-10-31 (79%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £199.60-£400.33/MWh, net margin £120.90
- C1g (gas): tariff £51.19-£108.96/MWh, net margin £120.74
- C2 (electricity): tariff £335.91-£521.36/MWh, net margin £582.61
- C2g (gas): tariff £82.03-£136.66/MWh, net margin £265.13
- C3 (electricity): tariff £189.75-£276.59/MWh, net margin £147.04
- C3g (gas): tariff £48.52-£103.79/MWh, net margin £143.62
- C4 (electricity): tariff £174.99-£506.37/MWh, net margin £285.10
- C4g (gas): tariff £42.02-£210.22/MWh, net margin £340.93
- C5 (electricity): tariff £199.60-£400.33/MWh, net margin £569.62
- C6 (electricity): tariff £335.91-£521.36/MWh, net margin £1,091.81
- Cost to serve per customer (whole-run total, average £618.93, range £95.63-£1,458.12):
  - C1: cost to serve £655.06, net margin after cost to serve £221.49
  - C1g: cost to serve £111.21, net margin after cost to serve £561.02
  - C2: cost to serve £772.86, net margin after cost to serve £1,626.62
  - C2g: cost to serve £133.02, net margin after cost to serve £899.18
  - C3: cost to serve £599.86, net margin after cost to serve £197.00
  - C3g: cost to serve £95.63, net margin after cost to serve £563.12
  - C4: cost to serve £709.09, net margin after cost to serve £803.85
  - C4g: cost to serve £204.67, net margin after cost to serve £986.14
  - C5: cost to serve £1,458.12, net margin after cost to serve £2,822.36
  - C6: cost to serve £1,449.78, net margin after cost to serve £4,100.88

**Portfolio Health**

- Capital cost ratio: 12.2% of gross
- Treasury drawdown events (>=10% threshold): 183 -- £33,995.86 -> £30,301.78 (10.9%); £33,996.30 -> £30,302.49 (10.9%); £33,996.74 -> £30,303.20 (10.9%); £33,997.18 -> £30,303.93 (10.9%); £33,997.62 -> £30,304.63 (10.9%); £33,998.06 -> £30,305.34 (10.9%); £33,998.50 -> £30,306.04 (10.9%); £33,998.94 -> £30,306.75 (10.9%); £33,999.38 -> £30,307.45 (10.9%); £33,999.82 -> £30,308.17 (10.9%); £34,000.26 -> £30,308.89 (10.9%); £34,000.70 -> £30,309.60 (10.9%); £34,001.14 -> £30,310.30 (10.9%); £34,001.58 -> £30,311.01 (10.9%); £34,002.02 -> £30,311.71 (10.9%); £34,002.46 -> £30,312.42 (10.9%); £34,002.90 -> £30,313.13 (10.9%); £34,003.34 -> £30,313.86 (10.9%); £34,003.78 -> £30,314.56 (10.8%); £34,004.22 -> £30,315.27 (10.8%); £34,004.66 -> £30,315.97 (10.8%); £34,005.10 -> £30,316.68 (10.8%); £34,005.54 -> £30,317.39 (10.8%); £34,005.98 -> £30,318.09 (10.8%); £34,006.42 -> £30,318.81 (10.8%); £34,006.86 -> £30,319.51 (10.8%); £34,007.30 -> £30,320.21 (10.8%); £34,007.74 -> £30,320.92 (10.8%); £34,008.18 -> £30,321.62 (10.8%); £34,008.62 -> £30,322.32 (10.8%); £34,009.06 -> £30,323.02 (10.8%); £34,009.50 -> £30,323.75 (10.8%); £34,009.93 -> £30,324.45 (10.8%); £34,010.36 -> £30,325.15 (10.8%); £34,010.79 -> £30,325.86 (10.8%); £34,011.22 -> £30,326.56 (10.8%); £34,011.65 -> £30,327.26 (10.8%); £34,012.07 -> £30,327.96 (10.8%); £34,012.50 -> £30,328.68 (10.8%); £34,012.93 -> £30,329.39 (10.8%); £34,013.36 -> £30,330.09 (10.8%); £34,013.79 -> £30,330.80 (10.8%); £34,014.22 -> £30,331.50 (10.8%); £34,014.65 -> £30,332.20 (10.8%); £34,015.08 -> £30,332.90 (10.8%); £34,015.50 -> £30,333.62 (10.8%); £34,015.93 -> £30,334.33 (10.8%); £34,016.36 -> £30,335.03 (10.8%); £34,016.79 -> £30,335.73 (10.8%); £34,017.22 -> £30,336.44 (10.8%); £34,017.65 -> £30,337.14 (10.8%); £34,018.08 -> £30,337.84 (10.8%); £34,018.51 -> £30,338.56 (10.8%); £34,018.93 -> £30,339.27 (10.8%); £34,019.36 -> £30,339.97 (10.8%); £34,019.79 -> £30,340.67 (10.8%); £34,020.22 -> £30,341.38 (10.8%); £34,020.65 -> £30,342.08 (10.8%); £34,021.08 -> £30,342.78 (10.8%); £34,021.51 -> £30,343.50 (10.8%); £34,021.94 -> £30,344.21 (10.8%); £34,022.36 -> £30,344.91 (10.8%); £34,022.79 -> £30,345.61 (10.8%); £34,023.21 -> £30,346.32 (10.8%); £34,023.63 -> £30,347.02 (10.8%); £34,024.05 -> £30,347.72 (10.8%); £34,024.47 -> £30,348.44 (10.8%); £34,024.89 -> £30,349.20 (10.8%); £34,025.31 -> £30,349.96 (10.8%); £34,025.74 -> £30,350.71 (10.8%); £34,026.16 -> £30,351.48 (10.8%); £34,026.58 -> £30,352.25 (10.8%); £34,027.00 -> £30,353.03 (10.8%); £34,027.42 -> £30,353.81 (10.8%); £34,027.84 -> £30,354.56 (10.8%); £34,028.26 -> £30,355.32 (10.8%); £34,028.68 -> £30,356.08 (10.8%); £34,029.10 -> £30,356.83 (10.8%); £34,029.52 -> £30,357.59 (10.8%); £34,029.94 -> £30,358.36 (10.8%); £34,030.36 -> £30,359.14 (10.8%); £34,030.78 -> £30,359.89 (10.8%); £34,031.20 -> £30,360.65 (10.8%); £34,031.62 -> £30,361.41 (10.8%); £34,032.04 -> £30,362.16 (10.8%); £34,032.46 -> £30,362.92 (10.8%); £34,032.88 -> £30,363.69 (10.8%); £34,033.30 -> £30,364.46 (10.8%); £34,033.72 -> £30,365.22 (10.8%); £34,034.14 -> £30,365.98 (10.8%); £34,034.56 -> £30,366.74 (10.8%); £34,034.98 -> £30,367.49 (10.8%); £34,440.72 -> £30,848.23 (10.4%); £34,441.25 -> £30,848.55 (10.4%); £34,441.78 -> £30,848.87 (10.4%); £34,442.31 -> £30,849.18 (10.4%); £34,442.84 -> £30,849.49 (10.4%); £34,443.37 -> £30,849.80 (10.4%); £34,443.90 -> £30,850.11 (10.4%); £34,444.43 -> £30,850.42 (10.4%); £34,444.96 -> £30,850.74 (10.4%); £34,445.49 -> £30,851.06 (10.4%); £34,446.02 -> £30,851.37 (10.4%); £34,446.55 -> £30,851.68 (10.4%); £34,447.07 -> £30,851.99 (10.4%); £34,447.60 -> £30,852.30 (10.4%); £34,448.13 -> £30,852.61 (10.4%); £34,448.66 -> £30,852.93 (10.4%); £34,449.19 -> £30,853.25 (10.4%); £34,449.72 -> £30,853.56 (10.4%); £34,450.25 -> £30,853.87 (10.4%); £34,450.78 -> £30,854.18 (10.4%); £34,451.31 -> £30,854.49 (10.4%); £34,451.84 -> £30,854.80 (10.4%); £34,452.37 -> £30,855.12 (10.4%); £34,452.90 -> £30,855.44 (10.4%); £34,453.43 -> £30,855.75 (10.4%); £34,453.96 -> £30,856.06 (10.4%); £34,454.49 -> £30,856.37 (10.4%); £34,455.02 -> £30,856.68 (10.4%); £34,455.55 -> £30,856.99 (10.4%); £34,456.08 -> £30,857.31 (10.4%); £34,456.61 -> £30,857.72 (10.4%); £34,457.13 -> £30,858.11 (10.4%); £34,457.66 -> £30,858.50 (10.4%); £34,458.18 -> £30,858.89 (10.4%); £34,458.70 -> £30,859.27 (10.4%); £34,459.23 -> £30,859.66 (10.4%); £34,459.75 -> £30,860.05 (10.4%); £34,460.27 -> £30,860.47 (10.4%); £34,460.79 -> £30,860.85 (10.4%); £34,461.32 -> £30,861.24 (10.4%); £34,461.84 -> £30,861.63 (10.4%); £34,462.36 -> £30,862.02 (10.4%); £34,462.88 -> £30,862.41 (10.4%); £34,463.41 -> £30,862.80 (10.4%); £34,463.93 -> £30,863.21 (10.4%); £34,464.45 -> £30,863.60 (10.4%); £34,464.98 -> £30,863.99 (10.4%); £34,465.50 -> £30,864.38 (10.4%); £34,466.02 -> £30,864.76 (10.4%); £34,466.54 -> £30,865.15 (10.4%); £34,467.07 -> £30,865.54 (10.4%); £34,467.59 -> £30,865.96 (10.4%); £34,468.11 -> £30,866.34 (10.4%); £34,468.63 -> £30,866.73 (10.4%); £34,469.16 -> £30,867.12 (10.5%); £34,469.68 -> £30,867.51 (10.5%); £34,470.20 -> £30,867.90 (10.5%); £34,470.72 -> £30,868.29 (10.5%); £34,471.25 -> £30,868.70 (10.5%); £34,471.77 -> £30,869.09 (10.5%); £34,472.29 -> £30,869.48 (10.5%); £34,472.82 -> £30,869.86 (10.5%); £34,473.38 -> £30,870.25 (10.5%); £34,473.94 -> £30,870.64 (10.5%); £34,474.50 -> £30,871.03 (10.5%); £34,475.07 -> £30,871.45 (10.5%); £34,475.63 -> £30,871.83 (10.5%); £34,476.19 -> £30,872.22 (10.5%); £34,476.76 -> £30,872.61 (10.5%); £34,477.32 -> £30,873.00 (10.5%); £34,477.88 -> £30,873.39 (10.5%); £34,478.45 -> £30,873.78 (10.5%); £34,479.01 -> £30,874.19 (10.5%); £34,479.57 -> £30,874.58 (10.5%); £34,480.14 -> £30,874.97 (10.5%); £34,480.70 -> £30,875.35 (10.5%); £34,481.26 -> £30,875.74 (10.5%); £34,481.82 -> £30,876.13 (10.5%); £34,482.39 -> £30,876.52 (10.5%); £34,482.95 -> £30,876.93 (10.5%); £34,483.51 -> £30,877.32 (10.5%); £34,484.08 -> £30,877.71 (10.5%); £34,484.64 -> £30,878.10 (10.5%); £34,485.20 -> £30,878.49 (10.5%); £34,485.77 -> £30,878.88 (10.5%); £34,486.33 -> £30,879.27 (10.5%); £34,486.89 -> £30,879.68 (10.5%); £34,487.46 -> £30,880.07 (10.5%); £34,488.02 -> £30,880.46 (10.5%); £34,488.58 -> £30,880.84 (10.5%); £34,489.15 -> £30,881.23 (10.5%)
- Bills issued: 120, average clarity 0.923, average bill shock 9.8%, bad debt provision £599.54, avg complaint probability 3.0%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £4,136.40 vs. naked (unhedged) net margin: £6,266.97
- hedging cost £2,130.57 vs. a fully unhedged book (actual net £4,136.40 vs. naked net £6,266.97)
  - C1: actual £173.85 vs. naked £341.13 -- hedging cost £167.28
  - C1g: actual £140.72 vs. naked £139.71 -- hedging added £1.01
  - C2: actual £655.42 vs. naked £1,610.75 -- hedging cost £955.34
  - C2g: actual £294.66 vs. naked £538.26 -- hedging cost £243.60
  - C3: actual £197.27 vs. naked £385.50 -- hedging cost £188.23
  - C3g: actual £155.87 vs. naked £146.61 -- hedging added £9.26
  - C4: actual £289.23 vs. naked £559.40 -- hedging cost £270.18
  - C4g: actual £207.04 vs. naked £106.13 -- hedging added £100.92
  - C5: actual £752.54 vs. naked £1,048.78 -- hedging cost £296.24
  - C6: actual £1,269.80 vs. naked £1,390.69 -- hedging cost £120.89

**Year narrative:** 2023 produced a net gain of £3,667.51 across 10 accounts. The risk committee intervened 1 time(s), raising hedge fractions in response to elevated VaR. 16 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £3,200.62 (gross £3,709.94, capital £509.32)
  - Electricity: gross £2,988.43, capital £457.60, net £2,530.83
  - Gas: gross £721.51, capital £51.72, net £669.79
- Treasury at year end: £35,906.43
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 0.90 (avg 0.90), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 1.00 (avg 1.00), C4 0.85 (avg 0.85), C4g 1.00 (avg 1.00), C5 0.85 (avg 0.85), C6 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C2g on 2024-03-30 period 1, net margin £-0.26

**Customer Book**

- Active accounts: 10 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £1,749.38
- Highest CLV: C6 (£3,450.46); Lowest CLV: C3 (£641.62)
- Bill shock events (>=20%): 17 -- C1 2024-01-31 (49%); C1 2024-04-30 (24%); C1g 2024-01-31 (51%); C5 2024-01-31 (41%); C5 2024-02-29 (22%); C5 2024-05-31 (27%); C5 2024-09-30 (20%); C5 2024-10-31 (28%); C5 2024-11-30 (38%); C2 2024-04-30 (61%); C2g 2024-04-30 (53%); C6 2024-04-30 (63%); C6 2024-05-31 (30%); C6 2024-09-30 (26%); C6 2024-10-31 (24%); C6 2024-11-30 (39%); C3 2024-04-30 (22%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £191.76-£199.60/MWh, net margin £174.01
- C1g (gas): tariff £50.96-£51.19/MWh, net margin £141.07
- C2 (electricity): tariff £151.31-£335.91/MWh, net margin £371.95
- C2g (gas): tariff £38.67-£82.03/MWh, net margin £163.49
- C3 (electricity): tariff £148.64-£189.75/MWh, net margin £175.12
- C3g (gas): tariff £39.75-£48.52/MWh, net margin £147.04
- C4 (electricity): tariff £154.37-£174.99/MWh, net margin £279.89
- C4g (gas): tariff £42.02-£45.27/MWh, net margin £218.19
- C5 (electricity): tariff £191.76-£199.60/MWh, net margin £753.42
- C6 (electricity): tariff £151.31-£335.91/MWh, net margin £776.43
- Cost to serve per customer (whole-run total, average £618.93, range £95.63-£1,458.12):
  - C1: cost to serve £655.06, net margin after cost to serve £221.49
  - C1g: cost to serve £111.21, net margin after cost to serve £561.02
  - C2: cost to serve £772.86, net margin after cost to serve £1,626.62
  - C2g: cost to serve £133.02, net margin after cost to serve £899.18
  - C3: cost to serve £599.86, net margin after cost to serve £197.00
  - C3g: cost to serve £95.63, net margin after cost to serve £563.12
  - C4: cost to serve £709.09, net margin after cost to serve £803.85
  - C4g: cost to serve £204.67, net margin after cost to serve £986.14
  - C5: cost to serve £1,458.12, net margin after cost to serve £2,822.36
  - C6: cost to serve £1,449.78, net margin after cost to serve £4,100.88

**Portfolio Health**

- Capital cost ratio: 13.7% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 120, average clarity 0.926, average bill shock 9.4%, bad debt provision £307.03, avg complaint probability 3.0%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £1,868.72 vs. naked (unhedged) net margin: £612.89
- hedging added £1,255.84 vs. a fully unhedged book (actual net £1,868.72 vs. naked net £612.89)
  - C1: actual £73.18 vs. naked £97.29 -- hedging cost £24.11
  - C1g: actual £57.21 vs. naked £15.17 -- hedging added £42.03
  - C2: actual £251.23 vs. naked £395.52 -- hedging cost £144.30
  - C2g: actual £113.71 vs. naked £-28.87 -- hedging added £142.58
  - C3: actual £135.77 vs. naked £151.80 -- hedging cost £16.02
  - C3g: actual £124.96 vs. naked £-38.28 -- hedging added £163.24
  - C4: actual £170.38 vs. naked £200.38 -- hedging cost £30.00
  - C4g: actual £160.46 vs. naked £-7.49 -- hedging added £167.96
  - C5: actual £340.37 vs. naked £232.23 -- hedging added £108.15
  - C6: actual £441.45 vs. naked £-404.86 -- hedging added £846.31

**Year narrative:** 2024 produced a net gain of £3,200.62 across 10 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 17 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £1,400.71 (gross £1,635.19, capital £234.49)
  - Electricity: gross £1,343.76, capital £221.64, net £1,122.11
  - Gas: gross £291.44, capital £12.84, net £278.60
- Treasury at year end: £36,657.88
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.85 (avg 0.85), C2g 0.95 (avg 0.95), C6 0.95 (avg 0.95)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C6 on 2025-01-08 period 34, net margin £-1.92

**Customer Book**

- Active accounts: 10 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £1,749.38
- Highest CLV: C6 (£3,450.46); Lowest CLV: C3 (£641.62)
- Bill shock events (>=20%): 19 -- C1 2025-04-30 (23%); C1 2025-06-07 (78%); C1g 2025-06-07 (77%); C5 2025-04-30 (31%); C5 2025-06-07 (79%); C2 2025-04-30 (97%); C2 2025-06-07 (78%); C2g 2025-04-30 (48%); C2g 2025-06-07 (77%); C6 2025-01-31 (25%); C6 2025-02-28 (20%); C6 2025-04-30 (70%); C6 2025-05-31 (21%); C6 2025-06-07 (76%); C3 2025-04-30 (22%); C3 2025-06-07 (78%); C3g 2025-06-07 (77%); C4 2025-06-07 (78%); C4g 2025-06-07 (77%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £191.76/MWh, net margin £72.64
- C1g (gas): tariff £50.96/MWh, net margin £57.00
- C2 (electricity): tariff £151.31-£385.40/MWh, net margin £191.59
- C2g (gas): tariff £38.67-£61.57/MWh, net margin £63.60
- C3 (electricity): tariff £148.64/MWh, net margin £62.36
- C3g (gas): tariff £39.75/MWh, net margin £57.39
- C4 (electricity): tariff £154.37/MWh, net margin £104.46
- C4g (gas): tariff £45.27/MWh, net margin £100.61
- C5 (electricity): tariff £191.76/MWh, net margin £342.67
- C6 (electricity): tariff £151.31-£385.40/MWh, net margin £348.38
- Cost to serve per customer (whole-run total, average £618.93, range £95.63-£1,458.12):
  - C1: cost to serve £655.06, net margin after cost to serve £221.49
  - C1g: cost to serve £111.21, net margin after cost to serve £561.02
  - C2: cost to serve £772.86, net margin after cost to serve £1,626.62
  - C2g: cost to serve £133.02, net margin after cost to serve £899.18
  - C3: cost to serve £599.86, net margin after cost to serve £197.00
  - C3g: cost to serve £95.63, net margin after cost to serve £563.12
  - C4: cost to serve £709.09, net margin after cost to serve £803.85
  - C4g: cost to serve £204.67, net margin after cost to serve £986.14
  - C5: cost to serve £1,458.12, net margin after cost to serve £2,822.36
  - C6: cost to serve £1,449.78, net margin after cost to serve £4,100.88

**Portfolio Health**

- Capital cost ratio: 14.3% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 60, average clarity 0.856, average bill shock 23.6%, bad debt provision £144.30, avg complaint probability 5.3%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £368.71 vs. naked (unhedged) net margin: £87.54
- hedging added £281.17 vs. a fully unhedged book (actual net £368.71 vs. naked net £87.54)
  - C2: actual £131.07 vs. naked £311.37 -- hedging cost £180.30
  - C2g: actual £39.10 vs. naked £28.34 -- hedging added £10.76
  - C6: actual £198.53 vs. naked £-252.17 -- hedging added £450.71

**Year narrative:** 2025 produced a net gain of £1,400.71 across 10 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 19 customer(s) experienced a bill shock of >=20%.
