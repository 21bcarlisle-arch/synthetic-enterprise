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

## Phase Summary Protocol

At the end of every phase write `docs/observability/PHASE_<ID>_SUMMARY.md` with:
- What was built (3-4 bullets, concrete file paths)
- Key findings (3-4 bullets)
- Key decisions made (3-4 bullets)
- Open questions (1-2 bullets)
- Token efficiency (frontier vs local tokens, what was produced)

One page, readable in 60 seconds. Commit and push before sending NTFY.

## Delegation Protocol

Two local models, routed by task type via `tools/delegate_ollama.py --task-type coder|analysis` (`localhost:11434`, one running at a time — swap, don't run both simultaneously):

**`qwen2.5-coder:14b`** ("coder" tasks — code stays local):
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

## Phase 2a — SME Segment [Run after Phase 1c, parallel with 1d]

Add one SME customer alongside the resi cohort.

Deliverables:
1. Add C5: SME, acquired 2016-01-01, London small office, Profile Class 3, EAC 25,000 kWh, `segment` = "SME"
2. Confirm `commodity` and `segment` fields are first-class in the customer schema
3. Run C5 through the same pricing, hedging, and settlement pipeline as resi — confirm no segment-specific code needed
4. Report C5 2016 P&L alongside resi cohort — note differences in shape risk profile (PC3 vs PC1)

Constraint: if any code change is needed for SME, it must be backwards-compatible with resi. No if/else on segment type in the core pipeline.

No gate. Write PHASE_2a_SUMMARY.md and send NTFY.

---

## Phase 2b — Gas Dual Fuel [BLOCKED: start after Phase 1c complete]

Add gas supply to C1-C4, making them dual-fuel.

Deliverables:
1. Research and document the best free historical NBP gas price data source back to 2016 in `docs/data-sources/gas-nbp.md`
2. Add gas commodity records to C1-C4: AQ field (not EAC), CV conversion factor (~39.5 MJ/m³), separate gas tariff pricing
3. Extend pricing and hedging pipeline to handle gas — commodity field routes to the correct price feed automatically
4. Run 2016 settlement for all four customers, both commodities — report dual-fuel P&L

Constraint: gas and electricity run through the same pipeline. Commodity is a routing field, not a code branch.

**[REVIEW_GATE]** — write PHASE_2b_SUMMARY.md, send NTFY, then wait.

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

## Phase 3b — Physics Engine Calibration: Wholesale Price Model

**Objective:** Build and calibrate the merit-order wholesale price engine. This is the first step toward Regime 3 — validate the synthetic price model against 9 years of real SSP data before trusting it for forward projection.

**Do not start until Phase 2 is complete.**

Deliverables:
1. `sim/price_engine.py` — merit-order price model:
   - Gas floor: `P_gas_floor = gas_price / thermal_efficiency` (start with `thermal_efficiency = 0.50`)
   - System margin shape: `P_HH = P_gas_floor × (demand / renewable_generation)^γ` where `γ` is parameterized between 1.5 and 2.5
   - Wind cubic physics: cut-in <3 m/s (zero), cubic ramp 3-12 m/s (P ∝ v³), rated flat 12-25 m/s, storm cut-out >25 m/s (zero)
2. Calibration run: generate synthetic prices for 2016-2025, compare against real Elexon SSP
3. `docs/calibration/price-engine.md` — calibration report: error distribution, systematic bias, γ parameter fit
4. Gate: does the calibrated engine produce price distributions that match real SSP within acceptable bounds?

**[REVIEW_GATE]** — Rich reviews calibration report before the price engine graduates to Regime 3.

---

## Phase 3c — Physics Engine Calibration: Weather Model

**Objective:** Build and calibrate the two-pass weather engine. Validate synthetic weather against real Open-Meteo historical data for all four customer locations.

**Do not start until Phase 3b calibration is approved.**

Deliverables:
1. `sim/weather_engine.py` — two-pass model:
   - Pass 1: national macro conditions (mean-reverting jump-diffusion, regime-switching between standard and stressed covariance matrices)
   - Pass 2: regional micro-climates via Cholesky decomposition (physically bound to national front, preserving local variation)
   - Half-hourly translation: temperature (diurnal sine wave, peak period 30/15:00, trough period 10/05:00), solar irradiance (clear-sky envelope × cloud attenuation), wind (Ornstein-Uhlenbeck process)
2. Calibration run: generate synthetic weather for 2016-2025, compare against real Open-Meteo data for all four locations
3. `docs/calibration/weather-engine.md` — calibration report

**[REVIEW_GATE]** — Rich reviews before weather engine graduates to Regime 3.

---

## Phase 4a — Fully Synthetic Ecosystem Bootstrap

**Objective:** Combine calibrated physics engines with the evolved agent to run forward beyond 2025. First fully synthetic run.

**Prerequisites:** Phase 3b and 3c gates cleared. All records carry `data_regime` field.

**Do not design in detail until Phase 3 is complete — this is a placeholder only.**

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
