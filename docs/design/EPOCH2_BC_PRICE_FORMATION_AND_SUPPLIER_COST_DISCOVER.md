# Epoch-2 atoms B + C — GB wholesale PRICE FORMATION and supplier ACTUAL COST (DISCOVER pass, doc-only)

**Status:** DISCOVER, doc-only. Provenance: **proposal**. No level claimed. Writes **no** `sim/`/`company/`/`harness/`
code, edits neither `maturity_map.yaml` nor any engine, touches only `docs/design/`. **W1 BUILD stays CLOSED**
(Epoch-3 BUILD-gated per `EPOCH_GATING_AND_ATOM_AUTHORSHIP` Rule 1; this campaign proceeds through DISCOVER/FRAME until
the director opens it). Isolated worktree; no push; one commit.

**Source of task:** `docs/staging/DIRECTOR_CAMPAIGN_EPOCH2_COUPLED_WORLD_2026-07-19.md` requirement 3 ("the market and
cost logic must be DISCOVERED, not handed over"), decomposed as atoms **B** (price formation) and **C** (supplier cost)
in `docs/design/EPOCH2_COUPLED_WORLD_CAMPAIGN_DECOMPOSITION.md`.

**No network this session.** Every external market fact is flagged **`[recall — verify at BUILD]`**, exactly as the
director required (he explicitly does NOT want a sketched causal chain built as physics; Historical Ground Truth forbids
fabricating a specific date/figure in a DISCOVER doc). Structural claims are stated as structure; anywhere a number
would be load-bearing is flagged, not invented. Repo figures below are quoted from code/committed docs read this session.

**Relationship to prior DISCOVER passes (consolidates, does not re-derive).** This doc owns the two things the director
named as *load-bearing for everything downstream* and that no prior doc owns end-to-end: (1) price as an **emergent
output** of the national system, and (2) a supplier's cost as a **weighted average of prior purchases, not the spot
print** — and the P&L geography that follows from (2). It builds directly on:
- `W1_6_PHYSICS_PRICE_SIGNAL_DISCOVER.md` — the merit-order price engine audit + the **~10× SSP miscalibration** of the
  raw-ratio form (inherited here as a hard upstream dependency, §6).
- `W1_COUPLED_WEATHER_CASCADE_DISCOVER.md` — the `weather → demand → gen → residual → price → imbalance → capital`
  cascade and its compounding tail; the hypothesis in §3 is the *company-cost* reading of that cascade's imbalance
  link (F/G).
- `docs/design/WEATHER_PHYSICS_HIERARCHY_DESIGN.md` §1.4 — the authoritative five-equation chain (not re-derived).

---

## 1. How GB wholesale price FORMS — price as an OUTPUT of the national system

The director's correction is the spine of this section: *"National wholesale price is an output at a national level of
global energy prices and weather. Itself driven by industrial and residential demand and interconnection. This drives
the supplier to price for retail products bought now. But otherwise, if fixed prices bought before, the actual price
doesn't change."* Framed and discovered (not taken as a spec) below.

### 1.1 The causal structure — price is emergent, never an input

Read top-down; each arrow is a coupling, not a formula to hardcode. **The load-bearing framing is that the national
wholesale print is the *last thing computed*, not the first — it falls out of supply meeting demand; it is never set.**

```
 GLOBAL fuel + carbon               WEATHER (national + regional)
   gas (NBP/TTF), coal,               temperature → heating/cooling demand
   oil, LNG, UK/EU-ETS                wind speed  → wind output
        │                             cloud/irradiance → solar output
        │                                     │
        ▼                                     ▼
   plant SRMC (marginal cost)         national DEMAND  (industrial + residential + commercial)
   per unit = fuel/η + carbon·EF/η          │            interconnection (imports/exports)
        │                                    ▼
        └──────────────►  MERIT-ORDER STACK  ◄─────────  renewable OUTPUT (near-zero SRMC)
                          (dispatch cheapest→dearest        subtracts from demand → RESIDUAL demand
                           until supply = demand)                       │
                                    │                                   │
                                    ▼                                   │
                        the LAST (marginal) unit dispatched ◄───────────┘
                        sets the clearing price
                                    │
                                    ▼
                        NATIONAL WHOLESALE PRINT  (day-ahead clearing / within-day / SSP-SBP)
                                = an OUTPUT of system tightness
```

The two families of driver, per the director's framing:
- **Global energy prices** set the *level* of the stack — where each thermal plant sits on the SRMC ladder. When global
  gas rises, the whole marginal-cost curve shifts up, so the clearing price rises even at unchanged demand. `[recall —
  verify at BUILD]` GB gas references NBP; continental TTF and global LNG arbitrage move NBP.
- **Weather** sets *how far up the stack the system has to climb* — it moves both demand (cold → heating load) and
  renewable supply (still/cloudy → less wind/solar), and therefore **residual demand** = the load the *thermal* fleet
  must serve. Higher residual demand → a more expensive marginal plant → a higher print. This is the coupling the
  weather-cascade DISCOVER already owns end-to-end.

Interconnection sits across both: GB imports when a neighbour is cheaper and exports when GB is cheaper, so a GB print
can be *set by a foreign marginal plant transmitted across a cable* — interconnectors flatten GB toward the coupled
Continental price and can either relieve or (when the neighbour is also short in the same cold/still European regime)
*fail to relieve* a GB tightness. `[recall — verify at BUILD]` GB links: France (IFA/IFA2/ElecLink), Netherlands
(BritNed), Belgium (Nemo), Norway (NSL), Ireland (EWIC/Moyle); a "cold-and-still" event is frequently *European-wide*,
so interconnector relief is weakest exactly when GB needs it most (a joint-tail sharpener — cross-references the cascade
doc §2 compounding).

### 1.2 Merit order and gas-sets-the-margin — the intuition, framed; and what the repo actually does

- **Marginal-cost dispatch.** Generators are stacked lowest-to-highest SRMC (must-run/CfD renewables and nuclear near
  zero; mid-merit CCGT gas; peaking OCGT/reciprocating/storage at the top) and dispatched until supply meets demand.
  The **last unit sets the price for all** — a single-clearing-price auction. `[recall — verify at BUILD]` GB day-ahead
  clears on N2EX / EPEX SPOT; the Balancing Mechanism and system-price (SSP/SBP cash-out) are a *separate* settlement
  mechanism layered on top.
- **Gas sets the margin, most of the time.** For most GB half-hours the marginal (price-setting) plant is a CCGT, so the
  wholesale price tracks **gas-plant SRMC ≈ gas/η + carbon·EF/η**. "The wholesale price follows gas" is a decent
  first-order intuition — but it is an *emergent* consequence of gas usually being marginal, not a law: in a very
  high-renewables half-hour the marginal plant can be renewable-driven (price → near zero or **negative** when must-run
  low-carbon output exceeds demand), and in a very tight half-hour it can be an expensive peaker (price spikes far above
  gas SRMC). **The convexity is real and structural** — near full dispatch a small demand increment jumps to a much
  dearer plant.
- **What the repo actually uses for the price print (important dependency):** in every production simulation phase the
  price print is **real historical Elexon SSP**, looked up by exact `(settlementDate, settlementPeriod)` from
  `sim/system_prices_history.py` (cache `sim/cache/elexon_ssp_full.json`) — **not** a generated curve. The synthetic
  merit-order engine `sim/price_engine.py` (`gas_floor·(demand/renewable)^γ`, γ∈[1.5,2.5], cubic turbine curve) exists
  but is **gated OFF pending calibration** — its own docstring says every phase continues to use real historical SSP
  until the SSP validation gate clears. For *beyond-history* (Regime 3) projection the active generator is a **statistical
  OLS**, `SSP ~ gas_price + demand_mw + wind_mw` (`simulation/run_phase3b_regression.py`; MAE ≈ £34/MWh, R²≈0.39), not
  the merit-order physics.
- **The known break (inherited from `W1_6_PHYSICS_PRICE_SIGNAL_DISCOVER.md` §1.2 / `docs/calibration/price-engine.md`):**
  the merit-order ratio form **overestimated real SSP by ~10× even at the lowest γ** (raw national-MW inputs give
  `demand/renewable` a median ≈3.46, and `^1.5` multiplies the gas floor ≈6.4×, pushing prices to thousands of £/MWh);
  it gets monotonically worse toward γ=2.5. **Two missing physics terms:** **carbon (UK ETS)** is absent from
  `gas_floor_price` entirely; and the calibrated ratio was *raw* demand/renewables, not the residual-demand-over-
  dispatchable-margin form the physics chain specifies. Both are upstream blockers on the *magnitude* of a generated
  price (not its direction) — §6. **For B specifically this means:** the "price is an emergent output" *structure* is
  right and partly real (SSP is exogenous-historical today, which is trivially "not set by the company"), but the
  *generative* merit-order route that would make price emerge from weather+fuel inside the SIM is not yet trustworthy —
  it is a design target, calibration-blocked, not a working baseline.

### 1.3 The SPOT print vs what a retailer actually pays — the crucial distinction

This is the hinge into §2 and must not be blurred:

- The **spot / wholesale print** (day-ahead clearing, within-day, and SSP/SBP cash-out) is the *marginal* price to buy
  or sell one more MWh **right now**. It is volatile, spiky, and is the number headlines quote (repo: crisis SSP reached
  £9,999/MWh, per `company/market/imbalance.py`).
- A **retailer almost never pays the spot print for most of its energy.** It pays a **weighted average of the forward
  purchases it made over the preceding months/years** (the hedge book), plus the spot print **only on the residual it
  did not pre-buy** (imbalance / top-up / sell-back). The spot print therefore drives (a) the price of **new** forward
  purchases it makes today (which feed *future* average cost and *today's* retail pricing decisions), and (b) the cost
  of **the gap** between what it hedged and what its customers actually consumed. It does **not** re-price energy already
  bought. **This is exactly the director's "otherwise, if fixed prices bought before, the actual price doesn't change."**

---

## 2. How a supplier's ACTUAL cost behaves — a weighted average of PRIOR purchases, not the spot print

### 2.1 The load-bearing distinction

A supplier's realised wholesale cost for a delivery period is **not** the spot print for that period. It is:

```
actual_cost(t)  =  Σ_p  volume_p · price_p          ← the HEDGE BOOK: forward purchases fixed BEFORE t,
                   ────────────────────────           each at the price prevailing WHEN it was bought
                        Σ_p volume_p                   (a volume-weighted average of prior fixings = WAPP)

                +  ( demand_realised(t) − hedged_volume(t) ) · spot_print(t)      ← the UN-hedged increment,
                                                                                   transacted AT delivery-time spot
                                                                                   (imbalance / top-up / sell-back)
```

The first term is a **weighted average of prices struck in the past** — it moves slowly, lagging spot by the tenor of
the book, and is *insensitive* to today's spot move on the portion already fixed. The second term is the **only** place
today's spot print bites, and it is proportional to the **volume error** (`demand_realised − hedged_volume`), positive
(short → buy top-up at spot) or negative (long → sell back at spot).

### 2.2 Where a price move actually HITS the P&L — and where it does NOT

| Position | A wholesale price move… | …hits P&L? | Why |
|---|---|---|---|
| Energy **already hedged** (fixed forward before delivery) for volume the customer **does** consume | | **NO** | Price was struck in the past; the fixing is a sunk contract. This is the director's "the actual price doesn't change." Insulated on price. |
| Customers on **fixed-price retail tariffs** matched by that hedge | | **NO (on cost)** | Both legs fixed; margin locked. Exposure here is *volume/credit*, not price. |
| The **un-hedged increment** — demand above (or below) the hedged quantity | | **YES** | Bought/sold at delivery-time spot; the imbalance double-hit (§3). Repo: short buys at `SSP·(1+premium)`, long sells at `≈SBP·0.95`. |
| **New retail products priced today** (new-business quotes, renewals repricing) | | **YES (forward-looking)** | Priced off *today's forward curve* — a spot/forward move changes the tariff it must quote to protect margin. The director's "drives the supplier to price for retail products bought now." |
| **Variable/SVT tariffs** (and the price-cap mechanism) | | **YES (lagged, pass-through)** | Cost floats with a lagged wholesale index; the cap itself is a lagged wholesale average `[recall — verify at BUILD: Ofgem cap uses a trailing observation window]`. |
| **Hedge slippage / roll**: book sized to a *forecast* volume that proved wrong | | **YES (indirect)** | A price move only bites via the *forecast error* — i.e. via volume. The pivot to §3. |

**The one-line cost physics:** a wholesale spike is **mostly a non-event for an already-hedged book against fixed-price
demand** — it bites on (i) the volume the supplier failed to pre-buy, transacted at spike prices, and (ii) the price of
*new* buying / new retail pricing. The exposure is on **volume + new buying**, not on the price of already-fixed
positions. A model that re-prices the whole book at spot each period is **wrong** and would massively overstate the
supplier's price sensitivity — an anti-pattern §4 must forbid.

### 2.3 Repo grounding — the machinery exists, split across the epistemic wall

The hedge-book / cost machinery already exists and matches §2.1 closely; **the two sides sit on opposite sides of the
epistemic wall** and BUILD must respect that:

**SIM-truth side (the company may NOT read):**
- **`sim/hedging.py`** — the actual blended cost, exactly the §2.1 shape:
  `wholesale_cost = hedged_volume/1000·hedge_price + unhedged_volume/1000·spot_price`, where
  `hedged_volume = hedge_fraction·consumption`, `hedge_price` = the forward locked in at term start, `spot_price` = real
  SSP. `hedge_fraction=0` → fully naked (all spot), `1` → fully hedged. **This is the mechanism B/C's cost physics is
  really about.** *Fidelity note (a real simplification to register at BUILD):* the hedged leg uses a **single**
  `hedge_price` per term, i.e. it collapses a real laddered/staggered forward book into one fixing — the true WAPP is a
  volume-weighted average over *many* trades at different times. The single-fixing form still captures "cost lags spot /
  fixed price doesn't move", but under-represents the *smoothing* a real staggered book gives and the roll dynamics.
- **`sim/hedging_strategy.py`** — the hedge-fraction *decision*: one lever, `MIN_HEDGE_FLOOR = 0.85` (a supply-mandate
  floor, not a speculative book), `INITIAL = 0.85`, `EVOLUTION_STEP = 0.1`; raise if it beats naked margin, lower (to the
  floor) if it underperforms. **This floor is load-bearing for §3's precondition A** — the current book is *structurally
  hedged* (0.80–0.90 population, per CLAUDE.md), so the "for a hedged supplier" condition holds by construction.
- **`simulation/settlement.py`** — the base per-customer settlement path costs at **spot SSP directly**
  (`wholesale_cost = consumption/1000·system_sell_price`) — the "buy everything at spot" baseline; the hedged variant is
  `sim/hedging.py::settle_hedged_period`. **The base spot-direct path is exactly the BC-2 anti-pattern in the codebase**
  — any cost path that re-prices consumed volume at spot without a hedge book overstates price sensitivity; flag which
  path each consumer uses at BUILD.
- **`simulation/portfolio_pnl.py`** — pure aggregation only (rolls up settlement's per-record margin), no cost logic.

**Company-observable side (the company builds its OWN belief from its OWN trades):**
- **`company/trading/wholesale_position_report.py`** — `wapp_gbp_per_mwh` per delivery month; `commodity_cost = wapp·
  hedged_volume`; `mtm = (current_market_price − wapp)·hedged_volume`; hedge_fraction, NOP, RAG banding. This is the
  company's *observed* weighted-average purchase price.
- **`company/market/gas_otc_book.py::average_buy_price_p_th()`** = `Σ(volume·price)/Σ(volume)` over BUY trades — the
  literal weighted-average-of-hedged-positions formula.
- **`company/trading/forward_book.py`** — individual forward contracts; settle P&L = `(agreed_price − actual_spot)·
  hedged_mwh` (positive when the forward locked in above spot) + MtM + bid-ask.
- **`company/market/imbalance.py`** / **`company/trading/imbalance_charge_register.py`** — the §2.1 second term as the
  company sees it: short → buy at `SSP·(1+premium)` (`premium 0.18` normal, **`1.2` stress**); long → receive at
  `≈SBP·0.95`, `SBP > SSP` always. **The stress premium (1.2 → 120% uplift, crisis SSP to £9,999/MWh) is the concrete
  "transacted at the moment it is most expensive"** of the §3 hypothesis.
- **`company/pricing/break_even_assessor.py`** — cost-to-serve vs Ofgem cap; `uncovered_loss = (break_even − cap)·
  consumption/100` — where a wholesale rise pushes customers net-negative under a lagged cap.
- **`company/pricing/margin_feedback.py`** — realised-margin → renewal surcharge (the forward-looking repricing channel,
  §2.2 row 4).
- **`company/finance/treasury.py`** — cash/working-capital/MCR only; it does **not** compute hedge cost (that lives in
  `sim/hedging.py` + the trading books). A dependency to note so BUILD doesn't look for cost physics here.

**The wall in one line:** the SIM's true blended cost (`sim/hedging.py`) and the company's *believed* WAPP (the trading
books) are the two sides of the coupled-triad gap — the company cannot read `sim/hedging.py`; it must infer its cost
structure from its own trades, bills and settlement. **BUILD audit #1:** confirm no company path re-prices hedged volume
at spot (a BC-2 defect) — the base `settlement.py` spot-direct path shows the anti-pattern is present for un-hedged flows.

---

## 3. TEST THE HYPOTHESIS — is the dominant weather→P&L path VOLUME or PRICE?

**The advisor's hypothesis, offered to be tested or refuted (NOT built):** *for a hedged supplier the dominant weather
coupling runs through VOLUME — consumption deviating from the hedged quantity, with the increment transacted at the
moment it is most expensive — rather than through the price of already-purchased energy.*

### 3.1 Verdict — SUPPORTED for a hedged book, on structural + repo grounds. With two sharpening conditions and one caveat.

**Finding: the hypothesis holds for a *hedged* supplier, and the mechanism is a multiplicative volume×price interaction
in the joint tail, not "volume instead of price."** Reasoning, from §1–§2 and the repo mechanics:

1. **The price of already-purchased energy is, by construction, insensitive to a weather-driven spot move** (§2.2 rows
   1–2; `sim/hedging.py` charges the hedged leg at `hedge_price`, the term-start fixing, regardless of delivery-time
   spot). The cold∧still spike does not re-price it. So the *direct* price path onto the *existing book* is ≈0 by design
   — the director's "the actual price doesn't change." The hypothesis's denial of the price path **on the fixed book** is
   correct and is literally how the code works.

2. **The residual exposure is the volume error, transacted at exactly the worst moment.** In a cold∧still cascade the
   book is **short** (metered demand plateaus above the hedged/forecast quantity — cascade link B) at the *same time* as
   cash-out spikes (link E). Repo: `sim/hedging.py`'s unhedged leg is charged at spot, and `company/market/imbalance.py`
   charges the short increment at `SSP·(1+premium)` with the **stress premium 1.2** — so the increment is transacted at a
   *super-spot* price precisely in the stressed regime. Volume-short and price-high are **positively correlated** (cascade
   §1 row F). The cost of the increment is `Δvolume · SSP·(1+premium_stress)` — **all three factors driven by the same
   weather regime**. The dominant weather→P&L path for a hedged book is therefore this imbalance/top-up term, whose price
   factor matters **only through the un-hedged volume**: remove the volume error and the spike costs nothing. That is the
   hypothesis, and both structure and code support it.

3. **Sharpening condition A — dominant only to the extent the book is actually hedged, and here it is.** For a
   naked/under-hedged book the price path is NOT insulated: a large open position realises at spot and price bites
   directly, dominating volume. The hypothesis is conditional on "*hedged* supplier" — and the repo's `MIN_HEDGE_FLOOR =
   0.85` plus the 0.80–0.90 population hedge ratio mean **the condition holds by construction in the current model**. The
   project's own near-naked-hedging episode (`HEDGE_VOLATILITY_LOOKBACK_FORESIGHT_BUG.md`) is exactly the regime where the
   hypothesis would *flip* to price-dominated. Honest statement: **for a well-hedged book (the current one) the coupling
   is volume-dominated; the hedge ratio is the dial that sets how true that is.**

4. **Sharpening condition B — "volume" = forecast/hedge error, and it also carries the new-buying + retail-repricing
   channels.** The weather regime also drives the price at which the supplier tops up / rolls the book *now* (feeds future
   WAPP) and the forward curve off which it prices new/renewing retail products (§2.2 rows 4–5; `margin_feedback.py`,
   `renewal_pricing_engine.py`). These are price-channel effects but they act on **new volume**, not the existing book —
   consistent with "exposure is on volume + new buying," not a refutation.

5. **Caveat — it is a volume×price *interaction*, and that is where suppliers die; do not collapse it to "volume only."**
   The dangerous quantity is the **covariance** term `E[Δvolume·spot]` in the joint tail, not either marginal. A model
   that (a) prices the whole book at spot **overstates** price sensitivity (the `settlement.py` spot-direct anti-pattern),
   but a model that (b) prices volume error at *average* spot **understates** cost by erasing exactly the coincidence
   (short ∧ spike) that kills suppliers — the same joint-tail-beats-marginals lesson as the cascade doc §2 and director
   requirement 4. **So: the dominant path is volume, but the cost lives in the volume-price coupling; the correct model
   is neither price-only nor volume-only but the joint term.**

**Net verdict:** the hypothesis is **SUPPORTED as the dominant path for a hedged book** — the weather→P&L coupling runs
through the un-hedged volume increment transacted at (super-)spike prices, not through re-pricing already-bought energy —
**provided** (A) the book is actually hedged (it is: floor 0.85) and (B) "volume" is read as hedge/forecast error plus
new-buying volume. The one correction to the framing: it is a **volume×price interaction (joint tail)**, and the price
factor is load-bearing *inside* that product even though it is inert on the fixed book.

### 3.2 What data would CONFIRM or REFUTE it at BUILD

`[all requires network / real data pulls — none available this session]`
- **Decompose realised wholesale P&L into three attributed terms** over historical cold∧still spells: (fixed-book cost at
  struck `hedge_price`) vs (imbalance volume × cash-out incl. stress premium) vs (mark-to-market of new buying). The
  hypothesis predicts the **second term dominates the P&L *variance* in the joint tail** for a hedged book. Refuted if the
  fixed-book term or a naked open position dominates.
- **Regress ΔP&L on Δspot and on volume-error separately, then on their product**, restricted to the winter joint tail.
  Hypothesis predicts the **interaction term** carries most explanatory power; a large standalone Δspot coefficient on the
  *existing book* would refute (would imply the book is being re-priced ⇒ not really hedged, or the model is wrong).
- **Sweep `hedge_fraction`** (0 → 1, straddling the 0.85 floor) and show the volume-vs-price dominance **crosses over** as
  the book goes hedged → naked (mechanistically confirms sharpening condition A; directly exercisable against
  `sim/hedging.py`).
- Requires: metered demand vs hedged-volume series, real SSP/SBP cash-out, the forward-purchase ledger (struck
  prices + volumes — the multi-trade WAPP `sim/hedging.py` currently collapses), and a recalibrated price engine (§6).
  **Connects to `W1_COUPLED_WEATHER_CASCADE_DISCOVER.md`** links F/G (the volume→residual→price→imbalance chain the
  cascade already frames) — this section is the *company-cost* reading of that cascade's terminal links.

---

## 4. Candidate INVARIANTS for a future L1/L2 (R10-class, R15-failable, NO code)

Stated in the R10 class-failing style (each fails a *class* of defect, not an instance). **No level claimed; provenance:
proposal.**

> **INVARIANT BC-1 (price is an emergent OUTPUT, never a set input).** In any *generated* run, the wholesale print must be
> **derivable** from the contemporaneous system state (fuel/carbon level, demand, renewable output → residual demand →
> marginal plant) and must **not** be readable back from any stored "target price" parameter. A code path that draws price
> independently of demand/supply, or sets price as an exogenous series decoupled from residual demand, fails. (Extends
> `W1_6`'s "price is NEVER an independent draw." Note the current-repo nuance: production runs use *real historical* SSP,
> which is legitimately exogenous-to-the-company; BC-1 binds the *generative/Regime-3* path, and names `bimodal_generator.py`
> — price from a fitted distribution with no weather coupling — as what it forbids as the *baseline* generator, though it
> may survive as a *curriculum* content generator, §5.)

> **INVARIANT BC-2 (supplier cost LAGS spot via the hedge book — a spot move does NOT re-price fixed positions).** For a
> book with hedged fraction `h` on consumed volume, a wholesale shock `Δspot` at delivery must change realised cost by **at
> most `(1−h)·Δspot·volume` plus the new-buying/roll term — and by ≈0 on the fixed `h·volume`**. Test: hold the book fixed,
> inject a spot spike, assert cost on the already-fixed portion is **unchanged** and the delta is confined to the un-hedged
> increment. A model that re-prices the whole book at spot (delta ≈ `Δspot·volume`) **fails** — this is the §2.2
> anti-pattern, present in the repo as the base `settlement.py` spot-direct path; BC-2 is the guard that keeps hedged flows
> off it. The single most important invariant, because it is the exact way a naive cost model overstates price sensitivity.

> **INVARIANT BC-3 (the weather→cost coupling is VOLUME-path-dominated for a hedged book — the hypothesis, made
> testable).** Over injected cold∧still spells, for a book at target hedge ratio, the share of wholesale-P&L tail variance
> attributable to the **volume×cash-out interaction term** must **exceed** the share attributable to re-pricing the fixed
> book (which BC-2 pins near zero) — and the dominance must **weaken monotonically as `hedge_fraction` falls toward naked**
> (where the price path re-dominates). A run in which a hedged book's tail P&L is driven by fixed-book re-pricing fails
> BC-2; a run in which the volume×price interaction has *vanished* (volume error priced at average, not tail, spot) fails
> the joint-tail requirement (director req 4) and under-states supplier risk.

**R15 — the invariants must be able to FAIL (mutation directions, designed not coded):**
- **BC-1 killer mutation:** replace the merit-order derivation with an exogenous price draw (or read back a stored
  target). BC-1 must fire.
- **BC-2 killer mutation:** make the cost engine re-price the hedged book at delivery-time spot (delete `sim/hedging.py`'s
  "hedged leg charged at term-start `hedge_price`" behaviour — i.e. route hedged flows through the `settlement.py`
  spot-direct path). BC-2 must fire — cost delta jumps to `≈Δspot·volume`.
- **BC-3 killer mutation:** (a) price the volume error at *average* spot instead of tail cash-out (drop the imbalance
  stress premium) → the interaction term collapses, BC-3's joint-tail arm must fire; (b) hold dominance constant as
  `hedge_fraction`→0 → the monotonicity arm must fire.
- **TAUTOLOGY guard:** the checker recomputes cost from the *independent* struck-price ledger + realised volume + observed
  spot — never reads back a stored "expected cost"; P&L attribution is computed from the ledger, not a stored decomposition.
- **FAIL-OPEN guard:** an empty book, `h`=0, zero volume error, a NaN spot, or a zero-margin division must **fail loud**,
  never pass on a degenerate run.
- **FAIL-SILENT guard:** if the struck-price ledger or the realised-volume series is unavailable, the check is a **FAILED**
  check, never skipped-and-green.

---

## 5. Wall / curriculum (R13, director requirement 5) + portability

- **Baseline (blind to P&L):** price-formation physics (merit order, gas-sets-the-margin, residual-demand→price
  convexity, interconnector coupling) and the cost physics (weighted-average book, spot-on-the-increment) are **baseline**
  — calibrated to reality, decided **blind to company P&L**, changed only for fidelity reasons (R12/R13). If the company
  loses money because it mis-hedged into a faithfully-severe spike, that is a **finding**, never a licence to soften the
  price or the cash-out premium.
- **The wall — the company sees only observables and must INFER its own cost structure.** The company **never** reads
  `sim/hedging.py`, the merit-order engine, γ, the residual calc, the regime label, or the generating processes. It
  observes only: the **published wholesale/forward prices** it can transact at, its **own bills and settlement** (SSP/SBP
  cash-out on its own imbalance volume, `company/market/imbalance.py`), its **own metered volumes**, and its **own
  struck-price ledger / WAPP** (its own past trades, the trading books §2.3). It must **infer** its cost structure, hedge
  effectiveness, and the volume×price coupling from these — imperfectly, as a real supplier does. The measured
  **belief-vs-truth gap** (`sim/hedging.py` true blended cost vs the company's believed WAPP-based cost sensitivity,
  especially in the joint tail) **is the deliverable** — a company that models itself as price-sensitive on its fixed
  book, or prices volume error at average spot, carries a measurable gap. Randomness lives **behind the curtain** in the
  SIM.
- **Curriculum (director's):** *which* price regimes and cost stresses the company lives through — a 2022-style crisis, a
  negative-price high-renewables spell, a specific cold∧still cascade severity — is **director-authored, named, versioned
  curriculum** (R13), never silent parameter drift and never agent-tuned toward a gap number. `bimodal_generator.py` may
  legitimately survive as a *curriculum content generator* (per the W1_6 open question) while BC-1 binds the *baseline*
  mechanism.
- **Portability (C-S / PORTABILITY):** keyed by *function*, not GB constants — "gas sets the margin" generalises to "the
  marginal fuel sets the margin"; the hedge-book cost model has no GB-specific term; interconnection is a neighbour-price
  coupling, not a hardcoded cable list. Percentile-keyed tails (winter-p10) re-derive per geography. Carbon is a *regime*
  term (UK ETS today), obligations-register-keyed, not implicitly one scheme forever.

---

## 6. Open questions / what BUILD needs (unresolvable without network or a director call)

1. **Price-engine SSP recalibration is a HARD upstream blocker** (inherited from `W1_6_PHYSICS_PRICE_SIGNAL_DISCOVER.md`
   §1.2 / `docs/calibration/price-engine.md`): the merit-order ratio form **overestimates real SSP by ~10×** in its
   raw-demand/raw-renewable form; the residual-demand-over-dispatchable-margin form has **never been calibrated**, and the
   **carbon (UK ETS) term is missing entirely** from `gas_floor_price`. Production runs sidestep this by using real
   historical SSP, but the *generative* B path (weather→price inside the SIM) cannot be trusted until this clears. The
   *direction* of every claim here is robust; the *magnitude* of a generated spike (and the £ size of the §3 volume×price
   interaction) is a BUILD output, reported not tuned (R12).
2. **Real data series needed** (no network here): NBP/TTF gas, UK-ETS allowance price + emissions factor, real SSP/SBP
   cash-out, national demand + wind + solar output, interconnector flows, and — for §2/§3 — the **historical
   forward-purchase ledger** (struck prices + volumes; the multi-trade WAPP `sim/hedging.py` currently collapses into one
   `hedge_price`) and metered-vs-hedged-volume series. Route via the discovery-agent against Ofgem/Elexon/NESO/DESNZ/ICE
   at BUILD; **fabricate no figure** in the interim.
3. **Hedge-book fidelity gap:** `sim/hedging.py` uses a **single** term-start `hedge_price` for the hedged leg, collapsing
   a real laddered/staggered forward book (many trades → true WAPP, as the company-side `gas_otc_book.average_buy_price`
   already models) into one fixing. Whether to enrich the SIM cost to a multi-trade WAPP (adds roll/smoothing dynamics, and
   makes §3's "new-buying at spike prices feeds future cost" channel first-class) is a BUILD scope call — register as a
   named simplification (R10) if deferred.
4. **BC-2 audit of existing cost paths:** confirm which flows use `sim/hedging.py::settle_hedged_period` vs the base
   `settlement.py` spot-direct path; any hedged flow on the spot-direct path is a BC-2 defect to fix at BUILD, not a new
   discovery.
5. **Coupled-triad registration:** the B/C cost-gap is the company-cost twin of the weather cascade's imbalance link.
   BUILD registers the pair(s) in `background/coupled_triad.py::_AUTHORITATIVE_COUPLING` (no weather/cost pair today, per
   the cascade doc §0) and adds a `coupled_gap_ledger.json` row so the Proof-door panel renders the cost gap — a BUILD act,
   off-front until the director opens W1.
6. **Interconnector fidelity** — whether the baseline needs an explicit neighbour-price coupling or can treat
   interconnection as a residual-demand adjustment is an open modelling call (affects joint-tail severity: European-wide
   cold∧still weakens import relief exactly in the tail). Scope decision for the director/BUILD.

---

*Sources read/reasoned this session (no network): `docs/staging/DIRECTOR_CAMPAIGN_EPOCH2_COUPLED_WORLD_2026-07-19.md`,
`docs/design/EPOCH2_COUPLED_WORLD_CAMPAIGN_DECOMPOSITION.md` (atoms B, C), `docs/design/W1_6_PHYSICS_PRICE_SIGNAL_DISCOVER.md`
(price engine audit + ~10× SSP miscalibration + missing carbon term), `docs/design/W1_COUPLED_WEATHER_CASCADE_DISCOVER.md`
(weather→…→imbalance→capital cascade, joint-tail compounding, links F/G), `docs/design/WEATHER_PHYSICS_HIERARCHY_DESIGN.md`
§1.4 (cited, not re-derived); repo cost/hedge machinery read this session: `sim/hedging.py` (blended cost + hedge_fraction),
`sim/hedging_strategy.py` (0.85 floor + evolution), `sim/system_prices_history.py` (real SSP is the live price print),
`sim/price_engine.py` (merit-order engine, gated off), `simulation/settlement.py` (spot-direct base path),
`simulation/portfolio_pnl.py` (aggregation only), `company/market/imbalance.py` (SSP/SBP + stress premium 1.2),
`company/trading/{wholesale_position_report,forward_book,imbalance_charge_register}.py`,
`company/market/gas_otc_book.py` (WAPP), `company/finance/treasury.py` (cash only),
`company/pricing/{break_even_assessor,margin_feedback,renewal_pricing_engine}.py`, `docs/calibration/price-engine.md`
(the OLS regression addendum). All external market-structure facts flagged `[recall — verify at BUILD]`; no figure
fabricated (Historical Ground Truth). R10/R12/R13/R15, COUPLED_TRIAD, epistemic wall referenced inline.*
