**Severity:** INFO · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: one write-off date for a leaver's debt, graded on the first fresh run carrying it (2026-10-29)

Written before any run carries the change. Item `the-write-off-date-is-one-for-the-page-the-sweep-and-the-desk`.
It grades class (a) of `INV_OVERDUE_WITHIN_PAGE_BALANCE` alongside
`SEAT_PREREGISTRATION_A_CREDIT_BILL_POSTS_TO_THE_DESK_AND_THE_ROW_NETS_ONE_ACCOUNT_2026-10-29.md`
and `SEAT_PREREGISTRATION_AN_OCCUPIERS_BILLS_READ_THE_TRIADS_PAYMENT_TRUTH_2026-10-28.md`.

## What changed

The company's write-off of a closed account, a year after its final bill
(`company/billing/arrears_engine.closed_account_write_off_date`), is now the one date:
- the desk writes the balance off on that day inside its walk and ends the journey
  (`CollectionsJourneyDesk._write_off_if_closed`, rule `CLOSED_ACCOUNT_RULE`);
- the world's close write-off, which the page's arrears history and the P&L read, is dated by it
  (`simulation/arrears_engine.WRITE_OFF_DATE_CONVENTION = "company_closed_account_write_off"`).

Before: page at the final bill's due date; sweep a year after the final bill, after the loop; desk at
the six-year bar. Knowledge: `docs/market_research/debt_and_collections.md` s.7.3. Control:
`tests/company/billing/test_a_leavers_debt_has_one_write_off_date.py`, both legs mutation-proven.

## Baseline

b2fc50facf book, class (a): 723 steps on 112 households (33 on `OCC-`, 690 other).

## Predictions

- **P1.** Class (a) (a desk step dated on or after the page's first write-off on the household,
  overdue above the page's balance) falls from 723 to under 100. What is left: a dual-fuel account
  where one fuel leaves and the other stays (the page writes the leaving fuel off; the company's
  account is still billed, so it is not closed), and legs whose world final bill and company final
  bill differ by date.
- **P2.** On single-fuel leavers with a close write-off on the page, the desk's `write_off` stage
  under `CLOSED_ACCOUNT_RULE` is on the page's `WRITTEN_OFF` date on at least 95% of accounts.
- **P3.** Total bad debt (`emergent_bad_debt_lines` "total", summed over keys) moves by under 1%:
  amounts and the recovery share are unchanged, only dates move. Per-year figures may move where an
  account has a record in its write-off's new year; the grade lists any year moving more than 5%.
- **P4.** Desk statute-bar write-offs on leavers' accounts fall to near zero (a leaver is written off
  at a year, before any six-year bar).
- **P5.** The post-loop sweep (`company_provision.write_offs_posted`) posts under 10% of what it
  posted on the baseline: the desk has taken the rest on the same date.

A refuted prediction is kept here beside the result, not revised.

## Run

Named 2026-10-29 04:50 GMT, before the run has started (it is queued for memory). The queued
`fresh-run-0b2879ef7d` predates 2b70102f9, so it cannot grade this. A second run carries it:
`launch_long_job` job `fresh-run-209c3350ab`, worktree `/var/tmp/fresh-run-wt-209c3350ab` (origin
209c3350ab, locked), script `/var/tmp/fresh-run-scripts/arm.py`, output `/var/tmp/fresh-run-out-209c3350ab`.
Graded by `/var/tmp/wo-grade-209c-scripts/after_run.sh`: the ledger, the full suite, the overdue
row's classes (`/var/tmp/onepay-scripts/lag_occ4.py`), and P2 to P5 (`wo_probe.py`).

Baseline for P2 to P5, measured by `wo_probe.py` on the b2fc50facf ledger before this run exists:
- P2: 25 single-fuel accounts and 103 multi-leg accounts carry a page write-off; on none of the 25 does
  the desk write off under `CLOSED_ACCOUNT_RULE` (the rule did not exist).
- P4: 106 desk statute-bar write-offs on accounts the page wrote off (3 on accounts it did not).
- P5: `write_offs_posted` 106.
- P3: `write_off_at_close_gbp` summed £12,323.59; `bad_debt_gbp` by year 2016 to 2025: 1,929.90,
  6,006.53, 5,908.97, 5,517.42, 4,761.42, 4,359.10, 6,238.40, 9,483.00, 7,814.76, 5,301.13.

The fresh run at 209c3350ab also carries every fix the 0b2879ef7d run grades. Its other rows are a
second reading of that pre-registration, not a grade of it.

## Results

