# Pre-registration: the ending-term arms against flat, six dice seeds, on a book after `c09847b7c`

**Written 2026-11-25 by the delivery seat (executor), claim
`preregister-the-ending-term-arms-against-flat-on-a-post-c09847b7c-book`. No arm of this run had
started when this was written, and no output of it exists.** This is the follow-on that §3 of
`SEAT_PREREG_THE_ENDING_TERM_BELIEF_ON_THE_COMING_BOOK_2026-11-22.md` fixed before its grade. The
grade (§5 there, landed `9c1b75713`) took the first branch: conditioned AUC 0.882 [0.840, 0.924],
paired against the live belief 0.487 [0.416, 0.564]. The switch-on rule (director, 23 Oct) needs
paired arms, and a standing book cannot supply them.

**Premise re-measured at draw.** All three commits the item cites are already on origin. That is
expected, because they are the inputs, not this work. No six-seed prereg for these arms existed in
`docs/staging/`, and no `/var/tmp/*` directory held their outputs. So the work was not spent.

## 0. What runs

- **Code.** One detached worktree, `/var/tmp/se-etarms-wt`. The driver creates it at whatever
  `origin/main` is once this file is there, so the run descends from `c09847b7c` and from this
  file's own landing (§0.2 needs that). Its HEAD sha is written to `/var/tmp/se-etarms-out/HEAD`
  before any arm starts. Every output's `producing_commit` has to equal it.
- **Arms.** `python3 -m tools.per_customer_switch_arms {flat,all_on_ending_term} OUT --dice-seed N`
  for **N = 2, 3, 4, 5, 6, 7**. That is 12 arm-runs, one at a time. Each one goes through
  `background.launch_long_job`, which holds it in a queue until the box has room. The driver is
  `/var/tmp/se-etarms-out/drive.sh`. Outputs go to `/var/tmp/se-etarms-out/s{N}/{arm}.{json,log,rc}`.
  The seed numbers are reused, but this is a different book, so none of these runs is pooled with
  §14 or with the 24 Oct re-take.
