# The domestic gas year: about 85% of it follows heating degree days, not 70%

**Knowledge:** what-a-house-does-to-its-energy

*K8 page for `W2_30_gas_heating_fraction_calibration_target_knowledge_page` (autonomous worker, 2026-11-19). It is
written before any change to the world's gas shape. It answers the GAP in
`docs/staging/SEAT_FINDING_W2_30_THE_GAS_WINTER_OVER_SHARE_IS_THE_WORLDS_70_30_FALLBACK_NOT_THE_PROXY_2026-11-18.md`
(78a6c22cf): which domestic gas Jan:Jul ratio the world's population fallback
(`simulation/gas_settlement.py` `_GAS_BOILER_HEATING_FRACTION = 0.70`) should be calibrated to, and why "DUKES 4.3
~5.3x" and the DESNZ monthly 7.3 disagree. No world constant changes here.*

## 1. The answer in three sentences

When the world's own two-term form (a heating term proportional to HDD plus a flat term) is fitted to DESNZ's
published domestic gas against DESNZ's published heating degree days, it fits 2023–25 monthly at R² 0.97 and gives
a heating fraction of **0.85** on the 1991–2020 normal-weather basis. Every year from 2016 to 2025 lies between
**0.82 and 0.87** on quarterly data. The "~5.3x" the 0.70 was calibrated to is **not a published Jan:Jul ratio**.
It matches the published **Q1:Q3 quarterly** ratio (4.7–5.5 at normal weather), and no DESNZ table published a
domestic monthly series before January 2023. The 7.3 is a real Jan:Jul ratio, but three years of actual weather
(range 6.4–9.7) are a poor target. The quantity to calibrate is the fraction, not a ratio.

## 2. The sources, and what each one is

All three are DESNZ Energy Trends workbooks, retrieved 2026-11-19 from gov.uk. They were read on the harness, not by
any runtime (W6).

| table | file read | what it gives | basis |
|---|---|---|---|
| **ET 4.2** Natural gas supply and demand, monthly | `ET_4.2_OCT_26.xlsx`, sheet `Month (GWh)`, column `Domestic` | domestic gas by month, **from January 2023 only**. Earlier months are `[x]`, "data not available" | actual weather. "Official Statistics in Development". The column sits under the workbook's "Sales" heading |
| **ET 4.1** Natural gas supply and consumption, quarterly | `ET_4.1_SEP_26.xlsx`, sheet `Quarter (GWh)`, row `Domestic` | domestic gas by quarter, 1998 to Q2 2026 | actual weather. Accredited Official Statistics |
| **ET 7.1** Average temperatures and heating degree days | `ET_7.1_OCT_26.xlsx`, sheet `Data Heating Degree Days` | average daily HDD by month, 2002–2026, and the 1991–2020 30-year mean | Met Office stations, **base 15.5 °C** (Note 1), the same base as the world's `sim.weather_hdd.HDD_BASE_TEMP_C` |

**DUKES Table 4.3, as cited by the constant's comment, could not be matched to any domestic monthly series.** DUKES
publishes annual commodity balances. DESNZ's monthly domestic split starts in 2023 (ET 4.2 above). So "DUKES Table
4.3 residential gas monthly shares (2016-2020 avg)" (`simulation/gas_settlement.py`, the comments on
`GAS_CONSUMPTION_MONTHLY_PROFILE` and `_GAS_BOILER_HEATING_FRACTION`) cannot be a DESNZ domestic monthly series as
worded. What the comment's figure *does* match is in §4. **GAP:** the original source behind the Phase 59 profile is
unrecovered. The comment is a citation that cannot be reached, not a fact this page can confirm.

## 3. Method

Each year's domestic gas, monthly (ET 4.2) or quarterly (ET 4.1), was fitted by least squares to
`kWh = a·HDD + b·days`, using that period's actual HDD (ET 7.1 daily average × days). This is the world's form
exactly (`resi_daily_gas_kwh`: a heating term in HDD plus a flat DHW/cooking term per day). The heating fraction on
the world's basis is the heating share **at normal weather**, because the world's constant is defined as "annual
total conserved when actual HDD equals reference HDD":

    f_normal = a·H_norm / (a·H_norm + b·365),   H_norm = 2,058 (ET 7.1 1991–2020 mean, summed by month)

The share at the year's own actual HDD is also printed, because it differs. Warm years carry less heating.

## 4. Results

**Monthly, 2023–25 (ET 4.2 × ET 7.1).**

| year | domestic TWh | Jan/Jul actual | Jun–Aug share | fit R² | f at actual HDD | **f at normal HDD** | Jan/Jul at normal HDD |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2023 | 241.8 | 6.53 | 7.21% | 0.969 | 0.830 | **0.848** | 7.15 |
| 2024 | 252.3 | 6.35 | 8.04% | 0.978 | 0.830 | **0.849** | 7.20 |
| 2025 | 250.4 | 9.65 | 6.47% | 0.966 | 0.841 | **0.858** | 7.47 |
| 3-yr share average | | **7.31** | 7.23% | | | | |

