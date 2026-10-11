# How much a same household's use moves year on year, and how much it moved in 2022

**Knowledge:** metering-and-reads

**Asked by** the discovery task following
`how_far_a_settled_eac_sits_from_next_years_use.md`, which measured NEED 2026 consecutive-year
domestic electricity change (median \|r−1\| 14.7%, 2021→2022 median ratio r=0.923) and named four
things bundled inside that spread: real household change (weather, occupancy, appliances,
behaviour), change of occupier, EAC↔AA transitions, and 100 kWh rounding. The world simulation
needs only the **real household change** component, net of occupier turnover and estimation
artefacts — weather it already has; household change and the 2022 price response it lacks. This
document looks for published evidence that sizes those two pieces directly, from sources that
compare **the same household/meter across years**, not the dwelling-level industry figure NEED
gives.

Two questions, kept separate throughout:
1. Year-on-year variation in a *same household's* actual metered annual consumption, in an
   ordinary (non-crisis) year, weather-corrected where possible.
2. The 2022 price-crisis demand response: how much the same households cut gas and electricity
   use, weather-corrected, and how heterogeneous that cut was.

---

## 1. Year-on-year variation in the same household, ordinary years

**No GB study publishes a same-household, weather-corrected, non-crisis-year distribution of
year-on-year change with percentiles (median \|change\|, p90), analogous to the NEED table in the
source document.** That is a **GAP**. The closest published evidence is assembled below, and none
of it is a clean substitute.

### Closest available: SERL same-household counterfactual, "year 2" of the COVID study

> "Our analysis showed that median annual observed energy consumption... [year 1 of the pandemic,
> April 2020–March 2021] compared to counterfactual... electricity consumption increased by 7.8%;
> gas by 5.7% in year 1... [year 2, April 2021–March 2022]... (2.2%; 0.2%)."

— Zapata-Webborn, E. et al. (2023), *The impact of COVID-19 on household energy consumption in
England and Wales from April 2020 to March 2022*, Energy and Buildings 297, 113428. Method:
XGBoost/neural-net/elastic-net counterfactual models trained on each of 508 (electricity) and 326
(gas) households' own pre-pandemic (to Feb 2020) data, predicting what that **same household**
would have used given the weather that actually occurred; "reduction" is observed minus
counterfactual. Table 4 (quoted figures above).

**What this licenses.** Year 2 of that study (April 2021–March 2022) had no national lockdown and
only the Jan–Mar 2021 restrictions fell in year 1, so it is the nearest published approximation to
an "ordinary" weather-corrected year for a matched GB household panel: **median change at the
whole-sample level was +2.2% electricity, +0.2% gas** against a household's own weather-corrected
counterfactual. That is far smaller than NEED's bundled 14.7% median \|change\|, which is exactly
what is expected: the NEED figure also carries occupier turnover, EAC↔AA transitions and
rounding, none of which apply here (SERL households keep their own smart-meter history).

**What it does not license.**
- It is a **sample median of household-level means**, not a distribution of individual household
  changes. Fig. 4 of the paper plots **monthly** median and IQR of the *sample*, not an annual
  per-household IQR; the paper does not report an annual p10/p90 or median-of-\|change\| across
  households as a single number. Reading percentile spread off the chart would be inventing a
  number from a picture — **not done here**.
- 2021/22 still carries pandemic residue (the paper itself notes "some households continued to
  use up to around 1 kWh of electricity per day or 15–20% more than predicted throughout
  2021/22, others decreased by similar levels" — so *individual* households were still swinging by
  that much; only the sample median was small).
- N is modest (508 electricity, 326 gas households), self-selected SERL volunteers.

### Cross-check, not GB: occupant-vs-building variance decomposition

> "For the studied databases, the results indicate that approximately 50% of the variance in
> heating consumption between houses can be explained by differences related to occupants. The
> other 50% can be explained by the characteristics of the building itself..."

— Van den Brom, P., Hansen, A.R., Gram-Hanssen, K., Meijer, A., Visscher, H. (2019),
*Variances in residential heating consumption – Importance of building characteristics and
occupants analysed by movers and stayers*, Applied Energy 250, pp.713–728.
https://doi.org/10.1016/j.apenergy.2019.05.078. Netherlands and Denmark, district heating and gas,
social and private housing.

