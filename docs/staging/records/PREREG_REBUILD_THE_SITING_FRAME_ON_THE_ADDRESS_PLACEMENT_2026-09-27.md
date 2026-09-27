**Severity:** LATENT · **Lane:** W2_customer_generator · **Atom:** `W2_19_who_lives_where_money_and_composition`

# PRE-REGISTRATION — rebuilding the household siting frame on the placement its builder now uses

Filed 2026-09-27 BEFORE the rebuild, for remedy 1 of
`SEAT_FINDING_THE_COMMITTED_SITING_FRAME_PREDATES_ITS_OWN_PLACEMENT_AND_A_LIFE_EVENT_ERASES_FOUR_NEED_FIELDS_2026-09-27.md`.

**The change (one variable):** `python3 -m tools.household_siting_frame --build`, then
`--build-output-areas`, at HEAD, no code change. Only the artefacts move. The frame was built
2026-09-07 03:49 on the 3x3-window placement and `census_weights` moved to ONSUD four hours later.

Predictions:

- P1. `--build-output-areas` ring census is `{"0": <every cell>}`. Ring 1 and ring 2 (2,942 + 2 today)
  go to zero, because every cell of the rebuilt frame is a cell the address placement put
  households in.
- P2. Household total is unchanged to within rounding (27,129,010). Placement moves households,
  it does not add them.
- P3. Scotland's cell count rises from 35,389 to 51,864, as the finding measured.
- P4. The `weather_cell_siting` join goes to 0 missed households (3 today, in 111 cells).
- P5. Household-weighted means of winter temperature, annual wind and annual sun, read from the
  frame's own cells, move by LESS than the placement change itself moved them (1.28% / 1.07% /
  0.11% of an SD). I cannot say the sign.
- P6. Tests that read the committed frame stay green except any that pin a count of the old frame
  as a literal. Those are named and fixed to the property, not to the new number.

## Result (filed after the rebuild, predictions above unedited)

| | old frame (window placement) | rebuilt (ONSUD) |
|---|---|---|
| cells | 179,931 | 197,116 |
| distinct coordinates | 175,188 | 194,865 (= the occupied land cells, exactly) |
| households | 27,129,010 | 27,121,764 |
| households off the land grid | 154,127 | 167,328 |
| output-area rings | 0: rest, 1: 2,942, 2: 2 | 0: 197,116 |
| frame coordinates missing from the weather partition | 111 cells, 31.5 households | 0 |

- **P1 HOLDS.** Every cell takes its own output areas.
- **P2 REFUTED AS WORDED, and the explanation is in the manifest.** The frame lost 7,246 households
  (0.027%). The placement put 13,201 MORE households in coastal cells off the HadUK land grid, and
  frame households = placed (27,289,092) − off-grid (167,328). The census total is unchanged
  (27,291,846; 2,754 households in 45 areas with no ONSUD address). So placement did not add or
  remove households, but it DID move some off the grid the frame is cut to. I did not predict that.
- **P3 HOLDS.** Scotland 35,389 → 51,864 cells.
- **P4 HOLDS.** 0 misses. The 2026-09-16 docstring said the residual was 3 households; measured
  here it was 31.5 (the frame weights are fractional). Either way the residual is now 0.
- **P5 HOLDS.** Household-weighted means over the frame's own cells, as a share of the grid SD:
  winter temperature −0.0088 °C (−0.68%), annual wind +0.0086 (+0.62%), annual sun −0.14 (−0.07%).
  All are below the placement change's own 1.28% / 1.07% / 0.11%.
- **P6 HOLDS.** 174 tests over every reader of the frame are green, and none pinned an old count.

**Not measured here, and not claimed:** what this moves in the book. Every household's cell can
move, so each home's weather and output-area headcount prior are redrawn. The world moved for a
fidelity reason, decided without looking at a company result.

Control: `tests/tools/test_household_siting_frame.py::test_the_committed_frame_was_built_by_the_placement_the_weather_cells_were_cut_over`
asserts the frame's coordinates and the occupied land cells are the same set. It reds on the old
frame and names the 111 cells.

The manifest's `source` said "OS Open UPRN" and now names ONSUD, which is what `census_weights`
reads.
