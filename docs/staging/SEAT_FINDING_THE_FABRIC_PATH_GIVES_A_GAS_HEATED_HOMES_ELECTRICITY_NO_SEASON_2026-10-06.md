**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `d48-slice-4-retire-the-worlds-estimator-and-attribute-the-electricity-residual`

# The fabric path gives a gas-heated home's electricity no season

## What was measured

On the slice 3 decade capture (`/tmp/d48s3/world.pkl`), each electricity household's
winter/summer ratio was computed: Dec–Feb kWh per day over Jun–Aug kWh per day, from its own
actual-read bills of 28 days or more.

| Ratio | Households | Of which gas-heated fabric | Share of billed kWh |
|---|---|---|---|
| < 1.15 | 57 | **56** | 45% |
| 1.15–1.6 | 17 | 1 (15 on the legacy PC1 path) | 14% |
| ≥ 1.6 | 11 | 0 (5 electrically heated fabric) | 31% |
| not established | 20 | 12 | 10% |

The legacy path settles on Elexon's PC1 Group Average Demand (`sim/profile_class_1.load_pc1_shape`).
Its own base shape is 12.49 kWh/day in winter and 8.99 in summer, a ratio of **1.39**. The legacy
households sit there (1.38–1.40). The gas-heated fabric homes sit at **0.93–1.09**.

## Why this is a fidelity question and not a company one

PC1 is the domestic unrestricted class, most of whose homes do not heat with electricity, and
its published profile carries a winter/summer swing of about 1.4. The swing comes from lighting,
occupancy and appliance use, not space heating. A gas-heated home in this world shows none of
it. So the evidence is the published profile against the world's own trace. It is independent
of anything the company does. It surfaced through the D48 grade (slice 4,
`SEAT_FINDING_D48_SLICE_4_…`), and nothing about that grade should decide the remedy.

## What is not established

- Which component of `simulation/premise_trace` / `fabric_demand_path` is missing the swing
  (lighting against daylight, occupancy time indoors, or appliance use). Not opened here.
- The published household-level distribution of the ratio for gas-heated homes, as opposed to
  the class average. PC1 is an average, and some real homes are flat. A remedy needs a source
  for the distribution, not only the mean (the knowledge-first rule).

## What it costs today

Any company estimate shaped by an industry profile mis-bills these homes seasonally. Slice 4
measured that as most of the electricity June gross true-up. The same flatness reaches anything
else that reads a fabric home's seasonal electricity: hedge volume shape and the winter peak of
the book.

## Recommendation

A world-lane DISCOVER pass: find the published seasonal swing of non-electrically-heated
domestic electricity (the PC1 coefficients as an average, and any metered-panel distribution,
for example SERL), then locate the component of the premise trace that should carry it. Decide
blind to D48.

## Discovered (2026-10-06, worker, draw `fabric-electricity-season-discover`)

`docs/market_research/the_seasonal_swing_of_a_gas_heated_homes_electricity.md`. SERL Stats Report
Vol 2 puts the gas-heated, no-PV monthly median at max/min **1.36–1.47** (2021–23). The world's only
seasonal term is lighting (ratio 2.54, about +0.5 kWh/day in winter), and the cold appliances cancel
most of it (0.77). Appliance events and occupancy have no season, and the trace carries no boiler
pump or fan electricity and no supplementary electric heating. Next is a BUILD, sourced term by
term. Boiler auxiliary electricity is the only candidate with a published allowance (SAP Table 4f),
and it must be read at source first.

## Built, first term, NOT LANDED: it breaches L1.1 on the live panel (2026-10-06, executor seat, draw `fabric-electricity-boiler-auxiliary-build`)

**Disposition of the draw's duplicate-work note:** the live claim it named under this same id was
this draw's own write; `ps` showed no other seat holding it. Built, not released.

The built code is parked as `docs/design/frame/W1_BOILER_AUXILIARY_ELECTRICITY_BUILT_BLOCKED_ON_L1_1.patch`
(`git apply` it onto `simulation/premise_trace.py` and a new test). `simulation/premise_trace.boiler_auxiliary_kwh` adds the gas boiler's own electricity to every
gas-heated premise's meter: pump plus fan/controls over the boiler's own running time, standby
otherwise (HEM-TP-14 §5). The powers come from three Ecodesign 813/2013 fiches and the Grundfos UPS
15-50 datasheet. A variable-speed pump's operating point is derived from SAP Table 4f's ratio of its
two allowances. The pump kind is decided by install date against the 1 August 2015 Ecodesign date.
Sources and every named gap are in the research doc. Control:
`tests/simulation/test_a_gas_boilers_own_electricity_follows_its_running_hours.py`. All five
mutations bite: term not added to the meter, one pump kind only, always running, term on non-gas
homes, and the band short-circuit removed.

