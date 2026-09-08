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

---

# PRE-REGISTRATION 2 — collapsing the FOURTH home, and what must NOT move

**2026-09-08, later. Lane 0 delivery, `the-level-legs-clause-is-the-bands-fourth-home`.** Written
and landed BEFORE the edit, so the predictions below can refute the diagnosis rather than describe
it. The account is appended under this section, beside them, never in place of them.

## The premise, re-measured at draw time

Alive. `656a45f54` is an ancestor of `origin/main` and its own message names this residue as still
open. At `fdc16f4c6` the recital is still in the tree:
`_composition_in_this_world` composes `the level leg runs {lo} to {hi} and CHANGES SIGN` from
`min(measured)`/`max(measured)` over `floor_current["seeds"][*]["level_advantage_gbp"]` — the same
rows `_verdict_stability(floor_current, bound, LEVEL_CONTRAST)` reduces to `redraw_min_gbp` and
`redraw_max_gbp`, which `#arms-redraw` renders as the price-level row's Lowest and Highest cells.

## What the item did not know, and it changes what "done" can claim

**On today's publish the refusal does not fire.** `current_world.composition.readable` is `true`
and `why_not_readable` is `null`, because this world's level leg is sign-stable: £18,582 /
£20,337 / £19,569, all positive. So the fourth home is **latent, not live** — it is a sentence that
becomes a second home for the price-level row's numbers on any world whose level leg straddles
zero, which is the state the leg was in as recently as the `NOISE_FLOOR_ONLY_LIVE` floor
(-£882.45 / +£1,733.38 / +£9,085.08).

That is a weaker claim than "a reader is meeting two homes today" and it is the true one. It also
says where the control has to live: on the substituted straddling floor, in the generator's unit
test, not at the door.

## Predictions — filed before the edit

1. **No published byte moves.** `site/data/value_arms.json` regenerates identical, because the
   branch being edited is unreachable on this world's floor. If any published figure or sentence
   moves, the diagnosis above is **wrong** — it would mean the refusal fires somewhere I have not
   found — and the finding is that, not the collapse.
2. On the straddling floor the refusal will carry a **pointer** at the band table and will contain
   **neither** `£-882.45` **nor** `£9,085.08`, while `level_leg.verdict_stability` carries both.
3. `min(measured)` and `max(measured)` will equal `redraw_min_gbp` and `redraw_max_gbp` **exactly**
   on that subject. This is asserted, not assumed: a pointer at a table holding different numbers
   is worse than the recital it replaced, and two routes to one number is this file's named cost.
4. **The share range stays in prose.** `The share itself spans {slo} to {shi}` is a range of
   `level_share_of_advantage`, a ratio; `#arms-redraw` has three sterling columns and no share
   column, so the table is not its home and retiring it would be a **deletion dressed as a
   collapse**. Same test as `656a45f54` applied to the placement word: what stays is what no cell
   carries.
5. **`CHANGES SIGN` stays**, for the same reason. It is a *reading* of the family, not a member of
   it. `test_the_level_share_is_refused_when_its_numerator_has_no_sign` keys to that string and
   must stay green with nothing edited in it.
6. **The door file stays green with no edit.** `_composition_defects` matches
   `_door_prose(why_not_readable)[:80]`; the first 80 characters are before the clause being
   replaced. Predicted: 90 passed, 1 skipped, unchanged.
7. **The pointer must be fail-closed and the fallback must be reachable.** Where the table's
   price-level row carries no family — no bound read in this world, or a seed row missing the
   contrast — the refusal must **recite the numbers**, because then prose is the only home and a
   pointer would send the reader to an amber `NOT RE-DRAWN` cell. Predicted: a two-subject control
   where `level_stability` is the ONLY thing that moves renders two different refusals.

## The poisons to be run, and what each must red

| Poison | Predicted |
|---|---|
| restore the min/max recital beside the pointer | **RED** on the new one-home control, and only there |
| point at the table with `level_stability` not `checked` | **RED** on the fallback leg of the same control |
| substitute the whole advantage's family for the level leg's | **RED** on the identity assert (prediction 3) |
| drop `CHANGES SIGN` | **RED** on the existing sign control, untouched |

## The account — measured, beside the predictions and not in place of them

**Done.** `_the_level_legs_family` is the one producer of that clause. On a world whose price-level
row carries a family the refusal says *"Its own lowest, mean and highest are the price-level row of
the re-draw band table higher up this section"*; the two edges are gone from it. `#arms-redraw` is
now the family's only numeric home for **all three** contrasts.

| Prediction | Result |
|---|---|
| 1 — no published byte moves | **HELD.** The feed regenerated with only `generated_at` and `publishing_tree_commit` moved; every figure and every sentence byte-identical, so the feed was not committed |
| 2 — pointer, and neither edge in the refusal | **HELD** |
| 3 — `min(measured)` == `redraw_min_gbp` exactly | **HELD** (`-1302.9943640000129` / `8664.540695999982` off the floor's own rows) |
| 4 — the share range stays | **HELD** — `-124.5%` to `28451.6%` still published; no table column holds a ratio |
| 5 — `CHANGES SIGN` stays, sign control untouched and green | **HELD** |
| 6 — door green with no edit | **HELD.** 91 passed, 1 skipped (I predicted 90 — a rung landed from another lane between the prediction and the run; the substance, green with nothing edited, held) |
| 7 — the fallback is reachable and recites | **HELD** |

### R15 — the poisons, each run against the real builder and reverted

| Poison | Predicted | Measured |
|---|---|---|
| restore the min/max recital beside the pointer | RED on the one-home control, only there | **RED**, 118 others passed |
| render the pointer where `checked` is False | RED on the fallback leg | **RED** |
| hand the WHOLE ADVANTAGE's family over as the level leg's | RED on the identity assert | **SURVIVED — 119 passed.** See below |
| drop `CHANGES SIGN` | RED on the existing sign control | **RED** — that control plus two others |

### The prediction that was wrong, and it was a missing test rather than an equivalence

Poison 3 survived, and the reason is worth more than the poison. The identity assert reads the
edges from `level_leg.verdict_stability` — the leg's own block — so it cannot see WHICH family the
build handed to the composition. And the pointer branch reads no number out of the family it is
given: it only asks whether it is `checked`. On that subject both families are checked, so
substituting one for the other changed nothing observable.

That is a real fail-open, not an equivalence. The hazard is a page that points at the price-level
row while that row renders an amber **NOT RE-DRAWN** — the two edges then reach a reader in
neither place, which is strictly worse than the recital this work retired.

The witness is a floor where the two families **disagree** about being checked: one seed row short
of `level_advantage_gbp`, nothing else touched. `_verdict_stability` refuses that leg (no bound is
read) while the whole advantage's own family still checks, and the refusal's `measured` drops the
short row and still holds two straddling draws. Handing the wrong family over then prints the
pointer where the recital was owed. With that leg added, poison 3 **REDS**.

Kept here rather than quietly folded into the design: a control keyed to the leg's own block
looked like it was checking the wiring and was blind to it, which is this project's named
`calls-the-estimator-directly` shape one layer along.

### What this does NOT close

The two producers point at the same table in two sentences that describe it from two different
places on the page — `#arms-composition` sits below `#arms-redraw`, so neither can reuse the
other's words. They share the property, which is controlled, and not the prose, which is not: a
table renamed or moved would leave whichever producer was not touched describing it wrongly. That
is a smaller defect than the one closed here and no control is proposed for it.
