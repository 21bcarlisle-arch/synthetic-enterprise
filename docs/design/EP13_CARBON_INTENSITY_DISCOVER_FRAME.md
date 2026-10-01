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

---

## 10. 2026-08-27 — the ORACLE BOUND: perfect biomass knowledge is worth −0.005 of correlation

**The named next gap is refuted before it is built.** The map's own record, written 2026-08-26 at
the end of the must-run pass, said: *"The residual explains only 2.6-33.5% of biomass's variance —
a CfD plant runs on AVAILABILITY, so its low readings are outages. The next gap is an outage model,
not a tidier percentile."* That sentence is now wrong, and the arithmetic is below.

**Measurement, not a repair.** No constant changed, no wiring changed, no level moved.
`BIOMASS_DISPATCH_WIRED` is still `False` and the published feed is byte-for-byte the series it was.

### The method: measure the ceiling before building the approximation

An outage model is an *approximation to knowing what the biomass fleet was able to do in each half
hour*. So hand the dispatch that knowledge **exactly** — the metered half-hourly outturn, pinned
with `biomass_floor_mw == biomass_capacity_mw`, leaving the clamp in
`grid_carbon_intensity.emissions_rate_t_per_mwh` no freedom — and measure how far the gap to NESO's
published series closes. **Whatever the oracle cannot buy, no approximation to it can buy.**

That treatment may never be published, and that is the reason the bound is worth taking this way:
NESO prices biomass at 120 gCO2/kWh, so a metered biomass reading is an emissions term, and handing
it across the wall makes this NESO's arithmetic with a different cache. **An illegal treatment is
still a legitimate bound**, because a bound is a fact about what is *knowable* and not a route to a
number. `tools/ep13_biomass_oracle_bound.py::oracle_is_unreachable_from` keeps that structural — an
AST walk over the publishing module, not a promise — and the run publishes
`oracle_reaches_the_published_feed: false` beside its own results.

Three treatments, one process, identical caches: **flat** (2,400 MW every half hour — *the published
series*), **envelope** (the built-but-off annual demonstrated range), **oracle** (the metered outturn).

### Both controls held, and they are opposites

| control | what it refuses | measured |
|---|---|---|
| **route agreement** — `flat` must reproduce the shipped `build_shape` on every shape diagnostic | a comparison between two *codepaths* rather than two *treatments* | max abs diff **1.1e-16 to 1.8e-15** in every year |
| **oracle bite** — the treatment must actually move the rate | "perfect knowledge does not help" that is really "perfect knowledge was never applied" (R15 fail-silent) | **2.8–5.9%** mean rate change, **72–93%** of half hours moved, up to 29% in one |

Both are mutation-proven in `tests/tools/test_ep13_biomass_oracle_bound.py` — including the fixture
defect this project has been caught by before: a panel built *at* `MUST_RUN_BIOMASS_MW` cannot see
its own treatment, because at the fallback value the treated and untreated arithmetic are identical.

### The result

| year | corr flat | corr envelope | **corr ORACLE** | mae flat → oracle | within-day overstated flat → oracle | p95/p5 overstated flat → oracle |
|---|---|---|---|---|---|---|
| 2019 | 0.8826 | 0.8831 | **0.8740** | 0.1122 → 0.1103 | 1.478 → 1.438 | 1.389 → 1.328 |
| 2020 | 0.8687 | 0.8713 | **0.8668** | 0.1326 → 0.1321 | 1.457 → 1.470 | 1.158 → 1.221 |
| 2021 | 0.9088 | 0.9083 | **0.9102** | 0.1046 → 0.1005 | 1.403 → 1.384 | 1.262 → 1.246 |
| 2022 | 0.8707 | 0.8672 | **0.8778** | 0.1495 → 0.1412 | 1.538 → 1.533 | 1.133 → 1.208 |
| 2023 | 0.7952 | 0.7971 | **0.7879** | 0.2037 → 0.2069 | 1.469 → 1.468 | 1.571 → 1.848 |
| 2024 | 0.7456 | 0.7529 | **0.7255** | 0.2675 → 0.2764 | 1.352 → 1.354 | 1.753 → **2.040** |
| mean | 0.8453 | 0.8466 | **0.8403** | — | 1.4496 → 1.4409 | — |

**Correlation is the axis holding L3, and the oracle moves it the wrong way.** Worse in four years
of six, mean −0.0050, and **worst of all in 2024 (−0.0201)** — the year the level is held on, where
perfect knowledge undoes the whole of the must-run pass's 0.726 → 0.746 gain. Within-day
overstatement — the only axis a household can act on — moves 1.4496 → 1.4409, i.e. **0.6% of a 45%
error**. p95/p5 overstatement gets *worse* in four years of six and much worse in the two most
recent (1.753 → 2.040 in 2024). Every honest end is published: mean absolute error does improve, in
four years of six, and the envelope treatment beats the oracle on correlation in four of six.

### Why — and it is not that biomass is small

**70–86% of the biomass fleet's variation is BETWEEN days, not within them.** Decomposed the same
way `compare_shapes` decomposes the shape error, the fleet's within-day share of variance runs:

| 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|
| 0.170 | 0.214 | 0.185 | 0.217 | 0.152 | 0.137 | 0.295 | 0.236 |

An outage is a *multi-week* event: the fleet's 14-day rolling demonstrated availability ran
816 → 3,223 MW inside 2023 alone, and only 74 of 2,982 day-over-day steps exceed 200 MW. So a
biomass availability series carries almost no *within-day* information — and the within-day axis is
the one holding the level. That is the structural reason the ceiling is this low, and it applies to
**any** treatment of biomass, an outage model included.

The second half of the answer is sharper and is the part worth carrying forward: **the oracle makes
the recent years worse**, and a term that gets *worse* under better information was absorbing an
error somewhere else. Biomass sits inside the must-run block, so pinning it exactly changes the
block's size in precisely the half hours where the thermal stack is near zero — 16.1% of 2024's half
hours and 30.8% of 2025's, by this atom's own earlier measurement. **INFERRED, not observed:** the
flat 2,400 MW was partly standing in for the clean-end level error, and removing it exposes that
error rather than creating one. What would check it: re-run the oracle restricted to the half hours
where the post-import residual exceeds the must-run block, and see whether the correlation loss
disappears.

### What this does and does not license

* **It does not license wiring the envelope.** The envelope beats flat on correlation in four years
  of six here, but it lost on four axes of five in the pass that built it and it is off for that
  reason. Nothing in a bound is an argument for a treatment.
* **It does not license lowering anything.** R12: these are diagnostics. The published series is
  unchanged.
* **It retires the outage model as EP13's next gap.** L3 needs correlation, correlation needs
  *timing*, and biomass has almost no timing in it. The next gap has to be found on the within-day
  axis — which, on this atom's record, means the gas stack's own dispatch timing, not a fourth
  availability series.
* **The second Expert Hour is still untaken**, and it is now the only *named* thing between this
  atom and a level move. LAW A: the drawn plan said 2 → 3; the plan is a diagnostic.

Reproduce: `python3 -m tools.ep13_biomass_oracle_bound` →
`docs/observability/ep13_biomass_oracle_bound.json`.

**OWED — DISCHARGED 2026-08-27, see §12.** This atom's map entry was **11,954 B
against the 12,288 B per-atom cap — 334 B of headroom, and the fattest entry in the map.**
That is the EP1 shape exactly: the *next* pass on EP13 cannot write its note, and because the
pre-commit gate is tree-wide it will refuse **every lane's** commit, not just this one. The
control's own named remedy applies — rehome the accreted history to
`docs/design/simplifications/EP13_adapter_carbon_intensity.yaml` and leave one comment — and it is
a separate job from this measurement, deliberately not done inside it. This pass kept its own
addition to ~640 B and *corrected* the sentence it replaced rather than accreting beside it.

## 11. 2026-08-27 — the INPUT CEILING: the dispatch programme is capped at ~+0.01 correlation

**The claim this pass tested was already written down, and had never been measured.**
`sim/grid_carbon_intensity.py` says it in the docstring:

> "A dispatch model handed demand, wind and solar can only be a function of residual demand;
> GB's actual intensity increasingly is not."

Six passes have moved this atom's error terms — coal, the cables, the thermal floor, the measured
must-run fleet, the biomass envelope — and correlation, the axis holding the level, has moved
**0.726 → 0.746 in total**. Each pass named the next gap and built it. This pass measured the
ceiling of the whole remaining programme instead, which is the move §10 made one term down and
which retired an entire outage model for the cost of one measurement.

**METHOD.** Hand the model's own inputs to the *best possible function of them* and see where
correlation lands. Three rungs and a null, one process, identical caches, all scored by the same
`neso.compare_shapes` over the same held-out half hours:

| rung | what it bounds |
|---|---|
| `baseline` | `build_shape` as shipped — where the atom is |
| `recalibration_ceiling` | best possible function of the model's **own output** — bounds every post-hoc factor, curve and clamp |
| `input_ceiling` | best possible function of the model's **own inputs** — bounds every merit order, efficiency curve, coal-availability model and outage model |
| `null_ceiling` | the input ceiling refitted on a **shuffled** target — must collapse |

The two coordinates are the model's own reduction of its inputs, both intensive: `u` = thermal
residual / demand, `v` = import carbon / demand. Fitted as cell means on **odd** days of the
month, scored on **even** days — whole days either side, because the axis under measurement is
*within-day* ordering and a split that cut days in half would let the fit see the morning of a day
it is scored on the evening of. Fitting is in **intensity space**, not carbon space: NESO's series
is loss-corrected to a consumed basis and the reconstruction sits at the transmission boundary, so
`published × demand` is not GB's burnt carbon and subtracting an import term would mix a basis
difference into the target.

**THE RESULT — the inputs are exhausted.**

| year | baseline | recalibration | **input ceiling** | held-out gain |
|---|---|---|---|---|
| 2019 | 0.8815 | 0.8816 | 0.8757 | −0.0057 |
| 2020 | 0.8732 | 0.8726 | 0.8726 | −0.0006 |
| 2021 | 0.9075 | 0.9066 | 0.9087 | +0.0013 |
| 2022 | 0.8699 | 0.8694 | 0.8931 | +0.0231 |
| 2023 | 0.7973 | 0.7983 | 0.8071 | +0.0098 |
| **2024** | **0.7425** | 0.7462 | 0.7268 | **−0.0157** |

**In 2024 — the year that holds the level — the best possible function of the model's inputs
scores BELOW the shipped model out of sample, at every resolution tested.** No merit order, no
efficiency curve, no coal-availability model and no outage model can move that year's number,
because the information is not in the inputs. Recalibration is capped even harder: the best
possible function of the model's own output buys at most **+0.0037** in any year, so no factor,
curve or clamp of the kind the last six passes applied is worth building either.

