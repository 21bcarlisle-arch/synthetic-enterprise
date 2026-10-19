# Pre-registration: what switching `next_best_action_decides_per_household` on changes

**Written 2026-10-19 ~14:10Z, before the flip.** Claim `switch-on-nba-per-household-after-the-c35-grade`
(Lane 0, seat). The flip is the next commit after this one. No run or probe was read to write it.

## What the switch is, said first

`DecisionPolicy.next_best_action_decides_per_household` (`company/policy/decision_policy.py`) is read
in exactly one place: `company.crm.next_best_action.states_for_decision`. On, the legs of one billing
account that reach a C34/C35 decision on one date become one state. Their margins are summed, they
carry one hazard, and their headroom under the default is the sum of the legs' headroom. Off, each leg
is its own decision. The defect it fixes is that, decided per leg, one household's advice is costed
twice and its retention rise is taken twice against one benefit (the worker finding of 2026-10-18).

## Who reaches it (asked of the tree at `4958a4945`, not assumed)

- **The engine does not reach it.** A grep of `company/`, `simulation/` and `saas/` finds no caller
  of `states_for_decision`, `household_state`, `next_best_action.decide`, `price_retention_rise` or
  `price_share`. The engine imports only `in_contact_holdout` from `next_best_action`, through
  `company/interfaces/contact_programme.py`. C34 and C35 are decided only inside harness
  instruments.
- **The one instrument that reaches it sets the switch itself.** `tools/retention_rise_count.main`
  builds `dataclasses.replace(CURRENT_POLICY, next_best_action_decides_per_household=per_household)`
  from its `--per-household` flag, so changing the default does not move either of its readings.
- `tools/decision_probe.py` does not import `next_best_action` at all.

## Predictions

- **N1. In any engine run, 0 decisions change, for dual households or anyone else.** The run output
  of a run at the flip's sha equals one at its parent, to the byte, at a fixed seed, apart from
  fields that record the sha or the policy's own field values. The direction asked for ("how many
  dual households' decisions change, and which way") is **none, either way**, because no production
  path makes a C34/C35 decision.
- **N2. `retention_rise_count` prints the same figures, both off and with `--per-household`,** at the
  flip's sha as at its parent, given the same probe and run output.
- **N3. The decisions that do change are the instruments' default ones.** Any caller that hands
  `states_for_decision` a standing policy (`CURRENT_POLICY` and every policy built from it, plus
  `NAIVE_POLICY`, which takes the dataclass default) now decides once per dual household instead of
  once per leg. **On the 8b6fea024 dual book, even that change is 0 decisions.** The C35 grade
  (§8 of `SEAT_PREREG_B11_C35_C34_ON_THE_FIRST_PUBLISHED_DUAL_FUEL_RUN_2026-10-18.md`, read before
  this file was finished) found that the probe writes no dual household's gas leg. Its 182 rows form
  182 single-row groups, and off and `--per-household` print the same 144/546. So 0 of the 129 dual
  households in the probe change decision, either way. On a probe that writes both legs, I expect
  the change to go in the direction of the 18 Oct finding's table: fewer decisions, and at most one
  rise per household. I give no count until that instrument exists.

## What this means for the item that asked

The item asked for a count of changed dual decisions on this book. That count is zero by
construction, so **the flip fixes the defect for the day C35 or C34 gets a production caller, and
not before.** It is still owed. The item's own reason is that it must be on before any retention
rise is switched on, and a rise switched on through a new caller would otherwise inherit per-leg
deciding silently. The control that lands with the flip asserts the property: a standing policy
decides a dual household once. It does not assert today's value of a boolean. Whoever wires C34/C35
into the engine has to make N1 false. That needs its own prediction then, measured as on against
off on a run.

**What would refute this.** If a run at the flip's sha differs from its parent in any decision or
any money figure, then a caller exists that this grep missed, and N1 is wrong.