**Confidence L for GB purposes** — not a GB study, not GB fuel/climate/tariff context, and it
decomposes cross-sectional variance (between dwellings) rather than measuring one household's
year-on-year swing. It is included only because its "movers vs stayers" design is precisely the
split NEED cannot make, and it shows that **occupant-attributable variance is roughly comparable
in size to building-attributable variance** — a sanity check that "real household change" is not a
small residual next to the fabric, but genuinely about half the story in at least one European
heating-consumption dataset. It does not transfer a number to GB electricity/gas.

### What else was checked and found silent
- The DESNZ NEED 2026 headline report and its Annex C (comparisons with other sources) discuss
  only cross-sectional stock medians (all dwellings each year, not a matched panel) and state nothing
  about a same-household distribution.
- No SERL, DESNZ or Ofgem publication found gives a same-household weather-corrected
  year-on-year change distribution for a year with no price shock and no pandemic restriction.

---

## 2. The 2022 price-crisis demand response

This is well published, from three independent sources that converge.

### A. Same-household panel, weather-corrected, winter 2022/23 vs winter 2021/22 (SERL)

> "Electricity consumption was 8.4% lower and gas consumption 10.8% lower than the previous
> winter (accounting for weather), saving consumers around £29/month."

— Zapata-Webborn, E. et al. (2024), *Winter demand falls as fuel bills rise: Understanding the
energy impacts of the cost-of-living crisis on British households*, Energy and Buildings 305,
113869. N = 5,594 GB households with both electricity and gas smart-meter data, Oct 2022–Mar 2023
vs a per-household XGBoost counterfactual trained on Oct 2021–Mar 2022 (same households, weather
held in the model).

| fuel | median reduction (% of weather-corrected counterfactual) | IQR | mean | sd |
|---|---:|---:|---:|---:|
| electricity | **8.38%** | (−0.48%, 17.56%) | 7.08% | 24.24 |
| gas | **10.78%** | (1.19%, 22.44%) | 11.74% | 24.86 |

(Table 2, "Reduction (% of prediction)". Negative values = consumption *rose* versus the
counterfactual; Fig. 1 histograms show a long tail of households whose consumption fell by more
than 50%, and a visible minority whose consumption rose, by up to roughly 50%.)

Price elasticities, same households, same paper: **median short-run electricity price elasticity
−0.099 (IQR −0.223, 0.016); gas −0.071 (IQR −0.144, −0.010)** — split further by self-reported
financial wellbeing in Fig. 3 (poorer households more elastic on gas, wealthier households more
elastic on electricity). Quintile 5 (top 20% reducers, ≥23.8% total reduction) cut their mean
thermostat setting by 1.8°C versus 0.9°C for the rest of the sample, and were 2.3× more likely to
report being unable to keep comfortably warm (Table D1, Fig. 6, Table D2).

**Confidence H.** This is the only peer-reviewed, same-household, weather-corrected, GB-wide
estimate of the 2022/23 demand response found, with a reported distribution (not just a mean).

### B. National aggregate, weather ("temperature") corrected, calendar year 2021 vs 2022 (DESNZ)

DESNZ, *Energy Consumption in the UK 2025*, Table C9 ("Domestic; average consumption
(2008–2024)"), `ECUK_2025_Consumption_tables.xlsx`, downloaded from
https://www.gov.uk/government/statistics/energy-consumption-in-the-uk-2025 (2025-09-25, data
updated to 2026-04-20). Temperature-corrected average consumption per household/customer:

| fuel | 2021 (kWh) | 2022 (kWh) | % change, temperature-corrected | % change, unadjusted |
|---|---:|---:|---:|---:|
| electricity | 3,789 | 3,466 | **−8.5%** | −10.3% |
| gas | 12,793 | 11,314 | **−11.6%** | −19.2% |

**This is annual (not winter-only), whole-stock (not same households matched), UK-wide, and
weather-corrected using DESNZ's own methodology** (distinct from SERL's XGBoost counterfactual).
Per the NEED Annex C footnote, DESNZ's own published comparisons actually use the *unadjusted*
electricity figure and the *temperature-corrected* gas figure as the standard cross-source
comparator, because electricity's weather sensitivity is small and the correction method differs
between publications — treat the electricity temperature-corrected column with more caution than
the gas one.

