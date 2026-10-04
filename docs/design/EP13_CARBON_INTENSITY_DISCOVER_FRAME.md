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

## 22. 2026-10-01 — THE SHARED-INPUT NULL: the correlation no longer grades the merit order

§21 asked the second Expert Hour to weigh one thing before it counts 0.95 as fidelity: NESO's
actual is built from the metered mix, and the reconstruction now reads much of that mix. That
weighing is a measurement, so it was run instead of argued.

**The null arm, one variable away from the shipped feed.** Same INDO demand, exports, FUELHH
`WIND` (AGWS fallback), imports at their NESO rates, NUCLEAR+NPSHYD must-run and the AGWS solar
denominator. The whole positive residual then burns at ONE factor, the year's best-efficiency
CCGT rate. Removed: the coal band, the biomass envelope, the thermal floor, the CCGT efficiency
curve and the OCGT tier, which together are the merit order. The script (scratch, not shipped) is
`/var/tmp/se-ep13-s22/measure.py`. **Instrument check:** the shipped arm reproduces §21 to the
last digit (2019: 0.948, 0.070, 1.23; 2022: 0.969; 2024: 0.955, 0.106).

**Prediction, written at 21:12:38 before the script existed.** In 2019–24 the null's
correlation would be 0.00–0.03 BELOW the shipped arm each year, with the sign low-confidence. Its
within-day swing would be lower than the shipped arm's by 0.02–0.10.

| year | corr shipped | corr null | Δ | MAE shipped | null | within-day × shipped | null | between-day × shipped | null | p95/p5 shipped | null | NESO |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2019 | 0.948 | 0.938 | −0.010 | 0.070 | 0.070 | 1.23 | 0.98 | 0.99 | 0.82 | 3.25 | 2.50 | 2.78 |
| 2020 | 0.931 | 0.916 | −0.014 | 0.098 | 0.099 | 1.20 | 1.01 | 1.01 | 0.89 | 3.73 | 3.12 | 3.12 |
| 2021 | 0.958 | 0.956 | −0.002 | 0.065 | 0.073 | 1.13 | 0.93 | 0.93 | 0.81 | 3.42 | 2.65 | 3.26 |
| 2022 | 0.969 | **0.971** | +0.002 | 0.065 | 0.067 | — | — | — | — | — | — | — |
| 2023 | 0.969 | 0.967 | −0.003 | 0.074 | 0.084 | 1.13 | 0.96 | 0.98 | 0.85 | 5.68 | 4.12 | 4.35 |
| 2024 | 0.955 | 0.946 | −0.008 | 0.106 | 0.130 | 1.09 | 0.90 | 0.89 | 0.75 | 6.66 | 4.35 | 5.06 |

2022: the null has one half hour with no fossil and no import, so `compare_shapes` refuses its
spread (correctly). Correlation and MAE there are taken directly, on the same common keys and
the same renormalisation. 2016–18 and 2025 have no NESO overlap to compare.

**Against the prediction.** Correlation held: the null sits 0.002–0.014 below in five years, and
in 2022 it sits 0.002 ABOVE, which is the sign I flagged as uncertain. Within-day swing was
refuted in size: the null is lower by 0.17–0.25, not 0.02–0.10, and it lands on or UNDER NESO
(0.90–1.01) where the shipped arm overstates (1.09–1.23).

**What it establishes.**
- **Almost all of the 0.93–0.97 is the shared-input residual.** Demand minus metered wind,
  imports and nuclear, at a single gas factor, reaches 0.92–0.97 on its own. The model's merit
  order adds at most 0.015 to the correlation, and in 2022 it takes 0.002 away. **Correlation
  with NESO can no longer grade the merit order.** The gains in §19–§21 were input corrections.
  They are real, but they say nothing about whether the dispatch is right.
- **The merit order shows up in the SWING, and there it overshoots.** The null understates
  within-day swing slightly (0.90–1.01x) and between-day swing more (0.75–0.89x). The shipped
  merit order lifts both. Between-day lands near NESO (0.89–1.01). Within-day overshoots to
  1.09–1.23. Within-day is the axis a shifting claim acts on, so the merit order's one visible
  effect on that axis is the error direction that flatters the product.
- **The p95/p5 tells the same story.** The null is at or under NESO in every year. The shipped
  arm is over NESO in 2019, 2020, 2023 and 2024.

**What it does NOT establish.**
- **Which merit-order element carries the within-day overshoot.** The efficiency curve (dirtier
  per MWh at high load) and the OCGT tier are the candidates. The null removed five elements at
  once, so this run cannot attribute it. The next one-variable runs restore them one at a time.
- **That the null is a better published series.** It understates between-day swing by up to a
  quarter, and it is not offered as a replacement.

**For the Expert Hour.** The question §21 put to it is answered: do not count 0.95 as fidelity
of the dispatch. The statistics that can grade the merit order are the within-day and
between-day swing ratios measured against this null, together with §14's per-fuel oracle.
No level move.

**Correction, 2026-10-02 (§23):** the claim above that the merit order's visible effect is a
within-day overshoot was mostly an artefact of the null. The null burned the 2,400 MW biomass
block as gas, and that flattens the swing. With measured biomass in the null, most of the
overshoot is still there. See §23.

## 23. 2026-10-02 — THE ELEMENTS ONE AT A TIME: the null's overshoot was the null's own biomass error

§22 removed five elements at once and could not say which one carries the within-day overshoot.
This pass restores them one at a time. Each element is ADDED to the null alone and REMOVED from
the shipped arm alone. The five are: **B** the biomass block (a flat 2,400 MW at 120 g, because
the shipped feed passes no envelope), **F** the thermal floor, **E** the CCGT efficiency curve,
**C** the coal band and **O** the OCGT tier. The scratch scripts are `/var/tmp/se-ep13-s23/`
(`measure.py`, `oracle2.py`, with the timestamped predictions in `prediction.txt`).
**Instrument check:** with all five on, the reimplementation reproduces the shipped arm's
correlation and within-day ratio to 1e-9 in every year 2019–24 (asserted in the script).

**Prediction 1 (07:30Z, before the script existed).** E would carry the largest share (+0.08–0.15
of within-day), B +0.03–0.08, F would lower it by 0–0.05, and C and O would each move it <0.02.

Within-day swing ratio (reconstruction ÷ NESO):

| arm | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| null | 0.980 | 1.010 | 0.925 | — | 0.958 | 0.901 |
| shipped | 1.227 | 1.199 | 1.132 | 1.135 | 1.125 | 1.091 |
| null + B | 1.172 | 1.212 | 1.099 | 1.128 | 1.118 | 1.065 |
| null + E | 1.044 | 1.062 | 0.978 | — | 0.986 | 0.936 |
| null + F / + C / + O | ≤ +0.004 | | | | | (C +0.025 in 2019) |
| shipped − B | 1.066 | 1.065 | 0.980 | 1.018 | 0.987 | 0.937 |
| shipped − E | 1.165 | 1.145 | 1.079 | 1.097 | 1.098 | 1.059 |
| shipped − F | 1.240 | 1.262 | 1.150 | 1.164 | 1.144 | 1.097 |
| shipped − C / − O | ≤ 0.006 change | | | | | |

**Prediction 1 was refuted on the rank.** B carries +0.16–0.20, and E only +0.03–0.06. F
lowers the swing, as predicted (removing it raises the swing by 0.006–0.063), and C and O are
inert after 2019. Correlation moves ≤0.009 for every element, so it still grades nothing here.

**But B being the biggest switch does not make B the error.** In the null, the biomass block
burns at the gas rate. That error has its own direction: a flat high-carbon block flattens the
relative swing. So the second question is what the RIGHT biomass does. Three ORACLE arms put
measured biomass in place of the flat block. They are measurement only: the half-hourly series
may never reach the shipped dispatch (`elexon_fuel_outturn.biomass_by_period`). FUELHH biomass
averages 1.5–2.2 GW over 2019–24, below the 2,400 MW constant, and it falls to 50–380 MW at its
floor.

**Prediction 2 (written after table 1, before the oracle script).** With measured half-hourly
biomass, within-day would land within 0.05 of 1.00. The year mean would remove less than half
the overshoot, and the envelope would sit between the two.

| arm | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| shipped (flat 2,400) | 1.227 | 1.199 | 1.132 | 1.135 | 1.125 | 1.091 |
| shipped, B = year's measured mean | 1.199 | 1.185 | 1.118 | 1.106 | 1.078 | 1.076 |
| shipped, B = envelope dispatch | 1.276 | 1.220 | 1.174 | 1.164 | 1.170 | 1.152 |
| shipped, B = measured half-hourly (oracle) | 1.168 | 1.171 | 1.093 | 1.081 | 1.061 | 1.026 |
| null, B = measured half-hourly (oracle) | 1.104 | 1.134 | 1.050 | 1.053 | 1.037 | 0.994 |

**Prediction 2 was refuted.** Measured biomass leaves the shipped arm at 1.03–1.17. The year
mean removes 0.01–0.05, and the envelope ADDS 0.02–0.06, so it is not between the two.
**Prediction 3** (the null with measured biomass would sit at 1.00–1.10 and E would add the last
0.03–0.06) held in five years. 2020 came in at 1.134.

**What it establishes.**
- **§22's null was not a fair null.** Its within-day ratio of 0.90–1.01 came from burning
  biomass as gas. A null that carries biomass at its true output and factor reaches 0.99–1.13,
  with no merit order at all.
- **So the overshoot splits three ways** (shipped, 2019–24). Up to 0.13 is in the **shared
  inputs**: it is there before any dispatch. 0.02–0.06 is the **merit order**, almost all of it
  E. 0.03–0.07 is the **biomass block being flat and too high**: shipped against shipped with
  the measured series.
- **The envelope dispatch is the wrong biomass rule for swing.** It adds overshoot in every year,
  which agrees with s10's decision not to ship it.
- **The permitted biomass correction is the year's measured mean** (an annual scalar, coal's
  grain). It is worth 0.01–0.05 of within-day and leaves correlation within 0.001. It is small,
  and it is a candidate build, not yet built: it moves the published feed, so it needs its own
  pass.

**What it does NOT establish.**
- **Which shared input carries the remaining 0.0–0.13.** 2019–21 carry the most. The candidates
  are the denominator and the demand definition: NESO's denominator includes embedded wind and
  solar estimates, and the model's has AGWS solar but no embedded wind. Pumped storage, which
  sits in neither, is another candidate. That is the next one-variable run, on the fair null.
- **Whether the overshoot matters at the grain a customer acts on.** The ratio is national and
  half-hourly. A shifting claim reads the gap between particular half hours.

**For the Expert Hour.** Grade the swing against the FAIR null (measured biomass), not §22's.
The merit order's own contribution to within-day swing is 0.02–0.06, and the dispatch rule is
not where most of the swing error lives. No level move.

## 24. 2026-10-02 — THE SHARED INPUTS, ONE AT A TIME: the swing error is a missing fleet, pumped storage, on both legs

§23 left 0.0–0.13 of within-day overshoot in the shared inputs, before any dispatch, and named
two candidates: embedded wind in the denominator, and pumped storage. This pass adds each to
§23's FAIR null (measured half-hourly biomass, the whole residual at the year's best CCGT rate).
The scratch scripts are `/var/tmp/se-ep13-s24/` (`measure.py`, `pump.py`, `shipped.py`, with
the timestamped predictions in `prediction.txt`). **Instrument checks:** the fair null reproduces
§23's `null B=meas` row to 0.0006 in every year, and the shipped reimplementation reproduces the
published feed to 1e-9 (both asserted in the scripts).

**The arms, and what each one is on NESO's definition.**
- **P: PS generation**, FUELHH, served at zero carbon (NESO's factor is 0) and taken off the
  residual. It is not added to the denominator, because PS output serves INDO demand and is
  already inside it. It averages 166–220 MW over a year, about 900 MW in the evening peak.
- **P′: P plus pumping.** FUELHH PS goes negative when it pumps, at 220–290 MW a year and about
  1 GW overnight. INDO excludes pumping, but GB generates it, and NESO's mix counts that
  generation. So pumping is added to load, the same way §20 added exports.
- **W: NESO's embedded wind estimate** (`sim/neso_embedded_generation.py`), 1.65–2.06 GW a
  year, added to the denominator as §19 did for solar. It is generation under the metering point.
  NESO's denominator carries it.

**Predictions (07:41Z, before the script existed).** P1: P lowers within-day by 0.02–0.06 in
every year. P2: P does not carry the year pattern (its effect spreads <0.03 across years). W1: W
moves within-day by <0.03, leaning up. The arms add to within 0.01, correlation moves <0.01, and
2019–20 keep 0.05–0.10 of overshoot after P. **Addendum, after that table and before `pump.py`:**
P′ lowers within-day a further 0.01–0.03 beyond P.

Fair null, within-day swing ratio (reconstruction ÷ NESO):

| arm | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| fair null | 1.104 | 1.134 | 1.050 | 1.053 | 1.037 | 0.994 |
| + P | 1.060 | 1.091 | 1.006 | 1.005 | 0.996 | 0.951 |
| + W | 1.158 | 1.191 | 1.094 | 1.096 | 1.072 | 1.031 |
| + P + W | 1.114 | 1.149 | 1.051 | 1.048 | 1.032 | 0.989 |
| + P′ | 0.946 | 0.984 | 0.898 | 0.907 | 0.902 | 0.844 |
| **+ P′ + W** | **1.004** | **1.045** | **0.946** | **0.955** | **0.941** | **0.886** |

Between-day for + P′ + W: 0.957, 1.015, 0.940, 0.950, 0.938, 0.840 (fair null 0.80–0.94).
Correlation for + P′ + W: 0.933–0.982 (fair null 0.926–0.972).

**Against the predictions.** P1 and P2 held: P lowers within-day by 0.043–0.048, and the spread
across years is 0.005. W1 held on the sign and was refuted on the size: +0.035 to +0.057.
Additivity held (P + W is within 0.005 of the sum). Correlation held: every arm moves it by
<0.01 except P′, which moves it by up to 0.013. The 2019–20 residual after P held (0.060, 0.091).
**The addendum was refuted by a factor of about five.** Pumping lowers within-day by a further
0.10–0.11 beyond P in every year. It is overnight load in the troughs, served at the gas rate,
so it lifts exactly the half hours the swing is measured from.

**On the shipped merit order** (biomass at the year's measured mean, the permitted correction
from §23). **Prediction 3 (written before `shipped.py`):** with P′ + W added, within-day lands
at 0.95–1.10 in every year, and between-day lands within 0.10 of 1.00.

| shipped arm | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| shipped (published feed) | 1.227 | 1.199 | 1.132 | 1.135 | 1.125 | 1.091 |
| B = year mean | 1.199 | 1.185 | 1.118 | 1.106 | 1.078 | 1.076 |
| B = year mean + P′ | 1.034 | 1.065 | 0.969 | 0.967 | 0.949 | 0.927 |
| **B = year mean + P′ + W** | **1.090** | **1.123** | **1.015** | **1.012** | **0.987** | **0.965** |

Between-day for the last row: 1.038, 1.103, 0.990, 1.019, 0.990, 0.917. Correlation:
0.934–0.980, up 0.003–0.015. **Prediction 3 held in five years and was refuted in 2020**
(within-day 1.123, between-day 1.103). 2020 is the COVID demand year, and it is the one year
the fair null also leaves over NESO.

**What it establishes.**
- **Most of the within-day overshoot is a missing fleet.** The reconstruction has no pumped
  storage. Its peak generation displaces gas, and its overnight pumping adds load in the
  troughs. Together they are worth 0.14–0.16 of within-day swing in every year. That is about
  three times the merit order (§23: 0.02–0.06), and more than every other element measured
  across §22–§24.
- **Embedded wind is definitionally owed, and it pushes the other way.** It belongs in the
  denominator on NESO's definition, and it lifts both swings by 0.04–0.09. Built alone it would
  make the published within-day overshoot WORSE, which is why it waits for PS.
- **The 2024 level gap is not addressed here.** These are shape ratios, renormalised per year.

**What it does NOT establish.**
- **That P′ can be built as measured.** Half-hourly PS is refused by `elexon_fuel_outturn`'s
  condition 2: it goes negative, so it is a dispatch decision, which makes it the merit order
  wearing a zero factor. P′ is an ORACLE. The buildable form is the model's own PS rule: pump in
  the troughs, generate at the peaks, with the year's measured energy as an annual scalar (coal's
  grain). P′ is the ceiling on what that rule can recover. It is not what the rule will recover.
