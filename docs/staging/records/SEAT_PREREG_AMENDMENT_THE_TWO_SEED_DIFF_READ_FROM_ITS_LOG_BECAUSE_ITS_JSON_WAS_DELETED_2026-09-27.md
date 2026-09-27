**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `value-arms-error-bar`
**Class:** `measurements_that_mirror`

# Amendment: the two-seed diff is read from its log, because its JSON was deleted — and P0 has failed

**Filed 2026-09-27T14:20Z, before any per-account number was computed from the log.** Amends
`SEAT_PREREG_WHICH_ACCOUNTS_THE_TWO_STATE_SELECTION_SWITCH_LIVES_IN_AND_WHETHER_PER_ACCOUNT_CONTRIBUTIONS_ARE_INDEPENDENT_2026-09-27.md`.

## What happened to the run

`longjob-two-state-account-diff-20260927` finished at 07:08 local (2 seeds, 9,584 s). It wrote
`docs/observability/value_cycle_ab_s1_two_state_diff_20260927.json` **inside the executor's
worktree `/var/tmp/se-seat-executor`**, untracked. The next executor turn reset that worktree and
the JSON is gone — no copy on disk anywhere, no commit. The log
(`docs/observability/two_state_diff_20260927.log`, 62 MB) survived only because `*.log` is
gitignored and the reset spared ignored files. **A long job launched from the executor worktree must
write its artefact outside it**; that is a finding of its own, filed alongside.

## What was seen BEFORE this amendment (so it cannot be a prediction)

The log's closing summary, and nothing per-account:

| seed | `selection_gbp` now | shard (`ba9bc6733`) | Δ |
|---|---|---|---|
| 11111 | −£4,238.56 | −£3,802.80 | −£435.76 |
| 88888 | +£1,105.54 | +£1,548.26 | −£442.72 |
| state distance | £5,344.10 | £5,351.06 | −£6.96 |

**P0 FAILS as written** (tolerance £1). The tree moved the residual's *level* by ≈ −£440 between
`ba9bc6733` and the run's commit, on both seeds almost equally, and moved the *state distance* by
0.13%. So the prereg's own rule applies to the level: nothing here is compared with the 18-seed
shard. The two seeds are still in opposite states at one commit, so the within-run contrast between
them is still a same-commit, one-variable diff of the switch. It is graded as that and only that.

Also seen: the log splits into six sim runs (three arms × two seeds, `=== Phase 2b` headers), and the
`Total bad debt provision` line is identical across seeds in runs 1 and 2 (£18,743.69, £18,844.99)
and differs in run 3 (£18,637.07 vs £18,927.55).

## The substitute instrument, and its own control

Per-term `actual_net=£` lines (`<account> (<fuel>) term N (...)`) and churn-roll lines
(`<account> <date>: p_churn=… p_retain=… roll=… [*** CHURNED ***]`) per run.

- **L0 — the arm order must be established, not assumed.** Runs 1/2/3 within a seed are
  control/value/level only if the per-term columns of runs 1 and 2 are identical across seeds AND
  run 3's differs. If runs 1 or 2 differ between seeds, the value arm moved and the one-variable
  premise is void.
- **L1 — the log's per-account figure is not the published clock.** `actual_net` per term is the
  sim's own term margin, not the `settled-realised` sum `net_by_billing_account_gbp` publishes. The
  diff of summed `actual_net` between the two level runs must land within 10% of the observed
  £5,344.10 state distance to be read as the same quantity. Outside that, P1–P3 are graded on a
  different quantity and say so.

## Predictions, carried over unchanged, applied to the level-arm diff (run 3 vs run 6)

P1 (≤ 3 accounts hold ≥ 90% of the absolute difference), P2 (a roster difference: an account
settles in one seed's level run and not the other, or moves > £3,000), P3 (Herfindahl > 0.10),
P5 (gross/net > 2) — as written. **P4 cannot be graded from the log** (no priced-renewal-per-account
vector is printed) and is declared ungradable here, not quietly dropped.

**P6 (new, filed now): the switch is ONE churn outcome.** Between the two level runs, exactly one or
two accounts have a different churn-roll *outcome* at a renewal (retained in one, churned in the
other), and the account whose outcome flips is the account at the top of the P1 ranking. *Refuted
if* three or more accounts flip outcome, or if the top-ranked account's outcomes are identical in
both runs (the money moved with no change of fate: a pricing/consumption mechanism).
