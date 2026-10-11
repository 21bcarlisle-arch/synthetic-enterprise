**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history`

# Pre-registration: B11 slice 8, tenure given calendar year on the book's later cohorts

Written 2026-10-11, before any exit had been counted by calendar year and contract year together.
Claim `b11-tenure-vs-calendar-on-a-second-founding-year`. It lands with the code that measures it
(`exit_cells`, `standardised_ratios`, `pooled_ratio` in `company/analytics/forward_clv.py`), and
that commit precedes the measurement. Results go in a separate finding. This file is not edited
after the run.

## The premise, re-measured: no second founding year exists, and none is needed for young tenure

The item asked for a run whose book opens after 2016. A census of every run output on this
machine (4,950 distinct files under `/var/tmp` and `/home/rich`, deduplicated by content) found
**none**. Every one opens in 2016. So a second founding year would need a new run, and choosing the
year the company is founded in is a curriculum choice, which is the director's.

But the slice-5 book (`/var/tmp/b11s5_run/run_output_b11s5.json`, 773 billing accounts) is not one
cohort. Accounts by the year they opened: 2016 432, 2017 43, 2018 48, 2019 46, 2020 43, 2021 43,
2022 27, 2023 25, 2024 45, 2025 21. That is 341 accounts in nine later cohorts. Each of contract
years 0 to about 4 is therefore seen in several calendar years. Slice 7's collinearity holds for
the 2016 cohort and for the oldest contract years, which only that cohort reaches. It does not hold
for the young years.

These counts are the only thing read from the book before this file. Exits were not counted.

## The measurement

"Later cohorts" means accounts whose first supplied month is in 2017 or later. "2016 cohort"
means the rest. Both are taken whole to the book's end at 2025-06. This is not a backtest, and no
cut is involved.

- **M1. Tenure given calendar year, later cohorts.** `exit_cells` over the later cohorts, and
  `standardised_ratios(c, c, rate_by="calendar_year", report_by="contract_year")`.
- **M2. The mirror: calendar year given tenure, later cohorts.** `rate_by="contract_year",
  report_by="calendar_year"`.
- **M3. The 2016 cohort against the later cohorts' calendar-year rates**, reported by calendar year
  and pooled. The subject is the 2016 cohort's cells, the reference is the later cohorts' cells,
  and `rate_by = report_by = "calendar_year"`.
- M1 to M3 are run all-cause. M1 is run again switch-only, with each account in
  `move_outs_from_run_output` censored.

Only contract years with at least 6 expected exits are graded in M1. The rest are reported and
not graded, because a ratio on fewer exits has no usable interval.

## Predictions

- **P1. Tenure carries nothing once the year is held.** In M1 all-cause, every graded contract
  year's 95% interval holds 1. *Refuted* if any graded contract year excludes 1. *Prior:* slice 7
  found the switch level is the regime. I know of no fixed-term-end mechanism that the world
  applies to an acquired account's tenure. I hold this at about 60%, and contract year 0 is the
  likeliest place for it to break.
- **P2. Calendar year carries a lot once tenure is held.** In M2, at least one year from 2017 to
  2020 has an interval wholly above 1, and at least one year from 2021 to 2023 has one wholly below 1.
- **P3. The 2016 cohort leaves less often than the later cohorts did in the same years.** M3's
  pooled ratio is between 0.5 and 0.95, and its interval excludes 1. The reasoning is selection:
  the survivors of a heterogeneous cohort are its stayers. Long tenure and the founder cohort
  cannot be separated in this measurement. A ratio below 1 is either one, and this file does not
  claim to know which.
- **P4. Switch-only M1 reads as all-cause M1 does**, on the same graded years.

## What each result means for the per-customer rule

- **P1 holds.** On the years this book can separate, the contract-year table knows nothing that
  calendar time does not. The per-customer departure level is recency for every cohort, not only
  the founders. The L3 claim that a tenure table knows something stays unearned (EP17 blocks it
  anyway), and the honest per-customer departure covariate would be the regime, not tenure.
  A second founding year would only add the oldest contract years, which only one cohort reaches.
- **P1 refuted.** The tenure table carries information beyond calendar time on young years. The
  next slice should fit the contract-year table standardised for calendar year, rather than raw,
  so that recency stops leaking into it.
- **P3 holds.** The founders' low late-year hazard is not only recency. It is long tenure or the
  founder cohort, and only a second founding year can split those two. That is the case for
  proposing such a run to the director.
- **P3 refuted (ratio about 1).** The founders leave like everyone else in the same year. Slice 7's
  "recency, not tenure" reading then covers the founders too, and nothing is left for a second
  founding year to separate.
