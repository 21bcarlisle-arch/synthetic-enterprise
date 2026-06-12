# The Synthetic Enterprise — Master Backlog

> **How this works:** Read this file at the start of every session. Execute phases in order. After each phase write `docs/observability/PHASE_<ID>_SUMMARY.md`, send an NTFY notification to `ntfy.sh/skynet-synthetic`, then proceed to the next phase automatically. Gates (`[REVIEW_GATE]`) pause execution and wait for a new instruction before proceeding.

## NTFY Protocol

Send all notifications via: `curl -d "message" ntfy.sh/skynet-synthetic`

**Any file referenced in a notification must be a raw GitHub URL, not a blob URL** — Rich's strategy advisor reads these links directly and needs raw text, not a rendered HTML page. Format:
`https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/[filepath]`
(e.g. a reference to `docs/observability/PHASE_1d_SUMMARY.md` becomes `https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/docs/observability/PHASE_1d_SUMMARY.md`). This only works for files already committed and pushed to `main` — push before sending the notification, never after (this is also already required by the Phase Summary Protocol below).

Required notifications:
1. Session start: `"Agent started. Next phase: [ID]"`
2. Phase started: `"Phase [ID] started: [description]"`
3. Phase complete: `"Phase [ID] complete. Summary at https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/docs/observability/PHASE_[ID]_SUMMARY.md"`
4. Gate reached: `"GATE after Phase [ID]. Waiting for instruction before proceeding."`
5. Error: `"ERROR in Phase [ID]: [brief description]"`

## Staging Review Protocol

The file API's `/write` endpoint targets `docs/staging/` (not `docs/instructions/` directly), so externally-submitted
instruction files always pass through review before they can affect the agent's own behaviour.

At the start of every session (and on each polling cycle thereafter):
1. Check `docs/staging/` for any new files.
2. Review each one on its merits.
3. **Two-way door** (reversible — e.g. a new backlog item, a clarification, a non-destructive config tweak):
   promote it by moving/copying the file into `docs/instructions/`, then delete it from `docs/staging/`.
4. **One-way door** (anything spending money, deleting data, changing irreversible external state, or otherwise
   matching the "Reversibility is law" escalation criteria): do **not** promote automatically. Leave the file in
   `docs/staging/` and send an NTFY to `skynet-synthetic` summarising the item and asking Rich to approve promotion,
   including the raw GitHub URL to the staged file.

## Phase Summary Protocol

At the end of every phase write `docs/observability/PHASE_<ID>_SUMMARY.md` with:
- What was built (3-4 bullets, concrete file paths)
- Key findings (3-4 bullets)
- Key decisions made (3-4 bullets)
- Open questions (1-2 bullets)
- Token efficiency (frontier vs local tokens, what was produced)

One page, readable in 60 seconds. Commit and push before sending NTFY.

## Harness Rule (standing instruction)

`make check` must pass before any REVIEW_GATE is cleared and before any phase summary is committed.
Every new feature instruction must include: write the test that proves it works.

## Delegation Protocol

