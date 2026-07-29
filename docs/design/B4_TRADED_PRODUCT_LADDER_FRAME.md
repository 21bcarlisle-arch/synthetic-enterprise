# B4_traded_product_ladder — FRAME

DISCOVER + FRAME only. No build code. Lane-3 fork, verified against disk (`path:line`),
not inherited from BACKLOG.md prose. Atom: `docs/design/maturity_map.yaml` id
`B4_traded_product_ladder` (lane `W1_market_weather`, epoch 3, `level_current: 0`,
`file_scope: [sim/product_ladder.py, tests/sim/test_product_ladder.py]`).

## 1. Verified current state

### 1a. The SIM-side forward price is a single scalar, monotone in tenor, and cannot invert

`sim/forward_curve.py:138-209` `generate_forward_price()` computes

```
forward = spot_ewma × seasonal_shape(delivery_months, fuel) × (1 + term_premium)
```

- `term_premium` (`sim/forward_curve.py:198-201`) = `base_premium × sqrt(tenor_years) × (risk_factor/1.2)`,
  `base_premium` is `BASE_TERM_PREMIUM=0.06` (electricity) / `GAS_BASE_TERM_PREMIUM=0.05` (gas)
  (`sim/forward_curve.py:101-103`). `sqrt(tenor_years) ≥ 0` always, so this term can only ever
  **add** a non-negative premium as tenor lengthens — it structurally cannot produce backwardation
  (near-dated priced above far-dated) on its own.
- `seasonal_shape()` (`sim/forward_curve.py:126-135`) averages a **static** monthly-multiplier table
  (`MONTH_SEASONAL_MULTIPLIER` / `GAS_MONTH_SEASONAL_MULTIPLIER`, `sim/forward_curve.py:69-88`,
  loaded once from `sim/data/seasonal_calibration.json` or a hardcoded fallback) — the same
  winter-high/summer-low shape every calendar year, in every scenario. It never inverts either.
- The function returns **one float** for a given `(acquisition_date, contract_length_months, fuel)`
  — there is no multi-tenor curve object, no set of independently-priced points.
- This module is SIM-internal. The company does not call it directly (that would be a wall
  breach); it is cross-checked here only to establish that even the ground-truth generator has
  no term-structure-inversion machinery today, so B4 is not "wire up an existing inverting curve",
  it is "build the inversion mechanism, then the ladder on top of it."

### 1b. The COMPANY-side pricer already has a genuine, wall-safe contango/backwardation slope — but it is one scalar slope on one point estimate, not a ladder

`company/pricing/tariff_engine.py:87-96` (`_estimate_term_structure_slope`, defined
`:137-182`) computes an **observable-only** slope: short-EWMA(30d) vs long-EWMA(90d) of the
company's own spot price history, capped `[TERM_SLOPE_FLOOR=-0.08, TERM_SLOPE_CAP=0.15]`/year
(`:94-95`). Positive slope = contango, negative = backwardation — genuinely derived from state
(not scripted), and it **can and does invert** sign as the observed short/long EWMA ratio moves.
Applied at `:349-355`:

```python
slope = _estimate_term_structure_slope(delivery_date, price_records)
tenor_years = term_months / 12.0
dynamic_slope_premium = slope * tenor_years
return base * (1.0 + risk_premium + structural_term_premium + dynamic_slope_premium)
```

This is wired live: `company/interfaces/sim_interface.py:320-322`
(`SimInterface.get_forward_price` → `CompanyTariffEngine.get_forward_price`,
defined `company/pricing/tariff_engine.py:269`). So **term-structure inversion is already
representable and already live** — but only as a single continuous slope parameter applied to
one point estimate for one requested tenor at a time, computed on demand. There is no object
that holds "Summer-26, Winter-26, Q1-27, month-ahead" as five simultaneously-observable,
independently-priced instruments whose relative order could cross (e.g. Q1-27 < Winter-26 while
month-ahead > both). B4's "moving term structure across NAMED products" does not exist; a
"moving slope on an anonymous single tenor" does.

### 1c. Three separate tenor-taxonomy enums already exist as unwired shelf-ware — duplicated, never instantiated in production

