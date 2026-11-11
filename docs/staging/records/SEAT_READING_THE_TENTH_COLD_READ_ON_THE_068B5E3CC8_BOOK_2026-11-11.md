**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# The tenth cold read, on the 068b5e3cc8 book: the book does not pass the publisher's gate after all, and a meter data-quality analyst finds four new classes (2026-11-11)

**What this is.** This is the correctness ruling's step 6 reading
(`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`, "Exit test"). It is the
lane-0 item `the-tenth-cold-read-on-the-first-book-that-passes-the-gate`, graded against
`records/SEAT_PREREGISTRATION_THE_TENTH_COLD_READ_ON_THE_068B5E3CC8_BOOK_2026-11-11.md` (landed 807811584, before
the packet rendered).

**The book and the pages.**
- The book is `run_output_068b5e3cc8_20261110T190254Z.json`: 1,302 accounts, 53,921 invoices, 757 households in the
  picker.
- The pages were built in a scratch tree at origin 6fff2c2575 (`/var/tmp/tenth-read/tree`, served on
  127.0.0.1:8801), using the publisher's customer-page chain followed by `generate_explore_hh_day` and
  `generate_explore_carbon`, per the ninth read's correction. **These are not the live pages.**
- The cast is 8 of 8 filled: switch_in PROS-2025-0022, renewal PROS-2022-0011, estimate_trap PROS-2017-0264,
  mover SYN-2016-527, debt PROS-2016-0054, ev PROS-2017-0183, storage_heating PROS-2020-0189, shock_2022
  PROS-2019-0246.
- Section B was drawn with `random.Random(20261111)` from 657 households: the picker less the 99 households in any
  earlier draw or cast, and less this cast. The draw, as accounts 1 to 10: SYN-2016-258, PROS-2023-0223,
  SYN-2016-078, PROS-2016-0264, SYN-2016-282, SYN-2016-018, SYN-2016-511, OCC-c2c2a33d47d7, PROS-2018-0016,
  OCC-88636921e9c6.
- **The trade, new to these reads:** a supply-point registration and meter data-quality analyst. The blind tree is
  `/var/tmp/tenth-read/blind`, which `blind_worktree --check` reported clean. The reader returned 32 objections.

| exit-test leg | verdict |
|---|---|
| 1. The suite on a fresh run's full book: zero unexplained breaches | **NOT MET.** The publisher's gate refuses: `INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO` has 3 breaches against the exception's `max_breached` of 2. The third is SYN-2016-493, GBP 11.56 of credit left since 2022. The 6fff2c257 "pass" came from a scratch grade that could not read this row. See `SEAT_FINDING_THE_068B5E3CC8_BOOK_DOES_NOT_PASS_THE_PUBLISHERS_GATE_THE_SCRATCH_GRADE_COULD_NOT_READ_THE_CLOSED_ACCOUNT_ROW_2026-11-11.md` |
| 2. All eight slots filled validly or honestly empty | **NOT MET.** 8 of 8 are filled. The 2022-shock slot prints "the household's use did not explain the change" over a 29% rise in use (N28). The EV slot tells a six-year customer "Your first electricity bill is ready" (N28) |
| 3. One cold read finds no new class | **NOT MET.** Four new classes: N25 to N28 |

**The stretch does not exit.** The advisor file stays where it is.

**A deviation from the preregistration, said plainly.** The preregistration said that if the gate did not pass, "the
read stops". The method I wrote ran the gate *after* the brief, which is the ninth read's order. So the reader had
already been briefed when the gate refused. I let the read finish. The breach that refuses the book is one GBP 11.56
instance of a class that is already excepted and named, so the reader's blindness to open classes is not materially
weaker than on a passing book. **But this is not the exit test's leg three on a passing book, and it must not be
counted as one.** For the next read, run the gate before the brief.

## Predictions against results

