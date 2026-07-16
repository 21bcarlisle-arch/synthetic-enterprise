# C13_weather_normalisation — DISCOVER pass (doc-only)

**Status:** DISCOVER, not FRAME. `C13_weather_normalisation` is `level_current: 0`,
`loop_stage: idle`, epoch 3, BUILD-gated to `W1_2_generate_futures`/the L1-L4 physics
landing first. This doc does not open BUILD, does not edit `maturity_map.yaml`, and
writes no sim/company code. It (a) audits what already exists in the repo so the
company-side twin is not duplicated, and (b) extends
`docs/design/WEATHER_PHYSICS_HIERARCHY_DESIGN.md` §6 (which already frames C13's wall,
gap formula, and hedging-frontier strategy at FRAME depth) with concrete, real-method
grounding for how a UK supplier actually weather-normalises, and how the gap would be
computed against the *current* seam code as it exists today, not a hypothetical one.

Relationship to the FRAME doc: §6 there is authoritative for the gap formula and the
wall statement — this doc does not re-derive them, it (1) confirms them against the
real repo state, (2) supplies the domain method (HDD/CDD regression, CWV, AQ weather
correction) the FRAME doc names only as "genuinely hard, genuinely done badly in
industry" without specifying the method, and (3) names the concrete seam gap (no
weather-observable method exists on `SimInterface` today) that BUILD will have to close.

---

## 1. Repo audit — what exists today (honest overlap check)

