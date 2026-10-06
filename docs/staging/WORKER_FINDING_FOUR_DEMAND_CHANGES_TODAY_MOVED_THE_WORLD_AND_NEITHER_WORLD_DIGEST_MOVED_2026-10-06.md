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
