**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# The twelfth cold read, on the 6fe7827ab2 book with its pages rebuilt at origin: a billing-systems test analyst finds one new serious class and one presentation class (2026-11-13)

**What this is.** The correctness ruling's cold-read leg, graded against
`records/SEAT_PREREGISTRATION_THE_TWELFTH_COLD_READ_ON_THE_6FE7827AB2_BOOK_AT_ORIGIN_2026-11-13.md` (fc0a2ed72). That
preregistration landed before the checks ran, before the draw and before the brief. Its hash file is
`/var/tmp/twelfth-read/prereg.sha256` (02:58:23Z). Lane-0 item `a-cold-read-ahead-of-the-16-nov-book`.

**The eleventh read's serious class.** N29 is filed with an owner
(`SEAT_FINDING_A_CLOSING_DUAL_FUEL_HOUSEHOLD_IS_REFUNDED_ON_ONE_FUEL_WHILE_IT_OWES_ON_THE_OTHER_2026-11-11.md`,
`EP4_collections_journey`) and fixed in 3af02a2dd1. Nothing needed filing.

## The setup

- **The book and the pages.** `run_output_6fe7827ab2_20261111T140730Z.json`. Its pages were rebuilt at origin
  1d86d8e71f in `/var/tmp/twelfth-read/tree`, by the publisher's chain plus hh_day and carbon.
  - The carbon step now asks git whether its inputs match HEAD. The scratch tree was given a throwaway repo holding
    those inputs for that one step.
  - These pages carry the N28 fix (7d43952ff7) and the page half of N29.
  - They were served on 127.0.0.1:8812. **These are not the live pages.**
- **The gate:** **PERMITS False.** `INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO` has 5 breaches against a ceiling of 1, and
  8 rows are excepted.
  - The 5 legs are exactly the 12 Nov replay's: four cross-arm legs and SYN-2016-139, the named refund-clock leg. In a
    cross-arm leg, the run sized its refund with the older engine and the page re-walks the account at HEAD.
  - So the refusal comes from reading an old book with new page code, not from a company defect. **Exit leg one is not
    gradeable on this build.**
- **The cast:** 8 of 8 filled, the same households as the eleventh read.
- **Section B:** drawn with `random.Random(20261113)` from a pool of 637. The pool is the picker's 757, less every
  earlier draw or cast, less this cast.
  - The draw: PROS-2018-0096, OCC-207a02e4ac32, OCC-f8ada09eac47, SYN-2016-132, OCC-101208fa8e36, SYN-2016-309,
    OCC-7ec00b802506, SYN-2016-418, OCC-f9acff98642e, OCC-a097d0031a9f.
- **The trade, new to these reads:** a billing-systems test analyst.
- **The blind tree:** `/var/tmp/twelfth-read/blind`, which `blind_worktree --check` reported clean.
- **The reader** used Read on BRIEF.md only and returned 35 objections. It stopped once after writing its priors
  (lines 1 to 30) and was resumed in the same context, so the priors stood before it read the packet.

| exit-test leg | verdict |
|---|---|
| 1. Suite on a fresh run's full book | **Not gradeable on this build.** The refusal is the four-leg cross arm plus the named refund-clock leg. The 16 Nov book grades it |
| 2. All eight slots valid or honestly empty | **MET on the reader's verdict.** All eight are "yes", the debt journey "weakly". The N28 sentences no longer print against their bills. The EV slot's one stale debt-stage line (O30) is presentation |
| 3. No new serious class | **NOT MET.** **N30**: a dual-fuel home's two traditional meters are read separately. When one fuel is read the other is estimated, in 89% of such pairs, on 359 households. It changes what each bill charges, so it is serious by the rule. See `SEAT_FINDING_A_DUAL_FUEL_HOMES_TWO_TRADITIONAL_METERS_ARE_READ_ON_SEPARATE_DAYS…_2026-11-13.md` (owner `W2_36`) |