**Confidence H for the direction and rough size; note the population is different.** The striking
thing is how close this **national, unmatched, whole-stock** figure sits to the SERL **matched,
same-household** figure above: electricity −8.5% (DESNZ) vs −8.4% (SERL, median); gas −11.6%
(DESNZ) vs −10.8% (SERL, median). Two independent methods and populations landing within ~1
percentage point of each other is a reasonably strong cross-check that the *median* household
response was genuinely in the region of "electricity down ~8–9%, gas down ~11–12%" net of weather
— even though neither number alone separates occupier turnover from behavioural response (DESNZ's
is a stock average across a changing population; SERL's is a matched panel, which is the cleaner
of the two for that purpose).

### C. NEED cross-sectional stock median (already measured in the source document, repeated here only as the third leg)

From `how_far_a_settled_eac_sits_from_next_years_use.md` and the NEED 2026 headline report
(`NEED-report-june-2026.pdf`, p.1): **"record (since 2005) year on year falls in median gas and
electricity consumption between 2021 and 2022"**; cumulative England & Wales fall 2021→2024 was
**13% for gas, 9% for electricity**, "across all property, household and area characteristics."
This is dwelling-level (not household-level — NEED follows the meter/address, so it still bundles
occupier turnover and EAC↔AA noise) and is consistent in direction and rough size with A and B,
but should not be read as a fourth independent confirmation of the *same-household* size — it is
the same kind of figure the source document already flagged as bundled.

### Secondary citations found inside source A, not independently verified here
Zapata-Webborn et al. (2024) cite, without the primary documents having been read in this task:
- OBR, March 2023: "weather-adjusted household gas demand in winter 2022/23 was around 15% lower
  than before Russia's invasion" (national aggregate, not same-household).
- K. Harris, DESNZ *Energy Trends Quarterly*, January 2023: Q1 2023 temperature-adjusted domestic
  energy consumption down 9.5% overall vs Q1 2022 (11% reduction in industrial consumption) —
  national aggregate.
- Both are **named for the next reader, not read here** (confidence not assigned).

---

## What this licenses and does not license, for the world model

**Licenses:**
- A world term for **the 2022 price-crisis household response** can be anchored to a
  weather-corrected, same-household median of roughly **−8% electricity, −11% gas**, with real
  heterogeneity around it: the SERL IQR (electricity −0.5%→+18%, gas +1%→+22% reduction) is the
  best published distribution and should be the calibration target, not the median alone — a
  flat −8%/−11% shift for every household would under-state the spread the data actually shows
  (some households barely moved or used more; the top quintile cut over 24%).
- A price elasticity, if the world wants one directly rather than a reduction target: median
  short-run electricity ≈ −0.10, gas ≈ −0.07 (SERL), both smaller in magnitude than typical
  literature estimates the same paper cites (−0.10 to −0.28 gas, Pellini's −0.607 long-run
  electricity), so these are short-run, crisis-specific, and should not be read as the world's
  general-purpose elasticity.
- Convergence between the matched-panel (SERL) and whole-stock (DESNZ) figures is evidence the
  *median* size is reasonably well established; it does not establish the *shape* of the
  cross-household distribution beyond what SERL's IQR gives for a 5,594-household sample.

**Does not license:**
- No number here should be used for the "real household change in an ordinary year" term except
  as a loose upper bound: SERL's year-2 COVID figures (+2.2% electricity, +0.2% gas, sample
  median, not weather-and-pandemic-clean) are the only same-household weather-corrected,
  non-crisis-adjacent number found, and they are not a distribution, not a clean "ordinary" year
  (pandemic residue), and from a self-selected sample two orders of magnitude smaller than NEED's
  330,884 pairs. **This remains a GAP** — filed, not filled.
- The Van den Brom et al. (2019) 50/50 occupant/building variance split is Dutch/Danish
  district-heating and gas data, cross-sectional, and must not be used as a GB number; it is
  context only, for the practitioner question of whether "occupant effects are a rounding error
  next to the building" (they are not, in that dataset).
