**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: one fresh full run at 0b2879ef7d grades the six fixes in code (2026-10-29)

**Item:** `one-fresh-run-grades-the-fixes-in-code` (Lane 0, under
`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md` step 4). **Filed before
the launch.** Every prediction below is fixed before any output of this run exists. A wrong one stays beside its
result.

**Run.** `launch_long_job` job `fresh-run-0b2879ef7d`, worktree `/var/tmp/fresh-run-wt-0b2879ef7d` (origin 0b2879ef7d),
script `/var/tmp/fresh-run-scripts/arm.py`, output `/var/tmp/fresh-run-out-0b2879ef7d`. Graded with the runner from a
worktree at the same origin: `build_ledger.py` -> `export_raw.py` -> `python3 -m tools.domain_invariant_runner`.

**What the run carries that no graded book has.** The last graded book is 37abacdf42 (28 Oct). Since then:

| commit | what | row it moves |
|---|---|---|
| 558ee46245 | an occupier's bills read the triad's payment truth | `INV_OVERDUE_WITHIN_PAGE_BALANCE` (OCC- legs) |
| 1b82c3c0e3 | a DD is collected on its date or returned | `INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE` |
| 1bdd86b849 | E1: estimate from under six months of reads is the registry figure; E3: actual bill opens on the previous closing | `INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER`, `INV_OPENING_IS_THE_PREVIOUS_CLOSING`, `INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS` |
| 5b1b1497bb + 93095acd57 | the meter type printed is one value per supply point; each bill carries the type the supplier holds (leg 2 live) | `INV_METER_TYPE_ONE_VALUE_PER_SUPPLY_POINT` |
| 82d26fbd4e | the page prints the EPG support; the revenue row grades B + E on settled kWh | `INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE` |
| 0b2879ef7d | a credit bill posts to the desk as a credit | `INV_OVERDUE_WITHIN_PAGE_BALANCE` (non-OCC) |

Several of these change the same book at once. So a row that two commits touch can be graded but not attributed
between them. Where that is so, the prediction says it.

## Predictions

Baselines are the current ceilings in `docs/design/DOMAIN_INVARIANT_EXCEPTIONS.yaml` and the book each was set on.

- **P1. `INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER`** (13 on 37abacdf42: 8 after a single read, 5 summer runs on
  heating households). **3 to 7, point 5.** E1 removes the 8 single-read runs. It does not touch the 5 summer
  runs. A registry figure billed on a household far from it may set a new run, so the floor is not 5. Above 9
  means E1 is not reaching the bills it was written for.
- **P2. `INV_OPENING_IS_THE_PREVIOUS_CLOSING`** (13, all E4's ToU class, measured on the 37abacdf42 ledger rebuilt
  with E3). **13, range 10 to 16, every one the first single-rate bill after a ToU stretch.** E3 is in the run now
  rather than a rebuild. Nothing has fixed E4. A breach that is not the ToU class refutes "E3 is whole".
