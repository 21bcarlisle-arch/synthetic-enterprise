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

---

# DISCHARGED 2026-08-14 — option 1, reconciled to one series with a class control

Drawn by RUNG 1c (OPS12 clause 3) as the live BLOCKING finding in `F_risk_compliance`. Discharged by
**option 1** (reconcile to a single sourced series with one owner, delete the other two, plus a
control that fails if a second reappears), not option 2. Option 2 was not taken because it required
the director only if a *value* had to be chosen — and it did not, see below.

## The repair changed no published value, deliberately

The finding refused to name a true value (no network that tick, no source fetched). A repair that
picked a winner on the merits would have asserted exactly the claim the finding declined to make. So
the surviving series is the **published construction**, and all ten published figures are identical
across the move — pinned test-side in
`tests/company/regulatory/test_carbon_emissions_single_series.py::test_the_published_value_is_unchanged_by_the_reconciliation`
against the table measured at the top of this document.

The published construction survived on three grounds that are independent of which series is right:

1. It is the only one with a consumer. The other two had **zero renderers between them**, so keeping
   either would have silently revalued a published table.
2. It is **derived** (mix x factor, both visible) rather than an opaque literal. EP13 replaces the
   mix side with a real feed; it cannot replace a bare number it cannot decompose.
3. Its basis is at least statable: lifecycle factors x annual generation mix. Recorded in
   `GRID_INTENSITY_PROVENANCE`, R9-labelled — the factor citation is `inferred` and unverified, and
   the module says so rather than implying a source it never fetched.

## What changed

| file | change |
|---|---|
| `company/regulatory/carbon_emissions.py` | **SOLE OWNER.** `UK_GRID_FUEL_MIX` (moved verbatim out of the annual report's function body), `grid_intensity_g_co2e_per_kwh()`, `grid_intensity_is_extrapolated()`, `GAS_EMISSION_FACTOR_G_CO2E_PER_KWH`, `GRID_INTENSITY_PROVENANCE` |
| `company/billing/carbon_footprint.py` | `_ELECTRICITY_INTENSITY_G_CO2E_PER_KWH` **deleted**; `electricity_intensity()` delegates. Gas 0.18316 collapsed to the published 0.183 |
| `company/sustainability/carbon_intensity_register.py` | `_GRID_AVERAGE_INTENSITY` **deleted**; `vs_grid_average` delegates. Docstring's dead DESNZ citation replaced with what is actually true |
| `saas/reporting/annual_report.py` | the local `_UK_FUEL_MIX` / `_GAS_G_PER_KWH` **deleted**; imports the owner |
| `tools/grid_intensity_guard.py` | **new** — the R10 class control, three arms, ratchet, fails rc=2 on a coverage hole |
| `tools/pre_commit_test_gate.py` | control registered in `CONTROL_TESTS` — runs on every code commit, not only when the guard is edited |

## R15 — the control is proved both ways

`tests/tools/test_grid_intensity_guard.py`, 22 tests, 1.6s. The strongest is not synthetic:
`test_it_catches_all_three_real_deleted_series` runs the arms over the three tables **exactly as
they stood before this repair** and gets three hits, one per arm — including the copy that hid as a
local inside `_section_carbon_emissions`, which a module-scope scan would have missed. Confirmed
independently against a `git archive HEAD` of the pre-repair tree: 3 hits, 0 after.

It is also proved NOT to fire: a year-keyed table of standing charges, a two-year table, a per-fuel
dict keyed by fuel name, and a `sim/` generation-factor table are all left alone. And it fails
**rc=2, never rc=0**, when it loses its subject — owner missing, owner no longer declaring the
series, scanned package absent, or a module that will not parse (R15 killers 2 and 3).

## Also fixed in the same section, and it was not in the original finding

`saas/reporting/annual_report.py:5465` closed the published table with a **hardcoded sentence that
contradicted the table directly above it**: *"2016 ~290g/kWh -> 2025 ~175g/kWh (40% reduction)"*
against a 2016 row reading **315g/kWh** and an actual fall of **44%** (290 is the 2017 value). A
prose summary that is not computed from the table it summarises is the same defect one layer up — a
fourth copy of the series, in English. Now derived, and pinned by
`test_the_sections_closing_sentence_agrees_with_its_own_table`.

**R11, stated precisely:** the code is correct and the pin is green, but `docs/reports/ANNUAL_REPORT.md`
still carries the old sentence on disk. The report regenerates from a simulation run
(`tools/run_annual_report.py`), so the rendered surface updates on the next run rather than in this
tick. The ten `Grid Intensity` values in the published table are unchanged and need no regeneration.

## What is NOT closed, and is filed rather than implied

`WORKER_FINDING_TWO_PUBLISHED_FUEL_MIX_TABLES_DISAGREE_ON_LOW_CARBON_2026-08-14.md` (**BLOCKING**,
same lane). Measuring the residue found a fourth published table —
`company/billing/fuel_mix.py::_FUEL_MIX_BY_YEAR`, which renders the report's *other* fuel-mix
section — and the two sections publish a `Low Carbon %` column for the same years differing by up to
**3.4pp**, with the sign flipping. Reconciling it revalues a published table, which needs a source
this tick did not have. It is carried as the guard's single ratchet entry, so it is named and cannot
grow. That finding also records the per-fuel factor residue (hydro 6x apart across three surviving
tables) and the remaining single-scalar gas/grid factors.

**Evidence:** 1,688 tests pass across `tests/company/regulatory/`, `tests/company/sustainability/`,
`tests/company/billing/test_carbon_footprint.py`, `tests/company/test_phase_ol_carbon_emissions.py`
and `tests/tools/test_grid_intensity_guard.py`; 910 in `tests/saas/reporting/`; 535 across the
carbon/report `-k` selection. `python3 -m tools.epistemic_verifier` PASS.

## One record owed, and why it was not written in this tick

The discharge is **not** appended to `docs/design/simplifications/EP13_adapter_carbon_intensity.yaml`.
Writing it there is a two-file atomic change — the store file plus the atom's
`simplifications_count` in `docs/design/maturity_map.yaml` — and the map currently carries **another
lane's 676-line `notes_rehomed` change staged in the shared index**, so a pathspec commit of the map
would sweep their in-flight work into this commit.

`tests/design/test_simplifications_store.py::test_counts_match_file_contents` is **already red at
HEAD** for this atom independently of anything here (`map simplifications_count=None != store file
count=1`, verified against `git show HEAD:` for both files), so appending would have deepened a
pre-existing red rather than created one. Not touching the store surface also keeps
`STORE_CONTRACT_TESTS` out of this commit's gate selection, which is the honest reason as well as
the convenient one — stated so it is not mistaken for the whole story.

**Owed:** append the discharge note and the two new evidence paths
(`docs/staging/done/WORKER_FINDING_THREE_LIVE_GRID_INTENSITY_SERIES_DISAGREE_BY_HALF_2026-08-14.md`,
`tools/grid_intensity_guard.py`) to the atom store, and set the map's `simplifications_count`, once
the rehoming lane has landed. The discharge itself is recorded in
`docs/design/EP13_CARBON_INTENSITY_DISCOVER_FRAME.md` §1 and §7 in the meantime, which is the
document the atom's `evidence` already points at.
