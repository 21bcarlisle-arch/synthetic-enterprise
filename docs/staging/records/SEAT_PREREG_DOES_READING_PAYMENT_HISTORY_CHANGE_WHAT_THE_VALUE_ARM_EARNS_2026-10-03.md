# Pre-registration: does reading payment history change what the value arm earns?

**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`

Written 2026-10-03, BEFORE either leg below ran. The predictions are dated by this file's first
commit, and any later edit to them is a correction made beside them, never in place of them.

## What changed, and the one variable

The pricing fix (director, 2026-10-03: "renewal_margin_uplift forwards neither arrears nor credit
risk to decide_margin") lands as one commit, C. Its parent on origin is P. Between P and C the
world is byte-identical: the fix touches only the company's price and the reads the run makes for
it, and those reads are pure. So one seed run at P and at C differs in exactly one variable. And
because the seed fixes every roll in both, the per-seed difference C - P carries no
between-seed noise. That pairing is the design, and it is why two seeds are enough to be worth
running.

## The run

`tools.run_value_cycle_ab --level-arm --noise-floor-seeds 61001,61002 --redraw-key churn_roll`,
full window, once at P and once at C. Serial, one leg resident, queued behind the depth-or-width
width pairs that are already waiting.

## Predictions (falsifiable, and some of them should fail if the fix is wrong)

- **P1. The control is untouched.** `control_net_gbp` at C equals P to the penny on both seeds. The
  flat-rule arm returns before reading anything. If this fails, the fix leaked into the control
  and nothing else below can be read.
- **P2. The fix reaches the run.** At C, at least one value-arm renewal per seed carries
  `receivable_expected_loss_gbp > 0`. At P the field does not exist. If every row reads 0 at C, the
  run-loop wiring is not reaching the ledger: a door green in tests and dead in production.
- **P3. Debtors are priced up on average, not down.** Among value-arm renewals at C where the
  ledger showed money owed, the mean chosen margin exceeds the same renewals' margin at P. The
  printed table predicts this for modest debtors and the reverse for the extreme one. If the mean
  falls, the extreme-debtor branch dominates the book, and the practitioner question in the stretch
  log is the binding one.
- **P4. PROS-2016-0098, seed 61002.** At P, the value arm retained it at its 2017-03-23 renewal
  (P(stay) 0.76 against the level arm's 0.57), and it then ran up about GBP 12k of arrears. I
  predict its 2017 offer at C is HIGHER than at P: after one year of billing its ledger already
  shows non-payment, so the flow term outweighs the small stock term. I hold this weakly. If its
  arrears were small at 2017-03-23, the fix had nothing to see, and I will say that rather than
  count a miss.
- **P5. What I do NOT predict.** The sign of the change in `selection_gbp`. Two seeds of a residual
  whose per-seed sd is about GBP 4,700 cannot carry it. The pairing removes the between-seed
  noise, but not the split-path lottery a changed price creates (stretch log 2026-10-03). Any
  sign read off C - P is reported with that caveat attached, not as a result.

## How each is graded

P1 by equality. P2 and P3 off the value-arm log at C against P, joined on (customer, commodity,
term start). P4 off the same join for one row. Written up beneath this section as a `## Result`,
with each prediction marked held or refuted. A refuted one stays beside its result.
