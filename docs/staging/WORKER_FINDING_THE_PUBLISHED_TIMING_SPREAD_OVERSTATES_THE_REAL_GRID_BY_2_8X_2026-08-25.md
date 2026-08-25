**Severity:** BLOCKING · **Lane:** W4_the_wall

**Discharged:** `site/test_explore_second_clock.py::test_the_SPREAD_is_never_shown_without_its_MEASURED_correction`,
`tests/tools/test_grid_intensity_feed_and_explore_carbon.py::test_a_year_sharing_ONE_half_hour_does_not_count_toward_the_headline`,
`tests/tools/test_grid_intensity_feed_and_explore_carbon.py::test_the_headline_says_we_OVERSTATE_and_by_how_much`
— landed `145b90074`, 2026-08-25, and **the finding was RIGHT when it was written rather than
wrong now.** The first node is the falsifier that matters: it renders the real page through its
own boot path and fails if the spread ever appears without the measured correction beside it,
which is exactly the sentence this document was filed about. Mutation-proven by restoring the
pre-correction wording verbatim — red, then green on restore.

The other two close the half the finding did not know it had. The headline was 2.85x on its
first computation because 2018 shared exactly ONE half hour with the published series, giving a
spread of 1.0 and a correlation of 0.00 — a vacuous row reading as perfect agreement and
dragging our apparent fidelity 10% closer to the grid than it is. Guarded, and the true figure
is 3.16x.

**Rank:** immediately after the EP1 unblock (which this is held behind, deliberately — see below).

BLOCKING is the honest reading: a figure is live on a public surface, it is quotable, it is the
mission's own central claim, and it is now MEASURED to overstate the world by about 2.8x. The
director's standing rule on figures is three lawful outcomes — correct, caveat, or withdraw —
and freezing is not one of them. This document is the record that the correction exists, is
written, and is held out of its commit for a stated reason rather than forgotten.

# The Explore page publishes a timing spread that overstates the real grid by ~2.8x, and the measurement that says so already exists

All claims `observed-with-evidence` unless labelled.

## The live figure

`site/explore/index.html`, rendered under every measured household's carbon panel:

> Across 2021 as a whole the dirtiest 5% of half hours ran **5.1×** the cleanest 5%, so timing
> is worth that much at most and never more.

and for a 2025 day, **18.6×**. The numbers come from `by_year[year].p95_over_p5` in
`docs/market_data/grid_intensity_feed.json`, which is this model's own reconstructed shape.

The sentence reads as a fact about the GRID. It is a fact about the MODEL.

## What the measurement says

`ee6dd4fd2` fetched NESO's published national carbon-intensity series into
`sim/neso_carbon_intensity.py` and measured both shapes re-normalised over the half hours they
share — so the difference is physics, not coverage:

    year      half hours   ours min   NESO min   ours max   NESO max   spread ours/NESO   corr
    2019         16,923      0.057      0.217      1.707      2.019     29.8x /  9.3x     0.85
    2020         16,492      0.055      0.244      1.942      1.965     35.3x /  8.1x     0.82
    2021         16,646      0.056      0.195      1.792      1.769     31.9x /  9.1x     0.90
    2022         14,929      0.070      0.211      2.043      1.741     29.3x /  8.3x     0.82
    2023         17,362      0.058      0.165      1.896      1.958     32.4x / 11.9x     0.77
    2024         17,492      0.059      0.105      1.981      2.279     33.8x / 21.6x     0.68

**This shape swings ~32x where NESO's swings ~11.4x. Every timing figure derived from it
overstates the range by about 2.8x.** The clean end is where it comes from: our quietest half
hours read ~0.059 against a published floor averaging 0.189. The dirty end holds up.

## Why the page carries it

Because the module docstring is not the number. `sim/grid_carbon_intensity.py` carries the
correction in full and correctly; the page quotes `p95_over_p5` and a sentence written before
the comparison existed. A caveat that lives beside the code is not carried by the figure when
the figure is quoted, and this is the figure a reader would quote.

This is my own defect twice over and worth saying so plainly: I wrote the original error-bar
sentence as a recollection in the grammar of a measurement ("0.05 against NESO's 0.16", never
run), and I published a spread with no error bar at all. A tick found both.

## The correction, written and verified, held out of its commit

`/tmp/claude-1000/-/c6cee6e9-62fb-45a2-8e17-d45aa524771f/scratchpad/apply_neso.py` applies it;
the substance, if that scratch file is gone, is three changes:

1. `tools/generate_grid_intensity_feed.py` gains `versus_published(shape, demand)` — calls
   `sim.neso_carbon_intensity.published_shape` + `compare_shapes` per year off the cached
   series, and emits `spread_overstated_by`. Returns `{"available": False, "why": ...}` when the
   cache is absent, because a comparison silently missing from a feed reads as one that came out
   clean.
2. `tools/generate_explore_carbon.py` forwards `versus_published` onto the page's data.
3. `site/explore/index.html` renders the spread **only** when the measured comparison is
   available, and never without it: "…ran 5.1× on this model's own shape — which measures 2.8×
   wider than NESO's published series over the years both cover, so read the timing figures
   above as an upper bound by about that factor."

Plus a control in `site/test_explore_second_clock.py`: the page must not render a spread
without its measured correction beside it, mutation-proven by deleting the correction clause.

## Why it is held

`worker_tick` relaunched the EP1 store-roll landing detached (PID 1158791) with the explicit
note **"DO NOT START ANOTHER EP1 LANDING -- it would race this one and force it to re-gate"**.
Any commit at all moves HEAD and forces that 45-minute gate to restart, and EP1 is the blocker
that stops every lane moving a level. Landing a 3-file page fix ahead of it would trade a
tree-wide unblock for a same-day figure correction.