- **P3. `INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS`** (153). **I cannot yet say.** E1 changes every estimate on
  an account with under six months of reads. The row's reference window and the estimator's are still not
  traced against each other (the exception's open cause). Either direction is possible.
- **P4. `INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE`** (288 on 1a02c46116). **35 or fewer**, as filed by 82d26fbd4e,
  each in its classes (a) catch-up not netting to settlement, (b) an uncorrected estimate, (c) a part-month first
  bill. E1 changes estimates, which is the cause of (a) and (b), so the split between them is not predicted.
- **P5. `INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE`** (181). **10 or fewer**, as filed by 1b82c3c0e3. Any
  remainder is a mover's final bill paid late on a DD leg. Above 30 means a DD still pays late somewhere. This row is the measure of "no DD collected late without a
  return": its remaining leg is exactly that case.
- **P6. `INV_OVERDUE_WITHIN_PAGE_BALANCE`** (9,455 on b2fc50facf; 9,510 on 129e7de698, which carries neither fix).
  By class, with the same probe (`/var/tmp/onepay-scripts/lag_occ4.py`):

  | class | b2fc50facf | predicted |
  |---|---|---|
  | OCC- steps (558ee46245) | 2,489 | under 400 |
  | non-OCC steps | 6,965 | under 4,500 (credit-bill P1); above 5,500 means the credit bill was not the main cause |
  | (a) after the page's write-off | 723 | about 723 (650 to 800): no commit touches it |
  | cross-fuel netting | 487 | 150 or fewer (credit-bill P2) |
  | total | 9,454 | under 4,900, about 2,985 of it class (b) pennies, which no commit touches |

  These are the two pre-registrations' predictions combined, not new ones
  (`SEAT_PREREGISTRATION_AN_OCCUPIERS_BILLS_READ_THE_TRIADS_PAYMENT_TRUTH_2026-10-28.md` P1 and P2;
  `SEAT_PREREGISTRATION_A_CREDIT_BILL_POSTS_TO_THE_DESK_AND_THE_ROW_NETS_ONE_ACCOUNT_2026-10-29.md` P1 to P3).
  1b82c3c0e3 also moves this row: a DD that paid late made the desk see an overdue the page settled later. So
  the non-OCC fall cannot be attributed between the DD fix and the credit bill on this run. The grade says
  that and does not divide it.
- **P7. `INV_METER_TYPE_ONE_VALUE_PER_SUPPLY_POINT`** (no exception; leg 2 graded for the first time on a run's
  own bills). **0.** `SMART_METER_EXCHANGE` is False at origin, so the type cannot change between bills, and the
  header and the bills both come from the supplier's record. A breach is a real disagreement between the reads
  log and the supplier record, and it is a finding.
- **P8. The other excepted rows** should be unchanged within one: `INV_PPM_NOT_CREDIT_BILLED` 12, both EBSS rows 6,
  `INV_SMART_METER_BILLED_ON_ITS_OWN_READS` 4, `INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL` 10.
  `INV_STATUTE_BARRED_WRITE_OFF_AGE` (3): **I cannot yet say.** 558ee46245 changes OCC-6e59dd8b63e8's payment
  record, and the credit bill changes what the desk's ledger holds.
- **P9. Unexcepted breaches.** Rows other than these that breach on this book: **0**. A new one is a finding, not
  noise.

## Results

To be graded after the run. The exceptions file is then set to each measured count with its cause, or the
exception is retired.

**Status, 05:11 UTC 29 Oct: not started.** `fresh-run-0b2879ef7d` has been in `launch_long_job`'s queue since 03:35.
It was first held behind four pending landings, and now waits for memory: 12,500 MB declared peak against
`sim-runner` and `head-green-census` resident. `fresh-run-209c3350ab` (the one-write-off-date grade, which also
carries all six fixes) is queued behind it. No output exists, so every prediction above still stands unread. A
waiter on the job runs `/var/tmp/fresh-run-0b28-scripts/after_run.sh` into `/var/tmp/fresh-grade-0b28/` when it
ends. The untracked draft `SEAT_PREREGISTRATION_ONE_FRESH_RUN_GRADES_THE_FIXES_IN_CODE_2026-10-29.md` in the shared
tree (02:27, `BASE_PLACEHOLDER` run line) is this record's superseded first draft. It is not a second
pre-registration.

**Status, 07:12 UTC 29 Oct: still queued, and the grade waiter is re-armed.** The four landings that held it
have cleared. It now waits only for memory, behind `head-green-census` at about 12 GB resident. The waiter
named above died with the session that armed it, so nothing was set to grade the book when the run ended. A
transient unit `grade-chain-fresh-run-0b2879ef7d` now carries the waiter, so it no longer dies with a session.
It waits on queue pid 529128, follows `longjob-fresh-run-0b2879ef7d` to its end, and then runs `after_run.sh`
into `/var/tmp/fresh-grade-0b28/` (`ALLDONE` on success, `NO_DONE` if the run left no `DONE.json`). No
output has been read. Every prediction above still stands.

**07:45 GMT: the chain is re-armed.** `chain.sh` waited only once, and `wait_for` caps a wait at 6 h,
so a queue that ran past about 13:12 would have written `NO_DONE` over a run that had not yet started.
The unit now runs `/var/tmp/fresh-run-0b28-scripts/chain2.sh`, which re-arms the wait while queue pid
529128 lives; otherwise it is unchanged. The old unit was stopped before it read anything. Done by the
209c3350ab grade (item `the-one-write-off-date-is-graded-on-a-fresh-run`), which hit the same defect.
