# GB Multi-Plant SRMC Dispatch Stack — Heat Rates, O&M, Carbon, Merit Order

**Serves**: fidelity row `W1_6_physics_price_signal` (`sim/price_engine.py`), the "remaining named
gap" identified in `docs/design/frame/W1_6_merit_order_reconstruction_FRAME.md` §2 — published
GB ground truth for a **multi-plant short-run-marginal-cost (SRMC) dispatch stack**, replacing the
live single-CCGT-floor + global scarcity-multiplier reduced form.

**Task context (do not re-derive, cited as pre-loaded ground truth)**:
- `docs/market_research/ssp_dispatchable_fleet_renewables_era_boundaries_2026-07-24.md` — DUKES
  Ch.5 capacity/renewables-share era boundaries, coal exit (30 Sep 2024).
- `docs/market_research/ssp_scarcity_constants_external_benchmark_2026-07-24.md` — £6,000/MWh
  cash-out ceiling, LOLE ≤3h/yr reliability standard, CCGT confirmed as GB reference marginal
  technology (Capacity Market Net-CONE).

**Epistemic scope**: discovery-only, external published sources + `docs/market_research/`. No
`sim/`, `company/`, or any simulation code read or touched (the FRAME doc's quoted excerpts of
`sim/price_engine.py`, supplied in the task brief, are the only simulation-layer text referenced
below — this document does not itself read that file). No simulation output read or used to shape
any figure below (R13). No fabricated constants — every numeric claim below is either cited to a
resolvable published source or explicitly marked `NAMED GAP (R10)`.

**Retrieved**: 2026-07-25. Network available this session (`gov.uk`, `assets.publishing.service.gov.uk`
all HTTP 200); DESNZ/gov.uk direct-URL + `/api/search.json` route worked reliably (same pattern
noted in the 2026-07-24 pass); general web search engines and Elexon's own site were not probed
this session (not needed — all target data was found on DESNZ/gov.uk).

---

## ASSUMPTIONS / NAMED GAPS — read this first

1. **OCGT / peaker fleet-average efficiency has NO DUKES fleet-average series** (DUKES 5.10.C
   only breaks out CCGT, coal, and nuclear — OCGT is buried inside "conventional thermal and other
   stations", not separately reported). What is available is **new-build reference-plant**
   efficiency from DESNZ's Electricity Generation Costs modelling assumptions (§1 below) — a
   defensible peaker-tier proxy, but NOT a fleet-average matching the CCGT/coal treatment.
   **NAMED GAP (R10)**: no OCGT fleet-average time series 2016-2025 was found.
2. **Coal Variable O&M was not found in either DESNZ generation-cost workbook checked** (the 2016
   report's Table 19/Case 1 only price new-build CCGT/OCGT, since no new coal build was being
   contemplated by 2016; the 2025 report has no coal column at all, since coal is fully exited).
   **NAMED GAP (R10)**: coal variable O&M for 2016-2024 not found in a primary DESNZ source this
   session; a 2013 DECC report was checked but its plain-text PDF extraction produced column-order
   artefacts too unreliable to cite as ground truth (flagged, not used).
3. **EU ETS (2016-2020) / UK ETS (2021-2024) actual annual-average market price time series was
   NOT found this session.** `gov.uk`'s "Determinations of the EU ETS carbon price" and
   "Determinations of the UK ETS carbon price" pages are civil-penalty default-price
   determinations, not a published historical average-price series; DESNZ's "Traded carbon
   values" publications are forward-looking modelling *appraisal* trajectories (2025 report's
   Table 1 starts at 2025, does not tabulate 2016-2024 actuals); DUKES Chapter 1/5 has no ETS
   price table; external financial-data aggregators (World Bank Carbon Pricing Dashboard, Ember,
   TradingEconomics) returned HTTP 403/301 or required JS this session. **NAMED GAP (R10)** — see
   §4 for what a future pass should try (ICE/EEX historical settlement data, or DESNZ's Digest of
   UK Energy Statistics annex tables not yet checked).