Editing `site/**` in the working tree would be worse still: the producer's site-lane gate runs
those tests against the WORKING TREE, so a half-applied edit refuses the publisher's commit —
which is exactly the outage I caused earlier today between 07:15Z and 08:05Z, and is already
filed as `WORKER_FINDING_THE_PRODUCER_RUNS_THE_WORKING_TREE_SO_A_HALF_TYPED_EDIT_IS_AN_OUTAGE`.

So: nothing is touched, and this document is the mechanism instead.

## What to do

Draw this the moment EP1's landing resolves, either way. Apply the three changes, regenerate
(`generate_grid_intensity_feed` then `generate_explore_carbon` — in that order, the feed sizes
its window from the days the page names), verify on the rendered page, and land.

If EP1 is still in flight when this is drawn: leave it in flight and wait. This finding is
about a figure that has been wrong for hours, not minutes; the tree-wide blocker is worth more.

## Evidence

- `git log -1 --format=%B ee6dd4fd2` — the measured table above, and the ZeroDivisionError the
  first run against the real feed raised (NESO publishes `actual: 0` for five half hours — a
  feed outage, not a clean grid).
- `python3 -c "import json;print(json.load(open('docs/market_data/grid_intensity_feed.json'))['by_year']['2021']['p95_over_p5'])"` — 5.08.
- `site/explore/index.html`, `carbonDayPanel()` — the sentence quoted at the top.
- `ps -p 1158791` — the EP1 landing this is held behind.

## Note, 2026-08-25 11:00 UTC — the EP1 landing this is held behind, attempt 4

`worker_tick`'s relaunch (PID 1158791) was **dead** when checked: process gone,
`/tmp/ep1_land_relaunch.log` zero bytes, HEAD unchanged. It was launched from a bounded tick's
session and was reaped with it, which makes three consecutive attempts killed by their LAUNCHER
and none by a red gate:

    attempt 1  `timeout 4000` fired mid-gate            -- 66 min of green discarded
    attempt 2  the tick killed the wrapper; GNU timeout holds its child in a separate
               process group, so the whole chain died with it
    attempt 3  launched "detached" from a bounded tick session, reaped with that session,
               zero bytes of output

That is the class, and it is smaller and more fixable than "a store whose register entry can be
written before the code it claims exists": **a landing whose gate outruns the lifetime of the
seat that launched it can never complete.** The gate is ~45 minutes per attempt and re-runs in
full on any HEAD move; every launcher so far has had a shorter lifetime than that.

Attempt 4 is running as **PID 1160950, its own session leader** (`setsid nohup`, no wrapper,
output `/tmp/ep1_land_attempt4.log`). It is immune to a wrapper timeout and to its launcher's
session ending. The tick's standing note — DO NOT START ANOTHER EP1 LANDING — still holds
against a LIVE one; this replaced a dead one and the evidence for "dead" is above.

If attempt 4 also fails, the thing to fix is `tools/surgical_land.py`'s retry: on a lost HEAD
race it re-runs the WHOLE gate against the new base, so a commit whose gate is slower than the
interval between other lanes' commits can never win. The selection is path-based
(`pre_commit_test_gate.select_targets`) and the gate already computes an import closure, so a
targeted retry — re-gate only the intersection of this commit's selection with the paths the
base move touched — is available and would turn a 45-minute retry into a two-minute one.

## Note, 2026-08-25 11:20 UTC — a SECOND outage of mine, found and stopped

**The publisher has been refused on every cycle since 09:25 UTC, and the cause was my
uncommitted map edit sitting in the shared index.** `episode_failures` reached 3 with
`total_red: 0` — the publisher's own suite was GREEN every time and the COMMIT was refused:

    [level-gate] ❌ COMMIT REFUSED (OPS11 -- a live BLOCKING finding refuses new level-raises
    in its own lane):
    §0: level_current 0->2 on EP13_adapter_carbon_intensity raises a level in lane
        `W4_the_wall`, which is HELD by 1 live BLOCKING finding(s):
        WORKER_FINDING_EP13_MAP_SAYS_PARKED_AND_UNBUILT_WHILE_THE_SITE_PUBLISHES_IT

I had staged `level_current: 0 -> 2` on EP13 and then held it out of its commit when the
simplifications blocker appeared. It stayed in the index. The publisher commits by pathspec but
the LEVEL GATE reads the tree, so from 09:25 every publish cycle carried my level raise into a
lane a tick had just marked BLOCKING — and the finding that exists to say the map is wrong was
refusing the correction to the map. Circular, and mine.

Reverted to HEAD (`git restore --source=HEAD --staged --worktree`); the edit is preserved at
`scratchpad/ep13_map.patch`, 40 changed lines, one hunk, EP13 only — checked before discarding.

THIS IS THE THIRD TIME TODAY THE SAME CLASS HAS BITTEN, which makes it an R3 two-strike signal
rather than three accidents:

  1. 07:15-08:05Z — a `site/**` edit without its test update refused the publisher's commit.
  2. 09:25-11:20Z — a staged map edit refused it again, this time invisibly, because the
     failure was in a gate nobody was watching and `total_red: 0` made the state file read
     healthy.
  3. And the EP1 landing has been starved four times over by the same underlying fact: **the
     producer runs the shared working tree, so anything held in it is live.**

Already filed as `WORKER_FINDING_THE_PRODUCER_RUNS_THE_WORKING_TREE_SO_A_HALF_TYPED_EDIT_IS_AN_
OUTAGE_2026-08-24`. What today adds is that the INDEX counts too, and that a
`commit_refused` with `total_red: 0` is the shape this failure takes — a publish-gate state
file that looks green while nothing has published for two hours.

**A worker holding work out of a commit must hold it OUT OF THE TREE, not out of the pathspec.**
