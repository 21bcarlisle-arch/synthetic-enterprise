**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# The third cold read, on the fresh 129e7de698 book: all three legs not met. The overdue row is over its ceiling, the debt slot's example is invalid, and one new class: the meter type is printed from two records (2026-10-28)

**What this is.** The reading the director's correctness ruling asks for
(`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`, "Exit test").
It is graded against
`records/SEAT_PREREGISTRATION_THE_THIRD_COLD_READ_ON_THE_129E7DE698_BOOK_2026-10-28.md`, whose results
section holds the row-by-row grade beside each prediction. Item `the-third-cold-read`.

**The book.** `fresh-run-129e7de698`, exit clean, 4,255 s. It was not relaunched.
`fresh-run-37abacdf42` was not touched. The book predates `c4738b64c`, `37abacdf4` and `558ee4624`.
**None of the 35 objections below traces to a cause one of those three fixed.** The nearest is the
printed opening register (`37abacdf42`, finding E3), and no objection rests on it.

| exit-test leg | verdict, on the stricter reading |
|---|---|
| 1. Zero unexplained breaches on a fresh run's full book | **NOT MET.** The gate refuses: INV_OVERDUE_WITHIN_PAGE_BALANCE is 9,510, over its 9,455 ceiling. Separately, all ten excepted rows name an open defect, so none counts as explained |
| 2. All eight slots filled validly or honestly empty | **NOT MET.** The debt-journey slot's household is not a valid example, and the seat confirmed it on the record |
| 3. One cold read finds no new class | **NOT MET.** One new class (N8), confirmed in the page's code |

**The stretch does not exit.** The ruled order stays closed.

## Leg one

Graded at 129e7de698 over 1,293 accounts (`/var/tmp/third-read/grade.txt`). Of 22 row predictions, 21 held.
INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS (249 against 250–335) was refuted, by one.

The predicted mover, INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER, fell from 11 to 1. That is `6bdf089925` working.

**The one row over its ceiling** is INV_OVERDUE_WITHIN_PAGE_BALANCE: +55 net (+127/−72 steps) on 21
households.
- 20 of the 21 have re-estimated bills.
- The desk's journeys moved on 530 legs, but the bills moved on only 164.
- So **I cannot yet say** the whole rise is the estimate fix.

**The stricter reading.** The ten excepted rows each name an open defect: "until …" a fix or a run.
By the item's rule, none of them is explained. Leg one would therefore be NOT MET even if the
ceiling held. The second reading graded this leg MET on "cause named"; this one does not.

## Leg two

The cast was rebuilt at origin a068e5a865's tools: 7 filled, 1 empty (storage heating), as predicted.
The fills are the same households as the 1691ec0ecd cast, with the mover (SYN-2016-417) filled for the first time.

