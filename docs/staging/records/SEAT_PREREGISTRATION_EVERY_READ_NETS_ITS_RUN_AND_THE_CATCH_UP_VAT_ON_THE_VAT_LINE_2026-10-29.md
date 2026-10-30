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

**Correction, beside the commit ids above (2026-10-30).** dc5762e0b was a worktree-local landing
and never reached origin. The fix reached origin as a83d60c27, merged as ecb7e21fb. The run is
`fresh-run-ecb7e21fb`, with output in `/var/tmp/fresh-run-out-ecb7e21fb` and grades in
`/var/tmp/fresh-grade-ecb7e21fb/`, both launched by synthetic-enterprise-49. Read
"the dc5762e0b book" above as the ecb7e21fb book.

## Item 2, drawn again: the work is the 3dc5a92948 run's, not a new one (2026-10-30, worker)

The same Lane 0 id was drawn a second time, asking for a fresh run at origin HEAD, graded on the
full suite, with the Explore pages built and the exception ceilings reset. That run already exists.
`fresh-run-3dc5a92948` was launched at 02:41Z under the seat's claim
`fresh-run-at-the-svt-one-list-price-fix` (ad7b0393a). Its commit contains class F (053377eac),
the catch-up VAT (789d0a6d2), the pre-bill VAT fix (a83d60c27), the desk cure (70e66b721) and
N1/N8/N9 (e8149d6d0, 90b330d09). At 02:45Z the run had reached 2016-05. Its chain,
`grade-chain-3dc5a92948.service` (`/var/tmp/svt-fix-run-scripts/chain.sh`), builds the ledger and
runs the five rows, the pre-cap SVT revenue and the full suite (`grade.py`) once `DONE.json` exists.
A second run would cost about the same hours to produce the same book, so this id is released.

The chain does not cover everything. On that book, after `ALLDONE`, three things are still owed:
1. build the Explore cast and customer pages, then grade the debt slot's four checks and the N1, N8
   and N9 households on them;
2. grade each prediction above, and P1 of the desk-cure record, as held or refuted beside it;
3. set each `max_breached` to what the book measures, and retire any row that reads 0.

Those three are the input `the-fifth-cold-read` waits on.

## The fifth cold read, drawn before its input exists (2026-10-30 03:35Z, worker)

`the-fifth-cold-read` was drawn while `fresh-run-3dc5a92948` was still computing: at 03:35Z the
log reached 2024-06, `DONE.json` did not exist, and `grade-chain-3dc5a92948` was still polling for it.
The direction row says "once item 2's grade and rebuilt pages are on origin, and not before", and
none of the three owed items above exists yet. So nothing was read, and the claim is released
without a reading. The three items stay under the live focus row `grade-the-e83e2de665-book-every-read-nets-its-run`
(the seat's `fresh-run-at-the-svt-one-list-price-fix` claim covers only the SVT and EPG rows). The
cold read can be drawn once `/var/tmp/fresh-grade-3dc5a92948/ALLDONE` exists AND the Explore pages
built from that book are on origin. Do not draw it on `ALLDONE` alone.

## Graded on the fresh 3dc5a92948 book (2026-10-30)

Every prediction for item 2 **held**:
- 0 of 6,452 reconciliations left uncorrected.
- 0 catch-ups with their VAT off the VAT line.
- Revenue row 1, PROS-2017-0117, the open tail named above (2,175.58 against 2,202.12).
- Applied catch-ups 6,447, within 10% of 3,705 + 2,747.

The full grade is in `docs/staging/records/SEAT_RECORD_THE_3DC5A92948_BOOK_GRADED_AND_ITS_PAGES_BUILT_2026-10-30.md`.
