**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# The eighth cold read, on the b3ce2a4e73 book: leg one not met, leg two not met, leg three not met. Five new classes: electricity use that barely moves year to year, a 2017 gas SVT 30% under its neighbours, false cap breaches on two-register homes, a direct debit that is the bill, and a margin several times the library's (2026-11-04)

**What this is.** This is the reading the correctness ruling asks for
(`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`, "Exit test"). It is the
lane-0 item `the-eighth-cold-read`, graded against
`records/SEAT_PREREGISTRATION_THE_EIGHTH_COLD_READ_ON_THE_B3CE2A4E73_BOOK_2026-11-04.md`.

**Timing.**
- The preregistration's bytes (sha256 `7f749df2…c3f5f5`) were written and hashed before the brief.
- The reader was briefed at 12:06:10Z.
- The prereg landed as baf83d15d.

**The book and the pages.**
- The book is b3ce2a4e73: 1,291 accounts, 52,715 invoices, 751 households in the picker.
- The pages are focus item 1's unpublished build at `/var/tmp/fresh-grade-b3ce2a4e73/tree/site/`, served on
  127.0.0.1:8798. They are not the live pages.

| exit-test leg | verdict |
|---|---|
| 1. The suite on a fresh run's full book: zero unexplained breaches | **NOT MET.** 203 unexcepted breaches on 7 rows (focus item 1's record). This read adds no row. Five of its classes have none yet |
| 2. All eight slots filled validly or honestly empty | **NOT MET as shown.** 7 of 8 are filled and EV is honestly empty. The renewal and storage slots print a cap breach that is not one (N19) |
| 3. One cold read finds no new class | **NOT MET.** Five new classes, each confirmed on the record: N17–N21 |

**The stretch does not exit.** The advisor file stays where it is.

## Predictions against results

| # | prediction | result |
|---|---|---|
| P1 | 7 of 8 filled; EV empty | **Held** |
| P2 | the reader grades 6 or 7 of 7 filled slots valid | **Refuted.** 5 yes, debt "partly", mover "no" |
| P3 | 20–45 objections | **Held** (38) |
| P4 | at least one new class | **Held** (five) |
| P5 | at least two price-level objections, all known | **Split.** Several were raised, but O1 and O2 are a new class (N19). O29 is the known E7 line. O33 and O34 are N16 on a second surface |
| P6 | check (a): 0 default bills under the wholesale floor | **Held** (0 of 22,761 cap-era and all pre-cap default bills). My first pass said 2,560. I had added the EPG support twice: `epg_discount_gbp` (ex-VAT) and `epg_support_gbp` (the same sum, inc-VAT) |
| P7 | check (a): default bills over the median-region cap, non-zero, on ≤ 22 households | **Refuted.** 8,820 bills on 482 households sit over the median-region figure. None is more than 10% over, and the cap-era median is 1.000 of the cap, so that is regional spread. The 22 `above_cap` households are N19's false breaches, not this |
| P8 | check (a): 0 standing charges over the cap | **Refuted as worded.** 10 bills on 10 households sit over the median-region figure, each by under 0.5%. That is regional; none is a breach |
| P9 | check (b): 0 serials carrying two supply numbers | **Held** |
| P10 | check (b): about 10 gas actual-read pairs repeating to 0.1 kWh | **Held** (14 of 4,107). N13's fix holds |
| P11 | check (c): bills settled by DD after the mandate ended, non-zero | **Not gradeable on the pages.** They carry no mandate event. 45 accounts change method; 1 (SYN-2016-538) resumes DD after paying on receipt |
| P12 | leg one NOT MET, leg two MET, leg three NOT MET | **Leg two refuted** (N19 on two slots). The others held |

## Leg two: the eight slots

