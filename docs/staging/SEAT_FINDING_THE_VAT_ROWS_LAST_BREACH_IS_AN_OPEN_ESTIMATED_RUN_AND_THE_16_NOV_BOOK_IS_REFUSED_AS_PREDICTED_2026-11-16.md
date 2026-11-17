**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The VAT row's last breach is an open estimated run, and the 16 Nov book is refused as predicted (2026-11-16)

*Delivery seat, claim `the-four-unexcepted-rows-on-the-16-nov-book`. Follows
`WORKER_FINDING_THE_REVENUE_ROW_READ_NO_BACK_BILLING_BAR_AND_ITS_LAST_BREACH_IS_AN_UNREAD_TAIL_2026-11-16.md`.*

## 1. The direction record's prediction, graded

Filed in `DIRECTION.yaml` before the grade: the 07:05 book on f7e17b1316 "is refused on at least
INV_OVERDUE_WITHIN_BALANCE and INV_OVERDUE_WITHIN_PAGE_BALANCE".

**Right.** process_run_complete refused it at 12:31Z and again at 13:15Z (`sim-runner-log.md`):
INV_OVERDUE_WITHIN_BALANCE 4, INV_OVERDUE_WITHIN_PAGE_BALANCE 7, INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE 1,
INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR 5 (over the exception's max of 1). The seat reproduced the
same four counts at origin 2f23ad063 code on the shared tree's site data for that book
(`tools.domain_invariant_runner --ledger docs/state/billing_ledger.json --printed site/data/customers`).
The prediction was weak: the book carried none of the fixes, so it could only be right.

## 2. The VAT row's last breach: PROS-2025-0095g

**Cause, named.** The account opened 8 Apr 2025 and is still supplied at the record's end (no final
bill on its timeline). Its last actual read is May; its only later bill (1-7 Jun, the last week of the
record) is an estimate of £7.84 before VAT. The row bounded that open run's error by the run's own size
(U). The knowledge page (`unbilled_energy_and_revenue_assurance.md` §1, K2) says billed differs from
consumed "until the next actual read", either sign, with no magnitude. U-as-its-own-size is a bound
nobody established. The estimate missed by 178% of itself, and the gap is £0.79 beyond the bound.

