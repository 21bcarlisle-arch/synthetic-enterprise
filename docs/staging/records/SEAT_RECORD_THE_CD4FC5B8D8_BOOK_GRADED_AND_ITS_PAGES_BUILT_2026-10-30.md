**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** none — Lane 0 `the-fresh-run-at-the-meter-fixes`

# The cd4fc5b8d8 book, graded, with its pages built: the meter fixes moved every new breach onto profile class 2 (2026-10-30)

Under the correctness stretch (`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`).
This is the first fresh book to carry the Economy 7 two-register bill (fca63e87d), the PC2 per-register estimate
(32ddfa8ca) and the per-supply-point serial (6ef8f1b67). **It does not carry the gas build (N11).** Only that
build's K8 page is on origin (e0f8c1fbed), so the run went ahead without it, as DIRECTION allowed.

**The run.** Job `fresh-run-cd4fc5b8d8`, output `/var/tmp/fresh-run-out-cd4fc5b8d8`. It was launched 13:09Z and
SURVIVED (rc 0, 79 min). The pretest of `tests/company/billing` run whole found
`SEAT_FINDING_TESTS_COMPANY_BILLING_RUN_WHOLE_REDS_41_TESTS_THAT_PASS_ALONE_2026-10-30.md`. The grade chain
`grade-chain-cd4fc5b8d8` wrote `/var/tmp/fresh-grade-cd4fc5b8d8/`:
- `ledger.json`
- `grade.txt` / `grade.json`, the full suite
- `journeys.txt`
- `f_vat.txt`
- `debt_p4.txt`
- `n189.txt`
- `cast.txt`
- the pages, at `tree/site/data/`

The per-row breach lists are in `/var/tmp/grade-cd4f-trace/all_hits.json`, from the same grade with every
breach kept (`grade_hits.py`).

## The headline: 1,034 unexcepted breaches, and every new one is on a profile class 2 home

On the 3dc5a92948 book the suite read 0 unexcepted breaches. On this book it reads **1,034 across 9 rows**, so
**the publish is refused**. One row is a defect in the row itself, and this commit fixes it. Every other new
breach is on an account that settles on profile class 2. **None is on a PC1 or gas account** except the 6 PC1
EBSS breaches, which are the old 6.

| row | 3dc5a92948 | cd4fc5b8d8 | where |
|---|---|---|---|
| INV_SVT_ONE_PRICE_PER_REGION_METHOD_WINDOW | 0 | **690**, then **0** after this commit's row fix | 23 PC2 accounts, all below the median |
| INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS | 0 | **170** | 31 PC2 accounts; above in Nov-Mar, below in Jun-Sep |
| INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL | 6 | **120** | 22 PC2 accounts |
| INV_EBSS_CREDIT_EACH_MONTH / _ON_THE_BILL | 6 / 6 | **21 / 21** | 15 on PC2, plus the old 6 on PC1 |
| INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE | 1 | **4** | 4 PC2 accounts; page bills £0.2k-£3.9k below revenue |
| INV_E7_METER_BILLED_ON_TWO_REGISTERS | (new) | **4** | OCC-23ee23cb44e4, OCC-7e06d09fc108: the first two bills print Anytime |
| INV_TOU_BANDS_SUM_TO_THE_TOTAL | (new) | **2** | the same two accounts, at the change from Anytime to Day/Night |
| INV_PERIODS_CONTIGUOUS | (new) | **2** | OCC-8c6b8bb21743 (62-day gap), PROS-2020-0189 (152-day gap) |

**The SVT row was the row, not the bill: fixed here.** Every one of the 690 breaches is an E7 SVT's Day/Night
blend, at 14.64p in Jan 2019 (Day 18.83p, Night 8.85p), set against the single-rate SVT median of 15.73p. The cap
sets single-rate and multi-register electricity each its own level (SLC 28AD). The multi-register SVT row grades
these terms **clean, 0 of 356**. The one-price row, though, pooled both arrangements into one group.
- Graded by the registers each term prints, the same split `_svt_term_windows` uses, the row reads **0 of
  32,493 single-rate and 0 of 859 multi-register**.
- `tools/domain_invariant_runner.ev_svt_one_price` now groups by metering arrangement.
- `test_an_economy_7_svt_is_priced_against_its_own_metering_arrangement_not_single_rate` is red on the pooled
  key and green on the fix.

**The rest I cannot yet attribute to the bill or to the row, one row at a time.** The two builds landed together,
so the cause is shared, and I name it as a class. The finding filed with this record
(`SEAT_FINDING_THE_E7_AND_PC2_BUILDS_LEAVE_EIGHT_ROWS_BREACHED_ON_PROFILE_CLASS_2_HOMES_2026-10-30.md`) carries the
trace, row by row. Some of it reads as real defects in the bill, rather than in a row that has not caught up:
- page bills up to £3.9k below revenue on one account;
- no EBSS credit on 15 PC2 bills;
- 152-day gaps between periods.

## Each prediction, held or refuted

### The launch's own question (run_case, 13:09Z)