Two local models, routed by task type via `tools/delegate_ollama.py --task-type coder|analysis` (`localhost:11434`, one running at a time — swap, don't run both simultaneously):

**`qwen3:14b`** ("coder" tasks — code stays local):
- All code generation and file writing
- Data transformation scripts
- Test scaffolding

**`qwen2.5:7b`** ("analysis" tasks — drafts only, frontier reviews and edits before anything is committed):
- Analysing settlement-result CSVs and producing structured summaries
- Drafting `PHASE_SUMMARY.md` files (frontier reviews and edits the draft — never commits it raw)
- Writing README updates and inline code comments
- Extracting key figures from result tables
- Drafting `STATUS.md` updates

**Stays on frontier, always:**
- Architecture decisions
- Reviewing local-model output before committing (code AND analysis/drafts)
- One-way door decisions
- Genuine blockers

General delegation notes:
- When asking for edits, supply the full current file content verbatim
- Watch for Qwen quirks: markdown fence wrapping, placeholder echoes, multi-constraint ordering slips, and (for "copy this file, change only X" requests) a tendency to silently regenerate parts the instruction said to leave untouched — keep those diffs small or hand-write the orchestration instead
- Goal: frontier touches results and decisions only — drafting and analysis routes to local models, with frontier review as the gate before anything ships

## Where We Are

Completed: Phase 0a (scaffold), Phase 0b (4-customer PC1 resi portfolio, 2016 Q4 P&L = -£77.67), Phase 0c (full 2016 P&L = -£78.28, dissatisfaction counter, CLV seed). The supplier lost money in every quarter of 2016. Root cause: naked spot exposure with no hedging. Forward curve pricing and hedging are the primary fixes.

---

## Phase 1a — Customer Cohort & Geography

Give the four existing customers distinct identities, locations, and home characteristics.

Deliverables:
1. Create/update `saas/customers.py` with four customer profiles:
   - C1 (2016-01-01): London urban flat, 2-bed, EPC D, EAC 2,800 kWh
   - C2 (2016-04-01): Manchester suburban semi, 3-bed, EPC D, EAC 3,500 kWh
   - C3 (2016-07-01): Glasgow tenement flat, 2-bed, EPC E, EAC 3,200 kWh
   - C4 (2016-10-01): Cotswolds rural detached, 4-bed, EPC E, EAC 5,500 kWh
2. Each record must include: `customer_id`, `acquisition_date`, `location` (lat/lon + region), `home_type`, `bedrooms`, `epc_rating`, `eac_kwh`, `commodity` (= "electricity"), `contract_type` (= "fixed_1yr"), `segment` (= "resi")
3. `commodity` must be a field not a hardcoded assumption — open door for gas
4. Update `docs/data-sources/customers.md` documenting the cohort
5. Re-run Phase 0c settlement with updated profiles — confirm P&L unchanged

Constraints: commodity column exists from day one. EAC nullable for future smart meters. Location stored as both lat/lon and human-readable region.

Commit after each deliverable. No gate.

---

## Phase 1b — Weather Data Capture

Ingest historical daily weather for all four customer locations, 2016-2025. Store it — do not correlate yet.

Deliverables:
1. Research best free UK historical weather API (preferred: Open-Meteo — free, no key, covers UK back to 2016). Document in `docs/data-sources/weather.md`
2. Write `sim/weather_ingestor.py` — fetches daily weather by lat/lon and date range. Fields: `date`, `location_id`, `temperature_max_c`, `temperature_min_c`, `temperature_mean_c`, `wind_speed_mean_ms`, `cloud_cover_pct`, `precipitation_mm`
3. Pull weather for all four locations, 2016-01-01 to 2025-06-07. Store as CSV in `sim/weather_data/` — one file per location

Constraints: same date granularity as settlement data. Do not correlate to consumption or prices yet. Schema must accommodate future sub-daily resolution.

Commit after each deliverable. No gate.

---

## Phase 1c — Forward Curve Pricing

Replace 30-day spot lookback pricing with a synthetic forward curve. This is the primary fix for the 2016 losses.

Deliverables:
1. Write `sim/forward_curve.py` — given acquisition date and contract length (default 12 months), generates a synthetic forward price using: (a) 90-day rolling average SSP as base, (b) σ of SSP over the same 90 days × risk factor (start 1.2), (c) seasonal adjustment (winter +15%, summer -5%)
2. Update `saas/tariff_pricing.py` — replace 30-day lookback with forward curve price. Margin remains 5%
3. Re-run full 2016 settlement with forward curve pricing — compare P&L to Phase 0c baseline (-£78.28)
4. Run full 2016-2025 window with forward curve pricing — report portfolio P&L by year

Constraints: forward curve lives in SIM side behind the interface seam. Risk factor and seasonal adjustments are configurable parameters. Forward price clearly labelled as synthetic per Law 3.

**[REVIEW_GATE]** — write PHASE_1c_SUMMARY.md, send NTFY, then wait for instruction before proceeding.

---

## Phase 1d — Hedging Strategy (Agent-Discovered, Time-Evolving)

**Objective:** The agent learns to hedge the portfolio over time using available wholesale instruments. It makes decisions using only information available at each decision point (Point-in-Time Blindfold applies to strategy, not just data). It observes outcomes and evolves its approach at each contract renewal cycle.

**Design principle:** Do not give the agent a pre-defined strategy to test. Give it instruments and let it reason about how to use them. The gate at this phase reviews whether the agent's initial reasoning and evolution logic make domain sense — not which strategy "won."

### Wholesale Instrument Menu (Electricity)

The agent may use any combination of these instruments when hedging a customer position:

| Instrument | Tenor | Typical use |
|---|---|---|
| Day-ahead spot | Next day | Top-up / short-term balancing |
| Month-ahead | M+1 | Short-term cover |
| Quarterly (Q+1 to Q+4) | 3 months | Medium-term volume matching |
| Seasonal strip (Summer/Winter) | ~6 months | Seasonal shape management |
| Annual (Cal+1, Cal+2) | 12 months | Long-term fixed price cover |

Instruments are purchased at the forward price available at the decision date (from `sim/forward_curve.py`). No instrument gives the agent knowledge of future spot prices.

### Decision Function (Initial)

At each customer acquisition or renewal date, the agent must:
1. Review what it knows: current forward curve shape, volatility (σ), season, time of year
2. Choose a hedge position: which instruments to buy, what volume (% of EAC), what tenor
3. Record the hedge book: instrument, price, volume, delivery period
4. At settlement: compute actual cost (hedge price × hedged volume + spot × unhedged volume) vs tariff revenue

### Evolution Mechanic (No Foresight)

After each contract year completes:
1. Agent observes: realised P&L vs expected P&L, where cost exceeded tariff, which periods drove losses
2. Agent updates its hedging parameters for the next cycle — e.g., increase hedge ratio, extend tenor, add seasonal cover
3. Update must be based only on observed history up to that date — no look-ahead, no knowing what 2022 will bring
4. Document the reasoning: why did it change the approach, what signal drove the adjustment

### Deliverables

1. Implement hedge book in `sim/hedging.py` — records positions, computes cost at settlement, supports multiple instrument types
2. Implement decision function in `sim/hedging_strategy.py` — agent's reasoning at each acquisition/renewal date, based only on PiT-available information
3. Implement evolution mechanic — after each year, agent reviews outcomes and updates strategy parameters
4. Run the full 2016-2025 window with renewals active — report annual P&L, hedge effectiveness, how the strategy evolves year by year
5. Document in `docs/simulation-strategy.md`: how the strategy evolved, what signals drove changes, whether it improved over time

### Constraints

- No look-ahead: decisions made only on data available at the decision date
- Hedge book lives in SIM side behind the interface seam
- Volume assumption: EAC realised exactly for now — volume risk is a future phase
- Instrument prices sourced from `sim/forward_curve.py` — the synthetic forward series, per Law 3

**[REVIEW_GATE]** — write PHASE_1d_SUMMARY.md showing: the agent's initial hedging reasoning, how the strategy evolved year by year, and the nine-year P&L outcome. Send NTFY. Rich reviews whether the evolution logic makes domain sense before Phase 1e.

---

## Phase 1e — Nine-Year Portfolio Run with Enterprise Risk Physics

**Objective:** Run the complete 2016-2025 simulation with the hedging agent from Phase 1d, augmented with real clearinghouse economics. The agent must discover organically that holding naked risk is not free. No strategy is pre-specified — the capital mechanics create the incentive to hedge.

### Starting Conditions

- Reset all four customers' `hedge_fraction` to **0.50** (neutral prior — do not carry forward Phase 1d's converged 0.00 position; that was a lesson documented, not a state to inherit)
- Portfolio treasury: **£3,250 initial cash balance** (single pool shared across all four customers, representing ~3 months of expected wholesale cost)
- Simulation window: 2016-01-01 → 2025-06-07, full renewal cycle as established in Phase 1d

