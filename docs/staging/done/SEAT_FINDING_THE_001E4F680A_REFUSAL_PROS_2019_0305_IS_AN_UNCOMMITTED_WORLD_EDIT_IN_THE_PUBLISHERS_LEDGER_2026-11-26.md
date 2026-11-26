**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`

# The 001e4f680a refusal: PROS-2019-0305's breach comes from an uncommitted world edit in the publisher's ledger, not from the desk

The delivery seat wrote this on 26 Nov 2026, working the claim
`the-publish-wall-causes-two-to-five-are-closed-before-the-001e4f680a-book-is-graded`.

BLOCKING: the publisher grades a book on a ledger it regenerates from the shared tree's bytes. One
uncommitted world edit put a breach into the refusal that committed code does not produce. The same
edit is still on disk, and it will do the same to the 91c32797b3 book now building.

## The premise, re-measured

The 001e4f680a book (`run_complete_20261126T090839Z`) was graded at 11:18Z on 26 Nov, before this
item could file a prediction for it. Its refusal reads:

| row | 001e4f680a | owner, on origin |
|---|---|---|
| INV_UNIT_RATE_EPG_HOUSEHOLD | gone | 10bf51c37 (keyed to the read-tenths class) |
| INV_EBSS_CREDIT_* (two rows) | gone | 5e63e640ef (both exceptions retired) |
| INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS | gone | 204b68cca5 (one quote figure per read segment) |
| INV_OVERDUE_WITHIN_BALANCE | 2 | SYN-2016-107: 91c32797b3. PROS-2019-0305: **this finding** |
| INV_OVERDUE_WITHIN_PAGE_BALANCE | 8, all SYN-2016-099 | named in 470513f81b, not built |
| INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR | 7 | 9ed3dc9787 (weather cells), predicted |
| INV_A_CLOSING_REFUND_IS_WITHIN_THE_HOUSEHOLD_CREDIT | 1 of 8 outside class (PROS-2023-0338g) | named in 91c32797b3's finding; waits on `n29-close-set-off-nets-issued-debt` |

So items 2 to 5 of the direction were already taken by other turns. The one row without a named
cause was the second INV_OVERDUE_WITHIN_BALANCE breach. 91c32797b3 predicted that row would go
"1 -> 0", and this book shows 2.

## PROS-2019-0305, read

The desk opened a journey on 16 Oct 2020. It printed GBP 65.32 overdue, **1 day** overdue. That is
both electricity bills: INV15858 (September, GBP 63.29) and INV15859 (the 1 Oct stub final, GBP 2.03).
The ledger the gate graded has both bills issued 4 Oct and due 18 Oct, and both legs paid everything
due by 16 Oct. So the evaluator reads "nothing overdue".

1 day overdue on 16 Oct means the desk aged the balance from a bill due 15 Oct, which is a bill
issued 1 Oct. With committed code, `simulation.arrears_engine.bill_issue_date("PROS-2019-0305",
"2020-10-01")` is **1 Oct** (its own draw is 0 days late). On the shared tree it is **4 Oct**.
`simulation/arrears_engine.py` there has held an uncommitted edit since 11:24Z (mtime). The edit
reads "A LEG'S BILLS ARE ISSUED IN PERIOD ORDER": the issue date is held behind the leg's three
earlier periods. That is the world-side remedy 470513f81b weighed for SYN-2016-099.

The book ran in a clean worktree and stamped `imports_off_commit` empty, so its desk dated INV15859
on 1 Oct. Under the balance FIFO (`age_balance`), the uncovered tail then starts at a 1 Oct bill, so
the whole GBP 65.32 ages from 15 Oct. That is the printed figure. Replayed with `age_balance` over the
page events, the 4 Oct dating gives -2 days and the 1 Oct dating gives exactly GBP 65.32 at 1 day.

The decisive measurement: I regenerated the ledger from the same run output with committed code
(`tools.generate_billing_ledger.generate` in a worktree at fe14865204), then graded it with the same
runner and page.

- **Committed bytes:** INV_OVERDUE_WITHIN_BALANCE **1**, only SYN-2016-107.
- **The shared tree's 11:37Z ledger:** **2**, SYN-2016-107 and PROS-2019-0305.
- **Every other row is identical** between the two, breach for breach.

So PROS-2019-0305 is not a desk defect. The desk's date is the committed world's date. The breach is
the evaluator grading the run's journeys against a ledger written by a world the run never ran.

## The class: the publisher's own steps have no off-commit reading

`background/sim_runner.py` measures the run's import closure (`code_closure.imports_off_commit`), and
`process_run_complete.imports_off_commit_refusal` refuses a run that drew its figures from bytes no
commit holds. Then `process_run_complete` regenerates the billing ledger, the customer pages and the
invariant grade **in the shared tree**, and nothing measures those imports. On the shared tree now,
`imports_off_commit` gives:

- `tools/generate_billing_ledger.py` closure: `['simulation/arrears_engine.py']`;
- `tools/domain_invariant_runner.py` closure: `[]`;
- `tools/generate_customer_data.py` closure: `[]`.

So the reading is precise (one file) and cheap. It can be taken at grade time. This is the
9ed3dc9787 shape, an orphaned working-tree build read as if committed, on the publisher's side
of the run rather than the run's.

There is a second, distinct skew, and it is not built here. Once the issue-order edit LANDS, every
book run before it is graded against a ledger generated with it, and the same row appears on a
committed tree. A ledger regenerated by world code that differs from the run's `producing_commit`
does not describe that run. Evaluator code may legitimately be newer, as the EBSS and estimate rows
were graded. World-writer code may not.

## What is not done, and why

- **No guard is built this turn.** The refusal shape needs a decision I have not made: refuse the
  grade, or grade on the run's commit in a clean worktree. Refusing wedges the publish on any
  lane's in-flight world edit. Grading in a clean worktree is the right shape, but it moves every
  publisher step. Handed on below.
- **The uncommitted edit is not touched.** It is another lane's in-flight work. It is very likely the
  SYN-2016-099 world fix. Whoever lands it must know the consequence: a book built before it
  is graded with it.

## Prediction for the 91c32797b3 book, filed before it is graded

`run_output_91c32797b3_20261126T122405Z` started 12:24Z in `/var/tmp/se-sim-runner-book` and carries
10bf51c37, 5e63e640ef, 204b68cca5, 9ed3dc9787 and 91c32797b3, but not the issue-order edit. Over the
same world:

- INV_UNIT_RATE_EPG_HOUSEHOLD, both EBSS rows, INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS: not
  in the refusal.
- **INV_OVERDUE_WITHIN_BALANCE: 0** if the gate's ledger is generated on committed bytes. **1
  (PROS-2019-0305)** if the issue-order edit is still on disk, or has landed, when the gate runs. Any
  other count means this attribution is wrong.
- INV_OVERDUE_WITHIN_PAGE_BALANCE: 8 on SYN-2016-099 on committed bytes. I cannot say what it reads
  under the issue-order edit. The edit moves SYN-2016-099's February bill relative to its final bill
  in the ledger, but not in the run.
- INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR: at most 1 leg breach (SYN-2016-206g), with the share
  below its 1% bound (9ed3dc9787's prediction, carried).
- INV_A_CLOSING_REFUND_IS_WITHIN_THE_HOUSEHOLD_CREDIT: 1 of 8 outside its class (PROS-2023-0338g),
  until `n29-close-set-off-nets-issued-debt` lands.

So the 91c32797b3 book is still predicted to refuse, on SYN-2016-099 and PROS-2023-0338g, whichever
bytes it is graded on. Neither may be passed by widening an exception.

## Probe

`/tmp/seat_pw/` (not committed): `dump.py` (raw book), `probe.py` / `probe_head.py` (the full-breach
wrapper over `domain_invariant_runner`, on the shared ledger and the committed regeneration), and
`shift.py` (the `age_balance` replay at both datings).

## The prediction, graded (worker tick, 26 Nov 14:50Z)

The 91c32797b3 book was graded at 14:28Z. By then the issue-order edit had LANDED as d688a224a6
(13:17Z), so this was the second skew: a committed tree whose world code is newer than the run.
I re-graded the shared ledger with the finding's own probe, `/tmp/w_pw/probe.py`, against
`docs/state/billing_ledger.json.gz` at 14:18Z.

- INV_OVERDUE_WITHIN_BALANCE **1, PROS-2019-0305** (journey opened 2020-10-16). SYN-2016-107 is gone
  (91c32797b3). This matches the predicted "1 if the edit is on disk or has landed".
- INV_OVERDUE_WITHIN_PAGE_BALANCE 8, all SYN-2016-099 (1.30 against 0.68). The book's desk ran
  before d688a224a6, so the page still prints the old ordering.
- INV_A_CLOSING_REFUND_IS_WITHIN_THE_HOUSEHOLD_CREDIT: 1 of 8 outside the class, PROS-2023-0338g.
  7f90f9563a has since fixed that on origin.
- Gas repeat 1, inside its exception, as 9ed3dc9787 predicted.

So no breach on this book is a defect in code at origin/main e4dda28119. Each one is a fix that
landed after the run, or a ledger graded on world bytes newer than the run's. **The unwedge is a
book run at or after e4dda28119.** Predicted for that book: INV_OVERDUE_WITHIN_BALANCE 0,
INV_OVERDUE_WITHIN_PAGE_BALANCE 0, refund rows all inside the class. Any breach on those three rows
refutes this.

The guard (grade world-writer steps on the run's producing_commit) is claimed by the delivery
seat as `the-publisher-grades-a-book-on-the-bytes-its-run-ran` (claimed 14:34Z, in flight). This
item closes on that build's commit, not here.

## Built, later on 26 Nov (claim `the-publisher-grades-a-book-on-the-bytes-its-run-ran`)

The shape chosen: **the ledger is written on the run's commit, and the evaluator stays at HEAD.**
Refusing outright was rejected because the static closure of `tools/generate_billing_ledger.py` is
353 files and `simulation/arrears_engine.py` alone took 8 commits in the week before this. A refusal
on "the closure differs from the run's commit" would refuse nearly every book, which is the
always-red detector. Regenerating in a clean checkout of the run's commit is never refused for
that reason.

`background/process_run_complete.py::generate_ledger_on_run_commit` takes
`code_closure.imports_off_commit(tools/generate_billing_ledger.py, <marker git hash>)` over the
shared tree. That one `git diff <run commit>` reads both skews at once: an uncommitted edit, and a
world edit landed after the run. Then:

- measured identical: the ledger is written in-process, as before, at no extra cost;
- off commit: it is written by a subprocess in a throwaway checkout of the run's commit
  (`_materialise_head_into`, the gate's own checkout machinery), to the shared ledger path;
- unmeasured, or the checkout failed: nothing is written, the step raises (so the publish-step
  ledger records it), and the record carries the reason.

`_domain_invariant_gate_permits_publish` now grades the live ledger only when this cycle's record
says it was written for this run's commit. Otherwise it writes **NOT GRADED** with the reason and
refuses while enforcing, the same as an ungradable book. Before this, a failed ledger step left the
previous book's ledger on disk, and the gate graded that.

Controls: `tests/background/test_the_publisher_grades_a_book_on_the_bytes_its_run_ran.py`. The
first runs a real tiny repo whose world file is dirty and checks that the ledger reads the
committed bytes. The second is a partition control: all three routes are reachable. The third
checks that the gate does not grade an unproven ledger. Three mutations were run, and each one
fired: "always in-process", "unmeasured treated as clean" and "provenance check dropped".

What this does NOT cover, and is not yet measured:

- The ledger step's position. It reads the step's `git_hash`, which is the marker's `Git:` line
  (the run's commit). A marker with `unknown` is refused upstream by `stamp_not_on_origin_refusal`.
- The other publisher steps. `generate_customer_data`, `generate_invoice_data` and
  `domain_invariant_runner` have no `sim/` or `simulation/` file in their static closure, so they
  are evaluator/presentation code and stay at HEAD. That claim rests on the static graph. A step
  that re-asks the world through a lazy import the graph misses would not be seen.
- The cost of the cold checkout on a live book has not been measured. The timeout is 1200s, which
  is 20x the ~1 minute the in-process step took on the 26 Nov books.

The uncommitted issue-order edit on the shared tree was not touched.

## Graded on the 76f894811d book (delivery seat, 26 Nov 2026 21:5xZ)

Book: `run_output_76f894811d_20261126T155009Z.json`, 1,382 accounts, 54,463 bills. It descends from
7f90f9563a, d688a224a, 91c32797b3, 9ed3dc9787 and e4dda28119. Its ledger was written in a clean
checkout of 76f894811d (fcd2facdcd's route; sim-runner-log 21:02Z). The publisher's own gate,
`docs/reports/DOMAIN_INVARIANTS.md` at 21:11Z, reads **0 unexcepted breaches across 0 invariants, 6
excepted: the publish stands.** I re-ran the same runner (`load_book` with the printed customer files,
then `run`, then `gate`) on a snapshot of that ledger and the completed customer files. It
reproduced the table row for row. Probe outputs: `/var/tmp/grade76/` (not committed).

| prediction (filed 14:50Z, for a book at or after e4dda28119) | measured | grade |
|---|---|---|
| INV_OVERDUE_WITHIN_BALANCE 0 | 0 of 946. PROS-2019-0305 opens no breaching journey | **held** |
| INV_OVERDUE_WITHIN_PAGE_BALANCE 0 | 0 of 5,630 printed collections steps | **held** |
| Closing refunds all inside their class | 6 of 159, all `other_leg_debt_collected_after_the_refund`, 0 outside | **held** |

The guard this item waited on is built (fcd2facdcd), and this book is the first graded through it. The
ledger was written in a clean checkout of 76f894811d, although the shared tree differed in four world
writers.