| File | Side | What it actually does | Overlap with C13? |
|---|---|---|---|
| `sim/weather_engine.py` | SIM | Phase-3c two-pass national-AR1 + regional-Cholesky weather generator, with a regime-switching **innovation covariance** (variance-widening "stressed" state, not the blocking-high mechanism the FRAME doc specifies for `W1_3`). Produces national + regional temperature/wind/solar/cloud series. | None — this is the L1/L2 *generator*, not a company model. It is what C13 would be measured *against*, never read directly (SIM internal). |
| `sim/weather_hdd.py` | SIM | Per-customer **HDD weather factor** for gas consumption: `get_hdd`/`get_monthly_hdd`/`get_weather_factor` read a real per-customer weather CSV (`sim/weather_data/{id}.csv`, Open-Meteo reanalysis for C1-C4 only, base temp 15.5°C per DECC/Ofgem domestic gas convention) and compare actual monthly HDD to a UK 1991-2020 Met-Office-sourced climate-normal table (`REFERENCE_MONTHLY_HDD`), clipped to [0.3, 2.0]. Called from `simulation/gas_settlement.py` and `simulation/run_phase2b.py`. | **Close but not the same thing — flagged explicitly.** This computes the SIM's own ground-truth weather-adjustment for gas *settlement volumes* (a physics input), using the customer's real weather CSV directly. It is SIM-side (reads `sim/weather_data/` unbounded, no as-of/wall discipline, feeds settlement math) — a real supplier does not get to read its own customers' true per-property temperature series like this; it only ever sees the *regional/national* published weather and its own confounded meter reads. C13 must NOT reuse `weather_hdd.py`'s code path — it must reconstruct the equivalent HDD/CDD *method* company-side, from observables only. This is the single most important "don't just import it" finding of this pass. |
| `sim/weather_price_sensitivity.py` | SIM | Forward-price cold-spell multiplier from a lookback-window HDD average (Point-in-Time-safe: only uses weather before `acquisition_date`). Seed constants flagged as provisional pending customer-archetype enrichment. | None directly — this is a pricing/forward-curve concern (feeds `W1_6`-style physics), not book demand normalisation. Worth noting C13's regional degree-day series, once it exists, is a plausible *future* company-side input to a cold-spell risk read, but that is out of scope here. |
| `simulation/weather_inputs.py` | SIM | Pure I/O: loads `sim/weather_data/{id}.csv` (temperature + cloud cover), resolving each of the ~31-account cast to whichever of C1-C4 shares its `location`. No settlement/company logic. | None — infrastructure only. Confirms the weather CSV coverage is genuinely thin (4 real locations backing the whole book today), which bears directly on C13's statistical-power caveat (§4). |
| `company/interfaces/sim_interface.py` (`SimInterface`/`StubSimInterface`/`LiveSimInterface`) | seam | Methods today: `get_settlement_data`, `get_forward_price`, `get_customer_status`, `notify_churn`, `notify_acquisition`, `get_churn_estimate`, `notify_retention_attempt`. **No weather/degree-day/forecast method exists.** | **Confirmed gap.** C13 cannot be built without a new typed crossing (a `get_regional_weather_forecast`/`get_regional_weather_outturn`-shaped method), consistent with the typed-flow-seam preference (BACKGROUND_LANE_AND_WALL.md) and the wall's own statement that regional weather is public/company-knowable. This is a **BUILD-time addition**, correctly not built now. |
| `company/interfaces/point_in_time_view.py` | seam | Docstring explicitly states scope: "price/forward observables via `market_data_port` now; **weather/generation/demand left for a later pass** unless a similar caller-trusted gap is found there too (not yet audited)." | **Direct confirmation from the codebase itself** that weather crossing the wall as a bounded, as-of-safe observable is unbuilt and known-unbuilt — not an oversight this pass discovered, an already-logged scope limit. C13's BUILD will be that "later pass" for the weather axis specifically. |
| `company/interfaces/recorded_sim_interface.py` | seam | Classifies weather as an **EXOGENOUS** observable (market curve / weather baseline / regulatory publications) suitable for pure replay in the low-memory recorded-trace path — the company's own actions cannot move the weather. | Confirms the correct wall classification for C13's inputs: regional weather forecast/outturn is exogenous-replayable; the company's own meter reads are endogenous (book-specific, must run live). |
| `saas/property_model.py` | company | Docstring references weather-driven demand (4c-2) and HDD but the module itself is property/archetype modelling, not a weather-normalisation regression. | No functional overlap found. |
| `company/compliance/domain_invariants.py` | company | TDCV (Typical Domestic Consumption Value) bands — Ofgem-sourced annual kWh bands by Low/Medium/High profile, **not** weather-normalised, no degree-day correction. | Not overlapping, but relevant: C13's no-skill baseline (§3) could plausibly be phrased against TDCV bands rather than a flat national degree-day factor — noted as an open question, §5. |
| `docs/design/COUPLED_TRIAD_DESIGN.md` §1 | design | General gap formula `gap = raw_gap/g0`, wall table (θ in SIM, b in company via `sim_interface.py`, gap computed only in harness), four worked examples (classification, attribution, TV-distance, detection-rate) — **no weather-specific worked example yet.** | C13 would be the **fifth** worked gap formula in that family; §5 below writes it in the same notation the other four use. |
| `background/coupled_triad.py::_AUTHORITATIVE_COUPLING` | code | Cross-check table currently has `W2_7→C9, W2_8→C10, W2_5→C7, W2_4→C6, W2_10→C12, W2_6→C8, W2_9→C11`. **`W1_5→C13` is NOT yet present** — the maturity-map entry's own note flags this ("extend `_AUTHORITATIVE_COUPLING` with `W1_5<->C13` when this twin opens for BUILD"), confirmed still true. | Named as an explicit BUILD-open action item, not done here (would require editing `background/coupled_triad.py`, out of this fork's scope). |

**Conclusion of the audit:** there is no existing company-side weather-normalisation
code to build on or duplicate. The closest-looking artefact (`sim/weather_hdd.py`) is
SIM-side ground truth and must specifically NOT be imported by the company twin — it
reads real per-customer weather files directly, which is exactly the kind of read a
real supplier cannot do. C13 is genuinely greenfield company-side work. The
`point_in_time_view.py` docstring's own "left for a later pass" line is independent
corroboration (written before this DISCOVER pass) that this is a real, known-open gap,
not one invented for this exercise.

---

## 2. How a real UK supplier weather-normalises demand (the actual method)

Named methods, real practice, so BUILD has a concrete target rather than an abstract
"regress against weather":

- **Heating/cooling degree days (HDD/CDD).** UK domestic gas convention: HDD base
  15.5°C (the base `sim/weather_hdd.py` already uses, DECC/Ofgem-sourced — same
  convention, different side of the wall). Electricity demand in GB is less
  strongly HDD-linear than gas (electric heating is a minority, but heat pumps and
  electric heating are growing — the same base-temperature regression method applies
  once a plausible base temp is fitted for the electric book).
- **Seasonal normal comparison.** NESO/National Grid ESO's own demand-forecasting
  practice compares actual national demand to a rolling **seasonal normal** (typically
  a multi-year, e.g. 10-30-year, average for the calendar day/period) and reports
  demand "weather-corrected to seasonal normal" — the same convention a supplier
  applies to its own book: normalise actual consumption to what it would have been
  under average/seasonal-normal weather, so book-growth and weather noise don't
  confound each other period to period.