### The Risk Engine (add to `sim/risk_engine.py`)

**1. Dual-Window VaR**

At each contract term start, calculate:

```
VaR_current = 1.645 × σ_recent × V_naked × P_forward
VaR_stressed = 1.645 × σ_stressed × V_naked × P_forward
Active_Collateral = max(VaR_current, VaR_stressed)
```

Where:
- `σ_recent` = standard deviation of SSP over the trailing 12 months (rolling, PiT-safe)
- `σ_stressed` = regime-dependent floor (see below — NOT the 2021-2022 σ at simulation start)
- `V_naked` = unhedged volume for the term (EAC × (1 - hedge_fraction))
- `P_forward` = forward price at term start

**Stressed VaR floor — PiT-safe and historically accurate:**
- 2016-01-01 → 2022-12-31: `σ_stressed` = **0.50** (50% — reflecting the pre-reform Ofgem capital adequacy environment; lax by design, historically correct)
- 2023-01-01 onwards: `σ_stressed` = **1.50** (150% — Ofgem post-crisis capital adequacy reforms; the regulatory environment the agent operates under permanently changes after the crisis)

This transition is not foresight — it is a regulatory change the agent experiences at the point it happens.

**2. Cost of Capital**

Each settlement period, deduct from the portfolio treasury:

