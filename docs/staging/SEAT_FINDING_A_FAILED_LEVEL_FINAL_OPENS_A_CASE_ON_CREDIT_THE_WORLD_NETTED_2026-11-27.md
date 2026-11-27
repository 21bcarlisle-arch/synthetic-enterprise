**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`
**Knowledge:** `home-moves` -- `docs/market_research/home_moves.md` s.8.8a (SLC 31H.12, choice 11)

# A failed level final opens an arrears case on credit the world had netted (OCC-cede70b10116g, PROS-2024-0270g)

Found 27 Nov 2026, grading the record
`records/SEAT_RESULT_THE_FINAL_BILL_ASK_GRADED_ON_THE_FIRST_BOOK_AFTER_B4BA8CB4F_2026-11-27.md`.

## Measured (601887d76a book, published page)

OCC-cede70b10116g's final gas bill is 113.13 (Jan 2024, on level DD). The world's `final_month_nets`
row nets 95.72 of ledger credit, asks 17.41, the DD fails, and the household part-pays 8.45. That
leaves 8.96 owed, and the run sets the elec leg's closing credit against it. The page's walk finds
only 3.22 of credit in its pool when the bill fails. It then nets the 8.96 set-off and opens a case at
**92.50**, with first and second notices and "Balance still open -- GBP92.50 unpaid". The leg still
closes at 0.00, because the level-difference reconciliation clears it at the close. The cash agrees.
The letters do not.

PROS-2024-0270g is the same shape: the page case is 54.08, the world's ask 13.27, and the credit 40.81.

## Cause (read, not yet proven by a replay)

On a level leg, the excess of level collections over bill faces is not in the walk's `pool` when the
final fails (`simulation/arrears_engine.py`, kind 0 event). `_net` draws every kind, so this is not
the paid branch's kind restriction (`short`, near line 1521), which b4ba8cb4f fixed for paid finals.
The surplus is reconciled through `level_collection_difference` at the close, so a failed level final
sees none of it.

## The fix, when it is taken

Knowledge first (K8): `home_moves.md` s.8.8a should say that a failed final's arrears is what the bill
asked, so the face less the credit on the account (SLC 31H.12). Then make the walk post the world's
`credit_taken_gbp` on a failed level final the way the paid branch does. Draw what is short from the
level surplus, so it is not counted twice at the close. Predict before the replay: cede's case would
be 8.96 or less and PROS-2024-0270g's 13.27 or less, and no leg's closing balance would move.
