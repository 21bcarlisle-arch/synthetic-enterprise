**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# The fifth cold read, on the 3dc5a92948 book: leg two met, leg three not met. Two new classes: one meter serial on up to 34 supply points, and every gas read held as a kWh register (2026-10-30)

**What this is.** This is the reading that the director's correctness ruling asks for
(`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`, "Exit test").
- Item: `fifth-cold-read-on-the-3dc5a92948-book` (DIRECTION row `the-fifth-cold-read`).
- Graded against `docs/staging/records/SEAT_PREREGISTRATION_THE_FIFTH_COLD_READ_ON_THE_3DC5A92948_BOOK_2026-10-30.md`,
  which landed as `25c865c06` before the reader was briefed.

**The book and the pages.**
- The book is `/var/tmp/fresh-run-out-3dc5a92948`, outcome SURVIVED.
- The pages are `/var/tmp/grade-3dc5-pages/tree/site/`, built from this book at 3dc5a92948 with the
  fixed `_owed_past_due` (`74d6c0759c`). There are 1,293 pages.
- They were served on 127.0.0.1:8791. Port 8765 was already held by another process, so it was not used.

| exit-test leg | verdict |
|---|---|
| 1. The suite on a fresh run's full book: zero unexplained breaches | **Met in substance**, as graded at `74d6c0759c` / `51a39fd752` (0 unexplained, 8 excepted rows). Not retaken here |
| 2. All eight slots filled validly or honestly empty | **MET**, with conduct caveats on the renewal and debt slots that are existing classes (below) |
| 3. One cold read finds no new class | **NOT MET.** Two new classes, each confirmed on the record and in code: N10 and N11 |

**The stretch does not exit**, and the ruled order stays closed. The advisor file stays where it is.

## Predictions against results

