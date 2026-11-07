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
