# FRAME — W1_4_regional_weather_field — regional weather field, consolidated

**Atom:** `W1_4_regional_weather_field` | **Lane:** `W1_market_weather` | **Dial:** 3
**level_current:** 0 → **level_target:** 3 | **depends_on:** `W1_3_national_weather_signal`
**Stage:** Lane-3 DISCOVER/FRAME, doc-only. `loop_stage: idle` — BUILD-gated behind W1_3.
No sim/company/saas code, no test, no `maturity_map.yaml` edit in this pass.

**What this document is.** This atom already carries three prior artefacts: the dedicated
frame `docs/design/frame/W1_4_regional_weather_field_FRAME.md`, the mechanism-authoritative
`docs/design/WEATHER_PHYSICS_HIERARCHY_DESIGN.md` §1.2 (director-set: "the mechanism is
ours ... physics first"), and the repo-audit `docs/design/W1_4_REGIONAL_WEATHER_FIELD_DISCOVER.md`.
This document does **not** re-derive a competing design. It **consolidates** those three into
one FRAME artifact that states the problem, the concrete region set, the generative model, the
formal invariant + its mutation-test design, feasibility bounds, RNG/blindfold discipline, and
the L0→L3 decomposition in one place, so a BUILD pass has a single entry point rather than three.
Where a design choice is already settled upstream, this doc cites it rather than restating it in
different words; where a question is still genuinely open (region key, exact weight source), it
says so rather than inventing an answer.

---

## 1. Problem — why regional weather matters, on top of the national signal

`W1_3` produces one number per variable (temperature, wind, solar/cloud) per settlement period
for **GB as a whole**. That national signal drives national heating demand and national
renewable output — but it hides real, material spatial structure a supplier is exposed to:

- **Regional demand.** GB has a real, persistent north-south and coastal-inland temperature
  gradient (Met Office climate normals): northern Scotland and inland/upland areas run
  measurably colder in winter than London and the south coast on the *same* day. A supplier
  whose book is regionally concentrated (e.g. weighted to Scotland) feels a colder winter than
  the national HDD average implies; a book weighted to the South East feels a milder one. Flat
  national HDD correction misprices this.
- **Regional renewable generation.** GB wind capacity (onshore and offshore) is heavily
  concentrated in Scotland and the North Sea approaches, not spread evenly across the country;
  solar irradiance has a real south-north gradient. National wind/solar output is a
  capacity-weighted sum over regions with very different installed capacity and very different
  local weather, not a flat multiplier on one national wind speed. This matters directly to the
  L4 price chain (`W1_6`, `WEATHER_PHYSICS_HIERARCHY_DESIGN.md` §1.4): the same national
  blocking-high can hit a wind-heavy region harder than the national mean suggests.
- **Network/settlement realism.** Regional structure is the substrate for GSP Group Take,
  DUoS charging (already regionalised in `company/market/duos_ledger.py::DNOArea`), and later
  network-constraint/curtailment atoms — none of which exist meaningfully on top of a single
  national number.

The risk this atom must not create: an **independent** per-region draw. If regions are drawn
independently of each other and of the national signal, the resulting field is (a) spatially
incoherent — Scotland could freeze while the adjacent Borders stay mild, which real synoptic
weather does not do — and (b) **disconnected from W1_3**, i.e. a second, contradictory weather
story rather than a decomposition of the one true national number. Both failure modes are closed
by the design below: spatial correlation (§3) and the aggregation-consistency invariant (§4).

---

## 2. Region decomposition — the region set and demand weights

### 2.1 Candidate region keys (repo audit, `W1_4_REGIONAL_WEATHER_FIELD_DISCOVER.md` §2.1)

Three real GB partitions are candidates, and the repo already has usable structure for two of
them:

- **DNO licence areas (14).** Already implemented as a real-UK-region enum:
  `company/market/duos_ledger.py::DNOArea` — `NORTHERN, YORKSHIRE, EAST_MIDLANDS, WEST_MIDLANDS,
  SOUTH_WESTERN, SOUTHERN, EASTERN, LONDON, SOUTH_EASTERN, MERSEYRAIL, NORTH_WESTERN,
  EAST_OF_SCOTLAND, HYDRO, SOUTH_WALES` — used today purely for DUoS network-charge billing,
  disconnected from weather. Two value names (`MERSEYRAIL`, `EAST_OF_SCOTLAND`) look like
  probable naming slips against the real licence-area names (Merseyside & North Wales / SP
  Manweb; South/Central Scotland — SP Distribution); **flagged unverified, not corrected here**
  — correcting a billing enum is out of this atom's `file_scope` (`docs/design` only)
  regardless, and the correction belongs to a BUILD-time check against Ofgem's licensed-DNO
  list, not a guess in a design doc.
- **GSP Groups (~14, lettered).** The settlement-native partition used for supplier "GSP Group
  Take" line-loss adjustment (referenced in `docs/data-sources/profile-class-1.md`,
  `docs/PROJECT_OVERVIEW.md`'s MeterPoint model). Closely related to, but not verified identical
  to, the DNO partition.
- **The 4 existing calibration locations, extended.** `sim/weather_engine.py`'s Pass-2 Cholesky
  mechanism (§3 below) is already calibrated against 4 real Open-Meteo point series (`C1..C4` =
  London/Manchester/Glasgow/Cotswolds, per `simulation/weather_inputs.py`'s docstring), a
  hand-picked spread for calibration variety, not an administrative partition.

**Which key BUILD should choose is named as the first genuinely open BUILD decision, not
resolved here** (both the FRAME and DISCOVER predecessors leave it open, for good reason — it is
a real-data-availability question, not a design-taste one). Two considerations for BUILD:
DNO areas reuse the *existing* `DUoSLedger` billing code (one canonical region key across two
lanes, avoiding a second disconnected regional taxonomy); GSP Groups are the closer fit if the
intent is direct alignment with Elexon/BSC settlement profiling. Either choice is compatible
with everything else in this document — the generative model and the invariant are stated over
an abstract region set `𝓡`, not over a specific enum.

### 2.2 Demand weights `wᵣ` — must be REAL, not derived from the project's own cast

The reconciliation invariant (§4) is only physically meaningful if `wᵣ` is a genuine demand
share, `Σ_r wᵣ = 1`, sourced independently of this project's own ~31-account customer cast (that
cast is far too small and non-representative to imply a real regional split). The correct class
of source is **DESNZ sub-national electricity/gas consumption statistics** (regional
consumption shares) — named as a class here, not fetched (no network access in this Lane-3
fork; a `discovery-agent` pull is the right mechanism, matching the anchoring rule below).
Generation-relevant variables (wind, solar) reconcile under a **different** weight — regional
**installed-capacity share** for that technology, not demand share — because national wind
output is a capacity-weighted sum, not a population-weighted one; sourced from DESNZ/NESO
regional generation-capacity statistics, again a different real source than the demand weights.

**Anchoring rule (anti-marking-own-homework, inherited from `WEATHER_PHYSICS_HIERARCHY_DESIGN.md`
§5):** the GENERATOR anchor (real historical weather/demand used to fit the field) and the
VALIDATOR anchor (independent published sub-national statistics used to check the reconciled
aggregate) must be **different sources**. The company never validates against SIM ground truth;
the harness validates the SIM's own regional field against a source the field was not fitted on.

---

## 3. Generative model — spatially-correlated deviations around the national anchor

### 3.1 What already exists (do not re-invent)

`sim/weather_engine.py` Pass 2 already implements the reusable mechanism:

```python
def fit_regional_cholesky(location_daily, national_daily) -> dict[str, dict]:
    # for each macro variable: deviations = location_series - national_series
    # cov = np.cov(deviations.T) + jitter; cholesky = np.linalg.cholesky(cov)

def simulate_regional_deviations(regional_params, n_days, rng) -> dict[str, dict[str, np.ndarray]]:
    # z ~ N(0, I); deviations = z @ cholesky.T + mean   (per location, per variable)
```

This **fits a real cross-location covariance** of `(location − national)` deviations from
calibration data and draws **correlated** deviations via a Cholesky factor — i.e. neighbouring
/ correlated locations do **not** get independent noise; the mechanism already preserves real
spatial correlation and is already "physically bound" to the national series (deviations are
defined *relative to* the national Pass-1 output, never replacing it). This is genuinely the
spatial-correlation half of L2 — it is not greenfield. What it is **not yet** is: (a) keyed to a
real administrative region set rather than 4 hand-picked points, (b) attached to any demand/
capacity weight, and (c) made aggregation-consistent (§4) — none of that exists in
`sim/weather_engine.py` or `tests/sim/test_weather_engine.py` today.

### 3.2 The construction, generalised to a named region set

For each region `r ∈ 𝓡` and weather variable `v` (temperature, wind, solar/cloud):

```
X_{r,v}(t) = X_national,v(t) + Δ_{r,v}(t)
```

`Δ_r` is drawn from a mean-zero spatial field whose covariance is **distance-keyed**:
`Cov(Δ_r, Δ_s) = σ² · k(dist(r,s))`, an exponential/Matérn kernel `k` whose correlation length
is fitted so neighbouring regions covary strongly and distant ones weakly (Cornwall and Devon
move together; Cornwall and Aberdeen do not). This is the existing Cholesky mechanism above,
generalised from 4 calibration points to the chosen region set (§2.1) — an extension of
calibration data, not a new algorithm, per `W1_4_REGIONAL_WEATHER_FIELD_DISCOVER.md` §3.

**Method choice for the reconciliation step itself** (settled by `WEATHER_PHYSICS_HIERARCHY_DESIGN.md`
§1.2, adopted here rather than re-litigated): **projection, not luck**. A raw Cholesky draw does
*not* satisfy the reconciliation invariant on its own (the weighted deviations don't sum to
zero by construction). After drawing `Δ`, apply a demand-weighted-mean projection:

```
Δ'_r = Δ_r − Σ_s w_s · Δ_s        # subtract the weighted mean deviation
```

This makes `Σ_r wᵣ · Δ'_r = 0` **identically** — an algebraic projection onto the
zero-weighted-mean manifold — so §4's invariant holds by construction, not by chance. The
alternative considered and rejected as the *primary* mechanism: "conditional sampling given the
national signal" (draw regional structure conditioned on the fixed national value). This is
mathematically equivalent in spirit but the FRAME's projection form is preferred because it is
a simple, auditable, one-line linear operation on an existing draw — the SIMPLICITY GUARD
floor — rather than requiring a new conditional-sampling machinery.

---

## 4. The aggregation-consistency invariant — formal statement + mutation-test design

### 4.1 Formal statement

Let `wᵣ` be region `r`'s reconciliation weight for variable `v` (demand share for temperature;
capacity share for wind/solar; `Σ_r wᵣ = 1`, sourced per §2.2). Define the reconciliation
residual for variable `v` at settlement period `t`:

