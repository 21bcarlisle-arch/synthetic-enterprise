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
