**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`

# Pre-registration: the page resolves a final bill on the world's ask (SYN-2016-244 class)

Written 26 Nov 2026, before the page was regenerated. The parent finding is
`SEAT_FINDING_SYN_2016_244_THE_PAGE_PRINTS_A_FINAL_BILL_REFUND_THE_WORLD_NEVER_MADE_2026-11-26.md`.

## What the five legs are (read before the build, 91c32797b3 book, `world_walk_truth.final_month_nets`)

There are two separate defects, not one.

1. **Paid final bill, credit held to the close (SYN-2016-244, SYN-2016-360g, and SYN-2016-099 on
   this older book).** The world netted ledger credit (`credit_taken_gbp` 26.71 / 3.03 / 0.62). On
   the page, that credit sits in the walk's pool as a `repayment`-kind excess (settlements at a
   month's face, above what was open). A level leg's paid bill draws only `credit` and `set_off`
   (`balance_settlement_from_outcomes`), so the final bill was printed at its face and the excess
   was refunded at the close.
2. **Failed final bill, part paid on the face (OCC-cede70b10116g, OCC-6387bf64272a).** This one is
   the WORLD's defect, not only the page's. `LivePaymentTriad` calls `mover_final_bill_outcome`
   with the face, not the ask. So the gone household "part-paid" 57.23 of a bill that asked 3.61,
   and the world refunded the excess. A household cannot part-pay more than it was asked. The exit
   model's outcome draw does not read the amount (`resolve_final_bill`: only `recovered_gbp`
   scales with `billed`), so passing the ask moves no outcome, only the size of the part.
3. **SYN-2016-139** is not a cash defect. Its failed final closes at 5.19 on both sides. The page
   nets 8.97 of repayment against it and the level difference adds 2.80, where the world names
   6.17 of ledger credit. That is the same balance with a different attribution, and it is not
   changed here.

## The build

* World (`background/live_payment_triad.py`): a mover's final bill's exit is drawn on `ask_gbp`,
  and `part_share` is the part over the ask.
* Truth (`simulation/world_payment_truth.build`): a final bill's told outcome carries
  `credit_taken_gbp` and the cash `part_paid_gbp` beside `debit_asked_gbp`.
* Page walk (`simulation/arrears_engine`): a failed final takes the world's part cash when the
  truth carries it, else `part_share` times the ask (face - credit_taken + debit_asked). A paid
  final bill that carries `credit_taken_gbp` draws that much waiting credit of any kind and posts
  it as `credit`, so the page prints the smaller payment (SLC 31H.12).

## Predictions (91c32797b3 book, page only: the book predates the world change)

* SYN-2016-244: final payment printed 25.55 (was 52.26), credit applied 26.71, no closing refund.
* SYN-2016-360g: final payment 0.00, settled by credit 3.03, closing refund 24.65 (was 27.68).
  The rest of the gap to the world's ledger (-9.29) is a separate disagreement and is not touched.
* SYN-2016-099: final payment 0.00, credit 0.62; closing refund falls by 0.62.
* OCC-cede70b10116g: this old book carries no part cash, so the page takes share x ask, 1.75
  (was 57.23), and closes owed 1.86 with no refund (was refunded 53.62). On this book that
  disagrees with the old world's crossed 57.23. The world change removes the disagreement on the
  next book.
* OCC-6387bf64272a: part 2.88 (was 2.93).
* No other leg's printed final-bill payment or closing refund moves.

## Graded (26 Nov, the same day, before landing)

Method: `/var/tmp/rev32/patch.py` copies `credit_taken_gbp` from `final_month_nets` onto the book's
truth (273 final months), then `tools.generate_billing_ledger.generate` runs before and after the
build, and the two pages are diffed customer by customer.

* SYN-2016-244: **held.** Pays 25.55, credit applied 26.71.
* SYN-2016-360g: **held.** Pays 0.00, credit applied 3.03.
* SYN-2016-099: **refuted.** It does not move. Its credit is not in the walk's pool at the final bill;
  the finding records it as fixed at the world by d688a224a, and this older book predates that.
* OCC-cede70b10116g: **held.** Part 1.75. OCC-6387bf64272a: **held.** Part 2.88.
* "No other leg moves": **refuted.** PROS-2016-0370g and SYN-2016-530 moved too. Each failed final
  asked a scheme debit beside its face, so share x ask exceeded the face, and the first build opened
  their cases at -10.18 and -22.17. Fixed by choice 36 (`home_moves.md` s.8.8j): the part meets the
  charges first, and the rest is `debit_paid_gbp`. After that, their cases are 0.00 and their parts
  12.89 and 26.46. On this old book that is more than the old world crossed (0.75 and 2.55), because
  the world change gives the share its new meaning.
* The balances: with the book's stale refund log, three legs print -26.71, -3.03 and -53.62. With
  the log recomputed from the new walk (`run_patched2.json`), all six moved legs print balance 0.00.

**Still open, for the first book after this commit (no book exists yet):** the world's part is drawn on the
ask, so `final_month_nets.part_paid_gbp` on cede-shaped legs is at most `ask_gbp`. The run's own
refund log and the page agree on these legs. INV_A_CLOSING_REFUND_IS_WITHIN_THE_HOUSEHOLD_CREDIT has
no new breach.
