**Severity:** RECORDED · **Lane:** C_customer_ops · **Epoch:** 2 · **Atom:** `EP4_collections_journey`

# The refund clock (ceeefa5960) accounts for the N29 blind row's whole move, 31 of 130 → 23 of 132 (2026-11-16)

*Claim `n29-blind-row-ceeefa5960-one-variable`. Tests the hypothesis in
`SEAT_RESULT_THE_STATEMENT_WALK_DOES_NOT_MOVE_THE_N29_BLIND_ROW_2026-11-16.md`: ceeefa5960 moves refund days but not
amounts, and the blind row (`INV_A_CLOSING_REFUND_IS_WITHIN_THE_HOUSEHOLD_CREDIT`) grades credit per day.*

**Pre-registration** (`/var/tmp/n29c/PREDICTION.txt`, filed before either arm was built):
- P1: the after arm reproduces the book, 23 of 132.
- P2: the before arm reads 28–33.
- P3: the denominator is 132 in both arms.
- Refutation: a gap of 2 or less.

## Method: one variable, on one run

- **Run:** `docs/reports/run_output_8a300fa561_20261116T031305Z.json`, the 16 Nov book. ceeefa5960 changes
  behaviour in one place only: `generate_credit_refund_log` starts reg 6D's clock on `bill_issue_date`. It used to
  start it on the final bill's period end. Its other two edits are algebraic identities. `simulated_bill_issue_date`
  equals the old due date less the payment terms, and `bill_due_date` is unchanged. The log is built in phase 4c,
  after the company loop has finished, so no company decision reads it. The run can therefore be replayed rather
  than re-run.
- **Arms:** two worktrees at 8a300fa561. **A (before)** reverts that one line to `period_end`. **B (after)** is the
  code as it stands. Each arm regenerates the refund log from the run (`/var/tmp/s6b/diff.py`). A's log replaces the
  run's `credit_refund_log` in a copy (`/var/tmp/n29c/cmp.py`). Both arms then go through the publisher's five-step
  page chain (`/var/tmp/fab-ab2/chain_full.py`) and are graded by `runner.run`.
- **Control:** B's regenerated log equals the run's stored log on **all 187 refunds**, field for field. A's log
  differs from it in 145 request days and 114 paid days, with **0 amounts** changed.
- **Scope:** the replay carries the log into the billing ledger (set-off days, refund days) and the pages. It does not
  redo phase 4c's own bad-debt re-walk inside the run JSON, and the page does not read that re-walk.

## Result

| | checked | breached | unbounded (choice 24) | banded lines |
|---|---:|---:|---:|---:|
| A: clock at period end (ceeefa5960 reverted) | 130 | **31** | 2 | 132 |
| B: clock at bill issue (the 8a300fa561 book) | 132 | **23** | 0 | 132 |
| *for comparison: the e17ebc596 book arm (14 Nov)* | *130* | *31* | | |

Arm A reproduces the e17ebc596 arm exactly, in both numerator and denominator. **ceeefa5960 accounts for all 8 of
the move and for the denominator's +2. On this row, nothing else in the window adds anything.** Every other row of
the publisher's verdict is identical across the arms: "19 unexcepted across 5 rows, 7 excepted" on both, and C5
and P1 are unchanged.

**The predictions graded:**
- P1: B reads 23 of 132. **Held.**
- P2: A reads 31. **Held**, and it is all 8 rather than "most".
- P3: denominator identical. **Refuted.** It is 130 against 132. The row's `checked` excludes unbounded lines. Two
  refunds that used to fall before their sibling leg had closed now fall after it, so the row grades them.

## The 12 lines that change (`/var/tmp/n29c/moved.json`)

There are 132 banded lines in both arms, one per leg. 120 keep their verdict: 99 are fine in both arms and 21 breach
in both.

- **10 go from breach to fine.** In each case the refund now falls 1–8 days later, and by then the household's other
  leg has stopped owing. Worked case: PROS-2017-0258g is refunded £32.90. Under the old clock that happens on
  14 Oct 2021, while its electricity leg PROS-2017-0258 still owes £59.52 on its final bill (paid by DD on 15 Oct), so
  the household credit is £0. Under the issue-day clock the refund falls on 22 Oct, after that payment, and the bound
  is £32.90. The other nine: OCC-654d4bb148dag, OCC-a040abd80a7fg, OCC-cede70b10116, PROS-2017-0264g, PROS-2019-0008,
  PROS-2020-0012, SYN-2016-144, SYN-2016-147g and SYN-2016-234g.
- **2 go from unbounded to breach.** SYN-2016-007 breaches with a bound of £28.08 against a £32.75 refund.
  SYN-2016-026g breaches with a bound of £0 against a £5.94 refund. Under the old clock, both refunds fell before
  the sibling leg's final bill, so the row could not set a bound (choice 24).

**What this does and does not say.** The 10 breaches clear because of **timing**, not because of any change to
netting. The earlier days were wrong: reg 6D's clock cannot start before the final bill exists (home_moves.md
s.8.8 choice 2). So these 10 were artefacts of an impossible date, and the 23 that remain are the row's real
residual. The fix is not cosmetic, but it also proves nothing about the netting itself. The 21 lines that breach in
both arms, plus the 2 newly bounded ones, are the next question for this row. So is any line where a set-off and a
sibling's last payment fall in a different order.

## Correction beside the earlier claim

In `SEAT_RESULT_THE_STATEMENT_WALK_DOES_NOT_MOVE_THE_N29_BLIND_ROW_2026-11-16.md`, "the leading candidate is
ceeefa5960 … a hypothesis, not yet measured" is now measured. It is the cause, and the alternative that the
population moved 130 → 132 is withdrawn. The +2 is these same two lines changing from unbounded to bounded, not new
households.

**Reverse.** Delete this file and the one-line correction it adds to the statement-walk record.