```
Monthly_CoC = Active_Collateral × WACC / 12
```

Where `WACC` = **0.10** (10% annualised — mid-range of the 8-12% typical for energy retail).

Deduct proportionally per settlement period (i.e. divide by number of periods in the month). Record as `capital_cost_gbp` in the settlement record.

**3. Treasury & Administration Event**

- `treasury_cash_balance` starts at £3,250 and updates each period: `+margin_gbp - capital_cost_gbp`
- If `treasury_cash_balance` <= 0 at any point: trigger **Administration Event** — log the date, the proximate cause (margin call vs accumulated CoC drain), and halt the simulation for that run
- Report whether the portfolio survives the full nine-year window or enters administration, and if so when and why

### Evolution Rule (carry forward from Phase 1d, unchanged)

The agent still uses Phase 1d's `evolve_hedge_fraction()` — compare completed term margin against naked counterfactual, step by 0.1, deadband ±£5. Do not modify it. The CoC signal will now compete with and reshape the evolution signal organically — let it do so without pre-specifying the outcome.

### Deliverables

1. `sim/risk_engine.py` — VaR calculation (dual window), CoC deduction, treasury tracking, administration event trigger
2. Update `simulation/hedged_settlement.py` — incorporate CoC deduction into per-period P&L
3. Update `simulation/run_phase1d.py` → `simulation/run_phase1e.py` — full nine-year run with risk engine active, administration event handling
4. Report per year: gross margin, capital costs, net margin (gross minus CoC), treasury balance end of year, hedge_fraction per customer end of year, VaR_current vs VaR_stressed
5. Report the full hedge_fraction evolution per customer year by year — did the agent discover the ~40-60% optimal zone organically?
6. Report whether administration was triggered and if so when and why
7. `docs/simulation-strategy.md` — update with Phase 1e findings: did the risk physics produce emergent hedging behaviour? How did the 2023 regulatory floor change affect the agent?

### Delegation

- `sim/risk_engine.py` — delegate to `qwen2.5-coder:14b` with full algorithm spec as above. Supply exact formula. Review output before committing.
- `simulation/run_phase1e.py` — hand-write orchestration (Phase 1d finding: orchestration scripts touching existing schemas produce wrong field names when delegated)
- Analysis and PHASE_1e_SUMMARY.md — delegate to `qwen2.5:7b`
- Frontier reviews all output before committing

### NTFY

Send raw URL in all notifications:
- Phase started: `"Phase 1e started — enterprise risk physics active, treasury £3,250, hedge reset to 0.50"`
- Phase complete: `"Phase 1e complete. [survived/administration on DATE]. Net 9yr margin: £X. Hedge converged to: X%. Summary: https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/docs/observability/PHASE_1e_SUMMARY.md"`
- Gate: `"GATE after Phase 1e — Rich reviews whether risk physics produced organic hedging behaviour before Phase 2"`

**[REVIEW_GATE]** after delivering results and summary. This is the key Phase 1 milestone.

---

## Phase 2 — Context Handshake, SME Segment & Gas Dual Fuel

### The Context Handshake (build first, before Phase 2a or 2b)

**Objective:** Implement the risk committee agent wake-up mechanism. This breaks the hf=0.00 structural blindness identified in Phase 1e by giving an LLM agent direct visibility of treasury dynamics and VaR regime — information the evolution rule is structurally blind to.

**Design:**

1. Write `sim/risk_committee.py` — the wake-up trigger and context packager:
   - Monitor two hard thresholds after every settlement period:
     - Treasury drawdown > 10% from its rolling 12-month peak
     - VaR_current > VaR_stressed × 1.2 (current risk exceeds stressed floor by 20%)
   - When either threshold is breached, package the context handshake summary (see format below) and write it to `docs/context-handshake-latest.md`
   - Flag the session for a risk committee wake-up

