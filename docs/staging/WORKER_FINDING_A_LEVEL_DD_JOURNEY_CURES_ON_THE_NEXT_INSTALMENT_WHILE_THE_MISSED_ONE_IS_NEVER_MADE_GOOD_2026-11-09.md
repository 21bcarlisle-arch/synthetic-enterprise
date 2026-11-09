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
