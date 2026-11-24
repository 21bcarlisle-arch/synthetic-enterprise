**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Result: the pre-crisis France-shortfall runs priced against SAP in two of three runs, and the month's own net export carries 39% of the chain's miss (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
Pre-registered in `docs/staging/records/WORKER_PREREG_DID_THE_PRE_CRISIS_FRANCE_SHORTFALL_RUNS_MOVE_GB_POWER_AGAINST_SAP_2026-11-24.md`
(`b981dbbcf`), pushed to origin before the probe ran. Probe `/var/tmp/wpc_13c/measure_13c.py`, sha256
`4dfd66d6…d1735`, unchanged. Raw output: `/var/tmp/wpc_13c/out.json`. **Nothing in `sim/` changed.***

## Outcomes beside the predictions

| # | Prediction | Outcome | |
|---|---|---|---|
| P1 | C3 reproduces 4.22 / 16.81 / 6.18 | 4.22 / 16.81 / 6.18 | held |
| P2 | C3 mean bias over S ≤ −£3 | −4.29 | held |
| P3 | C3 gap over S ≤ −£3 | −5.24 (S −4.29 against a control of +0.95, 19 months) | held |
| P4 | Record SSP/floor over S ≥ control + 0.05 | 1.365 against 1.111 (+0.254) | held |
| P5 | Run 1 has the most negative gap | run 1 −8.52, run 3 −4.19, run 2 +4.33 | held |
| P6 | C3m closes at least half of C3's gap | −5.24 → −3.20 (39%) | **missed** |
| P7 | C3m pre MAE ≤ 4.22 | 4.40 | **missed** |

Five of seven held. **Rule (c) fires.** The runs moved price, and the net-flow month mean does not carry it.

## By run

| Run | Months | Record SSP/floor (control) | C3 bias (gap) | C3m bias (gap) | GB net export, month mean |
|---|---|---|---|---|---|
| 1 | Oct 2016-Jan 2017 | 1.477 (1.112) | −6.79 (−8.52) | −4.15 (−6.68) | −634, −916, −586, −195 MW |
| 2 | Nov 2017 | 1.092 (1.054) | +7.57 (+4.33) | +11.73 (+8.01) | +81 MW |
| 3 | Jul 2020 | 1.191 (1.107) | −6.17 (−4.19) | −5.15 (−2.94) | −387 MW |

C3's months in run 1: Oct −8.22, **Nov −22.72**, Dec +0.91, Jan +2.87. Without Nov 2016, the run's gap is
about −£3.2. One month carries most of the run.

## What it says

- **GAP 13c, partly closed: yes, at the month, in two of three runs.** Before the crisis, a France shortfall
  raised GB power above the gas-plus-carbon floor beyond what the same calendar month shows in other years. That
  held in autumn 2016 (+0.37 on the ratio) and in Jul 2020 (+0.08). Nov 2017 is a shortfall by §5b's definition,
  with GB a net exporter overall that month, and it did not price (+0.04). The chain over-prices it instead.
- **The net-flow term is not the whole mechanism.** On the record, each month's own net export takes out 39% of
  the S gap. It costs pre-crisis accuracy overall (4.22 → 4.40) and post-crisis accuracy (6.18 → 6.73). It helps
  the crisis (16.81 → 13.64), which repeats the timescale arm. The rest of autumn 2016's markup is not attributed.
  GB's own capacity margin in Nov 2016 is one candidate. A scarcity term the leg does not see is another. Neither
  is checked.
- **For the forward years** (director row `the-forward-world-has-bands-for-gas`, and §5b option 1): the record
  shows a neighbour shortfall moving GB's price in three runs (2016, 2020, 2022), not only 2022. Before the
  crisis the size is about £5/MWh across the run months, against the chain's form. That is a monthly fact. A
  drawn event that only moves net flow would carry less than half of it, on this measure.

## Correction beside the prediction

P6 assumed a pre-crisis shortfall worked the way 2022 did, as an export load on GB plant. In autumn 2016 GB's
total net flow stayed an import of 0.2-0.9 GW, so the swing was smaller than the price move. The prediction was
wrong in that, and it stays beside the outcome.