**One further new class, presentation only: N31.** A printed catch-up bill hides the catch-up's VAT in the VAT line above
it. See `SEAT_FINDING_A_PRINTED_CATCH_UP_BILL_HIDES_THE_CATCH_UPS_VAT_IN_THE_VAT_LINE_ABOVE_IT_2026-11-13.md`.

## The seat's named checks, over every page file

These are the checks from triage row `a-cold-reader-sees-only-what-its-trade-looks-for`. The scripts are in
`/var/tmp/twelfth-read/scripts/`.

| check | result |
|---|---|
| Meter identity across supply points (`checks.py` b) | 214 serials on two or more accounts across the book. This is the fifth read's class, still live. Every account's first read is 0 (1,302 of 1,302) |
| Reads repeating to the decimal (b) | Electricity: 451 actual reads repeat last year's month, on 125 households; the same-month median change is 0.73%. Gas: 17 repeats on 12 households; the median change is 13.03%. These are known rows |
| Payment method on the bill's date (c) | 11 bills on C6 paid by prepayment. 46 accounts change method. 1 account moves from direct debit to pay on receipt and back. Known |
| **Gas billed with a volume (new, `gasvol.py`)** | All 24,274 gas bills carry an m³ volume. Volume × 1.02264 × CV ÷ 3.6 gives the metered kWh on every bill once the catch-up's kWh is counted. No actual read falls below an earlier actual. The CV is a fixed stand-in of 39.5 on every bill and is labelled as one: the fifth read's class, known |
| The trade's own arithmetic (`arith.py`, domestic bills) | 47,528 bills. VAT is 5% on all of them, and the 2 SME accounts are excluded. The standing charge is days × rate, the registers sum to the commodity line, and the totals close. One read differs from its use by 0.2 kWh. Due dates are 14 to 21 days after the bill |

## Predictions against results

| # | prediction | result |
|---|---|---|
| R1 | The gate refuses on the closed-account row, cross-arm legs only, p ≈ 0.6 | **Held, with one correction.** The fifth leg, SYN-2016-139, is the named refund-clock leg, not a cross-arm leg |
| R2 | `checks.py` matches the eleventh read | **Held** on b and c. Two a-rows moved slightly (9,130 → 9,109; 9 → 6) |
| R3 | Some gas bills carry no volume (p ≈ 0.7); conversion exact on at least 95%; the CV a stand-in everywhere | **First part refuted:** every gas bill carries a volume. The second and third parts held |
| R4 | Closed a year: 0 accounts in credit; debt between GBP 2k and 5k | **Credit refuted:** 4 accounts hold GBP 425.10. That is exactly the four cross-arm legs (65.17 + 133.14 + 106.30 + 120.49), which the preregistration had named. Debt **held** at GBP 3,461.29 on 65 accounts |
| R5 | N25 between 600 and 800 | **Held** (711) |
| R6 | Cast 8 of 8, and no N28 sentence contradicts its bills | **Held** |
| R7 | At least one new class, p(none) ≈ 0.3 | **Held** (two: N30 serious, N31 presentation) |
| R8 | A proration or price-split objection, p ≈ 0.6 | **Held** (O12, O13) |
| R9 | 20 to 40 objections | **Held** (35) |
| R10 | Leg two MET, p ≈ 0.5; leg three NOT MET | **Held** on both |

## The objections, graded