Three independent enumerations of "named tenor buckets" already live in the tree, each with its
own dataclass and its own unit tests, and **none is instantiated anywhere outside its own test
file** (`grep -rln "HedgingSchedule(\|GasForwardCurve(\|ForwardCurveConfidenceBand(\|WholesalePriceMonitor("`
over `company/`, `saas/`, `sim/`, minus the defining modules themselves, returns only
`company/market/ppa_book.py` referencing `hedging_schedule.py`'s types — no production
`run_*` script constructs any of these):

- `company/market/hedging_schedule.py:10-14` — `HedgeTenor`: `MONTH_AHEAD, QUARTER_AHEAD,
  SEASON_AHEAD, YEAR_AHEAD` (4 buckets). `HedgingSchedule.add_contract()` (`:87-101`) takes a
  **caller-supplied literal price** per contract (see `tests/company/market/test_hedging_schedule.py:18-19`,
  `150.0`/`80.0` hand-fed) — it is a hedge-vs-forecast BOOKKEEPING ledger, not a price generator.
- `company/trading/gas_forward_curve.py:29-37` — `GasTenorBand`: `DAY_AHEAD,
  BALANCE_OF_MONTH, FRONT_MONTH, SUMMER, WINTER, CAL_PLUS_1, CAL_PLUS_2` (7 buckets), each with a
  hand-calibrated `_GAS_CONFIDENCE_INTERVAL_PCT` (`:39-47`). `GasForwardCurve.add_point()`
  (`:93-95`) again takes a caller-supplied `mid_price_pence_per_therm` — no generator produces
  the 7 points from one market state; `winter_summer_spread()` (`:109-114`) can only report
  whatever spread the caller happened to feed in.
- `company/trading/forward_curve_confidence.py:31-36` — `TenorBand`: `FRONT_MONTH,
  NEAR_QUARTER, FAR_QUARTER, NEAR_SEASONAL, FAR_SEASONAL` (5 buckets), each with a hand-calibrated
  `_CONFIDENCE_INTERVAL_PCT` (`:40-46`) — a THIRD, differently-named tenor taxonomy over
  materially the same delivery-horizon concept as `GasTenorBand`.

These three enums do not agree on names or bucket counts for what is conceptually the same
axis (delivery horizon), and none is fed by a term-structure generator. This is the
"named product" *vocabulary* already invented three times independently and shelved; B4 should
retire/consolidate into ONE taxonomy plus a real generator behind it, not add a fourth.

### 1d. The company's hedge book trades ONE scalar per customer term, never a named product

`company/trading/forward_book.py:26-67` (`ForwardContract`) and `TradingBook.open_hedge()`
(`:184-187`) record exactly one `agreed_price_gbp_per_mwh` for the whole customer term
(`term_start`→`term_end`), sourced from the single-scalar `CompanyTariffEngine.get_forward_price`
call at signing. There is no notion of the company buying "the Winter-26 block" vs "the Q1-27
strip" as separate instruments — confirming the atom's stated gap ("the company hedges in named
products, not in an abstraction") is real and unbuilt: today it hedges in exactly one
abstraction (a single blended forward number) per term.

### 1e. A wall-safe, non-scripted state substrate for generating inversion already exists one layer over, from the sibling atom SPINE_1/B2

`sim/scenario/spine.py:69` — `PATH_FIELDS = ("gas_trend", "economy_factor",
"renewables_buildout", "storage_capacity")`; `sim/scenario/spine.py:122` `ScenarioSpine` is an
immutable, versioned, ratification-gated exogenous-path object (module docstring `:9-45`,
wall enforced by `tests/sim/test_scenario_spine.py::test_wall`). `storage_capacity` in
particular is exactly the real-world driver of genuine gas term-structure inversion (a
storage-squeeze year prices near-dated gas ABOVE far-dated, the reverse of the normal winter
premium — cf. `docs/design/SPINE_3_GAS_STORAGE_CRISIS_FRAME.md`, cited in the map's B2/SPINE_3
simplifications at `docs/design/maturity_map.yaml:2635`). **B4 should not invent its own
state-to-inversion driver; it should consume `ScenarioSpine.paths_as_of()`'s `storage_capacity`
and `gas_trend` on the SIM side of the wall to derive per-tenor price relationships that can
cross, exactly the way B2/SPINE_3 already derives crisis pricing from the same substrate** — this
gives inversion "generated from state" for free instead of a second parallel mechanism.

