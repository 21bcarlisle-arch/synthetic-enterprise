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

**09:40 GMT: a prediction for P3's rise, written before any breach list is read.** The 209c3350ab book
(below) carries all six fixes and breaches P3's row 269 times, against 153 on 37abacdf42. Only its
total and five examples have been read. E1 bills the registry EAC/AQ until the company's own reads
span 182 days (273 for gas). The registry figure is a national-profile annual, not this meter's
recent reads, so an estimate taken from it can sit outside a band the row draws from the last two
reads. **T1:** at least 116 of the 269 (the rise) fall on bills where the meter's first actual read
before the bill is under 182 days (gas: 273) before the bill starts. That is E1's registry branch.
**T2:** at least 100 of 37abacdf42's 153 breach again on the same bill on 209c3350ab, because nothing
touched the reference-window cause. If T1 fails, E1 is not the cause of the rise and I cannot yet say
what is.

## Results: graded on the fresh 209c3350ab book (10:15 GMT 29 Oct)

**Why that book and not 0b28's.** `fresh-run-209c3350ab` started at origin 209c3350ab, which has all six
commits above as ancestors and also carries the one write-off date (2b70102f9e, the 186072 re-land). It
finished at 09:14. Its book is the fresh full run this item asked for, so P1 to P9 are graded on it.
Only two predictions are confounded by the write-off date, and they are marked. `fresh-run-0b2879ef7d`
is still queued for memory (unit `longjob-fresh-run-0b2879ef7d-queued`, grade chain armed). It is
now only the one-variable run for the close write-off's −£457, which is continuation
`split-the-close-write-off-fall-on-the-0b28-book`'s work, not this record's. Grade:
`/var/tmp/wo-grade-209c/grade.json`. Full breach lists: `/var/tmp/est-probe/rows209c.json`,
`/var/tmp/est-probe/209c.json` (and `37ab.json` for the comparison).

| | row | before | predicted | measured | verdict |
|---|---|---|---|---|---|
| P1 | `INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER` | 13 | 3 to 7, point 5 | **6** | holds. Every run is in summer and above 3; the 8 single-read runs are gone. Two are gas legs, which the "5 summer runs" did not foresee |
| P2 | `INV_OPENING_IS_THE_PREVIOUS_CLOSING` | 13 | 13 (10 to 16), all ToU | **13** | the count holds. The four accounts the exception names are among them; the ToU class itself is not re-traced on this book |
| P3 | `INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS` | 153 | I cannot yet say | **269** | traced: see T1/T2 below |
| P4 | `INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE` | 288 | 35 or fewer | **24** (13 above, 11 below) | holds. The split into (a) to (c) is not re-measured |
| P5 | `INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE` | 181 | 10 or fewer | **6** | holds. Five are gas legs with one to two missed DDs without a return. The "mover's final bill" cause is **not checked** |
| P6 | `INV_OVERDUE_WITHIN_PAGE_BALANCE` | 9,455 | under 4,900 | **2,500** of 19,491 steps | the total holds. Class (a) is 0, not "about 723": **confounded**, because the write-off date removed it, which is what 2b70102f9e's own grade predicted. The OCC/non-OCC split is not produced by the probe's output on this book, so those two class predictions are **ungraded** |
| P7 | `INV_METER_TYPE_ONE_VALUE_PER_SUPPLY_POINT` | — | 0 | **0** of 1,293 | holds |
| P8 | PPM 12, EBSS 6 and 6 | — | unchanged within one | 12, 6, 6 | holds |
| P8 | `INV_SMART_METER_BILLED_ON_ITS_OWN_READS` | 4 | 4 within one | **0** breached, 21 flagged | **refuted**. Not traced; 93095acd57 (each bill carries the supplier's own meter type) is the likely mover |
| P8 | `INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL` | 10 | 10 within one | **6** (3 account-years) | **refuted**. PROS-2017-0336 no longer breaches; why is not traced |
| P8 | `INV_STATUTE_BARRED_WRITE_OFF_AGE` | 3 | I cannot yet say | UNREACHED | **confounded**: a leaver is now written off at a year, so the book has no statute-barred write-off |
| P9 | unexcepted rows other than these | — | 0 | **0** | holds |

**P6 by class (added 11:00 GMT 29 Oct). Correction:** the row above says the probe does not split OCC from
non-OCC on this book. It does: its `(class, is_OCC)` keys carry the split, and I misread them. Re-run on
`/var/tmp/wo-grade-209c/ledger.json` (output `/var/tmp/wo-grade-209c/lag.txt`). The probe counts 2,526
steps where the row counts 2,500. Its `other` class alone is 2,499, so the 27 payment-lag steps may be
the gap. I cannot yet say whether the row leaves them out.

| class | b2fc50facf | predicted | 209c3350ab | verdict |
|---|---|---|---|---|
| OCC- steps | 2,489 | under 400 | **223** (218 other, 5 payment lag) | holds |
| non-OCC steps | 6,965 | under 4,500; above 5,500 refutes the credit bill as main cause | **2,303** (2,281 other, 22 payment lag) | holds. The fall cannot be split between 1b82c3c0e3's DD date and the credit bill, as P6 said |
| (a) after the page's write-off | 723 | about 723 | **0** | confounded by the write-off date (above) |
| cross-fuel netting | 487 | 150 or fewer | **101** (51 non-OCC, 50 OCC) | holds |
| class (b) pennies, at most 2p | about 2,985 | untouched by any commit | **1,679** | **refuted.** It fell by about 1,300. The book carries seven changes, so I cannot say which one moved them |

**T1 and T2 (P3's trace).** T2 holds: 130 of 37abacdf42's 153 breach again on the same bill. T1 holds as
worded: 191 of the 269 are in E1's registry branch (≥116). The trace is stronger than T1 asked. All 139
new breaches are in the branch, each the same bill under the same band with only its estimate moved,
and so are all 23 that disappeared and all 1,451 estimates that moved. The 78 outside the branch are the
carried reference-window cause. **Correction:** my first classifier put 47 of the 139 outside the
branch. It measured from the first actual read to the bill's start, where E1 measures from the
change-of-supply read to the latest actual read. Re-classed under E1's definition, all 139 are inside.
The conflict between E1 and the row is a finding:
`docs/staging/SEAT_FINDING_E1_BILLS_THE_REGISTRY_FIGURE_OVER_A_METERS_OWN_READS_AND_SETS_139_ESTIMATE_BREACHES_2026-10-29.md`.

**What the exceptions file now says.** Every row above is set to its 209c3350ab count with its cause. Each
open class is marked open: P5's six, the overdue row's 820 steps over 2p, the 78, and the summer
overshoot. `INV_STATUTE_BARRED_WRITE_OFF_AGE` and `INV_SMART_METER_BILLED_ON_ITS_OWN_READS` are retired.
The suite now gates the 209c3350ab book at **0 unexcepted, 10 excepted: the publish stands.** This is
not the correctness stretch's exit. That needs zero *unexplained* breaches, and the open classes above
are not explained.

**For the next cold read:** take the book of `fresh-run-209c3350ab` (`/var/tmp/fresh-run-out-209c3350ab`,
ledger `/var/tmp/wo-grade-209c/ledger.json`).
