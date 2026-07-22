# The wholesale value chain — products, shaped cost, and where trading value is created (FRAME)

**Source:** `docs/staging/DIRECTOR_STEER_WHOLESALE_VALUE_CHAIN_2026-07-22.md` (advisor carrying the
director's Epoch-2 correction). **Type:** [STEER] — DISCOVER→FRAME first, *mechanism mine*, the
construct in the steer is the **wall**. Tagged **contract-touching — propose-then-proceed, 2h veto**.

**Status:** DISCOVER→FRAME, **doc-only**. Provenance: **proposal**. Writes **no** `sim/`/`company/`/
`harness/` code, edits **neither** `maturity_map.yaml` **nor** any engine, claims **no** level, touches
only `docs/design/`. Candidate atoms below are *named*, not registered (orchestrator is sole map writer
per THREE_LANES until `H9`). No network this session — every external market fact is flagged
**`[recall — verify at BUILD]`**; repo anchors are quoted from files read this session; **no figure
fabricated** (Historical Ground Truth).

**Relationship to prior work (consolidates + extends, does NOT fork):**
- `docs/design/THE_VALUE_CYCLE_FRAMING.md` — the ratified Epoch-2 spine (bitemporal log + as-of
  interfaces; C3 "pricing organ meets late truth"; ex-ante cost stack + ex-post margin bridge). This
  FRAME is the **wholesale/trading limb** of that spine, not a new epoch.
- `docs/design/EPOCH2_BC_PRICE_FORMATION_AND_SUPPLIER_COST_DISCOVER.md` — owns **price-as-emergent-output**
  (BC-1) and **cost-lags-spot-via-the-hedge-book / WAPP** (BC-2), and the **volume×price joint-tail**
  hypothesis (BC-3). This FRAME **inherits all three invariants unchanged** and adds the four constructs
  BC does *not* own end-to-end: the **shaped-cost benchmark**, the **product ladder with moving term
  structure**, the **cover fan + value-add ledger (achieved vs benchmark)**, and **tariffs derived from
  the stack**.
- `docs/staging/ADVISOR_DISCOVERY_WHOLESALE_ANCHORS_2026-07-22.md` — **companion sourced-evidence**
  doc (advisor web research). Folded into §3/§8 below as **`[advisor-sourced — verify vs primary at
  BUILD]`** candidates (R9: verify, do not inherit); a **board blind-spec** of a competent GB trading
  function is incoming — reconcile all three (board / this evidence / primary-source DISCOVER) at BUILD,
  disagreements are findings.
- `docs/design/W1_6_PHYSICS_PRICE_SIGNAL_DISCOVER.md` — the merit-order price engine audit and its
  **~10× SSP miscalibration** in raw-ratio form; production runs use **real historical SSP**, the
  generative engine is gated off. Inherited as the hard upstream on any *generated* curve (§8).

---

## 1. What the steer adds — the gap between "we have hedging" and "we have a trading organ"

The director's verdict: *"We still have really simplistic wholesale products. Really just a day or spot,
with a largely static view of contango vs backwardation… The data needs to drive the actions we know are
done to create value. I'm not convinced what we have does that."*

He is right, and the repo confirms it precisely. The machinery is **broad but flat**: there is a hedge
*fraction* decision (`sim/hedging_strategy.py`, floor 0.85), a WAPP report
(`company/trading/wholesale_position_report.py`), a forward *point*-pricer
(`sim/forward_curve.py::generate_forward_price` = EWMA(30d) spot × seasonal shape × (1+term_premium)),
a shape-risk book, a NOP register, an imbalance charge register. What is **missing** is the thing that
turns those into a *value-creating desk*:

1. **No benchmark to trade against.** There is no annualised shaped energy cost — the number every real
   supply desk is measured against and that the price-cap wholesale allowance is built from. Without it,
   "did trading add or destroy value?" has no denominator.
2. **No product ladder.** Hedging collapses to a **single term-start `hedge_price`** (`sim/hedging.py`;
   BC §2.3 fidelity note). The company forward (`company/pricing/tariff_engine.py::get_forward_price`,
   `COMPANY_LOOKBACK_DAYS=120`) is *richer than the "trailing mean" label* — it already carries a
   regime premium and a **dynamic contango/backwardation slope** (`:340-353`). But it is **one blended
   forward number**, not a **ladder of distinct products** (Winter/Summer baseload, quarters, months,
   day-ahead) each with its **own price that moves**. Those product concepts *do* exist — but as three
   **disjoint silos** never composed: `GasTenorBand` (`gas_forward_curve.py`, gas-only), `ShapeBand`
   (`shape_risk_book.py`, baseload/peak/off-peak), `HedgeTenor` (`hedging_schedule.py`,
   month/quarter/season/year-ahead). The director's "largely static contango" is right *at the book
   level*: there is no single product ladder whose per-product term structure moves coherently.
3. **No cover fan.** Cover % accrues, product by product and horizon by horizon, over time as the book is
   built — the classic hedging "fan". Today there is a scalar hedge fraction, not a fan.
4. **No value-add ledger.** Achieved cost vs the shaped benchmark — decomposed into what the desk *did*
   (locked early / rolled / left open) — is the trading P&L attribution. It does not exist.
5. **Tariffs are asserted beside the cost, not derived from it.** `company/pricing/ofgem_price_cap.py`
   is a **static annual cap table**; `tariff_engine.py` exists but no visible cost *stack* (shaped
   wholesale + network + policy + operating + margin) drives the quoted retail price.

The construct below is the director's, and it is the wall. The mechanism is mine.

## 2. Repo grounding — extend these, do not fork them

| Construct the steer needs | Already exists? | Anchor (verified this session) | Verdict |
|---|---|---|---|
| Within-day × seasonal demand shape | Yes | `sim/profile_class_1.py::load_pc1_shape` (48 HH values from real published GAD, season/day-type) | **The shape input to the benchmark.** Reuse. |
| Premise/weather demand | Yes | `sim/weather_demand_chain.py` | Feeds annual volume/shape. |
| Company demand estimate (EAC) | Yes | `company/trading/hedge_decision.py` (`eac_kwh` input, company-observable) | The volume the benchmark is priced for. |
| Seasonal + within-day shape (uncomposed) | Yes, silos | `company/market/seasonal_demand.py` (monthly), `load_forecast.py` (quarterly) + `sim/profile_class_{1,3}.py` (HH GAD) | **Compose** into a book-level annual shape — new. |
| Company forward (the "120-day" curve) | Yes, blended | `company/pricing/tariff_engine.py::get_forward_price` (`:269-355`, EWMA-120 + regime premium + **dynamic contango slope** `:349-353`) | **Decompose** the one blended number into a **product ladder** — new. |
| SIM-truth forward curve | Yes | `sim/forward_curve.py::generate_forward_price` (spot_ewma×seasonal×(1+sqrt-tenor premium)) | The ground-truth curve; basis gap to company curve is the point. |
| Product silos to unify | Yes, disjoint | `GasTenorBand` (`gas_forward_curve.py`), `ShapeBand` (`shape_risk_book.py`), `HedgeTenor` (`hedging_schedule.py`) | **Unify into one product abstraction** — new. |
| Term-structure confidence bands | Yes | `company/trading/forward_curve_confidence.py` (front tight → back wide) | Scaffold for per-product uncertainty. |
| Hedge decision (VaR-constrained) | Yes | `company/trading/hedge_decision.py` (VaR 95%, bid-ask by tenor) | **The buyer** in the loop. Extend to buy *products*. |
| Hedge schedule (forward delivery by month) | Yes | `company/market/hedging_schedule.py` (`ForwardContractDelivery`, `HedgeTenor`) | **Cover-ledger scaffold** — extend into the fan. |
| Blended cost (SIM truth) | Yes, single-fixing | `sim/hedging.py::settle_hedged_period` (`hedged·hedge_price + unhedged·spot`) | Enrich to laddered WAPP (BC §6.3). |
| WAPP / observed cost (company belief) | Yes | `company/trading/wholesale_position_report.py` (`wapp_gbp_per_mwh`, MtM, NOP, RAG) | The company's *believed* cost — one side of the gap. |
| Cover-the-short detection | Yes | `company/trading/power_auction_monitor.py` + `net_open_position_register.py` | The **cover-fan** driver. Extend. |
| Shape risk (peak/base) | Yes | `company/trading/shape_risk_book.py` (short/long-peak, shape P&L) | **The peak/base desk-pack surface.** Reuse. |
| Imbalance / cash-out on residual | Yes, spread-form | `company/market/imbalance.py` (SSP·(1+premium), stress 1.2; a spread-over-spot, not a true SIP engine) | The **residual leg** of the loop. |
| Cost stack (wholesale+network+policy+operating) | **Yes** | `company/pricing/cost_to_serve.py::CostToServeBreakdown` (`:36-98`); margin added in `tariff_engine.py` (target 8%) | **The stack largely exists** — wire the *shaped* wholesale line + surface margin (§3.4). |
| Published price cap | Coarse | `company/pricing/ofgem_price_cap.py` (static annual £/MWh table) | Keep as an *observable* the company prices under; build own shaped allowance (§3.1/§8.1). |

**One-line reading (honest about extend vs unify):** the *cost/hedge/price* engines (both forward
curves, the VaR hedge decision, the cost stack, W1_6) are genuinely built and are **extended**, not
forked. The *product ladder* and the *book-level annual shape* exist only as **disjoint silos**
(`GasTenorBand`/`ShapeBand`/`HedgeTenor`; monthly/quarterly/HH shape) and are honestly **unified /
composed**, not "extended from one thing." The build adds two things on top: a **term dimension** (one
product abstraction across the ladder) and a **benchmark** (the shaped cost) to score against. Consistent
with THE_VALUE_CYCLE_FRAMING §3 ("extend, don't rebuild").

## 3. The design (the director's five, made mechanistic)

### 3.1 The shaped-cost benchmark — the spine

**Definition.** For a residential book: take the annual demand shape (`load_pc1_shape` seasonal ×
within-day, scaled to book EAC), price that shape half-hour by half-hour against the **wholesale curve as
of a pricing date**, and get the **annual shaped energy cost — £/customer and £/MWh-shaped**. This is the
standard supply-desk view and, structurally, how the **price-cap wholesale allowance** is built.
**`[advisor-sourced 2026-07-22 — verify vs primary at BUILD]`** the Ofgem cap wholesale allowance uses a
**3-month observation window, 1.5-month notice lag, 12-month forward view** (quarterly cap periods; was
**6-2-12**, semi-annual, pre-2022 — the methodology change is itself a fidelity event), and Ofgem's MHHS
technical paper **diagrams demand shaped from peak + baseload contracts to a half-hourly profile** —
literally this construct, regulator-drawn. The cap index's stated simplification (it assumes suppliers
buy only *quarterly* products, whereas real suppliers trade seasonal + quarterly) means the SIM models
the *real* behaviour and can **score the cap-index as a benchmark belief** against achieved cost.

