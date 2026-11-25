**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`
**Knowledge:** `home-moves` -- `docs/market_research/home_moves.md` s.8.8c (choices 25, 26)

# Result: a switching level leaver's final bill netted by the world, graded on f2c6979d01 (2026-11-25)

Grades `SEAT_PREREG_A_SWITCHING_LEVEL_LEAVERS_FINAL_BILL_NETTED_BY_THE_WORLD_2026-11-23.md` on the first book
whose producing commit descends from 7527a2e36c: `run_output_f2c6979d01_20261124T215935Z.json` and its
`world_walk_truth_f2c6979d01_20261124T215935Z.json` (`git merge-base --is-ancestor 7527a2e36c f2c6979d01` is true).

**Method.** The prereg's `replay.py` and `table.py`, run from a detached worktree at f2c6979d01. The only edits
were the two book paths and the scratch output directory: `/var/tmp/grade-sll/` instead of `/var/tmp/ll-scripts/`,
so the baseline's `under_refunded_legs.json` survived for the leg match. No line of logic changed. The replay
reproduced `closing_balances` on 871 legs with **0 mismatches**, so the grade is not refused. The leaver set is
871 legs against the baseline's 854 (+2%, inside the 10% line), so totals stand.

**The base moved a long way.** f2c6979d01 is 213 commits past 6a588a832f, and 40 files under `simulation/` and
`company/` changed in that span. Of the baseline's 149 legs, **124** are still netted legs with the same final
period. Faces differ on 84 of them, so the matched comparisons below include other commits' effects. They are
not an A/B test of this change.

## Against the bands

| | Baseline | Prediction | f2c6979d01 | Verdict |
|---|---|---|---|---|
| Netted legs collected at face | 149, GBP 3,673.83 | 0 to 5, GBP 0 to 100 | **0 legs, GBP 0** (232 netted legs, GBP 5,405.15) | **CONFIRMED** |
| Under-refund by year | 28.77 to 806.14 | 0 to 25 each year | no year has a leg | **CONFIRMED** |
| Final DDs presenting nothing (ask 0) | 0 | 70 to 100 | **89** of the 124 matched legs | **CONFIRMED** |
| Money in on those legs' final bills | 5,077.71 face less earlier nets | falls by 3,100 to 4,250 | face less ask on the 124 matched legs: 4,125.55 - 822.97 = **3,302.58**. That is 3,968 scaled to 149 legs. It is an upper bound, because the fixed scripts do not recover the earlier credit-bill nets | **CONSISTENT** (bounded, not exact) |
| Refunds on matched legs | 9,244.83 | moves by less than GBP 50 | 9,373.28, **+128.45**. On the 40 legs with identical face and page-net it is +21.31 (19 legs moved) | **CLAUSE TRIPPED, confounded** (see below) |
| `netted_ledger_credit_legs` | 84, GBP 1,768.48 | 200 to 260, GBP 4,700 to 6,200 | **270, GBP 7,508.01** | **OVER BAND** |
| Reverse legs (world nets more than the page) | 8, GBP 201.03 | 6 to 12, under GBP 300 | **30, GBP 585.17** | **REFUTED** |
| Addendum: debit-half rows not in `home_move_outs` | 0 | more than 0 (direction only) | **147 legs, GBP 11,434.11 debit asked**. All 44 baseline debit rows were movers | **CONFIRMED (direction)** |

**The refund clause.** The prereg said a refund move of GBP 50 or more would mean the change reached the page or
the company. As written, the clause fires: +128.45 on the matched legs. Three things point the other way:

- The replay rebuilds every `closing_balances` value from bills and behaviour alone, through
  `simulation.arrears_engine.balance_settlement_from_outcomes`. Nothing the triad asks feeds it. A refund pays
  that closing.
- On all 76 legs whose refund moved, it moved by exactly as much as the closing did. For example, SYN-2016-323g went
  from -202.94 to -265.53, and the face also moved.
- The 213 intervening commits changed the faces and other bills on these accounts.

My read is that the move is the trunk's, not this change's. A same-base A/B (this book's commit, with and
without `closing=left`) would settle it. That needs a run, and I have not done one.

## The new finding: the world now nets past the page on 30 switch-away legs (GBP 585.17)

Every reverse leg has the same shape. The world's `ledger_balance_gbp` holds a large credit, takes the whole
face from it (`credit_taken_gbp` = face, ask 0), and the page nets only the credit-bill credit. Example:
OCC-3c914ee8cef5g 2017-03 has face 56.45, page-net 44.01, world ledger -162.66, world takes 56.45, and closing 0.
The page records 12.44 collected that the world never presented. In 14 of the 30 legs the closing is 0 and there
is no refund event. Opening the final month on any closure carried choice 25's ledger net to switch-aways, and
their world ledger credit is larger than the page's closing credit. Of the four net-reading rows, this is the
one the prereg did not see coming. The book's page cash and the world's cash disagree by GBP 585.17 on these
legs. Some of that overlaps the 270-leg over-band row.

It is LATENT: no published figure is graded on it yet. It is the same class as the 149-leg defect this change
fixed, now in the opposite direction: the page and the world read different credits at a final bill. The next
piece is to find why the world's ledger credit on a switch-away exceeds the page's closing credit, and which of
the two is right under SLC 27.17.

**Reverse.** Delete this file. It changes no code.