```
ρ_agg(v, t) = Σ_r wᵣ(v) · X_{r,v}(t)  −  X_national,v(t)

INVARIANT (I1):  |ρ_agg(v, t)| ≤ tol_agg     for every variable v, every period t
```

Because `Δ'_r` is constructed by projection (§3.2), `Σ_r wᵣ · X_r = X_national` holds **exactly,
up to floating point** — `tol_agg` is therefore a *numerical* tolerance (machine-epsilon scale
plus float accumulation over `|𝓡|` regions), never a modelling fudge-factor. "Every region
freezing while the national mean stays mild" is not merely improbable under this construction —
it is **off the manifold and cannot be constructed**, which is the acceptance bar this atom's
own name sets ("AGGREGATION-CONSISTENT... an invariant, mutation-tested").

### 4.2 Mutation-test design (R15 — a control that cannot fail is worse than none)

The invariant is worthless as a control unless it can be shown to **fire**. Design, closing all
three R15 killer patterns explicitly:

- **Primary mutation (perturb a region off-manifold).** After the projection step, add a fixed
  offset `ε ≫ tol_agg` to one region's deviation for one variable (e.g. drive one region's
  temperature 10°C colder than the projected value, or scale one region's wind deviation by a
  large factor) **without re-running the projection**. Assert the check **FIRES**:
  `|ρ_agg(v,t)| > tol_agg`. This is the atom's own defect scenario named in the ATOM brief:
  *a region's value is perturbed so the aggregate breaks*.
