**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** EP17_varied_population_draw (drawn as LANE 3 DISCOVER/FRAME; the draw itself was the defect)

# The discovery pass ceiling bound the one draw function production never calls

**2026-09-16, scheduled tick, worker seat.** The tick drew `EP17_varied_population_draw` as
LANE 3 DISCOVER/FRAME work. That atom's own `block_reason` has said this since 2026-08-26:

> DISCOVERY DISPOSITION 2026-08-26 (delivery seat, over the discovery pass ceiling at 6 passes
> with the level never having moved): **no further DISCOVER pass is authorised** [...] Re-opens
> the day epoch 4 is named; until then a pass here is the livelock, not the work.

So the drawn work was the thing the director's ruling of 2026-08-19 exists to make impossible.
I did not take the pass. The finding is the draw.

## What was actually wrong

`tools/discovery_pass_ceiling.saturated_ids()` is correct and EP17 is in it — 10 atoms are. The
filter that consumes it lived inline in `supervisor._idle_discover_frame_draw`.

**Nothing in production calls that function.** Its live callers are this repo's tests and two of
its own docstrings. The three-lane self-refill draws lane 3 through
`_idle_discover_frame_draw_concurrent` (`supervisor.py:5553`), and so do the two rest-legitimacy
checks (`:3419`, `:6051`). That function never consulted the ceiling at all.

Measured on the live map before the repair, `exclude_stalled=False` so nothing was written:

| | atoms returned | over the ceiling |
|---|---|---|
| before | 17 | 2 — `EP16_anchored_generators`, `EP17_varied_population_draw` |
| after | 15 | 0 |

Two, not ten, because the other eight are already removed by a different leg — frame-saturation,
`blocked_on`, non-idle, or no gap. That is why this stood: the lane looked bounded from every
direction except the one that mattered, and the two atoms that leaked are the two with the
highest dials in the pool (60 each), so they are exactly the ones the weighted draw reaches.

The lane is not starved by the fix: 15 idle atoms remain drawable.

## Why the R15 proof could not see it

`tests/tools/test_discovery_pass_ceiling.py` has three controls on the drawing rule —
skips-saturated, all-saturated-is-empty, uncomputable-ceiling-closes-the-tier. All three drive
`_idle_discover_frame_draw`. Every one of them passed, for a year of ticks, over a production
path none of them touched. The sibling file
`tests/background/test_frame_saturation_draw_marker.py` states in its own module docstring that
"both draw entry points are covered" — true of FRAME saturation, which it is about, and not of
the ceiling.

This is the catalogued shape: **the control was proven on a function that is not the subject.**

## The repair

One implementation, not two copies: `supervisor._under_pass_ceiling(candidates, where)` now holds
the filter, the fail-closed contract and the ruling's reasoning, and **both** draws call it. A
second entry point cannot drift from the first because there is no second copy to drift.

Fail-closed direction is unchanged and now applies on the production path: an unreadable ceiling
closes the discovery tier rather than reopening an unbounded lane. BUILD and HARDEN stay drawable,
so the loop is pushed toward work that moves state, never halted.

The concurrent filter sits exactly where the sibling puts it — after frame-saturation, before the
stall preference — so `_prefer_least_stalled` ranks the genuinely drawable set instead of ranking
atoms that will not be offered.

## The control, and the proof it can fail

`test_every_idle_discovery_entry_point_honours_the_pass_ceiling` and the two MUTATION legs beside
it are parametrised over `IDLE_DISCOVERY_DRAW_ENTRY_POINTS` — the partition, not a member of it.
Each stubs `saturated_ids` (the subject is the WIRING; the survey has its own tests above) and
drives three rungs: nothing saturated → the draw offers these atoms; one atom saturated → that
one is gone and the rest remain; everything saturated → empty.

Rung 1 is what makes rung 2 attributable. Without it, a draw that returned little anyway would
pass the disappearance test.

**Mutation run.** Disarming only the concurrent call site turned all three `[concurrent]` legs red
and left all three `[single]` legs green — the fire is attributable to the new wiring and not to
the shared helper. Restored, 48 passed / 1 skipped.

**And the all-saturated leg was wrong on its first draft**, against correct code, which is worth
keeping visible: it saturated *this entry point's own offer*. The single draw returns ONE
dial-weighted pick per call, so forty calls are a SAMPLE, and saturating a sample leaves the
unsampled remainder drawable. The population is the concurrent draw's full candidate set; the
test now takes it from there and asserts the two entry points still share a population, so the
day they stop sharing one, this control says so instead of quietly measuring one of them.

## The sibling is production-dead, and it is deliberately still here

`_idle_discover_frame_draw` has no production caller now and had none before this repair — that
is the whole finding. It is NOT deleted in this commit, and the reason is not caution: it is the
second half of the partition the new control is written over. Deleting it would delete the six
ceiling legs and the `test_frame_saturation_draw_marker.py` coverage that drive it, to remove a
function whose only remaining cost is that it exists. If it is ever removed, the parametrisation
list `IDLE_DISCOVERY_DRAW_ENTRY_POINTS` is the one place that has to shrink with it, and the
population assertion in the all-saturated leg is what will notice if it does not.

## What this does not fix

`_is_externally_blocked` still reads `blocked_on` only and never `block_reason`. EP17 carries its
disposition in `block_reason` and has no `blocked_on`, so the prose that says "no further DISCOVER
pass is authorised" is not what stopped the draw — the ceiling is. That is the known
`abolished_block_classes.LIVE_CLAIM_FIELDS` gap and it is not widened here: making prose gate a
draw is the wrong lever, and the ceiling reaches this atom on the measurement instead.
