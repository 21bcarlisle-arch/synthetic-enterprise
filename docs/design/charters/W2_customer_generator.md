# W2 — Customer Generator: lane charter

**Dial reached 3 (SPIKE_WEEKEND DISCOVER/FRAME charter flood, 2026-07-11)** — charter earned
per the map's own rule ("a lane earns its charter when its dial reaches 3+").

## Mission

The customer book this company serves must be generated the way a real GB domestic energy
population actually looks — real archetype distributions (home type, payment channel, tenure,
fuel poverty, occupancy), and eventually a real per-run DRAW rather than one fixed, memorised
cast, sitting inside a world that eventually has real competitors in it too. "A real supplier's
book composition varies run to run / cohort to cohort" (`W2_2_population_draw`'s own
`real_world_twin`, `docs/design/maturity_map.yaml`).

## Sub-capability tree

- **W2_1_archetype_layers** — customer archetype layers (home type, payment channel, tenure,
  fuel poverty, occupancy) for the EXISTING fixed cast. AT TARGET.
- **W2_2_population_draw** — per-run stochastic population draw, replacing today's fixed cast
  (depends on the same reveal-over-time timing discipline as `W1_reveal_over_time` — see
  `docs/design/charters/W1_market_weather.md`'s own sub-capability tree, which already names
  this atom as riding "the same spine's timing discipline").
- **W2_3_competitor_field** — the world-side competitor population. Sibling to lane B's
  `B4_competitor_field` (the company-side/strategic view of the identical missing capability —
  one real market, two faces, same relationship pattern as W1/D2).

## What L2/L3/L4 mean in this lane's terms

**W2_1_archetype_layers (AT TARGET — level 3/3):** "harden" from here means widening real
archetype variety further (e.g. more granular property-type bands) or re-verifying the existing
distributions against a newer survey wave as one becomes available — not a gap, an ongoing
maintenance discipline.

**W2_2_population_draw (genuinely unbuilt — level 0, target 2):**
- **L1 (current):** a fixed cast — `saas/customers.py::CUSTOMERS` is a hardcoded Python list
  literal, identical every run, no RNG over composition/mix/count at all
  (`docs/design/EPOCH2_EVIDENCE.md` Q6, observed-with-evidence). Every run plays "a
  demonstration," in the epoch-2 evidence pass's own words, not "an experiment."
