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
