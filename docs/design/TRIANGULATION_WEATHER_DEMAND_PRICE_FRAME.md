# Triangulation extended — weather, demand, and wholesale price FORMATION (DISCOVER→FRAME)

**Source:** `docs/staging/in_progress/DIRECTOR_STEER_TRIANGULATION_WEATHER_DEMAND_PRICE_2026-07-22.md`
(advisor carrying the director's direction). **Type:** [STEER] — extends the Spec-001 triangulation
pattern (blind board expectation × advisor documentary anchors × primary DISCOVER) to three further
domains. Mechanism mine; the constructs in the steer are the **wall**. Tagged
**narrow/reversible; generator/engine changes remain propose-then-proceed.**

**Status:** DISCOVER→FRAME, **doc-only**. Provenance: **proposal**. Writes **no** `sim/`/`company/`/
`harness/` code, edits **neither** `maturity_map.yaml` **nor** any engine, claims **no** level, does
**not** edit `DIRECTOR_CANON.md` (director-reserved, Law B — the design principle below is recorded
**proposed-for-canon**, the director ratifies). Touches only `docs/design/`. Candidate atoms are
*named, not registered* (orchestrator is sole map writer per THREE_LANES until `H9`).
**No network this session** (autonomous run) — every external market/literature fact is flagged
**`[recall — verify at BUILD]`**; in-repo levels/files are quoted from the live
`docs/design/maturity_map.yaml` and named files read this session; **no figure fabricated**
(Historical Ground Truth).

**Reconciliation tension noted up front (agent-confirmed 2026-07-22):** the three DISCOVER docs
(`C13_…`, `W1_6_…`, `EPOCH2_BC_…`) still self-describe as `level_current: 0` / "no level claimed" in
their own prose — they were written 2026-07-16, BUILD-gated. The **live map has since moved W1_3,
W1_4, W1_5, W1_6 and C13 to level 3.** *The docs are the frame; the map is the current truth.* This
FRAME cites the map for levels.

---

## 1. The design principle the steer establishes — recorded, PROPOSED-FOR-CANON

> **PRINCIPLE (proposed canon, v1, 2026-07-22): Model the fundamentals; generate the residual as a
> calibrated stochastic process with honest tails and regime behaviour; never pretend to forecast the
> unforecastable.**

Concretely, four sub-clauses, each with its in-repo reconciliation:

1. **Fundamentals are *caused*, not drawn** — weather→demand coupling, merit-order stack,
   storage/flow seasonality, capacity evolution. *Repo already embodies this:* invariant **BC-1**
   (`EPOCH2_BC_…` line 300) — "price is an emergent OUTPUT, never a set input"; `W1_6` L3
   (`sim/weather_price_chain.py`) derives price via `national weather → demand + renewable output →
   residual demand → merit order → wholesale price (price is NEVER an independent draw)`. **Met.**
2. **The residual is *drawn* from calibrated distributions with the right tail mass and regime
   structure** — outage timing, geopolitics, sentiment spikes. *Repo's named open gap:* the
   **spike-tail defect** is exactly this residual being under-drawn — the company twin
   `weather_price_belief.py` "under-predicts the convex cold-still spike by a signed −17.4 GBP/MWh on
   the tail." **Partial — the fundamental spike is caused (157 vs 72 GBP/MWh from one weather draw);
   the *residual* tail is the acknowledged under-draw.** This is the sharpest cross-domain finding.
3. **Mean reversion holds within a regime and breaks across regimes** (2021–22 is the proof case; a
   single-regime mean-reverting model is disqualified by our own decade record). *Repo status:*
   `sim/forward_curve.py` is `spot_ewma(half-life 30d) × seasonal_shape × (1+term_premium)` — a
   **single-regime EWMA**. This is **not a defect** *because it is a COMPANY-SIDE belief model* (a
   fixed-rate-tariff forward pricer) — see clause 4; it would be a defect only if it were the SIM's
   generator. Flag for the board reconciliation: confirm the *generative* price path carries regime
   structure, not just the belief pricer. **Partial — belief-side single-regime is correct-by-design;
   generator-side regime structure to be proven against Spec 004.**
4. **The wall split for beliefs** — recency, sentiment, adaptive expectations are properties of the
   COMPANY's belief formation, not of the true process; model them company-side and *score* them.
   *Repo already embodies this:* the 120-day trailing estimator and the EWMA(30d) forward pricer are
   recency-biased BELIEFS the desk must outgrow; the COUPLED_TRIAD scores the belief-vs-truth gap
   (`coupled_gap_ledger.json`). **Met — this is the design's spine, not a new ask.**

**Why propose-for-canon and not just record:** the steer says "record it as canon when framed." Canon
(`DIRECTOR_CANON.md`) is director-authored only (bumped on overturn, never silently edited — Law B).
So this principle is staged here for the director/twin to ratify into canon; until then it is a FRAME
principle, not canon.

---

## 2. Spec 002 — WEATHER (existing cascade tested against the blind board spec)

**Current in-repo state (map-confirmed levels):**

| atom | level | file | one-line (quoted) |
|---|---|---|---|
| `W1_3_national_weather_signal` | **L3** | `sim/weather_engine.py` | "coherent AUTOCORRELATED joint national temp/wind/solar signal"; sim winter D1 decile lift **2.875**, within real CI [1.54, 3.38] |
| `W1_4_regional_weather_field` | **L3** | `sim/weather_engine.py` | "spatially-correlated regional deviations … AGGREGATION-CONSISTENT with the national signal (invariant, mutation-tested)" |
| `C13_weather_normalisation` | **L3** (map) | `company/pricing/weather_normalisation_belief.py` | company INFERS book weather-sensitivity from confounded meter data; **wall-clean**, reconstructs HDD/CDD company-side, must NOT reuse `weather_hdd.py` |
| `W1_7_renewable_capacity_trends` | **L0** | — | not built |
| `W1_8_zonal_locational_pricing` | **L0** | — | not built |
| `W1_9_dsr_flex_markets` | **L0** | — | not built |

**Reconciliation finding (C13 level tension):** map records C13 `level_current: 3`, but the atom's own
map note (line ~1419) reads "BUILD L2 PROPOSED" and the agent reports "built to L2 then HARDENed; L3 is
director-reserved." **This is a finding, not a fact I resolve:** either the map's `level_current: 3` is
a self-promotion the level gate should revert (per the *levels-are-proposals* precedent), or an L3
ratification exists in the ledger. **Verify `gate_authorizations.jsonl` before trusting the 3**
(R16 — the ledger is authority, not the map field or a commit message). Flagged for the orchestrator.

**Prior-art anchors (advisor candidates — `[recall — verify at BUILD]`):** stochastic weather
generators (WGEN lineage and successors); ERA5/reanalysis as the truth source; HDD/CDD demand
literature. In-repo the Open-Meteo record already anchors the national signal; `sim/weather_hdd.py`
uses 1991–2020 Met Office monthly HDD normals.

**"NOT credible" battery seed (Spec 002) — a weather model is NOT credible if:** (a) national temp/wind/
solar are drawn independently (no joint autocorrelation / no blocking-high regime); (b) regional field
does not reconcile to the national aggregate; (c) no cold∧still joint tail (the entry-shock decile
lift 2.34× is the anchor); (d) it cannot reproduce a multi-day persistence event. These join the
standing practitioner fidelity oracle established by Spec 001, per the steer.

---

## 3. Spec 003 — DEMAND variability and drivers (W1_5 machinery tested)

**Current in-repo state:** `W1_5_premise_demand_shape` **L3** (`simulation/premise_demand.py` +
`sim/weather_demand_chain.py`): "each property's half-hourly demand = f(LOCAL weather, thermal
performance, heating type, occupancy, archetype) + idiosyncratic noise; aggregate reconciles to
national (invariant, mutation-tested)"; degree-day OLS on real INDO/Open-Meteo, **R²=0.55**.
`simulation/demand_model.py` composes `(base_shape + heating_load + cooling_load) × occupancy_multiplier
+ ev_charging_load − solar_generation` (HDD base 15.5°C, CDD base 22°C, 48-period settlement shapes).
Data anchor: `docs/market_research/ons_consumption_profiles.md` — Ofgem TDCV bands from 2026-07-01:
Low 6,000 / Medium 9,500 / High 14,000 kWh/yr.