**THE CONTROL THAT MAKES IT A CEILING AND NOT A NUMBER** is the resolution sweep, because a single
grid cannot distinguish *the inputs are exhausted* from *this binning is too coarse*. They separate
under refinement: if in-sample gain climbs while held-out gain stays flat, the extra resolution is
being spent on memorisation and the information limit has been reached.

| grid | cells | mean in-sample gain (upper bound) | mean held-out gain |
|---|---|---|---|
| 8×3 | 24 | −0.0023 | −0.0053 |
| 16×4 | 64 | +0.0081 | +0.0013 |
| 24×5 | 120 | +0.0109 | +0.0020 |
| 40×6 | 240 | +0.0120 | +0.0012 |
| 64×8 | 512 | +0.0067 | +0.0009 |

**In-sample gain plateaus at +0.012 across a 21× refinement and then falls; held-out gain never
exceeds +0.002.** The in-sample column is the rigorous half: no function of the inputs at a given
resolution can beat the in-sample cell means on the very half hours they were fitted to, so it is
an *upper bound* that does not depend on the split, the seed or the null. **The largest in-sample
gain in any year at any grid is +0.0295** (2022, 40×6).

**WHAT THIS DOES NOT SAY.** A ceiling bounds a model *class*; it is not a prediction that any
buildable model reaches it. A high ceiling would not have promised a build succeeds — only the low
direction is load-bearing, and it is the direction the atom needed. It also says nothing about the
*level* axis, which five earlier passes did move and which is not in dispute.

**WHAT IT MEANS FOR L3.** The remaining gap is not reachable by dispatch work of any kind, so the
"next gap on the within-day axis" the map has carried since 2026-08-26 is **retired as a build**.
L3 on this atom requires a **new input carrying within-day timing information the model cannot
currently see** — not a better model of the inputs it has. The most obvious candidate, named as a
hypothesis and explicitly *not* measured here, is embedded (distribution-connected) generation:
Elexon's AGWS meters transmission-connected wind and solar, GB's embedded solar fleet is large and
its output is strongly within-day, and NESO's published series accounts for it while this
reconstruction cannot see it at all. That is a DISCOVER question, not a build.

**R15.** 16 tests in `tests/tools/test_ep13_input_ceiling.py`; **9 named mutations run and
confirmed RED, then restored GREEN.** Two of them matter more than the rest, because this pass's
finding is a NEGATIVE and an instrument that can only ever report "no headroom" reports a
*constant* — R15's fourth shape, where mutation testing stays red because it was always red. So
the load-bearing test builds a world where the inputs *do* carry headroom the shipped model misses
and requires the instrument to find it.

**ONE MUTATION SURVIVED ON THE FIRST BATTERY AND THE FIXTURE WAS THE FAULT, not the tool.**
Replacing every cell mean with the grand mean — a fit that never happens — left the headroom test
green. The cause: that test's "bad" shipped model responded to `u` with inverted curvature, so its
correlation was about **−1** and the gain to beat was ~2.0; a bar of +0.05 against a baseline of −1
is cleared by any function with a positive slope. The baseline is now a *competent* model that
gets `u` right and cannot see `v`, which is the real shape of the thing being bounded, and the test
additionally asserts the surface **reaches** the target (>0.95) — an assertion a flat surface
cannot survive. A second mutation forcing every cell through the u-marginal fallback now also
fires, which is what proves the 2-D fit is genuinely exercised rather than the 1-D marginal.

Two further defects in the same file were found the same way and fixed: a **dead assertion**
(`... if "controls" in row else True`, where `controls` is never a key of a `measure_year` row),
and a fixture too small to populate the grid it tested — 28 days left ~5 fit half hours per cell,
so the null rung scored 0.52 against a signal of 0.999 and read as a leaking fit. **The null is now
a distribution across five seeds, not a single draw**, and its threshold is *derived* from the
effective cell count (3/√N) rather than chosen — the surface takes one value per cell, so the
effective sample behind a null correlation is the cell count, and single draws of ±0.2 are ordinary
at 120 cells. Observed maximum is 0.2413 (2021) against a 0.2739 threshold.

**A finding about the instrument, kept because it is about the real data's shape.** Quantile edges
cannot split a tie, and `v` is *exactly zero* for every half hour before the cables existed. Left
undeduplicated, those edges create empty bins and the grid silently shrinks — the artefact would
report 120 cells while the fit answered from a handful. Edges are now strictly increasing and the
artefact publishes `effective_cells`, the resolution the population actually supported, which is
what every derived threshold reads.

Reproduce: `python3 -m tools.ep13_input_ceiling` → `docs/observability/ep13_input_ceiling.json`.

## 12. 2026-08-27 — the OWED map-cap item is discharged: the narrative is rehomed, verbatim

**The wedge §10 named was 348 B away and it would have refused every lane's commit, not this one's.**
Measured at draw: `EP13_adapter_carbon_intensity` occupied **11,940 B of the 12,288 B per-atom cap**,
the fattest entry in a 298-atom map whose mean entry is 1,079 B. The control
(`tests/design/test_simplifications_store.py::test_map_within_per_atom_budget`) is tree-wide and runs
in the pre-commit gate on any map or store change, so the *next* pass on this atom — §11's own note ran
to ~1,100 B — would have taken the entry over and stopped publishing for every lane at once.

**The move is the control's own named remedy, and the one H27/H32 already made.** The accreted
level-hold narrative — 111 comment lines, seven passes of it, from `# STILL L2 as of 2026-08-25` down
to `Record: §10-11. LAW A.` — is now `level_hold_note` in
`docs/design/simplifications/EP13_adapter_carbon_intensity.yaml`, declared in the map's
`notes_rehomed: [name, origin_note, level_hold_note]`. The map keeps an eight-line pointer.

**Nothing was reworded, shortened, dropped or reordered.** Only the `#` comment markers were stripped.
The round trip was asserted before the map was touched: `notes_for_atom(...)['level_hold_note']` is
byte-identical to the text removed. **This is the point of doing it as a rehome rather than a
compaction** — the two moves available at a wedge are to raise the number or to launder the history,
and this project has refused both. A third exists and it is mechanical.

| | before | after |
|---|---|---|
| EP13 map entry | 11,940 B (348 B headroom) | **2,293 B (9,995 B headroom)** |
| whole map | — | 311,909 B, mean 1,047 B/atom |
| EP13 note tenant | 727 B | 10,630 B of 32,768 B |
| EP13 store file | 46,542 B | 56,590 B, under the 65,536 B roll watermark |
| fattest atom in the map | EP13 | `SITE1_expert_doors`, 10,495 B |

**The narrative is now MORE readable by machine, not less.** A YAML comment is invisible to every
parser; a `level_hold_note` is what `simplifications_store.notes_for_atom` and `hydrate` already
serve to the supervisor's draw and the site generators.

**Controls, all eight the gate selects for these two paths, green:**
`test_simplifications_store.py`, `test_atom_notes_store.py`, `test_atom_records_store.py`,
`test_maturity_map_facets.py`, `test_map_reconciliation.py`, `test_gate_authorization.py`,
`test_coupled_triad_gate.py`, `test_generate_proof_coupled_gaps.py`, `test_level_promotion_gate.py`
— 189 tests. The R15 both-ways pair on the cap itself
(`test_per_atom_budget_fires_on_accretion_and_on_one_fat_atom`, plus the empty-population vacuity
guard) is among them and still fires on its own named defects, so the headroom is reported by a
control that can still fail.

**No level moved, no number changed, no science was done.** §11's finding stands as written: L3 needs
a new input carrying within-day timing, and embedded generation is DISCOVER work, unmeasured. What
changed is that the pass which takes that on can now write down what it finds.

