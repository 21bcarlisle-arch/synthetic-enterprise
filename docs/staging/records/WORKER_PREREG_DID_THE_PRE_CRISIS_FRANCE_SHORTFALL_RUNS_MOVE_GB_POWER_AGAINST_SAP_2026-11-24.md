**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Pre-registration: did the pre-crisis France-shortfall runs move GB power against SAP, and does the month's own net export carry it? (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
This is Next (1) of the neighbour-shortfall K8 note (`c3b385236`), and it measures the electricity page's
§5b GAP 13c. Filed and landed before the probe runs. **Nothing in `sim/` changes.***

## The question

§5b counts five runs of months in which GB's net flow with France was at or below zero. Three are pre-crisis:
Oct 2016-Jan 2017 (4 months), Nov 2017 and Jul 2020. On the record, 2022's run carried the price leg's crisis
markup on SAP. **Did the three smaller pre-crisis runs also lift GB's power price above what gas and carbon
explain? Does the chain's shippable form (C3), which carries only each year's net-export level, run low in
those months? And does each month's own net export take that out?**

If the answer is yes, a neighbour shortfall prices on the record five times, not once. That bears on §5b's
option 1 (a drawn forward event) in the director row `the-forward-world-has-bands-for-gas`.

## Definitions, stated before measuring

- **Shortfall months (S):** 2016-10, 2016-11, 2016-12, 2017-01, 2017-11 and 2020-07, taken from §5b's table
  as published. Nov-Dec 2021 is in the crisis regime and is excluded.
- **Bias:** chain minus record, demand-weighted by month, £/MWh. A negative value means the chain is low.
- **Control (same calendar month):** the mean bias over pre-crisis months (to 2021-06) with the same calendar
  month that are not in S. The **gap** is bias(S) minus control. It removes any seasonal miss the chain has in
  every year.
- **Record-only ratio:** the monthly mean SSP over the monthly mean floor, where floor is (SAP + carbon × EF) /
  efficiency, on the half-hourly fit rows. It is compared with the same calendar-month control. This needs no
  chain.
- **Arms:** **C3** is the control: SAP, net export at the year mean, demand by year, solar out (`df7cd4297`).
  **C3m** changes one thing. Net export is each month's own real mean, on both the leg refit and the chain
  side.

Probe: `/var/tmp/wpc_13c/measure_13c.py`, sha256 `4dfd66d6…d1735`, derived from `/var/tmp/wpc_c/measure_c.py`.

## Seen before the run (disclosed)

- §5b's France monthly table.
- C3's bias by year from `d2a4630783`: 2016 −3.38, 2017 +1.85, 2018 +3.73, 2019 +0.79, 2020 −2.47. The net-export
  year means: 2016 −1.91 GW, 2017 −1.78 GW, 2020 −2.08 GW.
- No monthly residual and no monthly total net export has been computed.

## Predictions

| # | Prediction |
|---|---|
| P1 | Control: C3 reproduces 4.22 / 16.81 / 6.18 (pre / crisis / post monthly MAE) within £0.01. |
| P2 | C3's mean bias over the six S months is at most −£3. |
| P3 | C3's gap over the six S months (against the same-calendar control) is at most −£3. |
| P4 | The record's SSP/floor ratio over S exceeds its same-calendar control by at least 0.05. |
| P5 | Run 1 (Oct 2016-Jan 2017) has the most negative gap of the three runs. |
| P6 | C3m closes at least half of C3's S gap: \|gap(C3m)\| ≤ 0.5 × \|gap(C3)\|. |
| P7 | C3m's pre-crisis monthly MAE is no worse than C3's 4.22. |

## Decision rule, filed before the run

- **(a) P3 and P6 both hold.** The pre-crisis runs priced against SAP through the net-flow term. GAP 13c closes
  "yes". The record shows a neighbour shortfall moving price in more than one run, and the director row gains
  that fact beside option 1.
- **(b) P3 fails (gap above −£1.5).** At the month, the pre-crisis runs did not move price beyond SAP. GAP 13c
  closes "not at the month". The priced event is 2022's alone, and option 3 (state it beside the figure)
  carries the record.
- **(c) Otherwise** (P3 holds and P6 fails, or the gap lies between −£3 and −£1.5). The run moved price, but the
  net-flow month mean does not carry it, or the effect is marginal. GAP 13c stays open with the measured size
  stated, and it is not attributed.