- **That pumping is served by gas.** The null burns all residual load at one gas rate. Some
  overnight pumping is in fact served by surplus wind, so P′ may overstate how much pumping
  lifts the troughs.

**Candidate build, in order:** (1) a PS rule inside the merit order, at the annual grain,
graded against the P′ oracle row above; (2) embedded wind in the denominator, landed WITH (1) or
after it, never alone; (3) biomass at the year's mean (§23). Each moves the published feed, so
each needs its own pass. No level move and no code change.

## 25. 2026-10-02 — PUMPED STORAGE, BUILT AS A RULE: the oracle is not a ceiling, and the within-day error changes sign

§24 named the build: a PS rule inside the merit order, at the annual grain, graded against the
P′ oracle. This pass built it, graded it, and wired it into the published feed. Scratch scripts
are in `/var/tmp/se-ep13-s25/` (`rule.py`, `timing.py`, `feed.py`, with timestamped predictions
in `prediction.txt`). **Instrument checks:** each rule spends exactly the year's measured PS
energy on both legs, and the no-PS shape reproduces the committed feed's records to five places.

**What crosses.** PS fails condition 2, so only coal's grain crosses:
`elexon_fuel_outturn.pumped_storage_by_year` gives four scalars a year (mean generation, mean
pumping, largest of each). No half-hourly PS reading reaches the dispatch.

**Two rules, run before choosing.** R1, a rectangle: generate at the year's largest output in
the day's highest-residual half hours until the day's energy is spent, and pump the same way in
the lowest. R2, a water-fill: shave the day's residual peak down to one level and fill its
trough up to another, each leg capped at the year's largest. The residual is the load after
imports and the zero-carbon must-run.

**Predictions (14:22Z, before `rule.py`).** P1: R2 recovers 60–100% of the oracle's within-day
cut in every year. P2: R1 recovers less than R2 in every year. P3: neither moves correlation by
more than 0.015 or between-day by more than 0.03. P4: R2 overshoots the oracle in at most one year.

On §24's base (biomass at the year mean), within-day swing ratio:

| arm | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| B=mean | 1.199 | 1.185 | 1.118 | 1.106 | 1.078 | 1.076 |
| + P′ (measured PS, the oracle) | 1.034 | 1.065 | 0.969 | 0.967 | 0.949 | 0.927 |
| + R1 | 1.029 | 1.053 | 0.955 | 0.938 | 0.932 | 0.904 |
| + R2 | 1.010 | 1.042 | 0.937 | 0.927 | 0.913 | 0.889 |

Share of the oracle's cut recovered: R1 1.03–1.21, R2 1.15–1.29.

**Against the predictions.** P1 was refuted on the high side: R2 recovers 115–129%, not 60–100%.
P2 held: R1 cuts less than R2 in every year. P3 held: correlation moved ≤0.009, between-day
≤0.011. P4 was refuted: R2 overshoots in all six years. **So §24's claim that P′ is "the ceiling
on what the rule can recover" is wrong.** A rule with perfect foresight of the day's residual
flattens the day MORE than GB's fleet did. Real PS also holds reserve and answers to price and
frequency, so it does not sit only on the residual's extremes.

**Choosing the rule, on timing and not on the grade.** Half-hourly correlation of each rule's PS
against measured PS (`timing.py`): R1 0.54–0.69, R2 0.67–0.81, so R2 is higher in every year.
By settlement-period band (2019–24 pooled, measured / R1 / R2, MW): overnight SP07–12 −917 /
−1,089 / −969; evening SP37–42 630 / 880 / 818; midday SP25–30 1 / −100 / −81. Both rules pump
a little into the midday solar trough, where GB does not, and both over-generate at the evening
peak. **R2 is built** (`grid_carbon_intensity.pumped_storage_schedule`).

**On the published order (flat 2,400 MW biomass).** **Prediction P5 (written before
`feed.py`):** within-day lands at 1.02–1.07 / 1.04–1.08 / 0.94–0.98 / 0.92–0.96 / 0.92–0.96 /
0.88–0.92; correlation rises 0.003–0.012; between-day moves <0.02.

| published feed | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| within-day, HEAD | 1.227 | 1.199 | 1.132 | 1.135 | 1.125 | 1.091 |
| **within-day, s25** | **1.038** | **1.058** | **0.951** | **0.957** | **0.959** | **0.904** |
| between-day, s25 | 0.982 | 1.030 | 0.929 | 0.978 | 0.988 | 0.894 |
| correlation, HEAD → s25 | .948→.958 | .931→.933 | .958→.964 | .970→.975 | .969→.972 | .955→.959 |

P5's within-day held in every year, and between-day held. Correlation rose in every year, but
2020's +0.002 is under the predicted 0.003 floor, so that leg was refuted narrowly. Headline
means: within-day 1.15x → 0.98x; p95/p5 1.19x → 1.07x; max/min 1.09x → 0.99x; mean absolute
error 0.080 → 0.074.

**What it changes on the page.** The error-direction sentence said the within-day swing was too
wide in every year, so any shifting benefit was an upper bound. That is no longer true. It is too
wide in 2019–20 and too narrow in 2021–24. `ERROR_DIRECTION` now says so, and its control reads
the wide and narrow years back out of the sentence against the feed, instead of asserting
`min(within) > max(between)`. That old assertion went red on this change, correctly.

**What it does NOT establish.**
- **That the narrow years are right.** The rule's foresight and its pumping into the solar trough
  both narrow the day. The understatement from 2021 is partly the rule's own error, not fidelity.
- **Embedded wind is still owed** (§24: +0.04–0.06 within-day, on NESO's definition). With PS now
  in, nothing in §24's sequencing stops it, and it would move 2021–24 back toward 1.0.

**Controls.** Five new or re-keyed. Six mutations were run and all were killed: pumping left out
of the load, the generation cap dropped, the water-fill bisection inverted, pumping signed
negative in the reducer, the schedule not handed to the rate, and PS dropped from `generate()`.

**Next.** (1) Embedded wind in the denominator, its own pass, graded by §24's arithmetic.
(2) Then biomass at the year's mean (§23). No level move: the Expert Hour still has to weigh how
much of the 0.93–0.98 correlation is shared inputs (§22).

## 26. 2026-10-02 — EMBEDDED WIND, IN THE DENOMINATOR: the within-day error is now centred, and the between-day swing is too wide

§24 measured embedded wind as owed on NESO's definition, and §25 named it as the next pass.
INDO is net of embedded wind in the same way it is net of embedded solar, so the dispatch does
not change: the tonnes are identical and only the divisor moves. `generate()` now hands
`build_shape` AGWS solar plus NESO's `EMBEDDED_WIND_GENERATION`
(`generate_grid_intensity_feed.embedded_generation_by_period`). The scratch script and the
timestamped predictions are in `/var/tmp/se-ep13-s26/` (`feed.py`, `prediction.txt`).

**Coverage first.** The NESO cache held 2018–2025 only, and `build_shape` skips any half hour
the embedded map lacks, so wiring it unchanged would have dropped 2016–17 from the feed. The two
pinned resources were fetched from the real CKAN datastore (17,568 and 17,520 periods) and
appended to `sim/cache/neso_embedded_generation.json`. That cache is gitignored, so this is a
step to repeat on a fresh checkout (`python3 -m sim.neso_embedded_generation`, all years). After
the fetch, every AGWS solar half hour has a NESO wind reading: none is dropped, and the feed
still covers 157,125 half hours. The bound instrument reads per year, so its 2018–25 figures do
not move. NESO embedded wind averages 1.2 GW (2016) to 2.1 GW (2020) over a year.

**Predictions (15:22Z, before `feed.py`).** P1: within-day rises +0.035 to +0.060 in every year.
P2: between-day rises +0.02 to +0.09 in every year. P3: correlation moves <0.010. P4: the headline
within-day mean goes 0.98x → 1.01–1.04x, and p95/p5 goes 1.07x → 1.08–1.13x. P5: 2021–23
within-day end within 0.03 of 1.00, and 2024 stays under 0.97.

| published feed | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| within-day, s25 | 1.038 | 1.058 | 0.951 | 0.957 | 0.959 | 0.904 |
| **within-day, s26** | **1.092** | **1.115** | **0.996** | **1.000** | **0.995** | **0.941** |
| between-day, s25 → s26 | .982→1.065 | 1.030→1.123 | .929→1.006 | .978→1.049 | .988→1.041 | .893→.946 |
| correlation, s25 → s26 | .9575→.9592 | .9334→.9317 | .9635→.9659 | .9751→.9773 | .9721→.9741 | .9585→.9594 |
| mean abs error, s25 → s26 | .058→.063 | .093→.105 | .061→.059 | .058→.058 | .070→.071 | .105→.101 |

Headline: within-day mean 0.98x → 1.02x; between-day mean 0.97 → 1.04; p95/p5 1.07x → 1.18x;
max/min 0.99x → 1.12x.

**Against the predictions.** P1 held: +0.036 to +0.057. P3 held: correlation moved ≤0.003. P5
held. P4 held on the within-day mean (1.02x) and **was refuted on p95/p5**: it is 1.18x, not
1.08–1.13x. P2 held in five years and **was refuted narrowly in 2020** (+0.093). The p95/p5 miss
has the same cause as the between-day rise. Embedded wind is large on windy days, which the
model already reads as clean, so dividing by it makes clean days cleaner. That widens the
distribution between days more than within them. p95/p5 is a whole-year statistic and the
between-day spread dominates it.

**What it changes on the page.** Within-day is now too wide in 2019–20, MATCHED to two places in
2021–22, and too narrow in 2023–24. 2022 sits at 1.0003. The direction control asked `> 1.0` on
the unrounded value, so it would have called 2022 too wide. It now reads each year at the two
places the sentence prints, and asks for three sides (wide, matched, narrow), with every headline
year on exactly one. `ERROR_DIRECTION` says the shifting benefit is an upper bound in 2019–20,
about right in 2021–22, and an understatement in 2023–24. It also says p95/p5 is 1.18x and that
most of it is between days.

**What it establishes.** Every definitional input §18–§24 named is now in the denominator:
embedded solar, exports and embedded wind. On the axis a household acts on, the mean error is
+0.02. 2019–20 are still wide by 0.09–0.11, and 2024 is still narrow by 0.06.

**What it does NOT establish.**
- **That the between-day width is a new error.** Before s26 the between-day swing was narrow in
  most years, partly because the denominator was short on windy days. It now overshoots in five
  years of six. Two things may be behind that: the fixed 2,400 MW biomass block, which §23 named
  and which runs flat through windy days, and the PS rule's foresight. Neither has been measured
  on this axis, so the cause cannot yet be named.
- **That NESO's embedded wind estimate is right.** It is a weather-model estimate, not a meter
  read (see `sim/neso_embedded_generation.py`). A gain measured against it is a gain against
  NESO's estimate.

**Controls.** Two new: the published records carry the shape that divides by wind and solar,
not solar alone; and both branches of `embedded_generation_by_period` (sum where NESO covers the
half hour, absent where it does not). The direction control was re-keyed to three sides at the
printed precision. Mutations: wind dropped from the sum (killed by 2), solar kept where NESO
has no wind (killed by 1), and `generate()` reverted to solar alone with the feed regenerated
(killed by 2).

**Next.** (1) Biomass at the year's measured mean (§23), now graded on BETWEEN-day as well as
within, because the flat block is the first candidate for the new between-day overshoot.
(2) The 2024 level, +1.3 GW and still unattributed. No level move: the Expert Hour still has to
weigh the shared-input share of the correlation (§22).

## 27. 2026-10-02 — BIOMASS AT THE YEAR'S MEASURED MEAN: the flat block carries the right energy, and the within-day mean lands on 1.00

§23 named the year's measured mean as the permitted biomass correction (an annual scalar, coal's
grain), and §26 asked for it to be graded on between-day as well. The block stays FLAT: both
envelope ends are set to FUELHH's `mean_mw` (`generate_grid_intensity_feed.biomass_flat_at_year_mean`),
which `emissions_rate_t_per_mwh` collapses to a constant. So this decides nothing about WHEN
biomass ran, and `BIOMASS_DISPATCH_WIRED` stays False. The mean was chosen on definition, as the
one flat level that carries the year's measured biomass energy, and not on fit. `build_shape`
used to warn `mean_mw` off as the figure a goal-seeker would reach for; that warning was about
using it as an envelope END, and it is now worded that way. 2016 has no envelope and keeps
2,400 MW. 2017's mean comes from Nov–Dec only (2,887 half hours). Scratch and the timestamped
predictions are in `/var/tmp/se-ep13-s27/` (`measure.py`, `prediction.txt`). **Instrument check:**
the reimplementation's s26 arm reproduces the committed feed's records to five places.

