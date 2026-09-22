# PRE-REGISTRATION — what bounding the roster price at its producer does

**Filed:** 2026-09-22, BEFORE the change is written and BEFORE the feed is regenerated.
**Subject:** `tools/generate_value_arms_data._rosters_to_state_a_sign`.
**Why pre-registered:** the money-leg equivalent (964036259) filed six predictions and all six held.
An identical claim about the mirror leg is only evidence if it is written down first.

## The defect being repaired

`rosters_needed_to_state_a_sign` is `ceil((1.96 / |sds_from_chance|)^2)`. `sds_from_chance` is
`(auc - 0.5) / null_sd` — an ESTIMATE, and it sits in the DENOMINATOR. The count is asked only
where the reading has failed `clears_its_own_null`, which IS the statement that the denominator's
interval at that bar contains zero. A denominator that may be zero gives a quotient with no upper
bound. This is the FOURTH instance of the rule 06e316ae4, 5742edb1c and 964036259 each removed one
instance of; it was found by 964036259's census and filed rather than folded in.

**One difference from the money leg, stated so it is not read as an oversight:** the money leg's
error is `sd/sqrt(n)`, ESTIMATED from the same draws, which is why its bar is a t point that widens
with `n`. Here `null_sd` is `sqrt((n1+n2+1)/(12*n1*n2))` — an exact function of the two outcome
counts, estimated from nothing. So the error unit is exact and the bar is the normal point. The
denominator's interval is therefore `sds_from_chance ± 1` in standardised units, which is one exact
null SD either side, and NOT a t interval. The gate is still keyed to the verdict the artefact
publishes, so the two cannot drift.

## Predictions

**P1.** The live block at `error_bar/discrimination_across_the_family/against_the_statistics_own_null/
rosters_to_state_a_sign` flips `rosters_needed_to_state_a_sign` from `4` to `null`, because its
`sds_from_chance` is 1.0840 against a 1.9600 bar and so fails it.

**P2.** `rosters_at_the_point_estimate` carries `4` in the new block — the arithmetic is renamed out
of the grammar of a plan, not deleted.

**P3.** The two published endpoints are the denominator one exact null SD either side: 0.08403 →
**545 rosters**, and 2.08403 → **1 roster**. They come back in the opposite order to the bounds that
produced them, and 545 against a point estimate of 4 is the evidence the quantity diverges rather
than interpolates.

**P4.** This family's one-error interval [0.0840, 2.0840] does NOT contain zero, but its interval AT
ITS OWN SIGN BAR [-0.8759, 3.0440] does. So `these_two_are_not_a_range` must render the "at its own
sign bar" wording, not the bare one. If it renders the bare wording the conditional is inverted.

**P5.** `tests/tools/test_generate_value_arms_data.py` monotonicity leg reds BEFORE repair with a
`TypeError`, not an assertion failure: `near = _rosters_to_state_a_sign(1.0)` fails the bar so its
count becomes `None`, `far = _rosters_to_state_a_sign(2.5)` clears it and stays `1`, and `None > 1`
is not comparable. The leg is KEPT and re-pointed at the point estimate, where the property it
asserts — the price falls as the reading moves from chance — is true over the WHOLE partition
rather than over the clearing half alone.

**P6.** `site/test_the_baseline_comparison_reaches_the_reader.py::
test_the_two_prices_NEVER_render_without_the_unit_that_makes_them_comparable` stays GREEN without
being edited: it drives a CONSTRUCTED feed that carries the count, so it exercises the clearing-state
render, which still prints. If it reds, the render was keyed to the wrong thing.

**P7.** The page prose stops saying "about 4 independent ROSTERS". Both legs of that sentence are now
withheld — the money leg already carries no price on this family — so the sentence must say that
NEITHER question is costed and why, rather than falling through to a full stop. "No price exists"
and "nobody costed it" are opposite readings and the second is the one silence spells.

**P8.** Bare unbounded roster counts reachable on the live feed: 1 before, 0 after.

## What would refute the frame rather than the numbers

If the clearing state turned out to be unreachable — i.e. if no roster reading can ever clear its
own null — then the gate would be a guard that refuses everything and passes every test written
about it (CLAUDE.md's rare-branch trap). The control must therefore assert the partition is
INHABITED on both sides before asserting what each side does.
