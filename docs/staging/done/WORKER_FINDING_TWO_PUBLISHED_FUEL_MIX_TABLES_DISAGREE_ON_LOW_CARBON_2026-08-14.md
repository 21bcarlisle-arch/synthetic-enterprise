# [WORKER-FINDING] The annual report publishes `Low Carbon %` twice for the same years, from two different tables, and the two disagree by up to 3.4pp (2026-08-14)

**Severity:** BLOCKING · **Lane:** F_risk_compliance · **Status:** DISCHARGED 2026-08-14 by clause 2
— the limitation is now stated in the report itself, under BOTH tables, derived from both at render
time. No published figure was revalued; the two tables still disagree and the ratchet entry stands.

**Discharged:** `tests/company/regulatory/test_fuel_mix_reconciliation.py::test_both_sections_carry_it`,
`tests/company/regulatory/test_fuel_mix_reconciliation.py::test_the_note_is_read_from_the_tables_not_narrated`,
`tests/company/regulatory/test_fuel_mix_reconciliation.py::test_making_the_tables_agree_silences_the_note`

— found while discharging
`WORKER_FINDING_THREE_LIVE_GRID_INTENSITY_SERIES_DISAGREE_BY_HALF_2026-08-14.md`, whose §"the three
sources" already named this table as "a fourth, partly-redundant artefact" without measuring it.
Measured now.

**Why BLOCKING and not LATENT.** The ruling's test is "a published figure may be wrong." Both
columns are *rendered*, in the *same document*, under the *same metric name*, for the *same years*.
At most one is right. Grading it LATENT because the sibling finding just closed and the lane would
re-block is the anti-pattern `background/finding_severity.py` names in its own docstring; it is
graded on the definition.

## The measurement

`observed-with-evidence`, at HEAD, by executing the shipped code and by reading the published
markdown. `Low Carbon %` = renewable + nuclear (+ biomass, in the eight-bucket table only).

| year | Carbon Emissions Reporting Observatory (`ANNUAL_REPORT.md:2159`) | UK Grid Fuel Mix Disclosure (`ANNUAL_REPORT.md:1214`) | diff (pp) |
|---|---|---|---|
| 2016 | 45% | 45.5% | 0.5 |
| 2017 | 49% | 49.7% | 0.7 |
| 2018 | 51% | 52.3% | 1.3 |
| 2019 | 57% | 54.3% | **2.7** |
| 2020 | 59% | 58.9% | 0.1 |
| 2021 | 56% | 54.3% | 1.7 |
| 2022 | 57% | 55.0% | 2.0 |
| 2023 | 59% | 62.4% | **3.4** |
| 2024 | 64% | 65.5% | 1.5 |
| 2025 | 68% | 68.5% | 0.5 |

**The sign flips.** 2019 and 2021–22 have the Observatory *higher*; 2018, 2023–24 have the
Disclosure higher. A constant offset would be one definitional difference stated once. An
alternating one is two independently maintained tables.

The underlying mixes disagree too, on buckets that are not definitional at all:

* **gas**: max 2.8pp apart (2020 — 33.0% vs 35.8%)
* **nuclear**: max 2.5pp apart (2021 — 17.0% vs 14.5%)
* **coal**: max 0.8pp apart (2020 — 1.0% vs 1.8%)
* **renewable including biomass**: max 2.8pp apart (2023 — 45.0% vs 47.8%)

Both sum to exactly 100.0% in all ten years, so neither is a partial mix; they are two whole,
different claims about the same national grid.

## The two tables

* **`company/regulatory/carbon_emissions.py::UK_GRID_FUEL_MIX`** — eight buckets (coal, gas,
  nuclear, wind, solar, hydro, biomass, imports). Renders the **Carbon Emissions Reporting
  Observatory**, both its `Low Carbon %` column and (via the per-fuel factors) its `Grid Intensity`
  column. Became the single owner of the annual intensity series on 2026-08-14.
