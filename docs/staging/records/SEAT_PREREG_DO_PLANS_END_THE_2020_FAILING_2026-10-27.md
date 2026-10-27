**Knowledge:** none -- a descriptive split of a world-only control arm, for the BLOCKING crisis bad-debt finding; no new domain claim

# Do the world's plans end the 2020 failing? (pre-registered 2026-10-27)

**Written before the run was launched.** It follows the refuted price-held capture
(`SEAT_PREREG_THE_PRICE_HELD_CAPTURE_2020_21_2026-10-27.md`). That capture found that the world's 2020
fall in failed share is mostly the same tenured households failing less. Of 2019's 80 failing accounts,
62 stay billed, and their 2020 failed pounds are GBP 2,468 against 7,129 the year before.

## The run

One world-only run with the control arm's code (no simulation, background, company, sim or saas path
differs from `21f216076f`), default book and dice, to 2021-03-31. Harness:
`/var/tmp/price_held/dump_plans.py 2021-03-31 /var/tmp/price_held/plans.json`. It is `dump.py`
plus the world's `HouseholdPlanBook` at the end, which holds the agreements (date, kind, months),
the debt-meter moves, and the stress tier by billed month.

**Check C0, before anything is read:** every 2016-2020 record matches `arm_off.json` (same account,
dates, result and amount). If it does not, the run is not the control and nothing below is graded.

## Definitions

- A *repeat account* is one that fails a bill issued in Y-1 and is still billed in Y.
- An account is *under an agreement* in Y if any agreement (any kind) or a debt-meter move is dated on
  or before 30 June of Y.
- *The drop* is the repeat accounts' failed pounds in 2019 less those in 2020. This is measured on
  their own Y=2019 and Y=2020 cohorts.

## Predictions

- **Q1 (plans are the cause).** Repeat accounts under an agreement account for **at least two thirds**
  of the drop. Under one third refutes plans as the cause.
- **Q2 (stress is the cause).** The share of residential credit bills at the top stress tier falls
  by at least a third from 2019 to 2020. A fall under a tenth refutes stress as the cause.
- Both can hold, and neither can. If neither holds, the next candidates are the per-bill draw's
  own year terms and the order the legs post in. Neither is ranked yet.
