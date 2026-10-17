**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`
**Knowledge:** read-access-and-theft-duties

# A read instruction at the 11th estimate: at the read end the bar on the crossed runs falls from £3,929 to £5; at no access nothing moves

*Worker tick, 2026-10-17. Direction item `the-company-instructs-a-read-before-the-21b4-year`.
Knowledge: `docs/market_research/read_access_and_theft_duties.md` §2.8 (K8, same commit).
Predictions and their grades: `docs/staging/records/WORKER_PREREG_WHAT_A_READ_INSTRUCTION_AT_THE_ELEVENTH_ESTIMATE_REACHES_AT_BOTH_ACCESS_ENDS_2026-10-17.md`.*

## What was built

- **Company.** `company/billing/read_duty_register.py`:
  - `read_instruction_due` instructs a read on the 11th estimate in a row, and again at each later
    year of the run (the 23rd, the 35th). Prepayment gets none.
  - `read_instruction_register` lists the instructions: raised date, the visit's period, and the
    outcome.
  - The trigger is the last bill from which a visit can still meet the 21B.4 year. When a supplier
    first asks for a read is unpublished (GAP, §2.8). That makes this the **latest** compliant
    timing, not a chosen one.
- **Seam.** `build_monthly_bills(instruct_reads=False)` is the switch, and it is off by default.
  When it is on and the period's own read did not arrive, the company asks the feed
  `ReadArrivalFeed.instructed_read_for`.
  - The direction named `company/interfaces/sim_interface.py`, but the read seam is the
    `ReadArrivalFeed` Protocol, which `company/interfaces/bill_assembly.py` re-exports. The call was
    put there, beside `final_read_for`, and `sim_interface.py` is unchanged.
- **World.** `SimulatedReadFeed(instructed_read_arm=...)` answers through
  `simulate_instructed_read`, which is the must-read's visit (`must_read_reads`, 367f20023) on its
  own key and its own arm.
  - `q6_read_visit_access_failure_rate` is null, so `register` is the no-access end and `ceiling`
    is the read end. There is no midpoint.
  - A read that arrives anyway is never replaced.
- **Default off is unchanged.** On the fixture, the bills with the switch off are equal to the bills
  without the argument. No bill carries a `read_instruction_*` key, and a feed with no
  `instructed_read_for` still bills.

## Controls (each mutation run in-process, then reverted; placebo green)

- `tests/company/billing/test_the_company_instructs_a_read_before_the_21b4_year.py` checks the whole
  partition in one statement.
  - Red under: the trigger at 10 (one bill early), at 12 (one bill late), once per run instead of
    once a year, prepayment included, and a visit asked when the ordinary read had already arrived.
  - The last mutation was green until account C5 was added. That was a missing test, not an
    equivalence.
- `tests/simulation/test_meter_reads.py::test_an_instructed_visit_reads_at_the_ceiling_finds_no_access_under_the_gap_and_keeps_its_own_arm`
  is red under: every visit reads, a read that arrived is replaced, and the arm is shared with the
  must-read.
- `tests/tools/test_closing_estimate_run_money.py::test_the_grade_places_the_instructed_visit_where_the_billing_run_does`
  checks that the grade puts each visit where the billing run does.

## What it is worth on the graded book

`/var/tmp/closing-money-run-20261017.json` (cc23de757), with
`python3 -m tools.closing_estimate_run_money --read-duty --instructed-read`. This is a
decomposition, and the read end is an upper bound.

| | no access | read |
|---|---|---|
| Instructions raised (electricity / gas) | 211 / 121 | the same 332 |
| Open closing undercharge new demand, whole book | £3,470.63 | **£2,662.61** |
| … on the 12 crossed undercharge runs | £1,761.88 | **£953.86** (£925.08 of it is C7) |
| 21BA bar on the 12 crossed undercharge runs, at closure | £3,929.05 | **£5.49** |
| On-supply catch-up write-off on runs of 12+ estimates | £515.25 | none: the visits true up £6,990.56, and none of it is barred |

- **No access changes nothing.** The run bills as before. What the company gains is a dated record
  of the step 21B.4 asks for.
  - That record does not earn the 21BA.2(c) exception. Ofgem asks for requests the household
    "ignore[s] or refuse[s]", and the world cannot tell no one home from a refusal (§2.4, §2.5 GAP).
- **At the read end, the money mostly moves on supply.** £6,990.56 is trued up inside 12 months on
  bills the household is still receiving. Recovering it is a **transfer** (M2). What is created is
  a shorter run, a smaller correction, and £3.9k less write-off at closure.
- **The truth lies between the two ends**, and where depends on the access-failure rate. That is
  the practitioner question in §7: of visits to traditional credit meters, what share fail?

## Filed for after the publish, not built

1. **Re-estimate from the visit's read.** The decomposition keeps the old estimate after a read. A
   real run would rebase on it, and C7's £925 tail is mostly that overstatement. This needs a
   re-run with `instruct_reads=True` at both arms, after the 2026-10-19 publish.
2. **A self-read prompt, and a household that answers it.** That is a world change (§2.8).
3. **Wiring the switch into `run_phase2b`**, so a published run can carry it, once the director's
   order puts billing accuracy's chase on the published path.

## Seen in passing

`tests/company/billing/test_collections_journey.py::test_a_live_run_asks_the_world_for_a_prepayment_meter_at_the_ninety_day_rung`
is red in the shared tree and green in a clean `origin/main` worktree with this change.

- The shared tree carries another lane's uncommitted `simulation/population_draw.py` and
  `simulation/premise_population.py` edits. They are the likely cause; this was not tested one
  variable at a time.
- Whoever lands those edits will meet this red.