**Why it is the spine.** It is the **denominator for everything downstream**: the tariff cost stack
(§3.4) starts from it; the trading value-add ledger (§3.3) is *achieved cost minus this benchmark*; the
hedge program (§3.3) exists to *lock this number in* against forecast volume. The director's line —
**"everything the trading function buys must roughly add up to this number"** — is the benchmark's
operational meaning and BC-4's test (§6).

**Mechanism (proposed, mine).** A pure function `shaped_annual_cost(demand_shape, curve, as_of) →
{gbp_per_customer, gbp_per_mwh_shaped, by_season, by_product_bucket}`. It is **as-of-bound** (uses only
the curve knowable at `as_of` — Point-in-Time Blindfold; it consumes the same as-of interface the
bitemporal spine provides). It is **derived, never stored as a target** (R12 — a diagnostic, not a goal).

### 3.2 The product ladder + moving term structure

**Products (the ladder).** Seasonal baseload (Winter-N / Summer-N), quarters (Q1–Q4), months (prompt +
forward months), day-ahead — one **unified product abstraction** that subsumes today's three disjoint
silos (`GasTenorBand`, `ShapeBand`, `HedgeTenor`). Each product is a distinct instrument with its own
price series and its own liquidity/spread. Peak vs base as a shape dimension is `shape_risk_book.py`'s
`ShapeBand`, lifted into the shared abstraction rather than left gas-tenor/hedge-tenor-parallel.

