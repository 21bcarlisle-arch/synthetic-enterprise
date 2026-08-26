# EP13 — Carbon from the actual grid, half-hour by half-hour: DISCOVER + FRAME

**Atom:** `EP13_adapter_carbon_intensity` · lane `W4_the_wall` · epoch 3 · level 0 → 3 · `loop_stage: idle`
**Draw:** 2026-08-14 worker tick, LANE 3 (DISCOVER/FRAME only). **No BUILD code written** — the atom is
epoch-gated (`block_reason`: director-reserved curriculum sequencing, R13), and EPOCH_GATING_AND_ATOM_AUTHORSHIP
Rule 1 permits DISCOVER/FRAME on a parked atom and forbids BUILD.
**Level:** HELD at 0. EP13's deliverable is an **adapter**; this document is *about* it, which is the
`EP10_adapter_uk_link_xoserve` call, not the `EP19_counterparty_qualification_paths` one (where the
register **was** the deliverable). `docs/design/maturity_map.yaml` also carries another lane's staged
`level_current` hunk in the shared index — no map edit from this tick either.
**No network this tick.** Every claim below is `observed-with-evidence` against disk at HEAD unless
marked `[verify-at-BUILD]`. Nothing about the live API's current behaviour is asserted from memory.

---

## 0. What the atom says it is, and what it turns out to be

The atom's `gain` is one sentence: *"The carbon ledger gets ground truth from day one instead of a
factor table."*

**There is no factor table. There are three, they disagree by up to 55.6%, and the one an adapter
would naturally feed is the one nothing reads.** That is the finding this pass turns on, and it
changes what the first EP13 move is: not *fetch*, but *choose which consumer you are replacing.*

The second thing the atom's own text gets wrong is smaller and sharper. Its `name:` says *"Regional
intensity multiplied by half-hourly usage is the abatement ledger's ground truth."* That product is
**emissions**, not abatement. `ADVISOR_SCOPE_BRIEF_CARBON_2026-08-04.md` §A says it plainly: of the
three quantities — emissions, abatement, £/tonne — *"only the first is observable"*, and abatement is
a counterfactual. EP13 can supply ground truth to the **emissions** ledger. It cannot, even in
principle, supply it to the abatement ledger, because no feed can observe the world that did not
happen. That is not a reason to shrink the atom; it is the difference between an achievable L3 and
one whose exit criterion can never be met.

---

## 1. DISCOVER — the factor table is three tables, and the published one is the highest

Three annual national grid-intensity series live at HEAD. All three cite DESNZ. Computed this tick by
executing the shipped code, not by reading it:

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

Sources, and their reach:

* **`saas/reporting/annual_report.py:5414`** — `_UK_FUEL_MIX`, ten `FuelMixRecord`s declared **inside
  the function body** of `_section_carbon_emissions`, blended through
  `carbon_emissions.FuelMixRecord.emission_intensity_g_per_kwh`. **This is the published one.**
  `docs/reports/ANNUAL_REPORT.md:2159` "Carbon Emissions Reporting Observatory" renders it: a
  `Grid Intensity` column reading `315g/kWh` (2016) → `175g/kWh` (2025), and an `Elec CO2 (t)` column
  derived from it.
* **`company/billing/carbon_footprint.py:14`** — `_ELECTRICITY_INTENSITY_G_CO2E_PER_KWH`, the lowest
  series. Its only non-test importer is `company/portal/app.py:35`, which imports `estimate_carbon`
  **and never calls it** (one occurrence in the file, the import line). `tools/generate_saas_coverage_data.py:55`
  names the module in a coverage-taxonomy string, not a value. So **nothing renders this series.**
* **`company/sustainability/carbon_intensity_register.py:57`** — `_GRID_AVERAGE_INTENSITY`, the
  highest. **Zero non-test importers.** This is the module EP13's title points at, and it is the one
  with no consumer at all.

There is also a fourth, partly-redundant table: `company/billing/fuel_mix.py::get_fuel_mix` returns a
five-bucket mix (`renewable/nuclear/gas/coal/other`) which the annual report does **not** use for this
section — it declares its own eight-bucket copy instead. Two fuel-mix tables, one blended series.

**Consequence for EP13.** Wiring a half-hourly feed into `carbon_intensity_register` changes no
published number whatsoever — it would be the twelfth module in a stack of eleven that nothing calls,
the `EP10` §1 shape in a different costume. The only wiring that can move a level under R11 is into
the annual report's path, and that path currently reads a table declared inside a function.

Staged separately as its own finding, because it is a **published** figure and outlives this atom:
`WORKER_FINDING_THREE_LIVE_GRID_INTENSITY_SERIES_DISAGREE_BY_HALF_2026-08-14.md`.

