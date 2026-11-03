**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# The sixth cold read, on the 85b044be54 book: leg one met in substance, legs two and three not met. Two new classes: a two-rate bill prints one summed read, and metered gas repeats last year's month to the decimal on a third of gas legs (2026-11-03)

**What this is.** This is the reading the correctness ruling asks for
(`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`, "Exit test").
- DIRECTION row: `the-sixth-cold-read`.
- It is graded against `docs/staging/records/SEAT_PREREGISTRATION_THE_SIXTH_COLD_READ_ON_THE_85B044BE54_BOOK_2026-11-03.md`.
  That file was landed as `13e071abb` before the reader was briefed. Origin moved under the promote, so the
  same bytes went to origin as `06cd9e330`, which is after the brief. The record of the prediction's timing is
  13e071abb.

**The book and the pages.**
- The book is `/var/tmp/fresh-run-out-85b044be54`: 1,293 accounts, 52,828 invoices and 752 households in the picker.
- The pages are `/var/tmp/fresh-grade-85b044be54/tree/site/`, built by its own grade chain. They were served on
  127.0.0.1:8793.
- 08f267b666 is newer, but it has no built Explore pages (see the pre-registration), so it was not read.

| exit-test leg | verdict |
|---|---|
| 1. The suite on a fresh run's full book: zero unexplained breaches | **Met in substance, not as the gate reads it.** The gate refused this book on 9 unexcepted breaches on 4 rows. Each is traced in `SEAT_RECORD_THE_85B044BE54_BOOK_GRADED_AGAINST_BOTH_PREREGISTRATIONS_2026-11-02.md` and fixed after the book (1b709ac0e9, 8cf2ecb744). The next book, 65bbdc6787, cleared all nine and carries one named, dated exception. N13 below is a breach the suite has no row for, so "zero unexplained" was true only of the rows that existed |
| 2. All eight slots filled validly or honestly empty | **NOT MET.** 7 of 8 are filled and EV is honestly empty, but the storage-heating slot's story does not show its feature (below) |
| 3. One cold read finds no new class | **NOT MET.** Two new classes, each confirmed on the record: N12 and N13 |

**The stretch does not exit.** The advisor file stays where it is.

## Predictions against results

| # | prediction | result |
|---|---|---|
| P1 | 7 of 8 filled; EV empty | **Held** |
| P2 | the reader grades the storage slot valid | **Refuted.** "Storage heating (PROS-2017-0233): no. Nothing printed shows two registers or a cheaper night rate." The seat agrees as shown (leg two) |
| P3 | 20–45 objections | **Held** (34) |
| P4 | at least one new class | **Held** (two: N12, N13) |
| P5 | N10 and N11 do not recur | **Split.** N10 (shared serial): **held**, not raised, and check (c) reads 0. N11 (gas as a kWh register): the class is closed on the pages, since every gas bill carries m³, CF and CV (check (a)). But the reader's O33 says "gas is never shown in m³ … so the gas kWh conversion can't be checked anywhere in the packet". That is true of the packet: the Billed stage shows a dual-fuel home's electricity bill, so only the 45 gas-only homes ever render a gas conversion. Recorded as N11's presentation tail, not a new class |
| P6 | check (a): every gas page has a volume and conversion | **Held.** 0 of 20,922 gas bills on 514 pages lack one. Rendered on three gas-only homes, e.g. OCC-158240531dd9: "Opening read 490.349 m³ … Gas used 15.551 m³ … Correction factor × 1.02264 … Calorific value (a fixed figure, not the period's published average) × 39.5 MJ/m³ … ÷ 3.6 MJ per kWh 174.5 kWh". The arithmetic checks |
| P7 | check (b): PC2 periods on one register | **Held.** 2 of 1,733 PC2 bills on 39 pages, the two known OCC stubs (OCC-23ee23cb44e4 2022-01-25, OCC-7e06d09fc108 2024-11-23, fixed in 1b709ac0e9). Rendered: PROS-2017-0233 bills "Usage (Day) 131.8 kWh × 13.13p" and "Usage (Night) 52.3 kWh × 3.37p". That check found N12 |
| P8 | check (c): serials on two or more supply points | **Held.** 0 of 928 serials |
| P9 | leg one met in substance, leg two MET, leg three NOT MET | **Leg two refuted** (storage slot). The others held |

