**Severity:** RECORDED · **Lane:** C_customer_ops · **Epoch:** 2 · **Atom:** `EP4_collections_journey`

# The statement walk (84a44b51c3) does not move the N29 blind row: 0 of the 8, so the prediction on file is refuted (2026-11-16)

*Claim `n29-blind-row-23-attributed`. This grades the prediction filed in
`SEAT_RESULT_THE_16_NOV_BOOK_ON_THE_N29_ROWS_2026-11-16.md`: "a one-variable page rebuild of this run at 84a44b51c3^
against 84a44b51c3 moves the blind row by most of the 8. If it moves by 2 or fewer, the cause lies elsewhere in
the window."*

**My prediction, filed before the rebuild** (`/var/tmp/n29b/PREDICTION.txt`): it moves by **0**. The blind row reads
`ledger.entries` in `site/data/customers/<id>.json`. Only `tools/generate_payment_ledger_data.build_account_ledger`
writes that field, and importing that module never loads `company.billing.statement_export`.

## The measurement

- **Input, the same for both arms:** the published billing ledger (`docs/state/billing_ledger.json`, built from
  run `f7e17b1316`, 1,306 customers) and a copy of the published customer pages. The 8a300fa561 book's ledger was
  no longer on the shared tree. The variable under test is code, not the run, and this book also reads 23 of 132.
- **Arms:** detached worktrees at `84a44b51c3^` and `84a44b51c3`. Each ran `generate_payment_ledger_data.generate`
  over its own copy. `statement_export` was loaded in neither arm.
- **Grade:** the current runner's `ev_closing_refund_within_household_credit` over each set of pages.

| | checked | breached |
|---|---:|---:|
| published pages, not rebuilt | 132 | 23 |
| rebuilt at 84a44b51c3^ | 132 | 23 |
| rebuilt at 84a44b51c3 | 132 | 23 |

`diff -rq` finds **0 differing files** across all 1,306 pages, both between the two arms and between each arm and
the published pages. **Movement: 0. The prediction on file is refuted. Mine held.**

## Where the 8 can come from

- **Not the page code, in the whole window.** 19 commits in `e17ebc596..8a300fa561` touch the page builder's import
  closure, all of them in `company/billing/collections_journey.py`, `winter_moratorium.py`, the PSR register,
  `decision_event_ledger.py`, `generate_explore_cast.py` or `wall_protocol.py`. Rather than argue each one, a second
  rebuild was pre-registered (addendum in `/var/tmp/n29b/PREDICTION.txt`, prediction 0). It used the same ledger and
  pages, with worktrees at **e17ebc596** and **8a300fa561**. The result is 0 differing files out of 1,306, so the
  blind row reads 23 in both. **The whole move from 31 to 23 is upstream of the page.** It lies in the run (refunds
  and their days), in the billing ledger built from it, or in which households are graded. This test cannot see a
  change to the code that builds the billing ledger, because both arms read one ledger.
- **Not S6b (69866925bd).** On this same book its one-variable arms show 0 refund paid-date moves and identical
  closing balances (`SEAT_RECORD_S6B_GRADED_ON_THE_16_NOV_BOOK_ZERO_NETTING_DAYS_AND_NO_REFUND_MOVES_2026-11-16.md`).
- **The leading candidate is ceeefa5960** (reg 6D's clock starts on the day the final bill is issued). It is in the
  8a300fa561 book. Neither e17ebc596 arm carries it: the 14 Nov amendment says "neither arm carrying ceeefa5960 or
  69866925b". It moved 134 of 176 refund clocks, which moves refund **days** but not amounts. That fits every
  fact: P3's amounts match the e17ebc596 arm to the penny, while the blind row grades credit **per day** (this
  leg's credit and the other leg's end-of-day debt on the refund day). This is a hypothesis, not yet measured. The
  population change (130 → 132 households graded) is the other open explanation. *Measured 2026-11-16 (`SEAT_RESULT_THE_REFUND_CLOCK_MOVES_THE_N29_BLIND_ROW_31_TO_23_2026-11-16.md`): ceeefa5960 is the whole move, 31 of 130 → 23 of 132 on one run; the +2 is two refund lines leaving choice 24's unbounded set, not new households.*

**Next, a one-variable test:** the world refund log and page at ceeefa5960^ against ceeefa5960 on one run, grading
the blind row. Handed on as `n29-blind-row-ceeefa5960-one-variable`.

## Corrections made beside the claims

- In `SEAT_PREREG_THE_16_NOV_BOOK_ON_THE_N29_ROWS_2026-11-12.md`, the 16 Nov correction said the statement walk's
  effect on P2 was "unproven". It is now measured at 0, so the original line, "the statement walk cannot move them",
  holds for P2.
- In `SEAT_RESULT_THE_16_NOV_BOOK_ON_THE_N29_ROWS_2026-11-16.md`, the claim that "84a44b51c3 changed what the page
  prints for the 84 set-off legs" was wrong. It changed the *statement*, `statement_export`, not the customer page
  the blind row reads.

**Reverse.** Delete this file and revert the two marked corrections.
