**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** none — Lane 0 `a-read-to-read-bill-drops-no-energy`

# Pre-registration: every actual read nets its run, and the catch-up's VAT is on the VAT line (2026-10-29)

**Written 2026-10-29, before the replay below was run.** Two fixes are graded together:
- **F**, this item. `_resolve_catchup`'s £5 floor no longer drops the correction. Finding:
  `SEAT_FINDING_AN_ACTUAL_READ_UNDER_FIVE_POUNDS_OFF_THE_ESTIMATES_NEVER_CORRECTS_THEM_THE_REVENUE_ROWS_CLASS_E_2026-10-29.md`.
  Knowledge: `docs/market_research/how_a_supplier_shapes_an_estimate_for_an_unread_month.md` §9.
- **789d0a6d2**: the catch-up's VAT moves onto `vat_gbp`. Finding:
  `SEAT_FINDING_A_CATCH_UP_IS_ADDED_TO_THE_BILL_GROSS_AND_ITS_VAT_NEVER_REACHES_THE_VAT_LINE_2026-10-29.md`.

The 9553d403b7 book (`/var/tmp/fresh-run-out-9553d403b7`) predates both fixes.

## Predictions, written before measuring

| quantity | on the 9553d403b7 book | predicted after F + 789d0a6d2 |
|---|---|---|
| actual-read reconciliations of an estimate run left uncorrected (non-zero) | 2,747 | **0** |
| bills carrying a catch-up whose VAT line leaves out the catch-up's VAT | 3,705 | **0** |
| `INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE` breaches | 25 | **1** (PROS-2017-0117, an open run of under-estimates; neither fix touches it) |

**Predicted for the offline replay:** the 24 named accounts in the two findings leave the row and
no account enters it. **What would refute it:** any of the 24 still breaching, or a new breach.
That would mean the correction's ex-VAT amount does not equal the account's gap. A back-billing bar
on a dropped sub-£5 run is one way that could happen (a run reaching past 12 months). Bars cannot
make the dropped count non-zero, since a fully barred run has `chargeable_gbp` 0.

**Predicted for the next fresh run (item 2), the same three rows:** 0, 0, and at most 1 breach on
the revenue row, plus any new open-estimate-tail accounts. Each of those must be named as an open
tail. Applied catch-ups rise from 3,705 by about the 2,747 formerly dropped, less any run that
rounds to 0.00. A rise of more than 10% either way is a surprise to trace.

## Method

The replay does not re-run the world. It reads the book's own bills (`top__bills.pkl.gz`) and changes
two things:
- each dropped run's correction is applied, ex-VAT, to the account's billed amount;
- each applied catch-up's VAT, Σ(`true_vat_gbp` − `vat_gbp`) over its run, is moved out of the
  before-VAT amount.

It then grades each account on the row's band (R ± U ± 1% R), with the page's R and U taken from the
graded book. The script is `/var/tmp/clse/replay_f_vat.py`.

## Result

*(Filled below after the replay, unedited above this line.)*
Replay run 2026-10-29 at 969ba56b6b with the F fix in the tree, `/var/tmp/clse/replay_f_vat.py
/var/tmp/fresh-run-out-9553d403b7 /var/tmp/clse/book9553.pkl`:

| quantity | 9553d403b7 book | after F + 789d0a6d2 (replay) | prediction |
|---|---|---|---|
| actual-read reconciliations of an estimate run | 6,452 | 6,452 | — |
| left uncorrected, non-zero | **2,744** | 0 (the fix applies every non-zero run; `test_a_read_to_read_bill_drops_no_energy.py`) | 0 ✔ |
| applied catch-ups whose VAT is not on the VAT line | 3,705 | 0 (789d0a6d2) | 0 ✔ |
| revenue-row breaches | 25 | **1**, PROS-2017-0117 (value 2,175.55 against lower bound 2,202.09) | 1 ✔ |

No account entered the row. All 24 named accounts left it.

**Correction, beside the count.** The finding's 2,747 "dropped as immaterial" includes 3 runs whose
correction rounds to £0.00. Those still add no line under the fix, which is right. The non-zero
dropped count is 2,744.

**Correction to the method, beside it.** The first replay pass took the catch-up's VAT as
Σ(true VAT − billed VAT) over the book's estimated bills. It gave 2 breaches, with PROS-2025-0106
moving the wrong way (681.12 → 701.95). The cause was the replay, not the code. Both of that
account's estimates were *held*. A held month enters the code's run at 0.00 billed and 0.00 VAT
(`monthly_bill_assembly` lines 987–991), but the book's bills carry the would-be amounts and no
held marker. The pass graded above takes the VAT from the correction's own gross, at the bill's
rate. 789d0a6d2's own formula reads the run's held entries, so it was already right.

**PROS-2017-0117's residue, named.** An open run of under-estimates on an account whose history ends
on an estimate, so no read reaches a catch-up. Its value rose from 2,148.44 to 2,175.55 (an earlier
dropped run was netted), but it is still below its band. This is not class F or the VAT defect. It
stays on the exceptions file as the open-tail class.

## Item 2: no run at e83e2de665 exists to grade (2026-10-30, seat executor)

Lane 0 `grade-the-e83e2de665-book-every-read-nets-its-run` was drawn to grade the three rows above
on `fresh-run-e83e2de665`. That run was never launched, so no book exists to grade. The pre-launch
tests at e83e2de665 (`/var/tmp/pretest-e83e2de665.log`) found 1 red in 5,047:
`test_the_accounts_closing_balance_is_the_sum_of_its_two_fuels`. It was bisected to 789d0a6d20,
whose pre-bill VAT-rate check graded a base that included the catch-up line, so a catch-up bill
was held (a held final credit bill means the credit is never given). The run's owner landed the
fix in its own worktree as dc5762e0b, which is not yet on origin at 12210b3b6e. The run launches
at that commit instead.

The three rows are already in that run's grade chain (`/var/tmp/fresh-grade-e83e-scripts/after_run.sh`):
- `f_vat_rows.py` counts the first two rows. It reads 2,744 / 3,705 on the 9553d403b7 book, so it can fire.
- `/var/tmp/fresh-run-0b28-scripts/grade.py` grades the revenue row against
  `DOMAIN_INVARIANT_EXCEPTIONS.yaml`.

Grading the rows separately would only duplicate that chain, so this item is released without a
grade. The predictions above stand unchanged and are graded on the dc5762e0b book. One caution for
that grade: dc5762e0b changes `pre_bill_validation` only, which decides which bills are held, not
what a catch-up carries. It should not move the first two rows. A hold that changes could move the
revenue row by the value of a held bill.
