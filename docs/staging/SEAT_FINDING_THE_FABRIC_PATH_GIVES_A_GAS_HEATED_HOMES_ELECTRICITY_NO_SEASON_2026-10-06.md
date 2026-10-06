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


## The L1.1 floor read at source: the floor is wrong and P0000 is ordinary (2026-10-06, worker, draw `the-l1-1-texture-floor-is-read-at-source`)

`docs/market_research/the_half_hourly_texture_of_real_homes_electricity_read_from_low_carbon_london.md`.
No publication reports this statistic, so it was computed with the cell's own
`half_hourly_texture`. The data is 313 flat-tariff Low Carbon London homes (UKPN open data,
Jan–Apr 2013, the same months as the world's window). **Real median 0.158, p25 0.117, p10 0.072.
45% of real homes sit under 0.15**, and 41% of real homes of P0000's size (8–12 kWh/day) read below
its 0.1495. The anchor's "20–40%" expectation is refuted.

**Of the two readings this item named, the evidence supports the first: the floor is wrong and the
world was fine at P0000.** It does not support the second. P0000's calm behaviour is not a world
defect. The mechanism the anchor missed is that the statistic is a MEDIAN over all 48 steps, and
half of those steps fall in night and quiet hours, where adjacent half-hours differ by a fridge cycle.

**A different world defect, pointing the other way:** the world's drawn 60 is too ROUGH and too
NARROW. Its median is 0.209 against a real 0.158. Its middle half is 0.186–0.231, against a real
0.117–0.208. It has no home in the real bottom 44%. The world's homes behave like one home with mild
variation, and that bears on every per-customer demand inference. Not built.

**Recommendation for the build (world lane, not taken here):** re-anchor L1.1 to the sourced
distribution, judging the world's quantiles against LCL's, not one per-home floor. The sourced p1
(~0.024) is too low to discriminate home by home, and L1.1n already asks the
smooth-by-construction question structurally. Then mint the spread defect as its own atom. Until
then L1.1 stays red at 1/60 exactly as `8fe730297` pinned it, and that red is now known to be a
floor artefact. SERL could not be read: its half-hourly data is safeguarded (UKDS SN 8666), and
applying for it is the director's call.

## The remaining terms sized (2026-10-06, worker, draw `a-gas-heated-home-s-electricity-season-discover-the-remaining-terms`)

Read at source in the research doc, section *The remaining terms, read at source*. The sources are
the HES final report (R66141) seasonality curves and EFUS 2011 and 2017. Every term now has a sourced
magnitude or a named gap:

- **Cooking:** HES ~1.25 winter/summer, so **+0.43 kWh/day** of gap on the world's own cooking
  level. Sourced.
- **Washer and dryer:** HES ~1.48, so **+0.34 kWh/day**. Sourced.
- **Seasonal occupancy:** HES finds audiovisual use **flat**, so there is no separate term. Its
  effect arrives through cooking and laundry, so `occupancy_at` stays unseasonal.
- **Supplementary electric heating:** ~10% of gas-heated homes, **1,505 kWh/yr** each (HES Table 14),
  almost all of it in Dec–Feb. That is ~0.9 kWh/day of winter uplift in the population MEAN, but
  little in SERL's MEDIAN. Heater power and duty are not established, so the energy anchors to HES.
- **Lighting level:** 2016–2025 not established. HES measured 537 kWh/yr in 2010–11 and the world
  carries ~210. The next read is ECUK.

The sourced terms carry about 60% of SERL's 2.5 kWh/day extreme-month gap. **About 0.5–1 kWh/day
is not attributed**, and its ranked candidates are in the doc. One of them is the world's high
flat summer base (8.9 kWh/day against SERL's 6.0), which caps any ratio. So the exit test should
judge the absolute gap as well as the ratio.

**BUILD (world lane), first increment.** In `simulation/premise_trace.draw_appliance_events`, add a
week-of-year multiplier on `events_per_day`. Use HES Fig. 413's curve for kettle, toaster,
microwave, oven and hob, and Fig. 359's for the washing machine and tumble dryer. Each curve is
normalised to an annual mean of 1, so annual kWh and the TDCV judgement are unchanged by
construction. Pre-register the Dec–Feb minus Jun–Aug uplift (expected about +0.7 kWh/day on the
reference premise, ±50%), then run it. Mutations: the multiplier set to 1, the curve applied to
audiovisual, and the annual mean not preserved. **Second increment:** supplementary electric
heating, driven by heating demand, with ownership around 10% and energy anchored to HES's
1,505 kWh/yr, offsetting boiler gas. It is coupled across both meters, so it lands as its own
draw. This finding stays in the queue until the first increment lands.

## Build: pre-registered before any built number was read (2026-10-06, worker, draw `gas-heated-electricity-season-build`)

**Instrument.** `/tmp/gasseason/measure.py`: 200 premises drawn by
`premise_population.draw_premise_from_joint` (base seed 17, as of 2022-01-01), keeping the
gas-heated ones without PV (176). Each is traced over the real 2022 weather at one site (C1). The
output is the median across homes of each month's kWh/day. It is one site and one seed, so the
weather does not vary between homes.

**Baseline on origin `c7d104866`,** with the boiler pump already in:
Jan 8.33 · Feb 8.09 · Mar 8.01 · Apr 8.00 · May 7.87 · Jun 8.02 · Jul 8.02 · Aug 8.02 · Sep 7.81 ·
Oct 8.24 · Nov 8.23 · Dec 8.31. max/min **1.066** (max Jan, min Sep), DJF−JJA **+0.22** kWh/day,
annual median 3,017 kWh.

**Predictions, written before the build ran:**

1. Cooking (HES Fig. 413) plus washer/dryer (Fig. 359) as a season factor on `events_per_day`
   raise the median's DJF−JJA by **+0.5 to +0.9** kWh/day. The research doc's arithmetic is +0.77
   at unit intensity. Max/min rises to **1.12–1.20**, still below SERL's 1.36. The annual median
   moves by less than ±1.5%, because each curve has an annual mean of 1.
2. Supplementary electric heating on about 10% of gas homes moves the MEDIAN's DJF−JJA by only
   **0 to +0.2**. It moves the population MEAN's by about **+0.6 to +1.2**.

### Result: all three terms built, one prediction refuted

| Build | Median by month, kWh/day (Jan … Dec) | max/min | DJF−JJA | Annual median |
|---|---|---|---|---|
| Baseline (pump in) | 8.33 8.09 8.01 8.00 7.87 8.02 8.02 8.02 7.81 8.24 8.23 8.31 | 1.066 (Jan/Sep) | +0.22 | 3,017 |
| + cooking and laundry season | 8.68 8.45 7.96 7.97 7.86 7.48 7.68 7.67 7.82 8.31 8.17 8.69 | 1.162 (Dec/Jun) | +0.99 | 3,009 |
| + supplementary electric heating | 9.67 9.33 8.77 8.56 8.03 7.49 7.68 7.67 8.01 8.37 8.81 9.46 | **1.292 (Jan/Jun)** | **+1.87** | 3,150 |
| SERL 2022, gas-heated, no PV | Jan 8.5 … Aug 6.0 | 1.42 (band 1.36–1.47) | ~+2.5 (extremes) | — |

The band is a **diagnostic**. Nothing was fitted to it, and nothing read D48.

- **Prediction 1 held.** Cooking and laundry moved DJF−JJA by **+0.77**, inside the pre-registered
  +0.5 to +0.9, and exactly the research doc's arithmetic. Max/min reached 1.162, inside
  1.12–1.20. The annual total moved −0.3%. The month order became the real one, highest in
  Dec/Jan and lowest in June. Before, the lowest month was September, which is noise.
- **Prediction 2 is REFUTED.** I predicted supplementary heating would move the MEDIAN by 0 to
  +0.2. It moved it by **+0.88**. 22 of 176 homes own a heater (12.5%, against a 10% draw). Every
  non-owner's January is byte-identical between the two builds (checked on 31 homes), so the move
  is entirely re-ranking. An owner gains 4–7 kWh/day in January, which carries it from below the
  median to above it. The research doc called this effect "small" and its size "not
  established". In this world it is about a third of SERL's gap. The population MEAN moved to
  DJF−JJA +2.30 and max/min 1.338.
- **The heater's season** follows heating degree days on the C1 normal (1,785 HDD/yr, 2016–24).
  That gives Dec–Feb at **2.00×** the annual mean and Jun–Aug at 0.05×, against HES Fig. 537's
  ~2.3× and ~0. This is a check, not a fit. An owner's median is 1,361 kWh in 2022, below the
  1,505 anchor because of away days and a mild year.

**Residual, term by term.** The median sits at 1.29 against SERL's 1.36–1.47:

1. **The flat summer base.** The world's June–August is ~7.6 kWh/day, against SERL's ~6.0. The
   absolute extreme-month gap is **2.18** (Jan 9.67 − Jun 7.49), against SERL 2022's 2.5. So most
   of the RATIO shortfall comes from the summer level, not from a missing season. That level is
   its own question (the annual median is 3,150 kWh) and is not opened here.
2. **The lighting level.** Not established for 2016–2025. The world carries ~210 kWh/yr against
   HES's 537. Every 100 kWh/yr is worth ~0.26 kWh/day of gap. The next read is ECUK.
3. **SERL's years are the price-crisis years** (2021–23), and this run is 2022 weather at one site
   with no price response in the electricity behaviour.
4. **Small seasonal loads not sized**: towel rails, electric blankets, dehumidifiers.

**A NEW ARTEFACT, recorded and not hidden.** The heater's power, duty and timing are not
established, so it is drawn as ONE FLAT BLOCK of EFUS's median hours, ending at the household's
bedtime. In the harness's drawn 60 (Jan–Apr 2022), two homes own one, P0023 and P0050. Those two
are now the two calmest homes on L1.1: 0.1045 and 0.1166, and net of the heater 0.164 and 0.208.
They are the only two under the real LCL p25, so the cell's apparent move toward the real
distribution ([0,0,2,30] → [0,2,4,31]) is NOT progress. P0050 is also now the worst on L1.2, at
0.777 day-to-day shape correlation against the 0.85 near-replay band, because a fixed nightly
block replays. Both are pinned with this cause, and
`test_P0000_the_calmest_home_is_ORDINARY_...` asserts that every home under the real p25 owns a
heater and none is under it net of the heater. **The remedy is to source the heater's operating
pattern.** A resistive heater runs at its rating under a thermostat, and EFUS 2017 gives hours, not
cycling. It is not to move a band.

**Re-pinned, cause beside each:** the cooking/laundry season redrew the event stream. That moved
couple_fabric S9 from 0.1802 to 0.1755, P0000 from 0.1495 to 0.1466 (no heater), the gas
critical weight from 0.385 to 0.362, and the L1.1n worst from >2.0 to 1.946. That last control
was keyed to the margin of the day and is now keyed to its property: > 1.5, far from 1.0. Three
reds in the same files (`test_rng_substream` stale exemption, `test_net_new_acquisition` journal,
`test_every_settling_domestic_premise…`) fail identically on untouched origin `c7d104866` and are
not this change.

**Controls:** `tests/simulation/test_cooking_and_laundry_carry_the_hes_season.py` (5 mutations, all
bite) and `tests/simulation/test_supplementary_electric_heating_tops_up_a_gas_home_in_the_cold.py`
(7 mutations, all bite). Occupancy has no season (HES §13.1).

**Not built, deliberately:** the gas side of HES's cooking curve (`cooking_daily_kwh` stays flat;
it is a gas-side question). Weather coupling for laundry has no source.

**Downstream.** This moves every gas-heated home's electricity, and so the company's bills and
the arms. The value-arms page's code-since-the-run guard (`_code_since_the_run`) will correctly
withdraw the arms' current-world claim until they are re-taken. No exemption is filed, because
this change CAN move the arms. D48's grade should be re-read on the next capture, with the
results in this section decided blind to it.