**Fix, as a class.** A shortfall below the lower side on an account whose estimated run is still OPEN
(at least one bill after its last actual read, and no final bill closing it) is graded a **flag**, not a
breach: the record holds no read that could establish an error in either direction. A CLOSED account
keeps its breach, because its estimated final bill closed the run (§1, "An estimated final bill closes
its run"). The upper side is unchanged.

**Prediction, filed before the re-grade** (same book, same data, code changed only in this row):
INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE goes breached 1 -> 0 and flagged 0 -> 1, the flag being
PROS-2025-0095g. No other row's breached or flagged count moves.

**Result: as predicted.** INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE moves from 1 breached and 0 flagged
to 0 breached and 1 flagged. The flag is `PROS-2025-0095g gas R 151.39`, 141.25 against 142.04. Every
other row's (breached, flagged, checked) is identical. The test
`test_a_shortfall_in_an_open_estimated_run_flags_and_a_closed_one_still_breaches` covers the whole
partition in one control: open run gives a flag, a final bill gives a breach, an actual last read gives a
breach. Three mutations each turn it red: the branch removed, the final-bill check removed, and the
actual-read check removed.

**Not established.** Whether the June estimate itself is poor (12.3/day against May's actual 27.5/day).
That is `INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS`'s question, and this record does not answer it.

## 3. What still refuses a book newer than 6fe7827ab2, and who owns it

Graded on f7e17b1316 at this commit's code:

| row | count | cause | owner | fixed on origin? |
|---|---|---|---|---|
| INV_OVERDUE_WITHIN_BALANCE | 4 | D5: the desk opens a journey on a scheme debit no bill asked for | `DD_seasonal_cashflow_physics` (focus item 2) | **no**: the build has not started |
| INV_OVERDUE_WITHIN_PAGE_BALANCE | 7 | D5, the same (SYN-2016-471 misdated) | `DD_seasonal_cashflow_physics` | **no** |
| INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR | 5 | 39 settled records beyond any weather cell | fc3129a86 | yes, but not in this book |
| INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE | 0 (1 flag) | open estimated run (above) | this commit | yes |
| cast tariff row | 0 here | | 157e05c23 | yes |

So no book can publish until D5's build lands. A book built before then reproduces rows 4 and 7.
That is why the next book's launch condition (§4) names the D5 build as an unmet requirement and
does not leave it out.

## 4. The next book's launch condition

`sim_runner.book_admission` runs after `code_admission` on every cycle. It reads
`background/next_book_requires.yaml` and defers the book unless both of these hold:

- HEAD carries 157e05c23, fc3129a86, 163bf831a and 586e304ce (the open-run fix);
- D5's debit half has landed. Its row reads `commit: null` with owner `DD_seasonal_cashflow_physics`.
  Whoever lands D5 writes its commit in.

It also defers while any `longjob-*-queued` unit is active. A long job waits in that unit only while
`resource_headroom` refuses it, so while one exists the box does not admit both. If systemd gives no
answer, that is a deferral, not an empty queue. A running long job was already yielded to by
`cycle_admission`.

**Expiry.** The file lapses on 2026-11-24, and a log line says so. A row nobody fills in therefore
cannot hold books past the next Monday window unseen.

**Reverse.** Delete the file, or delete one row.

**Done-means, honestly.** No book newer than 6fe7827ab2 is published. The rows still refusing any book
are INV_OVERDUE_WITHIN_BALANCE (4) and INV_OVERDUE_WITHIN_PAGE_BALANCE (7). Both are owned by
`DD_seasonal_cashflow_physics`, whose build has not started.

## 5. 16:30Z, worker tick (RUNG-1 wedge draw): the D5 world half is not landed, and nothing is landing it

- **The publisher's 16:06Z re-gate, graded against a prediction written first.** It was predicted to be
  refused on the same three rows. **Right**: at 16:19Z it was refused on INV_OVERDUE_WITHIN_BALANCE 4,
  INV_OVERDUE_WITHIN_PAGE_BALANCE 7, and INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR 5. That is
  the seventh grade of this one 07:05Z book since 12:31Z, about one every 40 minutes. Each takes
  about 15 minutes and 1.8 GB. No test ran, so there is no red test to find. Memory is not short
  (12.4 GB free with the twin resident), so the retries cost CPU, not the twin's room.
- **The D5 world half (`FINAL_BILL_ASKS_THE_LEVEL_DEBIT = False`, `background/live_payment_triad.py`)
  is neither on HEAD nor on origin.** It exists only as an uncommitted edit in the shared working tree.
  The landing (`surgical_land` pid 976146) is gone. Its only log line is `/tmp/d5land.log`:
  `attempt 1/3 lost the race: HEAD 57158c97c -> 1d903a79f; re-gating the new base`. Nothing follows
  it, `/tmp/d5land2.log` is empty, and at 16:20Z no surgical_land or launch_long_job process is alive.
- **What it lost the race to was this wedge's own exhaust.** 1d903a79f is the publisher's
  "verification paused banner" commit. Each refused re-grade of the 07:05Z book lands one
  (ec2c57f18, 60e067ebe, 1d903a79f). So a retry that cannot pass moves HEAD under the one landing
  that could make the next book pass. I cannot yet say whether a banner commit also killed the
  re-gate, or something else ended the process. The log stops before saying why.
- **Not acted on, and why.** `DD_seasonal_cashflow_physics` is claimed by the seat (claimed 15:42Z),
  and a seat-executor turn started at 16:16Z. Re-launching the switched-off land from a worker tick
  would collide with that claim. Whoever holds D5 next should relaunch the world-half land from
  the working-tree hunks (`tools/isolate_hunks.py` + `surgical_land --content`) at a moment when
  the publisher is not mid-cycle. The next banner commit comes about 13 minutes into each
  publisher cycle.

## 6. ~19:30Z, worker tick (RUNG-1 wedge draw): the D5 world half is now on origin (ddde5880c, merge 43dfd323e)

- **The seat's own relaunch died too.** The 18:21Z land (pid 1613918) left an empty `/var/tmp/d5land.rfeo/land.log`
  and no process. Its saved bytes still matched the shared tree, so this tick landed them unchanged.
- **The primary checkout refused it** (HEAD one behind origin). It was landed from a worktree on origin/main.
  It lost the race once more, to banner 96458df0b, and was re-gated by merge and promoted.
- **It moves no row value: the switch is off.** The 19:07Z re-grade was refused on the same three rows,
  so this does not unwedge the publish. Rows 4 and 7 wait for the switch-on row in
  `background/next_book_requires.yaml` (`commit: null`): the page's `balance_settlement_from_outcomes`,
  the runner's choice 27, and SYN-2016-471's desk misdating.
- **`DD_seasonal_cashflow_physics` is no longer claimed** (the promotion's binding says it was swept).
  Nobody holds the switch-on now. It is handed on via `seat_continuation`.

## 7. 17 Nov, 16:20Z, delivery seat: the D5-on book's grade, filed before the book runs

*Claim `the-d5-book-is-graded-and-published-or-its-refusals-named`. At filing, step 6 is in pair 2's
last run (simulated Sept 2020 at 16:15Z, about 90 min a run), and `d5book-pause-watch` has not fired. No book newer
than f7e17b1316 exists. This file gathers the predictions already on record and adds the one that was not.*

### What the book must carry, checked before it runs

- `background/next_book_requires.yaml` names 341df4965 (D5 switched on), so `book_admission` defers any book
  without it. The shared tree's `background/live_payment_triad.py:168` reads `FINAL_BILL_ASKS_THE_LEVEL_DEBIT = True`.
- 317b1d56c (the walk-ordering counter, `settlements_behind_the_walk`) is not a row in that file. The grade checks
  `run_complete`'s `Git:` line is a descendant of both commits, and says so if it is not.

### Predictions (only the last one is new here)

| row | 16 Nov (f7e17b1316) | predicted | filed in |
|---|---|---|---|
| INV_OVERDUE_WITHIN_BALANCE (4) | 4 | at most 1 | D5 pre-registration, prediction 1 |
| INV_OVERDUE_WITHIN_PAGE_BALANCE (7) | 7 | 2, SYN-2016-001's 15 Aug 2023 steps only; SYN-2016-471 gone | same, predictions 2 and 3 |
| INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR | 5 | at most 1, within the exception (SYN-2016-206g at most) | fc3129a86's message |
| INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE | 0 (1 flag) | 0 breached | 586e304ce |

**New: the publish verdict.** The book is **refused on INV_OVERDUE_WITHIN_PAGE_BALANCE alone**, by SYN-2016-001.
The book redraws nothing, so its 15 Aug 2023 gas lump crosses behind the walk again, and
`settlements_behind_the_walk` names at least one walk. If the publish passes, prediction 2 is refuted: the lump moved
or the walk order changed, and I cannot say which until the counter is read.

**What this book cannot say.** It carries every commit since f7e17b1316, so it is not a one-variable run. A row
that matches is consistent with its named fix and does not attribute the change to it. A row this table does not
list that newly refuses is a finding in its own right, not a refutation of the table.

### Owners if the prediction holds

- Row 7 (SYN-2016-001): the walk-ordering class from the D5 pre-registration ("SYN-2016-001 traced to a class"). It
  has no owner in `next_book_requires.yaml` yet. The grade names one.

## 8. 17 Nov, 18:05Z, delivery seat: the pause fired, the book is held by an uncommitted walk fix, and §7's row-7 prediction is amended before the book runs

- **The pause fired cleanly.** `d5book-pause-watch` saw pair 2 on disk at 17:41:15Z and stopped step 6.
  The child had already printed `pair [33333, 44444] done` (seed 44444: 833 draws, 20,030 s). Both
  `member_33333_44444.json` and `control_33333_44444.json` were written at 17:40:48Z, and the sidecar
  holds both seeds. Nothing was lost to the stop.
- **sim-runner has not taken the book.** It deferred at 17:39Z on memory, before the stop. Since 17:44Z it
  defers every cycle with `the code a run would import is not origin's: background/live_payment_triad.py`.
  The shared tree holds an uncommitted edit made at 17:15Z by a scheduled-tick worker (pid 413423, started
  17:01Z). In `record_period`, `_settle_held(account_id)` becomes `_deliver_settlements_through(previous_due)`.
  There is a matching test, `test_a_re_presented_level_collection_crosses_before_the_walk_passes_its_day`,
  in `tests/background/test_a_lump_crossing_behind_the_desks_walk_is_counted.py`. That is the walk-ordering
  class that owns §7's row-7 refusal. The edit is that worker's, so the seat does not touch it.
  `code_admission` is doing its job: a book on bytes origin does not hold would be unattributable.
- **What the deferral costs.** The watcher relaunches step 6 at 01:41Z 18 Nov whether or not a book
  lands (its 8 h deadline). The book takes about 1 h 52 min, so it must be admitted by about 23:45Z to finish
  inside the pause.
- **The amended prediction (filed before the book; §7's table is otherwise unchanged).** If the book
  carries the worker's fix, it is a second change to row 7's cause. SYN-2016-001 pays both fuels by
  **standard credit** (2023 payments 21496/21497 and 21610/21611 are `standard_credit`), so its lump is
  not the re-presented level collection the fix's test names. The fix delivers every held settlement through
  `previous_due`, though, not only level ones. So I cannot yet say whether it reaches SYN-2016-001.
  Pre-registered: **row 7 reads 2 or 0, nothing else.** 2 means the fix does not reach a
  standard-credit lump, and `settlements_behind_the_walk` must name a walk for it. 0 means it does, and the
  counter must read 0 for that account. Any other value, or a 0 with a non-zero counter, refutes this.
  If the book is built WITHOUT the fix, §7 stands as written. The grade reads `run_complete`'s `Git:` line to
  say which book it was.
