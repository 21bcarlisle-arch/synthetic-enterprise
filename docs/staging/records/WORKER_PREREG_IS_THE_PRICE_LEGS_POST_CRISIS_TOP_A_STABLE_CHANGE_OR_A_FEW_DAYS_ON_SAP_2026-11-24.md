**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Pre-registration: is the price leg's post-crisis top a stable change, or a few days? On SAP (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
This is next step 1 named by the low-gas hinge result: "the 14 GW+ post-crisis top (1.27 against 1.17, 107
days), with its prediction filed first". It is filed and landed before the probe runs. The probe is
`/var/tmp/top_sap/probe.py`, sha256 `3cd56b578cf25ec5…`. It is the shape arm's probe
(`/var/tmp/shape_sap/probe.py`, sha256 `053d6857…`) up to its BINS line, unchanged, with the top arms added
after it. **Nothing in `sim/` changes.***

## What is known before the run, and what was seen

- **Leg P with the hinge (S1)**: price = floor × (b0 + b1·c + b2·max(0, c − 14) + b3·max(0, 6 − c)), fitted
  on pre-crisis days only. On real c its post-crisis MAE / bias is 4.89 / +2.44. On the 107 post-crisis days
  above 14 GW it prices at 1.267 of the floor, where the record clears at 1.174.
- **Seen before this was written:** the electricity page's §1b table (post-crisis there means 2023 H2 to
  2025 H1). Post-crisis the record reads 1.01 at 10-12 GW, 1.07 at 12-14, 1.06 at 14-16 (46 days), 1.09 at
  16-18 (20) and 1.38 at 18-20 (22). Before the crisis it reads 1.05, 1.10, 1.14, 1.28 and 1.35. The gap
  opens at 12 GW, is widest at 16-18, and is gone by 18-20. A straight post-crisis slope above 12 GW cannot
  fit both the dip and the 18-20 return. The knot at 12 GW comes from this table.
- **Size, before the run [calc]:** 107 of about 915 post-crisis days, about 0.09 of a floor of about £90 on
  those days. That is about £8 a day on them, or roughly £1.0-1.4 of monthly bias, since those days are
  winter-weighted. The top cannot carry all of the +2.44.
- **Not seen:** any fit with a post-crisis top term, any by-year split of the top, or any score.

## Arms (scored on real c, post-crisis unless stated)

| Arm | Design | Fitted on |
|---|---|---|
| T0 (control) | S1 | pre-crisis days only |
| **T1** | S1 + post × max(0, c − 12) | pre-crisis days and post-crisis days except the scored year (2023 H2, 2024, 2025 each held out in turn) |
| T2 (oracle) | the same as T1 | pre-crisis and every post-crisis day, in sample |

There is also a by-year diagnostic: for each year 2016-2025, the days at 14 GW or more, the record's ratio to
the floor, and T0's.

## Predictions

| # | Prediction |
|---|---|
| H-T0 | T0 reproduces S1's leg-P-on-real rows to every printed figure (post 4.89 / +2.44) |
| H-T1 | In each of 2023, 2024 and 2025 with ten or more top days, the record's top ratio is below T0's by 0.03 or more |
| H-T2 | In each pre-crisis year with ten or more top days, the record's top ratio is within ±0.06 of T0's |
| H-T3 | T1's post-top coefficient is negative for every held-out year, in [−0.04, −0.005] per GW |
| H-T4 | T1 post bias in [+1.2, +2.2] (from +2.44); post MAE in [4.2, 4.9] |
| H-T5 | T2 post bias in [+0.9, +1.9]; T2 sits below T1 |
| H-T6 | T1 and T2 leave pre and crisis rows within ±0.10 of T0's (the term is zero there; only refitting moves them) |

## Decision rule

- **(a)** If H-T1 holds for at least two post-crisis years, T1's coefficient is negative for every held-out
  year, and T1 moves post bias by £0.8 or more: the post-crisis top is a stable change, not a few days. It is a
  date term, though, and a forward year cannot carry a date term without a mechanism. The next step is K8 on
  what flattened the top after 2023 (battery fleet growth, Capacity Market margin, lower demand at a given gas
  output), before anything is built.
- **(b)** Otherwise, the top is not a stable change on this record. The build keeps S1's pre-crisis top and
  states the post-crisis top residual beside every forward figure. The price leg's diagnostic arms end here,
  and item 4 waits only on the shippable record-years build, which the SAP splice finding carries.

Reverse: delete this record.
