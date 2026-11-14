**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 2 · **Atom:** `EP4_collections_journey`

# Pre-registration: the 16 Nov book on the N29 rows (2026-11-12)

Filed on 12 Nov, before the 16 Nov 04:00 book exists. Direction holds new books until then ("A book run now would
have to be rerun"), so the item `n29-setoff-ceiling-graded-on-fresh-book` cannot grade one today. This file
records what it should read.

## The replay this rests on

The page chain (customer data, ledger, invoices, payment ledger, reaction chain) was built at origin 90279e5318
over `/var/tmp/n29/run_setoff.json` (producing commit 6fe7827ab2). It was graded the way the publisher grades
(`runner.load_book` + `runner.run`). The results are in `/tmp/n29g/inv_pub.json`.

- `INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO`: **5 breached** of 1,683. This matches the 1c66aceab6 reading.
- `INV_A_CLOSING_REFUND_IS_WITHIN_THE_HOUSEHOLD_CREDIT`: **29 of 124**.

## A cause for each of the 5 (measured, `/tmp/n29g/cause.py`, `/tmp/n29g/dates.py`)

| leg | page credit left | origin walk closing | run's refund + set-off | cause |
|---|---:|---:|---:|---|
| PROS-2019-0318 | 65.17 | -176.50 | 111.33 | cross arm |
| PROS-2021-0117 | 133.14 | -133.14 | 0 (the run closed it at 0.00) | cross arm |
| SYN-2016-047 | 106.30 | -417.44 | 311.14 | cross arm |
| SYN-2016-142g | 120.49 | -120.49 | 0 (the run closed it at 0.00) | cross arm |
| SYN-2016-139 | 32.04 | -32.04 | 32.04 | **refund clock** |

- **Cross arm, 4 of 5.** The page credit left equals origin's walk closing minus the run's refund, to the penny, for
  each of the 4. This is the class in
  `WORKER_FINDING_THE_PAGE_RE_WALKS_THE_CLOSE_AT_ITS_OWN_COMMIT_SO_AN_OLDER_RUNS_REFUND_LOG_MEETS_A_NEWER_CREDIT_2026-11-11.md`.
  The run sized its refunds with `balance_settlement_from_outcomes` at 6fe7827ab2. The page re-walks the account
  at HEAD, and `simulation/arrears_engine.py` changed by 97 lines in between. The earlier one-variable control (the
  same JSON, with page code at 123dd6d525 and then at 1c66aceab6) places the change at 1c66aceab6, the level leaver's
  closing credit meeting its final bill only.
- **SYN-2016-139 is a disagreement inside origin's code, not a cross arm.** Origin's walk and the run agree on the
  amount (32.04) and on the refund clock's start (`money_in_out` = 2022-04-27). The page prints no cash on 27 Apr,
  only a returned direct debit and a GBP 0.00 `credit_applied` (the household's payment of 2021-05-07, netted
  against the final bill). So the page starts the reg 6D clock at the 13 Apr final bill, and the clock ends on
  29 Apr. The refund was paid on 12 May. See `SEAT_FINDING_OLD_CREDIT_NETTED_AT_CLOSE_STARTS_THE_REFUND_CLOCK_LATE_2026-11-12.md`
  in `docs/staging/`.

## Predictions for the 16 Nov book, graded by the publisher

1. `INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO` breaches only on **SYN-2016-139** (−32.04 on 29 Apr 2022). Any other
   account breaching would show this file wrong. The 4 cross-arm legs read 0, because the run and the page walk at
   the same commit. If `simulation/arrears_engine.py` or `simulation/credit_refund_events.py` moves between the
   book's `producing_commit` and the publisher's HEAD, this prediction does not apply. Say so rather than grade it.
   Different households may draw, because the book carries other fixes. Read "only SYN-2016-139" as "only
   refund-clock breaches of the same class".
2. The blind row reads **29 ± 3 breached** (the replay at HEAD reads 29). It does not read 31, the figure the
   exception's own text predicted, which was taken on 123dd6d525. Lower the ceiling to the count it reads.
3. The total of refunds with a set-off is 42 legs, ±5, because the book carries other changes.

## Amendment, 2026-11-14: what the insulation change (e17ebc596) moves, before the book exists

This amendment is about e17ebc596 only. It changes the world's insulation draw after the predictions above were filed.
The one-variable book A/B, e17ebc596^ against e17ebc596, same seed, neither arm carrying ceeefa5960 or 69866925b (`docs/staging/records/SEAT_RECORD_WHAT_THE_INSULATION_CHANGE_CAN_MOVE_IN_THE_16_NOV_PREREGISTRATIONS_2026-11-13.md`). The predictions above are kept as filed. **Fabric can move this file's counts.** Subtract the shift below
before grading the 16 Nov book, which carries this change as well as the ones the predictions were written for.

| | e17ebc596^ | e17ebc596 | now predicts |
|---|---:|---:|---|
| P1 `INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO` breached | 0 of 1,668 | 0 of 1,679 | unchanged. The breach count did not move. **PROS-2021-0117 is not on the new book** (the campaign no longer wins it), so the cross-arm check reads 3 legs, not 4 |
| P2 blind row breached | 30 of 129 | 31 of 130 | **30 ± 3** (was 29 ± 3) |
| P3 refunds with a set-off | 45 of 184 | 43 of 187 | **40 ± 5** (was 42 ± 5) |

PROS-2019-0318 stays on the book and moves from POOR to PARTIAL. No household with a changed fabric is named in P1.

**Reverse.** Delete this file.