| # | prediction | result |
|---|---|---|
| P1 | 6 of 8 filled; ev and storage_heating empty | **Held** |
| P2 | the reader grades the debt slot (SYN-2016-210) valid | **Refuted.** The reader graded it "partly". The seat grades it valid by its rule and its four checks; see leg two |
| P3 | 20–45 objections | **Held** (27) |
| P4 | at least one new class | **Held** (two: N10, N11) |
| P5 | N1, N8 and N9 do not recur by name | **Held.** PROS-2019-0246: £598.04 − £67.00 = "£531.04 to pay" (reader's Q3). OCC-2f64fad94fe7 prints "Unit rate, all-in before VAT	7.07 p/kWh", the Jan–Mar 2024 cap, with one "Meter	Smart" and "Supply point	1305736345 (MPRN)" |
| P6 | SYN-2016-550 prints one owed figure per moment and still carries an unpaid old bill held flat | **Split.** Old bills held flat: **held.** On electricity, Oct 2018 (8.47 outstanding) and May 2020 (60.08) total £68.55; on gas, Dec 2023 is £187.53, all unchased. One figure per moment: **refuted.** The page prints "balance £68.55" (the ledger panel is electricity only) beside "Owed on 4 Jul 2025 £256.08" (both fuels). That is the one-fuel-panel class (the first read's O32 family), not a new one |
| P7 | leg two MET; leg three NOT MET | **Held** |

## Leg two: the eight slots

| slot | household | reader | seat |
|---|---|---|---|
| switch_in | PROS-2025-0022 | yes | Valid. "Three months in" is two months: the first read's O12 |
| renewal | SYN-2016-031 | yes by rule, no as conduct | Valid by the rule, as on the third and fourth reads. The notice falls on expiry (`INV_RENEWAL_NOTICE_42_TO_49_DAYS`), and the fix is billed at the cap (O5) |
| estimate_trap | PROS-2017-0264 | yes | Valid |
| mover | PROS-2017-0351 | yes | Valid. Closing actual read, final bill, new occupant, refund in 10 working days |
| debt | SYN-2016-210 | partly | Valid by its rule and its four checks (see below) |
| ev | empty | honest, mostly plain | Honest |
| storage_heating | empty | honest, not plain | Honest. "96 match the rule" beside "no profile class 2 meter (96 of 96)" is the third read's O21 copy. Single-rate storage billing is item 3, already filed |
| shock_2022 | PROS-2019-0246 | yes | Valid. N1 is closed on this page |

**Why the seat grades the debt slot valid where the reader says "partly".**
- The ending agrees with the page. "24 Mar 2025 · Debt cleared" prints "Nothing owed", the 1 Feb 2025
  bill (£78.30) is paid that day, and the 1 Mar bill was paid inside 14 days. So the fourth check
  passes, and on the ledger, not only on the predicate.
- The reader's fault is conduct, and it is real. On the ledger, 20 electricity bills from Dec 2022 to
  May 2025 are paid 34–100 days after they are raised, and one is paid 712 days after. Yet the page
  records only two notice pairs, Apr–May 2023 on electricity and Nov–Dec 2023 on gas, and the journey
  sits "past the top rung" for 26 months.
- That is the open "after the last rung" GAP
  (`docs/staging/done/SEAT_FINDING_THE_COLLECTIONS_DESK_WALKS_BACK_DOWN_ITS_OWN_LADDER_2026-10-24.md`,
  `docs/market_research/company_debt_management.md`). The decision dated before the journey opened
  ("20 Nov 2022 … £122.29") is the first read's O17. "£172.73 overdue", which counts bills 13 days
  old, is the overdue class the fourth read named.
- None of these is new, and the household is a true example of what the desk does. Under F11, I record
  that a leg graded MET on a slot whose conduct a professional reads as "barely modelled" is a
  generous reading. If the director reads it otherwise, leg two is not met for the same reason as
  on the fourth read.

## Leg three: the read

**Method.** Ruling step 6, the fourth read's route (`/var/tmp/fourth-read-scripts/render.mjs`).
- Every cast moment was rendered with Playwright.
- Six households were drawn with `random.Random(20261031).sample` from the picker's 752, less the four
  earlier reads' 25 (727 left): PROS-2023-0291, PROS-2020-0012, SYN-2016-051, OCC-7c2500b09b7b,
  SYN-2016-279 and OCC-392d56a03faa.
- OCC-2f64fad94fe7 and SYN-2016-550 were added by name, as the DIRECTION row asks.
- The packet is `/var/tmp/fifth-read/packet.txt` (3,401 lines, 142,887 characters). The brief is
  `/var/tmp/fifth-read/brief.md`, which carries three named questions.
- A fresh Opus agent read only the packet, as a twenty-year GB retail-energy professional, and wrote
  its priors first.
- The seat checked 37 key quotes against the packet. All 37 are verbatim.

**Independence: false.** The reader is the same model family as the builder.

**The reader's verdict.** The pages show "a billing engine that is priced right, wrapped in account,
metering and collections records that no real supplier could issue". It confirmed:
- cap, EPG and EBSS rates to the penny, with EBSS on electricity only and £66/£66/£67;
- every Section B bill's arithmetic and 5% VAT, except one penny (O27);
- the DESNZ gas factors, the MPRN on the gas-only page, the mover's refund timing, and the 2024–25
  gas cap path.

### The two new classes

**N10. One meter serial sits on up to 34 supply points** (reader's O6).
- The quote is "meter M00062062" on PROS-2023-0291 (supply point 15…, North East) and on
  OCC-7c2500b09b7b (10…, Eastern).
- Over the rebuilt pages there are 127 distinct serials in 1,293 pages. 96 of them sit on 2–34 supply
  points, all across distribution prefixes.
- Confirmed in the code. `tools/generate_billing_ledger._meter_serial` is `sum(ord(c) * 31 …)`, which
  ignores character order, so the ids collide.
- Finding: `docs/staging/SEAT_FINDING_THE_FIFTH_COLD_READ_FINDS_ONE_METER_SERIAL_ON_UP_TO_34_SUPPLY_POINTS_BECAUSE_THE_SERIAL_IS_AN_ORDER_BLIND_CHECKSUM_2026-10-30.md`.
- The reader's "register runs backwards" follows from the shared serial, and is not a separate class.
  The reader's "registers start at zero at switch-in" is the open opening-read finding
  (`…PRINTS_6436_OPENING_READS_NOBODY_TOOK_2026-10-28.md`).

**N11. Every gas read is held and billed as a kWh register, with no volume and no conversion**
(reader's O7, Q2).
- The quote is "1104.4 kWh × 5.038p/kWh (gas) = £55.64", over "Opening read 7,503.2" and "Closing read
  8,607.6" in kWh. The same page says gas is "kWh read from its own gas meter, converted at gross
  calorific value".
- All 23,816 gas invoices on 586 pages carry kWh register reads and no volume field.
- The roster's `cv_factor` and `cf` are never read on the read or bill path.
- Finding: `docs/staging/SEAT_FINDING_THE_FIFTH_COLD_READ_FINDS_EVERY_GAS_READ_HELD_AND_BILLED_AS_A_KWH_REGISTER_WITH_NO_VOLUME_OR_CONVERSION_2026-10-30.md`.
  Its K8 knowledge page is owed before any build, and which side of the seam the volume belongs to is
  not yet decided.

Neither class was raised by the four earlier readers, though every read had gas pages and serials in
front of it. That is a finding about the reader as well as about the pages. No earlier reader raised the
meter's identity or its unit, and the seat's rows took `meter_serial` as given.

### Existing classes, by objection

- **Pricing and renewal.**
  - O1 (a fix billed at the cap, one £/MWh across two fuels) is the first read's O5 and O7.
  - O2 is `INV_RENEWAL_NOTICE_42_TO_49_DAYS`.
  - O14 (truth dated to the wrong renewal, 0.0%) is the first read's O9 and O11 family.
  - O15 is the overdue class.
- **The deemed share.**
  - O3 is the first read's O26 and the fourth read's O24: the ledgers' gaps are exactly
    `total_deemed_gbp`, at £113.70, £178.15 and £174.72.
  - O4 is the same cause. Stage 6's "Billed, VAT included" £1,138.69 is £1,302.04 billed less £163.35
    deemed, while revenue includes the deemed share.
- **Margin and cost.**
  - O5 is the first read's O25.
  - O21 (2016–17 SVT levels) is not confirmed. No pre-cap SVT row is breached on this book, so it is
    recorded and not classed.
- **Bill lines and identifiers.**
  - O8 is the first read's O34.
  - O9 is the first read's O32 family.
  - O19's smart gas page carrying traditional-meter carbon copy is the N8 / O32 family. Its zero-use
    first bill is N9's stub, and N9 is now honestly labelled.
- **Payments.**
  - O10's copy is the fourth read's "flat monthly amount".
  - O10's one-fuel ledger and O12's two owed figures are the O32 family (P6).
- **Collections.**
  - O11 is the "after the last rung" GAP, the first read's O17, and the overdue class (leg two).
  - O12's held balances are the first read's O27 and the desk-versus-ledger findings.
- **Copy.**
  - O13 is the first read's O23.
  - O16 is the third read's O21.
  - O20 is the denominators the second read recorded.
  - O22 is the second read's paths.
  - O23 is the first read's O12.
  - O24 is the second read's percentage-point line.
  - O26 (EPG disclosure on one page and not another) is the second read's unshown price guarantee.
- **World.**
  - O17 (London degree days for every region) is **recorded, not classed**. My first draft called it
    the weather-cell ruling's known single-cell GAP. That was wrong: the ruling names four world
    weather nodes, and no earlier read raised this. The page prints its basis openly
    (`site/explore/index.html` uses one London series for every household, "the same series the
    simulation's own gas settlement is driven by"). So it is a disclosed approximation, not a
    misstatement, unless a household's demand was driven by another node. That is the measurement
    that settles it, and it is not taken here. If it was, the page's r is computed against the wrong
    weather and the class is new. Leg three is not met either way.
  - O18 (no crisis demand response) is N4, deferred by DIRECTION.
  - O18's estimated flat use is E1's 179.
- **O25** is `INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL` (6, excepted).
- **O27, one penny of VAT on a catch-up bill**, is not traced here. The catch-up VAT row reads 0 on
  this book, so this is a rounding-basis question at most, recorded and not classed.

## What follows

- N10 and N11 each have a BLOCKING finding and a blind row landed with this reading
  (`docs/design/DOMAIN_INVARIANTS.yaml`). Neither row is checkable until the record carries what it grades.
- N10's fix is small and drawable. N11 needs its K8 page and a seam decision first.
- The next exit attempt needs both closed, a fresh run graded on leg one, and a sixth read.
- A sixth read's brief should name the meter's identity and the gas unit among the things a
  professional checks, now that four reads went past them.

## The sixth cold read, drawn before its inputs exist (2026-10-30, seat-executor)

`the-sixth-cold-read` was drawn with origin at 192900fc3a. Its direction row says "once item 3's
grade and pages and item 4's tool are on origin, and not before". Neither is:

- **Item 3's book doesn't exist.** It waits on item 2 (`a-gas-read-is-a-volume-and-the-bill-converts-it`),
  and only item 2's K8 page is on origin (e0f8c1fbed). The C1–C3 build hasn't landed: no commit
  since that page touches `company/interfaces/sim_interface.py` or `company/billing` for gas volume.
  No run is in flight, so no grade or rebuilt pages exist.
- **Item 4's tool isn't on origin.** `tools/blind_review.py` is AO9's packet assembler, not the sparse
  worktree. `tools/blind_worktree.py` and its test are staged, uncommitted, in another lane's
  `/var/tmp/wt-blind-worktree`.

So nothing was read, no pre-registration was written (it would name a book that doesn't exist),
and the claim is released. Leg three stays open on the fifth read's two classes (N10 graded 0 by
6ef8f1b678; N11 not built). Draw the sixth read only once item 2's build, item 3's grade record in
`docs/staging/records/` with its rebuilt Explore pages, and `tools/blind_worktree.py` are all on origin.
