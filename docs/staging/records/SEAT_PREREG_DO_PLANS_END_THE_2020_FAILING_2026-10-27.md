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

## Graded (2026-10-27, 22:20Z): Q1 refuted, Q2 inconclusive, C0 failed narrowly and is characterised

- **C0 fails as written.** 29 of about 25,000 records differ, all from 2020-05 on, and every one is a
  prepayment `success` bill 1p apart (for example ACC-PROS-2018-0176, GBP 12.55 against 12.54). These
  are probably end-of-run amounts on a meter leg, since this run ends a year earlier. **All 962 failed
  records match exactly.** Every number below reads failed records only. The C0 failure is reported
  rather than waived, and nothing below depends on the differing bills.
- **Q1 is refuted, and more strongly than the prediction framed it.** The world agrees **no plan at
  all**: 2,923 offers, 0 accepted, 0 declined, all unanswered, and no debt-meter moves. That is by
  design. Plan take-up is a named GAP (`simulation/plan_offer_response.py`,
  `PUBLISHED_BASIS.take_up_rate=None`). Repeat accounts under an agreement number 0 in both years.
- **Q2 is inconclusive.** The top stress tier's share of noted months goes from 2.31% (134 of 5,812)
  in 2019 to 2.01% (105 of 5,222) in 2020, a fall of 13%. That is between the 10% refutation line and
  the 33% support line. *Deviation:* this counts all noted months, including prepayment and SME, not
  only residential credit bills as filed. A 13% move in a tier that sets one input of the per-bill
  draw is too small to halve a failed share whose pounds come mostly from the budget path.

**What the run does show.** Seven accounts carry 42-47% of each year's failed pounds, on both dice
seeds. Several fail every bill in 2019. SYN-2016-549 fails GBP 1,126 of 1,126 billed in 2019 and
none of 1,079 billed in 2020. Next: `SEAT_PREREG_IS_THE_2020_HALVING_A_FEW_HOUSEHOLDS_2026-10-27.md`.
