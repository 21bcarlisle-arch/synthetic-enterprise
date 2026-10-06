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
  heating*. Their total is 4,878 kWh/yr, against 3,638 kWh/yr for homes without electric heating
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
