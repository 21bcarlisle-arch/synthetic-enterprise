**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration and result: which parts of the re-draw band actually reach the reader

**The prediction below was written and committed before the measurement. Filed by the delivery
seat, 2026-09-08.**

## The claim I was given, and where it is wrong

The lane-0 direction states: *"`site/data/value_arms.json` publishes GBP 2,335.87 while carrying
redraw_min GBP 450.99, redraw_mean GBP 1,450.64 and redraw_max GBP 2,433.70 in the same object, and
no HTML or JS file under `site/` mentions any band field — the reader is shown the winner of the
redraw and not the redraw."*

**The first half is true and the second half does not follow.** No HTML or JS reads
`verdict_stability.*` by name — that is correct, and it is what a grep returns. But the band still
reached the reader, because `tools/generate_value_arms_data._leg_clause` composes the min, the max,
the spread, the count that clears it and the mean into `headline`, and
`site/capabilities/index.html` renders `d.headline` verbatim at `#arms-headline`. A reader of the
live page met "spans £451 to £2,434" and "those re-draws average £1,451" already. Further,
`site/test_the_baseline_comparison_reaches_the_reader.py::test_the_figure_from_the_world_that_is_live_reaches_the_reader_and_never_as_resolved`
already asserted `redraw_min_gbp` and `redraw_max_gbp` were in the rendered text.

The direction's remedy was right and its stated cause was not. The real defect is one step in:
**the band was carried by a single opaque generator-composed string, so only two of its five
numbers had a control and no part of it could be failed on its own.** That is this project's own
named shape — a published cause authored as prose, going stale beside the measurement it describes.

## The prediction, written before the run

1. `redraw_mean_gbp` reaches the rendered page for the whole-advantage contrast and for the
   selection leg (both go through `_leg_clause`), and **no test anywhere reds if that sentence is
   deleted from the feed's headline.** The only in-repo reader of `redraw_mean_gbp` outside the
   generator is `tests/tools/test_generate_value_arms_data.py`, which checks the field's arithmetic
   and not whether a reader meets it.
2. The **level leg's** mean (£3,312) reaches the reader nowhere at all. Its clause is composed by
   `_composition_in_this_world`, which prints that leg's range and its sign change and not its
   centre.
3. Therefore, the falsifiable one: delete the `Those re-draws average {mean}` sentence from the
   live feed's headline, re-render the real door through `site/_live_harness.mjs`, and **the whole
   of `site/test_the_baseline_comparison_reaches_the_reader.py` stays green.**

## RESULT — prediction 3 confirmed

Stripping both occurrences of `Those re-draws average … the mean does.` from the live feed's
headline and driving the real door with it: **84 passed, 1 skipped.** Not one rung noticed that the
mean had been taken off the page. The mean could have been dropped from the published page by any
edit to the generator's prose, on any day, and every control in this repository would have stayed
green.

Prediction 2 held on inspection: the level leg's centre appeared in no rendered string at all.

### Why the mean is the number that carries the finding

The range on its own is the flattering reading. A reader told the advantage spans £451 to £2,434
still takes the published £2,336 as the answer. Told the same family averages £1,451, they can see
the run drew near the top of its own family. On the **choosing leg** — the only leg on that page
that could be value CREATED rather than moved — the family's centre is **−£1,861** while the
published draw is **+£2,177**. The published figure and the centre of its own family are on
opposite sides of zero. Min and max alone do not say that.

## What was done

`site/capabilities/index.html` now renders `#arms-redraw` directly under the headline, built by
`redrawBand()` from `current_world.verdict_stability.*` per contrast: published draw, number of
re-draws, lowest, **mean**, highest, and where in its own family that draw fell — for the whole
advantage and for both legs. It fails closed on every branch: no current-world run renders "No
re-draw band is shown"; a contrast carrying no family renders **NOT RE-DRAWN** in amber with its
reason, never a blank cell.

The one quantity the page derives — the ABOVE/BELOW/AT word — is asserted to agree with the feed's
own prose in `verdict_withheld_because`, so the two statements of that one fact cannot drift apart
silently.