- **Secondary mutation (attack the weights, not the field).** Swap the reconciliation weights
  used at check-time from the real demand/capacity shares to a naive **uniform** `1/|𝓡|` split
  while the field was projected under the real weights. Assert the residual **reopens** —
  proves the check is actually reading `wᵣ`, not a hardcoded pass.
- **TAUTOLOGY guard (R15 independence requirement).** The checker must recompute
  `Σ_r wᵣ X_r(t)` **independently from the region series** and compare it to the **national
  series held from W1_3**, produced upstream and never re-derived from the same regional
  deviations being checked. A checker that reads back a "national" value computed *from* the
  regional sum would always pass — this is the exact TAUTOLOGY pattern R15 forbids, and the
  reason `depends_on: W1_3_national_weather_signal` matters structurally, not just for
  sequencing: W1_3's output is the independent anchor this invariant checks against.
- **FAIL-OPEN guard.** An empty/missing region set, all-zero deviations, a missing weight for
  a region, or a NaN weight/deviation must make the check **FAIL**, not pass trivially — a
  degenerate field is not a reconciled field. Concretely: the check asserts `|𝓡| > 0`,
  `Σ_r wᵣ` finite and ≈1, and every region has a finite deviation *before* computing `ρ_agg`;
  any of those failing is itself a fired failure, never a silent skip.
