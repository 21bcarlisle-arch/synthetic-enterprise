**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# The second cold read, on the fresh 1691ec0ecd book: leg one met, leg two not met (the mover slot's reason is false), leg three not met (seven new classes) (2026-10-28)

**What this is.** This is the reading the director's correctness ruling asks for
(`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`, "Exit test").
It covers the three legs, each graded against
`docs/staging/records/SEAT_PREREGISTRATION_THE_SECOND_COLD_READ_RUN_PER_ROW_BREACHES_AND_THE_EIGHT_EXPLORE_SLOTS_2026-10-27.md`
as amended on 28 Oct. Item `the-second-cold-read-on-one-fresh-full-run`.

**The book.** The fresh full run at origin `1691ec0ecd`: `launch_long_job`, exit 0, 3,268 s, output in
`/var/tmp/fresh-run-out-1691ec0ecd`. No other run was launched. Nothing in `simulation/`, `company/`,
`saas/`, `sim/`, the runner, the cast generator or `DOMAIN_INVARIANTS.yaml` changed between that commit
and origin `28cc9fa39b`, where this was graded. So the code that made the book is the code on origin.

| exit-test leg | verdict |
|---|---|
| 1. Zero unexplained breaches on the full book of a fresh run | **MET.** 0 unexcepted. All four breached rows have a cause named on this book |
| 2. All eight Explore slots filled validly or honestly empty | **NOT MET.** The mover slot is empty by a hard-coded `return None`, and its stated reason is two-thirds false on this book |
| 3. One cold read finds no new class of error | **NOT MET.** 40 objections; seven are new classes, outside both the first read's 37 and the suite's rows |

**The correctness stretch does not exit.** The ruled order (levers, then the baseline comparison) stays
closed. Two of the three legs fail, so as the item says, the stretch continues.

## Leg one: the suite on every account of the book

Graded with `tools.domain_invariant_runner --ledger`, using origin's `DOMAIN_INVARIANTS.yaml` and
`DOMAIN_INVARIANT_EXCEPTIONS.yaml`, over 1,293 accounts and 52,899 bill periods. It is byte-identical
in every row to the one-due-date grade of the same book (`/var/tmp/onedue-grade-1691/report_ledger.txt`).
The full report is in `/var/tmp/second-cold-read-1691/report.txt`.

**38 of the 43 rows are CLEAN, FLAGGED or UNREACHED with 0 breaches. Four are BREACHED and excepted.
Four are UNCHECKABLE, each for its stated reason.**

| breached row | count | cause on this book |
|---|---|---|
| INV_PPM_NOT_CREDIT_BILLED | 12 of 6,272 | Account C6, the SME prepayment leg, which the row's domestic carve-out does not cover. 0 domestic |
| INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23 | 3 of 2,274 | **The grader's, not the run's (diagnosed this turn).** See below |
| INV_OVERDUE_WITHIN_BALANCE | 4 of 7,380 | The four accounts in the billing ledger's exception_queue. Their bills are held for VAT review and the desk dunns them anyway. The defect is open but its cause is named (1470776471) |
| INV_STATUTE_BARRED_WRITE_OFF_AGE | 3 of 64 | The first write-off is dated before a final bill's later payment, which did not restart the bar. The defect is open but its shape is named (1470776471) |

**The EBSS three, diagnosed.** The exception on origin still described the 2eeb3f0b3 book's seven
occupier months. It said they would retire on "a run carrying the occupier month credit". This run
carries that credit (`ff937d809e` is an ancestor of `1691ec0ecd`), so that reason is refuted. The three
breaches left fall on three of the same four occupier accounts, and all three have one shape: the first
full month after a mid-month opening.

| account | opened (move-out) | void | supply starts | breached month |
|---|---|---|---|---|
| OCC-bec72a04dec8 | 2022-10-27 | 21 days, private renter | 2022-11-17 | 2022-11 |
| OCC-eb8498f3f8aa | 2023-01-17 | 21 days, private renter | 2023-02-07 | 2023-02 |
| OCC-e3e94f81161b | 2023-02-23 | 21 days, private renter | 2023-03-16 | 2023-03 |

