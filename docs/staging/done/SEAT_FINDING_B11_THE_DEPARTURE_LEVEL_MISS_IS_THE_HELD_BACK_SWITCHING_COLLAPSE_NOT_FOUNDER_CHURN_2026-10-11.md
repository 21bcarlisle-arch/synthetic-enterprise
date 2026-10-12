**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history`

# B11 slice 6 result: the departure-level miss comes from switching collapsing in the held-back years, not from founder churn in the fit years

**Fate (2026-10-12, clear-the-decks):** DONE -- 11844e412. B11 slice 6 result graded: level miss attributed to held-back switching collapse

Claim `b11-departure-level-calibration`. The predictions were written before the measurement and
landed with the code that makes it, in `4212a9a56`:
`docs/staging/records/SEAT_PREREG_B11_SIXTH_SLICE_WHY_BOTH_RULES_OVER_PREDICT_HELD_BACK_DEPARTURE_2026-10-11.md`.
This file grades them and leaves them as written.

## The run

This uses the same book as slice 5: `/var/tmp/b11s5_run/run_output_b11s5.json`, run at `3f1ebfac3`
with home moves on. The cut is 2020 and 247 accounts are graded. Each figure below comes from
`backtest_run_output(path, 2020, None, gas, hazard_fit_from_year=…)` at `4212a9a56`.

## C1: the implementation check

- **Calibration reproduces exactly.** The mean departure p minus the realised rate is
  **+0.361 (+0.299, +0.423)** for the per-customer rule and **+0.241 (+0.180, +0.303)** for the
  flat rule. The realised rate is 0.429.
- **The whole-book AUCs reproduce:** 0.515 and 0.524.
- **The per-outcome AUCs do not match slice 5's figures.**

  | outcome | rule | slice 5 said | this code | sklearn |
  |---|---|---|---|---|
  | switcher | per-customer | 0.583 | 0.575 | 0.575 |
  | switcher | flat | 0.588 | 0.583 | 0.583 |
  | mover | per-customer | 0.432 | 0.433 | 0.433 |
  | mover | flat | 0.447 | 0.444 | 0.444 |

  `sklearn.metrics.roc_auc_score` agrees with the module to four places on the same forecasts, so
  slice 5's hand-computed figures are wrong in the third place. That finding is corrected beside
  the claim. The DeLong standard error was also checked against 1,000 bootstrap resamples: 0.0361
  against 0.0354 for the AUC, and 0.0220 against 0.0226 for the paired difference.

## The book's departure record by calendar year

Every account on supply is counted here, not only the graded accounts. The rates are per account
per month.

| year | months at risk | departures | rate | switch rate | move rate |
|---|---|---|---|---|---|
| 2016 | 2,668 | 27 | 0.0101 | 0.0037 | 0.0064 |
| 2017 | 4,665 | 98 | 0.0210 | 0.0167 | 0.0043 |
| 2018 | 4,093 | 90 | 0.0220 | 0.0166 | 0.0054 |
| 2019 | 3,491 | 91 | 0.0261 | 0.0186 | 0.0074 |
| 2020 | 3,139 | 64 | 0.0204 | 0.0153 | 0.0051 |
| 2021 | 2,958 | 43 | 0.0145 | 0.0081 | 0.0064 |
| 2022 | 2,975 | 18 | **0.0061** | **0.0013** | 0.0047 |
| 2023 | 3,071 | 19 | 0.0062 | 0.0039 | 0.0023 |
| 2024 | 3,184 | 35 | 0.0110 | 0.0060 | 0.0050 |
| 2025 (to June) | 1,627 | 18 | 0.0111 | 0.0080 | 0.0031 |

## The predictions, graded

- **P1 (H1 refuted): HELD.** The 2016–2017 departure rate is 0.0171 and the 2019–2020 rate is
  0.0234, a ratio of 0.73. The early fit years churned *less* than the late ones. **H1 is
  refuted: founder churn does not cause the over-prediction.**
- **P2 (a recency window does not fix it): HELD, narrowly.** With the hazard fitted on 2020 alone,
  the flat rule's calibration is **+0.199 (+0.136, +0.262)**, which only just clears the +0.19 bar.
  Fitted from 2019 it is +0.278, and from 2018 it is +0.278. Moving the window later makes the miss
  larger, except at the one-year window.
- **P3 (H2, the held-back world moved): HELD.** The 2021–2022 rate is 0.0103, or 0.50 × the 2020
  rate. In 2022 alone it is 0.30 ×.
- **P4 (the fall is in switches): HELD.** The held-back switch rate is 0.0052, which is 0.35 × the
  fit window's 0.0149. The held-back move rate is 0.0044, which is 0.79 × the fit window's 0.0056.
  In 2022 there were 4 switches in 2,975 account-months.
- **P5 (no ranking difference): HELD.** The paired AUC difference, per-customer minus flat, is:
  - whole book: −0.009 (−0.053, +0.034)
  - switchers: −0.008 (−0.057, +0.041)
  - movers: −0.011 (−0.074, +0.051)

  All three verdicts are "cannot tell". The same holds under every hazard window tried.

**H3, a calendar confound in the tenure table: not supported as stated, and it cannot be
separated on one book.**
*Corrected by slice 7, `SEAT_FINDING_B11_THE_MOVE_TERM_TRANSFERS_AND_THE_SWITCH_TERM_IS_THE_REGIME_2026-10-11.md`:
at cuts 2020, 2022 and 2023 the oldest contract year is fitted on the cut year alone, so for the
founders the per-customer level IS that calendar year's rate. H3 holds in that form.*
- 2019 is the highest year in the fit window. 2020 is not.
- In 2020, contract year 4 (the 2016 founders) left at 0.0293, against 0.0204 for the whole book
  in the same year. So at least part of the tenure gradient is not calendar time.
- On one book, cohort, tenure and calendar year are collinear. Contract year 0's 0.0101 is the 2016
  founders' first year, so it cannot be told apart from 2016 itself.

## What this means

1. **The 0.24–0.36 level miss belongs to the held-back world's regime, not to the fit.** In the
   world, switching collapsed across 2021–2023 and reached nearly nothing in 2022. That matches
   the GB record after fixed offers were withdrawn in autumn 2021. Moves held at about 0.8 × their
   earlier rate.
2. **A supplier fitting at December 2020 could not have seen the collapse.** It began nine months
   after the cut. Calibrating the level to the held-back rate would be fitting to the answer, and
   no fit window inside 2016–2020 brings the miss inside its interval.
3. **The prediction I would make for a later cut is arithmetic, and is stated here so it can
   refute me.** At a 2022 cut the fit window is 2016–2022, with a pooled monthly rate of about
   0.018. The held-back window is 2023 to 2025-06, at about 0.009. Over 30 months that puts flat p
   at about 0.42 against about 0.24 realised. *(Graded in slice 7: 0.418 against 0.249, +0.169.)* **So a later cut is predicted to still over-predict,
   by roughly 0.15–0.2.** A later cut does not answer the level question either. The level depends
   on the regime.
4. **The miss is in the switch hazard. The move hazard transferred.** A forecast that separates
   the two causes would carry the regime risk on the switch term alone. The move term is the part
   of departure that held across the crisis.
5. **On this book neither rule ranks anybody.** The whole-book AUC is about 0.52, with an interval
   of ±0.07 that includes 0.5. The per-customer rule's tenure table adds level and no ranking, and
   EP17 still blocks the L3 claim.

## Disposition

- `departure_calibration` and `departure_ranking` now carry the grade. The per-outcome Brier is
  gone, replaced by AUC against stayers. `hazard_fit_from_year` stays as a reading aid; the default
  is unchanged.
- **Next slice, company code, needs no director.** Run the cut-2022 and cut-2023 backtests against
  point 3's arithmetic prediction. Then decide whether the departure level should be published with
  an explicit regime caveat and a switch/move-separated survival, instead of a calibrated constant.
  Handed on as a continuation.
