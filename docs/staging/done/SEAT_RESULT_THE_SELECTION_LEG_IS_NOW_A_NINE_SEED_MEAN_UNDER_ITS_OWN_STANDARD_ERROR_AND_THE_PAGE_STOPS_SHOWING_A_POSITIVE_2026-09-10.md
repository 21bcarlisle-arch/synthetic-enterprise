# SEAT RESULT — the selection leg is a nine-seed MEAN under its own STANDARD ERROR, and the page has stopped showing a positive

**Severity:** RECORDED · **Lane:** A_strategy_governance

**Date:** 2026-09-10 (delivery seat, lane 0 draw)
**Claim:** `the-selection-leg-is-published-from-one-run-and-bounded-by-nine`
**Pre-registration:** none — see *What this record cannot claim* below, which is the honest
version of that absence rather than a missing file.

---

## What the reader met until this landed

`site/data/value_arms.json` told a reader the per-customer choosing was worth **+£319.10** — the
value arm's net minus the level arm's net out of the **one** published run — and printed
**±£1,810.50** beside it, which is the standard **deviation** of that identical contrast across
**nine** seed re-draws. `spread_to_point_estimate_ratio` divided the second by the first.

The nine-seed family's own mean of that same contrast is **−£1,078.17**, with a standard error of
**£603.50**.

So the two numbers a reader took as one statement were two correct figures over two different
populations, their ratio was not a quantity, and **the sign a reader carried away was the opposite
of the sign the best estimate we hold supports.** On the one contrast the mission turns on: the
advantage has to come from inference, the level arm *is* the baseline for the choosing, and this
was the last surface still showing the choosing in the black. The independent ranking cut already
read `worse_than_chance` at p=0.0045 and agreed in sign.

## What the feed publishes now

| field | value | over |
|---|---|---|
| `error_bar.bounds_figure_gbp` | −1,078.17 | 9 seeds (`bounds_figure_seeds: 9`) |
| `error_bar.selection_leg.bound_gbp` | 603.50 (`bound_statistic: sem_gbp`) | 9 seeds (`bound_seeds: 9`) |
| `error_bar.selection_leg.one_draw_moves_gbp` | 1,810.50 | the family's stdev — **never divided into the mean** |
| `error_bar.single_run_gbp` | 319.10 | **1 seed** (`single_run_seeds: 1`), `single_run_on_the_other_side_of_zero: true` |
| `error_bar.selection_leg.sems_from_zero` | 1.787 | against `SIGN_NEEDS_SEMS_FROM_ZERO = 1.96` |
| `error_bar.selection_leg.sign_is_stateable` | `false` → `sign: null` | |

`estimate_seeds == bound_seeds` is now an **invariant of the block that builds them**
(`_leg_over_its_own_family`), not a coincidence of today's artefacts: both come out of one call,
so they can no longer be picked up from different places.

**The honest answer is still "cannot tell", and the page says so with the nine-seed mean in front
of the reader** rather than the one-run figure:

> *"…the choosing is worth −£1,078 on average across the 9 seed re-draws — and that mean sits 1.8
> standard errors from zero against the ±£604 standard error those same 9 pin it to, short of the
> 1.96 this page requires before stating a side. So this book CANNOT RESOLVE whether the
> per-customer choosing is worth anything at all, in either direction. The single run every other
> figure on this page is drawn from is one member of those 9 and came out at £319 — on the other
> side of zero from the estimate above."*

Every number in that sentence names the population it is over, which is what the item asked for.

## The interconnection this correction broke three paragraphs away

`MORE_SEEDS_WOULD_NOT` had said, for weeks and correctly, *"More seeds would not resolve it:
re-drawing the dice measures this spread again, it does not shrink it."* That is true of the
standard **deviation**, and it was true of the gate the page ran at the time — one run against
that deviation.

**It became false the moment the estimate became the family's mean**, because a mean's standard
error falls as 1/√n and seeds are then exactly what buys the direction. Repairing which population
an estimate comes from made a sentence elsewhere on the same page wrong, with nothing in the file
able to notice: the constant and the gate never met. The constant now separates the two quantities
instead of choosing between them, and points at
`error_bar.selection_leg.seeds_needed_to_state_a_sign` — **11**, derived from the family on disk,
arithmetic on this family's mean and width and labelled as not a forecast.

