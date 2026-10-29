# Pre-registration: a credit bill posts to the desk (2026-10-29)

Written before any run carries it. Grade on the first fresh full run whose commit includes this
change and 558ee4624 (`INV_OVERDUE_WITHIN_PAGE_BALANCE`).

## What each figure counts

- *Overdue* (desk): `undisputed_overdue_gbp` of the billing account's company ledger, which both
  fuel legs of a household share (`live_payment_triad.account_of`). It is unpaid open items after
  credit notes and payments.
- *Owed* (row): the sum of both fuel pages' last `running_balance_gbp`, where a page nets a credit
  bill against its next bill.

Both are per billing account, spanning both fuels. So the row's cross-fuel netting is not a row
defect: the desk's ledger was the one that failed to net, because it never received the credit bill.
The row stays as it is. The page was right, and the desk is the record being fixed.

## Change

`record_period(credit_gbp=...)`; a negative issued ask posts as `ADJUSTMENT_CREDIT` without an
invoice ref; `AccountLedger._replay_allocation` applies it oldest-first and does not count it as cash.
Test: `tests/company/test_a_credit_bill_reduces_the_next_bill_the_desk_chases.py`, red on origin
(the invoice-less credit was ignored, leaving 57.18 owed where 0 is). The oracle in
`test_account_ledger_carried_state.py` gained the same rule.

## Predictions (stated before the output)

- **P1.** Of the up-to-2,067 steps after a credit bill, most clear; non-`OCC-` breaches fall from
  6,965 to under 4,500. If they stay above 5,500, the credit bill was not the main cause.
- **P2.** The 487 cross-fuel steps clear with it (they are the same dropped credit, seen across
  fuels). If more than 150 remain, the row's definition is the question, not the desk.
- **P3.** Class (a), steps after the page's write-off, is unchanged at about 723: not touched.
- **P4.** Cash conservation holds (`verify_allocation_conserved` raises nowhere).
- **P5.** Bad debt moves by under 1%: the credit changes what the desk chases, not what the world
  paid.

## Not done in this change

The one write-off date (class a). Recommendation and the GAP label are in
`debt_and_collections.md` §7.3; the build changes the world engine's declared convention, the
company's sweep and the desk's journey, and needs its own run.
