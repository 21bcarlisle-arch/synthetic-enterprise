**Severity:** INFO · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The figures the level direct debit will move on the next fresh run (N20 build, 2026-11-04)

**Why this exists.** The N20 build makes the households the world put on a level direct debit pay the level
amount, on both cash records: the page ledger (`tools/generate_billing_ledger.py`) and the books
(`saas/ledger.build_ledger`, through `close_the_books(level_dd_collections=...)`). No run was launched. This
is the list of published figures the next fresh run will move, filed before that run so that each movement is
a prediction and not a discovery.

**Design:** `SEAT_READING_WHICH_ORGAN_IS_THE_DIRECT_DEBIT_ON_THE_4669D77DDD_BOOK_2026-11-04.md`. **Knowledge:**
`docs/market_research/payments_and_direct_debit_2026-10-25.md`, "What a level direct debit must be".

## Measured before the run (4669d77ddd book, schedule injected, `/var/tmp/n20-build/`)

- The share of DD collections equal to their bill falls from **0.963 to 0.207** (7,326 of 35,307). The
  prediction filed before it was measured was 0.12–0.25.
- 758 of 934 balance-book accounts are on a level amount (0.81, against a draw share of 0.825).
- The page ledger's successful DD cash is £2,173,751.98 today and £2,170,487.46 level. The total barely moves,
  but the timing moves a lot: the level-minus-bill difference per account-month has a median of £12.68 and a
  p90 of £59.11, and the book-wide monthly difference ranges from −£26.9k (Jan 2023) to +£18.6k.
- The bars double-count before the build: of £46,669.41 in DD bars, **£20,311.13 (204 actions)** was written
  off on accounts whose every bill up to the bar date the ledger showed collected. After the build:
  - bars on level accounts write off a debit the cash carries;
  - bars on variable accounts (about £5.6k on the run-as-built book) are no longer booked, because those
    accounts pay each bill and their arrears are the engine's write-offs.

## What moves, by surface (grade each on the next fresh run)

**Cash flow (M3, "cash flow")**
- `ledger_pnl.cash_collected_gbp` and `cash_net_margin_gbp`: the total moves slightly, and the in-year timing
  is now level.
- `company/finance/pnl.py` cash-basis revenue (`payment_received_event` as revenue): its monthly profile
  flattens.
- `company/finance/treasury.py`, `credit_facility.py` and `segment_capital.py`: monthly cash positions and
  facility draws. Expect higher cash in autumn and lower in late winter.
- `saas/reporting/annual_report.py`: the sentence "cash_collected = bills − bad_debt" no longer holds month by
  month. It holds only over whole years of level collections. **Its wording must change.**
- `saas/reporting/css_statement.py`: memo line "cash collected (banked)".

**Balance sheet**
- `company/finance/double_entry.py`: receivables on level accounts go into credit in summer. The held credit
  now appears as a liability funded by cash.
- `dd3_held_credit_balance_sheet`: cash rises with the liability. The −£80,966.66 equity understatement
  should largely close. Predicted: it falls by at least half. Whether it closes in full depends on the
  balance book's held credit still counting variable accounts (see "Not done" below).
- `ledger_pnl.back_billing_write_off_gbp`: falls by the variable-account bars, about £5.6k on 4669d77ddd.

**Bill shock and the household's experience (M3, "certainty" and "control")**
- Page ledgers (`site/data/customers/*.json` via `tools/generate_payment_ledger_data.py`, the Explore cast
  `tools/generate_explore_cast.py`, `company/billing/statement_export.py` and `raw_account_export.py`):
  - `payment_received` rows become the level amount on the payment day;
  - balances build credit in summer;
  - the page's sentence "a flat monthly amount against a seasonal bill" becomes true for level accounts.
- Any bill-shock figure that reads what the household paid month to month falls for level accounts. Any
  figure that reads the bill is unchanged. Name which one each published bill-shock number is before grading
  it (`what_bill_shock_is.md`).
- The domain-invariant rows graded on ledger payments may move, including the event-walk and VAT readers in
  the post-publish reds. Check each against the new payment amounts rather than assuming that it moved.

## Not done in this slice (owed, in order)

1. **An evaluator for the blind row.** `INV_DD_COLLECTIONS_EQUAL_TO_THE_BILL_WITHIN_THE_VARIABLE_DD_SHARE`
   reads NO_EVALUATOR in `tools/domain_invariant_runner.py` until one is written. The book-level leg is held
   meanwhile by `tests/company/billing/test_the_share_of_dd_collections_equal_to_their_bill_sits_inside_the_published_belief.py`,
   which reads "cannot tell" (xfail) until a run carries `level_dd_collections`, and is live after that.
2. **The balance book's own summary and held credit** (`dd_balance_book.summary()`, DD3) still count variable
   accounts. Only the booked bars are filtered. The published held-credit and barred totals should be scoped
   to level accounts too.
3. **The pairing edge.** The page ledger pairs a month's collection only with a DD bill. The books pair it with
   any bill that month. They can disagree only where a level account has a DD bill and a non-DD bill in one
   month (a spell change).

**Reverse.** Revert the N20 build commit, which reverses every change in this slice. Nothing was re-run or
published.