The door test that pinned those exact words is now `from tools.generate_value_arms_data import
MORE_SEEDS_WOULD_NOT` and asserts the constant **reaches the reader**. It had been keyed to
today's answer, and it would have gone red on a page that became more honest.

## The control, and that it can fail

`site/test_the_baseline_comparison_reaches_the_reader.py::test_the_rendered_selection_ESTIMATE_and_its_BOUND_are_over_the_SAME_seed_count`

Keyed to the **property**: it asserts nothing about −£1,078, about nine, or about which side of
zero anything is on. It asserts the seed count behind the figure a reader meets equals the seed
count behind the bound printed beside it, that both counts are stated at all, that the count and
the figure are the **same object**, and that both reach the rendered DOM. Re-run the floor at 40
seeds and it stays green; publish a one-run figure under a forty-seed band and it reds.

**Mutation-proven from the real producer, staged into a scratch index** (this file reads the
**index** copy, so a working-tree poison proves nothing), feed regenerated from the poisoned bytes
each time. Clean run is **137 passed, 1 skipped**:

| poison | result |
|---|---|
| `_error_bar` publishes `bounds_figure_gbp: point_estimate` again — the one run, one word, everything else untouched | **3 failed** (this rung, the WHICH-FIGURE rung, the reachability rung) |
| `_error_bar` publishes `bounds_figure_seeds: 1` while the figure stays the mean | **2 failed** |
| the DOOR drops the whole `eb.selection_leg` render block | **3 failed** |
| the DOOR renders `single_run_gbp` where the estimate goes | **3 failed** |

All four counts are what the control's own docstring predicted before I ran them. The reachability half
(`test_MUTATION_an_estimate_and_a_bound_over_DIFFERENT_seed_counts_is_caught`) drives the
historical defect through the real door, requires the shared helper to raise, **and** requires the
unpoisoned feed through the same door to pass — so the rung cannot be satisfied by a guard that
refuses everything.

## What this record cannot claim

**I did not build most of this and I did not pre-register it.** The repair was already sitting
**uncommitted in the shared tree** when this tick drew the item — the claim
`the-selection-leg-is-published-from-one-run-and-bounded-by-nine` was held with `paths: []`, so
nothing had been bound and a sweep would have taken it. What this tick did is the part that was
missing, and it is the part that decides whether any of it is true:

1. Reproduced the staged feed from the working-tree producer — **5 differing leaves out of the
   whole document**, all of them `generated_at` and the publishing-tree sha. The staged bytes are
   genuinely this producer's output and not a hand-edit.
2. Found that the producer's working-tree diff carried a **foreign block** — `_the_pair_is_the_reading`
   / `read_it_beside_the_value_arm_figure`, whose only reader
   (`tests/tools/test_the_within_year_remedy_is_indexed_on_decisions.py`) is *also* uncommitted and
   belongs to the `run-the-ab-pass-and-let-the-independent-grading-reach-the-page` claim. Landing
   it here would have put a published feed block at HEAD with nothing that reads it — a
   `no_caller_and_never_runs` instance minted by a lane that does not own it. `isolate_hunks` kept
   9 of 11 hunks; the two dropped ones stay in the working tree for that claim.
3. **Regenerated the feed from the ISOLATED bytes**, not from the shared tree, because a generated
   companion built with a foreign block present publishes fields the landed producer cannot make.
   Confirmed absent: `read_it_beside_the_value_arm_figure`.
4. Graded and mutation-proved against a scratch `GIT_INDEX_FILE`, so nothing above touched the
   shared index another lane commits from.

## The first landing was REFUSED, and what it caught is the real content of this tick

The gate red-carded the first attempt with **8 failures**, and both causes were things the door
suite in the shared worktree structurally could not see:

* **`tests/tools/test_generate_value_arms_data.py` was untouched at HEAD** and pins the old
  behaviour in six places — `bounds_figure_gbp == split["selection_gbp"]`,
  `spread_to_point_estimate_ratio`, `point_estimate_inside_the_measured_band`, and the literal
  words *"More seeds would not resolve it"*. That file is the producer's unit suite; the door
  suite says nothing about it, so the whole repair looked complete while its own unit tests
  contradicted it.