| slot | reader | seat's check |
|---|---|---|
| switch_in PROS-2025-0022 | valid | the payment record "0 of 0 bills paid" beside £196.41 to pay and four bills is N3 (counters), existing |
| renewal SYN-2016-031 | rule yes, conduct no | "Fixed at 152.0 £/MWh from 25 Jan 2019" on bills priced at the cap is the first read's O5, existing |
| estimate_trap PROS-2017-0264 | valid | the "£45.43 credited" vs "£33.68 credit" pair is the first read's O15, still open |
| mover SYN-2016-417 | mostly valid | see O9 and O10 below |
| **debt SYN-2016-356** | **not valid** | **Confirmed.** The page dates "First overdue notice" (25 Nov 2016) before the slot's own "Missed a payment" moment (15 Dec). At that moment it prints "4 of 4 bills paid, 0 returned, 0 missed". The slot ranks on depth, but the page shows no DCA placement although the ledger's `arrears_history` holds one (PLACED_WITH_DCA, 30 Sep 2018). The page and the desk are two ladders on two write-off dates (the overdue finding's open cause). Every part is an existing class, but **together they make the slot's chosen story one the record contradicts**, and the slot's validity predicate passed it |
| ev SYN-2016-050 | valid | the garbled "Fixed at Tariff renewed from 8 Feb 2019" is the first read's O9/O11 |
| storage_heating (empty) | honest, not plain | "95 match the rule" while 95 of 95 lack the meter the rule names is copy: the slot's candidate filter is not its rule. The first read noted the internal account-id check too |
| shock_2022 PROS-2019-0246 | valid | the EBSS credit announced but not netted from "£598.04 owed" is N1, still open |

## Leg three: the read

**Method: ruling step 6, the second read's route.**
- The scratch site was served from `/var/tmp/third-read/tree` and every cast moment rendered.
- Six households were drawn with `random.Random(20261029).sample` from the picker's 752, less the first and second reads' twelve (740 left):
  SYN-2016-299, SYN-2016-151, PROS-2018-0359, SYN-2016-479, PROS-2025-0153 and SYN-2016-180.
- The packet is `/var/tmp/third-read/packet.txt` (3,120 lines).
- A fresh Opus agent read only that file, briefed as a twenty-year GB retail-energy professional, and wrote its priors first. The brief is `/var/tmp/third-read/brief.md`.
- The seat checked 26 key quotes against the packet. All are verbatim; two sit in tab-separated cells.

**Independence: false.** The reader is the same model family as the builder.

**35 objections** (predicted 20–45, held). The reader's verdict: "a billing engine that computes
correctly line by line but whose labels, ledgers and narratives are not bound to what was actually
charged". It confirmed the 2021–22 cap and EPG rates to the penny, VAT at 5% on every Section B
line, and the DESNZ gas and T&D factors.

### The new class

**N8. One fact about the meter is printed from two records that disagree.**
- Reader's objection: O25.
- Quotes: "Meter	Traditional" and "This household has a smart meter and there is still no day to draw", on SYN-2016-479 and PROS-2025-0153.
- **Confirmed in the code.** The header's label is `tools/generate_customer_data._meter`, from the `saas.customers` record, which defaults to traditional. The day clock's sentence is `site/explore/index.html` `hhDayPanels`, from `HH_META.smartUnread`.
- SYN-2016-479 bills on read type M on every period of both fuels.
- This is not the first read's O32 (day-clock text on a gas-only account) and no row grades it. It is the "one definition with several homes" shape.

Finding: `docs/staging/SEAT_FINDING_THE_THIRD_COLD_READ_FINDS_THE_METER_TYPE_PRINTED_FROM_TWO_RECORDS_THAT_DISAGREE_2026-10-28.md`.

### Existing classes, by objection

- **Prices and tariff labels:**
  - O1, O2, O4 and O6: the printed fix against bills at the cap, one rate across two fuels, a "saving" measured from a rate the customer was never billed, and an offer sized on one leg. These are the first read's O5 and O7. O4 follows from O1: against what was actually billed, the 2024 fix sits about level with the cap.
  - O14: pre-cap SVT levels, the first read's O3.
  - O25b: a single-rate SVT billed on two registers. This is O5's family plus E4's ToU bands.
  - O32: the energy/network split, the first read's O34. **The reader's "network flat across nine years" is refuted.** Electricity non-commodity runs 52 → 80 → 55 £/MWh over 2016–2025 and gas 9 → 16 → 10 on this ledger. The reader saw three years that happen to sit near 55.
- **Renewal:**
  - O3 is the first read's O6, the page-side remainder (the row is CLEAN at 1,171).
  - O5 is the first read's O8 and O9.
- **Bills:**
  - O9 and O16: the mover's Jan 2021 and the EV home's Feb 2020 are actual-read bills with `catchup_applied` true, printed with no catch-up line (516 kWh at £54.32; 1,102 kWh at £16.39). This is N1's class, a credit the ledger holds that the page's bill omits, met here on catch-ups rather than EBSS. It widens N1's row and is not a new class.
  - O15 and O17 are the first read's O15. O24 is O34. O25c, the opening read 0.0, is INV_OPENING_READ's GAP (W2_36).
- **Collections:**
  - O7, "the household's answer is not known to the company", is the filed take-up GAP (`domestic_repayment_plan_take_up_and_keep_rates.md`). A practitioner reads it as implausible, and it stays a GAP until a source exists.
  - O11 is N3 and the first read's O10 and O16–O18. O12 is the first read's O27.
  - O13 and O29 are the three write-off dates of the open overdue finding.
  - **O13's legal claim is refuted.** The desk writes off £912.82 on 17 Jul 2024, then the Aug 2018 bills on their own six-year dates (14, 18, 19 and 31 Aug 2024). The bar is per bill. The page prints only the first write-off, which is presentation.
- **Ledger and definitions:**
  - O22 is the first read's O28 (one fuel's ledger shown as the household's).
  - O23 is N2 and INV_BILLED_EX_VAT.
  - O26 and O30 are N5.
  - O27 is the first read's O29. O28 is the first read's O27. O31 is the first read's O25. O33 and O34 are its O33 and O11. O19 is its O23.
- **Others:**
  - O10, gas not passed to the occupant: refuted as data. OCC-a03b34fb68c1 holds both legs. The copy names one meter point.
  - O20 is ruling step 3 (storage heating).
  - O21 is the storage slot's copy.
  - O35 (no prepayment, no Warm Home Discount in the packet) is not confirmed as a defect. No household drawn is shown to qualify. It is recorded, not classed.

**The prediction.** "At least one new class" held. The predicted location, the mover's final bill
and closing balance, missed: the reader checked that bill and found it right. The class came from Section B.

## What follows

- N8 goes to its finding, with its row to follow: written blind from the knowledge pages, in the form "the meter type a page prints has one home".
- Leg two needs the debt slot's validity predicate to see the page's own ladder (the notice before the miss, and the counters). That waits on the overdue finding's write-off home. The slot is not patched around it.
- N1's row widens to catch-ups (O9/O16).
- The next exit attempt needs a run carrying `c4738b64c`, `37abacdf4` and `558ee4624` and the open items above, graded, then a fourth read.
