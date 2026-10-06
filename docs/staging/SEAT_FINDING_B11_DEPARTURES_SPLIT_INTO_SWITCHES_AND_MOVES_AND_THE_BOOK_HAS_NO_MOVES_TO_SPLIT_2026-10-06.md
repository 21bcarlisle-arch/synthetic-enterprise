**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history`

# B11 slice 4: departures split into switches and moves, and the book we run has no moves to split

## What was built

`company/analytics/forward_clv.py`:

- `move_outs_from_run_output` reads the run's `home_move_outs` register. It takes `household` and
  `move_date` only, which is what a supplier learns from a move-out notice and its final read. The
  register's `journey_state` and `catchable` belong to the world and are not read.
- With no register it returns `None`, and the backtest carries `LIMITATION_NO_MOVE_REGISTER` and a
  `None` split. That is not the same as `{}`, which means "nobody moved".
- `run_backtest(move_out_month_by_account=)` counts the fit and held-back departures as switch or
  move. A departure is a move only when its last supplied month is the account's move-out month,
  so an account that switched away before a later move date counts as a switch.
- It also fits `switch_hazard_by_contract_year`, with each move censored at its date.
- The forecast's survival stays all-cause, because margin stops however the account leaves.
  A test holds this.
- `backtest_run_output` passes the register through.

Four tests. Eight mutations, each red. A ninth first crashed on an unbound name instead of reddening
a test. It was rewritten as "censor moves inside the forecast's own hazard fit" and then went red.

## What the tracked run says

`docs/reports/run_output_latest.json` has no `home_move_outs`. The world generates moves only behind
`docs/design/curriculum/home_moves_activation.json`, which is **off**. Its stated reason is that the
incoming deemed occupant is not yet supplied (B7 slice 3). So on the book we run, every departure has
a switching cause, and the split is `None` with its reason.

The old limitation text implied a gap on the company side ("the book records only that supply
ended"). In fact the cause is in the world. B7's frame finding said this first: `home_move_won` is
rolled on every churn whatever its cause, so the run has never had a move as a way to leave.

## What this unblocks and what it does not

- **Unblocks:** C34 can price a retention action against the switch hazard rather than the
  all-cause one, as soon as a book carries moves.
- **Does not unblock:** grading. A run with moves needs B7 slice 3 and then the director's switch on
  the curriculum file. That file already carries the recommendation, so there is no new ask.
- **Still open, unchanged:**
  - B11's production caller, which needs book count first (EP17, the director's open row).
  - L2 VERIFY.

Level stays at 1.
