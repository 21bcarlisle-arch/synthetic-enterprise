# [WORKER-FINDING] Three live grid-intensity series, all citing DESNZ, disagree by up to 55.6% — and the one the annual report publishes is the highest (2026-08-14)

**Severity:** BLOCKING · **Lane:** F_risk_compliance · **Status:** measured and reported, not fixed —
found on an `EP13_adapter_carbon_intensity` LANE 3 DISCOVER/FRAME draw, which forbids BUILD code
(EPOCH_GATING_AND_ATOM_AUTHORSHIP Rule 1). Full context:
`docs/design/EP13_CARBON_INTENSITY_DISCOVER_FRAME.md` §1.

**Why BLOCKING and not LATENT.** The ruling's own test is "a published figure may be wrong."
`docs/reports/ANNUAL_REPORT.md:2159` publishes a `Grid Intensity` column and an `Elec CO2 (t)` column
derived from it. Three series in this tree claim to measure the same quantity from the same cited
source and disagree by more than half; at most one of them is right, and the published one is not
obviously it. Grading this LATENT to keep the lane open is the exact anti-pattern
`background/finding_severity.py` names in its own docstring, so it is graded on the definition.

## The measurement

`observed-with-evidence`, at HEAD, computed this tick by **executing the shipped code** (not by reading
the literals — the published column is a blend, not a table lookup):

| year | annual report (**PUBLISHED**) | `carbon_footprint` | `carbon_intensity_register` | spread |
|---|---|---|---|---|
| 2016 | 315.4 | 266 | 350.0 | 31.6% |
| 2017 | 289.7 | 246 | 312.0 | 26.8% |
| 2018 | 273.8 | 233 | 283.0 | 21.5% |
| 2019 | 243.9 | 214 | 256.0 | 19.6% |
| 2020 | 225.3 | 181 | 228.0 | 26.0% |
| 2021 | 242.7 | 190 | 233.0 | 27.7% |
| 2022 | 237.0 | 165 | 210.0 | 43.6% |
| 2023 | 219.3 | 141 | 196.0 | 55.5% |
| 2024 | 196.1 | 126 | 181.0 | 55.6% |
| 2025 | 175.2 | 115 | 165.0 | 52.3% |

**The spread widens over time** — 19.6% in 2019, 55.6% in 2024 — so this is not a one-off transcription
slip. The three are decarbonising at different rates: 2016→2025 the published series falls 44%,
`carbon_footprint` 57%, `carbon_intensity_register` 53%.

## The three sources and what each one reaches

* **`saas/reporting/annual_report.py:5414` — `_UK_FUEL_MIX`.** Ten `FuelMixRecord`s declared **inside
  the function body** of `_section_carbon_emissions`, blended by
  `company/regulatory/carbon_emissions.py::FuelMixRecord.emission_intensity_g_per_kwh` (line 49)
  against `_EMISSION_FACTORS_G_CO2_PER_KWH` (line 10). **Published** —
  `docs/reports/ANNUAL_REPORT.md:2159` "Carbon Emissions Reporting Observatory", `315g/kWh` (2016)
  through `175g/kWh` (2025), with `Elec CO2 (t)` and a `**Total**` row derived from it. Header cites
  *"DESNZ/National Grid annual fuel mix data"*.
* **`company/billing/carbon_footprint.py:14` — `_ELECTRICITY_INTENSITY_G_CO2E_PER_KWH`.** Comment
  cites *"UK DESNZ grid intensity (annual averages)"*. The lowest series. Its only non-test importer
  is `company/portal/app.py:35`, which imports `estimate_carbon` and **never calls it** — one
  occurrence in the file, the import line itself. `tools/generate_saas_coverage_data.py:55` names the
  module in a coverage-taxonomy string, not a value. **Nothing renders this series.**
* **`company/sustainability/carbon_intensity_register.py:57` — `_GRID_AVERAGE_INTENSITY`.** Module
  docstring cites *"DESNZ (formerly BEIS) grid average intensity: ~196 gCO2/kWh 2023 (down from 350g
  2016)"*. The highest series. **Zero non-test importers.**

There is a fourth, partly-redundant artefact: `company/billing/fuel_mix.py::get_fuel_mix` returns a
five-bucket mix (`renewable/nuclear/gas/coal/other`); the annual report does **not** use it for this
section, declaring its own eight-bucket copy instead. Two fuel-mix tables feeding one report.

## What is *not* claimed

**No claim about which series is correct.** This tick had no network and no external source was
fetched, so naming a true value would be fabricating one. All three sit in a broadly plausible band;
the finding is that they are **mutually inconsistent and unreconciled**, which is falsifiable from
disk alone and is independent of which is right.

## What discharges it

One of:

1. **Reconcile to a single sourced series** with one owner, cited to a named publication and vintage,
   and delete the other two — with a control that fails if a second grid-intensity literal reappears
   (the class remedy, per R10: an instance fix does not close this).
2. **Record and accept the limitation explicitly** — the ruling's own escape hatch for a BLOCKING
   finding. That is a decision about what the company is willing to publish, so it is stated for the
   director rather than taken here.

`EP13_adapter_carbon_intensity` is the atom that eventually replaces the survivor with a real
half-hourly feed, but it **cannot** do this repair: EP13 is epoch-3 parked, and until there is one
consumer there is nothing for a feed to replace. Sequencing is in the FRAME doc §7.

## Also observed in the same section, recorded not drawn

`saas/reporting/annual_report.py:5445` derives electricity volume as `elec_mwh = rev / 150_000.0` — a
hardcoded £150/MWh divisor — producing 0–28 MWh per year for the entire book, and a decade total of
~30.8 tCO₂. The intensity column is the smaller of the two errors in the same published table. Queued
per SELF_INTERRUPT discipline (the supply is infinite), not fixed on sight.