**`[advisor-sourced 2026-07-22 — verify vs primary at BUILD]` conventions to build to:** Winter = Oct–Mar,
Summer = Apr–Sep; **baseload** = continuous 23:00–23:00 equal each hour (ICE UK Base spec); **peak** =
07:00–19:00 London weekdays (EFA blocks 3–5), off-peak = the rest; EFA day = six 4-hour blocks from
23:00. ICE lists consecutive months (up to ~156), quarters, seasons, calendars, **registrable as strips**
across any consecutive run → so the SIM product set is *seasonal base + peak, quarters, months, DA*, with
months/quarters/seasons **rollable into strips**. Venues by horizon: forwards/futures (ICE + bilateral
OTC) → **day-ahead single-price auction (N2EX/EPEX — the most-quoted GB signal)** → continuous intraday to
gate-closure T-1h → balancing at the **single imbalance price (SSP=SBP**, which our settlement record
already shows correctly).

**Moving term structure.** The company forward (`tariff_engine.py`) *already* moves at the **book** level
(regime premium + dynamic contango slope, `:340-353`) — but it is one blended number, so contango cannot
move *differently per product*. BUILD gives each product on the ladder its own **term-structure state**
that *shifts* with regime: contango in calm/well-supplied conditions, backwardation into a
tight-winter/low-storage/crisis regime, and the *shape of the whole curve* re-forms — not a single slope
knob. **`[advisor-sourced 2026-07-22 — verify vs primary]`** this is not invented: the cap methodology
itself carries an **ex-ante backwardation allowance** — constructed by comparing the index-approach cost
against a nominal supplier buying only in-season — i.e. a *published, dynamic* contango/backwardation
mechanism, the direct answer to the director's "largely static view of contango vs backwardation." This
is **inherited, not invented**: prices move because the *underlying drivers* move (BC-1 —
price is an emergent output of fuel + residual demand; the ladder is the multi-tenor projection of that),
never a hand-drawn shape. `forward_curve_confidence.py`'s front-tight→back-wide bands are the scaffold
for per-product widening uncertainty out the curve.