2. Write `sim/risk_committee_agent.py` — the LLM agent (frontier model only, not delegated):
   - Reads `docs/context-handshake-latest.md`
   - Adjusts exactly one lever: `hedge_fraction` for the customer(s) whose VaR triggered the threshold
   - Writes the updated parameter back to the simulation state
   - Logs its reasoning in `docs/observability/risk-committee-log.md` (one entry per wake-up)
   - Returns to sleep immediately

3. Context handshake format (write to `docs/context-handshake-latest.md` on each trigger):
```
## Risk Committee Wake-Up — [timestamp]
Trigger: [treasury drawdown X% / VaR breach X%]
Treasury balance: £X (peak: £X, drawdown: X%)
Portfolio gross margin YTD: £X | Net margin YTD: £X
Active collateral: £X | Monthly CoC: £X
VaR_current: £X | VaR_stressed: £X | Ratio: X
Per-customer hedge_fraction: C1=X C2=X C3=X C4=X
Rolling 12m SSP avg: £X/MWh | σ_recent: X
Regime: [pre/post 2023 regulatory change]
Recommendation requested: adjust hedge_fraction for [customer(s)]
Constraint: minimum adjustment +0.10, maximum single adjustment +0.30
```

4. The risk committee agent must:
   - Justify its decision in plain English in the log
   - Never decrease hedge_fraction (it only acts when risk is elevated)
   - Return to sleep after a single adjustment — no further intervention until the next threshold breach

**Constraints:**
- Zero LLM activity except at threshold breaches — the inner loop remains pure Python/NumPy
- The agent adjusts one lever only — hedge_fraction. It does not change treasury policy, tariff margins, or contract terms
- The evolution rule (`evolve_hedge_fraction()`) continues to run unchanged alongside the risk committee — they are two independent signals; the evolution rule can still decrease the fraction between wake-ups

**Commit risk_committee.py and risk_committee_agent.py separately. No gate on this — it is infrastructure, not a deliverable.**

---

## Phase 2a — SME Segment

**Objective:** Add SME customers alongside resi. Tests whether the pipeline handles multiple segments cleanly and whether the risk physics and Context Handshake behave correctly at larger volumes.

**Deliverables:**

1. Add two SME customers to `saas/customers.py`:
   - C5 (acquired 2016-01-01): London, small office, Profile Class 3, EAC 25,000 kWh, `segment`="SME", `commodity`="electricity"
   - C6 (acquired 2016-04-01): Manchester, warehouse unit, Profile Class 3, EAC 45,000 kWh, `segment`="SME", `commodity`="electricity"

2. Confirm the full pipeline (pricing, hedging, settlement, risk engine, Context Handshake) handles SME customers without segment-specific code. If any code change is needed it must be backwards-compatible — no if/else on segment type in the core pipeline.

3. Update the shared portfolio treasury: starting balance scales with portfolio size. New starting balance = £3,250 × (total portfolio EAC / original 4-customer EAC). Calculate and apply.

4. Run full 2016-2025 with all six customers (C1-C4 resi + C5-C6 SME). Report:
   - Annual P&L per customer and portfolio total
   - Context Handshake wake-up log — did the risk committee fire? When? What did it do?
   - Did the SME customers' larger volumes change the treasury dynamics vs resi-only?
   - Per-customer CLV accumulated

5. Pull PC3 shape profile data (same source as PC1 — Elexon portal) and document in `docs/data-sources/profile-class-3.md`

**Delegation:** PC3 shape loader — delegate to qwen2.5-coder:14b with full source verbatim. Orchestration — hand-written. Analysis and summary — delegate to qwen2.5:7b.

**[REVIEW_GATE]** — write PHASE_2a_SUMMARY.md, send NTFY with raw URL and headline figures. Include: did the Context Handshake fire and did it make domain-sensible decisions?

---

## Phase 2b — Gas Dual Fuel

**Prerequisite:** Phase 2a gate cleared.

**Objective:** Add gas supply to C1-C4 resi customers (dual fuel). Tests the commodity abstraction — gas and electricity must route through the same pipeline with commodity as a field, not a branch.