| objection | grade |
|---|---|
| O23: on the same date, one fuel has an actual read and the other is estimated | **NEW, N30, serious.** Measured book-wide (above) |
| O15: VAT printed above a catch-up it includes | **NEW, N31, presentation.** Money correct |
| O3, O4: "deemed account" entries clear billed charges, and stage 5 and stage 6 disagree | **Known, N26** (the eleventh read's control, found unaided again). Every gap the reader named is a `deemed_account` entry: B3 104.63, B5 324.57, B10 96.31, B2 the whole 96.38, B7 81.08 |
| O1: every register starts at zero | **Known** (seat check b; the opening-reads finding) |
| O2, O21: printed energy-only rate; network as a lump sum | **Known presentation** (the tenth read's O11/O13) |
| O5, O31, O32, O33, O34 | **Known presentation** (fuel-leg balances, denominators, method not printed, no due date or MPRN). O34 is a label |
| O6: direct-debit credit not reviewed | **Known**, the level-DD family |
| O7, O25: write-off with no steps; overdue moving with no bill | **Known**: the recovery-note family and the per-bill dunning family |
| O8: SYN-2016-418 refunded GBP 2.13 on electricity while gas owed GBP 22.20; gas still prints GBP 23.68 after its write-off | **Known**: N29 (world half not in this book) and the written-off-yet-owed final-bill netting. Its world net, 37d934286, is graded on the 16 Nov book |
| O9, O24: the switch-in balance; credit before any bill | **Known, N23.** The O9 arithmetic is the eleventh read's O8 again |
| O10: "23 of 23 paid" beside GBP 657.06 owed | **Known, recurring** |
| O11: a renewal offered at a negative expected value; one £/MWh figure for an E7 home | **Known** renewal-floor family; the rate is presentation |
| O12, O13: a term end not split | **Known, with a correction to the reader.** The March 2017 bill on SYN-2016-132 *is* priced split. Its 13.13p all-in rate is a 13-day fixed / 18-day standard variable blend (≈ 13.2p), printed as one "Fixed" rate. That is the mixed-term presentation family (`INV_HOUSEHOLD_PAGE_TARIFF_IS_THE_BILLED_TERM`, flagged), and the drift is N25 |
| O14: fixed CV | **Known**, the fifth read's class, labelled on the bill |
| O16, O17: flat electricity year on year; "1.4×" on five homes | **Known**, `INV_ELEC_MONTHLY_USE_MOVES_YEAR_ON_YEAR_LIKE_A_HOUSEHOLD` (breached). The sentence is computed (`site/explore/index.html:872`). Five identical ratios are a symptom of the flat electricity shape |
| O18: national prices and London weather | **Known** (W1_14 weather; one national range printed) |
| O19: one supply point printed on a dual-fuel home | **Known** (the tenth read's O2) |
| O20: B6 off-peak 2.40p in Jan 2017 | **Known**, the fixed-floor family (a-rows) |
| O22: 18 months of estimates, and a correction against the trend | **Known**, `INV_READ_DUTY_ANNUAL` and `INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER` |
| O26: PC2 estimates per register; rates drifting 0.01p | **Known**: the PC2 per-register estimate finding, and N25 |
| O27: 67% off-peak with no shiftable load | **Reader inference.** The Peak band is a narrow evening window (settlement periods 32 to 38, `simulation/demand_response.py`). Profile class 1 homes on this tariff put 67 to 73% off-peak across all 83 of them. The window is not printed, which is presentation |
| O28: winter electricity swing; 2,856 kWh in a month | **Known**, the electric-heating verdict row |
| O29: the 2022 shock total cannot be traced | **Known**, N26 with the EBSS sentence family |
| O30: a stale debt line on the EV slot; no solar export | The stale line is presentation (N28 family). Export is not a class: the Smart Export Guarantee binds suppliers with 150,000 or more domestic customers |
| O35: a first bill with no energy | **Known** (the fourth read) |

## What the reader found right

- Bill line arithmetic and VAT on every Section B bill. The seat's `arith.py` confirms it book-wide.
- EBSS and EPG amounts and months.
- Gas conversion, the catch-up kWh, and the E7 register sums.
- Cap-date price changes aligned to bill periods.
- Three closing refunds within 10 working days.
- Carbon refusing a part year.

## Next

- N30 goes knowledge first (K8). The read-coupling practice is a practitioner fact with no published share, so it is
  carried as a GAP with a range. Then the world build (`W2_36`), then its blind row.
- N31 goes to the household page's bill block.
- The 16 Nov book grades leg one. A thirteenth read on that book, with a trade not yet used, is the next cold read. It
  cannot meet leg three until N30 is fixed on a book.
