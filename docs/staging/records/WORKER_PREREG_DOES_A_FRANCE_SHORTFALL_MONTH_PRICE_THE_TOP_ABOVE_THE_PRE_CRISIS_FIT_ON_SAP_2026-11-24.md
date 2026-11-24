**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Pre-registration: does a France-shortfall month price the top above the pre-crisis fit? On SAP (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
This is next step 1 named by the top arm's result
(`WORKER_RESULT_THE_PRICE_LEGS_TOP_MOVES_BY_YEAR_BEFORE_THE_CRISIS_TOO_SO_THE_POST_CRISIS_TOP_IS_NOT_YET_A_REGIME_2026-11-24.md`,
`0a1adccc1`). It is filed and landed before the probe runs. The probe is `/var/tmp/nsf_top/probe.py`, sha256
`4c2491faab843748…`. It is the top arm's probe (`/var/tmp/top_sap/probe.py`) up to its TOP ARM line, unchanged,
with the arms below added after it. **Nothing in `sim/` changes.***

## What it is, before it is counted

- **A France-shortfall month** is the electricity page's §5b definition and nothing else: the calendar-month
  mean of GB's net flow with France (FUELHH INTFR + INTIFA2 + INTELEC, last publish per half hour and cable,
  + is import) at or below zero. §5b counts 16 of 120 months.
- **The top** is days with daily mean CCGT output of 14 GW or more. Its **residual** is the record's mean price
  over the mean floor, minus S1's (leg P with the low-gas hinge, fitted on pre-crisis days only) over the same
  floor, on the same days.

## What is known before the run, and what was seen

- **Seen, after the top arm ran, and the reason this arm exists:** by calendar year, every year with a §5b
  shortfall month has a top ratio of 1.24 or more (2016 1.43, 2017 1.24, 2020 1.31, 2021 1.29, 2022 1.26), and
  every year without one 1.23 or less (2018 1.12, 2019 1.15, 2023 1.18, 2024 1.14, 2025 1.23). The split was
  found by looking. It is the hypothesis under test, not evidence for it.
- **Seen in §5b:** the shortfall months are Oct 2016-Jan 2017, Nov 2017, Jul 2020, Nov-Dec 2021 and Apr-Nov
  2022. Four of five runs start in October or November, so a shortfall month is also usually a winter month,
  when the top has the most days. Season is the confounder the calendar-matched arm exists for.
- **Not seen:** any top residual by month, any within-year split, or any calendar-matched comparison.

## Arms (all on real CCGT output, top days only)

| Arm | What it compares |
|---|---|
| N0 (control) | The probe's shortfall-month set against §5b's 16 months |
| N1 | Pooled residual, shortfall months against all other months; with 2022 and without it |
| N2 | Within each shortfall year (2016, 2017, 2020, 2021, 2022): shortfall months against that year's other months |
| N3 | Each shortfall month against the same calendar month in the years without a shortfall that month (needs five top days each side) |
| N4 | The non-shortfall months of 2016, 2017, 2020 and 2021, against the years with no shortfall (2018, 2019, 2023-25) |

N4 is the discriminating arm. If the shortfall carries the top, a shortfall year's other months should look like
a year without one. If they do not, the split is a year effect that the shortfall happens to coincide with.

## Predictions

| # | Prediction |
|---|---|
| H-N0 | N0 reproduces §5b's 16 months exactly |
| H-N1 | Without 2022, the pooled shortfall-month residual is 0.08 or more above the non-shortfall months' |
| H-N2 | In each of 2016, 2017, 2020 and 2021 that has five or more top days in shortfall months, those months' residual is 0.05 or more above the same year's other months |
| H-N3 | The calendar-matched mean difference, without 2022, is +0.08 or more |
| H-N4 | The non-shortfall months of the four pre-crisis shortfall years sit 0.05 or more above the years with none (a year effect beyond the shortfall is predicted, mainly from 2016's January to September) |

## Decision rule

- **(a) The shortfall carries the top.** H-N1 and H-N3 hold, and N4's gap is below 0.05. The top's by-year
  spread is then mostly the neighbour event. A forward top term belongs to the drawn event (§5b option 1), not
  to the price leg. It goes beside the bands row `the-forward-world-has-bands-for-gas` in `for_the_director`,
  after a K8 section on French nuclear availability, and nothing is built first.
- **(b) A year effect, not the shortfall.** N4's gap is 0.05 or more and N3's mean difference is below +0.04.
  The split was a coincidence of year levels. The price leg's diagnostic arms on the top end here. The build keeps
  S1's top, with the by-year spread (−0.14 to +0.20) stated beside every forward figure.
- **(c) Anything else is mixed.** The build is the same as (b), because erring against the thesis is the safe
  direction (F11). The shortfall is recorded as a partial candidate, with its calendar-matched size.

In every case, item 4's record-years build waits only on the SAP splice finding.

Reverse: delete this record.
