**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`

# FINDING — the size term turned the book's smallest accounts from floor-bound to ceiling-bound, and the only thing that noticed was a control pinned to the old answer

Found 2026-09-25 while landing the Lane 0 claim `bill-stress-hazard-from-the-arrears-ledger`. Two
test modules in the churn/pricing subject were RED AT HEAD and absent from
`docs/staging/reference/HEAD_RED_REGISTER.md`; both reds are residue of `3b01193a8` (2026-09-23),
the commit that bounded the refuted bill-stress knee and added the SIZE TERM beside it. The reds
are repaired in this commit. **The behaviour change underneath one of them is not, and it is the
finding.**

## What was measured

`decide_margin(arm=VALUE_BASED)` at the real micro-consumption shape the earlier walk found —
5 accounts, 190–340 kWh/year, 98.55 GBP standing charge, cost to serve 6.00 GBP/yr, one period,
ceiling 250 GBP/MWh — and the company's own P(leave) at a 50% rise for the same consumptions:

| EAC kWh/yr | chosen margin GBP/MWh | `endpoint_side` | P(leave) at +50% |
|---|---|---|---|
| 200 | 100.00 | `ceiling` | 0.092 |
| 340 | 100.00 | `ceiling` | 0.114 |
| 1,000 | 100.00 | `ceiling` | 0.220 |
| 2,500 (TDCV Medium) | 35.25 | interior | 0.460 |

Before `3b01193a8` the 200 kWh account chose **0.50 GBP/MWh — the floor**. The arm now prices it
at the top of everything it is allowed to offer.

## Why, and it is not a defect in the size term

The size term is sourced and right: a percentage is not a quantity a household responds to, pounds
are, and `size_scale = annual_consumption_kwh / SIZE_REFERENCE_KWH_ELEC` scales the rate response
accordingly. A 200 kWh household's 50% rise is about 12 GBP a year. The model now says — correctly
— that such a household barely responds to price. The value arm reads that and does the only thing
a maximiser can do with a rate-insensitive customer: charge the most it is permitted to.

**So the model became more honest and the decision it feeds became less defensible**, and nothing
in the tree connects those two sentences. That is the shape worth the finding: the size term was
argued, sourced and controlled as a BELIEF, and the belief feeds a DECISION whose behaviour at the
extreme of the new function nobody looked at.

## What is NOT claimed here

- That the arm is wrong. It is doing what expected value says. The question is whether a book that
  charges its smallest, least-engaged accounts the ceiling is one this company wants, and that is
  the director's, not a test's.
- That the fairness bound is absent. `max_offered_rate_gbp_per_mwh` and the support bound both
  bind here and the chosen 100.00 is the top of what they allow — the arm is not unbounded, it is
  at its bound. `endpoint_side` says so on every one of these decisions, which is exactly what
  that field was added for, and it is the only reason this was findable at all.
- Any number for what the smallest accounts *should* be charged. None is established.

## The two reds, and what was done with them

* `tests/company/crm/test_captive_floor_and_market_netting.py::test_every_estimate_BELOW_the_elbow_is_unchanged_because_the_calibration_was_not_touched`
  — its probe passed `3100.0` as the fourth positional argument under the stale name
  `prev_annual_bill_gbp`; the fourth positional is `annual_consumption_kwh`. Harmless until the
  size term made consumption load-bearing. **Repaired** by consuming `SIZE_REFERENCE_KWH_ELEC`, so
  `size_scale` is exactly 1.0 and the frozen numbers again say what they claim — that the
  SATURATION moved nothing. Keyed to the property: a future size-term change cannot red this file,
  a change to the elbow still does.
* `tests/company/pricing/test_value_based_renewal.py::test_a_FLOOR_bound_choice_is_not_reported_as_the_arm_STRAINING_UPWARD`
  — pinned to those same five accounts, i.e. to yesterday's answer. **Repaired** by keying it to
  the property (fixed revenue dominating the commodity leg is still floor-bound; a
  standing-charge-led 3,100 kWh account at 300 GBP/yr is the live example) and by adding a
  partition control asserting `floor`, `ceiling` and interior are all reachable, which no previous
  leg required.

## The coupling worth naming

Both reds are two days old and neither is in the HEAD-red register, which
`SEAT_FINDING_A_GENUINELY_RED_ARCHITECTURE_TEST_IS_ABSENT_FROM_THE_REGISTER_THAT_NOW_GRADES_THE_MAP_2026-09-25`
already reports as two census runs stale. This is a second independent instance of that finding's
subject on a different lane, which raises its severity rather than duplicating it: the register is
now load-bearing for the maturity map's own silence.

A THIRD unregistered red was found in the same sweep and is NOT repaired here, because it is a
different lane's subject and a drive-by would be a guess:
`tests/company/billing/test_the_statement_shows_how_each_bill_reached_its_number.py::test_the_vat_charged_on_every_catchup_bill_matches_the_NET_base_across_the_real_book`,
red at `17a88051c`, reproduced in a clean worktree at HEAD. A FOURTH, same sweep, same status --
`tests/tools/test_the_feed_check_can_grade_the_working_tree.py::test_the_churn_belief_chain_is_actually_walked`,
reproduced in a clean worktree at `f465f3663`: `docs/observability/churn_belief_size_response.json`
is in `WATCHED_DERIVED_ARTEFACTS` and its generator produces no row for it, so the test's own
words apply to itself -- *"a watched derived artefact was never produced by the generator that owns
it, so nothing compared it and the sweep below is over an empty set"*. That is on the same
publisher this commit's sibling touches, and it is the reason this finding does not also claim the
churn-belief page is being checked.

So FOUR genuine reds were found by one commit's ordinary test selection and none of the four is in
the register. The register's observation store holds 37 rows; the number of actual reds at HEAD is
at least 41, and nobody can say what it is, which is the thing that matters rather than the
arithmetic.

## Falsifier

If the arm's behaviour at 200 kWh is later argued to be correct AND the director accepts pricing
the smallest accounts at the ceiling, this finding closes with that ruling recorded beside it. If
instead a bound is added, the control to write is one asserting that the arm's choice for a
micro-consumption account is NOT the top of the permitted range — keyed to the property, not to
whatever number the bound lands on.