**One finding staged, not fixed** (SELF_INTERRUPT — it is in no gate's target set and blocks nothing):
`WORKER_FINDING_THE_EVIDENCE_PAGE_FIXTURE_COPIES_ONE_OF_THE_MAPS_TWO_HALVES_2026-08-27.md`. The
evidence page's fail-open floor test is red at HEAD — 15 citations against a >50 bar — because its
fixture copies `maturity_map.yaml` and not the closed half, so 224 of 298 atoms vanish from the
fixture's map. The live page builds 214. Attributed to HEAD with both sources restored; unrelated to
this change.

## 13. 2026-08-28 — the PEER BOUND: the target is reproducible at 0.97, so the axis is not exhausted

**Four candidates have now been retired by measuring their ceiling first, and every one of those
measurements came back negative.** The biomass outage model (§10), the merit-order programme
(§11), post-hoc recalibration (§11) and embedded generation (the eighth pass) all reported no
headroom. A programme that has heard "no headroom" four times running has to ask a question it had
never asked, because §11's instrument cannot answer it:

> **Is the target reproducible at all?**

`ep13_input_ceiling` bounds the best function of **the model's own inputs**. It cannot distinguish
*the information is not in these inputs* from *the information is not anywhere*, and those two have
opposite consequences. The first says find a new input. The second says the axis is measuring the
counterparty's own noise and no build of any kind can move it — which, after four negatives, was
becoming the comfortable reading.

**The discriminator was free and had been in the cache the whole time.** NESO publishes a
`forecast` on every one of the 104,454 half hours it publishes an `actual` for, and nothing had
ever scored one against the other on this axis. Score the publisher's own forecast against the
publisher's own outturn, on the same held-out even days, through the same `neso.compare_shapes`,
and the answer is a fact about the **target** rather than about us. It fits nothing, so it costs
seconds where §11 cost 85 minutes.

**THE RESULT — the target is reproducible, and the reconstruction is nowhere near it.**

| year | baseline (shipped) | **peer forecast** | peer − baseline | peer's own day mean |
|---|---|---|---|---|
| 2019 | 0.8814 | **0.9649** | +0.084 | 0.8312 |
| 2020 | 0.8732 | **0.9679** | +0.095 | 0.8422 |
| 2021 | 0.9075 | **0.9790** | +0.072 | 0.8457 |
| 2022 | 0.8699 | **0.9779** | +0.108 | 0.8863 |
| 2023 | 0.7973 | **0.9749** | +0.178 | 0.8881 |
| **2024** | **0.7425** | **0.9711** | **+0.229** | 0.8544 |

**In 2024 — the year that has held the level for eight passes — the publisher's own ex-ante
forecast scores 0.229 of correlation above the shipped reconstruction.** The within-day axis is
not noise. §11's ceiling was a fact about the reconstruction's *inputs*, exactly as it said, and
the diagnosis it wrote down — *L3 needs a new input carrying within-day timing* — is **confirmed
rather than retired**. This is the first positive result the atom has had in five measurements.

**THE PERSISTENCE LADDER, which is what makes 0.97 readable and cuts the claim down.** Carbon
intensity is heavily autocorrelated, so a correlation of 0.97 means nothing until you know what a
copy of the recent past scores. Every rung below is the outturn itself, lagged, scored by the same
function on the same keys — a model any reader can rebuild in three lines:

| year | lag 1 (30 min) | lag 2 (1 h) | lag 4 (2 h) | lag 48 (1 day) | **peer sits at** |
|---|---|---|---|---|---|
| 2019 | 0.9922 | 0.9731 | 0.9160 | 0.5340 | **2.29 half hours** |
| 2021 | 0.9937 | 0.9789 | 0.9321 | 0.6017 | **1.99** |
| 2024 | 0.9930 | 0.9776 | 0.9306 | 0.6328 | **2.28** |

**NESO's published forecast is worth about a one-hour persistence model, and a one-day persistence
model collapses to 0.60.** That is the honest size of the peer's achievement, and it makes the
finding *stronger*, not weaker: the information the reconstruction is missing is not exotic. A
copy of the grid an hour ago beats it by 0.24 in 2024.

**WHAT THIS BOUND IS NOT, stated because the high number invites over-reading.** It is **not an
oracle** — it holds no truth and can be beaten. It is **not independent**: NESO's `actual` is
itself a model, built from the same factor table, the same embedded-generation estimate and the
same loss correction as its forecast, so the common-mode part cancels and this **overstates** what
an outside reconstruction could reach. The optimism runs in the safe direction and that is the
whole reason it was worth measuring — a *low* peer would have closed the atom's remaining
programme outright; a high one promises nothing about any build. And the ladder bounds the peer's
*skill*, not its *horizon*: it says 0.97 is attainable by a model that knows the outturn an hour
ago, not that NESO's forecast only looks an hour ahead.

**CONTROLS — five, all green in all six years, and the tautology guard is the one to read first.**
If the `forecast` field were back-filled from the outturn for settled half hours this would be a
series compared with itself and would report ~1.0 by construction, which is R15's first killer
exactly. Measured: the two are bit-identical on **4.1%** of half hours and differ by a mean of
**9.8 g**; a copy scores 100% and 0 g. The null rung (the forecast dealt to other half hours)
collapses to −0.023…+0.020 against a derived 3/√n bar. The peer beats its own day mean by
0.09–0.15, so its advantage is genuinely within-day. The ladder **brackets** the peer in every
year — a ladder entirely below it would bound it on one side only, and a one-sided containment
check passes by being wide. Both sides are refused together at NESO's own published coal factor
(937 g/kWh, the dirtiest grid GB could physically be), because a filter on one side of a
comparison measures the filter; 6 half hours refused.

**R15 — EIGHT NAMED MUTATIONS, and one survived and the CONTROL was the fault.**
`peer_beats_its_own_day_mean`, written as the obvious `peer > peer_day_mean`, **passed** under its
own defect: when the mutation replaces the forecast with its own day mean the two sides are equal
*by construction*, and they differed by 1.1e-16 of floating point, which a strict inequality reads
as an advantage. **A control comparing two quantities that its own named defect makes identical is
fail-open without a materiality margin** — it reports rounding noise as a finding. Fixed with
`MIN_WITHIN_DAY_ADVANTAGE = 0.01`, more than ten times below the measured gap so the bar is
visibly not carrying the result, and the test now asserts both that the mutation makes the sides
equal (or it is testing something else) and that the margin binds.

**A FINDING ABOUT THE ATOM'S OWN EXIT AXIS, recorded and DELIBERATELY NOT ACTED ON.** A statistic
that a lag-1 copy wins at 0.993 is a weak discriminator for a *structural* reconstruction, and this
atom's level has been decided on it for eight passes. That observation arrives from an agent whose
own score on that axis is the thing being held — which is precisely the shape R12 and R13 exist to
refuse, and the shape of taking the robust statistic *because* it is the flattering one. So it is
written down here and **nothing follows from it in this pass**: the exit axis is unchanged,
`level_target` is unchanged, the level stays at **2**, and the recommendation — that a
reconstruction be scored on a statistic autocorrelation does not dominate, alongside correlation
rather than instead of it — is the director's to take or leave. Exit-test integrity is a WALL.

**WHAT THIS POINTS AT, named as a hypothesis and explicitly NOT built.** NESO's forecast is built
from a forecast **per fuel**; the reconstruction reduces everything to a residual and a merit
order, which §11 proved is exhausted. Elexon's half-hourly FUELHH per-fuel outturn is already in
`sim/cache` and already read for coal, biomass and the must-run block. An oracle rung handing the
fit per-fuel outturn would bound that input — and would be **not publishable**, of the same class
as §11's input ceiling, because it is NESO's arithmetic. Its value would be as a bound: if it comes
in near 1.0 the missing information is squarely the fuel mix, and the buildable question becomes
how much of the fuel mix is forecastable from published day-ahead data. That is the next
measurement, and it is a measurement before it is a build.

**No level move. LAW A.** Reproduce: `python3 -m tools.ep13_peer_bound` →
`docs/observability/ep13_peer_bound.json`. Controls: `tests/tools/test_ep13_peer_bound.py`, 16
tests.

---

## 14. 2026-08-30 — the PER-FUEL ORACLE: the timing is in CCGT, the one fuel the model never sees

§13 ended by naming this measurement and deliberately not building it: *NESO forecasts PER FUEL
where this model reduces everything to a residual.* This is that measurement, and it is the atom's
first result that names a **build target** rather than retiring a candidate.

### What the shipped reconstruction does, stated plainly, because it is the thing being tested

`build_shape` never sees a fuel dispatched. It takes demand, subtracts renewables, imports and the
zero-carbon must-run block, and splits what is left by a merit order it decides for itself. Coal
enters as one *capacity* per year, biomass as one annual *envelope* — availability, not dispatch.
The half-hourly question "how much gas is running right now" is answered by a residual.

### The instrument, and the one thing it is NOT

Hold the TRUE half-hourly per-fuel outturn from Elexon FUELHH, put it through NESO's own published
factor table, score the result against NESO's published outturn on the same held-out even days
through the same `neso.compare_shapes`. It fits nothing, so it costs minutes where §11's ceiling
cost 85.

**IT IS NOT A CEILING, and every previous oracle on this atom was.** §10 and the embedded pass both
bounded a candidate from *above*: perfect knowledge of the input, so a negative retires the
candidate outright. That is how four candidates died. This one is **handicapped** — embedded
generation, interconnectors, OIL and OTHER are all missing from the arithmetic, and all three
omissions cost it accuracy it could have had. So it is an **attainment floor** on what per-fuel
truth is worth, not a ceiling on it. A negative here would have retired nothing. *(This correction
is recorded because the preregistration filed before the run got it wrong and said a negative would
make per-fuel the fifth retirement. It would not have.)*

The inversion is why the **positive** is worth more than a positive ceiling would be: a
handicapped model that still reaches 0.9352 has proved the input carries the information, and a
better-equipped one can only do better.

### THE RESULT

| year | baseline (shipped) | **per-fuel oracle** | oracle − baseline | oracle's own day mean | gen/demand | MAE vs NESO |
|---|---|---|---|---|---|---|
| 2019 | 0.8819 | **0.9665** | +0.085 | 0.8268 | 0.970 | 14.7 g |
| 2020 | 0.8737 | **0.9634** | +0.090 | 0.8369 | 0.988 | 11.7 g |
| 2021 | 0.9078 | **0.9780** | +0.070 | 0.8419 | 0.964 | 16.9 g |
| 2022 | 0.8698 | **0.9823** | +0.113 | 0.8850 | 1.063 | 14.4 g |
| 2023 | 0.7973 | **0.9434** | +0.146 | 0.8602 | 0.911 | 30.3 g |
| **2024** | **0.7425** | **0.9352** | **+0.193** | 0.8185 | 0.874 | 33.1 g |

**In 2024 — the year that has held this level for nine passes — per-fuel truth is worth +0.193 of
correlation, and closes 84% of the distance to the peer bound's 0.9711.**

### THE ABLATION LADDER, which is the part that survives every caveat above

A number saying "per-fuel truth is worth +0.19" tells the atom to find per-fuel data. It does not
say *which fuel*, and the fuels are not equally observable from outside: coal availability is an
annual fact about steel, gas dispatch is a half-hourly decision. So each fuel is flattened to its
own day mean in turn — its within-day timing deleted, every other fuel left at truth — and what it
costs is what its timing was worth.

| year | COAL | **CCGT** | OCGT | BIOMASS | WIND |
|---|---|---|---|---|---|
| 2019 | −0.0137 | **−0.0787** | +0.0001 | −0.0008 | −0.0314 |
| 2020 | −0.0056 | **−0.0760** | +0.0002 | −0.0004 | −0.0220 |
| 2021 | −0.0106 | **−0.0766** | +0.0002 | −0.0001 | −0.0257 |
| 2022 | −0.0040 | **−0.0522** | +0.0001 | −0.0002 | −0.0313 |
| 2023 | −0.0034 | **−0.0566** | +0.0000 | +0.0001 | −0.0000 |
| **2024** | −0.0013 | **−0.0949** | −0.0001 | −0.0003 | +0.0024 |

**The within-day timing is almost entirely in CCGT, in every one of the six years.** Flattening gas
costs 0.052–0.095; flattening coal costs 0.001–0.014 and biomass 0.0003. This is a fact about the
GB grid rather than about the reconstruction, and it holds even if the headline number above is
dismissed entirely.

### AND IT EXPLAINS THE DECAY NOBODY HAD ACCOUNTED FOR

The baseline falls 0.88 → 0.74 across the window and eight passes treated that as the model getting
worse. It is not. **WIND's ablation cost collapses from −0.031 to ~0 while CCGT's grows to its
largest**, so the within-day information *migrated* into the one fuel the model cannot observe.
The reconstruction did not decay; the grid moved the answer out of its reach. Coal's own collapse
(−0.0137 → −0.0013) is the same story one fuel over, and it is the fuel this model *does* hold.

### THE TAUTOLOGY GUARD, first thing a reader should check

NESO's `actual` is itself a metered fuel mix through a factor table. If FUELHH were the same mix
and this the same table, the measurement would be NESO's arithmetic replayed at ~1.0 by
construction — R15's first killer. Measured: **bit-identical on 0.000 of half hours**, mean
absolute difference **11.7–33.1 g** against a 2.0 g bar. That gap is the embedded, interconnector
and loss terms showing up as exactly what they are.

### FAIL CLOSED ON AN ABSENT FUEL — the defect the first draft had

The four FUELHH caches do not cover identical half hours; BIOMASS begins later than COAL. The first
draft summed an absent fuel as zero, which is not "no gas was running" but "no reading" — and it
deletes the largest carbon term on the system and publishes a clean grid. Every fuel in
`HELD_FUELS` must be present or the half hour is refused: **28,813 refused, 99.6% of them in
2016–17** before the biomass cache begins, which is why this table starts at 2019.

### R15 — SEVENTEEN TESTS, and the control that had to be keyed to the property

The load-bearing test is the inverse of the previous four bounds'. Those reported negatives, so
their danger was an instrument that can only say "no headroom". This reports a **positive**, so its
danger is one that says "big headroom" whatever it is handed:
`test_the_instrument_reports_a_LOW_oracle_when_THE_FUELS_DO_NOT_CARRY_THE_TIMING` builds a world
where the timing lives somewhere the fuel mix cannot see and requires the oracle to fall *below*
the shipped baseline. Beside it, `test_the_ablation_ladder_NAMES_THE_FUEL_THAT_CARRIES_THE_TIMING`
puts the swing in CCGT in advance and requires the ladder to finger it by a 5× margin.

**The coverage control is the one worth reading.** Generation over demand is all that stands
between this instrument and a silently rescaled intensity — but 2022 comes in at **1.063**, because
GB was a net *exporter* that year. A bound capped at 1.0, which is what the preregistration
predicted, would have gone red **because the world got more honest**. That is the failure mode this
project has hit repeatedly, so the shipped bound is keyed to the property (a sum of generation is
near demand, 0.80–1.20) and `test_the_coverage_bound_admits_a_NET_EXPORT_year` pins 1.063 open
against a later pass re-tightening it.

### What this licenses, and what it does not

**L3's build is a publishable proxy for within-day CCGT dispatch.** That is the first time this
atom has had a named target rather than a retired candidate. The oracle itself may never be
published — it is NESO's factor table on metered truth — and
`oracle_reaches_the_published_feed` is False by AST walk, not by promise.

**No level move. LAW A.** Reproduce: `python3 -m tools.ep13_per_fuel_oracle_bound` →
`docs/observability/ep13_per_fuel_oracle_bound.json`. Controls:
`tests/tools/test_ep13_per_fuel_oracle_bound.py`, 17 tests. Prediction filed before the run:
`docs/staging/WORKER_PREREGISTRATION_WHAT_THE_PER_FUEL_ORACLE_MUST_SHOW_2026-08-30.md`.

---

## 15. 2026-08-31 — the CCGT SWAP CEILING: the model knows WHEN gas runs, not HOW MUCH

§14 ended by naming L3's build target — *a publishable proxy for within-day CCGT dispatch* — on the
strength of a +0.193 measured by an oracle that **replaced the whole arithmetic at once**: factor
mapping, denominator, fuel coverage, the must-run block, coal's dispatch and the CCGT efficiency
band, with imports dropped from both sides. This project's own rule applies to its own instruments:
*when a result moves and more than one thing changed, you cannot attribute it.* This is the
one-variable version, and **it refutes the reading §14 was given.**

### The instrument

`tools/ep13_ccgt_swap_ceiling.py` re-implements `emissions_rate_t_per_mwh` line for line with one
override point at `ccgt_mw`, and proves the copy with the override off: **max drift 0.0** against
`gci.build_shape` on the same population. Read that first — without it every rung below is a second
model, and the difference would be attributed to the substitution.

**IT IS A CEILING, WHICH INVERTS §14.** §14's oracle was handicapped and bounded the input from
*below*; a negative there retired nothing. This one hands the shipped model **perfect** knowledge of
the exact quantity a proxy would approximate and changes nothing else, so no build of that class can
beat it and a negative retires the target outright. Up to error cancellation, as always: a proxy
whose errors offset the model's other errors could score above it, and one that does is fitting the
residual rather than modelling gas.

### THE RESULT

Baseline is 0.7385 in 2024 rather than §14's 0.7425 because the population is restricted to half
hours carrying a metered gas reading — the same restriction applied to **every** rung, so no gain
below is partly a coverage difference.

| year | baseline | **+TIMING** | +level | +full | flat gas | NULL | gas r | gas r *within* | model MW | true MW |
|---|---|---|---|---|---|---|---|---|---|---|
| 2019 | 0.8814 | **+0.0170** | −0.0637 | −0.0321 | −0.5427 | −0.2860 | 0.898 | 0.866 | 11,346 | 13,116 |
| 2020 | 0.8726 | **+0.0209** | −0.0784 | −0.0608 | −0.4717 | −0.2928 | 0.902 | 0.866 | 9,330 | 10,974 |
| 2021 | 0.9098 | **+0.0039** | −0.0407 | −0.0251 | −0.5026 | −0.3071 | 0.901 | 0.870 | 10,747 | 12,415 |
| 2022 | 0.8725 | **+0.0232** | +0.0053 | +0.0077 | −0.2662 | −0.2336 | 0.823 | 0.825 | 9,498 | 12,366 |
| 2023 | 0.8021 | **+0.0393** | +0.0595 | +0.1299 | −0.1492 | −0.2365 | 0.860 | 0.820 | 9,408 | 9,981 |
| **2024** | **0.7385** | **+0.0485** | **+0.1162** | **+0.2163** | −0.1409 | −0.2192 | 0.832 | **0.807** | 8,846 | 8,339 |

### THE NAMED BUILD TARGET IS CAPPED AT +0.05, AND IS RETIRED

Perfect within-day CCGT timing, at the level the residual already decides, is worth **+0.0485 in
2024** and +0.004 to +0.049 across the window. The distance still to be closed is the peer bound's:
0.9711 − 0.7385 = **0.233**. The target §14 named closes **21% of it** at its theoretical best.

**That is the fifth candidate retired by measuring its ceiling before building it** — after the
biomass outage model, the merit-order programme, post-hoc recalibration and embedded generation —
and it is the first retirement of a target this atom had already committed to. §14's floor could not
have done it: a floor says "at least this much is there" and never "no more than this".

### WHERE THE +0.193 ACTUALLY LIVES

Decomposed on the shipped model, in 2024: **timing +0.0485, level +0.1162, both together +0.2163.**
The level is worth **2.4×** the timing, and the two interact for a further +0.052.

The direct diagnostic on the MW series says the same thing without any of the shape machinery: **the
model's implied gas already tracks the metered series within days at r = 0.807–0.870**, falling only
0.06 across six years. §14's ablation ladder established that the *grid's* within-day information is
in CCGT — that stands, and nothing here disturbs it. What does not stand is the sentence it was read
as: *the model cannot see when gas runs.* It sees most of it.

**Flattening gas inside the day costs 0.14–0.54.** So within-day gas variation carries most of this
shape's correlation, and the reconstruction already holds all but 0.05 of the attainable part. Both
facts are needed together and either alone misleads.

### THE DECAY, EXPLAINED A THIRD TIME AND DIFFERENTLY

Eight passes read the fall from 0.88 to 0.74 as the model getting worse. §14 read it as the
information migrating into a fuel the model cannot see. This says which *property* of that fuel
migrated: within-day r falls only 0.866 → 0.807, while the level rung's worth goes **−0.064 → +0.116**.
And the bias flips sign — in 2019 the model dispatches 11,346 MW of gas against a true 13,116
(**13% low**); in 2024 it dispatches 8,846 against 8,339 (**6% high**).

**The reconstruction did not stop knowing when gas runs. It started being wrong about how much.**

### ONLY ONE RUNG IS A CEILING, AND IT IS NOT THE BIGGEST NUMBER

`ccgt_timing` is day-total preserving by construction, so the half hour is still met by the same
energy and the substitution is genuinely one variable. **`ccgt_level` and `ccgt_full` are not**:
they move the daily gas total without re-deciding the residual's other terms, so part of what they
report is that disturbance. They point at an axis; they do not bound it. Stated here rather than in
a footnote because the largest number in the table is one of them, and it is the one a later pass
will be tempted to quote.

### R15 — THIRTEEN TESTS, AND THE REAL RUN CAUGHT TWO CONTROL DEFECTS

**The load-bearing test is inverted from the four negative bounds'.** They reported negatives, so
their danger was an instrument that can only say "no headroom"; this reports a positive, so its
danger is one that says "big headroom" whatever it is handed.
`test_the_instrument_reports_NO_gain_when_THE_MODEL_ALREADY_HAS_THE_TIMING` hands it a truth series
identical to the model's own and requires both the gain and the distinctness control to go to zero.

**THE NULL CONTROL WAS KEYED TO A GUESSED ANSWER AND WENT RED AGAINST A SOUND INSTRUMENT.** The
first draft asked for `abs(null gain) < 0.01` — "the null collapses to nothing". Scrambled timing
does not sit at nothing: it replaces the model's own gas timing with *wrong* timing and must hurt,
measured at −0.219 to −0.307. A control pinned to today's expected answer, going red because the
world behaved correctly, is this project's own named failure shape and a fresh instance of it.
Repaired to the property — *a null may not FLATTER* — plus a discrimination leg, because "did not
gain" alone is satisfied by an instrument that reports one constant whatever it is handed.

**`timing_beats_level` COMPARED AGAINST THE WRONG RUNG AND REPORTED TRUE IN EVERY YEAR.** The first
draft had no level rung; it labelled `ccgt_day_mean` "the level-only rung", which it is not — it
deletes within-day variation rather than isolating the level. The comparison was therefore against a
destruction rung, and it read True in all six years including the two where the honest answer is
False. **A comparison is only as good as the name of what it compares against**, and the repair was
to build the complement (`ccgt_level`) rather than to reword the label.

**One MISSING TEST found by mutation, and it was not the flattering finding.** Two mutations survived
the first battery. `test_substituting_the_models_OWN_gas_changes_NOTHING` survived a uniform scale of
the subject — established as an **equivalence**, since a targeted mutation of the override path fires
it. The AST-walk test survived a plain substring search — established as a **missing test**: all four
fixtures were real imports, on which a substring search and an AST walk agree. The leg that separates
them is a source that *mentions* this module without importing it, which is every doc comment a later
pass will write next to the feed pointing here; a substring search would call that a leak, and the
cheapest repair would be deleting the pointer a reader needs.

### NEXT, named as a hypothesis and NOT built

**The daily and seasonal LEVEL of gas**, worth +0.116 in 2024 on a rung that is a diagnostic rather
than a bound. Two things must happen before it is a target: a proper ceiling on it, with the residual
re-decided so the energy balance holds, and a check that it is *publishable* — a daily gas figure is
a far softer thing to proxy from outside than a half-hourly dispatch, which is the first time this
atom's next candidate has looked easier rather than harder.

**No level move. LAW A.** Reproduce: `python3 -m tools.ep13_ccgt_swap_ceiling` →
`docs/observability/ep13_ccgt_swap_ceiling.json`. Controls:
`tests/tools/test_ep13_ccgt_swap_ceiling.py`. Preregistration and its scorecard, one confirmed of
five: `docs/staging/WORKER_PREREGISTRATION_WHAT_THE_CCGT_SWAP_CEILING_MUST_SHOW_2026-08-31.md`.

---

## 16. 2026-09-03 — THE BALANCED LEVEL CEILING: it cannot be built inside the shipped merit order

§15 named the daily and seasonal LEVEL of gas as the next candidate and owed two things before it
could be a target: **a proper ceiling on it, with the residual re-decided so the energy balance
holds**, and a check that it is publishable. This pass built the first. **The answer is that the
ceiling §15 specified cannot be constructed inside the shipped model**, and that is a finding about
the method rather than about the world.

### What was built

`tools/ep13_ccgt_level_ceiling.py` imposes truth's daily gas level and re-splits the shipped
dispatch around it — coal and the peaker band take what gas no longer serves, at their shipped
factors — so the substitution moves *which* units ran and not *how much* energy ran. With no
override it reduces to `gci.build_shape` exactly: re-implementation drift **0.0**.

### THE ANCHOR IS NOT `thermal_mw`, AND THE OBVIOUS READING OF §15 IS WRONG

The natural reading of "the energy balance holds" is `gas + coal + peaker == thermal_mw`. **The
SHIPPED model does not satisfy that.** Whenever the residual exceeds the CCGT fleet (30,000 MW) plus
the peaker headroom (7,000 MW) the stack truncates and serves less than it demanded — at demand
50,000 MW with 3,000 MW of renewables it is 2,000 MW short, with no override anywhere near it.

A control keyed to `thermal_mw` would have reported **the shipped model's truncation as this
substitution's imbalance**, in every high-demand half hour: a control going red for the world rather
than for the instrument, this project's own named failure shape, freshly minted in the very pass
whose subject is an unattributable number. Caught by a four-line smoke test at real inputs *before
the instrument was run*, and corrected beside the claim in the preregistration rather than over it.

### THE RESULT: NO YEAR HAS A READABLE CEILING

| year | baseline | balanced | unbalanced | difference | cap share |
|---|---|---|---|---|---|
| 2019 | 0.8819 | −0.0025 | −0.0635 | +0.0610 | **0.831** |
| 2020 | 0.8737 | +0.0056 | −0.0781 | +0.0837 | **0.813** |
| 2021 | 0.9078 | −0.0046 | −0.0394 | +0.0348 | **0.837** |
| 2022 | 0.8697 | −0.0228 | +0.0071 | −0.0299 | **0.852** |
| 2023 | 0.7973 | −0.1070 | +0.0646 | −0.1716 | **0.726** |
| 2024 | 0.7425 | −0.1523 | +0.1151 | −0.2674 | **0.531** |

`the_caps_are_not_carrying_the_rung` is **RED in all six years**. Conserving energy means gas can
only be raised as far as coal and the peakers were actually running, and where the residual sits
below the CCGT fleet that headroom is exactly **zero** — so the rung is pinned to the baseline on
every half hour of every day whose true gas level runs above the model's. That is roughly half of
them by construction, and 83% in 2019 where §15 measured the model running 13% LOW.

**The negative numbers are not the ceiling and are not quoted as one.** A rung pinned to its own
baseline on most of its population is measuring the pin.

### THE CONTROL THAT SAYS SO WAS FAIL-OPEN IN THE FIRST DRAFT, AND THIS IS THE PART TO READ

`control_bound_share` counted the fleet clamps and a non-zero balance. It read **0.000–0.050** and
passed every year. It did not count `capped_to_served` — binding **117,510** times run-wide against
the clamps' **1,293** — and it *could not*, because **the cap restores the balance**, so a
balance-derived share is blind to it by construction. Corrected, the share is 0.531–0.852 and the
control is red everywhere.

**Uncorrected, this pass would have published a confident sixth retirement with six negative numbers
behind it**, and the retirement would have been wrong. A control that exists to refuse a rung its
caps are carrying, and that does not count the cap actually carrying it, does not merely fail to
fire — it certifies the opposite.

### WHAT IS AND IS NOT ESTABLISHED

**Established:** a ceiling on the daily gas level cannot be built by re-splitting the shipped
dispatch, because the model has no other dispatchable source for gas to trade against in the
majority of half hours. §15's `ccgt_level` +0.116 remains unquotable, and is now unquotable for a
second reason as well.

**NOT established, and the tempting reading:** *"five of six years negative, so the level is worth
nothing — retire it."* **The daily and seasonal gas level is NOT the sixth retired candidate.**
Two independent reasons: the cap control refuses every year, and the discrimination leg fails in
four of six (in 2022–2024 scrambled day levels score *better* than correct ones, which by control
6's own logic makes a bare negative unreadable). The candidate is **undecided**, not retired — the
first time on this atom that a pass has ended without moving one either way, and the honest place
to leave it.

**The publishability check §15 owed stays un-run**, now because it is premature rather than moot.

### WHAT WOULD DECIDE IT

The construction needs an absorber that is not the OCGT peaker band. Every downward level correction
here is met by the dirtiest unit in the stack, so the rung charges a carbon penalty for a change
that in the real world was met by imports, embedded generation or lower demand. Naming what should
absorb a gas-level correction is the question this pass leaves, and it is a different question from
the one §15 asked.

### R15 — EIGHTEEN TESTS, TWO SURVIVORS ON THE FIRST BATTERY, ONE OF THEM AN EQUIVALENCE

Twelve mutations run, ten red immediately. Both survivors were the load-bearing pair, which is the
uncomfortable finding and not the flattering one.

**`remaining_mw = thermal_mw - ccgt_mw` — established an EQUIVALENCE, by argument rather than by
assumption.** `thermal_mw` and `served_baseline_mw` differ only where the peaker band saturates, and
in exactly those half hours `remaining_mw` is already past the saturation point under both
readings — so coal and peaker take identical values and no emissions figure moves. The anchor choice
*is* load-bearing, but in `balance_mw`, not in the dispatch split; mutating it there
(`− served_baseline_mw` → `− thermal_mw`) fires four tests.

**The second survivor was a MALFORMED MUTATION of my own** — a partial revert that is a no-op
wherever coal capacity is zero. The clean form (the balanced branch not re-deciding at all, which is
§15's defect reinstated) fires two tests. Recorded rather than quietly re-run, because a mutation
that survives because it was badly written reads in a log exactly like one that survives because the
control is weak.

**A wall guard that could not fail, caught by its own negative leg.** The first draft imported
`ceiling_is_unreachable_from` from `ep13_ccgt_swap_ceiling`. That function derives its subject from
`Path(__file__).stem`, which binds to the module where it is *defined* — so it asked "does the
published feed import the SWAP ceiling?", answered truthfully about the wrong module, and would have
reported this module unreachable no matter what imported it. The four other EP13 bounds each define
their own copy for exactly this reason; the reuse was the novel mistake.

**No level move. LAW A.** Reproduce: `python3 -m tools.ep13_ccgt_level_ceiling` →
`docs/observability/ep13_ccgt_level_ceiling.json`. Controls:
`tests/tools/test_ep13_ccgt_level_ceiling.py`. Preregistration, its pre-run correction and its
scorecard: `docs/staging/done/WORKER_PREREGISTRATION_WHAT_THE_BALANCED_GAS_LEVEL_CEILING_MUST_SHOW_2026-09-03.md`.

## 17. 2026-09-30 — WHAT ABSORBS A GAS-LEVEL DEPARTURE: not the peakers, and after 2019 not the thermal stack

§16 left one question: *what should absorb a gas-level correction, if not the OCGT peaker band?*
It can be answered by measurement, so this pass measured it. No instrument was built and no level
moved. **This was not preregistered.** It is a decomposition run once, and it should be read as one.

### The measurement

For every half hour with a metered CCGT reading, `gap = model gas − metered CCGT`. The model's gas is
`dispatch_rate`'s `implied_ccgt_mw` with no override (the shipped merit order, the same inputs
`measure()` uses). The gap is averaged per day (days with ≥46 periods), and then regressed, one
component at a time, on each part of the identity that the cached FUELHH can see:

- metered COAL. The model dispatches none below the 30 GW CCGT fleet, so every metered coal MW has
  gone into the model's gas.
- metered OCGT.
- metered BIOMASS minus the model's constant.
- metered NUCLEAR+NPSHYD minus the model's must-run.
- metered positive interconnector flow minus the priced imports the model subtracts.

Each slope is the share of the daily gap that component moves with. `rest = 1 − Σ` is a
**remainder, not a measurement**. It holds everything the caches cannot see: the INDO demand
definition, AGWS wind against transmission-metered wind, pumped storage, OIL, OTHER.

| year | days | mean gap MW | sd MW | coal | OCGT | biomass | must-run | imports | **rest** |
|---|---|---|---|---|---|---|---|---|---|
| 2017 | 60 | +1193 | 2212 | +0.93 | +0.00 | +0.16 | +0.00 | +0.00 | −0.09 |
| 2018 | 355 | −1162 | 2487 | +0.77 | +0.00 | +0.02 | +0.00 | +0.00 | +0.22 |
| 2019 | 351 | −1804 | 1637 | +0.38 | −0.00 | +0.14 | −0.00 | −0.00 | **+0.48** |
| 2020 | 341 | −1588 | 1525 | +0.35 | +0.00 | +0.12 | −0.00 | +0.00 | **+0.53** |
| 2021 | 348 | −1616 | 1599 | +0.23 | +0.01 | +0.14 | −0.00 | +0.08 | **+0.54** |
| 2022 | 292 | −2994 | 2509 | +0.10 | −0.00 | +0.10 | −0.00 | +0.11 | **+0.70** |
| 2023 | 358 | −616 | 2233 | +0.03 | +0.00 | +0.09 | +0.00 | +0.00 | **+0.87** |
| 2024 | 361 | +522 | 2350 | −0.03 | +0.00 | +0.06 | +0.00 | +0.07 | **+0.90** |
| 2025 | 156 | −2434 | 1365 | +0.00 | +0.01 | +0.14 | +0.00 | +0.19 | +0.66 |

### What it establishes

**The OCGT peaker band absorbs 0.00–0.01 of the real day-level gas departure in every year.** The
construction in §16 sends every downward correction to that band. In the real system it carried
effectively none of it, so the carbon penalty §16's balanced rung charged was an artefact of its
construction. That settles the question §16 asked, and it settles it against the peaker band.

**Coal was the absorber until 2019 and is gone by 2023:** 0.93 → 0.77 → 0.38 → 0.03. Inside that
window, the balanced construction's first absorber (coal) was the right one. What broke it there was
the cap: gas could not be *raised* past what the stack served. The absorber was not the problem.

**From 2019 on, most of the departure is outside the thermal stack altogether:** 48% rising to 90% by
2024. In those years the model's gas level is wrong because the model's *thermal requirement* is
wrong. Something on the demand/wind side of the residual differs from what was metered. So a
construction that conserves the model's served total is conserving the wrong number. **The frame
§15 and §16 shared, "impose truth's gas level and re-split within the stack", is the wrong frame for
2019 onward, and it cannot be repaired by choosing a better absorber inside the stack.**

This also accounts for §15's decay across the window. The source of the model's gas error moved
from a fuel it cannot dispatch (coal, 2016–18) to an input it is handed (2019+). That reading is
consistent with the table but was not tested separately.

### What it does NOT establish

- **Which input carries the remainder.** The cached FUELHH holds only COAL, CCGT, OCGT, NUCLEAR,
  NPSHYD, BIOMASS and the interconnectors. WIND, PS, OIL and OTHER were never fetched, so the
  remainder cannot be split. The leading candidate is unmeasured. AGWS wind includes an embedded
  estimate that transmission-metered gas never sees, and it is the input whose share grows with
  wind build-out, as the remainder does.
- **Anything about the correlation ceiling.** This is a decomposition of the gas *level* error, not
  a rung. No gain is claimed.
- **2017 and 2025 are partial years** (60 and 156 days) and are shown for completeness only.

### NEXT, named and NOT built

1. Fetch FUELHH `WIND`, `PS`, `OIL`, `OTHER` into a fifth cache through `sim/elexon_fuel_outturn.py`,
   the existing adapter, with the same wall line: they go to measurement and never to the dispatch.
   Then split the remainder.
2. If the remainder is the wind definition (AGWS against transmission), that is an **input
   fidelity correction** to `build_shape`. It is not a ceiling, and it is decided blind to the
   correlation it moves.
3. Only after that does a level rung mean anything. It would be the §16 **unbalanced** rung with the
   corrected residual, not the balanced one.

No level move. LAW A.

Reproduce: save the script below and run it as `PYTHONPATH=. python3 <file>` from the repo root.
It takes a few minutes and needs the `sim/cache/elexon_*` caches. It was re-run from this text and
matched the table to the last digit.

```python
import json
from collections import defaultdict
from pathlib import Path
from sim import elexon_fuel_outturn as fuel
from sim import grid_carbon_intensity as gci
from sim.generation_demand_history import aggregate_renewable_generation
from tools.generate_grid_intensity_feed import AGWS_CACHE, DEMAND_CACHE, aggregate_demand, fuel_mix
from tools.ep13_per_fuel_oracle_bound import per_fuel_by_period
from tools.ep13_ccgt_level_ceiling import dispatch_rate

demand = aggregate_demand(json.loads(Path(DEMAND_CACHE).read_text()))
wind = aggregate_renewable_generation(json.loads(Path(AGWS_CACHE).read_text()))
imports, coal_cap, _c, floors_r, must_run, _m, _e = fuel_mix()
floors = {y: r["floor_mw"] for y, r in floors_r.items()}
metered = [per_fuel_by_period(fuel.load_cached_thermal()),
           per_fuel_by_period(json.loads(Path(fuel.CACHE_PATH).read_text())),
           per_fuel_by_period(json.loads(Path(fuel.BIOMASS_CACHE_PATH).read_text())),
           per_fuel_by_period(fuel.load_cached_zero_carbon_must_run())]
days = defaultdict(lambda: defaultdict(list))
for k in demand:
    if k not in wind or any(k not in m for m in metered) or "CCGT" not in metered[0][k]:
        continue
    y = int(k[0][:4]); imp, rate = imports.get(k, (0.0, 0.0))
    try:
        _, gas, _, _ = dispatch_rate(demand[k], wind[k], y, import_mw=imp, import_rate_t_per_mwh=rate,
                                     coal_capacity_mw=coal_cap.get(y, 0.0), thermal_floor_mw=floors.get(y, 0.0),
                                     zero_carbon_must_run_mw=must_run.get(k))
    except Exception:
        continue
    t = {f: v for m in metered for f, v in m[k].items()}
    d = days[k[0]]
    d["gap"].append(gas - t["CCGT"]); d["coal"].append(t.get("COAL", 0.0)); d["ocgt"].append(t.get("OCGT", 0.0))
    d["bio"].append(t.get("BIOMASS", 0.0) - gci.MUST_RUN_BIOMASS_MW)
    d["zc"].append(t.get("NUCLEAR", 0) + t.get("NPSHYD", 0) - float(must_run.get(k, gci.MUST_RUN_ZERO_CARBON_MW)))
    d["imp"].append(sum(v for f, v in t.items() if f.startswith("INT") and v > 0) - imp)
mean = lambda x: sum(x) / len(x)
def slope(xs, ys):
    mx, my = mean(xs), mean(ys); sxx = sum((a - mx) ** 2 for a in xs)
    return sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / sxx
by_year = defaultdict(list)
for day, d in days.items():
    if len(d["gap"]) >= 46:
        by_year[day[:4]].append({c: mean(v) for c, v in d.items()})
for y, rows in sorted(by_year.items()):
    g = [r["gap"] for r in rows]
    s = {c: slope(g, [r[c] for r in rows]) for c in ("coal", "ocgt", "bio", "zc", "imp")}
    print(y, len(rows), round(mean(g)), {c: round(v, 2) for c, v in s.items()}, "rest", round(1 - sum(s.values()), 2))
```

## 18. 2026-09-30 — THE REMAINDER, SPLIT: solar counted twice, then offshore wind counted short

§17's NEXT step 1 is done. FUELHH `WIND`, `PS`, `OIL` and `OTHER` are fetched through the existing
adapter into a fifth cache (`sim/elexon_fuel_outturn.py --remainder`, `REMAINDER_CACHE_PATH`,
700,940 rows over 2016–2025). They are used for measurement only. No `*_by_period` view exists for
them, and `test_the_remainder_series_never_reaches_the_dispatch` holds that line. **Not
preregistered.** This is §17's decomposition with five more columns, run once.

The five new columns are each read against how the model builds its residual. The residual is INDO
(transmission demand, already net of embedded generation) minus AGWS wind+solar:

- **wind** = FUELHH `WIND` − AGWS wind (onshore + offshore), i.e. metered wind minus the wind the model subtracts.
- **solar** = −AGWS solar. All of it is embedded, and INDO is already net of it.
- **ps** = FUELHH `PS`, signed. Pumping is load that INDO excludes.
- **oil+oth** = `OIL` + `OTHER`.
- **exp** = the sum of negative interconnector flows. Exports are generation that INDO excludes.

| year | days | gap MW | coal | OCGT | bio | must-run | imports | **wind** | **solar** | ps | oil+oth | **exp** | rest |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2017 | 60 | +1193 | +0.93 | +0.00 | +0.16 | +0.00 | +0.00 | −0.01 | +0.02 | −0.00 | −0.00 | −0.04 | −0.06 |
| 2018 | 355 | −1162 | +0.77 | +0.00 | +0.02 | +0.00 | +0.00 | +0.05 | +0.23 | −0.00 | −0.00 | −0.03 | −0.04 |
| 2019 | 351 | −1804 | +0.38 | −0.00 | +0.14 | −0.00 | −0.00 | +0.12 | **+0.40** | −0.01 | +0.01 | −0.01 | −0.04 |
| 2020 | 341 | −1588 | +0.35 | +0.00 | +0.12 | −0.00 | +0.00 | +0.12 | **+0.40** | −0.01 | −0.00 | +0.09 | −0.08 |
| 2021 | 348 | −1616 | +0.23 | +0.01 | +0.14 | −0.00 | +0.08 | +0.16 | **+0.40** | +0.01 | +0.01 | −0.01 | −0.03 |
| 2022 | 292 | −2994 | +0.10 | −0.00 | +0.10 | −0.00 | +0.11 | +0.04 | +0.20 | −0.00 | −0.01 | **+0.45** | +0.02 |
| 2023 | 358 | −616 | +0.03 | +0.00 | +0.09 | +0.00 | +0.00 | **+0.70** | +0.15 | −0.00 | −0.00 | +0.09 | −0.07 |
| 2024 | 361 | +522 | −0.03 | +0.00 | +0.06 | +0.00 | +0.07 | **+1.02** | −0.01 | +0.00 | +0.00 | +0.04 | −0.15 |
| 2025 | 156 | −2434 | +0.00 | +0.01 | +0.14 | +0.00 | +0.19 | +0.10 | +0.30 | +0.00 | +0.02 | +0.20 | +0.04 |

Mean component levels, MW: solar about −1,300 in every full year. Exports −425 (2019) to −2,444
(2022). Wind −282 (2018) to +1,383 (2024).

### What it establishes

**The remainder closes.** `rest` is −0.15 to +0.04 in every year, down from +0.48 to +0.90. The
identity now accounts for the model's daily gas error. The error has three sources outside the
thermal stack, and they take turns:

1. **Solar is subtracted twice, 2018–2022.** INDO is already net of embedded solar, and the model
   subtracts AGWS solar from it again. That costs about 1.3 GW of gas every year and carries 0.40
   of the daily variation in 2019–2021. This matches INDO's published definition. It is a
   definitional error in the model's input, not something the grid did.
2. **Exports, 2022.** GB exported heavily to France that year. INDO excludes exports, so the gas
   that served them is invisible to the model. This carries 0.45 of 2022.
3. **The wind input, 2023–2024.** It carries 0.70 and then 1.02.

PS, OIL and OTHER carry nothing (|slope| ≤ 0.02). The OCGT band still carries nothing.

### The reading that is ODD, and is not built on

§17 named the leading candidate as AGWS wind carrying embedded output that the metered side never
sees, which would make AGWS wind *larger* than metered wind. **The sign is the other way.** From
2019 on, metered FUELHH `WIND` runs above AGWS wind by up to 1.4 GW. By psrType:

| year | FUELHH WIND | AGWS onshore | AGWS offshore | AGWS solar |
|---|---|---|---|---|
| 2020 | 6181 | 2994 | 3067 | 1323 |
| 2022 | 7151 | 3598 | 3044 | 1274 |
| 2023 | 7245 | 2963 | 2939 | 1322 |
| 2024 | 7471 | 3103 | 3003 | 1436 |
| 2025 (part) | 7313 | 3708 | 5297 | 2019 |

**In the cached AGWS series, offshore wind stays flat at about 3 GW from 2020 to 2024 and then jumps
to 5.3 GW in 2025.** GB's offshore fleet was growing through those years, so a flat mean is
not what the industry would expect. There are three possible causes, and **which one it is has NOT
been established**:

- the published AGWS (B1630) series omits units,
- our cache walk dropped rows,
- a psrType was relabelled.

**Cause (b) is excluded for the one week checked.** AGWS for 2023-06-01..06 was re-fetched live
and compared with the cache. Means per psrType agree within 2% (offshore 731 vs 745 MW, onshore 991
vs 997, solar 2752 vs 2733). So the gap sits between two *published* series, not in our walk.
Monthly means make it plain:

| month | FUELHH WIND | AGWS onshore | AGWS offshore |
|---|---|---|---|
| 2023-01 | 10593 | 4676 | 4516 |
| 2023-06 | 4201 | 1471 | 1047 |
| 2024-07 | 4724 | 1496 | 535 |

Transmission-metered wind exceeding onshore+offshore AGWS by 2–3 GW is odd against how the two
series are described. AGWS is meant to be the wider of the two. **This is a question for someone who
knows the trade, not one to build on.** It was put to the director on 2026-09-30.

The rest of cause (a)/(c) is settled by the annual offshore generation in DUKES Table 6.1 against the
AGWS annual sum. That has not been run. Until it is, the "wind" column says only that the model
subtracts less wind than FUELHH metered. It does not say why.

One thing is on record for the fix that follows. FUELHH `WIND` passes both of the adapter's
half-hourly crossing conditions (NESO factor exactly 0, and never negative), so handing it to
`build_shape` *in place of* AGWS wind would be the same class of observable as AGWS itself. It
would not be the answer with a different cache. That is a candidate, not a decision.

### What it does NOT establish

- **Any fix.** §17 NEXT step 2 (an input fidelity correction to `build_shape`) now has three
  candidates rather than one: remove the solar double-subtraction, account for exports, and
  correct the wind input. Each is decided blind to the correlation it moves. The wind one waits on
  the AGWS check above.
- **A joint attribution.** The slopes are one-component-at-a-time shares of the gap, as in §17. They
  sum to about 1 because the identity closes, not because they were fitted jointly.
- **Anything about the correlation ceiling.** This is still a level decomposition, not a rung.

Reproduce: save the §17 script and replace the `metered` list with the one below. It adds
`fuel.load_cached_remainder()` as the fifth cache, skips periods without `WIND`, and appends these
five columns (with `w = aggregate_wind_generation(agws).get(k, 0.0)`, from
`sim.generation_demand_history`):

```python
d["wind"].append(t["WIND"] - w)
d["solar"].append(-(wind[k] - w))
d["ps"].append(t.get("PS", 0.0))
d["oiloth"].append(t.get("OIL", 0.0) + t.get("OTHER", 0.0))
d["exp"].append(sum(v for f, v in t.items() if f.startswith("INT") and v < 0))
```

It runs in about 13 s once the caches exist.

## 19. 2026-09-30 — THE SOLAR CORRECTION, built on the definition and measured after

§18's first candidate is built. The choice rests on INDO's published definition, not on the
correlation it moves. INDO is transmission demand and is already net of embedded generation. GB
solar is embedded. So AGWS solar comes out of the dispatch residual, which was counting it twice.
It goes into the rate's DENOMINATOR instead: the intensity is per MWh *consumed*, and GB consumed
that solar output. NESO's national figure counts embedded solar as zero-carbon supply. Correcting
only the residual would have fixed the gas level and then divided by the wrong demand, so both
halves go in together. The parameter is `embedded_generation_mw` / `embedded_generation_by_period`
in `sim/grid_carbon_intensity.py`, and its default of 0.0 is the old series exactly.

**Prediction, written before the first run.**
- **Level.** The model's gas rises by about the AGWS solar mean (~1.3 GW) in each full year.
  §18's solar column should fall to about 0 when that decomposition is re-run on the corrected model.
- **Correlation with NESO.** Up in every full year 2018–2024, by +0.01 to +0.05, and most in the
  years with the most solar. My confidence in the SIGN is low: the numerator and the denominator
  both move at midday, in opposite directions.

**Named gap, not closed here.** The year's normalisation is still INDO-weighted, so every caller's
`demand_weighted_mean` check still holds on the demand it has. The honest weight is consumption
(INDO plus embedded). That changes one scalar per year, not the shape's correlation. It is left
for the pass that changes the feed's anchor contract.

### The result, measured after the build

Shipped shape against NESO's published series, all half hours, `neso.compare_shapes`. Old means
the pre-fix publishing call (wind+solar in the residual, INDO denominator).

| year | corr old | corr new | MAE old | MAE new | within-day × old | new | between-day × old | new |
|---|---|---|---|---|---|---|---|---|
| 2019 | 0.883 | **0.903** | 0.112 | 0.088 | 1.48 | 1.29 | 1.00 | 0.91 |
| 2020 | 0.869 | **0.884** | 0.133 | 0.115 | 1.46 | 1.32 | 0.95 | 0.93 |
| 2021 | 0.909 | **0.936** | 0.105 | 0.078 | 1.40 | 1.23 | 0.98 | 0.92 |
| 2022 | 0.871 | **0.908** | 0.150 | 0.115 | 1.54 | 1.32 | 0.97 | 0.94 |
| 2023 | 0.795 | **0.800** | 0.204 | 0.193 | 1.47 | 1.28 | 0.98 | 0.95 |
| 2024 | 0.746 | **0.732** | 0.268 | 0.265 | 1.35 | 1.13 | 0.92 | 0.87 |

Mean model-minus-metered CCGT, MW (the level): 2016 −1214 → +32, 2018 −1147 → +80,
2019 −1794 → −579, 2021 −1607 → −490, 2022 −2840 → −1728, 2023 −621 → +536, 2024 +493 → +1728.

**The level prediction held.** Gas rose by 1.1–1.3 GW in every year. 2016–18 now sit within
±80 MW of metered CCGT. The residuals left are §18's other two sources: exports in 2022, and the
short wind input from 2023, which now shows as an OVERSHOOT.

**The correlation prediction was REFUTED in one year.** Correlation rose in 2019–2023 (+0.005 to
+0.037) and FELL in 2024 (−0.013). "Up in every full year" was wrong, and it stays on record here.
MAE fell in every year. So did within-day overstatement: its mean went from 1.45x to 1.26x.
Between-day now reads slightly UNDER the published series (0.87–0.95x). p95/p5 went from 1.38x to
1.31x, and max/min from 1.01x to 1.08x. A likely reading of 2024, **not tested**: it is the year the
wind input overshoots most (+1.7 GW of gas), and raising gas at midday adds weight on the axis
that input already gets wrong. It is the wind question put to the director, and it is not built on.

The feed prose (`NAMED_GAPS`, `ERROR_DIRECTION`) and the module docstring now quote these figures.
`test_the_WITHIN_DAY_FIGURES_QUOTED_in_ERROR_DIRECTION_are_the_MEASURED_ones` holds them to the
feed. New controls: `test_EMBEDDED_generation_never_enters_the_residual_and_only_divides`, the
skip/keep partition beside it, and
`test_EMBEDDED_SOLAR_is_out_of_the_residual_and_in_the_denominator_of_the_published_feed`. Four
mutations ran (renewables back to wind+solar, the embedded keyword dropped, solar subtracted in
the residual, solar out of the denominator) and each one turned a control red.

No level move. The atom's L3 bar (the Expert Hour, s13's 0.97 peer bound) is not reached.

## 20. 2026-09-30 — THE EXPORT CORRECTION, decided on INDO's definition

§18's second candidate. INDO excludes interconnector exports, so the GB generation that served
them was invisible to the dispatch: the model burned gas for GB's own demand only, and 2022 (GB
exporting ~2.4 GW to France on average) read 1.7 GW short of metered CCGT after §19.

