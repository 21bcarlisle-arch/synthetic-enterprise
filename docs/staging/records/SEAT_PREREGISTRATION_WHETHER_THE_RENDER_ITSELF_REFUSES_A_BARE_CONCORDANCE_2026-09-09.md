**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — promote-the-09-08b-pair-and-give-the-fixed-horizon-cut-its-own-interval) · **Class:** controls_that_cannot_fail

# Pre-registration: does the PAGE refuse a bare concordance, or only the producer?

**Written before the probe is run.** The drawn item's property is *"no concordance of any cut
renders anywhere on the page without an interval computed on that cut's own sample."* Two controls
exist and both are per-subject:

* `test_the_method_number_never_appears_without_its_interval` — the survivor headline only.
* `test_NO_CUT_of_the_bridge_reaches_the_reader_without_the_interval_its_own_n_earns` — the bridge
  legs, discovered from `produced["legs"]` so it does follow that partition.

Both drive the surface through the **producer**. `_horizon_leg_published` moves the number to
`concordance_withheld` when `null_spread` is absent, so every existing feed reaching the door is
already refused upstream. **Nothing yet asks what the render does with a leg the producer did not
refuse.** That matters because the property is stated about the page, and the producer's refusal is
one edit away from being relaxed by a lane that never reads this test.

Reading `fixedHorizonBlock`'s `row()` in `site/capabilities/index.html`: `figure` is set from `c`
alone, and the withheld branch is gated on `c === null && leg.withheld`. The bound cell has its own
branch for `lo === null || hi === null`, whose comment says *"A leg with a number and no interval
cannot occur — the row above withholds the number — so an empty cell here would be a rendering
defect and is written as one rather than left to look like a missing value."*

## Predictions

**P1.** Handed a leg with `concordance` set and `null_95_low`/`null_95_high` absent — the shape the
producer will not emit today — the render prints **the number to four decimals** and an amber *"no
interval on this cut's own n"* cell beside it. The number reaches the reader.
*Refuted if the row renders `withheld`, or a dash, or omits the figure.*

**P2.** Neither existing door test fires on that feed. `test_NO_CUT_of_the_bridge...` builds its
subject through `_skill_fixed_horizon`, so it cannot construct this input at all.
*Refuted if either test goes red when driven on the poisoned feed.*

**P3 — the will-not-move claim.** The **live** page is unaffected: the promoted 09-08b artefact
carries no per-leg spread, so `_skill_fixed_horizon` returns the withheld block and the live
rendering shows no bridge table at all. This is independent rather than merely conceptually
separate — the poisoned feed is constructed in the test and never written to `site/data/`, and no
code path the repair touches is upstream of `generate_value_arms_data`.
*Refuted if the live feed's rendered bytes change at all.*

## What I will do with each answer

If P1 confirms, the page holds the property in exactly one place — upstream — and the item's
"door test keyed to the property" cannot be honestly claimed. The repair is to make `row()` refuse
a number it has no interval for, and to hold it with a control that discovers the cuts
**structurally from the feed** rather than naming today's four, so a third cut added tomorrow is
covered by construction.

If P1 is refuted the render already refuses, the property holds in both places, and the only thing
missing is the control that says so — a smaller piece of work, and this document records that I
expected otherwise.
