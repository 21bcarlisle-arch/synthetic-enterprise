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