> **DISCHARGED 2026-08-14** (option 1), on a RUNG 1c blocking-finding draw — now at
> `docs/staging/done/`. The three series are one: sole owner
> `company/regulatory/carbon_emissions.py::grid_intensity_g_co2e_per_kwh`, class control
> `tools/grid_intensity_guard.py` in the gate's `CONTROL_TESTS`. **No published value changed** —
> the surviving series is the published construction, because the finding named no true value and a
> repair that picked one would have asserted the claim the finding declined to make. §7 step 1 below
> is therefore complete, and **EP13 now has the single consumer it was waiting for**. A successor
> finding is live in the same lane:
> `WORKER_FINDING_TWO_PUBLISHED_FUEL_MIX_TABLES_DISAGREE_ON_LOW_CARBON_2026-08-14.md` — the report's
> two sections publish `Low Carbon %` for the same years 3.4pp apart.

*(Observed in passing, recorded not fixed: the same report section derives electricity volume as
`elec_mwh = rev / 150_000.0` — a hardcoded £150/MWh divisor — giving 0–28 MWh a year for the whole
book. The intensity column is the smaller error of the two. Queued per SELF_INTERRUPT, not drawn.)*

## 2. DISCOVER — supplying only the average series decides a director values-call by omission

The Carbon Intensity API publishes an **average** intensity: generation-weighted, loss-corrected
(`ADVISOR_SCOPE_BRIEF_CARBON` §B — *"corrected for losses… do not apply a further loss adjustment"*).

`E5_carbon_three_ledger` has **"grid marginal vs average"** on its open list of six **director
values-calls** — surfaced twice (`2026-07-20` DISCOVER, `2026-07-29` FRAME) and decided neither time.

The world can already produce the other side. `sim/merit_order_reconstruction.py` carries
`EF_GAS_TCO2_PER_MWH_E_BY_YEAR` (line 134) and `EF_COAL_TCO2_PER_MWH_E_BY_YEAR` (line 138), and
computes which plant sets the price per settlement period. A **marginal** intensity series is nearly
free from machinery that is already wired and live.

So an adapter that lands the average series alone does not leave the values-call open — it answers it
by being the only series available. That is the R13 shape exactly: the agent sits on both sides of the
wall, so a choice with a values dimension must face the director rather than be settled by what was
convenient to build. **EP13 must emit its rows with `basis` on them and must not be the sole supplier
of a basis.**

The two bases also answer different questions, which is why this is not pedantry:

* *What did this household's consumption represent?* → **average**. The emissions ledger.
* *What does moving a kWh from 18:00 to 03:00 avoid?* → **marginal**. The abatement question, and the
  entire justification for time-shifting advice.

## 3. DISCOVER — the regional join key exists, in the right vocabulary, on the wrong side of the wall

The atom's value is *regional* intensity. The join needs a region per customer.

* **The vocabulary exists and matches.** `simulation/adoption_geography.py:360` declares
  `_GB_REGIONS`, commented verbatim *"14 GB GSP/DNO areas"* — `north_scotland`, `south_scotland`,
  `north_east_england`, `north_west_england`, `yorkshire`, `north_wales_mersey`, `south_wales`,
  `east_midlands`, `west_midlands`, `eastern_england`, `london`, `southern_england`,
  `south_east_england`, `south_west_england`. That is the same geography the API's regional series
  uses `[verify-at-BUILD: confirm the API's `regionid` ordering and its national/England/Scotland/Wales
  extras before mapping]`.
* **It is world-side.** `adoption_geography` is imported by `simulation/population_draw.py` and by its
  own test. Nothing under `company/` imports it, and it must not — it is a world internal.
* **The company's own field is declared and never written.** `company/billing/meter_points.py:42`
  carries `gsp_group: str | None = None  # GSP group code e.g. "_A" to "_P"`. `grep` for `gsp_group`
  across the repo returns **that one line and nothing else** — no producer, no consumer. And
  `meter_points` itself has no non-test importers (already recorded in the EP10 pass).

**So the company has no region for any customer, and national intensity is the only joinable series
today.** The fix is small and wall-legal: a real supplier *does* know each supply point's GSP group —
it is in the supply-point record and derivable from the MPAN. It is an observable, not an internal, so
it may cross. What is forbidden is reading `_GB_REGIONS` from `company/`; what is required is the world
publishing the GSP group per supply point as an observable the company then holds itself.

## 4. DISCOVER — the multiplicand is two days of three customers