**The decision, on the definition, before any run.** Exported MWh were GENERATED here, so they go
into the residual the GB stack dispatches. They also go into the DENOMINATOR: the intensity is
taken over everything the stack and the cables supplied, which is the average-mix convention and
the one NESO's national series is published on (a generation mix plus imports; nothing in it
traces an exported MWh to a plant). Adding exports to the numerator alone WOULD charge exported
emissions to GB demand, which is what `elexon_fuel_outturn.to_settlement_periods` rightly refused;
adding them to both charges the export the half hour's average rate and leaves GB demand the same
average. That docstring's "exports are DROPPED" was a third convention — the export takes the
MARGINAL gas and GB demand keeps the infra-marginal mix — and it is replaced, not kept beside.
Each cable is still clamped individually, so an export on one cable never nets against an import
on another. Pumping (also outside INDO) is not added: §18 measured it at |slope| ≤ 0.02.

**Prediction, written before the first run.**
- **Level.** Model gas rises by about the year's mean export wherever the CCGT band has room:
  2022 from −1728 MW to between +400 and +900 MW against metered CCGT; 2019 from −579 to about
  −150; 2024 overshoots further (+1728 → about +2,000), because the wind input is still short.
- **Correlation with NESO.** |Δ| ≤ 0.02 in every year except 2022. 2022 up by +0.005 to +0.03.
  Low confidence on the sign everywhere: exports and the dilution of the denominator move
  together, so the rate moves less than the gas does.