The 7.31 in the seat finding and in `how_a_supplier_shapes_an_estimate_for_an_unread_month.md` §4 reproduces exactly.
Its per-year range, 6.35 to 9.65, is mostly July. July's HDD is near zero and moves the ratio's denominator, and
January 2025 ran 1.2 HDD/day above normal. A Jan:Jul ratio of actuals is the least stable shape statistic there is.

**Quarterly, 2016–25 (ET 4.1 × ET 7.1).** Four points and two parameters per year, so each year is a weak fit. The
decade is the point.

| year | Q1/Q3 actual | Q3 share | annual HDD | **f at normal HDD** | Q1/Q3 at normal HDD |
|---|---:|---:|---:|---:|---:|
| 2016 | 5.96 | 6.9% | 2,021 | 0.826 | 4.82 |
| 2017 | 4.59 | 8.7% | 1,889 | 0.835 | 4.94 |
| 2018 | 5.81 | 8.0% | 1,992 | 0.848 | 5.13 |
| 2019 | 5.85 | 6.9% | 1,983 | 0.866 | 5.44 |
| 2020 | 4.22 | 9.3% | 1,865 | 0.848 | 5.14 |
| 2021 | 6.01 | 7.2% | 2,021 | 0.818 | 4.70 |
| 2022 | 5.75 | 7.7% | 1,790 | 0.866 | 5.43 |
| 2023 | 5.68 | 7.6% | 1,800 | 0.858 | 5.30 |
| 2024 | 4.67 | 8.8% | 1,781 | 0.863 | 5.39 |
| 2025 | 5.66 | 7.8% | 1,797 | 0.867 | 5.46 |
| **mean** | | | | **0.850** (0.818–0.867) | **5.18** |

**The world, at the same inputs** (two-term shares, computed from `REFERENCE_MONTHLY_HDD` and the DESNZ normal):

| heating fraction | on the world's `REFERENCE_MONTHLY_HDD` | on DESNZ 1991–2020 normal HDD |
|---|---|---|
| 0.70 (shipped) | Jan/Jul **5.30**, Jun–Aug 8.9% | Jan/Jul 4.30, Jun–Aug 10.7% |
| 0.75 | 6.43, 7.8% | (n/a) |
| 0.80 | 8.06, 6.6% | 5.94, 8.6% |
| 0.85 | 10.59, 5.4% | **7.22, 7.5%** |

## 5. Reconciling 5.3 and 7.3: the three candidate explanations, ranked by evidence

1. **The 5.3 was a quarterly ratio read as a monthly one. Most likely.** The published domestic Q1:Q3 ratio at
   normal weather averages 5.18 over 2016–25, and its range of 4.7–5.5 brackets 5.3. No domestic monthly series
   existed to give a 2016–2020 Jan:Jul. f = 0.70 was then chosen to make the *world's* Jan/Jul equal 5.30 on
   `REFERENCE_MONTHLY_HDD`, and it does so to two decimals. A Q1:Q3 ratio averages three months at each end. It is
   always much flatter than the peak month over the trough month, so a model fitted to it with Jan:Jul is too flat.
   Status: **strongly supported inference, not established**, because the original source is unrecovered (§2 GAP).
2. **The year window. Ruled out.** The fitted fraction is 0.82–0.87 in every year, 2016–22 as much as 2023–25. The
   2022–23 demand reduction lowered total domestic gas by about 18% (302 TWh in 2021 to a mean of 248 TWh over 2023–25) and
   did not flatten the year. If anything it sharpened it slightly: the mean f is 0.84 over 2016–21 and 0.86 over 2022–25. This matches the
   seat finding's own split, where the bias on 2023–25 was 104% of the all-years size.
3. **Actual against seasonal-normal weather. Real, but it is noise around 7.2, not the gap from 5.3.** Normalising
   each 2023–25 year to 1991–2020 weather gives a Jan/Jul of 7.15–7.47. The three-year actual 7.31 is close to normal
   only because a warm 2023–24 and a cold January 2025 offset each other.
4. **Sales against consumption. Small, and not the cause.** ET 4.2 domestic is published under "Sales". ET 4.1 is
   "consumption". Over 2023–25, where both exist, the fitted f differs by 0.009–0.014, with the quarterly fit higher.
   That is about what moving from monthly to quarterly resolution would do on its own. **GAP:** neither workbook states
   how DESNZ allocates monthly domestic demand. It is probably from NDM allocation, the same profiles a supplier
   sees, but that is unconfirmed.

