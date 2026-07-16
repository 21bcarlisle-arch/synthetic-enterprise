# W1_6_physics_price_signal — DISCOVER pass (doc-only, no BUILD)

**Atom:** `W1_6_physics_price_signal` — "L4 price as a DERIVED output: national
weather → national demand + renewable output → residual demand → merit order
→ wholesale price (price is NEVER an independent draw)." `level_current: 0`,
`level_target: 3`, epoch 3 (BUILD-gated), `loop_stage: idle` (DISCOVER/FRAME
workable now, per EPOCH_GATING_AND_ATOM_AUTHORSHIP). `depends_on:
[W1_3_national_weather_signal, W1_5_premise_demand_shape]`.

**This pass does not edit `maturity_map.yaml`, write sim/company code, or
change `level_current`.** It is a repo audit (what already exists) plus a
grounding of the atom in real GB power-market price-formation structure. Scope
is `docs/design/` only, per this fork's instruction.

---

## 1. Repo audit — what already exists (honest accounting)

The prior FRAME pass for this atom (`docs/design/WEATHER_PHYSICS_HIERARCHY_DESIGN.md`
§1.4/§4) already asserts "no new price engine is built" and names the reuse
plan. This DISCOVER pass verified that claim against the actual code, and adds
one finding the FRAME pass's own citation does not surface: **the named engine
already failed its own calibration gate and was formally superseded**, a fact
recorded in `docs/calibration/price-engine.md` but not carried into the FRAME
doc's reuse table (§4) or open-questions section (§9).

### 1.1 `sim/price_engine.py` — the merit-order physics engine (Phase 3b, built)

Three components, all real code, not proposals:
- `gas_floor_price(gas_price_gbp_per_mwh, thermal_efficiency=0.50)` =
  `gas_price / thermal_efficiency` — the SRMC of a CCGT.
- `system_margin_price(gas_floor, demand_mw, renewable_generation_mw, gamma)` =
  `gas_floor * (demand/renewable_generation) ** gamma`, `gamma ∈ [1.5, 2.5]`
  enforced.
- `wind_power_output_fraction(wind_speed_ms, rated_power_mw)` — the standard
  idealised turbine power curve (cut-in 3 m/s → cubic ramp → rated at 12 m/s →
  cut-out 25 m/s). This is the exact function the FRAME doc's §1.4 step (3)
  and §4 table cite as reusable for wind output from L1 weather.
- `synthetic_price(...)` — chains gas floor → margin price.

15 tests exist (`tests/sim/test_price_engine.py`) covering boundary
conditions, monotonicity, gamma validation, cubic-ramp shape.

### 1.2 The calibration finding this atom must inherit honestly

`docs/calibration/price-engine.md` records a real calibration run
(`simulation/run_phase3b_calibration.py`) against real SSP for 2019 (calm) and
2022 (crisis), scanning `gamma` across the full spec'd `[1.5, 2.5]` range:

| Year | Actual SSP mean | Best gamma in spec range | MAE @ best | Correlation |
|---|---|---|---|---|
| 2019 | £41.75/MWh | 1.5 (range floor) | £496.33 | 0.203 |
| 2022 | £200.07/MWh | 1.5 (range floor) | £3,212.08 | 0.244 |

**The formula as specified overestimates real SSP by roughly 10x even at the
lowest allowed gamma, and gets monotonically worse as gamma rises toward
2.5** (these are the report's own measured figures, not re-derived here).
Diagnosis in the report: raw national MW inputs give
`demand_mw / renewable_generation_mw` a typical value of 3–5 (national
demand ~26.6 GW vs wind+solar ~8.0 GW in the 2022 sample), and raising even
that ratio to `gamma=1.5` multiplies the gas floor by ~6×, pushing prices
into the thousands of £/MWh — far past real SSP, which rarely exceeds a few
hundred £/MWh even in the 2022 crisis. Diagnostic-only exploration outside the
spec'd range found `gamma≈0` (i.e. price ≈ gas floor alone, ignoring the
margin ratio entirely) fit *better* than any spec'd gamma — meaning **the
margin term, in this raw-ratio form, actively hurts the fit at every value the
spec allows.**

