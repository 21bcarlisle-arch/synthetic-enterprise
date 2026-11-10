**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`
**Knowledge:** `payments-and-direct-debit` -- `docs/market_research/payments_and_direct_debit_2026-10-25.md` "What is owed"

# A level-return case on the page is capped at its own bill's remainder (2026-11-09)

**Parent.** `WORKER_FINDING_A_LEVEL_DD_JOURNEY_CURES_ON_THE_NEXT_INSTALMENT_WHILE_THE_MISSED_ONE_IS_NEVER_MADE_GOOD_2026-11-09.md`,
section "The residual, not fixed here: a case can exceed its own bill". On the 4dee9854a4 book re-generated with
50030bb60, 84 level cases on 58 accounts print GBP 5,871.65 above their own bill's remainder, because the desk figure
a level case takes is the journey's running total (PROS-2019-0246 16165: face 60.48, repaid 60.48, prints 269.94).

**What "own bill's remainder" counts.** The invoice's face as asked (`asked - part_paid`), less the credits and
repayments matched to that invoice (`credits_applied`), floored at 0. It is the same figure a non-level failed bill
prints as its case. A level case prints the lesser of that and the desk's shortfall.

**Why the cap could lose debt.** A level case's desk figure includes earlier months' shortfall inside the journey.
That earlier shortfall is already on the page if the earlier miss opened its own case; then the running total
double-counts it and the cap only removes the double count. It is lost only where the earlier miss opened NO case
(no desk figure on its day because the journey was already open, or the other leg took it).

## Pre-registration (filed before the measurement is run)

Instrument: an instrumented copy of the level-return branch, run on `run_output_4dee9854a4_20261109T160658Z.json`,
recording every failed level return (account, journey, day, desk shortfall, own remainder, case opened or not).
For each over-cap case, the debt the cap could lose is bounded by `min(excess, sum of the own remainders of earlier
failed level returns on the same billing account, inside the same journey, that opened no case)`.

- **Prediction:** the bound is small: under 10% of the GBP 5,871.65 excess (under GBP 587), because a journey's
  misses are each dated by their own collection day, and each one the desk saw short opens a stage on that day.
- **Refuted if** the bound is 10% of the excess or more. Then the cap is not the fix as it stands: the earlier
  no-case misses need cases of their own first, and that is built instead.
- **The build's own legs** (from the parent, unchanged): the 84 cases read 0 above remainder; the 6 residual
  left-level holds read 0; the 12 on-receipt holds are unchanged; total outstanding falls by no more than GBP 5,871.65.

## The measurement, graded (seat executor, 9 Nov 2026 ~22:30 GMT)

Instruments: `/var/tmp/capprobe/` (`gbl_probe.py` is the 50030bb60 generator plus one recording line; its ledger is
byte-identical to `/var/tmp/shapea-arm/ledger.json`; `analyse2.py`, `recon.py`).

- 531 failed level returns: 201 opened a case, 330 did not (314 with no desk figure that day, i.e. nothing short).
- Over-cap cases, counted as printed (`max(shortfall - credits, 0)`) above own remainder: **93 on 61 accounts,
  GBP 7,039.59**.
- **Earlier in-journey misses that opened no case, before an over-cap case: 0. Bound on lost debt: GBP 0.00.**
- Widened to "any earlier no-case miss on the account since its previous journey ended": 2 cases, GBP 136.27 bound
  (1.9%). Both earlier misses (PROS-2019-0063g 9 Nov 2022, SYN-2016-499 8 Aug 2017) carried a desk figure of 0, so the
  desk saw nothing short on those days; the bound is not debt the desk carried.
- **Prediction (under 10%) held.**

**Correction, beside the parent's figure.** The parent's 84 cases / GBP 5,871.65 were counted off the ledger's
`face_gbp - repaid_gbp - credit_applied_gbp`. On a level case `credit_applied_gbp` is derived from the desk figure,
not the bill's credits, so that is not the bill's remainder. On the same arm the same formula reads 111 cases,
GBP 5,871.93. The definition above reads 93 cases, GBP 7,039.59.

## The build, graded on the same book (one change, one book: attributable)

Change (`tools/generate_billing_ledger.py`): a level case's gross is `min(desk shortfall, asked - part_paid)`, then
netted of its own credits as before. The leg still TAKES the uncapped shortfall for the one-leg rule, so the cap
never hands the running total's excess to the other fuel (mutation "taken capped" fires on that test).
Control: `tests/tools/test_a_level_return_case_is_owed_net_of_its_own_repayment_and_on_one_leg.py`, 8 tests. Each
of the three mutations fires: no cap (3 fail), taken capped (1 fail), cap to zero (8 fail). Ledger tests: 208 pass.
`test_reconciliation_identity_holds_across_full_live_book` fails at HEAD too: it reads the committed 3 Nov book
(OCC-00909e50a521), is filed in `SEAT_FINDING_THE_B3CE2A4E73_BOOK_FAILS_THE_DOMAIN_INVARIANT_GATE_ON_SEVEN_ROWS_2026-11-04.md`,
and is not this change.

Arm `/var/tmp/cap-arm/ledger.json` against control `/var/tmp/shapea-arm/ledger.json` (`/var/tmp/capprobe/grade.py`, `holds.py`):

| Leg (filed before the build) | Result | Graded |
|---|---|---|
| The over-remainder cases read 0 | 111 → 27, totalling GBP 0.28: penny roundings on non-level OCC/PROS invoices | **held** |
| The 6 residual left-level holds read 0 | 5 of 6 gone (PROS-2019-0246 ×3, SYN-2016-253g, SYN-2016-360). SYN-2016-536's 16 Feb 2023 hold stays, now over 49914 (face 38.21, credit 14.16, owes 24.05) and 50041 (face 19.88, owes 19.88): neither is above its own bill | **5 of 6; the 1 is a different class** |
| The 12 on-receipt holds are unchanged | 12, same invoices, same figures | **held** |
| Total outstanding falls by no more than GBP 5,871.65 | falls GBP 6,435.44 (17,386.73 → 10,951.29), 87 invoices, none rises | **FELL**: the bound was the wrong definition (above). Against the probe's: 7,039.59 − 604.15 already written off on the page = 6,435.44 exactly |

PROS-2019-0246 16165 prints 0 (was 269.94).

**Left open.**
- SYN-2016-536's hold is over unpaid level-era remainders on a leaver. That is the "true leavers" class in the parent
  finding, not a cap defect.
- On the 6 written-off over-cap cases (GBP 604.15), the page's write-off stage is now `min(capped case, desk write-off)`.
  The desk wrote off its running total. That is the C7 class again (desk heavier than the page). Whether the P&L reads
  the desk's write-off is still the parent's open question.

## The level cap meets the C7 schedule fix on one book; the write-off gap is the engine writing off level-paid bills (2026-11-10) (seat executor)

**Answers this finding's "Left open"** (SYN-2016-536's
hold and the GBP 604.15 desk/page write-off gap). 2353f8b00 (the cap, ledger side) was graded only on a re-generated
4dee9854a4 book; dea1c34fd (the C7 schedule fix, world side) changes the run. The two meet first on the book at origin
78f82e4242 (`longjob-book-78f82e4242`, launched 10 Nov 00:02 GMT by the worker holding
`the-first-book-after-the-overdue-fixes-is-run-off-tree-and-gated`). This seat grades that book and does not run a second.

### SYN-2016-536's remaining hold, named (measured on the 4dee9854a4 cap-arm ledger, `/var/tmp/cap-arm/ledger.json`)

The hold is the desk curing journey 2020-04-15 on **16 Feb 2023** while the page still holds 49914 (elec, Nov 2018,
owes GBP 24.05) and 50041 (gas, Oct 2020, owes GBP 19.88). It is two different things on the two legs, and neither is a
cap defect:

- **Gas leg: a true leaver from level DD.** SYN-2016-536g paid level DD until 13 May 2020 (43 instalments), then paid
  on receipt by standard credit, mid-journey. Its page running balance is GBP 112.14 on 15 Apr 2020 and stays in the
  balance to book end (GBP 178.12 = 112.14 + the three unpaid standard-credit bills 50041, 50084, 50086 at 65.98).
  The 112.14 is level-era under-collection plus two missed instalments (50035 GBP 23.38, 50036 GBP 16.39) whose cases
  print `ARREARS_REPAID` with no cash against them. **No invoice holds it.** When a level DD stops, the shortfall
  against the schedule becomes the balance, and a supplier bills it. Here it sits in the running balance and is never
  asked for. That is the parent worker finding's "the missed one is never made good" class, on a leaver.
- **Elec leg: still level, misread as left.** SYN-2016-536 paid level DD to 2 Jun 2025 (101 instalments) and ends
  **GBP 121.45 in credit** on the page, while printing 49914 at GBP 24.05 overdue since 2018. Two defects: (a) the
  hold reader (`split.py`'s "latest payment is level") reads the leg as not level on 16 Feb 2023, because the latest
  dated payment is the EBSS `scheme_credit` row of 18 Jan 2023, not the 3 Jan DD; (b) an in-credit level leg
  printing a 2018 bill as overdue is the BLOCKING class in
  `SEAT_FINDING_A_LEVEL_DIRECT_DEBIT_HOUSEHOLD_IS_DUNNED_PER_BILL_SO_ITS_PAGE_PRINTS_OVERDUE_WHILE_IN_CREDIT_2026-11-07.md`.
  Only GBP 14.16 of the credit was netted against it.

So the "1 of 6 residual holds" is not one residual. It is a gas leaver whose level shortfall nobody bills, plus an elec
leg that reads as overdue while in credit.

### The write-off gap is larger than GBP 604.15, and was there before the cap

Reader: `/var/tmp/capgrade/wo.py`. The engine side is `resolved_settlement`, called exactly as
`tools/generate_billing_ledger.py` calls it. The P&L side is `compute_emergent_bad_debt`, called as
`tests/tools/test_the_ledger_and_the_pnl_write_off_agree_on_the_real_book.py` calls it.
Same run (4dee9854a4), two ledgers:

| | control (`shapea-arm`, pre-cap) | cap-arm (2353f8b00) |
|---|---|---|
| engine write-offs | 268, GBP 10,812.78 | 268, GBP 10,812.78 |
| page written-off cases | 220, GBP 9,824.19 | 220, GBP 9,220.04 |
| engine minus page | 73 cases, GBP 988.59 | 68 cases, GBP 1,592.74 |
| ... level-paid, page opened NO case | 38, GBP 1,417.13 | 38, GBP 1,417.13 |
| ... level-paid, page case lighter | 25, GBP -266.95 | 20, GBP +337.20 |
| ... not level-paid | 10, GBP -161.59 | 10, GBP -161.59 |
| ledger vs P&L, accounts disagreeing | 83, P&L heavier by GBP 1,876.89 | 79, P&L heavier by GBP 2,481.04 |

The cap moved the gap by exactly 1,592.74 - 988.59 = GBP 604.15: the parent's figure, reconciled. **The larger
class predates the cap.** In 38 cases the engine writes off the face of a level-paid bill (OCC-01e79fcf2d4f 263: bill
GBP 24.14 against an GBP 80 instalment) where the desk saw nothing short on the return day, so the page opens no case
and shows no debt. The P&L books bad debt that the page says was never owed. This is the C7 shape again: the desk's
or engine's per-bill view is heavier than the page's schedule view. Ten non-level cases run the other way (page
heavier by GBP 161.59) and are unexplained here.

`test_the_ledger_and_the_pnl_write_off_agree_per_account` reads `run_output_latest`. On this book it would fail on 79
accounts.

**Correction (same session, ~00:45 GMT, after c243a2063): the table above reads the wrong page figure.** It counted a
written-off case's `arrears_gbp`, which is the case's face. The money the page writes off is the `WRITTEN_OFF` stage's
`amount_gbp`, `min(case, engine)`. The 10 "not level-paid" rows are this artefact: each stage amount equals the
engine's, and the gap is the part recovered before write-off. Re-read on the stage amount:

| | control (pre-cap) | cap-arm |
|---|---|---|
| page written off | 220, GBP 9,036.12 | 220, GBP 9,036.12 |
| engine minus page | 57, GBP 1,776.66 | 57, GBP 1,776.66 |
| ... level-paid, page opened no case | 38, GBP 1,417.13 | 38, GBP 1,417.13 |
| ... level-paid, page case lighter | 19, GBP 359.53 | 19, GBP 359.53 |
| ... not level-paid | 0 | 0 |
| ledger vs P&L, accounts disagreeing | 89, P&L heavier by GBP 2,664.96 | the same |

- **The cap opened no write-off gap.** On the 6 written-off over-cap cases, the engine's figure was already below the
  capped case. The cap changed their face (`arrears_gbp`), not what was written off. The parent's "GBP 604.15 write-off
  gap" is a face difference. It is withdrawn as a gap.
- **The real gap is older and has three homes for one quantity:**
  - the P&L's `compute_emergent_bad_debt`, which is not passed `level_dd_collections`: GBP 11,701.08;
  - the generator's `resolved_settlement`, which is passed them: GBP 10,812.78;
  - the page: GBP 9,036.12.

  The 57 level-paid cases are where the engine writes off a bill's face against a level schedule that the page reads
  as nothing short, or as less short.
- `test_the_ledger_and_the_pnl_write_off_agree_per_account` also sums `arrears_gbp`. On a partly recovered case it
  compares the face with the P&L's net. That is a reader defect in the control itself.
- P3 below stands as filed, graded on the stage-amount reader (`wo.py` as corrected).

### Pre-registration for the 78f82e4242 book (filed before any of its output exists)

Grade chain: `/var/tmp/capgrade/after_run.sh <run json> /var/tmp/book-wt-78f82e4242`. It regenerates the ledger with
78f82e4242's generator, then runs `grade2.py` (the capprobe `grade.py` readers, cap-arm as control), `split.py` +
`holds2.py` (`holds.py` on the book's own split), and `wo.py`.

- **P1, the cap holds on a new book.** 0 over-remainder cases on level-paid invoices. All residual over-remainder rows
  are penny roundings, totalling under GBP 1.00. 0 positive-face invoices owe above their face.
  *Refuted if* any level-paid case exceeds its remainder by more than 1p.
- **P2, holds.** The on-receipt holds (PROS-2018-0016 x10, SYN-2016-217 x2) are unchanged. Neither commit touches an
  on-receipt leg. If the world draws SYN-2016-536 identically, its hold stays over 49914 and 50041: dea1c34fd withdraws
  presented-or-not schedule rows, not 2018/2020 unpaid bills. *Refuted if* it goes. Then the schedule fix reached
  the leaver's balance, which would be news.
- **P3, the write-off gap is not closed by either commit.** The "level-paid, page opened no case" class persists at 30
  or more cases and GBP 1,000 or more. Ledger vs P&L disagreement persists on 60 or more accounts. Neither commit
  touches the engine's per-bill write-off of a level-paid bill.
  *Refuted if* engine minus page falls below GBP 500.
- **Attribution.** Any movement against the cap-arm between the two books cannot be split between dea1c34fd,
  19eebf6c3e and draw differences. Only properties (P1) and class presence (P2, P3) are graded, not deltas.

NEXT: none -- grade the 78f82e4242 book on this chain and write held or fell beside each leg.