## Leg two: the eight slots

| slot | household | reader | seat |
|---|---|---|---|
| switch_in | PROS-2025-0022 | yes | Valid. "Three months in" is two months: the first read's O12 |
| renewal | SYN-2016-031 | technically yes | Valid by rule, as on reads three to five. The notice falls on expiry, and the fix is billed at the cap (the first read's O5 and O7) |
| estimate_trap | PROS-2017-0264 | yes | Valid |
| mover | SYN-2016-368 | no | **Valid on the record.** The reader's O5 ("£43.78 owed is relabelled a refunded credit") is a misreading the page invites. The electricity ledger credits the full £67 Feb EBSS, applies £48.85 to the final bill and refunds the £20.87 left on 8 Mar. Gas £64.65 is paid on 12 Mar. Both fuels are at zero, so the account settles. Two page defects remain. The story dates "Credit refunded" 12 Mar, which is the gas payment, not the 8 Mar refund. And "less its £48.85 Energy Bills Support Scheme credit" prints only the part applied (O6). Both are the cross-fuel O32 family |
| debt | SYN-2016-210 | no | Valid by its rule and its four checks, as on the fifth read. O9, O10 and O11 are the first read's O17, the overdue class, and the "after the last rung" GAP. Under F11, recorded as generous, as before |
| ev | empty | honest, mostly plain | Honest. The reader notes a duplicated reason (1,750–3,300 kWh twice), which is copy |
| storage_heating | PROS-2017-0233 | no | **Not valid as shown.** The household is right on the record: every bill charges Day and Night (check (b)). But the slot's story is "Switched in" then an August first bill printed "£28.33 for 172 kWh, estimated", one figure and no register. A professional reading the example sees no two-rate billing. The rule is met and the feature is not shown. The fix is page-side: a winter moment with its Day and Night lines. The Billed stage would also print N12 |
| shock_2022 | PROS-2019-0246 | yes | Valid. The causal sentence (O13) is the first read's O23 |

## Leg three: the read

**Method.**
- The pre-registration's route, with the reader's tree made by `tools/blind_worktree.py` at
  `/var/tmp/blind/sixth-read-85b044be54`. `--check` was clean, and MANIFEST.json names only the book and the ruling.
- The brief carried the rendered packet (3,576 lines): the eight slots, every moment, and eight random households,
  OCC-924f5fe3f622, OCC-efcdf9ab970d, PROS-2016-0121, PROS-2017-0293, SYN-2016-498, SYN-2016-492, OCC-dbfb5a98d04d
  and OCC-6387bf64272a.
- The reader's trade was GB metering and settlement. The brief named no expected finding and asked no named
  question.
- The reader's transcript shows 9 tool calls, all `Read` of `BRIEF.md`. It opened nothing else.
- It declared one breach of its own protocol: it wrote its priors after its first 400-line chunk, which ran past
  the packet's start. Its priors are therefore not strictly blind to slot 1.
- **Independence: false.** The reader is the same model family as the builder.

**The reader's verdict.** "What can be trusted today is the unit-price arithmetic. The record of what each customer
contracted for and owed cannot." It confirmed:
- every Section B bill's arithmetic and 5% VAT;
- cap, EPG and EBSS rates;
- DESNZ gas factors, grid losses and the smart-data consent wording;
- MPAN formats, ledgers 3–6 to the penny, and the PROS-2019-0246 EPG bill (£598.16 against £598.04 printed).

### The two new classes

**N12. A two-rate bill prints one summed read that no register shows.**
- The seat found it in named check (b). The reader's O12 is the slot-level face of it.
- PROS-2017-0233, Billed stage: "Opening read 3,622.7 / Closing read 3,806.8" under the Day and Night lines.
  The record holds Day 1,978.5 → 2,110.3 and Night 1,644.2 → 1,696.5, and 3,622.7 is their sum.
- In the code, `gasReadRows` prints the bill-level `opening_read_kwh` for every electricity bill and never reads
  `inv.registers`. That affects 1,731 two-register bills on 39 PC2 pages.
- Finding: `docs/staging/SEAT_FINDING_THE_SIXTH_COLD_READ_FINDS_A_TWO_RATE_BILL_PRINTS_ONE_SUMMED_READ_NO_REGISTER_SHOWS_2026-11-03.md`.

**N13. Metered gas repeats last year's same month to the decimal on a third of gas legs** (reader's O23).
- The quote: "2021 5,979 kWh / 2022 5,979 kWh / 2023 5,979 kWh", with "62 bill(s), 0 on an estimated read".
- 1,635 of 4,413 gas month-pairs on actual or prepayment-meter reads repeat to 0.1 kWh, in every year and every
  month, winter included. 114 of 383 legs repeat on 10% or more of their pairs. Electricity repeats on 0–8%.
