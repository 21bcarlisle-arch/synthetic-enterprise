# The world presents £0 collections, some of them "returned", and settles bills that other money already cleared (2026-11-05)

**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`. Claim
`settlement-cash-the-world-sends-for-a-bill-already-cleared`. Picks up the three items 9744dd436 left
open in `docs/market_research/debt_and_collections.md` s.7.3 ("Open, not changed here").

## Premise, re-measured at draw time

9744dd436 is an ancestor of origin/main (be1e7e0101). It is the commit that named the three defects
open, not one that fixed them. All three are still in the code at be1e7e0101:
`background/live_payment_triad.record_period` draws an outcome for every ask, £0 included, and
`simulation/arrears_engine.balance_settlement_from_outcomes` prices a settlement at what its bill
asked whatever is still open, and labels pooled credit with its latest kind.

## Counted on the fd91027799 book, before any change

Script: `/var/tmp/settle-cleared-scripts/count.py`. It replays the engine's own walk with counters,
over `run_output_fd91027799_20261105T004022Z.json`.

| Class | Count | Legs |
|---|---|---|
| (1a) A credit-bill month (asked £0) whose world collection outcome is "failed" | 29 (8 DD, 20 standard credit, 1 prepayment), of 547 credit-bill months with a world outcome | n/a |
| (1b) A failed bill a waiting credit had paid in full (asked £0) | 5, of which 4 also have a settlement queued | OCC-cede70b10116, PROS-2016-0020g, SYN-2016-215, SYN-2016-291, SYN-2016-366 |
| (2) A settlement carrying more than is still open on its fuel's contract | 25 of 1,447 settlements, £1,497.46 over the open balance | 19 legs |
| (3) A settlement's excess landing on a credit-bill remainder, which is then relabelled "repayment" | 3, hiding £299.35 of credit from the page | PROS-2017-0351, PROS-2020-0126g, SYN-2016-380 |

## What the knowledge layer says, and the choice

Neither rule is in the knowledge layer. A web search found nothing published on either: no Bacs
document on a zero-value collection item, and no supplier practice on sizing an arrears repayment.
Both are taken as stated beliefs from strong logic, recorded as GAP in debt_and_collections.md
s.7.3:

- **Nil due, nothing presented.** A Direct Debit is a pull for a stated amount. When the amount due
  is £0, no item is submitted, so there is nothing for the payer's bank to return. A "returned" £0
  DD, or a £0 standard-credit payment that "failed", is not an event a supplier could observe. The
  bill is settled by the credit on the day it falls due.
- **A household repays what it is told it owes, never more.** Its statement shows the balance. A
  later settlement of a bill that a credit, or other money, has already cleared has nothing left to
  settle. The smallest change is the one taken here: each settlement keeps its per-bill draw and
  date, and carries the lesser of what the bill asked and what is still open on that fuel's
  contract on the day it lands. GAP: whether a household in arrears clears its whole balance or one
  bill at a time. This keeps one bill at a time, as before.

## Pre-registration, filed before the change and before any fresh book carries it

On the first fresh book that carries the fix, counted with the same script:

- (1a) and (1b) fall to **0**. No credit-bill month and no fully credited bill carries a failed
  outcome, and none has a settlement.
- (2) falls to **0**. The triad and the engine size the settlement with the same walk.
- (3) falls to **0**. Pooled credit keeps each sum's own kind.
- The P&L's bad debt **rises by £0-1,500**. The removed excess was credit that either netted a later
  failed bill (which now stays open) or was refunded at close (which no longer happens).
- Outcomes that do not involve a £0 ask stay identical. The triad's draws are keyed by period, not
  amount. The exception: a changed desk ledger can move a desk contact, and through it an
  early-contact response. **I cannot yet say** how many. That will be counted, not assumed to be zero.

## Graded on the first fresh book carrying the fix, 8c7489e0d9 (2026-11-07 ~18:10 GMT): two of four held

The full grade, and what it rests on, is in `SEAT_FINDING_THE_B3CE2A4E73_BOOK_FAILS_THE_DOMAIN_INVARIANT_GATE_ON_SEVEN_ROWS_2026-11-04.md`, under
"The 8c7489e0d9 book graded". The counts come from the CURRENT engine's walk (`/var/tmp/se-grade-8c74-scripts/v3/count.py`).
This script's own replay prices settlements at the pre-fix rule.
- (1a) **0**: held. (3) **0**: held.
- (1b) **1** (OCC-cede70b10116), against a filed 0.
- (2) **19 settlements, GBP 682.47, on 18 legs**, against a filed 0 (fd91027799: 25, GBP 1,497.46). **Refuted.** The sizing
  does not use one walk. SYN-2016-047's failed Jul 2021 DD (GBP 64.38) settled in full on 20 Jul 2023. The engine's walk held only
  GBP 20.71 open, after a credit of GBP 43.67 due 15 Jun 2023. So `open_on_contract_gbp(self._leg_rows[...], settled_on)` in
  `background/live_payment_triad.py` did not count that credit. SYN-2016-255 and -329 have the same shape. Two candidate causes, neither tested:
  - the crossing happens before the credit row is appended (a `force` crossing, or a record order that is not calendar order);
  - the triad's leg rows disagree with `_resolve_bills`'s rows.
- **Bad debt, filed as a rise of GBP 0-1,500.** The two P&L figures do not agree on the sign:
  - the ledger P&L's `bad_debt_gbp` rose by **GBP 0.44** (62,586.78 to 62,587.22), at the bottom of the range;
  - the run's `total_bad_debt_gbp` **fell by GBP 417.33** (10,281.07 to 9,863.74), all of it in 2025 (1,585.28 to 1,167.94).
  These are two different quantities, and I have not established which one the prediction meant. So the prediction is held on
  one and refuted on the other, and I cannot yet say why 2025 moved. `provisioned_bad_debt_gbp` rose by GBP 1.44.
- I have not counted desk contacts.
- **Where to test (i) first.** `simulation/run_phase2b.py` posts a whole term's months at once, taking terms in order of their start
  date (`while all_terms: heappop`). So a reader that crosses with `force=True` (`provision_stock`,
  `write_off_closed_balances`) while an earlier-starting term posts can cross another account's lump before
  that account's later term has posted the credit.
- **Correction to (2), same day.** "Refuted" was wrong. The count compared each settlement's FACE with the open balance,
  because the world's truth kept no cash for a crossed settlement and `repayment_rows` priced it at the face. SYN-2016-047's
  64.38 is its bill's face, not what crossed. The engine cut it again, so no P&L carried the GBP 682.47. The truth now
  records the cash, and the engine's row carries it. (2) is re-graded on the first book that carries that change, with a
  prediction of 0. The full correction is in the B3CE2A4E73 finding, beside the grade.

## Read on the 84f7fc8fe0 book, the first carrying 12a470de7 (2026-11-08, claim `read-the-triad-settlement-count-on-84f7fc8fe0`)

`run_output_84f7fc8fe0_20261108T021850Z.json`. 12a470de72 is an ancestor of 84f7fc8fe0. Read at origin 1a899c4d0f.
No commit between the book and origin touches `background/live_payment_triad.py`. Scratch: `/var/tmp/grade-84f7-triad/`.

**Pre-registration for (b)'s ledger leg, filed before it is read.** The desk's own record is checked against itself
(P1 below). The independent leg replays the published billing ledger: for each cured journey, is a bill due on or before
the cure date still unpaid on the account, oldest first, after the day's cash? **Prediction: 0 to 3.** The residue
allowed is the per-invoice versus FIFO allocation shape (P4 read 2 to 3 on 3dc5a92948). More than 3 means the desk and
the ledger disagree on cash, which is a new defect and not this one.

**(a) Settlements whose cash is over what the engine's walk holds open: 0 of 1,426 priced. Filed 0. HELD.**
Same script as the 8c7489e0d9 grade (`/var/tmp/se-grade-8c74-scripts/v3/count.py`, the probe inside
`balance_settlement_from_outcomes`), output `count_v3.txt`. Its other counters also read 0: cash over the amount asked, and a
settlement of a nil ask, which is (1b) on this walk. The probe can fire: it read 19 on 8c7489e0d9 when the row carried
the face. With the row now carrying the triad's cash, the triad's `_cross_settlement` walk and the engine's walk agree on
every settlement. So (ii), a disagreement between `_leg_rows` and `_resolve_bills`, is not present on this book. This book
was not built from a counterfactual run, so "no P&L figure moves from 12a470de7" is not graded here.

**(b) Desk journeys closed "cured" while a bill due by that day is still owed (SYN-2016-550 class).**
- **The desk's own record: 0 of 976 cures** end with `days_overdue == 0`, and 0 end with a positive `overdue_gbp`. That is
  P1 of `records/SEAT_PREDICTION_THE_DESK_CURES_NOTHING_ON_A_DUE_DATE_IT_STILL_HOLDS_2026-10-29.md`, still held. Journeys:
  1,128 (976 cured, 86 written off, 66 open). Journeys reaching final_notice: 208. Reaching prepayment_offered: 138.
- **The ledger leg, against the 0-to-3 filed above: I cannot yet grade it.** My replay (`ledger_leg.py` over the published
  ledger) does not yet match the ledger. It started at 576 and dropped as I added three kinds of entry it had missed:
  - EBSS scheme credits, about GBP 66-67 a month;
  - deemed shares billed to the occupier;
  - repayments recorded only as ARREARS_REPAID stages in `arrears_history`, not in `payments`.

  It still reads **186 cures on 96 accounts**. In **184** of them, the ledger's own invoices hold nothing outstanding at
  run end, and many residues stay the same across years of later cures (GBP 34.91, 67.00, 134.00). That is the shape of
  another entry the replay still misses, not of debt the ledger is holding (`outstanding_check.txt`).

  The other **2** are **SYN-2016-021**, which cured on 1 Jan and 21 Jun 2023. It still has INV22817 (GBP 52.22, due
  26 Mar 2019) and INV22820 (GBP 31.07, due 15 Jun 2019) outstanding at run end. That is the live case
  `company_debt_management.md` already names, and it is a real candidate for the class.
- **The next step, one variable:** build the ledger leg from the ledger's own running balance, not from my list of what it
  is made of. If none exists, use the page's balance reader that the Explore fourth check uses
  (`tools.generate_explore_cast._debt_page_failures`). Then re-count SYN-2016-021 and the 184.
  Hand-off: `the-desk-cure-ledger-leg-on-84f7fc8fe0`.

**Disposition.** (a) is 0 on its population, so this finding's own claim is graded and it moves to done/. The open part
of (b) is the collections desk's journey, not this finding's world settlement, and it goes on as the hand-off above.

## Done

2026-11-08: (a) read 0 of 1,426 on 84f7fc8fe0, as filed. Moved to done/. (b)'s ledger leg continues as `the-desk-cure-ledger-leg-on-84f7fc8fe0`.