The means for 2019–24 are 1,965 / 2,048 / 2,170 / 1,708 / 1,526 / 2,142 MW, all below 2,400. The
`MUST_RUN_BIOMASS_MW` comment and the module's history said 2024's outturn "averages nearer
2.7 GW". FUELHH says 2,142 MW, and both places are corrected beside the claim.

**Predictions (22:28Z, before `measure.py`).** P1: within-day falls in every year by
0.010–0.055, with the largest fall in 2023 or 2022. P2: between-day falls in every year by
0.010–0.060, in the same rank order. P3: correlation moves <0.003. P4: the within-day mean goes
1.02x → 0.99–1.01x and p95/p5 goes 1.18x → 1.10–1.16x. P5: 2024 moves away from 1.0, to
0.920–0.935, and 2019–20 stay above 1.04.

| published feed | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| within-day, s26 | 1.092 | 1.115 | 0.996 | 1.000 | 0.995 | 0.941 |
| **within-day, s27** | **1.064** | **1.097** | **0.983** | **0.972** | **0.950** | **0.926** |
| between-day, s26 → s27 | 1.065→1.048 | 1.123→1.111 | 1.006→.997 | 1.049→1.027 | 1.041→1.002 | .946→.934 |
| correlation, s26 → s27 | .9592→.9592 | .9317→.9307 | .9659→.9658 | .9773→.9775 | .9741→.9736 | .9594→.9590 |
| mean abs error, s26 → s27 | .063→.061 | .105→.104 | .059→.059 | .058→.056 | .071→.069 | .101→.102 |

Headline: the within-day mean goes 1.02x → 1.00x, between-day 1.04 → 1.02, and p95/p5 1.18x →
1.13x. **max/min goes 1.12x → 1.21x, which is worse and was not predicted.**

**Against the predictions.** P1 held: −0.013 to −0.044, largest in 2023. P3 held (≤0.001). P4
held. P5 held. P2 held on the sign in every year and on the size in five. **It was refuted in
2021, at −0.009 against a −0.010 floor.** The rank held: 2023, 2022, 2019, then the rest.
max/min is two half hours wide, and nothing here was run to say why it moved.

**What it changes on the page.** Within-day is now too wide in 2019–20 and too narrow in
2021–24. No year rounds to 1.00, so the MATCHED side of the direction control is empty. A
shifting benefit computed here is an upper bound in 2019–20 and an understatement from 2021,
by 0.02–0.07 of the swing. Between-day is still over 1.0 in four years of six (2019, 2020,
2022, 2023), by 0.002–0.11.

**What it does NOT establish.**
- **Why between-day still overshoots in 2019–20.** The year mean takes out 0.01–0.04 and leaves
  2020 at 1.11. The PS rule's foresight (§25) is the named candidate left, and it has not been
  run on between-day.
- **That a flat block is right.** GB's fleet runs at 0.2–3.1 GW within a year (p1–p99). Its
  timing is an outage question, refused at condition 1 and unmodelled.

**Controls.** Two new: the published records are the year-mean shape and not the 2,400 MW one;
and the helper puts the mean at both ends, while a year it is not given keeps 2,400 MW. Two
mutations, both killed: `generate()` passed `None`, with the feed regenerated, and the helper
passing `capacity_mw` through as the top end. The `SHAPE_BASIS` control now asks for the
"FLAT block, held at the fleet's measured annual mean" wording.

**Next.** (1) The PS rule's foresight, graded on between-day. (2) The 2024 level, +1.3 GW and
still unattributed. No level move: the Expert Hour still has to weigh the shared-input share of
the correlation (§22).

## 28. 2026-10-03 — PUMPED STORAGE ON THE BETWEEN-DAY AXIS: the rule's foresight is not why 2019–20 swing too wide between days

§27 named the PS rule's foresight as the one candidate left for the between-day overshoot
(2019 1.048, 2020 1.111). This pass measured it and built nothing. Scratch and the timestamped
predictions are in `/var/tmp/se-ep13-s28/` (`measure.py`, `prediction.txt`, `out.txt`).
**Instrument check:** the shipped-rule arm reproduces the committed feed's records to five places.

**Four arms on the s27 base**, with `pumped_storage_schedule` swapped in-process and nothing else
changed. N: no PS. O: measured half-hourly PS, the oracle (refused at condition 2, so it is
scratch only). R2: the shipped water-fill. D: R2's water-fill, but each day spends THAT day's
measured generation and pumping energy instead of the year's mean. D separates the rule's
within-day placement from its even split of energy across days.

**Predictions (23:07Z, before `measure.py`).** P1: between-day |R2 − O| < 0.015 in every year.
P2: between-day |R2 − N| < 0.015 in every year. P3: O leaves 2020 above 1.08. P4: within-day
O > R2 in every year, by 0.02–0.05. P5: D sits between O and R2 on within-day in at least 4 of 6.

| between-day | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| N no PS | 1.054 | 1.100 | 0.996 | 1.025 | 1.001 | 0.931 |
| **R2 shipped** | **1.048** | **1.111** | **0.997** | **1.027** | **1.002** | **0.934** |
| O oracle | 1.038 | 1.103 | 0.990 | 1.019 | 0.990 | 0.917 |
| D day energy | 1.037 | 1.105 | 0.990 | 1.020 | 0.991 | 0.919 |

| within-day | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| N no PS | 1.252 | 1.242 | 1.163 | 1.148 | 1.114 | 1.110 |
| **R2 shipped** | **1.064** | **1.097** | **0.983** | **0.972** | **0.950** | **0.926** |
| O oracle | 1.090 | 1.123 | 1.015 | 1.012 | 0.987 | 0.965 |
| D day energy | 1.055 | 1.097 | 0.983 | 0.970 | 0.945 | 0.924 |

Correlation: R2 .959/.931/.966/.978/.974/.959; O is +0.003 to +0.006 above it, D +0.001 to
+0.004, N −0.001 to −0.004.

**Against the predictions.** P2 held (≤0.012). P3 held: the oracle leaves 2020 at 1.103. P4
held: O is 0.026–0.041 wider within the day. P1 held in 2019–23 (≤0.012) and **was refuted in
2024 at 0.017**. P5 **was refuted**: D sits at or below R2 within the day in five years of six,
not between O and R2.

**What it establishes.**
- **PS is not the between-day cause.** With GB's real PS dispatch, 2019 is still 1.04 and 2020
  1.10. Taking PS out entirely moves between-day by ≤0.012. So the 2019–20 overshoot is somewhere
  else, and §26 is where it appeared: embedded wind in the denominator raised between-day by
  +0.04 to +0.09, the largest move on that axis of any pass. It is now the leading candidate,
  and it is NESO's weather-model estimate, not a meter read.
- **What the rule gets wrong between days is the even energy split, not the foresight.** D and O
  agree on between-day to within 0.002 in every year. Once each day carries its true energy, the
  rule's between-day error is gone. Its remaining gap to O, 0.007–0.017, is the year-mean energy
  spent the same every day.
- **The within-day overshoot is all placement.** Handing the rule the true daily energy narrows
  the day slightly further, not less. So the 115–129% of §25 comes from where in the day the
  rule puts the energy (foresight, and answering only to the residual), not from how much.

**What it does NOT establish.**
- **That a daily-energy rule is buildable.** A day's measured PS energy is a dispatch decision at
  a daily grain, and condition 2 refuses it the same way it refuses the half hour. A rule that
  set the day's energy from the day's own residual spread would cross nothing. It is worth at
  most 0.007–0.017 between-day and +0.001–0.004 correlation, so it is not the next pass.
- **That embedded wind is the cause.** It is named from §26's table, not measured on this base.

**Controls.** None. Nothing shipped changed, and the feed is byte-identical.

**Next.** (1) Embedded wind on the between-day axis: on the s27 base, NESO's estimate against
its per-year scaled mean, and against none, graded on between-day and p95/p5. (2) The 2024 level,
+1.3 GW and still unattributed. No level move: the Expert Hour still has to weigh the
shared-input share of the correlation (§22).

## 29. 2026-10-03 — EMBEDDED WIND ON THE BETWEEN-DAY AXIS: the overshoot is carried by WHEN the wind blows, and the meters agree with NESO on when

§28 put embedded wind first in line for the between-day overshoot (2019 1.048, 2020 1.111). This
pass measured it and built nothing. Scratch and the timestamped predictions are in
`/var/tmp/se-ep13-s29/` (`measure.py`, `prediction.txt`, `out.txt`). **Instrument check:** the
shipped arm reproduces the committed feed's records to five places.

**Four arms on the s27 base**, with only the embedded map passed to `build_shape` changed. S: the
shipped map, AGWS solar plus NESO's embedded wind each half hour. W0: solar only. WM: NESO's
wind held flat at its own year mean, so the energy is right but there is no timing. WT: metered
transmission wind (FUELHH) scaled each year to NESO's embedded energy, so the timing comes from
meters and not from NESO's weather model. NESO's embedded wind averages 1.65–2.06 GW over
2019–24.

**Predictions (01:55Z, before `measure.py`).** P1: between-day W0 < S by 0.03–0.09 in every
year, with 2020 landing 1.02–1.08. P2: between-day |WM − W0| < 0.015 in every year. P3:
between-day |WT − S| < 0.02 in every year. P4: headline p95/p5 W0 1.06–1.10x, S 1.13x. P5:
correlation W0 below S by 0.000–0.005 in every year.

| between-day | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| **S shipped** | **1.048** | **1.111** | **0.997** | **1.027** | **1.002** | **0.934** |
| W0 solar only | 0.963 | 1.019 | 0.920 | 0.955 | 0.948 | 0.881 |
| WM wind flat | 0.974 | 1.026 | 0.926 | 0.957 | 0.953 | 0.889 |
| WT metered timing | 1.051 | 1.116 | 1.005 | 1.033 | 1.005 | 0.928 |

| within-day | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| **S shipped** | **1.064** | **1.097** | **0.983** | **0.972** | **0.950** | **0.926** |
| W0 solar only | 1.009 | 1.040 | 0.937 | 0.927 | 0.914 | 0.889 |
| WM wind flat | 1.043 | 1.070 | 0.962 | 0.938 | 0.923 | 0.904 |
| WT metered timing | 1.071 | 1.102 | 0.989 | 0.978 | 0.955 | 0.931 |

Headline p95/p5 (max/min): S 1.13x (1.21x), W0 1.02x (1.06x), WM 1.04x (1.08x), WT 1.13x
(1.20x). Correlation: S .959/.931/.966/.978/.974/.959; W0 is 0.001–0.002 below it except
2020 (+0.002), WM is −0.004 to +0.005, and WT is −0.004 to −0.001. Mean absolute error is lower
without timed wind in 2019–20 (W0 .057/.093 against S .061/.104) and higher in 2021–24.

**Against the predictions.** P2 held (≤0.012). P3 held (≤0.008). P1 held in five years and **was
refuted in 2020**: S − W0 is 0.093, and W0 lands at 1.019, just under the 1.02 floor. P4 held on
S and **was refuted on W0**: without embedded wind p95/p5 is 1.02x, narrower than predicted. So
nearly all of s26's p95/p5 rise came from wind. P5 **was refuted in 2020**, where W0 correlates
better than S.

**What it establishes.**
- **The between-day overshoot is carried by the TIMING of embedded wind, not its energy.** Adding
  the year's embedded energy flat moves between-day by ≤0.012. Putting it on the right days moves
  it +0.05 to +0.09. Without timed wind, between-day is narrow in every year but 2020.
- **NESO's timing is not the error.** Metered transmission wind, scaled to the same energy,
  reproduces NESO's between-day to 0.008 and p95/p5 exactly. The between-day effect comes from
  real windiness, not from NESO's weather model.
- **So the overshoot is not in the denominator input. It is in what the model does on windy days.**
  Embedded wind is owed by definition (§24) and its timing is corroborated by meters. Once it is
  in the denominator, windy days come out cleaner relative to calm days than NESO publishes them.
  The model therefore over-cleans windy days, or under-cleans calm ones, in the numerator, and it
  did so before s26 too: the old short denominator was hiding it.

**What it does NOT establish.**
- **That NESO's embedded wind ENERGY is right.** WT borrows NESO's annual energy, so magnitude is
  untested. A DUKES check on embedded wind energy, like §21's AGWS check, is the cheap test. If
  NESO runs high, part of the overshoot is magnitude.
- **Which part of the numerator over-cleans windy days.** Candidates are gas displaced too
  readily on windy days (the merit order's swing, §23) and interconnector imports that do not
  track wind. Neither was run here.

**Controls.** None. Nothing shipped changed, and the feed is byte-identical.

**Next.** (1) DUKES embedded-wind energy against NESO's annual estimate, per year (the magnitude
leg this pass could not test). (2) The numerator on windy days: emissions per MWh of residual,
binned by wind decile, against NESO's implied figure. (3) The 2024 level, +1.3 GW and still
unattributed. No level move: the Expert Hour still has to weigh the shared-input share of the
correlation (§22).

## 30. 2026-10-03 — EMBEDDED WIND'S MAGNITUDE AGAINST DESNZ: NESO is not high, so the energy is not the overshoot

§29 left the magnitude leg open: WT borrowed NESO's annual embedded energy, so if NESO ran high,
part of the between-day overshoot would be magnitude. This pass measured it and built nothing. No
fetch. Scratch and the timestamped predictions are in `/var/tmp/se-ep13-s30/` (`measure.py`,
`prediction.txt`, `out.txt`).

