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
