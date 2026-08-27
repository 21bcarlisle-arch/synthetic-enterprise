# A contract anniversary is 365 days, so the renewal schedule walks backwards through the calendar

**Date:** 2026-08-27. **Author:** the delivery seat, while chasing why `belief_vs_outcome` can
score only 24 of 42 priced renewals. **Status:** MEASURED, NOT FIXED — see "Why this is not
repaired here".

## The measurement

`saas/churn_model.py` sets `CONTRACT_LENGTH_DAYS = 365` and `_renewal_periods` steps by
`acquisition_date + 365 * n`. Over the simulation's own window:

```
a 1-January-2016 account, ten years of renewals:
  2016-12, 2017-12, 2018-12, 2019-12, 2020-12, 2021-12, 2022-12, 2023-12, 2024-12, 2025-12

a 1-April-2016 account:
  2017-04, 2018-04, 2019-04, 2020-03, 2021-03, 2022-03, 2023-03, 2024-03, 2025-03
```

**The January account never has a renewal in January.** Not once in ten years. Its first
anniversary is recorded in December 2016, because 2016 is a leap year and 365 days from 1 January
2016 is 31 December 2016 — a day short of a year, and the schedule never gets that day back.

**The April account drifts out of April in 2020** and stays in March for the rest of the decade.
Same cause, one leap year later.

The window 2016–2025 contains three leap years (2016, 2020, 2024), so a schedule pinned to
365-day steps loses three days against the calendar and crosses a month boundary for any account
whose anniversary sits near one. Every account acquired on the 1st of a month is near one.

## Why it matters

`renewal_period` is a `"YYYY-MM"` string, and it is a JOIN KEY. `roll_lifecycle_event` looks up
`win_rates[account]` for `r["renewal_period"] == term_month` and **returns None when there is no
entry** — no churn decision is rolled at all. So a schedule that drifts by a month does not
merely mislabel a renewal; it can silence one.

It is also simply wrong as domain modelling. A supply contract renews on its anniversary. Real
suppliers write terms in months or calendar years, and Ofgem's own contract-end notifications are
keyed to a calendar anniversary. A customer acquired on 1 April renews on 1 April, in every year,
including leap years.

## What this does NOT establish

**It does not prove this is the cause of the unmatched decisions**, and that link is deliberately
not claimed. What is measured about those is:

* `belief_vs_outcome` scores 24 of 42 priced renewals on the residential book (57%).
* The unmatched are the SAME SIX ACCOUNTS every year — C2, C6, C8 (April), C3, C9 (July), C4
  (October).
* Those six are exactly the accounts acquired on 2016-04-01, 2016-07-01 and 2016-10-01. The ones
  that match were acquired 2016-01-01.

The join is `(customer_id, term_start)` against `(customer_id, event_date)`, and settling which
side carries which date needs the per-row log, which the saved artefact does not keep — it
publishes aggregates. That is a live A/B run, and this finding does not pretend to have done it.

**Three hypotheses were formed and discarded before this one** while reading rather than
measuring: a calendar-boundary effect in `records_so_far`, a "January matches and others do not"
reading, and a derivation that predicted the exact OPPOSITE set of accounts would fail. The
measured facts above are what survived; the mechanism connecting them to the unmatched rows is
open.

## Why this is not repaired here

Changing `CONTRACT_LENGTH_DAYS = 365` to a calendar-anniversary step moves **every renewal
decision in the simulation**, and therefore every churn roll, every price, and every number in
the P&L. It is an R13-legitimate baseline change — decided for fidelity, on the calendar, blind
to what it does to the company's results — but it wants its own before/after measurement rather
than to ride inside a session that has already landed nine commits.

It is also the second time today this seat has been tempted to make a world change at the end of
a long session on the strength of a mechanism it had not proven. The first time, the mechanism
turned out to be wrong twice over
(`WORKER_FINDING_THE_GAS_LEG_AQ_IS_INVENTED_NOT_DERIVED_FROM_THE_DWELLING_2026-08-27.md`).

## The next step, precisely

Run the value-cycle A/B with the per-row belief log retained, and print, for one unmatched pair
(`C2`, `2017-04-01`), the arm's `term_start` beside every `customer_events` entry for `C2` in
2017. That is one measurement and it settles which side drifts. Only then change the step.
