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

NEXT: none -- the cap is landed; the remaining hold and the write-off gap belong to the parent finding's open threads.
