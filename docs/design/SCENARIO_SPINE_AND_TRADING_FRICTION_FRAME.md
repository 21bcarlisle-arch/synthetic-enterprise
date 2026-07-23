# Scenario spine, trading friction, and the pricing of forecast error (FRAME)

**Source:** `docs/staging/DIRECTOR_STEER_SCENARIO_SPINE_AND_TRADING_FRICTION_2026-07-23.md` — a [STEER] via the
advisor bridge carrying a live director conversation (2026-07-23). Decisions in §"Director decisions" of the
steer are DECIDED (director's 20-year domain judgment); mechanism design is mine.

**Type:** [STEER] — DISCOVER→FRAME first for the scenario spine (A); a friction AMENDMENT to the already-authorized
WVC BUILD (B); follow-ons registered not built (C). **The construct in the steer is the wall.**

**Status:** DISCOVER→FRAME, **doc-only**. Provenance: **proposal**. Writes **no** `sim/`/`company/`/`saas/`/
`harness/` code, edits **neither** `maturity_map.yaml` **nor** any engine, claims **no** level, touches only
`docs/design/` (+ a companion sourced-evidence file under `docs/market_research/`). Candidate atoms below are
**named**, not registered (orchestrator is sole map writer per THREE_LANES until `H9`). Network **is** available
this session (probed: ofgem.gov.uk → 200), so external market anchors are **sourced with citation** in the
companion research file `docs/market_research/scenario_spine_and_friction_anchors_2026-07-23.md`; any figure that
research could not source from a primary/near-primary publisher is flagged **UNSOURCED — verify at BUILD**. No
figure is fabricated (Historical Ground Truth).

**Relationship to prior work (extends + amends, does NOT fork):**
- `docs/design/WHOLESALE_VALUE_CHAIN_FRAME.md` — the ratified WVC FRAME (veto lapsed; `WVC_1→WVC_5` BUILD on
  standing authority). This document **amends** it: decision 5 makes the friction term first-class in the
  value-add ledger from v1, and the scenario spine becomes the exogenous world WVC's benchmark and formation are
  computed *against*. It does not re-open WVC's product ladder / cover fan / benchmark constructs.
- `docs/design/BOARD_SPEC_004_RECONCILIATION.md` — price-formation reconciliation, 16 MET / 15 PARTIAL / 11
  ABSENT, findings F1–F5. This FRAME's follow-on (3) closes **F2** (regime layer on wrong axis) and **F4** (gas
  ingested, not formed — the load-bearing gap); the scenario spine's gas *trend* is exogenous (decision 1) while
  the seasonal/storage *structure* is formed (follow-on 3).
- `sim/scenario/` — existing generators (`gas_scenario_generator.py`, `bimodal_generator.py`,
  `fidelity_check.py`). The spine is an **extension of this package**, not a new lane (see §A.1 — OPEN resolved).
- `sim/weather_price_chain.py` / `company/pricing/weather_price_belief.py` — the coupled weather→price→imbalance
  triad the spine feeds; the spine changes the *world* the chain runs in, not the chain.
- `background/coupled_triad.py` + `coupled_gap_ledger.json` — where the scenario-vs-belief and friction gaps
  surface (§B.4, §D).

---

## 1. The governing rationale (record this — it is the frame for ALL wholesale work)

**The wholesale machinery exists to PRICE FORECAST ERROR.** Getting customer numbers, demand shape, or weather
response wrong is not a scoring abstraction — it becomes one of three real costs:

