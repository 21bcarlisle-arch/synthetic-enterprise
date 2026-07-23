# Occupancy → Consumption Volume & Shape — Market Research (W2_13 Job 2)

**Scope note (epistemic-wall boundary):** This document covers **Job 2 only** of the
W2_13_occupancy_consumption_volume_shape DISCOVER brief — real-world UK anchoring of a
people-count / household-composition response for demand volume and half-hourly shape. It
does **not** cover Job 1 (locating the exact code seam in `simulation/premise_demand.py` /
`simulation/demand_model.py::build_demand_shape` where `occupancy_multiplier` currently
attaches). The discovery-agent role is constrained to external published sources plus
`docs/market_research/` — it does not read `simulation/**`, `company/**`, or `saas/**`, and
does not author `docs/design/` build-seam documents. Job 1 (code-seam identification) and the
combined DISCOVER-COMPLETE writeup at `docs/design/W2_13_OCCUPANCY_CONSUMPTION_VOLUME_SHAPE_DISCOVER.md`
must be produced by an agent authorized to read `simulation/**` and write `docs/design/**`,
using the findings below as its Job 2 input. No simulation code was read or touched to produce
this document.

---

## 1. Household size distribution (context — already anchored, not repeated in full)

Already in `docs/market_research/ASSUMPTIONS.md` (Household Segment & Psychology section,
2026-07-08, confidence H): ONS Census 2021 table TS017, England — 1-person 30.1%, 2-person
34.0%, 3-4-person 28.9% (3-person 16.0%, 4-person 12.9%), 5+-person 7.0%. Mean 2.37
persons/household. This is the population-share anchor a build would sample **household size**
from; it is NOT repeated as a new row below.

## 2. Volume gradient — electricity and gas consumption by number of adults (NEED)

**domain**: electricity_pricing / gas_pricing (consumption volume, not price)
**assumption_tested**: Does electricity/gas annual consumption rise with occupant count, and
is the rise sublinear (economies of scale per additional person) as the director's causal
sketch assumes?
**benchmark_value**: DESNZ NEED "Consumption_additional_EW_2023.xlsx", Table A13 (gas) and
Table A14 (electricity), "by number of adults", England & Wales, **2023 gas/electricity year**
(gas year mid-May 2023–mid-May 2024; electricity year Feb 2023–Jan 2024), median kWh/year:

| Number of adults | Gas median (kWh/yr) | Δ vs prior band | Electricity median (kWh/yr) | Δ vs prior band |
|---|---|---|---|---|
| 1 | 8,546 | — | 1,993 | — |
| 2 | 10,624 | +24.3% | 2,867 | +43.8% |
| 3 | 11,576 | +9.0% | 3,318 | +15.7% |
| 4 | 12,734 | +10.0% | 3,772 | +13.6% |
| 5 or more | 14,486 | +13.8% (vs 4) | 4,129 | +9.5% (vs 4) |
| Unknown adults | 8,024 | n/a | 1,850 | n/a |

