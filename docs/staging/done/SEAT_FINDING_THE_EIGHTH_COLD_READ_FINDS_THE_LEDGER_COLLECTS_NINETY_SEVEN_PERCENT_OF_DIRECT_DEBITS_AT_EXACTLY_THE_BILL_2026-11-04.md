**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# N20. The ledger collects 97% of direct debits at exactly the bill, so the book's direct debit is a variable one, while the page says it is level and most GB households pay a level amount (2026-11-04)

**Source.** Reader objection O30 in the eighth cold read
(`records/SEAT_READING_THE_EIGHTH_COLD_READ_ON_THE_B3CE2A4E73_BOOK_2026-11-04.md`), confirmed by the seat over every
page ledger of the b3ce2a4e73 book (`/var/tmp/eighth-read/scripts/o4_o30_o35.py`).

**What the page prints.** "A direct debit is a flat monthly amount against a seasonal bill, so the balance builds
credit in summer and draws it down in winter." The reader read three Section B ledgers and found each invoice
collected in full about 14 days after it was raised. On those ledgers the balance never goes into credit.

**What the record shows.** Of 35,122 direct-debit payments on the page ledgers, **33,992 (96.8%) equal the amount
of the invoice they settle to the penny**. In this book, a direct debit is the bill, collected on its due date.
`INV_DD_STEP_CHANGE` flags 1,827 of 34,182 successive collections, and it is a flag: it cannot fail a book whose
direct debits all follow the bill.

**Why it is wrong.** `docs/market_research/what_bill_shock_is.md`:
- About 74% of GB domestic households pay by direct debit.
- Ofgem counts **15 million households paying by fixed direct debit and in credit** (year to June 2025), and about
  17 million on the later window.
- So at least about 72% of direct-debit households pay a level amount. The exact fixed/variable split is a stated
  GAP, but its lower bound is not near 3%.
- A level direct debit is what makes SLC 27.15 reviews, credit balances, and "the payment change, not the bill"
  mean anything.

**Two homes for one definition.** The supplier's DD balance book (`simulation/dd_balance_book.py`) does model a
level direct debit with annual reviews. Its open finding is
`SEAT_FINDING_THE_DD_BALANCE_BOOK_KEEPS_A_LEVEL_DD_RUNNING_AFTER_THE_MANDATE_ENDED_2026-11-03.md`. The ledger the
pages print does not take its collections from it. **I cannot yet say** which is the system of record for cash.
- If it is the ledger, the level direct debit, its reviews and its barred balances exist only in a side book.
- If it is the balance book, every page ledger misstates when and how much each household paid.

**What a fix needs (K8).** The knowledge page first states the fixed/variable belief with its range. Then one
home for a direct-debit collection, read by both the ledger and the reviews.

**The row this owes (ruling step 6).** It must be written blind from the knowledge page: the share of
direct-debit collections equal to the bill they settle sits at or below the variable-DD share the page states as
a belief with a range. A household on a level direct debit shows a credit balance in at least one summer month.

**Read 2026-11-04 (seat): the ledger is the cash organ; the balance book narrates.** On 4669d77ddd the
balance book sets a level amount for 934 DD accounts. The ledger collects it in 4 of 35,306 collections and
from 0 accounts in every month. 33,996 collections (96.3%) are the bill. The book's bars (£46,983.97 written
off) and its held credit (£80,966.66 liability, equity cut by the same) are still booked against cash that
never held them. Reading, counts and the build slice `D_level_dd_is_the_collection`, with its red tests named:
`records/SEAT_READING_WHICH_ORGAN_IS_THE_DIRECT_DEBIT_ON_THE_4669D77DDD_BOOK_2026-11-04.md`. Knowledge:
`docs/market_research/payments_and_direct_debit_2026-10-25.md`, "What a level direct debit must be". This
finding stays open until the slice lands.

**Reverse.** Delete this file. Nothing outside `docs/staging/` was touched.

## Done

2026-11-04, the N20 build (delivery lane `the-ledger-collects-the-level-direct-debit`).
- The world draws a level or variable flag per DD household (`simulation/household_segments.pays_a_level_direct_debit`,
  0.70–0.95 from the knowledge page, at its midpoint).
- The page ledger and the books read one level schedule (`simulation/dd_level_collection_book.level_dd_collections`)
  and landed together. The books' DD bars are filtered to level accounts.
- Tests:
  - `tests/company/billing/test_a_level_direct_debit_account_pays_its_level_amount_not_its_bill.py` (with the
    partition leg and the two-cash-record agreement leg);
  - `tests/company/billing/test_the_share_of_dd_collections_equal_to_their_bill_sits_inside_the_published_belief.py`.
- The blind row `INV_DD_COLLECTIONS_EQUAL_TO_THE_BILL_WITHIN_THE_VARIABLE_DD_SHARE` is in
  `docs/design/DOMAIN_INVARIANTS.yaml`.
- On 4669d77ddd with the schedule injected, the bill-equal share falls from 0.963 to 0.207.
- The figures the next fresh run moves, and the three owed follow-ups, are in
  `records/SEAT_RECORD_THE_FIGURES_THE_LEVEL_DIRECT_DEBIT_WILL_MOVE_ON_THE_NEXT_FRESH_RUN_2026-11-04.md`.