**Wall discipline.** SIM owns the *true* forward outturn per product; the company observes only the
**published curve it can transact at** and builds its ladder belief from that. The naive **120-day
trailing view** the steer names is the company's **starting** belief (§3.5) — the thing trading
experience must *improve*, measured as a gap.

**Portability (C-S / PORTABILITY):** products keyed by *function* (season/quarter/month/DA), not by GB
product codes; "gas sets the margin" generalises to "the marginal fuel sets the margin"; product is
first-class wherever fuel is one (power **and** gas ladders — `gas_forward_curve.py` already present).

### 3.3 The value-creation loop, as scoreable activities

This is the director's construct 3, made into a measured loop. Each arrow is an *activity* that creates
or destroys value, and the loop closes on the §3.1 benchmark.

```
  book demand FORECAST  ──►  HEDGE PROGRAM buys PRODUCTS across the ladder over time
  (EAC × shape, §3.1)         (hedge_decision.py extended: which product, which tenor, how much, when)
        │                                     │
        │                                     ▼
        │                         COVER % by product & horizon, accruing over time  =  THE FAN
        │                         (power_auction_monitor "cover the short" → a cover ledger)
        ▼                                     │
  realised metered volume  ──►  RESIDUAL = realised − covered  settles at the single IMBALANCE price
  (weather-driven)              (company/market/imbalance.py — SSP·(1+premium), stress 1.2)
                                              │
                                              ▼
     ACHIEVED wholesale cost  =  Σ(covered_p · struck_price_p)  +  residual · cash-out
                                              │
                                              ▼
     TRADING VALUE-ADD LEDGER  =  ACHIEVED cost  −  SHAPED BENCHMARK (§3.1)
       decomposed into: timing (locked early vs curve) | shape (peak/base vs flat) |
       volume/forecast error (the residual leg) | roll (rolled vs held)
```