**The quantity.** DESNZ does not publish embedded wind as such. It publishes all wind
(`docs/market_research/w1_7_dukes_generation_and_load_factor_annual.json`, ET 6.1, onshore plus
offshore). FUELHH `WIND` is the transmission-metered part (§21 showed it agrees with DESNZ wherever
the two can be compared). So **DESNZ-implied embedded wind = ET 6.1 total wind − FUELHH WIND**,
per calendar year. NESO's figure is the annual sum of `wind_mw` in the cached embedded series.
Both caches cover 100% of the half hours in every year. **The bases differ:** ET 6.1 is UK, so it
includes Northern Ireland; FUELHH and NESO are GB. Northern Ireland's wind output is not in the
knowledge layer, so the implied figure is an upper bound on GB embedded wind, by an unsized amount.

**Predictions (02:15Z, before `measure.py` was written).** P1: NESO / implied lies in 0.75–1.00
in every year 2019–24. P2: NESO never exceeds the implied UK figure. P3: the ratio varies by less
than 0.15 across 2019–24.

| GWh | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|---|
| ET 6.1 wind (UK) | 37,159 | 49,641 | 56,908 | 63,835 | 75,623 | 64,924 | 80,214 | 82,767 | 83,618 |
| FUELHH WIND (GB) | 21,193 | 32,337 | 39,413 | 46,431 | 54,680 | 48,954 | 61,641 | 63,396 | 65,642 |
| implied embedded (UK) | 15,967 | 17,304 | 17,495 | 17,404 | 20,943 | 15,969 | 18,573 | 19,372 | 17,976 |
| NESO embedded (GB) | 10,708 | 13,590 | 14,625 | 15,545 | 18,242 | 14,827 | 16,580 | 15,567 | 16,972 |
| **NESO / implied** | 0.671 | 0.785 | 0.836 | **0.893** | **0.871** | **0.928** | **0.893** | **0.804** | **0.944** |
| gap, mean MW | 599 | 424 | 328 | 212 | 308 | 130 | 228 | 434 | 114 |

**Against the predictions.** All three held. P3 held only just, with a spread of 0.140 against
0.15.

**What it establishes.**
- **NESO's embedded wind is not too large.** In 2019–24 it is 0.80–0.94 of the UK figure DESNZ
  implies. That figure still includes Northern Ireland. The magnitude leg §29 left open therefore
  cannot explain the between-day overshoot. If NESO's figure is wrong, it is LOW, and more embedded
  energy on windy days would widen between-day further, not narrow it.
- **2020, the outlier year on between-day (1.111), is unremarkable here** (0.871, mid-range). So
  magnitude does not single out the year the overshoot is worst in.
- §29's conclusion stands. The overshoot is in what the numerator does on windy days, and the next
  pass is the numerator by wind decile.

**What it does NOT establish.**
- **How much of the 114–434 MW gap is Northern Ireland.** Northern Ireland's wind generation is an
  unsourced gap, so the gap cannot be split between NI and a GB shortfall in NESO's estimate. In
  2023 the ratio dips to 0.804, a 434 MW gap, and nothing here attributes that.
- **That FUELHH carries every transmission-connected wind unit.** A non-BM transmission unit would
  sit in the implied figure and push the ratio down. In that case NESO would be even less likely to
  be high, so the direction of the conclusion holds.
- 2016–18 ratios of 0.67–0.84 are reported and not weighed. Those years are outside the 2019–24
  comparison window.

**Side reading, not a leg of this pass.** NESO's embedded SOLAR is 0.90–0.97 of ET 6.1 solar
(also UK) in every year. The model does not consume it (its solar is AGWS, §19).

**Controls.** None. Nothing shipped changed and the feed is byte-identical.

**Next.** (1) The numerator on windy days: emissions per MWh of residual, binned by wind decile,
against NESO's implied figure. (2) The 2024 level, +1.3 GW and still unattributed. (3) A
Northern Ireland wind figure (DfE NI publishes annual renewable generation), which would close
the basis gap in this table. No level move.

## 31. 2026-10-03 — THE NUMERATOR BY WIND DECILE: windy days come out too clean in every year, and the model's gas runs high on calm days, not low on windy ones

§29 placed the between-day overshoot in the numerator on windy days. This pass binned it by wind
and built nothing. No fetch. Scratch and the timestamped predictions are in `/var/tmp/se-ep13-s31/`
(`measure.py`, `prediction.txt`, `out.txt`, `out.json`). **Instrument check:** the shipped arm
reproduces the committed feed's records to five places. The fuel split comes from an exec'd copy
of `emissions_rate_t_per_mwh` with one recording line added before its `return`, so it is the
shipped dispatch's own numbers.

**The quantities.** Days are ranked within each year by **wind share** = (FUELHH transmission
wind + NESO embedded wind) / (INDO + embedded), then cut into deciles D1 (calm) to D10 (windy).
Per decile: **M/P** is the demand-weighted mean of the model's shape over NESO's, both
renormalised over the common half hours of the year. Below 1 means the model calls those days
cleaner than NESO does. **Gas gap** is the model's gas (CCGT band plus peakers) minus metered
FUELHH CCGT+OCGT, as mean MW. The second is a diagnostic reading, not an input: half-hourly gas
still never crosses into the dispatch.

**Predictions (02:27Z, before `measure.py`).** P1: M/P(D10) < M/P(D1) in every year 2019–24. P2:
D10 − D1 lies in −0.20 to −0.05 in every year. P3: the gas gap is lower in D10 than in D1 in at
least 5 of 6 years. P4: 2020 has the most negative D10 − D1.

| | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| M/P calm D1 | 1.028 | 1.044 | 1.019 | 1.013 | 1.000 | 0.989 |
| M/P windy D10 | 0.935 | **0.833** | 0.981 | 0.954 | 0.983 | 0.945 |
| **M/P D10 − D1** | −0.093 | **−0.211** | −0.038 | −0.059 | −0.017 | −0.044 |
| gas gap D1, MW | +402 | +667 | +669 | +1,066 | +1,428 | +2,149 |
| gas gap D10, MW | −330 | −758 | −274 | −371 | +75 | +54 |
| **gas gap D10 − D1** | −732 | −1,425 | −943 | −1,437 | −1,353 | −2,095 |

In 2019–20 M/P falls steadily across the deciles: 1.03 to 0.93 in 2019, and 1.04 to 0.83 in
2020. From 2021 it is flat within about ±0.02 from D1 to D9, and the fall is all in D10. The gas
gap falls in every year. It is positive on calm days and turns negative on the windiest days in
2019–22. In 2023–24 it is positive in every decile and only reaches about zero at D10. The full
per-decile table is in `out.txt`.

**Against the predictions.** P1 held in all six years. P3 held in all six. P4 held. **P2 was
refuted in four years of six:** 2020 is steeper than the −0.20 floor (−0.211), and 2021, 2023 and
2024 are shallower than −0.05. The gradient is steep in 2019–20 and small after.

**What it establishes.**
- **The over-clean is a wind effect, and it is monotone where it is large.** Windy days come out
  too clean relative to calm days in every year. 2020's between-day overshoot (1.111) is the
  steepest gradient, at −0.21.
- **In gas MW, the model's error is mostly too MUCH gas on calm days.** It is not too little on
  windy days. On calm days the model burns 0.4–2.1 GW more than the meters show; on the windiest
  days it is within 0.8 GW, either side. §29's either/or ("over-cleans windy days or under-cleans
  calm ones") resolves toward the calm side. The exception is D10 in 2019–22, where the model runs
  below metered gas. 2020 D10 is the clearest case: 758 MW short, at M/P 0.833.
- **The 2024 level gap is in the calm days.** 2024's +1.3 GW (NEXT (2) in §29–30) is a gas gap of
  about 2.1 GW in D1–D5, falling to zero at D10. So whatever supplies it runs when the wind does
  not.

**What it does NOT establish.**
- **What the calm-day excess gas actually is.** The candidates are fleets FUELHH CCGT+OCGT does
  not count but the remainder does (§17: OIL, OTHER, the INDO remainder), and demand the model
  serves that GB met some other way. Neither was split here.
- **Why the windiest decile runs short of metered gas.** One industry reading is that
  transmission constraints curtail wind north of the boundaries while gas runs south of them. The
  model curtails wind only when wind beats national demand. That is a hypothesis; nothing here
  measures it, and constraint volumes are not in the knowledge layer.
- **How the gas gap converts to M/P.** In 2023 a 1,353 MW gap gradient goes with an M/P gradient
  of −0.017, and in 2020 a 1,425 MW gradient goes with −0.211. Imports, the flat biomass block and
  the denominator all sit between the two. The two columns count different things, so they are
  not divided.

**Controls.** None. Nothing shipped changed, and the feed is byte-identical.

**Next.** (1) Split the calm-day excess: model gas against FUELHH CCGT+OCGT+OIL+OTHER by decile,
and INDO against the stack's own total. (2) Size the D10 shortfall against published constraint
volumes, if a source exists (else file the gap). (3) A Northern Ireland wind figure (§30). No level
move.

## 32. 2026-10-04 — THE CALM-DAY EXCESS, SPLIT: the level is the unpriced Norway and Denmark imports, and the gradient is biomass and coal

§31's NEXT (1). Measured, nothing shipped changed. No fetch. Scratch and the timestamped predictions
are in `/var/tmp/se-ep13-s32/` (`measure.py`, `decompose.py`, `bracket.py`, `prediction.txt`, and an
`out.txt`, `decompose.txt` and `bracket.txt` beside each). **Instrument check:** §31's deciles, and
the same exec'd copy of `emissions_rate_t_per_mwh` recording every served component before its
`return`. The shipped arm reproduces the committed feed's records to five places, and the D1/D10
gas gaps reproduce §31's to the megawatt.

**The quantities.** Per decile, mean MW. Each **gap** is the model's component minus the matching
metered FUELHH fuel: coal, biomass, pumped storage, and imports. The import gap is against *all*
clamped cables, so it equals minus the flow of the two cables with no published factor (INTNSL and
INTVKL). The model serves that flow as GB generation (`imports_by_period`, by design since 2026-08-25).
**OIL+OTHER** is metered only, because the model has no such fleet. The **INDO residual** is INDO
minus (all FUELHH generation plus clamped imports minus exports). Together these close the identity
gas gap = −coal − biomass − PS − import gaps + OIL+OTHER + INDO residual. It closes **to 0 MW at D1 in
every year, and to 15–92 MW at D10.** The D10 remainder is the model's own wind curtailment.

**Predictions (17:18Z, before `measure.py`).** P1: OIL+OTHER closes under a quarter of the D1 gap in
2023 and 2024. P2: metered biomass is higher at D1 than at D10 in ≥5 of 6 years. P3: the INDO
residual differs between D1 and D10 by under 300 MW in every year. P4: model coal sits below metered
coal at D1 in 2019 and 2020.

| year-mean, MW | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| gas gap (model − CCGT+OCGT) | +146 | +99 | +363 | +697 | +1,018 | **+1,549** |
| unpriced imports served as GB gas | 0 | 0 | 172 | 531 | 1,034 | **1,702** |
| OIL+OTHER (no model fleet) | 89 | 167 | 211 | 292 | 294 | 382 |
| model coal short of metered | 640 | 509 | 579 | 479 | 315 | 179 |
| INDO residual | −593 | −581 | −590 | −594 | −625 | −716 |
| priced share of imported MWh | 1.00 | 1.00 | 0.95 | 0.72 | 0.73 | **0.66** |

| D10 − D1, MW | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| gas gap | −748 | −1,425 | −944 | −1,462 | −1,353 | −2,068 |
| from biomass (flat block vs timed fleet) | −279 | **−1,051** | −305 | −683 | −337 | **−1,032** |
| from coal | −329 | −224 | **−601** | −393 | −211 | −97 |
| from unpriced imports | 0 | 0 | +145 | −153 | **−501** | −523 |
| from pumped storage | −124 | −162 | −120 | −144 | −203 | −277 |
| from OIL+OTHER | +18 | −21 | −88 | −114 | −21 | −51 |
| from the INDO residual | −34 | −59 | +1 | −14 | −95 | −106 |

**Against the predictions.** All four held. P1: 22% and 20%. P2: 6 of 6. P3: largest 106 MW. P4: −775
and −699 MW. The predictions were safe ones, and they establish less than the identity does.

**What it establishes.**
- **The level is the unpriced cables.** From 2021 the gas gap's year mean grows step for step with
  NSL plus Viking flow. In 2023–24 that flow exceeds the whole gap, and coal, biomass and the
  constant INDO residual net out the rest. §29–31's unattributed 2024 "+1.3 GW" is this flow. The
  hole is already named and quoted on the feed, but as **0.84 over the whole series**. By year it
  is 0.95 in 2021, 0.72 in 2022, 0.73 in 2023 and **0.66 in 2024**. The whole-series figure reads
  as small exactly in the years where the gap is large.