- **FAIL-SILENT guard.** If the national signal (W1_3's output) or the weight table is
  unavailable at check time, the check reports **FAILED**, never green-by-absence — matching
  the doctrine that an unavailable check is a failed check, not a skipped one.

The mutation tests, once BUILD writes them, are this atom's L2/L3 promotion evidence — per R15,
no level credit for the invariant without them, and per COUPLED_TRIAD this atom may not reach
L3 until the company has also been tested against the field (§6).

---

## 5. Feasibility bounds

Regional values must be physically possible, independent of the reconciliation invariant (a
field can reconcile in aggregate while still containing an individually impossible region):

- **Temperature:** within a plausible regional range for the season (e.g. bounded around the
  national value by a climatologically-justified spread; a region should not read 20°C colder
  than the national mean in a single period). Exact bound calibrated from real regional
  temperature-spread data (Met Office), not invented.
- **Wind:** non-negative; bounded by a regional climatological ceiling consistent with the
  existing turbine power-curve treatment in `sim/price_engine.py` (cut-in 3 m/s, cut-out
  25 m/s) — a region reading implausibly above the cut-out ceiling for its typical climate is a
  feasibility violation, not merely a tail event.
- **Solar/irradiance:** non-negative, diurnally consistent (zero at night, bounded by the
  clear-sky envelope already in `weather_engine.py` attenuated by cloud) — a region can't show
  daytime irradiance exceeding its clear-sky ceiling.

A named feasibility check rejects an infeasible regional value; a planted out-of-range region
(e.g. wind speed set above the physical ceiling) is a further mutation test, distinct from and
additional to §4.2's reconciliation mutations — a field can pass reconciliation and still fail
feasibility, and both must be checked independently.

---

## 6. RNG substream discipline + Point-in-Time Blindfold

- **C-S2 — named substream.** Regional deviation draws come from their **own named, seeded
  substream** — `regional_field` (matching the naming already fixed in
  `WEATHER_PHYSICS_HIERARCHY_DESIGN.md` §7), distinct from `national_regime` (W1_3), from
  `premise_noise` (W1_5), and from every other subsystem's substream, derived the same way
  `simulation/population_draw.py::_substream()` already does (SHA-256 of base seed + salt →
  an independent `random.Random`/`np.random.Generator`). This is the direct, tested precedent
  for the 01:09Z incident's lesson: adding or altering regional draws must never shift any
  other subsystem's output.
- **Deterministic replay.** Same seed ⇒ identical regional field ⇒ identical reconciliation
  residual on replay — required for the mutation tests themselves to be reproducible, and for
  the harness's belief-vs-truth gap (§7) to be a stable measurement rather than re-rolled noise.
- **Point-in-Time Blindfold.** Regional weather is **company-knowable** — real regional weather
  forecasts and outturns are genuinely published (Met Office regional data, third-party
  services), so this sits on the **public side of the wall**, unlike W1_3's latent regime state
  or W1_5's true premise thermal parameters, which stay SIM-internal. The company may read
  realised regional weather through a new typed seam method (not built now — no weather-shaped
  method exists on `company/interfaces/sim_interface.py` today, confirmed independently by the
  `C13_weather_normalisation` DISCOVER pass); it may never read the region-covariance
  parameters, the RNG substream state, or the pre-projection raw Cholesky draw.

---

## 7. COUPLED TRIAD (the gap is the score)

- **SIM adds:** the regional ground-truth field — spatially-coherent, feasible, reconciling to
  W1_3's national signal by construction. SIM knows the true per-region path and therefore the
  true regional demand/embedded-generation consequence.
- **COMPANY discovers/copes (may be wrong):** never reads the SIM's regional field directly. It
  observes regional *consequences* through the wall — its own book's regional metered demand,
  published regional weather it could buy, its exposure concentrated or diversified across
  regions. A company that treats the country as spatially uniform, or misjudges its own
  regional concentration, is a permitted failure mode, not a defect — exactly the
  national-vs-regional hedging frontier `WEATHER_PHYSICS_HIERARCHY_DESIGN.md` §6.3 names (GB
  has no regional forward market, so regional basis genuinely cannot be hedged today; both
  "hedge to national and eat basis risk" and "over-protect regionally and eat cost/illiquidity"
  are real, non-free strategies).
- **HARNESS measures:** the company's regional demand/generation estimate vs SIM truth per
  region (the gap), **and** enforces the reconciliation invariant as a structural gate on the
  SIM field itself (§4). Per COUPLED_TRIAD, this atom may not reach L3 until the company has
  been tested against the regional field and the gap measured — the pairing is with
  `C13_weather_normalisation` / `W1_5_premise_demand_shape`'s coupled twin, not designed fresh
  here (already specified in `WEATHER_PHYSICS_HIERARCHY_DESIGN.md` §6).

---

## 8. Level decomposition (L0 → L3) + file_scope

| Level | Scope | file_scope it would touch |
|---|---|---|
| **L0** (current) | Nothing regional-specific credited; only the 4-point calibration mechanism exists, disconnected from any real region/weight/invariant. | — |
| **L1** (this FRAME) | Design consolidated: region-key options named, generative model specified (reuse of existing Cholesky + projection step), invariant stated formally, mutation-test design specified, feasibility bounds named, RNG/blindfold discipline fixed. **No code.** | `docs/design/` only |
| **L2** (BUILD target — matches the atom's own DoD) | Region-key decision made (§2.1) and demand/capacity weights sourced (§2.2, discovery-agent pull against DESNZ/NESO); Cholesky calibration extended from 4 points to the chosen region set (or new real per-region Open-Meteo pulls via `sim/weather_ingestor.py`); the projection step (§3.2) implemented; invariant I1 (§4.1) implemented and its full mutation-test suite (§4.2) passing; feasibility checks (§5) implemented; RNG substream (§6) wired. | `sim/weather_engine.py`, `sim/weather_data/`, `sim/weather_ingestor.py`, `tests/sim/test_weather_engine.py`, possibly `company/market/duos_ledger.py` (if DNO key reused — read-only reuse, not billing-logic change) |
| **L3** | Time-varying weights (regional demand/capacity shares evolve over the simulated years, e.g. growing northern wind capacity); regional network-constraint/curtailment consequences wired into a later atom; curriculum-controlled regional severity events (director-authored per R13); C-S5 time-scale-invariance of the reconciliation stated explicitly; the COUPLED TRIAD gap (§7) measured and reported. | adds `company/interfaces/sim_interface.py` (new typed regional-weather seam method), harness reporting paths |

**BUILD-gating restated:** this atom cannot leave L0 for BUILD purposes until `W1_3` exposes a
stable national signal (nothing to decompose or reconcile against otherwise) **and** the
reconciliation weights have a benchmark source. DISCOVER/FRAME work (this document, region-key
research, weight-sourcing) is available now and does not itself move BUILD level — L1 here
records the FRAME artifact only, consistent with the atom's `loop_stage: idle` / epoch-3 gate.

---

## 9. Portability + scale-readiness (cited, not re-derived)

- **Portability:** the region set is a configurable key set + weight table behind a typed
  `RegionField`-shaped construction, not a hardcoded "14 GSP Groups" constant — a second
  geography supplies its own region set/weights/covariance without touching the reconciliation
  logic, which is geography-independent by design (weighted-sum-equals-anchor is an algebraic
  identity, not GB-specific).
- **C-S1/C-S4:** regional values arrive/persist through the same append-only event-log / typed
  seam discipline as the national signal; no company-side consumer may assume batch
  completeness across all regions at once.
- **C-S5:** the reconciliation invariant itself is time-scale invariant (an algebraic identity
  over whatever time index the national signal uses); the *sampling* method's granularity
  assumptions (if any) are registered as a named simplification at L3, not asserted now.
- **SIMPLICITY GUARD:** a region set + a weight table + a covariance kernel + a linear
  projection step. No region-adapter cathedral, no GIS engine, no new storage architecture —
  the existing Cholesky mechanism and the existing DUoS region enum are reused, not replaced.

---

## 10. Curriculum note (R13)

**Baseline** (blind to company P&L): real regional climatology — inter-region correlation
structure, demand/capacity weights, typical regional offsets — calibrated only for
fidelity-to-reality, never adjusted because company results look wrong. **Curriculum**
(director-owned): *regional severity* — how extreme a regional cold snap, wind lull, or
region-specific event a given world throws at the company — is a named, versioned,
director-authored scenario, never silent parameter drift and never tuned by the agent in
response to outcomes.

---

*Sources consolidated in this pass: `docs/design/frame/W1_4_regional_weather_field_FRAME.md`
(prior dedicated FRAME — invariant statement, spatial-coherence rationale, level decomposition);
`docs/design/WEATHER_PHYSICS_HIERARCHY_DESIGN.md` §1.2/§2/§6/§7 (director-set, authoritative
mechanism: projection-based I1, RNG substream names, wall/blindfold ruling, coupled-gap
metric); `docs/design/W1_4_REGIONAL_WEATHER_FIELD_DISCOVER.md` (repo audit — confirms
`sim/weather_engine.py`'s `fit_regional_cholesky`/`simulate_regional_deviations` already exist
and are reusable; grounds the region-key choice in real `DNOArea`/GSP structure; flags the
`MERSEYRAIL`/`EAST_OF_SCOTLAND` naming question, unresolved, out of scope here);
`sim/weather_engine.py` (read directly, lines ~173-215, this pass); `company/market/duos_ledger.py::DNOArea`
(read directly, this pass); `docs/design/maturity_map.yaml` (`W1_4_regional_weather_field`
entry and its full simplification history, read directly — confirms `level_current: 0`,
`depends_on: [W1_3_national_weather_signal]`, `file_scope: [docs/design]`); `CLAUDE.md`
(R15, C-S1/C-S2/C-S4/C-S5, R13, COUPLED_TRIAD, epoch-gating, portability constraints).*
