**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# The fourth cold read, on the 209c3350ab book: legs two and three not met. The debt slot's example closes "Debt cleared" on a page that still shows £258.84 owed, and one new class: the committed tariff price is read from one bill (2026-10-29)

**What this is.** The reading the director's correctness ruling asks for
(`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`, "Exit
test"), on legs two and three. Item `the-fourth-cold-read-on-the-209c-book`. It is graded against
`docs/staging/records/SEAT_PREREGISTRATION_THE_FOURTH_COLD_READ_ON_THE_209C3350AB_BOOK_2026-10-29.md`
(landed `a546bab2e` before the reader was briefed).

**The book and the tools.**
- The book is `/var/tmp/fresh-run-out-209c3350ab`, exit clean.
- The pages and the cast were rebuilt at origin `1ba034b9c8` (after items 1 to 3) in the scratch
  tree `/var/tmp/fourth-read/tree`, using the third read's chain (`/var/tmp/fourth-read-scripts/`).
- The build gave 1,293 pages and 52,927 invoices.

| exit-test leg | verdict |
|---|---|
| 2. All eight slots filled validly or honestly empty | **NOT MET.** The debt slot's household is not a valid example. The reader graded it no, and the seat confirmed it on the ledger |
| 3. One cold read finds no new class | **NOT MET.** One new class (N9), confirmed in the page's code |

Leg one was not retaken in this item. **The stretch does not exit**, and the ruled order stays closed.

## Predictions against results

| # | prediction | result |
|---|---|---|
| P1 | 6 of 8 filled; ev and storage heating empty | **Held** |
| P2 | debt slot neither SYN-2016-356 nor PROS-2018-0222 | **Held** (SYN-2016-550) |
| P3 | 20–45 objections | **Held** (35) |
| P4 | at least one new class | **Held** (N9) |
| P5 | the one-rate fix graded an existing class | **Held** (the first read's O5) |
| P6 | PROS-2018-0222's move-out classed new | **Refuted.** The record holds the move (a final bill on 12 Aug 2019 on an estimated closing read, and moved out on 13 Aug, on both legs). The household view prints none of it. That is the first read's O21 (the page does not know supply ended), not a new class |
| P7 | leg two NOT MET only if a filled slot is invalid; leg three NOT MET | **Held** |

## Leg two: the eight slots

| slot | household | reader | seat |
|---|---|---|---|
| switch_in | PROS-2025-0022 | yes, caveat | Valid. "A full first quarter" is two months, the first read's O12 |
| renewal | SYN-2016-031 | partly | Valid by the rule, not as conduct. The fix is billed at the cap (O5), the notice falls on the expiry day (`INV_RENEWAL_NOTICE_42_TO_49_DAYS`), and the leaver's record stops. Same grade as the third read |
| estimate_trap | PROS-2017-0264 | yes | Valid. The "£45.43 back" copy is the first read's O15 |
| mover | PROS-2017-0351 | yes | Valid. Closing actual read, final bill, new occupant, refund on the 10th working day. The final bill's catch-up is unshown (N1, widened to catch-ups) |
| **debt** | **SYN-2016-550** | **no** | **Not valid.** See below |
| ev | empty | honest, mostly plain | Honest. 6 match, and each fails the 1,750–3,300 kWh EV checks |
| storage_heating | empty | honest, not plain | Honest. "96 match the rule" beside "no profile class 2 meter (96 of 96)" is the candidate filter, not the rule (the third read's O21 copy). The book's ToU bills on non-PC2 accounts are E4 / `2a2c5c5770` |
| shock_2022 | PROS-2019-0246 | yes | Valid. The EBSS credit is not netted from "£598.04 to pay" (N1) |

**Why the debt slot fails.** The story ends "15 Dec 2024 · Debt cleared". At that moment the page
prints "£258.84 owed", exactly the figure it printed at the 17 Jan 2024 miss. On the ledger:
- £71.31 is an electricity bill from 2 Nov 2018. It is unpaid and has been held flat for six years.
- £187.53 is the gas bill of 7 Jan 2024. It is unpaid through Dec 2024, while every later bill is
  paid on its due date.
- 71.31 + 187.53 = 258.84. So the desk closed a journey over two bills the ledger still holds.

This is the open desk-versus-ledger class:
`SEAT_FINDING_THE_DESK_DUNS_BILLS_THE_LEDGER_HELD_FOR_REVIEW_AND_BARS_A_WRITE_OFF_BEFORE_A_FINAL_BILLS_PAYMENT_2026-10-28.md`,
`SEAT_FINDING_THE_PAGE_PRINTS_MORE_OVERDUE_THAN_IT_SAYS_IS_OWED_ON_493_OF_752_HOUSEHOLDS_2026-10-28.md`,
and the first read's O27 (frozen balances never chased).

Two further faults sit on the same story:
- The decision log at the miss prints "14 Dec 2023: Payment plan offered … £378.05 overdue". That is
  a decision from an earlier, closed journey. `1ba034b9c8` accepted such decisions as history, but
  the page gives no journey boundary, so a reader sees a plan offered before the miss. That is the
  first read's O17, and `1ba034b9c8`'s "history" reading needs the page to say so.
- £633.17 "overdue" on 13 Feb counts two bills raised on 31 Jan and paid on 14 Feb. That is the
  overdue row's class.

Every part is an existing class. But, as with SYN-2016-356 on the third read, **the slot's validity
predicate passed an ending that its own page contradicts**. The predicate's missing check is that an
ending of "cleared" or "repaid" needs the page's owed figure at that moment to agree.

## Leg three: the read

**Method.** Ruling step 6, the third read's route:
- The scratch site was served from `/var/tmp/fourth-read/tree`, and every cast moment was rendered with Playwright.
- Six households were drawn with `random.Random(20261030).sample` from the picker's 752, less the three earlier reads' eighteen (734 left): SYN-2016-326, PROS-2018-0223, SYN-2016-352, PROS-2024-0321, SYN-2016-104 and OCC-2f64fad94fe7.
- PROS-2018-0222 was added seventh, by name.
- The packet is `/var/tmp/fourth-read/packet.txt` (3,185 lines, 128,195 characters), and the brief is `/var/tmp/fourth-read/brief.md`.
- A fresh Opus agent read only the packet, as a twenty-year GB retail-energy professional, and wrote its priors first. It answered two named questions.
- The return is in `/var/tmp/fourth-read/reader.jsonl`.
- The seat checked 32 key quotes against the packet, and all 32 are verbatim.

**Independence: false.** The reader is the same model family as the builder.

**The reader's verdict:** "The arithmetic is right line by line, but the account histories do not
hold together". It confirmed the 2021–22 cap and EPG rates to the penny, EBSS only on electricity
accounts live through the scheme, VAT at 5%, and the DESNZ gas and T&D factors.

### The new class

**N9. The committed tariff price is read from one bill.** Reader's O26, on OCC-2f64fad94fe7:
"Unit rate, all-in before VAT	0.00 p/kWh", with a 0.00p/0.00p/0.00p stack beside £0.2830/day.
- Confirmed in the code. `stagePriced` takes `d.invoices[0]`, a 0 kWh, no-rate stub (22–29 Feb 2024).
- It hits 44 of 1,293 pages and 25 of the picker's 752.
- No row grades the printed committed price, because the price rows grade bills.
- Finding: `docs/staging/SEAT_FINDING_THE_FOURTH_COLD_READ_FINDS_THE_COMMITTED_TARIFF_PRICE_READ_FROM_ONE_BILL_SO_A_ZERO_USE_FIRST_BILL_PRINTS_0P_2026-10-29.md`.
- Row: `INV_COMMITTED_PRICE_IS_THE_TARIFFS_PRICE_PER_FUEL_AT_A_DATE`, written blind and landed with this reading.

### Not confirmed, recorded

- **O14, use against occupancy.** "five plus person" on about 1,700 kWh a year (PROS-2017-0351, mostly estimated bills). In 2019, the book's resi electricity medians by occupancy are: one person 3,978, two 3,909, three to four 4,771, five plus 4,609 kWh. Those totals may mix fuels on dual-fuel pages. If the ordering is real, it is a world-fidelity question. No knowledge page establishes the GB gradient, so this is a GAP, not a confirmed class, and no row is written from a guess.
- **O28, EPG subsidy "25–35% high": refuted.** SYN-2016-352's support per kWh is about 17.0p (Q4 2022), about 29–33p (Q1 2023) and about 15–16p (Q2 2023). Those are the commons cap-minus-EPG gaps ex VAT (51.89/67.47/50.60 against 34.0p incl. VAT). The reader's estimate left out Apr–Jun 2023.

### Existing classes, by objection

- **The fix against the bills:** O1, O2, O3, and Q2 are the first read's O5. Q2's 132.0 £/MWh sits on PROS-2018-0222's timeline on both legs. It is tagged `electricity` on the gas leg, beside a gas step of 1.87p to 1.71p and an electricity step of 12.18p to 11.02p, so it matches neither fuel. The timeline is not rendered on the household view, so the reader graded its siblings: 152.0, 137.0, 145.0 and 257.0, all wrong except 257.0 as ex-VAT electricity.
- **Renewal:**
  - O4 is `INV_RENEWAL_NOTICE_42_TO_49_DAYS` and the renewal-notice finding.
  - O5 is the first read's O11 (an SVT "renewal"), and its repeated rows are the first read's O24 shape.
  - O17 is the first read's O9, and O18 is its O7.
  - O19 is the first read's O21 (the record stops).
- **Labels:** O6 is the first read's O9 and O11 (the garbled "Fixed at Tariff renewed").
- **Collections:**
  - O7 is the first read's O17, plus the history presentation above.
  - O8 is the desk-versus-ledger class (leg two).
  - O9 is the filed take-up GAP.
  - O11 is the overdue row, and its counters are N3.
- **Credits and catch-ups omitted from the page:**
  - O12 is N1.
  - O15 and O34 are N1, widened to catch-ups (the third read's O9 and O16).
  - O24 is N1 with the first read's O26. OCC-2f64fad94fe7's £174.72 is `total_deemed_gbp`, the deemed account's share, which the page's ledger line does not print, and stage 6 prints the collected figure as "billed".
- **Definitions with two homes:**
  - O25 is N2.
  - O29 is N5.
  - O23 is the first read's O28.
  - O26's "Meter Smart" beside "meter type is not on the supplier's record" is N8.
  - O26's "Supply point —" on a gas-only account is the first read's O32 family (the page reads electricity fields). Line 775 reads `mpan` only, and this account's MPRN is on record.
- **Copy:**
  - O10 (paths on the page) is as the second read recorded.
  - O13 is the first read's O23.
  - O16 is its O12.
  - O20 is its O15.
  - O21 is its O34.
  - O22 is its "flat monthly amount".
  - O33 is its O13, and the chart label is O21.
- **Book:**
  - O27 is the first read's O25 (margin).
  - O30 is ruling step 3 and E4.
  - O31 is the first read's O33.
  - O32 is the first read's O1 and O2.
  - O35 and Q1 are the first read's O21, as in P6.

## What follows

- N9 goes to its finding, and its row lands here. The fix and its red-on-origin test are drawable.
- The debt slot's predicate needs a fourth check: a "cleared" or "repaid" ending agrees with the page's owed figure at that moment. The cause is the open desk-versus-ledger finding, and the slot is not patched around it.
- The next exit attempt needs N9, N8 and N1 closed, the debt-slot check, a fresh run graded on leg one, and then a fifth read.