**A coupled constant, flagged.** The fraction and the HDD table it multiplies cannot be calibrated apart.
`REFERENCE_MONTHLY_HDD` has July at 5 and June at 30. DESNZ's 1991–2020 normal is 19 and 51. The annual totals agree
(2,066 against 2,058), but the world's reference year is more peaked in summer. So f = 0.85 on the world's reference
table gives a Jan/Jul of 10.6, not 7.2. The world settles each premise on its *own* HadUK-Grid cell HDD, not on the
reference, so the reference table only sets the normalisation and the fallback for premises without a sky. **GAP:**
`REFERENCE_MONTHLY_HDD` carries no source in its comment, and its summer months sit below the DESNZ normal.

## 6. What the published series says the two-term form gets wrong

The two-term residual (actual minus fit, as a share of the year) repeats in all three years:

| | Jan | Feb | Mar | **Apr** | May | Jun | Jul | Aug | Sep | Oct | Nov | **Dec** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2023 | +0.5 | +0.3 | −0.2 | **−2.2** | −1.2 | +0.1 | +0.7 | +0.3 | +0.5 | −0.3 | −0.1 | **+1.7** |
| 2024 | −0.3 | +0.7 | −0.5 | **−1.3** | +0.3 | −0.7 | +0.4 | +0.6 | −0.5 | 0.0 | −0.3 | **+1.6** |
| 2025 | −0.2 | +0.2 | −1.0 | **−2.1** | −1.6 | +0.3 | +0.5 | +0.7 | −0.1 | +0.8 | +0.8 | **+1.6** |

Real households use 1.3–2.2% of the year *less* gas in April than the HDD the month carries would imply. They use
about 1.6% *more* in December. This is the "heating off in spring" behaviour that residual 4 of the seat finding
hypothesised for the world's fabric provider, which heats deeper into spring than DESNZ. It is now **observed in the
published national series, direction and size**. December's excess is consistent with the season's start and the
holidays (occupancy). That reading is a hypothesis. The national data establishes only the residual.

## 7. The choices this page hands to the build, and what it leaves open

- **The calibration target is the heating fraction on the normal-weather basis: 0.85, with a published range of
  0.82–0.87 over 2016–25.** It is not a Jan:Jul ratio. Jan:Jul is a check, and it must be computed on the same HDD
  basis as the target (7.2 at DESNZ normal). F11, erring against the thesis: the company's estimator already uses the
  DESNZ shape, so a steeper world *shrinks* the gap the D48 finding reported. The world fix must be graded on the book
  after skip0, with the seat finding's table as the pre-registered baseline. It is a baseline (R13) change, decided on
  this page's evidence and blind to company results.
- **Before the constant moves, `REFERENCE_MONTHLY_HDD` needs a source or a re-basis on ET 7.1's 1991–2020 mean.**
  Moving f alone on today's reference table overshoots in summer (§5).
- **The world's fabric provider already reproduces DESNZ in aggregate** (Jan/Jul 7.23, per the seat finding). It
  needs no recalibration from this page. Its spring residual matches §6.