**Weather drives demand; balancing closes out.** This is exactly BC §3's volume×price joint tail —
the cover fan is *how much of that tail the desk pre-empted*. A well-run desk shrinks the residual leg
into the winter tail; a poorly-run one is short into the spike. **The gap is the score** (COUPLED_TRIAD):
SIM knows the true achieved cost; the company believes its WAPP-based cost; the belief-vs-truth gap in
the joint tail is the deliverable.

**New primitives (proposed, mine, all extensions):**
- **Cover ledger** — cover % by (product, horizon) over pricing time; the fan is its time-series. Extends
  `power_auction_monitor.py` + `net_open_position_register.py`.
- **Value-add ledger** — achieved − benchmark, attributed to timing/shape/volume/roll. New register
  (`company/trading/`), computed from the *independent* struck-price ledger + realised volume + observed
  cash-out (tautology guard, §6), never from a stored expected-cost.

### 3.4 Tariffs derive from the stack

**Fixed tariffs lock the shaped forward cost at acquisition** (§3.1 priced as-of the sign date) **plus
network + policy + operating + margin.** **Variable/SVT reprices cap-methodology-like** (a lagged
wholesale index; the cap itself is a trailing wholesale average `[recall — verify at BUILD]`). The retail
price is then **driven by** the data, not asserted beside it. **The stack largely exists already:**
`company/pricing/cost_to_serve.py::CostToServeBreakdown` already carries wholesale + network + policy +
operating lines (margin is added downstream in `tariff_engine.py`, target ~8%). The gap is that its
**wholesale line is not the §3.1 shaped cost**, and the full stack is not surfaced as *the* driver of the
quoted tariff. `WVC_5` wires the shaped cost into `cost_to_serve`'s wholesale line and surfaces the whole
stack (incl. the separately-held margin) so tariff = Σ(named lines). The static cap table in
`ofgem_price_cap.py` is kept as a **published-cap observable** the company must price under (a real
supplier does not set the cap), with the constructed stack as its own cost belief — leaning per §8.1,
director/BUILD call. **`[advisor-sourced 2026-07-22 — verify vs primary]`** the wholesale line is not one
number: the cap's own construction adds **shaping, imbalance, transaction-cost** allowances, a **+1%
additional risk allowance**, and the **ex-ante backwardation allowance** (§3.2) on top of the raw shaped
commodity — so `cost_to_serve`'s wholesale line should itself decompose into commodity + these named
uplifts (with a regime-stress precedent: the 2022 £61/customer volatility adjustment), and bid-ask
spreads for base/peak are **non-linear in volatility** (Octopus consultation evidence) — an anchor for
the spread/transaction-cost term, not a flat %.

**Wall discipline (critical — this is contract-touching):** no silent change to *billed history*. Tariff
derivation changes the *forward* pricing logic; already-issued bills are immutable events (bitemporal
spine). A re-derivation lands as a new event, never a rewrite (THE_VALUE_CYCLE_FRAMING C2/C5).

### 3.5 The epistemic wall + the naive estimator as *starting* belief