**Not yet: the run has not started (06:15 GMT).** `fresh-run-209c3350ab` has been queued since 04:42, behind
`fresh-run-0b2879ef7d` (queued 03:35). Both wait for memory: the box was holding a 2.5-hour full
pytest (about 4 GB) and an annual-report run, and each fresh run declares a 12,500 MB peak against a
23,008 MB budget. No output exists, so P1 to P5 are unread and stand as written. The grade fixture is
in place and unchanged: run worktree at 209c3350ab, `after_run.sh`, `wo_probe.py`, `lag_occ4.py`. A
`tools.wait_for` waiter on `arm.py /var/tmp/fresh-run-out-209c3350ab` runs the grade once `DONE.json` exists.

**07:45 GMT: still queued, and the waiter had died.** The `tools.wait_for` waiter on `arm.py` named
above was gone, so the book would have finished ungraded, the same failure the 0b2879ef7d grade hit. A
transient unit `grade-chain-fresh-run-209c3350ab` (systemd --user, script
`/var/tmp/wo-grade-209c-scripts/chain.sh`) now waits on queue pid 1172912, follows
`longjob-fresh-run-209c3350ab` to its end, and runs `after_run.sh` into `/var/tmp/wo-grade-209c/`
(`ALLDONE`, or `NO_DONE` if no `DONE.json`). `wait_for` caps a single wait at 6 h, so the chain re-arms
while the queue pid lives: a queue longer than 6 h would otherwise grade an empty output dir. No output
read. P1 to P5 stand as written.

**07:59:51 GMT: the run has started.** For three hours the queue log showed only `HELD: landings come
before experiments` lines, which read as landings starving the queue. They were not what held it. At
07:47 a pending landing was present in 33 of 40 samples taken 15 s apart (82%; the prediction written
first was at least 70%). But the one 90 s gap with no landing (07:51:23 to 07:52:53) launched nothing.
The full-suite census (`head-green-census`, pid 562397, about 5 GB measured) was still on the box
then. It exited at 07:54:46 (`ActiveState=failed`). Resident memory fell to 1.8 GB, and 209c started
at the next gap, five minutes later. The queue retries in `launch_long_job.main` print only their
first `NoRoom`, so a memory refusal after it leaves no trace: the log names the landing hold and
hides the memory hold. Fixed in the commit that records this: a retry now prints whenever the cause changes (control `test_a_queue_names_each_new_cause_of_its_wait_not_only_the_first`, mutation-proven). The grade chain was waiting on job unit `longjob-fresh-run-209c3350ab` by
07:59:56. `fresh-run-0b2879ef7d` is still queued: it cannot fit beside this run (12.5 + 12.5 GB
against a 23 GB budget). No output read. P1 to P5 stand as written.

**09:18 GMT: graded.** `fresh-run-209c3350ab` wrote `DONE.json` at 09:14 (4,459 s, nothing skipped), and
the chain wrote `ALLDONE` at 09:16 (`/var/tmp/wo-grade-209c/`: `grade.txt`, `lag.txt`,
`wo.txt`). Same 1,293 accounts as the baseline. Below, each prediction as written, then the reading.

- **P1 holds, and more strongly than predicted.** Class (a) is **0 steps** (723 on b2fc50facf):
  `lag_occ4.py` prints no `after_page_write_off` key at all. The residue I predicted (a dual-fuel
  account where one fuel leaves and the other stays, and world/company final bills on different dates)
  does not appear as class (a). The leg-level split in P2 explains why: on such an account the desk
  writes the leaving leg off on its own date, and from then on no step prints more than the pages say.
- **P2 holds.** All 21 of 21 single-fuel accounts with a page write-off have the desk's
  `CLOSED_ACCOUNT_RULE` write-off on the page's `WRITTEN_OFF` date (share 1.000; prediction ≥0.95).
  This was not predicted: on multi-leg accounts the share is 34 of 86. 48 have the desk's close
  write-off on a different day from the household's *first* page write-off, and 4 have none. This
  probe compares each leg's write-off with the first one on the household, so a second leg written off
  on its own later date counts as "other day". That is why class (a) can be 0 while the share is
  0.395. This is a limit of the probe, not a breach.
- **P3 holds on the measure stated.** The arrears lines summed over every key come to £682,254.91,
  against £683,208.02 on the baseline: −0.14% (prediction: under 1%). `bad_debt_gbp` by year moves at
  most 0.28% in any year (2020: £4,761.42 → £4,748.17). The ten-year total moves +£10.75 (+0.02%). No
  year moves more than 5%. **But one part of "amounts unchanged, only dates move" is refuted.**
  `write_off_at_close_gbp` falls £457.42 (£12,323.59 → £11,866.17, −3.7%) across 65 accounts: 36 of
  them are `OCC-` legs carrying £418.14 of the fall, and on 43 of the 65 `pre_4c_net_gbp` does not move. `dca_recovery_gbp` falls about
  12% of each account's drop (£1,503.46 → £1,447.60), as it would if the recovery share applied to a
  smaller write-off. **I cannot yet say what causes it.** This run also carries the six fixes the 0b28
  run grades, including 558ee46245 (occupiers' bills read the triad's payment truth), and that fix
  touches exactly the `OCC-` legs.
