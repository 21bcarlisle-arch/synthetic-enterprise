**Severity:** LATENT · **Lane:** A_strategy_governance · **Atom:** `value-arms-error-bar` · **Class:** `measurements_that_mirror`

# The two-seed diff under the balance-at-close rule: B1–B5 all hold, one variable, and the selection sign does not move

**2026-09-28.** This grades
`SEAT_PREREG_THE_TWO_STATE_DIFF_RERUN_UNDER_THE_BALANCE_AT_CLOSE_RULE_2026-09-27.md`. The run was
stranded overnight with nobody to grade it. Its queued one-variable baseline had also finished,
at 03:17Z, so this grading is **one variable**. It is not the two-variable reading the drawn item
expected.

## The three artefacts

| run | producing commit (read from the artefact) | artefact |
|---|---|---|
| old rule, before the world commits | `de1677d74` | `/var/tmp/se-two-state-diff-rerun/account_diff.json` |
| **old rule, baseline** | `cefd2c04a` (= `6ba548633^`) | `/var/tmp/se-two-state-balance-rule-baseline/{value_cycle_ab,account_diff}.json` |
| **balance-at-close rule** | `d993a9797` | `/var/tmp/se-two-state-balance-rule/{value_cycle_ab,account_diff}.json` |

Between the baseline and the rule run, the only code that changed under `simulation/`, `company/`,
`saas/` and the runner is `simulation/arrears_engine.py` and `tools/generate_billing_ledger.py`.
The prereg's correction established that. Each `account_diff.json` was written by
`python3 -m tools.selection_residual_decomposition --account-diff <artefact> --json <beside it>`.

## The figures, settled-realised clock

| | `cefd2c04a` old rule | `d993a9797` balance rule | rule's move |
|---|---|---|---|
| selection, seed 11111 | −£4,387.72 | −£4,834.56 | −£446.84 |
| selection, seed 88888 | +£919.23 | +£949.49 | +£30.26 |
| selection, two-seed mean | −£1,734.24 | −£1,942.53 | −£208.29 |
| `PROS-2016-0098` state move | −£5,310.36 | −£5,787.58 | −£477.22 |
| Herfindahl | 0.9941 | 0.9946 | |
| value arm net (both seeds) | £181,309.19 | £180,807.30 | −£501.89 |
| level arm net, 11111 | £185,696.91 | £185,641.86 | −£55.05 |
| level arm net, 88888 | £180,389.96 | £179,857.81 | −£532.15 |
| control net, 11111 / 88888 | £172,106.81 / £170,476.98 | £171,684.37 / £170,033.59 | −£422.44 / −£443.39 |

## Grades

- **B1 CONFIRMED.** `PROS-2016-0098` moves −£477.22 from the baseline, inside ±£913. Against the
  prereg's literal comparator (−£5,349.74 at `de1677d74`) it moves −£437.84, also inside. The
  mechanism the bound assumed, where only recovery at the write-off year moves, is *consistent*
  with this, not isolated by it: the level arm loses £532 in the state where 0098 leaves and £55
  where it stays. No per-leg split of that account was taken.
- **B2 CONFIRMED.** Seed 11111 stays negative, 88888 stays positive, and the mean stays negative.
- **B3 CONFIRMED.** Herfindahl is 0.9946, with one account holding 90% of the movement.
- **B4 CONFIRMED.** Every arm on every seed moves by less than £1,000 (largest −£532.15).
- **B5 CONFIRMED, exactly.** The baseline's run 0 on seed 11111 prints 110 lifecycle events and
  net margin £155,141.00, identical to the rule run. In fact all six printed run summaries are
  byte-identical in net margin and provision between the two logs. The rule acts only through the
  settled-realised re-booking and never reaches the sim's own printed P&L. The roster change from
  104 to 110 events is therefore the world commits' doing (`d9374ae9e`, `c08932808`), as guessed.

## The two-variable total, reported as asked

Against `de1677d74`, the value arm moved +£2,920.76 (£177,886.55 → £180,807.30). Of that, the world
commits contributed **+£3,422.65** and the rule **−£501.89**. On the level arm, the world commits
contributed +£3,571.81 on seed 11111 and +£3,608.96 on seed 88888.

## What this settles and what it does not

The balance-at-close rule, on its own, does not move the selection sign on either seed. It widens
the switch by £477. The published reading, "one account's churn roll, inside its own noise", stands.

What it leaves open is the leg the rule deliberately left `None`: provision on a stayer's aged
arrears (leg 4b). That leg acts in exactly the state where `PROS-2016-0098` stays, and its rate
turns on C1. The C1 bracket run is filed as the next record beside this one.
