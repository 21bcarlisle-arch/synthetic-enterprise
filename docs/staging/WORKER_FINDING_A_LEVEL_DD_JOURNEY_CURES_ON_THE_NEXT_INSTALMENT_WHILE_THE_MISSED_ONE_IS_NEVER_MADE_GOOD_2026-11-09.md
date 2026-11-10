**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`
**Knowledge:** `payments-and-direct-debit` -- `docs/market_research/payments_and_direct_debit_2026-10-25.md` "What is owed"

# A level DD journey cures when the next instalment is collected, but the missed one is never made good (2026-11-09)

**Found by.** The desk-cure ledger leg pre-registered on the level-DD finding (`SEAT_FINDING_A_LEVEL_DIRECT_DEBIT_HOUSEHOLD_IS_DUNNED_PER_BILL_SO_ITS_PAGE_PRINTS_OVERDUE_WHILE_IN_CREDIT_2026-11-07.md`,
"Added pre-registration leg"). It said that if the leg failed it would become its own finding. It failed on the first
two books carrying step 2b (a3136e29fa). The grade is on that finding, in the section "The desk-cure ledger leg and the
BSCP504 rows on the step 2b books".

**The trace (298149a1fc book, `/var/tmp/grade-2981/ledger.json`).** SYN-2016-549's electricity pays a GBP 45 level DD.
- 4 Apr 2018: the instalment fails. On 5 Apr the desk opens a journey, overdue GBP 45.
- 4 May 2018: the next instalment, GBP 45, is collected. The desk cures the journey ("overdue balance cleared on the
  ledger", overdue 0).
- The failed April GBP 45 is never collected again. Invoice 50827 is still outstanding at GBP 45 at run end (4 Jul 2025).
- The pattern repeats: 4 Sep 2018 fails, the desk opens, then cures on 26 Nov. The 4 Sep and 4 Oct failures are still
  outstanding at run end (GBP 45 and GBP 90).
- The household then leaves level DD for standard credit. The desk cures 27 later journeys while those failed
  instalments are still on the page.

Ofgem's letter of 20 Sep 2011 (App. 2 para 2.8, quoted on the knowledge page) says a DD customer who defaults on a
payment is in debt. Collecting May's instalment does not make good April's. **The desk's cure seems to read the shortfall
for the current period, not the shortfall carried forward against the schedule.** That is the hypothesis. I have not
yet traced it in `company/` code.

**Size, on the 298149a1fc book** (the reader is `/var/tmp/grade-84f7-ledgerleg/split.py` with level legs capped at the
schedule shortfall; the split is `/var/tmp/grade-2981-cure/compose.py`; output in `/var/tmp/grade-2981-cure/`):

| Shape at the cure | Cures held over a debt | Accounts |
|---|---:|---:|
| Level DD at cure, and an invoice due by the cure is still unpaid at run end | 88 | 43 |
| Level DD at cure, and nothing due by the cure is unpaid at run end | 104 | 83 |
| Left level DD, and an invoice due by the cure is still unpaid at run end | 151 | 19 |
| Left level DD, and nothing due by the cure is unpaid at run end | 3 | 1 |
| Never on level DD | 1 | 1 |

The 88 and the 151 fit the hypothesis: the debt never goes away. **The 104 I cannot yet say.** The reader was written
before step 2b. It measures a level leg's shortfall from invoice-keyed level payments, so it may be counting a
seasonal debit that step 2b's schedule does not owe.

**Not the cause:** two schedules. On this book `only_post_loop` is 0 and `differ` is 0.2% (the level-DD finding's
298149a1fc grade).

**What done means.** On the first book after the fix:
- no level-DD journey cures while a failed instalment presented before the cure has not been made good;
- the 88 + 151 shapes read 0;
- every non-level journey keeps its cure date.

The control: a two-instalment level account whose first instalment fails and whose second succeeds. The control must
keep the journey open. A partition leg is also needed: an account whose failed instalment is re-presented and collected
must cure.

**Recommended next, one variable.** Find the cure predicate for a level leg in the collections desk (step 2b's
"shortfall against the schedule"). Then print its shortfall for SYN-2016-549 on 4 May 2018. The prediction, filed before
reading the code: it prints 0, because it compares May's collection against May's instalment.

## Correction, before any run: the predicate is cumulative, so the filed mechanism is wrong (worker, 9 Nov 2026 ~08:00 GMT)

The hypothesis above said the cure "reads the shortfall for the current period". **It does not.**
`arrears_engine.level_shortfall` (`company/billing/arrears_engine.py:254`) computes
`min(requested to date - received to date, debit balance)`. That is cumulative. A failed April instalment that was never
made good stays in "requested". The prediction filed above ("prints 0, because it compares May's collection against May's
instalment") is withdrawn as a mechanism. It was refuted by reading the code, not by running it.

Two candidates remain, read from the code and not yet printed:
1. **The debit-balance cap.** A shortfall is counted only up to the debit balance (Ofgem: "a shortfall in credit is
   nothing owed"). If the desk's ledger balance on the cure day is nil or in credit, the journey cures by design. The page
   then still shows the failed instalment's invoice as outstanding. That would make it a page-and-desk disagreement
   about one account, not a false cure. The page reader put SYN-2016-549 at GBP 2.79 owed on 4 May 2018. So the two
   balances differ by at least that much on that day.
2. **Once level, always level.** The desk's `level_of` (`payment_observation_consumer.py:901`) returns a schedule
   for any account that has *ever* had a level collection requested. So `_step(level=True)` follows the account after it
   leaves level DD. On that path, a journey cures whenever the view shows nothing overdue. It never asks
   `_owes_a_bill_due_by`, and it opens only on a level return. This fits the 151 cures on 19 accounts that left level DD.
   One example is SYN-2016-549 in 2020: on standard credit, three failed bills unpaid, journeys cured.

**Prediction, filed before printing:** on SYN-2016-549, `level_of` is non-None after its last level request on
24 Jan 2019. Candidate 2 accounts for at least 140 of the 151 left-level cures. Candidate 1 accounts for most of the 88
level-at-cure cures that still have an unpaid invoice. Recommended next, one variable: replay the desk on SYN-2016-549
alone and print `level_of`, `level_shortfall` and `ledger.balance` on each cure day.

## The replay, graded (worker, 9 Nov 2026)

**Readers.** `/var/tmp/grade-2981-replay/replay.py` replays the desk predicate on one account from a ledger
rebuilt off the page rows. `desk_own.py` and `join.py` grade the whole book from the desk's own cure stage:
`days_overdue` 0 means the view held a shortfall item aged 0 days, and None means it held no item.
**The rebuild is not faithful past 2022.** It lacks write-offs and the cash the desk posts itself. On 272 cures it
reads a shortfall more than 0 days old where the desk read none, so the book-wide grade uses only the desk's own record.

**SYN-2016-549, each cure day:**
- 4 May 2018: level_of is set; level_shortfall is GBP 45.00, aged 0 days; the balance is GBP 201.82.
- 26 Nov 2018: level_shortfall is GBP 42.84, aged 0 days; the balance is GBP 204.70.
- The desk recorded both cures as overdue 0 and days 0. That is an item aged 0 days, not the absence of an item.
- Every cure from 14 Apr 2020 on is after the last level request (24 Jan 2019). level_of is still set. The desk read
  days None, meaning no item. `_owes_a_bill_due_by` reads True on every one in the rebuild.

**The prediction, graded:**
1. *level_of is non-None after 24 Jan 2019:* **HELD.** `_level_requests` is never cleared.
2. *Candidate 2 explains 140 or more of the 151 left-level cures:* **HELD.** 150 of 151 cured with no item in a level view.
   That view never asks for the scheme's debit. The one left is aged 0 days.
3. *Candidate 1 explains most of the 88:* **FELL.** 43 of the 88 cured on an item aged 0 days. At most 45 could be the
   debit-balance cap or a met schedule.

**The cause the prediction missed, a third mechanism.** The shortfall is cumulative, as the 08:00 correction says. But
the cash is applied to the oldest request first. So the next instalment's cash meets the failed one, and the shortfall
moves onto the request presented that day. That request ages 0 days. The desk cured on "the view reads nothing
overdue", which needs more than 0 days. The non-level path already guards this exact day-of-due shape with
`_owes_a_bill_due_by`. The level path had no equivalent. Book-wide on the desk's own record: 110 level-at-cure cures
are of this shape, and 91 had no item.

## The fix (worker, 9 Nov 2026)

- `arrears_engine.on_level_dd(ledger, schedule, on)` decides whether an account is still on level DD. It is, while
  some supply leg's latest bill issued by `on` is one a level collection paid for. The leg is the part of the bill
  reference before its first `::`. It is per leg because 61 accounts on 298149a1fc mix a level leg with a non-level
  one. Level requests are always DD, so their correlation id is the invoice reference.
- The desk walks an account on its schedule only while `on_level_dd`. A level journey cures only when
  `level_shortfall` is None. The view's "nothing overdue" is no longer enough. An account that has left level DD is
  walked on its bills: it cures only if `not _owes_a_bill_due_by`.
- The consumer's collections view reads the schedule only while `on_level_dd`. After that, it ages the balance on
  its bills, the debit the scheme ran up included.
- **Control and partition leg, in one test:** `test_a_missed_instalment_not_made_good_holds_the_journey_and_a_made_good_one_cures`.
  The made-good branch is asserted first. The left-level leg is `test_an_account_that_left_level_dd_is_dunned_on_its_bills`.
  At HEAD that account cured on 6 Mar 2025 with GBP 260 owed on bills past due.
- **Mutations:**
  - M1, the level cure reads the view again: red.
  - M4, the level cure never fires: red, on two tests.
  - M3, the view keeps the schedule after the account leaves level: red, on the opening amount.
  - M2, the desk keeps the account on level after it leaves: **does not fire alone. This is a missing test, not an
    equivalence.** The fixed view still blocks the cure, except when a left-level household pays down to a balance
    that sits only on a bill due that day. There, the level path's `level_shortfall` excludes today's ask and cures,
    and `_owes_a_bill_due_by` holds. No fixture here builds that case. It is filed below.

**GAP, filed: no closing statement for a level scheme.** Once an account leaves level DD, its scheme debit is aged
from the due dates of the bills it sat on. The fixture's journey opens at GBP 290 and goes straight to the plan-offer
rung. A real supplier sends a closing statement with its own terms. Ofgem's para 2.8 says a debit at the end of a
payment scheme is not debt by itself. Nothing in the tree models that statement, so the opening rung on a left-level
account is harsher than practice. That is the open half of this fix. It needs a knowledge-page entry before it is
built (K8).
*The K8 entry is written (worker, 9 Nov 2026): `docs/market_research/payments_and_direct_debit_2026-10-25.md`,
"Leaving level direct debit with a debit: the closing statement". It proposes a 28-day closing statement that opens
the journey on its first rung. The build is not done, and the entry holds the build's prediction.*

## Prediction for the first book carrying the fix (filed before any such book exists)

- The finding's 151 shape (left level, an invoice due by the cure unpaid at run end) reads **0**.
- Within the 88 shape, the 43 cures on an item aged 0 days read **0**. **The 45 with no item I predict will persist.**
  These are level-at-cure cures where the schedule was met or the balance cap applied, while a bill the scheme had not
  covered is unpaid at run end. That is a seasonal debit, which para 2.8 says is not debt. So the drawn "88 reads 0"
  is not what this fix should do, and I am not claiming it.
- Cure dates on accounts that never held a level request are **byte-identical**: neither predicate changed for them.
- **Expected and unsized:** more journeys, and longer ones, on accounts that left level DD in seasonal debit. Their
  debit is now dunned. I cannot yet say how many.
- **Refuted if:** any non-level journey's cure date moves; or any level-at-cure cure is recorded on an item aged
  0 days; or any left-level cure lands while `_owes_a_bill_due_by` holds.

## M2's missing test, built (delivery seat, 9 Nov 2026 ~11:20 GMT)

The test is `test_a_left_level_household_one_bill_behind_does_not_cure_on_each_due_date`, in the same file.

**The case.** The household is on level DD from October to December at its bills' own GBP 100, so it leaves level DD
square. January's bill fails and is never paid. Every later bill is collected at its face on its due date.

**What the desk sees on each due date.** The cash goes to the oldest bill first. The GBP 100 still owed moves onto the
bill due that day, and the view reads it 0 days overdue. The stopped schedule has been met. Only `_owes_a_bill_due_by`
holds the journey open.

**The partition leg runs first.** It is the same household with January re-collected 20 days late. The desk must cure
that one.

**Results:**
- At HEAD: 8 of 8 tests pass.
- With M2 applied (the desk passes `level[0]` whenever `level_of` is set): this test goes red and the other 7 stay green.
  The mutant cured on 14 Mar and 14 Apr 2025, each time with GBP 100 owed and an item aged 0 days. That is the left-level
  aged-0d shape the book prediction says reads 0.
- **M2 is now a mutation that fires, not a missing test.**

## The book grade: not yet run, because no book carries the fix (9 Nov 2026 ~11:20 GMT)

The newest book is 9d7dcfc19c (run finished 10:45 UTC). It is **not** a descendant of d8264b525e, which landed at 10:39.

The shared tree's HEAD does carry the fix. The sim runner logged "Waiting 4685s before next run" at 10:58, so the next run
starts at about 12:16 UTC and finishes at about 14:10 UTC. That is the first book that can grade the prediction above.

**The instrument, fixed now:**
- Copy that run's `docs/state/billing_ledger.json`.
- Run `python3 /var/tmp/grade-2981-replay/desk_own.py <ledger>` from a repo worktree.
- The prediction's three refutation legs read off its rows:
  - `('left level', 'aged 0d item')` reads 0;
  - `('level at cure', 'aged 0d item')` reads 0;
  - `('left level', 'days=None')` is graded against `_owes_a_bill_due_by` through `join.py`, which needs the
    `split.py` rows first.
- Never-level cure dates are byte-identical only between two arms from one recipe. Across a different book that leg
  cannot be graded: it reads "cannot say", not "held".

**The pre-fix reference is 298149a1fc (`desk_own.txt`):** 2 left-level aged 0d, 195 left-level no item, 110 level-at-cure
aged 0d, 91 level-at-cure no item.

## The book that grades it: launched off the shared tree (delivery seat, 9 Nov 2026 ~12:50 GMT)

**Why not the sim runner's run.** The runner has deferred every cycle since 12:16 UTC. The shared tree holds
uncommitted W3_3 bytes in `simulation/policy_costs.py` and `simulation/hedged_settlement.py`, and they belong to a live
worker tick (pid 938268). `sim_runner` has no clean-extract route: it always runs in the shared tree. So this book runs
outside the loop, as `fresh-run-209c3350ab` did. It touches nothing of the holder's.

**The run.** `launch_long_job` job `book-505df564e3`. It runs in a locked worktree `/var/tmp/book-wt-505df564e3`, which is
origin 505df564e3 and carries both d8264b525e and e0aeece0d. The import closure reads clean against 505df564e3
(`paths: []`). The output is `docs/reports/run_output_505df564e3_20261109T124818Z.json`, and it is promoted by hand once it completes.
The grade chain is `/var/tmp/grade-505d-scripts/after_run.sh`, writing to `/var/tmp/grade-505d/`. Its readers are the
ones named above, copied and pointed at the run worktree instead of the shared tree.

**The never-level leg can be graded after all.** The section above says it needs two arms from one recipe. The
9d7dcfc19c book is that second arm. Between 9d7dcfc19c and 505df564e3, the only commits touching `company/`, `simulation/`,
`saas/` or `sim/` are d8264b525e, e0aeece0d and their merge. Both ledgers are rebuilt with one reader, the 505df564e3 one,
and the control is at `/var/tmp/grade-505d/control-9d7d/`. Cure dates are compared on accounts with no level-DD payment at all.
**One caveat, written down before the run.** The arm carries two fixes. e0aeece0d changes cash on level leavers, and
the cash reaches the treasury, so a never-level account could still move through a company-wide decision. If a
never-level journey moves, that is the first cause to rule out before calling the prediction refuted.

**The control arm, read before the arm exists** (9d7dcfc19c, the pre-fix book, same readers):
- `desk_own`: left level, aged 0d: **2**. Left level, no item: **195**. Level at cure, aged 0d: **110**. Level at cure, no item: **91**.
  These are the same counts as 298149a1fc.
- `compose`: **347** holds on 109 accounts. Left level with an invoice unpaid at run end: **151** (19 accounts). Level at
  cure with an invoice unpaid: **90** (45 accounts).
- `join` within the unpaid shapes: left level, aged 0d: **1**. Left level, no item: **150**. Level at cure, aged 0d: **45**.
  Level at cure, no item: **45**.
- So on the one-recipe baseline, the prediction's targets are 151 → 0, then 45 → 0 (it read 43 on 298149a1fc), and 45
  persists.

**Started 13:05:35 GMT.** The queue held it behind the W3_3 landing. A detached unit, `grade-chain-book-505df564e3`, waits
for the job to end and then runs `after_run.sh`. It writes `ALLDONE` or `NO_DONE` in `/var/tmp/grade-505d/`.

No output has been read. The prediction above stands as written.

## The closing statement: before count, build, and its prediction graded (worker, 9 Nov 2026 ~14:00 GMT)

**Instrument.** The 505df564e3 book was still running, so this grade replays the desk itself over the
9d7dcfc19c book's page ledger (`/var/tmp/grade-505d/control-9d7d/ledger.json`), once with HEAD's `company/`
(3c78bc24c1, which carries d8264b525e) and once with the build. Each arm runs the same 180 level-DD accounts and the
same ledger, so the code is the only thing that changes. Scripts: `/var/tmp/closing-stmt/scripts/replay.py` and `compare.py`.
- A replayed journey is the desk's own walk on a ledger rebuilt from the page.
- The replay asks no Breathing Space register, and every bill asks its face.
- So these are not the book's own journeys.

**The before figure.** On HEAD, **7** left-level journeys on **7** accounts open on a scheme debit no statement ever
demanded: their oldest unpaid bill is a level-paid bill. All 7 open between 30 and 85 days overdue. The first rung is
the **plan offer on 5** and the final notice on 2.

**The build.** `arrears_engine.left_level_asks` and the desk's statement openers are built as the K8 entry
(payments_and_direct_debit, "Leaving level direct debit with a debit") proposed. Three refinements were forced by a
probe and are recorded on that page: two-stage cash allocation; a missed instalment keeps its date only when a journey
held it on the day of leaving; past-due is split from current. The control is
`tests/company/billing/test_a_level_dd_leaver_is_sent_a_closing_statement_before_its_debit_is_dunned.py`:
- The partition asserts both branches first: a statement left unpaid opens, and one paid inside 28 days never opens.
- Six mutations fire: no re-dating, no statement opener, no carve, always carve, single-stage allocation, and whole
  balance printed overdue.
- One existing assertion was keyed to the old reading. It had GBP 290 overdue on 15 Feb with the scheme debit not yet
  due. It is corrected beside the claim.

**The prediction e3242c6bb filed, graded on the replay:**
- *The plan-offer rung is never the first rung of a left-level journey:* **HELD.** It was the first rung on 5 of 9
  before, and is on 0 of 9 after. All 9 open 1 day overdue, at `reminder` (8) or `reminder_2` (1).
- *No left-level journey opens earlier than 28 days after the leg's last level collection:* **FELL, on 3 of 9** (also 3
  on HEAD). The prediction was wrong, and the cause is not the build. Those three accounts never left level DD. Each
  level collection is presented before the bill it pays is issued, so when the latest issued bill is not level-paid,
  `arrears_engine.on_level_dd` (d8264b525e) reads the account as having left. 5 of the 8 "leaver" accounts carry on
  collecting level into 2025. That is a defect in the leaving predicate. It is filed here as the next item and is not
  fixed in this commit. Under the build, those false leavers now open on the first rung at small sums (GBP 7.39,
  GBP 27.15). Before the build they opened at the plan offer or the final notice.
- *Never-level journeys are byte-identical:* **cannot say from this replay**, because it replays level accounts only.
  By construction, an account with no level schedule takes the unchanged path (`level_of` None). The 278 journeys
  opened while on level are byte-identical between the arms.
- *Direction of the overdue rows:* **I cannot yet say.** That needs a book that carries the build.

**GAPs carried as GAPs.** These are unchanged from the K8 entry:
1. The term is 14 to 28 days. The build uses 28, at `CLOSING_STATEMENT_TERM_DAYS`.
2. Whether the statement is a standalone statement or folded into the first bill.
3. Whether the debit is spread by default.

**Not changed, and downstream of this:**
- `cash_forecast_provision`, `default_belief` and the consumer's page `snapshot` still age a leaver's balance by bill
  date.
- The provision therefore still ages the scheme debit from the level bills.
- It is named here, not fixed.

NEXT: the leaving predicate. `on_level_dd` must not read an account that is still collecting level as having left.

## The 505df564e3 book, graded: two legs held, the left-level leg fell, and the overdue rows quadrupled (seat executor, 9 Nov 2026 ~15:40 GMT)

**The book.** `book-505df564e3` ran from 13:05 to about 14:50 GMT, at origin 505df564e3, which carries d8264b525e and
e0aeece0d. Its run json is `docs/reports/run_output_505df564e3_20261109T124818Z.json` on the shared tree. The grade chain
ran `after_run.sh` unchanged, and its outputs are in `/var/tmp/grade-505d/`. The control is 9d7dcfc19c, rebuilt with the
same readers (`control-9d7d/`). **The ledger is `/var/tmp/grade-505d/ledger.json`**, and the closed-account grade
(`grade-the-level-dd-close-on-its-first-book`) reads that path.

**The prediction, leg by leg** (arm against the one-recipe control):

| Leg (filed before any book) | Control 9d7dcfc19c | Arm 505df564e3 | Verdict |
|---|---|---|---|
| The 151 left-level shape (an invoice due by the cure still unpaid at run end) reads 0 | 151 on 19 accounts | **45 on 8 accounts** | **FELL** (residual named below) |
| Level-at-cure cures on an item aged 0 days read 0 (`join`) | 45 | **0** | **HELD** |
| Level-at-cure cures on an item aged 0 days (`desk_own`, every cure) | 110 | **0** | **HELD** |
| Left-level cures on an item aged 0 days (`desk_own`) | 2 | **0** | held |
| Schedule-met or cap cures with no item persist | 45 | **74 on 41 accounts** | **HELD** in kind. Why 45 became 74 I cannot yet say. |
| Never-level cure dates are byte-identical | 643 journeys | 643, `identical True`, none only in one arm | **HELD** |
| Cures held over a debt (the class listed wrong at 347) | 347 on 109 accounts | 191 on 92 accounts | moved, not cleared |

**The residual: 45 left-level cures on 8 accounts, all true leavers.** Every one is dated after that account's last level
collection: PROS-2018-0016, PROS-2019-0246, SYN-2016-206, -217, -244, -253, -360 and -487. So it is **not** the
false-leaver defect named in the section above. All 8 were in the control's 151, and none is new.
- **Shape.** What stays unpaid is the remainder of a failed level instalment from the level era, never made good. For
  example, SYN-2016-487's GBP 24 failed on 12 Oct 2017 and left GBP 3.07 on each leg. SYN-2016-206's GBP 64.15 failed in
  May 2016 and left GBP 15.36. Those invoices are still outstanding at run end.
- **The two ledgers disagree.** Replaying 505df564e3's own `on_level_dd` and `_owes_a_bill_due_by` on a ledger rebuilt
  from the page (`/var/tmp/grade-505d-residual/residual.py`) reads `on_level_dd=False, owes=True` on **all 45**. So the
  predicate the fix added would have refused every one of them. The desk cured anyway, and printed `days_overdue` None
  or negative. Its in-run ledger does not count the level-era remainder as a bill owed, and the page does.
- **Mechanism: not established.** The next question is how the in-run ledger allocates a failed level request's
  remainder (oldest-first carry against per-invoice), measured on SYN-2016-487 on 19 Jun 2019. That day the desk read
  GBP 0 overdue after a GBP 29.70 payment, and the page replay reads GBP 27.81 owed. The closing-statement build
  (8e73c52356, the section above) re-dates a missed instalment on leaving, so the next book may move this. It has not
  been graded.

**The full gate** (`domain_invariant_runner`, 1302 accounts, read with the same `grade.py` on both arms):
- **Arm: 614 unexcepted breaches across 2 invariants, 8 excepted. ENFORCED: the publish is refused.**
  - INV_OVERDUE_WITHIN_BALANCE: **129** (control 71).
  - INV_OVERDUE_WITHIN_PAGE_BALANCE: **485** (control 80).
- **Control, the same reader:** 151 (71 + 80). That is the figure `process_run`'s gate refused 9d7dcfc19c on, so the
  reader is not the cause. I predicted "it reproduces 71 and 80" before running it. **Held.**
- **Excepted rows, arm (control):**
  - INV_UNIT_RATE_EPG_HOUSEHOLD 336 (337)
  - INV_PPM_NOT_CREDIT_BILLED 12
  - INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23 7 (7)
  - INV_EBSS_CREDIT_ON_THE_BILL 7 (7)
  - INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER 7 (7)
  - INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR 1
  - INV_ELEC_MONTHLY_USE_MOVES_YEAR_ON_YEAR_LIKE_A_HOUSEHOLD 2
  - INV_PLAN_REOFFER_FOLLOWS_A_MISSED_BILL 21 (20)
- Every other row has the same status in both arms. Their checked counts fall by about 0.2% (bill periods 53,921 →
  53,835): the book is slightly smaller, through the company-wide cash route the caveat above named.

**Where the new overdue breaches sit** (`overdue_breaches.py`, every breach, grouped by the account's level status at
run end):

| Row | Control: still level / left level | Arm: still level / left level |
|---|---|---|
| INV_OVERDUE_WITHIN_BALANCE (journey openings) | 49 / 22 | **105 / 24** |
| INV_OVERDUE_WITHIN_PAGE_BALANCE (printed steps) | 20 / 60, on 6 accounts | **320 / 165, on 72 accounts** |

- Most of the growth is on accounts **still collecting level DD at run end**.
- That is the shape the false-leaver defect above predicts. `on_level_dd` reads a still-level account as having left
  whenever the latest issued bill is not level-paid. Such an account is then walked on its bills, and prints an overdue
  figure its page balance does not hold.
- **I cannot yet attribute it.** The arm carries two fixes, and no third arm separates them. The test is whether the
  320 still-level page steps fall to about the control's 20 on the first book carrying a corrected leaving predicate.
  That prediction is filed here, before such a book exists.

**What this means for the claim.**
- The level-at-cure half of d8264b525e is **correct on a book**: the aged-0d shape is gone, and never-level journeys
  are untouched.
- The left-level half is **not correct yet**, for two reasons:
  - true leavers still cure over a level-era remainder their own ledger does not see;
  - false leavers are dunned while still paying level.
- The fix made the gate **worse** (151 → 614). No book carrying it can be published until the leaving predicate is
  corrected.

NEXT: the leaving predicate (`on_level_dd` must not read a still-collecting account as left), then the level-era
remainder on true leavers.

## The 45 left-level holds: the page is wrong, not the desk (worker, 9 Nov 2026 ~17:00 GMT)

**Instruments.** All of these are in `/var/tmp/grade-505d-remainder/`. Each reads `/var/tmp/grade-505d/ledger.json` (the page)
and `docs/reports/run_output_505df564e3_20261109T124818Z.json` (the run).
- `trace487.py`: the page rebuild (residual.py's `build`) against every figure the desk printed.
- `window487.py`: the rebuild's events where the two figures part.
- `shapes.py`, `explain45.py`, `count_a.py`, `count_a2.py`: the census.

**Where the in-run ledger puts a failed level request's remainder.** The answer is oldest-first carry on one account
balance. It is never kept per invoice, and it is never dropped.
- The desk's `AccountLedger` holds one balance per billing account.
- A returned level collection posts no cash. Its shortfall is `level_shortfall`: requested less received, capped at the
  balance.
- Later cash is allocated by remittance, otherwise oldest first (`_post_cash` → `AccountLedger.allocate`). So the next
  money in meets the remainder first.
- Once the account has left level DD, the 505df564e3 desk reads the same oldest-first walk (`fifo_unpaid_bills`).

**SYN-2016-487, traced.**
- On 13 Oct 2017 the level collection of GBP 24 was returned. The desk opened a journey at GBP 3.07, which is the
  account's debit balance that day.
- The rebuild agrees with the desk to the penny on 13 Oct, 28 Oct and 7 Nov 2017. From 18 Jan 2018 the rebuild reads
  **GBP 39.61 more owed** than the desk on every stage date, through to Dec 2019.
- On 17 Jun 2019 the desk read 17.90 and the rebuild 57.51. On 19 Jun, after the GBP 29.70 payment, the desk read 0 and
  the rebuild 27.81. The 27.81 is that same 39.61 gap less the 11.80 credit the desk was holding.
- The 39.61 opens between 7 Nov 2017 and 18 Jan 2018. Over that window the desk took in GBP 109.76 of cash. That equals
  the household's two repayments (25.70 + 19.06) plus three of the level collections the run presented: elec 24 on
  13 Nov and 12 Dec, gas 17 on 27 Nov. The match is within the 0.02 of rounding between the run's bills and the page's
  bills.
- The page shows none of those level collections. Its settlement engine (`simulation/arrears_engine.paying_method` over
  `supplier_dd_spells`) took the household off DD after two Refer-to-Payer returns on its per-bill DD book (15 Nov and
  15 Dec 2017). From then on it prints every bill as standard credit and failed. The run's own `level_dd_collections`
  carries on presenting 24 and 17 each month until Sep 2018.

**What the page prints at run end, and why it is wrong (shape A).** `tools/generate_billing_ledger.py` (the level-return
branch, about line 983) builds the case for a returned level collection like this:
- It sets the case amount to the desk's figure for the day after the miss (`desk_overdue_on`). That figure is keyed by
  billing account, so a two-fuel account gets the same account-level figure on **each** leg. For SYN-2016-487 that is
  3.07 on 46965 and 3.07 on 47070.
- It then sets `outstanding_gbp = arrears_gbp`, without netting the repayment the case itself records. 46965's stages
  read `ARREARS_REPAID 25.70` on 17 Dec 2017, but it prints 3.07 owed for ever.
- The tell is that `credit_applied_gbp = asked - part_paid - amount - repaid` comes out **negative**, at exactly
  −arrears on every such case.

**The census.**
- All 8 accounts carry shape A. 7 of the 8 also carry shape B: the run's level schedule collects for 7 to 10 months past
  the last level payment the page shows. SYN-2016-217 does not.
- **33 of the 45** holds have nothing due and unpaid at run end except shape-A invoices.
- The other 12 also carry one ordinary on-receipt case that is real page debt:
  - PROS-2018-0016, 13762: GBP 98.30, 10 holds;
  - SYN-2016-217, 33999: GBP 5.20, 2 holds.

  Why the desk cured over those I cannot yet say. PROS-2018-0016 carries shape B, so a cash gap is the first candidate.
- **Book-wide, shape A is 178 cases, GBP 16,445.40, on 100 billing accounts** (the control reads 184, GBP 17,053.50, on
  100). It splits two ways:
  - A1, 82 cases, GBP 3,172.05: the recorded repayment is at least the case, and the page still prints it.
  - A2, 96 cases, GBP 13,273.35: the desk's cumulative shortfall is above the face the household repaid. The repayment
    is ignored there too.
- 7 billing accounts carry the same account-level figure on both legs in one month.

**Which side is wrong.**
- **On shape A, the page.** It prints as owed a case its own record shows repaid. On a dual-fuel account it prints the
  account's one shortfall twice. The desk's cure on 19 Jun 2019 is correct on the cash the desk holds.
- **On shape B, I cannot yet say.** The run says level DD went on being collected. The page's settlement engine says the
  mandate was off. One of the two records is wrong about Nov 2017 to Sep 2018. That needs its own trace of what the
  world's bank returned on those level requests, and the run json does not log their outcomes.
- So the cure is not over a debt the desk failed to see. It is over a debt the page invented, on a household the desk
  had told it was clear. That is the same "told it is cleared while the page shows it owing" defect, sitting on the
  page side.

**Does 8e73c52356's closing statement already re-date this remainder? No.**
- `left_level_asks` changes only what the desk asks and when. The desk's ledger does not carry this remainder: the
  household's repayment and the level cash met it, oldest first.
- The figure that holds these rows is the page's per-invoice case amount, written by `tools/generate_billing_ledger.py`,
  and 8e73c52356 does not touch it.

**Prediction for the first book carrying 8e73c52356 with `tools/generate_billing_ledger.py`'s level-return branch
unchanged** (filed before that book exists):
- `count_a.py` reads shape-A cases at 178 ± 18. The case opens on the desk's figure on the day of the return, and
  8e73c52356 changes only left-level journeys.
- The 14 shape-A invoices on the 8 accounts print the same outstanding amounts. For example, SYN-2016-487 is 3.07 + 3.07.
- The shape-A-only left-level holds do not read 0. I do not predict their count, because 8e73c52356 moves left-level
  cure dates.
- **Refuted if** shape A reads 0, or any of the 14 invoices prints 0, on a book with that branch unchanged.

**The fix, filed and not built.** It is built only after that book is graded, so that one book does not carry two
changes. In `tools/generate_billing_ledger.py`:
1. Net the case's own repayments and credits against the desk's figure:
   `outstanding = max(0, desk figure - repaid - credit)`.
2. Put an account-level desk figure on one leg only, not on each.

The prediction for the first book carrying it:
- A1 reads 0.
- The 33 shape-A-only holds read 0.
- A2's printed total falls by at least the sum of its recorded repayments.
- No invoice outside shape A changes its outstanding amount.

**Open, not settled here:**
- shape B: which record is right about level collections after two Refer-to-Payer returns;
- the 12 holds over a real on-receipt case.

NEXT: grade the 8e73c52356 book against the prediction above, then build the page fix.

## The leaving predicate, measured: the premise was mostly wrong, and a narrower defect is fixed (seat executor, 9 Nov 2026 ~17:30 GMT)

**The premise, re-measured before building.** The section above read the 320 still-level page steps as false
leavers. I tested that on the 505df564e3 page ledger, with that commit's own `on_level_dd`, on each breach's date
(`/var/tmp/ondd-probe/classify.py`).
- `on_level_dd` reads **level on every one of the 320**, and on every one of the 105 journey-opening rows.
- **312 of the 320 are on 63 accounts that never collect level again** after the breach. C7 is one: its final bill
  was June 2019, and it was written off on 30 Jun 2020. "Still level at end" in `overdue_breaches.py` means only
  that the last payment was a level collection, so it puts closed accounts in the still-level column.
- The other 8 are on 4 accounts that do go on collecting level.
- **Correction, beside the claim above:** the 320 are not the false-leaver shape. The prediction filed there (320
  falls to about 20 on the first book with a corrected predicate) **I now expect to FAIL**. It stays as filed.

**What the 320 are, as far as measured.** The desk's in-run figure exceeds the page balance on closed accounts. On
C7 it printed GBP 66.67 overdue on 16 Jul 2019, against a page balance of GBP 48.55. A desk replay over the page
ledger (`/var/tmp/ondd-probe/replay_bal.py`) opens **0** journeys over the balance, under 505df564e3's code and
under HEAD's. So the breach lives in how the run's own ledger differs from the page on a closing account, and not in
the predicate. **Mechanism not established.** The next measurement is C7's run ledger against its page on 16 Jul
2019. The 505df564e3 book also does not carry 8e73c52356 (the closing statement), so the next book moves these
rows for that reason too.

**The defect that is real, and is fixed here.** A bill that asked nothing read as the leg having left. Two kinds of
bill ask nothing:
- an EBSS-covered bill, which the run posts net of its credit, at GBP 0;
- a month whose level amount is GBP 0, which presents nothing and records no request.

On the netted page ledger (`/var/tmp/ondd-probe/probe_net.py`), 505df564e3's `on_level_dd` reads **6 accounts that
go on collecting level as having left, on 359 account-days**. The build reads **0 and 0**.
- K8: `payments_and_direct_debit_2026-10-25.md`, "A month the level schedule asks nothing of is not a departure".
- The change: `arrears_engine._shows_how_it_pays` and `LevelSchedule.nil_refs`. The triad also records a nil ask
  as asked nothing (`note_bill_asked`).
- The controls are `tests/company/billing/test_a_level_dd_month_that_asks_nothing_is_not_read_as_leaving.py` (the
  partition: a nil month reads level, and a billed month off the schedule still reads left) and
  `tests/simulation/test_a_level_dd_household_is_dunned_on_its_schedule_not_its_bills.py::test_a_level_month_of_nothing_is_not_read_as_leaving_level_dd`
  (end to end through the triad).
- Mutations that fire: no skip, which fails all three; no triad note, which fails the triad test.
- One equivalence: the GBP 0 face check. A GBP 0 bill's ask is its face, so `level_schedule_of` already puts it in
  `nil_refs`. The check was deleted.

**The world side, named and not changed.** The world presents no level collection in an EBSS month for a level
account. Published practice kept collecting, refunded, or lowered the DD (`energy_bills_support_scheme_delivery.md`,
GAP "for direct debit, the world nets the credit"). That GAP is already filed, and nothing new is filed here.

NEXT: grade a book carrying this change and 8e73c52356 on the same readers. Then C7's run ledger against its page on
16 Jul 2019, the closing-account overdue that exceeds the balance.

**The book that grades it (launched 9 Nov 2026 16:07 GMT, no output read).**
- **The run.** `launch_long_job` job `book-4dee9854a4`, out of loop, in the locked worktree
  `/var/tmp/book-wt-4dee9854a4`. The shared tree's uncommitted W3_3 bytes still defer `sim_runner`. The book is at
  origin 4dee9854a4, which carries 3feea0ac3 (this fix) and 8e73c52356 (the closing statement). The import
  closure is clean (`paths: []`). Its run json path is in `/var/tmp/grade-ondd-scripts/RUN_PATH`.
- **The grade.** The unit `grade-chain-book-4dee9854a4` waits for the run, then runs `/var/tmp/grade-ondd-scripts/after_run.sh`.
  Those are the 505d readers, plus `overdue_breaches.py`, `classify.py` and `probe_net.py`. The control is the
  505df564e3 ledger. The chain writes `ALLDONE` or `NO_DONE` in `/var/tmp/grade-ondd/`.
- **Predictions, filed above before any output:**
  - `probe_net` reads 0 still-collecting accounts as left.
  - `classify` shows no breach on a leg that goes on collecting level while reading as left.
  - The never-level journeys are identical, unless 8e73c52356 moved one through company-wide cash, which is the
    first cause to rule out.
  - The 320 still-level page rows do **not** fall to about 20.
  - The total overdue movement **cannot be attributed between the two commits**, because this book carries both.

**The same book grades the shape-A prediction (worker, 9 Nov 2026 ~16:20 GMT).** book-4dee9854a4 carries 8e73c52356,
and `tools/generate_billing_ledger.py` is unchanged from 505df564e3. So it is the book named in "Prediction for the first book carrying
8e73c52356 with the level-return branch unchanged" above. Grade it with `/var/tmp/grade-505d-remainder/count_a.py`
on that book's ledger: shape A at 178 ± 18, SYN-2016-487 still at 3.07 + 3.07. The page fix waits for that grade.

## C7 on 16 Jul 2019: the desk's ledger, not its view, is GBP 18.12 heavier than the page (seat executor, 9 Nov 2026 ~16:45 GMT)

Measured on the 505df564e3 book: `run_output_505df564e3_20261109T124818Z.json` against `/var/tmp/grade-505d/ledger.json`.
C7 is a single-fuel electricity account. It has no `C7g`.

**What agrees.**
- **Bills:** the run has 42, totalling GBP 4,915.22. The page has the same 42, totalling 4,915.27. Every difference is a
  rounding difference of 0.01.
- **Cash:** the run's `level_dd_collections` and the page's payments are the same 42 (date, amount) pairs, GBP 4,866.72,
  with no extras on either side.
- **Closing balance:** the run's `closing_balances` reads 48.55, the same as the page.

**What does not.**
- The desk printed GBP 66.67 overdue at every stage, from 16 Jul 2019 to the write-off on 30 Jun 2020. It wrote off
  **66.67**.
- `_write_off_if_closed` posts `closed_balance_due_for_write_off(ledger, on)`, which is the desk ledger's own balance.
  So the desk's `AccountLedger` held 66.67 owed where the page and `closing_balances` hold 48.55.
- That is a real divergence of GBP 18.12 between the two records. It is not an artefact of the ageing view.
- 66.67 is exactly the page's running balance between the 5 Jun 2019 bill and the 12 Jun collection of GBP 108
  (48.55 + 108 − 89.88). That may be a coincidence, so I record it as a lead and not as a mechanism.
- **The opening day rules out one reading of that lead.** `days_overdue = 1` on 16 Jul puts the unmet ask at 15 Jul,
  the final bill's due date. Under `level_shortfall`, every level request was met, so the desk did receive the 12 Jun
  cash. A ledger missing the 12 Jun payment would have aged the shortfall from 12 Jun, at 34 days.
- What fits both figures: the desk ledger carries GBP 18.12 more debit, or less credit, than the page. The extra is
  not in a `BILL_DEBIT`, because `other_asks` reads only bills, and the final bill alone (89.88) bounds the shortfall
  above 66.67.
- **Mechanism not established.** The run json carries no desk ledger events, so this book cannot name the GBP 18.12.
  The next instrument is a dump of C7's in-run `ledger_book.ledger("C7").events()` at the end of the run, or a
  replay of C7 alone.

**Why it matters beyond C7.** If this shape is the 63 closed accounts behind the 312 still-level rows, then:
- the desk writes off more than the page says is owed;
- bad debt is overstated by the sum of these gaps, if the P&L reads the desk's write-off.

I cannot yet say whether it does. That is the question after the mechanism.

**Prediction for book-4dee9854a4** (filed before any of its output was read, at 16:45 GMT with the run still going):
- C7's journey opens on 16 Jul 2019 at GBP 66.67 and writes off 66.67.
- Neither 3feea0ac3 (the nil-ask predicate) nor 8e73c52356 (the closing statement, which applies to left-level
  journeys) touches how the desk's ledger is posted, and C7 reads level throughout.
- **Refuted if** C7's write-off reads 48.55, or any figure other than 66.67.

## book-4dee9854a4, graded: the nil-ask predicate holds, shape A holds, and C7's opening moved but its write-off did not (seat executor, 9 Nov 2026 ~18:05 GMT)

**What was measured.**
- **The run:** `run_output_4dee9854a4_20261109T160658Z.json`, at origin 4dee9854a4. It carries 3feea0ac3 and 8e73c52356.
- **The readers:** `/var/tmp/grade-ondd/` (ALLDONE 17:56), with the 505df564e3 book as the control.
- **The predictions:** filed in the two sections above before any output existed. The C7 prediction landed as
  e24cf12d4 at 16:4x, with the run still going.

| Prediction | Result | Graded |
|---|---|---|
| `probe_net` reads 0 still-collecting accounts as left | `{'accounts': 394}`. No `with_false_days` key, so 0 accounts and 0 account-days (control 6 and 359) | **held** |
| `classify` shows no breach on a leg that goes on collecting level while reading as left | no "reads LEFT" class in either invariant. Every row reads level | **held** |
| The never-level journeys are identical | 643 against 643, identical True | **held** |
| The 320 still-level page rows do not fall to about 20 | **396** (control 320) | **held**. The fix was never going to move them, as the "leaving predicate, measured" section says |
| The total overdue movement cannot be attributed between the two commits | BALANCE 129, of which 106 still level and 23 left (control 129: 105 and 24). PAGE_BALANCE 509, of which 396 and 113 (control 485: 320 and 165) | **stands**. The book carries both commits |
| Shape A at 178 ± 18 | **182**, GBP 16,826.18, on 100 accounts, 7 stamped on both legs (control 178, 16,445.40, 100, 7) | **held** |
| SYN-2016-487 still prints 3.07 + 3.07 | 46965 3.07, 47070 3.07 | **held** |
| C7 writes off 66.67 | write-off on 30 Jun 2020, GBP 66.67. `closing_balances` still 48.55 | **held** |
| C7 opens on 16 Jul 2019 at 66.67 | it opens on **30 Jul 2019**, at 66.67 | **REFUTED on the date** |

**The refuted half, read and not explained away.**
- I predicted that neither commit touches C7, "because C7 reads level throughout". The opening moved 14 days, so
  something in this book changed how the desk walks C7.
- 30 Jul is the day after 1 Jul + 28. That is the final bill's date plus `CLOSING_STATEMENT_TERM_DAYS`, the
  shape 8e73c52356 introduced.
- The likeliest reading: the desk now reads C7's final bill, which no level collection paid, as a leaving, and
  dates the miss from the closing statement.
- **I cannot yet say whether 3feea0ac3 or 8e73c52356 caused it.** Both are in this book. The closing-statement term
  is the evidence for 8e73c52356, and it is not a one-variable run.
- What did not move is the GBP 18.12 between the desk ledger and the page. That is the defect that matters, because
  it is the amount written off.

**What this closes, and what it hands on.**
- The nil-ask leaving predicate is graded. Its fix holds on a real book, with 0 false leavers.
- The shape-A page fix filed in "The 45 left-level holds" was waiting only for this grade. It is now unblocked, and
  its own prediction (A1 reads 0, the 33 shape-A-only holds read 0) is filed in that section.
- The 396 still-level page rows remain the C7 shape: closed accounts whose desk ledger is heavier than the page. Their
  mechanism needs C7's in-run `ledger_book.ledger("C7").events()`, which no run json carries.

NEXT: build the shape-A page fix in tools/generate_billing_ledger.py, then name C7's GBP 18.12 from an in-run ledger dump.

## The shape-A page fix, built and graded on the 4dee9854a4 book (seat executor, 9 Nov 2026 ~19:30 GMT)

**What changed.** The level-return branch of `tools/generate_billing_ledger.py`, as filed in "The 45 left-level holds":
1. A case now owes `max(0, desk figure - repaid - credit)`, counting this case's own repayments and credits.
   `credit_applied_gbp` on a level case is now only the credit the repayment did not cover. It is never negative.
2. The desk's figure belongs to the account, so the two legs share it within one journey. A leg's case carries only
   what the journey's figure rose by over the other leg's case.

The control is `tests/tools/test_a_level_return_case_is_owed_net_of_its_own_repayment_and_on_one_leg.py`. Its partition
leg asserts three outcomes: a level case still owed, a level case repaid, and no case opened. Mutations that fire:
- HEAD's branch: 4 of 5 tests fail;
- no netting: 2 fail;
- no one-leg rule: 3 fail;
- HEAD's credit formula: 1 fails.

The ledger tests (38 files, 378 passed) are green.

**The grade.** I re-generated the 4dee9854a4 book's page with the fix (`/var/tmp/shapea-arm/`, `grade.py`). The
control is `/var/tmp/grade-ondd/ledger.json`. One book and one change, so the movement is attributable.

| Prediction (filed before the build) | Result | Graded |
|---|---|---|
| A1 reads 0 | 82 cases (GBP 3,172.11) now print 0 | **held** |
| The 33 shape-A-only holds read 0 | left-level holds over an unpaid invoice fall from 46 on 9 accounts to **18 on 6**. The 12 named on-receipt holds remain: PROS-2018-0016 13762 (10 holds) and SYN-2016-217g 33999 (2 holds). That leaves 6 on 4 accounts (below) | **mostly held, 6 short** |
| A2's printed total falls by at least its recorded repayments | GBP 13,654.07 falls to 6,811.32. The fall is 6,842.75, against repayments of 5,025.47 | **held** |
| No invoice outside shape A changes its outstanding amount | **8 move**, by GBP −245.16 | **FELL** |
| SYN-2016-487 | 46965 and 47070 both print 0 | held |

- Total outstanding on the page falls from GBP 27,646.75 to 17,386.73.
- count_a.py now reads 0, but that is by construction: its tell, a negative `credit_applied`, can no longer occur. The
  reading is not evidence that shape A has gone. The rows above are the evidence.

**Why the "outside shape A" leg fell.** It is the same defect, outside count_a's tell. All 8 are level-return cases
whose bill face was large enough to keep the old `credit_applied` positive, so the tell missed them. Example:
PROS-2019-0261g 16339 records repaid 53.48 against a case of 53.48, and it printed 53.48 owed. None of the 8 moved
because of the one-leg rule. That rule removed 16 duplicate cases, all on gas legs and all inside shape A. So the
filed partition, which defined shape A through the tell, was narrower than the defect.

**The residual, not fixed here: a case can exceed its own bill.** Inside one journey, the desk's figure is the running
total, so it can include shortfalls from earlier months. A bill repaid in full can therefore still print what
earlier months left unpaid. PROS-2019-0246 16165 has face 60.48, repaid 60.48, and still prints 269.94.
- On the arm, **84 level cases on 58 accounts print GBP 5,871.65 more than their own bill's remainder** (face less
  repaid and credit).
- These cases are the 6 left-level holds above:
  - PROS-2019-0246 (3);
  - SYN-2016-253g (1);
  - SYN-2016-360 (1);
  - SYN-2016-536 (1).
- The obvious fix caps a level case at its bill's remainder. That loses debt only where an earlier miss in the same
  journey opened no case of its own, and I have not measured how often that happens. So it is its own change, on
  its own book.
- **Prediction for it, filed now:**
  - the 84 cases read 0 above remainder;
  - the 6 residual holds read 0;
  - the 12 on-receipt holds are unchanged;
  - the page's total outstanding falls by no more than GBP 5,871.65.

**Also moved, and not explained here.** "Every invoice paid, page in debit at run end" in compose.txt rises from 193
to 209 accounts. That is expected in kind: the per-invoice figures no longer carry the cases that had stood in for
the balance. It means the page's account balance and its invoices still disagree on those 16 accounts. That is
the C7 class (a desk ledger heavier than the page), now visible on 16 more accounts. It is not a new defect.

NEXT: cap a level case at its own bill's remainder, after measuring how often an earlier in-journey miss opened no case.

## C7's GBP 18.12, named from the code: the leaving month's level collection is on the page and never reached the desk (seat executor, 9 Nov 2026 ~21:00 GMT)

**The mechanism, read from the code and checked on C7's own figures.**
- `simulation/run_phase2b.py::_post_month_bill` calls `_level_in_loop.collect(cid, month, left)` for every level leg.
  With `left=True` (the open month of a leg that left, posted at run end), `InLoopLevelCollection.collect` still
  appends the month's level row to `collected`, which becomes `level_dd_collections`, which the page collects.
- The same call hands the triad `level_collection=None if left else _level_row`. So the desk is presented the final
  bill's face on the bill path, and never the level row.
- C7, final month June 2019: the page collects the level GBP 108 on 12 Jun; the desk is presented the final bill's
  face, GBP 89.88, which the `dd_collection_book` records as collected. 108 − 89.88 = **18.12**, the whole gap.
- It also explains the opening date, which the earlier "missing 12 Jun collection" lead could not: the desk received
  every level request it was shown, and its unmet figure is aged from the final bill's due date.
- So the earlier claim "the extra is not in a `BILL_DEBIT`" stands; the extra is **less credit** in the desk:
  89.88 of cash where the page has 108.

**Which record is right.** The household was supplied, and on level DD, through June. Published practice takes
that month's level collection and then states the closing balance on the final bill
(`payments_and_direct_debit_2026-10-25.md`). The page's 12 Jun 108 is the right one. The desk's record replaces it
with the final bill's face, which is neither the level amount nor the closing balance. The final bill's own
settlement (the closing balance, 48.55 for C7) is then not presented to anyone: that is a second, separate gap.

**Prediction for the population, filed before measuring it** (book `run_output_4dee9854a4_20261109T160658Z.json`):
- For every collections journey that ends in a write-off on an account that closed, and whose last billed month has
  a row in `level_dd_collections`, the desk's written-off figure minus the page's `closing_balances` equals that
  row's level amount minus the final month's bill face, to within GBP 0.05, on at least 90% of such accounts.
- Most of the 63 closed accounts behind the 312 still-level page rows are in that set.
- **Refuted if** fewer than 90% match, or the matched gap is not where the 312 rows sit.

**Graded (same evening, on the 4dee9854a4 book and its page `/var/tmp/grade-ondd/ledger.json`; script
`/var/tmp/c7-1812/measure2.py`, rows and classes beside it).** What each figure counts: an *account* is a billing
account (both legs); *write-off* is the desk's `write_off` stage amount on its page journey (all 152 by rule
`closed_account_unpaid_a_year_after_its_final_bill`); *page* is minus the sum of the legs' page `balance_gbp`;
*gap* is write-off − page.

| Class | Accounts | Gap sum, GBP |
|---|---|---|
| Final month on level, gap = level row − final face (**the C7 shape**) | 64 | +929.97 (40 heavier by +1,548.92; 24 lighter) |
| Final month on level, gap unexplained | 47 | −5,040.75 |
| C7 shape plus exactly one −400 | 1 | −323.57 |
| Final month not on level, gap exactly −400 per account | 3 | −1,200.00 |
| Final month not on level, gap unexplained | 17 | −6,642.78 |
| Desk and page agree | 20 | −0.04 |

- **The prediction FAILED as filed:** 64 of the 114 level-final-month accounts match (56%, not ≥90%). The
  mechanism is real and exact on 64 accounts, C7 among them, but it is not the only divergence on closed accounts.
- **The worry in the drawn item is wrong in direction.** Across the 152 written-off accounts the desk wrote off
  GBP 25,580.62 against page balances of GBP 37,857.79. The C7 shape overstates write-offs by GBP 1,548.92 on 40
  accounts. A larger, unexplained class (64 accounts, −11,683.53) has the desk writing off much less than the page
  says is owed. Several gaps are exactly −400.00, the EBSS credit: the page and the desk disagree on whether the
  scheme's credit reached a closed account.
- **Does the P&L read it?** `total_bad_debt_gbp` (9,493.66) is the world's `bad_debt_gbp` on settlement records and
  does not read the desk. The desk's write-offs (`write_off_closed_balances`) feed the company's provision stocks
  (`_company_provision_by_year_end`), so the IFRS 9 charge reads the desk's ledger. Which way the gap moves that
  charge I cannot yet say: the desk is lighter in total, and the provision is a stock read, not a sum of write-offs.
- I did not check whether the 40 heavier accounts are the ones behind the 396 still-level page rows. That was the
  second leg of the prediction, and it stays ungraded.

**The fix, filed and not built (world side, its own book).** In `_post_month_bill`, either the leaving month's level
row reaches the triad when its collection date falls inside supply (what practice does), with the final bill then
asking the closing balance, or `collect(..., left=True)` stops recording a row the triad never presents. The first is
right and touches the mover/churn final-bill exit model (`mover_final_bill_outcome` runs only when `level is None`),
so it needs the K8 page amended first. The second is a one-line consistency fix that makes the page agree with a
desk that is itself wrong. Recommendation: the first.

NEXT: name the −400 and the 64 accounts where the desk writes off less than the page (the larger class), before the
C7-shape fix, because it is twelve times the size.

## The consistency fix lands, and its prediction is filed before any book carries it (worker, 9 Nov 2026 ~22:30 GMT)

**What lands.** These are the bytes written at 18:30 in the shared tree, unchanged. The schedule holds only what the world
presented: `LivePaymentTriad.last_level_presented`, `InLoopLevelCollection.withdraw`, and the `withdraw` call after
`record_period` in `run_phase2b._post_month_bill`. The K8 page is `payments_and_direct_debit_2026-10-25.md`, "What is
owed" and "One record of what was collected". The control is
`tests/simulation/test_the_level_schedule_holds_only_what_the_world_presented.py`. Two mutations fire. With `withdraw`
made a no-op, both tests fail. With the triad reporting the row it was handed, the partition test fails.

**Why this and not the 21:00 recommendation first.** The 21:00 section above recommends the world-side fix: present the
leaving month's level row, then ask the closing balance. It calls this one "a page that agrees with a desk that is itself
wrong". **Correction, beside that claim:** the desk is not wrong about the cash. It records what the world presented,
which was GBP 89.88 on 15 Jul. The fidelity defect is in the world. It skips a collection a real supplier would take.
The page printed GBP 108 that nobody collected. This fix makes the page show the world's cash. The world-side fix is
still owed, and it is still the larger one. It needs its own K8 amendment ("What this does not settle" on the page).

**Prediction for the first book carrying this commit, filed before any of its output exists.**
- C7: `closing_balances`, the page balance and the desk's write-off all read **66.67** to the penny.
- **The 396 still-level PAGE_BALANCE rows fall to about 94, between 80 and 110. They do not fall below 40.**
  - I split the 4dee9854a4 rows by account class (`/var/tmp/c7-1812/classes.json` and `rows.json`).
  - 300 rows sit on 39 accounts of the C7 shape, where the desk is heavier, plus 2 on the one C7+EBSS account. Those rows close.
  - 84 rows sit on 12 accounts in the "level, unexplained" class, and 10 sit on 2 accounts that were not written off.
    This fix does not touch either group.
  - **Correction, beside the 19:30 prediction ("below 40"):** that prediction was filed before the class split
    existed, and the split refutes it as a mechanism.
- The 24 lighter C7-shape accounts open no new PAGE_BALANCE row. The page falls to the desk's figure, and the desk's
  overdue cannot exceed its own balance.
- **Refuted if** C7 still closes on 48.55 on the page, the still-level count stays above 110, or it falls below 80.
  A fall below 80 would mean the fix also moved a class I read as untouched.

NEXT: grade the first book carrying this commit against the prediction above, then the K8 amendment for the leaver's closing-balance collection.

## The first book carrying all three overdue fixes: pre-registration, filed before it starts (worker, 10 Nov 2026 ~00:05 GMT)

**The book.** Origin 78f82e4242, run from the clean locked worktree `/var/tmp/book-wt-78f82e4242`. Its import closure
reads `paths: []`. sim-runner is still deferring on the shared tree's non-origin bytes, so this book runs outside the loop,
as 4dee9854a4 did. It carries four billing changes since 4dee9854a4, so **no movement below can be attributed to any one
of them**:
- dea1c34fdf (C7, world): the schedule holds only what the world presented.
- 50030bb606 and 2353f8b001 (shape A and its cap, page): a level-return case owes what its own record has not met, on
  one leg and capped at its bill.
- 19eebf6c3e (page and statement): the ledger balance is the page's.
- 78f82e4242 (the suite): INV_OVERDUE_WITHIN_BALANCE reads a level leg on its schedule.

**The control** is the 4dee9854a4 book, graded at `/var/tmp/grade-ondd/` on the readers then in force. The grade uses
the same readers (`/var/tmp/grade-ondd-scripts/`), run from the book's worktree, so the domain-invariant rows are
78f82e4242's.

| Row | 4dee9854a4 | Prediction for 78f82e4242 | Refuted if |
|---|---:|---|---|
| INV_OVERDUE_WITHIN_BALANCE (new reader) | 5 (replay) | **0 to 10**. The 5 are scheme-end residues on level legs, and C7's world change touches leavers' final months, so it may move them either way | above 10 |
| INV_OVERDUE_WITHIN_PAGE_BALANCE, still-level steps | 396 | **80 to 110**, as filed at ~22:30 ("The consistency fix lands") | above 110 or below 80 |
| INV_OVERDUE_WITHIN_PAGE_BALANCE, left-level steps | 113 | **at most 113**. The shape-A cap removes case figures above a bill's remainder, which can only lower what the page prints as owed past due. I cannot say by how much | above 125 |
| INV_OVERDUE_WITHIN_PAGE_BALANCE, total | 509 | **80 to 225** | outside that range |
| Shape A: level cases printing above their own bill's remainder | 84 (on the shape-A arm) | **0** (pennies on non-level invoices allowed, as in the cap grade: under GBP 1 in total) | any level case above its remainder |
| Shape A: the 12 on-receipt left-level holds | 12 | **12**, the same invoices | any change |
| C7: `closing_balances`, page balance, desk write-off | 48.55 / 48.55 / 66.67 | **all 66.67** | the page still closes on 48.55 |
| Every other suite row | as in `/var/tmp/grade-ondd/grade.txt` | **no new unexcepted row**; the excepted rows keep their exception | any third unexcepted row |
| The gate | refused, 638 unexcepted on 2 rows | **refused**: PAGE_BALANCE is predicted at 80 or more, and no filed change claims to close it | the gate passes |

What a pass would mean, and what I expect instead: the gate is refused on INV_OVERDUE_WITHIN_PAGE_BALANCE alone. The
remaining still-level steps are the "level, unexplained" closed accounts (84 rows on 12) and the 2 accounts not written
off (10 rows). Their owner is the write-off-reaches-the-page item (`page-balance-omits-credit-on-closed-accounts`, the
EBSS finding's "Open" section). If that is what the grade shows, done is naming those classes with that owner, not a pass.

**Launched after the table above was written** (the file as it stood then hashed sha256 `21573c92…f024f466f` at
00:02:40Z; the run started at 00:02:48Z).
- **The run.** `launch_long_job` job `book-78f82e4242`, unit `longjob-book-78f82e4242`, in the locked worktree
  `/var/tmp/book-wt-78f82e4242`. Output: `docs/reports/run_output_78f82e4242_20261110T000247Z.json`, promoted by hand
  if it passes. Log: `/var/tmp/longjob-book-78f82e4242.log`.
- **The grade.** Unit `longjob-grade-chain-book-78f82e4242` waits for the run, then runs
  `/var/tmp/grade-78f-scripts/after_run.sh` (the 4dee readers, control `/var/tmp/grade-ondd/`). It writes `ALLDONE` or
  `NO_DONE` in `/var/tmp/grade-78f/`. Whoever reads it grades the table above, held or fell beside each row.

## Book 78f82e4242, graded against the table above (worker, 10 Nov 2026 ~03:00 GMT)

The run finished at 01:46Z, and the grade chain wrote `ALLDONE` at 01:49Z. The data is in `/var/tmp/grade-78f/`
(`grade.txt`, `overdue_breaches.txt`, `arm_overdue.json`, `split.txt`). The control is `/var/tmp/grade-ondd/`. Every
count below comes from the readers in force at 78f82e4242, the same ones the table was filed against.

| Row | Predicted | Measured | |
|---|---|---:|---|
| INV_OVERDUE_WITHIN_BALANCE | 0 to 10 | **60**, all on left-level legs | **FELL** |
| PAGE_BALANCE, still-level steps | 80 to 110 | **2** (SYN-2016-291, "collects level after") | **FELL** (below 80) |
| PAGE_BALANCE, left-level steps | at most 113 (refuted above 125) | **135** | **FELL** |
| PAGE_BALANCE, total | 80 to 225 | **137** on 8 accounts | held on the count only, see below |
| Shape A: level cases above their remainder | 0 | **0**. The 28 non-level penny roundings total GBP 0.29 | **HELD** |
| Shape A: the 12 on-receipt holds | 12 | **12**, the same invoices (P2 in 5cfbea2477) | **HELD** |
| C7: `closing_balances` / page / desk write-off | all 66.67 | **66.67 / 66.67 / 66.67** (control 48.55 / 48.55 / 66.67) | **HELD** |
| Any other suite row | no new unexcepted row | the same 8 excepted rows with the same exceptions; no third unexcepted row | **HELD** |
| The gate | refused | **refused: 197 unexcepted on 2 rows** (control 638) | **HELD** |

**The total held only by accident.** It is not evidence. Its two legs moved in opposite directions to the
prediction, and the errors cancelled:
- The still-level class fell to 2. The refutation clause said a fall below 80 would mean "the fix also moved a
  class I read as untouched", and it did. The 84 "level, unexplained" rows on 12 accounts and the 10 rows on the 2
  accounts that were not written off closed along with the C7 shape. This book carries four changes, so **I cannot
  yet say which of them closed those rows.**
- The left-level class rose from 113 to 135. That is the opposite of "can only lower". The cap does not raise it,
  so the rise comes from another change in the book: C7's schedule hand-back moves legs from still-level to
  left-level. That is a hypothesis, not a measurement.

**INV_OVERDUE_WITHIN_BALANCE fell, and its cause is the row's reading.** That was the stated meaning of a miss.
189b32460e has since fixed the reader: the debit a leaver owes the scheme counts once the closing statement is due.
That fix takes this book from 60 to 2 (SYN-2016-496 and SYN-2016-007, both desk residues). 703edeb89b changes the
desk for both of them, and that change needs a new book to be graded.

**Breach classes still open on this book, with count and owner:**
- **INV_OVERDUE_WITHIN_PAGE_BALANCE, left-level steps: 135.** Owner: the desk-write-off-reaches-the-page work
  (`SEAT_FINDING_THE_DESKS_WRITE_OFF_OF_A_CLOSED_ACCOUNT_NEVER_REACHED_THE_PAGE_2026-11-10.md`, P5). They sit on 7
  accounts: SYN-2016-021 (58), SYN-2016-549 (44), PROS-2017-0045 (8), SYN-2016-123 (8), SYN-2016-611 (8),
  PROS-2021-0117 (7) and SYN-2016-581 (2). Its graded residue is the desk writing off less than the page shows.
  That landed as b512dec267 after this book was cut, so the count needs a re-grade on a later book or a page
  regeneration.
- **INV_OVERDUE_WITHIN_PAGE_BALANCE, still-level steps: 2.** SYN-2016-291 collects level after the step. No owner
  has been named yet. It is the only row of its class left.
- **INV_OVERDUE_WITHIN_BALANCE: 2** on origin's reader (60 on the reader graded here). Owner: the desk's
  level-leaver dunning (703edeb89b), which needs a new book to grade.

**Early publish this week: MISSED.** The director said yes to an early publish on 8 Nov, and that yes needed a
passing book. 78f82e4242 is refused on two rows with 197 unexcepted breaches. Nothing is offered to the publisher,
and the tenth cold read's embargo stays in place. The next book that can pass must carry b512dec267, 189b32460e and
703edeb89b together. Even then, it has to clear 135 page-balance steps that no landed change has yet been measured
to close.

NEXT: run the next book from origin at or after 703edeb89b, off a clean worktree, and grade it on origin's readers.
Predict the left-level page-balance count before the run starts.

## A leaver's scheme debit no document asks for: measured, and the cure count pre-registered before any build (worker, 10 Nov 2026 ~03:20 GMT)

*Drawn as `a-level-dd-leavers-schedule-shortfall-is-billed`. The id it retires,
`a-true-level-dd-leaver-cures-over-a-level-era-remainder-its-ledger-does-not-see`, is disposed as premise-spent by
50030bb606: its question was answered by "The 45 left-level holds: the page is wrong" and the shape-A fix that 78f82e4242
graded. K8 first: "What is owed" on `payments_and_direct_debit_2026-10-25.md` now says what happens to a debit at the end
of a scheme that is not rolled into a new one. It is still owed, it is not debt until asked once in writing, and a missed
instalment is made good only by cash that meets it.*

**What each figure counts.**
- A *leg* is one `customer_id` on the page, one fuel of a billing account.
- A leg has *left level* when its last payment that moved money was not a level collection and an earlier one was.
  A row that moved no money is not a payment, for example an EBSS-covered bill asking GBP 0.
- *Owed* is the page balance when it is a debit. *Asked* is the sum of the leg's invoices' `outstanding_gbp`. *Unasked*
  is owed less asked, when above GBP 0.01.
- A leg is *live* unless its last bill period ends more than 45 days before the book date.

**The instrument.** `/var/tmp/lvl-shortfall/census2.py` measures the debit. The cure count uses `readers/split.py` and
`readers/compose.py`, which are the grade-78f readers with one fix each.
- **The split.py fix the drawn item asked for.** split.py took the latest payment row as the leg's payment method, so an
  EBSS-covered row that moved no money read as "not level". So did compose.py's `last_level`. Both now skip rows with
  `amount_gbp` of 0. On every ledger below, the fix moves one hold from "left level" to "level at cure" (143 becomes 144)
  and changes no count.
- **The pages.** Both books' pages are regenerated with origin 7f69f78825's generator (`/var/tmp/lvl-shortfall/regen-*`),
  so b512dec267 (the desk's write-off reaches the page) is in both. The closed-leaver class is that work's, not this one's.

| Book (page at 7f69f78825) | Live leaver legs with unasked debit | GBP | Closed leaver legs | GBP | Cures held over a debt (split) | compose: left level, invoice unpaid / none unpaid |
|---|---:|---:|---:|---:|---:|---|
| 4dee9854a4 | 21 | 6,859.12 | 7 | 309.27 | **193** on 92 accounts | 12 / 36 |
| 78f82e4242 | 22 | 6,945.89 | 147 | 10,681.09 | **193** on 92 accounts | 12 / 36 |

- The cure count is 193 on both books, on the pages as graded and as regenerated. It was 347 on the 9d7dcfc19c control.
  The reader counts the desk's own cures (834 on each book), and these books share them at this grain.
- **SYN-2016-536g, the drawn example, traced.** Its page balance owes GBP 178.12 at book end. Three open cases ask
  65.98 of it: 50041's 19.88, 50084's 30.29 and 50086's 15.81. **112.14 is asked by nothing.** That is the gas leg's
  debit on 13 Mar 2020, the day of its last level collection, less the 13.69 repaid on 50026 in 2019.
- **Correction, beside the drawn item.** The item says 50035 and 50036 "print ARREARS_REPAID with no cash". They are
  real cash. The world's payment truth posts `repayment` rows (`simulation/arrears_engine`, outcome `repayment`): GBP
  16.39 on 10 Sep 2020, then 6.99 and 16.39 on 12 Mar 2022. The page balance counts them as `arrears_resolved`. What is
  missing is a payment row for them on the page, not the money. They repaid the two bills' faces (23.38 and 16.39), not
  the 26.83 instalments the bills stood behind.
- **The desk's side, on 536.** The desk dunned an account-level figure of about GBP 100 to 130 from Apr 2020. It cured on
  16 Feb 2023, when the page's gas leg owed 132.02, including 50041, which had been failed since Nov 2020. The electricity
  leg was still on level DD, so `on_level_dd` kept the whole account on the schedule. **Why `level_shortfall` read
  nothing that day I cannot yet say.** A desk replay over the regenerated page
  (`/var/tmp/lvl-shortfall/replay_one.py`) reads GBP 169.49 short on that day, so it does not reproduce the cure. That
  replay posts no EBSS credit. Its balance is 508.97 against the page's 243, so it is not faithful past 2022, the
  caveat the 9 Nov replay already carried. There are two candidates, neither one printed:
  - the run's desk counts the EBSS credit as cash received against requests the schedule stopped making in EBSS months;
  - the gas leg's later on-receipt cash meets the schedule's asks.

  The next instrument is the in-run desk's `level_shortfall` on that day. No run json carries it.
- **4 of the 22 live legs** are on accounts whose other leg is still on level DD: PROS-2020-0223g, SYN-2016-048,
  SYN-2016-525g and SYN-2016-536g, GBP 1,272.88 in all. They carry **20 of the 193 holds**. The other 18 legs are on
  accounts where every leg has left level DD. There the desk already asks a closing statement (`left_level_asks`), and
  the page prints none.

**The build this pre-registers, in two parts, each graded alone.**
- **(P) The page asks what the desk asks.** `tools/generate_billing_ledger.py` prints a closing statement for each live
  leg that leaves level DD in debit. The statement asks that leg's debit on the day of its last level collection, net of
  its open cases, due 28 days later. Its outstanding figure is what later cash and credit have not met.
- **(D) The desk asks it on a mixed account.** When one leg leaves and another stays on level DD, the leaving leg's
  statement becomes an ask that `level_shortfall` counts, dated from that leg's own leaving. This also closes 703edeb89b's
  GAP on SYN-2016-345, the leg's own leaving date.

**Predictions, filed before either part is built.**

(P), on the two pages regenerated with (P) alone (one variable):
- Live leaver legs with unasked debit read **at most 1 leg and GBP 5** on each book, against 21 and 22 now.
- Closed leaver legs are **unchanged**: 7 / 309.27 and 147 / 10,681.09.
- Cures held over a debt stay at **193** on each book. The reader counts the desk's cures, and a page change cannot move
  them.
- compose's "left level DD, an invoice due by the cure is still unpaid" **rises from 12 to between 12 and 33**. On the 78f
  page, 21 left-level holds on live-leaver accounts fall after their leg's statement would be due.
- Every invoice that is not a statement keeps its outstanding figure to the penny.
- **Refuted if** any of these misses.

(D), on the first book carrying it:
- The 20 holds on the 4 mixed accounts fall to **at most 4**.
- The total falls from 193 to **between 173 and 180**.
- Cure dates on accounts with no level-DD payment are **byte-identical**.
- **Refuted if** the total rises, or any never-level cure moves.

NEXT: build (P) in `tools/generate_billing_ledger.py`, then grade it on both regenerated pages against the table above.

## (P) built and graded: the page now asks a leaver's scheme debit, and three of five legs fell (worker, 10 Nov 2026 ~03:15 GMT)

**What changed.** `tools/generate_billing_ledger.leaver_closing_statement` adds a `closing_statement` record to each leg
that leaves level DD in debit.
- The leg leaves on the issue date of its first bill after its last level-collected one. That is the day `on_level_dd`
  reads it as gone.
- The statement asks the leg's page balance the day before, less what open cases asked that day. It is due 28 days
  later (`arrears_engine.CLOSING_STATEMENT_TERM_DAYS`).
- Its `outstanding_gbp` is what the balance owes beyond every invoice's own figure at the book's end, up to what it asked.
- It is a demand and not a charge, so no balance moves.
- No statement is sent where the only bill after leaving is the leg's final bill.

**The control** is `tests/tools/test_a_level_dd_leavers_scheme_debit_is_asked_on_a_closing_statement.py`, 5 tests. It
asserts the partition first: an unpaid debit is asked and outstanding, and a debit met by later cash is asked and reads 0.
Six mutations fire:
- no statement: 2 tests red;
- outstanding set to asked: 2 red;
- open cases not netted: 1 red;
- cases repaid after leaving not counted as asking on the day: 1 red;
- a final bill alone gets a statement: 2 red;
- leaving dated at the last level bill: 2 red.

**The grade.** Each book's page is regenerated twice from the same run json, at 7f69f78825 and with this change. One
variable, so every movement is attributable. The pages are in `/var/tmp/lvl-shortfall/regen-*` and `armP-*`. The
readers are `census3.py` and `readers/compose3.py`, which are census2 and compose with the statement's outstanding
counted as asked.

| Prediction (filed in 8ec00af80) | 4dee9854a4 | 78f82e4242 | |
|---|---|---|---|
| Live leaver legs with unasked debit: at most 1 leg and GBP 5 | 21 legs, 6,859.12 → **4 legs, 403.86** | 22 legs, 6,945.89 → **5 legs, 490.63** | **FELL** |
| Closed leaver legs unchanged | 7, 309.27 → **1, 37.01** | 147, 10,681.09 → **141, 10,408.83** | **FELL** |
| Cures held over a debt stay at 193 | **193** on 92 accounts | **193** on 92 accounts | **HELD** |
| compose "left level DD, invoice unpaid" rises from 12 to between 12 and 33 | **47** | **47** | **FELL** (above the range) |
| Every other invoice keeps its outstanding figure to the penny | 0 legs moved, 0 balances moved | 0 legs moved, 0 balances moved | **HELD** |

**Why each fell, as measured.**
- **The closed class moved, and "unchanged" was a mistake in how I classified, not in the code.**
  - "Closed" is read at the book's end. A leg that left level DD years before it left supply is sent a statement on its
    leaving day, which is right.
  - 50 legs get a statement on each book. On 78f82e4242 these are:
    - 28 in the census's "left level" class (21 live, 7 closed);
    - 9 with no unasked debit, whose statement later cash met;
    - 7 in its "never level" class;
    - 6 in its "still level" class.

    The last two classes need a gloss:
    - "never level" means all their level collections were returned (PROS-2018-0016, SYN-2016-206);
    - "still level" means they left after their last successful level collection (PROS-2024-0321: two returns in
      Feb 2025, then on receipt).
  - The census's class reader is narrower than the leaving the generator dates.
- **The 5 live residues, not explained.**
  - SYN-2016-380: GBP 356.94 left of 2,273.27;
  - SYN-2016-549g: 6.90;
  - SYN-2016-525g: 5.75;
  - SYN-2016-487g: 34.27;
  - SYN-2016-247: 86.77. Its only bill after leaving is a final bill, so it is the final-bill class, the world-side
    question on this page's "What this does not settle".

  The rest is debit that arose after the leaving day with no invoice asking for it. **Mechanism not established.**
- **compose's rise is the point of the change.** 36 left-level holds read "no invoice unpaid" because the debit had no
  document. 35 of them now read an unpaid statement, and 13 level-at-cure holds do too. The desk cures over a demand
  the page now prints on **68 of the 193 holds** (47 + 21), against 20 before. That is the desk part (D), now visible
  on the page.

**SYN-2016-536g:** its statement was issued 3 Jul 2020, due 31 Jul 2020, asked GBP 112.14, and GBP 112.14 is still
outstanding at the book's end.

NEXT: (D), the desk's cure on a mixed account. On a book carrying (P), grade it against the (D) prediction in
8ec00af80. Before that, find out why the in-run desk cured SYN-2016-536 on 16 Feb 2023, from the in-run
`level_shortfall`.

**Re-graded on the merged base (worker, 10 Nov 2026 ~03:50 GMT).** 3099252c85, the repaid level return reaching the page,
landed between the grade above and the promotion. It changes the page's balances. So 78f82e4242's page was regenerated
again at b04e3832fd, once without (P) and once with it (`/var/tmp/lvl-shortfall/m-ctl`, `m-arm`):
- **Live leaver legs with unasked debit: 15 legs and GBP 5,671.45 fall to 4 legs and GBP 410.88.**
  - SYN-2016-380 holds 356.94 of the remainder.
  - SYN-2016-247 holds 29.77. That is the final-bill class.
- Closed leavers: 117 legs and 7,601.11 fall to 114 legs and 7,537.80.
- Statements: 35 legs get one, not 50. The repayments now on the page meet some leavers' debit before they leave, so no
  statement is asked.
- 0 balances and 0 invoice figures moved.
- So on origin the first figure in this section's title reads **15 legs and GBP 5,671.45** before (P), not 22 and
  6,945.89. Those were measured at 7f69f78825 and stand as measured there.

## (D) built: why the desk cured SYN-2016-536, and each leg's statement on a mixed account (worker, 10 Nov 2026 ~05:30 GMT)

**Why the in-run desk cured SYN-2016-536 on 16 Feb 2023.** Neither filed candidate was the cause. The real cause was the
day boundary between an ask and the cash that paid it.
- The replay posts bills at their gross face. The run posts them net of EBSS (`payer_ask_gbp`). With bills posted net
  (`/var/tmp/lvl-desk-probe/replay_net.py`, `NET=1`), the replay's balance is GBP 242.97 on 16 Feb, against the page's 243.
  So EBSS explains the old replay's balance gap, which is four GBP 66.67 instalments. It does not explain the cure.
  **Candidate 1 is refuted.**
- The shortfall is GBP 150.75 on 15 Feb, **49.02 on 16 Feb**, and 150.75 again on 17 Feb. On 16 Feb the gas leg paid
  bill 50068 (GBP 101.73) on its due date. `level_shortfall` counted cash through `as_of`. It counted a bill no level
  collection paid only after its due date (`d < as_of`). So that one day, the gas leg's on-time cash met the
  electricity schedule's missed requests (GBP 63.33, returned in 2017 and 2018) and 50041. This is candidate 2, narrowed
  to its mechanism: the cash is the gas leg's own and arrives on time, and the cure needed only the one-day boundary.
- No ask anywhere held the gas leg's scheme debit, because the account was still level through its electricity leg.
- **I cannot yet say** what the GBP 49.02 the replay still reads on 16 Feb is. The replay does not reproduce the run's
  journeys on this account: it keeps the 2018 journey open until 2025.

**What changed (one commit, two mechanisms).**
1. `arrears_engine.leg_leave_dates` and `leg_statement_asks` give each leg that leaves level DD while another leg stays
   on it its own closing statement. The statement is the leg's level-era bills, less its own credit notes, less its level
   requests. It is due 28 days after the leg's own leaving. `level_shortfall` counts it, and the journey walk can open on
   its due date.
2. `left_level_asks` dates each leg's level-paid remainder from that leg's own statement. That closes 703edeb89b's
   SYN-2016-345 GAP.
3. `level_shortfall` counts every ask from its own due date (`d <= as_of`), as it already counted the requests.

On the 536 replay, 16 Feb now reads GBP 93.62 short (49.02 plus the 44.60 statement), so the day cannot cure.

**Control:** `tests/company/billing/test_a_leg_leaving_level_dd_beside_a_level_leg_owes_its_own_statement.py`, 6 tests.
It asserts the partition first: an unpaid statement opens a journey and holds it, and one paid late cures that day.
Six mutations fire:
- no leg statement asked: 4 red;
- asks counted only after their due date: 1 red;
- credit note ignored: 1 red;
- requests not subtracted: 6 red;
- `left_level_asks` dated from the account's leaving: 1 red;
- the journey not walked on the leg statement's due date: 1 red.

A seventh mutation did not fire, and it was an equivalence: a guard excluding the leg that leaves with the account. The
guard is removed, and `leg_statement_asks` says why. `level_shortfall` is read only while the account is on level DD,
and on its leaving day, when that leg's statement is not yet due. The one case the guard decided, an account that left
whole and came back, it decided wrongly.

**Replay over the 4 mixed accounts on the merged-base page (`m-arm`), origin c5d99ba357 against this change:**
- PROS-2020-0223: 4 cures fall to 0, and the 2023 journey is held;
- SYN-2016-048, 525 and 536: unchanged. On this replay 536 never cures in between, so it cannot show the fix.

**Prediction for the first book carrying this, filed before any such book.** It replaces the (D) rows above, because two
mechanisms now land together. A book cannot separate them, and the replay can.
- The 20 holds on the 4 mixed accounts fall to **at most 4**.
- The total of 193 falls to **between 150 and 180**. The range is wider than (D)'s 173 to 180, because the due-day boundary
  reaches every level account with an on-receipt ask.
- Cure dates on accounts with no level request are **byte-identical**. `level_shortfall` reads only level accounts.
- **Refuted if** the total rises, or any never-level cure moves.

**Filed, not fixed:** cash paid *before* its bill's due date still meets another leg's older missed request until that
date. The K8 page names this as open.

NEXT: grade the prediction on the first book carrying this commit.

## The b8da2eed18 book: its control moved the base, so the prediction is re-read before the arm exists (worker, 10 Nov 2026 ~04:20 GMT)

*Drawn as `grade-the-leg-statement-desk-on-a-book`. Written while the book is queued and has not started, so no arm
figure exists.*

**The book.** `launch_long_job` job `book-b8da2eed18`, in the locked worktree `/var/tmp/book-wt-b8da2eed18`, which is
origin b8da2eed18 and clean. It is queued behind the head-green census for memory. Two in-run desk changes separate it
from the 78f82e4242 book: 703edeb89b (a leaver is dunned per leg) and b8da2eed18. 3099252c85 and b512dec267 touch only
`statement_export.py`, which is page-side. The grade chain is `/var/tmp/grade-b8da-scripts/after_run.sh`, writing to
`/var/tmp/grade-b8da/`, with the readers in `/var/tmp/lvl-shortfall/readers/` (split and compose with the GBP 0 row fix).

**The control is the 78f82e4242 run on b8da2eed18's page generator** (`/var/tmp/grade-b8da/control-78f/`). Only the run
then differs between the arms. It reads:
- **155** holds on 81 accounts, not 193. Same run, same desk cures (834). The page alone moved the count, through (P),
  3099252c85 and b512dec267.
- **18** on the 4 mixed accounts, not 20: PROS-2020-0223 4, SYN-2016-048 9, SYN-2016-525 3, SYN-2016-536 2.

**So the filed total (150 to 180 from 193) can no longer show the desk change.** The page alone already reads 155,
inside that range. The filed rows are still graded as written, and that reading is marked uninformative. The reading that
can fail is the same claimed effect, rebased onto the one-variable control:
- The total falls from 155 to **between 112 and 142**. That is the filed fall of 13 to 43.
- The 4 mixed accounts fall from 18 to **at most 4**, unchanged from the filing.
- Never-level desk journeys (account, open, cure, exit) are **identical** to the control's.
- **Refuted if** the total rises above 155, or any never-level journey moves.

**What I expect, written before the arm exists: the mixed-account row is likely to fall.** The (D) section's replay
moved only PROS-2020-0223 (4 to 0) and left 048, 525 and 536 unchanged. If the book follows the replay, 14 of the 18
remain, and "at most 4" is refuted. The replay is not the run, and 703edeb89b is in the book and not in the replay. I
cannot say which way it moves them.

## The book at origin's head, dca2ea1e7f: pre-registration, filed before it starts (seat executor, 10 Nov 2026 ~05:45 GMT)

*Drawn as `the-book-carrying-the-leaver-statement-and-desk-fixes-is-run-off-tree-and-gated`.*

**Premise, re-measured.** (P) landed as 059d2b55c1, and its surgical_land pid 1688374 is gone. The b8da2eed18 book is
still queued: it has not started, so no book carries (P). It also carries no in-run change after b8da2eed18. Origin's head,
dca2ea1e7f, carries every fix this item names. Since 78f82e4242 it adds these in-run changes:
- 703edeb89b and b8da2eed18 (desk);
- 47fdeacd5e (the world's settlement walk credits a level household's repayment at its cash);
- 3099252c85 and b512dec267 (page, plus their in-run halves).

So no movement below can be attributed to any one of them. The b8da2eed18 book stays queued: it is the one-variable
desk arm, and this book does not replace it.

**The control** is the 78f82e4242 run, regenerated through dca2ea1e7f's page generator (`/var/tmp/grade-dca2/control-78f/`).
The page code is the same in both arms, so every difference below is the run. The readers are in
`/var/tmp/grade-dca2-scripts/`: the 78f chain (`grade`, `overdue_breaches`, `classify`, `split`, `compose`,
`never_level`, `desk_own`), plus `census3` (leaver legs), `mixed` (holds on mixed accounts) and `wo_owed`.
`wo_owed` reproduces the filed 29 accounts and GBP 1,987.24 on `/var/tmp/desk29/ledger.json` exactly. The control already
reads far below the 78f grade, because the page fixes since then are in it:

| Row | Control (78f run, head page) | Prediction for the dca2ea1e7f book | Refuted if |
|---|---:|---|---|
| INV_OVERDUE_WITHIN_BALANCE | 2 (SYN-2016-007, SYN-2016-496: 703edeb89b's two) | **0 to 2, and neither 007 nor 496 is in it**. 703edeb89b was built for exactly these two | 007 or 496 still breach, or above 2 |
| PAGE_BALANCE, still-level steps | 0 | **0 to 5**. b8da2eed18 moves desk journeys on level accounts | above 5 |
| PAGE_BALANCE, left-level steps | 22, all on SYN-2016-549 | **at most 22**. The desk changes only make a leaver's dunning narrower. I cannot say whether 549 clears | above 30 |
| Unexcepted total | 24 on 2 rows | **at most 27**, on no third row | above 27, or a third unexcepted row |
| The 8 excepted rows | as in control `grade.txt` | the same exceptions hold | an excepted row loses its exception |
| Written-off accounts still printing owed | 30, GBP 2,121.64 | **fall, to between 12 and 28 accounts, and GBP at most 1,900**. The stale-refund part of class R (GBP 336.60 on 18 refunds) "should go on the next book", per the desk finding's trace. The per-leg part stays | count above 28, or GBP above 1,900 |
| Live leaver legs with unasked debit (census3) | 4 legs, GBP 415.70 | **at most 5 legs, GBP at most 450**. SYN-2016-380's 356.94 stays | above 5 legs or GBP 450 |
| Holds on the 4 mixed accounts / all holds | 15 / 139 | **mixed at most 4; all between 96 and 126** (the (D) fall of 13 to 43, rebased). Not attributable to (D) alone: 47fdeacd5e moves cash in the same book | mixed above 4, or the total rises above 139 |
| The gate | refused, 24 on 2 rows | **refused**, on PAGE_BALANCE (SYN-2016-549) at least | the gate passes |

If the gate passes, the book goes to the publisher at once, under the director's 8 Nov yes ("one early publish as soon
as a book passes the full gate"). Then the tenth cold read's embargo is lifted. If it is refused, each remaining breach
class is named with its count and owner.

**Launched after the table above was written** (the file as it stood then hashed sha256 `171be7a5…1d036143` at 05:21:18Z).
- **The run.** `launch_long_job` job `book-dca2ea1e7f`, in the clean worktree `/var/tmp/book-wt-dca2ea1e7f` (origin
  dca2ea1e7f, imports-off-commit `paths: []`). It is queued behind the head-green census for memory, as the b8da2eed18
  book is. Output: `/home/rich/synthetic-enterprise/docs/reports/run_output_dca2ea1e7f_20261110T052128Z.json`. Log: `/var/tmp/longjob-book-dca2ea1e7f.log`.
- **The grade.** Unit `longjob-grade-chain-book-dca2ea1e7f` waits for the run, then runs
  `/var/tmp/grade-dca2-scripts/after_run.sh` into `/var/tmp/grade-dca2/arm/`. It writes `ALLDONE` or `NO_DONE`.
  Whoever reads it grades the table above, writing held or fell beside each row.

## The b8da2eed18 grade, drawn again: the book has not started, so nothing is graded (seat executor, 10 Nov 2026 ~08:30 GMT)

*Drawn as `grade-the-leg-statement-desk-on-a-book`.* I re-measured the premise. No book carrying b8da2eed1 has run.
- `longjob-book-b8da2eed18-queued` and `longjob-book-dca2ea1e7f-queued` are both still queued. They wait behind
  `tools.head_green_census` (pid 1903956, 4h 04m elapsed). Its pytest child has used 3h 40m of CPU at 90%, so it is busy,
  not hung. They also wait behind a run of surgical_land commit gates ("landings come before experiments").
- No `run_output_b8da2eed18_*` exists, and `/var/tmp/grade-b8da/` holds only `chain.log`, `control-78f` and `land1.log`.
- The grade chain is armed: unit `longjob-grade-chain-book-b8da2eed18` runs `/var/tmp/grade-b8da-scripts/after_run.sh`
  into `/var/tmp/grade-b8da/`, and writes `CORE_DONE` and then `ALLDONE`, or `NO_DONE`.

The prediction to grade is the rebased one in the 04:20 section above: total 155 falls to 112–142, the mixed accounts fall
from 18 to at most 4, and never-level journeys are identical. It stands unchanged. I relaunched nothing, because a second
copy would run over the same seeds. The grade passes to the continuation `grade-b8da-book-when-its-chain-writes-alldone`,
which can be taken once `/var/tmp/grade-b8da/ALLDONE` exists.

## The 08:26:45 poweroff killed both books: dca2ea1e7f relaunched, a head book pre-registered, the b8da arm dropped (seat executor, 10 Nov 2026 ~19:10 GMT)

*Drawn as `the-books-killed-by-the-10-nov-poweroff-are-relaunched-and-graded`.*

**What died.** The guest powered off at 08:26:45 GMT. `book-dca2ea1e7f` had been running for two minutes: it was
admitted at 08:24:11Z, and its log ends at 08:26:20 in the Phase 2b customer listing. The poweroff also took
`book-b8da2eed18` (still queued), and both grade-chain units with it. At 18:55 no process or `longjob-*` unit survived. The
launch register settles a row only from a systemd exit record, and these had none, so it held them at UNKNOWN. I settled
both rows that claimed `live` (`book-dca2ea1e7f`, `grade-chain-book-b8da2eed18`) to `died`, with the cause "guest
poweroff 08:26:45". `book-b8da2eed18` had no record of its own. I dropped the continuation
`grade-b8da-book-when-its-chain-writes-alldone`, because its ALLDONE can no longer be written. The old log is kept as
`/var/tmp/longjob-book-dca2ea1e7f.killed-0826.log`.

**The "salvage" 264dcb92f is not this book's.** It is a worker-tick `fork_salvage` commit, also stamped 08:26:44. It holds
`book_growth_campaign.json`, `book_subset_verdict.json` and `token-log.md`, and nothing from the book's worktree.
`/var/tmp/book-wt-dca2ea1e7f` no longer existed, so I rebuilt it clean at dca2ea1e7f (imports-off-commit `paths: []`).

**dca2ea1e7f relaunched, the same run and the same readers.** I used `tools.run_annual_report` over the full window,
not fast, as the 78f82e4242 control ran. It went through `launch_long_job` and was admitted at 18:58:44Z. The new artefact
is `docs/reports/run_output_dca2ea1e7f_20261110T185708Z.json` (RUN_PATH updated). Its grade chain,
`longjob-grade-chain-book-dca2ea1e7f`, runs `/var/tmp/grade-dca2-scripts/after_run.sh` into `/var/tmp/grade-dca2/arm/`.
The table filed at ~05:45 above stands unchanged and is the one this book is graded against.

**A second book does not fit beside it, so the b8da2eed18 desk-only arm is dropped.** I asked the admission at 19:02. It
would refuse the head book: 19,592 MB resident plus a 12,500 MB declared peak is 32,092 MB, against 23,010 MB. Memory
cannot admit a third book beside two that do not fit together. The desk-only arm would also have answered a question
the dca2 book makes moot: what b8da2eed18 alone moves, when no published figure waits on that split. So I am not running
it. I queued the head book on `--wait-for-pid` of the dca2 run, so it starts when dca2 ends, and never alongside it.

### The head book, 068b5e3cc8: pre-registration, filed before it starts

Since dca2ea1e7f, origin's head adds two commits that touch the run's code. **6fb708f3ae** (class L) keeps a credit
bill's month's level collection. It changes the arrears engine (run) and the ledger generator (page). **d7c214a392**
gzips the committed billing ledger. It changes how readers open the file, and I expect no figure to move from it.

**Two controls.**
- (a) The 78f82e4242 run through head's page generator, `/var/tmp/grade-head/control-78f/`, measured 19:00. It moves
  only these rows against the dca2-page control:
  - written-off accounts printing owed: 30 / GBP 2,121.64 to 27 / GBP 1,230.90;
  - left-level closed legs' unasked GBP: 7,318.46 to 4,749.88;
  - all holds: 139 to 142.
  The unexcepted total is still 24 on the same 2 rows. So class L's page half is already in this control.
- (b) The dca2ea1e7f BOOK through head's page generator (`/var/tmp/grade-head/cross-dca2/`), written by the head chain
  before it grades. Against (b), the head book differs only in class L's run half. Against (a), it carries everything.

| Row | Control (a) | Prediction for the 068b5e3cc8 book | Refuted if |
|---|---:|---|---|
| INV_OVERDUE_WITHIN_BALANCE | 2 (007, 496) | **0 to 2, neither 007 nor 496**, as for dca2 | 007 or 496 breach, or above 2 |
| PAGE_BALANCE, still-level steps | 0 | **0 to 5** | above 5 |
| PAGE_BALANCE, left-level steps | 22, all SYN-2016-549 | **at most 22**. Class L lowers leaver balances. That could raise "overdue above balance" on 549g, and I cannot say which way | above 30 |
| Unexcepted total | 24 on 2 rows | **at most 27, no third row** | above 27, or a third unexcepted row |
| The 8 excepted rows | as (a) | the same exceptions hold | an excepted row loses its exception |
| Written-off accounts printing owed | 27, GBP 1,230.90 | **9 to 27 accounts, GBP at most 1,230.90**. The class-R stale-refund part (GBP 336.60) and the desk fixes come on top of class L's page half, which (a) already holds. SYN-2016-218 stays off the list | count above 27, GBP above 1,230.90, or SYN-2016-218 on it |
| Class L, run half, against (b) | n/a | **no leaver leg's unasked GBP rises against (b), and the left-level closed total does not rise**. This is the filed P2 (59 of 850 world-walk closing balances fall, none rise), seen through the page | any leaver class's unasked GBP above (b)'s |
| Bad debt, head book against the dca2 book | n/a | **`total_bad_debt_gbp` no higher than the dca2 book's**. The closing balance sizes write-off, and class L only lowers it | head above dca2 |
| Live leaver legs with unasked debit (census3) | 4, GBP 415.70 | **at most 5 legs, GBP at most 450** | above 5 or GBP 450 |
| Holds: mixed / all | 15 / 142 | **mixed at most 4; all between 96 and 129** (dca2's fall, rebased by +3) | mixed above 4, or all above 142 |
| The gate | refused, 24 on 2 rows | **refused**, on PAGE_BALANCE (SYN-2016-549) at least | the gate passes |

A gate pass goes to the publisher at once, under the director's 8 Nov yes, and lifts the tenth cold read's embargo. A
refusal names each remaining breach class with its count and owner.

## Book dca2ea1e7f, graded against its table: six rows held, two fell, and the gate refuses on one class, 22 steps on SYN-2016-549 (seat executor, 10 Nov 2026 ~21:00 GMT)

*Drawn as `the-books-killed-by-the-10-nov-poweroff-are-relaunched-and-graded`.*

The relaunched book ran from 18:58:44Z to about 20:50Z (`run_output_dca2ea1e7f_20261110T185708Z.json`, 1,302 accounts,
3,492,820 ledger events). Its chain wrote `ALLDONE` into `/var/tmp/grade-dca2/arm/`. The control is
`/var/tmp/grade-dca2/control-78f/`, as filed at ~05:45. The table was not edited after it was filed.

| Row | Control | Prediction | Book | Verdict |
|---|---:|---|---:|---|
| INV_OVERDUE_WITHIN_BALANCE | 2 (007, 496) | 0 to 2, neither 007 nor 496 | **0** | **held**. 703edeb89b cleared both |
| PAGE_BALANCE, still-level steps | 0 | 0 to 5 | **0** | **held** |
| PAGE_BALANCE, left-level steps | 22, all SYN-2016-549 | at most 22 | **22, all SYN-2016-549** | **held**. It did not move at all: 549 does not clear |
| Unexcepted total | 24 on 2 rows | at most 27, no third row | **22 on 1 row** | **held** |
| The 8 excepted rows | as control | the same exceptions hold | identical counts (337, 12, 7, 7, 7, 1, 2, 19) | **held** |
| Written-off accounts printing owed | 30, GBP 2,121.64 | 12 to 28, GBP at most 1,900 | **32, GBP 2,142.37** | **fell**. See below |
| Live leaver legs with unasked debit | 4, GBP 415.70 | at most 5, GBP at most 450 | **3, GBP 385.85** | **held**. SYN-2016-247's GBP 29.77 leg is gone; 380's 356.86 stays |
| Holds: mixed / all | 15 / 139 | mixed at most 4; all 96 to 126 | **11 / 116** | **fell** on mixed (PROS-2020-0223 went 4 to 0; 048, 525 and 536 are unchanged at 6, 3 and 2); all held |
| The gate | refused, 24 on 2 rows | refused, on PAGE_BALANCE (549) at least | **refused, 22 on 1 row** | **held** |

**The written-off row fell, and the direction is wrong, not only the size.** I predicted that the class-R stale-refund
part (GBP 336.60 on 18 refunds) would leave this book. It did not. Against the control, three accounts entered
(SYN-2016-155 GBP 10.81, 368 GBP 53.92, 558 GBP 36.74), one left (612, GBP 68.51), and six moved (091 up 19.04,
455 up 6.68, 151 up 3.36; 584 down 22.37, 342 down 15.73, PROS-2018-0359 down 3.21). Two explanations fit, and the
evidence does not yet choose between them. Either the stale-refund cure is not in any commit this book carries, or
47fdeacd5e's cash crediting moved which accounts close with a balance. This row is not a gate invariant. Its owner is
`desk-write-off-reaches-the-page` (class L, `SEAT_FINDING_THE_DESKS_WRITE_OFF_OF_A_CLOSED_ACCOUNT_NEVER_REACHED_THE_PAGE_2026-11-10.md`),
which the head book 068b5e3cc8 carries. Its own prediction, at most 27 and at most GBP 1,230.90 against control (a), now
grades on the head book.

**The mixed row fell on size, and the total held.** Only PROS-2020-0223's four holds cleared. The (D) fall I rebased
from the b8da arm assumed every mixed account moved. SYN-2016-048, 525 and 536 are untouched. Not a gate invariant.
Owner: the (D) leg statement on a mixed account (section "(D) built", above).

**Bad debt** on this book: `total_bad_debt_gbp` GBP 9,620.64 (settled-realised). The head book's "no higher than the
dca2 book's" row grades against this number.

### The gate refuses. Every remaining breach class, with its count and owner

| Class | Count | Owner |
|---|---:|---|
| INV_OVERDUE_WITHIN_PAGE_BALANCE, left level, SYN-2016-549 (class L′: a credit bill waits for the next bill in the world and meets the scheme debit on the page) | 22 steps, 1 account | D_billing_metering, next item `a-credit-bill-meets-the-scheme-debit-before-the-next-bill` (`SEAT_FINDING_A_CREDIT_BILL_WAITS_FOR_THE_NEXT_BILL_IN_THE_WORLD_AND_MEETS_THE_SCHEME_DEBIT_ON_THE_PAGE_2026-11-10.md`, a49ba851b) |

That is the only unexcepted class. The book is **not** offered to the publisher, and the tenth cold read's embargo
stays. The head book 068b5e3cc8 started at about 20:50Z when this one ended, and its chain grades its own table
(filed above at ~19:10). I predict the gate refuses there too, on the same 22: 6fb708f3a fixed class L, and class L′
is the other branch, which no landed commit touches yet.
