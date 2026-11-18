**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`
**Discharged:** `docs/reports/domain_invariants.json`

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

## 9. 17 Nov, ~20:55Z, seat executor: the D5-on book is graded, and refused on two rows

*Claim `the-d5-book-is-graded-and-published-or-its-refusals-named`. The book: `run_complete_20261117T181948Z.md`,
`Git: 18f201c5bf`, finished 20:04:47Z (6,299 s). 18f201c5bf descends from 341df4965 (D5 on) and 317b1d56c (the walk
counter), and it IS the walk fix of §8. So §8's amended prediction is the one graded. Grade: the publisher's own
`docs/reports/domain_invariants.json` (git 18f201c5bf, 20:18:58Z), with every breach re-listed by the seat from the
same ledger and pages through `tools/domain_invariant_runner` evaluators, read-only.*

### Predicted against observed

| row | 16 Nov | predicted (§7, §8) | observed | |
|---|---|---|---|---|
| INV_OVERDUE_WITHIN_BALANCE (4) | 4 | at most 1 | **0** of 978 | held |
| INV_OVERDUE_WITHIN_PAGE_BALANCE (7) | 7 | 2 or 0 (§8) | **20** of 6,144, four households | **refuted** |
| INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR | 5 | at most 1, SYN-2016-206g | **1**, SYN-2016-206g, within the exception | held |
| INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE | 0 (1 flag) | 0 breached | **0** (1 flag) | held |
| INV_A_CLOSING_REFUND_IS_WITHIN_THE_HOUSEHOLD_CREDIT | not refusing | not on the table | **24** of 132, over the exception's max of 23 | new refusal |

**Publish verdict: refused**, on row 7 and on the closing-refund row. §7's "refused on row 7 alone" is refuted, by a
row the table did not list. The book carries every commit since f7e17b1316, so no row's move is attributed to D5.

### Row 7: four households, three of them leavers

- **SYN-2016-001, 2 steps** (15 Aug 2023, 386.23 against 329.71): unchanged from f7e17b1316, to the penny. That
  means the walk fix in 18f201c5bf does not reach this standard-credit lump. It is §8's "2" branch.
- **SYN-2016-471, 5 steps** (24 Apr to 25 Jun 2021, 38.13 against 28.78). **The D5 pre-registration's prediction 3
  is refuted.** The household still appears with the switch on, and the journey now opens on 24 Apr, not 30 Mar. By
  that prediction's own words the next trace is the desk misdating (`left_level_asks` reading bill 45883 as an
  on-receipt bill).
- **New on this book: SYN-2016-523** (5 steps, 20 Aug to 21 Oct 2023, 139.33 against 114.05) **and SYN-2016-546**
  (8 steps, 8 Dec 2018 to 7 Mar 2019, 49.98 against 43.25). Each prints one figure over a whole journey, above the
  page's balance. 471, 523 and 546 are all leavers: each page's `payment_record` ends at the move-out (`as_of`).
  523's gas leg and 546's electricity leg each carry one returned debit before leaving.
  **Hypothesis, not established:** all three are one class, the desk's ask for a leaver dated from a bill the final
  bill already netted. That is 471's open trace. The D5 switch-on was predicted to stop this path being reached. On
  this book it does not.
- **Owner:** `DD_seasonal_cashflow_physics` (D5's owner, and 471's open trace).
- **The walk counter cannot name a walk here, on any book.** `settlements_behind_the_walk`, `later_settlements` and
  `final_month_nets` are built in `simulation/run_phase2b.py:6523-6529`. But the run output is assembled by a key
  whitelist in `saas/reporting/annual_report.py` (`collections_journeys` is on it at line 1012; these three are not).
  The 18f201c5bf run output's 133 keys hold none of them. Nothing in `tools/`, `background/` or `saas/` reads them.
  So the D5 pre-registration's "the next book names the path" cannot happen, and neither can the "final_month_nets
  grade" this item's WHY lists. They are world truth, so the remedy is a harness-side artefact written beside the run
  output, not a `saas/` key. That is a seam decision (the interface steward's), filed here, not built.
  **Owner:** `DD_seasonal_cashflow_physics`, with the interface steward on the seam.

### The closing-refund row: 24 against a ceiling of 23

- Against the N29 record's 23 (`/var/tmp/n29r/classified.json`, the 8a300fa561 book): 22 are the same households.
  PROS-2020-0110g has left the row. **SYN-2016-037g** (refund 15 May 2020, 23.92 against 0) and **SYN-2016-368**
  (10 Mar 2023, 54.41 against 0) are new. So 23 − 1 + 2 = 24.
- **Class not established for the two new ones.** All 23 of N29's were `issued-not-yet-collected`. The two new ones
  are the same shape by value against bound, but they are not classified.
- **The exception's ceiling is a count of one book** (`max_breached: 23`, `DOMAIN_INVARIANT_EXCEPTIONS.yaml:258`).
  A redraw that swaps households moves it by one either way. That is a control keyed to today's answer, so this
  refusal says little about whether N29 got worse. **Owner:** `EP4_collections_journey` (the N29 finding,
  `SEAT_FINDING_THE_N29_BLIND_ROWS_23_..._2026-11-16.md`). Its options: re-scope the exception to the class (every
  breach `issued-not-yet-collected`) instead of a count, or land the N29 walk fix. The seat does not widen the
  ceiling to publish.

### Step 6 and the pause

- `longjob-value-test-step-6-flag1` is running again (admitted 20:04:47Z). Its log shows
  `pair [11111, 22222] already on disk, kept` and `pair [33333, 44444] already on disk, kept`, so it resumes at the
  third pair.
- **The watcher fired on the wrong marker.** At 19:21:15Z it named `run_complete_20261116T070501Z.md`, the refused
  16 Nov book, not this one. Its `find -newer stopped.stamp` reads mtime, and the publisher's refusal stamp
  (`<!-- domain-invariant-refused ... at=19:20:20 -->`) appends to that old marker. The relaunch then queued for
  memory behind sim-runner's book (7,066 MB) and was admitted the second that book finished. **The outcome was right
  by accident**: had memory allowed, step 6 would have restarted beside the book. One-line remedy for the next
  pause: match a marker name not present at the stop, not mtime. No pause is armed now.

## 10. 18 Nov, worker tick: the book after the refusals is published; retired (~13:30 GMT)

The 6af7fd0bfd book (built 18 Nov 07:02Z, published by 43fa9534d9, live on poesys.net) carries D5 switched on (341df49657), the row-7 leaver fix (594ed82390) and the walk writer (d645233e8b). Its committed `docs/reports/domain_invariants.json` reads `refuse: false`, `unexcepted: []`.

- **INV_VAT_RATE: CLEAN, 0 of 53,605 periods.**
- INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER reads 8, excepted, and retires on (a) as before.
- INV_A_CLOSING_REFUND_IS_WITHIN_THE_HOUSEHOLD_CREDIT reads 24. It is excepted on the N29 class (153a675ad4), not on a
  one-book count. That is §9's first option. The fix itself stays with EP4 under the N29 finding.
- Rows 4 and 7 read 0. Graded in the D5 and row-7 findings, both now in `done/`.

**One item is carried, not built.** §9's watcher remedy for the next pause is to match a marker name that was not
present at the stop, instead of reading mtime. No pause is armed, so nothing reads it today. It belongs to whoever
next arms a pause around a book.

Moved to `done/`.
