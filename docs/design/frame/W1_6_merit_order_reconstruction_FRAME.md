<!-- SUPERVISOR_DRAW: self-drawable -->
<!-- FRAME (doc-only, drawable now per THREE_LANES L3 / EPOCH_GATING). BUILD held behind the
     propose-then-proceed window (open until 2026-07-28) per PLANNER_MINTED_merit_order_reconstruction_discover_2026-07-25.md.
     This is scope items 1 (FRAME live-vs-target + exact diff) and 3 (acceptance test + invariant + R15 mutation).
     Item 2 (DISCOVER ground truth) is PARTLY SATISFIED by the 2026-07-24 pass — remaining gap named in §3. -->

# FRAME — Merit-order / gas-first price-engine reconstruction (W1_6 physics price signal)

**Atom / row:** `W1_6_physics_price_signal` · fidelity row `ssp_residual_demand_scarcity_calibration_2026_07_19`
**Serves:** DIRECTOR_AXES axis 3 (Believability); Board Spec 004 (Price Formation) reconstructibility; the named unblock for `PLANNER_MINTED_ssp_negative_lift_cells` part (a); convergence with Board Spec 001 gas-first finding (F1).
**Status:** DISCOVER/FRAME (doc-only). BUILD held (R13 baseline discipline; propose-then-proceed window to 2026-07-28). Any level claim stays `blocked_on: director_level_up`.

This doc makes the fix **named** in `DIRECTOR_RULING_SSP_BASELINE_HELD_MERIT_ORDER_FIRST_2026-07-25` — the merit-order reconstruction — **drawable** (R16: a fix named only in a ruling body is invisible to the draw). It does not build the engine.

---

## 1. FRAME — the live form vs the target form, and the exact diff

### 1a. What `sim/` price formation does today (evidence-cited)

Live in `sim/price_engine.py` (module docstring calls itself "merit-order wholesale price model", but the marginal-cost structure is a **single, globally-fitted reduced form**, not a dispatched plant stack):

**Gas floor** (`gas_floor_price`, lines 110–128):

    P_gas_floor = (gas_price + carbon_price · EF_GAS_TCO2_PER_MWH_TH) / thermal_efficiency

with module constants `THERMAL_EFFICIENCY = 0.50`, `EF_GAS_TCO2_PER_MWH_TH = 0.184`, and
`carbon_price_gbp_per_tonne` **defaulting to 0.0 in every call** (no historical UK-ETS series is wired — module docstring §77–80; the carbon term is present but never exercised at runtime).

**Scarcity multiplier** (`system_margin_price`, lines 131–169):

    RD = demand_mw − renewable_generation_mw            (residual/thermal demand)
    x  = RD / DISPATCHABLE_CAPACITY_MW                   (DISPATCHABLE_CAPACITY_MW = 35000.0)
    multiplier = A0 + A1·x + A2 · max(0, x − X_TIGHT) ** SCARCITY_EXPONENT
    P_HH = P_gas_floor · multiplier

Calibrated constants (2026-07-19, module lines 99–103): `X_TIGHT = 0.70`, `SCARCITY_EXPONENT = 2.0`,
`A0 = 0.326998`, `A1 = 1.334629`, `A2 = 3.828327`. These were fit by grid-search over
(X_TIGHT, SCARCITY_EXPONENT) then closed-form least-squares for (A0, A1, A2) against real Elexon SSP
(`sim/cache/elexon_ssp_full.json` etc.; NBP gas via `sim/gas_prices_history.py`).

**Key structural properties of the live form:**
- It is **one global curve**: a single (A0, A1, A2) applies to every half-hour of 2016–2025. There is no plant-by-plant merit stack; "merit order" enters only as the *shape* of one multiplier on one gas floor.
- The scarcity term earns its keep only above `x > X_TIGHT = 0.70` — good intuition, but the **whole ordinary-day price** is the gas floor times `(A0 + A1·x)`, i.e. still a fitted line, not a dispatched marginal-plant cost.
- Carbon is structurally present but numerically absent (default 0.0), so ordinary-day price does not move with UK-ETS.

### 1b. The measured defect this repairs (evidence-cited)

Fidelity row `W1_6_physics_price_signal::ssp_residual_demand_scarcity_calibration_2026_07_19`
(`docs/observability/fidelity_evidence_ledger.json`) records the **per-cell lift** of the live form over the
best-of-naive-family baseline (`background/fidelity_emitter.py::_NAIVE_FAMILY_IDS =
("gas_floor_alone", "ols_regression_3feature")`), by year-cell (lift = MAE_naive − MAE_model, £/MWh; positive = model wins):

