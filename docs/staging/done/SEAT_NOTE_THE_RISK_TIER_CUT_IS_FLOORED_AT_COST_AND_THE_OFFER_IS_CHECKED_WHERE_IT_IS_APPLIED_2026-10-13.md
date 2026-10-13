**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** acquisition-and-retention-economics -- the rule is the company's own, `domain_invariants.DISCRETIONARY_RATE_NOT_BELOW_OWN_COST_FLOOR`; no new number

# The risk-tier retention cut is floored at cost, and the offer is checked where it is applied (2026-10-13)

**Fate (2026-10-13, clear-the-decks):** DONE -- 5c137eb5b B8: the risk-tier retention cut is floored at its own cost floor -- confirmed on origin.

*Direction `b8-the-risk-tiers-retention-cut-is-never-held-to-the-cost-floor`, autonomous worker.*

## What was wrong

The churn-belief tier cut (3/5/8%, `DecisionPolicy.retention_discount_for_risk`) was applied in
`simulation/run_phase2b.py` after `decide_renewal_rate` had returned and run its own floor check, and
nothing floored it. The price match always could not go under cost (`max(floor, best deal)`), so
every tiers-vs-match grade so far (a99685b68, b234e27bd) compared a cut allowed to sell below cost
with one that was not.

## The count at real inputs

Already on origin before this landing: 95b3a38d2 re-ran seed 61109 at d55598dd6 and found the only
two held renewals still below floor were both tier cuts. 68.73 x 0.92 = 63.23 against a floor of
68.34, and 64.06 x 0.97 = 62.14 against 63.61. This note cites that run and does not re-run it.

Printed after the change: a short run of `CURRENT_POLICY` to 2017-03-31, at origin 33322ee9c plus
this change (probe `/var/tmp/se-b8-tiers/probe.py`). Predictions were filed before the run in
`/var/tmp/se-b8-tiers/PREDICTIONS.txt`, and all three held:

- **P1 held.** The run completes and the new refusal never raises.
- **P2 held.** There were 20 tier calls, meaning renewals over the churn threshold, counted before
  the guard and the holdout. Left unfloored, **19 of the 20 would have offered below their own cost
  floor**. 1 got its whole tier, 7 were floored part-way, and 12 were withheld.
- **P3 held.** All 12 withheld calls are electricity re-fixes that sit at their floor to the penny,
  with 0.000% headroom. Writer 1's floor (03a0b66da) leaves them there. No call lacked a floor.
- Gas re-fixes carry 1.7-3.1% headroom, so a 3% tier mostly survives and a 5% tier is halved.

These 20 are not the "2 of 8" in 95b3a38d2. That run counted held renewals over the full window on
seed 61109, after the guard. This run counts tier calls in the first window, before the guard.

**What it means.** On the standing policy the tier cut is mostly a cut into cost. Electricity has
nothing to give once writer 1 floors it, so the standing run will now make few electricity retention
offers in the early years. This is the honest result of the rule. A margin left above the floor
would be a pricing choice to argue on its own, not something to buy back by weakening this check.

## What changed

- `company/interfaces/growth_desk.retention_cut_share_at_risk_tiers`: the tier share, taken no
  deeper than the re-fix's own cost floor. It returns None (no offer) where there is no floor, which
  is the same as the chain's writer 1, or where the re-fix already sits at or under its floor. The
  run records the reason as `the_fix_has_no_room_above_its_cost_floor`.
- `refuse_retention_offer_below_own_cost_floor` is called in the run loop where the offer's rate
  replaces the re-fix. It applies to both sizings, so a later sizing cannot sell under cost without
  the run raising.
- Both sizings read one `_price_match_inputs` floor.

**This changes the standing policy's runs.** `CURRENT_POLICY` sizes by tiers, so every offer that
used to cut through the floor is now smaller or withheld. No standing figure has been re-taken here.

## Controls

`tests/company/test_the_risk_tier_cut_is_held_to_the_cost_floor.py`, with five mutations. Each one
reds the file and the unmutated file is green:

1. drop the floor (4 red);
2. give the tier when the floor is None (1 red);
3. turn the refusal into a no-op (2 red);
4. take the run loop's refusal call out (1 red);
5. size the run loop by the bare tier (1 red).
6. return a whole tier as a float round-trip (`1 - u(1-t)/u` = 0.030000000000000027) rather than the
   tier itself (1 red). The commit gate caught this case first, in `test_run_phase2b_event_log`, before
   the control was tightened to cover it.

Two run-level tests in `tests/simulation/test_run_phase2b_event_log.py` change with the behaviour:

- The retention log's `discount_pct` is now graded as `0 < cut <= its own tier`, not as a member of
  the tier set, because a floored cut sits below its tier by design.
- The no-offer reasons accept `the_fix_has_no_room_above_its_cost_floor`.

## What is still open

The fair re-grade of tiers against price_match is now possible and has not been run. It should go
on fresh seeds at origin HEAD with this change, and it still waits on the hedge-at-quote and
value-arm-base changes the earlier fork's note named.
