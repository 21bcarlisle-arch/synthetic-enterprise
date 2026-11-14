**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# A level direct debit household is dunned per bill, so its page prints "overdue" while it is in credit (2026-11-07)

*BLOCKING: two unexcepted gate rows, and the 9 Nov publish has no other book that passes.*

**Found by.** The first book that carries N20's level DD schedule, `run_output_fa915ac0d7_20261107T184010Z.json`. It was
graded at origin 3ced67a162; the grade is in
`SEAT_FINDING_THE_B3CE2A4E73_BOOK_FAILS_THE_DOMAIN_INVARIANT_GATE_ON_SEVEN_ROWS_2026-11-04.md`, in its 7 Nov ~21:00 section.
The book before it (8c7489e0d9) differs only by 8178e24218, which saves the schedule. Graded at the same origin, that
book reads 0 on both rows below.

## What it is

Under a level direct debit, the household owes the **scheduled collection**, and its arrears are the **account's balance**.
No single bill is "due" by direct debit (`payments_and_direct_debit_2026-10-25.md`, "What a level direct debit must be").
Two readings on the page still assume that each DD pays its own bill by that bill's due date.

1. **INV_OVERDUE_WITHIN_PAGE_BALANCE: 1,724 of 6,695 steps, all on level-DD households (176 of 454).**
   - The collections journey (`collections_journeys` in the run output, which reaches the page through
     `tools/generate_billing_ledger.py`) opens on a per-bill DD outcome of "failed". It then prints that bill's face as overdue.
   - The page balance runs on the level schedule. So 852 of the steps print an overdue sum while the household is in credit or at zero, and 872 print more than it owes.
   - The excess has a median of GBP 46.51, a maximum of GBP 449.05 and a sum of GBP 113,865.
   - **Example.** OCC-226d3bc42b37 is GBP 73.57 in credit on 15 Mar 2025, after a level GBP 104.42 on 10 Mar. Its GBP 109.73 bill's DD is "returned" that day. The page then prints a missed payment, two reminders and a GBP 345.38 arrangement offer.
2. **INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE: 45 of 1,139, all level-DD supply points, "missed DD without a return".**
   - `tools/generate_explore_cast.payment_record` counts a bill as missed when no payment on it lands by its due date.
   - The ledger attaches each level collection to a bill of its month, and dates it on the schedule's collection day. When that day falls after the bill's due date, the bill reads "missed" although nothing failed.

## What is not yet known (I cannot yet say)

- Whether the world draws a DD **failure** per bill or per scheduled collection for a level household. On OCC-226d3bc42b37,
  the failed month has no level collection at all, and the failure is dated at the bill's due date at the bill's face. That
  suggests the per-bill outcome model still decides failure and the schedule only replaces successes. Read
  `simulation/dd_level_collection_book.py` and the ledger's `level` pop (`generate_billing_ledger.py`, about line 933) before
  choosing where the fix lives.
- What a GB supplier's collections desk does when a level DD is returned on an account in credit. The knowledge page comes first (K8):
  `debt_and_collections.md` and `payments_and_direct_debit_2026-10-25.md`. A return is chased as a missed payment
  (ADDACS/ARUDD). Whether arrears action opens while the account is in credit is likely the practitioner gap (K4). Mark it GAP if no source settles it.

## What done means

On the next book built after the fix:
- both rows read 0 on level-DD households;
- N20's Leg A stays at or below 0.30;
- the collections journey's printed overdue figure is the account's arrears (the missed collections net of credit), not a bill's face.

The share leg must not move. If it does, the fix has changed what the schedule collects rather than how a miss is read.

## Not recommended

A dated exception on INV_OVERDUE_WITHIN_PAGE_BALANCE. It would publish "GBPx overdue" to households that are in credit, which is exactly what the row was written to catch (cold reads O10, O16 and O18).

## Step 1, the payment record: pre-registration (seat, 8 Nov 2026, written before the grade is run)

**Where the fix lives, decided.** The knowledge section is "A returned level direct debit: what is missed, and what is
owed" in `payments_and_direct_debit_2026-10-25.md`. It splits the work into two steps.
- **Step 1, the page.** `payment_record` reads a level collection as on time on its own scheduled day. The page ledger's
  payment row carries the flag `level_dd` that the billing ledger already sets.
- **Step 2, the world and the desk.** Row 1 is not fixed on the page. Its figure is the desk's own journey from phase 2b,
  which never sees the schedule, so a page rewrite would print acts the company never took.

**Prediction.** Re-grade the fa915ac0d7 book (`/var/tmp/grade-fa91-seat/ledger.json`, unchanged) with
`/var/tmp/b3ce-grade-scripts/grade.py` at this commit:
- INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE: **45 -> 0**.
- INV_OVERDUE_WITHIN_PAGE_BALANCE: **unchanged at 1,724**.
- Every other row unchanged.

If the record row lands above 0, some level bills are missed for a reason other than the date their collection lands on.

**Graded (8 Nov, at origin 78e94ce98b plus this change; `/var/tmp/grade-fa91-levelrec/`).** The prediction held.

| Row | fa915ac0d7 at 3ced67a162 | at this change |
|---|---:|---:|
| INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE | 45 | **0** (CLEAN, 1,139 checked) |
| INV_OVERDUE_WITHIN_PAGE_BALANCE | 1,724 | **1,724** |
| every other row | | unchanged (diffed across all rows) |

The verdict goes from 1,772 unexcepted breaches on 3 rows to **1,727 on 2**. The publish is still refused, on row 1 and on
INV_BILLED_EX_VAT's mixed-version 3, which is predicted to clear on the first book built at or after 8b6316995.

## Step 2, still open: the world draws a return per scheduled collection, and the desk reads the account's balance

- **Where.** `background/live_payment_triad.LivePaymentTriad.record_period` takes one bill (due date, amount) and draws its
  outcome. The level schedule is built only in phase 4c (`simulation/run_phase4c_on_phase2b.py`, line 643), from DD2's
  balance book, after phase 2b's desk has walked every journey.
- **What it needs.** Phase 2b must know a level household's monthly amount when it collects. That amount is the
  registration DD and then each year's reviewed amount, through `company/interfaces/dd_review_outcome.py`. The collection
  is posted at that amount on the staggered day, and the per-bill outcome draw becomes a draw on that collection. A return
  is the collection's amount on its date. The desk already reads the account as one balance, so its overdue figure becomes
  the debit balance.
- **What moves.** The company's receivables, provision, cash timing and treasury on level accounts. Pre-register those
  figures before the first book built with it.
- **Not recommended** (unchanged): a dated exception on row 1, or a page-side rewrite of the desk's figure.

## Step 2, measured before building (worker, 8 Nov 2026)

These measurements are on the fa915ac0d7 book (`docs/reports/run_output_fa915ac0d7_20261107T184010Z.json`): its
`opening_dd_by_customer`, `annual_dd_review.events`, `level_dd_collections` (766 households, 29,519 months) and `bills`. They
settle where phase 2b can get the amount from.

1. **The in-loop review alone is not enough.**
   - `simulation/dd_review_in_loop.InLoopDDReview` already runs causally inside phase 2b. It reaches the company's
     `annual_dd_review_view` door, the same chain as the post-loop `annual_dd_review`.
   - Rebuilt from the opening amount and those review events, that chain gives the scheduled amount on **18,885 of 29,519**
     level months.
   - The other 10,634 differ, usually upward: median +GBP 5.89, range −71 to +461. Example: C2 reviews to GBP 35 in
     Apr 2017, and the schedule collects 35.70.
   - The difference is the review seeking the debit balance (`dd_review.REVIEW_SEEKS_BALANCE`, on since 20 Oct), plus DD
     spells. Both live only in `build_dd_balance_book`.
   - **So phase 2b must ask the balance book, not the review.**
2. **The balance book is almost causal, and where it is not, the schedule uses hindsight.**
   - Test: `build_dd_balance_book` run on a leg's bills up to month m, against the full book, on 40 sampled level households.
     **359 of 367** prefix months match.
   - The 8 that differ (−GBP 0.67 to +0.28) all come after runs of estimated bills.
   - The cause is `_true_charges` (`simulation/dd_balance_book.py:287`): an estimated period's true charge includes its share
     of a catch-up that a **later** read bills. So a review that seeks the balance sizes its step-up partly from a read the
     supplier has not yet taken.
   - That is the epistemic wall in miniature, inside the post-loop schedule: small in pounds, wrong in kind.
3. **Sanity.** The full book on bills alone (no spells, no term records) reproduces the published schedule on 1,590 of
   1,757 of the sample's months. The rest are the DD spells and closures the run passes in.

**Design, decided.**
- At each billed month, phase 2b asks `build_dd_balance_book` for a level leg's collection, over the bills and DD spells
  known so far. That is the same door the in-loop review uses, asked as it asks.
- It records that amount on the leg's staggered day. `record_period` then collects that collection, not the bill, and draws
  its outcome. A return is that amount on that day.
- Phase 4c's schedule must then be the **causal** one, the same amounts phase 2b collected, rather than a hindsight
  rebuild. Otherwise the page and the desk collect different sums on about 2% of months.
- The hindsight fix in `_true_charges` (a catch-up counts only from the date it was billed) is its own one-variable step,
  landed and graded first. It moves only the balance-seeking step-up.

**Pre-registration for the first book built with Step 2** (written before any build):
- INV_OVERDUE_WITHIN_PAGE_BALANCE: **1,724 → 0** on level-DD households.
- INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE stays **0**.
- N20's Leg A stays **≤ 0.30**. The share leg is **unchanged**.
- Level-DD returns: their count moves from per bill to per scheduled collection, and the total returned moves from bill faces
  to scheduled amounts. I cannot yet say in which direction the total moves.
- Receivables on level accounts fall, because in-credit accounts stop carrying a bill face as owed. The provision falls with
  them.
- Treasury's cash timing moves to the staggered day.
- Every non-level account: **byte-identical** payment events.

If a non-level account moves, the change has leaked past the mandate-type draw.

## Step 2a, the hindsight in `_true_charges`: pre-registration (seat, 8 Nov 2026, written before the code)

**The change.** A recovery action (an annual review that seeks the balance, or the final bill) reads each earlier
period's true charge **as known on the action's date**: its bill, plus the share of a catch-up only when the catch-up's
own bill ends on or before that date. `_true_charges` (the hindsight figure) is unchanged and still feeds the published
`true_charge_gbp` and `tools/dd_book_legs`. One variable: what the bar at a review may read.