SIM owns true curves and outturn; the company **forecasts, trades, and is scored on belief-vs-truth**.
Its **120-day** forward estimate (`tariff_engine.py`) is its **starting** belief per the director's
construct — today a *single blended* number (richer than a raw mean, but still one number, not a
per-product ladder belief), and trading experience is what must improve it into a resolved
product-by-product view. This is the coupled-triad framing made concrete for the wholesale organ:
the company's ladder belief, cover decisions, and cost attribution are all *approximations built from
observed outcomes*, and every one of them carries a measurable gap to SIM truth. A company that prices
its fixed book as spot-sensitive (BC-2 violation) or its residual at *average* rather than tail cash-out
(BC-3 violation) carries a gap the harness reports.

## 4. Candidate atoms (named, provenance: proposal — NOT registered this pass)

Proposed for the **`W4_the_wall` / trading** neighbourhood, Epoch-2, DISCOVER/FRAME-workable now,
BUILD-gated on the director opening the front + the 2h veto window. Levels/deps are proposals.

| id (proposed) | title | depends_on | notes |
|---|---|---|---|
| `WVC_1_shaped_cost_benchmark` | Annual shaped energy cost = the desk benchmark (§3.1) | `W1_5_premise_demand_shape`, forward curve | The spine; feeds tariff stack + value-add ledger. |
| `WVC_2_product_ladder` | **Unify** `GasTenorBand`/`ShapeBand`/`HedgeTenor` into one product ladder with **moving** per-product term structure (§3.2) | `WVC_1`, BC-1 (emergent price), W1_6 recal | Unifies the 3 silos; laddered WAPP enriches `sim/hedging.py`. |
| `WVC_3_hedge_program_cover_fan` | Hedge program buys products over time → cover ledger / fan (§3.3) | `WVC_2` | Extends `hedge_decision.py` + `hedging_schedule.py` + `power_auction_monitor.py`. |
| `WVC_4_value_add_ledger` | Achieved − benchmark, attributed timing/shape/volume/roll (§3.3) | `WVC_1`, `WVC_3` | New register; the trading P&L attribution + Proof-door gap row. |
| `WVC_5_tariff_from_stack` | Fixed/variable tariffs derived from the shaped cost stack (§3.4) | `WVC_1` | **Contract-touching** — the propose-then-proceed sub-item; billed history immutable. |

**Coupled-triad:** `WVC_4`'s achieved-vs-belief gap is the wholesale-cost twin of the weather cascade's
imbalance link (BC §6.5) — BUILD registers the pair in `background/coupled_triad.py` and adds a
`coupled_gap_ledger.json` row.

## 5. Desk-pack surfaces — outputs of this organ, NOT cosmetics (the director's believability axes)

Each is a *view of a ledger this organ produces*, and is what the director judges believability on:
1. **Curve evolution** — the ladder over time; contango↔backwardation actually moving (`WVC_2`).
2. **Cover fan** — cover % by product/horizon accreting toward delivery (`WVC_3`).
3. **Fixed/variable book split** — how much of the book is locked vs floating (`WVC_3` + `WVC_5`).
4. **Peak/base** — shape exposure (`shape_risk_book.py` surfaced).
5. **Value-add ledger** — achieved vs shaped benchmark, attributed (`WVC_4`).

Per R6/R11 these are *organ outputs verified to the rendered value on the live site*, never a report
section authored as the primary work.

## 6. Invariants — R10 class-failing, R15-failable (proposed, no code)

Inherits **BC-1/BC-2/BC-3 unchanged**. Adds:

> **INVARIANT WVC-1 (the benchmark closes — "everything bought roughly adds up to this number").** For a
> book at target cover, the **achieved wholesale cost must reconcile to the shaped benchmark within the
> attributed residual/timing/shape terms** — i.e. `benchmark + Σ(value-add attributions) = achieved`, to
> a defined tolerance. A value-add ledger whose terms do **not** sum to (achieved − benchmark) fails: the
> attribution is incomplete or the benchmark is not the real denominator.