| # | prediction | result |
|---|---|---|
| P1 | The gate on the scratch pages reproduces 6fff2c257: 0 unexcepted, refuse False | **Refuted.** The gate says PERMITS False: the closed-account row has 3 breaches against a cap of 2. Four rows that were NOT_IN_EXPORT on the scratch grade are graded here, and the other three of them are clean or flagged. All other rows' verdicts match |
| P2 | Cast 8 of 8 | **Held** |
| P3 | 0 serials on two or more supply numbers; supply numbers on two or more serials under 5% | **Held, and the second half too well:** 0 and 0 across 1,040 supply points. No meter is ever exchanged in ten years. That is the known D48 class (`WORKER_FINDING_D48_THE_ESTIMATED_SHARE_IS_FLAT_BECAUSE_NO_METER_IS_EVER_EXCHANGED_AFTER_ACQUISITION_2026-10-21.md`), not new. 214 serials sit on more than one account, all on one supply point each: successive occupants on the same meter, which is lawful |
| P4 | Electricity median same-month change under 3%; gas 8–18% | **Held**: electricity 0.73% (3,183 of 5,335 pairs under 1%; 451 repeats to 0.1 kWh), gas 13.03% (17 repeats) |
| P5 | 0 prepayment statements paid another way, outside the excepted class | **Held**: 0. 11 prepayment-paid bills, all on C6, which is the excepted INV_PPM_NOT_CREDIT_BILLED class |
| P6 | Closed balances still present, each side GBP 5k–40k | **Refuted, in the good direction.** Of 805 accounts whose last bill is a year or more old, 1 holds credit (SYN-2016-493, GBP 11.56) and 66 hold debt (GBP 3,635.92). The ninth read found GBP 15.7k and 21.6k. Class L' and the close fixes have done most of this |
| P7 | Control: the reader finds N17 unaided (p ≈ 0.6) | **Held** (O3: "eight years within ±0.4%") |
| P8 | 20–40 objections | **Held** (32) |
| P9 | One to three new classes | **Refuted on the upper side**: four |
| P10 | Nothing on one-serial-per-supply-point survives the seat's check | **Held, but only partly tested by eye.** The pages print one electricity serial per account and **no gas serial, MPRN or gas read at all** (O2), so the reader could not test the 34-supply-point row on gas. My check over every page file did: 0 |
| P11 | Leg one MET, leg two MET, leg three NOT MET | Leg one **refuted** (P1). Leg two **refuted** (N28 on two slots). Leg three **held** |

## The four new classes, each confirmed over every page file

Each one is filed as a blind row (`checkable: false`, evaluator owed), written by a separate agent that read
knowledge pages only. They are in `DOMAIN_INVARIANTS.yaml` under the ids below.

- **N25. A fixed term's prices move inside the term** (O9, "wrong"). `INV_FIXED_TERM_RATES_HOLD_FOR_THE_TERM`.
  - SYN-2016-078's fix from 22 Feb 2016 commits GBP 0.1860/day. Its bills print 0.1865 in March, 0.1937 from April,
    and 0.1943–0.1945 later.
  - Over the book, on single-term fixed runs (3 to 13 bills on one fixed tariff name, full months only), **the
    standing charge moves more than 1% on 711 of 862 runs**, and the all-in unit rate on 486, across 615 accounts
    (`/var/tmp/tenth-read/scripts/fixmove.py`).
  - The gate cannot see it: INV_UNIT_RATE_FIXED grades a fix "once at the window it was struck in", and
    INV_STANDING_CHARGE_FIXED checks only that the charge is non-negative.
  - On SYN-2016-078 the all-in unit rate holds at 11.05p for the whole fix except its last bill (12.11p, Feb 2017).
    The bills then go to SVT from March 2017, although the timeline's first renewal is 21 Feb 2018. I have not traced
    that gap.
- **N26. The page's ledger sentence does not add up** (O19, "wrong"). `INV_HOUSEHOLD_PAGE_LEDGER_SUMMARY_RECONCILES_TO_ITS_BALANCE`.
  - `site/explore/index.html` prints "Billed, collected, government bill credit, balance". It omits deemed amounts,
    refunds, write-offs and recoveries.
  - On **494 of 1,302** ledgers, billed − collected − credit ≠ balance. OCC-c2c2a33d47d7 is short by exactly its
    GBP 910.06 `total_deemed_gbp`, and OCC-88636921e9c6 by its GBP 365.32.
  - The ledger is right. The sentence is incomplete.
- **N27. The Paid stage is the electricity account's, shown as the household's** (O18, "wrong").
  `INV_HOUSEHOLD_PAGE_PAID_STAGE_COVERS_EVERY_FUEL_ACCOUNT`.
  - The page loads both legs, then sets `d = byFuel.electricity || byFuel.gas` and draws stage 5 from `d.ledger`
    alone. Every dual-fuel household therefore shows two balances.
  - For example, account 9 (PROS-2018-0016) shows a ledger balance of GBP 166.59 against "Owed on 4 Jul 2025
    GBP 242.04".
