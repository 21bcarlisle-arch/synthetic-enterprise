# The Synthetic Enterprise — Master Backlog

> **How this works:** Read this file at the start of every session. Execute phases in order. After each phase write `docs/observability/PHASE_<ID>_SUMMARY.md`, send an NTFY notification to `ntfy.sh/skynet-synthetic`, then proceed to the next phase automatically. Gates (`[REVIEW_GATE]`) pause execution and wait for a new instruction before proceeding.

## NTFY Protocol

Send all notifications via: `curl -d "message" ntfy.sh/skynet-synthetic`

Required notifications:
1. Session start: `"Agent started. Next phase: [ID]"`
2. Phase started: `"Phase [ID] started: [description]"`
3. Phase complete: `"Phase [ID] complete. Summary at docs/observability/PHASE_[ID]_SUMMARY.md"`
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

- Delegate all code generation and file writing to local Qwen (`qwen2.5-coder:14b` at `localhost:11434`)
- When asking for edits, supply the full current file content verbatim
- Watch for Qwen quirks: markdown fence wrapping, placeholder echoes, multi-constraint ordering slips
- Use frontier only for architecture decisions, reviewing Qwen output, genuine blockers, one-way doors

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

## Phase 1d — Hedging Strategy

Model the supplier's actual hedging position — what energy contracts back the fixed tariffs sold.

Deliverables:
1. Write `sim/hedging.py` — models the hedge book. Given acquisition date and expected volume (EAC): records hedge price and volume, computes at each settlement period: revenue (fixed tariff × volume), cost (hedge price × hedged volume + spot × unhedged volume), margin
2. Implement three hedge strategies as configurable options:
   - Strategy A (naked): 100% spot exposure — current baseline
   - Strategy B (full hedge): 100% of expected volume bought at acquisition date forward price
   - Strategy C (partial hedge): 80% at acquisition date forward price, 20% at spot
3. Run all three strategies across full 2016-2025 window — report annual P&L per strategy per customer and portfolio totals
4. Report: which strategy performed best in crisis years (2021-2022)? Which in stable years?

Constraints: hedge book lives in SIM side. Assume EAC is realised exactly for now — volume risk is Phase 2. All three strategies runnable from a single config flag.

**[REVIEW_GATE]** — write PHASE_1d_SUMMARY.md, send NTFY, then wait for instruction before proceeding.

---

## Phase 1e — Nine-Year Portfolio Run

Run the complete simulation 2016-2025 with forward curve pricing and the hedge strategy chosen at the Phase 1d gate.

Prerequisite: Phase 1d gate must be cleared and default hedge strategy confirmed before starting.

Deliverables:
1. Implement contract renewal in `saas/customers.py` — when a 1-year fixed contract ends, automatically renew at the forward curve price available at renewal date. Assume 100% renewal rate for now
2. Run full portfolio 2016-01-01 to 2025-06-07 with: forward curve pricing, chosen hedge strategy, contract renewals, all four customers
3. Report: annual P&L per customer, portfolio totals, CLV per customer accumulated, dissatisfaction events per year, worst and best years
4. Identify: did any customer CLV turn positive? Which years drove most losses? How does 2021-2022 show up?

**[REVIEW_GATE]** — write PHASE_1e_SUMMARY.md, send NTFY, then wait. This is the key Phase 1 milestone.

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