- **L2:** a real, DESNZ/Ofgem-anchored stochastic draw exists that can generate a NEW
  population matching real distributional properties (fuel-poverty incidence, tenure mix,
  payment-channel split, per `W2_1`'s own existing anchors), proven correct in isolation against
  those same real distributions.
- **L3:** the sim actually uses a per-run draw by default, not merely capable of one — today's
  fixed cast becomes an explicit, named regression/comparison baseline rather than the only mode
  that exists.
- **L4:** population draws are exposed as a director-controlled CURRICULUM lever per R13 (CLAUDE.md)
  — named, versioned draw configurations the director authors ("Scenario: high-fuel-poverty
  cohort"), never silently varied by the agent in response to company outcomes. This atom is a
  BASELINE-fidelity question (what does a real supplier's book actually look like across runs) —
  the curriculum use of it is the director's instrument, not this lane's to decide.

**W2_3_competitor_field (genuinely unbuilt — level 0, target 1):**
- **L1 (current):** no competitor concept exists at all — a single-supplier world.
- **L2:** a minimal competitor field exists with real GB-market-anchored pricing behaviour, even
  if simplistic (e.g. a small number of static rival tariffs).
- **L3:** competitors respond dynamically to this company's own pricing/retention actions.
- **L4:** a full multi-agent competitive market matching real GB switching dynamics (churn flows
  both ways, not just outward).

## Named best-practice references

- **DESNZ, *Annual Fuel Poverty Statistics in England, 2025* (2024 data, published 27 March
  2025)**, https://assets.publishing.service.gov.uk/media/67e51e2cbb6002588a90d5d5/annual-fuel-poverty-statistics-report-2025.pdf
  — the LILEE (Low Income Low Energy Efficiency) indicator puts English fuel poverty at ~9.9-11%
  in 2024, continuing a downward trend from 2023 (11.4%). `W2_1`'s own `fuel_poverty_for_customer()`
  anchor should be checked against this more recent figure the next time it's recalibrated (a
  separate decision, not actioned here, matching this codebase's own standing discipline of
  flagging recalibration rather than silently drifting).
- **"Synthetic population generation" / "spatial microsimulation"** — a real, named term of art.
  See the JASSS review *"Generation of Synthetic Populations in Social Simulations: A Review"*,
  https://www.jasss.org/25/2/6/6.pdf, and the ScienceDirect review of reweighting methods for
  synthetic spatial microdata, https://www.sciencedirect.com/science/article/abs/pii/S0198971512000336
  — both confirm this is established practice (transport, health, energy-demand modelling) for
  generating a NEW population matching real distributional properties from aggregate survey data,
  exactly `W2_2`'s own target shape, not a bespoke invention.
- **Ofgem, *State of the Market Report* (retail), 2025**,
  https://www.ofgem.gov.uk/sites/default/files/2025-04/OFG2296_State%20of%20the%20Market%20Report.pdf,
  and Ofgem's own *Retail Market Indicators* data portal,
  https://www.ofgem.gov.uk/news-and-insight/data/data-portal/retail-market-indicators — real,
  current anchor for `W2_3`: **17-21 active domestic suppliers** through 2025 (21 in March, 17 by
  September), with the **top 6 suppliers holding ~91-92%** of the domestic market. This REFINES
  the atom's own `real_world_twin` text ("~8 active suppliers") with a more current, more
  concentrated real picture — worth using when `W2_3` is eventually built: a realistic competitor
  field is a small number of large dominant suppliers plus a long tail, not ~8 evenly-sized rivals.

## Lane roadmap

1. **DONE (already at target):** `W2_1_archetype_layers` — real, DESNZ/Ofgem-anchored
   engagement/payment-channel/tenure/occupancy/fuel-poverty archetypes
   (`simulation/household_segments.py`), deterministically assigned per customer
   (`random.Random(f"engagement_{customer_id}")`, this codebase's standing per-customer-
   deterministic convention).
2. **Next (not this phase):** `W2_2_population_draw` — build the actual stochastic
   draw-generation function once the epoch-2 reveal-over-time spine's sequencing is set by the
   advisor's epoch framing (this atom explicitly rides that same timing discipline per
   `W1_market_weather.md`'s own sub-capability tree). This blocks the epoch-4 tournament
   precondition outright today (`docs/design/EPOCH2_EVIDENCE.md` Q6) — there is currently no
   lever to vary the population between runs at all.
3. **Later:** `W2_3_competitor_field` — the world-side competitor population, sequenced
   alongside lane B's `B4_competitor_field` (same missing capability, company-side face) once
   the director ranks it (per PRIORITIES.md's own P-1 rule).
4. **Curriculum exposure (R13):** once `W2_2` reaches L2, expose population draws as a
   director-authored curriculum instrument — named, versioned scenarios, never silent agent-side
   parameter drift.

## Simplifications register

- `W2_2_population_draw` has zero evidence today (`docs/design/maturity_map.yaml`) — no
  population-generation mechanism exists at all, only the fixed `CUSTOMERS` list literal. This is
  a genuine, registered gap, not a silent omission.
- `W2_3_competitor_field` likewise has zero evidence — a single-supplier world today. Framed here
  explicitly as a BASELINE-fidelity question (what does the real market look like) so that when it
  is eventually built, the "how hard should competitors be" curriculum question (R13) is kept
  separate from and decided after "what does a real competitor field actually look like."
- The newer DESNZ 2024 fuel-poverty figure this pass surfaced (~9.9-11%, LILEE indicator) is a
  DIFFERENT metric from `household_segments.py`'s own preserved ~29% "disengaged" population proxy
  (Ofgem Consumer Engagement Survey) — not a direct comparison. Flagged here only so a future
  recalibration pass doesn't conflate the two distinct anchors.
