**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`
**Knowledge:** `docs/market_research/what_a_supplier_holds_to_size_a_direct_debit.md` §8, the page amended in the same commit.

# The annual DD review seeks the balance by default: predictions, filed before any run carries it (worker, 2026-10-20)

`company/billing/dd_review.REVIEW_SEEKS_BALANCE` is now True. The condition for the flip
(`done/SEAT_FINDING_D48_A_THIRD_OF_DD_ACCOUNTS_..._2026-10-14.md`, condition (a)) was met on
17 Oct, and the 19 Oct publish (2a195224b) carries both arms on the billing page. Condition (b),
pairing the flip with a review rule that prices at current rates, is still a separate decision and
is not taken here. The guard the finding asked for landed first: under
`own_forecast_plus_balance`, which already adds the balance, the review does not also step up.

## What the change can reach

The DD balance book is built in phase 4c, after the world has run. Its `bar_actions` reach the
ledger as `dd_back_billing_write_off_event` (`saas/ledger.py`). Its step-ups change the level
debit collected, so they also change the held-credit and level-collection books. Nothing in
phase 2b reads the book, so **no household's churn, arrears or payment draw responds to a
step-up.** That is a GAP. The 2023 step-ups (median about £55 a month on the 19 Oct book) are
published, but they cannot press back on the company. Under F11, this flip's cost to the company
is therefore a lower bound.

## Baseline, measured just now

Run `run_output_44a21e3e8_20261020T085542Z.json`. The book is rebuilt with
`build_dd_balance_book` with dual-fuel offsets on, as the run sets them. The closed set is
`closed_ids_from_bills`, not the run's own churned set, so the figures carry that difference.

| Arm | Bars written off | of which at reviews | Bar actions | Step-ups | Barred if sought at run end |
|---|---|---|---|---|---|
| never seeks (the run as it was) | £23,199 | £0 | 141 | 0 | £57,625 |
| seeks (the run from now) | £27,643 | £25,211 | 379 | 1,091 | £1 |

## Predictions, for the first run carrying this commit against a same-world run without it

- **S1.** The run's `dd_balance_book` reports `seek_balance_at_review: true`, and
  `back_billing_barred_if_sought_at_run_end_gbp` is under £50.
- **S2.** DD back-billing write-offs on the ledger rise by between £3,500 and £5,500. Baseline:
  +£4,444.
- **S3.** Net margin falls by the S2 amount, within ±£500. Nothing else in the P&L moves, because
  phase 2b does not read the book. *Refuted if* net margin moves by more than £6,000, or rises. That
  would mean something reads the step-up that I have not found.
- **S4.** The billing page's headline barred share rises, about 35% to 39% on the 19 Oct book,
  while barred plus open exposure falls by more than half. The rising share is the denominator
  growing: more accounts are asked. The page must still show both arms
  (`site/test_the_billing_accuracy_reaches_the_reader.py`).

Graded here, beside each line, when the run lands.
