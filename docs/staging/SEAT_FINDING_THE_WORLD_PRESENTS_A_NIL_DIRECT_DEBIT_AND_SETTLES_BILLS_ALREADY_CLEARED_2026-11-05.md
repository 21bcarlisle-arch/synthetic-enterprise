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