### The result, measured after the build

Shipped shape (s19 call plus `exports_by_period`) against NESO's published series, all half hours,
`neso.compare_shapes`. Old is the s19 publishing call.

| year | corr old | corr new | MAE old | MAE new | within-day × old | new | between-day × old | new | gas − metered CCGT, MW old → new | mean export MW |
|---|---|---|---|---|---|---|---|---|---|---|
| 2019 | 0.903 | 0.909 | 0.088 | 0.083 | 1.29 | 1.27 | 0.91 | 0.90 | −579 → −178 | 424 |
| 2020 | 0.884 | 0.889 | 0.115 | 0.113 | 1.32 | 1.29 | 0.93 | 0.94 | −533 → −114 | 508 |
| 2021 | 0.936 | 0.936 | 0.077 | 0.077 | 1.23 | 1.19 | 0.92 | 0.92 | −490 → −23 | 507 |
| 2022 | 0.908 | **0.940** | 0.115 | 0.085 | 1.32 | 1.11 | 0.95 | 0.88 | **−1728 → +502** | 2363 |
| 2023 | 0.800 | 0.807 | 0.193 | 0.182 | 1.28 | 1.20 | 0.95 | 0.91 | +536 → +1537 | 1158 |
| 2024 | 0.732 | **0.720** | 0.265 | 0.271 | 1.13 | 1.07 | 0.87 | 0.84 | +1728 → **+2784** | 1209 |

