**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: the first book carrying the close-refund fix, graded only through the publisher's gate (2026-11-11)

*Lane-0 item `the-first-book-carrying-the-close-refund-fix-is-run-and-graded-through-the-publishers-gate`. This is
the exit-test book of the 26 Oct ruling. It retires the blocking finding
`SEAT_FINDING_THE_068B5E3CC8_BOOK_DOES_NOT_PASS_THE_PUBLISHERS_GATE_THE_SCRATCH_GRADE_COULD_NOT_READ_THE_CLOSED_ACCOUNT_ROW_2026-11-11.md`
if it grades 0 there. This table is filed before the book starts.*

## When it starts, and on what

When this was filed (05:30 GMT), neither fix was on origin. The close-refund fix ("A level leaver's final bill meets
its credit before the refund…", `/var/tmp/wt-close-refund-sizing`) had been refused once because its gate timed out at
3,600 s, and it was being landed again (surgical_land pid 1920905). Item 1 (`a-close-refund-waits-for-the-money-it-pays-out`,
the residual 12) was claimed and in progress. The direction says to launch "once item 1 is on origin, or if it stalls
after the close-refund fix alone is on origin". So the launch is armed, not made:

- `/var/tmp/crbook-scripts/waitlaunch.sh` runs as `longjob-launcher-crbook` and has an 8-hour deadline. It launches at
  origin/main's head only when all four of these hold:
  - (a) `tests/simulation/test_a_level_leavers_final_bill_meets_its_credit_before_the_refund.py` is on origin;
  - (b) this record's commit is an ancestor of origin/main;
  - (c) item 1's delivery-lane claim is gone, or 3 hours have passed since arming. Three hours with the claim still
    held counts as "stalls";
  - (d) no `longjob-book-*` or `longjob-grade-chain-*` unit is active.

  Then it launches `longjob-book-crfix-<sha>` and `longjob-grade-chain-book-crfix-<sha>` through `launch_long_job`.
- **Grading, the only chain allowed:** `/var/tmp/crbook-scripts/grade_one.sh`. This is the publisher's page chain
  (`/var/tmp/fourth-read-scripts/pages.py`, then explore_hh_day and explore_carbon) in a scratch tree built by
  `git archive <sha>`. Then comes `_domain_invariant_gate_permits_publish(<sha>)` (`/var/tmp/eleventh-read/scripts/gate.py`),
  with every row in `table.tsv`. The readers below run on the publisher-built `docs/state/billing_ledger.json`. The
  scratch `grade.py`/`after_run.sh` chain is not used.
- **Arm** `/var/tmp/crbook/arm/`: the new book. **Cross** `/var/tmp/crbook/cross/`: the D1 book e1587ec5b through the
  same page code. Arm against cross is the run half alone. `ALLDONE` or `NO_DONE`/`NO_LAUNCH` closes it.

**Which column applies.** Column B applies if any commit landed under item 1's focus id is an ancestor of the book's
sha. Otherwise column A applies, which is the close-refund fix alone.

## The control, measured through the same chain (not copied)

`/var/tmp/crbook/control/` is the D1 book `run_output_e1587ec5b_20261111T012324Z.json` through origin
**a481c9ab96**'s publisher chain and gate. The chain reproduces dc3e7dfeb4's verdict: **REFUSED, 208 unexcepted on 2
rows, 7 excepted**. All 8 Explore slots are filled.

**Corrected beside the item's claim.** The drawn item cites "347 level-DD cures over a debt (last read on 298149a1fc)".
That reading is two fixes old. The same reader (`compose.py`, holds over a debt) reads **116 on 70 accounts** on this
control. It read 193 on 4dee9854a4 and 78f82e4242. The item also cites "29, GBP 1,374.58" written off and printing
owed. That is 068b5e3cc8 on its own page. Through origin's page it is **29, GBP 1,249.62**, both since class L′
(7cf859beff) and here. The table uses the measured figures.

## The table

The close-refund effect was filed on 068b5e3cc8's output (`/var/tmp/close-refund-probe/{base,fix}`). It moved the
refund row from 205 to 12 and the refund lines from 238 to 176. The closed-account row went from 3 to 0, bad debt at
close fell by GBP 500.92, and the refund total fell by GBP 3,312.32. The D1 book shares 068b5e3cc8's refund and close
figures to the penny (D1 moves asks, not refunds), so the same deltas are predicted here.

| # | Row | Control (D1 book, a481c9ab96) | A: close-refund fix alone | B: plus item 1 | Refuted if |
|---|---|---:|---|---|---|
| 1 | INV_REFUND_WITHIN_THE_PAGE_CREDIT breached / refund lines | 205 / 238 | **8 to 18** over 150 to 200 lines | **0** over 150 to 200 lines | outside the column's range, or 0 lines |
| 2 | INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO breached | 3 (ceiling 2) | **0 to 2**, so not refusing | same | above 2 |
| 3 | Unexcepted total | 208 on 2 rows | **= row 1**, on 1 row | **0** | any other row unexcepted |
| 4 | The gate | refused | **refused, on row 1 alone** | **permits** | the other verdict |
| 5 | INV_OVERDUE_WITHIN_PAGE_BALANCE (no exception since dc3e7dfeb4) | 0 of 6,385 | **0 to 3** | same | above 3 |
| 6 | INV_PLAN_REOFFER_FOLLOWS_A_MISSED_BILL | 0 of 1,248 (a481c9ab96) | **0** | same | any |
| 7 | The 7 excepted rows: EPG 337, PPM 12, EBSS ×2 7/7, estimate run 7, gas repeat 1, elec yoy 2 | as listed | **each unchanged**. None reads refunds or closing balances. PPM, EBSS, gas and elec sit AT their ceilings, so +1 refuses | same | any moves |
| 8 | Refund GBP on the pages (`refunds.py`) | 24,692.96 | **falls by 2,500 to 4,000** | falls by 2,500 to 4,500 | outside |
| 9 | Legs refunded yet closing in page debit (`over_refund.py`) | 0 | **0** | 0 | any |
| 10 | Written-off accounts printing owed (`wo_owed.py`) | 29, GBP 1,249.62 | **24 to 31, GBP 900 to 1,300**. Credit that now nets a leaver's debt can only lower it | same | outside either bound |
| 11 | Level-DD cures held over a debt (`compose.py`) | 116 on 70 accounts | **106 to 126** | same | outside |
| 12 | Bad debt written off at close (`emergent_bad_debt_lines`, close) | GBP 10,794.48, 121 leg-years | **10,200 to 10,400** (falls about 500) | same ±100 | outside |
| 13 | Run `total_bad_debt_gbp` (settled-realised) | GBP 9,477.58 | **falls, by 0 to 800**. I cannot size it: it is a different clock from row 12 | same | rises |
| 14 | Cross arm, row 1 (D1 run through the new page) | — | **195 to 205**: the fix is in the run half (the walk), not the page | same | below 195 |
| 15 | Explore slots | 8 of 8 filled | **8 of 8 filled or honestly empty**, none breaching | same | a slot breaches |

**What this book can and cannot show.** Rows 1 to 4 are the exit test. Rows 8, 12 and 13 are published figures that
move. Each is marked against the 068b5e3cc8 offer, which is still open. The grade commit carries
`Graded: close-refund-book held= missed= code= reader= regressed=`. If the gate permits it, the book is offered to the
publisher under the director's 8 Nov yes ("One early publish as soon as a book passes the full gate"), with
`background.sim_runner --promote`. The eleventh cold read
(`the-eleventh-cold-read-on-the-first-book-the-gate-passes`) runs on it. If the gate refuses, every refusing row is named
with its count, cause and owner.

## Reverse

Stop the `longjob-launcher-crbook` unit. Delete this file. Nothing outside `docs/staging/` and `/var/tmp` is touched.

## State at 10:45 GMT (worker tick)

Not launched, and correctly so. `longjob-launcher-crbook` is alive and has logged `close-refund fix not on origin` every
five minutes since 05:40. The fix is not refused or lost. Its test
(`test_a_level_leavers_final_bill_meets_its_credit_before_the_refund.py`) and item 1's test
(`test_a_close_refund_waits_for_the_money_it_pays_out.py`) sit untracked in the seat executor's worktree
`/var/tmp/se-seat-executor` (pid 346075), beside uncommitted edits to `simulation/arrears_engine.py` and
`simulation/credit_refund_events.py`. The seat is landing the fix together with item 1. Condition (c), the three-hour
stall, lapsed at 08:40, so the book launches on the first poll after that landing reaches origin. The table above is
unchanged. Column B applies if item 1's commit is in the book's sha.

**Deadline.** The launcher gives up at **13:40 GMT** and writes `/var/tmp/crbook/NO_LAUNCH`. If that file exists and the
book has not launched, the next tick re-arms `waitlaunch.sh` under the same table. It must not launch a second book by
hand while `longjob-launcher-crbook` is active.

## State at 14:05 GMT (worker tick): launched on cab13bbd18

The first launcher expired at 13:41 without launching (`NO_LAUNCH.1`), as directed. The fix had not been landed: the
12:47 page landing lost the race to origin and its worker was killed. This tick landed it in two commits from
`/var/tmp/crfix2/recovered` and salvage 79d98bc344. **cf399ab43** is the K8 page, home_moves.md s.8.8c and s.8.8d.
**cab13bbd1** carries the engine, the 6-line `money_in` run wiring and both controls (5 passed).

- **Re-armed** as `longjob-launcher-crbook-2` (`waitlaunch2.sh`, 8 h from the wiring landing). Condition (c) used to
  name the retired item-1 claim. It now reads "`WIRING_SHA` cab13bbd1 is an ancestor of origin/main". It launched on
  its first poll: `longjob-book-crfix-cab13bbd18`, at 14:01:52Z, writing
  `docs/reports/run_output_cab13bbd18_20261111T140152Z.json`. `longjob-grade-chain-book-crfix-cab13bbd18` follows it
  through `grade_one.sh` (arm, then cross), and nothing else grades it.
- **Cure row:** `longjob-crbook-cure-row-2` (`cure_row_arm2.sh`) waits for `arm/DONE` and then grades the level-DD
  map's s.4 prediction, **112 to 120**. The first cure-row unit exited 6 at 12:46 because the first launcher was still
  alive.
- **The column is B.** s.8.8d, item 1's residual 12, is in cab13bbd1 itself. That puts it in the book's sha, so the
  predictions are row 1 **0**, row 3 **0** and row 4 **permits**. Every other row is unchanged from the table. I wrote
  this at 14:05, before any of the book's output existed.
- **Imports-off.** The launcher's reading failed under the unit (`SE_NTFY_TOPIC` unset, from importing
  background.notify), so the book was passed `--imports-off-commit ""`. `run_annual_report` then takes its own reading
  at start (line 624). A hand reading in the locked worktree a minute after launch gave `paths: []`.
  **Corrected at 14:08: wrong.** argparse refuses an empty value before line 624 is ever reached
  (`invalid loads value: ''`). The book died at launch, its grade chain wrote `NO_DONE` ("no run json"), and the
  cure-row unit exited with it. Nothing was graded. The markers are in `/var/tmp/crbook/failed-cab13-1406/`.
