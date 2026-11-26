**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`

# SYN-2016-244: the page prints a final-bill refund the world never made, because it holds the level surplus to the close

Split out of `SEAT_FINDING_SYN_2016_099_THE_PAGE_PRINTS_A_FINAL_BILL_PAYMENT_THE_WORLD_NEVER_ASKED_2026-11-26.md`
on 26 Nov 2026. d688a224a fixed SYN-2016-099 at its source: a leg's bills are now issued in period
order (`home_moves.md` s.8.8h choice 32). That fix does not reach this case. Nothing here breaches an
invariant.

## Measured (3d3a8ee691 book)

On SYN-2016-244's Jan 2018 final bill, the face was 52.26 and the world asked 25.55 (it netted the
leg's level surplus). The page paid the face, 52.26, and then printed a refund of 26.71 on 2 Feb.
The net cash is the same, 25.55, and both sides close at 0. But the page prints 26.71 more cash in
than moved, and a refund that never happened. By then the leg was on receipt (`standard_credit`). The
page walk holds the level surplus (`level_collection_difference`) to the close, and does not net it
against the paid final bill.

## The fix, when it is taken

The page should print the cash the world asked on a final bill. `world_payment_truth.build` already
carries `debit_asked_gbp`; it should carry `credit_taken_gbp` the same way, and `_resolve_bills`
should pay `face - credit_taken + debit_asked`. `balance_settlement_from_outcomes` must then post
`credit_taken` against that bill. This touches the close, the refund clock and
`INV_A_CLOSING_REFUND_IS_WITHIN_THE_HOUSEHOLD_CREDIT`, so it is a page-walk change, not one line.
Before building, count the class on a book made after d688a224a. The first finding counted 2 of 265
netted final bills, and one of those two was SYN-2016-099, which is now fixed at the world.

**Prediction:** on the first book after d688a224a, the 265 final bills where the world netted ledger
credit include exactly one that prints a non-level payment above the world's ask: SYN-2016-244.
