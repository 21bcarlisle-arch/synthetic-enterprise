# RESULT — the tied half's directions are judged, and all six unregistered pointers were false

**Severity:** LATENT · **Lane:** H_harness

Six here-relative sentences a reader could fetch from `/capabilities/` today pointed the wrong way.
None was reachable by any control in the tree until this landing. LATENT rather than BLOCKING: no
figure moves and no control's verdict is invalidated — what was wrong is where each sentence sends
a reader looking. All six are repaired in the producer and republished in the same landing, and the
rule that found them is standing, so this documents a closed defect rather than an open one.

Pre-registration:
`docs/staging/records/SEAT_PREREGISTRATION_THE_SIX_UNJUDGED_TIED_POINTERS_DIRECTIONS_2026-09-19.md`
— filed in the records room rather than the root, because a pre-registration is a record and the
root is the work queue; `staging_rooms --check` named that on the first landing attempt. It was
written before the probe existed. **It is kept beside this result, and where it was wrong it is
said so below rather than revised.**

## The premise, re-measured

`87c485285` is an ancestor of `origin/main` and landed the tied half judging HOMES only. Direction
was absent. **Premise NOT spent.** The duplicate-claim note named this item's own id;
`.seat_work_in_hand.json` does not exist on the shared tree and the only matching process was this
invocation. No rival, no disposition — the work was done.

## What the measurement found

Ten tied literals, four already registered, six not. The four registered ones all hold, as the
item predicted. **All six unregistered ones were false.**

| symbol:line | said | renders in | its referent renders in | verdict |
|---|---|---|---|---|
| `_leg_in_this_world`:9444 | "the figure above" | `#arms-legs-first` (0) | 0 and 2 | same, and below — never above |
| `WITHDRAWN_CLAIMS`:4299 | "the choosing figure below" | `#arms-note` (17) | 0 and 2 | both **above** |
| `_control_leg_agreement`:5588 | "the control row above" | `#arms-method` (14) | 14 | **same** |
| `_POPULATION_REPAIR_BIAS_NOT_A_GAIN`:10492 | "the figure above" | `#arms-redraw` (2) | 0 and 2 | above **and same** |
| `_population_repair_bias`:10581 | "the figure above" | `#arms-redraw` (2) | 0 and 2 | above **and same** |
| `_population_repair_bias`:10595 | "the figure above" | `#arms-redraw` (2) | 0 and 2 | above **and same** |

## Where the pre-registration was wrong, and it matters

I predicted all six false and all six are. **But I got the mechanism wrong on three of them, and
the wrong mechanism would have produced the wrong repair.** I predicted the three
`population_repair_bias` sentences land in `#arms-legs-first`, position 0, and are false because
nothing is above position 0. Measured, they land in `#arms-redraw`, position 2 — and the figure
they name renders in BOTH `#arms-legs-first` and `#arms-redraw`. So "above" is **true** of one home
of the referent and **false** of the other.

That is the parent defect's own shape — a subject with homes on two sides of the sentence — and it
is the one reading the prose cannot find, because the prose is right half the time. Had I trusted
my own arithmetic I would have repaired three sentences for a reason that was not the reason, and
the "nothing is above position 0" argument I was so confident in was simply not what was wrong.

I was also wrong about a field name inherited from the item: the choosing figure's referent is
**not** `current_world.selection_gbp`. That field exists, carries the identical value, and **no
door reads it** (measured: perturbing it moves no region). The door reads
`current_world.selection_leg.figure_gbp`. Registering the duplicate would have reported five
referents as "rendering nowhere" — a red naming the wrong cause and inviting a repair to prose that
was not the problem.

## The instrument, and the measurement that justifies it

Five of the six referents are NUMBERS. Both halves of this file locate a referent by PREFIXING a
string marker onto its value. **Measured: prefixing the marker onto
`current_world.selection_leg.figure_gbp` finds it in ZERO regions**, because the door puts it
through `gbp()` and `signed()`, which return null on a string. Moving the same number finds it in
two. So the existing probe would not merely have measured a page nobody publishes — it would have
reported five referents as rendering nowhere.