`docs/market_data/consumption_feed.json` is the company's half-hourly usage observable. Measured this
tick: **288 records = 3 customers (`C7`, `C8`, `C9`) × 2 dates (`2025-06-06`, `2025-06-07`) × 48
periods.** Keys: `customer_id / date / period / hour / kwh`.

Everything else is annual. `carbon_footprint.estimate_carbon(eac_kwh, commodity, year)` takes an
**EAC** — an annualised figure — which is why an annual intensity was the natural pairing.

**An annual kWh multiplied by a half-hourly intensity is not a valid product.** The half-hourly feed
only buys fidelity where a half-hourly multiplicand exists, and today that is 3 customers for 2 days.
This is the binding constraint on EP13's *value* — not API access, not EP6, not the values-calls. A
builder who lands a perfect ten-year half-hourly regional feed against an EAC book has bought a
rounding difference on an annual average and a much larger surface to be wrong on.

## 5. FRAME — the adapter's unit is `(period, as_of)`, not `(period)`

The atom's stated fidelity prize is the forecast/outturn split: *"the company acts on the FORECAST and
is settled against the ACTUAL, which is a belief-vs-truth gap available for free from a public API."*

This is genuinely different from EP10, and better. EP10's advertised gap had **no truth side** — the
world produced no gas residue to be wrong about. EP13's truth side is published by the counterparty,
so the gap needs no world change at all.

But the same endpoint that hands the company its forecast will hand it the outturn, and a *revised*
outturn later. Under the Point-in-Time Blindfold, an adapter whose signature is `intensity(period)` is
a leak: it cannot express "what was knowable on the morning of the 6th."

The existing OPEN-NOW adapters are no guide here, and it is worth naming why. `sim/generation_demand_history.py`
and `sim/system_prices_history.py` are historical-range fetchers with **no as-of dimension** — legal
precisely because they live in `sim/`, on the world side of the wall. EP13's output is a **company**
observable, so it needs the dimension they do not have.

