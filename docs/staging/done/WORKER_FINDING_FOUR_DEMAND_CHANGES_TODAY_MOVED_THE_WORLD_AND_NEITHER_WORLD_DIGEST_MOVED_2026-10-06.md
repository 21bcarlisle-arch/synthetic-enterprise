**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** `unminted` · **Claim:** none

# Four demand changes today moved the world, and neither world digest moved

Found while landing W1_29's per-home appliance stock (`pt.owned_stock`). `simulation/fabric_demand_path.py`
calls `generate_premise_trace`, so the stock draw changes every fabric-path home's electricity. A home
without a dishwasher, tumble dryer or freezer uses less. Today's other three changes did the same:
the boiler's pump and fan (`pt.boiler_auxiliary_kwh`), HES's cooking and laundry season, and supplementary
electric heating.

The two digests a run artefact carries do not see any of it:

- `departure_level_anchor.world_level_identity` digests the departure level only.
- `world_home_identity` digests the home STOCK, meaning fabric and composition through
  `year_premise_stock`. It does not cover the demand a home generates.

So a value-arms bound or a run artefact taken this morning and one taken tonight carry the same world
stamp from different demand worlds. This is the shape `world_home_identity`'s own docstring describes
("one digest value spans two different home populations"), one layer down: same homes, different
behaviour.

**Proposed remedy (not built):** extend the `world_home_identity` probe to also digest a short premise
trace for a few probe homes, for example a week on fixed weather. Anything that moves a home's demand would
then move the digest, as anything that moves its fabric already does. Measure the cost first. The module
says the stock probe is under 10 ms warm, and a trace probe will not be, so the price needs measuring
before anyone argues about it.

**What would refute this:** a control that already fails a value-arms bound when the demand generator
changes. None was found: `grep world_level_identity|world_home_identity` over `tools/` shows only the
two digests above.

---

## Disposition (2026-10-06, delivery seat, claim `the-world-digest-sees-demand`): BUILT

**Prediction, written before the mutation table ran:** each of the four changes, reverted in-process,
moves a one-week demand probe over the 96 stock-probe homes, and none of them moves the home-stock
digest. The supplementary-heater revert was the one I expected might NOT move, because only 10% of
gas homes own a heater and the probe could have drawn none. Measured: 5 of the 96 own one, so it
moves too. All five reverts moved the demand digest and left the stock digest unchanged (the
heater's annual kWh, 656 → 1505, was tested separately).

**What was built:**
- `simulation/world_home_identity.home_demand_identity()` runs the same 96 probe homes through
  `generate_premise_trace` for one real week of the C1 archive (2020-01-13 to 2020-01-19) and
  digests their half-hourly electricity and gas. `world_level_identity()` carries it as `demand`,
  so every run artefact stamped with `world_identity` now records it.
- **Cost, measured:** 1.65 s cold (about 0.75 s of that is the stock draw), 0.63 s warm, roughly
  7 ms per home-week. That is two orders above the stock probe's 10 ms. It is still a header
  cost, but every `world_level_identity()` caller now pays it.
- `tools/generate_value_arms_data._blind_envelope_demand_refusal`: the blind envelope (the
  flat-baseline comparison) refuses when an arm's `demand_digest` is missing, when the arms
  disagree, or when it differs from the live demand. The floor-family rows also carry
  `demand_digest`.
- Control: `tests/simulation/test_the_world_demand_digest_moves_with_the_demand.py`. I mutated the
  digest to a constant: all 5 revert tests went red, and the reproducibility and wiring controls
  stayed green.

**Consequence the page will show on its next regeneration:** the five 09-11 arms carry no demand
stamp, so the blind envelope is withheld until they are re-run here. That is correct, because they
were measured before all four changes. The re-run is handed on as a continuation.

**Not covered**, as stated in the part's own `what_this_does_not_cover`: anything
`fabric_demand_path` adds on top of the trace (the comfort constraint, away days, life-event
segments), and anything that shows only outside a January week.
