**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:**
W1_14_weather_cells_for_household_heat_load

# RESULT: Scotland is a LOST REGION, not the census join's scope — and the coverage figure was a GB denominator being read as the drawable population's

**Measured 2026-09-07 on real disk state.** Claim `W2_18-the-frame-has-no-scottish-region`. The
direction asked one question with two answers and told me to settle it: *is the frame's missing
Scottish region the census join's scope (England and Wales), or a lost region?* — and then either
extend the frame or make the refusal say which of the two it is.

## The answer: a lost region, and it is not close

The two answers take **opposite remedies**, which is why the question was worth settling rather than
hedging. If Scotland were outside the census join, extending the frame would need a data pull. It is
not outside it:

| Layer | Scotland? | Evidence |
|---|---|---|
| The census join | **IN** | `tools/weather_cell_weights.GB_COUNTRIES == ('E92000001', 'W92000004', 'S92000003')`; Scotland's Census 2022 is pulled, and the joiner **fails closed** if the file is absent — "Scotland is 8% of GB households and it is the cold, windy 8%" (the weather ruling's decision 9) |
| The GB coverage denominator | **IN** | 175,188 occupied land cells, household-weighted through that join |
| The curriculum's region marginal | **OUT** | `segmentation_curriculum_v1.json::region_marginal_synthetic_acquisitions`, 10 regions |
| The household siting frame | **OUT** | 139,938 cells, 10 regions, 24,664,503 households |

The loss is at the **curriculum**, and its own `basis` field says so in as many words: *"Census 2021
**England & Wales** household counts by region, normalised over the schema's 10-region set."*
Scotland's ~8% was **normalised away**, not excluded by a decision. `household_siting_frame.build()`
then asserts the frame's regions equal the curriculum's — correctly — and the absence propagates
into the artefact and out to every refusal.

So the frame is not missing a pull. It is missing a curriculum value, and the curriculum is the
director's instrument (R13, `.claude/rules/epistemic-wall-sim.md`: difficulty and population changes
are "named, versioned, director-authored artefacts, never silent parameter drift"). **Extending the
frame is therefore not mine to do**, which is why this turn took the direction's other branch and
made the refusal say which of the two it is.

## What the refusal used to say to a real Edinburgh coordinate

> 'Edinburgh' carries a real coordinate that is not in the derived artefact … **check it is a real
> GB land coordinate** before regenerating with `--derive`.

Edinburgh **is** a real GB land coordinate, in a country whose census this repository pulls and
weights into the very denominator the same refusal went on to quote. The remedy it named cannot
work: re-deriving sites only the locations handed to `derive()`, so no number of `--derive` runs
will ever site a Scottish coordinate. One reason was named where there were two.

It now names both, and says which one is which — including that the fix is a curriculum change and
where that lives. Reproduce: `siting_refusal({"region": "Edinburgh", "lat": 55.9533, "lon": -3.1883})`.

## The load-bearing half: two populations, one number

Found while establishing the above, and this is the part that was already published. The coverage
figures are household-weighted over the **whole GB grid, Scotland included**. The population that is
**looked up** in the artefact is the frame's — **England and Wales only**. Since 2026-09-07, 100% of
drawn households resolve against those figures, so the conflation is live. Both, measured:

| driver | GB households (published) | households THIS WORLD CAN DRAW (E&W) | error |
|---|---|---|---|
| winter temperature | 20.4% | **20.9%** | −0.6 pp |
| annual wind | 27.8% | **28.4%** | −0.6 pp |
| **annual sunshine** | 17.2% | **14.4%** | **+2.8 pp — a fifth of the true figure** |
| all three at once | 2.0% | **2.0%** | — |

Annual sunshine is the one that matters and it overstates. `all_three` — the figure the refusal
quotes and the one W1_14's gap is priced on — is unmoved at 2.0%, so **no decision taken on the
joint figure was wrong**. That is worth stating plainly: the defect is real, published, and its
blast radius on the number anyone actually used is zero.

This is the shape CLAUDE.md names as the project's most expensive recurring failure — *average unit
rate*, *net margin*, *bill shock*. Two populations, one percentage, for as long as the artefact has
existed.

### A thing I expected to find and did not

I expected Glasgow — the one archive site in the region no household can be drawn from — to be dead
weight for the drawable population. It is not. Dropping it costs the E&W population **6.6 pp of
winter-temperature cover and 7.1 pp of wind**: its cells reach into northern England. Recorded
because it was a prediction made before the measurement and refuted by it.

## What was built

* `coverage_over_frame()` — the second column above, computed from the two **committed** artefacts
  (no `~/.cache`, no netCDF, no k-means), so it cannot drift from what the world is using. Not baked
  into the artefact on purpose: a stored copy is a second source that can disagree with the frame it
  claims to describe.
* `FRAME_SCOPE` — the scope fact as **data**, because the refusal has to name it and a docstring
  nothing reads would rot beside it.
* `frame_regions()` — read from the frame's committed manifest, never asserted.
* Both refusal branches rewritten; the CLI prints the two populations **side by side, always**,
  because printing one column invites reading it as the other.

## The controls, and the poison round

Four mutations, each with its target **proven present** before patching (a patch that never applied
reports a survival that means nothing):

| # | Mutation | Killed by |
|---|---|---|
| M1 | `coverage_over_frame` returns the GB figure — the exact conflation | `…is_a_second_population_and_not_the_GB_figure_relabelled` |
| M2 | drop the household weighting (cell count instead) | `…is_household_weighted_and_not_a_cell_count` |
| M3 | the refusal stops saying which of the two causes it is | `…is_lost_and_not_the_census_joins_scope` |
| M4 | `frame_regions` loses a region | `…covers_exactly_the_regions_the_curriculum_can_draw` |

**M1 survived `test_the_archive_breadth_refusal_quotes_the_population_it_is_refusing`**, because
that control reads `coverage_over_frame` to build its own expectation, so both sides move together.
That is recorded in the control's own docstring rather than left for a reader to discover: its
subject is the refusal's *wording*, and the figure's independence belongs to M1's killer. Two
controls, one property each.

All 21 tests green in a **clean HEAD extract** — the shared tree currently cannot collect this
module at all, because another lane holds `simulation/weather_inputs.py` dirty with
`_WEATHER_SOURCE_CUSTOMERS` removed. That file is not in this landing and was not touched.

## What is left open, and it is the director's

`test_the_frame_covers_exactly_the_regions_the_curriculum_can_draw` is the tripwire: if a Scottish
region is ever added to the curriculum's marginal, it goes red until the frame is rebuilt, and the
rebuild is one command (`python3 -m tools.household_siting_frame`) against sources already pulled.

**My recommendation, for the director, on NTFY:** add Scotland to the region marginal. The company's
market is GB, the world's own census join already holds Scotland, and the frame can be rebuilt
without a new pull. The cost of leaving it is that ~8% of GB households — the cold, windy 8%, which
is the segment a heat-load atom exists to model — cannot be drawn at all, and every GB-labelled
coverage figure keeps describing a population the world cannot produce. This is a curriculum value,
so I have not changed it.