2016–18 and 2025 levels: +32 → +312, −51 → +339, +80 → +368, −1384 → −541. Headline p95/p5
overstatement 1.31x → 1.25x; max/min 1.08x → 1.12x.

**Against the prediction.**
- **Level: held in 2019 and 2022, wrong in size for 2024.** 2022 landed at +502 (band +400..+900),
  2019 at −178 (predicted about −150). 2024 overshoots to +2,784, not about +2,000: I guessed its
  exports from 2022's pattern and did not look them up; they average 1.2 GW. 2016–18, which sat
  within ±80 MW after s19, now read +310..+370 over metered: exports in those years are real
  (0.3–0.4 GW) and something else then compensated. Not attributed here.
- **Correlation: 2022 +0.032, just past the +0.03 bound — refuted at the top end, right in sign.**
  Every other year |Δ| ≤ 0.012 as predicted; 2024 fell again (−0.012), the second correction in a
  row to lower it. 2024 MAE rose (0.265 → 0.271), the only year it did.

**What it establishes.** With solar and exports now on INDO's definition, 2019–2022 sit within
0.6 GW of metered CCGT and 2023–24 overshoot by 1.5 and 2.8 GW. The overshoot is where §18's third
source (the wind input reading short) lives, and it is now the dominant level error by a
distance. Each definitional fix raised it, which is what it should do if the wind input is the
remaining cause; that is consistent with §18, not a test of it.

