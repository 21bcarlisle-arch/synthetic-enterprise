# Two UK electricity fuel mixes: what was generated, and what a supplier discloses

**Knowledge:** household-carbon-and-the-measures-that-save-it

*Written 2026-10-19 for item 4 of the director's steer of 19 Oct ("one home per fact"). Both sources
were fetched on the day. Before this page, the annual report published `Low Carbon %` twice, from two
hand tables with no vintage, up to 3.4 points apart. Neither table was either of the published
series it claimed to be.*

## 1. They are two facts, not one

DESNZ publishes two UK fuel mixes. They measure different things, and DESNZ says so on the
disclosure table itself (note 5): *"This differs from the UK generation mix published in UK Energy
Trends and the Digest of UK Energy Statistics as this table is compiled on an attribute basis in
line with the Fuel Mix Disclosure supply licence condition."*

| | **Generation mix** | **Fuel Mix Disclosure (FMD) UK fuel mix** |
|---|---|---|
| What it counts | Electricity **generated** in the UK, by fuel | Electricity **supplied** in the UK, by the attributes it carries |
| Imports | Not in it. Generation only | In it, allocated at the **European Attribute Mix** (32% coal in 2025) |
| Period | Calendar year | Disclosure period, **1 April to 31 March** |
| Buckets | Coal, oil, gas, nuclear, hydro, onshore/offshore wind, solar, thermal renewables (bioenergy), other fuels, storage | Coal, natural gas, nuclear, renewables, other |
| Publication | DUKES Table 5.6.C (annual); Energy Trends 5.1 (quarterly) | *Fuel mix disclosure data table*, one edition per period, overwritten in place on GOV.UK |
| Its job | A description of the system: what the grid burnt | A **licence requirement** (Electricity (Fuel Mix Disclosure) Regulations 2005; supply licence condition 21, per the table's own footnote): the UK comparison figure a supplier must show beside its own mix |

So the annual report's two sections should carry two different series, and they cannot agree. The
**Carbon Emissions Reporting Observatory** describes the grid, so it takes the generation mix. The
**UK Grid Fuel Mix Disclosure** is headed as the licence disclosure, so it takes the FMD UK mix. The
gap between them is now a defined difference, mostly imports and the April–March year.

## 2. What the old tables were (measured, not assumed)

- `company/billing/fuel_mix.py::_FUEL_MIX_BY_YEAR`, headed "Ofgem FMD", **was a generation mix**,
  not the FMD. Its renewable share tracks DUKES to within 0.1–0.3 points from 2016 to 2021 (2016:
  24.6 against DUKES 24.5; 2018: 33.0 against 33.0). From 2022 it drifts (2025: 55.0 against 52.1).
  That looks like an older vintage plus a projected 2025. Its coal (0.1% in 2025) is impossible on
  the FMD basis, which shows 4.7%.
- `company/regulatory/carbon_emissions.py::UK_GRID_FUEL_MIX` was **neither**. It is whole-number
  shares with a 3–8% imports bucket, which no generation mix carries. Its `Low Carbon %` was 3.3
  points above DUKES in 2019 and 3.7 above in 2025.

## 3. The figures, as fetched

**Generation, DUKES 5.6.C**, "All generating companies", `DUKES_5.6.xlsx`
(https://assets.publishing.service.gov.uk/media/688a31dda11f859994409290/DUKES_5.6.xlsx). Published
**Thursday 30 July 2026**, with new data for 2025. Revisions period 2017–2024. Fetched 2026-10-19.

The buckets are mapped as follows:
- wind = onshore + offshore;
- biomass = thermal renewables (DUKES note 9, "bioenergy");
- other = oil + other fuels + energy storage;
- imports = 0, because this is a generation basis.

DUKES' own "Total wind" row reads 11.91% for 2016 against onshore plus offshore at 10.96%. Note 11
says it includes shoreline wave and tidal. Only the onshore-plus-offshore figure reproduces DUKES'
published renewable share for 2016 (24.47%), so that is the figure used. Each year's renewable
buckets sum to DUKES' own "Renewable generation share" row within 0.02 points.

**Disclosure, DESNZ Fuel mix disclosure data table**, section "UK fuel mix … (for comparison,
including estimate for imports)". GOV.UK overwrites the page each year, so the earlier editions were
read from the Internet Archive's captures of
`gov.uk/government/publications/fuel-mix-disclosure-data-table/fuel-mix-disclosure-data-table`:

| Period | Capture | Coal | Gas | Nuclear | Renewables | Other |
|---|---|---|---|---|---|---|
| 2019/20 | 2020-11-22 | 3.9 | 39.4 | 16.6 | 37.9 | 2.2 |
| 2020/21 | 2022-01-03 | 2.7 | 38.2 | 16.1 | 40.3 | 2.7 |
| 2021/22 | 2023-02-24 | 3.8 | 38.5 | 16.1 | 38.7 | 2.9 |
| 2022/23 | 2024-02-04 | 3.4 | 39.3 | 13.9 | 40.8 | 2.6 |
| 2023/24 | 2024-09-28 | 6.3 | 35.0 | 12.7 | 43.2 | 2.8 |
| 2024/25 | 2025-10-07 | 5.9 | 33.3 | 16.2 | 42.1 | 2.5 |
| 2025/26 | live, updated 2026-08-03 | 4.7 | 31.4 | 13.7 | 48.0 | 2.2 |

**GAP: the 2016/17, 2017/18 and 2018/19 editions.** The current GOV.UK publication was first
published 2020-08-03. One search found the 2018 methodology note and Ofgem's letters, but not the
tables. The code carries these periods as absent, and the report says so. It does not borrow the
generation mix to fill them, because that is the other fact.

The block below is the one copy of the fetched figures.
`tests/company/regulatory/test_the_two_fuel_mixes_are_their_published_sources.py` asserts that both
code tables equal it, so an edit to either table without an edit here goes red.

```fuel-mix-sources
generation_dukes_5_6_c:
  # year: [coal, gas, nuclear, wind, solar, hydro, biomass, other]  (percent of UK generation)
  2016: [9.04, 42.27, 21.15, 10.96, 3.06, 1.58, 8.86, 3.07]
  2017: [6.66, 40.43, 20.8, 14.67, 3.39, 1.74, 9.43, 2.87]
  2018: [5.04, 39.4, 19.49, 17.05, 3.8, 1.63, 10.52, 3.07]
  2019: [2.11, 40.68, 17.17, 19.51, 3.8, 1.81, 11.47, 3.44]
  2020: [1.84, 36.06, 16.19, 24.37, 4.04, 2.22, 12.43, 2.85]
  2021: [2.2, 39.9, 14.97, 21.09, 3.94, 1.76, 12.99, 3.15]
  2022: [1.83, 38.74, 14.59, 24.7, 4.31, 1.56, 11.07, 3.2]
  2023: [1.24, 34.57, 13.8, 28.13, 5.06, 1.91, 11.59, 3.69]
  2024: [0.71, 30.56, 14.19, 29.23, 5.24, 2.0, 14.03, 4.03]
  2025: [0.0, 31.75, 12.21, 29.44, 6.86, 1.83, 13.98, 3.92]
dukes_renewable_generation_share:
  # DUKES 5.6.C's own "Renewable generation share" row, the check on the mapping above
  2016: 24.47
  2017: 29.24
  2018: 32.99
  2019: 36.59
  2020: 43.06
  2021: 39.78
  2022: 41.63
  2023: 46.69
  2024: 50.51
  2025: 52.11
disclosure_fmd_uk_mix:
  # period start year (1 April that year to 31 March the next): [coal, gas, nuclear, renewable, other]
  2019: [3.9, 39.4, 16.6, 37.9, 2.2]
  2020: [2.7, 38.2, 16.1, 40.3, 2.7]
  2021: [3.8, 38.5, 16.1, 38.7, 2.9]
  2022: [3.4, 39.3, 13.9, 40.8, 2.6]
  2023: [6.3, 35.0, 12.7, 43.2, 2.8]
  2024: [5.9, 33.3, 16.2, 42.1, 2.5]
  2025: [4.7, 31.4, 13.7, 48.0, 2.2]
```

## 4. What the two now say, side by side

Low carbon = renewables (including bioenergy) + nuclear on both bases, as the code computes it (generation from the two-decimal buckets above):

| Year | Generation (DUKES, calendar) | Disclosure (FMD, Apr–Mar from that year) | Gap |
|---|---|---|---|
| 2019 | 53.7 | 54.5 | −0.8 |
| 2020 | 59.2 | 56.4 | +2.8 |
| 2021 | 54.8 | 54.8 | 0.0 |
| 2022 | 56.3 | 54.7 | +1.6 |
| 2023 | 60.5 | 55.9 | +4.6 |
| 2024 | 64.7 | 58.3 | +6.4 |
| 2025 | 64.3 | 61.7 | +2.6 |

From 2022 the disclosure basis sits below generation. That fits imports rising (DESNZ: about 32% of
the European Attribute Mix is coal) and a low-carbon UK grid being diluted by them. **GAP: no
published decomposition of the gap** into imports, period offset and attribute allocation was found.
The direction is stated as consistent with the record, not measured.

## 5. Design choices (K8)

1. **Both series stay. Each has one home and one source.** The generation mix lives in
   `UK_GRID_FUEL_MIX`, rendered by the Observatory. The FMD UK mix lives in `_FUEL_MIX_BY_YEAR`,
   rendered by the FMD section and the customer portal. Retiring one would have left a section
   publishing the wrong quantity under its heading.
2. **The reconciliation note changes from "unreconciled, at most one is right" to "two defined
   quantities".** It is still derived from both tables at render time, and it names each basis and
   vintage.
3. **Absent FMD periods are absent.** `get_fuel_mix` used to clamp a year outside the table to the
   nearest year. It now returns `None` for a period with no fetched edition, and the report prints
   the gap.
4. **Generation-basis `imports_pct` is 0, and oil/other/storage go in a new `other_pct`.** The mix
   has no level role: national intensity is NESO's series (`grid_intensity_g_co2e_per_kwh`), and the
   lifecycle factors are not applied to this table.
5. **What moves on the published report** is a correction to sourced figures, said beside the claim:
   - The Observatory's `Low Carbon %` moves by up to 3.7 points (2025: 68 → 64).
   - The FMD section's 2016–2018 rows become a stated gap.
   - Its 2019–2025 low-carbon figures fall by up to 7.2 points (2024: 65.5 → 58.3), because they
     were never the disclosure basis.
   - "Renewable majority first achieved" no longer fires. On the supply basis renewables peak at
     48.0% (2025/26).