**Ground truth (do not research — use exactly what follows):**

NBP gas price data:
- Primary source: NGT MIPI API at https://mipidata.nationalgas.com/api
- Use System Average Price (SAP) — JSON, fields: `ApplicableFor` (gas day), `Value` (p/kWh)
- Do NOT use NESO CKAN — electricity only. Do NOT use ICE — paywalled.

AQ (Annualised Quantity):
- Use fixed synthetic AQ per customer (same logic as EAC for electricity)
- AQ field is nullable — do not hardcode. Weather-driven AQ adjustment is future work.

CV conversion formula:
```
kWh = V × CF × CV / 3.6
```
- CF = 1.02264 (standard UK legal value)
- CV = 39.5 MJ/m³ (fixed assumption — store as configurable field, not hardcoded constant)
- V in m³

**Deliverables:**

1. Pull historical NBP SAP data 2016-2025 from NGT MIPI API. Store in `sim/gas_data/nbp_sap.csv`. Document in `docs/data-sources/gas-nbp.md`.

2. Add gas commodity records to C1-C4 in `saas/customers.py`:
   - `commodity`="gas", `aq_kwh` (synthetic, based on home type and EPC rating — use ~12,000 kWh for C1 flat, ~15,000 for C2 semi, ~14,000 for C3 tenement, ~22,000 for C4 detached), `cv_factor`=39.5, `cf`=1.02264
   - Same acquisition dates, same contract structure (1-year fixed)

3. Extend pricing and hedging pipeline to handle gas:
   - `commodity` field routes to the correct price feed (NBP SAP for gas, Elexon SSP for electricity)
   - Forward curve logic applies to gas using NBP seasonal structure
   - Risk engine applies to gas positions — same VaR logic, commodity-aware

4. Run 2016-2025 with dual-fuel C1-C4 plus electricity-only C5-C6. Report:
   - Dual-fuel P&L per customer (electricity + gas separated)
   - Portfolio-level commodity exposure split (£ at risk: electricity vs gas)
   - Did the gas positions change the Context Handshake trigger frequency?

5. Confirm `data_regime`="historical" field is present on all gas records.

**Delegation:** NBP ingestion and CV conversion — delegate to qwen3:14b with full formula spec. Orchestration — hand-written. Analysis — qwen2.5:7b.

**[REVIEW_GATE]** — write PHASE_2b_SUMMARY.md, send NTFY with raw URL and headline dual-fuel P&L figures.

---

## Phase 3a — Experience Observability Depth [Run parallel with Phase 2]

Improve the customer reaction function from a simple counter to richer experience signals.

Deliverables:
1. Extend `saas/customer_reaction.py` with three signals per customer per billing period:
   - `bill_shock_score`: abs(this_bill - rolling_6_period_avg) / rolling_6_period_avg — triggers above 0.15
   - `cumulative_exposure`: running sum of (actual cost - tariff revenue)
   - `expectation_gap`: customer's expected bill (last bill × 1.02) vs actual bill
2. Store signals in a per-customer time series
3. Report: which customers had most bill shock events in 2016? In 2021-2022? Does profile differ by location or home type?

No gate. Write PHASE_3a_SUMMARY.md and send NTFY.

---

## The Synthetic Evolution Roadmap

This project runs in three distinct data regimes. Every piece of code must respect this sequencing:

**Regime 1 — Historical (Phases 1-2):** All simulation runs on real, public historical data (Elexon SSP/SBP, NESO, Open-Meteo). No synthetic generation. Law 1 applies absolutely. This window ends 2025-06-07.

**Regime 2 — Hybrid (Phase 3):** Real data as the backbone. Synthetic physics engines introduced for scenarios and stress tests *beyond* the historical window, or for counterfactuals ("what if the 2022 crisis lasted three winters?"). Each physics engine must be validated against real data before being trusted to run solo — validation is a formal deliverable, not an afterthought.

**Regime 3 — Fully Synthetic (Phase 4+):** The agent has learned from a decade of real market behaviour. Physics engines are calibrated. The sim runs forward decades beyond 2025, or backward into counterfactuals, without needing real data. This is the long-term goal: a fully synthetic energy market ecosystem that can be evolved and run for extended periods.

**The thesis this enables:** A sim calibrated on real data becomes a genuine forward simulation tool — not just a backtest. The kind of tool real suppliers would pay for.

