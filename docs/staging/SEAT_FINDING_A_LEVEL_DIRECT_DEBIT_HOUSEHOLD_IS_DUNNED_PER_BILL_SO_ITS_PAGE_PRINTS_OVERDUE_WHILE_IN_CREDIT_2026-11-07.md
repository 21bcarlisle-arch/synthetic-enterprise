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
