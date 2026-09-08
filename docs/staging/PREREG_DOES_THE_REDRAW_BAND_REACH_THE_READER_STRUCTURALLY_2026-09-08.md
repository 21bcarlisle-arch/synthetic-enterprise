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

## What is next, and what this does NOT fix

The headline still states the band in prose as well, and that prose is still uncontrolled in its
own right — a deletion there now leaves the table standing, which is the point, but it would leave
the page saying less than it did. The durable fix is for `_leg_clause` to stop being the band's
only structured home; the table is now that home and the prose could be shortened to point at it.
Not done here: it is a generator change with its own unit-test surface and it is not what makes the
reader safe today.
