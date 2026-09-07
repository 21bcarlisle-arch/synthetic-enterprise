# PRE-REGISTRATION — is Scotland outside the census join, or a region the labeller lost?

**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
W2_18_the_housing_joint_the_sample_and_the_ceiling

**Written 2026-09-07 in an isolated worktree, BEFORE any number below was computed.** Claim
`W2_18-the-frame-has-no-scottish-region`.

## The question, and why it is not rhetorical

`tools/household_siting_frame.py` builds a household siting frame over **ten regions — nine English
and Wales**. Its own scope note says Scotland is out because the curriculum's marginal has no
Scottish slot. W1_14's artefact, re-cut yesterday, publishes coverage over **175,188 occupied GB
land cells**, a grid that includes Scotland, and every one of the 210 drawn households resolves
against those figures — from a frame of **139,938 cells that cannot be Scottish**. Two populations,
one number.

The direction is to establish **which of two things that is**, and they demand opposite remedies:

* **(A) The census join's scope.** The sources genuinely stop at the England-and-Wales border, so
  the frame cannot be extended without a new pull, and the honest move is a refusal that says so.
* **(B) A lost region.** The sources already carry Scotland and something between them and the
  frame drops it, in which case the frame should be extended and the scope note is *false*.

## What I already know from reading, stated before measuring so it can be wrong

`tools/weather_cell_weights.py` pulls **Scotland's Census 2022** (`pull_scotland`,
`SCOTLAND_EXPECTED_AREAS = 46_351`), fails closed if it is absent with the words *"Scotland is 8% of
GB households and it is the cold, windy end"*, and `read_households()` merges it with TS041.
`census_weights(group_of=...)` drops any output area whose `group_of` returns `None` into
`output_area_outside_the_grouping`. The committed frame manifest records that counter at
**46,270** — within 81 of Scotland's output-area count.

`region_namer()` resolves an output area through `oa21_to_region_england.csv`, an
England-and-Wales-only lookup, and returns `None` for everything else.

So I expect **(B)**, and the numbers below are the test of it. If P1 fails, it is (A) or something
else and the remedy changes.

## Predictions

| # | Prediction |
|---|---|
| 1 | ≥ 99 % of the 46,270 `output_area_outside_the_grouping` drops are output areas with the NRS `S00` prefix — i.e. Scottish, present in the census join, discarded by the labeller |
| 2 | Labelling `S00*` as `Scotland` gives the frame a Scotland region of **2.3–2.7 M households** (published NRS Census 2022 total is ~2.5 M), and 7–10 % of the frame's GB household total |
| 3 | Distinct frame coordinates rise from 139,938 to **within 5 % of 175,188** — because if Scotland is the whole of the missing 35,250 cells, the two populations were one population all along |
| 4 | `output_area_outside_the_grouping` falls **below 200** |
| 5 | **Every one of the ten existing regions is unchanged — same cell count, same household count, to the row.** The change is additive or it is wrong. This is the prediction that can most easily fail and the one that matters: an E&W household that moves is a labelling bug, not a widening |
| 6 | The DRAWN book does **not** move. 210/210 still site, and none is Scottish, because the curriculum's marginal is untouched by this turn. Extending the frame does not extend the world |

## What each outcome means for the deliverable

* **P1 holds** → it is a lost region. Extend the frame; the scope note in
  `household_siting_frame.py` is false prose and gets corrected beside the correction, not deleted.
* **P1 fails** → it is the join's scope after all, and the deliverable is the refusal that names it.
* **P5 fails** → stop and do not land. A labelling change that moves an English region's households
  is a defect, whatever it does for Scotland.
* **P3 fails wide** (frame still far short of 175,188) → the two-populations gap has a *second*
  cause beyond Scotland, which is a new finding and not this claim's.

## What this pre-registration does NOT claim

It does not claim the world gains Scottish households. `region_marginal_synthetic_acquisitions` is
a ratified curriculum value whose own `basis` reads *"Census 2021 England & Wales household counts
by region, normalised over the schema's 10-region set"* — the marginal inherited the same
England-and-Wales scope from the same join. Whether the world should draw Scottish households is a
**fidelity change to the curriculum**, sourced from the same censuses, and it is named here as the
next piece rather than smuggled into this one.
