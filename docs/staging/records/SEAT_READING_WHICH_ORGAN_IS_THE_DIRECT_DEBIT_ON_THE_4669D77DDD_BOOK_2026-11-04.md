**Severity:** INFO · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# Which organ is the direct debit: the ledger collects the bill and the balance book only narrates a level amount, and two of its narrations reach the books (4669d77ddd, 2026-11-04)

**Asked by:** the delivery lane item `which-organ-is-the-direct-debit`, reading N20
(`../SEAT_FINDING_THE_EIGHTH_COLD_READ_FINDS_THE_LEDGER_COLLECTS_NINETY_SEVEN_PERCENT_OF_DIRECT_DEBITS_AT_EXACTLY_THE_BILL_2026-11-04.md`)
against `simulation/dd_balance_book.py`. Since 4669d77ddd the book reads the ledger's dated DD spells.

**Knowledge first:** `docs/market_research/payments_and_direct_debit_2026-10-25.md`, section "What a level
direct debit must be, and how many households pay one". In short:
- SLC 27.15 says a fixed amount is an estimate of use, on the best current information.
- Ofgem expects a household in credit to have its DD reduced.
- SLC 27.16 says credit is refunded on request.
- At least about 70–74% of GB direct-debit households pay a level amount [derived lower bound]. The exact
  split is a GAP. The belief stated for a build is 0.70–0.95.

## The answer

**The ledger is the system of record for cash. The balance book narrates.**

What a household's bank pays is the ledger's per-bill payment:
- `tools/generate_billing_ledger.py:901-911` sizes each DD payment at the invoice's printed total, less
  any EBSS credit and the deemed account's share. It is paid on the bill's due date.
- The run's P&L takes cash from the same per-bill rule: `saas/ledger.make_payment_received_event` books
  `total_amount_gbp - provision` per bill. `ledger_pnl.cash_collected_gbp` is £3,507,192.29.
- `simulation/dd_collection_book.py` (the Bacs-timed attempts) is also per bill. It holds 37,039 attempts.
  Its own docstring says the mandate amount "never sizes or gates a collection".

The balance book (`simulation/dd_balance_book.py`) and `simulation/dd_level_collection_book.py`:
- They compute a level amount per account and the balance it would carry.
- No payment record anywhere is sized by it. The balance book's docstring says so: it "touches no ledger /
  treasury / cash-timing figure".

**But it does not only narrate.** Two of its outputs are booked against a cash record that never held the
credit or debit they describe:
1. **The back-billing bars.** The run passes `back_billing_bars=dd_balance_book.bar_actions`
   (`simulation/run_phase4c_on_phase2b.py:881`). `saas/ledger.make_dd_back_billing_write_off_event` writes
   each one off as "revenue the supplier recognised and may not collect".
   - The book barred £42,515.75 at reviews and £3,170.63 at final bills. `ledger_pnl.back_billing_write_off_gbp`
     is £46,983.97 (that line also holds the non-DD bars).
   - The ledger collected every one of those bills in full, on its due date. The debit balance being barred
     exists only in the balance book. **I cannot yet say** how much of the £46,983.97 is written off against
     bills the cash record shows as paid. The size of the double-count is the first number the build slice
     prints.
2. **The held-credit liability.** `dd3_held_credit_balance_sheet` books £80,966.66 of "customer credit held"
   as a liability, with retained earnings at −£80,966.66. Its cash (£612,368) is the ledger's, which never
   collected that credit. True equity is stated £80,966.66 under naive equity for money the company was
   never paid.
   - Under a real level DD, the cash and the liability rise together and equity does not move. So this
     view understates equity by the whole held credit. It does not reveal a "cash-rich" condition.

So N20's two cases are both true at once:
- Every page ledger misstates when and how much a household on a level DD would pay.
- The level DD's credit and its bars are booked as if it had been collected.

## The counts (newest book, 4669d77ddd, `docs/reports/run_output_4669d77ddd_20261104T132452Z.json`; its page ledger `/var/tmp/grade-4669/ledger.json`)

Probe: `/var/tmp/n20-organ/count.py <run_json> <ledger_json>`, run 2026-11-04 from the repo root.
- It rebuilds the book with `build_dd_balance_book` over `closed_ids_from_bills` and `dd_spells_from_run`,
  with seek-at-review on as the run builds it.
- It reproduces the published `n_customers` exactly (934).
- Its final balance is £70,992.28 against a published £70,281.54. The closed set is rebuilt from bills,
  not from the run's churn list, as `review_arms_from_run`'s docstring warns. Account counts are unaffected.

