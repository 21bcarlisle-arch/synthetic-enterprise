**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** none — Lane 0 `grade-the-3dc5a92948-book-and-build-its-pages`

# The 3dc5a92948 book, graded, with its pages built (2026-10-30)

Under the correctness stretch (`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`).
This is the first fresh book to carry every billing fix, including the SVT one-list-price gate (ed8684442).

**The run.** Job `fresh-run-3dc5a92948`, output `/var/tmp/fresh-run-out-3dc5a92948`, outcome SURVIVED.
Its grade chain `grade-chain-3dc5a92948` wrote `/var/tmp/fresh-grade-3dc5a92948/`:
- `ledger.json`
- `grade_five.txt`, the leg-one rows
- `svt_revenue.txt`
- `grade.txt` / `grade.json`, the full suite

After the chain's `ALLDONE`, `/var/tmp/grade-3dc5-scripts/follow.sh` (the ecb7e21fb chain's steps, re-pointed) wrote
`/var/tmp/grade-3dc5-pages/`:
- `journeys.txt`, the desk-cure predictions
- `f_vat.txt`, the F/VAT rows
- the customer pages and Explore cast, built in a scratch export of 3dc5a92948 at `tree/site/data/`
- `debt_p4.txt`, the debt slot's checks
- `n189.txt`, the N1/N8/N9 page tests

## Is leg one met in substance? Not yet: one breach is unexplained

The suite ran over all 1,293 accounts: **0 unexcepted breaches, 9 excepted rows.** Eight of the nine are
explained, and their causes are on the exceptions file. **One breach is unexplained:** the standing charge of
SYN-2016-101g (gas, standard credit, Mar 2018), at 0.22 GBP/day against its group's median 0.215. It is the same
account-month that breached on the 9553d403b7 and ecb7e21fb books. Leg one asks for zero unexplained breaches,
so it is one short.

Explained is not fixed. Four of the eight explained rows are defects with an owed fix:
- INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL (6)
- INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS (179, E1)
- INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER (a: storage homes billed single-rate)
- INV_UNIT_RATE_EPG_HOUSEHOLD (373, print/volume scatter)

The remaining four are lawful tails or need an export that does not exist yet:
- PPM C6, the SME leg
- the two EBSS rows
- revenue (B)

## (b) Each prediction, held or refuted

### The SVT gate (ad7b0393a, in the leg-one finding)

| prediction | measured on 3dc5a92948 | verdict |
|---|---|---|
| SVT row: 0 unit-rate breaches + 1 standing-charge breach | 1 of 33,627: 0 unit rate, 1 standing charge (SYN-2016-101g) | **held** |
| off-list pre-cap SVT terms 2,490 -> 0 | 0 of 4,366 | **held** |
| pre-cap SVT revenue ex-VAT falls £5k-£12k, to £334.8k-£341.8k | 346,790.28 -> **340,391.67** (-6,398.61); commodity 190,740 -> 184,341 | **held** |
| bill count within ±2% of 8,950 | 8,950 | **held** |
| EPG row 373 ±15 | 373 | **held** |

### Every read nets its run, and the catch-up's VAT is on the VAT line

| prediction | measured | verdict |
|---|---|---|
| actual-read reconciliations left uncorrected (non-zero) -> 0 | 0 of 6,452 | **held** |
| catch-ups whose VAT is off the VAT line -> 0 | 0 | **held** |
| revenue row ≤ 1 plus named open tails | 1, PROS-2017-0117 (2,175.58 against 2,202.12), the open tail named in advance | **held** |
| applied catch-ups ≈ 3,705 + 2,747, within ±10% | 6,447 of 6,452 reconciliations | **held** |

### The desk cures nothing on a due date it still holds (70e66b721)

The baseline is the 209c3350ab book.

| prediction | measured | verdict |
|---|---|---|
| **P1** zero journeys `cured` with `days_overdue == 0` | **0** | **held** |
| P2 journeys 1,000-1,700 (from 3,563) | 1,072 on 379 accounts | held |
| P3 final_notice > 287 | 205 | **refuted** |
| P3 prepayment_offered > 158 | 138 | **refuted** |
| P3 open at run end > 47 | 64 | held |
| P4 fourth check refuses ≤ 10 debt stories (from 94) | 3, then **2** after the check fix below | held |

P3 is refuted. Fewer journeys reached the top rungs, not more. I cannot yet say why: P2-P4 were filed as
unattributable, and several fixes landed between 209c3350ab and this book. The journey counts are identical to the
ecb7e21fb book's (1,072 / 920 cured / 88 written off / 64 open), so the SVT gate moved none of them.

## (a) The pages, the cast and the debt slot