## 2. Where the epistemic wall sits for this atom

A real UK supplier's trading desk sees a **live broker/exchange screen**: named, quoted,
simultaneously-tradable instruments (Day-Ahead, Balance-of-Month, front Month, Summer/Winter
seasons, Q1–Q4, Cal+1/Cal+2), each with its own bid/offer and its own liquidity — it does NOT
see the fundamentals (storage levels, generation stack, weather forecast) that cause those quotes
to relate to each other the way they do. That is exactly the SIM/company seam already enforced
for gas storage (§1e): the SIM may compute tenor prices FROM `storage_capacity`/`gas_trend`, but
`company/**` may only ever receive the resulting **named-product price points**, through
`company/interfaces/sim_interface.py`, never the exogenous driver itself.

- **Wall-safe (build this):** a SIM-side ladder generator (e.g. `sim/product_ladder.py`, per the
  atom's declared `file_scope`) that reads `ScenarioSpine` paths and spot history and emits N
  independently-priced, named tenor points (Day-Ahead, front-Month, current Season, next 4
  Quarters, Cal+1) for a given `as_of` date; a company-side seam method
  (`SimInterface.get_product_ladder(fuel, as_of_date) -> list[LadderPoint]`, additive, alongside
  the existing scalar `get_forward_price`, which stays for backward compatibility) that exposes
  only the priced points, never `storage_capacity`/`gas_trend` themselves; a company-side reader
  that picks named products to hedge against (replacing the single scalar handed to
  `TradingBook.open_hedge`).
- **Wall breach (do not build):** any company-layer code importing `sim.scenario.spine`,
  reading `storage_capacity` directly, or a ladder generator that takes the CURRENT calendar
  month as an implicit "which regime am I in" signal the way `sim/scenario/gas_scenario_generator.py`
  already fails to consult the month at all (a documented sibling defect, not this atom's to fix,
  but a reminder that "reads the date" ≠ "reads the fundamentals" and is the wrong failure mode
  to introduce here too).

## 3. The COUPLED TRIAD gap

- **SIM depth added:** a genuinely invertible multi-tenor curve, driven by `ScenarioSpine`
  exogenous state (storage squeeze → near-dated gas priced above far-dated; a calm year →
  normal winter-premium contango), rather than the current always-non-negative, always-same-shape
  scalar in `sim/forward_curve.py`.
- **COMPANY copes through the wall:** the company observes only the named quoted points (per
  §2) and must infer which regime it is in and how much of its hedge book to place in which
  tenor — exactly as today's `_estimate_term_structure_slope` infers contango/backwardation from
  spot EWMA ratios (§1b) without ever seeing the SIM's true state. The company is allowed to
  misread the ladder (e.g. keep buying the historically-cheaper far tenor during an inversion it
  hasn't yet detected) — that misreading IS the interesting behaviour, not a bug to suppress.
- **HARNESS measures the gap:** compare the company's realised hedge cost against a same-period
  "perfect-foresight" cost computed from the SIM's true ladder (the same shape as B5's shaped-cost
  benchmark, which explicitly depends on B4 — `docs/design/maturity_map.yaml:2725`
  `depends_on: [B4_traded_product_ladder]`). A widening gap during a scripted-storage-squeeze
  scenario, closing again once enough history has accrued for the company's own slope estimator
  to pick up the inversion, is the observable proof the coupled triad asks for.

## 4. Tenor taxonomy proposed

Consolidate the three existing shelved enums (§1c) into ONE taxonomy, used by both fuels
(a gas-only 7-bucket taxonomy and an electricity-only 4/5-bucket taxonomy is exactly the kind of
fuel-hardcoding the portability constraints forbid, §6):

| Bucket | Horizon | Existing analogue reused |
|---|---|---|
| `DAY_AHEAD` | next delivery day | `GasTenorBand.DAY_AHEAD` |
| `MONTH_AHEAD` (balance-of-month folds into this near the roll) | 0–1 month | `HedgeTenor.MONTH_AHEAD` / `GasTenorBand.FRONT_MONTH` |
| `QUARTER` (Q1–Q4, calendar-quarter, named e.g. `Q1-27`) | 1–12 months | `HedgeTenor.QUARTER_AHEAD` |
| `SEASON` (Summer Apr–Sep / Winter Oct–Mar, named e.g. `WINTER-26`) | 1–24 months | `GasTenorBand.SUMMER`/`WINTER`, `HedgeTenor.SEASON_AHEAD` |
| `CAL_YEAR` (`CAL-27`, `CAL-28`) | 12+ months | `GasTenorBand.CAL_PLUS_1`/`CAL_PLUS_2`, `HedgeTenor.YEAR_AHEAD` |

Minimum 5 buckets satisfies BACKLOG B4's own DoD ("≥4 tenor buckets priced with a term
structure that can invert", `docs/design/maturity_map.yaml:2710`).

## 5. Generating inversion without scripting it (NEVER_ASK_WITHOUT_RECOMMENDING: generate from state)

Do **not** add a date-keyed or scenario-keyed "if crisis then invert" branch (that is the
unfalsifiable scripted-path failure mode the rule forbids, and it is exactly the trap
`sim/scenario/curriculum/crisis_2021_22.yaml` fell into as an inert, unconsumed hardcoded
trajectory — §1e). Instead:

1. Each tenor point's base price = `spot_ewma × seasonal_shape(tenor window)` (reuse
   `sim/forward_curve.py`'s existing EWMA/seasonal machinery, §1a — do not reinvent it).
2. A single **storage-driven near/far adjustment**, continuous in `storage_capacity` (from
   `ScenarioSpine.paths_as_of()`, §1e): below-normal storage capacity lifts near-dated tenors
   (Day-Ahead, Month, near Quarter) relative to far tenors (Cal+1/+2) monotonically as capacity
   falls — the same mechanism shape as `_estimate_term_structure_slope`'s EWMA-ratio slope
   (§1b), just keyed to the SIM's true storage state instead of the company's inferred spot
   trend. At `storage_capacity` = historical-normal, the adjustment is ~0 and the curve reduces
   to the existing seasonal contango; as capacity falls, the adjustment can flip enough tenor
   pairs to genuinely invert the ordering. No branch, no named year, no "if 2021"; the sign and
   magnitude fall out of the state variable in every scenario, replayed-history included (where
   `storage_capacity` should reproduce the real 2021/22 squeeze from ratified curriculum data,
   not a hand-authored override).
3. Falsifiability test: feed the generator two different `ScenarioSpine` worlds (one with a
   deep storage squeeze, one calm) and assert the SIGN of at least one tenor-pair ordering
   differs between them, driven only by `storage_capacity`/`gas_trend` — if the test author has
   to also change a date or add a special-case to make it invert, the mechanism is scripted, not
   generated, and the exit test should fail exactly that mutation (R15).

## 6. R13 baseline-vs-curriculum split

- **Baseline (fidelity-to-reality, decided blind to company P&L):** which named tenors trade
  in the real GB power/gas markets (Day-Ahead/BoM/Month/Season/Cal, per NBP/N2EX convention,
  §1c/§4); that gas has a steeper structural winter premium than power (already true in
  `sim/forward_curve.py:78-88` vs `:64-76`); that storage-driven near/far inversion is a real,
  observed UK gas-market phenomenon (2021/22, 2018 "Beast from the East") — none of this changes
  because a company P&L looks good or bad.
- **Curriculum (director's, named and versioned):** WHICH scenarios' `storage_capacity`/`gas_trend`
  paths the company actually lives through, and how often/severely a run samples a
  storage-squeeze world vs a calm one — this is `ScenarioSpine`'s existing ratification gate
  (`sim/scenario/spine.py:100-104` `ScenarioNotRatified`), not a new gate B4 needs to invent.
  B4 must not silently tune the near/far adjustment's magnitude to make company margins look
  more or less realistic (R12 anti-goal-seek) — the adjustment's calibration is a baseline/fidelity
  question (does it match the real 2021/22 NBP curve shape?), never a curriculum-difficulty dial.

## 7. Portability constraints that bite

- **Product-as-first-class (no second billing engine):** the ladder's tenor taxonomy (§4) must
  be a plain enum/value object keyed by delivery-window shape, not by fuel — gas and electricity
  should share ONE taxonomy (unlike today's fuel-duplicated `GasTenorBand`/`HedgeTenor`/`TenorBand`,
  §1c) so a second product (e.g. hydrogen, or a capacity-market product) fits the same ladder
  shape without a new engine.
- **No hardcoded settlement granularity:** `DAY_AHEAD` must not assume a UK half-hourly
  settlement period structure — keep it a calendar-day-ahead delivery window, deriving from
  whatever the market's settlement unit is, not from Elexon SP conventions baked into the type.
- **No counterparty hardcoding:** the ladder is priced instruments, not counterparties — keep it
  decoupled from `company/trading/forward_book.py`'s counterparty-attribution machinery (§1d's
  `assign_default_counterparty`), which should attribute a counterparty to a LADDER TRADE the
  same way it does today to a term hedge, unchanged.
- **C-S2 (deterministic replay):** the ladder generator must draw any stochastic element (if any)
  from its own named RNG substream, never reuse another subsystem's, per the standing scale
  constraint.

## 8. Exit test for level 3 (BACKLOG B4 DoD, `docs/design/maturity_map.yaml:2710`)

1. `sim/product_ladder.py` generates ≥5 simultaneously-priced, independently-observable named
   tenor points (§4) for a given `(fuel, as_of_date)` from `ScenarioSpine` + spot history alone.
2. A test asserts genuine invertibility: across ≥2 `ScenarioSpine` worlds differing only in
   `storage_capacity`, at least one tenor-pair's relative ordering (e.g. Month-ahead vs Cal+1)
   flips sign — driven by state, not a branch (§5.3, R15 mutation-testable: deleting the
   storage-capacity read should make the test fail).
3. A test asserts the ladder moves **independently of a single spot tick** — i.e. bumping one
   day's spot price alone must not move every tenor point by the same proportion (rules out a
   "curve = spot × constant per tenor" degenerate implementation masquerading as a ladder).