* **`company/billing/fuel_mix.py::_FUEL_MIX_BY_YEAR`** — five buckets (renewable, nuclear, gas,
  coal, other). Renders the **UK Grid Fuel Mix Disclosure** section via
  `saas/reporting/annual_report.py::_section_fuel_mix_disclosure` → `get_fuel_mix`. Docstring cites
  *"UK DESNZ Fuel Mix Disclosure, published annually"*; the other cites *"DESNZ/National Grid annual
  fuel mix data"*. Same cited publisher, no vintage on either.

The five-bucket figures carry one decimal place and move by fractions of a point year to year; the
eight-bucket ones are whole numbers. That is consistent with — but does not establish — the
five-bucket table being the transcribed series and the eight-bucket one a rounded reconstruction.
**No claim is made about which is correct**: this tick had no network and fetched no external
source, so naming a true value would be fabricating one.

## What is already mechanised

`tools/grid_intensity_guard.py` (landed 2026-08-14 with the sibling discharge) detects this table —
ARM 3, added specifically because arms 1 and 2 both missed a year-keyed table of *nested dicts*. It
is carried as the single entry in `KNOWN_SECOND_SERIES`, a ratchet that:

* fails the build if a **second** exemption is added without editing the guard,
* fails the build if this entry ever **stops** violating (`test_the_ratchet_has_no_stale_entries`),
  so fixing the instance forces deleting the entry rather than leaving a permanent hole.

So the class is closed and this instance is *named*, not hidden. What is owed is the reconciliation
itself.

## What discharges it

One of:

1. **Reconcile to one sourced mix**, cited to a named publication and vintage, with the other
   section deriving its columns from it — and the eight-bucket/five-bucket bucketing stated as a
   *view* rather than a second table. Then delete the `KNOWN_SECOND_SERIES` entry (the ratchet test
   will require it).
2. **Record and accept the limitation explicitly**, stating in the report itself that the two
   sections use different mix vintages and are not expected to agree.

Either way it revalues a published table, so it is a decision about what the company is willing to
publish — stated for the director rather than taken here, for the same reason the sibling finding's
repair deliberately changed no published value.

## What was actually done (2026-08-14, same-day discharge)

**Clause 2 was taken, and clause 1 was not.** Clause 1 needs a fetched source; this tick had no
network either, so picking a winner would have been the fabrication the finding refused. Clause 2
is reversible, changes no figure, and puts the disclosure where the misled reader actually is.
Recommended and taken rather than asked (`NEVER_ASK_WITHOUT_RECOMMENDING`) — revaluing nothing, it
is not one of the four reserved classes; `git revert` undoes it.

* `company/regulatory/fuel_mix_reconciliation.py` — a reconciliation **view**, not a third table.
  It reads both owners at call time and renders the disclosure paragraph. Every figure in the
  sentence is derived: edit either table and the published sentence moves with it; make them agree
  and it disappears. A note carrying a hardcoded "3.4pp" would have been a third copy of the same
  disagreement, false the first time either table moved.
* Both `_section_carbon_emissions` and `_section_fuel_mix_disclosure` in
  `saas/reporting/annual_report.py` now carry it — a reader who lands on only one of the two tables
  is the reader being misled, so one note would not have been a disclosure.
* `docs/reports/ANNUAL_REPORT.md` regenerated (R11). The diff is 5 lines: the two notes, plus the
  intensity summary correcting itself from `2016 ~290g/kWh -> 2025 ~175g/kWh (40% reduction)` to
  `2016 315g/kWh -> 2025 175g/kWh (44% reduction)`. **That second change is not this repair's** —
  it is the sibling finding's derive-don't-narrate fix, which landed in code earlier the same day
  while the published artefact was never regenerated. R2's shape on a document: committed was not
  published, and the stale prose sat under a table it contradicted until this regeneration.
