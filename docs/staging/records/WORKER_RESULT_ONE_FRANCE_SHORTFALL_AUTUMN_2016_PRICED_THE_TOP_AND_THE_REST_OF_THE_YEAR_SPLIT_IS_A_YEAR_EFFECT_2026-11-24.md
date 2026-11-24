**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Result: one France shortfall, autumn 2016, priced the top, and the rest of the year split is a year effect (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
Pre-registered in
`docs/staging/records/WORKER_PREREG_DOES_A_FRANCE_SHORTFALL_MONTH_PRICE_THE_TOP_ABOVE_THE_PRE_CRISIS_FIT_ON_SAP_2026-11-24.md`
(`a1b069a39`), which was landed and pushed to origin before the probe ran. The probe ran unamended (sha256
`4c2491fa…`) in a worktree at `a1b069a39`, with `sim/cache` linked from the main tree. Output is
`/var/tmp/nsf_top/out.json`. **Nothing in `sim/` changes.***

## Outcomes (days at 14 GW of CCGT or more; residual = record ÷ floor minus S1 ÷ floor)

| Arm | Shortfall | Comparison | Gap |
|---|---|---|---|
| N1, all years | +0.024 (277 days) | −0.006 (868) | +0.03 |
| N1, without 2022 | +0.028 (167) | −0.011 (826) | +0.04 |
| N2, 2016 | +0.337 (80) | +0.095 (110) | +0.24 |
| N2, 2017 | −0.074 (51) | +0.045 (110) | −0.12 |
| N2, 2020 | +0.114 (8) | +0.081 (77) | +0.03 |
| N2, 2021 | −0.074 (28) | +0.183 (91) | −0.26 |
| N2, 2022 | +0.022 (110) | +0.017 (42) | +0.01 |
| N4 | non-shortfall months of 2016/17/20/21: +0.116 (388) | years with none: −0.090 (438) | **+0.21** |

N3, each shortfall month against the same calendar month in the years without a shortfall that month (every
month had five or more top days on each side):

| Month | Difference | Month | Difference |
|---|---|---|---|
| 2016-10 | +0.37 | 2022-04 | −0.09 |
| **2016-11** | **+0.94** | 2022-05 | −0.07 |
| 2016-12 | −0.07 | 2022-06 | +0.12 |
| 2017-01 | +0.02 | 2022-07 | +0.11 |
| 2017-11 | −0.03 | 2022-08 | −0.05 |
| 2020-07 | +0.08 | 2022-09 | −0.39 |
| 2021-11 | +0.19 | 2022-10 | +0.25 |
| 2021-12 | −0.16 | 2022-11 | +0.09 |

Without 2022, the mean is **+0.167** over eight months. The median is +0.05. Without Oct-Nov 2016, the other six
average **+0.005** [calc, from the table].

| # | Prediction | Outcome |
|---|---|---|
| H-N0 | N0 reproduces §5b's 16 months | **Held**, exactly |
| H-N1 | Without 2022, the shortfall-month residual is 0.08 or more above the rest | **Refuted.** +0.04 |
| H-N2 | In each of 2016, 2017, 2020 and 2021, shortfall months are 0.05 or more above the same year's other months | **Refuted.** It holds in 2016 only. 2020 is +0.03, and 2017 and 2021 are below |
| H-N3 | The calendar-matched mean without 2022 is +0.08 or more | **Held as written, +0.167, but on one event.** Two months of autumn 2016 carry it, and the other six average +0.005 |
| H-N4 | The non-shortfall months of the shortfall years sit 0.05 or more above the years with none, mainly from 2016 | **Held on size, +0.21. Wrong on where it comes from.** 2021's other months (+0.18, which include the crisis onset from July) sit above 2016's (+0.10) |

Three of five held, and one of those three holds on a single event.

## What the rule says

- **Rule (a) does not fire.** H-N1 is refuted and N4's gap is 0.21, not below 0.05.
- **Rule (b) does not fire.** N3's mean is +0.167, not below +0.04.
- **Rule (c), mixed, applies.** The build is the same as (b). S1's top stays, and the by-year spread (−0.14 to
  +0.20 of the floor on 14 GW+ days) is stated beside every forward figure. No shortfall term is built.

## What it says, plainly

- **The clean ten-year split seen after the top arm was mostly a year effect.** A shortfall year's own other
  months sit 0.21 above the years with none, and inside those years shortfall months are not reliably higher
  than the rest (1 of 4).
- **One event did price the top: autumn 2016**, the Le Creusot checks that §5b dates. November 2016 priced
  +0.94 of the floor above the other Novembers, and October +0.37. The other seven pre-crisis shortfall months
  average about zero. So a neighbour shortfall *can* move the top a long way, but the record's other runs did
  not, and one event cannot set a size. In 2022 the comparison is inside the crisis, and four of its eight months are
  positive and four negative.
- **For the forward event in §5b (option 1):** the record supports a shortfall that sometimes prices and usually
  does not. A drawn event would need its price size drawn too, from a sample of one that priced. That belongs
  beside the bands row `the-forward-world-has-bands-for-gas` as context, not as a sourced band.
- **What it does not explain:** why the top moves by year at all (2016 +0.20, 2018-19 −0.10, 2021 +0.07 outside
  its shortfall months). Its candidates are not on this record's observables (scarcity pricing and the Capacity
  Market margin, in the electricity page's §7). I cannot yet say which, and it is not tested here.

## Next, still item 4

The price leg's diagnostic arms on the top end here. No arm on this record separates the year effect, and rule
(c) builds nothing. Item 4 now waits only on the shippable record-years build, which the SAP splice finding
carries, with S1's top and its stated by-year spread.

Reverse: delete this record.