| slot | household | reader | seat |
|---|---|---|---|
| switch_in | PROS-2025-0022 | yes, with caveats | Valid. "Three months in" is two (first read O12). The cast's bill line omits the standing charge (O20, presentation; it falls under the E7 finding's owed SLC 31A bill form) |
| renewal | SYN-2016-592 | yes, as its rule | **Not valid as shown.** It meets its rule, but every moment prints "breaks a published rule 53 times", which is false (N19). "7 missed, 0 returned" counts credit-settled bills (N15 on the page) |
| estimate_trap | PROS-2017-0264 | technically yes | Valid. O16, the opening read, is the known opening-read class |
| mover | SYN-2016-368 | no | **Valid on the record**, as on the sixth and seventh reads. O9 and O10 are the EBSS credit misreading those reads traced. O11, the refund on day 11, is the O32 family |
| debt | SYN-2016-217 | partly | Valid by its rule. O14 ("clears with no payment") is the open cleared-while-owed finding (3 households on this book). O15 is `INV_OVERDUE_WITHIN_PAGE_BALANCE` (128) |
| ev | empty | honest, fairly plain | Honest |
| storage_heating | PROS-2020-0189 | yes | **Not valid as shown.** The heating predicate holds (night share 82–85% in winter). But it prints a June 2022 cap breach that is N19's |
| shock_2022 | PROS-2019-0246 | yes | Valid. O19's causal line is the first read's O23. O18 (2,856 kWh in a month, one person) is `INV_ANNUAL_USE_ELEC_ACCOUNT`'s flag class |

## Leg three: the read

**Method.**
- The reader's tree is `/var/tmp/blind/eighth-read-b3ce2a4e73`. It was built from `tools/blind_worktree.py`'s
  `COLD_READER_SITE` and checked clean by `--check`. The leak check ran against the grade's `docs/reports/`, because
  there is no finished-book directory.
- The packet (2,868 lines) holds every moment of the eight slots and five random households:
  OCC-eb72725807da, PROS-2016-0187, SYN-2016-531, OCC-a8253b022c52 and SYN-2016-185.
- **The trade, new to these reads:** an Ofgem price-cap and tariff analyst.
- The brief carried the three seat-named questions and named no expected finding.
- The reader made 10 tool calls, all reads of `BRIEF.md`.
- **It wrote its priors after its first chunk ran past "THE PACKET BEGINS"** and said so. The priors are domain
  knowledge, not packet-shaped, but the order rule was broken. The next brief should place the line inside the first
  30 lines.
- **Independence: false.** The reader is the same model family as the builder.

**The reader's verdict.** "The price layer looks calibrated. The meter, payment and accounting layers do not."
- It confirmed the cap levels on the debt and 2022-shock slots to the pound, and the EPG unit and standing charge.
- It also confirmed the EBSS schedule, 5% VAT, the Section B bill arithmetic, the DESNZ carbon factors and the
  storage night share.

### The five new classes

**N17. Metered electricity barely moves from one year to the next** (named check (b), and the reader's O23 without
being told).
- The median same-month change is **1.1%**, against NEED's 14.7% for a whole year.
- 48.6% of 5,179 actual and prepayment pairs move less than 1%, and 352 repeat to 0.1 kWh.
- Gas, fixed by N13, is at 12.9% and credible.
- N13 had scoped electricity out ("the effect is on the gas leg").
- Finding: `docs/staging/SEAT_FINDING_THE_EIGHTH_COLD_READ_FINDS_METERED_ELECTRICITY_USE_BARELY_MOVES_FROM_ONE_YEAR_TO_THE_NEXT_2026-11-04.md`.

**N18. Every 2017 gas SVT bill is 2.67p all-in, against 3.81p in 2016 and 3.57p in 2018** (named check (a), seat
only).
- 2.67p is under the cheapest region's 2017 pass-through cost.
- The default dual-fuel unit cost falls 16% while the published default bill rose 4%.
- `INV_UNIT_RATE_SVT_GAS_PRE_CAP` reads only the energy line against DF+CM, so it is blind to this.
- Finding: `docs/staging/SEAT_FINDING_THE_EIGHTH_COLD_READ_FINDS_THE_2017_GAS_STANDARD_VARIABLE_RATE_THIRTY_PERCENT_UNDER_2016_AND_2018_2026-11-04.md`.

**N19. Two-register default bills are graded against the single-rate cap** (O1, O2).
- `default_tariff_invoice_excess_p_per_kwh` takes the single-rate ceiling at the household's own day/night mix.
- At SLC 28AD.31's 58/42 split, SYN-2016-592's Feb 2019 bill is 14.64p against a 14.63p multi-register cap.
- All 626 recorded excesses are profile class 2 bills.
- Finding: `docs/staging/SEAT_FINDING_THE_EIGHTH_COLD_READ_FINDS_TWO_REGISTER_DEFAULT_BILLS_GRADED_AGAINST_THE_SINGLE_RATE_CAP_SO_THE_PAGE_PRINTS_FALSE_CAP_BREACHES_2026-11-04.md`.

