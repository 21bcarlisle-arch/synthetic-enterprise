**Severity:** RECORDED · **Lane:** C_customer_ops · **Atom:** `C29_decisions_stop_being_lookup_tables` · **Direction item:** `grade-the-retention-netting-arms-1ac35d918`

# Result: the retention guard netting its own bad-debt belief, on the contribution guard

Grades `SEAT_PREREG_THE_RETENTION_GUARD_NETTING_ITS_OWN_BAD_DEBT_BELIEF_ON_THE_CONTRIBUTION_GUARD_2026-10-21.md`
(beside this file) against P1–P5 as written there. Both arms ran at `1ac35d918` in the locked
worktree `/var/tmp/se-retnet/wt`, one process each. `off` = `CURRENT_POLICY`; `net` = the same with
`retention_nets_bad_debt=True`. The unit `longjob-retention-nets-bad-debt-arms-1ac35d918` ended with
Result=success, ExecMainStatus=0. Read from `/var/tmp/se-retnet/off.json` and `net.json`.
Afterwards the worktree was unlocked and removed.

## The pair

| | off | net | net − off |
|---|---|---|---|
| retention offers | 113 | 108 | −5 (6 withdrawn, 1 added) |
| retention spend | £2,837.65 | £2,504.63 | −£333.02 |
| renewal departures | 97 | 97 | 0 |
| churned billing accounts | 354 | 354 | 0 |
| total_net | £600,806.22 | £600,835.40 | +£29.17 |
| total_bad_debt | £124,805.98 | £124,807.12 | +£1.14 |

Offers were matched on `(customer_id, event_date)`. The 6 that `net` dropped are C8 2017-04-01,
PROS-2016-0098 2017-03-31, SYN-2016-018 2017-01-11, SYN-2016-159 2017-03-28,
SYN-2016-582 2017-12-10 and SYN-2016-536 2021-11-20. In `off`, 4 of them were retained and 2
churned despite the offer. The one offer `net` added (PROS-2017-0116, 2018-04-12, £6.38) is path
divergence: netting can only lower the value. No offer common to both arms changed its outcome.

## Predictions

- **P1, offers withdrawn: HELD, below the point band.** Offers fell by 5. The predicted range was
  6–25 and the refutation line was "fewer than 4". Spend fell by £333, inside £250–£1,100.
  Separately from the arm comparison, the guard itself refused 8 of its 240 comparisons in `net`
  and 0 in `off`. Two of those 8 were on renewals that a later step would not have offered on
  anyway.
- **P2, who loses them: HELD.** None of the 6 withdrawn offers had a POOR or CRITICAL score (3 FAIR,
  2 EXCELLENT, 1 GOOD). In `off`, POOR/CRITICAL made up 10 of 113 offers (8.8%). 0% is within 10
  points of that, and nowhere near the 2x refutation line. The withdrawals land on thin-headroom
  offers, not on debtors. Six of the 8 refusing guard rows were at the 2.0% prior: early-2017
  renewals in cells with no resolved outcome yet.
- **P3, the belief: REFUTED on both legs.** The median `belief_rate` over `net` guard rows is
  **0.0029**, below the predicted [0.015, 0.030]. Only 72 of 240 rows sat at the prior. The cells
  learned fast and learned low. POOR/CRITICAL median 0.0116 against GOOD/EXCELLENT 0.0024 gives a
  ratio of **4.7x**, past the 2x line. By score: CRITICAL 0.0121, POOR 0.0024, FAIR 0.0039,
  GOOD 0.0023, EXCELLENT 0.0200 (EXCELLENT rows are mostly early, at the prior). The arrears-state
  cells do separate CRITICAL from the clean book. The separation does not reach the guard, though,
  because debtors' offers carry more headroom than a ~1% charge removes.
- **P4, churn: HELD at the lower edge.** Departures +0, churned accounts +0.
- **P5, retained margin: HELD.** `total_net` +£29, inside £0 to +£1,000. `total_bad_debt` +£1, under
  £500. The pair is not dominated by path divergence (|Δ| far below £3,000). **I cannot yet say why
  £333 of saved spend shows up as only +£29 of net.** All 4 retained-in-`off` withdrawals still
  stayed (departures unchanged), so the saved discount should have reached gross. Candidate
  explanations: the cost being a term estimate that the window does not fully realise (the 2021
  offer), or the 31 offers whose cost moved between arms. This is unattributed, not explained.

## A further finding the pair surfaced: the belief goes negative

3 guard rows in `net` carry a **negative** bad-debt belief (GOOD −0.0083; POOR −0.0046 and
−0.0053). In those rows the netting *adds* value to the offer (charge −£2.60 to −£3.70).
`default_belief` (`company/pricing/default_belief.py:341`) shrinks a cell's money-weighted
observed charge share towards the 2% prior. The charge is the year's change in provision plus
write-offs, so a cell of accounts that start in arrears and pay down books a negative charge, and
with one account-year of prior weight a thin cell crosses zero. An expected loss below zero is
absurd as a forward belief: the realised charge can release, but the expected loss on new billing
cannot be negative. It did not change any verdict here, because all 3 rows offered with large
headroom either way. It would matter for any consumer of `default_belief_rate` that prices with
it (`run_phase2b.py:2942`, the renewal chain). The fix is a class rule: either the belief floors at
0 with a named reason, or the observation separates release of opening provision from new loss.
Which one is a design choice, and belongs to the default-belief owner.

## What this changes (per the prereg's own table)

P1 and P2 hold, so **`retention_nets_bad_debt` stays off as a debtor fix**. As built, it trims
thin-headroom offers across the whole book, mostly at the prior, and never touches a POOR/CRITICAL
renewal. It moves `total_net` by +£29 on 113 offers, which is indistinguishable from nothing at
this book size. If the field is ever flipped, the case is that it is the correct valuation, not
that it stops the debtor transfer. The debtor transfer, if it is real, needs its own mechanism (the
prereg names two options, and the guard rule on accounts in arrears is a policy choice for the
director with a recommendation). The negative-belief absurdity above is the one concrete defect
the pair found. It goes to whoever next touches `default_belief`.
