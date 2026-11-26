**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`
**Knowledge:** `home-moves` -- `docs/market_research/home_moves.md` s.8.8g (GAP G8.19, third bullet), s.8.8h (choice 32)

# Result: the four unattributed final bills are one fixed leg, two grader artefacts and one page cause (2026-11-26)

This answers the "not attributed" line of
`SEAT_FINDING_THE_WORLD_PRESENTS_A_LEVEL_DD_BEFORE_A_PAYER_IS_NAMED_2026-11-25.md` (a7778473f). That record left four
legs (GBP 74.63) of the 23 switch-away final bills, where the world takes more than the page nets, with no cause:
SYN-2016-099, SYN-2016-144g, PROS-2017-0293g and PROS-2024-0270g. All four are now attributed. The residue, on both
the baseline book and the latest book, is **one shared cause**: the page resolves a final bill against its face, not
against the world's ask. That cause is already filed as
`docs/staging/SEAT_FINDING_SYN_2016_244_THE_PAGE_PRINTS_A_FINAL_BILL_REFUND_THE_WORLD_NEVER_MADE_2026-11-26.md`, and
this result widens that finding's class.

## What each figure counts

- **Final bill**, on the world side: one `final_month_nets` row of `world_walk_truth_<book>.json` with
  `ever_level` true. `credit_taken_gbp` is the ledger credit (level surplus and credit notes) the world nets
  against the face before it asks.
- **Page net**: the `kind == 'credit'` entries that `balance_settlement_from_outcomes` posts against that same bill,
  keyed `(leg, period_end, commodity)`.
- **"World takes more"**: `credit_taken_gbp` exceeds the page net by more than 0.01, in the row's own bill month.

## 1. The grader read the wrong row for two of the four

`allnet.py` (reproduced in the a7778473f record) took the final bill to be **the last row `_resolve_bills` emits for
the leg**. On a leg whose last failed level collection is settled by a repayment, that last row is the **settlement
repayment** (`outcome == 'repayment'`). Its `period_end` falls in the final-bill month, so the month filter passed it.
The credit lookup then keyed on the repayment's date, found nothing and read the page net as 0.

- **SYN-2016-144g** (Mar 2017). The last row was a repayment dated 2017-03-08. The page posts a credit of 31.60
  against the final bill (2017-03-18). The world's `credit_taken_gbp` is 31.60, so they **agree**.
- **PROS-2017-0293g** (Sep 2020). The last row was a repayment dated 2020-09-25. The page posts 7.44 against the
  final bill (2020-09-17). The world's take is 7.44, so they **agree**.

The corrected grader takes the last non-repayment row with the latest `period_end` (`/var/tmp/rev31/allnet2.py`, the
two-line change below). It drops both legs. It also admits final bills that the old grader's month filter had
silently excluded. On f2c6979d01 the count is therefore **27 world-takes-more bills, GBP 742.08**, not 23 and GBP
675.99. Of the 27, 22 are `OCC-` legs and 5 are not.

```python
for r in res:
    if r.get('outcome')=='repayment': continue
    if r['customer_id'] not in last or r['period_end']>=last[r['customer_id']]['period_end']: last[r['customer_id']]=r
