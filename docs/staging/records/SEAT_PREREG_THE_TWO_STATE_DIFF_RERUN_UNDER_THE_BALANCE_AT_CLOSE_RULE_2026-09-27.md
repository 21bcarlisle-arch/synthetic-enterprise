**Severity:** LATENT · **Lane:** A_strategy_governance · **Atom:** `value-arms-error-bar` · **Class:** `measurements_that_mirror`

# The two-seed level-arm diff, re-run under the balance-at-close write-off rule: predictions before the run

**2026-09-27.** Written before the run returned, so that the result can refute it. This follows
`SEAT_RESULT_THE_BALANCE_AT_CLOSE_WRITE_OFF_RULE_RUN_ALONE_2026-09-27.md`, whose S5 graded the
leaver amount on the real book by construction and left the recovery leg as a bound.

## The run

- Launched as unit `longjob-two-state-balance-rule-20260927` from a clean detached worktree of
  `d993a9797` (contains `6ba548633`) at `/var/tmp/se-balance-rule-rerun-src`. The shared tree has
  uncommitted edits that must not enter the measurement.
- Command: `python3 -u -m tools.run_value_cycle_ab --level-arm --noise-floor-seeds 11111,88888`.
- Artefact: `/var/tmp/se-two-state-balance-rule/value_cycle_ab.json`, outside any worktree.
- Log: `/var/tmp/longjob-two-state-balance-rule-20260927.log`. It takes about 2.7h.
- Liveness: `python3 -m background.launch_liveness --check`.

When it lands, run `python3 -m tools.selection_residual_decomposition --account-diff <artefact>`,
write the result beside it as `account_diff.json`, grade the predictions below, and remove the
worktree.

The comparison is the old-rule run of `de1677d74`, read from
`/var/tmp/se-two-state-diff-rerun/account_diff.json`:

- selection −£4,238.56 on seed 11111 and +£1,105.54 on seed 88888;
- value arm net £177,886.55 on both seeds;
- `PROS-2016-0098` state move −£5,349.74;
- Herfindahl 0.9936.

## Predictions

- **B1.** `PROS-2016-0098`'s state move stays within ±£913 of −£5,349.74, that is between
  −£6,262.74 and −£4,436.74. The write-off amount is unchanged, because it is a leaver in both
  fates. Only the recovery rate read at the write-off year can move, and that rate spans
  12%–25.5% of the write-off.
- **B2.** The selection figure keeps its sign on each seed: negative on 11111 and positive on
  88888. The two-seed mean also stays negative.
- **B3.** One account still holds the movement: Herfindahl > 0.9.
- **B4.** Each arm's net on each seed moves by less than £1,000 from the old-rule run. The only
  channels are the dating of write-offs and recovery, since no leaver's amount moves.

If B1 fails, the ±£913 bound was wrong, because it assumed recovery is the only leg that moves.
In that case the per-year booking (`_row_for`, S6) is the next suspect, and it is named rather
than reconciled.

## Correction, written 21:50Z while the run was in flight: the comparison above is two variables

I compared against the `de1677d74` run. Between that tree and `d993a9797`, three commits changed
the code the run executes, not one:

- `6ba548633`, the write-off rule;
- `d9374ae9e`, the siting frame rebuilt on the address placement, and a life event that keeps the
  fields it does not name;
- `c08932808`, the output-area headcount prior.

A difference from the `de1677d74` numbers therefore cannot be attributed to the rule. The first two
completed runs, parsed from the log for seed 11111, already show movement the rule alone should not
produce:

| run | old-rule log (`de1677d74`) | this run (`d993a9797`) |
|---|---|---|
| run 0: lifecycle events / term lines | 104 / 3,136 | **110 / 3,205** |
| run 0: net margin | £149,761.80 | £155,141.00 (+£5,379.20) |
| run 0: bad-debt provision | £18,743.69 | £18,950.83 |
| run 1: lifecycle events / term lines | 101 / 3,176 | 101 / 3,176 |
| run 1: net margin | £162,070.38 | £164,465.05 (+£2,394.67) |
| run 1: bad-debt provision | £18,844.99 | £18,806.50 (−£38.49) |

Run 0's roster changes. Run 1's margin moves 62 times its bad debt. Both point at the world
commits, not the rule, but that is a guess until it is measured.

**The one-variable baseline** is `6ba548633^` = `cefd2c04a`. Its code under `simulation/`,
`company/`, `saas/` and the runner differs from `d993a9797` only in `simulation/arrears_engine.py`
and `tools/generate_billing_ledger.py`. It is queued as unit
`longjob-two-state-balance-rule-baseline-20260927`, in a worktree at
`/var/tmp/se-balance-rule-baseline-src`. It waits for the first run's pid and then runs the same
command, writing to `/var/tmp/se-two-state-balance-rule-baseline/value_cycle_ab.json`. It is not
run in parallel because the first run's RSS is 8.1 GB with 10.9 GB free.

**B1–B4 are graded against that baseline, not against `de1677d74`.** Their wording stands with
"the old-rule run" meaning `cefd2c04a` under the same two seeds.

The `de1677d74` comparison is reported as the two-variable total. The world commits' share is the
difference between the two totals.

**A further prediction, filed now:**

- **B5.** Under the baseline, run 0 on seed 11111 also shows 110 lifecycle events, and its net
  margin is within £500 of £155,141.00. That would mean the roster change is the world commits'
  doing, not the rule's.