- **GAP:** the national figure is an average over all gas households. Whether low users are flatter (the seat
  finding's tercile cut: 4.94 against 5.69) is a property of the households themselves, or partly a measurement
  artefact, is not established from DESNZ data. NEED's annual consumption carries no monthly shape.

## 8. Why the `OCC-` gas accounts are missing from `gas_shape_provider_by_customer`

`simulation/run_phase2b.py` `_admit_incoming_occupant` (B7's incoming occupier) copies everything "keyed by meter
point" from the vacated premise to the new `OCC-` leg: weather, cloud cover, the half-hourly trace, the fabric series,
the property, the EAC and the fabric-eligibility verdict. It does **not** copy the premise's
`gas_heating_fraction_by_customer` entry or its `gas_shape_refusals` row. As a result:

1. at settlement, `gas_heating_fraction_by_customer.get(OCC-…)` is `None`, so `run_gas_term` falls to the population
   0.70 even where the premise has a fabric split. That is a fidelity defect, not only a record defect. The 241
   unrecorded account-years read Jan/Jul 4.82, which is the fallback's shape;
2. the run record (`gas_shape_provider_by_customer`, built from those two collections only) omits them, so the
   fallback they settle on is exactly the "silently keeping the population constant" that the record exists to show.

The fix belongs with the W2_30 world change, not here. Carry the premise's split onto the occupier's leg, or record a
refusal naming why it is not carried. A split is fitted to a household's own occupancy, so whether a new occupier
inherits the premise's fraction is a design choice to state on the relocation path's terms (§8.7 of
`home_moves.md`). Either way, every gas leg that settles must appear in the record. It changes the gas book, so it
lands with the recalibration and is graded on the same post-skip0 book.

## 9. GAP: what a published source sets an incoming occupier's heating fraction to

*Added 2026-11-20 for the legs the ERA5 pull can never move. The count is in the W2_30 simplification note,
`l3_gate_note` (SPLIT 2026-11-20).* On book 67d454905c, 433 gas legs settle on the 0.70 fallback. 319 of them wait only on
weather cells, which W1_14's pull fills. 114 never will: 113 `OCC-` legs (§8: the occupier's leg does not carry the
premise's split) and one leg whose own trace shows no cold response. For the `OCC-` legs the question is what an
incoming household's heating fraction is in a dwelling whose fabric the world already knows.

**No published source sets it.** What exists, and what each piece does and does not establish:

| source | what it establishes | why it does not set the fraction |
|---|---|---|
| This page, §4 (DESNZ ET 4.1/4.2 × ET 7.1) | the national domestic heating fraction is 0.85 (0.82–0.87, 2016–25) | a population average over all gas households. It is not conditioned on the dwelling or on a change of occupier |
| DECC, NEED *Annex C, Change of occupancy analysis* | gas use fell on average 2,100 kWh after a property sale, against 600 kWh in matched unsold properties. Property characteristics usually stay the same, so the difference is the occupiers | annual LEVEL only. NEED carries no monthly shape, so it says nothing about the heating SHARE |
| Sonderegger (1978), as reviewed by Huebner et al. (eceee 2015) | about 18% of the variability in gas use was attributed to occupants, estimated from houses that changed occupants | a loose estimate of variance in level, from one US sample. Not a share of the year that follows HDD |
| Dutch and Danish change-of-occupancy decompositions (TU Delft *A+BE* journal) | occupant effects on heating use are larger in more efficient buildings | not UK, and about level, not the seasonal split |

**What is established, as a stated belief with a range.** The fraction is fabric plus occupancy (the world fits it on
the household's own trace). The fabric part does not change at a move. So the premise's fitted fraction is the best
available prior for the occupier's leg, and the national 0.85 (0.82–0.87) is the floor-of-knowledge fallback for a
premise with no fit. Both are inferences from the world's own two-term form. Neither is a published occupier figure.

**GAP, named.** How far an incoming household's heating fraction sits from its predecessor's in the same dwelling.
Closing it needs same-dwelling, before-and-after monthly or daily gas, of the kind SERL holds. SERL is accredited
access and not pursued (canon §6). So the build that §8 names states its choice as a design choice ("inherit the
premise's fit") and carries this GAP. It does not cite a number. Nothing is built here.

## Sources

- DESNZ, *Energy Trends Table 4.2, Natural gas supply and demand*, `ET_4.2_OCT_26.xlsx` (published 29 Oct 2026),
  https://www.gov.uk/government/statistics/gas-section-4-energy-trends, retrieved 2026-11-19.
- DESNZ, *Energy Trends Table 4.1, Natural gas supply and consumption*, `ET_4.1_SEP_26.xlsx` (published 29 Sep 2026),
  same page, retrieved 2026-11-19.
- DESNZ, *Energy Trends Table 7.1, Average temperatures and heating degree days*, `ET_7.1_OCT_26.xlsx`,
  https://www.gov.uk/government/statistics/energy-trends-section-7-weather, retrieved 2026-11-19. Notes 1 and 3:
  base 15.5 °C, 30-year mean 1991–2020.
- This project: `simulation/gas_settlement.py` (`_GAS_BOILER_HEATING_FRACTION`, `GAS_CONSUMPTION_MONTHLY_PROFILE`,
  `resi_daily_gas_kwh`); `sim/weather_hdd.py` (`REFERENCE_MONTHLY_HDD`, `HDD_BASE_TEMP_C`);
  `docs/market_research/how_a_supplier_shapes_an_estimate_for_an_unread_month.md` §4.

**Reproduce.** Download the three workbooks. Read `Domestic` from ET 4.2 `Month (GWh)` and ET 4.1 `Quarter (GWh)`.
Read the first block of ET 7.1 `Data Heating Degree Days` (daily average × days in month). Least-squares fit
`[HDD, days]` per year with no intercept, then apply the `f_normal` formula in §3.
- DECC, *National Energy Efficiency Data-Framework, Annex C: Change of occupancy analysis*,
  https://assets.publishing.service.gov.uk/media/5a8061f1ed915d74e622e222/Annex_C_Change_of_occupancy_analysis.pdf,
  found 2026-11-20 by search. The figures in §9 are as the search summary quoted them; the PDF was not opened.
- Huebner et al., eceee 2015 Summer Study, https://proceedings.eceee.org/docs/2015/5-083-15_Huebner.pdf (citing
  Sonderegger 1978), found 2026-11-20 by search. Not opened.
- Dutch/Danish change-of-occupancy decomposition, *A+BE Architecture and the Built Environment*,
  https://journals.open.tudelft.nl/abe/article/download/6673/5470, found 2026-11-20 by search. Not opened.