- **P4 holds.** Desk statute-bar write-offs on leavers: **0** (106). Every desk write-off on the book
  (185) is under `CLOSED_ACCOUNT_RULE` on an account the page wrote off. So `INV_STATUTE_BARRED_WRITE_OFF_AGE`
  is now **UNREACHED**: no statute-barred write-off is left anywhere on the book, and its exception
  (3 of 64) has nothing to describe. That is expected when a leaver is written off at a year. It also
  means the row can no longer fail on a default book: a six-year bar now needs a stayer in debt for
  six years, and this book has none.
- **P5 holds.** `company_provision.write_offs_posted` is **0** (106; prediction under 10%).

**Prediction for the attribution, written 09:18 GMT before `fresh-run-0b2879ef7d` has started.**
That run carries the six fixes without the one write-off date, so it is the one-variable comparison
for the −£457 close write-off. My prediction is that the *date* causes it, not the occupier fix. Moving
the page's write-off from the final bill's due date to a year later lets a year of payments land
first, and an occupier's leg is the one that keeps paying after its final bill. **0b28's
`write_off_at_close_gbp` will be within £100 of £12,323.59 (the b2fc50facf figure), not near
£11,866.17.** If it lands near £11,866, the occupier fix caused the move and the date did not. In
that case P3's "only dates move" stands, and this paragraph is the wrong prediction.

**10:47 GMT: the attribution prediction is refuted. The occupier fix and its five companions cause
the whole fall; the date causes none of it.** `fresh-run-0b2879ef7d` wrote `DONE.json` (4,371 s,
nothing skipped; its worktree runs `WRITE_OFF_DATE_CONVENTION = "final_bill_due_date"`, so it is
the one-variable comparison). Probe `/var/tmp/wo-attr-0b28-scripts/attr.py`, over
`p2b__arrears_lines_by_customer.pkl.gz` on all three books (1,293 accounts each):

| book | carries | `write_off_at_close_gbp` | `dca_recovery_gbp` |
|---|---|---|---|
| b2fc50facf | neither | £12,323.59 | £1,503.46 |
| 0b2879ef7d | six fixes | **£11,866.17** | £1,447.60 |
| 209c3350ab | six fixes + one date | £11,866.17 | £1,447.60 |

- b2fc → 0b28: −£457.42 on 68 accounts (65 above 1p, the count given above). 36 `OCC-` legs carry
  −£418.14 and 32 others carry −£39.28.
- 0b28 → 209c: **£0.00 on 0 accounts.** The arrears lines are identical on every key for every
  customer, not only this one.
- So P3's "amounts unchanged, only dates move" **stands for the date change.** The −3.7% belongs to
  the six fixes, most of it to the `OCC-` legs that 558ee46245 touches. This split cannot separate
  the six fixes from each other.

**A second result I did not predict.** `bad_debt_gbp` is identical between 0b28 and 209c in every
year 2016–2025, and in every (customer, year) of `p2b__all_records` (0 differ). All the per-year
movement P3 reads above (at most 0.28%) is therefore the six fixes, not the date. Moving a leaver's
close write-off a year later moves nothing in the P&L. The likely mechanism, which I have not
established: `arrears_engine._row_for` books a figure dated after an account's last settlement
year on that account's last record. A leaver has no records after it leaves, so either date lands
in the same row. If so, 2b70102f9's claim that the P&L reads the one write-off date holds only in
name: the P&L books a leaver's write-off in its exit year. Filed:
`docs/staging/SEAT_FINDING_A_LEAVERS_WRITE_OFF_BOOKS_IN_ITS_EXIT_YEAR_WHATEVER_ITS_DATE_2026-10-29.md`.

**Second readings, not grades of this record.** On this book `INV_OVERDUE_WITHIN_PAGE_BALANCE`
breaches 2,500 of 19,491 steps (9,455 of 32,726 on b2fc50facf; the step count also changed). `lag_occ4.py`
attributes 27 to a page payment the desk has not yet seen and the rest to "other": 1,679 at most 2p,
675 up to £1, 145 above £1. `INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS` breaches 269 against its
exception's 153, so the full suite **refuses the publish** on this book. That is the 0b28
pre-registration's P3 ("I cannot yet say"), and its grade owns the ceilings. Neither is changed here.
