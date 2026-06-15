# Annual Report — The Synthetic Enterprise

## Executive Summary

This report covers 2016–2025 (10 calendar years,
the last partial). The business survived the full window.

- Starting treasury: £29,846.19
- Final treasury: £37,177.20
  (£7,331.01 net change)
- Revenue: £171,786.67
- Gross margin: £11,230.43
- Capital costs: £3,899.42
- Net margin: £7,331.01
- Capital cost ratio: 34.7% of gross
- Net margin as % of revenue: 4.3%
  (industry benchmark for a retail energy supplier: 2-5%)
- Risk committee (Context Handshake) interventions: 155
- Bills issued: 1434, average clarity 0.878,
  service quality score 0.919
- Enterprise value (CLV sum across 9 billing accounts): £1,810.07
- Cost to serve (whole portfolio): £8,609.40, net margin after cost to serve: £2,621.03
- Hedge effectiveness (whole window): hedging cost £27,427.04 vs. a fully unhedged book (actual net £7,331.01 vs. naked net £34,758.04)

- **2021** (crisis year): net margin £-63.46, 25 risk committee wake-up(s).
- **2022** (crisis year): net margin £825.91, 35 risk committee wake-up(s).

## Hedging Mandate — Before/After Phase 5c

Phase 5c replaced the old reactive hedging model (start at 50/50, risk committee reacts upward from there with no floor) with a minimum hedge mandate: every term starts at least 85% hedged (`MIN_HEDGE_FLOOR` in `sim/hedging_strategy.py`), modelling a real supplier's supply-obligation-first behaviour rather than a speculative book with a safety valve. Because capital cost is charged on the unhedged (active) position only, raising the floor to 85% caps that active position at 15% of volume by construction.

**Note:** the figures below come from two *different* simulation runs (this run vs. the preserved old-model snapshot) — do not subtract a figure from one run's row from a figure in the other's. This run: gross £11,230.43, capital £3,899.42, net £7,331.01. Old-model run: gross £45,417.31, capital £18,637.75, net £26,779.56.