- **N28. Narrated facts nobody checked** (O28, O29 and O14). `INV_HOUSEHOLD_PAGE_NARRATED_FACT_IS_TRUE_OF_THE_ACCOUNT`.
  The cast's `_template` asserts each of these unconditionally:
  - "Your first {fuel} bill is ready" on any moment of kind `first_bill`, which the EV slot uses for the first bill
    after the car (2023, on a 2017 account).
  - "the household's use did not explain the change" on every 2022-shock slot. PROS-2019-0246's compared month rose
    29% in use.
  - The mover's final bill reads "less its GBP 58.36 Energy Bills Support Scheme credit". The ledger credited
    GBP 66.00 and refunded the GBP 7.64 surplus on 9 Nov 2022.

## The other objections, graded

| objection | grade |
|---|---|
| O1 registers start at zero at supply start | **Known**: INV_OPENING_READ flags 1,302 of 1,302 (`SEAT_FINDING_THE_PRINTED_REGISTER_FIX_EXPOSES_ESTIMATES_FROM_ONE_READ_AND_PRINTS_6436_OPENING_READS_NOBODY_TOOK_2026-10-28.md`) |
| O2 no MPRN, gas serial or gas volume on any page | **Known**: the DIRECTION `wrong` row "a gas bill with no volume" |
| O3 electricity flat year on year | **Known**, N17 (excepted) |
| O4 monthly actual reads on traditional meters | Known family (D48, read frequency against meter type); not re-measured |
| O5 gas r computed over estimate-led years | Adjacent to N24 (excepted); the estimate-driven reading is a candidate, **not measured** |
| O6 London weather for every region | **Known**: W1_14 weather cells |
| O7 22 MWh electricity-only home said to heat otherwise | Known: INV_ELECTRIC_HEATING_VERDICT_AGREES_WITH_THE_HOMES_GAS_SUPPLY (uncheckable) |
| O8 closing read under the opening on an actual read | Presentation of the catch-up; known (`SEAT_FINDING_THE_PRINTED_REGISTER_FIX…`) |
| O10 SVT at or just over the GB-average cap | Regional spread, as in reads 8 and 9. The gate's four SVT rows are clean |
| O11, O13 the printed energy component under wholesale; the split rate | Known presentation: the printed component is not the all-in rate. The gate's floors read the all-in rate |
| O12 a single-rate renewal on a two-rate meter; a gap in 15–31 Jan 2023 | **Not graded** this turn |
| O15, O16 money before the first bill or on the switch date | Known, N23 (level DD collected before supply starts); not re-measured on this book |
| O17 "23 of 23 paid" beside GBP 657.06 owed | Recurring (ninth read O12/O13). INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE reads CLEAN on 1,139 here, so the reader's two slot cases are **not traced**. The row may be grading a different moment from the one the slot prints |
| O20, O21, O22 DD wording, credit held, DD under the bill then a write-off | Known families (level DD, the DD review), not re-measured |
| O23 GBP 1.43 debt left for 8.5 years | Known: the closed-account row's flag (89 standing debts) |
| O24 a debit "refunded as a credit" on the mover | **Reader miss.** GBP 36.31 = 58.36 + 43.95 − 66.00. Electricity was refunded GBP 7.64 and gas collected GBP 43.95, and both legs close at 0.00 |
| O25–O27, O30–O32 | Presentation, or the slot's own design (the debt slot is a final-bill debt by rule) |

## The seat-named checks, by eye and over every page

- **One meter serial per supply point:** 0 breaches on both fuels by script. By eye, only electricity is
  checkable, because the page prints no gas serial (O2). The DIRECTION row (four reads passed a serial shared by up to
  34 supply points) is **absent on this book**.
- **Same-month repetition:** see P4. The reader saw electricity's flatness unaided (O3).
- **Payment method on the bill's date:** see P5. Section B never states a method (O20), so the by-eye answer rests on
  inference.
- **A closed account's balance a year after its last bill:** see P6. The reader checked five closures and found one
  real case (O23, known) and one miss (O24).

## Reverse

Delete this file, the finding beside it, and the four blind rows from `DOMAIN_INVARIANTS.yaml`. No code is touched.