- **Composite Weather Variable (CWV).** The GB gas industry (historically National
  Grid Gas Transmission, now Xoserve, for NDM demand estimation/allocation) uses a
  published **Composite Weather Variable** — a blend of effective temperature (a
  smoothed/lagged temperature capturing thermal lag in buildings) and wind chill,
  because wind materially affects real heat loss/heating demand beyond temperature
  alone. This is the industry's actual answer to "temperature alone under-explains
  gas demand" — directly relevant to C13 because the SIM's own L1-L4 physics
  (`WEATHER_PHYSICS_HIERARCHY_DESIGN.md` §1.3) already ties premise heating response
  to *local* weather including wind-driven effects, so a company model using
  temperature-only degree days would itself under-explain demand relative to the
  SIM's ground truth — a candidate **named simplification** for C13's first cut, not
  a defect to hide (per R10).
- **Weather correction in Annual Quantity (AQ) reviews.** Gas suppliers routinely
  weather-correct a customer's rolling annual consumption estimate (AQ) against the
  degree-day-normal for the estimation period, because raw year-on-year consumption
  swings mostly track weather, not the customer's underlying usage pattern changing —
  the direct real-world analogue of "book demand this period is confounded by weather,
  strip it out before drawing any other conclusion (churn risk, tariff performance,
  hedge adequacy)."
- **Regression-based normalisation.** The general statistical method behind all of
  the above: fit consumption (or consumption per unit HDD/CDD) as a function of
  degree days per segment/region using the supplier's own historical meter data,
  then use the fitted coefficient to predict what consumption *should* be under a
  given (e.g. published-forecast) weather outturn. This is the shape C13's company
  model should take: **a fitted regression over the company's own confounded meter
  history, not a hand-set physical constant** — genuinely uncertain, genuinely
  re-fittable, genuinely capable of being wrong when the book's composition shifts
  (new joiners, churn, tariff mix change) faster than the regression window adapts.
  This is precisely why real suppliers get weather-normalisation wrong in practice
  (per the director's framing) — the regression conflates population composition
  change with weather sensitivity unless refit disciplined about window length and
  segment stability.

**Labelled uncertainty:** the exact CWV formula coefficients, NESO's current
seasonal-normal window length, and the precise electric-heating base temperature are
not asserted here as specific numbers — they are named as real, checkable methods
whose exact current parameterisation BUILD must confirm against a real published
source (Historical Ground Truth) rather than invent, matching the FRAME doc's own
"§9 open questions" discipline for numeric constants.

---

## 3. The company-side model, concretely (extends FRAME §6.1-6.2)

**What C13 CAN observe (repeating the wall, made concrete against real seam
methods):**
- Published **national and regional** weather forecasts/outturns — Met Office-class
  publications in reality; in this repo, a **new** `SimInterface` method BUILD must
  add (§1 finding), backed by the SIM's L1/L2 series (`sim/weather_engine.py`
  successor once `W1_3`/`W1_4` land) but exposed only as the outturn value, never the
  latent regime label.
- Its own **meter reads** — already crossable via `get_settlement_data(mpan, period)`
  on the existing `SimInterface`, i.e. no new method needed for this half.
- Wholesale prices — already crossable via `get_forward_price`.

**What C13 CANNOT observe:** each premise's true `thermal_i`/`heating_type_i` (L3
ground truth in `simulation/household.py`), the latent regime label (L1 internal to
`sim/weather_engine.py`), or the counterfactual demand under different weather.

**The model C13 fits, concretely:** a per-segment (or, until segmentation exists,
book-wide) regression of observed consumption against a regional degree-day series
built from the *observable* regional weather feed — i.e. exactly the "regression-based
normalisation" method of §2, fitted on the company's own settlement history via
`get_settlement_data`, and evaluated by feeding a given weather outturn back through
the fitted coefficient to produce a **predicted demand**. This predicted demand is
`b_i` (or, aggregated, `D̂_book`) in the FRAME doc's §6.2 gap formula. Nothing here
changes that formula; this section fixes what "the company's fitted weather-
normalisation model" concretely is, so BUILD has a named regression, not an
unspecified black box.

---

## 4. Honest limits specific to a DISCOVER pass (not asserted as designed)