- **Cost** (the 24 Oct re-take's §5 arithmetic). Each arm-run took about 55 minutes and about 7 GB,
  so the run needs about 11 hours of box time and no money. Six seeds come from the departure gross
  seed SD of about £4,100: t = 2.571 gives a half-width of about £4,310, against the 24 Oct mean of
  £5,709. The household-net leg has an SD of about £2,150, giving a half-width of about £2,250
  against £2,852. Six seeds clear zero only if those means and spreads hold on this book. That is a
  hope, not a prediction (§2).
- **The grade.** `tools/grade_per_customer_switch_seeds.py`, which needs three arms. As on 24 Oct,
  the ending_term output also fills the save_odds slot, so **save_odds − ending_term is a placebo
  that must read £0.00 in every channel**. Output: `/var/tmp/se-etarms-out/grade.txt`.

### 0.1 What `all_on_ending_term − flat` is

This is the design of §14, and it is not the switch on its own. The arm turns on
`renewal_belief_by_ending_term` **and** the three per-customer switches
(`next_best_action_decides_at_renewal`, `next_best_action_shares_by_retention_rise`,
`save_offer_decides_per_household`). Today `CURRENT_POLICY` has all three set to `False`. Flat
differs from both in the retention offer and its framing. So a positive result shows that the
bundle beats flat. It does not show what the ending-term belief adds on its own. §3 handles this.

### 0.2 The grader now counts drift exits, and the departure definition changed in this commit

Before this commit the `departure` channel read `customer_events` only. The 22 Nov record's §5.3
item 4 showed what that misses: on `f2c6979d01`, all **252** drift exits are only in
`svt_departures`, and none appears in `customer_events`. So a household that drifted off the
standard variable product in one arm only was graded as `same_choice` or `other`. Its lost margin
was counted as money, but never as a departure.

This commit makes three changes to `reduce_run`:
- It writes each `svt_departures` row into the household's rows as `left`, so a difference in drift
  exits is a `departure`.
- It keeps those households apart as `drift_departure`, with their own gross and net. That figure
  sits inside `departure` and is not added to it.
- It **refuses** a run output that has no `svt_departures` key, because such an output would read
  as one in which nobody drifted.

The new test `test_a_drift_exit_in_one_arm_only_is_a_departure_and_is_counted_apart` fails when the
row write is removed (mutation run, 25 Nov). On `f2c6979d01` the reducer joins 246 of the 252
drift households to a `per_cid_pnl` line. The 6 without one carry £0 in any channel.

**Consequence.** "Departure" here means renewal departures **plus** drift exits. The 4 Oct and
24 Oct grades counted renewal departures only. Their figures stay comparable only as context, and
the item's own definition is the one that changed.

### 0.3 What the arms grade besides the company (22 Nov §5.4, stated as asked)

The departure money in these arms comes from the desk treating default-anniversary households as
low-risk. The conditioned multiplier for `default` is 0.027 on `f2c6979d01`. On that book:
- the world rolls no departure at a default anniversary (P10c);
- only 2 of 252 drift exits fall inside a desk state's 365-day window.

So a positive `departure` figure partly grades **the world's no-departure-at-default rule**, not
only the company's skill. Counting drift exits (§0.2) stops the arms from winning on a channel the
world has switched off while ignoring the channel it left open. It does not make P10c true. Whether
GB households on a default anniversary really do not leave at that moment is a fidelity question.
This run does not answer it. A positive result here is read **conditional on P10c** and is
published with that condition beside it.

## 1. Setup facts (read, not predicted)

- `CURRENT_POLICY` has all four fields `False` (read 25 Nov).
- `f2c6979d01`, a standing book with the switch off, has 252 `svt_departures`, 111 `churned`
  renewal events and 0 overlaps between them.

## 2. Predictions (no output of this run read)

| | prediction | confidence |
|---|---|---|
| **E0 placebo** | save_odds − ending_term reads £0.00 and 0 households in every channel, `drift_departure` included, on every seed. If it fails, the grade is void and the grader is read first | 99% |
| **E1 dice reach the world** | every pair of flat seeds differs by ≥ 20 in its (household, date) departure set, renewal `churned` ∪ `svt_departures`. A pair below 20 voids the later seed | 90% |
| **E2 code** | every output's `producing_commit` equals `/var/tmp/se-etarms-out/HEAD` and carries `svt_departures`. Any that does not is void | 95% |
| **E3 drift exits reach the channel** | `drift_departure` households ≥ 1 on at least 4 of 6 seeds | 60% |
| **E4 drift share** | \|mean `drift_departure` gross\| < 25% of \|mean `departure` gross\| | 65% |
| **E5 departure gross** | positive on ≥ 4 of 6 seeds (70%); 6-seed 95% interval above zero | 45% |
| **E5n departure household net** | 6-seed 95% interval above zero | 40% |
| **E6 money** | mean net ≥ 0 | 75% |
| **Rule met** (§3: E5 and E5n and E6 all hold) | | 35% |

Why the confidence in E5 is below what the 24 Oct arithmetic implies: that arithmetic assumes the
24 Oct mean and spread carry over. About a month of world and company commits has landed since
`ff8437814e`. The departure channel rested on 4–6 households per seed, and the four seeds ranged
from +£1,806 to +£11,442. Erring against the thesis is the safe direction (F11).

## 3. Decision rule (fixed now)

The rule is the 23 Oct ruling's, as restated in 24 Oct §3 and 22 Nov §3. The switch is proposed
only if **all three** hold:
- the 6-seed 95% interval of `departure` gross against flat is above zero;
- the same is true by household net;
- mean net against flat is ≥ 0.

If the legs disagree, the switch is not proposed and the disagreement is reported. A net carried by
`parity` or `same_choice` is a transfer (M2) and does not count.

**What a pass proposes, given §0.1 and §0.3.** The arm is a bundle, so a pass cannot switch on
`renewal_belief_by_ending_term` alone. A pass proposes the bundle's four fields together for
`CURRENT_POLICY`. It is published conditional on P10c, and it carries an owed one-variable follow-on:
`all_on` against `all_on_ending_term`, which measures what the belief adds to the per-customer
offers. Under ruling point 2, a pass is the machine's switch-on **of that bundle**. A failure leaves
the switch off with this grade as its reason (point 3). Predicted: **not met, 65%**.

**Not answered here.** The household side of the per-customer offers (parent record F5) is still a
GAP. P10c's fidelity is not answered either (§0.3).

## 4. Launch

The launch is queued as a costed run through `background.launch_long_job --detach --job
etarms-driver`, with the driver above. The driver checks `origin/main` for this file and **refuses**
if it is missing. Only then does it create the worktree and start the first arm. The grade is
written into §5 of this file by the seat continuation
`grade-the-ending-term-arms-against-flat-six-seeds`, which is gated on
`/var/tmp/se-etarms-out/grade.rc`.