```

## 2. SYN-2016-099 is fixed at the world

This leg is attributed by `home_moves.md` s.8.8h choice 32 (`d688a224a6`, a leg's bills are issued in period order;
closed in `1eefc88d58`). The 91c32797b3 book predates that fix and still shows the leg (0.62).

## 3. The residue is one page cause

Corrected grader, run from a worktree at each book's own commit:

| book | world takes more | of which `OCC-` | non-`OCC-` legs |
|---|---|---|---|
| f2c6979d01 (baseline) | 27, GBP 742.08 | 22 | SYN-2016-099, SYN-2016-244, SYN-2016-360g, SYN-2016-139, PROS-2024-0270g |
| 91c32797b3 (latest, descends from a7778473f) | 6, GBP 132.44 | 2 | SYN-2016-099, SYN-2016-244, SYN-2016-360g, SYN-2016-139 |

Leave out SYN-2016-099 (section 2). Every remaining leg on 91c32797b3, and PROS-2024-0270g on f2c6979d01, has the
same shape. The world closes the account the way SLC 27.17 says: one final bill states the one balance, so the
ledger credit is netted against the face and the household is asked `face - credit_taken + debit_asked`. The page
never sees `credit_taken`. It resolves the final bill against its **face** and leaves the leg's credit in the walk,
where it comes out by one of two routes:

- **(a) The credit is held to the close and printed as a refund.** SYN-2016-244: the page pays 52.26 and refunds
  26.71; the world asks 25.55. SYN-2016-360g: the world takes 3.03 and asks 0; the page pays 3.03 and refunds 27.68
  at the close. The world's ledger credit is 9.29, so on this leg the two credits also differ. That is a second
  divergence, *not* explained here.
- **(b) A failed final DD is resolved on the face.** The page applies the world's `part_share` to the face, and
  takes the level surplus as `level_collection_difference` at the close.
  - Where `part_share` is 0, the closing balance agrees: SYN-2016-139 (page 5.19, world ask 5.19) and
    PROS-2024-0270g on f2c (19.75, 19.75). Only the printed lines differ.
  - Where `part_share` is above 0, the balance itself differs:
    - OCC-6387bf64272a: the page closes at 4.64. The world asks 7.57, of which 38% is paid.
    - **OCC-cede70b10116g**: the world asks 3.61. The page records 57.23 paid (0.4855 x the 117.87 face) and then
      refunds 53.62. The page prints about GBP 55 of cash in that never moved.

This is the remedy the SYN-2016-244 finding already names. `world_payment_truth` should carry `credit_taken_gbp`
beside `debit_asked_gbp`. `_resolve_bills` should resolve a final bill against `face - credit_taken + debit_asked`,
and `part_share` should apply to that ask. `balance_settlement_from_outcomes` should post `credit_taken` against the
bill. It is not built in this turn, because it moves the close, the refund clock and
`INV_A_CLOSING_REFUND_IS_WITHIN_THE_HOUSEHOLD_CREDIT` together.

## a7778473f's pre-registration, graded on 91c32797b3

The 91c32797b3 book descends from a7778473f. Each prediction is graded with the record's own scripts, run from a
worktree at 91c32797b3:

- **P1. Pass.** Level cash in no-payer months: 0 legs, GBP 0 (from 137 legs, GBP 27,134.55).
- **P2. Pass.** `OCC-` final bills where the world takes more: 2 (OCC-6387bf64272a, OCC-cede70b10116g), inside the
  predicted 0 to 2. Both are route (b) above.
- **P3. Pass.** World-takes-more final bills: 4 bills, GBP 135.43 with the record's grader; 6 bills, GBP 132.44
  with the corrected one. Both are inside 2 to 8 and under GBP 150.
- **P4. Refuted.** Closure refunds on `OCC-` legs moved from 30 refunds, GBP 4,907.79, to 36 refunds, GBP 6,425.09:
  **+1,517.30** on the same 264 `OCC-` legs (+1,092.37 on the 30 legs refunded in both books, and 424.93 on 6 legs
  newly refunded). The prediction allowed GBP 50. Four other commits lie between the two books, so this move is not
  yet a7778473f's alone. **Lead, not verified:** every one of the top five movers starts level collection three
  months later, and at a re-sized amount. OCC-654d4bb148dag goes from 27.75 to 53.04, and its level total rises from
  494.00 to 638.36 over fewer months. The likely mechanism is G8.19's second bullet: the level amount is still sized
  from bills that include the window months, but it is now collected over fewer of them. So it over-collects, and
  the close refunds the excess.

## Prediction (filed before any book carries the page fix)

On the first book whose commit carries the SYN-2016-244 page fix, graded with the corrected grader from a worktree at
that commit:

- **Q1.** Final bills where the world takes more than the page nets: **0**, apart from any SYN-2016-360g-like leg
  whose world and page credits differ before the final bill. There should be at most 1 of those.
- **Q2.** No final bill whose world `part_paid_gbp` is 0 shows a page `part_paid_gbp` above 0.01.
- **Q3.** Closing balances move only on route (a) and route (b) legs with `part_share` above 0. Every leg like
  SYN-2016-139, where `part_share` is 0, keeps its closing balance to the penny.

**Reverse.** This file only attributes and predicts. Deleting it restores the "not attributed" line.
