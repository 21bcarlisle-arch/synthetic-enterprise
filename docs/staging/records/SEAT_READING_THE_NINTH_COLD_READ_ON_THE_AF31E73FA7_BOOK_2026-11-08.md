**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# The ninth cold read, on the af31e73fa7 book: three new classes (weekend direct debits, a level DD collected before supply starts, diagnostics over part years), and the reader found the level-DD dunning defect unaided (2026-11-08)

**What this is.** This is the reading the correctness ruling's step 6 asks for
(`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`, "Exit test"). It is the
lane-0 item `the-ninth-cold-read-on-the-next-fresh-book`, graded against
`records/SEAT_PREREGISTRATION_THE_NINTH_COLD_READ_ON_THE_AF31E73FA7_BOOK_2026-11-08.md`.

**Timing.**
- The preregistration was written and hashed at 00:42:48Z (sha256 `41168a8b…db824c`), before the packet rendered.
  It landed as 27a9d0c2c.
- The reader was briefed at 00:44:43Z.
- The gate grade and the named checks ran after the brief.

**The book and the pages.**
- The book is `run_output_af31e73fa7_20261107T225950Z.json`: 1,302 accounts, 53,873 invoices, 757 households in the
  picker.
- The pages were built by the publisher's customer-page chain in a scratch tree at origin 8b8a737211
  (`/var/tmp/ninth-read/tree/`, served on 127.0.0.1:8799). **They are not the live pages.**
- The item named "the book running from f248d5ffa". The run in flight was af31e73fa7, its descendant, which carries
  8b6316995, 12a470de7 and the level DD schedule, and not the level-DD dunning fix.

| exit-test leg | verdict |
|---|---|
| 1. The suite on a fresh run's full book: zero unexplained breaches | **NOT MET.** The publisher's gate refuses: 1,729 unexcepted breaches on INV_OVERDUE_WITHIN_PAGE_BALANCE (the level-DD dunning finding), and 7 rows excepted |
| 2. All eight slots filled validly or honestly empty | **NOT MET as shown.** 8 of 8 are filled. The debt slot prints the level-DD false overdue (O9). The reader also refused the mover and the 2022-shock slots, both on known classes (below) |
| 3. One cold read finds no new class | **NOT MET.** Three new classes: N22, N23 and N24 |

**The stretch does not exit.** The advisor file stays where it is.

## The control on the reader: the level-DD dunning defect, unaided

The brief said nothing about level direct debits, dunning, arrears or "overdue". **The reader found the defect's
symptom unaided, twice, and the second half of it as well:**
- **O21.** PROS-2020-0104: "14 May 2025 payment failed £0.00", then "21 May 2025 notice" with the balance at
  "£-379.49". The reader called "a dunning notice to a customer £379 in credit" unsupportable. The gate breaches it on
  2025-05-15 (missed_payment, £60.74 against a bound of £0) and 2025-05-21 (reminder). PROS-2020-0104 is on a level DD.
- **O9.** SYN-2016-217, the debt slot: "£16.10 owed" with "GBP85.52 overdue". The gate breaches 2023-07 to 2023-12 and
  2024-06 to 2024-07 on this household, which is on a level DD.
