**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 2 · **Atom:** `EP4_collections_journey`

# Result: the closing set-off netted in the debt leg's own walk, replayed over 6fe7827ab2 (2026-11-12)

This reads against `SEAT_PREREG_THE_SET_OFF_NETTED_IN_THE_DEBT_LEGS_WALK_ON_6FE7827AB2_2026-11-12.md`. It
follows `SEAT_RESULT_THE_CLOSING_DUAL_FUEL_SET_OFF_REPLAYED_OVER_6FE7827AB2_2026-11-12.md`.

## What landed

`balance_settlement_from_outcomes(set_offs=)` nets each closing set-off against the debt leg's outstanding
bills, oldest first, as `kind` "set_off". It does this after `closing_out` is taken and before the write-off at
close, and it lowers the one balance a level leg is written off against. `set_offs_from_refund_log` turns the
run's `credit_refund_log` into that input. The run walks a second time with it, for the P&L lines and for debt
recovery. The page's walk reads the same input from the run JSON, so its case gets a CREDIT_APPLIED stage.
The P&L cut the first build posted beside the case is gone. Test:
`tests/simulation/test_a_closing_dual_fuel_household_is_set_off_before_it_is_refunded.py` (10 tests). All 7
mutations fire: no closing reduction, netting a non-leaver, the wrong kind, ignoring the remaining amount, the
loop off, no log rows, and the wrong `other_leg`.

## The readings (the publisher's ledger page chain over `/var/tmp/n29/run_setoff.json`, scratch tree)

| book | blind row | `INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO` | page write-offs, all legs |
|---|---|---|---|
| 6fe7827ab2 as published (control) | 60 of 149 | 0 breached, 87 flagged | GBP 26,821.26 |
| set-off posted beside the case | 31 of 124 | **4 breached**, 69 flagged | GBP 26,821.26 |
| **set-off netted in the walk** | **31 of 124** | **0 breached**, 69 flagged | GBP 26,749.03 |

No other row of the runner moved against the control.

## Against the predictions

1. **Held.** 0 breached. All 4 legs (OCC-6387bf64272a, SYN-2016-323, PROS-2016-0207, OCC-cede70b10116g) close at 0.
2. **Held, at the top of the band.** It reads 31. Netting in the walk does not change the debt leg's page balance
   on the refund day, so the same 31 two-walk households remain.
3. **Wrong.** I predicted the page write-offs would fall by GBP 1,000 to GBP 1,339.69. They fell by GBP 72.23. The
   world's walk falls by GBP 390.59, all of it on the close line. The cause is one I did not check before
   predicting: **all 42 debt legs are on a level direct debit.** GBP 949.10 of the GBP 1,339.69 set off met
   debt that the world's walk never wrote off. That is the part of a level leg's one balance its bills do not
   hold, a standing debt (s.8.8b choice 3). So the set-off lowered the balance there, not the write-off. The page balance on the 42 debt legs falls from GBP 1,927.21 to
   GBP 659.75. The gap between the walk's 390.59 and the page's 72.23 is on legs where the page's write-off
   already differed from the walk's before this change. That is the page/world two-walk class.

## What is still open

- **The 31.** These are households where the other leg's page balance differs from the world's closing balance.
  The two-walk class carries them. 23 of the 42 debt legs still print a non-zero balance after the set-off
  (GBP 659.75 in all). Each needs a cause.
- **The exception's ceiling** stays at 60 until a fresh run is graded. Then lower it to the count (31 predicted).
- `tests/tools/test_the_ledger_and_the_pnl_write_off_agree_on_the_real_book.py` was **red at clean origin/main**
  (39744630a1, measured in a detached worktree). It went red when 07111cd8b4 committed the 6fe7827ab2 book: 84
  accounts disagreed, and the book carries no held bill. It refused this landing's first attempt. Two reader
  defects are fixed in it. Its P&L side now passes `level_dd_collections` and the set-offs, as the run's own
  P&L does (84 -> 59). It reads the `WRITTEN_OFF` stage's amount, not the case's face, the reader defect
  named in `SEAT_FINDING_A_LEVEL_RETURN_CASE_IS_CAPPED_AT_ITS_OWN_BILLS_REMAINDER_2026-11-09.md` (59 -> 44).
  The 44 left are that finding's open level-paid class (P3). They are held by a **ceiling of 44**, which fires
  at 43 (mutation-checked), so a new disagreement still refuses. The held-bill vacuity leg is
  `xfail(strict=True)`, naming the book. Both come off as the class is fixed.

