**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 4 · **Atom:** `unminted`

**Knowledge:** none -- this is a SIM fidelity DISCOVER pass, not a knowledge-layer anchor. No knowledge
page covers how a household's electricity moves through the year; the nearest, metering-and-reads,
covers how reads arrive and not what they read.

# The seasonal swing of a gas-heated home's electricity, and where the world loses it

**Researched and measured 2026-10-06**, worker on the delivery seat's lane-0 draw
`fabric-electricity-season-discover`, answering
`docs/staging/SEAT_FINDING_THE_FABRIC_PATH_GIVES_A_GAS_HEATED_HOMES_ELECTRICITY_NO_SEASON_2026-10-06.md`.
Decided blind to D48: nothing below reads a company figure. **Nothing is built.**

## What the published record says

**SERL Statistical Report Vol 2** (Smart Energy Research Lab, UCL, rev. 2025;
<https://discovery.ucl.ac.uk/id/eprint/10189780/7/SERL_Stats_Report_Vol_2_rev.pdf>), about 13,000
smart-metered GB homes, of which 10,560 are gas-heated. Figure 4 and Table 3 give the **median
across homes** of daily electricity imports per month, for homes **with gas central heating and
without PV**. That is exactly the population at issue.

| Year | Lowest month | Highest month | Max / min |
|---|---|---|---|
| 2021 | 6.6 kWh/day (June) | 9.7 (January) | **1.47** |
| 2022 | 6.0 (August) | 8.5 (January) | **1.42** |
| 2023 | 5.8 (June) | 7.9 (December) | **1.36** |

The temperature-band view (§3.3, Figure 5) says the same thing: electricity in these homes rises
**30–50%** from days of 20–25 °C to days of −5–0 °C (2021: 6.6 → 9.8; 2022: 6.1 → 8.2).

SERL's own attribution, in its words: *"electric supplementary heating, increased lighting,
increased preparation of hot meals and hot drinks, and possibly increased indoor activities"*.
It also notes that air conditioning is still uncommon in GB homes.

**Household Electricity Survey 2010–11** (DECC/DEFRA/EST, 250 homes; *Early Findings*,
<https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/275483/early_findings_revised.pdf>)
gives the direction for one component: cold appliances use **more** in summer. Fridges and
freezers are at least 36% of baseload in summer and 25% in winter. Magnitude not read here.

This supports the finding's premise from a better source than PC1: PC1 is a class average that
includes some electrically heated homes, while SERL's figure is gas-heated only, and the swing is
still about 1.4.

## What the world does, by component

The swing sits in `generate_premise_trace` (`simulation/premise_trace.py`), in the base-load loop
and the event draw. Measured on one gas-combi semi (`tests/simulation/test_premise_trace.make_household`,
seed 42) over the real 2022 weather. Each component is isolated by zeroing its kW constant on the
same seed; the switch stream's draws do not depend on the kW, so the difference is exact.

| Component | Dec–Feb kWh/day | Jun–Aug kWh/day | Ratio |
|---|---|---|---|
| Meter electricity | 8.93 | 8.84 | **1.01** |
| Lighting (daylight-gated) | 0.82 | 0.32 | 2.54 |
| Electronics | 2.31 | 2.29 | 1.01 |
| Cold appliances | 1.37 | 1.76 | **0.77** |
| Event appliances + standby (residual) | ~4.4 | ~4.5 | ~1.0 |

Monthly, 2022: the world's max/min is 1.18, but its minimum is **March** and its maxima are January
and September. That is noise, not a season. SERL's 2022 is 1.42, with January highest and August
lowest.

So the world does have **one** seasonal term, and it is correctly signed: lighting, about +0.5 kWh/day
in winter. The cold appliances are also correctly signed, opposite to lighting (HES), and take back
about 0.4 kWh/day of it. **Nothing else in the trace knows what month it is.**

## Where the swing should come from, ranked by evidence

1. **Supplementary electric heating in gas-heated homes.** SERL names it first. The trace has no
   such term: a gas-heated home's space heat is 100% gas. Its **magnitude is NOT ESTABLISHED**: no
   source read here says what share of gas-heated homes run a plug-in heater, or for how much. SAP's
   secondary-heating fraction is a rating convention, not an observation, and is not a source for this.
2. **Boiler auxiliary electricity (pump, flue fan, controls).** This is physics the trace omits
   entirely: a gas boiler draws electricity while it fires. SAP Table 4f (and SEAI DEAP Table 4.9,
   which mirrors it) carries an allowance, reported by search as **130 kWh/yr for the
   central-heating pump and 45 kWh/yr for the flue fan**. **NOT verified at source** (the SEAI page
   returned 403, and the SAP 2012 code reference takes them as inputs). Read the SAP 10.2 Table 4f
   PDF before any constant is written. If it is confirmed, it should be tied to the boiler's own
   firing hours, which the trace already computes, and not to a calendar. On those figures it
   carries perhaps a third of the published swing.
3. **Cooking, hot drinks and indoor occupancy.** `draw_appliance_events` and `occupancy_at` have no
   season. SERL names both. Magnitude not established. HES's appliance-level monthly data is the
   place to read it; not done here.
4. **Lighting level.** The swing is present and steep (2.54), but the level is low: about 0.57 kWh/day,
   or 210 kWh/yr (`_LIGHTING_KW_PER_PERSON = 0.035`). The source for that level was not checked, so
   whether the lighting term is too small is open.
5. **Cold-appliance amplitude.** The direction is confirmed. Whether a 28% summer uplift is right is
   not.

## What done means for the build that follows

The exit test should not be a ratio for one home. It should be the **median across a set of
gas-heated fabric premises** of monthly electricity, with January or December highest, June to
August lowest, and max/min in SERL's 1.36–1.47 band, read as a diagnostic band (R12), not a target.
Each term added must come from a source; none of them should be fitted to reach the band.

## What is not established

- **The per-household distribution of the ratio** for gas-heated homes. SERL publishes the
  monthly median and annual percentiles, not the distribution of each home's own winter/summer
  ratio. The director decided not to pursue SERL microdata (`the_sample_is_8500_households_…md`),
  and this pass does not reopen that decision. The published median is the only anchor.
- The magnitudes of items 1, 3, 4 and 5 above. Item 2 is now read at source (section below); the pump-age split of the stock is not.
- The measurement is one premise on one seed. It matches the finding's 56 households at 0.93–1.09,
  but it is not itself a population.

## Item 2 read at source (2026-10-06, executor seat, same draw)

**Correction to item 2 above:** the "130 kWh/yr" pump figure is not SAP 10.2's. **SAP 10.2
(17-12-2021), Table 4f, p.168** (BRE, <https://files.bregroup.com/SAP/SAP%2010.2%20-%2017-12-2021.pdf>):

| Equipment | kWh/year |
|---|---|
| Circulation pump, 2013 or later | 41 |
| Circulation pump, 2012 or earlier | 165 |
| Circulation pump, unknown date | 115 |
| Gas boiler flue fan (if fan-assisted flue) | 45 |

Pump figures ×1.3 with no room thermostat. Note d) says the boiler figures come from Ecodesign
(811/2013) power measurements. The 45 kWh/yr flue fan is confirmed. SAP's internal-gains table
(Table 5a) sets the pump to **zero in summer months**, so SAP itself treats this electricity as
heating-season load.

**What this is and is not.** It is a rating allowance built from product power ratings. It is not
an observation of metered homes, so it bounds the term rather than measuring it. The physical term
is pump and fan power multiplied by the hours the boiler circulates, and the trace already
computes those hours.

**Size against SERL, arithmetic only:** a pre-2013 pump plus a fan-assisted flue gives 210 kWh/yr.
Spread over a heating season of about 7 months, that is about 1.0 kWh/day in winter and about zero
in summer. SERL's 2022 median runs 8.5 → 6.0 kWh/day, a gap of about 2.5. At the 2012-or-earlier
rating, the auxiliary term carries **about 40%** of the published swing. At the 2013-or-later rating
(41 + 45 = 86) it carries about 15%. Which of the two applies depends on the pump-age split of the
stock, which is **not established** here. The rest stays with items 1 and 3, whose magnitudes are
still unsourced.

**Build implication.** The world-lane BUILD has one sourced term it can write now: boiler-auxiliary
electricity at rated W during the boiler's own circulation hours. It needs the pump's rated W,
which the build should take from the per-unit power behind Table 4f (or from Ecodesign
circulator-pump EEI limits), not back-solve from kWh/yr. It also needs a pump-age assignment
that carries its gap explicitly.
