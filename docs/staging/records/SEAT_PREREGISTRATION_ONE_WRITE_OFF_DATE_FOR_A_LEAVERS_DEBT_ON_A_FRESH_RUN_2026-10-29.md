**Severity:** INFO · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: one write-off date for a leaver's debt, graded on the first fresh run carrying it (2026-10-29)

Written before any run carries the change. Item `the-write-off-date-is-one-for-the-page-the-sweep-and-the-desk`.
It grades class (a) of `INV_OVERDUE_WITHIN_PAGE_BALANCE` alongside
`SEAT_PREREGISTRATION_A_CREDIT_BILL_POSTS_TO_THE_DESK_AND_THE_ROW_NETS_ONE_ACCOUNT_2026-10-29.md`
and `SEAT_PREREGISTRATION_AN_OCCUPIERS_BILLS_READ_THE_TRIADS_PAYMENT_TRUTH_2026-10-28.md`.

## What changed

The company's write-off of a closed account, a year after its final bill
(`company/billing/arrears_engine.closed_account_write_off_date`), is now the one date:
- the desk writes the balance off on that day inside its walk and ends the journey
  (`CollectionsJourneyDesk._write_off_if_closed`, rule `CLOSED_ACCOUNT_RULE`);
- the world's close write-off, which the page's arrears history and the P&L read, is dated by it
  (`simulation/arrears_engine.WRITE_OFF_DATE_CONVENTION = "company_closed_account_write_off"`).

Before: page at the final bill's due date; sweep a year after the final bill, after the loop; desk at
the six-year bar. Knowledge: `docs/market_research/debt_and_collections.md` s.7.3. Control:
`tests/company/billing/test_a_leavers_debt_has_one_write_off_date.py`, both legs mutation-proven.

## Baseline

b2fc50facf book, class (a): 723 steps on 112 households (33 on `OCC-`, 690 other).

## Predictions

- **P1.** Class (a) (a desk step dated on or after the page's first write-off on the household,
  overdue above the page's balance) falls from 723 to under 100. What is left: a dual-fuel account
  where one fuel leaves and the other stays (the page writes the leaving fuel off; the company's
  account is still billed, so it is not closed), and legs whose world final bill and company final
  bill differ by date.
- **P2.** On single-fuel leavers with a close write-off on the page, the desk's `write_off` stage
  under `CLOSED_ACCOUNT_RULE` is on the page's `WRITTEN_OFF` date on at least 95% of accounts.
- **P3.** Total bad debt (`emergent_bad_debt_lines` "total", summed over keys) moves by under 1%:
  amounts and the recovery share are unchanged, only dates move. Per-year figures may move where an
  account has a record in its write-off's new year; the grade lists any year moving more than 5%.
- **P4.** Desk statute-bar write-offs on leavers' accounts fall to near zero (a leaver is written off
  at a year, before any six-year bar).
- **P5.** The post-loop sweep (`company_provision.write_offs_posted`) posts under 10% of what it
  posted on the baseline: the desk has taken the rest on the same date.

A refuted prediction is kept here beside the result, not revised.
