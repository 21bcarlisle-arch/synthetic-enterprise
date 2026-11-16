**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

# S6b graded on the 16 Nov book: no money-in day is set by a netting day, and S6b moves no refund on this book (2026-11-16)

*Grades `docs/design/REPAYMENT_POSTING_AREA_MAP_2026-11-14.md` s.6 (amended 14 Nov) and the S6b pre-registration
`/var/tmp/s6b/PREDICTION.txt` P1–P5, both filed before 69866925b was built. Claim:
`s6b-graded-on-the-first-book-that-carries-it-and-the-139-exception-dropped`.*

## The book and its code

- **Book:** `docs/reports/run_output_8a300fa561_20261116T031305Z.json`, the 16 Nov 04:00 book. It was built,
  and its publish was refused. These are run-artefact grades, so they are read on the built run, as the
  06:23 direction record re-pointed them.
- **Ledger:** `/var/tmp/grade-c915/ledger_8a30.json`, built from the same run.
- **Code:** a worktree at 8a300fa561. `git merge-base --is-ancestor 69866925b 8a300fa561` holds, so s.6's
  **0** branch is the one graded.
- **One-variable before arm:** the same worktree with only the S6b line in `simulation/arrears_engine.py`
  reverted. It reads the netting `date` where the fix reads `credit_period_end`. Both arms read the same
  run and the same ledger, so every difference between them is S6b's.

## Results

| Line | Prediction | Before arm | 16 Nov book (after) | Verdict |
|---|---|---|---|---|
| s.6 amended | 0 request days set by a netting day | 0 | **0** | **held** |
| s.6 amended | coincident real arrivals counted apart | 0 of 69 | 0 of 69 | nothing to count apart on this book |
| P1 | netting-dated money-in days 24 of 66 → 0 of N, N = 66 | 22 of 69 | **0 of 69** | the 0 **held**; N = 69 rather than 66, because this is a different run (fabric moved 66 → 69, as s.6's second amendment said). No leg vanished. |
| P2 | money-in changes on exactly those legs, every one earlier | — | 22 change, 22 earlier, 0 later, 0 vanish, 0 new | **held** |
| P3 | PROS-2019-0318 ≤ 22 Nov 2022 | 22 Nov 2022 | 22 Nov 2022 | held (unchanged) |
| P3 | SYN-2016-093 ≤ 13 Sep 2016 | 15 Sep 2016 | 13 Sep 2016 | held |
| P3 | SYN-2016-360 ≤ 16 Feb 2017 | 19 Oct 2017 | 19 Oct 2017 | **missed**. S6b does not move it on this book, and the arms agree, so the leg's money-in day differs from r98's because of the run, not the fix. |
| P3 | SYN-2016-139 < 27 Apr 2022 | 18 May 2021 | 7 May 2021 | held |
| P4 | refund amounts unchanged; paid dates move earlier or not at all, on ≤ 24 legs | 187 refunds | 0 amount changes, **0 paid-date moves** | held. Its "earlier" leg is vacuous here: on r98 it moved 3. |
| P5 | closing balances identical | 857 legs | identical | **held** |

## What this does and does not show about SYN-2016-139

SYN-2016-139's refund is requested on 13 Apr 2022 and paid on 29 Apr 2022, 10 working days later, with
`breached_reg_6d_deadline: False`. That date is the one the r98 replay predicted. **But it is the same in
both arms.** On this book the leg's repayment is netted in May 2021 and not against its Apr 2022 return,
so the money-in day sits nearly a year before the request day whichever rule dates it. **S6b is not what
puts SYN-2016-139 inside reg 6D on this book.**

The book carries three other changes that could each move it: the refund clock (ceeefa5960), the
insulation change, and fabric (e17ebc596). **I cannot yet say which one did.** Each changes the run, so
separating them needs one-variable runs, and none was made for this leg. S6b's own effect is measured
cleanly here, and it is zero on refunds.

## The exception

The SYN-2016-139 row (`INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO`) is **already gone**. 61d8c871d4 (07:04 today,
the N29 grade on this same book) dropped it after the row read 0 of 1,679. This item's ask for it is spent,
and nothing here touches `docs/design/DOMAIN_INVARIANT_EXCEPTIONS.yaml`. The exception tracked a defect
whose fix is S6b. The breach it covered is now absent for a reason other than that fix, so if the cause
reverts, nothing names it. The S6b control stays in place as EARLY_REPAID in
`tests/simulation/test_a_close_refund_waits_for_the_money_it_pays_out.py`, and reverting the engine line
turns it red.

## Method

- `/var/tmp/rpam/s/census.py <root> <run> <ledger>` at each root, for the S6 lines.
- The coincident-arrival count uses the same census with its `all(...)` test changed to "some netted repayment
  has earlier cash and some has cash on that very day".
- `/var/tmp/s6b/diff.py <root> <run> <out>` gives money-in, closing and `generate_credit_refund_log` per arm.
- Outputs: `/var/tmp/s6b/{census_8a30.txt,census_8a30_pre.txt,before_8a30.json,after_8a30.json}`.
