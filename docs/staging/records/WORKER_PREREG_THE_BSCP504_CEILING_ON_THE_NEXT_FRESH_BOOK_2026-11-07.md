**Severity:** RECORDED · **Lane:** D_billing · **Epoch:** unassigned · **Atom:** `unminted`

# [PREREG] The BSCP504 ceiling on the next fresh book (2026-11-07)

Written before any book carrying the change exists. The change: an electricity bill's domestic ceiling is
the larger of the 2,100 kWh/month screen and twice its registry figure's share of the bill's days
(BSCP504's read-validation rule), and the VAT half lifts only on a listed dwelling
(`docs/market_research/how_far_a_settled_eac_sits_from_next_years_use.md` §5). Gas is unchanged.

Measured on the fd91027799 book's ledger before the change (not a prediction): the exception queue is 16
bills, all on SYN-2016-175, SYN-2016-355 and PROS-2017-0233, each 0.91-1.18x its PC1 registry share and
1.00x its PC2 share.

**Predictions for the first fresh book built at or after the landing commit:**
1. No exception-queue entry is an electricity estimate on a listed dwelling with a registry figure whose
   kWh is within twice that figure's share. On a book drawing the same three homes, all 16 leave the queue.
   **Refuted** by any such entry.
2. The lift never adds a hold: every queued bill would also have been queued under the screen alone.
   **Refuted** by any queued bill under 2,100 kWh/month-equivalent held on a ceiling reason.
3. INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL reads 0, and its exception retires. **Refuted** if any of the
   14 checks remain; then the residual is the panel's own shape (no true-up kWh in the month it reconciles).
4. INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER and the catch-up rows on these three homes: **I cannot
   say.** Energy that was billed at the next read is now billed monthly, which moves both. No prediction.

## Addendum, 21:25 UTC 7 Nov: a control on the pre-change book, filed before it is read

The ledger builder runs `validate_bills` again with the code at the grader's HEAD
(`tools/generate_billing_ledger.py:377`). So grading the fa915ac0d7 book (built before 8b6316995) at HEAD
5035e71d4c separates the ledger-side lift from the run-side one (energy no longer rolled to the next read).
Predicted for the control: (1) and (2) as above, with no ceiling hold on the three homes; (3) **I cannot say**,
because the usage panel is drawn from the run's bills, which still carry the roll-forward. The fresh book
then adds only the run-side change.

**The control, read 21:20 UTC** (`/var/tmp/grade-8b63/fa915/`, the b3ce chain's `ledger.py` then `grade.py` at
5035e71d4c): exception queue **0** (16 on fd91027799 before the change), so (1) and (2) hold on the ledger side;
INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL **0 of 5,667** (14 on fd91027799), so the ledger-side lift alone clears
it, against my "cannot say". INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE stays **3**, exactly the three homes
(page bills 1.17-1.18x run revenue): the ledger now issues energy the run still rolled forward, so the fresh
book is where that row moves (filed at 20:39: at most 1). Est-run 7, none on the three homes.
