**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The seed price is bounded at the producer, and the census found a FOURTH instance

**Severity note:** the two unbounded counts this claim names were live on the published feed and
are now withheld with a named reason. A FOURTH instance of the same rule is identified below, is
still live on the feed, and is an open backlog item taken in the next commit of this turn.
**Filed:** 2026-09-22, delivery seat.
**Claim:** `the-producer-still-writes-an-unbounded-seed-count-into-every-artefact-it-draws`
**Pre-registration:** `docs/staging/records/PREREG_WHAT_BOUNDING_THE_SEED_COUNT_AT_THE_PRODUCER_DOES_TO_THE_LIVE_FEED_2026-09-22.md`

## Premise: LIVE, not spent

Both cited commits are ancestors of `origin/main` and the work was NOT done by another route.
5742edb1c fixed the page's `error_bar.selection_leg` key only;
`run_value_cycle_ab.distance_to_a_sign` was still emitting the bare count at that commit. The one
other live claim named by the draw's duplicate-work check is this very id held by this session.

## THE CENSUS FIRST, as the direction asked. A name match is not a consumer.

Forty-eight name matches for `seeds_needed_to_state_a_sign` across `tools/`, `site/` and `tests/`.
Classified by what each one DOES with the value:

| Site | Verdict |
|---|---|
| `run_value_cycle_ab.distance_to_a_sign` (emit) | **PRODUCER** — wrote the bare count |
| `run_value_cycle_ab` fold summary printer | **COPIES** — printed it as "it takes N seed(s)" |
| `generate_value_arms_data._auc_against_the_money_legs_price` | **COPIES** — republishes, by design and in its docstring |
| `generate_value_arms_data` rank-leg prose | **COPIES** the republished key |
| `generate_value_arms_data` `error_bar.selection_leg` | **DERIVES** — fixed by 5742edb1c |
| `generate_value_arms_data.current_world.*` | **DERIVES** — calls the producer live |
| `site/capabilities/index.html` render | **COPIES** — renders the republished key |
| remaining matches in `tests/` and docstrings | **MENTIONS** — prose about the defect, not readers |

**The census is what found the second live instance.** The item named one. The producer's output
reaches the published feed by TWO independent routes: `current_world.selection_leg` calls the
producer live, and the money leg is read out of a STORED artefact and republished. Grepping the
key alone would have found both; asking what each site does with the value is what separated the
four real consumers from the forty-four mentions.

## What was live on the feed at 5742edb1c

| key | sems from zero | bar | clears? | published |
|---|---|---|---|---|
| `current_world.distance_to_a_sign` | 24.091 | 2.306 | YES | 3 |
| `current_world.selection_leg.distance_to_a_sign` | **1.787** | 2.306 | **NO** | **14** |
| `current_world.level_leg.distance_to_a_sign` | 49.461 | 2.306 | YES | 2 |
| `…against_the_money_legs_price` | **0.686** | — | **NO** | **102** |

`14` and `102` are the unbounded quotient: the count scales as `(t·sd/|mean|)^2`, the estimate is
the DENOMINATOR, and it is quoted only when that estimate has failed its own sign bar — which is
the statement that the denominator's interval at that bar contains zero.

## What changed

**The bound is at the source.** `distance_to_a_sign` publishes an integer only when the family
clears its own bar — where the count is at most `n` and the seeds are already in hand — and
otherwise `None`, a named withholding, and a `seeds_needed_interval` carrying the two endpoint
prices one standard error either side. The gate is written as the verdict inequality, not via
`sems_from_zero`, so a zero spread reaches the branch it belongs in.

**The arithmetic is renamed, never deleted.** `seeds_at_the_point_estimate` carries it in BOTH
states. Withholding the measurement would hide the only figure in hand; publishing it as `needed`
promises that drawing that many settles the question, which is the false claim.

**The stored artefacts are re-graded, because a producer fix cannot reach them.** Every floor in
`docs/observability/` predates the bound and still carries the bare integer, and a floor costs
three decade passes at a 6.4 GB peak per seed — re-drawing to re-grade a key is not a remedy
anyone would spend. `_regrade_a_stored_distance_block` applies the gate to the block's OWN
published `sems_from_zero` and bar. It re-grades and does not re-price: no count is recomputed,
because a second implementation of the price is the drift republication exists to avoid. Blocks
from the bounded producer pass through untouched, detected by the key only that producer
writes — not by a date or commit stamp, since artefacts here are folded ACROSS commits.

**The absence is on the surface, in three places.** The CLI summary read the withheld count as
"infinitely many", spelling a zero mean, an exhausted search and an unbounded price as one
sentence. The page's prose fell through to a full stop. The page's JavaScript dropped the clause.
All three now state the withholding and why — "no price exists" and "nobody costed it" are
opposite readings and only one of them is true.

## The control was kept and re-pointed, not deleted

`test_the_seed_count_and_the_published_verdict_are_the_same_inequality` cross-checks two spellings
of one inequality and is worth keeping. Reading the inversion off the now-gated key would have left
it comparing the two spellings over the CLEARING HALF ALONE and taking the failing half on the
`None` branch — half the partition, with a green that looked identical. It now reads
`seeds_at_the_point_estimate`, which is the same inverting expression published in both states, so
the cross-check survives at full width. A new leg asserts the gate itself over the same straddling
sweep. **Mutation-proven:** forcing `clears_bar = True` reds it at the new leg. The sweep reaches
278 published counts and 406 withheld, so neither branch is theoretical.

## Predictions, all six held

`14`→`None` (point estimate 14, endpoints 7 and 59); `102`→`None` (point estimate 102); the two
clearing families kept `3` and `2` unchanged; `error_bar.selection_leg` untouched at `None`; bare
unbounded counts on the feed **2 → 0**; the control still straddles.

Green: 362 in the two tool suites, 880 in the whole site lane.

## THE FOURTH INSTANCE — found by the census, NOT fixed here

`_auc_against_its_own_null` computes
`rosters_needed = ceil((_AUC_SDS_TO_STATE_A_SIGN / |sds_from_chance|)^2)` and publishes it as a
bare `rosters_needed_to_state_a_sign`, live on the feed as **4** against `rosters_in_hand: 1`.

**This is the same quotient with the same estimate in the same position.** The denominator is the
observed distance in null SDs; the count is asked only when that distance has failed its bar; a
denominator that may be zero prices the question at no finite number of rosters. It fails its bar
right now — 4 rosters needed against 1 in hand.

It renders in the SAME SENTENCE as the money-leg seed price on
`site/capabilities/index.html`. Leaving one bounded and one bare in one sentence is not a
smaller version of this defect; it is the VAT shape reproduced inside a single line of prose, with
the two halves now disagreeing about whether an unbounded count may be printed.

**Next**: bound it on the same rule — `rosters_at_the_point_estimate` always,
`rosters_needed_to_state_a_sign` only when `|sds_from_chance|` clears
`_AUC_SDS_TO_STATE_A_SIGN`, named withholding otherwise. The endpoints are clean here: the
statistic's standard error is one null SD by construction, so the denominator's own interval is
`sds_from_chance ∓ 1`. Handed on rather than folded in, so this landing stays one reviewable claim.

## What this cost, and the rule it pays

Three commits removed this defect one instance at a time — 06e316ae4, 5742edb1c, and this one —
because each fixed the reader it met rather than the rule. The rule is: **a count whose
denominator is an estimate asked only in the state where that estimate may be zero has no upper
bound, and may not be published as an integer.** The fourth instance above was found in forty
seconds once the rule was stated as a rule, and it had been sitting beside the third one on the
same page line the whole time.
