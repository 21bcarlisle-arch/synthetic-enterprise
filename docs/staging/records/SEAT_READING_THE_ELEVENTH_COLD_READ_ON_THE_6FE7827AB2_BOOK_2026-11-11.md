**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# The eleventh cold read, on the 6fe7827ab2 book: the first book the publisher's gate passes, and an Energy Ombudsman investigator finds one new serious class (2026-11-11)

**What this is.** The correctness ruling's cold-read leg
(`advisor/done/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`). Since bb69c250de (11 Nov ruling)
the leg reads "no new SERIOUS class", per `serious_class_rule` in `docs/direction/priority_order.yaml`. It is graded
against `records/SEAT_PREREGISTRATION_THE_ELEVENTH_COLD_READ_RUNS_ON_THE_6FE7827AB2_CLOSE_REFUND_BOOK_2026-11-11.md`
(33e412c5d, landed before the brief rendered), which amends 1d25b4526c.

**Correction beside the claim.** The preregistration says it was written "at about 16:20 GMT". It was written at about
16:09 GMT; the hash file `/var/tmp/eleventh-read/run/prereg.sha256` carries the time. The order is unchanged: hash, then
checks, then draw, then brief.

**The book and the pages.**
- Book: `run_output_6fe7827ab2_20261111T140730Z.json`, the first carrying cab13bbd18's close-refund fix.
- Pages: built at 6fe7827ab2 by the publisher's chain, plus hh_day and carbon (`/var/tmp/crbook/arm/tree`). Origin
  50315088fb changes no page or gate code, so these are origin's pages.
- Served on 127.0.0.1:8811. **These are not the live pages.**
- **The gate:** `_domain_invariant_gate_permits_publish` returned **PERMITS True**, with 0 unexcepted and 7 excepted.
  It was graded before the brief existed, so the tenth read's deviation is not repeated.
- **The cast:** 8 of 8 filled.
  - switch_in PROS-2025-0022, renewal PROS-2022-0011, estimate_trap PROS-2017-0264, mover **PROS-2017-0351** (new),
    debt PROS-2016-0054, ev PROS-2017-0183, storage_heating PROS-2020-0189, shock_2022 PROS-2019-0246.
- **Section B:** drawn with `random.Random(20261112)` from a pool of 647 households. The pool is the picker's 757 less
  every earlier draw or cast and less this cast. The draw: PROS-2020-0016, SYN-2016-382, PROS-2019-0318, SYN-2016-156,
  PROS-2022-0237, SYN-2016-569, OCC-d17156aa03be, PROS-2021-0325, SYN-2016-252, SYN-2016-105.
- **The trade, new to these reads:** an Energy Ombudsman case investigator.
- **The blind tree:** `/var/tmp/eleventh-read/blind`, which `blind_worktree --check` reported clean. The reader used
  Read on BRIEF.md only and returned 31 objections.

| exit-test leg | verdict |
|---|---|
| 1. The suite on a fresh run's full book: zero unexplained breaches | **MET, for the first time.** PERMITS True: 0 unexcepted, and 7 rows breached inside their exceptions. `INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO` moves from 3 breaches to 0 (87 flagged), and `INV_REFUND_WITHIN_THE_PAGE_CREDIT` from 205 to 0 |
| 2. All eight slots filled validly or honestly empty | **NOT MET.** 8 of 8 are filled, but N28 is unfixed and the reader found it unaided on two slots. On the 2022 shock (O6), "the household's use did not explain the change" sits over a 29% rise. On the EV home (O23), "Your first electricity bill is ready" goes to a 2017 account in 2023 |
| 3. One cold read finds no new serious class | **NOT MET.** One new class, N29: a closing dual-fuel household is refunded on one fuel while it owes on the other. It moves money, so it is serious by the rule. 48 households, GBP 3,786.62 refunded against GBP 5,662.78 owed, of which GBP 2,254.02 was later written off. See `SEAT_FINDING_A_CLOSING_DUAL_FUEL_HOUSEHOLD_IS_REFUNDED_ON_ONE_FUEL_WHILE_IT_OWES_ON_THE_OTHER_2026-11-11.md` |

**The stretch does not exit.** It is two legs short. The close-refund fix did what it was built for: the book carries
no credit a year after closing, and no refund exceeds its leg's credit.

## Predictions against results