## Re-read after porting onto fix 2 (worker, 2026-11-12)

The salvage was ported onto origin/main 123dd6d525, which sits on top of fix 2 (9392920e60). The page
chain was re-run over `/var/tmp/n29/run_setoff.json`, the same run JSON, through `generate_customer_reaction_chain`,
and graded by the runner. A control did the same with clean origin/main.

| tree | blind row | `INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO` |
|---|---|---|
| origin/main 123dd6d525, no set-off (control) | 31 of 149 | 31 breached, 87 flagged |
| **origin/main + this build** | **31 of 124** | **1 breached**, 69 flagged |

**Correction.** This file read 0 breached above, and on the new base it reads 1. The 1 is SYN-2016-139: GBP 32.04
of credit is unrefunded on 2022-04-29, and the refund was paid on 2022-05-12. The household has no set-off. Its
page ledger is byte-identical with and without this build, and the control breaches on it too. So this build did
not cause it. Something that landed between 0367c57375 and 123dd6d525 moved it. My guess is fix 2's page side
meeting a run JSON written before fix 2. I cannot yet say, because the run JSON is older world code read by newer
page code. A fresh run settles it. On 16 Nov that row needs this account graded or excepted by name.

The 7 mutations were re-run on the port and all 7 fire. The control's blind row reads 31 of 149 against the
build's 31 of 124, because the run JSON already carries the netted refund log. The 60 is the published book's
count.

## Re-read at landing, on 1c66aceab6 (worker, 2026-11-12)

The port above was killed before it landed. The same diff was applied to origin/main 1c66aceab6, which
adds the level leaver's final-bill netting on top of bd58577a2c. The full page chain (customer data, ledger,
invoices, payment ledger, consumption, reaction chain) was re-run over `/var/tmp/n29/run_setoff.json` and
graded by the runner, with a control on clean 1c66aceab6 over the same JSON.

| tree | blind row | `INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO` |
|---|---|---|
| origin/main 1c66aceab6, no set-off (control) | 29 of 149 | 33 breached, 87 flagged |
| **1c66aceab6 + this build** | **29 of 124** | **5 breached**, 69 flagged |

**Correction to the re-read above.** It read 1 breached; on this base it reads 5. Before the control I
predicted that all 5 also breach without the build, and they do: SYN-2016-139 (as before), PROS-2019-0318,
PROS-2021-0117, SYN-2016-047 and SYN-2016-142g. On 3 of them the build lowers the unrefunded credit
without clearing it. The 4 new ones came with 1c66aceab6, the page-side leaver netting, meeting a run JSON
written before it. That is the same older-world, newer-page cause as SYN-2016-139, and it is still a guess
until a fresh run. The 7 mutations were re-run on this tree and all 7 fire.

## Landed from the second salvage (delivery seat, 2026-11-12)

The landing above was killed too. Its work survived as SALVAGE e88651bf48, which is this diff on 1c66aceab6.
The seat applied it to origin/main at landing time, and the patch was byte-identical. No commit between
1c66aceab6 and that base touches `simulation/`, `company/billing`, `company/interfaces`, the
`tools/generate_*` page writers, the runner or the invariant files, so the page chain this build feeds is the
code the 1c66aceab6 reading graded. The page chain was **not** re-run. That table stands as the measurement:
29 of 124 on the blind row and 5 breached, all 5 in the control. The 10 tests and the 7 mutations were
re-run on this tree.

**Reverse.** Delete this file.