* **`site/capabilities/index.html` — the DOOR — was staged and not in the path list.** It carries
  the 13 references that put `selection_leg.estimate_gbp`, `bound_gbp` and `single_run_gbp` on
  screen, and HEAD's copy has none of them. My scratch-index grading was green *because the
  shared index already held the new door*; the gate extract builds HEAD-plus-the-commit's-paths,
  so it graded the new feed against the OLD door and the two rendered legs went red. **A landing
  that leaves the door out of the pathspec grades green in the tree and red in the gate**, and
  the tree is the one place that cannot tell you.

### The fixture question the unit suite forced, and it is not a re-tune

`_floor_with_spread` builds three seeds at `(-s, 0, +s)` — sample deviation exactly `s`, **mean
exactly zero**. Under the old gate (`|one run| > s`) that was a clean instrument. Under the new
one (`|family mean| > 1.96 × sem`) a family centred on zero is 0.0 standard errors from zero
whatever `s` is, so `test_a_contrast_outside_its_seed_spread_gets_its_direction_back` became
**unpassable** and its three siblings unfalsifiable — a fixture that cannot express a direction
makes every direction test green for the wrong reason.

So `selection_mean` is now a parameter and the family's centre and its width are independently
controllable. This is the distinction that matters: **the fixture was not retuned until it agreed
with the answer** — the discriminating variable is unchanged (widen the spread, the leg withholds;
narrow it, the leg states a side), and what changed is that the fixture can now *hold* the
quantity the new gate reads. `_headline_with` defaults the family's centre to the run's own figure
because that is the **null case**: it is the state in which the old gate and the new one ask the
same question, so a test that only passes because the two populations disagree fails there instead
of on the real page.

### And one producer decision the unit suite forced

`bounds_figure_clock` was `point_clock` — the clock the published **run's** split declares. That
was right for exactly as long as the bar's subject *was* that run. It is now the family's mean, so
on a run whose split declares another basis the page would have published a real estimate with
**no clock beside it** — the one thing every financial figure here is forbidden to do, and
`test_a_split_on_another_clock_leaves_the_bar_with_NOTHING_TO_PLACE` is where it surfaced. The
bar's clock is now the floor's, which is the family's; `single_run_clock` carries the run's; and
when the run cannot be placed in the family, `single_run_seeds` is `None` rather than a `1` about
a run this page cannot place. What that test's name asks is now the narrower and true question:
the **member** has nothing to place, and the family is untouched.

**The working-tree copy of the feed was STALE and would have been the thing landed by a plain
pathspec commit.** `site/data/value_arms.json` on disk was a `12:22:41` generation with no
`sem_gbp` anywhere in the seed spreads — it predates the producer edit — while the index held the
`13:04:48` one. A pathspec stages the **working-tree** copy, so `git commit -- site/data/...` would
have published a feed with no bound to pair, and the door test reads the index, so it would have
gone red *at the commit that was supposed to fix it*.

## State of the tree this landed onto

Local `main` is **3 ahead / 9 behind `origin/main`**, and the three local commits are the head-red
untracking whose subject origin also carries (`bb5f2603e`). None of the three paths here differ
between local `HEAD` and `origin/main`, so this landing reverts nothing on either side — but the
divergence itself is somebody's next item and is **not** resolved by this one.

## What is next

* **The nine-seed floor is 11 seeds short of a stateable sign**, on its own arithmetic. That is the
  cheapest route to an answer this page has ever been able to price, and it is priced in the feed.
* `floor_decomposition` is still measured on a **different book** (104 of 2,009 priced against this
  page's 214 of 2,035), so no remedy is stated from it. Unchanged by this work.
* The `value_advantage_gbp` and `level_advantage_gbp` legs still pair a **one-run figure** against
  a nine-seed **standard deviation** via `_resolvable`. The selection leg was repaired because it
  is the thesis; the same population question is open on the other two, and `_seed_spreads` now
  publishes `sem_gbp` for all three, so the ingredients are on disk.