**Prediction, on the fa915ac0d7 book's bills, opening amounts and DD spells:**
- The prefix test (book on a leg's bills up to month m against the full book, the same 40-household sample idea):
  every month matches, where 359 of 367 did. If any month still differs, the hindsight has a second route.
- The final-bill bar (`barred_at_final_bills_gbp`) is **unchanged to the penny**: every catch-up a final bill's
  periods carry is billed by the final bill.
- Only reviews after a run of estimated bills move; their bar can move either way (a catch-up not yet billed can
  lower or raise a period's charge). I cannot yet say the sign of the total.
- Every leg with no catch-up before a review: byte-identical trajectory.

**Graded (8 Nov, on the fa915ac0d7 book's bills, rebuilt post-run with `closed_ids_from_bills` and `dd_spells_from_run`;
script `/var/tmp/l2a/measure.py`).**

| | before | after |
|---|---:|---:|
| prefix test, every DD leg with both a catch-up and a review step-up (538 legs, 31,379 months) | 322 differ | **0** |
| review bars, seeks arm (the switch's arm) | GBP 16,118.66 | GBP 17,157.86 |
| review step-ups (1,317) | GBP 14,755.34 | GBP 14,668.74 |
| final-bill bars, seeks arm | GBP 3,025.74 | GBP 3,084.16 |
| final-bill bars, never-seeks arm | GBP 27,732.31 | GBP 27,734.42 |
| run-end exposure, never-seeks arm | GBP 44,915.85 | GBP 44,904.34 |
| level trajectories moved (of 941) | | 91 |

- The prefix leg held: the hindsight had one route into the schedule, and it is closed.
- **My final-bill prediction was wrong**, and it was wrong in two ways.
  - On the seeks arm, all six moved final bills are legs whose earlier review bar moved, so what was left open changed.
  - On the never-seeks arm, two final bills and four run-end exposures moved, by GBP 9 or less. Every one of them is a
    leg that **left DD**, where the catch-up was billed on a receipt-paid bill after the last DD bill. The "final" action is
    dated at that last DD bill, so it could not have known the catch-up either. Same hindsight, second route, now closed.
- Reviews bar more in total (+GBP 1,039.20) and step up less (−GBP 86.60). A review that could see a later catch-up's
  upward share took more of the debit as barred and left less to step up. Without that sight, the oldest shortfall is
  smaller at the review, and more of it ages into a later action.
- Not changed: `_true_charges` itself, so the published `true_charge_gbp` and `tools/dd_book_legs` keep the end-of-run
  figure. That is a post-run reading, not an action.
- Control: `test_a_review_reads_only_the_catch_ups_billed_by_its_own_date` (the prefix property). Mutation-proven: with
  the as-of filter reverted, it goes red.
- **N20 Leg A and the page rows are not graded by this step.** They need a book built at this commit. The 91 moved
  legs change the level schedule that the page and the books read, so the next book carries this change.

**Step 2a is landed** as ee0982734c (8 Nov). A second draw of the same step that day, as
`a-dd-step-up-counts-a-catch-up-only-from-the-day-it-is-billed`, found it already on origin and changed nothing. Its
"367 of 367 on the 40-household sample" is met by the row above: 0 of 31,379 months differ over all 538 legs.

**Next, Step 2b** (continuation `level-dd-step-2b-phase-2b-collects-the-causal-level-amount`): phase 2b asks the balance book for each level leg's collection, the causal amount, and the outcome
draw goes on that collection.

**Grade item drawn early (seat executor, 04:10 UTC 8 Nov).** `grade-the-first-book-carrying-the-level-dd-fix-through-the-whole-gate-and-the-bscp504-prereg` was drawn with no book to grade. The newest book, `run_output_84f7fc8fe0_20261108T021850Z.json` (finished 03:59Z), and af31e73fa7 before it both carry 8b6316995 but not step 2a (ee0982734c). Step 2b is not on origin. The runner's next run starts about 05:18Z and will carry 2a only. This finding's own pre-registration (1,724 → 0) is for a book built with step 2, so that book cannot answer it. The item is re-keyed to the first book whose commit has the step 2b landing as an ancestor. Nothing was graded, and no book was started by hand.

**Grade item drawn early again (seat executor, 06:45 UTC 8 Nov).** `grade-the-first-book-built-after-level-dd-step-2b` was drawn with neither of its conditions met. Step 2b has no commit on origin (791df72b40), and the newest book is still `run_output_84f7fc8fe0_20261108T021850Z.json`. Nothing was graded. Its `DO NOT DRAW until <landing> AND <book>` is a spelling the draw cannot read, and the hand-off did not refuse it. The hand-off now does (`_EMBARGO_PHRASE` reads `until`). The grade has no successor item. Step 2b's own done-means already grades the first book built with it. Whoever lands 2b hands off the grade FROM that landing, with the book's path in a `DO NOT DRAW BEFORE /abs/path EXISTS` phrase. That grade carries the BSCP504 rows in `docs/staging/records/WORKER_PREREG_THE_BSCP504_CEILING_ON_THE_NEXT_FRESH_BOOK_2026-11-07.md` alongside this finding's 1,724 → 0.
## Step 2b, first increment: phase 2b asks the book, and phase 4c hands the page what phase 2b asked (worker, 8 Nov 2026)

**Landed in this commit.** The outcome draw is not touched yet.
- `simulation/dd_review_in_loop.InLoopLevelCollection`: as each month posts in `_post_month_bill`, a leg that
  `pays_a_level_direct_debit` asks `build_dd_balance_book` for this month's `collected_gbp`. The book reads the leg's
  bills and DD spells known so far: the stop board's bills to the month's end (`StopNoticeBoard.bills_before`, before
  the pre-bill gate, as phase 4c builds its book), and the rails' spells over the issued ones. The row is dated on the
  staggered day, held to supply start, and rolled to a Bacs day (N22/N23, `level_collection_dates`).
- **Asked once a window.** The standing amount, and its step-up, are set at the first DD bill of each 12-month
  window, so the amount is fixed for the window. A leg's final month asks again.
- Phase 4c's `level_dd_collections` is now the loop's schedule (`level_dd_schedule_from_the_loop`). The rebuild
  stays, as `level_dd_schedule_reconcile` beside it, and that reconcile is forwarded by `extract_report_data`.
  - A run with the dual-fuel offsets on keeps the rebuild, because the loop does not ask them.
  - A run with no loop schedule also keeps the rebuild.
- Control: `tests/simulation/test_phase_2b_collects_the_level_amount_the_book_would_set.py`.
  - A 40-month seasonal leg, opened low so a debit builds and the review steps up. Its amounts run GBP 30.00, 167.88,
    129.75 and 163.62. The loop's schedule equals the post-loop book's on all 40 months, and the book is asked 4 times.
  - Four mutations, all red: the window test removed; the cutoff a month early; the offsets switch ignored; no supply
    start.

**Pre-registration for the first book built at or after this commit** (written before any book carries it):
- `level_dd_schedule_reconcile.source` is `in_loop`.
- `differ` is **at most 2% of matched months**. Either way, it is not zero for a known reason I cannot yet size: the
  loop's bills are assembled without the run's `tenancy_links`, and before the final read a churned leg's last bill
  takes.
- `only_in_loop` and `only_post_loop` are **at most 1%** of months.
- INV_OVERDUE_WITHIN_PAGE_BALANCE is **unchanged in kind**. The desk still dunns the bill face, so it stays near 1,724
  and moves only by the months where the schedule changed.
- N20's share leg moves by at most the `differ` share.
- Every non-level account is **byte-identical**. The loop asks nothing for a leg the mandate draw puts on a variable
  amount.
- If `differ` is above 2%, then the in-loop bills and the published bills are not one assembly, and that is the next
  item, ahead of the outcome draw.

**Next, Step 2b's second increment** (still this continuation): `record_period` takes the loop's row for a level leg,
so the draw is on the collection (its amount, on its collection date). A return is that amount, and the desk's journey
opens on the account's debit balance rather than a bill's face. Its pre-registration is the "Step 2, measured before
building" block above (1,724 → 0). That landing, not this one, hands off the grade, in the shape the 06:45 note
asks for. The grade also reads this increment's `level_dd_schedule_reconcile` rows, against the pre-registration
here.

## Step 2b, second increment: the definition first, and why the world side cannot land alone (worker, 8 Nov 2026)

**Nothing in the run moves in this commit.** It corrects the definition the desk will be built on, and
measures why the outcome draw cannot change by itself.

**The definition, corrected.** The knowledge page said that on a level account "the household's arrears are the
account's debit balance". Ofgem's reporting definition says otherwise. A DD customer is in debt only "where they
have fallen into debt while on direct debit by defaulting on one or more payments". It excludes "all other
direct debit customers, including those customers with a debit at the end of a payment scheme" (letter of
20 Sep 2011, Appendix 2, para 2.8). So a level account in seasonal debit with every collection taken is
**not** in arrears. The page now says that, with the correction beside the old line
(`payments_and_direct_debit_2026-10-25.md`, "What is owed"). The desk's figure for the build is the shortfall against the schedule,
capped by the debit balance: `max(0, min(requested to date - received to date, debit balance))`. The journey opens
only on a return. The K4 gap narrows to the desk's operational step on the day of a return.

**Measured: why the outcome draw cannot change first.** The question is what the desk would do if phase 2b
presented each level collection at its amount on its day, and the desk kept ageing bills from their due dates as it
does now. A level collection for month m lands on the payment day *inside* month m, before month m's bill exists.
So a leg in seasonal debit has a bill unpaid at its due date with nothing missed. On the fa915ac0d7 page ledger
(`/var/tmp/grade-fa91-seat/ledger.json`; script `/var/tmp/l2b2-measure/fifo_on_level.py`, cash and bill faces as the
page carries them):
- 755 level legs and 31,395 bill due dates;
- **10,247 due dates on 544 legs** find the leg in debit with no level collection yet failed;
- median debit GBP 81.03.
- The maximum, GBP 4,608.14, is not checked. It is likely a leg that left DD and was paid on receipt afterwards, which the script
  does not separate.

So a world-only landing would replace 1,724 false steps with several thousand false journey *openings*. The world
change and the desk change land **together, or not at all**.

**The cut, decided.** One landing, three parts:
1. **World** (`LivePaymentTriad.record_period`, fed from `_post_month_bill`). A level leg that is not stopped,
   cancelled or on its final month presents `InLoopLevelCollection`'s row: that amount on its collection date. The
   per-period draw becomes the collection's outcome, still keyed by period, so no seed moves. The budget book and any
   later settlement read that amount. A credit bill posts its credit note and does not cancel the month's collection.
   The final month keeps the bill path, because a final bill is settled on its face.
2. **Desk** (`company/billing/collections_journey`, plus the view it reads). An account whose collection requests
   carry a level schedule is dunned on the shortfall above. Its bills' due dates are not openers. The company knows
   this from its own `CollectionRequest`s and the ARUDD returns, so it knows only what it asked for and what came back.
3. **Page**: a failed level payment row's arrears case is the shortfall, not the bill's face
   (`tools/generate_billing_ledger.py`, the `level` pop).

**Pre-registration**, the same as "Step 2, measured before building" with two additions. Both are written before any code:
- On level legs, journeys open **only** on a date where a level collection was returned. If any opens on a bill's
  due date, part 2 has a leak.
- The number of level-leg journeys is at most the number of returned level collections.

## Added pre-registration leg: the desk's cures, read on the page's balance (worker, 8 Nov 2026, before step 2b lands)

On 84f7fc8fe0, an independent reader read **85 of 976** desk cures with something still owed. The reader is the page's
running balance from `build_account_ledger`, read as `_owed_past_due` reads it, with level legs capped at their shortfall
against the schedule. **133 of 134** cures on the uncapped reading were on level-DD accounts. On **13** accounts (39 of the cures), every
invoice was marked paid while the page balance stayed in debit to run end. **6** of those had left level DD, so their
debit is one no bill asks for. The method and rows are in
`done/SEAT_FINDING_THE_WORLD_PRESENTS_A_NIL_DIRECT_DEBIT_AND_SETTLES_BILLS_ALREADY_CLEARED_2026-11-05.md`.

**Prediction for the first book carrying step 2b:** the same reader reads **0 to 3** cures over a shortfall. If it
reads more, the desk and the page still disagree about what a level account owes after step 2b. Also predicted: no account that has
left level DD carries a page debit with every bill marked paid. Today 6 do. If either fails, SYN-2016-550's DIRECTION row stays open, and the leg becomes its own finding.

## Step 2b, second increment: the world presents the level collection, the desk owes the schedule (worker, 8 Nov 2026)

**Landed in this commit, the three parts together**, on the definition in
`payments_and_direct_debit_2026-10-25.md`, "What is owed" (6bf6fce7f).
1. **World.** `run_phase2b._post_month_bill` hands `InLoopLevelCollection`'s row to
   `LivePaymentTriad.record_period(level_collection=...)`. A month collected by DD that is not a churned leg's final
   month, a mover's final month, stopped or cancelled presents that amount on its Bacs-rolled date. The outcome
   draw is unchanged (keyed by period), so only the amount and the date move. A return is the level amount. The
   bill still posts at its face, and a credit bill still posts its credit note without cancelling the collection.
   The world's own settlement walk (`_leg_rows`, which sizes a later repayment) reads the collection, so a repaid
   return repays the amount missed.
2. **Desk.** The company records its level requests (`note_level_collection_request`, its own act). Such an
   account is viewed through `arrears_engine.level_shortfall`: `max(0, min(requested - received, debit balance))`,
   aged from the oldest request the cash has not met. Its journey opens only on the day after an ARUDD return,
   and a bill a level collection paid opens nothing on its due date. It cures when the shortfall is met, even
   with a bill still unpaid in seasonal debit.
3. **Page.** A failed level payment row's arrears case is the desk's figure on the day the return counts as
   missed. If the desk has no stage that day, no case opens: either the return left nothing short (in credit), or
   a journey already open carries the debt.

4. **The walk.** The desk's walk read the ledger as complete to the latest bill due date of each leg. A level
   collection is dated inside its month, *before* that month's bill falls due, so this was no longer true. The
   first build raised `DunningOfAClearedDebtError` in a phase 2b run to Jun 2017: SYN-2016-452 was sent a
   reminder on 30 Jan 2017, and gas level cash then posted behind it, leaving the ledger at GBP -7.30.
   There were two routes, and both are closed.
   - The other leg's collection. `_walk_bound` now stops a level leg at the end of the last month it presented.
   - The term just popped. In phase 2b, a popped term leaves `_pending_starts` before its first month opens, so
     `legs_still_posting` did not count it. It now counts the term in hand. This gap was older than this change;
     level cash is what made it bite.
   - On the same window after the fix, 28 cash posts still land on or before an already-walked day. The
     examples are budget clearances posted on the walked day itself, and an occupier's gas leg paid on
     receipt. Neither is a level collection. Origin's count on the same window is in the commit message.

**Control.** `tests/simulation/test_a_level_dd_household_is_dunned_on_its_schedule_not_its_bills.py`, five legs.
- **The named household.** OCC-226d3bc42b37's electricity leg as af31e73fa7 billed it (Oct 2024 to Mar 2025,
  level GBP 104.42 on the 10th), with February's collection returned. No journey opens, and the one return is
  GBP 104.42 on 10 Feb, not the GBP 109.73 bill. On origin before this commit the test is red:
  `record_period` has no level argument.
- **Seasonal debit with every collection taken.** GBP 60 level, winter bills. The account is in debit, and
  nothing opens.
- **A return in seasonal debit.** The journey opens on 6 Jan at GBP 60, not at the debit balance. This is the
  partition control: the branch can be taken.
- **The return repaid.** The journey cures on 25 Jan while the account is still GBP 80 in debit with December's
  bill unpaid.
- **No collection lands on a walked day.** A dual-fuel level household, posted month by month: neither
  leg's collection is dated on or before the desk's walk. The cross-leg route is unit-tested. The term-in-hand
  route is covered by `tests/simulation/test_debt_objection.py`, which went red without it.
- **Eight mutations, all red:**
  - the desk ignores level;
  - the view reads bills;
  - the world presents the bill;
  - it opens on the return day rather than the day after;
  - the figure is the balance;
  - the cure waits on bills;
  - the world's settlement rows are bill-shaped;
  - the walk has no floor for a level leg.

**Named, not built.**
- The world's settlement walk does not cap at the debit balance, as the desk does. A household in credit can
  still repay a returned collection. This is the K4 gap the knowledge page keeps.
- `arrears_state` and `receivable` (the provision's reads) still age the balance. They are not the journey, and
  the pre-registration's receivables leg grades them as they stand.
- The dual-fuel offsets path keeps the post-loop rebuild, so with offsets on the loop presents nothing new. That
  path is off by default.

**Pre-registration for the first book built at or after this commit.** This is the "Step 2, measured before
building" block, with the two added legs and the desk-cure leg above. It is unchanged, and was written before
this code.
- INV_OVERDUE_WITHIN_PAGE_BALANCE: **1,724 → 0** on level-DD households.
- INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE: stays **0**.
- N20 Leg A: **≤ 0.30**. The share leg: **unchanged**.
- On level legs, journeys open **only** on a return date (plus one day). The number of level-leg journeys is
  **at most** the number of returned level collections.
- The page-balance cure reader: **0 to 3** cures over a shortfall. No account that left level DD carries a page
  debit with every bill marked paid.
- Every non-level account: **byte-identical** payment events.
- The increment-1 rows for `level_dd_schedule_reconcile`: `differ` **≤ 2%** of matched months, and `only_*`
  **≤ 1%**.
- The BSCP504 rows in `records/WORKER_PREREG_THE_BSCP504_CEILING_ON_THE_NEXT_FRESH_BOOK_2026-11-07.md`.
- **Added now:** level-DD returns are counted per collection, dated on the collection day, at the level amount.
  I cannot yet say whether their total moves up or down.

## The e50e7b8f68 book, the first carrying step 2b, graded (worker, 8 Nov 2026 ~23:50 GMT)

`run_output_e50e7b8f68_20261108T220440Z.json` (finished 23:40Z; a3136e29fa is an ancestor). Graded at origin
342599376c, which has no commit after the book that touches the ledger, the runner or the world. The grade used
`/var/tmp/b3ce-grade-scripts/` (ledger.py, then grade.py), and the level legs used `/var/tmp/grade-e50e/level_legs.py`.
Scratch: `/var/tmp/grade-e50e/`.

**First, the ledger could not be built.** `tools/generate_billing_ledger.py` raised `UnboundLocalError: arr` on
this book. Step 2b's page part sets `outcome_case = None` when the desk finds nothing short on the day after a level
return. The block that finishes a case was still keyed on the engine's raw `outcome`, so it called `arr.update`
on whatever case the loop last held. On the first such bill in a book that is a crash. Later in a book it rewrites the
previous bill's case, possibly another household's, with this bill's face. This commit fixes it: the block is now keyed on
`outcome_case`. The control is `tests/tools/test_a_level_return_with_nothing_short_opens_no_case_and_touches_no_other.py`.
It is red on a3136e29fa: the previous household's case took a face of 120 instead of 100, and the in-credit bill showed that
case's 100 as outstanding. A third leg is the partition control: a return that the desk found short still opens its case, at the desk's
figure. The publisher's 23:44 ledger was built from the shared tree with this fix in it, uncommitted. That ledger
matches mine case for case: 1,510 cases and 53,921 invoices, with no differences.

**The pre-registration, graded:**

| Filed prediction | Read | Held? |
|---|---|---|
| INV_OVERDUE_WITHIN_PAGE_BALANCE 1,724 → 0 | **80** of 6,076 steps (5 of 5 examples on level households) | **no** |
| INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE stays 0 | **194** of 1,139 (5 of 5 examples on non-level DD) | **no** (cause below, not step 2b) |
| Level-leg journeys open only the day after a level return | **159 of 655** on 741 all-level accounts | **no** |
| Level-leg journeys ≤ level returns | 655 vs 484; **105** accounts have more journeys than returns | **no** |
| INV_BILLED_EX_VAT ≤ 1 (filed 7 Nov for the first book after 8b6316995) | **0** | **yes** |
| Increment-1 reconcile, `differ` ≤ 2% | not computed: `level_dd_schedule_reconcile` reads `{"source": "post_loop_rebuild", "why": "dual-fuel offsets on: the loop does not ask them"}` | cannot tell |
| Page-balance cure reader 0–3; non-level byte-identical | not run. Three commits between 84f7fc8fe0 and this book move non-level DD (75f66f6521 among them), so byte-identity cannot isolate step 2b | cannot tell |

New and unexcepted: **INV_OVERDUE_WITHIN_BALANCE 71**. In 4 of its 5 examples a level household's journey opens the day
after a level return while the page balance shows nothing overdue. Verdict: **345 unexcepted breaches on 3 rows; the
publish is refused.**

**Why the level legs fail: the world and the page run two different schedules.** `DecisionPolicy.dd_review_offsets_dual_fuel_legs`
has been True for every standing policy since 3d518bdefc. Three docstrings still said "off by default", step 2b's commit
repeated that, and this commit corrects two of the docstrings. With offsets on, `level_dd_schedule_from_the_loop` hands
the page the **post-loop rebuild** (which carries the offsets). Phase 2b presents the world and the desk with
`InLoopLevelCollection`'s rows, which do not carry them. Example: PROS-2016-0207's page collects 20.07 on the 5th and
every collection succeeds. The desk opens on 13 Mar 2018 at 21.30, on its own schedule. The in-loop schedule is not
saved in the run output (`level_dd_collected_in_loop` stays in the phase 2b result), so I cannot yet say how many of
the 80 and the 71 are this split rather than something else. **Prediction:** with one schedule for world, desk and page,
INV_OVERDUE_WITHIN_PAGE_BALANCE and INV_OVERDUE_WITHIN_BALANCE fall to at most 5 on level households, and J1 holds on at least 95% of
openings.

**INV_PAYMENT_RECORD's 194 is a different defect, and a candidate is in hand.** C1's bill fell due on Sunday 8 May 2016,
and its DD was collected on Monday 9 May, the next Bacs processing day (75f66f6521). `payment_record` counts that as
"missed DD without a return". A collection on the next working day after a non-business due date is on time. Of
OCC-17ff099218d5's 50 payments, 9 are dated after their due date. I have not checked that all 194 are this case.

**Recommended next, one variable each:**
1. Make the schedule one schedule. Either phase 2b asks the book with the offsets, or phase 4c hands the page the
   loop's schedule whatever the offsets switch says. Save `level_dd_collected_in_loop` in the run output, so that the reconcile
   is computed and not skipped.
2. `generate_explore_cast.payment_record` (and any desk reading of due dates) reads a DD collected on the first
   Bacs processing day on or after its due date as on time. Count the 194 under that rule before building it.

## One schedule with the offsets on: phase 2b asks the offsets (worker, 9 Nov 2026)

**Which of the two, and why.** Phase 2b now asks the book with `dd_review_offsets_dual_fuel_legs` applied. The other
choice, handing the page the loop's schedule whatever the switch says, would have made world and page agree by
dropping the offsets from what every dual household is collected. Under SLC 27.8D the household's money moves:
a review the other leg's credit covers is not stepped up. Only this choice keeps that effect on what is actually
collected.

**What changed.**
- `InLoopLevelCollection(offsets_dual_fuel_legs=, still_supplied=)` asks the book over both legs as known at the
  cutoff. A leg that has left is billed and closed as a leaver.
- Phase 2b posts whole terms by start date, so the electricity term goes before the gas term of the same start.
  At the electricity review, the gas leg has therefore billed only to the end of the term before. The book reads
  "still ours" off a bill on or after the review, so it found the gas supply gone and offered nothing. A supplier
  knows it still supplies the gas leg, so `still_supplied` (a term of that leg still to post, or in hand) tells the
  book (`supplied_through`). Post-run, nothing passes it, so the post-loop book is unchanged.
- `StopNoticeBoard.observe` drops its cached bills for any cutoff later than a new row. Asking for the other leg
  before its term posted had cached an empty answer.
- `level_dd_schedule_from_the_loop` takes the loop's schedule whatever the switch says. The run output's
  `level_dd_collections` is that schedule, so the loop's rows are saved, and `level_dd_schedule_reconcile` is
  computed against the rebuild instead of being skipped. No second copy is written: when `source` is
  `in_loop` it would be byte-identical to `level_dd_collections`.

**Control.** `tests/simulation/test_a_dual_level_household_collects_one_schedule_with_the_offsets_on.py`.
- A dual household posted term by term. Its review sets a GBP 755.28 offset, which moves the electricity amount
  from 171.41 to 108.47. The loop equals the post-loop book on both legs, and the page takes the loop's schedule.
- Red on origin: `InLoopLevelCollection` takes no offsets argument.
- Partition control: with `still_supplied` off, the electricity leg misses its offset.
- With offsets off, the schedule is identical to the loop as it was built before.
- Five mutations, all red.

**Pre-registration for the first fresh book built at or after this commit** (written before any book carries it):
- INV_OVERDUE_WITHIN_PAGE_BALANCE **at most 5** and INV_OVERDUE_WITHIN_BALANCE **at most 5** on level households
  (80 and 71 on e50e7b8f68).
- J1 (a level leg's journey opens only the day after a level return) on **at least 95%** of level-leg openings
  (496 of 655 on e50e7b8f68).
- `level_dd_schedule_reconcile.source` is `in_loop`. `differ` is **at most 2%** of matched months, and each
  `only_*` is **at most 1%**: the increment-1 legs, first graded here.
- The post-loop book's `dual_fuel_offsets` count is within **10%** of e50e7b8f68's. The world's payments move,
  but the book is sized from bills.
- Single-fuel level households: the collection schedule is **byte-identical** to e50e7b8f68's on the same
  inputs, unless another commit moves them. If one moves, the board's cache was serving a stale answer
  somewhere off the offsets path, and that is a finding of its own.
- **Refuted if** either overdue row is above 20 on level households, or `differ` is above 5%. That would mean the
  split was not the main cause of the 80 and the 71.

## Recommended next 2, done: a DD collected on the next Bacs day is on time (seat, 9 Nov 2026)

**The count first, filed as the prediction for the fix.** On the e50e7b8f68 ledger (`/var/tmp/grade-e50e/ledger.json`),
with origin b97dcf8e15's `payment_record`: 194 accounts have missed DD > returns, matching the gate's 194. Every missed DD
bill on those accounts was sorted:

| missed DD bill on a breaching account | bills |
|---|---|
| due on a weekend or bank holiday, collected on the first Bacs processing day after it | **2,442** |
| due on a working day, collected later (after a return) | 86 |
| due on a non-working day, collected later than the first processing day | 28 |
| never paid | 18 |

**All 194 accounts are explained by the first row alone. Prediction: 194 -> 0, residual 0.** Script:
`/var/tmp/dd-bacs-count/count.py`.

**The fix.** `company/billing/collections_journey.last_day_to_pay(due, by_direct_debit=)` is the first England and
Wales working day on or after a DD's due date (`company.compliance.working_days`, the company's reading of the same
GOV.UK calendar 75f66f6521's `simulation/bacs_processing_day` reads; the company may not import the world's). For any
other method it is the due date (the knowledge page's GAP: no source read says a pay-on-receipt payment rolls).
`bill_missed` takes `by_direct_debit`, and `tools/generate_explore_cast.payment_record` passes it when the bill's ledger
rows are a DD's. Test: `tests/tools/test_a_dd_collected_on_the_next_bacs_day_is_on_time.py`. C1's Sunday 8 May 2016
due date collected Monday 9 May reads paid. That leg, the partition leg and the bank-holiday leg are red on b97dcf8e15.
The control, a DD collected Wednesday 11 May, reads missed before and after.

**Replayed on the same ledger.** INV_PAYMENT_RECORD's breaching accounts went from **194 to 0**, as predicted.
Book-wide, 2,442 bills moved from missed to paid: missed went from 6,595 to 4,153, missed DD from 2,729 to 287, and
returns held at 359. Bills due held at 47,534. On the full suite grade, no other row moved
(`/var/tmp/dd-bacs-count/grade_after.txt`). The verdict went from 345 unexcepted breaches on 3 rows to **151 on 2**:
INV_OVERDUE_WITHIN_BALANCE 71 and INV_OVERDUE_WITHIN_PAGE_BALANCE 80, both still recommended-next 1. The publish is still refused.

**The desk, measured, not changed.** Of 2,459 successful DD bills collected on the next processing day after an
off-day due date, the desk opened a "missed payment" journey the day after the due date on **9**. The baseline is 16
of 25,090 bills due and collected on a working day. The desk reads the balance, so a Monday collection mostly cures
the step it would open. `CollectionsDesk.advance` still dates `unpaid_on` from `missed_on(due)` with
`bill_paid_in_its_window` closing on the due date. That is the same misreading on a smaller scale, and changing it
moves the company's in-run behaviour. It needs a fresh run to grade, so it is filed as the next item rather than
folded in here. Prediction for that item: 9 -> 0 such openings, and no other journey count moves by more than 9.

**The desk, changed (2026-11-09).** The desk now reads a DD bill's `last_day_to_pay` too. The company knows which bills
it asked the bank to collect, because it submitted them: a DD `CollectionRequest`'s correlation id is the invoice ref
(`background/live_payment_triad.py`), so `PaymentObservationConsumer.note_collection_request` tells the desk
(`CollectionsJourneyDesk.note_bill_collected_by_direct_debit`). That bill's miss is dated from the first working day on
or after its due date, and `bill_paid_in_its_window` counts cash up to that day. Two places read it: the opener, and
the "further bill missed" re-offer. The second was not in the 9; it was found when mutating its window did not fire.
Tests: `tests/company/billing/test_the_desk_reads_a_next_bacs_day_dd_as_on_time.py`. A DD due Saturday and collected
Monday opens no journey and draws no re-offer. The same bill paid on receipt, or a DD collected Wednesday, still does.
Each of the three legs (consumer wiring, opener date, window) was reverted alone, and each turned the test red.
**Not yet graded on a run.** The prediction above stands as filed: 9 -> 0 openings, and no other journey count moves by
more than 9. The next fresh book grades it.

**Grade item drawn early (seat executor, 02:41 GMT 9 Nov).** `grade-the-desk-next-bacs-day-dd-on-the-next-book` was
drawn one minute after c915067a8 reached origin. No book carries it: the newest finished book is e50e7b8f68, and the
run in progress (`run_output_b9ad453df0_20261109T015606Z.json`, started 01:56) is built on b9ad453df0, which predates
the desk change. Nothing was graded and no run was started by hand. The premise is not spent. It is untested.

**The instrument, fixed before any post-fix book exists.** `/var/tmp/grade-desk-bacs/grade.py <ledger.json>`, run from a
worktree root, reads `collections_desk_journeys` against each DD bill's successful collection. On e50e7b8f68
(`/var/tmp/grade-desk-bacs/e50e_baseline.txt`) it reproduces the filed figures: 2,459 DD bills due on a non-working day
and collected on the next Bacs day; **9** have a `missed_payment` opener the day after the due date, **10** inside the
window (due, collection day]; 16 opened on bills due and collected on a working day; **0** `repayment_plan_reoffer`
rows fall in an off-day window. (Its working-day denominator is 5,475 DD bills collected on the day, not the 25,090
above, which counted every bill due and collected on a working day. The 16 is the same.)

**What grades it.** On the first book whose commit has c915067a8 as an ancestor: off-day openers in window **10 -> 0**
(the filed 9 -> 0 read day-after), off-day re-offers in window **0 -> 0**, the working-day 16 unchanged within its own
noise. The second leg, "no other journey count moves by more than 9", needs the b9ad453df0 book now running as its
comparator, not e50e7b8f68: b9ad453df0 changes the level-DD schedule the world collects. If any other world or company
commit lands between b9ad453df0 and the graded book (the closed-account close is in flight), that leg cannot be
attributed to c915067a8 and is reported as such. The 10 -> 0 leg reads this mechanism alone.

**Amendment, 2026-11-14: what the insulation change (e17ebc596) moves in the c915067a8 grade, before the book
exists.** This amendment is about e17ebc596 only. The first book carrying c915067a8 that is still ungraded (16 Nov) also
carries e17ebc596. The one-variable book A/B, e17ebc596^ against e17ebc596, same seed, neither arm carrying ceeefa5960 or 69866925b (`docs/staging/records/SEAT_RECORD_WHAT_THE_INSULATION_CHANGE_CAN_MOVE_IN_THE_16_NOV_PREREGISTRATIONS_2026-11-13.md`). Both arms carry c915067a8. The prediction above is kept as filed.
- **The 10 → 0 leg, off-day openers in window: fabric cannot move it on this run.** It reads 2 at both commits, and
  off-day re-offers read 0 at both. Its "→ 0" stands. A read, not a grade: both arms already read 2, not 0, so a
  miss on 16 Nov is not fabric.
- **"No other journey count moves by more than 9": fabric moves it, so this leg cannot be attributed on the 16 Nov
  book.** Fabric alone moves `arrangement_offered` 3,014 → 2,888 (−126), `repayment_plan_reoffer` 2,247 → 2,155 (−92),
  `missed_payment` 1,798 → 1,752 (−46) and `write_off` 280 → 266 (−14). Report that leg as unattributable.

**Amendment, 2026-11-14 (later, still before the 16 Nov book): can S6b or the statement walk move it too?** **Not directly, for both legs.** The off-day opener and re-offer counts and the journey counts come from the desk's collection journeys. They do not read the close refund log's paid days, which are the only thing S6b re-dates (`docs/design/REPAYMENT_POSTING_AREA_MAP_2026-11-14.md` s.8). Nor do they read `statement_export`, the only thing 84a44b51c changes. One indirect route exists: a set-off is dated by its refund's paid day (`set_offs_from_refund_log`, read by the ledger walk at `tools/generate_billing_ledger.py:474`), so S6b re-dates the debt leg's walk if it moves a refund that carries a set-off. On r98 it moved 3 refunds and none carried a set-off. So the unattributable leg stays unattributable because of fabric alone. These two changes are not expected to add to it.

## The b9ad453df0 book, the first carrying "one schedule", graded: refuted, and the main cause is a new defect (worker, 9 Nov 2026 ~05:00 GMT)

`run_output_b9ad453df0_20261109T015606Z.json` (finished 03:39Z). Graded at origin 0f074c607c, whose commits after
b9ad453df0 change only the company desk (c915067a8) and readers. The tools are the same as e50e7b8f68's: the ledger from
`/var/tmp/b3ce-grade-scripts/ledger.py`, the suite from `grade.py`, and `/var/tmp/grade-e50e/level_legs.py`. To list every
breach rather than five examples, `/var/tmp/grade-b9ad/all_breaches.py` and `split.py` were used. Scratch: `/var/tmp/grade-b9ad/`.

**The pre-registration, graded:**

| Filed prediction | Read | Held? |
|---|---|---|
| INV_OVERDUE_WITHIN_PAGE_BALANCE ≤ 5 on level households | **241** | **no** (refuted: over 20) |
| INV_OVERDUE_WITHIN_BALANCE ≤ 5 | **57** | **no** (refuted) |
| J1 on ≥ 95% of level-leg openings | **122 of 945** | **no** |
| reconcile `source` is `in_loop` | `in_loop` | yes |
| `differ` ≤ 2% of matched months | 1,169 of 16,517 (**7.1%**) | **no** (refuted: over 5%) |
| each `only_*` ≤ 1% | only_in_loop 176 (1.0%); only_post_loop **11,858 of 29,544 (40%)** | **no** |
| INV_PAYMENT_RECORD 0 (0f9ebbad56, read at origin) | **0** | yes |

Verdict: **299 unexcepted breaches on 3 rows (57 + 241 + 1 INV_DD_COLLECTIONS_EQUAL_TO_THE_BILL), so the publish is refused.**

**Why: the loop's schedule lost the gas leg of almost every dual household.** The loop's schedule holds 459 legs. e50e7b8f68's
rebuild held 766. The 307 legs it lost are all gas legs, and 291 of them have an electricity leg that is in the loop's
schedule. Cause: `InLoopLevelCollection._opening_of` cached its answer even when the leg had no records yet. With the offsets
on, the electricity leg's ask reads the gas leg's opening amount before the gas term has posted (phase 2b posts the
electricity term first). It got `None`, cached it, and the gas leg then returned `None` at every ask of its own. It collected
no level amount for the whole run, and the world and page billed it per bill while its electricity leg ran level. With
offsets off, the sibling is never asked, so this is new in b9ad453df0. The 22 dual gas legs that survived are households
whose gas term posted before the electricity leg's first ask. The step-2b control seeded `_opening` and never reached
`_opening_of`, which is why it was green.

**Attribution, from the full breach lists (households whose gas leg was dropped, against the rest):**

| Row | dropped-gas households | the rest |
|---|---|---|
| INV_OVERDUE_WITHIN_PAGE_BALANCE | 233 steps on 19 households | **8 steps, 1 household** |
| INV_OVERDUE_WITHIN_BALANCE | 48 on 37 | **9 on 9** |
| J1 openings the day after a level return | 92 of 886 | **30 of 59** |

The `differ` sample (OCC-01f752dc9316: 34.96 in the loop against 34 in the rebuild, reversed by 0.96 the next year) is also
a dropped-gas household: without the gas leg, its offsets differ. The run does not save the rebuild per row, so **I cannot
yet say** how much of the 1,169 is this.

**The fix (this commit).** `_opening_of` no longer caches a `None` given before the leg has records. Control:
`test_a_leg_asked_by_its_sibling_before_its_first_term_still_collects_its_own_level_amount` in
`tests/simulation/test_a_dual_level_household_collects_one_schedule_with_the_offsets_on.py`. It goes through `_opening_of`
with offsets on. Both legs must equal the post-loop rebuild, and its partition leg requires offsets off to collect gas. On
origin it is red: the gas leg collects nothing. The other four tests in the file are unchanged and green.

**Pre-registration for the first fresh book whose commit carries this fix** (written before any book holds it):
- The loop's `level_dd_collections` holds at least **740** legs, and `only_post_loop` is at most **2%** of post-loop months.
- INV_OVERDUE_WITHIN_PAGE_BALANCE at most **15** and INV_OVERDUE_WITHIN_BALANCE at most **15**: this book's residual
  (8 and 9), with room for the restored legs.
- `differ` at most **3%**.
- J1 is not predicted. On the households this defect did not touch, it holds on 30 of 59. Those 29 off-return openings are
  unexplained, and they are the next thing to read once the gas legs are back.
- **Refuted if** either overdue row is above 40, or `only_post_loop` is above 5%. That would mean something other than the
  opening cache is still splitting the schedules.

The next-Bacs-day desk grade (c915067a8, above) also needs a fresh book. A book built after this commit grades both, but its
"no other journey count moves by more than 9" leg cannot then be attributed to c915067a8 alone. Its 10 -> 0 leg still can.

## The third refusing row is the same defect: INV_DD_COLLECTIONS_EQUAL_TO_THE_BILL's Leg A, attributed (worker, 9 Nov 2026 04:52 GMT)

The b9ad453df0 book refuses on three rows. The section above attributes two of them. The third,
INV_DD_COLLECTIONS_EQUAL_TO_THE_BILL_WITHIN_THE_VARIABLE_DD_SHARE, reads 18,296 of 34,578 graded collections tracking
the bill (0.529, bound 0.30, 928 accounts), where the b3ce2a4e73 book read 0.217 after N20. It had no attribution or
prediction yet. The split uses the runner's own Leg A arithmetic and the same "dropped" set as `split.py` (in e50e7b8f68's
schedule, missing from b9ad453df0's). Script: `/var/tmp/grade-b9ad/leg_a_split.py`. It reproduces the gate's 18,296 / 34,578
exactly.

| legs | tracking / graded | share | accounts |
|---|---|---|---|
| dropped gas legs | 10,804 / 10,882 | **0.993** | 297 |
| the same households' electricity legs (level) | 0 / 10,505 | 0.000 | 281 |
| every other leg | 7,492 / 13,191 | 0.568 | 350 |

The dropped gas legs were billed per bill, so almost every collection they made equalled the bill. That is the whole
breach. If those legs are left out, the book reads 0.316, and its Wilson lower bound over 631 accounts sits below 0.30, so the
row would only be flagged. If they come back level, they contribute about 0 tracking, like their electricity siblings, and the book
reads about 7,492 / 34,578 = 0.217. That is the N20 reading.

**Pre-registration for the first fresh book carrying 1936f66251** (filed before any such book exists; the sim-runner's next
run starts about 05:09 GMT at HEAD 1936f66251):
- INV_DD_COLLECTIONS_EQUAL_TO_THE_BILL Leg A between **0.17 and 0.27**, so the row is FLAGGED, not BREACHED.
- **Refuted if** it reads above 0.30. That would mean some gas legs are still billed per bill under the level schedule. Read it
  beside this section's `only_post_loop` leg.

So all three refusing rows of this book, and the 11 publish-gate failures of this wedge episode, have one cause, already fixed on
origin. The gate keeps re-grading a book built before the fix, and that book cannot pass. **No test is red, and none can
be repaired.** The wedge clears, or fails with a new named cause, on the 05:09 run's book. That book should finish about 08:00
GMT, going by the last run's 2 h 50 min. No dated exception is proposed, for the reason under "Not recommended" above.

## The 298149a1fc book, the first carrying 1936f66251, graded, and the correctness-stretch exit test on it: not met (worker, 9 Nov 2026 ~07:10 GMT)

`run_output_298149a1fc_20261109T050900Z.json` (finished 06:57Z; 298149a1fc descends from 1936f66251). Graded from a clean
`git archive` of 0f4c93eea4 (no shared-tree edits) with the same scripts as the b9ad453df0 grade, copied to
`/var/tmp/grade-2981/` (`run.sh`). **The instrument was checked first:** run on the b9ad453df0 book, it reproduces the filed
299 unexcepted breaches on 3 rows, Leg A 18,296 / 34,578 and 459 legs exactly (`/var/tmp/grade-2981/control-b9ad/`).

**The two pre-registrations above, graded:**

| Filed prediction | Read | Held? |
|---|---|---|
| loop schedule holds ≥ 740 legs | **766** | yes |
| `only_post_loop` ≤ 2% of post-loop months | **0** of 29,546 | yes |
| `differ` ≤ 3% | 60 of 29,546 (0.2%) | yes |
| INV_DD_COLLECTIONS_EQUAL_TO_THE_BILL Leg A in 0.17 to 0.27 | **0.216** (7,494 / 34,638, 929 accounts) | yes: FLAGGED, not breached |
| INV_OVERDUE_WITHIN_PAGE_BALANCE ≤ 15 | **80** of 6,077 steps, on 6 households | **no**: refuted (over 40) |
| INV_OVERDUE_WITHIN_BALANCE ≤ 15 | **71** of 1,086 openings, on 70 accounts | **no**: refuted (over 40) |

Verdict: **151 unexcepted breaches on 2 rows; 8 excepted. The publish is refused** (the publisher's own grade of this
book had not run at 07:02; this is the same runner, and the instrument check above says it should match).

**The gas-leg defect is fixed**, and so is the third refusing row. **The refutation clause's reading is itself refuted.** It said
an overdue row above 40 "would mean something other than the opening cache is still splitting the schedules". The
schedules are not split: `only_post_loop` is 0 and `differ` is 0.2%. Both rows read exactly what they read on the
e50e7b8f68 replay (71 and 80). There they were attributed to two schedules, and that attribution is withdrawn: one schedule
gives the same counts. The residual on b9ad453df0 was 9 and 8 on the households the dropped legs did not touch. The
restored level gas legs bring the rest.

**INV_OVERDUE_WITHIN_BALANCE 71: the row cannot see an instalment default.** Classified per opening
(`/var/tmp/grade-2981/ab_INV_OVERDUE_WITHIN_BALANCE.json`):
- **70 of 71** open within 7 days after a failed level instalment on the household. On **40** of them the opening
  overdue equals the failed instalment(s) to the penny.
- **1** (PROS-2016-0370, 16 Jan 2017, GBP 6.91) has no return in the 7 days before. Its overdue is the gas bill (33.73)
  less the instalment (26.82): seasonal debit dunned, the defect this finding is named for.

By the definition this finding adopted from Ofgem (letter of 20 Sep 2011, App. 2 para 2.8, on
`payments_and_direct_debit_2026-10-25.md` "What is owed"), a DD customer who defaults on a payment is in debt. So these
70 journeys are owed. The row's second leg asks whether "a bill was unpaid past its due date". On a level account
the debt is the missed instalment, and the bill is settled against the schedule. **The row is wrong for level households,
not the desk.** The one exception is the desk.

**INV_OVERDUE_WITHIN_PAGE_BALANCE 80: 6 households, 53 steps on SYN-2016-021.** All 6 hold a level DD leg. Three
pay the other fuel by prepayment or standard credit (SYN-2016-021's electricity is prepayment, its gas is level DD).
The printed overdue (for example 40.65) is above the sum of both fuel pages' balances (26.67). **I cannot yet say** which
side is wrong. Candidate: the desk caps the shortfall by one leg's debit, `min(shortfall, debit balance)`, and the
row sums both pages, where a prepayment or credit page can hold a credit. Not traced.

**The exit test (ruling of 26 Oct), on this book:**
1. *Suite on the full book with zero unexplained breaches*: **not met.** 151 unexcepted on 2 rows. 70 of the 71
   are explained above as a row defect, but no dated exception names them yet, and 80 are not explained.
2. *Eight Explore slots filled validly or honestly empty*: **not graded on this book.** The cast is only written by
   a publish, and this one is refused. One check on the b9ad453df0 cast was refusing the publish two cycles running (the
   per-fuel tariff label). That was a parser defect, not a page error, and it is fixed at 0f4c93eea4.
3. *One cold read finds no new class*: **not run.** Leg 1 fails, so the exit cannot be met on this book. The ninth
   cold read (af31e73fa7) did find a new class: the closed-account balances finding.

**Recommended next, one variable each:**
1. **INV_OVERDUE_WITHIN_BALANCE's second leg reads an instalment default on a level household.** A journey on a level
   leg is owed when an instalment presented before the opening has failed and has not been made good. Every other
   household keeps the bill reading. Prediction for a re-grade of this same book (no run needed, since the row only
   reads): 71 -> 1, and the 1 is PROS-2016-0370. The row is the suite's, written blind from the Knowledge pages. So the change
   cites the page's corrected "What is owed" paragraph and is a factual correction to match it. It is not a new reading of the
   code.
2. **Trace SYN-2016-021's 53 steps**: compare the desk's overdue against each fuel page on the same day, before choosing
   which side moves.

## The desk-cure ledger leg and the BSCP504 rows on the step 2b books (worker, 9 Nov 2026 ~07:40 GMT)

Drawn as `grade-the-first-book-carrying-level-dd-step-2b-a3136e29f`. **Most of the premise was already spent.** The first
book carrying step 2b, e50e7b8f68, was graded above (~23:50 8 Nov), and so were b9ad453df0 and 298149a1fc. Two legs the
item names had not been graded on any step 2b book: the desk-cure ledger leg (5b32ecb0f4) and the BSCP504 rows. Both are
graded here. Scratch: `/var/tmp/grade-2981-cure/`. Code: the clean `git archive` of 0f4c93eea4 at `/var/tmp/grade-2981/code`.

**The instrument was checked first.** `leg.py` and `split.py`, run on the 84f7fc8fe0 ledger at this code, reproduce the filed
134 and 85 exactly.

| Filed prediction | 84f7fc8fe0 (control) | e50e7b8f68 | 298149a1fc | Held? |
|---|---:|---:|---:|---|
| Cures over a balance owed past due, level legs capped at the shortfall: 0 to 3 | 85 | **348** | **347** (109 accounts; 192 level at cure) | **no** |
| Uncapped reading | 134 | 352 | 351 | (not filed) |
| No account that left level DD carries a page debit with every bill paid (6 today) | 6 accounts | not computed | **1** account (SYN-2016-299, GBP 8.63, 3 cures) | **no** |
| SYN-2016-550 reads 0 | 0 | not computed | 0 of 6 cures | yes |

The prediction is refuted. The count went up, not down. Split by shape on 298149a1fc: **88** level-at-cure cures and **151**
cures on 19 accounts that later left level DD have an invoice due by the cure still unpaid at run end. Trace: SYN-2016-549's
electricity instalment fails on 4 Apr 2018. The desk cures when May's instalment is collected, and April's GBP 45 is still
outstanding at run end. **104** level-at-cure cures have nothing unpaid at run end. I cannot yet say whether those are the
desk or the reader, because the reader was written before step 2b. Following this leg's own clause, the defect is
now its own finding:
`WORKER_FINDING_A_LEVEL_DD_JOURNEY_CURES_ON_THE_NEXT_INSTALMENT_WHILE_THE_MISSED_ONE_IS_NEVER_MADE_GOOD_2026-11-09.md`.
SYN-2016-550's DIRECTION row stays open on that finding, as this leg said it would.

This also bears on INV_OVERDUE_WITHIN_BALANCE's recommended re-reading above ("owed when an instalment presented before the
opening has failed and has not been made good"). On these books such an instalment is often never made good at all. So
the re-reading would pass the 70 openings, and it would also show that the debt they open on outlives their cure.

**The BSCP504 rows** (`records/WORKER_PREREG_THE_BSCP504_CEILING_ON_THE_NEXT_FRESH_BOOK_2026-11-07.md`), on 298149a1fc. All
three homes are in the book.
1. Exception queue: **0** entries. (1) holds.
2. No ceiling hold under the screen: holds, because nothing is queued.
3. INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL: **0 of 5,671**. Holds.
4. INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE, filed at most 1: **0 of 1,302**. Holds, as it did on e50e7b8f68.
5. INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER: 7 breaches. No prediction was filed. None is on the three homes.

The BSCP504 prereg is fully graded and can retire.

## The tenth cold read waits on this finding (2026-11-09, worker tick)

The direction item `the-tenth-cold-read-carries-the-seat-named-checks` says to run "on the first book that passes item 1's
gate" and "if item 1's book fails, this waits". Item 1's book, `run_output_298149a1fc_20261109T050900Z.json`, was graded
by 7e8dfb553e and failed: 151 unexcepted breaches on INV_OVERDUE_WITHIN_BALANCE (71) and INV_OVERDUE_WITHIN_PAGE_BALANCE
(80). At 08:50 GMT no newer book is in `docs/reports/` and no run is in flight. So no read was run. Running it on this
book would grade household pages that the gate has already refused, and that would not count as the exit test's leg.

The read becomes ripe when a book carrying the fix for this finding's overdue rows passes the gate. The fix is also needed
for `WORKER_FINDING_A_LEVEL_DD_JOURNEY_CURES_ON_THE_NEXT_INSTALMENT_WHILE_THE_MISSED_ONE_IS_NEVER_MADE_GOOD_2026-11-09.md`.
The direction item is not released. Releasing it would tombstone the item, and the read is still owed. The four
seat-named checks stay with it unchanged: meter identity, read repetition, payment method on the bill date, and a
closed account's balance a year after its last bill.

**Still held, 10:50 GMT 9 Nov (worker tick).** The 9d7dcfc19c book (`run_output_9d7dcfc19c_20261109T085204Z.json`)
finished at 10:44. The publisher graded it at about 10:50 and refused it on the same two rows, at the same counts:
INV_OVERDUE_WITHIN_BALANCE 71 and INV_OVERDUE_WITHIN_PAGE_BALANCE 80. The seat filed at 09:22 that this book "can only
fail the same way" (DIRECTION.yaml `not_now`). That prediction **held**, to the count. The book's commit predates
d8264b525e (the level-DD cure fix) and the close still landing, so it carries neither. The read waits on H46's book,
the first one carrying both, and it is not drawn before 16:00 GMT today. That is the soonest such a book could finish:
the close is still landing, and a run takes about two hours.

**Still held, 16:30 GMT 9 Nov (seat executor).** The 505df564e3 book failed the gate: the overdue rows went up, not
down (see the cure finding, ~15:40). The next candidate is `book-4dee9854a4`, launched at 16:07 with about two hours
to run. Its own filed prediction is that the 320 still-level page rows do not fall, so it is not expected to pass
either. This read stays unrun and stays claimed for the first book that passes. The seat used the idle time on the
director's UKDS notice instead (`advisor/done/DIRECTOR_NOTICE_THE_UKDS_MICRODATA_IS_IN_UKDS_AND_YOURS_TO_READ_2026-11-09.md`).

## INV_OVERDUE_WITHIN_BALANCE read on the schedule: pre-registration (seat executor, 9 Nov 2026 ~23:40 GMT, filed before the new reader exists)

Drawn as `the-overdue-row-reads-a-level-dd-household-on-its-schedule` (recommended next 1, above). The claim
`page-balance-omits-credit-on-closed-accounts` names the same knowledge page. It is different work: the ledger's
`balance_gbp`, in `tools/generate_billing_ledger.py`. It touches neither this row nor the runner, so this is not one item
under two ids.

**What the row reads.** A level household is one with a leg whose latest bill that asked something, issued by the
opening, was met by a level collection (`payments[].level_dd`). This is the export's view of `arrears_engine.on_level_dd`,
read from the ledger's own payment record, not by calling the code under test. Such a household is owed when a level
instalment presented before the opening was returned and has not been made good. Made good means cash that is not a
scheduled instalment, landed on that leg after the return and by the opening, of at least the instalment. Every other
household keeps the bill reading.

**Found while reading the premise, before any count.** The 4dee9854a4 classification (`/var/tmp/grade-ondd/classify.txt`)
splits the 106 "still level" breaches into 49 that collect level after the opening and **57 that never collect level
again**. On the first of those, C2, there is no returned collection anywhere in the record (`level_dd` failed = 0). Its
electricity leg ends with bill 32 (31 Mar 2018) and its gas leg with bill 56 (4 Apr 2018). Each was met by the leg's last level
collection, of GBP 35.70 and GBP 47.49 against faces of GBP 49.23 and GBP 87.01. The journey opens on 3 May 2018.
`on_level_dd` reads C2 as level on that day because the last bill on each leg is a level-paid one. In fact the scheme
has ended, and what is owed is the debit it left. That is owed once demanded ("Leaving level direct debit with a debit",
on the same page). So the literal reading the item names ("an instalment ... has failed") would keep these 57 as breaches
of the row, when they are the desk acting correctly. Two readings are therefore pre-registered and both are run:

- **A, literal.** Level household: owed only when a returned instalment has not been made good.
- **B, A plus the leaver.** A level leg with no level collection after the opening, where its own bills less the
  cash and credit landed on it leave a debit at the opening, is owed that debit. Ofgem counts the debtor who "defaulted on
  one or more payments". A debit that has been demanded and not paid is that. Whether 28 days have passed since the demand
  is a timing question for another row, and it is not graded here.

**Predictions (filed before the reader exists).**

| Ledger | Today | A predicted | B predicted |
|---|---:|---:|---:|
| `/var/tmp/grade-ondd/ledger.json` (4dee9854a4) | 129 | 60 to 85 (the 49 clear to at most 5; the 57 leavers stay; most of the other 23 stay) | at most 35 (the 49 and at least 50 of the 57 clear; at least 15 of the other 23 stay) |
| 9d7dcfc19c control (`/var/tmp/grade-ovrow/ledger_9d7d.json`, built at this origin from `run_output_9d7dcfc19c_20261109T085204Z.json`) | 71 | at most 5 (70 of 71 open after a returned level instalment, as on 298149a1fc; PROS-2016-0370's GBP 6.91 seasonal debit stays) | at most 5, and the same as A or lower |

If B clears fewer than 50 of the 57, the leaver clause is the wrong reading and the row lands as A, with the residual
filed. The control's "today" figure is re-read on the regenerated ledger before anything else is run. If it is not 71,
that is reported, and the predictions are graded against what it does read.

### Graded (seat executor, 9 Nov 2026 ~00:10 GMT 10 Nov; scripts `/var/tmp/grade-ovrow-scripts/`, results `/var/tmp/grade-ovrow/`)

Both "today" figures reproduced on the regenerated ledgers before anything else was read: **129** and **71**.

| Ledger | Old | A filed | A read | B filed | B read | Held? |
|---|---:|---|---:|---|---:|---|
| 4dee9854a4 | 129 | 60 to 85 | 84 | at most 35 | 25 | **A held, B held** |
| 9d7dcfc19c control | 71 | at most 5 | **23** | at most 5 | **23** | **both fell** |

**Why the control fell, and the correction.** All 23 are journeys that passed the bill reading and breach the new
one. They sit on five households (SYN-2016-334 has 15 of them) that mix a level leg with a leg paying its own bills. The
journey opened on the other leg's unpaid bill. The reader took the household as level when any leg was, as
`on_level_dd`'s `any` does. That is the wrong unit for the row. The journey is the billing account's, so it is owed when
**either leg** has defaulted, each leg read on its own terms. This is a second variable, chosen after the control's
answer was known. So the per-leg figures below are **measured, not predictions held**:

| Ledger | Old | Per-leg A | Per-leg B (landed) |
|---|---:|---:|---:|
| 4dee9854a4 | 129 | 64 | **5** |
| 9d7dcfc19c control | 71 | 0 | **0** |

- **PROS-2016-0370**, which I predicted would stay, clears. Its gas level instalment of GBP 26.82 was returned on
  12 Dec 2016 and never made good, 35 days before the opening. The earlier classification looked back only 7 days, so it
  missed this. The row is right to call the household owed. Whether GBP 6.91 was the right figure is a question for the
  page row, not this one.
- **The sub-predictions on 4dee9854a4.**
  - The 49 that go on collecting clear to at most 5: **held**. None remains.
  - At least 50 of the 57 leavers clear: **held**. At most 5 remain.
  - At least 15 of the other 23 stay: **fell**. None stays. Per leg, each had a level leg that had defaulted.
- **The 5 that remain on 4dee9854a4 are the desk's, not the row's:** PROS-2018-0173 (19 Apr 2019, GBP 1.16),
  PROS-2023-0377, SYN-2016-287 (20 Sep 2018, GBP 0.27), SYN-2016-471, and SYN-2016-496 journey 1 (17 Aug 2018,
  GBP 45.48). Each is a level leg whose last level collection was before the opening, with nothing returned. Its
  own bills less what landed leave no debit, and its other leg, if it has one, has paid every bill. The desk opened
  "a bill is unpaid past its due date" on a leg that had defaulted on nothing. This is the PROS-2016-0370 shape from
  298149a1fc, a scheme-end residue dunned as debt. It belongs with
  `WORKER_FINDING_A_LEVEL_DD_JOURNEY_CURES_ON_THE_NEXT_INSTALMENT_WHILE_THE_MISSED_ONE_IS_NEVER_MADE_GOOD_2026-11-09.md`'s
  closing-statement build. The row stands as a breach on them, and no exception is filed.

**Control.** `tests/tools/test_the_overdue_row_reads_a_level_leg_on_its_schedule.py` asserts the partition first. A level
leg that owes, a level leg that does not, a bill leg that owes and a bill leg that does not each grade as they should.
Then: made good, never a bill face, an ended scheme's debit against its credit, and per leg. All five mutations fire:
made good ignored, no ended-scheme clause, no level reading, the ended-scheme clause on every level leg, and the
household read as level.

**Forward prediction (filed now, for the first fresh book graded at or after this commit, with no desk change to
level journeys in between):** INV_OVERDUE_WITHIN_BALANCE reads **at most 10**, and every breach is a level leg with
nothing returned and no debit at the opening. If it reads more, the row's level reading is wrong somewhere this
control did not reach.

**Recommended next:** the 5 residuals go to the closing-statement build. Gating a leaver's opening on a demand unpaid
28 days should clear them. The row is not widened to pass them.

## The forward prediction on the 78f82e4242 book: fell (5 -> 60), and the cause is the row's reading of a leaver (worker, 10 Nov 2026)

The drawn item (`level-dd-scheme-end-residue-dunned`) asked for the 5 residuals above to be cleared. I re-measured
the premise first, with the same runner on both book ledgers (`/var/tmp/cap-arm/ledger.json` and
`/var/tmp/capgrade/out/ledger.json`; scripts `/var/tmp/lvlres/`). The 4dee9854a4 cap-arm still reads 5. The
78f82e4242 book reads **60**. So the forward prediction above (at most 10, each a level leg) **fell**. As that
prediction said it would mean, the row's level reading was wrong somewhere the control did not reach.

**What it was.** dea1c34fd (world side) takes a month the world settled on its face off the level schedule. So a
leg whose last month was settled on its face now reads as having *left* level, because its latest bill that asked
something was not met by a level collection. The row then read that leg on its bills only. Every bill the scheme
had covered was met by its collection, so the scheme's debit read as paid. C7 shows the shape: GBP 108 a month was
collected against bills of GBP 120 to 163, the face-settled final bill was issued on 1 Jul 2019, and the desk opened
on 30 Jul at GBP 66.67. That is the closing statement's 28-day term, exactly as `left_level_asks` builds it. The desk
journey is the same on both books. Only the row's reading moved. All 60 were "nothing overdue" (read as not level),
including the original 5.

**The fix (the row, not the desk).** `_left_level_owed`: a leg that presented a level collection by the opening
but whose latest asked bill was not met by one has left. It left on the issue date of the first such bill after
its last level-met bill. It owes its debit (bills less what landed, by the opening) once the closing statement is
due, `LEFT_LEVEL_TERM_DAYS` = 28 after leaving. That term comes from the knowledge page "Leaving level direct debit
with a debit": the licence's 28-day demand clock and Budget Energy's four weeks. The term is part of the reading.
Without it, both residuals below would pass.

**Measured after the fix, not predicted:** 78f82e4242 **60 -> 2**. 4dee9854a4 cap-arm 5 -> 5 (unchanged, as it
must be: the clause reads only legs that have left). 9d7dcfc19c control 0 -> 0. Four of the original five
(PROS-2018-0173, PROS-2023-0377, SYN-2016-287, SYN-2016-471) clear on 78f82e4242. Their last month is now
face-settled, so their scheme debit reappears and is past its statement's term.

**Control:** `test_a_leaver_owes_its_schemes_debit_once_the_closing_statement_falls_due` checks three things: owed
after the term, not owed within it, and never owed on a credit. Three mutations fire: the clause dropped, the term
dropped, and the debit test dropped.

**The 2 that remain are the desk's, and both open inside the closing statement's term:**
- **SYN-2016-496 journey 1** (17 Aug 2018, GBP 45.48, "61 days overdue", opened straight onto final notice). The gas
  leg was level at GBP 18 against bills of GBP 12 to 32, and its final bill was issued on 10 Aug. The electricity
  leg was never level and paid every bill. 61 days before the opening is 17 Jun, the due date of electricity bill
  47807, which was paid on 17 Jun. This is the same journey, with the same figures, on the cap-arm.
- **SYN-2016-007** (24 Jan 2019, GBP 9.20, "1 day overdue"). The electricity leg collected GBP 38.01 four times
  against bills totalling GBP 137.26, so it stood GBP 14.78 in credit. Its final bill of GBP 9.20 was issued on
  9 Jan, due 23 Jan, and settled on its face on 23 Jan. The gas leg left on 23 Jan with a GBP 57.61 debit whose
  statement was not due until 20 Feb.

Both are two-leg billing accounts closing on small final bills. On each, the journey's figure matches neither leg's
statement. **Hypothesis, not tested:** the desk's account-level walk lets one leg's scheme shortfall land on the
other leg's on-receipt bills, which are then aged from their own due dates. This cannot be the whole story: many
of the 58 that cleared are two-leg accounts too. **I cannot yet say** which branch of `left_level_asks` /
`collections_journey` produces these two. The next step is to replay these two accounts through the desk on the
78f82e4242 book.

**Not graded here:** INV_OVERDUE_WITHIN_PAGE_BALANCE. It needs the printed pages (`--printed`), and no published
set carries this book.

**Forward prediction (filed now, for the first fresh book graded at or after this commit, with no desk change to
leavers in between):** INV_OVERDUE_WITHIN_BALANCE reads **at most 5**. Every breach is a journey opened within 28
days of a leg leaving level, on a two-leg account.

## The 2 desk residuals replayed: one leg's scheme debit landed on the other leg's paid bills (worker, 10 Nov 2026)

Drawn as `left-level-journey-opens-inside-the-statement-term`. Re-measured first: 189b32460e (the cited commit) is on
origin and its 2 residuals are still the desk's, so the premise stands. The replay script
(`/tmp/lvlreplay/replay.py`) rebuilds each billing account's desk ledger from the 78f82e4242 book's ledger
(`/var/tmp/capgrade/out/ledger.json`). Bills are `<leg>::<invoice>`. Cash is `payobs:<leg>::…`, as the triad's
correlation ids make it. The script then calls `arrears_engine` directly.

**The hypothesis held, and the branch is `left_level_asks`.** The unchanged code reproduces both journeys to the
penny. SYN-2016-007 opens on 24 Jan 2019 at GBP 9.20, 1 day overdue. SYN-2016-496 opens on 17 Aug 2018 at GBP 45.48,
61 days overdue. The walk before the day of leaving met every bill from one account-wide pool, oldest first. The gas
leg's scheme debit therefore used up cash the electricity leg had paid for its own bills, and the newest electricity
bills came out unpaid, each aged from its own due date. On 007 that was the final bill collected on its due date. On
496 it was bill 47807, paid on 17 Jun by standing credit.

**Two fixes were tried first and refuted by the replay, recorded so neither is tried again:**
- *On-receipt bills first:* this hid PROS-2018-0222's electricity final bill, whose own collection failed on 27 Aug 2019.
  That is a real default.
- *An on-receipt bill keeps cash that paid it within its window* (`bill_paid_in_its_window`): 496 stays, because its
  July electricity bill was paid 4 days late, on 19 Jul. That cash went back into the pool.

**The fix: cash meets its own leg's bills first** (`arrears_engine.cash_leg`). A crossing's reference starts with the
leg. A direct debit is referenced by the invoice it collects. A push payment is referenced by the leg's account, which
is invoice-ambiguous by design but not leg-ambiguous. What names no leg, plus any leg's leftover, then meets what
remains, oldest first. Knowledge: the new section "The debit a leaver owes is its leg's" on the payments page.

**Measured on the replay over all 160 openings made while off level on the 78f82e4242 book (not a prediction):** the old
code reproduces an overdue at all 160. The new code clears **5** and adds **0**:
- SYN-2016-007 and SYN-2016-496, the two residuals.
- SYN-2016-182: the gas final bill's collection failed, but that leg stood GBP 23.94 in credit.
- PROS-2017-0056: the same shape, GBP 14.03 in credit.
- SYN-2016-376: the old opening aged the gas debit from electricity bill 41969, which was paid on its due date. The first
  real miss (41970, due 20 Feb 2018) opens a day later.

The row called those last three owed, because it reads a leg's bills leniently after a failure. None of the three is a
row breach on either code.

**Control:** `tests/company/billing/test_a_leavers_cash_meets_its_own_legs_bills_first.py` asserts the partition
first: a paid own-leg bill is not overdue, and the same bill with its collection returned is. It then checks the
statement and the netting of surplus and unnamed cash. Three mutations fire: no leg attribution (3 fail), a leg's
surplus not pooled (1 fails), and own cash not used up (3 fail).

**Found, not fixed (GAP on the payments page):** the desk dates the statement from the *account's* leaving, which is
its last level leg. The page and the row date it per leg. SYN-2016-345 shows the gap: its electricity statement was due
on 24 Jan 2018, the account's on 15 Feb. Neither walk breaches the row there, but the next leaver build should date
each leg's statement from that leg's own leaving.

**Forward prediction (filed now, for the first fresh book graded at or after this commit):** INV_OVERDUE_WITHIN_BALANCE
reads **at most 2**. No breach is a journey whose opening figure is an own-leg bill paid by that leg's cash. If the
reading is higher, the per-leg walk misses a shape the 160 replayed openings did not contain.

## The stop condition fired: the next level-DD step is the area's map, not another fix (worker tick, 10 Nov 2026 ~19:00 GMT)

The director's 10 Nov steer asks that failure feed a loop that changes how we work
(`docs/staging/advisor/done/DIRECTOR_STEER_EVERY_FAILURE_FEEDS_A_LEARNING_LOOP_THAT_CHANGES_HOW_WE_WORK_2026-11-10.md`),
and names this area as the first case. A census of every graded prediction in this finding and its sister
(`WORKER_FINDING_A_LEVEL_DD_JOURNEY_CURES_..._2026-11-09.md`), 8 to 10 Nov: **80 graded, 34 missed. 18 missed
because our model of our own code was wrong, 8 because the reader was, 0 because we misread the domain.** The miss
rate did not fall over the three days. The insight and its prediction are W1 in `docs/institutional/ways_of_working.md`.

**So, from this commit:** no further level-DD fix is drawn until the map below exists. The fixes already landed
stay; graded books already running are still graded.

**The map** (`docs/design/LEVEL_DD_AREA_MAP.md`, not yet written):
- the states a level-DD supply leg and its account can be in: on level, instalment missed, returned, cured, leaving,
  left with a debit, left in credit, closed;
- for each state, the code that decides it on each of the four sides that hold an idea of what a level account
  owes: the world's schedule (`simulation/dd_level_collection_book.py`), the desk (`company/billing/arrears_engine.py`; the world also has `simulation/arrears_engine.py`, and the map says which decides each state), the
  page (`tools/generate_billing_ledger.py`) and the invariant rows (`INV_OVERDUE_WITHIN_*`, `INV_PAYMENT_RECORD_*`);
- each state traced on one real household from the newest graded book, printing what each side reads;
- where two sides disagree on a state, that row is the next fix, and its prediction names the state.

**Done means:** the map is written and every open prediction in this finding names the state it is about.

## The map is written: `docs/design/LEVEL_DD_AREA_MAP.md` (worker tick, 10 Nov 2026 ~22:00 GMT)

The map lists ten states (S1 to S10). For each, it names the code that decides it on every side, and it counts the
legs in each state on the newest graded book, dca2ea1e7f (`/var/tmp/lvlmap-trace/census.py` over
`/var/tmp/grade-dca2/arm/ledger.json`).

**One correction to the section above.** There are five sides, not four. The page does not work out its own cash. It
posts what the **world's** settlement walk says (`simulation/arrears_engine.balance_settlement_from_outcomes`). That
walk holds its own rule for a credit bill, apart from the triad's rule. Class L′ (SYN-2016-549g) is those two world
rules disagreeing. It is not the page disagreeing with the desk.

**Six disagreements, each named by its state** (map section 4):
- **D1** (S7c), the gate's only unexcepted class. It has an owner.
- **D2** (S3): on two-leg accounts, the desk opens on the account's figure while the returning leg has no page case.
  PROS-2017-0393g, 6 legs. New, and not traced.
- **D3** (S5): the desk cures while a returned instalment is still owed on the page. PROS-2020-0191, 8 legs. The
  sister finding's class, still present after d8264b525e.
- **D4** (S10): the desk wrote off and the page still owes. It has an owner.
- **D5** (S7/S9): the desk and the page define leaving differently. 436 legs leave on their final bill only, and the
  desk has no final-bill carve. This is a definition question for the knowledge page first.
- **D6** (S4): the desk caps a repaid return at the balance, and the world does not. K4.

**Every open prediction, with the state it is about:**

| Prediction | Where filed | State | Status |
|---|---|---|---|
| INV_OVERDUE_WITHIN_BALANCE at most 5, then at most 2, on the next fresh book | this finding, 10 Nov | S7 (leaving with a debit, the statement term) | **graded: held**, 0 on dca2ea1e7f |
| Head book 068b5e3cc8: OVERDUE_WITHIN_BALANCE 0 to 2 | sister finding, ~19:10 10 Nov | S7 | open, grades on 068b5e3cc8 |
| Head book: PAGE_BALANCE still-level steps 0 to 5 | sister | S1 to S3 | open |
| Head book: PAGE_BALANCE left-level steps at most 22, and the gate refuses on them | sister, and the dca2 grade | S7c (D1) | open |
| Head book: written-off accounts printing owed at most 27, GBP 1,230.90 | sister | S10 (D4) | open |
| Head book: class L's run half, with no leaver leg's unasked GBP rising | sister | S6 | open |
| Head book: live leaver legs with unasked debit at most 5, GBP 450; holds mixed at most 4 | sister | S7 (per-leg statement) | open |
| W1: at most 3 model misses in the next 20 graded level-DD predictions | `ways_of_working.md` | the area | open, review 24 Nov |

**So the stop condition's done-means holds:** the map is written, and every open prediction names its state. Level-DD
fixes may be drawn again, in the map's order: D1, then the traces of D2 and D3, then D5 on the knowledge page.
Each new prediction names its S-number.

## The rows are met on 6fe7827ab2, and the finding stays open (2026-11-11, worker tick)

"What done means" asked three things of the next book after the fix. The published 6fe7827ab2 book (cab13bbd18,
published at e816040ce8) reads as follows in its committed `docs/reports/domain_invariants.json` (git 6fe7827ab2):

| Done-means leg | Filed | 6fe7827ab2 |
|---|---|---|
| INV_OVERDUE_WITHIN_PAGE_BALANCE on level-DD households | 1,724 of 6,695 | **CLEAN, 0 of 6,385** |
| INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE | 45 of 1,139 | **CLEAN, 0 of 1,139** |
| N20 Leg A at or below 0.30 | | **0.216** (7,494 of 34,768, 929 accounts), FLAGGED and not breached |
| INV_OVERDUE_WITHIN_BALANCE (the account-level reading) | | CLEAN, 0 of 1,013 |

The share leg ("must not move") is **not re-measured here**. No published row carries it.

**Why this is not a retirement.** The eleventh cold read ran on this same book
(`records/SEAT_READING_THE_ELEVENTH_COLD_READ_ON_THE_6FE7827AB2_BOOK_2026-11-11.md`). It attributes O16 and O21
("standing arrears with GBP 0 notices; overdue rising with no bill") to this finding's per-bill dunning family,
"not traced to the penny". So the rows read 0 while a reader still sees the family on the page. Either the rows do
not reach that shape, or the attribution is wrong. That is the next step here: trace O16 and O21 on the 6fe7827ab2
pages, and either name the row that misses them or move them to the finding they belong to. The finding retires when
that trace is done and the share leg is read. D2 to D6 live in `docs/design/LEVEL_DD_AREA_MAP.md` and the sister
finding, and are not this file's done-means.

## O16 and O21 traced on the 6fe7827ab2 pages: one is this finding, still live; one belongs elsewhere (2026-11-12, worker tick)

**What was read.** The eleventh read's own pages (`/var/tmp/crbook/arm/tree/site/data/customers`, built at 6fe7827ab2),
and the brief the reader saw (`/var/tmp/eleventh-read/blind/BRIEF.md`). The reader's raw objections were not kept, so
O16 and O21 are mapped from the record's one-line summary and the lines of the brief that match it. Scripts:
`/var/tmp/o16o21/`. A leg is called "level" here if three or more of its DD collections carry the same amount. That
rule is this trace's own, not a published one.

**O16 ("standing arrears with GBP 0 notices") is not this finding.** In the brief, PROS-2020-0016's ledger prints
`notice £0.00 £139.12`. Every notice line on every page carries an amount of 0.00, because a notice moves no money. The
standing arrear behind it is GBP 62.06 left on INV17134 (Apr 2024) after a GBP 1.91 part payment. It stands for 14
months, while every later bill is paid in full on its own and the notices on INV17134 stop after the second one. The
household pays by **standard credit** (61 of 65 payments), not level DD. It belongs to the per-bill collections family
(split 1 of the dual-fuel collections finding), not here.

**O21 ("overdue rising with no bill") is not this finding either. It is a due-date disagreement between the desk and the page.**
PROS-2019-0246 (level, GBP 310.47 a month) opens a journey on 19 Nov 2022 at GBP 114.39 overdue. The desk's final
notice on **13 Dec 2022** says GBP 595.68 overdue. That is 114.39 plus INV16180 net of its EBSS credit (547.29 − 66.00 =
481.29). The page prints INV16180's due date as **17 Dec 2022**. The desk sums only items it holds as overdue
(`company/billing/arrears_engine.py`, `undisputed_overdue_gbp`), so the desk's due date for that bill is earlier than
the page's. On single-fuel pages, **170 of 1,388 collections steps (31 accounts)** print an overdue figure that the
page balance covers but that includes a bill the page prints as not yet due. `INV_OVERDUE_WITHIN_PAGE_BALANCE` cannot
see this, because its upper bound is what is owed, not what is owed and past due. A pointer is filed on that row's
finding. Which due date is wrong is not traced.

**What the trace found that does belong here: the ledger's notices still dun level households per bill, while they are in credit.**
The rows that read 0 grade the desk's collections steps and the payment record. Neither reads the ledger's own notice
lines, and those are the lines the reader sees under "MOST RECENT MOVEMENTS".
- Summed over both fuel pages as `INV_OVERDUE_WITHIN_PAGE_BALANCE` sums them, **42 of 1,106 notices on level legs (16
  households) are sent while the account is in credit or at zero**. On other legs it is 4 of 1,780. Example:
  SYN-2016-253 is GBP 155.55 in credit on 24 Jun 2024 and is sent "First overdue notice -- GBP52.89 outstanding".
- 434 of the 1,106 name one bill's face, differing from the leg's balance by more than GBP 1. That fails done-means
  bullet 3 ("the printed overdue figure is the account's arrears … not a bill's face") on the ledger's lines.
- **The cause:** `simulation/arrears_engine.arrears_stages` (line 746) opens a case for each failed bill, at that
  bill's arrears. It dates `ledger_notices(due_date, arrears_gbp)` (`company/billing/arrears_engine.py:731`, "for a
  bill missed on `due_date`") at due + 21 and due + 28, whatever the account's balance is on those days. The desk's
  journey was moved to the account. This second ladder was not.

**So the finding stays open, now with a named shape instead of an untraced objection.** Done means, on the next book:
no ledger notice on a level-DD household is dated on a day its account is in credit or at zero, and the notice's
amount is the account's arrears. That needs a row that reads ledger notices, written blind to the fix (the 26 Oct
ruling, step 4). The fix is a design choice between two options: the world's per-bill case asks the desk whether to
send each notice, or the notice reads the account. That choice goes on the knowledge page first (K8,
`debt_and_collections.md`). The share leg is still not read.

**Prediction, filed before any fix:** a blind row over ledger notices on this same book reads between 30 and 60
in-credit notices on level households. If it reads 0, either this trace's level rule or its two-page sum is wrong.

## The statement's notice lines yield to the desk: pre-registration (seat executor, 12 Nov 2026, filed before the row or the fix is run)

**The K8 choice is already made, and this closes a GAP it left.** `company_debt_management.md`, "Where the desk
runs, its silence is a decision" (3 Nov), chose "ask the desk": on an account the desk runs, none of the ledger's
FIRST/SECOND_NOTICE letters go on the record (`decision_event_ledger.yield_to_the_desk`). It applied the rule to the
reaction chain only, and said so: "The ledger's own `notice` rows on the account statement are untouched. They are a
second narrator on the statement, a GAP not addressed here." The 42 notices the 12 Nov trace found are those rows.
The amendment there (12 Nov) extends the same rule to the statement, in
`tools/generate_payment_ledger_data.build_account_ledger`. "Read the account" is rejected: it would make the
statement a third reader of the balance beside the desk's and the page's, which is the two-ladder shape again.

**The row.** A fresh agent writes a page row, blind to the fix: every `notice` line on a household's statement is
dated on a day the household's pages (both fuels, summed) owe more than zero.

**Predictions, all on the 6fe7827ab2 pages (`/var/tmp/crbook/arm/tree`):**
1. Before the fix, the row reads **30 to 60** violations on level legs (the 12 Nov prediction, kept), and 34 to 64
   over all legs. If it reads 0, the trace's two-page sum or its level rule is wrong.
2. After the fix, replayed by re-running the statement builder over the same `billing_ledger.json`: the row reads
   **0 on level households and at most 4 over all legs**. Any residual is on an account the desk never ran, where the
   ledger stays the only narrator by design.
3. Statement notice lines fall from about 2,886 to **at most 150**: the 3 Nov measurement left 6 ledger letters on
   the reaction chains, but the statement also carries the I&C DISPUTE_NOTICE, which the rule does not touch.
4. **No running balance moves.** A notice line is GBP 0.00, so every page's `running_balance_gbp` sequence, less its
   notice lines, is unchanged byte for byte.

### First measurement, per-account rule (12 Nov, after the predictions above)

The statement builder was replayed twice over the 6fe7827ab2 `billing_ledger.json` at this tree's HEAD, once with the
rule and once with it switched off. Only that one variable moved. Census: the 12 Nov trace's own method (summed fuel
pages, "level" = 3 or more equal DD payments). Scripts: `/var/tmp/n12credit/`.

| | rule off | rule on, per account |
|---|---|---|
| statement notice lines | 2,886 | 19 |
| in credit or at zero, level legs | 42 (16 households) | 10 (5) |
| in credit or at zero, other legs | 4 (3) | 1 (1) |
| non-notice entries changed, on any page | | 0 |

- Rule off reproduces the trace exactly (42 on 16 households, 4 on 3). So prediction 1's census holds; the row's own
  count is still to come from the blind row.
- Prediction 3 (at most 150 left) **held**. Prediction 4 (no balance moves) **held**.
- Prediction 2 (**0 on level households, at most 4 overall**) is **refuted**: 11 are left, on 6 households.
- **Why.** All 19 surviving lines are on 10 residential accounts that carry **no desk journey at all**, for example
  SYN-2016-310 at GBP 0.00 on 6 Aug 2017. The 3 Nov carve-out keeps the ledger as narrator wherever the desk "never
  ran". That carve-out was written for a book published before the run carried journeys. This book carries them on
  659 of 1,302 legs, so the desk walked every account, and opening nothing was its decision. I did not predict that
  every residual would sit in the carve-out.

### Second step, the carve-out keyed to the book: pre-registration (12 Nov, filed before the change)

**Change.** The statement builder asks whether the BOOK carries desk journeys on any leg. If it does, no ledger
FIRST/SECOND_NOTICE goes on any statement. A book without them keeps every ledger letter, as before. The I&C
DISPUTE_NOTICE is untouched.

**Predictions on the same replay:**
- statement notice lines go from 19 to **0**;
- the in-credit census goes from 11 to **0**;
- non-notice entries are unchanged on every page.

8 of the 19 lines are on accounts that owe on the day, where the desk opened nothing. A desk silent on a real debt is
`SEAT_FINDING_THE_DESK_NEVER_RAN_ON_FIVE_ACCOUNTS_..._2026-11-03.md`. Removing the ledger's letter does not hide that
debt: the balance still prints, and the miss is the desk's to fix. A pointer goes on that finding.

### Measured: the second step held, and the blind row (12 Nov)

**The blind row.** A fresh agent wrote `INV_NO_ARREARS_NOTICE_WHILE_THE_HOUSEHOLD_IS_IN_CREDIT` without seeing the fix
or this section. It lives in `tools/domain_invariant_runner.ev_no_arrears_notice_while_in_credit`, and its test is
`tests/tools/test_an_arrears_notice_is_never_sent_while_the_household_is_in_credit.py`. Mutation-proven: grading
each page on its own, passing an exact zero, and never breaching each turn tests red.

On the published 6fe7827ab2 pages it is **BREACHED, 47 of 2,886 notice lines, 20 households**:
- 43 of 1,106 are on level legs (17 households). Prediction 1 (30 to 60) **held**.
- 12 of the 47 are at exactly GBP 0.00. 18 are on a page that owes while the household's other fuel holds more
  credit.

The row's 47 against my census's 46 is a one-line difference in how a same-day balance is read. It is not traced.

**The second step, replayed on the same ledger.** Statement notice lines go from 19 to **0** (predicted 0, **held**).
The census goes from 11 to **0** (**held**). Non-notice entries are unchanged on all 1,302 pages (**held**). The row
reads **UNREACHED, 0 graded, 0 breached**. That is honest: with the desk in the book, the statement carries no
ledger letter. The row still fires on a pre-desk book, or if the letters come back. The desk's letters already face
the same page balance in `INV_OVERDUE_WITHIN_PAGE_BALANCE` (0 of 6,385 on this book).

**The build.** `tools/generate_payment_ledger_data.build_account_ledger(..., desk_in_book=)` and
`book_carries_the_desk`, test `tests/tools/test_a_statement_sends_no_ledger_letter_where_the_desk_dunned.py`. The
design is on `company_debt_management.md`, "The statement's notice lines yield too". Bullet 3 of the 12 Nov
done-means (the notice's amount is the account's arrears) is moot: no ledger notice is printed where the desk runs.

**Why this file stays open.** The live pages are 6fe7827ab2's, and they still print the 47 until the next publish
rebuilds them. The 11 Nov share leg is also still unread. This change moves no money, so it cannot move the share
leg, but the earlier steps could have. **Done means now:** the next published book reads this row as not BREACHED,
and N20's share leg is read on it. Then this file goes to done/.

**Unrelated, seen while testing:** `tests/tools/test_billing_and_payments_ledger.py::test_reconciliation_identity_holds_across_full_live_book`
fails on the committed site JSON for OCC-00909e50a521. Billed 567.45, collected 481.48, balance 0.00: GBP 85.97
unaccounted. That reading is of the committed pages, which this change does not regenerate, so it predates this
change. The cause is not traced.

### The share leg read; the row's half waits for the 16 Nov publish (worker, 12 Nov 2026 ~05:00 GMT)

**N20's share leg, read at origin 0367c57375** with the test's own `share_equal_to_the_bill` over `generate()`'s ledger
(script `/var/tmp/grade-nocredit-0454/share.py`, clean `git archive` of origin):

| book | successful DD collections equal to their bill | share | ceiling |
|---|---|---|---|
| 6fe7827ab2 (published) | 7,886 of 36,474 | **0.216** | 0.30 |
| 87e00e1458 (built 11 Nov 19:45, not published) | 7,886 of 36,474 | **0.216** | 0.30 |

So the 11 Nov share-leg condition holds on the live book. It agrees with the runner's Leg A (0.216, 7,494 of 34,768)
to three places, on a slightly different denominator: the test counts every successful DD, the row only graded ones.
0d2576c48 moves no money, so it cannot move this figure; the next book in line reads the same.

**The row's half cannot be graded yet.** No book has been published since 0d2576c48: origin's pages are still
6fe7827ab2's and still print the 47. That week's publish is spent, so the weekly window next opens **Mon 16 Nov
04:00**. **Done means, unchanged:** on that publish, `INV_NO_ARREARS_NOTICE_WHILE_THE_HOUSEHOLD_IS_IN_CREDIT` reads
UNREACHED or CLEAN, and the share leg stays at or below 0.30. Prediction for it: UNREACHED, 0 graded (the
replay's reading); share 0.216 if the published book is 87e00e1458, and within 0.17 to 0.27 on any later book.
Then this file goes to done/. The delivery-lane claim is released until then rather than re-drawn each tick.
