**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the renewal arm prices no gas)

# PREREG — what the billing-account record filter must move, and where the run that answers it is

The fix is landed (`27c7672f7`). The measurement is in flight and is NOT this document's evidence —
this is the prediction, written while the run is running and before any of its numbers exist.

## The run

| | |
|---|---|
| unit | `ab-leg-id-fixed.service` (`systemctl --user status ab-leg-id-fixed`) |
| launched | 2026-09-07T03:46:51+01:00, its own cgroup, not the seat's |
| log | `/var/tmp/ab_leg_id_fixed.log` — `START` on entry, `END <ts> rc=<code>` on exit |
| script | `/var/tmp/ab_leg_id_fixed.sh` |
| command | `python3 -m tools.run_value_cycle_ab --level-arm --out docs/observability/value_cycle_ab_leg_id_fixed_2026-09-07.json` |
| BEFORE | `docs/observability/value_cycle_ab_gas_admitted_2026-09-07.json` |
| world | digest `39a192ce04c1eda8`, same seed, same `--level-arm` three-arm shape |

**No `END` line and a truncated log = killed from outside**, not a module failure. Relaunch the same
script under a fresh `systemd-run --user --unit=… --collect`; the tool writes only at the end, so a
death re-buys the whole run and there is nothing to resume from.

## The prediction

One variable: `observed_account_state` matches a settled row to the account by
`_billing_account_id(...)` rather than by string equality. Nothing else moved between the two runs.

1. **`no_observed_history` falls from 179 toward 0.** It should not reach 0 exactly: a gas leg whose
   first settled row is inside the term it is being renewed for has no prior book under any id, and
   that refusal is correct.
2. **`priced` rises from 94** and **`accounts_priced` rises from 66**. This is the claim. If neither
   moves, the fix bought nothing and the 158 at `product_not_upliftable` is the whole story — the
   gas legs are on `svt`/unlabelled products no arm can price, which is a fact about the market and
   not about our code, and that is what goes on the surface instead.
3. **`decisions_scored` rises from 54** and the accounts behind it from 38.
4. **`detectable_excess` (0.090496) MOVES, and I cannot sign its direction.** More decisions is a
   larger denominator and a different population — domestic gas at a third of electricity's rate,
   under a much lower cap. A rise would be the arm finding headroom it was blind to; a fall would be
   the electricity book having been the flattering half. Either is a result; predicting neither is
   the honest position and saying so now is what stops it being rationalised afterwards.
5. **`observed_share_of_what_was_detectable` (0.5830) is the one to distrust.** Numerator and
   denominator both move, so a ratio that lands near 0.58 again says nothing.

## What is NOT predicted, and why

The realised `value_advantage_gbp`. Adding renewals to a run changes churn rolls downstream, so the
two runs' rosters diverge after the first gas renewal the arm prices differently — the artefact's
own `churn_roster_diff` is what says how far. A pounds delta across a diverged roster is not a
one-variable quantity and must not be read as one.

## When it lands

Put the before/after funnel **beside**
`SEAT_RESULT_ADMITTING_GAS_MOVED_THE_REFUSAL_AND_BOUGHT_ZERO_DECISIONS_BECAUSE_THE_ARM_ASKS_FOR_THE_GAS_LEGS_BOOK_UNDER_THE_WRONG_ID_2026-09-07.md`,
not replacing it — that document holds a wrong prediction of mine next to its result and is worth
more intact. Then `python3 -m background.delivery_lane --release the-arm-cannot-find-the-gas-legs-book-because-household-of-strips-the-suffix`.
