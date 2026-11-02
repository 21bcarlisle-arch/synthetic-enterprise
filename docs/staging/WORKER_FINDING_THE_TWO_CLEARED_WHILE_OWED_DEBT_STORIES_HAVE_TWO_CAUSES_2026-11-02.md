**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The two "cleared while still owed" debt stories have two different causes: a story past the ledger's clock, and one debt in two records (2026-11-02)

Focus item 1 part (3), `the-last-pc2-catch-up-defect-then-the-publish`. Both households were refused by the Explore
debt slot's fourth check on the 85b044be54 book (`/var/tmp/fresh-grade-85b044be54/debt_p4.txt`). Both pre-registrations
predicted they would survive, and they did. Neither touches a domain-invariant row, so neither blocks the publish.

## PROS-2025-0013: the story runs past the page ledger's own clock

- The page ledger is built `as of 2025-07-04` (the run's pages.log). Its last row is 2025-06-30, a first overdue notice
  for £9.74 (INV21342, a 7-day stub, DD returned 2025-06-23).
- The arrears engine's case (`ARR-PROS-2025-0013-2025-06-07`) ends `ARREARS_REPAID` on **2025-07-07**, three days after
  the as-of date. `tools/generate_payment_ledger_data.py` books that stage as a payment only up to `as_of`, so the
  ledger never shows it.
- The reaction chain carries `arrears_arrears_repaid` 2025-07-07 anyway, so the story says "cleared" over a balance
  the same page shows as owed.
- The company's `payments` list has no 2025-07-07 payment either. The repayment exists only in the world's arrears
  case.

**Fix locus:** the reaction chain (and any other timeline writer) should cut at the ledger's `as_of`, just as
the ledger does. The debt check is right to refuse this, so do not weaken it. Test shape: a case whose repaid
stage is after `as_of` prints no "cleared" moment.

## PROS-2020-0191: the collections desk cures a debt the arrears engine still holds

- The arrears engine opened `ARR-PROS-2020-0191-2023-09-30` for £40.73 (INV17575, DD returned 2023-10-20). It
  stays open, with no repayment and no credit, and is written off on 2026-04-01, after the book's end.
- The page's running balance carries that £40.73 unchanged from late 2023. Every later DD pays exactly its own
  bill, so the balance returns to £40.73 each month (2024-11-14, 2024-12-19, 2025-01-15).
- The company's collections desk journey (`company/billing/collections_journey.py:461`) reads overdue £126.09 on
  2025-01-15. It then enters `cured`, "overdue balance cleared on the ledger", on 2025-01-16, with overdue £0.
- The desk's overdue view and the arrears engine's case are two homes for one debt, and they disagree by £40.73.
  This is the shape CLAUDE.md names ("the journey's end having two homes").

**Not established:** which of the two is wrong. If the desk allocates each DD to the oldest debt, the £40.73 moves
onto the newest bill and is still overdue once that bill falls due, so `cured` is wrong. If the desk deliberately
leaves a case the arrears engine holds out of its view, the page should not tell one story from both. Read the
desk's `view` construction before choosing. Payment allocation on a domestic account is a regulated practice
question (SLC 27), so check the commons first (K8).

## What done means

PROS-2025-0013's story stops at the ledger's clock, with a test that reds on today's shape. PROS-2020-0191's two
records agree, or the page shows the case the desk leaves out. The debt slot's fourth check then refuses no
household on the next fresh book.
