**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** none — Lane 0 delivery · **Class:** measurements_that_mirror

# RESULT — the degenerate half is withdrawn at the producer, and the page's "lower bound" turned out to be attained

Discharges remedy items **1** and **2** of
`SEAT_FINDING_THE_FLOOR_DECOMPOSITIONS_REST_OF_BOOK_HALF_IS_EMPTY_ON_THIS_BOOK_SO_ITS_SHARE_IS_AN_IDENTITY_2026-09-10.md`.
Item 3 is not done and is handed on below.

**Landed:** `094d1d6c1` (producer + consumer + controls), `457bc0d77` (the attained bound).
Both promoted to origin/main and bound.

---

## What was wrong, restated as the two things that shipped

`docs/observability/value_cycle_ab_floor_decomposition.json` published
`priced_share_of_variance: 1.0`, `irreducible_sd_gbp: 0.0`, `share_is_decisive: true` with a
`share_margin_over_threshold` of **5.55 on a quantity bounded in [0, 1]**,
`larger_settled_book_would_resolve_it: true` and `priced_decisions_needed: 19`. The `except` leg
behind them returned the identical `value_advantage_gbp` — `2176.657272` — on all three seeds, over
5 accounts and 15 of the run's 350 elasticity calls. `v_except` is exactly zero, so not one of those
figures could have come out any other way.

`site/data/value_arms.json → current_world.selection_leg.what_would_settle_the_sign` said "the real
book is LARGER than this, never smaller" and named the work to pin it down: "the `only` and `except`
floor legs re-run on this book at these nine seeds — nine full three-arm passes each, not yet run."

## Item 2 — the producer withholds instead of publishing algebra

`KEYS_DERIVED_FROM_THE_REST_OF_BOOK_HALF` names the eleven keys that are an algebraic function of
`v_except`. `decompose_floor` sets every one to `None` when that variance is exactly zero, and
publishes `rest_of_book_half_is_degenerate`, `keys_withdrawn`, `why_those_keys_are_withdrawn` and
`what_would_make_the_rest_of_book_half_measurable` beside them.

**Keyed to the zero, not to a size.** No bar for "too few accounts" is set: any such bar would be a
number picked because a number was needed, and a leg over five households that returns a real spread
is a real, if imprecise, measurement.

`rest_of_book_sd_gbp` is deliberately **not** withdrawn — it is the leg's own measured spread and it
is honestly zero. `irreducible_sd_gbp` is the same number wearing the claim that no book gets under
it, and it is the claim, not the number, the empty half cannot support.

The withdrawal runs over the built dict and raises on a key it cannot find, so a rename cannot leave
a figure published under a new name.

**The self-contradiction beside it.** `what_each_count_counts` says the independent draw is the only
sample size here, `independent_draws_this_book` is `null`, and `priced_decisions_needed` was
published anyway. That is not a contradiction — `times_this_book` is scale-free and the decision
count is that multiplier in a unit — but the step between them was unstated, which is how a reader
arrives at one. `what_the_decision_unit_assumes` now states it in **both** branches: an assumption
printed only when it fails reads as an exception rather than as what the figure always rested on.

## The direction's second move is refuted, and the refutation was already on disk

The instruction was to re-run `--redraw-mode only|except` on the current book. That cannot be done,
and it is an observation rather than a derivation: the nine-seed `except` leg
(`longjob-floor-legs-20260910`, `c066c114b`) refused on its first seed after 39 minutes because the
arm's 100-account roster matched none of the 298 elasticity calls the run makes. So the artefact says
it in its own keys instead — the alternative the direction named. **The instrument got worse as the
arm got better**, and nothing was watching that direction.

## Item 1 — the page's bound is attained, not merely valid

This is the one that was live on a public surface, and it is the more interesting half.

The **maths** is right: `m = (V − V_rest)/(c² − V_rest)` rises with `V_rest`, so the published 44.9×
and 2.8× are the family's minimum and they do bound it. **Both inferences drawn from it are wrong on
this instrument.** With `V_rest` identically zero the corner is where this book actually sits, and
the legs the page pointed at cannot be run to raise it.

`_the_complement_this_bound_rests_on` reads the landed partition probe and answers empty / peopled /
cannot-say. `the_bound_is_attained` and the probe's counts are published beside the figures, so the
claim is checkable rather than taken. Matched on the world digest **and** the roster size — which is
all either artefact carries, and it says so rather than implying an account-by-account identity
neither publishes. Fail closed three ways: another world, another roster, or no count leaves the
ordinary lower-bound reading standing, which asks for a bigger book than needed.

**`is_a_lower_bound` does not flip, and that is the whole point.** Reporting an attained bound as
"not a bound" would say the arithmetic was wrong, and it is not. What an attained bound removes is
the expectation that something is coming to push it up.
`test_the_book_a_sign_would_need_is_a_lower_bound_over_every_split` is untouched and still green.

## A control corrected in place rather than deleted

`test_a_rest_of_book_ZERO_publishes_what_it_was_measured_over` asserted
`thin["priced_share_of_variance"] == fat["priced_share_of_variance"] == 1.0`. That was **true**, and
it was the defect: a 1.0 published identically over five households and over a hundred and eighty is
not a measurement. Both readings are still identical — the property the control is about — and the
identical reading is now a `None` naming its reason. The old line is kept beside the new one with why
it changed.

## What is NOT established by any of this

* **Whether the rest of the book's churn cascade moves `selection_gbp` at all.** The cascade's
  contribution measured here is zero and that is a fact about the instrument, not about the world.
  The page must not be read as saying the cascade does not matter.
* **That no seed anywhere finds a household outside the roster.** The production guard is per-seed
  and fires on the first; only seed 11111 was reached, plus a base-seed probe that agrees exactly.
  A `V_rest` measured over one household would be worth no more than the five-account one on disk.
* **Whether the published `±£1,810.50` is the right error bar for the claim it qualifies.** It is a
  defensible bound on the *selection mechanism*, which is what the leg is about. It is a
  **within-priced-book** spread and it has never varied the rest of the book, because on this book
  it cannot. That sentence is now on the page; it was not before.

## What is next — the finding's item 3, unchanged and now unblocked

**A floor keyed to something the rest of the book HAS.** The elasticity draw is the wrong key: the
complement never reaches it, and it gets *less* reachable every time the arm prices more of the book.
The quantity the rest of the book does have is its churn cascade. Until such a leg exists, no figure
on this page separates the priced households' own noise from the book's, and the page now says so in
its own words rather than implying that nine more passes would settle it.