- **Statistical power.** `simulation/weather_inputs.py` confirms real weather CSVs
  exist for only 4 locations (C1-C4) across the current ~31-account cast; a company-
  side regression fit on this cast is thin. This mirrors the FRAME doc's own §9
  "small-cast statistical power" caveat and is not a new finding, but the audit
  independently reconfirms the CSV coverage number is exactly 4, not an approximation.
- **No region partition exists yet.** C13's regional degree-day input depends on
  `W1_4_regional_weather_field` landing first (map `depends_on` already states
  `W1_5_premise_demand_shape`, which itself depends on `W1_4`) — the region set
  (GSP groups vs DNO regions vs the 4 existing locations) is an explicit BUILD
  decision, not resolved here.
- **The seam method doesn't exist.** As found in §1, `SimInterface` has no
  weather-observable method today. Until it does, C13 cannot be built even once its
  BUILD gate opens — this is a same-epoch prerequisite, not a blocker on C13 itself
  (it would land as part of C13's own BUILD phase, consistent with the typed-flow-seam
  preference for new crossings).
- **`_AUTHORITATIVE_COUPLING` is stale.** `background/coupled_triad.py` does not yet
  list `W1_5→C13`; the map's own simplification note already says so. Not fixed here
  (out of this fork's `docs/design/`-only scope) — flagged as a concrete pre-BUILD
  action item.
- **CWV/seasonal-normal exact parameters are named methods, not sourced numbers**
  (§2's labelled uncertainty) — BUILD must confirm current published figures rather
  than trust this doc's descriptions of the method.

---

## 5. Open questions (honest, for BUILD/FRAME to resolve, not answered here)

1. Should C13's no-skill baseline `g0` (FRAME §6.2: "flat national degree-day
   correction") instead be phrased against Ofgem TDCV bands (`domain_invariants.py`),
   which are already a real, cited, segment-differentiated baseline in this repo? Both
   are legitimate "no book-specific skill" baselines; TDCV is coarser (three bands, no
   weather term at all) than a flat national HDD factor (has a weather term, no
   regional/segment term) — they fail differently and either choice should be named
   explicitly at BUILD, not left implicit.
2. Electric-heating base temperature: real UK gas practice fixes 15.5°C; there is no
   settled equivalent constant for the electric-heating-inclusive book this
   simulation runs (heat pumps, resistive heating, mixed with non-heating load).
   BUILD should fit this from real electricity-demand-vs-temperature data
   (`sim/generation_demand_history.py` real Elexon demand is the generator anchor
   candidate) rather than reuse the gas figure by default.
3. Should the CWV wind-chill term be included in C13's first cut, or deferred as a
   named simplification (temperature-only HDD first, wind-adjusted CWV later)? §2
   argues temperature-only will systematically under-explain demand relative to the
   SIM's wind-coupled L3 physics once `W1_5` lands — worth deciding explicitly rather
   than discovering it as an unexplained residual at BUILD.
4. Refit cadence/window: how often does C13 re-fit its regression, and over what
   trailing window, given the book composition (new joiners/churners/tariff mix)
   changes over time and a stale window is exactly the real-world failure mode named
   in §2 ("weather-correction is a known error-prone step" — because suppliers under-
   or over-refit). Not designed here; a genuine BUILD-time judgement call.

---

*Sources consulted (repo, this pass): `sim/weather_engine.py`, `sim/weather_hdd.py`,
`sim/weather_price_sensitivity.py`, `simulation/weather_inputs.py`,
`company/interfaces/sim_interface.py`, `company/interfaces/point_in_time_view.py`,
`company/interfaces/recorded_sim_interface.py`, `saas/property_model.py`,
`company/compliance/domain_invariants.py`, `docs/design/COUPLED_TRIAD_DESIGN.md`,
`docs/design/WEATHER_PHYSICS_HIERARCHY_DESIGN.md`, `background/coupled_triad.py`,
`docs/design/maturity_map.yaml` (`C13_weather_normalisation` entry, read not edited).
Domain methods (HDD/CDD conventions, CWV, seasonal-normal, AQ weather correction, gas
NDM allocation practice) are named from general UK-energy-industry domain knowledge as
real, checkable methods; exact current-edition figures/coefficients are explicitly
flagged uncertain per §2/§4 and left for BUILD to confirm against a real published
source, per Historical Ground Truth.*
