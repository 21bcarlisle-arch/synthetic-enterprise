# W1_7 — Renewable capacity + generation-mix evolution over time (FRAME)

**Atom:** `W1_7_renewable_capacity_trends` (lane `W1_market_weather`, epoch 3, L0→3, `loop_stage: idle`)
**Stage:** FRAME (Lane-3 DISCOVER/FRAME, doc-only, **NO LEVEL MOVE** — L1 "Skeletal" requires BUILT
code per the rubric and this atom is Epoch-3 BUILD-gated, so a doc cannot move it off L0).
**Depends on:** `W1_6_physics_price_signal` (the merit-order price physics must land first — this
atom is a *trend layer on top of* the merit order, not a change to it).
**Author:** H17 Lane-3 governed fork, 2026-07-16. Grounded by reading `sim/generation_demand_history.py`,
`sim/price_engine.py`'s role in `WEATHER_PHYSICS_HIERARCHY_DESIGN.md` §5/§8, and the real GB
capacity record. No BUILD code; no map edit (F1 — level recorded via atom_status inbox).

---

## 1. The gap this atom owns (one sentence)

The merit-order price physics (`sim/price_engine.py`, L4 of the weather hierarchy) treats installed
**wind and solar capacity as a calibrated constant** — `WEATHER_PHYSICS_HIERARCHY_DESIGN.md` §8 says so
explicitly: *"today L4 treats capacity as a calibrated constant; the trend is a later layer on top."*
That is false to reality: GB's renewable fleet roughly **tripled** across the 2016→2025 window, and the
generation *mix* shifted structurally (coal → gas → wind), which is the single biggest driver of the
falling-baseload / rising-price-volatility / more-frequent-negative-pricing regime the sim's own price
engine is trying to reproduce. W1_7 makes capacity **time-varying** so the same weather draw produces a
*different* residual-demand → price mapping in 2016 than in 2025.

## 2. Why it is distinct from its neighbours (no overlap)

- **W1_3/W1_4/W1_5 (weather signal)** produce the *wind resource* `W_national(t)` and its regional/premise
  descendants — the **fuel**. W1_7 owns the **capacity that converts that fuel into MW**:
  `G_wind(t) = capacity_wind(τ) · power_curve(W_national(t))` — the hierarchy design's own equation (3),
  where today `capacity_wind` is a scalar and W1_7 makes it `capacity_wind(τ)`, a function of calendar
  epoch `τ` (distinct from the fast weather clock `t`).
- **W1_6 (physics price signal)** owns the merit-order mapping residual-demand → price. W1_7 does **not**
  re-open that mapping (R12 / §8: "L4 does not re-open the merit-order calibration"); it feeds W1_6 a
  *time-correct* renewable-generation input. If the coherent time-varying input then fails the existing
  SSP calibration gate, that is a **finding about the inputs**, surfaced not retuned.
- **W1_2 (synthetic futures)** is a stochastic *price-path* generator (the `bimodal_generator.py`
  mechanism). W1_7 is **not stochastic** — installed capacity is an observed/administered trajectory
  (auction results, commissioning dates), not a random walk. Its forward extension is *curriculum*
  (§6), not noise.

## 3. Real-world anchors (the generator side)

The generator is anchored to the **real GB capacity + generation record**, which the sim already partly
ingests:

- **Actual half-hourly renewable output, 2016→present** is already retrievable —
  `sim/generation_demand_history.py::get_demand_outturn_range` + the AGWS endpoint
  (`/generation/actual/per-type/wind-and-solar`, Elexon Insights Solution) return per-`psrType`
  MW for `Wind Onshore`, `Wind Offshore`, `Solar`. This is the **outturn**, i.e. capacity × weather;
  W1_7 needs the *capacity* factor separated from the weather factor.