| cell | regime | best naive baseline | lift (£/MWh) |
|------|--------|--------------------|--------------|
| y2016 | calm | gas_floor_alone | **+2.23** |
| y2017 | calm | gas_floor_alone | +0.25 |
| y2018 | calm | gas_floor_alone | +0.04 |
| y2019 | calm | ols_regression_3feature | **−0.79** |
| y2020 | calm | ols_regression_3feature | **−3.22** |
| … 2022 | crisis | — | **+5.55** (per mint) |

The pattern: the global scarcity form **under-fits the renewables-heavy, low-x calm years** (2019, 2020
negative — a 3-feature OLS beats it) and the +1.17 aggregate lift is carried almost entirely by the 2022
crisis. In plain terms: **it looks right on average because it is right in a crisis; on ordinary
renewables-heavy days it is not reconstructing price from fundamentals.** That is exactly the veteran
smell test Board Spec 004 puts at the centre.

The row's own `simplification_note` (`ssp_scarcity_form_calm_low_x_underfit_bounded_2026_07_24`) already
records this as an R10 named simplification, and `relationship.independent_anchor` records the standing gap:
*"no third-party published benchmark was used to cross-check the fitted A0/A1/A2 constants themselves"*
(bounded but not closed by the 2026-07-24 external pass — see §3).

### 1c. The target form (merit-order / gas-first)

A **stacked short-run-marginal-cost (SRMC) dispatch** against residual demand, where ordinary-day price is
the SRMC of the *marginal plant* rather than a fitted multiple of the gas floor:

- Build an ordered SRMC stack per plant *type* (nuclear/CCGT/OCGT/coal-until-2024/etc.), each type's SRMC =
  fuel-cost/efficiency + carbon·EF + variable-O&M (heat rates / efficiencies from published GB sources).
- Dispatch cheapest-first against residual demand `RD = demand − must-run renewables (+ nuclear/imports)`.
- **Ordinary-day price = SRMC of the marginal (last-dispatched) plant** — on most GB days that is a gas
  CCGT, so price ≈ NBP-gas/efficiency + carbon, moving with gas *and* carbon (Board Spec 004 / Spec 001 F1).
- **Scarcity earns its structure only in tight hours** — when RD approaches the top of the stack (peakers,
  reserve, cash-out), price rises convexly toward the regulatory scarcity ceiling. This is the *only* place a
  scarcity term survives; it is no longer a multiplier on ordinary hours.

### 1d. The exact diff (live → target)

| dimension | LIVE (today) | TARGET (merit-order) |
|-----------|--------------|----------------------|
| price basis, ordinary hours | `gas_floor · (A0 + A1·x)` — a fitted line on one floor | SRMC of the marginal dispatched plant (usually CCGT) |
| plant resolution | one implicit plant (single THERMAL_EFFICIENCY=0.50) | a typed SRMC stack (≥ nuclear/CCGT/OCGT/coal-until-2024) |
| carbon | present but 0.0 at runtime | live UK-ETS in every marginal-plant SRMC |
| scarcity | every-hour multiplier (`A0+A1·x` below tight) | tight-hours-only term toward the £6,000/MWh cash-out ceiling |
| calibration | global (A0,A1,A2) fit to the whole SSP curve | structural constants from published heat rates; no curve-fit of ordinary-day level |
| efficiency | fixed 0.50 | per-plant-type efficiencies |
| capacity | one `DISPATCHABLE_CAPACITY_MW = 35000` constant | typed capacities, time-indexed to fleet exit (coal to 2024) |

**The one-sentence fidelity delta:** ordinary-day price stops being a fitted multiple of a gas floor and
becomes the marginal-cost of the plant that actually sets the margin — pricing that is *right* rather than
pricing that merely *looks right now*.

---

## 2. DISCOVER — ground truth (delegate to `discovery-agent`, read-only → `docs/market_research/`)