Sample sizes are large (England & Wales gas-metered population ~18.7m dwellings in the 2023
row; the "number of adults" split is Experian-modelled data merged onto the NEED gas/electricity
meter-point panel, per NEED's own Note 2 methodology). Same table structure exists back to
2005 with the same monotonic-but-sublinear shape every year (2005 row: 1 adult £15,200
median gas vs 2 adults £18,200 = +19.7%, vs 5+ adults £22,400 = a cumulative +47% over the
1-adult base) — the sublinearity is not a one-year artefact.
**confidence**: H — primary DESNZ NEED accredited-official-statistics table, parsed directly
from the published `.xlsx` (not a secondary citation), current 2023 vintage, England & Wales
coverage matches the SIM's stated domestic population.
**source**: DESNZ "National Energy Efficiency Data-Framework (NEED): Summary of Analysis,
Great Britain, 2025" (26 June 2025), supporting data table `Consumption_additional_EW_2023.xlsx`,
Table_A13 and Table_A14, gov.uk/government/statistics/national-energy-efficiency-data-framework-need-consumption-data-tables-2025,
fetched and parsed directly (zipfile/XML, not a rendered view) 2026-07-23.
**date**: 2026-07-23
**finding**: Both fuels show a clear, real, sublinear volume response to occupant count —
electricity rises fastest on the 1→2-adult transition (+43.8%, consistent with a large shared
fixed base load — lighting, fridge/freezer, standby, cooking appliances — that a second adult
adds relatively little marginal draw to) and flattens sharply thereafter (+15.7%, +13.6%,
+9.5% for each successive adult). Gas shows the same qualitative shape but a smaller 1→2
jump (+24.3%) and steadier ~10-14% increments thereafter, consistent with space heating being
driven more by dwelling size/insulation (already covered elsewhere in this repo's household
physical-attribute rows) than occupant count, while hot water and cooking gas scale more
directly with people. **This is the strongest single anchor for the atom's volume-response
build** — a people-count multiplier curve should follow this real per-adult decay shape, not a
flat linear per-person scalar. **ANCHORED.**

## 3. A genuine gap in the NEED table: adults only, not total occupants or children

**domain**: other
**assumption_tested**: Can the NEED "number of adults" gradient above be used directly as a
proxy for total household size (adults + children), as the director's causal sketch implies
("people count, adults vs children where anchorable")?
**benchmark_value**: No — NEED Table A13/A14's "number of adults" variable is explicitly
adults-only (Experian-modelled), and NEED's separate "household size" banding (referenced in
`Consumption_multiple_attributes_EW_2023.xlsx` metadata and cross-checked against EFUS
methodology notes below) is a distinct field not cross-tabulated against number of adults in
the tables fetched this session. No NEED table decomposing consumption by (adults, children)
jointly was located this session.
**confidence**: M — confirmed by directly reading the fetched table's own column header
("Number of adults") and its footnote ("Number of adults is modelled data purchased from
Experian" — quoted from the parent NEED 2025 PDF page 8, footnote 3), not inferred.
**source**: Same NEED 2025 report and `Consumption_additional_EW_2023.xlsx` as §2, footnote 3
of the PDF (`need-report-june-2025.pdf`, page 8), fetched 2026-07-23.
**date**: 2026-07-23
**finding**: A build that wants a genuinely separate ADULTS vs CHILDREN volume weighting
cannot lift it directly from this table — the adults gradient above is the closest available
real anchor for total-occupant-count effects but conflates "more adults" with "more people"
generically. **R10-DISTRIBUTION-CANDIDATE**: if the build wants a distinct children-specific
volume increment (as opposed to reusing the adults curve as a general people-count curve),
that specific magnitude is an unanchored soft import and must be sampled from a distribution,
never a point estimate, with the gap stated in the build's own docstring.

## 4. Shape drivers — hours-at-home by household composition (EFUS 2017, heating & occupancy report)

**domain**: electricity_pricing (half-hourly shape, not price)
**assumption_tested**: Does household composition (size, presence of children, pensioner
status, employment) shift *when* people are home, and therefore when load is drawn — the
director's "hours-at-home" candidate shape driver?
**benchmark_value**: DESNZ/BRE "Energy Follow-Up Survey (EFUS): Heating patterns and
occupancy" report, based on EFUS 2017 survey wave, Interview 3 fieldwork winter 2018/19,
n=1,167–1,179 GB households depending on question:
- **Weekday daytime (9am–5pm) occupancy**: 43% of all households have someone home all
  day; 18% have no-one home; 39% variable.
- **By household size (weekday daytime, "someone in all day")**: 5-or-more-person households
  67% vs single-person households 37% — a ~30 percentage-point gap, directly household-size
  driven.
- **By pensioner presence**: households with someone over State Pension age 63% "in all day"
  vs households without 34%.
- **By employment status**: all-adults-unemployed households 60% "in all day" vs
  someone-employed households 35%.
- **Weekend (Sat/Sun) daytime occupancy**: 60% "in all day" (vs 43% weekday); the household-size
  gap narrows sharply at the weekend — single-person households 48% "in all day" vs 62-72%
  for all other household sizes (still a real gap, but much smaller than the weekday 30pp gap).
- **Evening (5pm–midnight) occupancy**: 88% of households have someone home on a weekday
  evening (vs 50-52% for morning/afternoon) — evening is a near-universal at-home period
  regardless of composition, consistent with Elexon Profile Class 1's well-established
  evening-peak shape already used in `sim/profile_class_1.py`.
- **Overnight occupancy**: 94% of households have someone home overnight on both weekdays
  and weekends — near-universal, again consistent with the existing PC1 overnight-baseload
  shape.
**confidence**: H — primary DESNZ/BRE accredited survey report, quoted directly from the PDF
text and figures, GB-representative sample, methodology section explicitly defines
"household size" and "children present" (≤16 years old) as derived survey variables.
**source**: DESNZ "Energy Follow-Up Survey: Heating patterns and occupancy" (EFUS 2017 report
series), gov.uk/government/publications/energy-follow-up-survey-efus-2017-reports,
`efus-heating-patterns-occupancy.pdf`, §4.1–4.2, fetched and text-extracted 2026-07-23.
**date**: 2026-07-23
**finding**: This is a real, quantified, GB-representative anchor for the "hours-at-home"
shape driver the director's causal sketch names — and it is composition-specific (household
size, pensioner presence, employment status all independently move the daytime-occupancy
rate by 25-30 percentage points). **The morning/afternoon (daytime) window is where
composition genuinely changes the shape** (43% vs 67% vs 34% "in all day" by different
composition cuts); evening and overnight are near-universally occupied (88-94%) regardless of
composition, so a build should concentrate the composition-driven shape adjustment on the
09:00-17:00 window specifically, not apply a uniform multiplier across all 48 half-hourly
periods. **ANCHORED** for the daytime-occupancy-rate direction and magnitude; converting an
"occupancy rate" (probability someone is home) into a specific kWh half-hourly shape
adjustment is a build-time modelling choice, not itself a further-anchored number —
**R10-DISTRIBUTION-CANDIDATE** for the exact shape-weight magnitude applied per half-hour,
even though the occupancy-rate inputs feeding it are H-confidence.