(Read from the run's `home_move_ins`.) Each home was empty at 00:00 on the breached month's 1st.
Annex C's "Vacant Properties" exception gives that month no credit
(`docs/market_research/energy_bills_support_scheme_delivery.md`, "Vacant Properties"), and the run
follows it: a void row takes the owner's branch in `run_phase2b`, which has no scheme credit. Every
later month on these accounts is credited. The evaluator counts the void month as on supply only
because the raw export carries no void window. **The breach is explained, and it is the row's.** In this
commit the exception is rewritten for this book: scope 3, reason as above, ceiling 7 → 3, and
`retired_by` the export carrying the void window.

**Leg one is MET on "unexplained".** Two of the four rows (overdue, statute bar) are still open defects
with named causes. The ruling's test is "unexplained", and none is. That is a weaker state than clean,
and it is said here so the leg is not read as clean.

### The grade against the pre-registration

The account count was predicted at 1,291 ± 5%. It is 1,293: **held.**

- **Held**, every row predicted at 0. Also held, every flagged band:
  - INV_UNIT_RATE_FIXED: 8 flagged, against a predicted 0–20.
  - INV_ANNUAL_USE_ELEC_ACCOUNT: 6 flagged, against 0–15.
  - INV_READ_DUTY_ANNUAL: 27.7%, against 20–35%.
  - INV_SETTLEMENT_ACTUAL_SHARE_ELEC: 1 of 1.
  - INV_DD_CADENCE: 59, against 30–120.
  - INV_DD_STEP_CHANGE: 4.3%, against 3–7%.
  - INV_BACK_BILLING_12M: 166, against 80–250.
  - INV_SERIAL_REGISTER_COUNT_STABLE: 2, against 0–5.
  - INV_PPM_NOT_CREDIT_BILLED: 12, all on the SME leg.
  - The four UNCHECKABLE rows: unchanged.
- **Refuted**, INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23: 3, against the predicted 0–2 branch. The cause
  is the void month above, which the pre-registration did not foresee.
- **Void, by the pre-registration's own rule** (a fix landed after it was written):
  - INV_RENEWAL_NOTICE_42_TO_49_DAYS: predicted ≥ 95%, graded 0 of 1,170. The SLC 22C statement landed
    after the file.
  - INV_OVERDUE_WITHIN_BALANCE: predicted 20–35% of openings, graded 0.1%.
  - INV_STATUTE_BARRED_WRITE_OFF_AGE: predicted 15–35, graded 3 of 64.
  The amendment voided both collections rows when the one-due-date fix landed.
- **Leg one predicted NOT met, graded MET: refuted.** All three rows the prediction rested on were
  fixed by landings after it.

## Leg two: the eight Explore slots

The customer pages and the cast were regenerated from this book into
`/var/tmp/second-cold-read-1691/tree` (a `git archive` of origin, so the shared tree was never written).
They were built by the publisher's own chain, in `process_run_complete` order: customer data, billing
ledger, invoices, payment ledger, consumption, reaction chain, sample, `customers.json`, then the cast.
The rebuild came to 1,293 customer files and 52,899 invoices. The invoice count equals the graded
period count.

**How the run output was rebuilt, because the publisher was not used.** `arm.py` pickled the raw output
only. The publisher calls `save_run_output_json` inside the run's own process, where the module rosters
are full. Here they were refilled from the run's own records, in
`/var/tmp/second-cold-read-scripts/build_run_output.py`:
- DRAWN (1,033) by importing `run_phase2b`.
- The 259 incoming occupants by the run's own `incoming_occupant_record` over `home_move_ins` and
  `home_move_outs`. Every rebuilt id equalled the run's.
- The 14 acquisitions by `register_acquired_point`. These feed only the segment map.

`per_customer_lifetime` came to 1,293, the graded account count. The occupants' `data_regime` is the
`HomeMove` default ("synthetic"), because the pickles do not carry it.

| slot | state | household or reason | against the prediction |
|---|---|---|---|
| switch_in | filled | PROS-2025-0022 | held (same household as the live cast) |
| renewal | filled | SYN-2016-031 | held (same) |
| estimate_trap | filled | PROS-2017-0264 | held (same) |
| mover | empty, 0 matched | "no move-out event and no final-bill marker…" | held as empty, but **the reason is false** (below) |
| debt | filled | SYN-2016-356 | held (same) |
| ev | **filled** | SYN-2016-050: +2,891 kWh a year, "not weather-normalised" | **refuted** (predicted empty) |
| storage_heating | empty, 96 matched, 0 pass | no profile class 2 meter (96 of 96), and seven other named checks | held |
| shock_2022 | filled | PROS-2019-0246 | held (same) |

**The mover slot is not honestly empty.** `_score_mover` is `return None` with no condition
(`tools/generate_explore_cast.py:625`). So the slot never ranks anything. The "0 matched" is the
constant, not a count. Its printed reason says "The published record carries no move-out event and no
final-bill marker". On this book's pages, `final_bill` timeline events stand on 866 accounts and
`moved_out` on 259. The live published pages carry them too: C1 has `final_bill` on 2016-04-20 and
`moved_out` on 2016-04-21, from `tools/generate_customer_reaction_chain.py:199`. The third clause is
true: no OCC- account names the household it replaced, so "followed by a new occupant" still cannot be
read. That is a guard that refuses everything, under a reason that has rotted. The ruling's own words
are "shown empty with the failing check named", and the named check here is wrong in two of its three
parts. Filed as
`docs/staging/SEAT_FINDING_THE_MOVER_SLOT_IS_EMPTY_BY_A_CONSTANT_AND_ITS_REASON_DENIES_A_RECORD_THE_PAGES_CARRY_2026-10-28.md`.

**The EV slot fills, and its effect line says "not weather-normalised".** Ruling step 3 lists "EV effects
measured on electricity and weather-normalised" as a root cause. The slot passes its own validity checks
(full year either side, effect within 1,750–3,300 kWh, rise after the car). The line it prints says
plainly that the normalisation step 3 asks for is not done. The blind reader objected to the EV home on other grounds (O18–O20: a fixed term with no renewal, a catch-up line, a low pre-car baseline), not on normalisation. The slot is graded as filled, with that caveat on the surface.

**Leg two: NOT MET**, on the mover slot alone, whatever the reader says about the six filled slots.

## Leg three: the cold read

**How it was taken.** This is the first read's method (`docs/staging/records/SEAT_RECORD_THE_FIRST_COLD_READ_ON_THE_4AE8DA9B0F_PAGES_2026-10-27.md`, section 2), on this book's pages:

1. The scratch `site/` was served locally and rendered by the first read's own Playwright script
   (`/tmp/coldread/render.mjs`). Every moment of all eight cast tabs was captured.
2. Six households were drawn from the page's own picker of 752 with `random.Random(20261028).sample`:
   SYN-2016-426, SYN-2016-329, SYN-2016-544, SYN-2016-601, SYN-2016-371 and OCC-423594fbfa6b. Each was
   captured through all six stages.
3. The packet is 113,755 characters (`/var/tmp/second-cold-read-1691/packet.txt`). Its only code path
   is the carbon basis line the page itself prints.
4. A fresh Opus agent, briefed as a twenty-year GB retail-energy professional, wrote its priors and
   then read only that file: no code, no repo, no commands, no web.
5. The seat then checked 14 of its key quotes against the packet, and all 14 are verbatim. Two sit in
   tab-separated table cells.

**Independence: false.** The reader is the same model family as the builder, so the blindfold gives
blindness, not independence.

**What it found: 40 objections** (O1–O40). The full text was the agent's return, as at the first read. Each objection is classified below by id,
with its quote checked. Its own verdict: "A GB energy professional would
not trust these examples as a record of a supplier's conduct". It also confirmed that cap and EPG
period unit rates and per-bill VAT arithmetic reconcile.

### New classes: not in the first read's 37, and no suite row covers them

| new class | objections | checked by the seat |
|---|---|---|
| **N1. The bill a page prints omits a credit the ledger holds, so the suite is green and the page is wrong** | O22 (the 2022-shock slot: Dec 2022 £598.04, no EBSS line) | Confirmed. PROS-2019-0246's raw export carries all six `scheme_credit` adjustments (£400). Its invoices carry `credit_applied_gbp: None` and the full amounts. `INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23` grades the ledger, so it passes. **The class is the suite reading a different record from the one the page prints.** The first read's O22 had no credit on any named account. This is new: a credited account whose bill hides it |
| **N2. Settlement revenue before VAT exceeds the VAT-inclusive amount billed, before any crisis support** | O27 | Confirmed on the page. OCC-423594fbfa6b (supplied 2016 to 2019) shows "Revenue, before VAT £2,277.10" against "Billed, VAT included £1,998.82" |
| **N3. The payment-record counters do not reconcile with the bills** | O13, O15 | Quotes verbatim: "34 payments, 4 returned, 42 missed" on a 50-bill account, and "6 payments, 4 returned, 0 missed" (a returned DD is not counted as missed, and the DD is kept after 4 of 6 returns) |
| **N4. No demand response to the 2022–23 prices** | O31 | Quote verbatim: electricity 2,467 / 2,511 / 2,494 kWh for 2021 to 2023 on SYN-2016-329. It is a world question, and the knowledge layer has `domestic_shift_response_arc.json`. Not yet measured book-wide |
| **N5. Two figures for one quantity in one year disagree** | O34 | Quote verbatim: the carbon panel's "Gas 1,345 kg 7,303 kWh billed over 8 month(s)" against a usage panel of 6,180 kWh for 2017 on SYN-2016-371. A part-year figure is also published against the method's own "has no figure" |
| **N6. Regulatory copy that misstates the smart data-access rule** | O39 | Quote verbatim, "read frequency is the customer's consent to give" (6 times). The reader's reading: monthly reads need no consent, daily reads are opt-out, half-hourly reads are opt-in. GAP: the commons copy of Ofgem's data access and privacy framework is not checked this turn |
| **N7. Estimates do not follow the latest actual reads** | O20 | Quote verbatim, the EV home's "avg 157 kWh/mo -> 398 kWh/mo", followed by a May 2020 estimate of 136 kWh. Not yet measured book-wide |

### Existing classes, already named in the first read, a finding or a row

- **Prices:**
  - O10, O17, O40: pre-2019 SVT levels. The first read's O3; the pre-cap floor amendment is still owed.
  - O25: one SVT price per region. `INV_SVT_ONE_PRICE_PER_REGION_METHOD_WINDOW`, UNCHECKABLE.
  - O1, O3: a fixed rate printed as one £/MWh, with bills that do not follow it. The first read's O5 and `SEAT_FINDING_THE_PRINTED_RATE_AGAINST_THE_CONTRACTED_TARIFF_2026-10-26.md`. O1's "5-year fix through 2022" may be a label artefact of the same thing; not established.
- **Renewal:** O2. The SLC 22C statement goes out on this book (row CLEAN, 0 of 1,170), but the page
  shows only the expiry-day decision. The first read's O6, now a page-side remainder.
- **Collections:**
  - O4, O14: overdue larger than owed, and notices out of order. The first read's O10, O16–O18. On this book the suite grades 4 openings (all exception_queue), so the page's figures come from a different record from the desk's. Same shape as N1.
  - O15: a write-off a month early. `INV_STATUTE_BARRED_WRITE_OFF_AGE`, excepted 3.
  - O27–O30, O36: DD as pay-on-receipt, frozen balances, credit on a closed account. The first read's O27, and focus item 2.
- **Definitions and labels:**
  - O26: margins. The first read's O25 (definitions), with the level now a B13 question.
  - O28: a one-fuel ledger shown as the household's. The first read's O28.
  - O32: r over part years. The first read's O29.
  - O33, O18: renewal rows on SVT accounts and garbled tariff labels. The first read's O9 and O11.
  - O35: the bill format. The first read's O34.
  - O37, O38: percentage points, and three book sizes. The first read's O11 and O33.
  - O9: "three months in". The first read's O12.
- **Root causes the ruling already names:**
  - O21, O24: storage heating and multi-rate meters (ruling step 3).
  - O16, O6: truth-side narrative and the 0.0% churn chance. The first read's O8, O20 and O21.
  - O23: "use did not explain". The first read's O23.
- **The empty slots:**
  - O12: the reader called the mover reason "honest". The seat's grade above shows it is not.
  - O21: the storage-heating reason, judged honest. The reader also judged "its account id is not in the public format" jargon (copy).

**Leg three: NOT MET.** The read finds new classes, seven of them. N1 matters most: the suite is green on
a defect a reader sees in one glance, because the suite and the page read different records of the same
bill. The prediction (at least one new class, among the renewal letter, the debt dates or a dual-fuel
cost-to-serve line) **held** on "not met". It missed which classes: the renewal letter's absence is O2,
an existing class, and the other two did not come up as new.

## What follows

- `docs/staging/SEAT_FINDING_THE_SECOND_COLD_READ_FINDS_SEVEN_NEW_CLASSES_AND_THE_SUITE_GRADES_A_RECORD_THE_PAGE_DOES_NOT_PRINT_2026-10-28.md`
  carries N1–N7 for drawing. Under step 6, each confirmed objection becomes a new invariant, so each one
  needs a row written blind from the knowledge pages. N1 needs the rows to grade what the page prints
  (the invoice and its credit lines), not only the ledger.
- `docs/staging/SEAT_FINDING_THE_MOVER_SLOT_IS_EMPTY_BY_A_CONSTANT_AND_ITS_REASON_DENIES_A_RECORD_THE_PAGES_CARRY_2026-10-28.md`
  covers leg two.
- The EBSS exception is rewritten for this book in this commit.
- **The stretch continues.** The next exit attempt needs N1 and the mover slot fixed, the seven classes
  as rows, a fresh run, and a third cold read.