- None of the figures here separate the price response from simultaneous weather in a year that
  was *also* unusually mild: 2022 was a warmer-than-average year in parts of GB. DESNZ's
  "temperature corrected" column and SERL's weather-matched counterfactual both claim to net this
  out, by different methods, which is part of why their convergence is informative — but neither
  source in this document independently re-derives GB 2022 weather anomalies, so "weather net of
  response" here relies on DESNZ's and SERL/UCL's own correction methodology, not a re-check of
  the weather data itself.
- The DESNZ Table C9 figures are UK-wide household/customer *averages*, driven by the full
  population (including house-building, deaths, and household formation/dissolution over the
  year) — they are not adjusted for stock turnover the way a matched panel is, and should be read
  as a population-average cross-check, not a per-household figure.

---

## Sources

- Zapata-Webborn, E., Hanmer, C., Oreszczyn, T., Huebner, G., McKenna, E., Few, J., Elam, S.,
  Pullinger, M., Cheshire, C., Friel, D., Masters, H., Whittaker, A. (2024), *Winter demand falls
  as fuel bills rise: Understanding the energy impacts of the cost-of-living crisis on British
  households*, Energy and Buildings 305, 113869.
  https://doi.org/10.1016/j.enbuild.2023.113869. PDF read:
  https://discovery.ucl.ac.uk/10185918/1/1-s2.0-S037877882301099X-main.pdf (retrieved 2026-10-11).
- Zapata-Webborn, E., McKenna, E., Pullinger, M., Cheshire, C., Masters, H., Whittaker, A., Few,
  J., Elam, S., Oreszczyn, T. (2023), *The impact of COVID-19 on household energy consumption in
  England and Wales from April 2020 to March 2022*, Energy and Buildings 297, 113428.
  https://doi.org/10.1016/j.enbuild.2023.113428. PDF read:
  https://discovery.ucl.ac.uk/id/eprint/10175342/1/1-s2.0-S0378778823006588-main.pdf (retrieved
  2026-10-11).
- DESNZ, *Energy Consumption in the UK (ECUK) 2025*, Consumption tables, Table C9
  (`ECUK_2025_Consumption_tables.xlsx`):
  https://assets.publishing.service.gov.uk/media/6925cb9047904590c9da2d21/ECUK_2025_Consumption_tables.xlsx,
  landing page https://www.gov.uk/government/statistics/energy-consumption-in-the-uk-2025
  (published 2025-09-25, data updated 2026-04-20; retrieved 2026-10-11).
- DESNZ, *Energy Consumption in the UK 2025* narrative PDF:
  https://assets.publishing.service.gov.uk/media/68d28e91275fc9339a248b98/Energy_Consumption_in_the_UK_2025.pdf
  (retrieved 2026-10-11) — domestic energy intensity commentary, p.11.
- DESNZ, *National Energy Efficiency Data-Framework (NEED): Summary of Analysis, Great Britain,
  2026* (11 June 2026):
  https://assets.publishing.service.gov.uk/media/6a2925376d178a6fb7e31fe8/NEED-report-june-2026.pdf
  (retrieved 2026-10-11), and Annex C, *Comparisons with other Sources*:
  https://assets.publishing.service.gov.uk/media/6a2823256d178a6fb7e31f9a/annex-c-comparisons-with-other-sources-2026.pdf
  (retrieved 2026-10-11).
- Van den Brom, P., Hansen, A.R., Gram-Hanssen, K., Meijer, A., Visscher, H. (2019), *Variances
  in residential heating consumption – Importance of building characteristics and occupants
  analysed by movers and stayers*, Applied Energy 250, 713–728.
  https://doi.org/10.1016/j.apenergy.2019.05.078. Abstract read via OpenAlex; full text not
  fetched (non-GB, cited for context only).
- Not read, named for the next reader: OBR March 2023 Economic and Fiscal Outlook (weather-adjusted
  gas demand estimate); DESNZ, *Energy Trends Quarterly*, January 2023 (K. Harris) — both cited
  secondhand inside Zapata-Webborn et al. (2024)'s introduction.
- Companion document, read first and not re-derived here:
  `docs/market_research/how_far_a_settled_eac_sits_from_next_years_use.md`.