| prediction | measured | verdict |
|---|---|---|
| INV_E7_METER_BILLED_ON_TWO_REGISTERS 0 (also N1, P3) | 4, on two occupier accounts whose first two bills print Anytime | **refuted** |
| INV_METER_SERIAL_ONE_SUPPLY_POINT (N10) 0 re-minted | 0 of 52,657 | **held** |
| INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER 6 -> 2 | 4: PROS-2017-0336 once, SYN-2016-565, SYN-2016-396g (b), PROS-2016-0263g (c); PROS-2024-0010 left | **refuted** (it fell by 2, not 4) |
| the storage-heating Explore slot fills | empty: "the record names no profile class 2 (Economy 7) meter for it (132 of 132)" | **refuted** |
| SVT row holds at 0 | 690 as graded at cd4fc5b8d8; 0 after the row fix above | **refuted as graded**; the cause is the row, not the price |
| F/VAT: reads left uncorrected 0, catch-ups off the VAT line 0 | 0 of 6,437; 0 | **held** |
| revenue row holds at 1 | 4, all PC2 | **refuted** |
| desk-cure P1: zero `cured` at `days_overdue == 0` | 0 of 1,069 journeys | **held** |
| estimate row holds at 0 (the declared policy, cb53859273) | 170, all PC2 | **refuted** |

### The E7 build's own (fca63e87d) and the PC2 estimate's own (32ddfa8ca)

| prediction | measured | verdict |
|---|---|---|
| N2: every storage home's electricity invoices print Day/Night | two PC2 occupier accounts print Anytime on their first two bills | **refuted** for those two |
| N3: INV_UNIT_RATE_SVT_ELEC_MULTI_REGISTER 0 | CLEAN, 0 of 356 | **held** |
| N4: storage homes' electricity revenue falls against 209c | not measured on this pass | **not graded** |
| P1: PROS-2017-0336, PROS-2024-0010 and SYN-2016-565 leave the estimate row | 0336 left; 0010 (4 bills) and 565 (1 bill) remain | **refuted** for 2 of 3 |
| P2: no storage home gains a breach from the estimator; any new breach is the row's PC1 reshaping | 170 new breaches on PC2 homes, seasonal (Nov-Mar above, Jun-Sep below) | **open**: the pattern is the shape P2 names, but the row's bound on a PC2 home has not been read, so the attribution is not made |
| P4: estimated kWh per bill on storage homes falls Apr-Aug against e400c589d | not measured on this pass | **not graded** |

### Left to the run after

**Item 2's gas prediction is left to the next run.** The gas build is not on origin, and
INV_GAS_READ_IS_A_VOLUME_CONVERTED_AT_CV_AND_CF reads UNCHECKABLE on this book, as written.

## The pages, the cast and the debt slot

**Cast: 6 of 8 filled.** EV and storage heating are honestly empty, each naming its failing checks. The slots
are the same as on 3dc5a92948, except the mover:

| slot | household |
|---|---|
| switch_in | PROS-2025-0022 |
| renewal | SYN-2016-031 |
| estimate_trap | PROS-2017-0264 |
| **mover** | **SYN-2016-368** (was PROS-2017-0351, which is now a PC2 account breaching the estimate row) |
| debt | SYN-2016-210 |
| shock_2022 | PROS-2019-0246 |

**The storage slot is empty on a check that contradicts the book.** It reads "the record names no profile class
2 meter" on all 132 households its rule matches, yet 31 or more accounts carry PC2 periods on this ledger. The
slot's check, or the field it reads, has not caught up with the E7 build. That is the first thing to trace for
the slot, and it is in the finding.

**N1/N8/N9 page tests on these pages:** 10 passed.

**Debt slot.** SYN-2016-210 passes all four checks. Of the 381 debt stories matched, 106 are refused by any check
and 2 by "cleared while still owed".

**The two "cleared while still owed" survivors are the same two as on 3dc5a92948, with nothing new:**
- **PROS-2025-0013:** the story outruns its own page. That record traced it, and it is unchanged.
- **PROS-2020-0191:** cause not established. It still needs `CollectionsJourneyDesk.advance` replayed over the
  account's ledger to 2025-01-16. That replay was not done on this pass.

The pages are at `/var/tmp/fresh-grade-cd4fc5b8d8/tree/site/data/`. The committed `site/` is not touched.

## The exceptions file

Ceilings are reset only where this book's count is at or below the old one.

**Reset or held:**
- INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER **6 -> 4**. Scope rewritten to the four runs.
- INV_UNIT_RATE_EPG_HOUSEHOLD **373 -> 350**.
- INV_PPM_NOT_CREDIT_BILLED stays at 12.

**Not raised, departing from DIRECTION on purpose:**
- EBSS 6 -> 21
- revenue 1 -> 4
- carbon 6 -> 120

Raising a ceiling over breaches nobody has traced would turn unexplained into excepted. The ruling's exit test
is "zero unexplained breaches". These rows stay unexcepted and refuse the publish until the finding's trace
names them.

**Retired:** no row reads 0 that still had an exception. SVT's was retired on 3dc5a92948, and the estimate row's
by cb53859273.

## The refused advisor file, seen

`docs/staging/advisor/DIRECTOR_STEER_TIME_IS_VALUE_A_SUPPLIER_CAN_CREATE_AND_THE_WORLD_MUST_FEEL_HASSLE_2026-10-30.md` was
flagged as unsigned at fe193364b. The diff from the advisor's signed 053a459f2 only appends the seat's own
`## Progress` section, and the signed ruling text is unchanged. **It is left in place, not moved to done/.**
The seat's note holds it open until item 1 (the wording) lands in its own lane. Moving it from here would close
an item another lane is still working.