**Structural / behavioural / stochastic split (the steer's premise-level ask), reconciled:**
- **Structural (physics + occupancy):** present as degree-day + occupancy-multiplier + heating-type
  parameters. **GAP (the key Spec-003 finding):** there is **no BREDEM/SAP/RdSAP or RC lumped-parameter
  thermal model** in-repo — thermal is a *parameter*, not a *physics network*. The steer's own anchor
  ("EPC data is *generated by* SAP/BREDEM, so using them closes a provenance loop") is **absent**, and
  couples directly to the segmentation work's EPC/census priors (see `[[project_segmentation_one_taxonomy]]`).
  Candidate atom below.
- **Behavioural:** occupancy multipliers exist; adaptive/elasticity response is thin — **partial**.
- **Stochastic:** idiosyncratic noise term present — **met at premise level**; between-home variance
  vs within-home-over-time variance not separately identified — **partial** (SERL's 63–80%
  variance-from-physics+occupancy `[recall — verify at BUILD]` is the calibration target).

**Prior-art anchors `[recall — verify at BUILD]`:** SAP/BREDEM/RdSAP (UK standard assessment physics);
lumped-parameter RC thermal models; SERL smart-meter validation studies; HDD/CDD demand literature.

**"NOT credible" battery seed (Spec 003):** (a) demand insensitive to a cold snap at the half-hour;
(b) no between-home heterogeneity beyond a scalar; (c) heating-type mix not reflected in shape; (d)
aggregate premise demand does not reconcile to national (already an enforced invariant — keep).

---

## 4. Spec 004 — WHOLESALE PRICE FORMATION (distinct from Spec 001's desk)

**Current in-repo state:** `W1_6_physics_price_signal` **L3** (`sim/weather_price_chain.py`): "price as
a DERIVED output: … residual demand → merit order → wholesale price (price is NEVER an independent
draw)"; cold-and-still corner → mechanistic spike **157 vs 72 GBP/MWh (2.2×) from ONE weather draw."
Merit-order engine: `sim/price_engine.py` (`gas_floor_price` / `system_margin_price` /
`wind_power_output_fraction`). Forward pricer: `sim/forward_curve.py` (company belief; §1 clause 3).

**The merit order — coherence with Spec 001's gas-first, confirmed:** the ~10× SSP miscalibration of
the raw-ratio form is **structurally fixed** (`docs/calibration/price-engine.md`, 2026-07-19): raw
`(demand/renewables)^γ` replaced by a residual-demand scarcity form `x = RD / DISPATCHABLE_CAPACITY
(~35,000 MW)`, `multiplier = A0 + A1·x + A2·max(0, x−0.70)^2`, fitted n=157,106 (2016-03…2025-06);
carbon term added (`EF_GAS = 0.184 tCO₂/MWh_th`) — "BASELINE FIDELITY correction, decided **blind to
company P&L**" (R13-clean). Marginal-gas-sets-power is thus already caused, matching Spec 001's
gas-first blind finding.

**BC invariants inherited unchanged (`EPOCH2_BC_…`):** **BC-1** price is emergent output (killer
mutation: exogenous price draw must fire); **BC-2** supplier cost LAGS spot via the hedge book (a spot
move does not re-price fixed positions — "the exact way a naive cost model overstates price
sensitivity"); **BC-3** weather→cost coupling is VOLUME-path-dominated for a hedged book, weakening
monotonically as hedge_fraction → naked.

**Stocks and flows (the steer's distinct Spec-004 ask), reconciled:** gas storage cycles, LNG,
interconnectors, wind displacement. *Wind displacement* is present (merit order via residual demand).
**Gas storage injection/withdrawal economics, LNG arbitrage, interconnector flows are ABSENT** — the
price engine is a point-in-time merit order with no inter-temporal storage state. This is the largest
Spec-004 structural gap and the natural home of "what is modellable vs long/short-term randomness":
storage seasonality is *modellable* (fundamental); outage/geopolitics/sentiment is *residual* (drawn).
Candidate atom below.

**Model-family evaluation (the steer's explicit ask — which family for the GENERATOR vs the COMPANY's
BELIEF):**
- **SIM generator → structural/fundamental merit-order (already the choice), plus a regime-switching
  residual for the irreducible tail.** Lucia–Schwartz jump-diffusion and Markov regime-switching are
  `[recall — verify at BUILD]` candidates for the *residual* process layered on top of the fundamental
  stack — NOT as a replacement for merit order. This directly serves clause 2 (under-drawn tail) and
  clause 3 (across-regime break). **This touches the price engine → propose-then-proceed, not built
  here.**
- **Company belief models → allowed to discover the simpler families** (single-regime mean reversion,
  EWMA, adaptive expectations) and be *scored* against the richer truth — the wall-split (clause 4).
  `forward_curve.py`'s single-regime EWMA is correct AS a belief; the gap it leaves on 2021–22 is a
  *measured finding*, not a bug to patch.

**"NOT credible" battery seed (Spec 004):** (a) price is an independent draw (BC-1); (b) supplier cost
tracks spot 1:1 with no hedge lag (BC-2); (c) no storage/inter-temporal state → no realistic winter
shape; (d) single-regime generator that mean-reverts through 2021–22; (e) tail mass too thin to
reproduce the observed spike distribution.

---

## 5. Candidate atoms (NAMED, not registered — orchestrator is sole map writer)

Each is DISCOVER/FRAME-workable NOW (doc-only); any BUILD touching the generator/price engine returns
as a proposal (propose-then-proceed, per the steer's risk tag).

- **`SPEC002_weather_reconcile`** — line-by-line met/partial/absent/NA of the W1_3/W1_4/C13 cascade vs
  board Spec 002 when it lands; resolve the C13 L2-vs-L3 ledger tension (§2). *DISCOVER now, doc-only.*
- **`SPEC003_housing_physics_gap`** — the BREDEM/SAP/RC-thermal absence (§3); closes the EPC→SAP
  provenance loop, couples to segmentation priors. *FRAME now; BUILD = new sim physics → proposal.*
- **`SPEC004_storage_flows`** — inter-temporal gas storage / LNG / interconnector state on the price
  engine (§4); the modellable-fundamental half of stocks-and-flows. *BUILD touches engine → proposal.*
- **`SPEC004_residual_regime_process`** — the calibrated regime-switching residual layered on the
  fundamental stack to fix the under-drawn tail (§1 clause 2, §4); the honest-tails machinery. *BUILD
  touches engine → proposal; the belief-side scoring is COUPLED_TRIAD, already live.*

---

## 6. Process (per the steer)

1. **DISCOVER now, don't wait for the board** — this doc is the primary-source + in-repo pass; the
   external-literature pass (WGEN/ERA5, SAP/BREDEM, Lucia–Schwartz/regime-switching, storage/LNG) is
   flagged `[recall — verify at BUILD]` because this is an autonomous no-network run — a networked
   session (or the discovery-agent with real sources) verifies each candidate against primary sources.
2. **When board Specs 002/003/004 land** — reconcile all three anchors line-by-line (board / this doc /
   primary DISCOVER); every disagreement is a finding; each domain's "NOT credible" battery (§2/§3/§4
   seeds) joins the standing practitioner fidelity oracle.
3. **Findings → proposals** via the VALUE_CHAIN steer's propose-then-proceed — **no silent scope
   changes.** DISCOVER/FRAME/reconciliation are reversible and proceed; generator/engine model-family
   changes come back as named proposals.

**The steer stays in `docs/staging/in_progress/` — genuinely open sub-item:** board Specs 002/003/004
have NOT landed (commissioned blind, in parallel); line-by-line reconciliation and the model-family
BUILD proposals are pending their arrival.