* R15, both mutations run and restored: dropping the `divergence_note` call from the Observatory
  section turns `test_both_sections_carry_it` red; replacing the derived figures with the literal
  `3.4pp`/`2023` turns `test_the_note_is_read_from_the_tables_not_narrated` red. The control fires
  on its own named defect in both directions.
* `tests/company/regulatory/test_carbon_emissions_single_series.py` — one repair not in scope but
  forced by it: `test_the_sections_closing_sentence_agrees_with_its_own_table` located its subject
  as `splitlines()[-1]`. Appending the disclosure below the summary turned it red without touching
  the sentence it is about — a harness convenience that had quietly made "the last line" the
  control's subject. Now located by content.

**What is NOT discharged.** The two tables still disagree; the `KNOWN_SECOND_SERIES` ratchet entry
in `tools/grid_intensity_guard.py` therefore stays, and `test_the_ratchet_has_no_stale_entries`
still forces its deletion on a real reconciliation. `EP13_adapter_carbon_intensity` still owns
sourcing it. The per-fuel factor residue in the section below remains recorded, not drawn.

`EP13_adapter_carbon_intensity` is the atom that eventually sources this properly; it is epoch-3
parked and cannot do it now (`docs/design/EP13_CARBON_INTENSITY_DISCOVER_FRAME.md` §7 step 1).

## Also measured in the same sweep, recorded not drawn

The **per-fuel factor** tables are a separate and larger residue — three of them survive, and they
are further apart than the annual series ever was:

| fuel | `carbon_emissions._EMISSION_FACTORS_G_CO2_PER_KWH` | `carbon_intensity_register._CARBON_INTENSITY_G_CO2_PER_KWH` | `fuel_mix_disclosure._CARBON_INTENSITY` |
|---|---|---|---|
| gas | 490.0 | 394.0 | 394.0 (CCGT) / 610.0 (OCGT) |
| biomass | 230.0 | 230.0 | 120.0 |
| hydro | 24.0 | 24.0 | 4.0 |
| solar | 41.0 | 41.0 | 33.0 |
| wind | 11.0 | 11.0 / 12.0 | 7.0 / 9.0 |

Hydro differs by **6x**, biomass by 92%, gas by 24%. The register's own table is internally
mixed-basis — a direct-combustion gas figure (394.0) beside lifecycle values for nuclear (12.0) and
wind (11.0). Neither the register nor the disclosure module has a renderer, so nothing published
depends on them today, which is why this half is recorded rather than drawn (SELF_INTERRUPT
discipline — the supply is infinite).

**Single-scalar factors**, same shape, after the sibling discharge collapsed two of four:

* `carbon_emissions.GAS_EMISSION_FACTOR_G_CO2E_PER_KWH` = 183.0 g/kWh — **published**, single owner
* `company/sustainability/environmental_impact.py:32 _GAS_EMISSION_FACTOR` = 0.18253 kg/kWh
* `background/fabric_gap_ledger.py:3235 CARBON_KG_PER_KWH["gas"]` = 0.183 kg/kWh
* `company/sustainability/environmental_impact.py:33 _GRID_ELECTRICITY_FACTOR` = 0.2104 kg/kWh
  ("UK national grid 2023 location-based") — 210.4 g/kWh against the owned series' 219.3 for 2023,
  4.1% apart. This one may be legitimately different: location-based corporate Scope 2 is not the
  same quantity as supplied-electricity lifecycle intensity. It is listed so the difference is a
  stated basis rather than an accident.
* `background/fabric_gap_ledger.py:3235 CARBON_KG_PER_KWH["electricity"]` = 0.207 kg/kWh, carrying
  no year at all.

`sim/merit_order_reconstruction.py` and `sim/price_engine.py` carry generation factors too. They are
**deliberately out of scope**: world physics on the far side of the epistemic wall, a different
quantity, and folding them into a company-side owner would be a breach rather than a reconciliation.
`tools/grid_intensity_guard.py` does not scan `sim/` or `simulation/` for exactly that reason, and
says so in its docstring.