> **INVARIANT WVC-2 (the ladder is derived, its term structure moves, and it is Blindfold-clean).** Each
> product's price must be **derivable** from the contemporaneous curve state (BC-1), the term structure
> must **change sign-of-slope** across at least one calm→crisis regime in the record (not a static
> shape), and no product price may read any data dated after its `as_of`. A curve whose contango is
> constant across regimes, or that uses a future print, fails.

> **INVARIANT WVC-3 (tariff = stack; billed history immutable).** A quoted forward tariff must **equal**
> the sum of its named cost-stack lines (shaped wholesale + network + policy + operating + margin) to a
> tolerance — no unexplained residual "asserted" price. Separately, **no tariff re-derivation may mutate
> any already-issued bill event** — a re-price lands as a new event or fails.

**R15 killer mutations (designed, not coded):**
- **WVC-1 killer:** drop one attribution term (e.g. delete the shape leg) → the sum-to-achieved check
  must fire. **FAIL-OPEN guard:** empty book / zero residual / NaN cash-out fails loud, never green.
- **WVC-2 killer:** freeze the term structure to a constant shape across the 2021→2022 regime → the
  moves-across-regime arm must fire. And feed a future print → the Blindfold arm must fire.
- **WVC-3 killer:** add an unexplained £/MWh constant to the tariff not in any stack line → the
  sum-to-stack check must fire. Mutate a historical bill on re-price → the immutability arm must fire.
- **TAUTOLOGY guard:** the value-add ledger recomputes achieved cost from the *independent* struck-price
  ledger + realised volume + observed cash-out — never reads back a stored "expected cost".
- **FAIL-SILENT guard:** if the struck-price ledger or realised-volume series is unavailable, every
  check is a **FAILED** check, never skipped-and-green.

## 7. Reconciliation — extend, don't fork (explicit)