## 5. Per-person consumption intensity falls with household size — corroborating evidence (EFUS water-use)

**domain**: other (corroborating, not itself a SIM parameter)
**assumption_tested**: Cross-check for the same "economies of scale per additional person"
direction found in the NEED volume gradient (§2), using an independent EFUS behavioural
measure (baths/showers per person per day) as a sanity check, not a new SIM input.
**benchmark_value**: EFUS heating-and-occupancy report §5.2.2: households taking
less-than-one shower/bath per person per day: three-or-more-person households 60-80% vs
two-person households 44% vs single-person households 26% — i.e. per-person water-use
intensity falls as household size rises, the same direction and rough proportionality as the
NEED per-adult electricity/gas gradient in §2. Households with dependent children present are
also more likely to under-1x-per-day per person (71% vs 38% without children present) —
suggesting a genuine children-present dampening effect on PER-PERSON intensity (not
necessarily on total household volume, which still rises with headcount per §2's "number of
adults" data — children aren't counted as "adults" in that table, so this doesn't resolve §3's
gap directly, but it is corroborating directional evidence that a naive "children count exactly
like adults" volume assumption would overstate the per-child increment).
**confidence**: M — same primary EFUS source as §4, but this is water-heating behaviour
(itself only a partial proxy for electricity/gas demand, since water heating fuel varies by
household — gas combi vs electric immersion/shower), used here as directional corroboration
only, not a standalone volume-gradient anchor.
**source**: Same EFUS heating-and-occupancy report as §4, §5.2.1–5.2.2, fetched 2026-07-23.
**date**: 2026-07-23
**finding**: Corroborates §2's sublinearity direction from an independent behavioural angle,
and separately corroborates §3's flagged gap that children's marginal per-person contribution
is measurably different (lower per-person, not necessarily lower in aggregate) from an
additional adult's. **Context only — not a standalone SIM parameter.**

## 6. Cooking fuel and overnight device load — explicitly NOT found this session

**domain**: other
**assumption_tested**: Can "cooking fuel" (gas vs electric hob/oven split by household
composition) and "overnight device load" (composition-driven baseline/standby draw) be
anchored to a published UK source, per the director's causal sketch?
**benchmark_value**: NOT FOUND this session for either sub-claim specifically cross-tabulated
by household composition. What partial context exists: EHS/DESNZ heating-system fuel-type
splits are anchored elsewhere in `ASSUMPTIONS.md` (gas boiler ~86% of homes) but that is
*heating* fuel, not *cooking* fuel, and is not composition-cross-tabulated. The EFUS
light-appliances report (`efus-light-appliances-smart-tech.pdf`, listed alongside the heating
report on the same gov.uk publication page, NOT fetched this session — genuine unexplored
lead, not a checked-and-empty result) is the most likely candidate source for an
appliance-ownership/overnight-standby-load composition breakdown and should be the first stop
for a future session closing this specific gap.
**confidence**: n/a (explicit non-finding)
**source**: Searched EFUS heating-and-occupancy report text (no cooking-fuel or
appliance-standby content found); `efus-light-appliances-smart-tech.pdf` identified as an
unexplored candidate at gov.uk/government/publications/energy-follow-up-survey-efus-2017-reports,
not fetched this session.
**date**: 2026-07-23
**finding**: Genuine gap, not invented. **R10-DISTRIBUTION-CANDIDATE**, and additionally
flagged as an open follow-up lead (the specific unfetched PDF) rather than a dead end — a
future discovery-agent pass on this same atom should fetch
`efus-light-appliances-smart-tech.pdf` before treating cooking-fuel/overnight-load as
permanently unanchorable.

---

## Summary for the Job-1-owning agent (code-seam + build)

The real-world response to wire, in order of anchoring strength:

1. **Volume**: per-adult sublinear multiplier — electricity +43.8%/+15.7%/+13.6%/+9.5% for
   the 2nd/3rd/4th/5th+ adult respectively vs the 1-adult median (2,867/3,318/3,772/4,129 kWh
   vs 1,993 kWh base); gas +24.3%/+9.0%/+10.0%/+13.8% (10,624/11,576/12,734/14,486 vs 8,546
   kWh base). Both H-confidence, DESNZ NEED 2023.
2. **Shape (daytime window only)**: composition-driven daytime (9am-5pm) occupancy-rate
   shift — household size, pensioner presence, and employment status each independently move
   the "someone home all day" rate by 25-30 percentage points (37% single-person vs 67%
   5+-person; 34% no-pensioner vs 63% pensioner-present; 35% employed vs 60%
   all-unemployed). Evening/overnight windows are near-universally occupied (88-94%)
   regardless of composition and should NOT be composition-adjusted. H-confidence for the
   occupancy-rate inputs; R10 for the exact kWh-shape-weight conversion.
3. **Children vs adults decomposition**: NEED's own table is adults-only; no NEED table
   splits adults vs children jointly. EFUS water-use data corroborates a children-present
   dampening effect on per-person (not necessarily per-household) intensity. R10-CANDIDATE —
   do not assume a child contributes the same marginal volume as an adult; sample it, flag it.
4. **Cooking fuel and overnight device load**: genuinely unanchored this session.
   R10-CANDIDATE, with a named unfetched follow-up source (`efus-light-appliances-smart-tech.pdf`).

**couples_with W1_5_premise_demand_shape**: these findings are Job-2 input only — the actual
fold-not-fork attachment point into `build_demand_shape`'s existing `occupancy_multiplier`
scalar is Job 1's responsibility (code-authorized agent), not determined here.