Controls: `test_an_EXPORT_is_served_by_the_stack_AND_divides_the_rate` (the export is exactly a
half hour with that much more demand), the covered/uncovered partition beside it,
`test_EXPORTS_are_read_per_cable_as_a_positive_MW_and_an_import_never_offsets_one`, and
`test_EXPORTS_are_served_and_divided_by_in_the_published_feed`. Five mutations ran (export out of
the denominator, out of the residual, dropped in `build_shape`, cables netted, dropped in
`generate()`) and each one turned a control red.

No level move. NEXT is unchanged in kind: the wind question is with the director (§18), then
§16's unbalanced rung on the corrected residual, then a second Expert Hour.

## 21. 2026-10-01 — THE AGWS CHECK §18 OWED: the published wind series is short in every year, not from 2023

§18 left one check unrun: DUKES annual offshore generation against the AGWS annual sum, which
separates "the published AGWS series omits units or relabels a psrType" from anything in our
walk. It needed no fetch. The sourced figure was already in the knowledge layer,
`docs/market_research/w1_7_dukes_generation_and_load_factor_annual.json` (DESNZ ET 6.1, fetched
2026-08-03, an independent collection from the Elexon settlement feeds).

AGWS is read from `sim/cache/elexon_agws_full.json`, last row wins per (half hour, psrType),
summed at 0.5 h and scaled to a full year by half-hour coverage. FUELHH `WIND` is read from
`fuel.load_cached_remainder()` in the same way. Both are in GWh.

