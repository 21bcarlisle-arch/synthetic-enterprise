**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 4 · **Atom:** `C_supply_start_consumer_routing`

# 2022 is a hollow year in the published run, and that hollow is what turns the crisis xfail into a pass

**Fate (2026-10-15):** ATOM -- folds into `C_supply_start_consumer_routing` (re-pointed 2026-10-15; an ATOM fate names its atom).
**Fate (2026-10-12, clear-the-decks):** ATOM -- find where years[y].bad_debt_gbp mis-keys the year (2022 write-offs booked to 2021), which makes the crisis-step-up xfail spuriously XPASS (P2)

Found while working the head-red register (2026-10-10). Re-run at `origin/main` 6a7a35721 in a
clean worktree, 6 of the register's 48 rows are still red. Two of them point at the same year.

## The two reds

1. `tests/company/compliance/test_crisis_bad_debt_validator.py::test_live_run_output_shows_crisis_step_up_headline`
   is `xfail(strict=True)` with the reason "no real 2021-22 crisis step-up until the affordability
   cluster is built". It now **XPASSES**: step-up x10.49 (crisis 4.997% against pre-crisis 0.477%).
2. `tests/saas/reporting/test_a_churned_account_has_a_departure_record.py::test_every_year_the_published_run_reports_appears_in_its_lifecycle_record`:
   "the run reports 10 years and its lifecycle record covers 9: ['2022']".

Both read the committed `docs/reports/run_output_latest.json` (a88fb2436, run git=998814330,
2026-10-05).

## What the year looks like

| year | active accounts | bills | revenue GBP | bad debt GBP | renewed | churned |
|---|---:|---:|---:|---:|---:|---:|
| 2020 | | | 39,921 | 501.2 | 20 | 2 |
| 2021 | 82 | 885 | 47,248 | **6,601.8 (13.97%)** | 13 | 3 |
| 2022 | 73 | 874 | 84,860 | **-6.4e-14** | **0** | **0** |
| 2023 | 75 | 893 | 117,559 | 189.4 | 6 | 0 |

The step-up "passes" because the 2021-22 rate is (6,601.8 + 0) / (47,248 + 84,860). That rests on
one year at 14%, and 2021's write-offs land before the cap rise of April 2022 that drove real
domestic debt. 2022 shows no bad debt and no lifecycle event at all, across 73 accounts and 874
bills. The bad debt is a float residue, not a zero: something was written off in 2022 and exactly
reversed.