- **Relaunched at 14:07 GMT** as `longjob-launcher-crbook-3` (`waitlaunch3.sh`). It loads `.env.ntfy` before taking the
  reading and writes `NO_LAUNCH` instead of launching on an empty one. The reading at launch was `{"commit":
  "6fe7827ab2", "paths": []}`. The book `longjob-book-crfix-6fe7827ab2` is running on origin 6fe7827ab2, which is
  cab13bbd18 plus this record and nothing else. Its grade chain is behind it, and `longjob-crbook-cure-row-3` is behind
  that. The path above is now `run_output_6fe7827ab2_*.json`, and `/var/tmp/crbook/RUN_PATH` names it.
- **Next tick:** when `/var/tmp/crbook/ALLDONE` exists, read held or fell for every row from `arm/` and `cross/`. Land
  them with a `Graded:` trailer. If the gate permits, offer the book with `background.sim_runner --promote` under the
  director's 8 Nov yes.

## Graded at 16:37 GMT (seat executor): all 15 rows held, in column B

The book `run_output_6fe7827ab2_20261111T140730Z.json` was graded only through `grade_one.sh`, with the arm at 15:59 and
the cross at 16:02. The readings are in `/var/tmp/crbook/{arm,cross}/`. Column B applied, as filed at 14:05.