`test_the_published_advantage_renders_beside_its_own_redraw_band` is the control. It is keyed to
the property, not to today's answer: every contrast the feed carries a checked family for must have
its min, mean and max on screen, all read from the feed, so a re-run that moves every number leaves
it green and a publish that drops a leg drops that leg's row.

### R15 — the mutations, each run against the live door and reverted

| Mutation | Result |
|---|---|
| delete `$("arms-redraw").innerHTML = redrawBand(d.current_world);` | **RED** — both new rungs |
| drop the mean column from `redrawBand` | **RED** on `redraw_mean_gbp` (`£1,451`) |
| render the whole advantage and neither leg | **RED** on the choosing row |
| strip `verdict_stability` from the feed (in-test) | **NOT RE-DRAWN** renders; mean absent |

`site/` whole: 620 passed, 34 skipped.

## What was next — DONE, later the same day

The section below is what this file left open. It is closed; the account is kept beside the
prediction rather than replacing it.

The prose home is retired. `_redraw_band_clause` no longer recites min, max and mean: it states the
placement (`sits ABOVE/BELOW/exactly AT the centre of its own family`) and names the table those
three numbers live in. The band's three edges now render in exactly one place, `#arms-redraw`,
where each fails on its own column.

**The placement stayed in both, on purpose, and it is the one thing checked for drift.** It is a
*reading* of the family, not a member of it, and no cell carries it. The door derives the same word
from two numbers already on screen and
`test_the_published_advantage_renders_beside_its_own_redraw_band` asserts the two agree.

**Three more homes for the same fact turned up while moving the first one**, all in the test
surface and each keyed to today's answer rather than to the property:

| Where | What it asserted | Now |
|---|---|---|
| `test_the_verdict_is_withheld_when_the_floors_own_redraws_reverse_it` | the literals `"£451"`, `"£2,434"`, `"£1,451"` inside the reason string | min/mean/max asserted against `verdict_stability` from the floor's own rows; the reason asserted to carry the pointer |
| `test_the_creation_leg_carries_its_own_live_world_bound_and_not_the_advantages` | all three edges present in `headline` | the edges asserted CARRIED; the count and the pointer asserted in the headline |
| `test_the_redraw_family_reaches_the_headline_on_the_branch_that_states_a_verdict` | all three edges present in the stated clause | the pointer present and the three edges **absent** — the one-home control |

The absence control lives in the generator's unit test and not at the door, because that subject's
family is substituted (£20,000/£20,100/£20,200) and cannot collide. Against the live page `£451`
is a substring of `£12,451`, and the same assertion would be a coin toss on the next re-run.

### The move off the headline was not a weakening, and that was measured

The edges came off **per-leg regions** of the headline. Landing them on a whole-table presence
check would have been the project's named fail-open the day a surface gains a second subject — and
this table has three. So `_the_bands_own_rows` cuts the table into one region per contrast and the
assertions are per row.

### R15 — the poisons, each run and reverted

| Poison | Result |
|---|---|
| swap the choosing and price-level legs' families between rows | **RED** on the choosing row — and all nine edges still on the page, so the whole-table check this replaced is **GREEN** under it (measured, not argued) |
| render every row from the whole advantage's family | **RED** on the choosing row's `redraw_min_gbp` |
| strip the band sentence from the published headline | **RED** on `_assert_the_headline_places_the_draw_in_its_family`, in the advantage's own region |
| restore the min/max/mean recital beside the pointer | **RED** on the one-home control in the generator's unit test |

`tests/tools/test_generate_value_arms_data.py`: 118 passed.
`site/test_the_baseline_comparison_reaches_the_reader.py`: 90 passed, 1 skipped.

### What this still does NOT fix

The level leg's own clause is composed by `_composition_in_this_world`, which prints that leg's
range and its sign change in prose of its own. That is a *fourth* statement of the same family,
beside the level leg's row in the table, and it was out of scope here: it is a different producer
with a different sentence and its own controls. It is the next one to collapse.