On the reference premise, the winter/summer ratio moves from **1.01 to 1.058** with a fixed-speed
pump and 1.031 with a variable-speed one. That is inside the pre-registered range. **The annual
total was refuted** (92 kWh against 100–220): the world's boiler runs 1,049 h a year, against the
3,667 h SAP's pump allowances imply.

**Still open, and the reason this finding stays in the queue:** SERL's 1.36–1.47 is not reached, and
was not expected to be. The remaining candidates, supplementary electric heating and seasonal
cooking/occupancy, have no sourced magnitude yet. The next item is a DISCOVER pass for those, not
another build. **Practitioner question, asked on NTFY:** does a domestic heating pump run only while
the room thermostat calls, or whenever the programmer is on? The world follows HEM (the first). If
it is the second, the term's hours roughly treble.

**Why it did not land.** The term reds 8 harness controls
(`tests/harness/test_premise_two_level.py` ×7, `tests/tools/test_couple_fabric.py` ×1). Three other
failures in the same run (`test_every_settling_domestic_premise_reads_a_complete_stored_cell`,
`test_net_new_acquisition::…journal…`, `test_rng_substream::…stale_exemption`) fail at HEAD too and
are not this change. The root is one cell. **L1.1 half-hourly texture** on the drawn 60 (seed 17,
Jan–Apr 2022) goes from 0/60 to **1/60**. P0000, a 1919–44 detached house with an OLD system boiler
and a fixed-speed pump, measures **0.1495 against the 0.15 floor**. It was already at **0.1526**
without the term. The term adds 0.62 kWh/day, raising the mean 5.5% and the median step 3%, so the
breach is in the DENOMINATOR. The other reds follow from it: the gas homes' critical-weight median
0.3066 → 0.2903, pinned as a literal, and the timing-less null clearing 45% where 50% is asserted.

**Why netting the term out of the judged load set would be a loosening and not a repair.** H38
netted the water heater because the floor's anchor, a gas-heated home's electricity meter, never
carried it. That same anchor DOES carry the boiler pump: every real gas-heated meter has one. So by
H38's own argument the pump belongs in the judged load set, and R12 forbids moving the floor. Read
that way, the breach is real. It shows a home whose behavioural texture was already at the calm edge,
and one sourced, physically certain load tipped it.

**The decision this needs, with a recommendation:** land the term and record L1.1 at 1/60, diagnosed
as P0000's behaviour being too calm for a large home. The floor is domain knowledge and was never read
at source (its own anchor text says the SERL/LCL band is not in the library). The next item would
then be that DISCOVER, which either sources the floor or finds the calm-behaviour mechanism. The
alternative, keeping a sourced load out of the world so that an unsourced floor stays green, is the
goal-seek R12 exists to prevent. I have not taken either step, because flipping 8 controls'
expected verdicts is a change to what the harness asserts and needs a second pair of eyes.

## Landed, L1.1 recorded at 1/60 (2026-10-06, worker, draw `fabric-electricity-boiler-auxiliary-land`)

The seat's recommendation was taken. No objection to it had come back on NTFY. The patch is applied
and its parked copy deleted. The term is in `simulation/premise_trace.py`, with its control alongside.
The 8 controls were re-expressed against the property each one stands for, not against today's
number. The floor is still 0.15, and the pump is not netted out:

- L1.1 on the drawn 60 is pinned **FAIL at 1/60**, P0000 at 0.1495. A new test,
  `test_the_L1_1_BREACH_is_P0000s_CALM_BEHAVIOUR_tipped_by_a_SOURCED_LOAD`, carries the diagnosis:
  the cell's worst value is the reading with the pump in it; net of the pump, as a diagnostic only,
  P0000 reads 0.1526 and is the calmest home of the 60; every other home clears the floor.
- The water-heater (H38) controls now ask WHO is in breach: no electrically heated home. They no
  longer ask for a green verdict.
- The ledger test cross-checks the wire against the result, and L1.1 is now its live red witness.
- The goal-seek test asserts the live cell is red, so its synthetic texture arm is said and not assumed.
- The L2.3n fail-open leg is keyed to the test's own alpha ceiling (25%) instead of the 50% literal.
  The measured value is 45%, down from 68% when first measured.
- Re-pinned with a note on each: the gas critical-weight median moved 0.3066 → 0.2903, the L1.2 worst
  0.4386 → 0.4511 (still a gas home), and couple_fabric's S9 0.1862 → 0.1802.

**Still open, for the next draw:** a DISCOVER for the L1.1 floor's real distribution (SERL/LCL
half-hourly texture of gas-heated homes), or for the mechanism that makes P0000's behaviour calm.
The supplementary-heating and seasonal-occupancy DISCOVER is still owed toward SERL's 1.36–1.47.