- **The calm-to-windy gradient is mostly biomass and coal**, and how the split falls changes by
  year. The flat block under-serves calm days and over-serves windy ones in every year: metered
  biomass is higher at D1 in 6 of 6. It is the largest single term in 2020, 2022 and 2024, around
  −1.0 GW in 2020 and 2024. Coal is the largest term in 2019 and 2021. The model burns 0.2–0.8 GW
  less coal than the meters in every decile through 2022. Pumped storage contributes 0.12–0.28 GW
  in every year (consistent with §28: the rule's even daily split). The unpriced cables join the
  gradient from 2023, because they import harder on calm days.
- **OIL+OTHER is a level, not a mechanism**: 0.07–0.43 GW, nearly flat across deciles.
- **The INDO residual is constant**, at −0.6 to −0.7 GW. Metered supply exceeds INDO by about that
  much on every kind of day (station load and pumping are outside INDO's definition), so it is not
  why calm days differ.

**The bracket (one variable, predictions P5–P7 appended at 17:21Z, after the decomposition and before
`bracket.py`).** Arm U0 hands the two unpriced cables to the dispatch as imports at 0 g/kWh. Zero is
the cleanest end a supply can have, so U0 is a **bracket end for a sensitivity**, not a proposed
factor. P5: correlation moves less than 0.01 in every year. P6: between-day moves less than 0.02 in
every year. P7: 2019–20 identical.

| shipped → U0 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| correlation | 0.9592 = | 0.9307 = | 0.9658→0.9699 | 0.9775→0.9820 | 0.9736→0.9780 | **0.9590→0.9729** |
| within-day overstated by | = | = | 0.983→1.000 | 0.972→1.000 | 0.950→1.013 | **0.926→1.062** |
| between-day overstated by | = | = | 0.997→1.013 | 1.027→1.069 | 1.002→1.066 | **0.934→1.078** |
| mean abs error | = | = | 0.059→0.055 | 0.056→0.052 | 0.069→0.067 | **0.102→0.089** |

P7 held. **P5 was refuted in 2024** (+0.014) and held elsewhere (+0.004 to +0.005). **P6 was refuted
in 2022, 2023 and 2024** (+0.04 to +0.14). Headline p95/p5 1.13→1.21, max/min 1.21→1.19.

**What the bracket establishes.**
- **The hole now matters to grading, and the 2026-08-25 test that dismissed it is superseded.** That
  pass imputed the covered cables' rate and found 2024's correlation moved 0.726→0.737 (and the
  wrong way in 2023), and it called the hole a coincidence. That was true of the model as it stood
  then. On today's model, correlation sits at 0.96. At the clean bracket end the hole is worth
  +0.014 in 2024, the largest single-year correlation move since §21, and −0.013 of mean error.
- **Two blockers were hiding each other.** Serving 1.7 GW of imports as GB gas damps the 2023–24
  swing, both within and between days. That is why those years read as *under*-swung (0.93) while
  2019–20 read as over-swung. Remove the hole and every year from 2021 is over-swung between days
  (1.01–1.08). That is the same direction as 2019–20, and it is the over-cleaned windy day of §29–31.
  The "narrow 2021–24" of §25–27 was partly this hole.

**What it does NOT establish.**
- **What NESO itself does with NSL and Viking flow** in the national actual it publishes. The
  factor table this module reads has no row for either. Whether NESO's series prices them at zero,
  at a generic rate, or leaves them out of its denominator is the question that decides where
  between the two arms the truth sits. It is not in the knowledge layer, and **it is the next
  knowledge item, not a number to pick.** Until it is answered, no factor ships, and U0 stays a
  bracket end.
- Why the model burns less coal than the meters in every decile through 2022. It is a level of
  0.2–0.8 GW, and the merit order's coal band was not split here.
- §31's NEXT (2), the D10 shortfall against constraint volumes, and (3), Northern Ireland wind.
  Neither was touched.

**Controls.** None. Nothing shipped changed, and the feed is byte-identical.

**Next.** (1) A knowledge pass: NESO's methodology for interconnectors with no factor (NSL and
Viking), from its own published methodology or API notes, filed in the knowledge layer. Then a
build decided on that answer, without looking at the correlation it moves. (2) Publish the import
coverage **by year** beside the whole-series 0.84, since 0.66 in 2024 is the figure that sizes the
hole. This is a small generator change. (3) The biomass block's timing is the largest remaining
gradient term in 2020, 2022 and 2024. A dispatch rule from annual scalars, in the shape of §25's PS
water-fill, is the candidate, and §10's retirement of biomass as a *target* still binds. No level
move.

## 33. 2026-10-04 — WHAT NESO DOES WITH THE CABLES IT HAS NO FACTOR FOR: North Sea Link is in its imports and priced low, and Viking and ElecLink are not in its mix at all

§32's NEXT (1), the knowledge pass. Measured, nothing shipped changed. Filed in the knowledge layer as
`docs/market_research/neso_carbon_intensity_interconnector_treatment_2026-10-04.md`, which carries the
tables. Scratch and the timestamped prediction are in `/var/tmp/se-ep13-s33/`.

**The published record does not answer it.** NESO's methodology was last revised 2021-09-24, before
either cable existed. Its import rule is a daily factor computed from each connected network's
ENTSO-E mix. Table 1's import rows are only the fallback defaults. The live factor endpoint has no
Norway or Denmark row.

**So it was measured from NESO's own outputs.** NESO's `/generation` imports share over its nuclear
share equals metered imports over metered nuclear, whatever denominator it uses. The instrument
check holds: gas/nuclear matches FUELHH to the third decimal place in every month.

**Prediction (19:40Z, before any of it ran).** P1: NESO's import share includes NSL *and* Viking.
**Half refuted.** NSL is in (a per-cable coefficient of about 1.0 in all 24 months of 2022 and
2024). Viking is out (0.00–0.22). **ElecLink is out too** (0.00–0.45), which nobody predicted. "All
but Viking and ElecLink" fits 2024 at MAE 0.04–0.12, against 0.21–0.44 for all cables.

**NSL's factor is low and not identified as a number.** Fitting NESO's actual intensity on its own
mix (scale 1.006 and 0.998) puts NSL at 23–36 g in the joint fit. Monthly estimates scatter from
−191 to +152. Pooled, the error rises steadily as the factor rises from 0: 2024 gives 6.17 g at
0, 7.26 at 120 and 10.93 at 394. **NSL is not priced like GB gas.** That matches Table 1 applied to
Norway's mostly-hydro mix.

**What it means for the build (decided here, before any arm is run against the grade):**
- **Viking: out of the numerator and out of the denominator**, which is NESO's own treatment.
  Its flow still physically displaces GB gas, so the dispatch should see it as an import. That
  leaves no factor to choose, so it is buildable now.
- **ElecLink: the shipped French factor is a reasonable reading of the rule, and it is not what the
  target does.** NESO leaves ElecLink out of its mix. Repricing it is a change to the target's
  definition, so it is the same build as Viking's, under the same rule.
- **NSL: in the denominator, at a factor that is still owed.** U0 (0 g) remains a bracket end. It is
  now the end the evidence favours, and it is still not a measured factor. The number is Norway's
  ENTSO-E mix with Table 1 applied. That needs an ENTSO-E token, which the box does not hold.
- The `elexon_fuel_outturn` docstring's ElecLink sentence is corrected beside the claim.

**Controls.** None. Nothing shipped changed.

**Next.** (1) Build "Viking and ElecLink are seen by the dispatch and left out of the target's
mix". This is one variable with no factor to pick. Write the prediction before the arm runs.
(2) NSL's factor. Either establish it from Norway's published mix (ENTSO-E, or an annual national
statistic as a coarser fallback), or keep the honest gap and name it. (3) §32's coverage by year
and the biomass rule stand. No level move.

## 34. 2026-10-04 — VIKING AND ELECLINK ARE SERVED AND LEFT OUT OF THE MIX: the 2024 within-day and between-day both reach 0.97x, and the headline spread widens

§33's NEXT (1), built. There was no factor to pick. `elexon_fuel_outturn.OUTSIDE_NESO_MIX`
(`INTELEC`, `INTVKL`) sends their import to a new `unmixed_import_mw`. The dispatch serves that
flow before the stack, adds no tonnes for it, and takes its MW out of the denominator. That is the
half hour with their MW taken off demand, and the control checks it to 1e-12. North Sea Link stays
uncovered and is still served as GB gas. The feed's `import_coverage` now counts only the imports
inside NESO's mix: 0.86 over the series, and 0.71 in 2022–2024 by year. The cable lists are
derived from the adapter's own tables.

**Prediction (filed before the arm ran, `/var/tmp/se-ep13-s34/prediction.txt`):**

| | predicted | measured | |
|---|---|---|---|
| P1 2019–21 bit-identical | identical | 2019–20 identical; **2021 not** | **refuted**: ElecLink metered flow starts 2021-09-18 (commissioning, 12 GWh), not May 2022 |
| P2 2024 correlation | 0.960–0.968 | 0.9590 → **0.9619** | held |
| P3 2024 between-day | 0.95–1.02 | 0.9336 → **0.9724** | held |
| P4 2022/23 correlation | moves <0.005 | −0.0002 / −0.0006 | held |
| P5 2024 within-day | 0.94–1.00 | 0.9264 → **0.9703** | held |

**Not predicted, and worse:** the headline p95/p5 goes from 1.13x to 1.15x and max/min from
1.21x to 1.23x. MAE improves in 2024 (0.102 → 0.097) and worsens slightly in 2022–23
(+0.0003 / +0.0011). This is a correction to the target's definition, not a tuning, so the worse
headline ships and is published in `ERROR_DIRECTION` beside the better years.

U0 (§32: NSL and Viking at 0 g, both in the denominator) reached 2024 corr 0.973. This arm reaches
0.962 with NSL still served as gas. So the remaining 2024 gap is mostly North Sea Link's, which is
consistent with §33's finding that its factor is low.

**Controls (each mutation-proven):** `test_the_cables_outside_NESOs_mix_are_unmixed_...` (drop
the cable from the set), `test_an_UNMIXED_import_displaces_gas_and_leaves_the_denominator_...`
(keep its MW in the denominator), `test_VIKING_and_ELECLINK_are_served_and_left_out_of_the_mix_in_the_published_feed`
(drop the input from `generate()`).

**A retired artefact moved, and its finding did not.** `docs/observability/ep13_embedded_generation_bound.json`
is reproduced by its producer under test, and the producer reads `fuel_mix()`'s priced imports.
ElecLink has now left those imports, so the artefact was regenerated. Its oracle headroom is still
negative in every year (2024: −0.091 → −0.105), so the embedded-generation retirement stands.

**Next.** (1) NSL's factor, from Norway's published mix, or keep the honest gap and name it. The
ENTSO-E token is not on the box. An annual national statistic is the coarser fallback, and it has
to be sourced, not picked. (2) §32's coverage by year and the biomass rule stand. No level move:
correlation is 0.93–0.97 against the 0.97 peer bound, and 2020 is still the outlier at 0.931.

## 35. 2026-10-04 — NORTH SEA LINK IS PRICED AT NORWAY'S PUBLISHED MIX: correlation reaches the peer bound in 2021–2024, and the shape now swings too wide in every year

§34's NEXT (1), built from a source rather than a pick. NESO's rule for an import is Table 1
applied to the connected network's mix. The daily ENTSO-E mix needs a token the box does not
hold. The annual national mix does not: Statistics Norway table 08307 publishes Norway's
production split into hydro, wind, solar and thermal. Under Table 1, only thermal carries
carbon. Thermal is 1.0–1.7% of production, and 08307 does not split it by fuel, so Table 1
brackets it between biomass (120) and CCGT (394). NSL therefore comes in at 1.2–6.5 g. The
shipped end is the HIGH one (4.0–6.8 g by year), because it cannot make Norway cleaner than
its fired plant. `elexon_fuel_outturn.import_factor` derives it per year, and a year 08307 does
not cover leaves the cable `uncovered`, served as gas. Sourced and tabled in
`docs/market_research/neso_carbon_intensity_interconnector_treatment_2026-10-04.md` (new section).

**Prediction (filed before the arm ran, `/var/tmp/se-ep13-s35/prediction.txt`):**

| | predicted | measured | |
|---|---|---|---|
| P1 2019–20 identical | identical | identical | held |
| P2 2024 correlation | 0.968–0.975 | 0.9619 → **0.9722** | held |
| P3 2024 between-day | 0.99–1.08 | 0.9724 → **1.0706** | held, at the top |
| P4 2024 within-day | 0.97–1.02 | 0.9703 → **1.0650** | **refuted**: over the band |
| P5 2022/23 correlation | +0.001–0.010 | +0.0047 / +0.0046 | held |
| P6 low end vs high end | < 0.001 on every statistic | correlation identical; swing up to 0.0015 | **refuted, narrowly** |
| P7 import coverage | ~1.0 | 1.0 in every year | held |

**By year (high end, shipped):** correlation 0.959 / 0.931 / 0.970 / 0.982 / 0.978 / 0.972
(2019–24). Within-day 1.06 / 1.10 / 1.00 / 1.00 / 1.02 / 1.07. Between-day 1.05 / 1.11 / 1.01 / 1.07
/ 1.07 / 1.07. MAE in 2024 0.097 → 0.089. Headline p95/p5 **1.15 → 1.22x (worse)**, max/min
1.23 → 1.21x.

**What it means.** §32 said "the hole hid the over-swing", and this confirms it at the shipped
factor: with the last cable in NESO's mix priced, the shape swings too WIDE between days in
every year and within the day in four of six. 2021–22 within-day sit at 1.00. The error
direction is no longer mixed. A time-shifting benefit read from this shape is an upper bound
in every year, and `ERROR_DIRECTION` now says so. Correlation is at or above the 0.97 peer
bound in 2021–2024. 2019 (0.959) and 2020 (0.931) are not, and neither had NSL. Their gap is
§32's gradient (the flat biomass block and coal), which this pass did not touch.

**The bracket is immaterial at this grade.** It moves correlation by less than 0.0001 and swing by
up to 0.0015, against a 0.10 move from pricing the cable at all. Narrowing it is owed to the
daily ENTSO-E mix, not to a choice. That is a named gap, not a blocker.

**Controls (each mutation-proven):** `test_NORTH_SEA_LINK_is_priced_by_table_1_applied_to_norways_published_mix`
(price at 0, price at 394 flat, price a year the table lacks: all fire).
`test_a_cable_with_no_published_factor_or_mix_is_reported_separately_and_never_priced` keeps the
uncovered branch reachable in a year with no published mix. The feed's `uncovered_cables` is now
empty, and its control says so. The retired embedded-generation artefact was regenerated: its
oracle headroom is still negative in every year (2024 −0.105 → −0.083), so the retirement stands.

**Next.** (1) §32's GRADIENT, now the largest visible error: the flat biomass block and coal, which
carry 2019–20's correlation and the over-swing in every year. Write the prediction before the
arm runs. (2) Coverage by year. No level move: L3 needs the reconstruction to fail like
reality, and a swing that is too wide in every year is a one-sided error, not a reality-like one.

## 36. 2026-10-04 — A BIOMASS RULE FROM THE ENVELOPE: the fleet's honest ends make it bang-bang, and every year swings too narrow

§35's NEXT (1), the biomass half of §32's gradient. Measured, nothing shipped changed. Scratch, the
rule as a patch (`armB.patch`) and the timestamped prediction are in `/var/tmp/se-ep13-s36-scratch/`.
**Instrument check:** the reimplemented base arm reproduces the committed feed's records to five
places (max diff 0.0, 959 records). On §31's wind-share deciles, the metered D1−D10 biomass gap is
within about 0.1 GW of §32's biomass column in every year.

**The rule (arm B), decided before it ran.** Biomass is dispatched by the model in the shape of
§25's PS rule, but over the year rather than the day, because the gradient sits between days. The
fleet ranks on the same pre-PS residual PS uses: b = clamp(R − L, `floor_mw`, `capacity_mw`), with
one level L a year set so the year's mean equals the measured `mean_mw`. Three annual scalars cross,
all from `biomass_envelope_by_year`, and no half-hourly biomass reading does. PS keeps its own
input, so its schedule is unchanged. The ends are the envelope's honest ones, the observed minimum
and maximum. `p1`/`p99` were not tried, because choosing ends after seeing the grade is fitting.

| predicted (21:44Z) | measured | |
|---|---|---|
| P1 between-day falls every year by 0.03–0.12 | falls every year, by 0.12–0.16 | **refuted on size** in 5 of 6 |
| P2 within-day falls every year by 0.02–0.08 | falls every year, by 0.16–0.20 | **refuted on size** in 6 of 6 |
| P3 correlation moves <0.010 | −0.009 to −0.019 every year | **refuted** in 5 of 6 (2024 held at −0.0095) |
| P4 rule vs metered timing positive, 0.2–0.6 | half-hourly 0.29–0.59 | held |
| P5 rule's D1−D10 exceeds metered in ≥4 of 6 | 6 of 6, by 2.2–8x | held |
| P6 headline p95/p5 falls from 1.22x | 1.22 → 0.90x (max/min 1.21 → 0.96x) | held, and now overshoots below 1.0 |

| arm B vs shipped | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| correlation | .959→.940 | .931→.912 | .970→.954 | .982→.972 | .978→.964 | .972→.963 |
| within-day overstated by | 1.06→0.86 | 1.10→0.92 | 1.00→0.83 | 1.00→0.84 | 1.02→0.83 | 1.07→0.87 |
| between-day overstated by | 1.05→0.91 | 1.11→0.97 | 1.01→0.90 | 1.07→0.92 | 1.07→0.91 | 1.07→0.93 |
| mean abs error | .061→.071 | .104→.104 | .055→.073 | .053→.067 | .068→.087 | .089→.096 |
| D1−D10 biomass, rule / metered (MW) | 2,003 / 280 | 2,335 / 1,121 | 2,000 / 294 | 2,637 / 786 | 2,748 / 344 | 2,424 / 1,042 |
| share of half hours at cap / at floor | .51/.32 | .53/.28 | .57/.28 | .43/.41 | .37/.45 | .53/.26 |

**What it establishes.**
- **The envelope cannot carry a dispatch rule.** Its ends are the most and least the whole fleet
  ever produced. The least is set by outages (50–383 MW against means of 1.5–2.2 GW). A rule
  between those ends that conserves energy runs bang-bang: at capacity for about half the year and
  at the outage floor for about a third. GB's fleet never behaves like that. The swing flips from
  too wide in every year to too narrow in every year, by more than it was wrong before.
- **Biomass does follow the residual, but only partly.** The rule's timing correlates with the
  meters at 0.29–0.59, and the fleet's calm-day excess is real in every year (+0.28 to +1.12 GW).
  But the rule's gradient is 2.2–8x that. Most of the fleet does not move with price. §10's
  "a CfD plant runs on availability" is consistent with this.
- §10's 2026-08-27 envelope-dispatch result (worse on four axes of five) is reproduced on today's
  model in a stronger form. It was not a relic of the old one.

**What it does NOT establish.**
- **Which part of the fleet follows price.** GB biomass sits under two support schemes. CfD units
  are paid per MWh at a strike price and run on availability. ROC units earn per MWh too, but on
  top of a wholesale price they can flex against. A rule that dispatches only the ROC share, at
  published capacities by year, needs no fitted slope. **That split is a knowledge item, not a
  number to pick.** It is not in the knowledge layer.
- Coal, the other half of §32's gradient, was not touched (0.2–0.8 GW short of the meters through
  2022, the largest term in 2019 and 2021).

