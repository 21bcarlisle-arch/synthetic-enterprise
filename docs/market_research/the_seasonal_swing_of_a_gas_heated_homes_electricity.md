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

**Landed 2026-10-06, with L1.1 recorded red at 1/60.** The term breaches the L1.1 texture floor for
one home of the 60-home harness panel: P0000 reads 0.1495 against 0.15, and read 0.1526 before the
term, already the calmest of the 60. The pump stays in the judged load set because a real gas-heated
meter carries one, and the floor did not move. The diagnosis is pinned in
`tests/harness/test_premise_two_level.py::test_the_L1_1_BREACH_is_P0000s_CALM_BEHAVIOUR_tipped_by_a_SOURCED_LOAD`.

**The pump-hours question is still open.** It was asked on NTFY on 2026-10-06: does a domestic
heating pump run only while the room thermostat calls, or whenever the programmer is on? No answer
had arrived when the term landed. The world follows HEM, which is the first reading. If the answer
is the second, the 1,049 h above roughly treble towards SAP's 3,667 h.

## The remaining terms, read at source (2026-10-06, worker, draw `a-gas-heated-home-s-electricity-season-discover-the-remaining-terms`)

This pass sizes the seasonal terms still missing after the boiler pump: supplementary electric
heating, plus seasonal cooking, occupancy and lighting. Decided blind to D48. **Nothing is built.**
The read-off values below come from published curves read by eye, to about ±0.05 on each factor.

### Sources

