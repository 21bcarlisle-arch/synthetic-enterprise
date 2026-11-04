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

## Done (2026-11-04)

**The measurement.** The book rebuilt over the published 0a6391d186 bills, with the runner's own closed
set (`supply_points_that_left`) and dual-fuel offsets on, reproduces the published summary exactly
(934 accounts; £20,448.73 at reviews; £2,974.26 at final bills; 272 barred). The finding's £20,271.46 /
£2,957.23 were not this book's published figures; these are. Each bar action cut by whether its date
sits in a spell off DD (`supplier_dd_spells` over `issued_bills`, read through `paying_method`):

| action | in a spell off DD | on a live mandate |
|---|---|---|
| review | £2,475.43 (35 actions) | £17,973.30 (360) |
| final bill | £83.14 (2) | £2,891.12 (54) |

68 of the 934 accounts in the book have a spell off DD; none signed a new mandate.

**The fix.** `simulation/dd_balance_book.py` admits a bill on `arrears_engine.paying_method` over the
spells (`dd_spells=`, the ledger's key and N14's), so a bill in a spell off DD is not a DD bill. A
re-signed mandate's first bill back collects one month, not one per month of the spell. The runner
and `review_arms_from_run` pass the spells (`dd_spells_from_run`). Rebuilt with them: reviews
£17,982.63 (-£2,466.10; the £9.33 gap to the cut is dual-fuel offsets resettling), final bills
£3,161.05 (+£186.79), accounts barred 253. The final-bill rise is three accounts that closed after a
stop: their balance is now barred as at the last DD bill, not at a final bill months later.

**The test.** `tests/simulation/test_the_dd_balance_book_ends_a_level_dd_where_the_mandate_ended.py`
asserts the partition first (a live mandate is admitted for every bill and its review bars), then that
a stopped account leaves the book at its stop, and that a re-signed mandate collects one month on
return. Mutations: admission read undated -> 2 red; the resume reset removed -> 1 red.

**Knowledge (K8).** back_billing_and_liability.md s.16: GAP 2 closed with the figures, and a new GAP
named: the next bill after a stop, paid on receipt, is the charge recovery action that asks for the
DD balance; the book does not take it (closed accounts bar at the last DD bill, open ones sit in
`barred_if_sought_at_run_end_gbp`).

**Not yet:** the published figures move on the next run, not on 0a6391d186's pages.