**Controls.** None. Nothing shipped changed, and the feed is byte-identical.

**Next.** (1) A knowledge pass: GB biomass capacity by support scheme and year (Drax's CfD unit and
its ROC units, Lynemouth, the others), from published scheme registers and annual reports. Then a
rule that flexes only the ROC share, written and predicted before it is graded. (2) Coal's short
level: split the merit order's coal band against FUELHH coal by decile. (3) Coverage by year. No
level move: the shipped swing is still too wide in every year, a one-sided error.

## 37. 2026-10-04 — THE BIOMASS FLEET BY SUPPORT SCHEME: Drax's RO units carry the calm-day excess, and the scheme is not the mechanism

§36's NEXT (1), a knowledge pass. Nothing shipped changed. Sourced and tabled in
`docs/market_research/gb_biomass_fleet_by_support_scheme_2026-10-04.md`. Per-unit Elexon B1610
pull, the prediction (filed before the pull) and the outputs are in `/var/tmp/se-ep13-s37/scratch/`.

**The fleet.** Drax 1 is on a CfD (from 2016-12-21). Drax 2-4 are on the RO (4 from Aug 2018),
about 1,975 MW. Lynemouth (420 MW) and Tees REP (285 MW, from 2023) are on CfDs. Wilton and Rothes
are small. Together they are 0.90-0.98 of FUELHH BIOMASS's mean.

**§36's premise was wrong.** "A CfD plant runs on availability" is not what the contract says. The
biomass CfDs settle against a season-ahead baseload reference price. So a CfD unit, like an RO unit,
earns the day's price plus a constant, and both can flex. Above the strike, the CfD constant is
negative. Drax held unit 1 back in 2022-23 (mean 440 -> 260 -> 129 MW).

**Measured (pre-registered P1-P5: 1 held, 4 refuted).** On year deciles, Drax 2-4 carry 0.86-1.33 of
the metered calm-day gap in 2020 and 2022-24, but about 0 in 2019 and 0.22 in 2021. On post-hoc
within-quarter deciles (calm days cluster in the summer outage season), Drax 2-4 carry **0.39 / 0.89
/ 0.57 / 0.85 / 0.86 / 0.96** (2019-24). Lynemouth is about 0 in every year. Drax 1 is small,
except 2021 (+220 MW). In 2019 the listed units miss most of the metered gap. That unit is not
established.

**What it means for the rule.** Flexing only the RO share is the right population, but not a
complete rule. Their capacity is flat at about 1,975 MW, while their within-season gradient runs
177-945 MW by year. A rule bounded by capacity alone gives roughly the same gradient every year, and
the real one varies fivefold. What sets the size (the clean-spark-to-biomass spread, the ROC cap,
pellet supply) is a knowledge item. It is not a slope to fit.

**Controls.** None. The feed is byte-identical.

**Next.** (1) Measure what sets the RO units' flex by year. The candidate is the day's price
against a biomass marginal cost net of ROC value, from published pellet prices and ROC buy-out.
Then build a rule that flexes only Drax 2-4 when that spread is negative, with a prediction written
first. (2) Coal's short level (§36 NEXT 2). (3) 2019's missing biomass unit. No level move.

## 38. 2026-10-04 — WHAT SETS DRAX'S RO FLEX: a price switch exists and moves by year, but how far windy days sit below it does not explain the size

§37's NEXT (1), measured. Nothing shipped changed. Elexon MID for 2021-24 was fetched with
`sim/market_index_history.get_market_index_range`, because the cache ends in 2020. The scripts, the
fetched series and the timestamped prediction are in `/var/tmp/se-ep13-s38/`.

**Prediction (filed 22:06Z, before any price-vs-output reading).** H: Drax 2-4 run when the day's
MID is above a switch price (fuel cost per MWh_e minus the ROC value) and back off below it. The flex
size is how far the calm and windy days straddle that switch. P1: in at least 5 of 6 years, output
on days below the year's best split is at least 300 MW lower than above it. P2: the 2022 switch is at
least £40 above 2019-20. P3: the rank correlation across years between the RO gap and the
windy-minus-calm share of days below the switch is at least 0.7. P4: 2019 and 2021 have under 15% of
days below their switch. P5: the switch lies within £20 of sourced fuel cost minus ROC. **A refuted
P1 or P3 refutes H as the mechanism.**

**The switch is real.** Drax 2-4 daily output, demeaned by calendar month so that outage season
drops out, binned by absolute daily MID:

| year | where output falls off | month-demeaned output below it |
|---|---|---|
| 2019 | no day is cheap enough to show one (the lowest bin is £20-30) | flat, ±40 MW |
| 2020 | ~£20 | −570 MW below £20 |
| 2021 | ~£55 | −324 (£40-50), −94 (£50-60) |
| 2022 | ~£125 | −304 to −156 across £60-130 |
| 2023 | ~£75, graded rather than a step | −285 to −311 below £60, −88 at £60-80 |
| 2024 | ~£55 | −767 below £20, −349 at £40-50, −76 at £50-60 |

The switch rises about £100 from 2020 to 2022 and falls back, which is the shape a fuel-cost switch
would have. It is not yet graded against a fuel cost (P5). No sourced pellet or Drax generation cost
is in the knowledge layer, and a recalled figure is not evidence.

**Graded.** P1 **held, 5 of 6.** The month-demeaned best-split gaps are +24 / +866 / +339 / +443 /
+534 / +860 MW, and 2019 fails. On raw output the 2019 gap is +167, still under 300. P2 **refuted
narrowly by its own instrument.** The best split is £78 in 2022 against £39 in 2019, which is +39.
2019's split is noise at a 24 MW gap, and against 2020 (£16) it is +62. The bin reading puts 2022 near
£125. P3 **refuted: rank 0.09.** With a 15-day minimum tail, the best split leaves only 4-6% of days
below it in five years out of six, and the windy-minus-calm share barely moves (0.25-0.36). P4: 2019
**refuted** (0.39 below its noise split) and 2021 held (0.06). P5 **ungraded.**

**Post-hoc, not pre-registered.** The switch was read off the table above, and depth was taken as
max(0, switch − MID) on within-quarter windy-decile days minus calm. Depth against the RO gap gives
rank 0.54 and Pearson 0.40. 2020 breaks it: the depth is about £4, and its flex is the largest in the
record. The response is not linear in depth. 2020's windy days sat right at the switch (£24 against
~£20), and its below-£20 days were the COVID demand trough. Per unit, Unit 4 is under the 125,000
ROC station cap, so most of its output earns no ROC. It does not switch higher than units 2 and 3 in
any year, so the cap is not the lever either. This rests on the BM-unit-to-Drax-unit mapping, which
is still an assumption (§37).

**What it means.** By H's own refutation rule, "flex size is how far the days straddle a step
switch" is refuted. What survives is narrower: Drax 2-4 respond to the day's price, around a level
that moves by year roughly as fuel cost would. The response is graded (2023 climbs smoothly from
£40 to £150), so a reconstruction rule needs a supply curve, not a step. Its location needs a
sourced fuel cost, not a fitted one.

**Controls.** None. The feed is byte-identical.

**Next.** (1) Source Drax's biomass generation cost per MWh by year from its annual reports, or a
published pellet index with a stated efficiency. Then grade the switch against it net of the ROC
value (`docs/domain_artefact_library/regulatory/ro_obligation_and_buyout.json`). (2) Only if (1)
holds: a Drax 2-4 rule as a supply curve around that cost, with its prediction written first. (3)
Coal's short level, 2019's missing biomass unit, and coverage by year all stand. No level move.

## 39. 2026-10-04 — WHAT LOCATES DRAX'S SWITCH: the published fuel cost grades only 2019, and in 2022 Drax names an opportunity cost instead

§38's NEXT (1), the knowledge pass. Nothing shipped changed. Filed in the knowledge layer as
`docs/market_research/drax_biomass_cost_and_the_ro_switch_2026-10-04.md`, which carries the sources
and tables. Scratch, fetched documents and the timestamped prediction are in `/var/tmp/se-ep13-s39/`.

**Prediction (23:16Z, before any cost or ROC figure was read).** H5 is §38's P5: the switch is fuel
cost per MWh_e minus the ROC value. P5a: the switch lies within £20 of that in at least 4 of 5 years
2020-24. P5b: the sourced fuel cost moves less than the switch's ~£100 rise from 2020 to 2022,
because the pellets are under long-term contract, so P5a fails in 2022. P5c: the ROC value moves by
less than £15 over 2020-24. P6 was added after reading Drax's FY2022 statement and before reading
output: H2 minus H1 output in 2022 exceeds every other year's by at least 150 MW.

**What is published.** Drax gives a biomass cost per MWh in only two places. One is c.£75-80 in 2019
(Capital Markets Day). The other is a December 2022 forecast of "over £100/MWh" all-in for 2023.
Every other year carries a $/t *production* cost FOB its own plants ($161 to $153 to $143), which
excludes shipping, third-party fibre and FX, so it is not a cost per MWh generated. The ROC side has
buy-out in the commons (£50.05 to £64.73 over OY2020-24). The recycle payment is not sourced, so
buy-out is only a lower bound on what a ROC earns.

**Graded.** P5a is **ungraded**. Fuel cost is published for none of 2020-24 except as 2023's
"over £100", and with both bounds pointing the same way that gives no bound on the switch. 2019 is
outside P5a's window. There, fuel minus buy-out is at most £26-31, and §38 found no day cheap enough
to show a switch below the £20-30 bin. That is **consistent, not a test.** P5b is ungraded in £/MWh,
but its alternative is now **stated by Drax**. The FY2022 results say it bought back first-half
positions, reprofiled generation to the second half, and that the European spot price of biomass
"created opportunities for the sale of biomass in addition to generation". In 2022 the pellet's
resale or later-half value set the switch, not its contract cost. P5c **held narrowly on buy-out
alone** (+£14.68). P6 is **refuted on its margin.** H2−H1 is +56 / −224 / +240 / **+306** / −84 / −11 MW,
so 2022 is the largest, but only 66 MW above 2021, and a half-year split carries outage season and
the price path.

