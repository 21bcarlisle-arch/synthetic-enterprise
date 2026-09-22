# PRE-REGISTRATION — what bounding the seed count AT THE PRODUCER does to the live feed

**Severity:** INFO (pre-registration; the finding it serves is filed separately)
**Filed:** 2026-09-22, delivery seat, before any regeneration.
**Claim:** `the-producer-still-writes-an-unbounded-seed-count-into-every-artefact-it-draws`

## What is being changed

`tools/run_value_cycle_ab.distance_to_a_sign` writes `seeds_needed_to_state_a_sign` as a bare
integer into every artefact it draws. The count solves `|m| > t(k-1)·s/sqrt(k)` for `k`, so the
ESTIMATE IS THE DENOMINATOR and the quotient has no upper bound when that denominator's own
interval contains zero. `generate_value_arms_data._seed_price_interval` established this on
2026-09-22 and 5742edb1c applied it to the page only — the producer was left writing the bare
count, so every artefact on disk still carries it and the next consumer rebuilds the defect.

The change bounds it at the source, on the same rule: an integer only when the denominator's
interval at the family's OWN bar excludes zero (which is exactly `clears the bar`), otherwise
`None` plus a named withholding and the two priced endpoints one standard error either side.

## The state of the feed BEFORE, read off `site/data/value_arms.json` at 5742edb1c

| key | `sems_from_zero` | bar | clears? | count published |
|---|---|---|---|---|
| `current_world.distance_to_a_sign` | 24.091 | 2.306 | YES | 3 |
| `current_world.selection_leg.distance_to_a_sign` | **1.787** | 2.306 | **NO** | **14** |
| `current_world.level_leg.distance_to_a_sign` | 49.461 | 2.306 | YES | 2 |
| `error_bar.selection_leg` (page-derived) | 2.495 | 2.110 | YES | None |
| `…against_the_money_legs_price` | 0.686 | — | **NO** | **102** |

**TWO live unbounded counts, not one.** The item named the producer; the census found that its
output reaches the published feed by two independent routes — the `current_world` selection leg
directly, and the money leg republished through `_auc_against_the_money_legs_price`, whose
docstring says in terms that it "republishes and does not recompute". That republication was the
right call when the producer's figure was believed sound and is precisely what carries the defect
now.

## Predictions, written before the run

1. `current_world.selection_leg.distance_to_a_sign.seeds_needed_to_state_a_sign`: `14` → `None`,
   with `seeds_needed_unavailable_because` non-empty and a `seeds_needed_interval` block carrying
   `at_the_point_estimate: 14` and two endpoint prices.
2. `…against_the_money_legs_price.money_leg_seeds_needed_to_state_a_sign`: `102` → `None`.
3. The two families that CLEAR their bar keep their integers unchanged: `3` and `2`. If either
   moves, the rule was keyed to something other than the property and the change is wrong.
4. `error_bar.selection_leg.seeds_needed_to_state_a_sign` stays `None` — already derived by
   5742edb1c; this change must not touch it.
5. Bare unbounded counts on the published feed: **2 → 0**.
6. The arithmetic is NOT deleted. `seeds_at_the_point_estimate` carries it in BOTH states, so
   `test_the_seed_count_and_the_published_verdict_are_the_same_inequality` keeps cross-checking
   two spellings of one inequality across the whole sweep rather than over the clearing half only.
   That control is re-pointed, never weakened: if it can only reach one verdict after the change,
   the change is wrong.

## What would refute this

- Prediction 3 failing: a clearing family losing its count means the guard read the verdict's
  current ANSWER rather than the denominator's interval.
- Prediction 6 failing (`stateable` or `unstateable` reaching zero in the sweep) means the control
  became a comparison of one answer with itself, which is the shape it was written against.

## Known consequence, not a prediction

`site/test_the_baseline_comparison_reaches_the_reader.py:7561` pins `102` in a fixture and
`site/test_the_selection_legs_bias_size_reaches_the_reader.py:331` reads the key. Fixtures pinned
to the shape the change removes will red; that is the door working, not a refutation.