| # | Row | Read | B predicted | Verdict |
|---|---|---|---|---|
| 1 | Refund breached / lines | **0** over 176 lines (176 legs) | 0 over 150 to 200 | HELD |
| 2 | Closed-account breached | **0** (87 flagged) | 0 to 2 | HELD |
| 3 | Unexcepted total | **0** | 0 | HELD |
| 4 | The gate | **PERMITS True**, 7 excepted | permits | HELD |
| 5 | INV_OVERDUE_WITHIN_PAGE_BALANCE | 0 of 6,385 | 0 to 3 | HELD |
| 6 | INV_PLAN_REOFFER_FOLLOWS_A_MISSED_BILL | 0 of 1,248 | 0 | HELD |
| 7 | The 7 excepted rows | EPG 337, PPM 12, EBSS 7/7, estimate run 7, gas 1, elec 2: all unchanged | unchanged | HELD |
| 8 | Refund GBP | 21,380.64, **down 3,312.32** | down 2,500 to 4,500 | HELD |
| 9 | Refunded legs closing in debit | 0 | 0 | HELD |
| 10 | Written-off accounts printing owed | 28, GBP 1,195.85 | 24 to 31, GBP 900 to 1,300 | HELD |
| 11 | Level-DD cures over a debt | 113 on 69 accounts | 106 to 126 | HELD |
| 12 | Bad debt at close | GBP 10,293.56, 119 leg-years (down 500.92) | 10,200 to 10,400 | HELD |
| 13 | Run `total_bad_debt_gbp` | GBP 9,037.78 (down 439.80) | down 0 to 800 | HELD |
| 14 | Cross arm, row 1 | 201 of 238 | 195 to 205 | HELD |
| 15 | Explore slots | 8 of 8 filled, `book_breaches {}` | 8 of 8, none breaching | HELD |

The level-DD map's s.4 cure count reads **113, inside 112 to 120: HELD**. That landed separately in 6073fee791, from the
same `arm/` reader.

**What the clean sweep does not show.** Rows 8 and 12 are not independent tests. They were predicted from 068b5e3cc8's
deltas, and they reproduce them to the penny (3,312.32 and 500.92). That confirms D1 moves asks, not money, but it is
one observation counted twice. Rows 1 to 4 are the exit test, and those are the rows that carry weight.

**Not predicted, and named here so it is not lost.** In the cross arm (the D1 run through the new page code),
INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO breaches **23**, against 3 on the control. It refuses that arm (224 unexcepted
on 2 rows). The page change alone makes more of the old run's closed accounts read short of zero, and the run half's
fix is what clears them. It does not touch this book, which reads 0. But it means the page and the run half cannot be
published separately. No row was written for it, so it is neither held nor fell.

**Offered.** `background.sim_runner --promote` wrote `docs/staging/run_complete_20261111T160541Z.md` at 16:05, naming
this JSON, and `run_output_latest.json` is byte-identical to it. The offer is under the director's 8 Nov yes. The
publisher's sweep takes it from here. The eleventh cold read ran on this book (ab2700c1e3).