**What it means.** The switch §38 found cannot take its location from published data. Fuel cost is
missing in five years of six, and in 2022 fuel cost is the wrong quantity even if it were known. A
Drax 2-4 rule whose location is "fuel cost minus ROC" would carry an honest `None` in those years.
§38's NEXT (2) was conditional on (1) holding, so it does not start. What remains buildable without
a picked number is a rule whose location is an *observable the world already holds*. The
reconstruction already uses FUELHH biomass output as an input. So a rule that dispatches the year's
measured biomass energy against the day's MID, in the shape of §25's PS water-fill with the price
ranking the days, needs no cost. Whether that is fair to the target is the question to settle
before it is built.

**Controls.** None. Nothing shipped changed.

**Next.** (1) Decide, and write down before any arm, whether "the year's measured biomass energy,
ranked across days by MID" is a fair reconstruction input under the independence test that
`sim/neso_carbon_intensity.py` passes. MID is a market observable and is not NESO's output. If it is
fair, build it as one variable with its prediction written first. (2) The ROC recycle value by year,
from Ofgem's annual RO reports, closes the ROC side of the bound. (3) Coal's short level, 2019's
missing biomass unit, and coverage by year all stand. No level move.

## 40. 2026-10-04 — PRICE AS THE BIOMASS RANKING: fair as an input, and refuted, because the meters follow the residual more closely than the price in every year

§39's NEXT (1). Nothing shipped changed. The scratch script, the output and the timestamped decision
and prediction are in `/var/tmp/se-ep13-s40-scratch/`.

**The decision, written before any arm (22:25Z).** The year's measured biomass energy, ranked across
half hours by MID, is a fair input. MID is Elexon's traded index, and nothing of NESO's factors, mix
or intensity goes into it. Only the three annual scalars §27 and §36 already use cross from the
meters, so condition 1's refusal of half-hourly biomass is not engaged: the timing comes from a
price, not from the meters. The named risk is that MID carries more than the residual, including
the gas price path. That is why a gain needed the timing leg against the meters before it could be
read as the mechanism.

**The one variable.** §36's rule, unchanged, with its ranking key changed from the pre-PS residual to
the half hour's MID. To change only the order, the year's residual values were re-assigned to half
hours in MID's rank order. Half hours with no MID (1-153 a year) got the flat block. The base arm
reproduces the committed feed to five places (max diff 0.0, 959 records). §36's arm B was re-run in
the same process.

| predicted (22:25Z) | measured | |
|---|---|---|
| P1 still bang-bang (cap + floor ≥ 0.6) | identical shares to B | **not a test.** Re-ordering the same values leaves the output's distribution unchanged by construction. I should have seen that before filing it. |
| P2 within-day < 1.0 in ≥ 5 of 6 | 0.92-0.98, 6 of 6 | held |
| P3 timing vs meters beats B in ≥ 4 of 6 | below B in **6 of 6**, about 0 in 2019-21 | **refuted, so H is refuted** |
| P4 calm-windy gradient below B in ≥ 4 of 6 and above metered in ≥ 4 of 6 | 6 of 6, and 5 of 6 | held |
| P5 corr within ±0.010 of B, below base in ≥ 4 of 6 | 2019 −0.012 and 2022 −0.013 off B; below base in 6 of 6 | refuted in 2 of 6, held |
| P6 nothing ships | within-day inside 0.95-1.05 in 2 of 6; corr down 0.010-0.024 | held |

| C (MID-ranked) vs B (residual-ranked) vs base | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| correlation, base / B / C | .959/.940/.928 | .931/.912/.905 | .970/.954/.957 | .982/.972/.959 | .978/.964/.958 | .972/.963/.962 |
| within-day overstated by, base / B / C | 1.06/.86/.96 | 1.10/.92/.98 | 1.00/.83/.95 | 1.00/.84/.93 | 1.02/.83/.92 | 1.07/.87/.94 |
| between-day overstated by, base / B / C | 1.05/.91/.98 | 1.11/.97/1.05 | 1.01/.90/1.00 | 1.07/.92/.98 | 1.07/.91/1.00 | 1.07/.93/.99 |
| rule vs metered biomass, half-hourly corr, B / C | .29/.04 | .45/.09 | .31/−.01 | .42/.39 | .35/.30 | .59/.41 |
| metered biomass, daily corr with MID / with residual | .01/.37 | .17/.49 | .10/.41 | .45/.50 | .37/.53 | .48/.58 |

**What it establishes.**
- **Within a year, the fleet follows the residual more closely than the price.** That holds in every
  year with no rule involved: daily corr 0.37-0.58 with the residual, and 0.01-0.48 with MID. In
  2019-21 the price ranking is about orthogonal to what the fleet did. That is the gas path: a
  year's absolute MID ranks its months by fuel cost (2021's second half) before it ranks its days by
  scarcity. §38 saw the switch only after demeaning output by month, so its finding stands and does
  not carry over to a year-wide ranking.
- **C's swing being nearest 1.0 is not progress.** Headline p95/p5 is 1.01x and between-day sits at
  0.98-1.05, the closest this atom has published. But it comes from a schedule that is uncorrelated
  with the fleet in three years of six. It is narrower than B because a near-random order makes a
  smaller calm-windy gradient. Correlation fell in every year. Quoting the swing would be choosing
  the flattering statistic.
- §36's diagnosis stands: the failure is the envelope's ends, not the ranking key. The best key
  available (the residual) cannot rescue a rule whose amplitude is set by outages.

**What it does NOT establish.**
- Whether MID ranked *within month* would beat the residual. That is a different variable, it was
  chosen after seeing this result, and it would carry a picked window. It was not tried.
- What sets the size of the flex (177-945 MW by year, §37). That is still the gap, and §39 found it
  cannot be located from published cost.

**Controls.** None. Nothing shipped changed, and the feed is byte-identical.

**Next.** (1) Coal's short level (§36 NEXT 2): split the merit order's coal band against FUELHH coal
by wind decile. It is the largest gradient term in 2019 and 2021, and it touches no biomass number.
(2) The ROC recycle value by year (§39 NEXT 2). (3) 2019's missing biomass unit, and coverage by
year. The biomass gradient is parked on its amplitude, which is knowledge-limited. No level move:
the shipped swing is still too wide in every year.

## 41. 2026-10-04 — COAL'S SHORT LEVEL: the shipped merit order serves almost no coal in any year, because the coal band sits above 30 GW of gas that the model never reaches

§40's NEXT (1). Measured, nothing shipped changed. Scratch, outputs and the timestamped predictions
are in `/var/tmp/se-ep13-s41/` (`measure.py`, `bracket.py`, `prediction.txt`, with `out.txt` and
`bracket.txt`). **Instrument check:** an exec'd copy of `emissions_rate_t_per_mwh` records each
served component. The shipped arm reproduces the committed feed's 959 records to five places.

