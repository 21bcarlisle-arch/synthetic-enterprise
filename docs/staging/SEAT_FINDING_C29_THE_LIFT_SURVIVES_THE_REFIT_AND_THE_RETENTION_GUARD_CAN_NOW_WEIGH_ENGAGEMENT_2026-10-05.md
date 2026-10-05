**Severity:** RECORDED · **Lane:** C_customer_ops · **Epoch:** 4 · **Atom:** `C29_decisions_stop_being_lookup_tables`

# The lift survives the refit, and the retention guard can now weigh engagement (off by default)

Claim `c29-regrade-the-engagement-lift-on-the-refitted-world-then-wire-the-retention-guard`. It was
drawn before its prerequisite had landed. The prerequisite's `surgical_land` was running at draw
time. It finished as `ae552db75`, gated with a receipt, on the branch `c29-refit-landed`. **At the
time of writing that commit is NOT on origin/main.** *Corrected the same morning: its seat had exited without promoting it, so this invocation merged origin into it under the gate (`768cf5bf2`) and promoted it. The refit is on origin.* This item's code does not depend on it. Only
the re-grade below reads the refitted world, and that ran in a worktree at `ae552db75`.

## 1. The re-grade: the world arm survives, and the book arm is still owed

The world arm uses `tools/c29_engagement_ranking.world_rolls`: 125 households on the live book,
rolled by the world's own `rolls_active_renewal` with each household's trait. The null shuffles
outcomes within each channel, 200 draws, seed `NULL_SEED`, with a 95% band.

| world | anniversaries | channel ρ | estimate ρ | lift | null band |
|---|---|---|---|---|---|
| pre-refit `862b9178a` | 5 | 0.080 | 0.820 | **0.740** | −0.188 … 0.123 |
| refitted `ae552db75` | 3 | 0.160 | 0.632 | **0.471** | −0.154 … 0.090 |
| refitted `ae552db75` | 5 | 0.160 | 0.671 | **0.511** | −0.163 … 0.102 |
| refitted `ae552db75` | 9 | 0.160 | 0.716 | **0.556** | −0.178 … 0.081 |

The channel-rate null arm reads a lift of exactly 0.000 in both worlds, as it must.

**Reading.** The refit narrowed the trait from 0.02–0.69 to 0.12–0.54, and the lift fell by about
a third. It is still about five times the top of its null. So the frame's refutation clause does
NOT fire, and decision #1 stays per-account. A Spearman lift measures ranking, not spread. What the
refit really cut is how much a correct ranking is WORTH, because the weights now sit closer together.
That is why it is the weighting of a guard, not the ranking, that has to be graded in the value arms.

**Owed: the BOOK arm.** `python3 -m tools.c29_engagement_ranking` runs the book arm against the
newest run output. Every run on disk predates the refit. The refit has to reach origin before the
scheduled run can draw the refitted world. **Prediction, filed before that run:** the book lift
falls by about the same third as the world arm, from 0.545 to about 0.35, and it stays above its
shuffle null's upper bound. If it lands inside the null, the frame's clause applies to the book,
and the weighting below must not be switched on in any arm.

*Graded 2026-10-05 on `run_output_7a3cdd060_20261005T115844Z`: lift 0.268, null −0.303 … 0.015.
Above the null held; the size did not (half, not a third). The value-arm pair ran. See
`SEAT_FINDING_C29_THE_BOOK_ARM_SURVIVES_THE_REFIT_AT_HALF_ITS_LIFT_2026-10-05.md`.*

## 2. The wiring: in place, off on every standing policy

- `DecisionPolicy.retention_weighs_engagement` defaults to `False`. Every standing policy leaves it
  off, so every existing run is unchanged.
- `company/crm/engagement_estimate.engagement_at` gives one account's estimate. It is fitted on the
  supplier's own term rows (`account_state_log`) and its own renewal departures
  (`customer_events_log`), one fuel at a time, with only rows dated strictly before the anniversary
  being decided. The book is the set of legs whose payment method the seam has been asked for at a
  renewal. It returns `None` when there is no book or no channel. In that case the guard is
  today's guard.
- `value_protected` is the guard's arithmetic, reached through the `growth_desk` door (`retention_engagement`, `retention_value_protected`), which hands back floats only: `(expected_margin + acq_cost_saved) ×
  estimate`, and unweighted when there is no estimate. It adds no new constant. The discount SIZE
  stays on the P(leave) tiers (PB5).
- When the policy is on, `retention_log` carries `engagement_estimate`. Default runs do not write
  the key.

Controls: `tests/company/test_the_retention_guard_weighs_value_by_engagement.py`. The partition leg
comes first: the weighting can both refuse and keep an offer. Three mutations each turn a leg red:
read the decided anniversary (`<=`), drop the weight, and count a future departure.

**Printed at real inputs before shipping.** I replayed the 53 retention offers in
`run_output_1279b164d_20261005T032309Z.json` (pre-refit world) through `engagement_at`, with each
offer's own date. **The weighting refuses 7 of the 53.** One has no estimate. Weights run from 0.04
to 0.83.

**A defect the smoke run found, and fixed before landing.** In the first draft, the book was only
the legs whose payment method was read inside the renewal block. A 2016–2020 run with the field on
weighed almost every offer at **1.0**: 26 of 28 offers had an estimate, and 2017–18 sat at
1.0/0.94/0.90. A household that rolls to the default never reaches that read, so the book held only
accounts that chose, and every channel rate came out at 1. The replay gave about 0.3–0.4 for the
same dates. That was the tell. Every domestic leg is now enrolled when its term row is written, and
a supplier knows every account's payment method. I re-ran it to 2019 after the fix: 23 of 24 offers carry an estimate, and the in-run weights for 2017 equal the replay's on the same dates (0.375, 0.308, 0.405). The values of 1.0 and 0.97 around the turn of 2018 are the small-book defect below.

**A defect found by printing.** `PROS-2016-0042` on 2018-02-12 weighs **0.0** after one anniversary.
Early in the run, the moment fit rests on a handful of accounts with two or more anniversaries, and
it returned zero shrinkage (`prior_strength == 0.0`). So a single rolled anniversary is read as
certainty. The estimator is honest at scale and over-confident on a small early book. Any value-arm
read of this field has to report how many of its refusals rest on `prior_strength == 0`. The remedy
needs a reason drawn from the published record, not a picked minimum count, so it is filed here and
not patched.

## 3. What done means, and what is left

Done this turn: the world-arm re-grade, the wiring, the controls and the real-input print.
Left, in order:

1. The refit `ae552db75` reaches origin.
2. The book arm on the first refitted run, graded against the prediction above.
3. Only if that survives: a value-arm pair (the same world, with the field off and on), read for
   retention cost saved against departures added, and for the `prior_strength == 0` share.
