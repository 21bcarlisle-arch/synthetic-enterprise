# [WORKER FINDING] The arms page's error bar bounded the superseded selection leg while the headline stated the realised one

**Severity:** LATENT · **Lane:** H_harness · **Raised:** 2026-08-29 · **Rank:** consolidated, no independent rank

LATENT and not BLOCKING: nothing was wedged and the page published. It was a published ratio whose
two sides count different quantities, and a derived sentence about a figure the page does not
state — an R14 defect on a live surface, not an obstruction to any lane.

**One line:** `site/data/value_arms.json` published `spread_to_point_estimate_ratio` = 5.69 and
`point_estimate_inside_the_measured_band` = `true` by dividing a **settled-realised** seed spread
(£2,577.80) by the **settled-provisioned** selection leg (£453.43), while the headline four
paragraphs above stated the settled-realised leg (£1,815.79) — which is *outside* the same band, at
a ratio of 1.42.

## Class registration

Belongs to `figures_on_a_superseded_clock`. Third instance, filed at the severity it had when
found. Written after its own repair, on the same rule the first instance records: the defect was
found and fixed inside a Lane 0 claim, and a class needs its instances as documents rather than as
commit archaeology.

## Observed, with evidence

`site/data/value_arms.json` as published at commit `3f6c29525`, and the clock-matched values
beside it:

```
                                        published        clock-matched
selection leg the bar bounded            £453.43         £1,815.79
spread_to_point_estimate_ratio             5.69              1.42
point_estimate_inside_the_measured_band    true             false
band the spread was measured over    -£4,273.97 .. +£872.96 (both cases)
```

The two legs are £1,362.36 apart. Every row the spread is computed from is read out of
`level_vs_selection` (`tools/run_value_cycle_ab.py:2535`), which declares `settled-realised`.

## Why it survived

`tools/generate_value_arms_data.py` already stated the correct rule, three functions above the
defect. `_provisioned.no_spread_on_this_clock` says in terms:

> "No seed spread has ever been measured on this superseded clock, so the figure above is a SIZE
> and not a direction … there is no artefact anywhere in this repo that could bound a provisioned
> contrast."

And then `build` handed `_error_bar` exactly that provisioned contrast. **One file, two functions,
opposite answers** — and the prose one was the correct one, so reading the module's own
documentation would have confirmed the defect rather than revealed it.

The control that should have caught it asked the same wrong question:
`test_the_selection_leg_and_its_error_bar_are_published_together` read `real["provisioned"]`, so
the test and the generator agreed with each other and neither was checked against the headline.
**A control that draws its subject from the same place as the code it checks cannot see a subject
error.**

Direction matters: the wrong pairing produced the *reassuring* answer. "The point estimate sits
inside that band" is the sentence a reader trusts most on that page, and the clock-matched truth is
that the estimate has left its own band.

## What repaired it

Same turn, commit below.

- `build` takes the point estimate from `realised.split`, which is available **only** when the
  split declares `settled-realised` — so the clock match is a property of where the figure came
  from, not a claim made at the call site.
- `error_bar` republishes `bounds_figure_gbp` / `bounds_figure_clock`, which makes the pairing a
  **reconciliation between two published fields** rather than something a reader must infer from
  position. The door renders both.
- `point_estimate_inside_the_measured_band` is a tri-state and its reading was a two-branch
  ternary, so `None` — "no figure on this spread's clock to place" — rendered as the measured
  claim "the point estimate now sits OUTSIDE the band". Three branches now.

Controls, each mutation run and reverted:

| mutation | reds |
|---|---|
| `point` ← provisioned (the defect, reinstated) | `test_the_error_bar_bounds_the_FIGURE_THE_HEADLINE_STATES`, `test_a_split_on_another_clock_leaves_the_bar_with_NOTHING_TO_PLACE` |
| tri-state collapsed back to two branches | `test_a_split_on_another_clock_leaves_the_bar_with_NOTHING_TO_PLACE` |
| drop the `bounds_figure_clock` provenance field | `test_the_error_bar_bounds_the_FIGURE_THE_HEADLINE_STATES` |
| delete the render clause from the door | `test_the_page_says_WHICH_FIGURE_the_error_bar_is_a_bar_on` |

Null rungs — the real artefacts fully published, the spread still published as a size in the
unknown branch — stay green under all four.

## What this class is now owed

Two of the three instances were found *inside the same file's own docstrings*, which already
stated the rule they broke. The class's open question is no longer "do we know the rule" but
**"which published ratios have never been checked that their two sides count one quantity?"** The
durable shape is the one used here: publish what a figure is *of*, beside it, so the pairing is
reconcilable from the artefact instead of from a docstring.

Still owed on this surface, unchanged by this repair and named rather than left:
`error_bar.clock_caveat` does not empty until a `--noise-floor` run carries the clock label the
producer now writes.
