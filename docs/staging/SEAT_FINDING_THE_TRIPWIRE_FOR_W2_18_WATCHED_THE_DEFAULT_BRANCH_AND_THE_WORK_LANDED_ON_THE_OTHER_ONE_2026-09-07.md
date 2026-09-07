# SEAT FINDING — W1_14's tripwire watched the default draw, and W2_18 landed on the other branch

**Date:** 2026-09-07
**Lane:** W1_market_weather / W2_18 (Lane 0 delivery claim `W2_18-coordinate-at-the-draw`)
**Severity:** RECORDED — nothing published was wrong. A control could not see the event it was
built for, and two refusals named remedies that cannot reach the population now receiving them.
**Status:** FIXED in the same commit (three controls re-keyed, two refusals rewritten, W1_14's
`block_reason` restated). The remaining gap is named below and is W1_14's own.
**Pre-registered before measurement:** `docs/staging/SEAT_PREREG_DID_THE_COORDINATE_REACH_THE_CELLS_2026-09-07.md`.
P1, P3 and P4 confirmed. **P2 was wrong in the honest direction** and is corrected below.

## What happened

`ec8a18710` landed W2_18's deliverable: `simulation/household_siting.coordinate_for_customer` draws
a 1 km cell from the region's own census household distribution, and `population_draw.
to_customer_dict` renders it. That is exactly the event W1_14's tripwire existed to catch. Its
docstring said so:

> "a coordinate at the draw breaks it. That is the point … Do not weaken it; delete it and move
> W1_14's level."

**It did not break.** The suite was green at HEAD.

## Why it could not break

`test_no_household_in_this_world_can_reach_the_cell_substitution_branch` drew its population with
`draw_population(7, acquisitions_per_year_lambda=40.0)` — no `draw_region=True`. That is the DEFAULT
placeholder region `UNKNOWN_SYNTHETIC`, which is the one region `household_siting` deliberately and
correctly refuses to site, because a region that is not a real region has no household distribution.

So the control asserted "no drawn household has a coordinate" against the only configuration in
which that must remain true. The capability landed on the non-default branch and the control was
measuring the default one. **R15: a control keyed to today's CONFIGURATION is blind to the branch
the work actually lands on** — a sibling of the catalogued "a control keyed to the population is
blind to the selected extreme".

## The measurement

Seed 7, `acquisitions_per_year_lambda=40`, 210 customers:

| | default (placeholder region) | `draw_region=True` |
|---|---|---|
| sited (`lat` is not None) | 0 (0.0%) | **210 (100.0%)** |
| resolved by `cells_for_location` | 0 | **0 (0.0%)** |

**P2 was wrong.** I predicted the resolved share would be low but non-zero, "near the artefact's
`all_three` coverage (~2–3.5%)". It is exactly zero, and my reason for expecting otherwise was a
misreading: `coverage` is computed over the whole occupied-land grid inside `derive()`, but what
gets PERSISTED is only `locations` — a table over the locations `derive()` was handed. That is seven
entries (`KNOWN_LOCATIONS` + `REACHABILITY_WITNESS`), keyed to four decimals (~11 m). An arbitrary
drawn coordinate cannot collide with it. The coverage figure and the lookup are not the same
population, and I differenced them without saying what each counted.

## The second defect: a refusal corrected on the wrong half

On 2026-09-06 `siting_refusal` was split so a premise with NO coordinate stopped being told to
"regenerate with `--derive`". That half was right. The same fix asserted, in
`test_a_premise_with_no_coordinate_is_refused_for_that_reason_and_not_told_to_re_derive`:

```python
assert "--derive" in wcs.siting_refusal(unsited), (
    "a real unsited coordinate IS fixed by re-deriving and the refusal must still say so")
