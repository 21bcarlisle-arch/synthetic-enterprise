**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`

# The GBP 1,338.06 EPG gap is two held bills of one won switch, and the close never booked a held bill's receipt

Found by the delivery seat on 25 Nov 2026, for the item `the-epg-receipt-books-what-the-treasury-paid`.
The publisher refused `docs/reports/run_output_f2c6979d01_20261124T215935Z.json` at 23:46Z on 24 Nov
for "EPG paid on settled kWh GBP 213,447.29 != booked GBP 212,109.23".

LATENT, not BLOCKING: the fix is in this commit. The run on the shared tree stays refused until the
next book passes the bills grade.

## Measured (`tools/grade_svt_invoices_over_ceiling.epg_receipt`, unchanged)

| book | bills carrying EPG | carved | paid (settled) | booked | gap |
|---|---|---|---|---|---|
| 6a588a832f (20 Nov) | 3,542 | 215,661.30 | 214,750.80 | 214,750.80 | 0.00 |
| f2c6979d01 (24 Nov) | 3,641 | 213,400.27 | 213,447.29 | 212,109.23 | **1,338.06** |

The gap is new in 6a588a832f..f2c6979d01. 6a588a832f's bills grade never ran (its book was refused
earlier, on the domain-invariant gate), and it passes now.

## The account list: one account, two bills, all carved and never booked

| account | fuel | bill | EPG quarter | basis | kWh | carved | paid | booked |
|---|---|---|---|---|---|---|---|---|
| SYN-2016-175_3 | electricity | Dec 2022 | 2022-Q4 | actual | 3,509.0 | 597.86 | 597.86 | 0 |
| SYN-2016-175_3 | electricity | Mar 2023 | 2023-Q1 | actual | 2,322.1 | 740.20 | 740.20 | 0 |
| | | | | | | | **1,338.06** | |

- **Booked at a different amount: none.** Re-booking the 54,152 bills the Tier-1 gate issued
  (`saas.ledger.make_epg_receipt_event`) gives GBP 212,109.23, which is the ledger to the penny.
- **Carved and never booked: the two bills above.** `validate_bills` held 11 of 54,163 bills, nine
  for SYN-2016-175_3 and two for OCC-d5419b4a0f6e, all on `vat_by_segment` (a "resi" label against
  a metered 2,156–3,509 kWh a month). Two of the 11 carry EPG. `close_the_books` built the ledger
  from `issued_bills` only, so their receipts were dropped along with their charges.

## Why the gap is new: f80fe39511 put the account on supply

SYN-2016-175_3 is a won switch in both books (it is in `acquired_customers` in each). In
6a588a832f it has **0 bills**. In f2c6979d01 it has **78**. f80fe39511 ("A won switch from an
electricity household is now put on supply from its win date") is an ancestor of f2c6979d01 and not
of 6a588a832f. Its message records the 6a588a832f state: 16 wins, none billed. So the account list
names the commit, not the candidate list in the item: none of 9caeb0a920, e09f1640a9 or 9739e7bad4
is involved, since every issued bill booked exactly.

**Stated limit.** The commit is named from the account list and the ancestry, not from a world
rerun at f80fe39511^ against f80fe39511. That rerun is a full book (about 2 hours). The one-variable
rerun that *was* done holds the bills fixed and varies only the close (below). The close defect
itself is older than f80fe39511. It is the same class c5a8090187 recorded on 24 Oct (GBP 5,898.10
carved and never booked, because `validate_bills` held five negative bills). That one was cleared
by removing the negative bills, not by fixing the booking.

## The fix, at its class (company/)

`company/finance/accounting_close.held_bill_epg_receipts` books an `epg_receipt_event` for every
bill the gate held. The knowledge page `docs/market_research/default_tariff_cap_and_epg_on_the_bill.md`
("How the supplier was paid, and on which volume") says why: the scheme paid on settled volume
reconciled to RF, and "the Treasury's payment never followed the bill at all". A held bill holds
back the household's charge, not the month's supply. The held bill's **charge** still never reaches
the books (`tests/company/interfaces/test_accounting_close_seam.py` is unchanged and green). This is
the same rule the close already applies to read visits: "Over every bill, held ones too".

- Test: `tests/company/finance/test_a_held_bills_epg_receipt_is_still_booked.py`. The mutation
  `test_mutation_booking_from_issued_bills_only_is_caught` performs the defect, which is the close
  as it stood at f2c6979d01, and the grader then shows the held bill's settled share as the gap.
- **One-variable rerun on f2c6979d01's own bills, through the fixed close:** paid GBP 213,447.29,
  booked GBP 213,447.29, gap 0.00, 11 held. The grader is unchanged and has not been loosened.
  (The settled records are not needed for this figure: EPG events are read off bills only.)

## Open, not fixed here

- **SYN-2016-175_3 is labelled `resi` and draws a company EAC of 21,100 kWh.** Nine of its 78 bills
  are held as a likely SME-as-household mislabel. Whether a won switch can carry that load as
  domestic is a world/acquisition question for the lane that owns f80fe39511's successor. The bills
  grade no longer depends on the answer.