4. **Published % of half-hours GB gas is the price-setting/marginal plant was NOT found this
   session** (searched REMA consultation/summer-update documents and DESNZ news releases; the
   REMA summer update 2025 confirms ~30% of GB generation is "still exposed to wholesale prices
   set by gas" as a *generation-share* statement, not a *marginal-hours* statistic). **NAMED GAP
   (R10)** — see §5.
5. **Thermal efficiency basis matters and is NOT always stated**: DUKES 5.10.C is explicitly
   **gross calorific value (GCV/HHV)** basis; the 2016 DECC generation-cost report is explicitly
   HHV; the **2025 DESNZ Annex A workbook does not state a basis** for its "Average fuel
   efficiency" row. Below, the 2025 figure is treated as **probably GCV/HHV** (M confidence,
   inferred) because it sits almost exactly on the same value as the explicitly-HHV 2016 report's
   H-class figure — but this is inference, not a quoted basis statement, and is flagged as such.

---

## 1. Per-plant-type thermal efficiency (heat rate)

### 1a. Fleet-average, gross CV (HHV) basis, DUKES 5.10.C, 2016-2024 (H confidence)

| Year | CCGT % | Coal % | Nuclear % |
|---|---|---|---|
| 2016 | 48.93 | 34.98 | 40.01 |
| 2017 | 48.69 | 34.86 | 39.99 |
| 2018 | 48.94 | 34.10 | 39.79 |
| 2019 | 48.78 | 32.05 | 39.97 |
| 2020 | 48.44 | 33.24 | 40.33 |
| 2021 | 49.00 | 34.82 | 39.86 |
| 2022 | 49.11 | 36.46 | 39.62 |
| 2023 | 49.91 | 35.82 | 39.71 |
| 2024 | 48.93 | 41.51 | 39.58 |