**Design:** the adapter's row is `(period, as_of) → {value_g_co2_per_kwh, basis: forecast|outturn,
region, vintage, source}`. Forecast rows carry their publication time; outturn rows carry theirs; a
revision is a new row, never an overwrite. This is the same shape R14 already forces on money
(clock/basis/provenance) and that the E5 FRAME already specified for carbon (CLOCK × BASIS ×
PROVENANCE). **EP13 is where that triple originates, so it should emit it rather than have it
retrofitted** — the E5 FRAME already found that `three_ledger_view()` drops basis at aggregation, and
a feed that never carried one guarantees that outcome.

## 6. FRAME — coverage, and why the tables cannot simply be deleted

`[verify-at-BUILD, no network this tick]` The API's series is understood to begin some years after the
simulation window opens; `sim/generation_demand_history.py` names that window as starting `2016-01-01`.
If the feed cannot reach 2016, **the early years still need a factor table**, and EP13 is a partial
replacement rather than a deletion.

That makes the seam the design problem. A series that switches basis mid-window without saying so is
the anachronistic-factor risk the E5 FRAME already named against the 2.1× swing in
`_GRID_AVERAGE_INTENSITY`.

**Do not design a silent fallback.** A period the feed does not cover must read `no_source` and
propagate as such — never a factor-table value dressed as a feed. This is E5's specified control C1
(*absent-feed zero: status `ok`/`no_source`/`insufficient_data`, never `0.0`*) and it is the fail-open
family that CARBON_NOT_A_TARGET's mechanisation section calls out by name: an unavailable carbon
reading must fail loud, never read as great.

## 7. FRAME — the smallest closed loop, in order

1. ~~**Reconcile the three series to one.**~~ **DONE 2026-08-14** — one owner
   (`company/regulatory/carbon_emissions.py`), two literals deleted, class control landed
   (`tools/grid_intensity_guard.py`). The single consumer a feed can replace now exists, so this
   step no longer gates the rest. It did NOT settle which series is *right*: nothing was sourced,
   and the surviving construction is `PROVISIONAL` in `GRID_INTENSITY_PROVENANCE`. Sourcing is
   still EP13's, and the successor finding
   (`WORKER_FINDING_TWO_PUBLISHED_FUEL_MIX_TABLES_DISAGREE_ON_LOW_CARBON_2026-08-14.md`) is where
   the remaining published disagreement lives.
2. **Publish GSP group per supply point as an observable** in the `_GB_REGIONS` vocabulary, and write
   the already-declared `meter_points.gsp_group`. Cheap, wall-legal, and it is the join key every
   regional thing downstream needs. Independent of the API.
3. **The adapter.** `(period, as_of) → {value, basis, region, vintage, source}`, national first,
   `no_source` rather than a substitute, regional behind step 2.
4. **Wire it to the surviving consumer from step 1**, so the move changes a rendered number (R11).
   This is the only step that can move a level, and it is gated on step 1.
5. ~~**The gap.**~~ **DONE 2026-08-26** — `neso_carbon_intensity.forecast_skill()` grades NESO's
   own published forecast against NESO's own published outturn, as a distribution per year, and
   `published_forecast_skill` carries it into the feed. Both sides were already in the cache
   fetched on 2026-08-25 for the shape comparison; no fetch was needed. The headline is a
   **ceiling**: following the published forecast captures a mean 86% of a day's achievable
   within-day saving (median 91%, p5 55%, and 7 days of 2,165 worse than not shifting at all).
   Unlike the reconstruction's overstatement, no improvement to this model can recover it, so the
   honest reading of any timing figure here is *(this model's overstatement) × (what a forecast
   could actually pick)* — and that sentence now reaches the customer page, pinned to the
   measurement by test. The step's "distribution, not a mean" clause is the load-bearing one and
   is enforced (`MIN_DAYS_FOR_A_DISTRIBUTION`, and percentiles beside every mean).
   One finding about the counterparty rather than about us: NESO's published *forecast* field
   carries six half hours in 2019 that are not a grid (13,579 gCO₂/kWh among them), refused
   against the maximum of NESO's own per-fuel factor table rather than trimmed by percentile.
6. **Only then**, marginal intensity from `merit_order_reconstruction` as a *second* series — and that
   is §2's director values-call, surfaced here, not taken here.

**What does not block any of this:** API access (free, no key, `OPEN NOW`); `EP6_wall_protocol_typing`,
which the atom lists as its `depends_on` but which is not load-bearing — one scalar per period per
region crosses the existing `sim_interface` seam without a typed protocol; and the six open values-calls,
because steps 1–5 are basis-agnostic *provided* each row carries its own basis.

## 8. FRAME — R12 gets sharper here, not looser, and the existing guard's subject cannot express it

`CARBON_NOT_A_TARGET_CONSTRAINT.md` §2 bans a carbon metric feeding "reward, selection, priority, or
ranking… not a pricing/personalisation decision loop". It is enforced by
`tests/company/test_carbon_not_a_target.py`, whose detector (`_imports_company_carbon`, lines 25–41)
keys on the **import path**: `company.carbon.*`, or any module whose last segment is `carbon_ledger`.

EP13 creates the first legitimate case of a carbon number a decision surface **must** read: shifting
advice is worthless without the forecast intensity. The distinction that resolves it has to be designed
in, not argued afterwards:

* **Forecast intensity (gCO₂/kWh) is a market input** — the same category as a price. A decision
  surface reading it is doing what a real supplier does. **Legal.**
* **The ledger figure (tCO₂e abated, £/tCO₂e) is the diagnostic.** Unreadable by any decision surface.
  **The constraint is unchanged for it.**

A path-keyed guard cannot draw that line. Land the adapter under `company.carbon` and shifting advice
becomes illegal-or-untestable; land it anywhere else (`company/sustainability/`, say) and the guard
does not reach whatever ledger-shaped thing later joins it there — the wrong-subject failure this
project has filed repeatedly. **The subject should be the quantity (a tCO₂e- or £/tonne-typed value),
not the import path.** Recorded as an EP13 design requirement; not fixed this tick (SELF_INTERRUPT —
the guard is green against its current subject and nothing is blocked on it).

Note the direction of the risk the `origin_note` warns about is confirmed, not softened: a real
half-hourly feed makes a carbon number cheap to publish and therefore cheap to optimise toward. The
counter-design is §7.5 — publish the forecast-vs-outturn **distribution**, which widens under tuning,
rather than a scalar that improves under it.

---

## 9. What this pass changed

* This document.
* `docs/design/simplifications/EP13_adapter_carbon_intensity.yaml` — findings recorded, and the atom's
  own two `evidence` pointers repaired (both named `docs/staging/…` paths that no longer exist; the
  live paths are appended alongside, never rewritten — the store is append-only by design).
* One finding staged, not fixed:
  `WORKER_FINDING_THREE_LIVE_GRID_INTENSITY_SERIES_DISAGREE_BY_HALF_2026-08-14.md`
  (**BLOCKING** · `F_risk_compliance`) — §1 above. **Discharged the same day** on a separate RUNG 1c
  draw; the document (with its discharge record appended) is now in `docs/staging/done/`.

Nothing under `company/`, `simulation/`, `sim/` or `saas/` was touched. No level moved.
