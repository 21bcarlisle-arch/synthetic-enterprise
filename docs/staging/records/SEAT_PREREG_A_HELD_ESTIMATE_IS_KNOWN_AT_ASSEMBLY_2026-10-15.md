**Severity:** ADVISORY · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** none — Lane 0 delivery
**Claim:** `a-held-estimate-is-known-at-assembly-knowledge-and-prereg-first`

# Pre-registration: what a held estimate known at assembly changes on the book

**Written before the code change.** Finding:
`docs/staging/WORKER_FINDING_NINE_CUSTOMER_YEARS_BILL_LESS_THAN_THEIR_GROSS_MARGIN_AT_ORIGIN_2026-10-14.md`.
Knowledge: `docs/market_research/back_billing_and_liability.md` §12.

## The change

In `build_monthly_bills`, an estimated bill that `pre_bill_validation.validate_bill` holds joins the
pending run with billed = £0 and billed kWh = 0. The catch-up at the next actual read then reconciles
against what was sent. Nothing else moves. Validation still runs downstream, and the same bills are
held. The DD and pay-on-bill comparators are unchanged.

## Measured on the published run (2248e3baf book, `run_output_latest.json.gz` of 2026-10-13 21:31)

Printed by replaying the rule over the run's bills (`/tmp/held_probe.py`, kept in this record's
numbers):

- 39,084 bills. 65 fail `validate_bill`. **41 of those are estimates** (the ledger's
  `held_bill_count` is 41, and the other 24 are actual bills released as confirmed domestic).
- **All 41 held estimates are followed by an actual read. None is left unresolved.** They fall in 11
  catch-ups on 4 accounts: PROS-2017-0336 (8 catch-ups, 35 estimates), PROS-2017-0117 (1, 4),
  PROS-2024-0065 (1, 1) and PROS-2025-0106 (1, 1).
- Their issued-estimate totals sum to **£20,335.71**.
- 10 of the 11 catch-ups are direct debit at the recovery action, which bars nothing at the catch-up.
  The 11th (PROS-2025-0106, pay on bill) spans 2 months, so the 12-month cap cannot bite.

## Predictions

- **P1 (book).** Billed total across the book rises by **exactly £20,335.71 (±£0.11 of rounding)**.
  All of it is on the 11 catch-up bills. No other bill's total changes.
- **P2 (the nine).** **7 of the 9 clear**, with netted billed ≥ gross:

  | Account-year | Billed now | + predicted | Gross |
  |---|---|---|---|
  | PROS-2017-0117 2018 | 299.37 | +1,189.78 | 881.07 |
  | PROS-2017-0336 2017 | 618.78 | +537.81 | 690.85 |
  | PROS-2017-0336 2018 | −106.00 | +3,959.49 | 2,073.73 |
  | PROS-2017-0336 2019 | −117.58 | +5,261.27 | 3,119.79 |
  | PROS-2017-0336 2020 | 725.65 | +4,436.91 | 3,133.22 |
  | PROS-2017-0336 2023 | 7,541.68 | +177.71 | 7,597.07 (narrowest: clears by £122) |
  | PROS-2025-0106 2025 | 216.43 | +303.64 | 323.89 |

- **P3 (the other two stay red, for a different reason).** `OCC-25ff8966357a` 2022 and
  `OCC-b7693802f91c` 2016 receive **£0**. They have no held bill. Both are a 6–8 day December stub
  (£0.57 vs £3.22; £0.59 vs £2.41). The gate's own netting spreads a later catch-up *credit* over the
  run pro rata by day, and that pulls a few pence out of the stub. That is the test's day-weighted
  attribution of a seasonal over-estimate, not this defect. They keep their `KNOWN_OPEN_INVERSIONS`
  rows under a corrected reason.
- **P4 (no new hold).** The 11 catch-up bills rise. None becomes newly held by `validate_bill`. If one
  is, that is a finding: a catch-up whose size a validator reads as an anomaly.

## How it is graded

The code change lands with a unit control. Grading on the book needs the next published run (the
Monday publish). At that run, re-print the `defect4` sweep. Then delete the seven
`_HELD_ESTIMATE_NETTED` rows and keep the two OCC rows, if and only if P2 and P3 hold. Grade each line
here beside its result.

## Grading design, written 2026-10-15 before the grading run (claim `the-held-estimate-fix-is-graded-against-its-pre-registration`)

**Why not the Monday publish.** P1 says no bill other than the 11 catch-ups changes. The next
published run will also carry 068928f47 and its successors (the storage-heater and water-heater
demand changes), which move the demand digest and so move every electrically heated home's bills.
On that run P1 is ungradeable by construction, and any P2 margin would mix two causes.

