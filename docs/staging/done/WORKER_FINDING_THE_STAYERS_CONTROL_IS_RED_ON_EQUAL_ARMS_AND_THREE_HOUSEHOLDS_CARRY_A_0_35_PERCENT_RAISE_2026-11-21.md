**Severity:** BLOCKING · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`

# The stayers control is red on equal arms, and three households carry a 0.35% raise (2026-11-21)

`tests/simulation/test_a_save_is_not_paid_for_by_the_stayers.py::test_no_stayer_price_moves_with_the_save_price`
is the last of the 13 owed in `HEAD_RED_REGISTER.md`. It has been red for 14 census runs, first seen 2026-10-10.
The other 12 pass at origin `86db26bbd0`, where other lanes fixed them on 20 and 21 Nov (`122c7bd899` .. `4ddb8222b5`).
Each of the 12 was confirmed red at the census HEAD `19e317f44` and green at `86db26bbd0`, both in clean worktrees.

## What was run

The whole control ran at origin `86db26bbd0` in a clean worktree. It took 32 min: 7 passed and 1 failed.

- **Line 76 is GREEN.** The `on` and `placebo` arms save the same 45 households. The 14 Oct fix
  (`_rate_the_rival_sees` in `simulation/run_phase2b.py`) is still in place. So this red is the director's
  condition itself, read on equal arms. It is not a precondition failure.
- **Line 95 is RED: 118 stayer account-terms are priced differently between the arms.** A probe dumped the
  full list without truncation (`/var/tmp/se-worker-stayers-probe/out.json`).

| window | moves | raised | largest relative raise | who |
|---|---:|---:|---:|---|
| 2017 | 24 | 4 | 4e-8 | 20 prospects, 4 customers |
| 2018 Jan-May | 38 | 29 | 6e-5 | 25 customers, 13 prospects |
| 2018 Jun-Sep | 56 | 27 | **0.0035** | 33 customers, 23 prospects |

Every move below 1e-4 is at most about £0.01/MWh. There are two kinds of row:

1. **The whisper: 114 rows, both signs, |relative| < 6e-5.** It starts on 2017-02-07, the first move being a
   prospect's acquisition quote. That is before any saved term has ended. The first save is on 2016-12-31.
2. **The material raise: 4 rows, 3 households, all in July 2018, each about +0.35% on both fuels.**
   - `SYN-2016-323g` on 2018-07-15: 35.2358 → 35.3583
   - `SYN-2016-334` and `SYN-2016-334g` on 2018-07-22: 143.3803 → 143.8856 and 34.9395 → 35.0610
   - `SYN-2016-339` on 2018-07-25: 142.7476 → 143.2507

   These rows fall after the first saved electricity term ends (2018-06-20). That is the window the docstring
   names for the premium channel.

## Prediction filed before the probe, and how it graded

The prediction is at `/var/tmp/se-worker-stayers-probe/PREDICTION.txt`.

- **P1 (0.6): the moves are mostly tiny and of both signs, a numeric channel.** HALF TRUE. 114 of the 118 are.
  The other four are a uniform +0.35% raise on both fuels of each household, which a numeric whisper does not
  explain.
- **P2 (0.5): at least one raise is above 0.5%.** FALSE. The maximum is 0.352%.
- **P3 (0.6): the moves start only after the first saved term ENDS.** FALSE. They start on 2017-02-07, on
  prospects' quotes.

## Ruled out

The shared-rise and save-odds policy channels are all off in `CURRENT_POLICY`:

- `renewal_rate_bills_the_shared_rise`
- `next_best_action_shares_by_retention_rise`
- `retention_weighs_save_odds`
- `renewal_belief_by_ending_term`
- `retention_save_rate_learned_against_holdout`

The comparator (`tools/save_on_loss_notice_arms.stayer_price_moves`) uses exact equality. That is the director's
condition as written. **Loosening it to a tolerance would hide the 0.35% rows and is not the fix.**

## Attribution

A second probe dumped every log row for the three households in both arms:
`/var/tmp/se-worker-stayers-probe/probe2.py`, with output in `out2.json`. Ten logs differ. Read together:

- **The portfolio premium is NOT the channel.** `rate_decomposition_log` shows the identical premium
  component in both arms: -2.5449% on electricity, and +2.3275% / +1.446% on gas. The
  `renewal_notice_log` and `renewal_decisions_log` rows are identical between the arms.
- **The move is already in `unit_rate_original`**, the strike that enters writer 1, before any premium is
  applied. For SYN-2016-334 it is 145.3803 off against 145.8856 on, and the gas legs move by the same +0.35%.
  On electricity, writer 1 floors at `cost_floor`, so the contracted rate equals that floor and carries the
  move one for one.
- Everything else that differs is downstream of the strike: `company_churn_estimate`, `rate_vs_svt_pct`,
  `perceived_bill_saving_gbp`, `var_pct_of_term_revenue` and `own_position_vs_default` on the riding leg.

**So the save reaches stayers through the term's own strike, not the premium.** The strike is built in
`company/pricing/renewal_desk.quote_renewal`. Its inputs are:

- the company forward (`_COMPANY_ENGINE.get_forward_price` over `observable_price_records`)
- the locked policy and network costs
- `published_svt_gbp_per_mwh` and `published_market_switching_multiplier`, which feed `_apply_competitive_ceiling`

A uniform +0.35% on both fuels of each household fits an input shared across fuels. **I cannot yet say which
input it is.** The candidates are an arm-dependent world input to the ceiling, such as the switching
multiplier, and the forward engine's state.

**Next, one variable:** log `company_fwd`, `published_svt_gbp_per_mwh` and
`published_market_switching_multiplier` at `quote_renewal` (and the gas twin) for these three households, in
both arms. Then the input that differs is the channel. That takes one 32-minute pair run.

**Prediction for that run, filed now:** the switching multiplier or the published SVT differs (about 0.5),
and the company forward is identical (about 0.6). If a world-published quantity differs between arms, the
save is leaking into the world's market state, as the rival ledger did on 14 Oct. That would be a fidelity
fix in `simulation/`, not a company pricing change.

## Resolution (2026-11-21, delivery seat)

**Closed by `dd3f004de`, promoted to origin in `ac5bf2b01`.** The channel is B12's bad-debt allowance
in the strike. The belief is money-weighted per arrears cell, so a saved account's lower bill with an
unchanged loss raised the cell's share. In the 7-year `worsening` cell, ACC-SYN-2016-067 billed
1173.40 at its save against 1288.38 at its renewal, which moved the belief 0.162094 → 0.166133
(×1.00348, the whole +0.35%). The 114 whisper rows are the same channel through the large cells;
all 31 accounts whose readings differ are saved. The pre-registration and its grades are in
`/var/tmp/se-seat-stayers-belief/PREDICTION.txt`. Q1, Q2 and Q3 were all TRUE.

Fix: `default_belief(held_on_a_save=)` does not read a saved account's readings resolved on or after
its first saved term starts. The run records the company's own saves where they are billed, through
`LivePaymentTriad.account_held_on_a_save` → `PaymentObservationConsumer.account_held_on_a_save`. The
comparator's exact equality is unchanged.

**Verified on the landed bytes:** `tests/simulation/test_a_save_is_not_paid_for_by_the_stayers.py`
and the default-belief tests ran on exactly this tree under launch_long_job
(`stayers-control-rebuilt-belief-fix`): 24 passed, rc=0, 32 min (`/var/tmp/se-stayers-rebuild-ctl.done`).
The new unit control is mutation-proven both ways.

The first build's working copies were lost from the shared tree after two refused landings. This
landing is a rebuild to the design recorded in its commit message.
