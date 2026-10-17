# Pre-registration: REVIEW_SEEKS_BALANCE switched on, graded against the 19 Oct published run (2026-10-17, written before either run exists)

**Subject:** `company/billing/dd_review.py::REVIEW_SEEKS_BALANCE` (False today; page condition (a)
met by `48c619bbf`). Finding:
`docs/staging/SEAT_FINDING_D48_A_THIRD_OF_DD_ACCOUNTS_ASKED_FOR_THEIR_BALANCE_LOSE_PART_OF_IT_BECAUSE_THE_REVIEW_NEVER_ASKS_2026-10-14.md`.
Earlier pre-registration, on a different question (seek vs never on one fixed book):
`SEAT_PREREGISTRATION_THE_DD_REVIEW_SEEKS_THE_BALANCE_ON_THE_2248E3BAF_RUN_2026-10-16.md`.

## The one-variable run

- **Arm A (control):** the run the 2026-10-19 Monday publish promotes, i.e. the commit in its own
  `producing_commit.commit`, the default book seed (`SE_POPULATION_SEED` unset, so
  `live_population._DEFAULT_BASE_SEED = 20260724`), and the curriculum's default env.
- **Arm B (treatment):** that same commit with ONE line changed, `REVIEW_SEEKS_BALANCE = True`, run
  through `simulation.run_phase4c_on_phase2b` under `background.launch_long_job` in a clean scratch
  worktree, with the same env.
- **Admission:** B must pass `background.code_closure --arm` (an empty `imports_off_commit` reading)
  and its `world_identity.digest` must equal A's. If either fails, the comparison is not one variable
  and nothing below is graded (`WORKER_FINDING_TWO_RUNS_AT_ONE_COMMIT_DRAW_DIFFERENT_BOOKS_FROM_FEBRUARY_2016_2026-10-15.md`).

## Where the sizes come from

Both arms rebuilt in-process (`dd_balance_book.build_dd_balance_book` on each run's own bills,
closed = last bill before the run's last billed month, default `last_year_spend` review rule):

| | 2248e3baf never | 2248e3baf seeks | 78f77c34e never | 78f77c34e seeks |
|---|---|---|---|---|
| met a recovery action | 422 | 610 | 421 | 612 |
| barred (accounts) | 153 | 239 | 150 | 243 |
| share barred | 36.3% | 39.2% | 35.6% | 39.7% |
| £ barred (at review / at final bill) | 33,770 (0 / 33,770) | 33,386 (26,771 / 6,615) | 35,230 (0 / 35,230) | 35,546 (29,678 / 5,868) |
| open exposure £ | 50,297 | 1 | 52,552 | 1 |
| barred + open exposure £ | 84,066 | 33,387 | 87,783 | 35,547 |
| portfolio final balance £ (+ = held for households) | -45,317 | +158,443 | -46,224 | +163,378 |
| held credit at run end £ | 18,589 | 160,329 | 18,705 | 165,589 |
| peak held credit £ | 19,953 | 161,723 | 18,705 | 165,589 |
| 2023 step-up median / p90 £/mo | 55.01 / 109.67 | | 56.59 / 124.14 | |

The two books are different runs at different commits, and every figure agrees within about 5%.
The ranges below are that spread widened for the commits between 78f77c34e and the publish
(closing reads, change-of-tenancy opening reads, the gas must-read, C34 holdout).

## Predictions (B against A, same commit)

**P1. Nothing upstream of the DD book moves: bills, revenue, settlement, arrears and treasury cash.**
`bills` are identical in count and in every amount, and so are `total_revenue_gbp`,
`total_gross_gbp` and the world's arrears and payment outcomes (`payment_behaviour`, the arrears
engine's rolls). The book draws no RNG and feeds nothing the world reads; the world's payment draw
does not see the DD amount. **Any difference here refutes the claim that this switch is one
variable, and that is the first thing to read.** Range: exactly zero.

**P2. The publisher's arms panel (`billacc-ddarms`) is byte-identical between A and B,** because it
rebuilds both arms from the same bills. What moves on the page is which arm is "as run".

**P3. The billing page's headline DD money line moves from the never arm to the seek arm:**
- accounts that met a recovery action: about +190 (range +150 to +230), to about 610 (560-660);
- barred share RISES by about 3.5 points (range +1 to +6), to about 39.5% (35-44%);
- £ barred roughly flat: change within ±£3,000 of A's, with about 80% (70-90%) of it now at reviews
  rather than final bills;
- open exposure falls from about £50k (£40k-£62k) to under £50;
- barred plus open exposure falls by about £52k (range £40k-£62k), to about 40% (35-45%) of A's.

**P4. DD amounts rise, concentrated in 2023.** Reviews that step the debit up number about 1,000
across the run (range 900-1,150), 2023 the largest year at about 220 (190-250). The 2023 step-up
median is £50-62 a month and its p90 £100-135. Every other year's median is under £15. Total extra
collected over the run (B's final balance minus A's, plus the change in bars) is about £205k
(range £170k-£250k).

**P5. Balances: the portfolio flips from net debit to net credit, and held credit rises about
ninefold.** Final portfolio balance moves from about -£46k (-£55k to -£38k) to about +£160k (+£130k
to +£190k). Held credit at run end moves from about £19k to about £162k (range £130k-£195k), roughly
£230 per DD account. Wherever the DD-H balance sheet (`saas/reporting/annual_report`) is published,
its held-credit liability moves by the same amount.

**P6. The ledger's SLC 21BA write-off moves by the change in £ barred only** (`back_billing_bars`
booked by `close_the_books`): within ±£3,000, sign not called. The 78f77c34e book gives +£316 and
2248e3baf gives -£384.

## What P5 means if it holds (filed now, so it is not a reading after the fact)

The seek arm recovers the debit, then keeps collecting. A `last_year_spend` reset after 2022-23
sizes 2024's debit on crisis-year spend, and the review never returns a credit. Ofgem's sentence
covers debit balances only. `what_a_supplier_holds_to_size_a_direct_debit.md` §8 lists credit
balances as a GAP. So if P5 holds, switching seek on by itself turns £46k the company is owed into
about £160k it holds of households' money at run end. That is a transfer, not value created (M2).
**Recommendation for the switch-on item:** read P5 before landing the flip. If it holds, close the
credit-balance GAP first (what published practice does with a credit at review), and land the
credit-side rule as its own one-variable change. Do not bundle it into this run.

## Grading

Graded in the D48 finding after both runs exist, every prediction HELD / REFUTED / MISSED with its
number. P1 or P2 failing voids P3-P6.
