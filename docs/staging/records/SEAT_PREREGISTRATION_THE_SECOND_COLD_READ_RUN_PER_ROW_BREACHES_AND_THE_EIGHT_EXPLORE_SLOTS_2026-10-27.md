# Pre-registration: the fresh full run for the second cold read, per-row breaches and the eight Explore slots (2026-10-27)

**Item:** `the-second-cold-read-on-one-fresh-full-run` (Lane 0, the exit test of the director's
correctness ruling of 26 Oct). **Status: filed, run NOT launched.** The item's own gate says "only
once items 1 to 3 are on origin; if any is not, write the pre-registration and stop."

## Why the run is not launched

Read at origin `97d18d3878` (20:11 UTC):

| focus item | on origin? |
|---|---|
| 1. the six cold-read rows read the company's own events | yes: `5e3e9966a5` (four rows' evaluators), `97d18d3878` (estimate run moved to the page; `NEXT: none`) |
| 2. a credit balance is refunded at exit and the residue traced | refund path yes (`13f8cc50c3`, page ledger). The trace of the 24 owing more is not shown on origin by this read |
| 3. the occupier EBSS credit is sized by the month, not the debt | **no.** No commit touches `occupier_scheme_credit` / `_occupier_credit_left` in `simulation/run_phase2b.py` since `2eeb3f0b32` |

Item 3 is a world fix that changes the book this run would grade, so launching now would spend the
one allowed run on a book that must be repeated. The run waits for item 3.

## Baseline these predictions are made from

Already seen: the grade of the 2eeb3f0b3 book with the six-row code (`/var/tmp/six-rows-regrade/grade.txt`,
1,291 accounts, 752 households). Not seen: any run at a later commit. The commits since 2eeb3f0b32
that touch `simulation/` or `company/` are `fccc0a41c7`, `79bbd9a3d3`, `9d7bd4a5c8` and `5e3e9966a5`.
The regrade ledger was rebuilt with their code, but the run under it was not re-simulated. So the
baseline carries their ledger-side effect and not any run-side effect. That is a source of error I
cannot size before the run. The predictions
assume the run is launched after item 3 lands and nothing else in `simulation/` or `company/` moves.
If anything else lands first, these predictions are void for the rows it touches, and the reading
must say so.

## Predictions, per DOMAIN_INVARIANTS.yaml row (BREACHED count; FLAGGED in brackets where non-zero)

The account count is predicted at 1,291 ± 5% and households at 752 ± 5%. Every count below scales
with it.