| # | prediction | result |
|---|---|---|
| Q1 | 0 accounts a year closed holding credit of GBP 5 or more; debt GBP 2k–5k | **Held.** 0 credit (the D1 book had SYN-2016-493 at GBP 11.56). Debt GBP 3,461.29 on 65 accounts |
| Q2 | N25 fixed runs with a moving standing charge: 600–800 | **Held** (711, unchanged) |
| Q3 | first read zero 1,302 of 1,302; electricity median under 1%; gas 8–18% | **Held** (1,302; 0.73%; 13.03%) |
| Q4 | Cast 8 of 8 | **Held** |
| Q5 | Control: the reader finds N26 unaided, p ≈ 0.5 | **Held.** O12 on OCC-d17156aa03be: "Billed £531.35, collected £456.31, balance £-35.21". The gap is GBP 110.25, exactly its `total_deemed_gbp` |
| Q6 | At least one new class, p(none) ≈ 0.2 | **Held** (one, N29) |
| Q7 | 20–40 objections | **Held** (31) |
| Q8 | At least one closing final-bill or refund objection, p ≈ 0.6 | **Held** (O13, O14, O15, and the (d) answers) |
| Q9 | Leg one MET, leg two NOT MET, leg three NOT MET | **Held** on all three |

## The objections, graded

| objection | grade |
|---|---|
| O14: one fuel refunded while the other's debt is written off (PROS-2019-0318) | **NEW, N29, serious.** Confirmed over every page file: 48 households |
| O1: a payment plan offered at GBP 93 overdue during an over-estimated run (mover) | **Known** estimate-accuracy family (`INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER`, excepted). Chasing an estimated bill is lawful. The GBP 916 over-estimate is that row's class |
| O2, O15: direct-debit credit built up without review (GBP 2,054; PROS-2022-0237) | **Known** level-DD and DD-review family (level-DD map s.4). Not re-measured |
| O3: 18 months unread | **Known**: `INV_READ_DUTY_ANNUAL` |
| O4, O5: "N of N paid" beside a debt | **Known, recurring** (ninth O12/O13, tenth O17) |
| O6, O23, O28: narrated facts | **Known, N28.** O28's GBP 916.14 is the ex-VAT catch-up inside a VAT-inclusive total, from `generate_explore_cast.py:383`, on 4 slots. It is the same template class as the tenth's EBSS sentence |
| O7: 2,856 kWh in a month for one person | **Known** (the tenth's O7; the electric-heating verdict row). 15,214 kWh in 2022 |
| O8: switch-in balance against "0 of 0 paid" | **Reader miss on the arithmetic.** GBP 125.31 of direct debit was collected on 17 Feb, before the first bills (GBP 68.49 + 98.55), which leaves GBP 41.73. That is N23 (direct debit collected before the bill) plus the payment-record row |
| O9, O10, O11: printed energy-only rate, night component 1.23p, range offered | **Known presentation** (the tenth's O11/O13). The gate's floors read the all-in rate |
| O12 | **N26**, the control (Q5) |
| O13: credit held after a short June bill | **Reader inference.** Every account's last bill ends 7 Jun 2025, the run's end. OCC-d17156aa03be did not close |
| O16, O21: standing arrears with GBP 0 notices; overdue rising with no bill | **Known** per-bill dunning and per-leg collections families (`SEAT_FINDING_A_LEVEL_DIRECT_DEBIT_HOUSEHOLD_IS_DUNNED_PER_BILL…`, split 1 of the dual-fuel collections finding). Not traced to the penny |
| O17: write-off with GBP 0 recovery notes; cost line over revenue | **Known.** The recovery-note family (`SEAT_FINDING_THE_DESKS_WRITE_OFF_OF_A_CLOSED_ACCOUNT_NEVER_REACHED_THE_PAGE…`) and the undefined margin (first read; SITE1 50315088fb). SYN-2016-105 carries 29 notice entries, so "no collection step visible" is a reader miss |
| O18, O19, O20 | **Known**: the electric-heating verdict row, N17/N24, and the W1_14 London weather |
| O22: rates drifting 0.01p inside a fix | **Known, N25** |
| O24, O27, O31 | Presentation, or known (cast tariff label FLAGGED; run end against ledger as-of; P&L margin) |
| O25: estimated register split on a storage-heater home | **Known** (the PC2 per-register estimate finding, 30 Oct) |
| O26: no prepayment in 18 households | **Reader inference.** 163 of 1,302 accounts on the book carry prepayment statements. The method is not printed on Section B, which is presentation |
| O29: no MPRN or gas serial printed | **Known** (the tenth's O2) |
| O30: credit on day one; gas about 2.5p in Jun 2018 | **Known**: N23, and the fixed-floor family. Not re-graded |

## What the reader found right

- The bill arithmetic and VAT on all ten Section B bills.
- The EPG and EBSS amounts.
- The stage 6 identities.
- The mover's and PROS-2022-0237's closing refunds, both within 10 working days.
- Nine of ten ledger sentences reconcile.
- Carbon refuses a part year.

## Next

N29 goes knowledge first (K8). The twelfth read waits for a book carrying both an N28 fix and an N29 fix. Until then
legs two and three cannot both be met.
