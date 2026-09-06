# SEAT FINDING — W1_14 was waiting on the I&C archive gap, and its subject is households

**Date:** 2026-09-06
**Lane:** W1_market_weather
**Severity:** RECORDED — the atom's stated blocker named the wrong set; nothing published was wrong,
and the correction is in the row and held by a control. Found under the Lane 0 delivery claim
`the-weather-cells-reach-the-world-or-w1-14-says-why-not`.
**Status:** FIXED in the same commit (refusal, two controls, `block_reason`, `blocked_on`). The
household gap it names is open and owned by W2_18.
**Pre-registered before measurement:**
`docs/staging/SEAT_PREREG_WEATHER_CELL_BRANCH_REACHABILITY_2026-09-06.md`. All four predictions
confirmed; P2 came back stronger than predicted.

## The claim that was wrong

`W1_14_weather_cells_for_household_heat_load` recorded its L1→L2 blocker as **archive breadth**:

> "the supply book has 6 distinct locations and 4 have archives, so Birmingham and Teesside are the
> whole gap … TWO pulls close it."

That is a true sentence about the supply book's **locations**. The atom's subject is the supply
book's **households**, and nobody had asked it of them. This is the project's own recurring shape —
*before measuring a thing, say what it is* — with the count taken off a set that is not the subject.
It is the third framing this same blocker has had in two days ("17 pulls" counted the partition,
"two pulls" counted the locations), and the first two were each corrected by re-counting rather than
by re-asking what was being counted.

## What the measurement says

**Supply book, by which step of `weather_inputs._weather_source_customer_id` answers:**

| step | count | who |
|---|---|---|
| 1 — exact location match | 14 | every resi and SME premise, plus `C_IC4` (Manchester) |
| 2 — derived cell substitution | **0** | — |
| 3 — refused | 4 | `C_IC1`, `C_IC2` (Birmingham), `C_IC3`, `C_IC3g` (Teesside) — **all I&C** |

Resi premises at an un-archived location: **none**. Birmingham and Teesside hold no household at
all. So the two pulls move I&C coverage from 0/4 to 4/4 and **household coverage from 100% to
100%**.

**Drawn population (210 customers, seed 7, `acquisitions_per_year_lambda=40`):**

| | placeholder region (default) | `draw_region=True` |
|---|---|---|
| `lat is None` | 210 (**100%**) | 210 (**100%**) |
| sited by the derivation | 0 | 0 |
| resolved to any archive | 0 | 0 |
| regions | `UNKNOWN_SYNTHETIC` | **ten real GB regions** |

The second column is the sharp one. With the curriculum on, the world already knows a household is
in Wales, or the North East, or the East Midlands — and still cannot site it, because
`population_draw.to_customer_dict` renders `{"lat": None, "lon": None, "region": ...}` and the
derived cells are keyed by coordinate.

**So step 2 is a branch no premise in this world can take, from both ends at once**: the named
premises never need it, and the drawn premises can never satisfy it. Its only reachability evidence
was `REACHABILITY_WITNESS`, a synthetic Cornish coordinate the module itself labels "not a premise".
That is the R15 shape — a branch that exists to be taken rarely, taken never — and it survived
because every existing control asked whether the branch *refuses correctly*, which a branch nothing
reaches passes perfectly.

## The second defect, found on the way

`siting_refusal` gave a premise with **no coordinate** the same answer as an **unsited real
coordinate**: *"regenerate with `--derive` before settling it"*. Re-deriving the entire GB grid can
site a real coordinate and can never site a missing one, so the seam's single most common refusal —
issued for 100% of drawn households — named a remedy that cannot work and pointed at the wrong lane.

## What was done

- `simulation/weather_cell_siting.siting_refusal` now has **three** refusals, not two. The
  no-coordinate case names the draw as the cause and W2_18/W1_24 as the remedy, and says explicitly
  that a coordinate must not be fabricated in the weather seam — that is the fabrication
  `fabric_physics.latitude_for_weather_site` refuses one layer down.
- Two controls in `tests/simulation/test_weather_cell_siting.py`, each naming its defect, both
  **proven by poison round**:
  - `test_a_premise_with_no_coordinate_is_refused_for_that_reason_and_not_told_to_re_derive` —
    killed by removing the new branch.
  - `test_no_household_in_this_world_can_reach_the_cell_substitution_branch` — killed independently
    by (a) giving drawn households a coordinate, and (b) removing a resi premise's exact-location
    archive so step 2 answers instead. **Leg (b) is why the control asserts the STEP and not the
    destination**: the first draft asserted the resolved CSV, and poison (b) passed it, because the
    cell branch returned the same site the exact match would have. A control keyed to today's answer
    instead of the property, caught by poisoning it.
- W1_14's `block_reason` restated and `blocked_on` set to `W2_18_the_housing_joint_the_sample_and_
  the_ceiling`, whose `file_scope` already names `simulation/population_draw.py`.

`test_no_household_in_this_world_can_reach_the_cell_substitution_branch` is deliberately pinned to
the claim *"the cells drive household heat load"* being **false**, so it goes red when the world gets
better. That is the intended direction: when it fails, W1_14's level moves and the control is
deleted, not weakened. Its docstring says so.

## What is still open, and for whom

1. **The household gap — W2_18.** A coordinate at the draw. Not startable here: the placeholder is
   deliberate and protected by `test_region_is_explicit_placeholder_not_fabricated`, and inventing a
   coordinate is a fabrication, not a wiring fix. The honest question W2_18 must answer is what
   sources a household's coordinate — the region marginal gives a region, and a region is not a
   point.
2. **The I&C gap — two Open-Meteo pulls.** Still real, still worth doing, no longer W1_14's
   precondition. Re-probed 2026-09-06 and Open-Meteo still answers
   HTTP 429 "Daily API request limit exceeded. Please try again tomorrow." External; clears on its
   own.

## What did not change

`level_current` stays at **1**. The wiring exists and is imported; the world's household heat load
is still not driven by the cells, and this finding is the reason it cannot be yet. Recording the
correct blocker is not progress toward L2 and must not be counted as any.
