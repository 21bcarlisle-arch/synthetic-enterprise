# What a cooking appliance uses in a year: HES 2012 per-appliance figures

**Knowledge:** none -- this is the per-appliance cooking energy read the seasonal-swing finding names as its next step. It anchors a SIM fidelity build, and no knowledge page covers household appliance energy yet.

## Sources

- Household Electricity Survey (Intertek Report R66141, Final Report Issue 4), DEFRA/DECC/EST,
  dated May 2012. https://assets.publishing.service.gov.uk/media/5a7c2fd940f0b67d0b11f6df/10043_R66141HouseholdElectricitySurveyFinalReportissue4.pdf
  (cached `/tmp/hes.pdf`, title-page confirms "Intertek Report R66141"; read via `pdftotext -layout`).
  Date read: 2026-10-08.
- EFUS 2011 Report 9: "Domestic appliances, cooking & cooling equipment", BRE for DECC, Dec 2013,
  BRE report 288143 (cached `/tmp/efus9.txt`). Date read: 2026-10-08.
- Checked and found no cooking content in: EFUS 2017 "Heating patterns and occupancy" (BEIS 2021,
  `/tmp/efus17.pdf`) and English Housing Survey Energy Report 2017-18 (`/tmp/ehs1718.txt`).

## 1. Per-appliance annual kWh per owning household (HES, Table 14 p.244 = Table 23 "All households" row, p.326-327)

| Appliance | Mean kWh/year | n monitored (Table 15, p.245) |
|---|---|---|
| Oven | 290 | 53 |
| Cooker (electric cook top) | 317 | 158 |
| Electric hob | 226 | 11 per Table 15; chapter 11.7 text (p.317) says "only ten hobs" — unreconciled |
| Microwave oven | 56 | 219 |
| Electric kettle | 167 | 243 |
| Toaster | 21.9 | 68 per Table 15; Appendix VI toaster page (p.482) says 65 — unreconciled |

No median is published for any cooking appliance; charts and tables give only the mean ("Average").

**Cooking total per household** (oven+cooker+hob+microwave+kettle+fryer+toaster summed, ch.11.1
p.300): all-household average **460 kWh/year**, range **429-505 kWh/year** across five household
types (ch.11.2 p.301): single pensioner 429, single non-pensioner 505, multiple pensioner 452,
household with children 422, multiple person/no dependent children 497 (Figs 414-418, pp.301-303).

**Table 23 (p.326-327), kWh/year by household type:**

| Household type | Oven | Cooker | Hob | Microwave | Kettle |
|---|---|---|---|---|---|
| Single pensioner (65+) | 267 | 300 | 177 | 44 | 141 |
| Single non-pensioner | 375 | 344 | n/a | 66 | 153 |
| Multiple pensioner | 211 | 326 | 148 | 51 | 185 |
| Household with children | 183 | 313 | 259 | 57 | 167 |
| Multiple person, no dependent children | 396 | 309 | 243 | 59 | 178 |
| All households | 290 | 317 | 226 | 56 | 167 |

The report warns (p.326) some household-type x appliance cells have very few households; it gives
no cell-level n, only the appliance-level n in Table 15.

**No gas-vs-electric cooking split is published for these kWh figures.** Chapter 11.6 (p.313) says
cookers "known to have a gas cook top are not analysed in this chapter" — the oven/cooker/hob
figures are for the electric-cooking subsample, but no parallel figure or count is given for the
excluded gas-cooking households.

**Other cooking appliances (Table 24 p.327 / Appendix VI pp.470-483), mean kWh/year (n):**
Fryer 52.0 (4), food steamer 52.7 (2), coffee machine 31.8 (12), bottle warmer 27.2 (1), bread maker
23.6 (12), toaster 21.9 (65), grill 12.8 (5), extractor hood 11.7 (39), yoghurt maker 8.0 (1), food
mixer 0.5 (4). Appendix VI's own index (p.471) lists "Hob" among the small appliances to profile,
but no Hob entry actually appears between Grill and Toaster — the only hob figures in the report
are from chapter 11.7, not Appendix VI.

## 2. Per-use energy and uses per day/week