- **Installed capacity by technology and year** — DESNZ/DUKES (Digest of UK Energy Statistics,
  Chapter 6 renewables) and NESO's historical registered-capacity series. Real shape to reproduce
  (order-of-magnitude, to be pinned at BUILD by a discovery-agent pass, **not** asserted here):
  GB offshore wind ~5→15 GW, onshore wind ~9→14 GW, solar PV ~10→16 GW across 2016→2025, with coal
  retiring to zero (last coal plant closed 2024) and CCGT gas moving from mid-merit baseload toward the
  marginal/price-setting plant it now usually is.
- **The forward capacity pipeline** — CfD auction rounds (AR1…AR6) and the Capacity Market T-4/T-1
  results give *committed* future commissioning with real delivery dates. This is the seam where
  BASELINE history ends and CURRICULUM begins (§6).

**Anti-marking-own-homework (binding, inherited from the atom's registration note):** the GENERATOR
anchors to the real capacity/commissioning record; the VALIDATOR must anchor to a **different**
independent published source — e.g. reproduce the *generation-mix share* (wind % of annual generation)
against DESNZ Energy Trends Table 6, a series **not used** to fit the capacity trajectory. The company
never validates against SIM ground truth.

## 4. Proposed shape (what BUILD would build — not built here)

A small deterministic capacity-trajectory subsystem read by `sim/price_engine.py` / the L4 merit-order:

- **L1 (skeletal):** replace the two scalar constants `capacity_wind`, `capacity_solar` with a
  **calendar-indexed lookup** `capacity_k(τ)` per technology `k ∈ {wind_onshore, wind_offshore, solar}`,
  populated from the real annual DUKES capacity series, piecewise-constant per year. The merit order is
  otherwise untouched. Immediately makes a 2016 cold-still spell price *differently* from a 2025 one.
- **L2 (regime-consistent):** smooth commissioning within a year to real commissioning dates where known;
  add the **coal→gas→wind merit-order re-stacking** so the *marginal plant* (and hence the gas-floor
  vs system-margin blend `price_engine.py` already models) shifts over `τ`. Coal exits the stack on its
  real retirement schedule.
- **L3 (target):** the forward window (post-2025) driven by a **director-authored capacity-scenario**
  (curriculum, §6) rather than a flat hold; generation-mix share reported as a first-class observable so
  the coupled company twin can *infer* the shifting price physics through the wall.

**Invariants (R15 — must be mutation-testable, FAIL-OPEN / FAIL-SILENT / TAUTOLOGY forbidden):**
- **A1 monotone-where-real:** `capacity_wind_offshore(τ)` is non-decreasing across the historical window
  (offshore never *de*-commissioned in GB 2016–25); a mutation that lets it fall must fire the check.
- **A2 outturn-consistency:** reconstructed `capacity_k(τ) · power_curve(W(t))` summed to annual energy
  must track the **independently-held** AGWS annual outturn within tolerance — the checker uses the real
  outturn series, **not** the capacity series it is validating (TAUTOLOGY guard).
- **A3 mix-share validator:** annual wind-share reproduced vs DESNZ Energy Trends Table 6 (the *different*
  source, A-M-O-H). Missing year / empty series / unavailable source = **FAILED** check, never a pass.
- **A4 no-coal-after-retirement:** coal contributes zero to the stack after its real closure date.

## 5. Scale / portability constraints touched (declare, don't retrofit)

- **C-S2 determinism/replay:** capacity is a *deterministic* function of `τ`; no RNG substream needed for
  the trajectory itself (a genuine simplification worth stating — contrast W1_2/W1_3 which do need named
  substreams). If a *scenario ensemble* is later drawn over forward capacity, **that** draw takes its own
  named substream (`capacity_scenario`), never a shared one (the 01:09Z-incident law).
- **C-S5 time-scale invariance:** the capacity clock `τ` (years/commissioning dates) is explicitly a
  **separate, slower clock** from the weather clock `t` (half-hours). W1_7's logic must not assume they
  tick together — a registered time-scale exception per R10, named here so BUILD declares it at L3+.
- **Portability:** capacity is keyed by *technology*, not hardcoded to GB fuels — a second market's fleet
  (different tech mix, different retirement schedule) fits the same `capacity_k(τ)` table behind the seam.

## 6. The R13 wall — where BASELINE ends and CURRICULUM begins (load-bearing)

- **Historical capacity 2016→2025 is BASELINE:** it may change **only for fidelity-to-reality reasons**,
  decided blind to company P&L. It is the real DUKES record; the company's results never justify moving it.
- **Forward capacity (post-2025) is CURRICULUM:** *which* buildout trajectory the company lives through
  (slow-buildout vs accelerated-net-zero vs a stalled-pipeline stress) is a **named, versioned,
  director-authored scenario** — never silent parameter drift, never tuned because a hedge looks wrong.
  This atom's BUILD delivers the **mechanism** (a capacity trajectory the price engine reads); the
  **content** (the named forward scenario) is the director's instrument, exactly as W1_2's mechanism/
  content split already established. Under the plain "hold 2025 capacity flat forward" default this atom is
  a faithful continuation, not a stress.

## 7. Coupled-triad note (A6)

W1_7 is a **WORLD/SIM** capability. Its company-side twin is the company's **belief about the shifting
generation mix** as it feeds hedging and forward-pricing decisions (the company observes published
generation-mix / capacity-market data through the wall, and *infers* the changing price physics — and is
allowed to be wrong). Per COUPLED_TRIAD, W1_7 does not reach L3 until a company capability has been tested
against the shifting mix and the belief-vs-truth gap measured (gap = company's assumed merit-order/price
sensitivity vs the SIM's realised time-varying one). No new coupling is *registered* here (BUILD-gated);
flagged so BUILD wires `W1_7 ↔ <company mix-belief>` into `background/coupled_triad.py` when opened.

## 8. BUILD-unblock gate (single line)

Epoch-3 BUILD-open **and** `W1_6_physics_price_signal` built (the merit-order price physics W1_7 layers
on). Until then: **held at L0**, DISCOVER/FRAME complete. A discovery-agent pass to pin the real
DUKES/NESO capacity numbers (§3) is the first BUILD step — the order-of-magnitude figures above are
**unverified this fork** (no network) and must not be leaned on for calibration until sourced.

## 9. Ordered BUILD task list (for the eventual BUILD turn — not started)

1. Discovery-agent: pin real annual installed-capacity series per technology, 2016→2025 (DUKES Ch.6 /
   NESO), + coal retirement dates, + DESNZ Energy Trends Table 6 mix-share validator series (different
   source).
2. Add `sim/renewable_capacity_trend.py`: `capacity_k(τ)` piecewise-constant lookup (L1).
3. Wire it into the L4 merit-order input in `sim/price_engine.py` (replace scalar constants) behind the
   existing typed input, no re-calibration of `γ`.
4. Mutation tests for A1–A4 (red-then-green): plant a falling-offshore mutation, a tautological
   self-validation, an empty-year validator, a post-retirement coal contribution — each must fire.
5. L2: commissioning-date smoothing + coal→gas→wind re-stacking of the marginal plant.
6. L3: forward window read from a **director-authored** capacity scenario (R13); register the coupled
   pair; declare the C-S5 time-scale exception.
7. Re-run `price_engine.py`'s SSP calibration gate — a failure is a *finding about the inputs* (R12),
   surfaced, never retuned.

**Proposed file_scope for BUILD:** `[sim/renewable_capacity_trend.py, sim/price_engine.py, tests/sim]`
— disjoint from W1_2 (`sim/scenario/*`) and W1_3/4/5 (`sim/weather_engine.py`); shares only the
technology-key constant with the weather generators.
## 10. BUILD-readiness assessment (2026-07-20, worker tick, doc-only, no level move)

**Trigger:** `depends_on: W1_6_physics_price_signal` reached **level_current: 3** (ratified 2026-07-20,
director console) and W1_7 carries an explicit director **BUILD_OPEN** (`gate_authorizations.jsonl`
ts=1784499318, "BUILD-OPEN: the W1/W2 cascade atoms"). So BOTH the upstream-dependency gate (§8) and
the loop_stage `stage_advance` gate are now **SATISFIED**. This section records — grounded by inspecting
the *landed* W1_6 code, not the pre-W1_6 assumptions in §1–§9 — exactly what is now available, one
correction that inspection forces, and the *remaining* gates, so the eventual code BUILD starts from truth.

**Correction to §4/§9 (the seam is not where the FRAME said): the renewable-capacity scalar lives in
`sim/weather_price_chain.py`, not `sim/price_engine.py`.** Inspection of the delivered W1_6:
- `sim/weather_price_chain.py` derives renewable output as `wind_fleet_mw * power_curve(wind_speed)` and
  `solar_fleet_mw * solar_envelope(doy, cloud)` (lines 198–259). Both `wind_fleet_mw` and `solar_fleet_mw`
  are **single scalars MEAN-MATCHED over the whole 2016–2025 window** — `wind_fleet = rec["wind_gen_mw"].mean()
  / frac.mean()` (line 220), analogously for solar (line 227). The module's own header (lines 53–54) names
  this gap and this atom by hand: *"WIND fleet is a single MEAN-MATCHED scalar over the whole window — the
  real fleet ~ doubled 2016–2025 (that time-trend is W1_7, an explicit follow-on)."* **This scalar pair is
  W1_7's L1 hook.**
- `sim/price_engine.py`'s `DISPATCHABLE_CAPACITY_MW = 35000.0` (§4/§9 pointed here) is a **different** fleet
  — the *dispatchable/thermal* capacity (CCGT/OCGT/coal/nuclear/interconnector) the merit-order scarcity
  ratio `x = RD / DISPATCHABLE_CAPACITY_MW` normalises against. It is W1_7-**adjacent** (the coal→gas→wind
  re-stacking of §4-L2 touches it) but it is NOT the renewable-capacity scalar. **Corrected BUILD file_scope:**
  `[sim/weather_price_chain.py (L1 renewable fleet trajectory), sim/price_engine.py (L2 dispatchable
  re-stacking only), tests/sim]` — the standalone `sim/renewable_capacity_trend.py` of §9 remains a
  reasonable home for the `capacity_k(τ)` lookup that `weather_price_chain.py` would then read.

**Finding — L1 mechanism is buildable WITHOUT network; only its independent validation is network-blocked.**
`weather_price_chain.py::load_daily_record` already ingests the **real per-`psrType` AGWS outturn** for the
whole window (`aggregate_wind_generation` / `aggregate_renewable_generation`, lines 119–163). An L1 that
replaces the whole-window mean-match with a **per-year mean-match** (`wind_fleet_mw(year)` = that year's
AGWS-outturn mean / that year's power-curve-fraction mean) makes the same weather draw price differently in
2016 vs 2025 *using data already on disk* — no DUKES installed-capacity series required for the mechanism.
**But** this makes A2 (§4, outturn-consistency) **tautological** — validating a per-year-mean-matched fleet
against the same-year AGWS outturn it was matched to proves nothing (the exact TAUTOLOGY the FRAME forbids).
So L1's *mechanism* is network-free; L1's *honest validation* is not — it needs the **A3 mix-share validator**
(annual wind-share vs DESNZ Energy Trends Table 6, a source NOT used in the mean-match) and, for L2, the
**DUKES Ch.6 installed-capacity series** to separate true installed capacity from load-factor. Those two are
the network-blocked discovery-agent pass (no network this worker tick).

**Remaining BUILD gates (recorded, not actioned — none agent-crossable):**
1. **file_scope gate.** W1_7's committed `file_scope` is `[docs/design]`. The code BUILD lands in
   `sim/weather_price_chain.py` (+ optional `sim/renewable_capacity_trend.py`, `tests/sim`) — a scope
   expansion only the sole-map-writer (orchestrator/director) opens. `docs/design/maturity_map.yaml` is a
   `schema_sim_structure` **gated path**, so `file_scope`/`level_current`/`loop_stage` are NOT self-edited here.
2. **discovery-agent network pass.** A3 mix-share validator source (DESNZ Energy Trends Table 6) + L2 DUKES
   Ch.6 installed-capacity series — required before any non-tautological L1 validation or any L2 claim. Not
   attempted this tick (no network in autonomous runs). The §3 order-of-magnitude capacity figures remain
   unverified and must not be leaned on for calibration until sourced.
3. **coupled-triad L3 gate (§7, unchanged).** W1_7 does not reach L3 until a company **mix-belief** capability
   exists, is tested against the shifting mix, and the belief-vs-truth gap is measured (`coupled_triad.py`).
   No such company capability exists yet — L3 is gated on building the coupled company twin, independent of
   the above. The BUILD wires `W1_7 ↔ <company mix-belief>` when that twin lands.

**Net:** upstream (W1_6→L3) and stage (BUILD_OPEN) gates cleared; a cheaper-than-expected L1 path identified
(per-year mean-match on already-ingested AGWS data) with the correct code seam pinned (`weather_price_chain.py`,
not `price_engine.py`). W1_7 code BUILD is now blocked ONLY on (a) a director/orchestrator `file_scope`
expansion and (b) the discovery-agent network pass for the independent validators. Level **HELD at 0** —
DISCOVER/FRAME does not move levels; `maturity_map.yaml` untouched (gated path). L1-PROPOSED pending file_scope
+ validator sourcing.

## 11. L1 BUILD LANDED (2026-07-20, worker tick — level HELD at 0, L1 PROPOSED)

**Built** (the §10 network-free L1 path, seam corrected to `weather_price_chain.py`):
- **`sim/renewable_capacity_trend.py`** — `fleet_trajectory()` mean-matches the renewable
  fleet WITHIN each calendar year on the AGWS outturn already ingested by
  `weather_price_chain.load_daily_record()`, giving a time-varying `capacity_wind(τ)` /
  `capacity_solar(τ)` (piecewise-constant, flat tails = R13 hold-2025-flat default). `τ` is the
  slow calendar clock, explicitly separate from the half-hourly weather clock `t` (C-S5).
- **`sim/weather_price_chain.py`** — `wind_output_from_speed` / `solar_output_from_weather` /
  `derive_price` / `residual_demand` gain an **optional `year=`** param. `year=None` keeps the
  whole-window scalar **byte-identical** (45 existing chain/price tests green → the SSP
  calibration gate is NOT re-opened, R12). With a year, `derive_price(year=2016)` ≠
  `derive_price(year=2025)` for the same windy draw — the atom's compounding claim delivered.
- **`tests/sim/test_renewable_capacity_trend.py`** — 10 tests, R15 mutation-proven for the
  invariants that are honestly checkable without network.

**Honesty boundary held (R15 / §10):** the per-year mean-match is an **effective** fleet
(capacity growth × residual load-factor), NOT pure installed capacity. **A2** (outturn-consistency)
and **A3** (mix-share) are deliberately **not claimed** — validating a per-year match against the
same-year outturn is tautological; the independent sources (DUKES Ch.6 capacity, DESNZ Energy Trends
Table 6) are network-blocked. Invariants asserted: TREND, NON-DEGENERACY, DETERMINISM (C-S2),
COVERAGE-FAIL-CLOSED.

**Gates observed (none crossed):** `maturity_map.yaml` untouched (gated path) — level HELD at 0,
L1 PROPOSED recorded via `docs/design/atom_status/W1_7_renewable_capacity_trends.yaml`. **file_scope
expansion requested** of the sole-map-writer (committed scope `[docs/design]`; code landed in `sim/`
+ `tests/sim`). Reconciler stayed QUIET (no map delta this fork).

**Remaining to L2/L3:** (a) discovery-agent network pass (DUKES + DESNZ) to separate capacity from
load-factor and enable non-tautological A1-strict/A2/A3; (b) flip `derive_price` default to
year-aware after re-running the SSP calibration gate (task 7); (c) coupled-triad L3 gate — register
`W1_7 ↔ <company mix-belief>` once that company capability exists (§7, unchanged).