**Representative central value (whole window)**: CCGT ≈ **49.0%** (range 48.4-49.9%, tight —
fleet average is stable across the decade despite the fleet itself changing composition); coal ≈
**34-35%** for 2016-2023 with a **41.5% outlier in 2024** (only ~18 MW of coal capacity remained
that year per the 2026-07-24 era-boundary doc — a residual/thin-sample artefact, not a genuine
fleet-efficiency jump, flagged not smoothed); nuclear ≈ **39.6-40.3%**, essentially flat (AGR/PWR
fleet, technology doesn't change year to year).

**Source**: DUKES Table 5.10.C "Thermal efficiency, gross calorific value basis, per cent",
`DUKES_5.10.xlsx`, sheet `5.10.B and 5.10.C`, downloaded from
`https://assets.publishing.service.gov.uk/media/688a28d6a11f85999440927a/DUKES_5.10.xlsx` (via
`https://www.gov.uk/government/statistics/electricity-chapter-5-digest-of-united-kingdom-energy-statistics-dukes`),
retrieved 2026-07-25. **Confidence: H** — primary published statistical series, read cell-by-cell
from the fetched workbook (year-column alignment double-checked against the sheet's own header
row after an initial off-by-one zip bug was caught and corrected).

### 1b. Modern/best new-build reference plant (H confidence, different population — not fleet-average)

| Technology | Efficiency (HHV) | Vintage / commissioning | Source |
|---|---|---|---|
| CCGT H-Class | 53.7% | ~2018-2025 reference build | DECC/BEIS 2016 report, Table 19 |
| CCGT F-Class | 52.8% | ~2018-2025 reference build | DECC/BEIS 2016 report, Table 19 |
| OCGT 600MW | 35.2% | ~2018-2020 reference build | DECC/BEIS 2016 report, Table 19 |
| OCGT 400MW | 34.2% | ~2018-2020 reference build | DECC/BEIS 2016 report, Table 19 |
| OCGT 300/299MW | 34.8% | ~2018-2020 reference build | DECC/BEIS 2016 report, Table 19 |
| OCGT 100MW | 35.2% | ~2018-2020 reference build | DECC/BEIS 2016 report, Table 19 |
| Gas CCGT (93% LF case) | 54% (basis unstated, M-confidence inferred as HHV — see Assumption 5) | 2030 commissioning | DESNZ Electricity Generation Costs 2025, Annex A |
| Gas OCGT 300MW (93% LF case) | 35% (basis as above) | 2030 commissioning | DESNZ Electricity Generation Costs 2025, Annex A |
| Gas OCGT 760MW (93% LF case) | 36% (basis as above) | 2030 commissioning | DESNZ Electricity Generation Costs 2025, Annex A |

**Sources**: (i) DECC/BEIS, *"Electricity Generation Costs (November 2016)"*, Annexes workbook
`Generation_Costs_Report_2016_Annexes.xlsx`, sheet `Table 19`, downloaded from
`https://assets.publishing.service.gov.uk/media/5ce55ca0ed915d247979f938/Generation_Costs_Report_2016_Annexes.xlsx`
(via `https://www.gov.uk/government/publications/beis-electricity-generation-costs-november-2016`),
retrieved 2026-07-25. (ii) DESNZ, *"Electricity Generation Costs 2025"*, Annex A workbook
`annex-a-additional-estimates-and-key-assumptions-2025.xlsx`, sheet `Technical and Cost
Assumptions`, downloaded from
`https://assets.publishing.service.gov.uk/media/69d8efec96c86b7513170229/annex-a-additional-estimates-and-key-assumptions-2025.xlsx`
(via `https://www.gov.uk/government/publications/electricity-generation-costs-2025`), retrieved
2026-07-25. Workbook's own general note: "All costs are in real 2024 GBP." **Confidence: H** for
the numeric values as fetched; the population (new-build reference plant, not fleet average) is a
structurally different quantity from §1a — see the cross-check below.

**Cross-check (worth noting for the reconstruction)**: the fleet-average CCGT efficiency (§1a,
~49% HHV, blending old and new units across 2016-2024) sits *below* the modern-build reference
(52.8-53.7% HHV, §1b) — exactly the direction expected (older vintage plants in the operating
fleet drag the average down from best-available technology). The near-identical 2016 H-class
figure (53.7% HHV) and 2025 Annex A "93% LF" figure (54%, basis unstated) support the M-confidence
inference in Assumption 5 that the 2025 figure is also HHV/gross-CV, not a switch to NCV/LHV
(switching to NCV would be expected to raise the figure to ~59-60%, not leave it near-identical).

---

## 2. Variable O&M (£/MWh)

| Technology | Variable O&M | Price basis / vintage | Source |
|---|---|---|---|
| CCGT (all classes) | £3/MWh | Medium case, DECC 2016 report (real terms of that report, not restated) | DECC/BEIS 2016 report, Table 19 / Case 1 |
| OCGT (all sizes) | £3/MWh | Medium case, DECC 2016 report | DECC/BEIS 2016 report, Table 19 / Case 1 |
| Gas CCGT (all load-factor cases) | £5/MWh | Real 2024 GBP, 2030-commissioning reference | DESNZ Electricity Generation Costs 2025, Annex A |
| Gas OCGT 300MW & 760MW (all load-factor cases) | £5/MWh | Real 2024 GBP, 2030-commissioning reference | DESNZ Electricity Generation Costs 2025, Annex A |
| Coal | **NAMED GAP (R10)** | — | not found in either workbook (see Assumption 2) |

**Sources**: same two DESNZ/DECC workbooks as §1b. **Confidence: H** for the two data points
(£3/MWh circa-2016 report, £5/MWh circa-2024/2025 report) as fetched; **L** for treating this as a
smooth time series in between — only two data points exist ~9 years apart, and no year-by-year
CCGT/OCGT variable O&M series was found. A modest real-terms rise (£3→£5/MWh) across the decade is
directionally plausible (input-cost inflation, ageing-fleet maintenance) but the actual path
between the two points is **not evidenced** — treat any interpolation as a stated simplification,
not a grounded figure.

---

## 3. Emission factors — gas and coal

### 3a. Fuel/thermal-input basis (tCO2 per MWh of fuel energy input, gross CV) — cross-checks the live `EF_GAS_TCO2_PER_MWH_TH = 0.184` constant

| Fuel | tCO2/MWh_thermal (gross CV) | Source |
|---|---|---|
| Natural gas | **0.1829** | DESNZ, *"Greenhouse gas reporting: conversion factors 2024"*, condensed-set workbook, sheet `Fuels`, row "Natural gas, kWh (Gross CV)" |
| Coal (electricity generation) | **0.31699** | Same source, sheet `Fuels`, row "Coal (electricity generation), kWh (Gross CV)" |

**Source**: DESNZ, *"UK Government GHG Conversion Factors for Company Reporting"*, 2024 dataset,
`ghg-conversion-factors-2024-condensed_set__for_most_users__v1_1.xlsx`, downloaded from
`https://assets.publishing.service.gov.uk/media/6722566a3758e4604742aa1e/ghg-conversion-factors-2024-condensed_set__for_most_users__v1_1.xlsx`
(via `https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024`),
retrieved 2026-07-25. **Confidence: H** — primary published DESNZ conversion-factor series, read
directly from the fetched workbook (also independently cross-checked against a second, published
row on the same sheet — "kWh (Net CV)" for the same fuel — as a basis-sanity check: Net CV gas
factor is 0.20264, higher than the Gross CV 0.1829, consistent with the workbook's own
gross-CV-vs-net-CV guidance text that net-CV energy content is lower per unit mass, so more CO2
per unit of net-CV-delivered-energy).

**Finding — the live engine's `EF_GAS_TCO2_PER_MWH_TH = 0.184` constant is well-grounded**: it
sits within 0.3% of the published 2024 gross-CV natural-gas factor (0.1829). **No correction is
needed to this specific constant.** What IS missing structurally (already named in the FRAME doc,
not re-derived here) is that `carbon_price_gbp_per_tonne` defaults to 0.0 at runtime, so this
otherwise-accurate emission factor is never actually multiplied by a nonzero carbon price in the
live ordinary-day price path.

### 3b. Per-electrical-MWh-supplied basis (tCO2/MWh_e) — a second, independent published series, useful as the SRMC-stack's electrical-output-basis emission factor

| Year | Gas tCO2/MWh_e | Coal tCO2/MWh_e |
|---|---|---|
| 2016 | 0.378 | 0.935 |
| 2017 | 0.380 | 0.918 |
| 2018 | 0.378 | 0.921 |
| 2019 | 0.367 | 0.992 |
| 2020 | 0.371 | 1.008 |
| 2021 | 0.376 | 0.970 |
| 2022 | 0.379 | 0.987 |
| 2023 (provisional) | 0.372 | 1.021 |
| 2024 (provisional) | 0.382 | 0.919 |

**Source**: DUKES Table 5.14 "Estimated carbon dioxide emission intensity of electricity supplied,
tonnes of CO2 per GWh supplied", `DUKES_5.14.xlsx`, downloaded from
`https://assets.publishing.service.gov.uk/media/688a2923a11f85999440927c/DUKES_5.14.xlsx` (via
`https://www.gov.uk/government/statistics/electricity-chapter-5-digest-of-united-kingdom-energy-statistics-dukes`),
retrieved 2026-07-25 (values converted from the table's native tCO2/GWh to tCO2/MWh by ÷1000; 2023
and 2024 are labelled provisional in the workbook's own note 3). **Confidence: H** for 2016-2022
(final figures); **H but provisional** for 2023-2024 per the source's own flag.

**Cross-check between §3a and §3b**: combining the §3a fuel-input factor with the §1a fleet-average
efficiency reproduces §3b almost exactly — e.g. gas 2016: 0.1829 tCO2/MWh_th ÷ 0.4893 efficiency =
0.374 tCO2/MWh_e, against the independently-published 0.378 (§3b) — **a ~1% gap between two
independently-sourced DESNZ series**, a strong internal-consistency check that both the emission
factor and the fleet-efficiency figures used above are mutually coherent, not cherry-picked.

---

## 4. UK carbon price — Carbon Price Support (H confidence, frozen) + ETS market price (NAMED GAP)

### 4a. Carbon Price Support (CPS) rate — the UK-specific top-up on the traded ETS price

| Taxable commodity | Rate | Period |
|---|---|---|
| Gas | £0.00331/kWh (gross CV) | **1 April 2016 to 31 March 2028 — unchanged for the entire window** |
| Coal and other solid fossil fuels | £1.54790/GJ (gross CV) | **1 April 2016 to 31 March 2028 — unchanged for the entire window** |

**Source**: HMRC, *"Climate Change Levy rates"*, `https://www.gov.uk/guidance/climate-change-levy-rates`,
retrieved 2026-07-25 (page last updated 2025-11-27 per its own change-log; the "1 April 2016 to 31
March 2028" band has been present since the page's original 2016-05-17 publication and has not
been altered by any of the six subsequent updates the page's own change-log lists). **Confidence:
H** — primary HMRC/gov.uk rate table, directly fetched and quoted verbatim.

**Converted to £/tCO2 (derived, using this document's own §3a emission factors, not a separately
published £/tCO2 CPS figure)**: gas CPS = £0.00331/kWh ÷ 0.184 tCO2/MWh_th (§3a) × 1000 ≈
**£18.0/tCO2**; coal CPS = £1.5479/GJ × 3.6 GJ→MWh ÷ 0.317 tCO2/MWh_th (§3a) ≈ **£17.6/tCO2**.
This reproduces the widely-cited "CPS frozen at £18/tCO2" figure from first principles using only
sources already fetched in this document — flagged here as a **derived cross-check (M confidence
for the £/tCO2 conversion specifically, H for the underlying £/kWh and £/GJ rates)**, not a
separately quoted £/tCO2 government figure.

**Finding — this is the single most load-bearing, cleanly-grounded input for the reconstruction**:
unlike the ETS market price (§4b, a genuine year-to-year variable), the UK's Carbon Price Support
top-up has been a **known constant (~£18/tCO2-equivalent) across the ENTIRE 2016-2025 window**,
confirmed to run through March 2028. A merit-order SRMC stack can treat CPS as a hard-coded,
time-invariant constant with H confidence — it is only the ETS component of "Total Carbon Price"
that genuinely needs a time series.

### 4b. EU ETS (2016-2020) / UK ETS (2021-2024/25) market price — NAMED GAP (R10)

**What was checked and did not yield a usable annual-average time series** (see Assumption 3 for
detail): HMRC's EU ETS/UK ETS "Determinations" pages (civil-penalty default prices, not a market
average); DESNZ's "Traded carbon values used for modelling purposes" 2023/2024/2025 publications
(forward-looking appraisal trajectories starting at the publication year — the 2025 edition's
Table 1 starts at **£44/tCO2e, real 2025 GBP, "Market Traded Carbon Values" central case for
2025**, the one genuinely-dated, H-confidence data point recoverable this session, but it is a
single year, not the 2016-2024 series needed); DUKES Chapters 1 and 5 (no ETS price table in
either); external carbon-price aggregators (World Bank Carbon Pricing Dashboard HTTP 403, Ember
HTTP 301-redirect requiring JS, TradingEconomics reachable but not a citable primary-data page for
a resolvable historical series in this session's time budget).

**Source for the one usable 2025 data point**: DESNZ, *"Traded carbon values used for modelling
purposes, 2025"*, HTML detail page
`https://www.gov.uk/government/publications/traded-carbon-values-used-for-modelling-purposes-2025/traded-carbon-values-used-for-modelling-purposes-2025`,
Table 1, retrieved 2026-07-25 ("Market Traded Carbon Values" column, year 2025 row = £44).
**Confidence: H** for this single 2025 figure; **gap for 2016-2024** stands.

**Recommended next-pass sources (not yet tried, named so the next DISCOVER doesn't re-spend this
session's search budget)**: (i) ICE Endex / EEX published historical EUA/UKA futures settlement
data (financial-market primary source, may need a different fetch route than this session's
`curl`); (ii) DESNZ's **Digest of UK Energy Statistics annex/data-tables collection** (not the
Chapter 1/5 narrative tables checked this session — DUKES has a broader "Annex" set that was not
enumerated); (iii) the **UK ETS Authority's own quarterly/annual reports** (`gov.uk` collection
"UK Emissions Trading Scheme (UK ETS): reports and scheme reviews", browsed at collection level
this session but individual report PDFs not opened for a price table); (iv) academic/NESO papers
citing EU ETS Phase III (2013-2020) and UK ETS (2021-) average auction clearing prices.

---

## 5. The merit order and how often gas is marginal

### 5a. Structural merit order (qualitative, cross-referenced against the 2026-07-24 pass's Finding 3 — CCGT confirmed GB reference marginal technology via Capacity Market Net-CONE)

Must-run baseload (nuclear, priced inelastically; wind/solar, zero/near-zero marginal cost) →
mid-merit thermal (CCGT, the confirmed GB reference marginal technology) → peaking plant
(OCGT/reciprocating engines, high fuel cost per MWh but low fixed cost, dispatched only at high
residual demand) → reserve/cash-out (toward the £6,000/MWh regulatory ceiling, per the
2026-07-24 pass's Finding 1). This structure is **not separately re-confirmed by a single
named source this session** — it is standard GB electricity-market architecture, consistent with
(a) the Capacity Market Net-CONE reference-technology finding already on record, and (b) the load
factor data in §5b below, which shows exactly the behaviour this ordering predicts.

### 5b. Load-factor evidence consistent with (not direct proof of) gas's mid-merit/marginal role, 2016-2024 (H confidence, DUKES 5.10.B)

| Year | CCGT load factor % | Coal load factor % |
|---|---|---|
| 2016 | 49.77 | 21.19 |
| 2017 | 45.48 | 17.33 |
| 2018 | 40.99 | 14.16 |
| 2019 | 41.49 | 7.82 |
| 2020 | 35.56 | 9.68 |
| 2021 | 39.94 | 12.67 |
| 2022 | 41.23 | 10.83 |
| 2023 | 33.02 | 11.63 |
| 2024 | 27.75 | 15.06 |

**Source**: DUKES Table 5.10.B "Plant load factor, per cent", same workbook/sheet as §1a,
retrieved 2026-07-25. **Confidence: H** for the figures; **M/inferred** for the interpretation
that follows. **Finding**: CCGT load factor fell steadily from ~50% (2016) to ~28% (2024) as
renewables build-out absorbed more baseload hours — consistent with CCGT increasingly being the
**marginal, not baseload**, plant across the window (a plant running only a third of the time is
by definition not baseload). Coal's much lower and more volatile load factor (7.8-21.2%) is
consistent with coal sitting *above* gas in the cost stack for most of the window (dispatched only
when gas + carbon costs made coal cheaper, e.g. price-spike years), rather than below it.

### 5c. % of half-hours gas is the price-setting/marginal plant — NAMED GAP (R10)

No published GB source giving a direct **% of settlement periods where gas is the marginal
price-setting plant**, for any part of 2016-2025, was found this session (search attempts against
REMA consultation/summer-update documents, DESNZ news releases, and general gov.uk full-text
search all returned no qualifying result — see Assumption 4). The closest adjacent published
statement found is qualitative and about *generation share*, not *marginal hours*: DESNZ's
"Decisive action to break influence of gas on electricity prices" (gov.uk news release,
retrieved 2026-07-25) states "a significant share of renewable generation – about 30% of
Britain's power supply – is still exposed to wholesale prices set by gas" — this is a
generation-share statistic (30% of MWh), not a marginal-hours statistic, and should not be
conflated with one. **NAMED GAP (R10)** for the specific % figure; the load-factor evidence in
§5b is the best available indirect proxy from this session.

---

## What this unblocks

This document closes the "remaining named gap" in
`docs/design/frame/W1_6_merit_order_reconstruction_FRAME.md` §2 to the extent published GB sources
allow: **the SRMC-stack BUILD now has grounded, cited inputs** for CCGT/coal/nuclear efficiency
(§1a, H-confidence fleet-average time series), a modern-build efficiency cross-check for the
peaker tier (§1b), CCGT/OCGT variable O&M bookends (§2), a cross-validated gas emission factor
that CONFIRMS the live engine's existing `EF_GAS_TCO2_PER_MWH_TH = 0.184` needs no correction
(§3a), an independent per-electrical-MWh emission-factor series for direct stack use (§3b), and —
the single cleanest finding — a **time-invariant, H-confidence UK Carbon Price Support constant
(~£18/tCO2, unchanged 1 April 2016 to 31 March 2028)** that can be wired into the ordinary-day SRMC
term immediately without waiting on the still-open ETS-market-price time series (§4b). Three
named gaps remain open for a follow-up DISCOVER pass before BUILD needs them: coal variable O&M
(§2), the EU ETS/UK ETS 2016-2024 annual-average market price series (§4b), and the %-of-hours-gas-
is-marginal statistic (§5c) — none of these block starting the SRMC-stack structural work, since
CPS alone (§4a) already reintroduces a nonzero, correctly-signed carbon term where the live engine
currently has zero. Per the FRAME doc, BUILD itself stays held behind the propose-then-proceed
window (open until 2026-07-28); this document is DISCOVER-only.

---

## Full source list

- DUKES Table 5.10 "Plant loads, demand and efficiency", `DUKES_5.10.xlsx` —
  https://assets.publishing.service.gov.uk/media/688a28d6a11f85999440927a/DUKES_5.10.xlsx
- DUKES Table 5.14 "Estimated carbon dioxide emission intensity of electricity supplied",
  `DUKES_5.14.xlsx` —
  https://assets.publishing.service.gov.uk/media/688a2923a11f85999440927c/DUKES_5.14.xlsx
- (both via https://www.gov.uk/government/statistics/electricity-chapter-5-digest-of-united-kingdom-energy-statistics-dukes)
- DECC/BEIS, "Electricity Generation Costs (November 2016)", Annexes workbook —
  https://assets.publishing.service.gov.uk/media/5ce55ca0ed915d247979f938/Generation_Costs_Report_2016_Annexes.xlsx
  (via https://www.gov.uk/government/publications/beis-electricity-generation-costs-november-2016)
- DESNZ, "Electricity Generation Costs 2025", Annex A workbook —
  https://assets.publishing.service.gov.uk/media/69d8efec96c86b7513170229/annex-a-additional-estimates-and-key-assumptions-2025.xlsx
  (via https://www.gov.uk/government/publications/electricity-generation-costs-2025)
- DESNZ, "Greenhouse gas reporting: conversion factors 2024", condensed-set workbook —
  https://assets.publishing.service.gov.uk/media/6722566a3758e4604742aa1e/ghg-conversion-factors-2024-condensed_set__for_most_users__v1_1.xlsx
  (via https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024)
- HMRC, "Climate Change Levy rates" — https://www.gov.uk/guidance/climate-change-levy-rates
- DESNZ, "Traded carbon values used for modelling purposes, 2025" —
  https://www.gov.uk/government/publications/traded-carbon-values-used-for-modelling-purposes-2025/traded-carbon-values-used-for-modelling-purposes-2025
- DESNZ, "Decisive action to break influence of gas on electricity prices" (news release) —
  https://www.gov.uk/government/news/decisive-action-to-break-influence-of-gas-on-electricity-prices
- DESNZ, "Review of Electricity Market Arrangements (REMA): Summer update, 2025" (browsed for
  context, no numeric figure quoted from it) —
  https://assets.publishing.service.gov.uk/media/686f71412557debd867cbeff/review-of-electricity-market-arrangements-rema-summer-update-2025.pdf
- Checked but not used as a citable primary source this session (named gaps / negative findings):
  HMRC "Determinations of the EU ETS carbon price" and "Determinations of the UK ETS carbon
  price" (civil-penalty default prices, not a market-average series); DECC "Electricity
  Generation Costs (December 2013)" PDF (coal O&M search — plain-text PDF-table extraction
  produced unreliable column alignment, not cited); World Bank Carbon Pricing Dashboard (HTTP
  403); Ember Climate (HTTP 301, JS-gated); TradingEconomics (reachable, not used — no resolvable
  primary time-series page found within this session's budget).

All retrieved 2026-07-25.
