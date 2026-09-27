**Severity:** LATENT · **Lane:** W2_customer_generator · **Atom:** `W2_19_who_lives_where_money_and_composition`

# PRE-REGISTRATION — a life event keeps every field it does not name

Filed 2026-09-27 BEFORE the measurement, for remedy 2 of
`SEAT_FINDING_THE_COMMITTED_SITING_FRAME_PREDATES_ITS_OWN_PLACEMENT_AND_A_LIFE_EVENT_ERASES_FOUR_NEED_FIELDS_2026-09-27.md`.

**The change (one variable):** `life_events.apply_events` builds its starting state from
`dataclasses.fields(Household)` instead of a hand list that stopped at `income_stress`.

**What the finding predicted:** demand moves for every home with a life event.

**What I predict instead, from reading the readers first:** no sim demand code reads
`floor_area_band`, `has_loft_insulation`, `has_cavity_wall_insulation` or `has_mains_gas_supply`
off a `Household` (`grep` over `simulation/` and `sim/`: only `premise_population` writes them,
and `fabric_physics` derives floor area from `bedrooms`). So:

- P1. The four fields survive every event type (control: one event of each type, every field the
  event does not name compares equal to the base).
- P2. The fabric trace for a home with an event changes by EXACTLY ZERO kWh in every half-hour,
  EXCEPT where an event changes no field it names (e.g. `new_baby` at MODERATE stress): before the
  fix such an event still opened a new segment, because the record lost its four fields; after
  it, it does not. I predict that difference, where it exists, is small and I cannot say its sign.
- P3. `tools/settlement_choice_probe.py`, which reads the four fields, sees them populated after
  a life event where it saw `None` before.

The measurement: generate ~200 premise-population homes with their life events, build the fabric
series with and without the fix in one process, and count half-hours that differ.

## Result (filed after the run, prediction above unedited)

One process, two arms: HEAD's `apply_events` loaded from its blob beside the fixed one; the same 600
homes from `draw_premise_from_joint` (the production stock, `STOCK_FROM_FITTED_JOINT = True`),
the same per-customer event streams 2016-2022, the same 2022 weather (`C1`), the same seed.

| | |
|---|---|
| homes with an event by 2022-12-31 | 273 of 600 (46%) |
| of those, `floor_area_band` lost under HEAD | 273 (all) |
| homes whose segment count differs | 0 |
| differing half-hours (elec + gas) | 0 of 9,565,920 |
| annual gas / elec delta | +0.00 kWh / +0.00 kWh |

- **P1 HOLDS** — `tests/simulation/test_life_event_keeps_every_field_it_does_not_name.py`, which
  reds against HEAD's `apply_events` (2 of 4 legs) and is green on the fix.
- **P2 HOLDS, and the finding's "demand moves" is REFUTED.** Nothing in the demand path reads the
  four fields today. The no-op-event segment split I allowed for did not occur in this sample, so it
  is neither confirmed nor ruled out.
- **P3** is by construction (the probe reads the field off the same record) and was not run.

What the defect actually cost: every reader of a post-event household that is NOT demand
(`tools/settlement_choice_probe.py`, the physical-layer census) saw `None` for half the homes. Its
cost to demand would have arrived the day a demand path started reading floor area from NEED rather
than from bedrooms, silently and only for homes with an event.