**The one-variable run instead.** A locked worktree at `2248e3baf` (the published book's own commit)
with only 650fdcdd7's `company/billing/monthly_bill_assembly.py` hunk applied
(`/var/tmp/se-heldgrade-2248e3baf`). Full `simulation.run_phase4c_on_phase2b.main()`, saved through
`save_run_output_json`. The arm it is compared with is the published
`run_output_2248e3baf_20261013T134447Z.json` (its bills are byte-equal to the `.gz` this record was
measured on; checked).

**Placebo leg, graded first.** Every bill outside the 11 catch-ups must be equal to the published
bill. If more than those 11 differ, the world has drifted between runs at one commit (weather store,
an untracked input or nondeterminism). In that case P1 is reported as *not gradeable on this run*
with the count of drifted bills. It is not reported as refuted.

**Then P1, P4 from the bills; P2, P3 from a ledger and customer sample regenerated from this run**
(in the scratch worktree, never committed), read through `billed_total_by_customer_year(...,
net_of_catchup=True)` at the billing account, as the gate does.

## Graded 2026-10-15 on the one-variable run (`run_output_2248e3baf_20261015T114732Z.json`, 108 min, scratch worktree, never committed)

**Placebo leg: FAILED, so the book-wide grades are not gradeable on this run, as the design above
says.** Run B carries 38,431 bills to A's 39,084. 171 customer ids are only in A and 160 only in B,
and 2,100 shared bills differ in money. The world digests are identical (`cdba75ebb9197b33`, demand
`7d6195c5eb1562ab`). **The divergence is not the fix feeding back** through treasury into
acquisition. The first differing bill is 2016-02-13, when different households sign
(PROS-2016-0042 only in B; PROS-2016-0054 and -0059 only in A). The first held estimate is 2017-12,
22 months later. Two runs at one commit drew different books. Filed:
`docs/staging/WORKER_FINDING_TWO_RUNS_AT_ONE_COMMIT_DRAW_DIFFERENT_BOOKS_FROM_FEBRUARY_2016_2026-10-15.md`.
**PROS-2017-0336 is not on B's book at all.** It carries 8 of the 11 catch-ups, 35 of the 41 held
estimates and 5 of the 7 P2 rows.

**What IS gradeable: the three subject accounts drawn in both runs.** Each has identical bill keys in
A and B, and on each one *only* the catch-up bill moved:

| Account | Catch-up bill | A → B | = the held estimates it now absorbs |
|---|---|---|---|
| PROS-2017-0117 | 2018-04-01..11 | 362.25 → 1,961.84 (**+1,599.59**) | 418.59 + 442.71 + 363.79 + 374.50 = 1,599.59 (4 periods) |
| PROS-2024-0065 | 2025-04 | 498.58 → 1,011.16 (**+512.58**) | 512.58 (1 period) |
| PROS-2025-0106 | 2025-06-01..07 | −365.40 → −61.76 (**+303.64**) | 303.64 (1 period) |

- **P1 (book): NOT GRADEABLE on this run** (placebo). On the 3 of 11 catch-ups that can be compared it
  holds to the penny: +£2,415.81 predicted, +£2,415.81 measured, and no other bill on those
  accounts changed. The remaining £17,919.90 sits on PROS-2017-0336 and is ungraded.
- **P2 (the nine): 2 of 7 gradeable, 2 of 2 cleared, to the penny.** PROS-2017-0117 2018 bills
  £1,489.15 (299.37 + 1,189.78) against £881.07 gross. PROS-2025-0106 2025 bills £520.07
  (216.43 + 303.64) against £323.89. The five PROS-2017-0336 rows (2017, 2018, 2019, 2020, 2023) are
  **ungraded**: the account is not drawn.
- **P3: HELD.** Both OCC rows are on B's book. They are unchanged at £0.57 vs £3.22 (2022) and
  £0.59 vs £2.41 (2016), and they are B's only two inversions in the whole defect4 sweep. They
  belong to `D46_the_validator_holds_against_the_varied_population` (the finding's atom), where
  the remedy is the gate's day-weighted attribution of a later credit into a December stub, not
  billing.
- **P4: HELD on the gradeable accounts.** No catch-up bill is newly held. The 0117 catch-up
  (2018-04-11) was held in A and is held in B; the 0065 and 0106 catch-ups are held in neither.
- **Out of sample, unpredicted, one case:** PROS-2024-0010 is drawn only in B. Its 2024-05 catch-up
  absorbs 2 held estimates (`catchup_unbilled_periods: 2`) and its years do not invert. Across B's
  whole sweep, the only inversions are the two P3 rows; A has nine.

**Disposition.** The finding stays in the staging root and its nine `KNOWN_OPEN_INVERSIONS` rows stay.
The committed ledger is still run A's, so deleting the two cleared rows would red the gate on the
artefact it reads. EP17's held-estimate condition is **not** closed: 5 of its 7 rows are ungraded.
Closing it needs a run that draws PROS-2017-0336, which first needs the book-drift finding's
one-variable placebo (2248e3baf *without* the hunk, under the same long-job unit).

## Re-graded on the `81c129fe8` arms (claim `grade-the-held-estimate-fix-on-the-81c12-arms`)

The design is in the book-drift finding, under "Re-grading the held-estimate fix". X0 is
`81c129fe8` clean. X1 is the same commit plus this fix's `monthly_bill_assembly.py` hunk (checked
line for line against `650fdcdd7`).

- **Q0 (placebo, X0 against published A): HELD, exactly.** The same 39,084 bill keys, 0 bills
  differing in any field, and a book total of £2,462,538.19 in both. So X1 against X0 grades the fix
  on A's own book, and PROS-2017-0336 is drawn. (Outside the bills, the hedge, credit-exposure and
  margin-call sections differ. The finding records it, and it does not touch this grade.)
- **P1, P2 (the five PROS-2017-0336 rows), P4: PENDING X1.** The first X1 launch died queued with
  the tick that started it. It was relaunched 2026-10-15 18:57 BST under `setsid`, waiting on the
  weekly publish run's memory, as unit `longjob-bookfix-81c12-x1`. `/var/tmp/se-placebo-out/post.sh`
  writes `grade_P1_x0_vs_x1.txt` and `grade_ledger_x{0,1}.txt`, then `POSTDONE`.
