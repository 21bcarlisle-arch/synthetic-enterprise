**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 2 · **Atom:** `EP4_collections_journey`
**Knowledge:** home-moves -- `docs/market_research/home_moves.md` s.8.8e (choices 21-24, the close set-off)

# The N29 blind row's 23 are one class: the close set-off nets only the debt the household never pays (2026-11-16)

*Claim `n29-blind-row-residual-23-on-the-issue-day-clock`. An earlier tick holding this claim wrote the successor
`n29-close-set-off-nets-issued-debt`, which cites this file by name, but the file never landed on origin, the shared
tree or any commit (`git log --all -S` empty, 16 Nov ~21:00Z). This is that record, re-measured from scratch.*

## Pre-registration (filed before any ledger was read)

`/var/tmp/n29r/PREDICTION.txt`, written before the dump. The prediction came from the successor's one-line claim, so
it was not blind to the class, only to the per-line arithmetic:

- P1: 23 of 23 are a set-off/payment ordering on the refund day. The other leg has a bill issued by the refund day and
  collected after it, and the bound's gap is that bill's unpaid part.
- P2: 0 are a real refund above the household's whole credit.
- P3: 0 are a grader misreading.
- Refuted by any line whose gap no issued, not-yet-collected bill on the other leg explains.

## Instrument

A worktree at 8a300fa561 (`/var/tmp/n29r/B`). The publisher's page chain (`/var/tmp/fab-ab2/chain_full.py`) runs over
`docs/reports/run_output_8a300fa561_20261116T031305Z.json`. Then `perline.py` records every band
`ev_closing_refund_within_household_credit` draws. **Control:** this reproduces the row at 23 breached of 132, the
same 23 lines as `/var/tmp/n29c/lines_B.json`. `/var/tmp/n29r/classify.py` reads each line's other leg: its
end-of-refund-day balance (`_balance_at`), its last bill on or before the refund day, its first payment after it, and
the run's own `credit_refund_log` set-off. Output: `/var/tmp/n29r/classified.json`.

## Result: P1, P2 and P3 all hold, 23 of 23

On every line, the other fuel leg owes money at the end of the refund day. In every case the money is the unpaid part
of a bill issued before the refund day. The same leg's next payment after the refund day clears exactly that amount.
In every line, the gap (refund less bound) equals min(refund, that amount). The 23 gaps total GBP 483.51.

| sub-shape | lines | what the run's set-off did |
|---|---|---|
| no set-off at all | 16 | `set_off_gbp` 0.0: the run's `closing_balances` read the other leg as clear |
| part set-off | 7 | it set off only the part already overdue (PROS-2016-0024g 13.05, PROS-2022-0237 113.2, SYN-2016-072 6.22, -237g 8.06, -294g 25.34, -323g 14.1, -420g 3.56). The final bill, issued but not yet collected, was missed |

How the other leg paid that bill: direct debit 3-14 days after the refund on 20 lines. By standard credit on 2 lines
(PROS-2023-0013g, 33 days later; SYN-2016-026, 14 days later). As "prepayment" on 1 line (OCC-69f8c5b4358b, a leg
whose payments are labelled prepayment but run 14 days after each bill, which is not this row's question).

SYN-2016-007 and SYN-2016-026g, the two lines the issue-day clock newly bounded, are the same class. They are not a
side effect of ceeefa5960.

## Why

`simulation/credit_refund_events.generate_credit_refund_log` sets off against `closing_balances`. That is
`arrears_engine.balance_settlement_from_outcomes`' balance "at the final bill", and it is built from the run's
payment OUTCOMES. A final bill that the mandate collects after the refund day is counted as paid. So the set-off,
made on the refund day, reads a collection that has not happened yet and nets nothing against it. The grader reads
the printed pages at the end of the refund day (choice 23), where that bill is still owed. The grader is right:
s.8.8e choice 21 sets the credit against the household's **closing debt**, and s.8.8f says the final bill IS the
closing demand. A debt that is issued but not yet due is still part of it.

So this is a defect in the world's set-off, not in the row. Its cost to the household is the money order, not the
amount: the household is refunded and then debited a few days later. A reader of PROS-2016-0024g sees GBP 135.21
refunded on 15 Jan while the other fuel owes 180.12, which the 20 Jan debit then takes. It also carries a latent
route by which a world-side decision on the refund day reads a later DD outcome.

## Ranked explanations considered

1. **The set-off reads a later-collected bill as paid** (above). This explains every line exactly, to the penny.
2. A grader reading (the end-of-day balance double-counting the set-off): ruled out. On the 7 part-set-off lines the
   gap is the after-set-off remainder, not the pre-set-off debt.
3. A real refund above the household's credit with no other-leg debt: none. Every gap is covered by other-leg debt.

## What carries it

The successor `n29-close-set-off-nets-issued-debt` builds the fix. **Correction to that hand-off:** it calls the fix
"home_moves.md s.8.8e proposed choice 25", but choice 25 is not on the page. s.8.8f records that "25 is cited in
code comments but is not on this page" (`background/live_payment_triad.py:1428`, s.8.8c). Choices 26-28 are D5's.
Under K8, the build first writes its choice on s.8.8e under the next free number. Its prediction for the replay is
0 of 132 breached on run_output_8a300fa561, and any surviving line refutes it.