**Cast: 6 of 8 filled. The EV and storage-heating slots are honestly empty, each naming the checks that fail.**
The cast is the same as on ecb7e21fb:

| slot | household |
|---|---|
| switch_in | PROS-2025-0022 |
| renewal | SYN-2016-031 |
| estimate_trap | PROS-2017-0264 |
| mover | PROS-2017-0351 |
| debt | SYN-2016-210 |
| shock_2022 | PROS-2019-0246 |

The suite's book breaches block no slot.

**N1/N8/N9 page tests on these pages:** `test_the_committed_price_is_the_tariffs_not_one_bills.py`,
`test_the_meter_has_one_home_on_a_gas_only_page.py` and
`test_the_cast_nets_the_bills_own_credit_and_names_its_catch_up.py`: **10 passed.**

**Debt slot, its four checks.** The slot's household, SYN-2016-210, passes all four. Of the 381 debt stories the
rule matches, the checks refuse:

| check | refused |
|---|---|
| overdue notice before the miss | 2 |
| nothing missed or returned beside a missed moment | 0 |
| agency placement no moment shows | 103 |
| cleared while still owed | 3, then 2 after the fix below |

### The three "cleared while still owed" households, traced by name

These are the same three as on the ecb7e21fb cast. Script: `/var/tmp/grade-3dc5-scripts/trace_cw.py`.

1. **SYN-2016-016. A defect in the check, not the desk: fixed in this commit.** The story is "cured" on 21 Mar
   2018, and the page put 33.95 past due. That 33.95 came from a **-36.70 credit invoice** (raised 7 Mar, printed due
   24 Mar). `_owed_past_due` subtracted it as a bill not yet due, which adds the credit back. A credit is available
   when it is raised. The desk read the same day as -3 days overdue, which is right. Fix: only a debit waits for its
   due date (`tools/generate_explore_cast._owed_past_due`).
   - Red then green: `test_a_credit_note_not_yet_due_is_not_added_back_to_what_is_owed`, with a can-refuse leg.
   - The reverted mutant reds it.
   - The rebuilt cast is unchanged.
2. **PROS-2025-0013. The story outruns its own page.** "Arrears repaid" is dated 7 Jul 2025. The page's payment
   ledger is as of 4 Jul 2025, and its last electricity row is the returned DD on the 9.74 bill (23 Jun). The
   check therefore reads 9.74 owed at a moment the page holds no record for. The refusal is correct for the page as
   printed. A moment dated after the record ends is a small class of its own, and I have not filed it. The slot
   refuses this household either way.
3. **PROS-2020-0191. The desk and the page disagree on what is owed: cause not established.** INV17530 (40.73,
   electricity, due 20 Oct 2023) had its DD returned and stays UNPAID on the page to the end of the book. Every
   later bill is paid exactly.
   - The desk's journey opened 17 Feb 2023. On 15 Jan 2025 it read 126.09 overdue, which is the page's gas 85.36
     plus that 40.73.
   - On 16 Jan 2025 gas paid 85.36, and the desk cured with 0 overdue.
   - 126.09 - 85.36 is 40.73, not 0. So either the desk's own ledger holds the 40.73 as paid when the page does not,
     or its view dropped it.
   - **I cannot yet say which.** The desk's ledger is not exported. Re-running `CollectionsJourneyDesk.advance`
     over this account's ledger through 2025-01-16 settles it.
   - The slot refuses it. It is the residue the desk-cure record's P4 named: "where the page's per-invoice
     allocation and the desk's FIFO disagree".

**Where the fifth cold read reads them.** `/var/tmp/grade-3dc5-pages/tree/site/data/` (`customers/`,
`explore_cast.json`, `customer_sample.json`), built from this book at 3dc5a92948 with the fixed `_owed_past_due`.
The committed `site/` is not touched: DIRECTION says the pages change only at the 2 Nov publish.

## (c) The exceptions file

Each `max_breached` is now this book's count:
- **INV_SVT_ONE_PRICE_PER_REGION_METHOD_WINDOW 1,068 -> 1.** Its `retired_by` now names the standing-charge trace.
- **INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE 25 -> 1.**
- **The other seven are unchanged:** EPG 373, PPM 12, the two EBSS rows 6 and 6, carbon 6, E1 179, estimated run
  6. Each reads exactly its ceiling. The six that ecb7e21fb's full suite graded carry the same five sampled
  breaches as there. EPG was graded there only by the leg-one rows, at 373.

No row reads 0, so none is retired. Checks:
- The runner over this book's grade passes with the new file.
- One more SVT breach than the ceiling refuses the publish.
- The gate's own tests pass: 64 passed.
