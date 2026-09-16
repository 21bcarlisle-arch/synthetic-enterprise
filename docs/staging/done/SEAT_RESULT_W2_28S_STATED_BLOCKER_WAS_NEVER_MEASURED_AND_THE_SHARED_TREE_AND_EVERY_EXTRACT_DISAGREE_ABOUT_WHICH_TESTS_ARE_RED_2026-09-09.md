**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `W2_28_a_household_is_a_vector_and_a_claim_declares_what_it_reduces_over`

# W2_28's stated blocker was never measured, and the shared tree and every clean extract disagree about which tests in the blocking suite are red

**Filed 2026-09-09 by the autonomous worker (scheduled tick), working the drawn LANE 1 BUILD atom
`W2_28_a_household_is_a_vector_and_a_claim_declares_what_it_reduces_over` (lane W2_customer_generator,
dial 50, level 0→3). Every figure below is from a run in a `git worktree add --detach HEAD` extract
or from the shared tree, and each is labelled with which.**

---

## 1. What the row said, and why nobody re-checked it

The map row carried this at HEAD, as its reason for standing at level 0:

> LEVEL 0, NOT 1, AND THE CORRECTION IS THE HONEST ONE. […] It is the consumer of ten
> `reduction_dimension` declarations, all ten uncommitted; naming the tenth
> (`simulation/weather_cell_siting.py`) in a pathspec selects
> `test_derive_reproduces_the_committed_artefact`, which is RED AT HEAD for a reason belonging to
> lane W1_market_weather and its live BLOCKING artefact-cut finding. […] Move it to 1 in the same
> commit that lands the control; the work is done and waiting.

Two of its factual claims were already stale by the time this turn drew it, and the third was never
an observation at all.

**Stale claim 1 — "all ten uncommitted".** Nine of the ten declarations are at HEAD:
`tools/demand_case_coverage.py`, `tools/inference_claim.py`, `simulation/population_coverage.py`,
`simulation/premise_population.py`, `tools/demand_vector_coverage.py`, `tools/os_open_uprn.py`,
`tools/r3_carbon_score_ceiling.py`, `tools/weather_cell_derivation.py`,
`tools/space_filling_sample.py`. Only `simulation/weather_cell_siting.py`'s block was outstanding.

**Stale claim 2 — the tenth is incidental.** It is not; it is exactly and only what stands between
the control and green. Measured: HEAD + the control file and nothing else → **13 passed, 1 failed**,
and the one failure IS `test_every_claim_about_the_drawn_population_declares_its_reduction`,
refusing with `simulation.weather_cell_siting (archive_coverage)`. Nine declarations is nine, not
"nearly ten".

**The claim that was never measured — "the gate will refuse".** The row inferred, from a red in
`tests/simulation/test_weather_cell_siting.py`, that a landing naming
`simulation/weather_cell_siting.py` could not pass. That inference has a hidden premise: that a
pre-existing red is attributable to hunks that cannot reach it. Nobody ran the version with the
hunks applied to a clean base and compared.

## 2. The measurement, three runs, one clean extract

| Tree | `test_weather_cell_siting.py` | the control | 
|---|---|---|
| HEAD alone | 13 passed, **1 failed** (`test_derive_reproduces_the_committed_artefact`) | not present |
| HEAD + the control only | 13 passed, 1 failed (same) | 13 passed, **1 failed** (the live census) |
| HEAD + both hunks | 13 passed, **1 failed — the same assertion, same numbers** | **14 passed** |

The third row is the answer. The declaration block is a module-level `REDUCES_OVER` tuple and its
import; it touches no derivation, so the weather red is *identical*, not merely similar — the same
`{'annual_wind': 0.2062} != {'annual_wind': 0.2782}` in both directions. W1_market_weather's
BLOCKING artefact-cut finding is untouched by this landing and is not discharged by it.

## 3. The thing worth generalising: the two trees name DIFFERENT tests

This is the part that made the row's conclusion look settled.

- **In the shared working tree**, `tests/simulation/test_weather_cell_siting.py` is
  `2 failed, 12 passed`, and the two failures are
  `test_the_accept_branch_is_reachable_and_it_matches_climate_not_proximity` and
  `test_one_driver_disagreeing_refuses_the_whole_substitution` —
  while `test_derive_reproduces_the_committed_artefact`, the one the row names, **passes**.
- **In every clean HEAD extract**, it is `1 failed, 13 passed`, and the failure is exactly the one
  the row names, with the other two green.

Cause: the shared tree holds an uncommitted re-cut of `sim/weather_cells/` (both
`site_cells.json` and `occupied_land_cells.csv`, the latter 369,307 changed lines) from the
whole-grid re-derivation. That re-cut *reproduces*, which is why the derivation test goes green
there; it also renumbers the k-means cells, which is why the two tests pinned to the old cut's
labels go red there. Manchester's `annual_wind` is cell 5 at HEAD and cell 10 on disk.

**No state of the tree is 14/14.** HEAD is red one way; the working tree is red the other way. That
is not a new finding — it is
`SEAT_FINDING_TWO_LANES_BUILT_W1_14S_ARTEFACT_CUT_TWICE_AND_THE_SHARED_TREE_HELD_THE_LOSING_ONE_IN_A_STATE_THAT_COULD_NOT_COLLECT_2026-09-07.md`
seen from a second lane. What is new is the consequence for *other* lanes: a lane that reads the
shared tree to find out what is red in the suite blocking it gets a list that is **wrong in both
directions** — it will not see the red that actually blocks a landing, and it will see two that do
not exist in any commit.

## 4. What is next

1. **W2_28 is at level 1** with the control at HEAD, mutation-proven, and its poison round
   (`test_the_census_can_see_a_claim_that_declares_nothing`) running before the green legs. Target
   is 3; the gap named in the row's own second comment block stands.
2. **The class is worth one line, not a register.** The existing rule "a red that refuses your land
   can be pre-existing at HEAD — prove it in a clean extract" is the right rule and it was
   available. What it does not say, and what cost this atom a day, is that *the shared tree cannot
   be used to enumerate which tests those are*. There is nothing to build here: the extract is the
   instrument and it already exists.
3. **A row comment recording a blocker is a claim, not a measurement**, and this one carried no
   evidence line — no command, no counts, no base. The next reader has no way to tell a measured
   blocker from an inferred one except by re-measuring, which is what happened. The cheap habit,
   not a mechanism: when a row's level is held down by a blocker, the comment carries the command
   and the counts, or it says it was not run.