| year | AGWS cover | AGWS offshore | DUKES offshore | ratio | AGWS onshore | DUKES onshore | ratio | FUELHH WIND |
|---|---|---|---|---|---|---|---|---|
| 2016 | 82% | 10,574 | 16,406 | 0.64 | 16,742 | 20,754 | 0.81 | 21,193 |
| 2017 | 98% | 14,696 | 20,916 | 0.70 | 22,656 | 28,725 | 0.79 | 32,337 |
| 2018 | 99% | 15,360 | 26,525 | 0.58 | 26,216 | 30,382 | 0.86 | 39,413 |
| 2019 | 98% | 19,900 | 31,975 | 0.62 | 24,758 | 31,860 | 0.78 | 46,431 |
| 2020 | 94% | 26,935 | 40,750 | 0.66 | 26,292 | 34,873 | 0.75 | 54,680 |
| 2021 | 96% | 24,967 | 35,597 | 0.70 | 24,454 | 29,327 | 0.83 | 48,954 |
| 2022 | 85% | 26,671 | 45,113 | 0.59 | 31,522 | 35,102 | 0.90 | 61,641 |
| 2023 | 100% | 25,745 | 49,435 | 0.52 | 25,959 | 33,332 | 0.78 | 63,396 |
| 2024 | 100% | 26,380 | 48,805 | 0.54 | 27,256 | 34,813 | 0.78 | 65,642 |

(2025's AGWS covers 43% of the year and is seasonal, so it is not compared.)

**What it establishes.**
- **AGWS offshore is 0.52–0.70 of DESNZ's offshore generation in EVERY year since 2016,** so the
  shortfall is not something that began in 2023. What changes in 2023–24 is its size: the ratio
  falls to 0.52–0.54 while the offshore fleet keeps growing and AGWS stays near 26 TWh. In mean
  MW the missing offshore output is about 1.4 GW in 2019, 2.1 GW in 2022 and 2.7 GW in 2023.
- **Taken together with §18's live re-fetch, our walk is excluded as the cause.** The gap is
  between two published series.
- **FUELHH `WIND` agrees with DESNZ wherever the two can be compared.** It exceeds DESNZ offshore
  in every year, by a margin of 5–16 TWh. That margin is the part of onshore that is
  transmission-connected, which is under half of DESNZ's onshore figure, and that is the expected
  shape. AGWS's total wind (51.7 TWh in 2023) is below transmission-metered wind alone (63.4 TWh),
  whereas DESNZ puts all GB wind at 82.8 TWh. So AGWS is the series that is short. FUELHH is not.

**What it does NOT establish.**
- **Why B1630 under-reports.** Missing BM units, or a psrType mapping, are still both open. That
  part of the question stays with the director as a practitioner question. It no longer blocks
  the definitional decision below.
- **Why 2019–22 sat within 0.6 GW of metered CCGT after §20 while carrying a 1.4–2.1 GW offshore
  shortfall.** Something else compensates in those years and it has not been attributed. So the
  swap below is expected to push 2019–22 UNDER metered CCGT, and that is predicted rather than
  hoped against.

**The decision, on INDO's definition, before any run.** INDO is transmission demand, net of
embedded generation. The wind that serves it is therefore TRANSMISSION-METERED wind, and that is
FUELHH `WIND` by definition. AGWS mixes embedded onshore output, which INDO is already net of,
with an offshore series this check shows is short. §18 recorded that FUELHH `WIND` passes both
crossing conditions (NESO factor 0, never negative). The candidate becomes the decision: swap
the residual's wind to FUELHH `WIND`, and fall back to AGWS for any half hour with no FUELHH
`WIND` reading. Embedded solar stays in the denominator, from AGWS, as in §19.

**Prediction, written before the build.** This is gas minus metered CCGT, in MW, against the §20
row. The model's gas falls by roughly the year's mean of (FUELHH WIND − AGWS wind), less wherever
the must-run floor or the coal band takes the cut instead:
- 2024: from +2,784 to between +1,200 and +1,700. 2023: from +1,537 to between 0 and +500.
- 2022: from +502 to between −300 and +200. 2019–21: down by 0–400 each.
- 2016–18, where AGWS wind runs ABOVE FUELHH (§18: −282 MW in 2018), the model's gas rises by up
  to 300.
- Correlation with NESO: 2023–24 up by +0.01 to +0.04. Every other year |Δ| ≤ 0.015. The sign is
  low-confidence, because §19 and §20 both lowered 2024 against my prediction.

(The prediction above was written at 20:44:43 on 2026-10-01. The measurement script was written
at 20:45:50 and its output at 20:46:04.)

### The result, measured after the build

The shipped call is the §20 call with `renewables = transmission_wind_by_period(agws)`, compared
against NESO's published series with `neso.compare_shapes`. Gas minus metered CCGT is
`ep13_ccgt_level_ceiling.dispatch_rate(demand + exports, wind, …)` against FUELHH `CCGT`, on
every half hour with a CCGT reading. **Instrument check:** the old arm reproduces the §20 table
to the last digit in every year (2019: 0.909, 0.083, −178; 2024: 0.720, 0.271, +2,784).

| year | corr old | corr new | MAE old | MAE new | within-day × old | new | between-day × old | new | gas − metered CCGT, MW old → new |
|---|---|---|---|---|---|---|---|---|---|
| 2019 | 0.909 | 0.948 | 0.083 | 0.070 | 1.27 | 1.23 | 0.90 | 0.98 | −178 → −331 |
| 2020 | 0.889 | 0.931 | 0.113 | 0.098 | 1.29 | 1.20 | 0.94 | 1.01 | −114 → −223 |
| 2021 | 0.936 | 0.958 | 0.077 | 0.065 | 1.19 | 1.13 | 0.92 | 0.93 | −23 → +103 |
| 2022 | 0.940 | 0.969 | 0.085 | 0.065 | 1.11 | 1.13 | 0.88 | 0.97 | +502 → +27 |
| 2023 | 0.807 | **0.969** | 0.182 | 0.074 | 1.20 | 1.13 | 0.91 | 0.98 | +1537 → +148 |
| 2024 | 0.720 | **0.955** | 0.271 | 0.106 | 1.07 | 1.09 | 0.84 | 0.89 | +2784 → **+1273** |

2016–18 and 2025 levels: +312 → +1,151, +339 → +840, +368 → +639, −541 → +815. Headline p95/p5
overstatement 1.25x → 1.19x, max/min 1.12x → 1.09x.

**Against the prediction.**
- **Level: held in 2019, 2020 and 2022–24, wrong in 2021 and 2016–17.** 2024 landed at +1,273
  (band +1,200..+1,700). 2023 landed at +148 (0..+500) and 2022 at +27 (−300..+200). 2021 ROSE by
  126 where I predicted a fall. 2016 and 2017 rose by 839 and 501, not "up to 300": AGWS wind
  runs above FUELHH there by more than §18's 2018 figure suggested, and I did not look.
- **Correlation: refuted in size everywhere, right in sign everywhere.** 2023–24 rose by +0.16
  and +0.24, not +0.01..+0.04. The other years rose by +0.02..+0.04, not |Δ| ≤ 0.015. I modelled
  the wind input as a LEVEL error with a small timing side-effect. It was the largest TIMING
  error left in the model, because the AGWS shortfall is not a constant offset: in 2024-07 AGWS
  offshore read 535 MW against a fleet doing several GW.

**What it establishes.** On INDO's definition of the wind input, the reconstruction's correlation
with NESO is 0.93–0.97 in every year 2019–2024. §13's peer bound (NESO's own forecast) is 0.97.
2022 and 2023 sit at it and 2024 is 0.015 below it. The 2024 decline that §19 and §20 each
deepened was the wind input. Each of those fixes removed an error that had been partly offsetting
it. That reading is consistent with the table, and it was not tested separately.

**What it does NOT establish.**
- **That the timing axis is closed.** 2019–20 are still 0.93–0.95. Within-day swing is still
  overstated in every year (1.09–1.23x). That overstatement is the error direction the feed
  carries on its face, and it still flatters a shifting claim.
- **Independence of the comparison.** NESO's published actual is built from the metered
  generation mix, and FUELHH `WIND` is part of that mix. Imports and must-run already crossed on
  the same terms. Wind is zero-carbon and enters only the residual, so gas is still decided by
  the model's merit order. But some of the correlation gained is agreement between shared inputs,
  and how much has not been measured. The Expert Hour must weigh that before it counts 0.95 as
  fidelity.
- **The level in 2024 (+1.3 GW) and in 2016–17 (+0.8 to +1.2 GW).** Neither is attributed.

Controls: `test_WIND_is_read_alone_from_the_remainder_last_row_wins_and_an_absent_reading_is_absent`,
`test_only_WIND_of_the_remainder_series_reaches_the_dispatch` (re-keyed from "none of it"),
`test_TRANSMISSION_WIND_takes_the_metered_reading_and_falls_back_to_AGWS_only_where_absent` (both
branches asserted reachable), and
`test_the_published_feed_subtracts_TRANSMISSION_METERED_wind_not_AGWS`. Six mutations ran, and
each one turned a control red: AGWS wind back in `generate()`, AGWS winning the merge, the
fallback dropped, the `WIND` filter dropped, the clamp dropped, and the remainder loaded a second
time in the generator.

No level move. The L3 bar is an Expert Hour, and the axis that blocked the last one (0.74–0.91)
is now 0.93–0.97. NEXT: the second Expert Hour, with the shared-input question above put to it
first.