`_numeric_referent_homes` sets the number to **two distinct values of the same sign and the same
order of magnitude**, renders each, and calls a region a home when its text differs between them.
Same sign and magnitude is the design, not tidiness: a number that gates a BRANCH changes prose
that never renders it, so perturbed-against-real cannot tell a home from a branch; two values on
the same side of every nearby threshold take the same branch, so the flip cancels and only regions
that render the digits survive. It needs to know nothing about the door's formatter — which is the
opinion `_REFERENTS` already refuses to hold about anchors.

**The door was measured deterministic** (two renders of one payload differ in no region), which is
what makes "these two renders differ" mean the number and not noise. It is asserted, not assumed.

**Stated over-report:** a region rendering a figure DERIVED from this one also moves and is counted
a home. That is the conservative direction — it can only add regions a pointer must be true from.

## The repairs

Four of the six had **no here-relative word that holds from every home**, because their referent
renders on both sides of them. For those the only correct repair is to name the subject, which is
true from anywhere — the repair `_decomposition_is_the_same_contrast` took. They consequently leave
this vocabulary and are no longer in the census. Two had a word that is true and were repaired to
it, so they stay under measurement and the claim goes on being re-asked.

- `_leg_in_this_world`: "The figure above is a single realisation" → "This leg's own figure is…"
- `_POPULATION_REPAIR_BIAS_NOT_A_GAIN`: "NOT A CORRECTION TO THE FIGURE ABOVE" → "…TO THE CHOOSING FIGURE"
- `_population_repair_bias` ×2: "THE FIGURE ABOVE IS BIASED DOWNWARD" → "THE CHOOSING FIGURE IS…"; "The figure above stands as published" → "The choosing figure stands…"
- `WITHDRAWN_CLAIMS`: "the choosing figure **below**" → "**above**" (true; stays in the vocabulary)
- `_control_leg_agreement`: "The control row **above**" → "**beside this**" (true; stays)

`site/data/value_arms.json` was republished through `tools.generate_value_arms_data` so the repairs
reach the reader — and because tied-ness is read off the feed, an unpublished repair would have
dropped the sentences into the untied half instead of fixing them. Diff: 10 lines of prose plus the
publish stamps.

## Controls, and that they can fail

Two new legs: `test_every_tied_here_relative_pointer_is_true_from_the_region_it_lands_in` and
`test_MUTATION_the_numeric_referent_probe_marks_a_number_the_string_probe_cannot`. Five mutations
run against the real tree and reverted, each named in the file's own R15 block. The two that matter
most: **restoring `WITHDRAWN_CLAIMS`' "below" and republishing gives two reds, one per home of the
figure; restoring `_population_repair_bias`' "the figure above" and republishing gives exactly ONE
red, naming `#arms-redraw` and not `#arms-legs-first`** — the leg tells the home where the claim
holds from the home where it does not, which is the discrimination the whole instrument is for.

## Two findings this pass produced and did not fix

1. **`current_world.selection_gbp` is a published field no door renders**, duplicating
   `current_world.selection_leg.figure_gbp` exactly. It is not a here-relative sentence so this
   rung does not own it, and it is now load-bearing as the numeric probe's poison — the unread
   number that must come back with no home. If a door ever starts rendering it, that mutation leg
   names itself rather than going quiet.
2. **The here-relative detector's noun list misses "run".** `_population_repair_bias`' clause still
   says "20 paths of pricing code away from the run above", which is a here-relative pointer by any
   reading and matches no pattern in `_HERE_RELATIVE` (`table|panel|chart|figure|row|block|section|
   list|column|note|box|card|band`). Adding a noun widens every sweep on the site at once, so it is
   filed rather than done in this landing.