1. a **residual position** settled at SSP (where the spike tail lives — model max £574 vs real £4,038, negatives
   0.013% vs 2.241%, per G4's ledger),
2. **rebalancing** paid through the **bid-offer spread** (friction), or
3. **early cover** paid for via **risk premium** (carry).

Forecast-accuracy value = the **avoided cost of the involuntary position**. This gives every belief-vs-truth gap
an **economic denominator**: `gap × marginal cost of being wrong`. That denominator IS the ratified
learning-value segmentation metric — now derived from market physics, not asserted.

**Supplier roles are answers to physics, not scripted org design:**
- **Hedger** ← price–volume covariance.
- **Trader** ← curve movement + friction.
- **Tariff designer** ← customers consume a *shape* but pay a *structure*, under a cap.
- **Risk / compliance** ← the absolute survival constraint + collateral in cash.

If a piece of physics is missing from the world, the corresponding organ never develops or degenerates. The named
failure: **costless rebalancing breeds a hyperactive fake trader** — an R12 fidelity bug (the world let it churn
for free), not alpha. The world forces the org design; we never script it. This is the **Epoch-4 tournament
thesis, grounded**.

**Where this rationale must be reflected (DoD 5):** every place the wholesale/trading lane states its purpose —
the WVC frame's §1, the trading atoms' `real_world_twin`/purpose lines, and the desk-pack surface captions — reads
back to "prices forecast error." Registered as a map-hygiene follow-on (§C, breadcrumb) so the sentence lands in
the atoms, not only here.

---

## 2. Director decisions (transmitted as decisions — DECIDED, not proposals)

1. **Gas is split, not formed whole.** The gas **TREND** (level path) is an exogenous, director-authored
   scenario input (R13 curriculum). The **SEASONAL/STORAGE STRUCTURE** around that trend is **FORMED** — a
   European storage stock-and-flow state producing winter/summer spreads, contango/backwardation, and capable of
   the 2022-style inversion under a fill-mandate stress. Answers Spec-004 F4 without modelling global LNG.
2. **Oil is demoted** to a scenario-spine economy/energy-complex proxy. GB/EU gas is hub-priced (NBP/TTF, LNG
   arbitrage at the margin); oil indexation is not the driver. **Do not build an oil→gas price mechanism.**
3. **Hybrid formation confirmed:** fundamental stack (spark spread, residual-demand scarcity) + a stochastic
   regime/jump layer **on the residual** — the FRAME §5 `SPEC004_residual_regime_process` direction stands.
   Neither pure fundamentals nor pure stochastic mean-reversion alone (a single-regime process fit to 2016–20
   calls 2022 impossible — measured, not asserted).
4. **Scenario rotation is the resilience mechanism.** "Resilience and the capability to endure, not pot luck in
   one world." Runs rotate through director-ratified worlds; the **historical 2016–25 replay remains the
   default/baseline world** (R13 baseline/curriculum split holds).
5. **Trading friction is first-class from day one.** Bid-offer spread is a **surface** — f(product, horizon,
   regime): front tight, far seasons wide (widening toward unbounded IS the liquidity limit), peak wider than
   baseload, blow-outs under stress. Churn cost = volume × half-spread, per strategy. **The WVC value-add ledger
   scores achieved-vs-benchmark NET of friction from its first version** — a static, externally-anchored
   spread-by-horizon table is acceptable initially; the regime-widening surface is a follow-on. Scoring gross
   would overstate every early result and move the bar later.
6. **Named physics the chain must surface as first-class outputs:** price–volume covariance (cold snap = more
   volume exactly when spot spikes — the mechanism that killed 2021's suppliers); the shape/cash-out residual
   (hedged blocks vs consumed half-hourly shape, settled at SSP — where the spike tail becomes commercially real).

---

## A. Scenario spine — SIM-side, propose-then-proceed

### A.1 OPEN resolved: extension of `sim/scenario/`, not a new lane

The spine is a **new module inside the existing `sim/scenario/` package** (`sim/scenario/spine.py` + a
curriculum registry), not a new atom-lane and not a fork of the generators. Rationale: `sim/scenario/` already
owns exogenous world inputs (`gas_scenario_generator.py`); the spine is the *container* those generators read
their exogenous paths from, plus the wall and the version pin. SIMPLICITY GUARD (scale addendum): a dataclass +
a committed JSON/YAML curriculum artefact, no repository-over-JSON cathedral, no adapter-for-future-adapters.

### A.2 Internal representation

A **`ScenarioSpine`** value object — immutable, version-pinned, keyed by `world_id` + `version` — holding
**time-indexed exogenous paths** for the run's world:

| Field | Type | Source of truth | Consumed by |
|---|---|---|---|
| `gas_trend` | £/therm (or p/therm) path vs time | director curriculum (R13) | price formation (spark spread), gas product ladder |
| `economy_factor` | dimensionless index vs time | director curriculum (demoted oil/complex proxy, decision 2) | demand generation (industrial/commercial load), never a gas driver |
| `renewables_buildout` | installed GW (wind+solar) path | director curriculum, anchored to NESO FEP | residual-demand scarcity → price formation |
| `storage_capacity` | TWh capacity + fill-mandate flags path | director curriculum | the FORMED seasonal/storage structure (follow-on 3) |
| `world_id`, `version`, `provenance` | metadata | curriculum artefact + `gate_authorizations`/ratification record | audit; run-history stamp |

The spine is **loaded once per run from a committed curriculum artefact**
(`sim/scenario/curriculum/<world_id>.yaml`), never synthesised at runtime, never mutated mid-run
(C-S2 deterministic replay — the same world + seed reproduces identical state; each generator draws from its own
named RNG substream so adding the spine shifts no existing draw). Persistence is behind the event-log/interface
abstraction (C-S4). The **default is `world_id: history_replay`**, which supplies the real 2016–25 record and
selects **no** exogenous overrides — see A.5 byte-identical guarantee.

### A.3 The wall (decision 4 / the steer's central construct)

The company **discovers the world through prices and its own book — it NEVER reads scenario state.** No
company-layer or saas-layer code may import `sim.scenario.spine`, and no `ScenarioSpine` field crosses
`company/interfaces/sim_interface.py`. The company sees: market-data feeds (prices), meter reads, its own bills,
cash-out settlement, published regulatory text. It infers gas trend / renewables buildout / storage state the way
a real supplier does — from observed prices and their moves — and is *allowed to be wrong* (the gap is the score).

This is the same import-direction epistemic law F1b proved for company comms: peeking is a `simulation.*` /
`sim.scenario.*` import, structurally detectable. See **§R15 obligation W1**.

### A.4 Consumption path (typed seam, C-S3 async-safe)

Price formation and demand generation read the spine through a **read-only accessor** on the SIM side
(`scenario_spine.paths_as_of(t)`), not a direct attribute reach — so the storage/formation follow-on (3) can
swap a static path for a formed stock-and-flow behind an unchanged signature (portability: no hardcoded
settlement granularity or clock speed). The accessor is Blindfold-clean by construction: `paths_as_of(t)` never
returns a value dated after `t` (the exogenous path is a *scenario input*, not a forecast the company reads).

### A.5 Byte-identical baseline guarantee (R15 obligation, DoD 4)

With `world_id: history_replay` (the default — i.e. **no scenario selected**), every existing run is
**byte-identical** to today. Proven by a golden-hash test over the run-output ledger, same discipline as the D3
actual-read test: hash the settled ledger of a fixed-seed baseline run before and after the spine lands; equal or
the change is a defect. This bounds the integration blast radius: the spine is *additive*, dormant unless a
non-baseline world is selected. See **§R15 obligation W2**.

### A.6 Launch-world set proposed (director ratifies the VALUES — R13)

The **mechanism** is mine to build now; the **parameter values** and **which worlds enter rotation** are the
director's, proposed here for ratification. Sourced anchors live in
`docs/market_research/scenario_spine_and_friction_anchors_2026-07-23.md` (companion research; every number cited
to publisher + date). Three worlds proposed as the launch set:

**(i) `neso_central` — a NESO FES 2025-anchored central path.** Anchored to NESO's de facto reference pathway
**Holistic Transition** (FES 2025, "Pathways to Net Zero", Nov 2025). Renewables (wind+solar): **49 GW (2024) →
113–124 GW (2030, +2.3–2.5×) → 227–256 GW (2050)**; electricity demand **57.5 GW / 287 TWh (2024) → 62–65 GW /
335–345 TWh (2030)** — capacity growth outpaces demand to 2030, the mechanistic driver of rising negative-price
frequency. Gas central trend from **DESNZ Fossil Fuel Price Assumptions 2025, Assumption B** (FES publishes no
p/therm table): **84 p/therm (2024) → 71 (2030) → 66 (2050 plateau)**. Purpose: the "expected future" the desk
plans against — where good forecasting looks boring and cheap.

**(ii) `crisis_2021_22` — a 2021→22 crisis-replay world.** Gas trend spiking (DESNZ Assumption B **226 p/therm
2022 annual avg**), EU storage-fill panic driving the winter/summer spread INVERSION (advisor decade review:
−£29.7 spread, 2022), price–volume covariance biting, SSP spike tail live. **SSP peak confirmed against Elexon
Insights API to ~1% of the sim's claim: real max £4,000.00/MWh exactly, 8 Jan 2021 SP39.** Ofgem's 26 Aug 2022
cap letter: wholesale-cost component **£1,077 → £2,491/yr in one quarter**, total cap £1,971 → £3,549 (**+80%**) —
the collateral/cash-not-P&L shock. Purpose: the world that killed real suppliers on cash — tests survival,
collateral, and whether the desk pre-empted the residual tail.

**(iii) `supply_glut` — an oversupply world.** Low gas trend, high renewables surplus, demand slack, negative-price
frequency up. Best-documented GB analogue self-computed from Elexon primary data (spring-2020 COVID collapse):
**SSP −£60 to −£66/MWh, 37.5–43.75% of half-hours negative (13 Apr / 24 May 2020), demand −23.7%** (INDO/ITSDO,
exceeding the commonly-cited ~20%). Purpose: the mirror of (ii) — where carry (paying early risk premium) is
punished and a hyperactive hedger destroys value; tests the org does NOT over-insure in calm.

**Sources:** all figures live-fetched/API-queried 2026-07-23, cited in
`docs/market_research/scenario_spine_and_friction_anchors_2026-07-23.md`. Flagged gaps for BUILD (fabricate
nothing): the exact 2.24% negative-half-hours over the full 2021–22 window (needs a bulk API scan), the intraday
NBP p/therm peak (Ofgem WMI portal blocked to automated fetch), the EU storage-fill Reg 2022/1032 numeric
targets (mechanism confirmed, primary text not fetched), and GB-vs-EU gas storage capacity.

**The 2016–25 history replay remains the default/baseline world** and is not in the rotation set — it is the R13
baseline the curriculum worlds are proposed *alongside*, never *instead of*.

### A.7 Scenario sampling — tail-heavy, with an importance-sampling split (director AMENDMENT 2026-07-23)

**Scenario selection across runs is NOT proportional Monte Carlo** (that burns the run budget rediscovering the
middle of the distribution — the scenario version of sampling customers proportionally, the exact defect the
segmentation value-frontier ruling corrected). Sampling is deliberately **TAIL-HEAVY**: overweight less-likely
variants, because learning value and survival information concentrate there. The rigor that keeps this honest is
an **importance-sampling split**:

1. **Two weightings, never conflated.** The **SAMPLING distribution** (which worlds actually run — tail-heavy) is
   distinct from the **PROBABILITY measure** (real-world likelihood — NESO pathway weightings, historical base
   rates). Any expected-value figure computed across runs **reweights each run by its true-world probability**, so
   EV stays unbiased while stress coverage stays dense. Conflating them drifts every valuation pessimistic — an
   R12-class distortion in the *opposite* direction to goal-seeking.
2. **Two verdicts, differently weighted.** EV is probability-weighted. **Survival is worst-case over the sampled
   set, UNWEIGHTED** — a world's unlikeliness discounts its EV contribution but never excuses dying in it.
   Survival stays a hard constraint outside the scalar (standing law); the scenario-level expression of G1's
   CVaR/worst-cell logic, mirroring Ofgem's supplier financial-resilience stress-test posture
   (regulation-as-fidelity-oracle: the rule exists because suppliers died in the tail).
3. **Weather draws inside each world follow the same principle.** W1_3's finding stands: the joint cold-and-still
   tail carries **~2.34× the mass independence predicts**. Within-world weather sampling overweights joint tails
   under the **same run-weight bookkeeping** — no double-counting between world-level and weather-level weights.
   **Composition (stated per the amendment):** the persisted per-run true-probability tag is the *product* of the
   world-selection true-probability and the within-world weather-draw true-probability (`p_run = p_world ×
   p_weather|world`); the sampling over-weight is likewise multiplicative, and the reweighting divides by the
   sampling weight at exactly one layer (the run), so neither layer's weight is applied twice.
4. **Weights are curriculum (R13), behind the wall.** Sampling weights AND true-probability assignments are
   director-owned, versioned artefacts. The company **NEVER observes either** — it does not know it is living in
   an overweighted tail; it just experiences a hard world. Only the tournament/scorer, *outside* the wall, applies
   the reweighting. (Extends the A.3 wall: the sampling/probability weights join the scenario state the company
   cannot read.)

**Run-weight bookkeeping (mechanism):** every run persists a `true_probability` tag alongside its output ledger
(C-S4 persistence-behind-interface), so any later aggregate can reweight without re-running. The scorer computes
EV as `Σ (run_metric × true_probability) / Σ true_probability` and survival as `min over runs (unweighted)`.

**Failure modes (amendment risk section):** (v) tail-heavy sampling silently leaking into fitness so the
tournament selects for *paranoia* rather than judgment — mitigated by reweighting at the scorer, R12 (no
diagnostic becomes a target), and the survival/EV split; (vi) the probability measure going stale as the real
world moves — mitigated by version-pinning + review at epoch boundaries (same cadence as harness best-practice
re-checks). See **§R15 obligation W5**.

### A.8 Gate — NON-VETOED (director ruling landed 2026-07-23)

The 2h veto window is **spent — the director did NOT veto** (`DIRECTOR_RULING_SCENARIO_NONVETO_AND_PRODUCT_STATUS_2026-07-23.md`,
commit 1dd89af03): "proceed — window not vetoed", the friction amendment rides the already-authorized WVC BUILD.
**Sequencing guard (binding):** the scenario FRAME and friction work run in the **WVC lane and must NOT preempt
PRODUCT-FIRST queue items 1–2** (site v5 pages; generator draw-wiring); if lanes contend, items 1–2 win the draw.
The **scenario parameter values** (A.6) and **which worlds enter rotation** remain a separate, standing director
gate (R13) — the mechanism proceeds; no non-baseline world enters rotation until its values are ratified.
One-way-door check: building the spine touches no real money, no external commitment, no safety control, no real
customer/market — reversible SIM machinery; PROCEED (SPINE_1 build) subject to the sequencing guard.

---

## B. Friction amendment to the authorized WVC BUILD (decision 5 — just do it, mitigations named)

### B.1 What amends

Decision 5 amends the WVC construct already framed in `WHOLESALE_VALUE_CHAIN_FRAME.md`. Two concrete changes to
the existing candidate atoms (no new atom):

- **`WVC_3_hedge_program_cover_fan`** — every cover-fan trade pays a **transaction cost = volume × half-spread**,
  looked up from the spread table by (product, horizon, regime). Costless rebalancing is now impossible — this is
  the mechanism that stops the hyperactive fake trader (decision 5 / §1).
- **`WVC_4_value_add_ledger`** — scores achieved-vs-benchmark **NET of friction from v1**, with the friction line
  attributed **separately** so gross is reconstructible (mitigation iii). Its invariant WVC-1
  (`benchmark + Σ attributions = achieved`) gains a **friction attribution term**; the sum-to-achieved check must
  include it or fail.

### B.2 Where the friction table lives

The bid-offer spread is a **market observable the desk pays**, not a company belief — so it lives SIM/market-side
as `sim/market/friction_table.py` (a sourced static table), exposed to the desk through the same market-observable
seam prices use (the company reads the spread it transacts at, exactly as a real desk sees a broker quote). The
**anchor values are registered in `ASSUMPTIONS.md`** per convention (the repo has no root `ASSUMPTIONS.md` today —
BUILD creates it or the agreed anchors doc; noted so BUILD doesn't silently invent a location).

### B.3 The initial static spread-by-horizon table (sourced)

A static, externally-anchored table is explicitly acceptable for v1 (decision 5); the regime-widening surface is
follow-on (4). Shape of the table: rows = product horizon (front month → far seasons/annual), columns =
baseload vs peak, plus an NBP-gas row; values = half-spread in £/MWh (or % of price). **Sourced from** the
existing repo research `docs/market_research/findings/bid_ask_spread_2026_06_23.md` (Ofgem Wholesale Market
Indicators + CMA Appendix 7.1), re-confirmed 2026-07-23 as still the best public source (the live Ofgem WMI portal
is currently inaccessible to automated fetch — a redirect loop — so BUILD refreshes it manually), plus the
Octopus/DESNZ consultation evidence already cited in the WVC frame (§3, "spreads for base/peak are non-linear in
volatility"). Known qualitative shape to preserve even where a precise number is
proprietary: **front tight, far seasons wide, peak > baseload, non-linear in volatility, widening toward the far
curve = the liquidity limit.** Where a value is proprietary and unsourceable, BUILD uses the best public bound and
flags it UNSOURCED in `ASSUMPTIONS.md` (fabricate nothing).

### B.4 Why net-of-friction from v1 (mitigation iii, re-based-later risk)

Scoring gross would overstate every early trading result and silently move the bar when friction lands later. By
carrying the friction term from v1 and logging it as a separate ledger line, gross is always reconstructible and
the bar never moves. The coupled-triad row (`coupled_gap_ledger.json`) records the friction-attributed gap
alongside the belief-vs-truth gap.

---

## C. Registered follow-ons (named map candidates — NOT built on this steer)

Sequenced candidates for the map, this doc cited as provenance. Named, not registered (orchestrator writes the
map). Levels/deps are proposals.

| id (proposed) | title | closes | depends_on | notes |
|---|---|---|---|---|
| `SPINE_1_scenario_world_state` | The `ScenarioSpine` object + curriculum registry + wall + byte-identical baseline (§A) | integration seam for rotation | `sim/scenario/` | The BUILD of A; proceeds after the 2h veto. |
| `SPINE_2_launch_worlds` | The three proposed worlds' ratified parameter VALUES (§A.6) | — | `SPINE_1`, director ratification (R13) | Values are director-gated; not agent-set. |
| `SPINE_3_gas_storage_crisis_regime` | Formed European storage stock-and-flow + gas-balance crisis regime (level+vol+corr jointly, persistent); the formed seasonal spread + its 2022 inversion | **F2 + F4** | `SPINE_1`, BC-1 | Steer follow-on (3). The load-bearing Spec-004 gap. |
| `SPINE_4_living_curve_and_spread_surface` | Forward curve as a living object with stored history; risk-premium dynamics (widen-after-crisis / compress-in-calm); liquidity horizon; full spread SURFACE with regime-widening | **F3** | `SPINE_3`, `WVC_2` | Steer follow-on (4). The object the cover fan accrues against; supersedes B.3's static table. |
| `SPINE_5_tail_machinery` | Stochastic outage process; interconnector/French channel; renewables-surplus negative-price floor | **F5** (formed tails once rotation leaves history) | `SPINE_3` | Steer follow-on (5). Ranked LAST — in-window the real Elexon record supplies tails. |

**Breadcrumbs registered (not atoms yet):**
- **Carbon limb of the spark spread** — the engine's own named R10 (UK-ETS term missing from merit-order). Cheap;
  may be wired earlier if trivially safe (W1_6 §1.2 blocker context).
- **Collateral / margin calls** — belong to the already-registered working-capital layer AND to this story
  (2022 broke hedged suppliers on **cash, not P&L**). `crisis_2021_22` world (A.6.ii) is where this bites.
- **Network / ancillary / locational costs** — PARKED, one breadcrumb: locational value re-enters at the
  customer-personalisation layer via distribution red-band avoidance, where it meets the £/tCO₂e thesis
  (postcode peak-avoidance value, UKPN-class constraints). Not built now.
- **Governing-rationale sentence** (§1, DoD 5) — a map-hygiene pass so "prices forecast error" lands in the
  wholesale atoms' purpose lines, not only in this doc.

---

## R15 obligations (DoD 4 — failable controls, named here, BUILT with their atoms)

Per R15 (a control that cannot fail is worse than none) + R13 (mitigations i–iv from the steer's risk section):

- **W1 — the wall test (mitigation ii, company-side leakage).** A mutation-testable epistemic check that no
  `company/**` or `saas/**` code imports `sim.scenario.spine` and no `ScenarioSpine` field crosses
  `sim_interface.py`. **Killer mutation:** add a `from sim.scenario.spine import ...` to a company module → the
  epistemic verifier must FAIL. FAIL-SILENT guard: if the verifier can't run (import graph unavailable), that is
  a FAILED check, never skipped-green. This extends the existing import-direction epistemic verifier (F1b
  precedent), not a new mechanism.
- **W2 — the byte-identical baseline test (mitigation iv, integration blast radius).** A golden-hash test: a
  fixed-seed `history_replay` run's settled ledger is byte-identical before/after the spine lands (§A.5).
  **Killer mutation:** make the spine loader apply a non-null override under `history_replay` → the hash diverges
  → the test FAILS. FAIL-OPEN guard: an empty/missing baseline hash is a FAILED check, never green.
- **W3 — curriculum-not-tuning guard (mitigation i, R12/R13).** The scenario parameter values are loaded ONLY
  from a committed, director-ratified curriculum artefact carrying a ratification record; no code path lets a
  company-P&L outcome write back a scenario value. **Killer mutation:** a test that a scenario value derived from
  a run's P&L is REJECTED at load (no write-back path exists). This is the R13 wall made mechanical: the agent
  controls both sides, so the curriculum must face the director.
- **W4 — friction never silently re-based (mitigation iii, decision 5).** The value-add ledger's friction term is
  a separate, always-present line from v1; gross is reconstructible. **Killer mutation:** drop the friction line
  (score gross) → invariant WVC-1's sum-to-achieved check must FAIL (the friction attribution is now missing from
  `benchmark + Σ attributions = achieved`).
- **W5 — no unweighted EV aggregate (amendment §A.7, failure mode v).** Any expected-value figure computed across
  runs MUST reweight by the persisted per-run `true_probability`; survival is the separate unweighted worst-case.
  **Killer mutation:** compute an EV aggregate as a plain mean over the tail-heavy sampled set (skip the
  reweighting) → the check must FAIL loudly (the biased-average trap is structurally uncommittable). FAIL-SILENT
  guard: a missing/NaN `true_probability` tag on any run in the aggregate is a FAILED check, never dropped-and-
  averaged. Survival's worst-case arm must remain unweighted (mutation: probability-weighting the survival verdict
  → FAIL).

---

## DoD (from the steer) — status this pass

1. **Scenario-spine FRAME on origin, veto window stated, launch-world set proposed with sourced anchors** — this
   doc (§A); 2h veto window stated (§A.7); three launch worlds proposed (§A.6) with anchors sourced in the
   companion research file. ✅ this pass (pending origin push).
2. **Friction term live in the first value-add ledger version, spread table sourced and registered** — SPEC'd
   here (§B) as the binding amendment to `WVC_3`/`WVC_4`; the CODE lands when those atoms build (the value-add
   ledger does not exist yet — friction is a constraint on its first version, not a standalone build). ⏳ BUILD
   (WVC_3/WVC_4), spec + sourced table this pass.
3. **Follow-ons (3)–(5) + carbon/collateral breadcrumbs registered as map candidates with this doc cited** —
   §C. ✅ this pass (named; orchestrator registers in the map).
4. **Wall test + byte-identical-baseline test named in the FRAME as R15 obligations** — §R15 (W1, W2, +W3, W4).
   ✅ this pass.
5. **Governing-rationale reflected wherever the wholesale lane states its purpose** — §1 records it; the
   propagation into atom purpose lines is registered as a map-hygiene breadcrumb (§C). ✅ recorded; ⏳ propagation.
6. **(amendment) FRAME states both weightings, their owners (director, R13), the per-run probability tag, the
   worst-case survival verdict, and the no-unweighted-aggregate R15 test** — §A.7 (sampling split, composition,
   bookkeeping) + §R15 W5. ✅ this pass.

**Not done this pass (correctly deferred):** the spine BUILD (after 2h veto), the friction CODE (with WVC_3/WVC_4),
the launch-world VALUE ratification (director, R13), and the map registration of the SPINE_* candidates
(orchestrator, sole map writer).