- **HES final report.** Intertek R66141, *Household Electricity Survey: A study of domestic
  electrical product usage*, issue 4, May 2012 (DEFRA/DECC/EST; 251 owner-occupied English homes,
  2010–11; 26 of them monitored for a full year;
  <https://assets.publishing.service.gov.uk/media/5a7c2fd940f0b67d0b11f6df/10043_R66141HouseholdElectricitySurveyFinalReportissue4.pdf>).
  For each appliance group, it publishes a 52-week **seasonality curve**, normalised to an annual
  mean of 1 and fitted on the 26 year-long homes.
- **EFUS 2011 Report 5.** *Secondary heating systems*, BRE 286733b for DECC, Dec 2013, n=2,616
  (<https://assets.publishing.service.gov.uk/media/5a74a0b3e5274a44083b8337/5_Secondary_Heating.pdf>).
- **EFUS 2017.** *Heating patterns and occupancy*, final report, BEIS 2021, winter interview
  n=1,340 (<https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1018727/efus-heating-patterns-occupancy.pdf>).
- **HES lighting.** CAR for DECC, *Further analysis of the Household Electricity Survey: Lighting*
  (<https://assets.publishing.service.gov.uk/media/5a7dbc54e5274a5eaea66049/Lighting_Report.pdf>).
- **HES summary paper.** Dunbabin, Palmer & Terry, ECEEE 2015,
  *The English Household Electricity Study 2010–11*
  (<https://proceedings.eceee.org/docs/2015/7-009-15_Dunbabin_pre.pdf>).

### HES seasonality curves against the world's components

The factors are each category's Dec–Feb and Jun–Aug mean, read from the curve.

| Group (HES figure) | Dec–Feb | Jun–Aug | Ratio | HES annual | World today |
|---|---|---|---|---|---|
| Cold appliances (Fig. 334) | ~0.83 | ~1.12 | ~0.74 | 162–427 per unit | **0.77, right** |
| Lighting (Fig. 465) | ~1.55 | ~0.60 | ~2.6 | 537 kWh | **2.54, shape right**; level below |
| Cooking (Fig. 413): oven, hob, microwave, kettle, toaster | ~1.09 | ~0.87 | **~1.25** | 460 kWh | **flat, missing** |
| Washing/drying (Fig. 359) | ~1.27 | ~0.86 | **~1.48** | washer 166, dryer 394 | **flat, missing** |
| Audiovisual (§13.1) | — | — | **1.0** | 553 kWh | flat, **right** |
| Space heating, additional-electric homes only (Fig. 537) | ~2.3 | ~0 | — | **1,505 kWh** | **absent** |

§13.1 says it verbatim: *"No seasonality effect was observed"* for audiovisual. **That settles the
occupancy question.** Being at home more in winter would show up first in the screens, and it does
not. So the world must NOT be given a seasonal `occupancy_at`, which would make electronics seasonal
against HES. Occupancy's seasonal effect arrives through cooking and laundry, and HES measures those
directly. Whether Fig. 359 includes dishwashers is not stated. The text says "washing/drying".

### Supplementary electric heating: real, sized, and mostly in the tail

- **Who.** HES (Dunbabin 2015): *"10% of households with gas also use electric heating to top up in
  cold weather."* EFUS 2011 Table 13: 4,197k of 19,691k central-heated households, **21%**, use one
  or more electric supplementary heaters. Table 6 adds **9.2%** who heat a room with an electric
  heater where the main system does not reach. EFUS 2017 reports a decline: supplementary heating
  of any fuel fell from 48% to **39%** of households. Of living-room users (32% of households), 33%
  use an electric heater, so about **11%** of all households.
- **How much.** HES Table 14: space heating of **1,505 kWh/yr** in homes *with additional electric
  heating*. *(Corrected later on 2026-10-06, see the last section: the world now takes CAR's
  656 kWh/yr for homes whose main heating is not electric. Over EFUS's hours, 1,505 needs more
  than a 13 A plug-in heater can draw.)* Their total is 4,878 kWh/yr, against 3,638 kWh/yr for homes without electric heating
  (Figs. 28–29). HES §15.2: *"mainly in the form of individual or portable heaters that were used
  occasionally"*. EFUS 2011: a 4.2-month season (mean), median 8 h/week. EFUS 2017: daily users
  (27% of supplementary users) run it a median of **4 h on a weekday** (IQR 2.5–6) and 5 h at the
  weekend.
- **Season.** HES Fig. 537 is about 2.3× the annual mean in Dec–Feb and about zero from June to
  August.
- **Size.** In a home that has it: 1,505 kWh/yr is ~4.1 kWh/day on average, so **~9.5 kWh/day
  Dec–Feb and ~0 in summer**. Across all homes at a 10% share: **~0.9 kWh/day** of winter uplift
  in the MEAN.
- **The median barely moves.** SERL's 1.36–1.47 is a MEDIAN across homes. A load carried by about
  10% of homes moves the median only by re-ranking homes near it, which is a small effect. So
  supplementary heating explains much of the MEAN's swing (and PC1's), but little of SERL's
  median's. The size of that re-ranking effect is **not established**: computing it needs the
  per-home distribution, which SERL does not publish.
- **Not established:** the heater's power and thermostat duty. 2 kW is a typical nameplate rating,
  not a measured operating point. The build should anchor energy to HES's 1,505 kWh/yr, not to
  watts × hours. Also not established: the 2016–2025 trend between HES/EFUS 2011 and EFUS 2017,
  beyond the 48% → 39% fall in supplementary heating of any fuel.

### Lighting level

HES 2010–11 measured **537 kWh/yr** (Table 25), in a stock of incandescent and CFL bulbs. The HES
lighting report projects **~290 kWh/yr by 2024** if 80% of lamps are low-energy. The world's
`_LIGHTING_KW_PER_PERSON = 0.035` gives about 210 kWh/yr, constant across 2016–2025. **The 2016–2025
level is not established.** No published per-home figure for the LED era was found (the ECUK
end-use tables were not read). Sensitivity: at HES's shape, every 100 kWh/yr of lighting adds
**~0.26 kWh/day** to the Dec–Feb minus Jun–Aug gap. A real stock trending down across the decade
would make the world's constant wrong at both ends.

### The budget: SERL's gap against what is sourced, as arithmetic (not a run)

The world's cooking and laundry levels are read from `APPLIANCE_CATALOGUE` at unit intensity. That
is power × duration × events: cooking ~1.94 kWh/day (oven 0.83, kettle 0.56, hob 0.44, the rest
0.12), washer plus dryer ~0.83. Dishwasher excluded.

| Term | Dec–Feb minus Jun–Aug, kWh/day | Status |
|---|---|---|
| Lighting (in the world) | +0.50 | built |
| Cold appliances (in the world) | −0.40 | built, HES-signed |
| Boiler pump and fan (fixed-speed) | +0.42 | landed 2026-10-06 |
| Cooking at HES's shape | **+0.43** | sourced, NOT built |
| Washer and dryer at HES's shape | **+0.34** | sourced, NOT built |
| Lighting raised to ~290 kWh/yr | +0.2 | level NOT established |
| Supplementary electric heating | ~+0.9 to the mean; small to the median | sized, NOT built |
| **Sum for a median home, without supplementary heating** | **~+1.5** | |

SERL 2022's monthly extremes, January 8.5 and August 6.0, differ by 2.5. The seasonal-mean gap is
smaller, but SERL's monthly table was not re-read here. The sourced terms carry about **60%** of
it. **What is left, roughly 0.5–1 kWh/day, is NOT ATTRIBUTED.** In rank order, the candidates are:

1. Supplementary heating's re-ranking effect on the median.
2. The world's high flat base. The world's summer is 8.9 kWh/day against SERL's 6.0, and a large
   unseasonal level shrinks any RATIO even when the absolute gap is right.
3. SERL's years being the price-crisis years.
4. Small seasonal loads not sized here, such as heated towel rails, electric blankets and
   dehumidifiers.

**Because of (2), the exit test for the build should compare the absolute Dec–Feb minus Jun–Aug
gap, not only the ratio.**

### Where each term belongs in `simulation/premise_trace`

- **Cooking and laundry go in `draw_appliance_events`**, as a week-of-year multiplier on
  `events_per_day`: Fig. 413's curve for kettle, toaster, microwave, oven and hob, and Fig. 359's
  for the washing machine and tumble dryer. Each curve is normalised to an annual mean of 1. That
  keeps every annual kWh, and so the 2,700 kWh TDCV judgement, unchanged by construction. The curve
  is a calendar fit. The mechanism behind the laundry curve (rain against line-drying) is not
  established, so weather coupling stays out until something sources it.
- **The flat cooking GAS layer (`cooking_daily_kwh`) contradicts this.** It is flat by design and
  says so. If HES's electric cooking curve also applies to gas hobs and ovens, the summer gas base
  is overstated, which is a gas-side question. Flagged here, not changed.
- **Supplementary electric heating is a new per-premise term beside `boiler_auxiliary_kwh`.** It
  needs an ownership draw at the published ~10% share of gas-heated homes. Its use should be
  driven by the world's own heating demand, not the calendar, with energy anchored to HES's
  1,505 kWh/yr. The heat delivered offsets boiler gas, so the term couples both meters. That makes
  it a bigger build than the calendar multipliers, and it comes second.
- **`occupancy_at` gets no seasonal term**, because HES measures audiovisual use as flat.
- **The lighting level stays at `_LIGHTING_KW_PER_PERSON`** until a 2016–2025 level is sourced.
  The next read is the DESNZ ECUK domestic end-use table.

## Built (2026-10-06, worker, draw `gas-heated-electricity-season-build`)

Cooking and laundry carry the season factors above (`premise_trace.appliance_season_factor`).
Supplementary electric heating is in (`premise_trace.supplementary_heating_kwh`): 10% of gas
homes, 1,505 kWh in a normal-HDD year, and it displaces boiler gas through the room's gain. Over
176 drawn gas-heated, no-PV homes in 2022, the median's max/min is **1.292** against SERL's
1.36–1.47, and DJF−JJA is +1.87. The re-ranking effect this doc called small is +0.88 kWh/day in
this world. The residual and a new artefact (the heater drawn as a flat block) are written up in
`docs/staging/SEAT_FINDING_THE_FABRIC_PATH_GIVES_A_GAS_HEATED_HOMES_ELECTRICITY_NO_SEASON_2026-10-06.md`.
The heater's operating pattern (power, cycling and timing) is now the named gap.

## The heater's operating pattern, read at source (2026-10-06, draw `supplementary-heater-operating-pattern-discover`)

- **HES R66141 Appendix IX, p.560, "Heater (individual)":** 46 monitored heaters, averaging
  1,076 kWh/yr (790 on workdays, 286 on holidays). The daily average load curves were read by eye.
  On workdays about 69% of the energy falls between 18:00 and 23:59, peaking at 21:00, with a small
  08:00 blip. On holidays there is a morning peak at 09:00–12:00 as well as an evening one. §15.3's
  Figures 544–545 are all electric heating, storage heaters included, and are not the supplementary
  heater's curve.
- **EFUS 2011 Report 5 §3.3.3:** of weekly users, 28% run supplementary heaters at set times, 65% do
  not, and 7% mix. Of the set-time users, 30% change their times at weekends. Start-time categories
  for set-time weekday users: wake-up 20%, daytime 14%, home-time (15:00–19:00) 56%, evening/night
  33%. Respondents could give more than one.
- **EFUS 2017 §3.6:** daily users run it 4 h on a weekday (IQR 2.5–6) and 5 h at the weekend (IQR 4–8).
- **Still not established:** on-power and thermostat cycling. No source read gives either.

Built in `premise_trace.supplementary_heating_kwh` / `heater_habit`. The result is in
`docs/staging/WORKER_FINDING_THE_SUPPLEMENTARY_HEATER_RUNS_WHEN_HES_AND_EFUS_SAY_AND_ITS_POWER_STAYS_UNSOURCED_2026-10-06.md`.

## The heater's power and cycling, and the lighting level (2026-10-06, worker, draw `gas-heated-electricity-season-the-two-unsourced-terms`)

### The heater's power: no source gives an on-power, and the ENERGY anchor is what was wrong

**On-power and thermostat cycling are NOT ESTABLISHED.** HES R66141 Appendix IX (p.560) publishes the
46 heaters' annual energy (1,076 kWh/yr per heater) and average load curves, not a power when on.
No other source read here gives a measured operating point. **Cycling is also below the meter's
resolution:** a plug-in heater's thermostat switches on a scale of minutes, so inside one half
hour the meter records the session's mean power, which is what an even spread gives. No cycling
term is built, and none is needed for a half-hourly trace. That would stop holding only if
measured cycles longer than 30 minutes were found.

**But printing the implied power at real inputs refutes the energy anchor.** The world spreads
`1,505 × HDD/normal` (C1 normal 1,784.6 HDD) over EFUS's session:

| Anchor kWh/yr | Day at 0 °C, kWh | kW over 2.5 h (EFUS LQ) | kW over 4 h (median) | Day at −3 °C (C1 2022's coldest), kW over 2.5 h |
|---|---|---|---|---|
| 1,505 (HES Table 14) | 13.07 | **5.23** | 3.27 | **6.24** |
| 1,076 (HES App. IX, per heater, all fuels) | 9.35 | 3.74 | 2.34 | 4.46 |
| **656 (CAR, gas and other non-electric homes)** | 5.70 | **2.28** | 1.42 | **2.72** |

A plug-in heater on a BS 1363 13 A socket cannot draw more than 230 V × 13 A ≈ **3.0 kW**. At 1,505,
a lower-quartile session needs 5–6 kW on any cold day. That is physically impossible for one heater
and implausible for the "individual or portable heaters" HES §15.2 describes.

**The source that fits the world's population.** Cambridge Architectural Research for DECC,
*Further Analysis of the Household Electricity Survey, Report 3: Models, labels and unusual
appliances*, "Homing in on secondary electric heating", pp.74–80
(<https://carltd.com/wp-content/uploads/2023/10/Report-3_Models-labels-and-unusual-appliances.pdf>).
This is the same HES survey, re-analysed for the Departments. It defines homes with secondary heating
as **"homes with electric space heaters that were monitored and for which the main heating is not
electric"**: 36 households. It explicitly rejects seasonal factors built from the tiny year-long
sample. Instead it sums, week by week through October to April, the mean of every secondary-heating
home monitored that week (6–11 homes a week, about 8 on average). Result: **656 kWh/yr per home
with secondary heating (5–95%: 610–700)**, and a worst-day 18:00–19:00 load of 0.48 kW. CAR's own
caveats: 40 more households said they had heaters that were never monitored, so the figure is high
if those heaters go unused. And it is about 4.6% of those homes' space-heating gas, against 4.1%
in an Energy Saving Trust field trial (Gastec 2009, 60 homes).

HES Table 14's 1,505 is for the group "with additional electric heating". Its definition was not
found in the report, so whether that group includes homes where electricity heats part of the
dwelling as a main system is **not established**. CAR's definition is the world's population
exactly (`household.is_gas_heated`), its estimator is the more careful of the two, and it is the only
one of the three that a 3 kW socket can deliver in EFUS's hours. **The world now takes 656.**
The HDD scaling, the 10% share, the timing and the session lengths are unchanged.

**Pre-registration, written before anything was run on the new anchor.** The baseline is the
1.292 / +1.87 row above, on origin `b9d1ec2f1`. The heater's timing landed after that row was
measured, but it moves no monthly total, so the baseline is re-read first.

1. **176-home median (`/tmp/gasseason/measure.py 200`, 2022, C1):** DJF−JJA falls from +1.87 to
   **+1.45 to +1.85**, and max/min from 1.292 to **1.22–1.29**, moving further from SERL's
   1.36–1.47. An owner's January uplift falls from 4–7 to about 2–3 kWh/day. That still carries most
   owners above the median, so the re-ranking effect shrinks by less than the energy does.
2. **L1.1, P0023 (set-time owner, 0.1056):** rises to **0.12–0.16**, back towards its 0.164 net of
   the heater. The count under the real p25 falls from 1 to **0**.
3. **L1.2, P0023 (0.578):** falls to **0.45–0.56**, because its repeating session is a smaller
   share of its day. The worst home may change.
4. **L2.4 spread (2.007):** moves by **less than 0.05**.

None of the four is a target. The band is a diagnostic, and the anchor was chosen on population,
estimator and the socket's limit before any of these was read.

**Result, against the pre-registration above** (filled in after the run; the predictions are not
edited). The new anchor is held by
`tests/simulation/test_supplementary_electric_heating_tops_up_a_gas_home_in_the_cold.py::test_one_plug_in_heater_can_deliver_the_anchor_in_efus_s_hours`,
which reds on all four weather sites when the anchor is put back to 1,505.

| | Before (1,505) | After (656) | Prediction | |
|---|---|---|---|---|
| 176-home median, by month Jan…Dec | 9.67 9.33 8.77 8.56 8.03 7.49 7.68 7.67 8.01 8.37 8.81 9.46 | 9.63 9.16 8.60 8.36 7.88 7.48 7.68 7.67 7.89 8.33 8.61 9.34 | | |
| max/min | 1.292 (Jan/Jun) | **1.288 (Jan/Jun)** | 1.22–1.29 | **held** |
| DJF−JJA, kWh/day | +1.87 | **+1.77** | +1.45 to +1.85 | **held** |
| Annual median, kWh | 3,151 | 3,078 | | |
| L1.1 P0023 | 0.1056 | **0.1347**; under the real p25: 1 → **0** | 0.12–0.16; 0 | **held** |
| L1.2 worst | P0023 0.578 | **P0000 0.4417**; P0023 is below that | P0023 0.45–0.56 | **refuted, low** |
| L2.4 spread | 2.007 | **1.931** | moves < 0.05 | **refuted** (0.076) |

Halving the heater's energy moved the median's DJF−JJA by only −0.10. That confirms the
pre-registered reasoning: the median's heater effect is a re-ranking, and most owners stay above the
median on 2–3 kWh/day of January uplift. The ratio stays at **1.29 against SERL's 1.36–1.47**, and
the sourced correction moved it slightly away from the band. That is the right direction for an
honest anchor, and nothing here was fitted to the band. L1.2 and L2.4 moved more than predicted:
P0023's set-time session was a bigger share of its day-to-day shape than estimated, and the owners
sat near the p90 of annual use.

### The lighting level: NOT ESTABLISHED, and the official series has a method break inside 2016–2025

**DESNZ ECUK 2025, End Use Table U3** (domestic consumption by end use and fuel, ktoe; revised
20 April 2026; <https://assets.publishing.service.gov.uk/media/69e6362644a079b27f997f8d/ECUK_2025_End_Use_tables_200426.xlsx>),
electricity for lighting. Converted at 11.63 GWh/ktoe, and divided by UK households (ONS *Families
and households*: 27.0m in 2015, 27.2m in 2017, 28.2m in 2022):

| Year | ktoe | ≈ kWh per household |
|---|---|---|
| 2010 | 1,211.5 | — (HES measured 537 in 2010–11) |
| 2016 | 1,003.3 | ~430 |
| 2019 | 912.4 | — |
| 2021 | 739.3 | ~305 |
| **2022** | **333.3** | **~137** |
| 2024 | 339.8 | ~140 |

The 55% fall from 2021 to 2022 is a **method break**, not behaviour. The ECUK 2025 Methodology Note
(p.11) says: *"From ECUK 2025 the electricity – lighting estimates have been updated to more
accurately capture the reduce in electricity requirement through the introduction of more
energy-efficient lightbulbs."* The years before 2022 were not re-estimated on the new basis. Both
regimes are **modelled** (Fuel Poverty / English Housing Survey inputs), not metered, and the same
note says ECUK's end-use research is in places "over 10 years old".

**What this establishes.** The world's ~210 kWh/yr per home (`_LIGHTING_KW_PER_PERSON = 0.035`,
constant across the decade) sits **inside** the official bracket: below the old method's
430 → 305 for 2016–21, and above the new method's ~137 for 2022–24. No published source gives
a single metered 2016–2025 level, and the official one cannot be read as a trend across 2021/22.
So **the level stays a named gap, and the constant is not changed.** Changing it to either regime
would be choosing a number, not reading one.

**The seasonal amplitude** follows from the level, because the shape is sourced: the world's
Dec–Feb/Jun–Aug lighting ratio is 2.54, against HES Fig. 465's ~2.6. At that shape, each 100 kWh/yr
of level is about 0.26 kWh/day of DJF−JJA. Across the official bracket (137 to 430 kWh/yr), lighting
contributes between about **−0.19 and +0.57 kWh/day** to the median's gap, relative to the world's
210. The 2022 run above is inside the new-method regime, where ECUK's ~137 would make the world's
lighting swing **smaller** by about 0.19 kWh/day, not larger. **Lighting is therefore not where
the remaining distance to SERL's 1.36–1.47 comes from** in 2022. The flat summer base (world
~7.6 kWh/day against SERL's ~6.0) stays first in the ranking of the residual.

### Both terms, closed as the draw asked

- **Supplementary heater:** the power when on is **not established**, and the research doc says so.
  Thermostat cycling is **below the half-hourly meter's resolution**, so no term is needed. The
  energy anchor was **corrected** to CAR's 656 kWh/yr, built and controlled.
- **Lighting level and amplitude:** **not established** for 2016–2025. ECUK brackets the world's
  constant on both sides of a method break. The shape is sourced, and the amplitude follows the
  level. Nothing is changed.

## The day's shape in 2022: the trough is right and the evening peak is 0.32 kWh/h too high (2026-10-08)

**Source, read at source 2026-10-08:** SERL Statistical Report Vol 2 (the same document as above),
§3.4, Figure 7 and **Table 6**: "the median of the mean electricity use in each half hour per
participant", for homes with gas central heating and no PV. For 2022 the minimum is **0.13 kWh/h at
04:30** and the maximum **0.48 kWh/h at 18:30**. 2023 gives 0.13 at 04:30 and 0.45 at 18:30. The table
publishes only the two extremes. The rest of the curve is in the figure and was not read off.

The same report's Table 3 (2022 monthly medians, January 8.5 and August 6.0 kWh/day) is the season
already cited above.

**The world, the same statistic.** Each home's mean kWh/h in each half hour across 2022 (C1 weather),
then the median across homes. 163 drawn gas-heated no-PV premises, base seed 17, origin `faa956270`:

| | Trough | Peak | Annual median |
|---|---|---|---|
| SERL 2022 | 0.13 at 04:30 | 0.48 at 18:30 | ~2,600 (monthly medians summed) |
| World | **0.128** at 03:30–04:30 | **0.803** at 19:30 (0.763 at 18:30) | 3,421 |

**What this says.** A real base load in 2022 is what the world draws. The trough is the always-on
load, the cold appliances and the boiler's standby, and it lands on SERL's 0.13. The world's whole
excess is **above** the base, and it peaks in the evening. A uniform 25 W always-on load would put
the trough at 0.07, half the real figure. So EFUS 2011's base-load anchor survives a 2022 check, even
though it predates LED lighting and the standby regulations.

What this does not say: SERL's figure is a median of means, so it does not split homes. Whether the
real evening peak is low because fewer homes cook electrically, or because each home uses less per
meal, cannot be read from it. The world-side split is in
`docs/staging/SEAT_FINDING_THE_FABRIC_PATH_GIVES_A_GAS_HEATED_HOMES_ELECTRICITY_NO_SEASON_2026-10-06.md`, 2026-10-08 (worker).

### Per-use annual levels: electronics on-mode and cold appliances (read 2026-10-08)

**HES (Intertek R66141, 2010–11), electronics split by state.** These are site averages, for the
audiovisual site and the computer site.

| Site | ON-mode | Standby | Annual (table) |
|---|---|---|---|
| Audiovisual (Fig 501, Table 26) | 123.8 W × 3,118 h ≈ **386 kWh** | 17.8 W × 4,213 h ≈ 75 kWh | 553 all households (441–630 by type) |
| Computer (Fig 535, Table 29) | 88 W × 1,945 h ≈ **171 kWh** | 9.3 W × 5,046 h ≈ 47 kWh | 240 all households (137–267) |

~~ON-mode together is ≈ **557 kWh/yr**.~~ **Corrected 2026-10-08 (executor seat):** 557 is per-SITE
average power × average hours, a product of means. It does not reconcile with HES's own annual
figures, which are per HOUSEHOLD: AV 386 + 75 = 461 against Table 26's 553, and computer 171 + 47 =
218 against Table 29's 240. On-mode per household from those annuals is (553 − 75) + (240 − 47) ≈
**671 kWh/yr**, or ≈ **651** if the on/standby split is applied in proportion. The world's mean, 673
over 163 gas no-PV homes, sits inside that, so the world's electronics is **not** above HES. Standby
belongs with the always-on draw (EFUS 2011's base), which already carries it. The 2010–11 stock was CRT/plasma televisions and desktops, so this is an
UPPER bound for 2016–2025. Standby is minimal 19:00–22:00, when the sites are most used.

**DECC/BRE cold appliances field trial (report HPR187-1003, Jan 2017; 766 households, monitored
Mar–Nov 2015)**
(<https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/585520/Cold_appliances_field_trial_report_FINAL_230117__2_.pdf>):
mean **354 ± 16 kWh/yr per appliance** (fridge-freezer 390, upright freezer 342, fridge with ice-box
274, larder fridge 201). Per household, adjusted to 1.47 appliances: **533 ± 32 kWh/yr** (473 with no
over-consuming appliance, 1,111 with one). England 2014: 10.5 TWh, 15.6% of domestic appliance
electricity, scaled from ECUK Table 3.10.

**Not established:** a 2020s per-use figure for either. ECUK 2025's U3 no longer splits appliances.
**What the world does with them:** see the 2026-10-08 level section of
`docs/staging/SEAT_FINDING_THE_FABRIC_PATH_GIVES_A_GAS_HEATED_HOMES_ELECTRICITY_NO_SEASON_2026-10-06.md`.

## A 2020s per-use trend: how far each 2010–15 figure should have fallen by 2022 (2026-10-08, executor seat, claim `a-gas-homes-per-use-electricity-has-a-2020s-trend`)

**Priors, filed before any 2020s source was opened.** These come from general knowledge of the
appliance-standards decade and are not sourced. They exist only so the read can refute them.

| Per-use figure the world rests on | Prior fall to 2022 |
|---|---|
| Electronics on-mode (HES 2010–11, ~651–671/household) | −25% to −45% (CRT/plasma to LED, desktops to laptops) |
| Cooking (HES Table 23, 2010–11) | −0% to −15% (stock change is slow; induction is marginal) |
| Cold (DECC/BRE 2015, 533/household) | −10% to −25% (A+ minimum from 2014, replacement over about 15 years) |

### Source: ECUK's electrical-product tables, the per-use series ECUK 2025 dropped

**DESNZ, ECUK 2023 Electrical Products tables** (published 28 Sep 2023, corrected 15 Dec 2023, data
1970–2022; <https://assets.publishing.service.gov.uk/media/657c2396254aaa000d050e1e/ECUK_2023_Electrical_Products_tables.xlsx>).
Table A1 gives UK GWh by appliance and Table A2 gives stock, so A1/A2 is kWh per appliance. The
same series in ECUK 2020 (to 2019) agrees on the categories used here. Divided by UK households
(ONS *Families and households*: 27.0m 2015, 27.8m 2019, 28.2m 2022, and **≈26.4m for 2011, which
is interpolated** from the bulletin's "+6.1% since 2012").

**Read this caveat before any number.** The tables say they are *"independently modelled and not
compatible with DUKES"*. A "Last updated" row dates each column's inputs. **Refreshed series:**
TVs (2020), cold (2018), monitors and power supplies (2018), ovens and hobs (2017), desktops and
laptops (2013). **Projections frozen at 2010 inputs:** set-top boxes, DVD, games consoles,
printers, microwaves, kettles, tumble and washer-dryers. A frozen column's trend is a 2010
forecast, not an observation. Consumer electronics (set-top, DVD, games, PSU) is published only to
2019. For 2020–22 it is `U` (unavailable).

### Per household (or per appliance), and the ratio to each source's own year

| Series | Source year → 2019 | → 2022 | Grade |
|---|---|---|---|
| TVs, kWh/household | 140 (2011) → 57 | → **52** (×0.37) | refreshed 2020 |
| Other consumer electronics, kWh/household | 312 (2011) → 181 (×0.58) | **not published** | mostly 2010 projections |
| Computing, kWh/household | 166 (2011) → 104 | → **116** (×0.70; rises after 2019) | 2013/2018 |
| Cold, kWh/household | 471 (2015) → 387 | → **347** (×0.74) | refreshed 2018 |
| Cold, kWh/appliance | 328 (2015) → 286 | → **259** (×0.79) | refreshed 2018 |
| Electric oven, kWh/appliance | 120 (2011) | → **96** (×0.80) | refreshed 2017 |
| Electric hob, kWh/appliance | 232 (2011) | → **194** (×0.84) | refreshed 2017 |
| Microwave / kettle, kWh/appliance | 108 / 169 (2011) | → 98 / 169 | 2010 projections; no evidence |

ECUK's levels are not HES's or BRE's. ECUK cold in 2015 is 471/household, against BRE's measured
533. An ECUK oven is 120 kWh/yr, against HES's 290 per owning home. **Only the ratios are carried
across.** Each one is applied to the measured figure from that measurement's own year.

### What each 2010–15 figure the world rests on should have become by 2022

| Per-use figure | Source level | Ratio to 2022 | **≈ 2022** | World (163 gas no-PV, seed 17, C1 2022) | World − trended |
|---|---|---|---|---|---|
| Electronics on-mode (HES 2010–11) | 651–671 (AV 478 + computing 193) | AV ×0.52 (TV to 2022, other CE held at 2019), computing ×0.70 | **≈ 370–382** | mean **673**, median 628 | **≈ +290 to +300** |
| Cooking (HES Table 23 at the world's fuel shares) | 514 | oven ×0.80, hob ×0.84; kettle, microwave and toaster held (no evidence) | **≈ 460** | mean 577, median 610 | **≈ +115** |
| Cold (DECC/BRE 2015) | 533 ± 32 | ×0.74 per household (×0.79 per appliance) | **≈ 393** (420 per appliance) | mean **391**, median 289 | **≈ 0** |

**Priors graded.** Electronics −25 to −45%: observed **−43%** (with other CE held at 2019) ✓, at
the edge. Cooking 0 to −15%: **−10%** ✓. Cold −10 to −25%: **−26%** per household ✗, just
outside, and −21% per appliance ✓.

**A level, not a trend inside the window.** The electronics ratio to 2010–11 is 0.61 (2016), 0.59
(2017), 0.57 (2018), 0.56 (2019), 0.56 (2020), 0.57 (2021), 0.57 (2022). The fall is almost
entirely before 2016. **Within the world's 2016–2025, electronics moves about 7%.** That answers the
question the 2026-10-08 finding left open: the vintage correction is mainly **one level for the
decade**. It is not a steep per-year trend. Cold keeps falling inside the window, by about 4% a
year at constant stock.

### What this changes

1. **Electronics is the constant above its source, once the source is dated.** The 2026-10-08
   per-use read found no in-world constant above its own source. That holds against the 2010–11
   source. Against the same source carried to 2022, electronics is ~+300 kWh/yr on the mean. That
   is roughly the size of the 0.055 → 0.0455 arm already run (−116), times 2.5. The constant is
   0.055 kW/person, so the trended level is about **0.055 × 376/673 ≈ 0.031**. A one-variable arm
   should show a mean meter fall of about −290 ± 40 and a 19:30 profile fall of about −0.08 kWh/h,
   with the trough unmoved. **That is a prediction to file and test, not a value to land.** It
   refits a world anchor, so it must budget the value-arms re-take.
   *Tested and landed 2026-10-08: 0.031. Mean meter −294, 19:30 profile −0.060, trough unmoved,
   annual median 3,090 → 2,760, season 1.273 → 1.301. The result is in the fabric-path staging
   finding.*
2. **Cooking is ~+115 above the trended source**, of which only ~54 is the dated oven/hob ratio and
   the rest is the earlier +63. It is the second term, and smaller.
3. **Cold should not come down.** The world's mean already sits where BRE 2015 lands in 2022 on
   ECUK's trend.
4. **Sum.** About +410 kWh/yr on the mean, against a meter mean of 3,395 and median of 3,141, and
   SERL 2022's ~2,600. That is most of the gap, before any 2022 price response. SERL's 2021 gas
   no-PV annual median is still unread, so **whether the remainder is the crisis cannot yet be
   said**.
   *Read 2026-10-08 (delivery seat): SERL's aggregated tables (figshare 25472560, sheet
   `Figure_4`) give all twelve monthly medians. Summed: **2,851 (2021), 2,535 (2022, not ~2,600),
   2,452 (2023)**. The published counterfactuals (−7.1% to −9.1%, winter 2022/23) put a 2022
   without the crisis at 2,674–2,717. Over about 2,900 homes the world reads 2,985, so the crisis
   explains ~150 of the gap and **a level excess of ~+270 remains**. Cooking at its dated source is
   −61 of it. The 163-home reading was a low draw. The split and both pre-registrations are in
   `docs/staging/SEAT_FINDING_A_GAS_HOMES_ELECTRICITY_LEVEL_SPLIT_INTO_THE_CRISIS_AND_A_LEVEL_EXCESS_2026-10-08.md`.*

### Not established

- **Other consumer electronics after 2019.** ECUK stops publishing it, and its pre-2019 values are
  2010 projections. The 2022 electronics figure holds it at 2019 per household. If it kept falling
  as TVs did, the trended on-mode is lower (~330).
- **Any measured 2020s per-use figure.** No EST/DESNZ follow-up to HES R66141 at appliance level
  was found. ECUK's series are modelled. SERL publishes the meter, not the uses. The ratios above
  are the best published trend, and they are model outputs.
- **2023–2025.** ECUK 2024 and 2025 publish no per-appliance table. The world's 2023–25 has no
  per-use evidence beyond 2022's.
- **Kettle, microwave, toaster.** Their per-unit figures are 2010 projections, so no fall is
  applied.

## The hour of the evening stack: HES time of use by end use (2026-10-09, executor seat, claim `the-evening-non-cooking-stack-against-hes-time-of-use`)

**Intertek R66141 Fig 245** (p.193): *Structure of the average hourly load curve, all days, all
households, without electric heating*. This is the mean of the household curves in W, by end use.
It was read by pixel colour at 250 dpi, with the axis calibrated on the chart's own gridlines.
Summed over the day, the reading gives lighting 510 kWh/yr (Table 25: 537) and AV+ICT 742 (Tables
26 + 29: 793), so it holds to 5–7% in level. Shares of each end use's day:

| End use | Peak hour | 17:00–24:00 | 18:00–24:00 | 00:00–06:00 | h18 ÷ h12 | h21 ÷ h18 |
|---|---|---|---|---|---|---|
| Lighting | 21:00 (161 W) | 0.591 | 0.536 | 0.115 | 3.54 | 1.63 |
| AV + ICT | 20:00–21:00 (148 W) | 0.451 | 0.389 | 0.118 | 1.60 | 1.09 |
| Dishwasher (Figs 404–408, mean of five household types, by eye ±3 W) | 19:00 (68 W) | 0.431 | 0.397 | 0.107 | 1.29 | 1.18 |
| Cooking (Fig 245) | 17:00 (150 W) | — | — | — | — | — |

The whole home is flat at about 585–600 W from 17:00 to 20:00. **CAR, *Further analysis of HES:
Lighting*** (p.24–25): an always-on lighting base of 8.2 W (95% CI 5.9–10.5, 72 kWh/yr); daytime
lighting, April–September 09:00–18:00 BST, of 24 W (workdays 23.6, holidays 25.6), against an
annual 518–550 kWh (59–63 W). Morning switch-off is 1.1 h after sunrise for low users and 2.4 h for
high users (holidays).

**Dating.** These are 2010–11 hours. The decade moved the level (LEDs, flat screens), and that is
dated separately above. No source read says it moved the hour, and none publishes a 2020s time of
use per end use. Used here as the decade's hour, which is an assumption.

**What the world does with it:**
`docs/staging/SEAT_FINDING_THE_EVENING_NON_COOKING_STACK_AGAINST_HES_TIME_OF_USE_2026-10-09.md`.

## The cooking hour: HES's per-appliance load curves (2026-10-09, claim `the-evening-cooking-hour-against-hes-fig-245`)

**Intertek R66141 Figs 432–433 (oven), 440–441 (electric hob), 444–445 (microwave), 448–449
(kettle)**, pp.311–323: each appliance's daily average load curve over its owning households, for
holidays and workdays. Read by pixel colour at 250 dpi on each chart's own gridline spacing, and
weighted (5 workdays + 2 holidays) / 7. Against HES's annual table: microwave 57 kWh (56), kettle
174 (167), oven 272 (290), hob 275 (226, n = 11 homes). Only the shape is used.

| Appliance | Peak hour | Share 18:00–24:00 | Share before 16:00 |
|---|---|---|---|
| Oven | 17:00 (120 W) | 0.358 | 0.378 |
| Electric hob | 18:00 (132 W) | 0.410 | 0.388 |
| Microwave | 17:00 (16 W) | 0.328 | — |
| Kettle | 07:00 (42 W) | 0.229 | — |

HES's text says both oven and hob are "mainly used in the evening between 17:00 and 18:00". Fig
245's all-household cooking bar (17:00 ≈ 150 W) is these curves weighted by ownership. The hourly
values are in `docs/staging/records/SEAT_PREREG_THE_EVENING_COOKING_HOUR_AGAINST_HES_2026-10-09.md`.
The dating is the same as above: a 2010–11 hour, used as the decade's.

**What the world does with it:**
`docs/staging/SEAT_FINDING_THE_EVENING_COOKING_HOUR_AGAINST_HES_2026-10-09.md`.
