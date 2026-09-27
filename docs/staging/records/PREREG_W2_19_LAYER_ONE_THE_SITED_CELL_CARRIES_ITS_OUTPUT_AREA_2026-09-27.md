**Severity:** RECORD · **Lane:** stage 1 — the people layer · **Atom:** `W2_19_who_lives_where_money_and_composition`

# Pre-registration: the sited cell carries its output area

**Written 2026-09-27 15:55 UTC, before building or measuring.** Follows
`SEAT_RESULT_W2_19_LAYER_ONE_REACHES_NO_HOME_AND_AT_REAL_INPUTS_WIRING_IT_MOVES_THE_MEAN_HEADCOUNT_0_09_2026-09-25.md`.

## What changes

`household_siting` draws a 1 km cell PPS over the region's households. It will then draw an output
area inside that cell, on its own substream, so every coordinate draw stays byte-identical. The draw
is PPS over **that OA's share of the cell's households**, which is the same placement
`weather_cell_weights.census_weights` used to build the cell weights (households split over an OA's
own addresses). That makes the joint (cell, OA) draw exactly the census placement. The 2026-09-25
probe weighted by raw ONSUD addresses instead. That is close but not the same, because an OA's
households-per-address ratio varies. So this is a deliberate change from the probe, stated here
before the answer is known.

Both inputs are committed as derived frames under `sim/`, so a tree without `~/.cache` gives the
same headcount for the same seed. Missing frames make the draw refuse. It never falls back to
national without saying so.

## Predictions, at the live book (`live_dwellings()`, default seed)

1. **Resolved homes = every non-Scotland dwelling.** At HEAD that is 231 − 13 = **218**. The probe's
   217/14 split was taken at an older HEAD, so this prediction is about today's book.
2. **Every Scottish dwelling carries its S-code OA and reads `national`**, because TS017 is E&W only.
3. **Mean headcount over the 231 homes: 2.336 ± 0.03.** The done-line says ±0.01. I expect to miss
   it about as often as I hit it: the OA picked within a cell differs from the probe's (different
   substream, different weights), and the probe changed 64 homes by 0.30 each, so the sampling
   noise on a 231-home mean is about 0.02. If it lands outside ±0.01 but inside ±0.03, that is the
   noise and not a defect. Outside ±0.03 is a defect to find.
4. The coordinate of every home is unchanged: 0 of 244 customers move.

## Results, written after the build (same day, 16:50 UTC). The predictions above are unedited.

| # | Predicted | Measured | |
|---|---|---|---|
| 1 | 218 resolved | **218 / 231** `output_area`, 13 `national` | hit |
| 2 | Scottish homes S00 + national | **13 / 13** carry an S00 area, all national | hit |
| 3 | mean 2.336 ± 0.03 | **2.277** over the 231 dwelling entries | **MISS** |
| 4 | 0 coordinates move | **0 of 244** customers, same id set, against a HEAD extract of `live_population()` | hit |

**Why 3 missed, and why the done-line it was checking cannot be met.** Three things, in the order
I found them:

1. **The 231 entries are 155 homes.** A dual-fuel `PROS-x` and its gas leg `PROS-xg` are one house,
   and they share a premise and a coordinate. This build gives them one area. The 2026-09-25 probe
   drew an area for each account separately, so it gave one house two areas. That is why it found
   207 distinct OAs and this finds 155. Counted per home: **realised local mean 2.297** against
   national 2.419.
2. **A realised mean over 155 homes has a standard error of about 0.09.** The done-line's "within
   0.01 of 2.336" asked a single draw to land in a band a ninth of its own noise. The ±0.03 I
   pre-registered was also too narrow, because I estimated the noise from the 64 homes that changed
   rather than from the whole draw. My error, left here beside the claim.
3. **The quantity that means something is the expected mean given the cells.** Averaging each
   home's area distribution over its cell's areas takes out the draw noise: **2.356**, against the
   ONS E&W 2.359 and the national TS017 mean 2.3645. So the book's sited cells are not biased
   toward small or large households. The realised 2.297 is one draw of a correctly conditioned
   population.

The national baseline also moved between the probe and HEAD (2.429 → 2.394 over the dwelling
entries), because the book changed. That is a fourth reason the probe's absolute numbers could not
be re-hit, independent of this change.

**Also found while building (filed as
`SEAT_FINDING_THE_COMMITTED_SITING_FRAME_PREDATES_ITS_OWN_PLACEMENT_AND_A_LIFE_EVENT_ERASES_FOUR_NEED_FIELDS_2026-09-27.md`):**
the committed household frame predates the address placement its builder now uses, and
`life_events.apply_events` drops every `Household` field added after `income_stress`.

## What "done" was taken to mean, leg by leg

The item's done-line had three legs. This build settles them as follows:

- **"A run artefact shows `people_count_source=output_area` for the E&W homes."** Held by a control
  on the live book instead
  (`test_household_siting.py::test_every_sited_england_and_wales_home_in_the_live_book_carries_its_output_area`).
  It asserts both branches are reached, every sited E&W home is local, and every Scottish home is
  S00 and national. It reds when `live_dwellings` drops the area (mutation-checked). A full sim run
  costs hours and would record the same fact once. The control records it on every commit.
- **"Mean within 0.01 of 2.336."** Replaced, for the reason given above, by the expected mean given
  the cells: 2.356 against ONS 2.359.
- **"No tree gives a different headcount for the same seed."** Both inputs are committed
  (`sim/household_siting/cell_output_area_frame.csv.gz`, `sim/people/ts017_household_size_by_oa21.csv.gz`),
  the bare `except` in `dwelling_records` is gone, and an absent frame raises.
  `test_dwelling_records.py` makes the cache reader explode and gets the same headcounts.

**And a leg the done-line did not have:** homes gaining areas split the headcount. The property
record became local while every fabric-path caller asked by id alone and stayed national, for 40
of 147 homes. The area now rides on `Household` too (set at the same seam as the dwelling's, and
carried through `life_events`). An AST census refuses any production headcount call that does not
pass the area.