| | accounts | collections |
|---|---:|---:|
| Balance book: DD accounts it **sets a level amount for** | **934** (+29 refused, no opening amount) | 35,829 level collections in `dd_level_collection_book`, £2,235,117.36 |
| Page ledger: DD accounts it **collects** from | 943 | 35,306 successful DD collections |
| …collections equal to the bill they settle | | **33,996 (96.3%)** |
| …collections equal to the balance book's level amount for that month | **0** accounts in every month | **4** |
| Accounts in both | 914 | |
| Ledger-only / book-only | 29 / 20 | |

**The 1,310 DD collections not equal to their bill:**
- 690 are the bill less an EBSS credit.
- 171 are the bill less the deemed account's share.
- 449 are not classified by this probe. They may be the printed total rounded against `total_amount_gbp`.
  That is unconfirmed.

None of them is a level amount.

**Example, C1.** The balance book sets £16.72 a month through 2016. The ledger collects £18.14, £16.37,
£17.16 and £11.39 in the first four months, which is each month's bill.

**Against the knowledge page.** 96.3% of DD collections equal their bill. The belief is that no more than
5–30% should. The book sits outside the range by a factor of three or more.

## Build design, not built in this item: one home for a DD collection (slice of `D_billing_metering`)

**Slice name:** `D_level_dd_is_the_collection`.

**K8:** the knowledge section above is the page. This record is the design. The build commit cites both.

**The choice.** A DD account collects the level amount the supplier set, on its payment day, every
month. The balance book becomes the source of the collection, not a side computation. The ledger's
per-bill payment for a level-DD account is replaced by the monthly level collection, allocated to open
invoices oldest first. That is the SLC 27.16 netting `_settle_oldest_first` already does inside the book.
Credit carries forward as account credit. The arrears engine's `payment_outcome` keeps deciding whether a
collection succeeds, with the same RNG sequence, so no failure pattern is redrawn.

**Who is on a level amount.**
- One world draw per DD leg: a level or variable flag, with share 0.70–0.95 from the knowledge page.
- Drawn once and carried with the mandate. It sits behind the wall like every other payment truth.
- The company sees only its own mandate type, because it set it.
- Variable-DD legs keep today's per-bill collection, so both kinds coexist, as `dd_level_collection_book`'s
  docstring already intends.
- The share is a stated belief with a range, carried as `origin` in `tools/domain_constant_origins.py`.
  It is not a constant picked to fill a slot.

**What follows mechanically once the ledger collects the level amount:**
- `payment_received` rows on the page are the level amount on the payment day.
- Credit builds in summer, so the page's sentence becomes true.
- The DD3 held credit is matched by the cash that funded it, so equity stops being understated.
- The bars write off a debit the cash record actually carries.

**Order.**
1. Red tests.
2. The world flag.
3. `generate_billing_ledger` reads the level schedule for flagged legs.
4. `saas/ledger` cash events read the same schedule.
5. Re-run.
6. Mark every published cash-flow, bill-shock and balance-sheet figure that moves.

Steps 3 and 4 land together, or the two cash records disagree.

**The red-on-today tests (named here, written in the build):**
- `tests/company/billing/test_a_level_direct_debit_account_pays_its_level_amount_not_its_bill.py`
  - Leg 1, the property: on a two-season synthetic level-DD account, every successful DD `payment_received`
    on the page ledger equals the balance book's `collected_gbp` for that month. The balance is in credit in
    at least one summer month. Red today: the ledger pays the bill.
  - Leg 2, the partition control: a variable-DD account in the same fixture still pays its bill. This shows
    the level branch can be taken and that it is not applied to everyone.
- `tests/company/billing/test_the_share_of_dd_collections_equal_to_their_bill_sits_inside_the_published_belief.py`
  - Book-level, over the newest run's ledger: the share of DD collections equal to the bill they settle is at
    most 0.30, the ceiling from the knowledge page's 0.70 lower bound.
  - Red today at 0.963.
  - Keyed to the property, not to today's number. It fails closed ("cannot tell") when there is no run.
- Ruling step 6 row for `docs/design/DOMAIN_INVARIANTS.yaml`, to be written blind from the knowledge page as
  N20 asks: `INV_DD_COLLECTIONS_EQUAL_TO_THE_BILL_WITHIN_THE_VARIABLE_DD_SHARE`.

**Before building, print first.** The size of the bars double-count: the DD bars on accounts whose ledger
shows the barred bills paid. The level-vs-bill difference per month across the book, so the cash-timing
change is known before any page moves.

**Direction of error until built:** against the company's credit-balance story. The ledger understates the
cash a real supplier would hold from level DDs. The books carry the liability and the write-offs anyway.
Erring against our own thesis (F11) is the safe direction, which is why this is a design and not a hotfix.

**Reverse.** Delete this file and the section of the knowledge page it cites. No code was touched.