- **O12 and O13**, the payment record against the balance ("0 of 0 bills paid" beside "£41.73 owed"; "81 of 83 bills
  paid" beside "£2,041.37 owed"). These are the finding's part 2, the row the publisher's gate cannot grade (below).

It named the symptom, not the mechanism. It never said "level". So this read is not blind to that class, and its
silence elsewhere is worth a little more than a reader's silence that had not passed the control.

## Predictions against results

| # | prediction | result |
|---|---|---|
| P1 | Both page rows CHECKED > 0 through the publisher's path, and no code change needed | **Split.** The loaders were right: the publisher's path does build `cast_tariffs` and `payment_tallies`, and MISSED_BILL read **28 checked** with no change. TARIFF read **UNREACHED, 0 checked**, because no page bill carried a `tariff_name`. The generator hunk that writes one had been stranded on the shared tree since 5 Nov. With it applied to the scratch pages, TARIFF reads **47,504 checked**. The generator lands with this reading. The page hunk and its door test wait for a publish to rebuild the live pages: the landing gate refused them, rightly, because the committed pages would all print "Not recorded on this bill" until then |
| P2 | TARIFF 0 breaches; MISSED_BILL ≥1 breach on level-DD households | TARIFF **held** (0 breached, 1,053 mid-bill flags). MISSED_BILL **refuted**: 0 breached, 12 flags ("fewer missed than unsettled" on the cast) |
| P3 | OVERDUE 1,000–2,500; PAYMENT_RECORD 20–80; the gate refuses | OVERDUE **held**: 1,729 on 177 households. 165 of them match a `level_dd_collections` key, and I have not traced the other 12. PAYMENT_RECORD **not gradeable**: NOT_IN_EXPORT on the publisher's path (finding below). The gate refuses: **held** |
| P4 | The reader finds the level-DD dunning unaided (p ≈ 0.6) | **Held** (O21, O9) |
| P5 | 25–45 objections | **Held** (28) |
| P6 | One to three new classes | **Held** (three) |
| P7 | 0 serials on two supply numbers; 0 default bills under the wholesale floor; default at the cap from 2019 | **Held** on the first two. The third, as worded: 9,019 of 23,111 capped default bills sit over the median-region cap, **none by more than 10%**. That is regional spread, as on the eighth read. I did not compute the median ratio |
| P8 | Electricity same-month change under 3%; gas 8–18% | **Held**: electricity 0.7% (59.7% of 5,333 pairs under 1%; 450 repeats to 0.1 kWh), gas 13.0% (17 repeats) |
| P9 | Named a contribution; 7–12% book-wide | **Held**: "Contribution after cost to serve", with a not-profit note. 9.31% on 1,300 resi accounts (£294,889 on £3,167,075 revenue, cost to serve £449,018). N21 graded 9.30% on fd91027799 |
| P10 | No prepayment statement paid another way, except the excepted class | **Held**: 0. 11 prepayment-paid bills on C6 are INV_PPM_NOT_CREDIT_BILLED's excepted class |
| P11 | Leg one NOT MET, leg two MET, leg three NOT MET | **Leg two refuted** (the debt slot). The others held |

## A correction to my own build, beside the claim

**My first gate grade read INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL at 4,031. That was my scratch tree, not the book.**
- The page chain I reused (`/var/tmp/fourth-read-scripts/pages.py`) regenerates the customer pages and the cast, but
  not `explore_carbon.json` or `explore_hh_days.json`.
- The publisher regenerates both before its gate (`process_run_complete`, "Generating explore carbon layer").
- Regenerated, the row is clean.
- **The packet was rendered before the regeneration.** So the reader's **O2** (carbon kWh against "Used") is that
  same artefact. Regenerated, SYN-2016-206's 2024 electricity reads 5,539.2 kWh on both panels.
- The fourth to eighth reads used the same chain. **I cannot now say** that none of their carbon objections was this
  artefact. The eighth's O24 cited a row count (14) that its own grade produced from a rebuilt panel, so that one
  was not.
- The next read's chain must run `generate_explore_hh_day` and `generate_explore_carbon` after `explore_cast`.

**A shared-tree slip, caught before it landed.**
- The stranded finding had a root copy, older and untracked, and a newer copy already in `done/` on origin. My `mv`
  overwrote the done copy with the root one.
- The landing refused on the path. I restored the done copy from origin and appended my section.
- The untracked root copy is gone from the shared tree. It was a stale duplicate of a done finding, and the doorbell
  listed it as unprocessed staging. Its bytes are at
  `/var/tmp/ninth-read/SEAT_FINDING_TWO_HOUSEHOLD_PAGE_ROWS_..._2026-11-07.md.orig`.

## Leg two: the eight slots

| slot | household | reader | seat |
|---|---|---|---|
| switch_in | PROS-2025-0022 | yes, with caveats | Valid. O12 is the level-DD payment record plus N23 |
| renewal | SYN-2016-592 | yes as its rule | Valid by its rule. O13's balance against its record is level-DD part 2. Its welcome credit is N23 |
| estimate_trap | PROS-2017-0264 | yes | Valid |
| mover | SYN-2016-527 | no | **Valid on the move.** O7 (a debt "refunded") is the closed-balance class, filed. O8 (EBSS "sized to the bill") is the sixth read's presentation class: the £66 covers the £58.36 bill and the rest is a credit |
| debt | SYN-2016-217 | no | **Not valid as shown**: O9 is the level-DD false overdue. O10 is the open cleared-while-owed class |
| ev | PROS-2017-0183 | yes in substance | Valid. "Your first electricity bill is ready" on a 2017 account is presentation |
| storage_heating | PROS-2020-0189 | yes | Valid |
| shock_2022 | PROS-2019-0246 | no | Valid by its rule. O22's 2,856 kWh is INV_ANNUAL_USE's flag class. The narrative line is the first read's O23. "Owed" beside "cleared" is cleared-while-owed |

## Leg three: the read

**Method.**
- The reader's tree is `/var/tmp/blind/ninth-read-af31e73fa7`, made by `tools/blind_worktree.py` and checked clean
  with `--check`. Its book stand-in (`/var/tmp/ninth-read/book/`) holds the run output and the ledger, so the leak
  check reads their names. The sim-runner's book has no pickles and no `DONE.json`.
- The packet (4,096 lines) holds every moment of the eight slots and all six stages of ten random households. The
  draw is in the preregistration.
- **The trade, new to these reads:** a revenue-assurance and billing-operations auditor.
- The brief put the priors-first rule in its first lines. The reader wrote its priors before its second read call:
  the order held this time.
- The reader made 10 tool calls, all reads of `BRIEF.md`.
- **Independence: false.** The reader is the same model family as the builder.

**The reader's verdict.** "The per-bill pricing and VAT arithmetic are sound and track the cap, EPG and EBSS closely.
But the account layer fails the basic tests."

### The three new classes

- **N22. Direct debits collected on weekends and Christmas Day** (O18).
  - 10,546 of 36,096 DD collections (29.2%) fall on a non-working day, on 922 accounts. That is 2/7 plus bank
    holidays, so no working-day calendar is applied.
  - Finding: `docs/staging/SEAT_FINDING_THE_NINTH_COLD_READ_FINDS_DIRECT_DEBITS_COLLECTED_ON_WEEKENDS_AND_CHRISTMAS_DAY_2026-11-08.md`.
- **N23. A level DD collected before the supply starts** (O11).
  - 336 accounts, all on a level DD. SYN-2016-592's first £131.07 is collected 4 Dec 2016, against a supply start of
    14 Dec.
  - It is new with N20's schedule (8178e24218), so no earlier book could show it.
  - Finding: `docs/staging/SEAT_FINDING_THE_NINTH_COLD_READ_FINDS_A_LEVEL_DIRECT_DEBIT_COLLECTED_BEFORE_THE_SUPPLY_STARTS_ON_336_ACCOUNTS_2026-11-08.md`.
- **N24. Household diagnostics computed over part years** (O4, O24).
  - "Gas against the weather" correlates calendar-year gas with degree days and includes part years: 297 of 304 gas
    pages. 259 print a negative r, and the page explains the swing as "something other than temperature".
  - The winter/summer heating verdict is printed from a 7-day summer stub.
  - Finding: `docs/staging/SEAT_FINDING_THE_NINTH_COLD_READ_FINDS_HOUSEHOLD_DIAGNOSTICS_COMPUTED_OVER_PART_YEARS_SO_GAS_RUNS_AGAINST_THE_WEATHER_ON_MOST_PAGES_2026-11-08.md`.
  - It corrects the eighth read's attribution of an r near 0 to the London series.

**Blind rows** for N22–N24 were written by a fresh agent from the knowledge pages and the published scheme rules
alone (`/var/tmp/ninth-read/blind_rows_N22_N24.yaml`). The agent wrote nine rows: three for N22 (dated on a Bacs processing day; the next-processing-day roll; Monday's share as the
roll predicts), two for N23 (the first level DD no earlier than supply start; opening-day credit), and four for N24 (full
supplied years only; r printed only with its interval; a full winter and summer for the ratio; the heating verdict against
the gas supply). Each cites its source and its GAPs. They land in `docs/design/DOMAIN_INVARIANTS.yaml` as
`checkable: false`, with their evaluators owed. The runner reads them UNCHECKABLE, which does not move the gate.

### Two more findings from confirmed objections

- **Closed accounts still holding balances years after their last bill** (O20, O7). This is the 25 Oct refund-log
  class, which is in `done/` and recurs on this book.
  - 213 accounts with no bill for a year or more hold a credit (£15,694 in all).
  - 208 hold a debt (£21,554).
  - Finding: `docs/staging/SEAT_FINDING_THE_NINTH_COLD_READ_FINDS_CLOSED_ACCOUNTS_STILL_HOLDING_CREDIT_AND_DEBT_YEARS_AFTER_THEIR_LAST_BILL_2026-11-08.md`.
  - Its blind row is owed.
- **The publisher's gate cannot grade INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE** (O12, O13). It reads
  NOT_IN_EXPORT, because `load_printed` never builds `payment_record`.
  - Finding: `docs/staging/SEAT_FINDING_THE_PUBLISHERS_GATE_CANNOT_GRADE_THE_PAYMENT_RECORD_ROW_SO_THE_LEVEL_DD_PAYMENT_RECORD_DEFECT_IS_INVISIBLE_TO_IT_2026-11-08.md`.

### Every other objection, by known class

| objection | disposition |
|---|---|
| O1 opening reads from zero, and new occupants not continuing the read | Known: opening reads from zero (eighth O22). 1,302 of 1,302 first reads are 0. The occupant case is the same class |
| O2 carbon kWh against use | **My scratch artefact** (above). Not on the book |
| O3 use repeats year on year | N17, the world side, under its dated exception. Gas repeats 17 (INV_GAS_MONTHLY_USE…) |
| O5, O6, O27 (revenue against billed) deemed-account credits; ledgers that do not roll | Known: ledger gaps equal to deemed charges (eighth O25, O31) |
| O8 EBSS "sized to the bill" | Known presentation (sixth read, the mover's credit) |
| O9, O21 overdue while in credit or over the balance | **The level-DD dunning finding** (the control) |
| O10, O22 (cleared beside owed) | Known: cleared-while-owed |
| O12, O13 payment record against the balance | The level-DD finding, part 2. The publisher-gate finding above |
| O13 churn belief at 100% on an account in debt | Not confirmed; a belief-model question, not filed |
| O14 a low estimate after a high correction; the credit shown ex-VAT | Known: estimates; the catch-up VAT post-publish reds |
| O15 E7 above the flat cap | N19 (closed): graded on the multi-register cap. The reader allowed it may be lawful |
| O16 a night rate drifting by 0.01p | Not confirmed (display rounding, untraced); not filed |
| O17 SVT 5.3p against 9.4p in Sep 2017 | Known: the energy component printed as the unit rate (eighth O29), pre-cap and regional |
| O19 flat-DD text against variable-DD ledgers | Presentation. About 21% of DD collections equal the bill by N20's design. SYN-2016-206's irregular payments are untraced |
| O22 2,856 kWh for one person; "use did not explain" | Known: INV_ANNUAL_USE flag class; first read O23 |
| O23 low use for the household size | Not confirmed (as eighth O17) |
| O25 labels: "first bill", duplicated renewal rows, pp against %, 757 against 707 | Presentation. The 707 is probably a stale scratch file, like O2. Not filed |
| O26 a one-day first bill | Known (first read) |
| O27 cost to serve per fuel account | N21 (disposed): the cap's sourced OC + PAAC + SMNCC per fuel account |
| O28 tariff history gaps | Known: contract layer (roll on the 1st; earlier O7, O13) |

### The five named checks, seat-run over every page (1,302 files)

- **One meter serial per supply point.** 0 accounts with a second serial, 0 serials on two supply numbers, 0 serial
  changes, 0 reads that fail to continue. Every account's first read is 0 (known).
- **Same-month repeats on both fuels.**
  - Electricity: median change 0.7%; 59.7% of 5,333 actual pairs move less than 1%; 450 repeat to 0.1 kWh (N17).
  - Gas: 13.0%; 17 repeats of 4,257.
- **The payment method on each bill's date.**
  - No prepayment statement is paid another way, and no bill is paid by two methods.
  - 45 accounts change method. One (SYN-2016-538) resumes DD after paying on receipt.
  - The date a DD lands is N22.
- **The unit rate between wholesale and cap, per fuel and year.**
  - The median SVT all-in ex-VAT rate by year tracks the cap: electricity 17.5p (2019), 27.0p (2022), 46.8p (2023);
    gas 3.9p, 7.0p, 12.0p.
  - The 2017 gas SVT is 3.81p, so N18 holds.
  - No default bill is under the wholesale floor, and none is more than 10% over the median-region cap.
  - **48 default bills on 46 households sit under the cheapest region's pass-through cost.** Examples: PROS-2017-0183,
    Jun 2024, all-in 18.91p against a cap of 23.35p; PROS-2017-0237, Aug 2020, 12.70p against 16.77p. **I cannot yet
    say** whether they are mixed-term bills like N19's class A. They are untraced and carried to the next read's check (a).
- **The contribution label after cost to serve.** It is labelled a contribution, not profit, and reads 9.31% book-wide.

**What the trade change bought.** A billing-operations auditor reconciled cash against balance. It passed the
control, and it found the two cash-calendar classes (N22, N23) that seven price, meter and collections reads never
raised. Its pricing pass agreed with the eighth read's.

Scratch: `/var/tmp/ninth-read/` (`packet.txt`, `BRIEF.md`, `draw.json`, `checks.json`, `gate*.txt`, `scripts/`).

## Reverse

Revert the commit that carries this record. It holds the five findings, the nine blind rows, the generator hunk and the
stranded finding's done section.
