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

## The build's per-unit powers, read at source (2026-10-06, executor seat, draw `fabric-electricity-boiler-auxiliary-build`)

**Structure: HEM-TP-14 §5** (DESNZ, *Home Energy Model: boiler methodology*, v3.0, Oct 2025;
<https://assets.publishing.service.gov.uk/media/690236256d9e8bf43eaf70a8/hem-tp-14-boiler-methodology.pdf>),
the government's successor to SAP, models a boiler's electricity as
`P_circ × running time + P_SB × standby time + el_flue × running time`, where `el_flue` for a
modulating boiler is interpolated between the Ecodesign part-load (`elmin`, measured at 30% output) and
full-load (`elmax`) electrical powers. The pump is a separate term from `elmax`. Reg. 813/2013 does
not itself say whether `elmax` includes an integrated circulator (read on EUR-Lex). The build follows
HEM and SAP Table 4f, which both count the pump separately. **If `elmax` does include the pump, the
build double-counts at most about 14 W of fan while running.**

**Fan and controls: Ecodesign 813/2013 product fiches**, three current UK gas boilers:

| Fiche | elmax W | elmin W | PSB W |
|---|---|---|---|
| Worcester-Bosch 24 kW (installer lit. 6720838565) | 29 | 14 | 1 |
| Worcester-Bosch 31 kW (contracts lit. 6720858191) | 42 | 18 | 4 |
| Vaillant ecoTEC plus 637 (VU GB 376/5-5 A, 38 kW) | 38 | 13 | 3 |

The build takes the median of each column: **38 / 14 / 3 W**. Three products are not a sample of the
stock. The spread is carried in the code's comment. These are condensing, fan-assisted boilers. Whether
the oldest band of the stock had a fan-assisted flue at all is **not established**. The build assumes
it did, and says so.

**Pump, fixed-speed (pre-Ecodesign): Grundfos UPS 15-50 N 130 datasheet**
(<https://www.anglianpumping.com/app/uploads/2023/03/97549426_UPS_15-50_N_130.pdf>): **35 W at speed 1,
45 W at speed 2, 50 W maximum.** The build uses speed 2. Which speed the stock's pumps are set to is
**not established**.

**Pump, variable-speed (Ecodesign 641/2009 as amended by 622/2012, EEI ≤ 0.23 for circulators
integrated in products from 1 August 2015):** a variable-speed pump's datasheet gives a range, not an
operating point. Grundfos UPM3 AUTO 15-70 is reported at P1 5–52 W, EEI 0.20. The operating point
is **not established** from a datasheet. The build derives it as `45 W × 41/165 = 11.2 W`. That is
the fixed-speed rating scaled by SAP Table 4f's own ratio of the two pump allowances, on the stated
assumption that SAP gives both the same running hours. It sits inside the UPM3's published range.
It is a derivation from two sources, not a measurement.

**Which pump a boiler has** follows from its install date against 1 August 2015. The household's
`boiler_age` band (NEW 0–5 y, MID 5–12 y, OLD 12+ y) gives the install-year window measured from the
trace's first day. Where the boiler falls inside its band is **one uniform draw per premise. Uniform
is an assumption, not a source.** The stock's real install-year distribution is the gap.

**Pre-registration, written before the term was run** (one gas-combi semi,
`tests/simulation/test_premise_trace.make_household`, seed 42, real 2022 weather, the same premise as
the component table above; the pump kind is forced each way):

- Fixed-speed pump: the Dec–Feb uplift will be **0.4–0.9 kWh/day** and the Jun–Aug uplift
  0.05–0.2 (hot-water firing plus standby). The meter's winter/summer ratio will move from 1.01 to
  **1.04–1.10**. The annual auxiliary total will be **100–220 kWh** (SAP's 165 + 45 = 210 is the
  rating allowance).
- Variable-speed pump: the winter uplift will be 0.2–0.5 kWh/day and the ratio **1.02–1.06**.
- Either way, the term alone does **not** reach SERL's 1.36–1.47. That is the expected outcome, not a
  defect. The rest of the swing is items 1 and 3, which are unsourced.

**Result, against the pre-registration above** (`/tmp/aux_measure.py`; same premise, seed and weather):

| Pump | Aux Dec–Feb kWh/day | Aux Jun–Aug | Annual aux kWh | Meter winter/summer |
|---|---|---|---|---|
| none (before) | 0 | 0 | 0 | 1.01 |
| fixed-speed 45 W | 0.52 | 0.10 | **92** | **1.058** |
| variable-speed 11.2 W | 0.28 | 0.09 | 56 | 1.031 |

The winter uplift, summer uplift and both ratios landed inside their predicted ranges. **The annual
total was refuted:** predicted 100–220 kWh, measured 92. The cause was measured, not argued. The
world's boiler runs **1,049 h a year** (7.3 h/day Dec–Feb, 0.3 h/day Jun–Aug, the summer hours being
hot water). SAP's two pump allowances each imply **3,667 h** at their wattage (165 kWh / 45 W =
41 kWh / 11.2 W). So the wattage is consistent with SAP and the hours are not. Possible causes,
not yet ranked: in real systems the pump runs whenever the programmer is on, not only while the
room thermostat calls; SAP's hours are deliberately generous; or the world's heating runs too few
hours. The third would also understate gas, and the world's gas is graded separately. The term
follows HEM's own convention (pump × boiler running time), so nothing is changed to close the gap.

The meter's monthly max/min moved from 1.18 to 1.21 with **March still the minimum**: one sourced
term makes the season visible on Dec–Feb against Jun–Aug, but the month-to-month noise of the
unseasonal components still dominates the monthly shape. SERL's 1.36–1.47 band is not reached, as
predicted. The rest is items 1 and 3.

**Not landed.** The term breaches the L1.1 texture floor for one home of the 60-home harness panel
(0.1495 against 0.15; 0.1526 before the term). It is parked as
`docs/design/frame/W1_BOILER_AUXILIARY_ELECTRICITY_BUILT_BLOCKED_ON_L1_1.patch`, and the decision it
needs is in `docs/staging/SEAT_FINDING_THE_FABRIC_PATH_GIVES_A_GAS_HEATED_HOMES_ELECTRICITY_NO_SEASON_2026-10-06.md`.