4. `company/interfaces/sim_interface.py` gains an additive `get_product_ladder` (or equivalent)
   method returning only named price points (no `storage_capacity`/`gas_trend`); a wall test
   (matching the existing `tests/sim/test_scenario_spine.py::test_wall` pattern) asserts no
   `company/**`/`saas/**` module imports `sim.scenario.spine` as a result of this change.
5. `company/trading/forward_book.py`'s `ForwardContract`/`TradingBook.open_hedge` (or a
   successor) records which NAMED product a hedge was placed in, not only a blended scalar
   price — i.e. a real consumer of the ladder exists, not just a generator with no reader
   (avoiding the exact shelf-ware failure mode documented in §1c for the three existing enums).
6. The three duplicate tenor enums (§1c) are consolidated or explicitly retired in favour of the
   one taxonomy (§4), closing the duplication rather than adding a fourth.

## 9. Recommended build shape (proceeding per PROCEED_BY_DEFAULT — reversible, no one-way door)

Build in this order, each step independently mergeable:

1. **SIM-side generator** (`sim/product_ladder.py`): pure function(s) taking `ScenarioSpine`
   paths-as-of + spot/gas price history, emitting the named ladder (§4/§5). Reuses
   `sim/forward_curve.py`'s EWMA/seasonal helpers rather than re-deriving them. This alone is
   testable and gives the invertibility exit test (§8.1-3) without touching the wall.
2. **Wall seam**: additive `get_product_ladder` on `SimInterface`/`StubSimInterface`/the real
   implementation (`company/interfaces/sim_interface.py`), mirroring the existing
   `get_forward_price` triple-implementation pattern at `:41,164,320`. Existing scalar
   `get_forward_price` stays untouched (backward-compatible, C-S1/idempotent).
3. **Company-side consumer**: extend `company/trading/forward_book.py`'s `ForwardContract` (or
   add a sibling type) to record a chosen named product per hedge, sourced from the new seam,
   feeding `TradingBook.open_hedge`. This is the step that makes B5 (shaped-cost benchmark)
   buildable, since B5 `depends_on: [B4_traded_product_ladder]`.
4. **Consolidate the three shelved enums** (§1c/§8.6) into the §4 taxonomy — a mechanical
   refactor once step 1-3 exist, not before (retrofit-on-touch, not speculative).

Recommend starting step 1 as the next BUILD atom for `B4_traded_product_ladder` once
BUILD-open for epoch 3 — it is the highest-leverage, most reversible slice (pure functions, no
wall surface, no existing caller to break) and unblocks the invertibility exit test standalone.