**Consequence recorded in the same doc, dated 2026-06-11 (director-directed,
predates this atom's 2026-07-13 registration):** the physics formula was
*deferred*, and a statistical OLS regression (`SSP ~ gas_price + demand_mw +
wind_mw`, fit on the full 2016-2025 window, `simulation/run_phase3b_regression.py`)
became **"the active Phase 3b/Regime 2 deliverable for synthetic SSP
generation."** That regression achieves MAE £33.96/MWh (≈44% relative error)
against a mean of £77.19/MWh, R²≈0.39 over the full window — a materially
better fit than the physics formula, though still leaving most variance
unexplained (expected for a 3-feature linear model of a market also driven by
carbon prices, interconnector flows, plant outages, and genuinely non-linear
merit-order effects).

**Why this matters for W1_6 specifically:** the FRAME doc's §4 table says
"No new price engine is built... L4 wires the existing `price_engine.py`."
That is true as a *code-reuse* statement (the wind curve and the gas-floor
function are sound and reusable in isolation — the calibration failure is in
the *margin/ratio term*, not the gas floor or the turbine curve). But it is
materially incomplete as a *calibration* statement: the specific chained
formula (`gas_floor * (demand/renewable)^gamma`) the atom's own real-world
twin points to has *already failed* the exact calibration test the FRAME
doc's §9 says W1_6 must pass ("if the coherent-input price fails the SSP
calibration gate, that is a finding about the inputs, surfaced not silently
retuned"). This is not a new failure to discover at BUILD time — it is a
**known, already-measured failure of the identical formula**, and BUILD
should not re-discover it as if for the first time. The FRAME doc's own §9
correctly anticipates *a* possible mismatch; this DISCOVER pass narrows it to
a specific, already-quantified one.

### 1.3 What this does NOT mean

It does not mean W1_6 is unbuildable, or that the merit-order *structure* is
wrong. Two of the report's own live findings point to real, plausible causes,
both consistent with the FRAME doc's L4 chain (§1.4) rather than contradicting
it:
- **Missing residual-demand framing.** The report's raw ratio uses gross
  national demand over gross renewable generation. The FRAME doc's own step
  (4) already specifies **residual demand** (`RD = D_national − G_wind −
  G_solar`) over a **dispatchable margin** denominator, not raw demand over
  raw renewables — a materially different (and more physically correct)
  ratio than what was calibrated in Phase 3b. The calibration report's own
  "Recommendation" section proposes exactly this direction (option 2:
  "residual-demand-share formulation... the fraction of demand that must be
  met by thermal generation"), independently arriving at close to the FRAME
  doc's already-specified L4 chain. **This has not yet been calibrated** —
  the 2026-06-11 calibration run tested the *old* ratio, not the FRAME doc's
  residual-demand-over-margin form.
- **A missing cost term: carbon.** `grep`-audited this session — no file in
  `sim/`, `simulation/`, or `docs/design/`/`docs/market_research/` contains
  any reference to a carbon price, UK ETS, EU ETS, or an emissions factor.
  `gas_floor_price()` computes SRMC as `gas_price / thermal_efficiency` only.
  Real GB gas-plant SRMC (see §2 below) includes a carbon-cost term that is
  *not small* — UK ETS allowance prices materially affect which plant is
  marginal and by how much, especially post-2021. This is a genuine missing
  physics term, not previously flagged in the FRAME doc or the calibration
  report, and independent of the ratio-form fix above.

### 1.4 Other already-built, adjacent price/weather machinery (uncredited overlap check)

Continuing the pattern the sibling W1_3/W1_5 DISCOVER passes already found
(built-but-uncredited capability), this pass checked the wider neighbourhood:

- **`sim/weather_engine.py::fit_national_macro_model()`** (found by the prior
  W1_3 DISCOVER pass, re-confirmed here): a regime-switching mean-reverting
  AR1 over joint national temp/wind/cloud, with a 2-state Markov chain and
  regime-specific innovation covariance (`cov_standard` / `cov_stressed`).
  This is the **feed** for W1_6's step (1)/(3) (national weather → wind
  output), and is real, tested code — but its regime trigger is
  **wind-residual-magnitude alone** (`abs(wind_resid) > 90th pctile`), not the
  joint cold-∧-low-wind condition the FRAME doc's L1 design requires. W1_6
  inherits this gap one layer down: **until W1_3's regime mechanism is
  actually joint, the "cold-and-still" price spike this atom exists to
  demonstrate (FRAME §1.4, "the one-coherent-draw chain, demonstrated") has
  no mechanistic guarantee to inherit — it would currently arise (if at all)
  only through the innovation covariance's fitted temp/wind correlation, the
  exact copula-thinning failure mode the whole hierarchy exists to avoid.**
  This is a hard sequencing dependency already correctly encoded in `depends_on`
  ([W1_3, W1_5]), and this pass confirms it is real, not just formally listed.

- **`sim/scenario/bimodal_generator.py`** (Phase 35a) — a *separate*,
  already-built forward price generator: a two-regime (high-gas-fraction vs
  low-gas-fraction) Markov-switching model with named Dunkelflaute/negative-
  price/crisis-spike overlays, calibrated to
  `docs/market_research/price_distribution_high_renewables_2027.md` (R&D
  findings, not the merit-order formula). This is **content-calibrated, not
  physics-derived** — it draws price directly from a fitted bimodal
  distribution with hand-set means/stds/multipliers (e.g.
  `dunkelflaute_multiplier_mean=1.8`), not from gas/demand/renewables
  fundamentals. It already produces Dunkelflaute price premia, which is
  exactly the L4 "cold-and-still spike" phenomenon W1_6 targets, but **by a
  different, non-mechanistic route** that does not derive from any weather
  draw at all (no coupling to `weather_engine.py`'s regime, confirmed by
  W1_3's own DISCOVER pass, restated here because W1_6 is the atom this
  divergence is actually *about*). **Open design question (not resolved
  here):** does W1_6 retire/absorb `bimodal_generator.py`'s regime-switching
  logic once the physics chain lands (their outputs would otherwise
  overlap/conflict — two independent ways to generate a forward price series,
  one physics-derived, one distribution-fitted), or do they serve genuinely
  different purposes (e.g. bimodal_generator as a fast CURRICULUM content
  generator per R13, W1_6 as the BASELINE mechanism)? This is a real
  reconciliation question for BUILD, flagged, not answered.

- **`sim/weather_price_sensitivity.py`** — a *third*, independently-built
  price-adjustment mechanism: a lookback-window HDD-average multiplier applied
  to `sim/forward_curve.py`'s quoted forward price when the trailing window
  signals a cold spell (`COLD_SPELL_HDD_THRESHOLD = 8.0` HDD, multiplier
  applied — exact multiplier value not re-quoted here without re-reading the
  full file, left for BUILD). This is explicitly a **backward-looking,
  decision-time heuristic** (correctly scoped to the Point-in-Time Blindfold:
  it uses only the same historical lookback window `forward_curve.py` already
  uses), not a mechanistic weather→price chain — a different kind of
  approximation from both `price_engine.py` and `bimodal_generator.py`. Three
  distinct price-adjustment mechanisms with three distinct calibration bases
  currently coexist in the repo with no reconciliation between them.

- **`sim/forward_curve.py::generate_forward_price()`** — per the existing
  W1_2 DISCOVER/FRAME finding (already on record, restated for W1_6's
  benefit): entirely deterministic (EWMA spot + fixed seasonal shape +
  sqrt(tenor) term premium), no noise term, returns one point price never a
  distribution. This is the function `company/interfaces/sim_interface.py::get_forward_price()`
  actually calls today — confirmed by direct read this session
  (`company/interfaces/sim_interface.py` lines ~252–270): it loads real
  historical SSP/NBP records via `sim/system_prices_history.py` /
  `sim/cache_store.py` for `"2015-11-07"`..`"2025-06-07"` and has **no branch
  for dates beyond that window**. This is the concrete seam gap W1_6 (jointly
  with W1_2) must eventually close: there is currently no synthetic-future
  price source wired to the company-facing observable at all beyond the real
  historical window.

### 1.5 Summary table — existing vs needed

| Piece | Exists? | Where | Status |
|---|---|---|---|
| Gas-floor SRMC | Yes | `sim/price_engine.py::gas_floor_price` | No carbon term (gap, §1.3) |
| Turbine power curve | Yes | `sim/price_engine.py::wind_power_output_fraction` | Reusable as-is per FRAME §4 |
| Demand/renewable margin→price | Yes, but | `sim/price_engine.py::system_margin_price` | **Failed calibration in its raw-ratio form** (§1.2); FRAME's residual-demand form not yet tested |
| Regime-switching national weather | Yes, partial | `sim/weather_engine.py::fit_national_macro_model` | Wind-only trigger, not joint cold∧still (W1_3's own gap, inherited here) |
| Real Elexon demand/wind/solar ingestion | Yes | `sim/generation_demand_history.py` | Generator-anchor-ready |
| Real SSP ingestion (validation target) | Yes | `sim/system_prices_history.py` | Validator-anchor-ready |
| Distribution-fitted bimodal/Dunkelflaute price | Yes, separate | `sim/scenario/bimodal_generator.py` | Non-mechanistic, uncoupled to weather; reconciliation question open |
| Lookback HDD forward-price multiplier | Yes, separate | `sim/weather_price_sensitivity.py` | Backward-looking heuristic, Blindfold-correct, uncoupled to weather regime |
| Deterministic forward-curve pricer (company-facing) | Yes | `sim/forward_curve.py::generate_forward_price` | No branch beyond real 2025-06-07 window — the actual seam gap |
| Company-facing price observable | Yes | `company/interfaces/sim_interface.py::get_forward_price` | Reads only real historical SSP/NBP today |
| Carbon price / UK ETS term anywhere | **No** | — | Genuine gap, not previously flagged |
| Joint L1→L4 wiring (residual demand → price, one coherent draw) | **No** | — | This atom's actual scope |

---

## 2. Grounding in real GB power-market price formation

This section states, at the level of structure (not numbers — no network
access this session; anything with a specific figure is flagged), how the
real GB wholesale market actually forms price, so the sim's approximation can
be checked against the right real-world target rather than an invented one.

- **Marginal-cost merit-order dispatch.** GB's day-ahead/within-day markets
  (N2EX, EPEX SPOT day-ahead auctions) and the Balancing Mechanism both
  clear, in structure, by stacking generators from lowest to highest
  short-run marginal cost (SRMC) until supply meets demand; the last
  (marginal) unit dispatched sets the clearing/system price. This is the real
  structural analogue of `price_engine.py`'s "gas floor + margin" idea — the
  code's framing (a single representative gas-marginal-cost floor scaled by a
  margin-tightness term) is a **simplification** of the true merit-order
  stack (which has many plant types at many SRMCs — nuclear and
  must-run/CfD-backed renewables near-zero, mid-merit gas/CCGT, peaking
  OCGT/reciprocating engines/storage at the top), not a wrong structure, but
  a coarse one-parameter proxy for it. `[UNVERIFIED, no network this
  session]` exactly how good a proxy a single gas-floor-times-ratio term is
  for the true multi-plant stack across regimes is an open empirical question
  the calibration report already partially answers (badly, in its
  current raw-ratio form).
- **Gas-plant SRMC has (at least) two cost components in reality, this repo
  models one.** A CCGT's real marginal cost is approximately
  `gas_price / thermal_efficiency + carbon_price × emissions_factor /
  thermal_efficiency` (fuel cost plus the cost of surrendering emissions
  allowances per unit of generation). `sim/price_engine.py::gas_floor_price`
  implements only the first term. The UK operates its own carbon-pricing
  scheme (UK ETS, since Jan 2021, replacing participation in the EU ETS
  post-Brexit) `[UNVERIFIED specifics — scheme design, current allowance
  price, and historical trajectory not re-checked this session; BUILD must
  confirm against a real published source, e.g. ICE/UK ETS auction results or
  DESNZ carbon price statistics, not fabricate a number]`. Whether this
  term's omission materially contributes to the calibration report's ~10x
  overestimate is not something this pass can determine (the report's error
  direction is *overestimate*, and adding a carbon cost would push the floor
  *up*, so carbon omission is not obviously the fix — more likely the ratio
  term is the dominant error source per §1.2's diagnosis — but the omission
  is real and independent of that finding).
- **Fuel and carbon are not the whole story either.** Real GB SSP is also
  shaped by: interconnector flows (GB imports/exports with France, Belgium,
  Netherlands, Norway, Ireland — a real GB price can be set by a foreign
  marginal plant transmitted across a cable), plant outages/availability,
  Balancing Mechanism actions distinct from the day-ahead clearing price, and
  (structurally different from the wholesale price this atom targets)
  Contracts-for-Difference strike prices and the Capacity Market, which
  affect generator *revenue* but not the SSP/wholesale clearing price itself.
  None of these are in scope for W1_6 as specified (the FRAME doc's chain is
  gas + demand + renewables only) — named here so a reviewer knows what is
  *deliberately* left out (an honest simplification, C-S5-style) versus what
  is an *unnoticed* gap (carbon, per above).
- **Renewables have near-zero SRMC and set price only via their effect on
  residual demand, not by bidding a cost themselves.** This is exactly the
  structural role the FRAME doc's step (4) (`RD = D − G_wind − G_solar`)
  gives them — renewables subtract from demand the thermal fleet must serve,
  rather than entering the merit-order stack at their own price. This is the
  one piece of real structure the FRAME doc already gets right in a way the
  Phase 3b raw-ratio calibration did not test (raw demand/renewable ratio ≠
  residual demand).
- **Real SSP is far more volatile/spiky than a smooth convex function of a
  ratio would suggest**, because the merit-order stack is not a smooth curve
  — it has discrete steps (each plant's SRMC), and near-full dispatch a small
  demand increase can require a much more expensive marginal plant (true
  merit-order convexity), while price can also go negative when must-run
  low-carbon generation exceeds demand and no flexible demand/storage absorbs
  it (real, observed GB phenomenon — this is exactly what
  `bimodal_generator.py`'s "negative price days" component already
  approximates by calibration rather than mechanism). W1_6's chain as
  specified does not have a negative-price branch (the ratio form is
  strictly positive) — an open question for BUILD (§3).

---

## 3. Open questions (honest, not decided here)

1. **Ratio-form recalibration is required, not optional, before BUILD can
   claim this atom's chain "works."** The FRAME doc's residual-demand-over-
   dispatchable-margin form has never been calibrated against real SSP — only
   the older raw-demand/raw-renewable ratio has, and it failed. BUILD's first
   real step is re-running `simulation/run_phase3b_calibration.py` (or a
   successor) against the *new* ratio form before trusting the chain, per R12
   (price is a diagnostic, never tuned toward a benchmark) — if it still
   fails, that is itself the finding, not a reason to retune gamma further.
2. **Carbon-cost term: add now or register as a named simplification?** Not
   decided here. Given it's a real, structurally simple addition
   (`+ carbon_price × emissions_factor / thermal_efficiency`) and a currently
   *undetected* gap (as opposed to the deliberately-scoped-out
   interconnector/CM/CfD items), this seems cheap to add at BUILD — but the
   calibration direction (would it help or hurt the existing overestimate)
   needs checking against real carbon-price data first, not assumed.
3. **Does `bimodal_generator.py` get retired, merged, or kept as a distinct
   CURRICULUM-layer generator once W1_6 lands?** Three coexisting
   price-adjustment mechanisms (`price_engine.py` physics,
   `bimodal_generator.py` fitted-distribution, `weather_price_sensitivity.py`
   lookback-heuristic) is not obviously a design a reviewer would recognise
   as coherent. Flagged, not resolved — this may be a legitimate
   baseline/curriculum split (R13) rather than redundancy, but that has not
   been argued anywhere in the repo yet.
4. **Negative pricing and discrete merit-order steps** — the FRAME chain's
   ratio form cannot go negative or represent discrete plant-level jumps;
   whether this matters for the calibration bar (MAE/correlation against real
   SSP, which does include negative and spiky periods) is untested.
5. **W1_3's joint-regime gap is a hard blocker, already correctly captured in
   `depends_on`.** This pass re-confirms (does not re-litigate) that W1_6
   cannot mechanistically demonstrate the cold-and-still price spike until
   W1_3's regime trigger is jointly cold∧wind, not wind-residual-only.
6. **Exact multiplier/threshold values in `weather_price_sensitivity.py`**
   were not re-quoted in this pass (file read only in part); BUILD should
   read it in full before deciding whether it is absorbed into the W1_6
   chain or left as a separate mechanism.

---

## 4. What this DISCOVER pass changes

Nothing in `maturity_map.yaml`. No code. It corrects one specific
under-citation in the existing FRAME design (the Phase 3b calibration
*failure* of the exact formula the FRAME doc names for reuse was on record in
`docs/calibration/price-engine.md` but not carried into
`WEATHER_PHYSICS_HIERARCHY_DESIGN.md`'s own reuse table or open questions),
names one previously-unflagged gap (no carbon-cost term anywhere in the
repo), and surfaces a reconciliation question across three independently-built
price-adjustment mechanisms that BUILD will otherwise discover piecemeal.

---

*Sources read this session: `sim/price_engine.py` (full),
`docs/calibration/price-engine.md` (full), `sim/generation_demand_history.py`
(full), `sim/scenario/bimodal_generator.py` (partial, header + params),
`sim/weather_hdd.py` (partial), `sim/weather_price_sensitivity.py` (partial,
header), `sim/system_prices_history.py` (partial, header),
`sim/weather_engine.py` (grep, regime/covariance sections),
`company/interfaces/sim_interface.py` (grep + partial read, `get_forward_price`
path), `docs/design/WEATHER_PHYSICS_HIERARCHY_DESIGN.md` (full),
`docs/design/maturity_map.yaml` (W1_6/W1_3/W1_5/W1_2 entries). Grep audit for
carbon/ETS terms across `sim/`, `simulation/`, `docs/design/`,
`docs/market_research/` returned zero hits. No network access this session —
all real-world market-structure claims in §2 are stated at a structural level
and flagged `[UNVERIFIED]` where a specific figure would be needed;
BUILD/discovery-agent should confirm against a real published source
(Ofgem/Elexon/DESNZ/ICE) before citing any number.*
