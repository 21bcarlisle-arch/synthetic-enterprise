<!-- SUPERVISOR_DRAW: self-drawable -->

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `W2_28_a_household_is_a_vector_and_a_claim_declares_what_it_reduces_over`

**Knowledge:** none — this is a landing/orphan state, not domain understanding.

# The canon's control was green in the working tree and red in every commit, because all ten of its suppliers were orphaned with it

## The premise I was given, and what it actually was

The tick drew `W2_31_people_phase1_the_physical_layer_stands_alone` as a level 0→3 build, and the
three director documents as unminted. Measured first, per R7:

- **The build was already done.** `simulation/household_physical_layer.py` and its seven controls
  landed at `bde2514dc`, forty-three minutes before the tick began.
- **The minting was already done.** `PLANNER_MINTED_the_ruling_and_the_canon_are_seven_eighths_
  minted_and_the_map_rows_are_not_at_head_2026-09-07.md` had checked all nine deliverables of the two
  canons and the ruling on 09-07 and found seven covered.
- **None of it was at `HEAD`.** All seven map rows — `W2_28`, `W2_29`, `W2_30`, `W2_31`, `W2_32`,
  `W2_33`, `W1_28` — returned nothing from `HEAD` *and* nothing from `origin/main`, which is eleven
  commits ahead. The canon's item-3 control was `??`.

So the drawn work was not a build. It was a landing, and the planner document had said so twenty
hours earlier and declined to do it because a pathspec commit of the map would have swept another
lane's lines. That contention had since cleared: the map diff was a single hunk, 295 insertions,
zero deletions, and every one of its seven `- id:` lines was a canon row.

## The thing the working tree could not tell me, twice

**`pytest` on the control passed. 14 passed. It passed again on the second run. It was worthless
as evidence, both times.**

`tools/surgical_land` gates the tree the commit *would* create, and that tree refused twice, each
time naming something the working tree had hidden:

1. **First refusal — `symbol_landing_check`:** `tools.demand_case_coverage.REDUCES_OVER` and
   `tools.weather_cell_derivation.REDUCES_OVER` "do not exist in this tree — the consumer landed and
   the supplier did not". Both declarations were uncommitted working-tree additions.
2. **Second refusal — the control's own assertion:**
   `test_every_claim_about_the_drawn_population_declares_its_reduction` failed in the created tree
   listing **eight further modules** — `generate_cohort_coverage`, `inference_claim`, `os_open_uprn`,
   `r3_carbon_score_ceiling`, `space_filling_sample`, `population_coverage`, `premise_population`,
   `weather_cell_siting`. Every one carries its `reduction_dimension` declaration only in the working
   tree; **zero of the ten are at `HEAD`.**

The canon's item-3 deliverable was **built in full and landed nowhere**. It is one control and ten
suppliers, and it could never have been landed piecemeal: the control asserts over the whole
population of claim-making modules, so it goes red unless every supplier lands in the same commit.
The working tree was green because it held all eleven pieces at once — the one configuration that
no commit contained.

`tools/space_filling_sample.py` turned out to carry a **second** canon deliverable in the same
orphaned hunk: `DIRECTOR_CANON_WHAT_THE_SYNTHETIC_BOOK_IS_2026-09-07` item 3, the tail-density
principle written where the sampling criterion is documented, as intent rather than side effect.

## The generalisable shape

A control whose subject is *the whole population of modules making a class of claim* has as many
suppliers as that population has members. For such a control, **"green in the working tree" carries
no information at all** — it is green exactly when every supplier is present, which is the state the
working tree accumulates and no commit ever reaches. The instrument that could see it is the gate
reading the created tree, and nothing else in the loop can: not the author's pytest run, not a
clean-`HEAD` extract (the control is not there either), not the ratchets.

This is the population-scoped twin of the known single-symbol case. `symbol_landing_check` catches
"consumer landed, supplier did not" for a *named symbol*. It caught two of the ten here — the two
the control imports by name — and was structurally blind to the other eight, which the control
discovers by scanning rather than importing. The second refusal was the control itself doing the job.

## The third refusal, and why the control still is not at HEAD

With all ten suppliers in the pathspec the coverage control passed — and the gate refused a third
time, on `tests/simulation/test_weather_cell_siting.py::test_derive_reproduces_the_committed_artefact`.

**That red is at HEAD and is not mine.** Proved in a clean detached worktree at `bde2514dc` with no
working-tree state: `1 failed`, the same driver shares (`annual_wind` 0.2062 against an expected
0.2782, `annual_sun` 0.2493 against 0.1725). My diff to `simulation/weather_cell_siting.py` is a
purely additive declaration and cannot reach `derive()`.

What hides it in the shared tree is that `sim/weather_cells/occupied_land_cells.csv` and
`sim/weather_cells/site_cells.json` — the committed artefacts the test reproduces against — are
themselves **modified and uncommitted**. So the test passes here and fails at every HEAD.

**I did not land those artefacts, deliberately.** Lane `W1_market_weather` carries a live BLOCKING
finding, `SEAT_FINDING_TWO_LANES_BUILT_W1_14S_ARTEFACT_CUT_TWICE_AND_THE_SHARED_TREE_HELD_THE_LOSING_
ONE_IN_A_STATE_THAT_COULD_NOT_COLLECT_2026-09-07`, which says exactly that the shared tree's copy of
this artefact may be the losing cut. Landing it blind to settle my own gate would be choosing
between two lanes' cuts on no evidence, to make a red go away. It belongs to that lane and that
finding.

**Consequence, stated rather than glossed:** the canon's item-3 control cannot reach HEAD until that
red clears, because the control needs `simulation.weather_cell_siting` declared, and naming that
module in a pathspec selects the red test. The ten declarations and the control are ready and
gate-clean apart from it. What landed here is the half that is independent — the seven map rows.

## What is next

1. **`W2_31`'s level is still `0` at the row that just landed**, though its module and seven controls
   have been at `HEAD` since `bde2514dc`. The promotion is a recorded move and deliberately not made
   in the landing commit; it is the next obvious increment and needs the level definition checked
   against what the build actually earned, not a bump to the target.
2. **Two of the nine deliverables remain genuinely uncovered** — `A50` (the supplier use-case
   register published to Capabilities with a derived status per item) and `A51` (the plain-English
   report to the director). Both are specified in full in the 09-07 planner document and were
   deliberately not written into the map by that tick. They are still not in it.
3. **Do not treat this as an argument for a new watcher.** The gate already caught it, twice, and
   named the exact cause both times. What failed was nobody running the gate on this work for twenty
   hours after it was written. The lesson is about *what evidence a population-scoped control's green
   is worth*, and it belongs in the R15 catalogue rather than in a new mechanism.

— Delivery seat, 2026-09-08.
