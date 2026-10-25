# Pre-registration: a closed account's balance at its final bill, first printing

**Written 2026-10-25, before the probe run started.** Claim
`a-closed-accounts-balance-at-its-final-bill-is-published` (Lane 0, seat). Knowledge:
`docs/market_research/home_moves.md` §8.8a.

**What is measured.** Each leaver leg's balance at its final bill's due date, from the walk that
writes it off (`arrears_engine.balance_settlement_from_outcomes`, `closing_out`): outstanding less
unapplied credit, owed positive. Then `move_out_final_bills` grades each home move-out's final bill
as carried, credit, settled or no_balance.

**The run.** The smallest that carries the field: `run_phase4c_on_phase2b.main`, 60 founder supply
points, report end 2020-12-31, settlement budget 0, same seed. One arm, no comparison: this is a
first printing, not an effect.

**Predictions, filed before the answer.**
1. Settled is the majority of the move-outs with a final bill. Most bills are paid.
2. Carried is non-zero: a mover with a failed bill still open at close.
3. Credit is rare, 0 to 3. The engine makes credit only from credit bills and overpaid repayments.
   Level-DD over-collection is in `dd_balance_book`, not here (§8.8a choice 4). If credit is 0, the
   branch is shown takeable by the fixture control alone, and the run's zero is that named limit,
   not evidence that no mover is owed.
4. Every closing debt equals the sum of that leg's write-offs at close (`LEG_CLOSE`), to the penny.
   They are one walk, and a mismatch is a defect.
5. no_balance is 0 to 2. A leg with no resolved row (B7, no named payer) has no balance.

## Result

Run 2026-10-25 at the build commit's tree. Probe: `/var/tmp/closing_balance_probe/probe.py`; output
`/var/tmp/closing_balance_probe/r60/` (summary.json, rows.json).

| Move-outs graded | Final bill on time | Carried | Credit | Settled | No balance |
|---|---|---|---|---|---|
| 34 | 34 (late cannot fire: issue at period end) | 5 (£1,302.90) | 7 (−£118.62) | 20 | 2 |

Across all 79 leaver legs with a balance (switchers as well as movers): owed £1,366.55, credit
−£253.74.

1. Settled is the majority: **held**, 20 of 34.
2. Carried is non-zero: **held**, 5.
3. Credit 0 to 3: **refuted**, 7. A credit bill or an overpaid repayment leaves more movers in credit
   than I expected. The refund log refunds none of the 7, and it refunds one mover the ledger says
   owes £27.64:
   `SEAT_FINDING_THE_CREDIT_REFUND_LOG_AND_THE_LEDGER_DISAGREE_ON_WHICH_MOVERS_ARE_OWED_2026-10-25.md`.
4. Closing debt equals the write-off at close: **held**, 0 mismatches over 79 legs.
5. No balance 0 to 2: **held**, 2. Both are one incoming occupant's two legs
   (OCC-4596105f2006, moved out 2019-06-03), which have a final bill and no balance. I have not
   established why. The likely reason is that the closure roster does not reach an `OCC-` household's
   legs. They are counted `no_balance` and never read as settled.