**This XPASS must not be read as the affordability cluster's result**, and the strict marker should
not be removed on its strength. Its reason text names exactly this shape ("do NOT satisfy this by
tuning a bad-debt parameter").

## End-to-end check: explanations the evidence allows, ranked

1. **The run lost 2022's lifecycle and arrears flow.** One defect would explain both reds: the
   empty event list, and a write-off netted exactly to zero. Evidence for: two independent
   artefacts show the same hollow year. Evidence against: none yet.
2. **The world is right and 2022 really had no decisions.** Real switching collapsed in 2022 and
   fixed deals were withdrawn, so a book of SVT rollers could show no "renewed" event. That cannot
   explain zero bad debt in the year domestic arrears rose most, so it can account for the
   lifecycle red only.
3. **2021's 14% is itself a timing artefact.** A write-off dated at the arrears case's open, not at
   its close, would pull 2022's debt into 2021. Testable by dating the 2021 write-off cases.

**I cannot yet say** which holds. The one-variable test is to read the 2021 write-off cases'
`opened_date` and `WRITTEN_OFF` dates and the 2022 renewal or SVT-roll records in the run's own
logs. Prediction, written before looking: (3) explains most of the 2021 spike, and (1) explains
the 2022 zero.

## Result, same day: the prediction is refuted, and the reading is sharper

The `WRITTEN_OFF` stages in `docs/state/billing_ledger.json`, which was built from the same run
(998814330), dated by their own stage date:

| year | write-off cases | GBP | run's `years[y].bad_debt_gbp` |
|---|---:|---:|---:|
| 2020 | 14 | 671.8 | 501.2 |
| 2021 | 11 | 646.5 | **6,601.8** |
| 2022 | 16 | **6,906.2** | **-6.4e-14** |
| 2023 | 4 | 228.2 | 189.4 |

The ledger puts the crisis debt in **2022**, and the run's yearly series puts nearly the same sum
in **2021** and nothing in 2022. Explanation (3) as written is wrong: 2021's write-offs are not
dated at case open, since the ledger's own 2021 cases are small and dated in 2021. What fits is
**a year misattribution between the ledger and the yearly P&L**: about GBP 6.6-6.9k of 2022
write-offs booked to 2021, leaving 2022 netted to a float zero. The two figures need not match
exactly, because a provision and a write-off are different bases. A whole year's shift between
them is not a basis difference.

So the strict XPASS is produced by a clock defect, not by affordability physics. Re-read
on the ledger's write-off dates, crisis 2021-22 is about 5.7% against 0.54% pre-crisis, so the step-up survives
the move. **I cannot yet say** whether the marker should go. That depends on whether the step-up
is emergent, which is the affordability cluster's question, not this one. The next step is to find
where `years[y].bad_debt_gbp` takes its year: a write-off keyed to the year a debt started, or to
the year before the run's 2022 reset, would produce this. The 2022 lifecycle red may be the same
defect, with events keyed off the same wrong year. That is untested.

## Re-read 2026-11-26 at HEAD b1399c1083: the hollow is gone, the year shift is not, and it is located

**Both original reds are cleared.** On the current `docs/reports/run_output_latest.json`, the
lifecycle test passes. The crisis test is an honest XFAIL, and since c0e3839087 its reason is the
real record's write-offs, not this hollow. 2022 now books GBP 338.95 of bad debt, and 2021 books
67.89.

**The shift the "Result" section found is still in every year.** Below, the ledger's `WRITTEN_OFF`
stages (`docs/state/billing_ledger.json`, built from run_output_76f894811d_20261126T155009Z) are
set against the run's `years[y].bad_debt_gbp`:

| year y | run bad_debt y | ledger write-offs y+1 | ledger write-offs y |
|---|---:|---:|---:|
| 2017 | 1,324.32 | 1,505.92 | 42.46 |
| 2018 | 1,374.86 | 1,417.41 | 1,505.92 |
| 2019 | 3,233.46 | 3,499.21 | 1,417.41 |
| 2020 | 151.11 | 175.75 | 3,499.21 |
| 2021 | 67.89 | 77.33 | 175.75 |
| 2022 | 338.95 | 367.95 | 77.33 |
| 2023 | 198.97 | 131.90 | 367.95 |
| 2024 | 289.24 | 313.53 | 131.90 |
| 2025 | 383.43 | 412.19 | 313.53 |

The run's year y tracks the ledger's year y+1, at about 92% of the amount (the provision and
write-off bases differ). The exception is 2023, where the run is above the ledger's 2024 (199 against 132).
I cannot yet say why: a stayer provision on the C1 bucket is one candidate. It does not track the ledger's year y.

**Mechanism.** `simulation/arrears_engine.py::_row_for` (line 1808). `compute_emergent_bad_debt`
keys each write-off by (customer, write-off year), and its docstring says the apply step books a
key dated after the account's last year "in that year". `_row_for` instead returns the account's
**last settlement record**, which is in an earlier year. A leaver's write-off at close falls after
its final settlement year, so it books into the P&L of the year before. `compute_debt_recovery`
goes through the same `_row_for`, so its recoveries shift the same way. This is a clock defect in
a published yearly series, not a basis difference.

**What the fix needs (a design change, not a one-line fix).** The P&L needs a row, or a
period-only line, in the write-off year for a customer who has no settlement row in that year, with
the treasury carry following it. Booking on the last record was chosen to stop the figure being
dropped silently (the 2026-09-27 balance-at-close record), so whatever replaces it must still not
drop the figure. Prediction, filed before building: once the fix is in, the run's year y matches
the ledger's year y within the basis gap (about 8%), and the 2019/2020 pair swaps to roughly
1.4k/3.3k.