**The mechanism, read from the code before measuring.** Coal is served only above the CCGT band:
`coal_mw = min(thermal_mw − CCGT_CAPACITY_MW, coal_capacity_mw)`, with `CCGT_CAPACITY_MW = 30,000`.
`coal_capacity_by_year` (the fleet's demonstrated maximum, 1.9–7.6 GW over 2019–24) only caps a band
that the model's thermal has to climb past 30 GW to enter.

**Predictions (22:55Z, before `measure.py`).** P1: model coal is 0 in ≥95% of half hours in every
year. P2: metered coal is above 50 MW in ≥40% of 2019's half hours and ≥25% of 2021's. P3: Oct–Mar
carries ≥70% of metered coal in each of 2019–22. P4: when metered coal ran, the model's thermal sat a
median ≥8 GW below the threshold in 2019 and 2021. P5: metered coal's calm-minus-windy difference is
≥70% of §32's coal gradient term.

| | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| model coal, year mean MW | **19** | 0 | 0.03 | 0 | 0.1 | 0 |
| metered coal, year mean MW | 652 | 507 | 575 | 480 | 316 | 179 |
| half hours with model coal at 0 | 0.992 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| half hours with metered coal > 50 MW | 0.56 | 0.40 | 0.60 | 0.56 | 0.50 | 0.36 |
| Oct–Mar share of metered coal | 0.86 | 0.91 | 0.65 | 0.68 | 0.79 | 0.66 |
| model thermal's median distance below 30 GW when metered coal ran, GW | 14.8 | 16.4 | 14.9 | 14.4 | 18.3 | 21.7 |
| metered gas (CCGT+OCGT) median, coal on / coal off, GW | 14.7/11.0 | 12.5/8.6 | 14.8/9.3 | 14.9/11.4 | 11.3/8.5 | 8.1/6.1 |
| metered coal, calm decile / windy decile, MW | 1,419/313 | 1,039/157 | 960/145 | 846/99 | 506/146 | 190/93 |
| metered coal by hour, 2019, MW | 188–230 overnight, 842–1,034 from 08:00 to 20:00 | | | | | |

**Against the predictions.** P1 held (99.2–100%). P2 held (0.56 and 0.60). **P3 was refuted in 2021
and 2022** (0.65 and 0.68): coal ran through the summer of 2021 and from July 2022, which is the gas
price, not the season. P4 held, and by twice the margin (14.8 and 14.9 GW). P5 held: metered coal
carries 100–117% of the coal-gap gradient in 2019 and 2021. **But this pass's deciles are not §32's
population.** §32 also needed NESO's mix and the FUELHH remainder rows in each half hour, and on its
days the 2019 coal gradient was −329 MW against −942 MW here. I cannot yet say which days carry the
difference. The direction and the conclusion are the same in both.

**What it establishes.**
- **Coal is a dead dial in the shipped model.** `coal_capacity_by_year` crosses, is tested, and moves
  nothing. The model serves 0–3% of metered coal in every year. That is the "no coal at all"
  behaviour the input was added to fix. §17's "coal carried 0.93/0.77 in 2017/18" and §32's "model
  coal short of metered by 179–640 MW" were both describing this, without naming the cause.
- **The ordering's stated simplification is wrong as written.** The comment above `coal_mw` says the
  half hours that mis-order are "few and their coal volume small". The direction it gives (coal
  understated) is right. The size is all of it. The flaw is in the threshold, not the ordering: a
  peaking fleet does run after mid-merit, but GB's mid-merit band ended where *running* gas ended,
  12–15 GW in the half hours coal ran. It did not end at 30 GW of nameplate. Corrected beside the
  claim in `sim/grid_carbon_intensity.py`.
- **Real coal ran as a daytime, winter, calm-day plant.** It ran 4–5x higher by day than overnight
  in 2019, and 2.0–8.5x higher on calm days than windy ones. Its on/off line in metered gas moved by
  year.

**The bracket (P6–P8 appended at 22:57Z, after `measure.py` and before `bracket.py`).** One variable:
coal served from the bottom of the thermal stack, displacing CCGT, as a flat block. Arm F is the
year's measured mean, which is coal's annual grain and so buildable. Arm M is each month's measured
mean, which is finer than that grain, so it is an oracle and not buildable. **Placebo Z** (a block of
0) reproduces the shipped statistics to four places in 2020–24. It differs only in 2019, where the
shipped band's 19 MW is worth +0.0015 of correlation.

| base → F → M | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| correlation | .959/.954/.959 | .931/.925/**.953** | .970/.968/.975 | .982/.982/.979 | .978/.979/.976 | .972/.972/.973 |
| within-day overstated by | 1.06/.93/.92 | 1.10/1.00/.98 | 1.00/.91/.90 | 1.00/.93/.92 | 1.02/.95/.94 | 1.07/1.03/1.03 |
| between-day overstated by | 1.05/.95/1.04 | 1.11/1.03/1.04 | 1.01/.95/.97 | 1.07/1.01/1.00 | 1.07/1.01/1.01 | 1.07/1.04/1.05 |
| mean abs error | .061/.061/.057 | .104/.099/**.077** | .055/.058/.050 | .053/.048/.053 | .068/.062/.065 | .089/.085/.084 |

Headline p95/p5 is 1.22 (base), 1.06 (F) and 1.08 (M). **P6 was refuted in 2019 and 2020**: F's
correlation fell by 0.0054 and 0.0053, against a bound of 0.005, and it fell rather than rose. It held
in the other four years. F's narrowing of 2019–21 held, and it overshoots below 1.0 within the day.
**P7 held** (M over F by +0.006 in 2019 and +0.028 in 2020). P8 held (2024 moves ≤0.001).

**What the bracket establishes.**
- **Coal's level is worth swing, and coal's timing is worth correlation.** Serving the right energy
  as a flat block takes the between-day overstatement to 0.95–1.04 and the headline p95/p5 from 1.22
  to 1.06. It also lowers correlation in 2019–21, because a flat block is clean on the calm days and
  dirty on the windy ones in the wrong proportion: the same failure as §27's biomass block. Timing
  the energy by month recovers 2020's correlation to 0.953, the largest move on that year since §21,
  and cuts its mean error by a quarter.
- **Neither arm ships.** F lowers correlation where coal matters. M reads coal's monthly energy from
  the meters, which condition 1 refuses at that grain.

**Controls.** None. Nothing shipped changed. The code comment correction moves no number.

**Next.** (1) A coal *position* from coal's own annual scalars, in place of the 30 GW threshold.
Candidate: the year's metered gas level at which coal comes on, as one scalar a year, at coal's
grain like the thermal floor. Whether an annual scalar read from metered gas passes condition 1 must
be argued before an arm runs. Graded against F and M here, and against the meters' daytime, calm-day
profile. (2) Whether `CCGT_CAPACITY_MW = 30,000` is also wrong as a capacity: DUKES 5.11's CCGT
nameplate, de-rated by availability. Knowledge first. (3) §40's ROC recycle and 2019's missing
biomass unit stand. No level move: the shipped swing is still too wide in every year.

## 42. 2026-10-05 — COAL AT THE TOP OF THE MODEL'S OWN STACK: the right energy in the right season, run as a peaker, and every year gets worse

§41's NEXT (1). Measured, and nothing shipped changed. The scratch script, its output and the timestamped
predictions are in `/var/tmp/se-ep13-s42/` (`arm.py`, `out.txt`, `prediction.txt`). **Instrument check:**
an exec'd copy of `emissions_rate_t_per_mwh` reproduces the committed feed to five places (max diff 0.0).
It also matches the uninstrumented shape exactly.

**What crosses, argued before the arm ran.** §41 offered a candidate: the metered gas level at which coal
comes on. It is not used here. It is one number a year, but it is read off the half hours in which two
carbon-bearing fleets ran together. That makes it a statistic of the dispatch decision, which condition 1
exists to keep out. It is not a fact about steel. This arm takes a position that needs no gas reading.
Coal fills the top of the model's OWN thermal: `coal = min(cap_y, max(0, thermal − L_y))`, displacing
CCGT. `L_y` is solved each year so the model's mean coal equals the year's measured coal mean. Only coal's
two annual scalars cross. One is the mean, which §41's buildable arm F already uses. The other is the
maximum, the shipped `coal_capacity_by_year`. This is the coal counterpart of §25's PS water-fill and
§36's biomass envelope. The 30 GW threshold is replaced by `L_y`.

**Predictions (23:10Z, before `arm.py`).** P1: L runs coal above 50 MW in ≤30% of half hours in each of
2019–22. P2: L's calm-to-windy coal ratio exceeds the meters' in 2019 and 2021. P3: L raises correlation
over base by ≥0.005 in 2019 and 2020, and beats §41's F in each of 2019–21. P4: L widens between-day
against base in 2019–21. P5: 2024's correlation moves ≤0.003. P6: the solved 2019 level is 15–25 GW of
model thermal.

**Placebo Z** is the same code with `L_y = ∞` (no coal at all). It reproduces base's statistics to four
places in 2020–24 and differs only in 2019, by the shipped band's 19 MW. That matches §41's placebo.

| base → L | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| solved `L_y`, GW of model thermal (coal cap, GW) | 18.6 (7.6) | 16.6 (4.4) | 17.2 (3.9) | 17.1 (3.0) | 15.0 (2.0) | 16.5 (1.9) |
| correlation | .959/**.943** | .931/**.924** | .970/**.950** | .982/**.961** | .978/**.968** | .972/.971 |
| within-day overstated by | 1.06/1.38 | 1.10/1.32 | 1.00/1.23 | 1.00/1.14 | 1.02/1.12 | 1.07/1.11 |
| between-day overstated by | 1.05/1.27 | 1.11/1.27 | 1.01/1.14 | 1.07/1.17 | 1.07/1.15 | 1.07/1.13 |
| mean abs error | .061/.097 | .104/.129 | .055/.083 | .053/.092 | .068/.097 | .089/.100 |
| half hours with coal > 50 MW, L / meters | .19/.56 | .18/.40 | .22/.60 | .25/.56 | .19/.50 | .11/.36 |
| coal on calm / windy decile days, MW, L | 2,459/0 | 1,921/0 | 1,391/0 | 1,480/0 | 1,040/0 | 637/0 |
| the same, meters | 1,419/313 | 1,039/157 | 960/145 | 846/99 | 506/146 | 190/93 |
| Oct–Mar share of coal, L / meters | .92/.86 | .75/.91 | .82/.65 | .65/.68 | .84/.79 | .97/.66 |
| half-hourly correlation of L's coal with metered coal | .78 | .51 | .68 | .43 | .51 | .28 |

Headline p95/p5 goes from 1.22 to **1.45**, and max/min from 1.21 to 1.40.

**Against the predictions.** P1 held (0.11–0.25). P2 held, and to the limit: L serves no coal at all on
the windiest tenth of days in any year, where the meters ran 93–313 MW. **P3 was refuted outright.**
Correlation FELL in every year, by 0.007 to 0.021, against base and against F. P4 held, and by far
more than predicted: between-day overstatement went from 1.01–1.11 to 1.13–1.27. P5 held (−0.001). P6
held (18.6 GW).

**What it establishes.**
- **Coal was not a peaker on GB's residual, in any year 2019–24.** Put at the top of the model's stack
  with the right annual energy, coal gets its season roughly right. Its winter share is within 0.17 of
  the meters' in four years of six. Its half-hourly timing correlates 0.28–0.78 with the meters. But
  it runs in a third to a half as many half hours as the real fleet did, at two to three times the
  output, and never on a windy day. The real fleet kept 93–313 MW running on the windiest days.
  Concentrating the energy that much adds carbon at the dirty end of every day and every calm week.
  Both swings get wider, and they were already too wide.
- **Two buildable shapes now bracket coal, and both fail.** §41's flat block is too flat: correlation
  falls 0.005 in 2019–20. This top-fill is too peaked: correlation falls 0.007–0.021 everywhere. The
  only arm that has improved anything is §41's monthly oracle (2020 correlation .931 to .953), and it
  times coal by the month. That is the same signal §41's P3 refutation pointed at. Coal ran through
  the summer of 2021 and from July 2022 because of the gas price, not the season and not the residual.
- **The same failure as §36.** An annual-grain envelope run as a rule on the model's own residual comes
  out bang-bang, for coal as it did for biomass. The fleet's real dispatch sits between "always on"
  and "only at the top", and no annual scalar we hold says where.
- **What does NOT follow.** That a blend of F and L would work. A mixing weight between them is a
  number nobody has published, so it is not tried here.

**Controls.** None. Nothing shipped changed, and the feed is byte-identical.

**Next.** (1) Coal's within-year timing as a PRICE question, not a residual one. `merit_order_
reconstruction.coal_srmc_gbp_per_mwh` already orders coal against gas, but the tree holds no coal
price series to feed it. Knowledge first: is a monthly published coal price (for example, the World
Bank Pink Sheet's monthly coal series, free) a fair input under condition 1? It is a traded index with
no NESO term, the same argument §40 made for MID. Would its monthly gas-coal switching grade against
§41's M oracle? (2) §41 NEXT (2) stands: whether `CCGT_CAPACITY_MW = 30,000` is right as a de-rated
capacity (DUKES 5.11). (3) §40's ROC recycle and 2019's missing biomass unit stand. No level move: the
shipped swing is still too wide in every year.

## 43. 2026-10-05 — COAL'S MONTH IS NOT ITS PRICE: the coal-gas cost gap ranks coal's months no better than demand does, and a monthly block shaped by the model's own thermal narrows the swing a household acts on

§42's NEXT (1), measured, with one follow-on arm. Nothing shipped changed. The scratch scripts, outputs and
timestamped predictions are in `/var/tmp/se-ep13-s43/` (`arm.py`, `arm2.py`, `armR.py`, `out*.txt`,
`prediction.txt`).

**What crosses, argued first.** The input is the World Bank Pink Sheet's monthly "Coal, South African"
series: f.o.b. Richards Bay, 6,000 kcal/kg NAR, $/t. It is free, and it is a traded index with no NESO
term and no GB dispatch statistic in it. That is the argument §40 made for MID, so condition 1 passes.
Gas is the Pink Sheet's TTF, the same series the tree already uses through FRED PNGASEUUSDM. The two
sources agree to cents in sampled months, but differ by $18 in October 2022 ($39 against $21). FX is
FRED EXUSUK, by month. Both fuels go through the tree's own `coal_srmc_gbp_per_mwh` and
`ccgt_srmc_gbp_per_mwh`, at fleet-average efficiency. `gap` is coal SRMC minus CCGT SRMC, in £/MWh
electrical; negative means coal was cheaper. Freight to ARA and the NAR-to-gross basis are left out. Both
are level shifts within a year, and a 5.4% gross bracket changes no month's sign in any year.

**An instrument fact found on the way.** The tree's ETS series is a NAMED GAP for 2022–24, and there
`carbon_price_total_gbp_per_tonne` returns CPS alone (£18/t). That makes coal look cheaper than gas in
every month of 2022–24. The carbon term is constant within a year, so within-year ranks are unaffected.
But for those years the SIGN is graded below by break-even carbon, not by the tree's total.

**Predictions (23:20Z, before any price was read).** P1: gap < 0 in ≥6 months of 2022, and ≤2 in each of
2019, 2020 and 2024. P2: the within-year Spearman ρ(−gap, metered monthly coal) is ≥0.5 in 2021 and 2022,
and |ρ| < 0.5 in at least 2 of 2019, 2020, 2023 and 2024. P3: pooled over 108 months (2016–24),
Pearson(gap, coal load factor) ≤ −0.3. P4: Newcastle coal in place of Richards Bay changes no P2 verdict.

| | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|
| ρ(−gap, metered coal), by month | .78 | .02 | .62 | .34 | **.03** | **.01** | .83 | −.90 |
| ρ(demand, metered coal), by month | .86 | .90 | .87 | .94 | .60 | .69 | .69 | .17 |
| ρ(−gap, demand) | .82 | −.21 | .69 | .47 | −.12 | −.32 | .81 | −.03 |
| months with coal cheaper (gap < 0) | 0 | 1 | 0 | 0 | 4 | 12 | (12) | (12) |
| total carbon at which coal = gas, £/t, min–max | 2–15 | 7–33 | −17–12 | −10–10 | 7–261 | 122–520 | 32–87 | 30–89 |

The demand row is the month's mean of the tree's demand cache, which starts in March 2016, so 2016 is not
in this table.

**Against the predictions.** P1 held where it can be graded. In 2019 and 2020 no month had coal cheaper,
and break-even carbon never exceeded £12/t against the tree's £40. In 2022 coal was cheaper in every month
at any carbon below £122/t. P1's 2024 leg is UNGRADED: break-even is £30–89/t, which straddles any
plausible 2024 total, and the tree holds none. **P2 was refuted in both legs.** The price ranks coal's
months at 0.03 in 2021 and 0.01 in 2022. Of 2019, 2020, 2023 and 2024, only 2020 is under 0.5. **P3 was
refuted** (−0.04, n = 108). P4 held. With Newcastle coal, 2019 is 0.80, 2020 0.45, 2021 0.03, 2022 0.19,
2023 0.59 and 2024 −0.87, so every verdict is unchanged.

**What it establishes.**
- **The month's price does not time GB coal, 2017–24.** In every year 2017–22, demand ranks coal's months
  better than the price gap does: 0.60–0.94 against 0.01–0.78. The years where the price looks right
  (2017, 2019, 2023) are the years where the price itself tracks demand (0.69–0.82), through gas's winter
  premium. Where price and demand part (2018, 2021, 2022), the price explains nothing (0.01–0.03).
- **The switch has no within-year variation in the years that matter.** In 2019 and 2020 coal was out of
  merit against fleet-average CCGT in every month. Even so it ran 2.0–2.4 GW in January and almost nothing
  in summer. In 2022 it was in merit in every month, and still ran from 9 MW to 990 MW by season. Coal's
  timing at monthly grain follows the residual in both regimes, not its own cost. §41's monthly oracle helps
  because it carries the SEASON, not the price.
- **2024's −0.90 is a closure, not a price.** Coal ran at 0 MW from October 2024, after Ratcliffe closed.
  The annual `coal_capacity_by_year` cannot see that, so every arm that sizes coal by year serves coal in
  Q4 2024.

**Arm R, the season with no price (predictions filed at 23:22Z, after P1–P4 were read).** Coal is
`min(cap_y, thermal_hh, k_y × the model's mean thermal for that month)`, flat within the month. `k_y` is
solved so the year's mean equals the measured mean. Only s42's two annual scalars cross, and the monthly
weight is the model's own thermal. P5: correlation rises ≥0.003 in 2019 and 2020, and moves ≤0.003 in
2023–24. P6: between-day ≤ base in 2019–21. P7: R's monthly coal ranks against the meters at ≥0.6 in each
of 2019–22. The instrument reproduces the committed feed exactly (max diff 0.0). The no-coal placebo is
§42's Z.

| base → R | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| correlation | .959/.958 | .931/.929 | .970/.970 | .982/.982 | .978/.978 | .972/.973 |
| within-day overstated by | 1.06/**0.93** | 1.10/0.99 | 1.00/**0.90** | 1.00/**0.93** | 1.02/**0.95** | 1.07/1.03 |
| between-day overstated by | 1.05/0.97 | 1.11/1.04 | 1.01/0.95 | 1.07/1.02 | 1.07/1.01 | 1.07/1.05 |
| mean abs error | .061/.058 | .104/.097 | .055/.055 | .053/.049 | .068/.063 | .089/.085 |
| monthly ρ, R's coal vs meters | .71 | .63 | .61 | −.02 | .49 | −.03 |
| half hours with coal > 50 MW, R / meters | 1.00/.56 | 1.00/.40 | 1.00/.60 | 1.00/.56 | 1.00/.50 | 1.00/.36 |

Headline p95/p5 goes from 1.22 to 1.07, and max/min from 1.21 to 0.89, which is now an understatement.
**P5 was refuted:** correlation fell 0.001 in 2019 and 0.002 in 2020. The 2023–24 leg held. P6 held. **P7
was refuted on 2022** (−0.02): in 2022 coal ran by something the model's thermal does not carry.

**Why R does not ship.** It improves between-day in every year, the headline in both statistics, and MAE in
5 of 6 years. But it moves within-day, the swing a household can act on, from at-or-above truth to BELOW it
in 4 of 6 years: 2021 goes from 1.00 to 0.90, and 2022 from 1.00 to 0.93. A coal block that runs all day
adds flat carbon to every half hour and compresses each day's ratio. The meters ran coal in only 36–60% of
half hours. That is the same failure as §41's F, at monthly rather than annual grain. Trading the axis the
product sells on for the axis it does not is not a fix. Correlation did not move.

**Controls.** None. Nothing shipped changed, and the feed is byte-identical.

**Next.** (1) Coal capacity by MONTH from published closure dates, which are public facts about steel. It
removes the coal every arm serves in Q4 2024 and in each closure year's tail. Measure it with base's
shape, not R's. (2) Coal's within-DAY shape is still the open question. F and R run it always on, L
runs it as a peaker, and the meters show neither (36–60% of half hours, 93–313 MW on windy days). No
annual or monthly scalar we hold has located it. (3) The tree's UK ETS is a named gap for 2022–24, so any
price-based coal arm in those years is ungradable for sign. That is already filed. (4) Still owed from
earlier passes: §41 NEXT (2), 30 GW as de-rated CCGT capacity (DUKES 5.11); §40's ROC recycle; and 2019's
missing biomass unit. No level move.