### The data_regime Field (open door — add now)

Every record in every data store must carry a `data_regime` field from day one:
- `"historical"` — sourced from real public data
- `"synthetic"` — generated by a physics model

This field is cheap to add now and a migration later. No exceptions. This is the boundary marker between Regime 1 and Regime 3.

### Physics Engine Calibration Requirement

Every synthetic physics engine built in Phase 3+ must include a formal calibration deliverable before being used in Regime 3:
- Run the engine over the 2016-2025 historical window
- Compare output against real data (SSP vs modelled price, real weather vs modelled weather, real consumption vs modelled consumption)
- Document calibration error and any systematic bias
- Only after calibration passes review does the engine graduate to Regime 3

Engines to build and calibrate (Phase 3+, do not build early):
- **Merit-order wholesale price engine** (gas floor + system margin shape + wind cubic physics)
- **Two-pass weather engine** (national macro regime-switching + regional Cholesky decomposition)
- **Thermal load physics** (U-fabric building envelope + solar gain — replaces PC1 profiles per property)
- **Bass Diffusion heat pump/EV adoption** (warps portfolio commodity exposure from gas to electricity over decades)

---

## The Context Handshake (Governing Execution Model)

This is the named execution model for all LLM agent activity. It must be respected in all phases.

**The principle:** Zero LLM activity in the inner simulation loop. The half-hourly settlement, weather generation, price calculations, and portfolio updates run entirely in vectorized NumPy/Polars code at full speed. LLM agents (the trading agent, the risk committee, the pricing agent) are completely dormant between wake-up events.

**Wake-up triggers (two types):**
1. **Scheduled decision boundaries** — quarterly risk reviews, contract pricing cycles, annual treasury reviews
2. **Hard threshold breaches** — treasury balance drops >10%, VaR exceeds stressed floor by >20%, administration event imminent

**The handshake protocol (every wake-up):**
1. The Python engine packages recent history into a structured Markdown executive summary
2. The LLM agent reads the summary, adjusts exactly one high-level lever (hedge_fraction, tariff_margin, or similar)
3. The updated parameter is written back to the simulation state file
4. The agent immediately returns to sleep
5. The Python engine resumes at full speed

**The executive summary format** (evolves as phases add layers):
```
## Agent Wake-Up Context — [timestamp]
Wake-up trigger: [scheduled/threshold breach — description]
Treasury balance: £X (change from last period: £X)
Portfolio P&L YTD: £X
Current hedge_fraction: X (per customer if diverged)
VaR_current: £X | VaR_stressed: £X | Active collateral: £X
Rolling 12m SSP avg: £X/MWh | σ: X%
Customer dissatisfaction events (last quarter): X
Open questions: [any escalation items for Rich]
```

This format must be updated in `docs/context-handshake.md` whenever a new data layer is added, so the agent always wakes up with a complete picture.

**Why this matters:** This is what allows decades of simulation to run without burning frontier tokens on every settlement period. The agent acts at the strategic level only. All tactical execution is code.

---

## Phase 3b — Wholesale Price Model: Statistical Regression (active) + Physics Engine (deferred to Regime 3)

**Objective:** Provide a wholesale price model for Regime 2 (synthetic forward beyond the historical window), validated against real SSP data.

**Do not start until Phase 2 is complete.**

**Status (2026-06-11): redesigned per Rich's direction ("Option B").** The
originally spec'd merit-order physics model (`sim/price_engine.py`: gas
floor / system margin shape `(demand/renewable)^γ` / wind cubic power curve)
was implemented, tested (15 tests), and calibrated against real 2019/2022
SSP — it overestimated SSP by ~10x at γ=1.5 (the spec floor) and got worse
toward γ=2.5 (see `docs/calibration/price-engine.md`, original sections).
**This physics model is deferred to Regime 3** — the module and its tests
remain in the repo (correct in isolation), but margin-term redesign is
parked, not abandoned, and is not the current deliverable.

**Active Phase 3b deliverable: statistical regression model.**
1. `simulation/run_phase3b_regression.py` — OLS regression of
   `SSP ~ gas_price + demand_mw + wind_mw` (intercept included), fit via
   `numpy.linalg.lstsq` (sklearn unavailable) on real 2016-03-01..2025-06-07
   data (157,106 settlement periods).
