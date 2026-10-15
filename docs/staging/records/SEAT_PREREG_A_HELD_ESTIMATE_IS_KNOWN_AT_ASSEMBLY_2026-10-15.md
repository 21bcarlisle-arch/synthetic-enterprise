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