| row | baseline | predicted on the fresh run |
|---|---|---|
| INV_UNIT_RATE_SVT_ELEC / _PRE_CAP / _GAS / _GAS_PRE_CAP | 0 / 0 / 0 / 0 | 0 each |
| INV_UNIT_RATE_SVT_ELEC_MULTI_REGISTER | unreached (0 checked) | unreached. The world has no multi-register SVT term |
| INV_UNIT_RATE_FIXED | 0 (8 flagged) | 0 (0–20 flagged) |
| INV_STANDING_CHARGE_SVT_ELEC / _GAS / _FIXED | 0 / 0 / 0 | 0 each |
| INV_ANNUAL_USE_ELEC_ACCOUNT / _GAS_ACCOUNT / _BOOK_MEDIAN | 0 / 0 / 0 | 0 each (elec flagged 0–15) |
| INV_READ_DUTY_ANNUAL | 0 (312 flagged, 27.7%) | 0 (20%–35% flagged). Nothing in the queue fixes the read duty, so the flag stays |
| INV_SETTLEMENT_ACTUAL_SHARE_ELEC | 0 (1 of 1 flagged) | 0 (1 of 1 flagged) |
| INV_BILL_AT_LEAST_TWICE_YEARLY, INV_OPENING_READ, INV_PAYMENT_PPM_AND_DD_NOT_CONCURRENT, INV_PAYMENT_AMOUNT_SIGN | 0 each | 0 each |
| INV_DD_CADENCE | 0 (61 flagged) | 0 (30–120 flagged) |
| INV_DD_STEP_CHANGE | 0 (1,626 flagged, 4.6%) | 0 (3%–7% flagged) |
| INV_PPM_NOT_CREDIT_BILLED | 12 (excepted, C6 SME leg) | 12 (excepted). 0 domestic |
| INV_FUEL_IDENTIFIER, INV_GAS_SINGLE_REGISTER, INV_CROSS_FUEL_PRICE_SCALE | 0 each | 0 each |
| INV_PERIODS_CONTIGUOUS, INV_PERIOD_CONSUMPTION_NON_NEGATIVE, INV_READ_MONOTONIC, INV_PERIOD_MATCHES_READS | 0 each | 0 each |
| INV_BACK_BILLING_12M | 0 (165 flagged) | 0 (80–250 flagged) |
| INV_VAT_RATE, INV_NON_COMMODITY_WITHIN_ALL_IN, INV_REGISTER_ID_ONE_LABEL, INV_MPAN_CORE_FORMAT, INV_COLLECTIONS_EVENTS_ORDERED | 0 each | 0 each |
| INV_SERIAL_REGISTER_COUNT_STABLE | 0 (2 flagged) | 0 (0–5 flagged) |
| **INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23** | 12 (7 occupier, 5 PROS joiner part-months) | **0–2 if item 3 is "one eligibility home" as the exception's `retired_by` names; 5 (±2) if item 3 fixes only the occupier path.** The reading must say which item 3 landed |
| **INV_RENEWAL_NOTICE_42_TO_49_DAYS** | 1,338 of 1,338 (excepted to 1,338) | **at least 95% of graded terms**. `renewal_notice_register` stays unwired. Risk: a count above 1,338 refuses the gate on scale alone, though the cause is the same |
| **INV_OVERDUE_WITHIN_BALANCE** (leg 2) | 1,987 of 7,151 (27.8%, excepted to 1,987) | **20%–35% of openings.** The two payment records are not reconciled by anything queued. Same scale risk against the ceiling |
| **INV_STATUTE_BARRED_WRITE_OFF_AGE** | 25 of 41 (excepted to 25) | **15–35 of 30–55 write-offs.** Same scale risk |
| INV_UNIT_RATE_EPG_HOUSEHOLD, INV_EV_ADOPTION_ELECTRICITY_ONLY, INV_SVT_ONE_PRICE_PER_REGION_METHOD_WINDOW, INV_ESTIMATE_RUN_WITHIN_TENURE | uncheckable | uncheckable, each for its stated reason |

**Leg one, predicted: NOT met.** Three rows (renewal notice, overdue leg 2, statute bar) are
breached, and each is excepted only to a ceiling and a "partly diagnosed" cause. Renewal is a
company defect with a known fix: the register exists and nothing calls it. That is a known cause, not
an unexplained one. The overdue leg's 1,769 "collected on time" openings have no established cause
(two payment records, which one is wrong is not yet said). So leg one fails on "zero unexplained"
unless that cause is established first.

## Predictions, the eight Explore slots

Baseline: the published cast (`site/data/explore_cast.json`, built 18:54 from the 4ae8da9b0f run).

| slot | baseline | predicted |
|---|---|---|
| switch_in | filled (PROS-2025-0022) | filled |
| renewal | filled (SYN-2016-031) | filled |
| estimate_trap | filled (PROS-2017-0264) | filled. The run is dated at its last estimated bill and is no longer than its fuel's bills (`97d18d3878`) |
| mover | empty, named: no move-out event, final bill or occupant link on the record | **empty, same reason.** Nothing queued carries a move-out to the record |
| debt | filled (SYN-2016-356) | filled. SYN-2016-356 is the household whose journeys open on the 29th against bills due on the 14th–19th. If it is still chosen, the cold reader will likely object to it |
| ev | empty, named: 21 match, none passes (16 lack a full year either side) | **empty.** The EV root cause (ruling step 3) is not on origin |
| storage_heating | empty, named: 96 match, none has a profile class 2 meter | **empty.** The storage-heating defect (ruling step 3) is not on origin |
| shock_2022 | filled (PROS-2019-0246) | filled |

**Leg two, predicted: met** (5 filled validly, 3 honestly empty with the failing check named). The
cold read decides "validly".

**Leg three, predicted: NOT met.** The cold reader will find at least one new class among: the
renewal letter the page never shows, the debt household's collection dates against its bill dates,
and a cost-to-serve line on a dual-fuel home. This is a guess at the reader, stated before the read.

## What launches the run

Item 3 on origin, with its red-then-green test. Then: re-check `simulation/` and `company/` for
anything landed after this file (void the rows it touches), and launch through `launch_long_job` at
origin HEAD. It must be a full run with `per_customer_lifetime`, not a pickled arm, and nothing may run
in parallel. Grade it with `tools/domain_invariant_runner.py`. Regenerate the customer pages and the
Explore cast into `/var/tmp`, run the blind cold read, and grade every row above, unedited.
