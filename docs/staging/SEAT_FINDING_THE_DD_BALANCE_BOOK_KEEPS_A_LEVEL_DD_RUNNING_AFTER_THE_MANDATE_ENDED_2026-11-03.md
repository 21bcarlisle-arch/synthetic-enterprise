**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The direct-debit balance book keeps a level DD running, and bars at its reviews, after the mandate has ended (2026-11-03)

**Source.** Found while closing N14 (`docs/staging/done/SEAT_FINDING_THE_SEVENTH_COLD_READ_FINDS_PAY_ON_RECEIPT_CUSTOMERS_BACK_BILLED_BEYOND_TWELVE_MONTHS_ON_A_DIRECT_DEBIT_THEY_CANCELLED_2026-11-03.md`).
Same defect class, second organ.

**What the code does.** `simulation/dd_balance_book.py:545` admits a bill to the DD balance book when
`payment_method(...)` (undated, the method the account was set up on) is `direct_debit`. The ledger takes
each payment's method from the dated spells off DD (`dd_collection_book.supplier_dd_spells`). So an account
whose DD was stopped, or cancelled at the bank, stays in the balance book for life. Its level collections
are modelled, its annual reviews run, and with `seek_balance_at_review` on (the shipped default) it can
have a balance barred at a review of a DD that does not exist. On 0a6391d186, 63 accounts carry a
catch-up the ledger records as paid on receipt (N14's census). PROS-2018-0016 has been off DD since its
Feb 2018 bill.

**What I cannot yet say.** How much of the £20,271.46 barred at reviews, or the £2,957.23 at final bills,
on 0a6391d186 sits in spells off DD. The run output publishes `barred_by_customer` only as a count. The
first measurement: rebuild the balance book over the published `bills` and cut `barred_by_customer` by
spell.

**What a fix needs.** The balance book reads the same dated key as the ledger and N14's billing feed
(`run_phase4c_on_phase2b.dated_payment_channel`): a bill inside a spell off DD is not a DD bill. The
knowledge is on `back_billing_and_liability.md` section 16 (GAP 2).