```

**That is false.** `derive()` sites only the locations passed to it and the CLI passes the same
seven, so bare `--derive` re-sites those seven and reaches no drawn household. The wrong leg
survived because when it was written, no real coordinate could reach that branch — it asserted a
remedy against an empty population. Since W2_18, 100% of drawn households land on it. **A refusal is
only tested by the population that actually receives it**, and this is the same shape as
`3088f8c71` ("the arm refused gas for a reason that had stopped being true") one layer up.

## What was done

- `weather_cell_siting.siting_refusal`'s unsited branch now names the real cause (a table over N
  handed locations, not a grid lookup), the real remedy (`derive(locations=...)`, cut over the
  population being looked up), and explicitly rules out a nearest-location fallback.
- The module docstring's "the binding constraint is a coordinate at the draw" is replaced by what is
  now true, with the superseded claim kept beside it.
- Three controls re-keyed from wording/configuration to the property:
  - `test_a_drawn_household_has_a_coordinate_and_the_artefact_still_cannot_look_it_up` (replaces the
    blind tripwire). **Both new legs poison-proven:** leg 2 killed by making
    `coordinate_for_customer` return None (`210 of 210 … W2_18 regressed`); leg 3 killed by adding
    one drawn coordinate to the artefact's `locations` (`1 drawn households now resolve`).
  - `test_a_premise_with_no_coordinate_…` — the false `--derive` leg replaced by its opposite.
  - `test_an_unsited_coordinate_is_refused_and_never_placed_by_nearest_anything` — was pinned to the
    literal string "has not been sited"; now asserts absence-from-artefact and the explicit refusal
    of proximity.
- W1_14 `block_reason` restated for the third time, each correction kept beside the last.

## What is still open

1. **W1_14's own artefact.** Cut `locations` over the population that gets looked up in it. The
   drawn coordinates are not arbitrary — they come from the committed frame's 144,542 cells, so a
   bounded re-cut is possible. That is a decision about artefact size and fidelity for the director's
   world, not a wiring fix, and it is W1_14's to make. Leg 3 of the new control goes red the moment
   it happens, which is the intended direction.
2. **The superseded-coverage red — now DISCHARGED here.** See the section below.
3. **The two I&C Open-Meteo pulls.** Still real, still HTTP 429 as of 2026-09-06, still not W1_14's
   precondition.

## The red that refused the landing, and what it forced

The commit above was **refused by the test gate** on
`test_derive_reproduces_the_committed_artefact` — a red I had already proved pre-existing at HEAD in
a clean extract. It is filed as
`SEAT_FINDING_THE_WEATHER_CELL_ARTEFACT_PUBLISHES_THE_CENTROID_METHODS_COVERAGE_AND_ITS_OWN_DERIVATION_NO_LONGER_REPRODUCES_IT_2026-09-06.md`
(BLOCKING, same lane, same atom), whose "what to do" ends: *"the regeneration and the surfaces have
to move together, and that is W1_14's lane's call, not a passing lane's."*

I am holding W1_14's file_scope and it was blocking the landing, so I made the call and did it.

**My own diagnosis was wrong first, and the correction is what made it safe.** I read the gap as a
degraded local pull (the header-only-CSV defect staged the day before) and wrote that down. The
discriminator settles it: `occupied_land_cells` is **175,188** fresh against **121,668** committed.
121,668 is the postcode-centroid method's figure; 175,188 is the OS Open UPRN address record's,
which the placement moved to on 2026-09-06. So the fresh derivation is the CORRECT one and the
committed artefact was one method behind — not degraded input. Had my first reading stood, the
right action would have been the opposite one (do not re-derive), which is why the number was worth
looking up before acting.

Done, in this commit:

1. `sim/weather_cells/site_cells.json` regenerated from the current placement.
2. The four percentages moved wherever they are quoted, each kept beside the superseded value:
   `simulation/weather_cell_siting.py`'s docstring table, `simulation/weather_inputs.py`'s step-2
   note, W1_14's `maturity_map` row, and `tools/generate_weather_cells_data.py`'s occupied-cell
   count. The refusal text needed no edit — it reads `all_three` from the artefact.

| driver | published (centroid) | true (UPRN) |
|---|---|---|
| winter temperature | 20.5% | **20.4%** |
| annual wind | 30.7% | **27.8%** |
| annual sunshine | 27.9% | **17.3%** |
| all three at once | 3.5% | **2.0%** |

Every superseded figure **overstated** the archive. Annual sunshine claimed 27.9% against a true
17.3% — the archive covered a little over half what the artefact said.

### The re-cut stranded the reachability witness, and that is the sharpest thing here

Regenerating the artefact turned two further controls red, and the second one matters well beyond
this atom.

`REACHABILITY_WITNESS` is a 1 km Cornish cell that the derivation puts in all three of London's
cells 300 km away. It exists for one reason, stated in its own comment: *"a branch this project
cannot prove is REACHABLE is one it must assume is unreachable (R15)"*. Every refusal test in the
file passes against a mechanism that refuses everything, so the witness is what makes them mean
anything.

**Under the corrected placement the old witness cell no longer shares all three of London's cells.**
`cell_matched_site(WITNESS)` returned `None`. For the duration of the re-derivation the accept
branch had NO witness and was unreachable again — the exact R15 failure the constant exists to
prevent, **reintroduced by a re-derivation rather than by a code change, and by the commit that was
making the numbers more honest.**

A witness is a measurement and it expires with the thing it witnesses. Nothing in the tree knew
that; the witness was a hardcoded pair of floats with no tie to the partition it was cut against.
The remedy was to **re-measure it, not to relax the assertion**: 28 cells share all three of
London's under the UPRN placement (17 under the centroid one) and the witness moved to the furthest,
(50.4689, -4.1492), 301 km out.

Two controls re-keyed while there:

- `test_the_accept_branch_is_reachable_and_it_matches_climate_not_proximity` asserted the distance
  as two per-axis deltas, one of which (`lon > 4.0`) was passing **by 0.02 degrees**. It now asserts
  a great-circle distance > 250 km — the actual property, and no longer one re-cut away from a red
  that would have meant nothing.
- `test_the_refusal_names_the_driver_that_disagreed` asserted the literal string
  `"3.5% of GB households"`. It now reads `all_three` from the artefact and formats it. A control
  pinned to today's answer went red because the code became more honest, which is exactly backwards
  and is CLAUDE.md's own named failure.

**What I deliberately did NOT touch:** the three `121,668` mentions in
`docs/market_research/how_many_weather_cells_britain_needs_and_why_the_answer_is_a_curve.md`, and
the ones in `tools/weather_cell_weights.py` / `tools/os_open_uprn.py`. Those are the
centroid-versus-UPRN comparison itself, which is exactly where that number belongs. The doc's line
24 does describe the CURVE's own derivation on the old placement — that is W1_19–W1_22's artefact,
which I have not re-derived, and rewriting the figure would claim a re-derivation I did not do.
**That is a real remaining gap and it is named here rather than papered over.**

## What did not change

`level_current` stays at **1**. A coordinate that exists and resolves nowhere is not a wired heat
load, and recording a better-understood blocker is not progress toward L2.