**N20. The direct debit is the bill** (O30).
- 33,992 of 35,122 DD payments (96.8%) equal the invoice they settle.
- At least about 72% of GB DD households pay a level amount.
- The DD balance book models a level DD that the ledger does not collect.
- Finding: `docs/staging/SEAT_FINDING_THE_EIGHTH_COLD_READ_FINDS_THE_LEDGER_COLLECTS_NINETY_SEVEN_PERCENT_OF_DIRECT_DEBITS_AT_EXACTLY_THE_BILL_2026-11-04.md`.

**N21. The pages publish a 14.5% margin after cost to serve** (O35), against the library's own 2–5% and an EBIT
allowance of about 2%.
- I cannot yet say whether a cost line is missing or the definition differs.
- Finding: `docs/staging/SEAT_FINDING_THE_EIGHTH_COLD_READ_FINDS_THE_PAGES_PUBLISH_A_FOURTEEN_PERCENT_MARGIN_AFTER_COST_TO_SERVE_AGAINST_THE_LIBRARYS_TWO_TO_FIVE_2026-11-04.md`.

**Two fixed classes on a second surface** (O4, O33, O34): the household page's tariff name (N16) and its bill
tally (N15). Finding: `docs/staging/SEAT_FINDING_THE_EIGHTH_COLD_READ_FINDS_N15_AND_N16_SURVIVE_ON_THE_SIX_STAGE_HOUSEHOLD_PAGE_2026-11-04.md`.

### The other objections, by known class

- **Opening reads from zero:** O22. 1,291 of 1,291 first bills open at 0.
- **Carbon against usage:** O24 (`INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL`, 14).
- **Ledger gaps equal to deemed charges:** O25 and O31.
- **EBSS void window:** O26 (excepted rows).
- **Energy component printed as the unit rate:** O29 (the E7 1.5p finding, which covers single-rate bills).
  Named check (a) puts the printed energy line under the wholesale floor on 7,502 single-register bills, as low as
  0.30p for gas.
- **Contract layer:** O7, O13 (roll on the 1st), O27.
- **Instrument presentation:** O3, O8.
- **Copy and denominators:** O21, O37.
- **The weather method:** O23's gas half, with r near 0 against degree days on two accounts. That is the London
  series class, not N13: gas month-pairs move 12.9%.
- **Not confirmed, and not filed:**
  - O5: a £12.7 gap on a catch-up credit. It is a candidate for the open catch-up VAT post-publish reds.
  - O6: an estimate after an actual read, on a storage home in November.
  - O17: low use.
  - O28: standing charges within regional spread, as P8.
  - O32: booked wholesale (folded into N21).
  - O36: a 2020 night rate of 6.89p.
  - O38: a prepayment meter labelled "Traditional".

### The three named checks, seat-run over every page (1,292 files)

- **(a) Price between wholesale and cap.**
  - Default tariffs sit at the cap: cap-era median 1.000 of the median-region level, never more than 1.8% over.
    Through 2022 gas SVT is never under 0.95 of the cap, so the director's original crisis-gas concern does not
    recur on this book.
  - No default bill sits under the wholesale floor.
  - Pre-cap gas SVT is N18.
  - Fixed rates graded at their strike window: 510 of 1,941 sit under the lowest-region pass-through floor and 3
    under DF+CM. All 3 are Jan–Mar 2023 strikes against a cap window still carrying summer 2022 prices. A
    two-sided fixed test needs the forward at the strike, which the pages do not carry: **GAP**, not a finding.
- **(b) What a meter is.**
  - One serial and one MPAN or MPRN per account and fuel, and no serial changes.
  - Reads break once (SYN-2016-604g, a gate breach already). Every account's first read is 0.
  - Electricity is N17.
- **(c) Payment method on the bill's date.**
  - On the cast, the printed "How you pay" agrees with the ledger's method on 25 of 25 moments.
  - Book-wide, no prepayment statement is paid another way. C6's 11 prepayment-paid bills are the excepted
    `INV_PPM_NOT_CREDIT_BILLED`.
  - The DD form itself is N20.

**What the trade change bought.** None of the seven earlier readers raised N19, N20 or N21. A pricing reader read
the price layer as right to the pound and still found three classes outside it. The named checks carried N17 and
N18, which no trade owns.

Scratch: `/var/tmp/eighth-read/` (`packet.txt`, `BRIEF.md`, `checks.json`, `draw.json`, `scripts/`).

## Reverse

Delete this record and the six findings it names. Nothing outside `docs/staging/` was touched.