- OCC-098fe5fa8b46's volume register gives 724.3 / 1,060.0 / 1,408.6 / 1,439.2 kWh for Oct–Jan in both 2020-21 and 2021-22.
- This is W1_14's class (a gas premise reading the monthly normal), closed on 30 Sep for 91 premises and present
  here on a book of 514 gas legs. **I cannot yet say** whether the world's demand reads the normal (that fix
  regressed or never reached these legs) or the company bills an AQ-profiled estimate labelled actual. The blind
  row-writer named the second.
- Finding: `docs/staging/SEAT_FINDING_THE_SIXTH_COLD_READ_FINDS_METERED_GAS_USE_REPEATING_LAST_YEARS_MONTH_TO_THE_DECIMAL_ON_A_THIRD_OF_GAS_LEGS_2026-11-03.md`.
- It also bears on the fifth read's O17 (London weather for every region), left unmeasured. On these legs the
  page's r is computed against weather that did not drive the use at all.

Neither class was raised by the five earlier readers. N13 sat in every Section B weather table they read.

### Existing classes, by objection

- **Contract layer.**
  - O1 and O3 are the first read's O5 and O7 (a fix billed at the cap, one £/MWh for two fuels).
  - O2 is the same family.
  - O15 is the account's current tariff name printed over a fixed-term bill (SYN-2016-498's Oct 2017 bill is
    `fixed` under "Standard Variable"), the O5 family.
  - O4 is `INV_RENEWAL_NOTICE_42_TO_49_DAYS`. O28 and O29 are the first read's O9 and O11.
  - O16 is the fourth read's N9: the committed rate is read from a 1-day, 5.4 kWh stub (29 Feb 2020).
- **Mover.** O5, O6 and O7 are the cross-fuel O32 family (leg two). O8 (missed on DD with none returned) is the
  "missed" count the second read recorded.
- **Debt.** O9, O10 and O11 are as on the fifth read.
- **Ledgers and revenue.**
  - O19's four gaps equal `total_deemed_gbp` to the penny (£111.25, £94.05, £83.10, £53.94): the first read's
    O26 and the fourth read's O24.
  - O20 is the same cause. O22 is the first read's O25.
- **Reads.** O14 (registers from zero at switch-in) is the open opening-read finding (`…6436_OPENING_READS…`).
  O33 is N11's presentation tail (P5).
- **Copy and presentation.**
  - O13 is the first read's O23. O18 is the first read's O34. O21 is the O32 family and the fourth read's flat
    monthly amount.
  - O24's London series is the fifth read's O17. Its part-year r is copy.
  - O25 is the N8 / O32 family. O26 is the carbon-against-usage class (`INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL`).
  - O27 is the second read's paths. O30 is the second read's denominators. O31 is the first read's O12.
    O32 is the second read's percentage-point line.
- **Recorded, not classed.**
  - O17 (pre-cap price levels) is as on the fifth read.
  - O34 (a 2016 smart meter reading actual 97% of months after a change of supplier, where SMETS1 often went dumb
    until DCC enrolment) is a practitioner point the knowledge layer does not settle. It needs a K8 look at
    `docs/market_research/smart_meters_and_half_hourly_settlement_2026-10-25.md` before it is either.

## What follows

- N12 and N13 each have a BLOCKING finding and a blind row landed with this reading. The rows were written by an
  agent that read only the knowledge layer.
- N12 is a page fix, small and drawable, together with the storage slot's winter moment.
- N13's first measurement decides its side: for one repeating leg, did the world's demand repeat, or only the
  billed read?
- N12's "no register shows" is narrowed: true of a traditional Economy 7 meter. A SMETS2 meter has a total
  register, so the defect is the sum printed instead of the band reads.
- The next exit attempt needs both closed, a book that passes the gate, and a seventh read.
- The 08f267b666 or 65bbdc6787 pages, once built, are the candidates.