2. `docs/calibration/price-engine.md` (Addendum) — fit-quality report:
   full-window MAE £33.96/MWh, R^2=0.386 (mean SSP £77.19/MWh); per-year
   breakdown shows R^2 ranging 0.08 (2016) to 0.295 (2022).
3. Gate: regression coefficients have physically sensible signs/magnitudes
   and the model is usable as the Regime 2 synthetic-SSP generator for
   forward projection beyond 2025-06-07, pending Rich's review of the fit
   quality above.

**[REVIEW_GATE] — CLEARED (2026-06-12).** Rich approved: R^2=0.386 is
acceptable for Regime 2 *distributional* behaviour. **Caveat (binding):**
this model is **not suitable for period-by-period price generation** — it
should be used to generate distributionally-realistic synthetic SSP series
(e.g. sampling/perturbing around its prediction plus residual variance), not
as a deterministic period-by-period price oracle. Physics-model margin-term
redesign remains a Regime 3 backlog item, not blocking this gate.

---

## Phase 3c — Physics Engine Calibration: Weather Model

**Objective:** Build and calibrate the two-pass weather engine. Validate synthetic weather against real Open-Meteo historical data for all four customer locations.

**Do not start until Phase 3b calibration is approved.** — Approved 2026-06-12, see Phase 3b above.

Deliverables:
1. `sim/weather_engine.py` — two-pass model:
   - Pass 1: national macro conditions (mean-reverting jump-diffusion, regime-switching between standard and stressed covariance matrices)
   - Pass 2: regional micro-climates via Cholesky decomposition (physically bound to national front, preserving local variation)
   - Half-hourly translation: temperature (diurnal sine wave, peak period 30/15:00, trough period 10/05:00), solar irradiance (clear-sky envelope × cloud attenuation), wind (Ornstein-Uhlenbeck process)
2. Calibration run: generate synthetic weather for 2016-2025, compare against real Open-Meteo data for all four locations
3. `docs/calibration/weather-engine.md` — calibration report

**[REVIEW_GATE] — CLEARED (2026-06-12).** Rich approved: 0.952 cross-location
temperature correlation (real vs synthetic) is "excellent" — weather engine
accepted for Regime 2.

---

## Phase 4a — Fully Synthetic Ecosystem Bootstrap

**Objective:** Combine calibrated physics engines with the evolved agent to run forward beyond 2025. First fully synthetic run.

**Prerequisites:** Phase 3b and 3c gates cleared. All records carry `data_regime` field.

**Do not design in detail until Phase 3 is complete — this is a placeholder only.**

---

## Phase 5: Smart Tariff Innovation (PLACEHOLDER - do not design in detail until Phase 4 is complete)

Introduce one smart tariff type (ToU as first candidate) and stress-test the full stack:

- Property asset layer: customer assets (EV, solar, heat pump, smart meter) by segment and location
- Behaviour model: consumption shape as a function of tariff signal, weather, and asset mix
- Dynamic forecasting: volume is no longer fixed shape - it responds to price
- Tariff-conditional hedging: hedge position depends on forecast behaviour under the tariff
- CLV under smart tariff: margin depends on how well behaviour was modelled and hedged

Key dependency: Phase 4 core value drivers must be complete on standard tariffs before Phase 5 begins.

First smart tariff candidate: ToU (time-of-use). EV and solar export follow.

This phase is where forecasting and hedging become coupled to the customer layer.

---

## Future Backlog (not yet designed — do not execute)

- Weather→consumption correlation
- Competitive pricing and churn mechanic
- Volume risk (actual vs AQ/EAC deviation)
- I&C segment
- Other countries
- EV flex / solar / battery
- VPP dispatch
- CLV model sophistication (PyMC-Marketing Shifted-BG/BG/BB)

---

## Completed Phase Index

| Phase | Description | Summary |
|-------|-------------|---------|
| 0a | Scaffold, seam, subagent roles, Elexon API | TBD |
| 0b | 4-customer portfolio, 2016 Q4 P&L = -£77.67 | TBD |
| 0c | Full 2016 P&L = -£78.28, dissatisfaction counter, CLV seed | docs/observability/phase0c-findings.md |
