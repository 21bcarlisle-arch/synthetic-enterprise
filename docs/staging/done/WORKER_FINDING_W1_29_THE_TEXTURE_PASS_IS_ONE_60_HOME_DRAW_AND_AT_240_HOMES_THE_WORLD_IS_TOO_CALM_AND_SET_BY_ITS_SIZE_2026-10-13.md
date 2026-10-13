**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** `W1_29_the_worlds_homes_are_drawn_too_alike_in_half_hourly_behaviour`

# W1_29: the texture pass is one 60-home draw, and at 240 homes the world is too calm and set by its size

**Fate (2026-10-13, clear-the-decks):** DONE -- c22f6c144; f17319e8f Stronger 240-home comparator + strict xfail + both-branches control all confirmed landed in tests/harness/test_premise_two_level.py. The underlying world-calmness defect itself stays open as atom W1_29 in the maturity map -- that is pre-existing tracked work, not an orphan of this finding.

Worker on the lane-1 self-refill BUILD draw of `W1_29`, 2026-10-13, at `origin/main` `e4595810a`, in an
isolated worktree. This was decided blind to company results, and nothing below reads a company figure.
Evidence and tables:
`docs/market_research/the_half_hourly_texture_of_real_homes_electricity_read_from_low_carbon_london.md`,
section "The pass is one 60-home draw ...".

## What was found

1. **The atom's exit is keyed to one underpowered draw.** The map row's exit is "`test_MEASURED_population_values`
   sees L1.1 PASS". That has held since 2026-10-08, on the drawn 60 (seed 17): [3, 14, 27, 44] homes under the
   real p10/p25/median/p75. The same cell over 240 homes is **red on seeds 17, 18 and 23** and passes on 19
   by a margin. Every time it is red on the calm side: 73-81 homes under the real p25 against 60 expected,
   and 194-197 under the real p75 against 180. The world's p90 is 0.23-0.24 against a real 0.311.
2. **The calm comes from size.** A world home's texture correlates −0.72 with log kWh/day (real −0.32 on
   kWh/day), and its log kWh/day correlates +0.81 with its log always-on draw. A big always-on draw makes a
   home big and calm at once. Homes under 5 kWh/day never sit under 0.15 (real 29%), and homes at 12-20
   kWh/day always do (real 60%). Real homes differ in size mostly through active use: above-base p90 is
   18.7 kWh/day real against 8.8 in the world. That is the same missing spread as the L2.4 red.
   *One-variable check, run after the first landing:* with only the always-on load put back to a uniform
   25 W, the drawn 60's r moves −0.665 → −0.469, and the median texture moves 0.161 → 0.213. The draw
   does tighten the coupling. But narrowing it is not the remedy, because the median would go with it.
   What is missing is a spread of active use that is independent of the always-on draw.
3. **"No two alike" holds.** No exact duplicate texture appeared in any draw.
4. **"Small busy flats" is not measurable against LCL**, which records no dwelling type. Nothing was keyed on
   flats.

## What was built (landed with this finding)

`tests/harness/test_premise_two_level.py` gained three things:

- A Fisher-z comparator of the world's texture~kWh/day correlation against LCL's −0.32 (n 313).
- A strict xfail, `test_a_world_homes_texture_is_no_more_set_by_its_size_than_a_real_homes`. On the drawn 60
  it reads r −0.665 and z −3.27.
- A control that both of the comparator's branches are reachable, `test_the_size_coupling_comparator_can_both_pass_and_fire`.

Two mutations were run, a constant True and a constant False result. Each reds the companion, and the
constant False result also turns the strict xfail into an XPASS. A comment beside the MEASURED pin
records the n 240 verdicts.

**No world draw changed.** The world digest and the value arms do not move, so there was no value-arms
run and no baseline/curriculum switch to wire.

## What was not built, and why

The remedy is a per-home spread of **active** use at a given household size. The knowledge layer has no
source for it (a GAP, named in the doc). Tuning a multiplier until LCL's quantiles match would make the
comparison its own source. The doc names DESNZ NEED's consumption by household characteristics and
HES 2012's per-household totals as the reads to try first.

## Proposals for the seat

- **Re-key W1_29's exit.** L1.1 should pass over at least 240 homes on more than one seed, and the size-coupling
  xfail should XPASS. The 60-home PASS should not be read as the exit being met. **The level stays at 1.**
  The map row's EVIDENCE comment still says only "the p10 leg is red", which is stale. It needs an
  orchestrator write, which this worker cannot make.
- **Next DISCOVER: the between-home spread of active electricity at a given household size**, from NEED/HES.
  It probably closes L2.4 and this atom together.
- Severity is LATENT, not BLOCKING. The L1.1 instrument is sound and is only underpowered at n 60. Nothing
  published reads the n 60 pass as the world's verdict: a grep of `site/data/` and
  `tools/generate_dashboard_data.py` finds L1.1 only in historical proof notes and in the map row, and the map
  row still calls the cell red.