No mean kWh-per-use is published for any cooking appliance. The only per-use data is a
distribution for the kettle (ch.11.9.1, p.325-326), not a mean: "98% of cycles consume fewer than
0.2 kWh and 65% fewer than 0.1 kWh" (Fig 450); for max power per cycle, "1% of the cycles have a
maximum power greater than 3 kW, 40% greater than 2 kW and 80% greater than 1 kW" (Fig 451).
Not published: any kWh/cycle mean, or uses-per-day/week, for oven, hob, kettle, microwave or
toaster (contrast the dishwasher, which gets an explicit cycles/year figure in Tables 21-22 that
cooking appliances do not).

## 3. Cooking contribution to the evening peak (W, ~18:00-19:00)

Not published as a number. Ch.11.4 (p.304) states only that the combined cooking load's "main peak
for both types of day was found in the evening between 17:00 and 19:00"; ch.11.5/11.7 (pp.311, 317)
say the oven and hob are "mainly used in the evening between 17:00 and 18:00." These are
qualitative statements attached to load-curve charts (Figs 420-429 cooking total, 432-433 oven,
440-441 hob) with no printed numeric labels at specific hours. I have not read a wattage off a
chart image, since that would be estimation.

## 4. Sample size

**251 households in England**; 1 gave insufficient data, leaving **250** usable (pp.1136, 2028,
3553). Of the 251, **26 were monitored for a full calendar year**; the rest for **one month only**
(p.1161; repeated p.300, ch.11.1). The 26 one-year households produced the seasonal correction
curve (Fig 413) used to annualise the one-month households' cooking consumption. Per-appliance
monitored counts (not household counts) are in Table 15 (p.245), given in section 1 above.

## 5. EFUS/EHS: gas cooking conditional on gas central heating

**NOT FOUND.** EFUS 2011 Report 9 gives only unconditional national figures: Table 13 (p.15) —
95.4% of households own an oven, 93.3% a hob (n=2,503/2,448); Table 15 (p.17) — of households
with an oven, 68.7% electric vs 29.3% gas; of households with a hob, 37.9% electric vs 61.2% gas.
No table in that report cross-tabulates cooking fuel against heating fuel. EFUS 2017 "Heating
patterns and occupancy" (searched for "electric oven/hob", "gas hob/cooker", "cooking fuel" — zero
matches) covers heating only, not appliances. EHS Energy Report 2017-18 (same search terms, zero
matches) covers EPCs, tariffs and gas-grid access, not cooking fuel. I did not locate, and have not
inferred, a published share of gas-centrally-heated English homes cooking with electricity.

## What is not established

- Per-use (per oven-use, per kettle-boil) mean kWh; uses-per-day/week — for any appliance.
- A numeric evening-peak wattage for cooking, oven or hob — only qualitative time windows.
- Gas-cooking-household kWh or appliance counts (chapter 11 excludes them, never quantifies them).
- Cell-level n for Table 23's household-type x appliance breakdown.
- A published cross-tab of cooking fuel conditional on heating fuel, in any of the three sources
  checked.
- Two small internal HES inconsistencies, unresolved in the source itself: hob n = 10 vs 11;
  toaster n = 65 vs 68.

## Against the world (seat, 2026-10-08)

The catalogue in `simulation/premise_trace.py` implies, per owning home at unit intensity, oven
~301, hob ~161 and kettle ~204 kWh/yr (seasonal-swing finding, 2026-10-08). Against HES: the oven is
on it (290), the hob is BELOW it (226, n=11), and the kettle is 22% ABOVE it (167, n=243). Per-use
energy therefore cannot be most of the world's remaining 0.21 kWh/h evening excess. The kettle is
the only clear overstatement, and the hob reads the other way.

The lead this opens is **timing, not level**. HES places oven and hob use mainly at 17:00–18:00, and
all cooking at 17:00–19:00. The world's cooking windows start at half-hours 32–42 and 33–43, shifted
by each home's routine. Its peak is at 20:00, against SERL's 18:30. A peak that is too late and too
tall is what a too-narrow, too-late start window produces: every home's evening meal lands in the
same few half-hours. That is a hypothesis, and nothing here measures it.
