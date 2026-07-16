# W1_4_regional_weather_field — DISCOVER pass (doc-only)

**Status:** DISCOVER, not FRAME/BUILD. `W1_4_regional_weather_field` is `level_current: 0`,
`level_target: 3`, `loop_stage: idle`, epoch 3, BUILD-gated behind `W1_3_national_weather_signal`
and (per CLAUDE.md's epoch gating) not opened until Epoch 3. This doc writes no sim/company code,
edits neither `maturity_map.yaml` nor any engine, and touches only `docs/design/`. It (a) audits
what already exists so the atom is not re-registered as greenfield when it isn't, and (b) grounds
the L2 "regional weather field" target in **real UK regional structure** (DNO/GSP regions,
regional weather variation, and its demand/renewable-output consequences) so BUILD has a concrete,
source-anchored target rather than an abstract "add regions" instruction.

**Relationship to `docs/design/WEATHER_PHYSICS_HIERARCHY_DESIGN.md` (the FRAME doc, §1.2):** that
doc is authoritative for the L2 *mechanism* — the projection-based aggregation-consistency
invariant (I1), the distance-keyed covariance kernel, the R15 mutation test shape, the four-layer
substream discipline. This doc does not re-derive or duplicate that design. It adds the thing the
FRAME doc explicitly deferred to "BUILD's first decision" (§9 there: *"Region partition and demand
weights `wᵣ` — GSP groups vs DNO regions vs an extended version of the four existing locations...
named as the first BUILD decision"*): a concrete audit of what real regional structure already
lives in this repo, and what a genuine 14-region field would add over the current 4-point one.
It also updates the map's own running finding (2026-07-15 DISCOVER note, same atom) that the
regional mechanism "substantially EXISTS" — this pass confirms that finding, narrows exactly what
"regional" should mean, and adds the real-UK-structure grounding that finding did not yet supply.

---

## 1. Repo audit — what exists today (honest overlap check)

| File | What it actually does | Regional? | Overlap with W1_4's L2 target |
|---|---|---|---|
| `sim/weather_engine.py` (Phase 3c, Pass 2: `fit_regional_cholesky`/`simulate_regional_deviations`) | Fits a **cross-location covariance** of `(location − national)` daily deviations for temperature/wind/cloud, Cholesky-factors it, and draws correlated per-location deviations from a shared `N(0,I)` draw. This genuinely **preserves real spatial correlation structure** between locations (Cornwall-like and Aberdeen-like locations are not independent draws) and is "physically bound" to the national Pass-1 series (the deviation is added on top of the national level, never replacing it). | **Only 4 points**, not regions. `location_daily`/`location_ids` are whichever locations the caller supplies calibration data for — see next row. | This **is** the spatially-correlated-deviation half of L2, already built and already correctly reusing the Cholesky factorisation the FRAME doc names as directly reusable. It is NOT yet keyed to any real administrative/settlement region, and NOT yet aggregation-consistent (next finding). |
| `sim/weather_data/{id}.csv` (4 files: `C1.csv`, `C2.csv`, `C3.csv`, `C4.csv`) | Real Open-Meteo historical reanalysis daily weather, one file per calibration location. | The engine's own docstring names the four as **London/Manchester/Glasgow/Cotswolds** — a hand-picked spread of point locations for calibration variety, not a partition of GB into administrative/settlement regions and not weighted by anything. | This is the entirety of the real weather data backing "regional" variation today — 4 points, not 14 regions, and no demand weight attached to any of them. |
| `simulation/weather_inputs.py` | Resolves every customer in `saas.customers.CUSTOMERS` (the ~31-account cast) to whichever of C1-C4 shares its exact `location` dict, so weather coverage is genuinely **4 real series total**, reused across the book. | Confirms the same finding from the point-weather side: there is no independent per-customer or per-region weather today, only 4 shared source series. | Directly relevant to what "regional" would add: today two customers "in the same region" get *identical* weather only if they happen to share the exact same hand-coded `location` dict; there is no region concept a new customer could be *assigned to*. |
| `sim/weather_hdd.py` | Per-customer HDD/weather-factor calculation reading the same 4 CSVs via `_resolve_source_cid`. UK base temp 15.5°C (DECC/Ofgem convention). | Same 4-point limitation, one level up the stack (gas settlement). | A regional field, once built, would be the natural upstream input here instead of the flat per-customer CSV lookup — not changed now. |
| `sim/weather_price_sensitivity.py` | National cold-spell forward-price multiplier from a lookback HDD average. | National only — no regional signal reaches pricing today. | Confirms L4 (`W1_6`) currently has no regional weather input to consume even once L2 exists; that wiring is a separate, later atom. |
| `company/market/duos_ledger.py::DNOArea` | An **already-built, real-UK-structure enum**: 14 named DNO licence-area values (`NORTHERN`, `YORKSHIRE`, `EAST_MIDLANDS`, `WEST_MIDLANDS`, `SOUTH_WESTERN`, `SOUTHERN`, `EASTERN`, `LONDON`, `SOUTH_EASTERN`, `MERSEYRAIL`, `NORTH_WESTERN`, `EAST_OF_SCOTLAND`, `HYDRO`, `SOUTH_WALES`), used today purely for **DUoS network-charge billing** (a real per-region unit rate table). | **Yes — this is a genuine 14-region UK taxonomy already living in the repo**, just on the billing side of the codebase, disconnected from weather entirely. | **The single most useful finding of this pass.** A regional weather field needs exactly this kind of real regional key. Rather than inventing a second, weather-specific region taxonomy, W1_4 should ask whether this *same* `DNOArea` enum (or the GSP-group set it approximates) is the right key to reuse — one canonical UK-region identifier used by both a billing module and a weather module, instead of two disconnected regional worldviews. See §4 for the naming caveats this enum itself carries. |
| `company/interfaces/sim_interface.py` / `point_in_time_view.py` | No weather-shaped method exists on the seam at all (confirmed independently by the `C13_weather_normalisation` DISCOVER pass, `docs/design/C13_WEATHER_NORMALISATION_DISCOVER.md` §1). | N/A | Regional weather, once built, is public/company-knowable (real forecasts and outturns are published) — it would cross the wall through a new typed method, not built now. |

**Conclusion of the audit, consistent with and sharpening the map's own 2026-07-15 finding on
this atom:** the *mechanism* for spatially-correlated regional deviation (Cholesky-factored
cross-location covariance, physically bound to a national front) is real and already built. What
does **not** exist is (a) any real UK regional partition behind it — today's "regions" are 4
hand-picked calibration points, not GSP groups or DNO areas, (b) any demand weight per region, and
(c) the aggregation-consistency invariant (§2 below) that the map's own DoD makes load-bearing.
This DISCOVER pass's job is to ground (a) and (b) in real structure; the FRAME doc already designed
(c)'s mechanism.

---

## 2. What a REGIONAL field concretely adds beyond today's 4-point weather

### 2.1 The real UK region set

GB electricity distribution is organised into **14 DNO licence areas**, operated by 6 DNO
groups (post-consolidation ownership; the licence areas themselves are the settlement-relevant
unit, not the parent company):

- UK Power Networks — London, Eastern, South Eastern (3 areas)
- National Grid Electricity Distribution (formerly Western Power Distribution) — East Midlands,
  West Midlands, South West, South Wales (4 areas)
- Electricity North West — North West (1 area)
- Northern Powergrid — Yorkshire, North East (2 areas)
- SP Energy Networks — SP Distribution (South/Central Scotland), SP Manweb (Merseyside &
  North Wales) (2 areas)
- Scottish and Southern Electricity Networks — Southern Electric Power Distribution (central
  southern England), Scottish Hydro Electric Power Distribution (North Scotland) (2 areas)

Total: 14. **This project already has a 14-value enum for exactly this partition**
(`company/market/duos_ledger.py::DNOArea`), used for DUoS billing. Two of its value names look
like plausible mismatches against the real licence-area names above and are flagged **unverified,
not corrected here** (Historical Ground Truth discipline — a BUILD-time check against a primary
source, not asserted as fact in this DISCOVER pass):
- `MERSEYRAIL` — almost certainly intended as SP Manweb's area (Merseyside & North Wales); "Merseyrail"
  is a Liverpool rail operator, not a DNO area name, so this reads like a naming slip in the
  existing enum, not a real licence-area name.
- `EAST_OF_SCOTLAND` / `HYDRO` — the real Scottish split is South/Central Scotland (SP Distribution)
  vs North Scotland (Scottish Hydro Electric Power Distribution, colloquially "Hydro"); `HYDRO` maps
  cleanly, `EAST_OF_SCOTLAND` less obviously to a real licence-area name.

Separately, GB settlement/profiling also uses **GSP Groups** (also ~14, lettered, used for
supplier "GSP Group Take" line-loss adjustment — referenced already in `docs/data-sources/profile-class-1.md`
and `PROJECT_OVERVIEW.md`'s MeterPoint model) — a closely related but not necessarily identical
partition to DNO licence areas. Which of the two (DNO areas vs GSP groups) is the more
settlement-correct key for a weather field is named here as an **open BUILD decision**, not
resolved in this pass — see §4.

### 2.2 What real regional variation would add over the current national+4-point model

None of the figures below are asserted as calibration-ready numbers — they are named as the
**real, well-documented structural facts** a 14-region field would need to reproduce, each flagged
for BUILD-time verification against a primary source (Met Office climate normals, DESNZ sub-national
consumption/generation statistics) rather than fabricated here:

- **Temperature gradient.** GB has a real, persistent north-south and coastal-inland temperature
  gradient — northern Scotland and inland/upland areas run measurably colder in winter than London
  and the south coast on the same day, and this gradient is the direct driver of regional heating-demand
  variation (higher HDD in the north). The *existence* and *sign* of this gradient is well established
  (Met Office climate normals); the *magnitude* per region-pair is a BUILD-time calibration question,
  not asserted here.
- **Wind resource concentration.** GB's wind generation capacity (onshore and offshore) is heavily
  concentrated in Scotland and the North Sea approaches, not evenly spread across the 14 regions —
  a blocking-high or wind-drought day does not hit "GB wind output" as one undifferentiated number,
  it hits specific regions' capacity harder than others. This matters directly for `W1_6`'s residual-demand
  chain: national wind output is a capacity-weighted sum over regions with very different installed
  wind capacity, not a flat multiplier on a single national wind speed. Exact regional capacity shares
  are a BUILD-time DESNZ/NESO data pull, not stated here.
- **Solar resource gradient.** Solar irradiance in GB has a real south-north and (to a lesser extent)
  east-west gradient — the south of England receives measurably more annual and peak-summer irradiance
  than Scotland — relevant to any region with meaningful embedded solar capacity. Again: real,
  well-documented direction; magnitude is a BUILD-time calibration item.
- **Demand weights are not uniform.** The 14 regions do not carry equal demand share — London/South
  East and the other UKPN/NGED areas cover far more customers/consumption than, say, North Scotland.
  The aggregation-consistency invariant (§2.3) is **only physically meaningful if `wᵣ` is a real
  demand-share weight**, not an equal 1/14 split; sourcing those weights from DESNZ sub-national
  consumption statistics (not fabricated, not derived from this project's own tiny ~31-account
  cast) is itself named as the first concrete BUILD task, consistent with the FRAME doc's own
  anchoring rule (generator/validator must be different real sources).

### 2.3 The aggregation-consistency invariant (restated briefly; FRAME doc is authoritative)

The FRAME doc (§1.2, §2) already specifies the exact mechanism this atom's own DoD requires and
the map's 2026-07-15 finding flags as the real remaining gap: a demand-weighted regional aggregate
must reconcile to the national series **by construction** (a projection step
`Δ'_r = Δ_r − Σ_s w_s·Δ_s` onto the zero-weighted-mean manifold, not a hoped-for property of a raw
draw), proven by an R15 mutation test that perturbs one region off-manifold and asserts the
reconciliation check fires. This DISCOVER pass adds nothing to that mechanism design — it confirms
it is still unbuilt (no such projection or invariant exists anywhere in `sim/weather_engine.py`
today; grep of `tests/sim/test_weather_engine.py` finds coverage of the Cholesky fit/simulate
functions only, no reconciliation test) and supplies the real `wᵣ` sourcing question (§2.2) the
FRAME doc left as a named BUILD decision.

---

## 3. Concrete BUILD scope this atom actually has left (not started now)

Restated precisely so a future BUILD pass does not re-discover this from scratch:

1. **Region partition decision** — DNO licence areas (reuse/fix `DNOArea`) vs GSP Groups vs a
   finer grid; a real, cited choice, not both maintained in parallel (§4 leaves this open).
2. **Real demand weights `wᵣ`** — sourced from DESNZ sub-national electricity/gas consumption
   statistics (a genuinely different source than anything this project generates), not derived
   from the project's own small customer cast.
3. **Extend the Cholesky calibration from 4 points to the full region set** — the existing
   `fit_regional_cholesky`/`simulate_regional_deviations` machinery in `weather_engine.py` is
   architecturally reusable as-is (it already accepts an arbitrary `location_daily` dict keyed by
   location id); this is a calibration-data-extension exercise, not a new algorithm.
4. **The aggregation-consistency projection + its R15 mutation test** — genuinely unbuilt; the
   real remaining engineering work per the map's own finding.
5. **Wire regional output into `W1_6`'s renewable-output step** (wind/solar capacity-weighted by
   region, §2.2) — named here as a real consequence of going regional, but is `W1_6`'s scope
   (`depends_on` already sequences `W1_6` after `W1_3`/`W1_5`, not `W1_4` directly — worth the
   orchestrator checking whether `W1_6` should also declare a dependency on `W1_4` once regional
   generation-mix wiring is real, since today `W1_6`'s design in the FRAME doc treats wind/solar
   as national-only).

None of this is built in this pass — doc-only, per scope.

---

## 4. Honest open questions (not resolved here)

- **DNO areas vs GSP Groups vs a coarser/finer grid** — which real partition is the settlement-correct
  key for a weather field is a genuine open BUILD decision. DNO areas are the natural fit for tying
  into the *existing* `DUoSLedger` billing code (one canonical region key across two lanes); GSP
  Groups are the natural fit if the intent is closer alignment with Elexon/BSC settlement profiling
  (`docs/data-sources/profile-class-1.md`'s "GSP Group Take"). This pass does not adjudicate it.
- **`DNOArea`'s `MERSEYRAIL`/`EAST_OF_SCOTLAND` naming** — flagged as likely imprecise against real
  DNO licence-area names (§2.1) but **not corrected here**; a BUILD-time check against a primary
  source (Ofgem's licensed DNO list) is the right venue, not a guess in a DISCOVER doc.
  Correcting a billing enum is out of this atom's `file_scope` (`docs/design` only) regardless.
- **Real demand-weight figures** — no numbers are stated in this doc; DESNZ sub-national statistics
  are named as the right class of source, not fetched (no network access available to this fork).
- **Regional wind/solar capacity shares** — same caveat; a real DESNZ/NESO data pull is needed before
  any specific regional generation-mix number is used in `W1_6`'s wiring.
- **Whether 4 calibration points can be meaningfully extended to 14 regions without new real
  weather data** — `sim/weather_data/` holds only 4 real Open-Meteo pulls today (C1-C4). A genuine
  14-region field needs either 10 more real per-region pulls (extending `sim/weather_ingestor.py`,
  which already hits the real Open-Meteo archive per Historical Ground Truth) or a documented,
  labelled interpolation/extrapolation scheme from the 4 real points — the former is more honest
  and is architecturally trivial given the ingestor already exists; a BUILD-time decision, not
  resolved here.
- **Relationship to `W2_2_population_draw`** — once customers are assigned a real region rather
  than a hand-coded `location` dict shared by coincidence, population draw and regional weather
  become coupled (a customer's region should probably be drawn consistent with real regional
  population/demand shares, not independently of them) — flagged, not designed, here.

---

## 5. Level-current note (observation only, no self-write)

Consistent with the map's own sole-map-writer discipline: this pass does **not** propose a level
change. The map's 2026-07-15 finding on this same atom already flagged `level_current=0` as
possibly under-stating the built Cholesky mechanism; this pass's own view is narrower and
consistent with that flag — the *spatial-correlation mechanism* is real (weighs toward L1-ish
credit), but **zero** of the real-UK-region grounding (region partition, demand weights, the
aggregation-consistency invariant, its mutation test) exists yet, which is precisely what this
atom's DoD (L2 target: "spatially-correlated regional deviations that are AGGREGATION-CONSISTENT
with the national signal") makes load-bearing. Re-levelling remains the orchestrator/director's
call.

---

*Sources: `sim/weather_engine.py` (Pass 2 Cholesky mechanism, read directly this pass);
`sim/weather_data/{C1,C2,C3,C4}.csv` + `simulation/weather_inputs.py` (confirms 4-point-only
coverage); `sim/weather_hdd.py`, `sim/weather_price_sensitivity.py` (downstream consumers, unchanged);
`company/market/duos_ledger.py::DNOArea` (existing real 14-region UK taxonomy, billing side);
`docs/data-sources/profile-class-1.md`, `docs/PROJECT_OVERVIEW.md` (GSP Group references elsewhere
in the repo); `docs/design/WEATHER_PHYSICS_HIERARCHY_DESIGN.md` §1.2/§2/§9 (authoritative L2
mechanism design, aggregation invariant, and the "first BUILD decision" framing this doc answers
part of); `docs/design/C13_WEATHER_NORMALISATION_DISCOVER.md` (confirms no weather method exists
on the company-facing seam); `docs/design/maturity_map.yaml` (`W1_4_regional_weather_field` and
`W1_3_national_weather_signal` entries, both DISCOVER-pass simplification notes read directly).
General DNO/GSP structural facts (14 DNO licence areas, 6 owning groups, Scotland/North Sea wind
concentration, south-of-England solar gradient) are standard, widely-published GB electricity-market
structure; specific magnitudes are explicitly NOT asserted and are flagged for a BUILD-time
discovery-agent pass against DESNZ/Met Office/NESO primary sources before any calibration relies on
them.*