**Partly satisfied already (2026-07-24 pass, cited, do not re-run):**
- `docs/market_research/ssp_dispatchable_fleet_renewables_era_boundaries_2026-07-24.md` — DUKES Ch.5 capacity/renewables-share era boundaries → time-indexes `DISPATCHABLE_CAPACITY_MW` and the coal-exit boundary (last GB coal plant closed 2024).
- `docs/market_research/ssp_scarcity_constants_external_benchmark_2026-07-24.md` — GB cash-out/scarcity **ceiling £6,000/MWh** (DDM design, observed-with-evidence); Reliability Standard **LOLE ≤ 3 h/yr**; **CCGT confirmed as GB reference marginal technology** (CM Net-CONE context); and the honest gap: **no published source uses the same reduced functional form** as the live A0/A1/A2 curve.

**Remaining named gap (the DISCOVER work this reconstruction still needs — network-dependent, not run this tick):**
a **multi-plant SRMC stack**, not a single CCGT floor: published GB heat rates / thermal efficiencies per
plant type (CCGT, OCGT, coal-until-2024, and reserve/peaker tiers), variable O&M, and a UK-ETS carbon-price
time series, from DESNZ/DUKES/BEIS/Ofgem/Elexon. **Pre-load ground-truth context before any local model
touches sources** (key learning). **No fabricated constants** — cite or leave a named gap (R10). Network was
403-on-probe this tick; register as the next drawable DISCOVER step, not a claimed closure.

---

## 3. DEFINE the acceptance test — the reconstructibility test, BEFORE any build

The reconstruction lands **only** when both of the following hold. These are written now so BUILD cannot
move its own goalposts (LAW A: the test is the only gate).

### 3a. The ordinary-day reconstructibility test (Board Spec 004)
On **ordinary (non-tight, non-crisis) half-hours** — define ordinary as `x = RD/capacity ≤ X_TIGHT` AND the
year-cell regime is `calm` — the reconstructed price must be **substantially reconstructible from gas +
carbon + demand + wind**: the marginal-plant SRMC prediction must beat the `gas_floor_alone` naive baseline
on MAE **within each calm year-cell, including the low-x renewables-heavy cells 2019 and 2020** where the
live form currently posts negative lift (−0.79, −3.22). Falsifiable, per-cell, no aggregate hiding a
crisis-carried win.

### 3b. The unmoved-baseline invariant (right-vs-tuned proof)
Re-measure the **same** `W1_6` per-cell lift table against the **same, unchanged** naive baseline family
(`background/fidelity_emitter.py::_NAIVE_FAMILY_IDS`, unedited) after the reconstruction. The naive family is
**frozen** — it is the ruler, not a knob. The proof that pricing became *right* rather than *tuned* is that
the calm-cell lifts move **positive on structure**, while the crisis-cell lift is **not inflated** by
re-baselining. **Do not re-baseline the benchmark to suit the new engine** (the ruling forbids exactly this).

### 3c. R13 / R12 discipline (binding on BUILD, not a wall against it)
The baseline changes for **fidelity-to-reality reasons only, decided blind to company P&L**. **No interim
tuning** — no per-cell fits, no regime-partition coefficient passes, no "temporary" recalibration while the
structural work waits. Motivation is reconstructibility-from-fundamentals, never how company results look.

### 3d. The R15 mutation the acceptance test must survive
The reconstructibility check must be a control that **can fail on its own named defect**. Two mutations it
must catch (else the test is theatre — TAUTOLOGY / FAIL-OPEN):
1. **Frozen-ruler mutation:** if a build edits `_NAIVE_FAMILY_IDS` (or shifts a naive baseline's MAE) to make
   the lift look positive, the invariant test must go **RED** — the baseline is checked by hash/identity, not
   recomputed from the same source it grades (independence).
2. **Crisis-carry mutation:** feed a reconstruction that wins only in the 2022 crisis cell and stays negative
   in 2019/2020; the per-cell (not aggregate) test must go **RED**. A test that passes on aggregate lift alone
   is FAIL-OPEN against exactly the defect this atom exists to repair.

---

## 4. Walls untouched (director-reserved)
- **Curriculum values** (scenario mix, difficulty) — R13, director-reserved. This touches the **baseline**
  price-formation form (fidelity), never the curriculum.
- **One-way doors** — none. DISCOVER is doc-only/reversible; BUILD is a git-reversible sim change behind the
  epistemic wall (no real market, no real money).
- **L3 level moves** — any level claim stays `blocked_on: director_level_up`.
- **Ground-truth fabrication forbidden** — DISCOVER cites published sources or registers a named gap; it
  never invents plant efficiencies or carbon costs.

— FRAME, drawn from `PLANNER_MINTED_merit_order_reconstruction_discover_2026-07-25.md` scope items 1 & 3, 2026-07-25.