- **Capital cost as % of gross margin**: 34.7% under the new mandate vs. 41.0% under the old reactive model.
- **2021 net margin**: £-63.46 under the new mandate vs. £-1,096.43 under the old reactive model.
- **Net margin as % of revenue**: this run 4.3%; old-model run Not available in current run output (see REPORTING_BACKLOG.md) (revenue wasn't captured in that snapshot).

**Whole-run net margin, three ways:**

- Mandate-hedged (actual, this run): £7,331.01
- Old reactive model (actual): £26,779.56
- Fully naked (this run's counterfactual): £34,758.04
- Fully naked (old run's counterfactual): £33,476.19

Comparing the two naked counterfactuals shows what changed in the underlying weather/price data between runs (LLM non-determinism in risk-committee responses also shifts these slightly run-to-run); comparing each model's actual to its own naked figure isolates what that model's hedging behaviour itself contributed.
## Hedge Effectiveness — Whole Run

This is the most strategically interesting question in the whole
simulation: did the risk committee's hedging interventions actually make
money, or just reduce variance?

- hedging cost £27,427.04 vs. a fully unhedged book (actual net £7,331.01 vs. naked net £34,758.04)
- **Best hedging decision of the run**: C6, term starting
  2021-03-31 (hedge fraction 0.85) -- hedging
  protected £1,497.22 vs. going naked.
- **Worst hedging decision of the run**: C5, term
  starting 2022-12-30 (hedge fraction 1.00) --
  over-hedging cost £3,360.13 vs. going
  naked.

## Segment Margin Trend

Not available in current run output (see REPORTING_BACKLOG.md)

## 2016

**Trading & Risk**

- Net margin: £554.47 (gross £889.66, capital £335.18)
  - Electricity: gross £799.14, capital £328.86, net £470.28
  - Gas: gross £90.52, capital £6.32, net £84.20
- Treasury at year end: £30,248.58
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.90), C1g 0.85 (avg 0.85), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 0.85 (avg 0.85), C4 0.85 (avg 0.85), C4g 0.85 (avg 0.85), C5 0.85 (avg 0.90), C6 0.85 (avg 0.85), C7 0.85 (avg 0.90), C8 0.85 (avg 0.85), C9 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 60
  - 2016-01-31: treasury £29,850.67, C1->1.00, VaR (current £135.51 / stressed £41.63) ratio 3.25
  - 2016-03-01: treasury £29,855.23, C1->1.00, VaR (current £135.51 / stressed £41.63) ratio 3.25
  - 2016-03-31: treasury £29,859.53, C1->1.00, VaR (current £135.51 / stressed £41.63) ratio 3.25
  - 2016-04-30: treasury £29,862.91, C1->1.00, VaR (current £135.51 / stressed £41.63) ratio 3.25
  - 2016-05-30: treasury £29,866.28, C1->1.00, VaR (current £135.51 / stressed £41.63) ratio 3.25
  - 2016-06-29: treasury £29,869.09, C1->1.00, VaR (current £135.51 / stressed £41.63) ratio 3.25
  - 2016-07-29: treasury £29,872.11, C1->1.00, VaR (current £135.51 / stressed £41.63) ratio 3.25
  - 2016-09-27: treasury £29,878.31, C1->1.00, VaR (current £135.51 / stressed £41.63) ratio 3.25
  - 2016-11-26: treasury £29,883.96, C1->1.00, VaR (current £135.51 / stressed £41.63) ratio 3.25
  - 2016-12-26: treasury £29,888.08, C1->1.00, VaR (current £135.51 / stressed £41.63) ratio 3.25
  - 2016-02-17: treasury £29,953.34, C1->0.95, C5->0.95, VaR (current £1,345.40 / stressed £413.34) ratio 3.25
  - 2016-03-18: treasury £29,977.39, C1->0.95, C5->0.95, VaR (current £1,345.40 / stressed £413.34) ratio 3.25
  - 2016-04-17: treasury £29,995.88, C1->1.00, C5->1.00, VaR (current £1,345.40 / stressed £413.34) ratio 3.25
  - 2016-05-17: treasury £30,009.72, C1->1.00, C5->1.00, VaR (current £1,345.40 / stressed £413.34) ratio 3.25
  - 2016-06-16: treasury £30,016.82, C1->1.00, C5->1.00, VaR (current £1,345.40 / stressed £413.34) ratio 3.25
  - 2016-07-16: treasury £30,021.63, C1->1.00, C5->1.00, VaR (current £1,345.40 / stressed £413.34) ratio 3.25
  - 2016-08-15: treasury £30,025.65, C1->0.95, C5->0.95, VaR (current £1,345.40 / stressed £413.34) ratio 3.25
  - 2016-09-14: treasury £30,028.78, C1->1.00, C5->1.00, VaR (current £1,345.40 / stressed £413.34) ratio 3.25
  - 2016-10-14: treasury £30,035.21, C1->0.95, C5->0.95, VaR (current £1,345.40 / stressed £413.34) ratio 3.25
  - 2016-11-13: treasury £30,043.90, C1->1.00, C5->1.00, VaR (current £1,345.40 / stressed £413.34) ratio 3.25
  - 2016-12-13: treasury £30,058.26, C1->1.00, C5->1.00, VaR (current £1,345.40 / stressed £413.34) ratio 3.25
  - 2016-02-12: treasury £30,097.08, C1->1.00, C5->1.00, C7->1.00, VaR (current £1,964.95 / stressed £603.68) ratio 3.25
  - 2016-03-13: treasury £30,118.23, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,964.95 / stressed £603.68) ratio 3.25
  - 2016-04-12: treasury £30,136.02, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,964.95 / stressed £603.68) ratio 3.25
  - 2016-05-12: treasury £30,148.38, C1->1.00, C5->1.00, C7->1.00, VaR (current £1,964.95 / stressed £603.68) ratio 3.25
  - 2016-08-10: treasury £30,162.50, C1->0.95, C5->0.95, C7->0.95, VaR (current £1,964.95 / stressed £603.68) ratio 3.25
  - 2016-09-09: treasury £30,165.59, C1->1.00, C5->1.00, C7->1.00, VaR (current £1,964.95 / stressed £603.68) ratio 3.25
  - 2016-11-08: treasury £30,180.85, C1->1.00, C5->1.00, C7->1.00, VaR (current £1,964.95 / stressed £603.68) ratio 3.25
  - 2016-04-08: treasury £30,207.27, C1->1.00, C5->1.00, C7->1.00, VaR (current £2,050.42 / stressed £639.27) ratio 3.21
  - 2016-05-08: treasury £30,212.19, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,050.42 / stressed £639.27) ratio 3.21
  - 2016-06-07: treasury £30,217.18, C1->1.00, C5->1.00, C7->1.00, VaR (current £2,050.42 / stressed £639.27) ratio 3.21
  - 2016-07-07: treasury £30,221.69, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,050.42 / stressed £639.27) ratio 3.21
  - 2016-08-06: treasury £30,226.49, C1->1.00, C5->1.00, C7->1.00, VaR (current £2,050.42 / stressed £639.27) ratio 3.21
  - 2016-09-05: treasury £30,231.38, C1->1.00, C5->1.00, C7->1.00, VaR (current £2,050.42 / stressed £639.27) ratio 3.21
  - 2016-11-04: treasury £30,240.60, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,050.42 / stressed £639.27) ratio 3.21
  - 2016-12-04: treasury £30,244.01, C1->1.00, C5->1.00, C7->1.00, VaR (current £2,050.42 / stressed £639.27) ratio 3.21
  - 2016-04-26: treasury £30,307.43, C1->1.00, C5->1.00, C7->1.00, VaR (current £3,149.30 / stressed £1,096.92) ratio 2.87
  - 2016-05-26: treasury £30,313.67, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,149.30 / stressed £1,096.92) ratio 2.87
  - 2016-06-25: treasury £30,314.36, C1->1.00, C5->1.00, C7->1.00, VaR (current £3,149.30 / stressed £1,096.92) ratio 2.87
  - 2016-08-24: treasury £30,315.47, C1->1.00, C5->1.00, C7->1.00, VaR (current £3,149.30 / stressed £1,096.92) ratio 2.87
  - 2016-09-23: treasury £30,314.70, C1->1.00, C5->1.00, C7->1.00, VaR (current £3,149.30 / stressed £1,096.92) ratio 2.87
  - 2016-10-23: treasury £30,316.90, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,149.30 / stressed £1,096.92) ratio 2.87
  - 2016-12-22: treasury £30,321.90, C1->1.00, C5->1.00, C7->1.00, VaR (current £3,149.30 / stressed £1,096.92) ratio 2.87
  - 2016-04-21: treasury £30,349.66, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,438.17 / stressed £1,217.23) ratio 2.82
  - 2016-05-21: treasury £30,356.81, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,438.17 / stressed £1,217.23) ratio 2.82
  - 2016-06-20: treasury £30,359.51, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,438.17 / stressed £1,217.23) ratio 2.82
  - 2016-07-20: treasury £30,361.20, C1->1.00, C5->1.00, C7->1.00, VaR (current £3,438.17 / stressed £1,217.23) ratio 2.82
  - 2016-08-19: treasury £30,362.33, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,438.17 / stressed £1,217.23) ratio 2.82
  - 2016-09-18: treasury £30,362.93, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,438.17 / stressed £1,217.23) ratio 2.82
  - 2016-12-17: treasury £30,376.73, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,438.17 / stressed £1,217.23) ratio 2.82
  - 2016-07-16: treasury £30,407.13, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,496.07 / stressed £1,244.40) ratio 2.81
  - 2016-08-15: treasury £30,409.20, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,496.07 / stressed £1,244.40) ratio 2.81
  - 2016-09-14: treasury £30,410.99, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,496.07 / stressed £1,244.40) ratio 2.81
  - 2016-12-13: treasury £30,415.18, C1->1.00, C5->1.00, C7->1.00, VaR (current £3,496.07 / stressed £1,244.40) ratio 2.81
  - 2016-08-02: treasury £30,454.60, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,719.90 / stressed £1,349.42) ratio 2.76
  - 2016-09-01: treasury £30,456.27, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,719.90 / stressed £1,349.42) ratio 2.76
  - 2016-11-30: treasury £30,463.14, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,719.90 / stressed £1,349.42) ratio 2.76
  - 2016-12-30: treasury £30,469.16, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,719.90 / stressed £1,349.42) ratio 2.76
  - 2016-10-28: treasury £30,500.63, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,831.27 / stressed £1,403.07) ratio 2.73
  - 2016-12-27: treasury £30,507.68, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,831.27 / stressed £1,403.07) ratio 2.73
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 3.07
- Worst single period: C8 on 2016-11-08 period 40, net margin £-0.43

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £201.12
- Highest CLV: C6 (£613.66); Lowest CLV: C1 (£-81.13)
- Bill shock events (>=20%): 23 -- C1 2016-04-30 (21%); C5 2016-04-30 (21%); C5 2016-05-31 (30%); C5 2016-06-30 (22%); C5 2016-10-31 (47%); C5 2016-11-30 (49%); C7 2016-04-30 (20%); C7 2016-05-31 (38%); C7 2016-06-30 (31%); C7 2016-10-31 (81%); C7 2016-11-30 (52%); C6 2016-05-31 (28%); C6 2016-06-30 (25%); C6 2016-10-31 (46%); C6 2016-11-30 (51%); C8 2016-05-31 (42%); C8 2016-06-30 (45%); C8 2016-09-30 (29%); C8 2016-10-31 (118%); C8 2016-11-30 (71%); C9 2016-09-30 (22%); C9 2016-10-31 (86%); C9 2016-11-30 (60%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £124.00-£155.49/MWh, net margin £42.20
- C1g (gas): tariff £16.55-£16.64/MWh, net margin £29.04
- C2 (electricity): tariff £85.45/MWh, net margin £42.66
- C2g (gas): tariff £18.07/MWh, net margin £30.30
- C3 (electricity): tariff £71.66/MWh, net margin £10.52
- C3g (gas): tariff £13.45/MWh, net margin £13.76
- C4 (electricity): tariff £82.05/MWh, net margin £11.44
- C4g (gas): tariff £14.32/MWh, net margin £11.09
- C5 (electricity): tariff £124.00-£155.49/MWh, net margin £149.82
- C6 (electricity): tariff £85.45/MWh, net margin £23.31
- C7 (electricity): tariff £124.00-£155.49/MWh, net margin £134.72
- C8 (electricity): tariff £85.45/MWh, net margin £38.56
- C9 (electricity): tariff £71.66/MWh, net margin £17.04
- Cost to serve per customer (whole-run total, average £662.26, range £88.06-£1,431.94):
  - C1: cost to serve £644.14, net margin after cost to serve £-290.51 -- **net-negative**
  - C1g: cost to serve £103.25, net margin after cost to serve £171.33
  - C2: cost to serve £747.57, net margin after cost to serve £387.84
  - C2g: cost to serve £121.48, net margin after cost to serve £333.75
  - C3: cost to serve £589.92, net margin after cost to serve £-289.89 -- **net-negative**
  - C3g: cost to serve £88.06, net margin after cost to serve £191.96
  - C4: cost to serve £690.13, net margin after cost to serve £-125.32 -- **net-negative**
  - C4g: cost to serve £189.40, net margin after cost to serve £237.83
  - C5: cost to serve £1,431.94, net margin after cost to serve £231.15
  - C6: cost to serve £1,417.21, net margin after cost to serve £876.34
  - C7: cost to serve £938.79, net margin after cost to serve £261.58
  - C8: cost to serve £892.43, net margin after cost to serve £655.87
  - C9: cost to serve £755.08, net margin after cost to serve £-20.89 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 37.7% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 108, average clarity 0.888, average bill shock 14.6%, bad debt provision £158.46, avg complaint probability 3.7%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £1,004.31 vs. naked (unhedged) net margin: £4,759.95
- hedging cost £3,755.64 vs. a fully unhedged book (actual net £1,004.31 vs. naked net £4,759.95)
  - C1: actual £71.95 vs. naked £522.36 -- hedging cost £450.41
  - C1g: actual £51.31 vs. naked £45.90 -- hedging added £5.41
  - C2: actual £56.94 vs. naked £257.68 -- hedging cost £200.74
  - C2g: actual £37.97 vs. naked £66.51 -- hedging cost £28.54
  - C3: actual £21.84 vs. naked £73.23 -- hedging cost £51.39
  - C3g: actual £24.44 vs. naked £-6.81 -- hedging added £31.25
  - C4: actual £47.60 vs. naked £197.09 -- hedging cost £149.48
  - C4g: actual £38.18 vs. naked £-13.49 -- hedging added £51.67
  - C5: actual £274.39 vs. naked £1,756.75 -- hedging cost £1,482.36
  - C6: actual £42.35 vs. naked £-44.28 -- hedging added £86.63
  - C7: actual £230.06 vs. naked £1,591.81 -- hedging cost £1,361.75
  - C8: actual £62.93 vs. naked £213.60 -- hedging cost £150.67
  - C9: actual £44.33 vs. naked £99.59 -- hedging cost £55.26

**Year narrative:** 2016 produced a net gain of £554.47 across 13 accounts. The risk committee intervened 60 time(s), raising hedge fractions in response to elevated VaR. 23 customer(s) experienced a bill shock of >=20%.

## 2017

**Trading & Risk**

- Net margin: £702.43 (gross £918.09, capital £215.66)
  - Electricity: gross £784.01, capital £205.70, net £578.30
  - Gas: gross £134.08, capital £9.96, net £124.12
- Treasury at year end: £30,897.67
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 0.95 (avg 0.95), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 0.95 (avg 0.95), C4 0.85 (avg 0.85), C4g 0.95 (avg 0.95), C5 0.85 (avg 0.85), C6 0.95 (avg 0.95), C7 0.85 (avg 0.85), C8 0.85 (avg 0.85), C9 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 33
  - 2017-01-03: treasury £30,249.03, C1->0.95, C5->0.95, C7->0.95, VaR (current £2,050.42 / stressed £639.27) ratio 3.21
  - 2017-03-04: treasury £30,258.01, C1->1.00, C5->1.00, C7->1.00, VaR (current £2,050.42 / stressed £639.27) ratio 3.21
  - 2017-02-20: treasury £30,333.03, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,149.30 / stressed £1,096.92) ratio 2.87
  - 2017-02-15: treasury £30,393.74, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,438.17 / stressed £1,217.23) ratio 2.82
  - 2017-01-12: treasury £30,417.32, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,496.07 / stressed £1,244.40) ratio 2.81
  - 2017-02-11: treasury £30,418.72, C1->1.00, C5->1.00, C7->1.00, VaR (current £3,496.07 / stressed £1,244.40) ratio 2.81
  - 2017-03-13: treasury £30,421.00, C1->1.00, C5->1.00, C7->1.00, VaR (current £3,496.07 / stressed £1,244.40) ratio 2.81
  - 2017-04-12: treasury £30,423.45, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,496.07 / stressed £1,244.40) ratio 2.81
  - 2017-05-12: treasury £30,425.25, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,496.07 / stressed £1,244.40) ratio 2.81
  - 2017-06-11: treasury £30,426.70, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,496.07 / stressed £1,244.40) ratio 2.81
  - 2017-01-29: treasury £30,473.54, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,719.90 / stressed £1,349.42) ratio 2.76
  - 2017-02-28: treasury £30,479.65, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,719.90 / stressed £1,349.42) ratio 2.76
  - 2017-04-29: treasury £30,492.07, C1->1.00, C5->1.00, C7->1.00, VaR (current £3,719.90 / stressed £1,349.42) ratio 2.76
  - 2017-05-29: treasury £30,494.20, C1->1.00, C5->1.00, C7->1.00, VaR (current £3,719.90 / stressed £1,349.42) ratio 2.76
  - 2017-01-26: treasury £30,511.41, C1->0.95, C5->1.00, C7->1.00, VaR (current £3,831.27 / stressed £1,403.07) ratio 2.73
  - 2017-02-25: treasury £30,515.43, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,831.27 / stressed £1,403.07) ratio 2.73
  - 2017-03-27: treasury £30,520.11, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,831.27 / stressed £1,403.07) ratio 2.73
  - 2017-04-26: treasury £30,524.56, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,831.27 / stressed £1,403.07) ratio 2.73
  - 2017-05-26: treasury £30,527.80, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,831.27 / stressed £1,403.07) ratio 2.73
  - 2017-06-25: treasury £30,531.85, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,831.27 / stressed £1,403.07) ratio 2.73
  - 2017-08-24: treasury £30,539.86, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,831.27 / stressed £1,403.07) ratio 2.73
  - 2017-09-23: treasury £30,543.47, C1->0.95, C5->0.95, C7->0.95, VaR (current £3,831.27 / stressed £1,403.07) ratio 2.73
  - 2017-01-15: treasury £30,583.60, C5->1.00, C7->1.00, VaR (current £3,737.16 / stressed £1,378.90) ratio 2.71
  - 2017-02-14: treasury £30,586.36, C5->1.00, C7->1.00, VaR (current £3,737.16 / stressed £1,378.90) ratio 2.71
  - 2017-03-16: treasury £30,589.37, C5->1.00, C7->1.00, VaR (current £3,737.16 / stressed £1,378.90) ratio 2.71
  - 2017-04-15: treasury £30,591.99, C5->0.95, C7->0.95, VaR (current £3,737.16 / stressed £1,378.90) ratio 2.71
  - 2017-05-15: treasury £30,594.24, C5->0.95, C7->0.95, VaR (current £3,737.16 / stressed £1,378.90) ratio 2.71
  - 2017-07-14: treasury £30,598.35, C5->0.95, C7->0.95, VaR (current £3,737.16 / stressed £1,378.90) ratio 2.71
  - 2017-08-13: treasury £30,600.43, C5->0.95, C7->0.95, VaR (current £3,737.16 / stressed £1,378.90) ratio 2.71
  - 2017-09-12: treasury £30,602.53, C5->0.95, C7->0.95, VaR (current £3,737.16 / stressed £1,378.90) ratio 2.71
  - 2017-10-12: treasury £30,604.78, C5->0.95, C7->0.95, VaR (current £3,737.16 / stressed £1,378.90) ratio 2.71
  - 2017-11-11: treasury £30,607.39, C5->0.95, C7->0.95, VaR (current £3,737.16 / stressed £1,378.90) ratio 2.71
  - 2017-12-11: treasury £30,610.22, C5->0.95, C7->0.95, VaR (current £3,737.16 / stressed £1,378.90) ratio 2.71
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.78
- Worst single period: C9 on 2017-05-17 period 34, net margin £-0.16

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £201.12
- Highest CLV: C6 (£613.66); Lowest CLV: C1 (£-81.13)
- Bill shock events (>=20%): 32 -- C1 2017-01-31 (25%); C1 2017-04-30 (21%); C5 2017-01-31 (45%); C5 2017-02-28 (23%); C5 2017-05-31 (22%); C5 2017-06-30 (23%); C5 2017-11-30 (62%); C7 2017-01-31 (52%); C7 2017-02-28 (28%); C7 2017-05-31 (31%); C7 2017-06-30 (31%); C7 2017-09-30 (28%); C7 2017-10-31 (20%); C7 2017-11-30 (76%); C6 2017-05-31 (24%); C6 2017-06-30 (21%); C6 2017-11-30 (55%); C8 2017-05-31 (42%); C8 2017-06-30 (38%); C8 2017-09-30 (52%); C8 2017-10-31 (22%); C8 2017-11-30 (89%); C8 2017-12-31 (23%); C3 2017-07-31 (49%); C3g 2017-07-31 (26%); C9 2017-05-31 (35%); C9 2017-06-30 (27%); C9 2017-07-31 (32%); C9 2017-09-30 (33%); C9 2017-10-31 (22%); C9 2017-11-30 (74%); C4g 2017-10-31 (38%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £83.15-£155.49/MWh, net margin £29.53
- C1g (gas): tariff £16.55-£22.59/MWh, net margin £22.26
- C2 (electricity): tariff £85.45-£94.31/MWh, net margin £61.44
- C2g (gas): tariff £18.07-£22.20/MWh, net margin £38.20
- C3 (electricity): tariff £71.66-£103.11/MWh, net margin £31.44
- C3g (gas): tariff £13.45-£16.39/MWh, net margin £24.92
- C4 (electricity): tariff £75.03-£82.05/MWh, net margin £45.71
- C4g (gas): tariff £14.32-£19.06/MWh, net margin £38.75
- C5 (electricity): tariff £83.15-£155.49/MWh, net margin £122.10
- C6 (electricity): tariff £85.45-£94.31/MWh, net margin £56.43
- C7 (electricity): tariff £83.15-£155.49/MWh, net margin £94.26
- C8 (electricity): tariff £85.45-£94.31/MWh, net margin £68.84
- C9 (electricity): tariff £71.66-£103.11/MWh, net margin £68.55
- Cost to serve per customer (whole-run total, average £662.26, range £88.06-£1,431.94):
  - C1: cost to serve £644.14, net margin after cost to serve £-290.51 -- **net-negative**
  - C1g: cost to serve £103.25, net margin after cost to serve £171.33
  - C2: cost to serve £747.57, net margin after cost to serve £387.84
  - C2g: cost to serve £121.48, net margin after cost to serve £333.75
  - C3: cost to serve £589.92, net margin after cost to serve £-289.89 -- **net-negative**
  - C3g: cost to serve £88.06, net margin after cost to serve £191.96
  - C4: cost to serve £690.13, net margin after cost to serve £-125.32 -- **net-negative**
  - C4g: cost to serve £189.40, net margin after cost to serve £237.83
  - C5: cost to serve £1,431.94, net margin after cost to serve £231.15
  - C6: cost to serve £1,417.21, net margin after cost to serve £876.34
  - C7: cost to serve £938.79, net margin after cost to serve £261.58
  - C8: cost to serve £892.43, net margin after cost to serve £655.87
  - C9: cost to serve £755.08, net margin after cost to serve £-20.89 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 23.5% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.889, average bill shock 12.8%, bad debt provision £243.83, avg complaint probability 3.7%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £629.97 vs. naked (unhedged) net margin: £1,542.36
- hedging cost £912.40 vs. a fully unhedged book (actual net £629.97 vs. naked net £1,542.36)
  - C1: actual £18.01 vs. naked £56.31 -- hedging cost £38.30
  - C1g: actual £25.47 vs. naked £-3.82 -- hedging added £29.29
  - C2: actual £60.63 vs. naked £277.93 -- hedging cost £217.30
  - C2g: actual £37.64 vs. naked £60.01 -- hedging cost £22.37
  - C3: actual £37.69 vs. naked £169.15 -- hedging cost £131.46
  - C3g: actual £26.92 vs. naked £-40.23 -- hedging added £67.15
  - C4: actual £30.23 vs. naked £84.71 -- hedging cost £54.48
  - C4g: actual £43.58 vs. naked £-51.34 -- hedging added £94.92
  - C5: actual £67.17 vs. naked £138.83 -- hedging cost £71.65
  - C6: actual £59.18 vs. naked £35.03 -- hedging added £24.15
  - C7: actual £57.66 vs. naked £166.18 -- hedging cost £108.52
  - C8: actual £74.08 vs. naked £275.66 -- hedging cost £201.58
  - C9: actual £91.70 vs. naked £373.96 -- hedging cost £282.26

**Year narrative:** 2017 produced a net gain of £702.43 across 13 accounts. The risk committee intervened 33 time(s), raising hedge fractions in response to elevated VaR. 32 customer(s) experienced a bill shock of >=20%.

## 2018

**Trading & Risk**

- Net margin: £660.75 (gross £816.87, capital £156.12)
  - Electricity: gross £672.10, capital £148.95, net £523.15
  - Gas: gross £144.77, capital £7.16, net £137.61
- Treasury at year end: £31,549.66
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 1.00 (avg 1.00), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 1.00 (avg 1.00), C4 0.85 (avg 0.85), C4g 1.00 (avg 1.00), C5 0.85 (avg 0.85), C6 1.00 (avg 1.00), C7 0.85 (avg 0.85), C8 0.85 (avg 0.85), C9 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C8 on 2018-03-01 period 43, net margin £-0.26

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £201.12
- Highest CLV: C6 (£613.66); Lowest CLV: C1 (£-81.13)
- Bill shock events (>=20%): 39 -- C1 2018-01-31 (46%); C1 2018-04-30 (20%); C1g 2018-01-31 (35%); C5 2018-01-31 (47%); C5 2018-04-30 (34%); C5 2018-05-31 (20%); C5 2018-06-30 (23%); C5 2018-10-31 (35%); C5 2018-11-30 (30%); C7 2018-01-31 (49%); C7 2018-04-30 (38%); C7 2018-05-31 (29%); C7 2018-06-30 (30%); C7 2018-09-30 (30%); C7 2018-10-31 (44%); C7 2018-11-30 (31%); C2 2018-04-30 (21%); C2g 2018-04-30 (26%); C6 2018-05-31 (23%); C6 2018-06-30 (24%); C6 2018-10-31 (33%); C6 2018-11-30 (23%); C8 2018-05-31 (41%); C8 2018-06-30 (44%); C8 2018-08-31 (27%); C8 2018-09-30 (60%); C8 2018-10-31 (56%); C8 2018-11-30 (30%); C3g 2018-07-31 (48%); C9 2018-04-30 (32%); C9 2018-05-31 (37%); C9 2018-06-30 (34%); C9 2018-07-31 (42%); C9 2018-08-31 (44%); C9 2018-09-30 (49%); C9 2018-10-31 (40%); C9 2018-12-31 (22%); C4 2018-10-31 (33%); C4g 2018-10-31 (55%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £83.15-£98.61/MWh, net margin £18.06
- C1g (gas): tariff £22.59-£26.30/MWh, net margin £25.55
- C2 (electricity): tariff £94.31-£132.76/MWh, net margin £82.66
- C2g (gas): tariff £22.20-£28.87/MWh, net margin £38.59
- C3 (electricity): tariff £82.35-£103.11/MWh, net margin £27.84
- C3g (gas): tariff £16.39-£23.49/MWh, net margin £28.64
- C4 (electricity): tariff £75.03-£94.66/MWh, net margin £33.56
- C4g (gas): tariff £19.06-£28.58/MWh, net margin £44.82
- C5 (electricity): tariff £83.15-£98.61/MWh, net margin £67.80
- C6 (electricity): tariff £94.31-£132.76/MWh, net margin £65.44
- C7 (electricity): tariff £83.15-£98.61/MWh, net margin £57.94
- C8 (electricity): tariff £94.31-£132.76/MWh, net margin £100.23
- C9 (electricity): tariff £82.35-£103.11/MWh, net margin £69.60
- Cost to serve per customer (whole-run total, average £662.26, range £88.06-£1,431.94):
  - C1: cost to serve £644.14, net margin after cost to serve £-290.51 -- **net-negative**
  - C1g: cost to serve £103.25, net margin after cost to serve £171.33
  - C2: cost to serve £747.57, net margin after cost to serve £387.84
  - C2g: cost to serve £121.48, net margin after cost to serve £333.75
  - C3: cost to serve £589.92, net margin after cost to serve £-289.89 -- **net-negative**
  - C3g: cost to serve £88.06, net margin after cost to serve £191.96
  - C4: cost to serve £690.13, net margin after cost to serve £-125.32 -- **net-negative**
  - C4g: cost to serve £189.40, net margin after cost to serve £237.83
  - C5: cost to serve £1,431.94, net margin after cost to serve £231.15
  - C6: cost to serve £1,417.21, net margin after cost to serve £876.34
  - C7: cost to serve £938.79, net margin after cost to serve £261.58
  - C8: cost to serve £892.43, net margin after cost to serve £655.87
  - C9: cost to serve £755.08, net margin after cost to serve £-20.89 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 19.1% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.887, average bill shock 13.0%, bad debt provision £232.46, avg complaint probability 3.7%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £906.39 vs. naked (unhedged) net margin: £4,317.94
- hedging cost £3,411.55 vs. a fully unhedged book (actual net £906.39 vs. naked net £4,317.94)
  - C1: actual £36.45 vs. naked £174.98 -- hedging cost £138.52
  - C1g: actual £27.55 vs. naked £147.39 -- hedging cost £119.84
  - C2: actual £96.86 vs. naked £500.07 -- hedging cost £403.22
  - C2g: actual £44.54 vs. naked £99.07 -- hedging cost £54.54
  - C3: actual £25.78 vs. naked £95.81 -- hedging cost £70.04
  - C3g: actual £31.67 vs. naked £51.89 -- hedging cost £20.23
  - C4: actual £62.81 vs. naked £291.95 -- hedging cost £229.14
  - C4g: actual £51.13 vs. naked £259.71 -- hedging cost £208.58
  - C5: actual £156.97 vs. naked £715.83 -- hedging cost £558.86
  - C6: actual £66.23 vs. naked £607.75 -- hedging cost £541.52
  - C7: actual £119.30 vs. naked £562.01 -- hedging cost £442.71
  - C8: actual £127.16 vs. naked £617.73 -- hedging cost £490.57
  - C9: actual £59.96 vs. naked £193.74 -- hedging cost £133.78

**Year narrative:** 2018 produced a net gain of £660.75 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 39 customer(s) experienced a bill shock of >=20%.

## 2019

**Trading & Risk**

- Net margin: £949.02 (gross £1,078.48, capital £129.46)
  - Electricity: gross £908.20, capital £123.83, net £784.37
  - Gas: gross £170.28, capital £5.63, net £164.65
- Treasury at year end: £32,441.48
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 0.90 (avg 0.90), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 0.90 (avg 0.90), C4 0.85 (avg 0.85), C4g 0.90 (avg 0.90), C5 0.85 (avg 0.85), C6 0.90 (avg 0.90), C7 0.85 (avg 0.85), C8 0.85 (avg 0.85), C9 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C5 on 2019-06-24 period 24, net margin £-0.05

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £201.12
- Highest CLV: C6 (£613.66); Lowest CLV: C1 (£-81.13)
- Bill shock events (>=20%): 38 -- C1 2019-04-30 (24%); C5 2019-01-31 (42%); C5 2019-02-28 (22%); C5 2019-06-30 (28%); C5 2019-10-31 (48%); C5 2019-11-30 (39%); C7 2019-01-31 (47%); C7 2019-02-28 (25%); C7 2019-05-31 (23%); C7 2019-06-30 (34%); C7 2019-10-31 (67%); C7 2019-11-30 (45%); C2 2019-04-30 (41%); C6 2019-02-28 (21%); C6 2019-04-30 (44%); C6 2019-06-30 (26%); C6 2019-09-30 (22%); C6 2019-10-31 (45%); C6 2019-11-30 (29%); C8 2019-01-31 (24%); C8 2019-02-28 (26%); C8 2019-04-30 (48%); C8 2019-06-30 (40%); C8 2019-07-31 (38%); C8 2019-09-30 (67%); C8 2019-10-31 (87%); C8 2019-11-30 (40%); C3 2019-04-30 (22%); C3g 2019-07-31 (29%); C9 2019-02-28 (25%); C9 2019-04-30 (25%); C9 2019-06-30 (37%); C9 2019-07-31 (41%); C9 2019-09-30 (56%); C9 2019-10-31 (74%); C9 2019-11-30 (40%); C4 2019-10-31 (26%); C4g 2019-10-31 (56%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £74.53-£98.61/MWh, net margin £36.49
- C1g (gas): tariff £15.70-£26.30/MWh, net margin £27.45
- C2 (electricity): tariff £93.81-£132.76/MWh, net margin £82.28
- C2g (gas): tariff £24.14-£28.87/MWh, net margin £55.13
- C3 (electricity): tariff £73.56-£82.35/MWh, net margin £30.73
- C3g (gas): tariff £16.11-£23.49/MWh, net margin £33.07
- C4 (electricity): tariff £66.05-£94.66/MWh, net margin £61.15
- C4g (gas): tariff £12.10-£28.58/MWh, net margin £49.01
- C5 (electricity): tariff £74.53-£98.61/MWh, net margin £157.42
- C6 (electricity): tariff £93.81-£132.76/MWh, net margin £98.56
- C7 (electricity): tariff £74.53-£98.61/MWh, net margin £119.51
- C8 (electricity): tariff £93.81-£132.76/MWh, net margin £122.97
- C9 (electricity): tariff £73.56-£82.35/MWh, net margin £75.25
- Cost to serve per customer (whole-run total, average £662.26, range £88.06-£1,431.94):
  - C1: cost to serve £644.14, net margin after cost to serve £-290.51 -- **net-negative**
  - C1g: cost to serve £103.25, net margin after cost to serve £171.33
  - C2: cost to serve £747.57, net margin after cost to serve £387.84
  - C2g: cost to serve £121.48, net margin after cost to serve £333.75
  - C3: cost to serve £589.92, net margin after cost to serve £-289.89 -- **net-negative**
  - C3g: cost to serve £88.06, net margin after cost to serve £191.96
  - C4: cost to serve £690.13, net margin after cost to serve £-125.32 -- **net-negative**
  - C4g: cost to serve £189.40, net margin after cost to serve £237.83
  - C5: cost to serve £1,431.94, net margin after cost to serve £231.15
  - C6: cost to serve £1,417.21, net margin after cost to serve £876.34
  - C7: cost to serve £938.79, net margin after cost to serve £261.58
  - C8: cost to serve £892.43, net margin after cost to serve £655.87
  - C9: cost to serve £755.08, net margin after cost to serve £-20.89 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 12.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.884, average bill shock 14.2%, bad debt provision £226.31, avg complaint probability 3.9%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £864.52 vs. naked (unhedged) net margin: £3,621.67
- hedging cost £2,757.15 vs. a fully unhedged book (actual net £864.52 vs. naked net £3,621.67)
  - C1: actual £26.23 vs. naked £112.99 -- hedging cost £86.76
  - C1g: actual £30.66 vs. naked £72.58 -- hedging cost £41.92
  - C2: actual £76.58 vs. naked £384.10 -- hedging cost £307.52
  - C2g: actual £56.94 vs. naked £186.65 -- hedging cost £129.71
  - C3: actual £33.88 vs. naked £152.50 -- hedging cost £118.61
  - C3g: actual £36.80 vs. naked £94.38 -- hedging cost £57.58
  - C4: actual £48.21 vs. naked £208.72 -- hedging cost £160.50
  - C4g: actual £49.74 vs. naked £76.99 -- hedging cost £27.25
  - C5: actual £107.87 vs. naked £429.14 -- hedging cost £321.27
  - C6: actual £119.78 vs. naked £663.95 -- hedging cost £544.17
  - C7: actual £82.65 vs. naked £349.57 -- hedging cost £266.92
  - C8: actual £110.00 vs. naked £522.53 -- hedging cost £412.53
  - C9: actual £85.17 vs. naked £367.57 -- hedging cost £282.41

**Year narrative:** 2019 produced a net gain of £949.02 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 38 customer(s) experienced a bill shock of >=20%.

## 2020

**Trading & Risk**

- Net margin: £805.95 (gross £1,000.75, capital £194.80)
  - Electricity: gross £844.66, capital £186.87, net £657.79
  - Gas: gross £156.09, capital £7.93, net £148.16
- Treasury at year end: £33,315.48
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 0.85 (avg 0.85), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 0.85 (avg 0.85), C4 0.85 (avg 0.85), C4g 0.85 (avg 0.85), C5 0.85 (avg 0.85), C6 0.85 (avg 0.85), C7 0.85 (avg 0.85), C8 0.85 (avg 0.85), C9 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C5 on 2020-03-04 period 37, net margin £-0.97

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £201.12
- Highest CLV: C6 (£613.66); Lowest CLV: C1 (£-81.13)
- Bill shock events (>=20%): 33 -- C1 2020-01-31 (24%); C1 2020-04-30 (23%); C1g 2020-01-31 (40%); C5 2020-01-31 (24%); C5 2020-04-30 (31%); C5 2020-10-31 (42%); C5 2020-11-30 (21%); C5 2020-12-31 (31%); C7 2020-01-31 (25%); C7 2020-04-30 (35%); C7 2020-06-30 (27%); C7 2020-10-31 (60%); C7 2020-11-30 (22%); C7 2020-12-31 (38%); C2g 2020-04-30 (47%); C6 2020-09-30 (23%); C6 2020-10-31 (37%); C6 2020-12-31 (27%); C8 2020-04-30 (30%); C8 2020-05-31 (25%); C8 2020-06-30 (35%); C8 2020-09-30 (57%); C8 2020-10-31 (69%); C8 2020-12-31 (42%); C3 2020-04-30 (21%); C3 2020-07-31 (24%); C3g 2020-07-31 (49%); C9 2020-04-30 (29%); C9 2020-05-31 (25%); C9 2020-06-30 (38%); C9 2020-09-30 (47%); C9 2020-10-31 (52%); C9 2020-12-31 (35%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £74.53-£106.09/MWh, net margin £25.85
- C1g (gas): tariff £15.70-£18.18/MWh, net margin £30.65
- C2 (electricity): tariff £93.81-£106.09/MWh, net margin £86.06
- C2g (gas): tariff £13.14-£24.14/MWh, net margin £41.65
- C3 (electricity): tariff £53.60-£73.56/MWh, net margin £24.35
- C3g (gas): tariff £7.79-£16.11/MWh, net margin £28.56
- C4 (electricity): tariff £66.05-£71.59/MWh, net margin £46.27
- C4g (gas): tariff £12.10-£12.67/MWh, net margin £47.31
- C5 (electricity): tariff £74.53-£106.09/MWh, net margin £104.79
- C6 (electricity): tariff £93.81-£106.09/MWh, net margin £121.71
- C7 (electricity): tariff £74.53-£106.09/MWh, net margin £81.14
- C8 (electricity): tariff £93.81-£106.09/MWh, net margin £110.00
- C9 (electricity): tariff £53.60-£73.56/MWh, net margin £57.62
- Cost to serve per customer (whole-run total, average £662.26, range £88.06-£1,431.94):
  - C1: cost to serve £644.14, net margin after cost to serve £-290.51 -- **net-negative**
  - C1g: cost to serve £103.25, net margin after cost to serve £171.33
  - C2: cost to serve £747.57, net margin after cost to serve £387.84
  - C2g: cost to serve £121.48, net margin after cost to serve £333.75
  - C3: cost to serve £589.92, net margin after cost to serve £-289.89 -- **net-negative**
  - C3g: cost to serve £88.06, net margin after cost to serve £191.96
  - C4: cost to serve £690.13, net margin after cost to serve £-125.32 -- **net-negative**
  - C4g: cost to serve £189.40, net margin after cost to serve £237.83
  - C5: cost to serve £1,431.94, net margin after cost to serve £231.15
  - C6: cost to serve £1,417.21, net margin after cost to serve £876.34
  - C7: cost to serve £938.79, net margin after cost to serve £261.58
  - C8: cost to serve £892.43, net margin after cost to serve £655.87
  - C9: cost to serve £755.08, net margin after cost to serve £-20.89 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 19.5% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.890, average bill shock 12.1%, bad debt provision £182.07, avg complaint probability 3.6%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £171.58 vs. naked (unhedged) net margin: £-1,365.10
- hedging added £1,536.68 vs. a fully unhedged book (actual net £171.58 vs. naked net £-1,365.10)
  - C1: actual £-7.74 vs. naked £-121.22 -- hedging added £113.48
  - C1g: actual £-23.27 vs. naked £-304.56 -- hedging added £281.29
  - C2: actual £79.95 vs. naked £400.56 -- hedging cost £320.61
  - C2g: actual £30.50 vs. naked £21.81 -- hedging added £8.69
  - C3: actual £2.61 vs. naked £-49.66 -- hedging added £52.27
  - C3g: actual £7.55 vs. naked £-113.93 -- hedging added £121.48
  - C4: actual £5.20 vs. naked £-80.78 -- hedging added £85.98
  - C4g: actual £-2.98 vs. naked £-285.42 -- hedging added £282.44
  - C5: actual £-74.25 vs. naked £-841.45 -- hedging added £767.20
  - C6: actual £102.43 vs. naked £329.32 -- hedging cost £226.88
  - C7: actual £-25.75 vs. naked £-418.43 -- hedging added £392.67
  - C8: actual £92.03 vs. naked £391.43 -- hedging cost £299.40
  - C9: actual £-14.70 vs. naked £-292.77 -- hedging added £278.07

**Year narrative:** 2020 produced a net gain of £805.95 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 33 customer(s) experienced a bill shock of >=20%.

## 2021

**Trading & Risk**

- Net margin: £-63.46 (gross £561.23, capital £624.69)
  - Electricity: gross £565.29, capital £614.61, net £-49.31
  - Gas: gross £-4.06, capital £10.08, net £-14.14
- Treasury at year end: £33,500.26
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.95 (avg 0.95), C1g 0.95 (avg 0.95), C2 0.85 (avg 0.85), C2g 0.95 (avg 0.95), C3 0.95 (avg 0.95), C3g 0.95 (avg 0.95), C4 0.95 (avg 0.95), C4g 0.95 (avg 0.95), C5 0.95 (avg 0.95), C6 0.85 (avg 0.85), C7 0.95 (avg 0.95), C8 0.85 (avg 0.85), C9 0.95 (avg 0.95)
- Risk committee (Context Handshake) interventions: 25
  - 2021-03-31: treasury £33,515.94, C2->0.95, C6->0.95, VaR (current £5,638.82 / stressed £2,167.54) ratio 2.60
  - 2021-04-30: treasury £33,501.69, C2->0.95, C6->0.95, VaR (current £5,638.82 / stressed £2,167.54) ratio 2.60
  - 2021-05-30: treasury £33,511.68, C2->0.95, C6->0.95, VaR (current £5,638.82 / stressed £2,167.54) ratio 2.60
  - 2021-06-29: treasury £33,505.50, C2->0.95, C6->0.95, VaR (current £5,638.82 / stressed £2,167.54) ratio 2.60
  - 2021-07-29: treasury £33,496.35, C2->0.95, C6->0.95, VaR (current £5,638.82 / stressed £2,167.54) ratio 2.60
  - 2021-08-28: treasury £33,485.79, C2->0.95, C6->0.95, VaR (current £5,638.82 / stressed £2,167.54) ratio 2.60
  - 2021-09-27: treasury £33,462.00, C2->0.95, C6->0.95, VaR (current £5,638.82 / stressed £2,167.54) ratio 2.60
  - 2021-10-27: treasury £33,448.16, C2->0.95, C6->0.95, VaR (current £5,638.82 / stressed £2,167.54) ratio 2.60
  - 2021-11-26: treasury £33,433.14, C2->0.95, C6->0.95, VaR (current £5,638.82 / stressed £2,167.54) ratio 2.60
  - 2021-12-26: treasury £33,404.52, C2->0.95, C6->0.95, VaR (current £5,638.82 / stressed £2,167.54) ratio 2.60
  - 2021-04-25: treasury £33,352.52, C2->0.95, C6->0.95, C8->0.95, VaR (current £6,385.86 / stressed £2,348.66) ratio 2.72
  - 2021-05-25: treasury £33,372.53, C2->0.95, C6->0.95, C8->0.95, VaR (current £6,385.86 / stressed £2,348.66) ratio 2.72
  - 2021-07-24: treasury £33,374.74, C2->1.00, C6->1.00, C8->1.00, VaR (current £6,385.86 / stressed £2,348.66) ratio 2.72
  - 2021-08-23: treasury £33,374.03, C2->0.95, C6->0.95, C8->0.95, VaR (current £6,385.86 / stressed £2,348.66) ratio 2.72
  - 2021-09-22: treasury £33,369.64, C2->0.95, C6->0.95, C8->0.95, VaR (current £6,385.86 / stressed £2,348.66) ratio 2.72
  - 2021-10-22: treasury £33,369.89, C2->0.95, C6->0.95, C8->0.95, VaR (current £6,385.86 / stressed £2,348.66) ratio 2.72
  - 2021-11-21: treasury £33,371.52, C2->0.95, C6->0.95, C8->0.95, VaR (current £6,385.86 / stressed £2,348.66) ratio 2.72
  - 2021-08-19: treasury £33,367.35, C2->0.95, C3->1.00, C6->0.95, C8->0.95, VaR (current £6,408.21 / stressed £2,350.86) ratio 2.73
  - 2021-10-18: treasury £33,369.14, C2->0.95, C3->1.00, C6->0.95, C8->0.95, VaR (current £6,408.21 / stressed £2,350.86) ratio 2.73
  - 2021-11-17: treasury £33,370.16, C2->0.95, C3->1.00, C6->0.95, C8->0.95, VaR (current £6,408.21 / stressed £2,350.86) ratio 2.73
  - 2021-12-17: treasury £33,370.51, C2->0.95, C3->1.00, C6->0.95, C8->0.95, VaR (current £6,408.21 / stressed £2,350.86) ratio 2.73
  - 2021-09-05: treasury £33,374.71, C2->0.95, C3->1.00, C6->0.95, C8->0.95, C9->1.00, VaR (current £6,494.61 / stressed £2,359.36) ratio 2.75
  - 2021-10-05: treasury £33,374.78, C2->0.95, C3->1.00, C6->0.95, C8->0.95, C9->1.00, VaR (current £6,494.61 / stressed £2,359.36) ratio 2.75
  - 2021-10-02: treasury £33,379.81, C2->0.95, C3->1.00, C4->1.00, C6->0.95, C8->0.95, C9->1.00, VaR (current £6,678.45 / stressed £2,398.29) ratio 2.78
  - 2021-12-31: treasury £33,403.68, C2->0.95, C3->1.00, C4->1.00, C6->0.95, C8->0.95, C9->1.00, VaR (current £6,678.45 / stressed £2,398.29) ratio 2.78
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.68
- Worst single period: C5 on 2021-01-08 period 39, net margin £-2.10

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £201.12
- Highest CLV: C6 (£613.66); Lowest CLV: C1 (£-81.13)
- Bill shock events (>=20%): 42 -- C1 2021-01-31 (39%); C1 2021-04-30 (22%); C1 2021-12-31 (22%); C1g 2021-12-31 (35%); C5 2021-01-31 (49%); C5 2021-05-31 (24%); C5 2021-06-30 (34%); C5 2021-10-31 (33%); C5 2021-11-30 (55%); C5 2021-12-31 (21%); C7 2021-01-31 (56%); C7 2021-05-31 (29%); C7 2021-06-30 (47%); C7 2021-10-31 (56%); C7 2021-11-30 (60%); C2 2021-04-30 (80%); C2g 2021-04-30 (75%); C6 2021-04-30 (94%); C6 2021-06-30 (37%); C6 2021-10-31 (29%); C6 2021-11-30 (53%); C8 2021-02-28 (21%); C8 2021-04-30 (103%); C8 2021-05-31 (28%); C8 2021-06-30 (63%); C8 2021-09-30 (24%); C8 2021-10-31 (78%); C8 2021-11-30 (81%); C3 2021-04-30 (21%); C3 2021-07-31 (211%); C3g 2021-07-31 (277%); C9 2021-02-28 (23%); C9 2021-05-31 (24%); C9 2021-06-30 (50%); C9 2021-07-31 (118%); C9 2021-08-31 (23%); C9 2021-09-30 (21%); C9 2021-10-31 (68%); C9 2021-11-30 (48%); C9 2021-12-31 (23%); C4 2021-10-31 (394%); C4g 2021-10-31 (352%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £106.09-£402.76/MWh, net margin £-7.71 -- **net-negative**
- C1g (gas): tariff £18.18-£105.38/MWh, net margin £-23.54 -- **net-negative**
- C2 (electricity): tariff £106.09-£231.72/MWh, net margin £93.16
- C2g (gas): tariff £13.14-£24.47/MWh, net margin £12.22
- C3 (electricity): tariff £53.60-£173.71/MWh, net margin £2.72
- C3g (gas): tariff £7.79-£31.30/MWh, net margin £1.73
- C4 (electricity): tariff £71.59-£385.03/MWh, net margin £18.42
- C4g (gas): tariff £12.67-£62.80/MWh, net margin £-4.56 -- **net-negative**
- C5 (electricity): tariff £106.09-£402.76/MWh, net margin £-76.55 -- **net-negative**
- C6 (electricity): tariff £106.09-£231.72/MWh, net margin £-86.92 -- **net-negative**
- C7 (electricity): tariff £106.09-£402.76/MWh, net margin £-27.01 -- **net-negative**
- C8 (electricity): tariff £106.09-£231.72/MWh, net margin £54.06
- C9 (electricity): tariff £53.60-£173.71/MWh, net margin £-19.48 -- **net-negative**
- Cost to serve per customer (whole-run total, average £662.26, range £88.06-£1,431.94):
  - C1: cost to serve £644.14, net margin after cost to serve £-290.51 -- **net-negative**
  - C1g: cost to serve £103.25, net margin after cost to serve £171.33
  - C2: cost to serve £747.57, net margin after cost to serve £387.84
  - C2g: cost to serve £121.48, net margin after cost to serve £333.75
  - C3: cost to serve £589.92, net margin after cost to serve £-289.89 -- **net-negative**
  - C3g: cost to serve £88.06, net margin after cost to serve £191.96
  - C4: cost to serve £690.13, net margin after cost to serve £-125.32 -- **net-negative**
  - C4g: cost to serve £189.40, net margin after cost to serve £237.83
  - C5: cost to serve £1,431.94, net margin after cost to serve £231.15
  - C6: cost to serve £1,417.21, net margin after cost to serve £876.34
  - C7: cost to serve £938.79, net margin after cost to serve £261.58
  - C8: cost to serve £892.43, net margin after cost to serve £655.87
  - C9: cost to serve £755.08, net margin after cost to serve £-20.89 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 111.3% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.864, average bill shock 23.7%, bad debt provision £313.72, avg complaint probability 4.5%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £424.45 vs. naked (unhedged) net margin: £-1,405.68
- hedging added £1,830.13 vs. a fully unhedged book (actual net £424.45 vs. naked net £-1,405.68)
  - C1: actual £47.27 vs. naked £452.33 -- hedging cost £405.06
  - C1g: actual £33.21 vs. naked £-79.05 -- hedging added £112.26
  - C2: actual £88.82 vs. naked £398.14 -- hedging cost £309.32
  - C2g: actual £4.80 vs. naked £-552.00 -- hedging added £556.81
  - C3: actual £10.32 vs. naked £-142.21 -- hedging added £152.52
  - C3g: actual £-0.30 vs. naked £-632.96 -- hedging added £632.67
  - C4: actual £82.55 vs. naked £746.66 -- hedging cost £664.11
  - C4g: actual £7.71 vs. naked £-991.43 -- hedging added £999.15
  - C5: actual £159.10 vs. naked £869.48 -- hedging cost £710.38
  - C6: actual £-174.68 vs. naked £-1,671.90 -- hedging added £1,497.22
  - C7: actual £136.25 vs. naked £1,116.65 -- hedging cost £980.40
  - C8: actual £22.79 vs. naked £-162.14 -- hedging added £184.92
  - C9: actual £6.61 vs. naked £-757.24 -- hedging added £763.85

**Year narrative:** 2021 (flagged crisis year) produced a net loss of £-63.46 across 13 accounts. The risk committee intervened 25 time(s), raising hedge fractions in response to elevated VaR. 42 customer(s) experienced a bill shock of >=20%.

## 2022

**Trading & Risk**

- Net margin: £825.91 (gross £1,397.89, capital £571.99)
  - Electricity: gross £1,271.52, capital £560.03, net £711.49
  - Gas: gross £126.37, capital £11.96, net £114.42
- Treasury at year end: £33,950.51
- Hedge fraction at first renewal this year (avg across year's terms): C1 1.00 (avg 1.00), C1g 1.00 (avg 1.00), C2 0.95 (avg 0.95), C2g 1.00 (avg 1.00), C3 1.00 (avg 1.00), C3g 1.00 (avg 1.00), C4 1.00 (avg 1.00), C4g 1.00 (avg 1.00), C5 1.00 (avg 1.00), C6 0.95 (avg 0.95), C7 1.00 (avg 1.00), C8 0.95 (avg 0.95), C9 1.00 (avg 1.00)
- Risk committee (Context Handshake) interventions: 35
  - 2022-01-25: treasury £33,384.67, C2->0.95, C6->0.95, VaR (current £5,638.82 / stressed £2,167.54) ratio 2.60
  - 2022-02-24: treasury £33,375.77, C2->0.95, C6->0.95, VaR (current £5,638.82 / stressed £2,167.54) ratio 2.60
  - 2022-03-26: treasury £33,346.23, C2->0.95, C6->0.95, VaR (current £5,638.82 / stressed £2,167.54) ratio 2.60
  - 2022-01-20: treasury £33,373.30, C2->0.95, C6->0.95, C8->0.95, VaR (current £6,385.86 / stressed £2,348.66) ratio 2.72
  - 2022-02-19: treasury £33,373.87, C2->0.95, C6->0.95, C8->0.95, VaR (current £6,385.86 / stressed £2,348.66) ratio 2.72
  - 2022-03-21: treasury £33,366.69, C2->0.95, C6->0.95, C8->0.95, VaR (current £6,385.86 / stressed £2,348.66) ratio 2.72
  - 2022-01-16: treasury £33,371.08, C2->0.95, C3->1.00, C6->0.95, C8->0.95, VaR (current £6,408.21 / stressed £2,350.86) ratio 2.73
  - 2022-05-16: treasury £33,373.45, C2->0.95, C3->1.00, C6->0.95, C8->0.95, VaR (current £6,408.21 / stressed £2,350.86) ratio 2.73
  - 2022-06-15: treasury £33,374.80, C2->0.95, C3->1.00, C6->0.95, C8->0.95, VaR (current £6,408.21 / stressed £2,350.86) ratio 2.73
  - 2022-01-03: treasury £33,377.66, C2->0.95, C3->1.00, C6->0.95, C8->0.95, C9->1.00, VaR (current £6,494.61 / stressed £2,359.36) ratio 2.75
  - 2022-03-04: treasury £33,379.62, C2->0.95, C3->1.00, C6->0.95, C8->0.95, C9->1.00, VaR (current £6,494.61 / stressed £2,359.36) ratio 2.75
  - 2022-04-03: treasury £33,377.03, C2->0.95, C3->1.00, C6->0.95, C8->0.95, C9->1.00, VaR (current £6,494.61 / stressed £2,359.36) ratio 2.75
  - 2022-06-02: treasury £33,381.04, C2->0.95, C3->1.00, C6->0.95, C8->0.95, C9->1.00, VaR (current £6,494.61 / stressed £2,359.36) ratio 2.75
  - 2022-01-30: treasury £33,411.88, C2->0.95, C6->0.95, C8->0.95, VaR (current £6,678.45 / stressed £2,398.29) ratio 2.78
  - 2022-04-30: treasury £33,434.92, C2->0.95, C3->1.00, C4->1.00, C6->0.95, C8->0.95, C9->1.00, VaR (current £6,678.45 / stressed £2,398.29) ratio 2.78
  - 2022-05-30: treasury £33,443.35, C2->0.95, C6->0.95, C8->0.95, VaR (current £6,678.45 / stressed £2,398.29) ratio 2.78
  - 2022-01-19: treasury £33,474.30, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C6->0.95, C8->0.95, C9->1.00, VaR (current £6,724.61 / stressed £2,408.36) ratio 2.79
  - 2022-05-19: treasury £33,492.09, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C6->0.95, C8->0.95, C9->1.00, VaR (current £6,724.61 / stressed £2,408.36) ratio 2.79
  - 2022-11-15: treasury £33,512.67, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C6->0.95, C8->0.95, C9->1.00, VaR (current £6,724.61 / stressed £2,408.36) ratio 2.79
  - 2022-12-15: treasury £33,516.38, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C6->0.95, C8->0.95, C9->1.00, VaR (current £6,724.61 / stressed £2,408.36) ratio 2.79
  - 2022-01-06: treasury £33,550.48, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C5->1.00, C6->0.95, C8->0.95, C9->1.00, VaR (current £7,136.76 / stressed £2,498.22) ratio 2.86
  - 2022-03-07: treasury £33,597.09, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C5->1.00, C6->0.95, C8->0.95, C9->1.00, VaR (current £7,136.76 / stressed £2,498.22) ratio 2.86
  - 2022-08-04: treasury £33,655.82, C2->0.95, C6->0.95, C8->0.95, VaR (current £7,136.76 / stressed £2,498.22) ratio 2.86
  - 2022-01-01: treasury £33,708.28, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C5->1.00, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £7,347.80 / stressed £2,544.24) ratio 2.89
  - 2022-03-02: treasury £33,751.82, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C5->1.00, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £7,347.80 / stressed £2,544.24) ratio 2.89
  - 2022-05-31: treasury £33,789.89, C1->1.00, C2->0.95, C3->1.00, C4->1.00, C5->1.00, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £7,347.80 / stressed £2,544.24) ratio 2.89
  - 2022-04-27: treasury £33,856.97, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £7,211.58 / stressed £2,515.33) ratio 2.87
  - 2022-06-26: treasury £33,881.41, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £7,211.58 / stressed £2,515.33) ratio 2.87
  - 2022-07-26: treasury £33,891.36, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £7,211.58 / stressed £2,515.33) ratio 2.87
  - 2022-08-25: treasury £33,898.62, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £7,211.58 / stressed £2,515.33) ratio 2.87
  - 2022-10-24: treasury £33,919.99, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £7,211.58 / stressed £2,515.33) ratio 2.87
  - 2022-11-23: treasury £33,935.83, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C6->0.95, C7->1.00, C8->0.95, C9->1.00, VaR (current £7,211.58 / stressed £2,515.33) ratio 2.87
  - 2022-06-14: treasury £34,070.59, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C7->1.00, C8->0.95, C9->1.00, VaR (current £5,460.16 / stressed £2,143.57) ratio 2.55
  - 2022-10-12: treasury £34,078.34, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C7->1.00, C8->0.95, C9->1.00, VaR (current £5,460.16 / stressed £2,143.57) ratio 2.55
  - 2022-12-11: treasury £34,121.20, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C7->1.00, C8->0.95, C9->1.00, VaR (current £5,460.16 / stressed £2,143.57) ratio 2.55
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.76
- Worst single period: C6 on 2022-01-24 period 34, net margin £-2.43

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £201.12
- Highest CLV: C6 (£613.66); Lowest CLV: C1 (£-81.13)
- Bill shock events (>=20%): 44 -- C1 2022-01-31 (223%); C1 2022-04-30 (21%); C1g 2022-01-31 (343%); C5 2022-01-31 (276%); C5 2022-02-28 (21%); C5 2022-04-30 (21%); C5 2022-05-31 (27%); C5 2022-11-30 (52%); C5 2022-12-31 (36%); C7 2022-01-31 (312%); C7 2022-02-28 (26%); C7 2022-04-30 (21%); C7 2022-05-31 (35%); C7 2022-06-30 (26%); C7 2022-09-30 (31%); C7 2022-11-30 (58%); C7 2022-12-31 (52%); C2 2022-04-30 (75%); C2g 2022-03-31 (26%); C2g 2022-04-30 (345%); C6 2022-04-30 (64%); C6 2022-05-31 (24%); C6 2022-09-30 (27%); C6 2022-11-30 (45%); C6 2022-12-31 (34%); C8 2022-02-28 (22%); C8 2022-04-30 (60%); C8 2022-05-31 (40%); C8 2022-06-30 (34%); C8 2022-07-31 (21%); C8 2022-09-30 (83%); C8 2022-10-31 (20%); C8 2022-11-30 (67%); C8 2022-12-31 (58%); C3 2022-07-31 (52%); C3g 2022-07-31 (200%); C9 2022-05-31 (31%); C9 2022-06-30 (30%); C9 2022-09-30 (49%); C9 2022-10-31 (33%); C9 2022-11-30 (41%); C9 2022-12-31 (54%); C4 2022-10-31 (29%); C4g 2022-10-31 (202%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £374.60-£402.76/MWh, net margin £47.90
- C1g (gas): tariff £102.05-£105.38/MWh, net margin £33.74
- C2 (electricity): tariff £231.72-£487.81/MWh, net margin £114.61
- C2g (gas): tariff £24.47-£127.96/MWh, net margin £36.40
- C3 (electricity): tariff £173.71-£258.86/MWh, net margin £15.97
- C3g (gas): tariff £31.30-£97.22/MWh, net margin £18.82
- C4 (electricity): tariff £385.03-£473.79/MWh, net margin £75.00
- C4g (gas): tariff £62.80-£196.77/MWh, net margin £25.46
- C5 (electricity): tariff £374.60-£402.76/MWh, net margin £166.55
- C6 (electricity): tariff £231.72-£487.81/MWh, net margin £26.69
- C7 (electricity): tariff £374.60-£402.76/MWh, net margin £140.09
- C8 (electricity): tariff £231.72-£487.81/MWh, net margin £93.58
- C9 (electricity): tariff £173.71-£258.86/MWh, net margin £31.11
- Cost to serve per customer (whole-run total, average £662.26, range £88.06-£1,431.94):
  - C1: cost to serve £644.14, net margin after cost to serve £-290.51 -- **net-negative**
  - C1g: cost to serve £103.25, net margin after cost to serve £171.33
  - C2: cost to serve £747.57, net margin after cost to serve £387.84
  - C2g: cost to serve £121.48, net margin after cost to serve £333.75
  - C3: cost to serve £589.92, net margin after cost to serve £-289.89 -- **net-negative**
  - C3g: cost to serve £88.06, net margin after cost to serve £191.96
  - C4: cost to serve £690.13, net margin after cost to serve £-125.32 -- **net-negative**
  - C4g: cost to serve £189.40, net margin after cost to serve £237.83
  - C5: cost to serve £1,431.94, net margin after cost to serve £231.15
  - C6: cost to serve £1,417.21, net margin after cost to serve £876.34
  - C7: cost to serve £938.79, net margin after cost to serve £261.58
  - C8: cost to serve £892.43, net margin after cost to serve £655.87
  - C9: cost to serve £755.08, net margin after cost to serve £-20.89 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 40.9% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.865, average bill shock 25.6%, bad debt provision £803.16, avg complaint probability 4.5%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £1,121.37 vs. naked (unhedged) net margin: £19,030.19
- hedging cost £17,908.82 vs. a fully unhedged book (actual net £1,121.37 vs. naked net £19,030.19)
  - C1: actual £24.59 vs. naked £872.20 -- hedging cost £847.61
  - C1g: actual £38.63 vs. naked £703.43 -- hedging cost £664.80
  - C2: actual £147.50 vs. naked £1,876.05 -- hedging cost £1,728.55
  - C2g: actual £53.03 vs. naked £399.40 -- hedging cost £346.38
  - C3: actual £22.99 vs. naked £238.03 -- hedging cost £215.04
  - C3g: actual £44.25 vs. naked £161.76 -- hedging cost £117.51
  - C4: actual £55.27 vs. naked £2,199.96 -- hedging cost £2,144.69
  - C4g: actual £96.22 vs. naked £2,961.18 -- hedging cost £2,864.96
  - C5: actual £116.77 vs. naked £3,476.90 -- hedging cost £3,360.13
  - C6: actual £189.89 vs. naked £1,020.98 -- hedging cost £831.09
  - C7: actual £81.56 vs. naked £2,656.38 -- hedging cost £2,574.81
  - C8: actual £190.59 vs. naked £2,107.91 -- hedging cost £1,917.32
  - C9: actual £60.08 vs. naked £356.01 -- hedging cost £295.94

**Year narrative:** 2022 (flagged crisis year) produced a net gain of £825.91 across 13 accounts. The risk committee intervened 35 time(s), raising hedge fractions in response to elevated VaR. 44 customer(s) experienced a bill shock of >=20%.

## 2023

**Trading & Risk**

- Net margin: £1,308.73 (gross £1,961.92, capital £653.18)
  - Electricity: gross £1,684.12, capital £619.08, net £1,065.04
  - Gas: gross £277.80, capital £34.10, net £243.70
- Treasury at year end: £35,149.39
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.90 (avg 0.90), C1g 0.90 (avg 0.90), C2 0.85 (avg 0.85), C2g 0.90 (avg 0.90), C3 0.90 (avg 0.90), C3g 0.90 (avg 0.90), C4 0.90 (avg 0.90), C4g 0.90 (avg 0.90), C5 0.90 (avg 0.90), C6 0.85 (avg 0.85), C7 0.90 (avg 0.90), C8 0.85 (avg 0.85), C9 0.90 (avg 0.90)
- Risk committee (Context Handshake) interventions: 2
  - 2023-01-10: treasury £34,147.86, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C7->1.00, C8->0.95, C9->1.00, VaR (current £5,460.16 / stressed £2,143.57) ratio 2.55
  - 2023-02-09: treasury £34,185.26, C1->1.00, C3->1.00, C4->1.00, C5->1.00, C7->1.00, C8->0.95, C9->1.00, VaR (current £5,460.16 / stressed £2,143.57) ratio 2.55
- VaR ratio (current vs stressed floor, avg of this year's wake-ups): 2.55
- Worst single period: C2g on 2023-03-31 period 1, net margin £-1.69

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £201.12
- Highest CLV: C6 (£613.66); Lowest CLV: C1 (£-81.13)
- Bill shock events (>=20%): 33 -- C1 2023-04-30 (21%); C5 2023-05-31 (23%); C5 2023-06-30 (26%); C5 2023-10-31 (33%); C5 2023-11-30 (55%); C7 2023-05-31 (32%); C7 2023-06-30 (35%); C7 2023-10-31 (52%); C7 2023-11-30 (65%); C2 2023-04-30 (50%); C2g 2023-04-30 (47%); C6 2023-04-30 (54%); C6 2023-05-31 (24%); C6 2023-06-30 (24%); C6 2023-10-31 (41%); C6 2023-11-30 (46%); C8 2023-04-30 (55%); C8 2023-05-31 (43%); C8 2023-06-30 (44%); C8 2023-10-31 (101%); C8 2023-11-30 (69%); C3 2023-07-31 (36%); C3g 2023-07-31 (56%); C9 2023-02-28 (20%); C9 2023-04-30 (25%); C9 2023-05-31 (34%); C9 2023-06-30 (46%); C9 2023-07-31 (28%); C9 2023-09-30 (23%); C9 2023-10-31 (76%); C9 2023-11-30 (53%); C4 2023-10-31 (67%); C4g 2023-10-31 (81%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £166.36-£374.60/MWh, net margin £23.97
- C1g (gas): tariff £42.92-£102.05/MWh, net margin £37.74
- C2 (electricity): tariff £279.73-£487.81/MWh, net margin £225.01
- C2g (gas): tariff £68.57-£127.96/MWh, net margin £80.61
- C3 (electricity): tariff £158.17-£258.86/MWh, net margin £36.47
- C3g (gas): tariff £40.69-£97.22/MWh, net margin £42.68
- C4 (electricity): tariff £145.89-£473.79/MWh, net margin £59.33
- C4g (gas): tariff £35.29-£196.77/MWh, net margin £82.67
- C5 (electricity): tariff £166.36-£374.60/MWh, net margin £109.74
- C6 (electricity): tariff £279.73-£487.81/MWh, net margin £198.67
- C7 (electricity): tariff £166.36-£374.60/MWh, net margin £78.64
- C8 (electricity): tariff £279.73-£487.81/MWh, net margin £254.09
- C9 (electricity): tariff £158.17-£258.86/MWh, net margin £79.11
- Cost to serve per customer (whole-run total, average £662.26, range £88.06-£1,431.94):
  - C1: cost to serve £644.14, net margin after cost to serve £-290.51 -- **net-negative**
  - C1g: cost to serve £103.25, net margin after cost to serve £171.33
  - C2: cost to serve £747.57, net margin after cost to serve £387.84
  - C2g: cost to serve £121.48, net margin after cost to serve £333.75
  - C3: cost to serve £589.92, net margin after cost to serve £-289.89 -- **net-negative**
  - C3g: cost to serve £88.06, net margin after cost to serve £191.96
  - C4: cost to serve £690.13, net margin after cost to serve £-125.32 -- **net-negative**
  - C4g: cost to serve £189.40, net margin after cost to serve £237.83
  - C5: cost to serve £1,431.94, net margin after cost to serve £231.15
  - C6: cost to serve £1,417.21, net margin after cost to serve £876.34
  - C7: cost to serve £938.79, net margin after cost to serve £261.58
  - C8: cost to serve £892.43, net margin after cost to serve £655.87
  - C9: cost to serve £755.08, net margin after cost to serve £-20.89 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 33.3% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.883, average bill shock 13.8%, bad debt provision £767.40, avg complaint probability 3.9%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £1,663.11 vs. naked (unhedged) net margin: £5,511.09
- hedging cost £3,847.98 vs. a fully unhedged book (actual net £1,663.11 vs. naked net £5,511.09)
  - C1: actual £48.30 vs. naked £215.57 -- hedging cost £167.28
  - C1g: actual £41.41 vs. naked £40.40 -- hedging added £1.01
  - C2: actual £253.77 vs. naked £1,209.11 -- hedging cost £955.34
  - C2g: actual £92.71 vs. naked £336.31 -- hedging cost £243.60
  - C3: actual £55.02 vs. naked £243.25 -- hedging cost £188.23
  - C3g: actual £46.31 vs. naked £37.04 -- hedging added £9.26
  - C4: actual £81.06 vs. naked £351.24 -- hedging cost £270.18
  - C4g: actual £58.93 vs. naked £-41.99 -- hedging added £100.92
  - C5: actual £170.62 vs. naked £466.86 -- hedging cost £296.24
  - C6: actual £239.78 vs. naked £360.67 -- hedging cost £120.89
  - C7: actual £140.90 vs. naked £551.51 -- hedging cost £410.61
  - C8: actual £307.91 vs. naked £1,298.90 -- hedging cost £990.99
  - C9: actual £126.40 vs. naked £442.23 -- hedging cost £315.82

**Year narrative:** 2023 produced a net gain of £1,308.73 across 13 accounts. The risk committee intervened 2 time(s), raising hedge fractions in response to elevated VaR. 33 customer(s) experienced a bill shock of >=20%.

## 2024

**Trading & Risk**

- Net margin: £1,220.79 (gross £1,913.60, capital £692.80)
  - Electricity: gross £1,662.10, capital £641.09, net £1,021.01
  - Gas: gross £251.50, capital £51.72, net £199.79
- Treasury at year end: £36,690.66
- Hedge fraction at first renewal this year (avg across year's terms): C1 0.85 (avg 0.85), C1g 0.90 (avg 0.90), C2 0.85 (avg 0.85), C2g 0.85 (avg 0.85), C3 0.85 (avg 0.85), C3g 1.00 (avg 1.00), C4 0.85 (avg 0.85), C4g 1.00 (avg 1.00), C5 0.85 (avg 0.85), C6 0.85 (avg 0.85), C7 0.85 (avg 0.85), C8 0.85 (avg 0.85), C9 0.85 (avg 0.85)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C2g on 2024-03-30 period 1, net margin £-0.51

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £201.12
- Highest CLV: C6 (£613.66); Lowest CLV: C1 (£-81.13)
- Bill shock events (>=20%): 37 -- C1 2024-01-31 (54%); C1 2024-04-30 (24%); C1g 2024-01-31 (56%); C5 2024-01-31 (47%); C5 2024-02-29 (22%); C5 2024-05-31 (27%); C5 2024-09-30 (20%); C5 2024-10-31 (28%); C5 2024-11-30 (38%); C7 2024-01-31 (45%); C7 2024-02-29 (26%); C7 2024-04-30 (21%); C7 2024-05-31 (36%); C7 2024-09-30 (33%); C7 2024-10-31 (35%); C7 2024-11-30 (46%); C2 2024-04-30 (61%); C2g 2024-04-30 (53%); C6 2024-04-30 (62%); C6 2024-05-31 (30%); C6 2024-09-30 (26%); C6 2024-10-31 (24%); C6 2024-11-30 (39%); C8 2024-02-29 (23%); C8 2024-04-30 (64%); C8 2024-05-31 (51%); C8 2024-07-31 (29%); C8 2024-09-30 (78%); C8 2024-10-31 (38%); C8 2024-11-30 (62%); C3 2024-04-30 (22%); C9 2024-04-30 (22%); C9 2024-05-31 (50%); C9 2024-07-31 (40%); C9 2024-09-30 (56%); C9 2024-10-31 (24%); C9 2024-11-30 (48%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £159.84-£166.36/MWh, net margin £48.11
- C1g (gas): tariff £42.73-£42.92/MWh, net margin £41.49
- C2 (electricity): tariff £126.19-£279.73/MWh, net margin £131.93
- C2g (gas): tariff £32.50-£68.57/MWh, net margin £44.02
- C3 (electricity): tariff £123.97-£158.17/MWh, net margin £47.90
- C3g (gas): tariff £33.40-£40.69/MWh, net margin £47.70
- C4 (electricity): tariff £128.74-£145.89/MWh, net margin £77.81
- C4g (gas): tariff £35.29-£37.99/MWh, net margin £66.57
- C5 (electricity): tariff £159.84-£166.36/MWh, net margin £168.70
- C6 (electricity): tariff £126.19-£279.73/MWh, net margin £122.33
- C7 (electricity): tariff £159.84-£166.36/MWh, net margin £140.04
- C8 (electricity): tariff £126.19-£279.73/MWh, net margin £180.92
- C9 (electricity): tariff £123.97-£158.17/MWh, net margin £103.27
- Cost to serve per customer (whole-run total, average £662.26, range £88.06-£1,431.94):
  - C1: cost to serve £644.14, net margin after cost to serve £-290.51 -- **net-negative**
  - C1g: cost to serve £103.25, net margin after cost to serve £171.33
  - C2: cost to serve £747.57, net margin after cost to serve £387.84
  - C2g: cost to serve £121.48, net margin after cost to serve £333.75
  - C3: cost to serve £589.92, net margin after cost to serve £-289.89 -- **net-negative**
  - C3g: cost to serve £88.06, net margin after cost to serve £191.96
  - C4: cost to serve £690.13, net margin after cost to serve £-125.32 -- **net-negative**
  - C4g: cost to serve £189.40, net margin after cost to serve £237.83
  - C5: cost to serve £1,431.94, net margin after cost to serve £231.15
  - C6: cost to serve £1,417.21, net margin after cost to serve £876.34
  - C7: cost to serve £938.79, net margin after cost to serve £261.58
  - C8: cost to serve £892.43, net margin after cost to serve £655.87
  - C9: cost to serve £755.08, net margin after cost to serve £-20.89 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 36.2% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 156, average clarity 0.883, average bill shock 13.6%, bad debt provision £372.60, avg complaint probability 3.8%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £449.65 vs. naked (unhedged) net margin: £-1,107.43
- hedging added £1,557.08 vs. a fully unhedged book (actual net £449.65 vs. naked net £-1,107.43)
  - C1: actual £17.56 vs. naked £41.66 -- hedging cost £24.11
  - C1g: actual £13.61 vs. naked £-28.42 -- hedging added £42.03
  - C2: actual £71.49 vs. naked £215.79 -- hedging cost £144.30
  - C2g: actual £21.17 vs. naked £-121.41 -- hedging added £142.58
  - C3: actual £30.05 vs. naked £46.08 -- hedging cost £16.02
  - C3g: actual £41.17 vs. naked £-122.07 -- hedging added £163.24
  - C4: actual £38.78 vs. naked £68.79 -- hedging cost £30.00
  - C4g: actual £49.89 vs. naked £-118.06 -- hedging added £167.96
  - C5: actual £50.28 vs. naked £-57.86 -- hedging added £108.15
  - C6: actual £-28.90 vs. naked £-875.20 -- hedging added £846.31
  - C7: actual £52.99 vs. naked £70.51 -- hedging cost £17.51
  - C8: actual £48.19 vs. naked £-101.93 -- hedging added £150.12
  - C9: actual £43.35 vs. naked £-125.29 -- hedging added £168.63

**Year narrative:** 2024 produced a net gain of £1,220.79 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 37 customer(s) experienced a bill shock of >=20%.

## 2025

**Trading & Risk**

- Net margin: £366.40 (gross £691.95, capital £325.54)
  - Electricity: gross £602.24, capital £312.70, net £289.54
  - Gas: gross £89.71, capital £12.84, net £76.86
- Treasury at year end: £36,773.89
- Hedge fraction at first renewal this year (avg across year's terms): C2 0.85 (avg 0.85), C2g 0.95 (avg 0.95), C6 0.95 (avg 0.95), C8 0.95 (avg 0.95)
- Risk committee (Context Handshake) interventions: 0
- VaR ratio (current vs stressed floor): no risk committee wake-up this year
- Worst single period: C6 on 2025-01-08 period 34, net margin £-2.04

**Customer Book**

- Active accounts: 13 (C1, C1g, C2, C2g, C3, C3g, C4, C4g, C5, C6, C7, C8, C9)
  - Resi electricity: 4, SME electricity: 2, gas (dual-fuel): 4
- New acquisitions this year: none
- Losses (churn / home move) during year: Not available in current run output (see REPORTING_BACKLOG.md) -- no churn mechanic is applied to the actual customer roster in the settlement run; 4b's churn/home-move models are point-in-time risk scores, not roster events.
- Average CLV across book (whole-run projection, per billing account): £201.12
- Highest CLV: C6 (£613.66); Lowest CLV: C1 (£-81.13)
- Bill shock events (>=20%): 32 -- C1 2025-04-30 (23%); C1 2025-06-07 (78%); C1g 2025-06-07 (77%); C5 2025-04-30 (31%); C5 2025-06-07 (79%); C7 2025-01-31 (21%); C7 2025-04-30 (37%); C7 2025-05-31 (22%); C7 2025-06-07 (80%); C2 2025-04-30 (97%); C2 2025-06-07 (78%); C2g 2025-04-30 (48%); C2g 2025-06-07 (77%); C6 2025-01-31 (25%); C6 2025-02-28 (20%); C6 2025-04-30 (70%); C6 2025-05-31 (21%); C6 2025-06-07 (76%); C8 2025-01-31 (39%); C8 2025-02-28 (24%); C8 2025-04-30 (44%); C8 2025-05-31 (38%); C8 2025-06-07 (73%); C3 2025-04-30 (22%); C3 2025-06-07 (78%); C3g 2025-06-07 (77%); C9 2025-01-31 (22%); C9 2025-04-30 (26%); C9 2025-05-31 (34%); C9 2025-06-07 (71%); C4 2025-06-07 (78%); C4g 2025-06-07 (77%)
- Churn risk: how many customers above threshold at year end: Not available in current run output (see REPORTING_BACKLOG.md)

**Pricing & Margin**

- C1 (electricity): tariff £159.84/MWh, net margin £18.20
- C1g (gas): tariff £42.73/MWh, net margin £14.21
- C2 (electricity): tariff £126.19-£320.90/MWh, net margin £61.60
- C2g (gas): tariff £32.50-£51.55/MWh, net margin £12.46
- C3 (electricity): tariff £123.97/MWh, net margin £12.26
- C3g (gas): tariff £33.40/MWh, net margin £18.91
- C4 (electricity): tariff £128.74/MWh, net margin £23.02
- C4g (gas): tariff £37.99/MWh, net margin £31.28
- C5 (electricity): tariff £159.84/MWh, net margin £58.55
- C6 (electricity): tariff £126.19-£320.90/MWh, net margin £4.31
- C7 (electricity): tariff £159.84/MWh, net margin £56.30
- C8 (electricity): tariff £126.19-£320.90/MWh, net margin £34.47
- C9 (electricity): tariff £123.97/MWh, net margin £20.83
- Cost to serve per customer (whole-run total, average £662.26, range £88.06-£1,431.94):
  - C1: cost to serve £644.14, net margin after cost to serve £-290.51 -- **net-negative**
  - C1g: cost to serve £103.25, net margin after cost to serve £171.33
  - C2: cost to serve £747.57, net margin after cost to serve £387.84
  - C2g: cost to serve £121.48, net margin after cost to serve £333.75
  - C3: cost to serve £589.92, net margin after cost to serve £-289.89 -- **net-negative**
  - C3g: cost to serve £88.06, net margin after cost to serve £191.96
  - C4: cost to serve £690.13, net margin after cost to serve £-125.32 -- **net-negative**
  - C4g: cost to serve £189.40, net margin after cost to serve £237.83
  - C5: cost to serve £1,431.94, net margin after cost to serve £231.15
  - C6: cost to serve £1,417.21, net margin after cost to serve £876.34
  - C7: cost to serve £938.79, net margin after cost to serve £261.58
  - C8: cost to serve £892.43, net margin after cost to serve £655.87
  - C9: cost to serve £755.08, net margin after cost to serve £-20.89 -- **net-negative**

**Portfolio Health**

- Capital cost ratio: 47.0% of gross
- Treasury drawdown events (>=10% threshold): none
- Bills issued: 78, average clarity 0.826, average bill shock 25.7%, bad debt provision £177.37, avg complaint probability 5.8%
- Regulatory threshold breaches: Not available in current run output (see REPORTING_BACKLOG.md)

**Hedge Effectiveness**

- Actual (hedged) net margin: £95.66 vs. naked (unhedged) net margin: £-146.95
- hedging added £242.62 vs. a fully unhedged book (actual net £95.66 vs. naked net £-146.95)
  - C2: actual £48.87 vs. naked £229.17 -- hedging cost £180.30
  - C2g: actual £10.27 vs. naked £-0.48 -- hedging added £10.76
  - C6: actual £14.47 vs. naked £-436.24 -- hedging added £450.71
  - C8: actual £22.05 vs. naked £60.60 -- hedging cost £38.55

**Year narrative:** 2025 produced a net gain of £366.40 across 13 accounts. The risk committee did not intervene -- VaR stayed within the stressed floor. 32 customer(s) experienced a bill shock of >=20%.