- **vs THE_VALUE_CYCLE_FRAMING:** this is the wholesale limb of C3 ("the pricing organ meets late
  truth"). The shaped benchmark is the *ex-ante* cost; the value-add ledger is the *ex-post* margin
  bridge specialised to the trading desk. Same spine, same as-of interfaces, same bitemporal immutability.
- **vs EPOCH2_BC:** BC-1/BC-2/BC-3 are load-bearing *inputs* here and are **not modified**. This FRAME
  does not touch price formation or the WAPP cost physics — it builds the *benchmark, ladder, fan and
  attribution layer on top* of them.
- **vs W1_6:** now built as `sim/weather_price_chain.py` (L4 residual-demand convex chain,
  `derive_price`/`cold_still_spike`) with a deliberately-naive company twin
  (`company/pricing/weather_price_belief.py`, linear) and a live gap monitor
  (`background/weather_price_triad.py`). The ladder's *generated* prices inherit W1_6's calibration
  status; until the merit-order SSP calibration clears (W1_6 §1.2, ~10× blocker), the ladder is anchored
  to **real historical curves** (the production path today), and the *generated* term structure is a
  BUILD deliverable reported-not-tuned (R12). **No new price engine** — the ladder is a multi-tenor
  *projection layer* over the existing chain, not a competitor to it.
- **No duplication:** `bimodal_generator.py` / `weather_price_sensitivity.py` reconciliation (three
  price-adjustment mechanisms, W1_6 §3) is **not** re-opened here — flagged as inherited (§8).

## 8. Open questions / director calls / what BUILD needs

1. **Cap: replace or observe?** Does the constructed shaped allowance **replace** the static cap table,
   or does the company keep the **published cap as an external observable it must price under** while
   holding its own constructed stack as belief? (Leaning: keep the published cap as observable — a real
   supplier does not set the cap — and derive its own cost stack behind it. Director/BUILD call.)
2. **Laddered WAPP in SIM:** enrich `sim/hedging.py`'s single `hedge_price` to a multi-trade WAPP now
   (adds roll/smoothing + makes "new buying at spike feeds future cost" first-class), or register as a
   named R10 simplification? (BC §6.3 open item — this FRAME needs it for the fan to be real; recommend
   enriching under `WVC_2`.)
3. **Generated-curve blocker (inherited, hard):** the merit-order SSP recalibration (~10× overestimate,
   missing carbon/UK-ETS term, untested residual-demand form — W1_6 §1.2). The ladder rests on **real
   historical curves** until this clears; no generated magnitude is trusted or tuned (R12).
4. **Curriculum vs baseline (R13):** *which* term-structure regimes the company lives through (a
   2018-style price-war contango, a 2021→22 backwardation crisis) is **director-authored curriculum**,
   never agent-tuned toward a value-add number.
5. **Data needed at BUILD:** the companion `ADVISOR_DISCOVERY_WHOLESALE_ANCHORS_2026-07-22.md` already
   sources the product conventions (folded above) and the cap 3-1.5-12 construction, but flags honest
   gaps to close via the discovery-agent against **primary** Ofgem/Elexon/NESO/DESNZ/ICE (R9 — verify,
   don't inherit): actual supplier hedge ladders (proprietary — bound from cap methodology + published
   strategy statements), historical seasonal/quarter forward **marks** (commercial ICIS/Argus/Platts —
   check Ofgem cap annexes for free proxies), N2EX DA history access terms, and NBP/TTF + UK-ETS series.
   The incoming **board blind-spec** of a competent GB trading function is the third leg to reconcile.
   **Fabricate no figure** in the interim.

## 9. Sequence + the gate

**DISCOVER** (this pass + a discovery-agent run at BUILD): real GB curve/product anchors + the annual
shape the book implies (§8.5). **FRAME** (this doc): ladder + benchmark + ledgers, reconciled with
THE_VALUE_CYCLE_FRAMING and W1_6, extending the existing engines. **BUILD** on standing authority **once
the director's 2h veto window on this FRAME lapses without objection** (the steer's explicit gate), in
atom order `WVC_1 → WVC_2 → WVC_3 → WVC_4 → WVC_5`, `WVC_5` (tariff-touching) built last behind the
immutability guard.

**Propose-then-proceed sub-item (parked-file header):** the one genuinely-open, contract-touching
decision is **`WVC_5_tariff_from_stack`** — whether the constructed cost stack *replaces* or *sits behind*
the published cap (§8.1), and confirmation that no billed-history mutation path exists. That is what the
2h veto covers; `WVC_1`–`WVC_4` are extensions of existing trading organs and proceed on standing
authority once framed.

---

*Sources read this session (no network): the staged steer; `docs/design/THE_VALUE_CYCLE_FRAMING.md`,
`W1_6_PHYSICS_PRICE_SIGNAL_DISCOVER.md`, `EPOCH2_BC_PRICE_FORMATION_AND_SUPPLIER_COST_DISCOVER.md`,
`FORWARD_DISCOVERY_REGISTER.md` (full); repo anchors verified: `sim/forward_curve.py` (header/params),
`sim/profile_class_1.py` (shape loader), `company/pricing/ofgem_price_cap.py` (static cap table),
`company/trading/hedge_decision.py` (VaR hedge decision), and the `company/trading/` +
`company/pricing/` inventories. A machinery-mapping pass additionally verified §2/§7 anchors
(`tariff_engine.py::get_forward_price` `:269-355`; the `GasTenorBand`/`ShapeBand`/`HedgeTenor` silos;
`cost_to_serve.py::CostToServeBreakdown`; `sim/weather_price_chain.py` + `weather_price_belief.py` +
`background/weather_price_triad.py`; the `sim_interface.py::get_forward_price` seam and its stubbed
settlement/status neighbours). All external market facts flagged `[recall — verify at BUILD]`; no figure
fabricated. R10/R12/R13/R15, COUPLED_TRIAD, epistemic wall, PORTABILITY/C-S referenced inline.*
