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
