# Synthetic Enterprise — Project Overview & Audit

*Last updated: 2026-06-30. 420+ commits. 5,623 tests passing. Codebase: ~47,500 lines across 303+ Python modules.*

**GitHub Pages (live):**
- This document: https://21bcarlisle-arch.github.io/synthetic-enterprise/PROJECT_OVERVIEW.md
- Annual report: https://21bcarlisle-arch.github.io/synthetic-enterprise/reports/ANNUAL_REPORT.md
- Assumptions: https://21bcarlisle-arch.github.io/synthetic-enterprise/market_research/ASSUMPTIONS.md
- Status: https://21bcarlisle-arch.github.io/synthetic-enterprise/status/LATEST.md

---

## 1. The Idea

Synthetic Enterprise is a high-fidelity simulation of a fully autonomous UK retail energy supplier — not a model of a company, but a running approximation of one.

The goal is to build something detailed enough that you could look at it and say *"that is how a real UK energy supplier works"* — and use it to build, test, and improve the systems that would run such a business autonomously.

**What makes it different from a financial model:**

| Financial model | Synthetic Enterprise |
|---|---|
| Spreadsheet of assumptions | Physical equations from real market mechanics |
| Annual figures | Half-hourly settlement (48 periods/day × 9.5 years = 165,000+ periods) |
| Static customer roster | Customer lifecycle: acquisition, renewal, churn, smart upgrade |
| Hypothetical prices | Real Elexon SSP data: 168,026 settlement records, 2015–2025 |
| One scenario | Continuously running; risk committee wakes on threshold breach |
| Managed by a person | Autonomous: Claude orchestrates, Qwen3 executes, no human in loop |

**The governing constraint:** the business layer cannot see future data. Every pricing, hedging, and risk decision is made using only information that a real supplier could have known at the time — enforced structurally in code, not by convention.

---

## 2. Architecture

The system has four layers, each with a clean seam to the next:

```
┌─────────────────────────────────────────────────────┐
│  BACKGROUND / AUTONOMOUS STACK                      │
│  session_watchdog · sim_runner · autonomous_runner  │
│  ntfy_responder · staging_watcher · health_check    │
└───────────────────┬─────────────────────────────────┘
                    │ orchestration & steering
┌───────────────────▼─────────────────────────────────┐
│  COMPANY LAYER (saas/)                              │
│  tariff_pricing · bill_generator · ledger           │
│  churn_model · clv_model · cost_to_serve            │
│  payment_behaviour · contact_model · growth_mandate │
│  non_commodity · customers · reporting              │
└───────────────────┬─────────────────────────────────┘
                    │ settlement records, prices, weather
┌───────────────────▼─────────────────────────────────┐
│  SIMULATION ENGINE (simulation/)                    │
│  run_phase2b · run_segments · hedged_settlement     │
│  gas_settlement · customer_events · renewals        │
│  demand_model · hh_consumption · segments           │
└───────────────────┬─────────────────────────────────┘
                    │ raw market data, physics models
┌───────────────────▼─────────────────────────────────┐
│  MARKET / PHYSICS LAYER (sim/)                      │
│  price_engine · forward_curve · hedging_strategy    │
│  risk_engine · risk_committee · weather_engine      │
│  profile_class_1/3 · system_prices_history          │
│  gas_prices_history · cache_store                   │
└─────────────────────────────────────────────────────┘
```

**Who does what:**
- **Rich (MD/board):** strategy, priorities, review. Communicates via NTFY and staging files.
- **Claude Code (orchestrator):** reads staged instructions, designs solutions, reviews output, manages build.
- **Qwen3:14b (via Ollama):** code generation and mechanical execution. All LLM calls in simulation use local Qwen — no frontier API spend in runs.

---

## 3. Real Data Used

### Electricity — Elexon Settlement System Prices (SSP)
- **File:** `sim/cache/elexon_ssp_full.json` (123 MB)
- **Records:** 168,026 half-hourly system sell price records
- **Range:** 2015-11-07 → 2025-06-07 (~9.5 years)
- **What it is:** the UK's real-time electricity imbalance price — what a supplier pays if it's short on a half-hour. Used as the spot price benchmark against which forward contracts are evaluated.
- **Captures:** the 2021–2022 energy crisis (SSP peaks >£4,000/MWh), the calm 2016–2020 period (SSP mostly £30–80/MWh), 2023 normalisation.

### Electricity — Demand & Generation History
- **Files:** `sim/cache/elexon_agws_full.json` (97 MB), `sim/cache/elexon_demand_full.json` (33 MB)
- **What it's used for:** supply/demand balance as an input to the weather-sensitive price engine; prefetched via `sim/prefetch_demand_generation.py`.

### Gas — NBP Daily Prices
- **Module:** `sim/gas_prices_history.py` (inline data)
- **Records:** 3,446 daily NBP (National Balancing Point) spot prices
- **Range:** 2016-01-01 → 2025-06-07
- **What it is:** UK wholesale gas reference price. Used for gas forward curve generation and gas term settlement.

### Weather — Open-Meteo
- **Cache:** `sim/cache/openmeteo_hourly_c1_2022.json`
- **Locations modelled:** London, Manchester, Glasgow, Cotswolds (4 weather nodes)
- **What it does:** regime-switching AR(1) temperature process with Cholesky cross-location correlation. Fitted to 2016–2025. Used to add weather sensitivity to demand shapes and forward price premia.

### Profile Class Shapes (synthetic calibrated to Elexon data)
- **PC1** (`sim/profile_class_1.py`): residential electricity. 48 half-hourly demand values per day. Calibrated to integrate to ~3,933 kWh/yr per average customer.
- **PC3** (`sim/profile_class_3.py`): SME electricity (non-half-hourly metered). Calibrated to ~13,610 kWh/yr.
- **Gas shape:** UK residential gas seasonal profile (winter-heavy).

### HH Smart Meter Data (synthetic)
- **Tool:** `tools/generate_hh_data.py`
- **Files:** `sim/hh_data/C7.csv`, `C8.csv`, `C9.csv` (three smart-meter customers)
- **What it is:** synthetic half-hourly consumption profiles that mimic real HH meter data: seasonal variation, time-of-day peaks, weather correlation, appliance-level noise.

---

## 4. Build History — Phase by Phase

### Phase 0 — Prove the Machine (early June 2026)
**What was built:** agentic loop, Elexon SSP data ingestion, basic settlement proof-of-concept.
**What it proved:** the architecture works end-to-end. Claude Code can orchestrate Qwen3 to write simulation code that runs against real data without hallucinating.

### Phase 1 — Old World Billing (resi electricity, fixed tariffs)
**Files:** `simulation/run_phase1c.py` through `run_phase1e_repriced.py`, `simulation/settlement.py`, `sim/hedging_strategy.py`, `sim/risk_engine.py`

**What was built:**
- Annual fixed-term contracts, 1-year renewal calendar
- Hedge fraction evolution: compare actual vs naked counterfactual each term, step up/down by 0.1
- Capital cost physics: VaR-based collateral cost charged on naked (unhedged) volume; dual-window (recent σ vs stressed regulatory floor)
- Context Handshake risk committee: agent wakes on VaR threshold breach, reads portfolio state, adjusts hedge fractions

**Key finding — regime-change blindness:** all 4 resi customers (C1–C4) converged toward hf=0.00 (fully naked) during the calm 2016–2020 period because spot beating forward every term. By the time the 2021–2022 energy crisis hit, they were fully naked with no capital signal to force re-hedging. Capital costs alone (Phase 1e) were insufficient to reverse this — once at hf=0.00, the counterfactual comparison becomes self-referential (same exposure → same CoC → zero signal). **This mirrors exactly how real UK suppliers failed in 2021.**

**Resolution:** Phase 5c mandates a minimum hedge floor (85%) — matching how real suppliers (EDF, Centrica) actually operate: supply obligation first, active position second.

### Phase 2 — SME Expansion + Gas
**Files:** `simulation/run_phase2a.py`, `simulation/run_phase2b.py`, `simulation/gas_settlement.py`, `saas/customers.py` (C5–C6 SME, C1g–C4g gas)

**What was built:**
- SME customers (C5: 25k kWh office, C6: 45k kWh warehouse) on PC3 profile
- Dual-fuel gas customers (C1g–C4g) with NBP price history and seasonal gas shape
- Gas term settlement: forward price based on NBP lookback + volatility premium, settled monthly against actual NBP spot
- Portfolio VaR aggregation across electricity and gas

**Key finding:** large SME customers (C6, 45k kWh) are net-negative under flat-margin pricing when capital physics applies. £6,470 capital costs exceeded £5,294 gross margin over 9.5 years. Capital cost ratio jumped from 37.6% (resi only) to 66.2% (with SME). Activity-based pricing is necessary, not optional.

**The positive finding:** large EAC (45k kWh) generates a capital cost signal loud enough to break the hf=0.00 trap — C6 was the only customer to self-correct toward higher hedging organically.

### Phase 3 — Physics Calibration
**Files:** `simulation/run_phase3b_calibration.py`, `simulation/run_phase3c_calibration.py`, `sim/price_engine.py`, `sim/weather_engine.py`, `docs/calibration/price-engine.md`, `docs/calibration/weather-engine.md`

**What was built:**
- **Price engine** (`sim/price_engine.py`): forward price = mean(SSP lookback) × seasonal multiplier + volatility premium (pstdev of daily means × risk factor). Separate summer/winter multipliers (1.2×/1.3×).
- **Weather engine** (`sim/weather_engine.py`): regime-switching AR(1) temperature model with Cholesky correlation across 4 UK locations. Fitted to 2016–2025 Open-Meteo data.
- **Weather-price sensitivity** (`sim/weather_price_sensitivity.py`): multiplier that maps temperature deviation from seasonal mean to forward price adjustment (cold spells → higher demand premium).
- **Forward curve fix** (`sim/forward_curve.py`): pstdev computed from daily means (not raw half-hourly records), reducing spurious volatility premium from ~116% to ~45% of base price.

**Calibration result:** forward prices track real SSP closely enough that the 9.5-year margin figures are stable and credible. The price engine doesn't hallucinate prices.

### Phase 4 — Customer Value Layer
**Files:** `saas/churn_model.py`, `saas/clv_model.py`, `saas/cost_to_serve.py`, `saas/home_move_win_rate.py`, `saas/contact_model.py`, `saas/enterprise_value.py`, `saas/bill_generator.py`, `saas/payment_behaviour.py`

**What was built:**
- **Bill generator:** produces itemised bills (unit rate, standing charge, non-commodity pass-through, VAT) per contract term
- **Churn model:** bill-shock driven (>20% YoY bill increase triggers churn probability); Shifted-BG CLV model via PyMC-Marketing
- **Cost-to-serve:** fixed annual overhead (billing IT, smart meter ops, regulatory levy) + variable bad-debt provision (2% resi, 1% SME)
- **Contact model:** complaint probability from bill clarity score (tariff complexity → confusion → complaints)
- **Home move win rate:** probability of retaining a customer who moves house
- **Enterprise value:** sum of CLV across billing accounts
- **Payment behaviour:** late payment model with bad-debt escalation

**Key finding:** cost-to-serve reveals activity-based pricing gap. Before CTS: net margin £13,958. After CTS (£6,460 overhead): operating net £+7,008 — still profitable, but the gap is material. Some named customers are net-negative after CTS; flagged with `NET_NEGATIVE` pricing action in the annual report.

### Phase 5 — Reporting + Mandate Redesign
**Files:** `saas/reporting/annual_report.py`, `tools/publish_report_gist.py`, `docs/reports/ANNUAL_REPORT.md`, `sim/hedging_strategy.py` (MIN_HEDGE_FLOOR), `simulation/run_phase4c_on_phase2b.py`

**What was built:**
- **`annual_report.py`** (1,400+ lines): full operator-facing annual report. Sections: executive summary, segment margin trend, whole-run hedge effectiveness, year-by-year P&L, per-customer pricing & margin, customer book, billing & payment health, risk committee, drawdown events, hedging mandate comparison (before/after Phase 5c), CLV trajectory, enterprise value, administration/insolvency section.
- **`run_phase4c_on_phase2b.py`**: single pipeline that runs Phase 2b settlement + all Phase 4 value layers (cost-to-serve, churn, CLV, home-move, enterprise value) in one pass. Produces the JSON that feeds the annual report.
- **Minimum hedge mandate (Phase 5c):** `MIN_HEDGE_FLOOR = 0.85`. Every term starts ≥85% hedged. Capital cost charged only on the unhedged 15%. Mandate comparison section in annual report shows before/after: 2021 net margin improved from −£1,096 (old reactive) to +£633 (mandate-hedged).
- **`make report`** / `make run`** / `make run-fast`**: CLI targets for report regeneration.
- **GitHub Pages publishing:** every commit to `main` triggers Pages rebuild. Annual report live in ~2 minutes.
- **NTFY completion notification:** fires after each full run with headline figures to Rich's phone.

### Phase 6 — Customer Events + HH Data
**Files:** `simulation/customer_events.py`, `simulation/renewals.py`, `simulation/hh_consumption.py`, `simulation/demand_model.py`, `tools/generate_hh_data.py`

**What was built:**
- **Customer events** (`customer_events.py`): churn events (actual departure at renewal, not just probability score); replacement onboarding (successor customer acquired when slot opens); event log fed into annual report
- **Renewals** (`renewals.py`): contract renewal decision engine — churn roll, home-move detection, bill-shock threshold
- **HH data path** (`hh_consumption.py`): C7, C8, C9 on real half-hourly consumption. `demand_model.py` dispatches between profile-class (C1–C6) and HH (C7–C9) paths.
- **HH data generation** (`tools/generate_hh_data.py`): synthetic but realistic half-hourly profiles for 3 customers, calibrated to seasonal patterns and PC1/PC3 shapes

**What this closed:** hollow gap #1 (no customer events) and hollow gap #4 (no HH data path). First time any customer has actually left the simulation.

### Phase 7 — Ledger + Payment Waterfall
**Files:** `saas/ledger.py`, `saas/non_commodity.py`, `simulation/run_phase4c_on_phase2b.py` (extended)

**What was built:**
- **Transaction ledger** (`ledger.py`): every financial event — bill raised, wholesale settled, hedge marked, non-commodity charged, VAT remitted, bad debt posted — as a timestamped journal entry with `DR/CR` accounting. 2,238,162 events in the latest full run.
- **Non-commodity costs** (`non_commodity.py`): network charges (DUoS, TNUoS, BSUoS), levies (RO, FiT, CfD, CM), standing charges — split by commodity and segment. Resi electricity: £55/MWh, SME electricity: £42/MWh, resi gas: £10/MWh.
- **Payment waterfall**: bill→payment→bad-debt escalation chain. Bad debt posts to ledger when unpaid 90 days.
- **Ledger-authoritative P&L**: headline figures (revenue, VAT, non-commodity, gross/net margin) now computed from summing ledger events, not formula. Annual report shows both ledger P&L and simulation P&L; they agree.

**What this closed:** hollow gap #2 (no ledger). Money now actually moves.

### Phase 8 — Growth Mandate
**Files:** `saas/growth_mandate.py`

**What was built:**
- Growth mandate configuration: `flat` (no active acquisition) or `growth` (targeted acquisition spend). Currently set to `flat`.
- Acquisition spend events: tracked in ledger and annual report (acquisition attempts, wins, spend).
- Fixed cost events: monthly overhead (£50/month) posted to ledger.

### Phase 9 — Bill Structure (VAT + Non-Commodity)
**Files:** `saas/non_commodity.py` (extended), `saas/bill_generator.py` (extended), `saas/ledger.py` (VAT events)

**What was built:**
- Full bill structure: commodity cost + non-commodity pass-through + standing charge + VAT. All-in customer bills now match real Ofgem bill structure.
- VAT remittance: 5% resi, 20% SME. Posted to ledger as a separate event.
- Company layer foundation (`company/`): billing invoices, CRM registry, P&L module — structural separation between the simulation environment and the company that operates in it.

**Latest run results (git 34d9cb2, 2016–2025):**
```
Customer bills (all-in):     £168,067
VAT remitted to HMRC:        (£13,907)
Revenue (ex-VAT):            £154,161
Non-commodity pass-through:  (£42,887)
Wholesale cost:              (£96,087)
Gross margin:                £15,186   (9.8% of revenue)
Capital costs:               (£1,228)
Net margin:                  £13,958   (9.1% of revenue)
Fixed overhead:              (£5,700)
Acquisition spend:           (£1,250)
Operating net:               £7,008    (profitable)
Treasury:                    £29,846 → £33,407
Ledger events:               2,238,162
Risk committee interventions: 160
Enterprise value:            −£1,635
Cost-to-serve (portfolio):   £6,460
Net after CTS:               £7,498
```

**Benchmark:** industry net margin 2–5%. SIM at 9.1% is above benchmark on commodity-only view; after overhead and CTS, operating net is 4.5% of revenue — within industry range.

### Phase 10 — Segment Customer Model
**Files:** `simulation/segments.py`, `simulation/run_segments.py`, `saas/reporting/segment_report.py`, `tests/simulation/test_segments.py`, `tests/saas/reporting/test_segment_report.py`

**What was built:**
- **`segments.py`**: `CustomerSegment` dataclass. 5 segments replacing 9 named individuals:

  | Segment | Customers | Commodity | Avg kWh | Location |
  |---|---|---|---|---|
  | resi_standard | 150 | electricity (PC1) | 3,100 | London |
  | resi_smart | 20 | electricity (PC1) | 2,800 | London |
  | sme_standard | 40 | electricity (PC3) | 35,000 | Manchester |
  | sme_smart | 5 | electricity (PC3) | 32,000 | Manchester |
  | gas_resi | 80 | gas | 13,250 | London |

- **Smart meter migration:** `apply_annual_headcount_changes()`. Each year: smart upgrades (resi_standard → resi_smart at 3–10%/yr, tracking UK rollout 2016–2025), churn (15% resi, 8% SME, 10% gas), acquisition. Non-mutating, deterministic, tested.
- **Volume:** `headcount × avg_kwh_per_customer × profile-shape-scale`. Same O(segments × periods) complexity as before; unit economics now credible at realistic headcounts.
- **Starting treasury:** £508,300 (£3,250 × 2,081,000 kWh ÷ 15,000 kWh reference — correctly sized to 295 customers).
- **`run_segments.py`**: full 2016–2025 simulation loop. Same hedging, risk committee, gas settlement, weather physics as run_phase2b — just at segment scale. Full run in progress (background, at 2017-09, treasury £531k).
- **`segment_report.py`**: standalone P&L report generator. Headcount trajectory table, per-segment unit economics (net/customer), smart-meter migration summary, year-by-year detail. CLI: `make segment-report`.

**Why segments:** the 9-customer named model has £0.17/customer/month overhead (vs £5.56 real). Segments make unit economics credible immediately — 295 customers vs 9. The model is ready for "economies of scale" analysis as headcount evolves over 9.5 years.

### Phase 11 — SIM/Company Barrier (Deep)
**Files:** `company/pricing/tariff_engine.py`, `company/crm/churn_model.py`, `simulation/run_phase2b.py` (company pricing integration)

**What was built:**
- **Company tariff engine** (`tariff_engine.py`): the company prices tariffs using only observable data — a rolling lookback mean of public SSP data, not the SIM forward curve. Returns `(unit_rate, forward_price)` where `forward_price` is the company's best estimate based on what it can see.
- **Company churn estimator** (`churn_model.py`): company estimates churn probability at renewal using bill-shock signal (YoY rate change %). Not the SIM's actual churn roll — a company-side observable-data estimate.
- **Pricing basis risk** and **churn basis risk**: recorded in `basis_risk_terms` and `churn_basis_risk` in run output. Company's observable estimate vs SIM ground truth — the gap is the basis risk.
- Both models are structurally constrained: no access to SIM internals. The company lives inside the epistemic boundary.

**What this opened:** the company now makes consequential decisions using imperfect models — which is the point. Divergence from SIM ground truth is now the primary signal for how much model risk exists.

### Phase 12 — Company CRM, Retention Offers, Divergence Tracking
**Files:** `company/crm/event_log.py`, `simulation/run_phase2b.py` (retention integration), `saas/reporting/annual_report.py` (retention + divergence sections)

**What was built:**
- **CompanyEventLog** (`event_log.py`): `ChurnEvent`, `AcquisitionEvent`, `RetentionEvent` dated artefacts. Company now has its own CRM record of customer events.
- **Pre-roll retention offers**: at each electricity renewal, if company churn estimate >30%, company makes a retention offer before the SIM rolls. Offer reduces SIM churn probability by 20%. Outcome recorded as "retained" or "churned_despite_offer".
- **Ledger retention cost**: foregone margin recorded as cash-out.
- **Margin-aware guard** (Phase 12d): offer only made when expected margin > retention cost. Crisis-year offers blocked when commodity margins collapse below the discount floor.
- **ROI analysis** (Phase 12c): `no_offer_churn_log` tracks missed opportunities; annual report shows retention P&L, ROI, and missed-opportunity breakdown.
- **Divergence tracking** (Phase 12e): `company_divergence` key in run output — year-by-year mean/max absolute error for both tariff pricing and churn estimation. Annual report "Company Model Divergence" section.
- **SIM_FAST_MODE=1**: full test suite in 16s (vs 38-min full sim run). Risk committee calls replaced with deterministic +0.10.

### Phase 13 — ToU Tariffs, Churn Model Accuracy, Seasonal Pricing
**Files:** `simulation/tou_periods.py`, `saas/tariff_pricing.py` (ToU pricing), `company/crm/churn_model.py` (bill burden), `company/pricing/tariff_engine.py` (seasonal)

**What was built:**
- **ToU tariffs** (Phase 13a): C7–C9 HH customers on time-of-use pricing. Peak (07:00-11:00, 16:00-20:00 weekdays) at 1.5× flat; off-peak at 0.786× flat; revenue-neutral at 30/70 split.
- **ToU utilization report** (Phase 13b): annual report shows per-customer peak utilization %, revenue premium vs flat equivalent. C8 (43.8% peak) earns ~+10% vs flat.
- **Bill burden signal** (Phase 13c): company churn model gains `annual_consumption_kwh` param. For high-spend customers (>£3,000 annual bill), bill stress term fires even when rate change is small. Fixed 3 "below threshold" false negatives (all large SME customers).
- **Seasonal pricing** (Phase 13d): company tariff engine — electricity winter delivery +8%, summer -4%. Fixes structural basis risk from 120-day lookback capturing wrong season.
- **Gas seasonal pricing** (Phase 13e): gas pricing fuel-aware — winter +15%, summer -8% (higher amplitude than electricity, matching real NBP heating-demand seasonality).

### Phase 14 — Adaptive Models, BESS, Bill Shock Portfolio View
**Files:** `company/pricing/tariff_engine.py` (adaptive lookback, ToU premium), `company/crm/churn_model.py` (hedge fraction), `saas/reporting/annual_report.py` (bill shock, ToU premium sections)

**What was built:**
- **Adaptive lookback** (Phase 14c): `_compute_adaptive_lookback()` in tariff engine. Crisis onset (high vol ratio) → shorten lookback to 30d floor so mean tracks current regime. Calm market → extend to 180d ceiling for smoother estimate. Expected 8–15pp tariff error reduction in 2021-22.
- **Tiered retention offers** (Phase 14a): `RETENTION_TIERS` [(≥75%→8%), (≥50%→5%), (≥30%→3%)] replaces flat 5% discount.
- **Gas churn sensitivity** (Phase 14b): `fuel` param in company churn model. Gas contracts stickier (fewer alternatives): `GAS_BASE_CHURN_RATE=0.08`, `GAS_RATE_SENSITIVITY=0.6`. `company_gas_churn_log` in run output.
- **Bill shock portfolio view** (Phase 14e): annual report aggregates `bill_shock_events` across years. Year-by-year count + worst spike; top-10 worst spikes with churn status. 274 events in latest run; worst: C2_2 2022-04-30 +1717%.
- **ToU revenue premium** (Phase 14d): annual report "ToU Premium" column — derives flat-equivalent revenue from avg_peak_rate / 1.5×; shows how much above-breakeven utilization earns.
- **Hedge fraction churn signal** (Phase 15d): `effective_rate_sensitivity = rate_sensitivity × (1 - hf × 0.4)`. Well-hedged customers less reactive to headline rate changes. Reduces 2021-22 churn overestimation.

### Phase 15 — Retention Economics Deepened
**Files:** `simulation/run_phase2b.py` (acquisition-aware guard), `saas/reporting/annual_report.py` (full ROI, gas pressure)

**What was built:**
- **Acquisition-aware guard** (Phase 15b): retention guard now `expected_margin + acq_cost_saved > ret_cost`. Unblocks crisis-year offers where margin < discount cost but avoiding acquisition is worth more.
- **Full economic ROI** (Phase 15c): retention section adds "Acquisition cost avoided" and "Full economic ROI" rows. Real cost of letting a customer walk = retention cost PLUS replacement acquisition cost.
- **Gas renewal pressure section** (Phase 15a): annual report `_section_gas_renewal_pressure()` from `company_gas_churn_log`. Year-by-year gas churn est table; elevated risk flagged; top-5 worst renewals.

### Phase 16 — Feedback Loops: Repricing, Durability, Margin Recovery
**Files:** `company/pricing/margin_feedback.py`, `simulation/run_phase2b.py` (surcharge integration), `saas/reporting/annual_report.py`

**What was built:**
- **Repricing impact assessment** (Phase 16a): annual report `_section_repricing_impact()` — for each NET_NEGATIVE customer, estimates churn risk if tariff raised to break-even. Active: repricing opportunity. Churned: retrospective counterfactual. All 6 active loss-making customers repriceable at <25% churn risk.
- **Retention durability** (Phase 16b): `_section_retention_durability()` — post-retention survival months per customer cohort. 4/7 retained customers eventually churned (avg 60 months post-retention). Shows whether retention produces durable outcomes or just delays churn.
- **Realized-margin feedback** (Phase 16c): `margin_feedback.py` — per-customer recovery surcharge (up to 20%) when prior term lost >5% of revenue. Closes the tariff feedback loop: company reacts to its own losses at each renewal. `margin_feedback_log` in run JSON.

### Phase 17 — Advanced Reporting + Portfolio Learning
**Files:** `company/pricing/tariff_engine.py` (portfolio premium), `saas/reporting/annual_report.py`

**What was built:**
- **Portfolio learning premium** (Phase 17a): `compute_portfolio_premium()` in tariff engine. If recent portfolio-wide electricity margin rates below 8% target → uplift up to +15% on all renewals; over-earning → up to -5% discount. Portfolio-wide, 4-term rolling window — slower-acting than Phase 16c surcharge. Together they form a two-speed feedback system.
- **Churn avoidability analysis** (Phase 17b): `_section_churn_avoidability()` — joins `no_offer_churn_log` with `company_event_log`. Classifies no-offer churns as "blind miss" (company_est < 30%) vs "deliberate pass" (uneconomical offer). Flags detectable blind misses (SIM p ≥ 30% while company said < 30%) — shows what the churn model's blind spots cost.
- **Per-customer lifetime P&L ranking** (Phase 17c): `_section_customer_pnl_ranking()` — ranks billing accounts by lifetime net margin. Surfaces which customers created vs destroyed value.
- **Dual-fuel account combined P&L** (Phase 17d): `_section_dual_fuel_pnl()` — pairs electricity+gas legs, shows combined lifetime margin. Flags gas accretive/dilutive per dual-fuel account. Answers: "did our gas offering add value to the relationship?"

### Phase 18–21 — Company Intelligence, Gas Calibration, Policy Costs
**Files:** `company/pricing/tariff_engine.py`, `simulation/policy_costs.py`, `simulation/hedged_settlement.py`, `saas/reporting/annual_report.py`

**What was built:**
- **Regime detection premium** (Phase 18a): `_compute_regime_premium()` in tariff engine. Compares 60d vs 180d spot price mean. Upward trend (ratio >1.10) → premium up to +15%; downward (ratio <0.90) → discount to -5%. Complements Phase 14c: 14c reacts to volatility, 18a reacts to trend direction. Expected: 2021-22 upward crisis trend → company applies 5-10% premium → reduced tariff under-pricing.
- **Gas-specific margin feedback + portfolio premium** (Phase 19a): Phases 16c and 17a extended to gas. Separate `portfolio_gas_margin_rates` tracking; `commodity` field added to all log dicts.
- **Gas risk premium** (Phase 20a): `GAS_RISK_PREMIUM_FRACTION=0.20` vs `ELECTRICITY_RISK_PREMIUM_FRACTION=0.15`. NBP basis risk is structurally higher — more volatile spot, less liquid forward market.
- **Explicit RO + CfD policy costs** (Phase 21a): `simulation/policy_costs.py` — year-indexed lookup tables for Renewables Obligation (£15.6–£31.8/MWh, 2016–2024) and CfD levy (negative in 2022 = crisis rebate). Unit rates now include policy cost pass-through at term pricing. Settlement records carry `ro_levy_gbp`, `cfd_levy_gbp`, `policy_cost_gbp` per period. Settlement uses SETTLEMENT DATE year; tariff uses TERM START year → authentic basis risk (2022 CfD rebate windfall for terms priced in 2021). Annual report `_section_policy_costs()` shows year-by-year breakdown with 2022 ⬇ CfD REBATE flag.

**R&D (Phase 21a):** Two scenario research agents documented energy market complexity and international stress scenarios. Key findings in `docs/market_research/`: negative price regime change (29→149→~1,000 hours/year peak 2027), bimodal price distribution at 70%+ renewables, UK January 2026 cold snap (£1,040/MWh), Dunkelflaute cross-border correlation, BESS market saturation. Institutional knowledge map updated with "Novel/Unseen Scenario Generation" domain.

- **Per-customer net assets solvency signal** (Phase 21b): `_section_solvency_signal()` in annual report — treasury ÷ active billing accounts each year-end. Ofgem licence floor: £0/account; capital adequacy target: £130/dual-fuel billing account. `_billing_account_id` dedup: C1g + C1 = one billing account. BREACH flag when negative; "below (gap)" when below target. 7 new tests (867 total).
- **Consumption recalibration** (Phase 21c): C1 resi 2,800→2,500 kWh/yr (Ofgem TDCV domestic medium); C5 SME small_office 25,000→15,000 kWh/yr (midrange 8,500–25,000 kWh real range). Both successors (C1_2, C5_2) updated. First-term tariff pricing and hedging now calibrated; subsequent terms self-correct via settlement-derived EAC (Phase 25a). 4 new tests (871 total).
- **Company hedging ownership** (Phase 22b): `company/risk/hedge_policy.py` — `company_evolve_hedge_fraction()` moves the hedging policy from `sim/hedging_strategy.py` to the company layer. `run_phase2b.py` now imports from `company.risk.hedge_policy`. Level 2 (decision boundary) separation CLOSED for hedging. `sim/hedging_strategy.py` preserved for historical runners. 8 new tests (879 total).
- **Second I&C customer** (Phase 27a): C_IC2 commercial office building — 1 GWh/year, Birmingham, acquisition 2018-01-01, "I&C" segment. `sim/hh_data/C_IC2.csv`: peak 135 kWh/period (08:00-18:00 Mon-Fri), +15% summer cooling (Jun-Aug), 30% Saturday, 8% Sunday. C_IC1 segment corrected "SME"→"I&C". Total ELEC EAC ~3.1 GWh; starting treasury £678k. 9 new tests (888 total).
- **CCL for business electricity** (Phase 27b): `simulation/policy_costs.py` adds `get_ccl_per_mwh()` — CCL exempt for resi domestic, main rate (£5.44→£7.35/MWh 2016-2024) for SME/I&C. April 2020 step-change correctly applied. CCL year Apr-Mar (same as RO obligation year). `run_hedged_term()` gains `segment` param; `ccl_gbp` recorded per settlement period; `policy_cost_gbp = ro + cfd + ccl`. Annual report `_section_policy_costs()` adds CCL column when non-zero (backward compatible). 9 new tests (897 total).
- **Volume tolerance tracking** (Phase 27c): `simulation/volume_tolerance.py` — `compute_term_volume_tolerance()` computes actual vs contracted ±10% at each I&C term end. Excess above +10% band costs spot; deficit below -10% triggers hedge unwind at spot (P&L = (spot-hedge_price) × hedged_deficit_kwh). `volume_tolerance_log` in run output; `_section_volume_tolerance()` in annual report with ⚠ breach flag. 12 new tests (909 total).
- **Triad risk** (Phase 27d): `simulation/triad.py` — `identify_triad_candidates()` (top-3 highest SSP periods Nov-Feb, ≥10 days apart) + `compute_triad_exposure()` (demand_kw × TNUoS tariff £/kW/year). `_TNUOS_TRIAD_TARIFF_BY_YEAR`: £46.23→£63.82/kW 2016-2024. Computed after term loop for each winter × each I&C customer; `triad_log` in run output; `_section_triad_exposure()` in annual report. 15 new tests (924 total).
- **I&C churn model** (Phase 27e): `company/crm/churn_model.py` gains `IC_BASE_CHURN_RATE=0.20`, `IC_RATE_SENSITIVITY=1.5`, `IC_TENURE_DISCOUNT_PER_YEAR=0.005`, `IC_BILL_STRESS_THRESHOLD_GBP=50,000`. `estimate_churn_probability()` gains `segment` param; I&C uses broker-driven constants. `run_phase2b.py` passes `segment=segment_for_churn` at electricity renewal. 6 new tests (930 total).
- **I&C portfolio summary** (Phase 28a): `_section_ic_portfolio()` in annual report — lifetime P&L, CCL/MWh, TNUoS Triad exposure, volume tolerance summary, year-by-year segment comparison (I&C vs SME vs Resi). Identifies I&C customers from CUSTOMERS module (`segment == "I&C"`) — not CCL proxy (fixed in 99e0b33: CCL proxy also matched C5 SME). 6 new tests (936 total, 907 non-integration).
- **Network charges DUoS + TNUoS** (Phase 29a): `simulation/policy_costs.py` adds `get_electricity_network_cost_per_mwh(date_str, segment)` — resi/SME combined DUoS+TNUoS unit rate, I&C HV DUoS-only (Triad TNUoS separate). `run_hedged_term()` records `network_cost_gbp` per period; `net_margin_gbp = margin_gbp - policy_cost_gbp - network_cost_gbp - capital_cost_gbp`. `price_fixed_tariff()` gains `network_cost_per_mwh` param. Annual report `_section_network_costs()` backward-compatible. 15 new tests.
- **Network charge calibration** (Phase 29b): `_NETWORK_COST_RESI_SME_BY_YEAR` recalibrated from Ofgem Annex 9 v1.10. Key change: 2022 £43→£66/MWh — BSUoS moved 100% to demand side from April 2022 (previously 50/50 demand/generator). Calibrated series: 2016: £43, 2017: £44, 2018: £42, 2019: £45, 2020: £46, 2021: £49, 2022: £66, 2023: £75, 2024: £69 (£/MWh). 907 non-integration tests passing in 7.74s.
- **Gas policy costs: gas CCL, gas network, GGL** (Phase 30b): `simulation/policy_costs.py` adds `_GAS_CCL_RATE_BY_YEAR` (£1.95–7.75/MWh, 2016–2024, HMRC Table 1; resi exempt; 2019 Budget 2016 rebalancing step), `_GAS_NETWORK_COST_BY_YEAR` (£9.0–17.6/MWh, all segments; 2023 peak = RIIO-GD2 + SOLR), `_GGL_RATE_GBP_PER_METER_YEAR` (per-MPRN normalised to £/MWh via AQ; 0 before 30 Nov 2021; all segments). `simulation/gas_settlement.py` adds `gas_ccl_gbp`, `ggl_gbp`, `gas_policy_cost_gbp`, `gas_network_cost_gbp` per record; `net_margin_gbp` deducts policy + network. `run_phase2b.py` passes gas CCL + GGL + network through at tariff pricing. Annual report `_section_gas_policy_costs()` (backward compatible). Research: `docs/market_research/gas_policy_costs_2016_2024.md`. 33 new tests (981 non-integration passing).
- **Active/passive split reporting** (Phase 33b): `saas/reporting/annual_report.py` adds `_section_active_passive_renewal()` — total active/passive counts with mean company estimates and abs errors per type, year-by-year table. Silent on pre-Phase-33a data (backward compatible). 6 new tests (1,047 passing).
- **Active/passive renewal split** (Phase 33a): `company/crm/churn_model.py` adds `is_active_renewal()` (35% active, 65% passive SVT-rollers; 2022 crisis forced passive), `estimate_passive_churn_probability()` (5% base, 0.1 rate sensitivity, 10% cap — SVT-inertia model). `simulation/customer_events.py`: `passive_churn_cap` param on `roll_lifecycle_event()` — caps SIM ground-truth churn for passive renewers. `run_phase2b.py`: draws active/passive at each electricity renewal; I&C always active (brokers shop every renewal). `churn_basis_risk` output includes `is_active_renewal` field. Effect: 65% of renewals get ~5% churn estimate (not 10-40%); fewer spurious retention offers; SIM churn capped at 10% for passive. 10 new tests (1,041 passing).
- **Gas book year-by-year P&L + commodity_split revenue/wholesale** (Phase 32a): `saas/reporting/annual_report.py` adds `_section_gas_pl(data)` — 8-column table (Year | Revenue | Wholesale | Gross | Policy | Network | Capital | Net | Net%) silent when no gas records. `commodity_split` loop now includes `revenue_gbp` and `wholesale_cost_gbp` per commodity. R&D: `docs/market_research/svt_rates_active_passive_2016_2025.md` — SVT unit rates 2016–2025, active/passive split (~35%/65%), crisis period dynamics, Phase 33 candidate identified. 11 new tests (1,031 non-integration passing).
- **Feed-in Tariff (FiT) levy** (Phase 31a): `simulation/policy_costs.py` adds `_FIT_LEVY_BY_YEAR` (£4.10–8.47/MWh, 2016–2024) and `get_fit_levy_per_mwh()`. FiT applies to ALL demand (no domestic exemption); `policy_cost_gbp = RO + CfD + CCL + CM + FiT`. Source: npower reconciled rates 2021-2024; Ofgem FiT Annual Reports 2019-2020; triangulated 2016-2018. Key: 2021 dip (£6.01/MWh — lower tariffs on newer post-2016 installs); 2024 £8.47/MWh (initial billing, TBC Nov 2026). Annual report 6-column policy costs table (backward compatible). Research: `docs/market_research/fit_levy_2016_2024.md`. 20 new tests (943 non-integration passing).
- **Capacity Market (CM) levy** (Phase 30a): `simulation/policy_costs.py` adds `_CM_LEVY_BY_YEAR` (£0.5–7.27/MWh, 2016–2024, Ofgem Annex 9 v1.8) and `get_cm_levy_per_mwh()`. CM applies to ALL demand segments — no domestic exemption unlike CCL. `policy_cost_gbp = RO + CfD + CCL + CM`. Tariff pass-through in `renewals.py`. Annual report `_section_policy_costs()` adds CM column (backward compatible). Key: 2021 cheapest (£4.67/MWh — cheap 2017 T-4 auction at only £8.40/kW); 2024 £7.27/MWh and rising. Research: `docs/market_research/capacity_market_levy_2016_2024.md`. 16 new tests (923 non-integration passing).

### Phase 22 — Post-Crisis Churn Hangover + Trailing-Margin CLV
**Files:** `company/crm/churn_model.py`, `saas/clv_model.py`, `simulation/run_phase2b.py`, `saas/reporting/annual_report.py`

**What was built:**
- **Crisis churn hangover** (`CRISIS_HANGOVER_BASE_UPLIFT=0.12`): +12pp churn when company observes prior-term net loss >20% of revenue; persists 2 renewal periods via `hangover_remaining` dict
- **Trailing-margin CLV** (`override_avg_margin_by_account` param): enables CLV variants using recent observed margin without rerunning settlement
- **EV analysis section** (`_section_enterprise_value_analysis()`): full-history EV vs 3yr-trailing EV; year-by-year net margin; per-account CLV comparison

**What this fixed:** 2024 failure mode — falling post-crisis rates collapse the rate-change signal to near-zero even for financially-stressed large-SME customers. Hangover mechanism fires on *observed losses* rather than rate change, catching customers the rate-only model misses. 22 new tests (826 total).

### Phase 23 — Company-Owned Demand Estimation
**Files:** `simulation/run_phase2b.py` (`_company_eac_estimate()`), `saas/reporting/annual_report.py` (`_section_demand_estimation()`)

**What was built:**
- **`_company_eac_estimate()`**: sums prior-year billing records (12 months before term start) for EAC estimate; falls back to SIM oracle only on first term (no prior billing)
- **Three `EFFECTIVE_EAC_KWH` oracle reads eliminated**: bill-burden churn signal, retention economics, missed-opportunity analysis — all now use company-observed billing history
- **`demand_estimation_log`** in run output: per-renewal company estimate vs SIM oracle (error_pct, source — "billing_history" or "oracle_fallback")
- **`_compute_company_divergence()`** extended with `demand_error_by_year` alongside tariff and churn error tracking
- **`_section_demand_estimation()`** in annual report: year-by-year mean/max abs error; prior-billing vs oracle fallback count; backward-compatible (silent when log absent)

**What this closed:** epistemic honesty violation — the company was reading SIM oracle EAC for three consequential decisions instead of observing its own billing records. Company demand estimation is now fully observable-data only. 12 new tests (838 total).

### Phase 24 — I&C Customer (First Industrial Account)
**Files:** `saas/customers.py` (C_IC1 customer record), `sim/hh_data/C_IC1.csv` (2 GWh HH data), `tests/simulation/test_phase24a_ic_customer.py`

**What was built:**
- **C_IC1**: 2 GWh/year I&C electricity customer, HH metered, Birmingham, acquired 2017-01-01
- **HH data**: `sim/hh_data/C_IC1.csv` — C7's shape scaled by 156× to ~2 GWh/year (3,446 days)
- **EAC derivation**: `EFFECTIVE_EAC_KWH["C_IC1"]` auto-computed from HH data via `estimate_annual_kwh()`
- **Churn saturation**: bill-stress term immediately saturates at `MAX_CHURN_PROBABILITY=0.95` for any plausible rate (£300k/year bill >> £3k threshold). Retention offer always made if margin > cost.
- **Scale-invariant economics**: starting treasury scales to £463k (from £30k) — adequate for I&C working capital. Retention cost proportionally large (5% = £15k per offer).

**What this proved:** the HH path, company tariff engine, retention system, and demand estimation all scale correctly to I&C volumes without code changes. 2021-22 crisis will show C_IC1 with large crisis losses (£400/MWh spot × 2 GWh unhedged exposure). 8 new tests (846 total).
### Phase 25 — EAC Calibration from Settlement + Solar Irradiance Wiring
**Files:** `simulation/run_phase2b.py` (`_derive_eac_from_settlement()`), `simulation/weather_inputs.py`, `tests/simulation/test_phase25a_eac_solar.py`

**What was built:**
- **`_derive_eac_from_settlement()`**: computes mean annual kWh from prior-year settlement records; 180-day minimum coverage guard; falls back to `EFFECTIVE_EAC_KWH` when insufficient data
- **`true_eac_kwh` in demand_estimation_log**: now reflects actual settled consumption (not declared EAC), closing the oracle read in Phase 23a's per-renewal comparison
- **Hedging block**: EAC now from `_company_eac_estimate()` (settlement-derived on renewal 2+), so hedging quantities calibrate from observed consumption not declared capacity
- **`load_weather_cloud_cover()` + `cloud_cover_for_customer()`** in `weather_inputs.py`: load half-hourly cloud cover data; C4 (solar rooftop) irradiance wired via `_weather_adjusted_shape_fn cloud_cover_means`

**What this closed:** the hedging model was still reading declared EAC rather than calibrating from actual settlement records — underestimating demand for growing customers. Solar irradiance now reduces C4 consumption on high-sun days. 8 new tests (854 total).

### Phase 43a — Company Trading Book (2026-06-23)
**Files:** `company/trading/forward_book.py`, `simulation/run_phase2b.py`, `tests/company/test_forward_book.py`

**What was built:**
- `ForwardContract` (frozen dataclass): customer_id, term_start, term_end, notional_mwh, agreed_price_gbp_per_mwh, hedge_fraction.
- `TradingBook`: `open_hedge()` at tariff signing; `settle_period()` computes hedge P&L per half-hour; `summary()` in run output.
- `simulation/run_phase2b.py`: for each fixed/pass-through electricity term, opens a ForwardContract (agreed_price = company_fwd — the company's own tariff engine output) and calls `settle_period()` per record, adding `hedge_pnl_gbp` field.
- Epistemic compliance: agreed_price comes from the company's own forward price calculation (published market data only — no SIM internals).

**Fidelity delta:** The company now runs a trading book. Hedge gain/loss is decomposed from supply margin per settlement period. 1-year fast run: 93 contracts, 44,196 MWh hedged, £406k hedge P&L.

**14 new tests (1,242+ total).**

### Phase 47a — Ofgem Domestic Price Cap (2026-06-24)
**Files:** `company/pricing/ofgem_price_cap.py` (new), `simulation/run_phase2b.py`, `tests/company/pricing/test_phase47a_ofgem_cap.py` (new)

**What was built:**
- `company/pricing/ofgem_price_cap.py`: `get_cap_unit_rate_gbp_per_mwh(fuel, year)` — annual lookup table, £/MWh, electricity and gas. Pre-2019: returns None (no cap). 2019: elec £165, gas £26. 2022 crisis peak: elec £305, gas £95 (EPG). 2024 normalisation: elec £210, gas £55.
- `simulation/run_phase2b.py`: After all uplifts (portfolio premium, margin surcharge, profitability uplift), clamp `unit_rate = min(unit_rate, cap)` for resi fixed-term customers when `year >= 2019`. Applied to both electricity and gas. I&C and SME customers are unaffected.
- `_RESI_CUSTOMER_IDS` frozenset at module level for O(1) segment lookup.

**Fidelity delta:** Domestic supply was loss-making sector-wide 2019-2022 (CSS data: EDF dom elec -6.1% gas EBIT 2023, -5.4% 2024; resi sector -4% to -10% 2021-2022). The SIM resi margin of 10.2% was impossible post-2019 under the cap. The cap now compresses resi margins in crisis years (2021-2023) matching real-world supplier experience. Closes "CRITICAL GAP" flagged in ASSUMPTIONS.md.

**10 new tests (1,260+ total).**

---

### Phase 47b — Cap-Aware Acquisition Gate (2026-06-24)
**Files:** `saas/growth_mandate.py`, `simulation/run_phase2b.py`, `tests/simulation/test_phase47b_acquisition_gate.py` (new)

**What was built:**
- `should_attempt_acquisition(segment, commodity, company_fwd_gbp_per_mwh, date_str)` in `saas/growth_mandate.py`: returns `(bool, reason | None)`. Gate fires for resi electricity when Ofgem cap < company_fwd (company would sell below wholesale cost). Non-resi and gas always proceed.
- `simulation/run_phase2b.py`: gate check before `roll_acquisition()` in churn block. Gate logs `acquisition_gate_event` to `acquisition_spend_events` with `gate_reason` field (£0 cost, no roll). Gate passes → existing roll logic unchanged.

**Fidelity delta:** Crisis-year domestic acquisition pause (2021-2023) now emerges as a rational company decision from observable economics, not a hard-coded rule. Real suppliers (Octopus, EDF, BG) paused domestic acquisition 2021-2023 when the EPG/cap made every new resi customer loss-making. The SIM company now makes the same rational choice: if the cap forces us to price below cost, don't try to acquire.

**10 new tests (1,270+ total).**

---

### Phase 53 — BSC Credit Cover as Working Capital Requirement (2026-06-25)
**Files:** `saas/capital/bsc_credit.py` (new), `saas/reporting/annual_report.py`, `tests/saas/capital/test_bsc_credit.py` (new)

**What was built:**
- `saas/capital/bsc_credit.py`: `compute_daily_wholesale_exposure(records)` — aggregates electricity wholesale_cost_gbp by settlement date (gas excluded; gas settlement under Xoserve/Gemserv, not BSC). `compute_bsc_credit_requirement(daily_exposure, window_days=28, buffer=1.2)` — rolling peak × buffer. `compute_bsc_credit_by_year(records)` — per-year dict with `peak_daily_wholesale_gbp`, `credit_cover_required_gbp`, `days_with_data`.
- `annual_report.py` `extract_report_data()`: pre-computes `bsc_credit_by_yr` from `all_records` (while in scope), stores `bsc_credit_required_gbp` and `bsc_peak_daily_gbp` per year in the `years` dict. New `_section_bsc_credit(data)` section in the annual report.
- Annual report output: per-year table (Peak Daily / Credit Cover / Treasury / Coverage Ratio / Status). Coverage < 5× flagged as "Watch"; < 2× as "STRESS". Crisis signature: 2022 peak daily £8,498 (£10,198 credit cover) vs 2016 £23 (£28) — 363× higher.

**Fidelity delta:** BSC credit cover is a real working capital obligation for every UK licensed supplier. Elexon collects credit cover to protect against default — the requirement spikes when SSP spikes, creating a capital squeeze exactly when margins are compressed. This is why 100+ small suppliers failed in 2021-2022: their BSC credit demands exceeded available capital. The simulation now tracks this per year and signals stress when coverage drops below 5×.

**14 new tests (1,369 total).**

---

### Phase 54 — Supplier Mutualization Levy (2021-2022 failure wave) (2026-06-25)
**Files:** `simulation/policy_costs.py`, `simulation/hedged_settlement.py`, `saas/reporting/annual_report.py`, `tests/simulation/test_mutualization_levy.py` (new)

**What was built:**
- `simulation/policy_costs.py`: `_MUTUALIZATION_LEVY_BY_YEAR` dict (2016–2024, £/MWh) + `get_mutualization_levy_per_mwh(date_str)`. Crisis values: 2021 £4.14/MWh (17 SoLR events, ~£1.2bn mutualized), 2022 £10.00/MWh (Bulb Special Administration Regime + BSC shortfall recovery, ~£2.9bn), 2023 £1.38/MWh (residual SAR wind-down). Pre/post-crisis years: £0.00/MWh.
- `simulation/hedged_settlement.py`: mutualization levy applied in all 3 electricity settlement paths (fixed/pass-through hedged, deemed, flex/trading). Added to `policy_cost_gbp` total and recorded as `mutualization_levy_gbp` per record.
- `saas/reporting/annual_report.py`: `extract_report_data()` aggregates `mutualization_levy_gbp` per year. `_section_policy_costs()` updated to include Mutualization column in the policy table (conditionally shown when non-zero).

**Fidelity delta:** When a licensed electricity supplier fails in the UK, their Renewable Obligation shortfalls, CfD underpayments, and BSC clearing obligations are mutualized across surviving suppliers pro-rata to metered volume. The 2021-2022 crisis triggered ~180 supplier SoLR events, creating a retroactive £10+/MWh levy in 2022 — a hidden cost that devastated margins for suppliers who hadn't priced it in. The simulation now tracks this as a real policy cost that spikes in crisis years, materially compressing net margins in 2021-2022.

**8 new tests (1,377 total).**

---

### Phase 56 — Gas Pass-Through Hedge Zero-Lock (2026-06-25)
**Files:** `simulation/run_phase2b.py`, `tests/simulation/test_gas_pass_through_hedge.py` (new)

**What was built:**
- `simulation/run_phase2b.py`: gas pass-through customers now force `hf = 0.0` at every term renewal, overriding the 0.85 RESET_HEDGE_FRACTION default. VaR decision block only runs for fixed-rate gas customers. `current_hf[cid]` is set to 0.0 before `run_gas_term()`.
- `tests/simulation/test_gas_pass_through_hedge.py`: 5 tests verifying zero-hedge margin stability vs non-zero-hedge wrong-way risk (windfall on spot spike, loss on spot reversion).

**Fidelity delta:** Removes a systematic wrong-way risk from the gas settlement. C_IC3g (5 GWh I&C spot-indexed gas, chemical plant, Teesside) was being hedged at 85% despite billing at daily spot price — this created a £125k windfall in 2021 (spot > forward) and a -86% net gas margin in 2023 (spot < expensive 2022 forward lock). A real supplier on a spot-indexed I&C gas contract would NOT hedge that book with a fixed forward — the customer bears the price risk. Now margin ≈ service_fee + network + policy per MWh, stable across spot regimes.

**5 new tests (1,394 total).**

---

### Phase 63 — F1 Double-Entry Ledger (2026-06-25)
**Files:** `company/finance/double_entry.py` (new), `tests/company/finance/test_double_entry.py` (new)

**What was built:**
- `company/finance/double_entry.py`: Chart of accounts (ACCOUNTS dict, 13 codes across 1xxx–6xxx ranges), `to_journal_entry()` translating all 9 existing ledger event types to DR/CR pairs, `build_journal()` with opening treasury entry, `account_balances()`, `trial_balance()` (DR == CR verification), `income_statement()` and `balance_sheet()` emerging from accounts.
- Every financial event now posts as a proper DR/CR pair: billing (DR Trade Receivables / CR Revenue), settlement (DR Wholesale / CR Cash), payment (DR Cash / CR Receivables), VAT remittance (DR Revenue / CR Cash), bad debt (DR Bad Debt Expense / CR Receivables), etc.
- `balance_sheet()` verifies Assets = Liabilities + Equity at period end. `income_statement()` cross-verified against existing `saas.ledger.derive_pnl()` — revenue, wholesale, gross margin agree.

**Fidelity delta:** The company now has a real double-entry accounting system. Previously: margin tracker with event log. Now: P&L and balance sheet emerge from account balances, trial balance reconciles, Assets = Liabilities + Equity holds for any valid journal. This is the foundational F1 item from Destinationvision.md — all subsequent financial infrastructure (FI1 management accounts, C1 invoice documents, FI2 budget vs actual) builds on this.

**24 new tests (1,480 total).**

---

### Phase 64 — FI1 Management Accounts from Double-Entry Journal (2026-06-25)
**Files:** `company/finance/management_accounts.py` (new), `tests/company/finance/test_management_accounts.py` (new), `saas/reporting/annual_report.py` (extended)

**What was built:**
- `company/finance/management_accounts.py`: `build_monthly_accounts()`, `annual_management_pack()`, `cross_check()` (journal vs sim net, <=5%).
- Annual report: 10-year P&L table + final-year balance sheet + cross-check vs simulation net.
- P&L and balance sheet emerge from double-entry account codes (4xxx=revenue, 5xxx=COGS, 6xxx=opex) not formulas.

**Fidelity delta:** Management accounts from double-entry journal. Foundation for FI2 budget vs actual.

**13 new tests (1,493 total).**

---

### Phase 66 -- C1 Invoice Line Items and Text Format (2026-06-25)
**Files:** `company/billing/invoice.py` (extended), `tests/company/billing/test_invoice.py` (extended)

**What was built:**
- Schema extended: `commodity_amount_gbp`, `non_commodity_amount_gbp` columns added (with ALTER TABLE migration for existing DBs).
- `create_invoice()` fixed: reads `standing_charge_gbp`, `non_commodity_amount_gbp`, `vat_gbp` from bill when available (Phase 9a+ bills); falls back to total_amount_gbp for legacy bills.
- `format_invoice_text(invoice)`: renders structured text invoice with energy charge, standing charge, network & levies, VAT, total, period, account, payment status.

**Fidelity delta:** Invoice documents now contain full line-item breakdown (energy, standing charge, network/levies, VAT). Previously: only total stored, standing charge hardcoded to 0. C1 real invoice documents now operational.

**9 new tests (1,514 total).**

---


---
### Phase 255 -- Customer Satisfaction Survey (CSS) tracker (2026-06-26)
**Files:** `company/crm/css_tracker.py` (new), `tests/company/crm/test_css_tracker.py` (new)

**What was built:**
- CSSPerformanceBand: TOP (≥7.8) / MID (6.0-7.8) / BOTTOM (<6.0).
- Historical industry averages: 2016-2025, with 2022 at 5.2/10 (crisis nadir).
- CSSResponse frozen: 6 dimensions (overall/billing_accuracy/ease_of_contact/value_for_money/meter_accuracy/complaint_handling); composite_score (overall 30%, others 14%); would_recommend (≥7.0); validation (1-10 range).
- CSSBook mutable: record_response(), annual_responses(), avg_score(year, dimension), performance_band(), vs_industry_avg(), recommend_rate(), css_summary().

**Fidelity delta:** Ofgem publishes annual CSS rankings and uses bottom-quartile performance as an "Enhanced Monitoring" trigger. The 2022 crisis dropped the industry-wide score to 5.2/10 — even suppliers that didn't collapse faced formal monitoring. vs_industry_avg() positions the supplier on the league table: a supplier at 5.5/10 in 2022 is actually +0.3 above average despite crisis conditions, which is meaningful for regulatory risk assessment. recommend_rate() feeds into NPS (Net Promoter Score) tracking — a key board KPI. Connects to ComplaintRegister (Ph218), ContactJourney (Ph244), and NPSTracker for a complete customer experience picture.

**Phase 256 -- Day-ahead electricity trading book (N2EX/EPEX SPOT UK) (2026-06-26)**
**Files:** company/market/day_ahead_book.py (new), tests/company/market/test_day_ahead_book.py (new)

**What was built:**
- DayAheadDirection: BUY / SELL.
- DayAheadAuction frozen: auction_id/delivery_date/direction/volume_mwh/bid_price_gbp_per_mwh/cleared_price_gbp_per_mwh/auctioned_at.
  Properties: cost_gbp (BUY=positive/SELL=negative), vs_forward_spread_gbp_per_mwh, is_crisis_price (>300 GBP/MWh).
- DayAheadBook: submit_auction() (validates volume>0 and auctioned_at before delivery_date), auctions_for_month(),
  net_position_mwh(), total_volume_mwh(), total_cost_gbp(), average_clearing_price() (volume-weighted),
  crisis_auctions(), monthly_summary(), day_ahead_summary().

**Fidelity delta:** N2EX day-ahead auction is the largest UK electricity market by volume. Suppliers buy ~60-70% of
daily energy in a once-daily clearing at ~11:00 CET for the following delivery day. Previously the company had
forwards (weeks ahead) and intraday (same day) but no day-ahead layer. Phase 256 closes this gap: trading
timeline is now complete: forwards -> day-ahead -> intraday -> BM. 2022 crisis: under-hedged supplier buying
100 MWh/day at DA 450/MWh pays 45,000/day vs 4,500 normal. vs_forward_spread tracks the DA premium over hedge.

**15 new tests (3,388 total).**

---
**Phase 257 -- Run Insight Generator / so-what layer (2026-06-26)**
**Files:** tools/generate_insights.py (new), tests/test_insights.py (new), background/process_run_complete.py (modified)

**What was built:**
- InsightArea enum: TRADING / CUSTOMERS / RISK / FINANCIAL / OPERATIONS.
- AreaInsight frozen dataclass: area, headline (one sentence), narrative (2-3 sentences), key_metrics (dict).
- RunInsights frozen dataclass: git_hash, generated_at, net_margin_gbp, executive_summary, insights tuple.
- generate_insights(): computes structured "so what" for all 5 areas from run output JSON.
- save_insights(): writes docs/observability/run_insights.json (current run snapshot).
- append_run_history(): accumulates docs/observability/run_history.json (one entry per run, deduplicates by git_hash).
- Integrated into process_run_complete.py: runs automatically after every sim run, before commit.

**Fidelity delta:** After every full sim run, the business generates a structured interpretation of its
own results. Executive summary from latest run: "Business survived the full 2016-2025 window including
the 2021-22 crisis. Net margin £6,322,836 (33.2% of revenue -- above 2-5% benchmark). Hedging cost
£4,044,933 vs going naked. 445 bill shock events (107 in crisis years); 17/18 retention offers accepted."
Direct response to Dashboardvision.md Phase A (Level 2 insight layer).

**15 new tests (3,403 total).**

---
**Phase 258 -- Dashboard Insights tab (2026-06-26)**
**Files:** site/index.html (modified), tools/generate_dashboard_data.py (modified), tests/tools/test_generate_dashboard_insights.py (new)

**What was built:**
- extract_insights() in generate_dashboard_data.py: loads run_insights.json into dashboard dict as D.insights.
- Insights tab added to poesys.net dashboard: nav button, view div, renderInsights() JS function.
- renderInsights() renders executive summary banner + 5 area cards (headline, narrative, key metrics).
- 4 new tests: absent path returns None, valid JSON returns dict, invalid JSON returns None, all 5 areas present.
- Direct response to Dashboardvision.md Phase A frontend: Level 2 insight layer now visible on dashboard.

**4 new tests (3,407 total).**

---
**Phase 259 -- Level 3 Coherence Executive Summary (2026-06-26)**
**Files:** tools/generate_insights.py (modified), tests/test_insights.py (modified), site/index.html (modified)

**What was built:**
- RunInsights extended: coherence_narrative (str) + recommended_actions (tuple, always 3).
- _generate_coherence(): reads 5 area insights, identifies dominant theme (crisis/concentration/hedging/steady-state), generates cross-area narrative paragraph, builds 3 action recommendations.
- PCL segment fix: uses cv.get("segment") == "I&C" + net_gbp fallback key (real data had different field names than test fixture).
- Dashboard Insights tab: Level 3 coherence card (teal border, cross-area synthesis) + Recommended Actions card (amber border, numbered list).
- 6 new tests: coherence present, 3 actions, survival mention, IC flagged, save/reload, hedge mention.
- Dashboardvision.md Phase C backbone: executive coherence summary live on poesys.net.

**6 new tests (3,413 total).**

---
**Phase 260 -- Strategic Coherence Infrastructure (2026-06-26)**
**Files:** docs/PRIORITIES.md (new), site/staging-status/index.html (new), site/timeline/index.html (new), docs/status/LATEST.md (updated), CLAUDE.md (updated)

**What was built:**
- docs/PRIORITIES.md: living priority file with Now/Next/Staged/Backlog/On-hold/Recently-completed sections. Standing rule: updated each session.
- site/staging-status/index.html: live view of docs/staging/ (staged) and docs/staging/done/ (actioned). Published to poesys.net/staging-status/.
- site/timeline/index.html: 299-phase git-log-extracted timeline table. Two velocity charts: phases-over-time and tests-over-time (705-3,413 test progression). Investor summary card. Published to poesys.net/timeline/.
- Coherence_and_velocity.md archived: instruction actioned.
- PRIORITIES.md standing instruction added to CLAUDE.md checklist.

**0 new tests (3,413 total) -- infrastructure only.**

---
**Phase 261 -- Year Spotlight (Dashboard Phase B partial) (2026-06-26)**
**Files:** site/index.html (modified), tests/tools/test_year_spotlight.py (new)

**What was built:**
- YEAR_FILTER state variable (null = all years, int = selected year).
- year-btn / spotlight CSS classes.
- selectYear(): toggles YEAR_FILTER, updates button active states, re-renders spotlight.
- renderSpotlight(): builds spotlight card with 8 KPIs from D.financial.annual, D.customers.book_annual, D.trading.hedge_annual. CRISIS YEAR badge for 2021/2022.
- Overview tab: year selector buttons row (2016-2025 + All) + spotlight container.
- 5 new tests: all 10 years in financial/hedge annual; crisis years in book_annual; bill_shock_count > 0 in 2022; 2022 shocks >= 2020.
- Dashboardvision Phase B partial: year drill-down live on poesys.net.

**5 new tests (3,418 total).**

---
**Phase 262 -- Run History Table (Dashboard Phase B) (2026-06-26)**
**Files:** tools/generate_insights.py (modified), tools/generate_dashboard_data.py (modified), site/index.html (modified), tests/tools/test_run_history.py (new)

**What was built:**
- `append_run_history()` guards: skips non-hex hashes and net_margin_gbp <= 0 (blocks test artifacts from polluting run_history.json).
- `extract_run_history(history_path, max_entries=10)` in generate_dashboard_data: returns last N run history entries or [].
- Dashboard JSON now includes `run_history` key.
- Insights tab: Run History table (hash, net margin, date) rendered below recommended actions.
- Cleaned test artifact entries from docs/observability/run_history.json.
- 6 new tests: fake-hash guard, negative-margin guard, real-hash writes, max_entries slice, missing-file empty, dashboard key present.

**6 new tests (3,424 total).**

---
**Phase 263 -- Four-Section Site Restructure (poesys.net) (2026-06-26)**
**Files:** site/customers/index.html (new), site/project/index.html (new), site/data/customers/*.json (new), site/data/phases.json (new), tools/generate_customer_data.py (new), background/process_run_complete.py (modified), site/index.html (modified), site/timeline/index.html (modified), site/staging-status/index.html (modified)

**What was built:**
- Persistent site-wide navigation bar (Supplier / Customers / Project / SIM-stub) added to all 4 HTML pages.
- /customers/: static SPA portal -- login by account ID, shows tariff/meter type, acquisition date, lifetime P&L (revenue/gross/net/CTS). 19 per-customer JSON files generated from run output.
- /project/: investor summary card (fetches live from dashboard.json + phases.json), 4 key discoveries, test+phase velocity charts (Chart.js), roadmap checklist.
- tools/generate_customer_data.py: generates site/data/customers/{id}.json + _index.json from run_output_latest.json.
- site/data/phases.json: test progression + phase dates extracted from git log (via timeline HTML) for velocity charts.
- process_run_complete.py: calls generate_customer_data() after every run; includes site/data/customers/ in auto-commit.
- Gate passed: nav visible on all pages; /customers/ loads with C1 login; /project/ shows investor summary + velocity charts.
- 13 new tests: customers/index exists, login form, nav bar, project/index exists, investor KPIs, charts, customer JSON present, C1 valid, phases.json, generate module.

**13 new tests (3,437 total).**

---
**Phase 264 -- Invoice Generation for Customer Portal (2026-06-26)**
**Files:** tools/generate_invoice_data.py (new), background/process_run_complete.py (modified), site/data/customers/*.json (updated)

**What was built:**
- Synthetic monthly invoice records from per-customer lifetime revenue (seasonal weighting).
- Gas: winter-heavy weights (1.45x Jan, 0.48x Jul); electricity: mild seasonal variation.
- Standing charge added per invoice: £0.28/day (elec), £0.27/day (gas), £1.20/day (I&C).
- Last invoice UNPAID, all prior PAID. Invoice ID format: {cid}-{yyyy}-{mm}.
- 19 customer files updated: C1 = 120 invoices ~£43/month; C_IC1 = 108 invoices ~£35k/month.
- process_run_complete.py wired to call generate_invoice_data on every run.
- 9 new tests: month count, invoice count, last UNPAID, rest PAID, revenue sanity, winter>summer gas, I&C>>resi, ID format, write-to-file.

**9 new tests (3,446 total).**

---
**Phase 265 -- NTFY Notable-Exception Digest (2026-06-26)**
**Files:** background/process_run_complete.py (modified), tests/tools/test_ntfy_digest.py (new)

**What was built:**
- `_run_history_max_net()`: reads run_history.json to find historical best net margin.
- `maybe_ntfy(data, net, insights=None)`: now sends NTFY only for:
  1. Administration events (existing behaviour).
  2. New all-time-high net margin (>1% above previous best).
  3. New all-time-low net margin (<50% of previous best, when previous best >£1M).
- Digest includes executive_summary and first recommended_action from RunInsights.
- Normal runs remain silent (standing policy from CLAUDE.md).
- 6 new tests: admin event NTFY, normal run silent, new-high NTFY, new-low NTFY, summary included, missing history.

**6 new tests (3,452 total).**

---
**Phase 266 -- Dashboard Phase D: "Talk to the Data" NL Query Interface (2026-06-26)**
**Files:** tools/generate_dashboard_data.py (modified), functions/api/query.js (new), site/index.html (modified), tests/tools/test_query_interface.py (new)

**What was built:**
- `extract_query_context(data)`: generates a compact (~2.6k char) text summary of run data for use as Claude API context — portfolio totals, annual performance, customer lifetime margins, retention summary, operations.
- `query_context` added to dashboard.json output (generated on every run).
- `functions/api/query.js`: Cloudflare Pages Function that proxies NL questions to Claude Haiku (claude-haiku-4-5-20251001). Reads ANTHROPIC_API_KEY env var. Handles CORS, missing API key, and API errors gracefully.
- "Query" tab added to poesys.net dashboard with: question input, Ask button, 5 example queries, chat-style answer history (newest on top), loading state, error handling.
- Dashboard now loads query_context from dashboard.json and sends it as context with each question.

**9 new tests (3,461 total).**

---
**Phase 267 -- Dashboard Phase B Completion: Year Filter on Financial, Trading, Customers Tabs (2026-06-26)**
**Files:** site/index.html (modified), tests/tools/test_year_filter_tabs.py (new)

**What was built:**
- `yearBtnsHtml()` helper: generates a reusable year selector bar (2016–2025 + All) using the shared `.year-btn` CSS class and `YEAR_FILTER` state.
- `mkChart()` updated to call `Chart.getChart(id).destroy()` before re-creating, allowing tabs to be re-rendered without Chart.js instance errors.
- `selectYear()` extended: after updating YEAR_FILTER and the Overview spotlight, clears the rendered cache for financial/trading/customers and re-renders the currently active tab.
- **Financial tab**: filters `D.financial.annual` by YEAR_FILTER; P&L stacked chart, commodity chart, and annual P&L table all reflect the selected year.
- **Trading tab**: filters `spot_monthly` by year prefix (month.startsWith(YEAR_FILTER)), and `hedge_annual` by year; spot price, crisis, and hedge charts zoom to the selected year.
- **Customers tab**: filters `book_annual` by year; heatmap shows only the selected year's column; lifecycle events and retention offers filtered to the selected year.
- All three tabs degrade cleanly to full 10-year view when YEAR_FILTER is null (All).

**8 new tests (3,469 total).**

---
**Phase 268 -- /sim/ Section: Wholesale Price Explorer (2026-06-26)**
**Files:** site/sim/index.html (new), tools/generate_sim_data.py (new), site/data/sim_data.json (new), background/process_run_complete.py (+generate_sim_data call), tests/tools/test_sim_section.py (new)

**What was built:**
- tools/generate_sim_data.py: reads sim/cache/elexon_ssp_full.json (168,026 HH records) and produces site/data/sim_data.json with monthly aggregates (mean/P95/P5/max/min/is_crisis), annual summaries, and top-10 peak records.
- site/sim/index.html: Wholesale Price Explorer. 6 KPI cards (2022 mean, 2016 mean, all-time peak, peak date, 10yr mean, crisis multiple). Chart.js monthly line chart: mean + P95 fill + red crisis zone overlay for 2021-22. Annual summary table with CRISIS badges. Top-10 peak SSP records (£4,037/MWh peak in Sep 2021). 2022 mean £199.50/MWh vs 2016 £39.41/MWh = 5x crisis multiple.
- Nav /sim/ link un-dimmed across all 5 existing pages (index, project, timeline, customers, staging-status).
- process_run_complete.py: generate_sim_data called on every run.

**10 new tests (3,479 total).**

---
**Phase 269 -- Customer Portal Billing Year Filter (2026-06-26)**
**Files:** site/customers/index.html (modified), tests/tools/test_billing_filter.py (new)

**What was built:**
- Year filter buttons (2016-2025 + All) above the Bills section in the customer portal. Clicking a year filters invoices to that year.
- Total spend KPI tile showing sum of filtered invoices, with count.
- Outstanding (UNPAID) KPI tile showing outstanding balance in amber, only when non-zero.
- Invoice list shows most-recent-first when filtered. No-results message for years with no invoices.
- BILL_YEAR state variable; filterBillYear(y) function updates state and re-renders; renderBills() is the isolated bills renderer.

**8 new tests (3,487 total).**

**Phase DH (2026-06-30):** BSC Settlement Run Tracking Register -- 25 new tests (5,648 total). company/market/bsc_settlement_run_register.py (new): SettlementRunType (SF/R1/R2/R3/RF with _SETTLEMENT_RUN_MONTHS mapping); AdjustmentDirection (CREDIT/DEBIT/NIL); SettlementRunRecord (frozen; adjustment_gbp=0 for SF; direction; variance_pct = |adj|/prior; is_material ≥5% threshold; is_final for RF only; expected_run_date via calendar arithmetic); BSCSettlementRunRegister (record_run/runs_for_date/by_run_type/material_variances/credits/debits/total_adjustment_gbp/total_credit_gbp/total_debit_gbp/finalised_dates/run_type_breakdown/settlement_summary). BSC P272/SVA: SF=T+14d initial; R1=T+5m; R2=T+14m; R3=T+26m; RF=T+28m final. Most material variance at R2/R3 as smart meter actuals replace NHH estimates. Smart meter rollout (MHHS) shrinks R2/R3 gap over time. Epistemic verifier: PASS.

**Phase DG (2026-06-30):** Consumer Vulnerability Duty Action Register -- 23 new tests (5,623 total). company/regulatory/consumer_vulnerability_register.py (new): VulnerabilityCategory (8: MEDICAL_DEPENDENCY/MENTAL_HEALTH/BEREAVED/FINANCIAL_HARDSHIP/ELDERLY_FRAIL/DISABILITY/LANGUAGE_BARRIER/TEMPORARY); VulnerabilityAction (10: PSR_ENROLMENT/PAYMENT_PLAN_OFFERED/PPM_WAIVER/DEBT_WRITEOFF/DISCONNECTION_HOLD/EXTRA_CONTACT/WARM_HOME_DISCOUNT/NOMINEE_ADDED/TARIFF_DOWNGRADE/ACCOUNT_FLAGGED); ActionOutcome (ACCEPTED/DECLINED/NO_RESPONSE/IN_PROGRESS); VulnerabilityActionRecord (frozen; follow_up_overdue(as_of)/is_medical/is_effective); ConsumerVulnerabilityRegister (record_action/actions_for/by_category/by_action_type/medical_dependency_accounts/overdue_follow_ups/effective_actions/effectiveness_rate/disconnection_holds/vulnerability_summary). Ofgem Consumer Vulnerability Strategy 2025 / SLC 26B. Companion to Phase DF (SAR) and Phase 329 (PSR). Epistemic verifier: PASS.

**Phase DF (2026-06-30):** Data Subject Access Request Register (UK GDPR Art.15) -- 32 new tests (5,600 total). company/regulatory/sar_register.py (new): SARStatus (RECEIVED/ACKNOWLEDGED/IN_PROGRESS/RESPONDED/EXTENDED/REFUSED/COMPLAINT_RAISED); SARTrigger (7: BILLING_DISPUTE/DEBT_DISPUTE/VULNERABILITY_CONCERN/GENERAL_ENQUIRY/PRE_LITIGATION/OMBUDSMAN_REFERRAL/UNKNOWN); SARRefusalReason (4: MANIFESTLY_UNFOUNDED/MANIFESTLY_EXCESSIVE/THIRD_PARTY_RIGHTS/LEGAL_EXEMPTION); SARRecord (frozen; deadline=received+30d standard/+90d extended; is_overdue(as_of)/days_to_deadline/days_to_respond/responded_within_deadline/is_active); SARRegister (receive/acknowledge/extend/respond/refuse/mark_ico_complaint/overdue/active/late_responses/by_trigger/compliance_rate/sar_summary). UK GDPR Art.15; 30-day standard/90-day extended for complex; no fee unless manifestly unfounded/excessive; max fine GBP17.5M. Companion to Phase DB (ICO breach). Epistemic verifier: PASS.

**Phase DA (2026-06-30):** Customer Communication Preference Register -- 12 new tests (6,140 total). company/crm/customer_comm_preferences.py (new): CommChannel (EMAIL/POST/PHONE/SMS/PORTAL/PAPER_BILL); CommPurpose (BILLING/SERVICE_NOTICE = essential/cannot be blocked; MARKETING = GDPR opt-in required; TARIFF_ALERT/TRIAD_ALERT); CustomerCommPreferences (set_preference/can_contact/set_marketing_opt_in/suppress); CustomerCommPreferenceRegister (set_preference/set_marketing_opt_in/suppress_account/can_contact/marketing_opt_in_accounts/suppressed_accounts/paperless_accounts/comm_preference_summary). GDPR Article 6 / PECR 2003 (SMS/email marketing opt-in) / SLC 25C (channel choice). Epistemic verifier: PASS.

**Phase CZ (2026-06-30):** Revenue Protection Register -- 12 new tests (6,128 total). company/billing/revenue_protection_register.py (new): RPCaseType (METER_TAMPERING/ILLEGAL_RECONNECTION/METER_BYPASS/ESTIMATION_FRAUD/SUPPLY_DIVERSION); RPCaseStatus (SUSPECTED/UNDER_INVESTIGATION/CONFIRMED/ESTIMATED_BILL_RAISED/RECOVERED/WRITTEN_OFF); RPCase (frozen; is_active/is_recoverable); RevenueProtectionRegister (open_case/confirm/raise_estimated_bill/recover/write_off/active_cases/confirmed_cases/total_estimated_loss_gbp/total_estimated_loss_kwh/cases_by_type/revenue_protection_summary). Theft exception: 3-year backbill permitted (vs SLC 31A 12-month cap for non-theft). Epistemic verifier: PASS.

**Phase CY (2026-06-30):** Supplier Fitness and Propriety Register -- 13 new tests (6,116 total). company/regulatory/supplier_fitness_register.py (new): FitnessRole (EXECUTIVE_DIRECTOR/NON_EXECUTIVE_DIRECTOR/SENIOR_MANAGER/MAJOR_SHAREHOLDER); FitnessConcernCategory (CRIMINAL_CONVICTION/BANKRUPTCY/DISQUALIFICATION/CONFLICT_OF_INTEREST/COMPETENCE_GAP/PRIOR_SUPPLIER_FAILURE); FitnessOutcome (FIT/FIT_WITH_CONDITIONS/UNDER_REVIEW/NOT_FIT); FitnessAssessment (frozen; review_due_date = assessment+365d; is_review_overdue/is_fit/has_concerns); SupplierFitnessRegister (assess/get/not_fit_persons/overdue_reviews/persons_with_concerns/prior_supplier_failure_risk/all_fit/fitness_summary). Ofgem LC 30A (June 2022): suppliers must ensure directors and senior managers are fit and proper; annual review. Epistemic verifier: PASS.

**Phase CX (2026-06-30):** Regulatory Breach Log -- 12 new tests (6,103 total). company/regulatory/regulatory_breach_log.py (new): BreachSeverity (LOW/MEDIUM/HIGH/CRITICAL); BreachStatus (POTENTIAL/CONFIRMED/REMEDIATED/CLOSED/REPORTED_TO_OFGEM); BreachSource (INTERNAL_AUDIT/SELF_DETECTION/OFGEM_REQUEST/CUSTOMER_COMPLAINT/THIRD_PARTY); RegulatoryBreachRecord (frozen; is_open/is_reportable: HIGH or CRITICAL + open); RegulatoryBreachLog (record/confirm/report_to_ofgem/remediate/open_breaches/critical_breaches/reportable_breaches/total_estimated_penalty_gbp/by_slc). Central breach register for SLC violations. Ofgem enforcement: penalty up to 10% of turnover; material breaches must be self-reported. Epistemic verifier: PASS.

**Phase CW (2026-06-30):** Licence Application and Variation Register -- 12 new tests (6,091 total). company/regulatory/licence_application_register.py (new): LicenceType (ELECTRICITY_DOMESTIC/GAS_DOMESTIC/ELECTRICITY_NON_DOMESTIC/GAS_NON_DOMESTIC); LicenceTier (TIER_1 <250,000 domestic customers / TIER_2 >=250,000); VariationReason (NEW_CATEGORY/CHANGE_OF_CONTROL/FINANCIAL_CONDITION/GEOGRAPHIC_EXPANSION/SPECIAL_CONDITION); LicenceRecord (frozen; has_special_conditions); LicenceApplication (frozen; is_open/is_approved); LicenceApplicationRegister (register_licence/submit_application/decide/active_licences/licences_with_special_conditions/open_applications/approved_applications). Post-2022: Ofgem requires explicit continuation application when FRA deteriorates; Special Conditions (SpC) imposed beyond standard SLC. Epistemic verifier: PASS.

**Phase CV (2026-06-30):** DA/DC Contract Register -- 12 new tests (6,079 total). company/market/dadc_contract_register.py (new): MeteringAgentType (DA/DC/DA_DC/MOA); MeterType (NHH/HH/SMETS2); AgentAppointment (frozen; is_active); DADCContractRegister (appoint/terminate/agent_for_mpan/mpans_without_dc/mpans_without_da/agents_by_name/da_dc_summary). BSC SVA: each MPAN must have appointed DC (reads/validates) and DA (aggregates HH data); DA_DC combined covers NHH meters; missing appointment = BSC breach risk; appointment notified via Elexon MDD. Epistemic verifier: PASS.

**Phase CU (2026-06-30):** Interruptible Gas Supply Register -- 13 new tests (6,067 total). company/market/interruptible_supply_register.py (new): SupplyFirmness (FIRM/INTERRUPTIBLE); InterruptionReason (COLD_WEATHER/NETWORK_CONSTRAINT/NGT_INSTRUCTION/SUPPLIER_DISCRETION); InterruptionEvent (frozen; notice_compliant: ≥2h per UNC TPD X3); InterruptibleContract (frozen; saving_vs_firm_gbp_pa at 15% INT discount vs 4p/kWh firm rate); InterruptibleSupplyRegister (register/record_interruption/events_for_account/annual_curtailment_days/over_cap_accounts: >30 days/notice_violations/total_portfolio_annual_kwh/interruptible_summary). Epistemic verifier: PASS.

**Phase CT (2026-06-30):** Shipper Code Register -- 13 new tests (6,054 total). company/market/shipper_code_register.py (new): LDZ enum (13 GB Local Distribution Zones: EA/EM/NE/NO/NT/NW/SC/SE/SO/SW/WM/WN/WS); LDZAuthorisation (frozen; effective_date/is_active); ShipperRecord (active_ldz_codes/ldz_coverage_count/is_national/can_supply_in/add_ldz/revoke_ldz); ShipperCodeRegister (register/suspend/active_shippers/suspended/shipper_summary). Xoserve UK Link: shipper code required for gas transportation under UNC; each LDZ requires separate authorisation; MPRN registry. Epistemic verifier: PASS.

**Phase CS (2026-06-30):** Gas Nomination Register -- 12 new tests (6,041 total). company/market/gas_nomination_register.py (new): NominationStatus (INITIAL/REVISED/CONFIRMED/SETTLED); ImbalanceDirection (LONG/SHORT/BALANCED ±5% tolerance); GasNominationRecord (frozen; effective_nominated_kwh — uses revised if set; imbalance_kwh / imbalance_pct / direction / is_in_tolerance); GasNominationRegister (nominate / revise / settle / out_of_tolerance_days / short_days / long_days / mean_imbalance_pct / nomination_summary). UNC: nominate by 08:30 each gas day (06:00-06:00); cash-out penalty applies outside ±5% tolerance; small shipper flex band. Epistemic verifier: PASS.

**Phase CR (2026-06-30):** Priority Services Register -- 12 new tests (6,029 total). company/regulatory/priority_services_register.py (new): PSRCategory (9 eligibility types — PENSIONABLE_AGE / DISABILITY / MEDICAL_EQUIPMENT / CHILD_UNDER_5 / CHRONIC_ILLNESS / MENTAL_HEALTH / VISUAL_IMPAIRMENT / HEARING_IMPAIRMENT / LANGUAGE_SUPPORT); PSRService (6 core services — PRIORITY_RECONNECTION / NOMINEE_SCHEME / GAS_SAFETY_CHECK / ALTERNATIVE_FORMAT / PASSWORD_SCHEME / ADVANCE_INTERRUPTION_NOTICE); PSRRecord (frozen; is_electricity_dependent / needs_priority_reconnection / is_review_overdue / is_compliant — ≥1 service enrolled); PriorityServicesRegister (active_records / electricity_dependent / priority_reconnection_customers / non_compliant_records / overdue_reviews / network_shared_count / psr_penetration_pct). SLC 26B: UK ~9M households on PSR (~31% domestic). Epistemic verifier: PASS.

**Phase CQ (2026-06-30):** Environmental Impact Register -- 12 new tests (6,017 total). company/sustainability/environmental_impact.py (new): EmissionScope (SCOPE_1 / SCOPE_2_LOCATION / SCOPE_2_MARKET / SCOPE_3_DOWNSTREAM); EmissionRecord (frozen; emissions_kgco2e / emissions_tco2e / emissions_mtco2e); EnvironmentalImpactRegister (record_gas_scope3 / record_electricity_scope3: market-based uses REGO×0 + grid×unmatched fraction; total_scope3_tco2e / emissions_by_year / peak_emission_year). DEFRA 2023 factors: gas 0.18253 kgCO₂e/kWh; UK grid 0.2104; REGO-backed = 0.0. Regulatory basis: SECR Regulations 2018 (>250 employees or >£36M turnover); TCFD climate disclosure. Epistemic verifier: PASS.

**Phase CP (2026-06-30):** BSC Settlement Exposure Report Section -- 12 new tests (6,005 total). saas/reporting/annual_report.py: _section_bsc_settlement_exposure() renders per-year BSC credit required and peak daily settlement amount; flags years where BSC credit > 0.4% of revenue with << marker; identifies peak credit year. BSC (Balancing and Settlement Code): Elexon requires suppliers to post credit cover for potential imbalance charges; scales with portfolio size and wholesale price level. 2022 peak: £10,210 credit; 2025 flagged at 0.51%. Wired before Phase CN. Epistemic verifier: PASS.

**Phase CO (2026-06-30):** Contract Exposure Register -- 12 new tests (5,993 total). company/crm/contract_exposure_register.py (new): ContractStatus (FIXED_TERM / STANDARD_VARIABLE / OUT_OF_CONTRACT / DEEMED / PENDING_RENEWAL); ContractSegment (DOMESTIC/SME/I&C); ContractRecord (frozen; is_fixed_term / is_svt / days_remaining / is_in_notice_window — SLC 22 42-day window / annual_contract_revenue_gbp); ContractExposureRegister (fixed_term_contracts / svt_contracts / in_notice_window / notice_not_issued — SLC 22 breach risk / svt_revenue_at_risk_gbp / exposure_summary). SVT contracts are at-risk; OOC I&C allows supplier exit. Epistemic verifier: PASS.

**Phase CN (2026-06-30):** Unit Economics Report Section -- 12 new tests (5,981 total). saas/reporting/annual_report.py: _section_unit_economics() renders per-active-customer revenue / gross margin / net margin by year; flags net margin <5% with << marker (below Ofgem FRA comfort); identifies best year (2024, £26,588/customer) and worst year (2021, £3,642/customer). Wired into generate_annual_report() before Phase CD (_section_customer_commodity_pnl). 2021: 3.3% net margin flagged; 2022 crisis compressed net despite record revenue (£248k/customer). Epistemic verifier: PASS.

**Phase CM (2026-06-30):** Market Share Estimator -- 12 new tests (5,969 total). company/market/market_share_estimator.py (new): MarketSegment (DOMESTIC / SME / INDUSTRIAL_COMMERCIAL); _UK_MARKET_SIZE benchmarks (29M domestic / 1.7M SME / 28k I&C, Ofgem/DESNZ published); _MICRO_SUPPLIER_THRESHOLD (<0.01% = micro); SegmentShareEstimate (frozen; market_share_pct / is_micro_supplier / customers_needed_for_1pct); MarketShareSnapshot (frozen; total_own / blended_share_pct / largest_segment / estimate_for_segment); MarketShareEstimator (record_year with optional market_overrides / snapshot_for_year / latest_snapshot / growth_rate_pct / share_trend / market_summary). Portfolio: 4 I&C = 0.0143% share; 9 domestic = 0.000031% (micro). Epistemic verifier: PASS.

**Phase CL (2026-06-30):** Fuel Mix Disclosure Book -- 12 new tests (5,957 total). company/regulatory/fuel_mix_disclosure.py (new): FuelSource enum (11 sources); _CARBON_INTENSITY lookup (7–820 gCO₂e/kWh) and _IS_RENEWABLE map; FuelMixComponent (frozen; weighted_carbon / is_renewable); FuelMixDisclosure (frozen; renewable_fraction / carbon_intensity_gco2_per_kwh / rego_coverage_fraction / is_fully_rego_matched — ≥1 REGO/MWh / unmatched_volume_mwh); FuelMixDisclosureBook (record_disclosure / carbon_trend / fully_matched_years / fmd_summary). Regulatory basis: SLC 21C annual FMD obligation; REGO = 1 MWh renewable; UK residual mix ~280 gCO₂e/kWh (DESNZ 2022). Epistemic verifier: PASS.

**Phase CK (2026-06-30):** Liquidity Stress Test Book -- 12 new tests (5,945 total). company/risk/liquidity_stress_test.py (new): StressScenario (frozen; wholesale_price_shock_pct / volume_shock_pct / initial_margin_shock_pct / stress_days; is_severe flag); LiquidityStressOutcome (SOLVENT / MARGIN_CONSTRAINED / CRITICAL / INSOLVENT); StressTestResult (frozen; vm_drain_gbp / im_additional_call_gbp / retail_revenue_inflow_gbp / ending_cash_gbp / survival_days / headroom_pct / total_cash_drain_gbp); LiquidityStressTestBook (run_scenario / standard_scenarios: mild/moderate/severe_2022 / worst_outcome with severity + cash tiebreaker / stress_summary). 2022 context: IM tripled + daily VM calls = insolvency within weeks. Ofgem FRA thresholds: 365d = GREEN, 90d = AMBER, <90d = CRITICAL, <0 = INSOLVENT. Epistemic verifier: PASS.

**Phase CJ (2026-06-30):** Initial Margin Register -- 12 new tests (5,933 total). company/trading/initial_margin_register.py (new): MarginAccountType (BILATERAL_OTC / EXCHANGE_CLEARED / INTERNAL_NETTING); IMStatus (POSTED/RETURNED/CALLED/PARTIAL); InitialMarginRecord (frozen; total_held_gbp = margin_posted_gbp + additional_call_gbp; margin_rate_pct_of_notional vs £100/MWh proxy; is_active); InitialMarginRegister (post_margin / issue_additional_call — CCP margin call increases IM requirement / return_margin / total_locked_gbp / records_by_counterparty / im_summary). Context: 2022 crisis — clearing houses tripled initial margin requirements; combined IM + variation margin (Phase CC) drain destroyed supplier liquidity within weeks. Complements Phase CC (OTC Variation Margin Book). Epistemic verifier: PASS.

**Phase CI (2026-06-30):** Annual Board Pack Synthesiser -- 12 new tests (5,921 total). company/risk/annual_board_pack.py (new): BoardSignalRAG (GREEN/AMBER/RED); BoardSignalCategory (Financial/Risk/Compliance/Portfolio/Strategic); BoardSignal (mutable; is_red/is_green); AnnualBoardPack (add_financial/risk/compliance/portfolio/strategic; red_signals / overall_rag — RED if any RED, AMBER if any AMBER; highest_risk_signals/signals_by_category/pack_summary). Synthesises all company-layer risk signals into a CEO-level annual board pack with overall RAG. Epistemic verifier: PASS.

**Phase CH (2026-06-30):** Net Open Position Register -- 12 new tests (5,909 total). company/trading/net_open_position_register.py (new): ExposureDirection (LONG_RETAIL/OVERHEDGED/FLAT ±5% tolerance); NOPSeverity (GREEN / AMBER ≥20% / RED ≥40%); DeliveryPeriodPosition (frozen; net_open_position_mwh / nop_pct_of_retail / hedge_fraction_pct / direction / severity); NetOpenPositionRegister (record / positions_for_year / positions_for_commodity / red_positions / long_retail_positions / overhedged_positions / aggregate_for_year / nop_summary). Core risk metric for UK suppliers: long retail / short market position in 2022 caused catastrophic mark-to-market losses. Epistemic verifier: PASS.

**Phase CG (2026-06-30):** Supplier Resilience Scorecard -- 12 new tests (5,897 total). company/risk/supplier_resilience_scorecard.py (new): PillarRAG (GREEN/AMBER/RED); PillarScore (frozen; score_value 1-3); SupplierResilienceScorecard — 5 pillar assessors: assess_liquidity (≥12m GREEN / ≥6m AMBER / <6m RED); assess_hedge_coverage (≥70% GREEN / ≥40% AMBER); assess_credit_quality (bad_debt ≤1% / ≤2.5%); assess_concentration (max_cust ≤20% / ≤35%); assess_stress_resilience (stressed_net ≥1.0x / ≥0.5x net_margin); composite_score/overall_rag/red_pillars/scorecard_summary. Ofgem FRA post-2022 framework. 2022 scenario: RED (hedge 35%, concentration 58%, stress -0.68x). Epistemic verifier: PASS.

**Phase CF (2026-06-30):** TPI Commission Book -- 12 new tests (5,885 total). company/market/tpi_commission_book.py (new): TPITier (NATIONAL/REGIONAL/INDEPENDENT/ONLINE per Ofgem 2022 Business Energy mandate); CommissionType (UPFRONT/TRAIL/HYBRID); TPIAgreement (frozen; is_compliant=is_disclosed_to_customer per Ofgem; rate_gbp_per_mwh); TPIPayment (frozen; rate_gbp_per_mwh from annual_kwh); TPICommissionBook (register_tpi/record_payment/non_compliant_agreements/payments_for_year/payments_for_customer/total_commission_gbp/total_for_year/avg_rate_gbp_per_mwh/tpi_summary). UK I&C trail rates £2-25/MWh; Ofgem requires disclosure to business customers since 2022. Epistemic verifier: PASS.

**Phase CE (2026-06-30):** SLC Compliance Tracker -- 12 new tests (5,873 total). company/regulatory/slc_compliance_tracker.py (new): SLCStatus (COMPLIANT/BREACH_RISK/BREACHED/N/A/UNKNOWN); SLCCategory (7: Billing/Credit/Debt/Metering/Renewal/Vulnerability/Smart); SLCObservation (frozen; severity_score 0-2; is_compliant/is_breached); SLCComplianceTracker (record/get/all_observations/breached/at_risk/compliant/total_breach_count/total_at_risk_count/overall_rag/by_category/highest_severity_slcs/compliance_summary). Consolidates SLC 6 (bills), 14 (refund), 21B (closure), 22 (renewal), 27 (debt), 27A (ATP), 31A (back-billing), 45 (smart meter) signals. Epistemic verifier: PASS.

**Phase CD (2026-06-30):** Customer Lifetime P&L by Commodity Section -- 12 new tests (5,861 total). _section_customer_commodity_pnl() in annual_report.py: shows per-customer lifetime electricity and gas net margins side-by-side; loss-making accounts marked *; gas-loss summary; gas portfolio net as % of total. Key findings: C_IC3g lifetime loss -£132,711; C4g -£1,950; C7 -£1,378; C5 -£42. Gas portfolio net = -£133,697 (loss-making overall). Confirms Phase AR gas exit decision rationale. Epistemic verifier: PASS.

**Phase CC (2026-06-30):** OTC Variation Margin Book -- 12 new tests (5,849 total). company/trading/otc_margin_book.py (new): MarginCallDirection (CALL/RETURN); MarginCallStatus (4 states); VariationMarginCall (frozen; cash_impact_gbp — negative for CALL, positive for RETURN; is_call_on_company; is_settled; is_overdue T+1 CSA standard); OTCMarginBook (record_call/settle_call/pending_calls/overdue_calls/total_cash_impact_gbp/total_pending_outflow_gbp/calls_by_counterparty/net_cash_for_year/margin_book_summary). Models the key 2022 supplier-failure mechanism: OTC forward positions move against company as prices rise, generating daily margin calls that drain treasury. Epistemic verifier: PASS.

**Phase CB (2026-06-30):** Hedge Value-Add Analysis Annual Report Section -- 12 new tests (5,837 total). _section_hedge_value_add() in annual_report.py: per-year actual hedged net margin vs hypothetical naked (spot-priced) net margin; hedging value-add; totals row; identifies largest/smallest hedging cost year. Key finding: hedging value-add ALWAYS negative across all 10 years — total cost £4.04M vs going naked. 2022 worst (-£988k); 2016 best (-£8.9k). Reflects UK market backwardation 2016-21 and partial hedging in crisis years. Epistemic verifier: PASS.

**Phase CA (2026-06-30):** Customer Service Quality Monitor + Annual Report Section -- 12 new tests (5,825 total). company/crm/service_quality_monitor.py (new): ServiceQualityRAG (GREEN/AMBER/RED); ServiceQualitySnapshot (clarity_rag/complaint_rag/bill_shock_rag/overall_rag/shock_rate_pct — all computed from observed billing data); ServiceQualityMonitor (record/worst_clarity_year/worst_complaint_year/worst_bill_shock_year/is_improving/quality_summary). _section_service_quality() in annual_report.py: 10-year table; 2022 = RED (clarity 0.791 / complaint 5.6% / shock 0.34%); 2025 declining. Ofgem benchmarks embedded. Epistemic verifier: PASS.

**Phase BZ (2026-06-30):** Portfolio Margin Sensitivity Analyser -- 12 new tests (5,813 total). company/finance/portfolio_margin_sensitivity.py (new): SensitivityFactor enum (5 types: wholesale/demand/churn/ncc/fixed); SensitivityScenario (frozen; is_adverse/severity); PortfolioMarginSensitivityBook — 5 shock methods + standard_sensitivity_table() (10-row board table) + most_sensitive_factor(). Wholesale +10% is most sensitive (-10.4%); NCC least sensitive (-1.2%). Company derives sensitivity from its own P&L fractions — epistemically valid. Connects Phase 318 (FRA), Phase BT (hedge evolution), Phase BS (committee). Epistemic verifier: PASS.

**Phase BY (2026-06-30):** VaR Trajectory and Treasury Evolution Section -- 12 new tests (5,801 total). saas/reporting/annual_report.py: _section_var_treasury_evolution(): shows per-year VaR ratio / ALERT(≥3.0)/WATCH(<3.0)/dash(no VaR) status / year-end treasury / net margin; identifies peak VaR year, peak treasury year, and total treasury growth. Key insights: VaR alerts in 2016-17 (early book) and 2022-23 (crisis). Treasury grew from £2.47M to £3.59M (+£1.12M). VaR ratio trigger = 3.0 (committee review threshold). Epistemic verifier: PASS.

**Phase BX (2026-06-30):** UK Grid Fuel Mix Disclosure Section -- 12 new tests (5,789 total). saas/reporting/annual_report.py: _section_fuel_mix_disclosure(): reads Ofgem FMD data per year (renewable/nuclear/gas/coal/other) from company.billing.fuel_mix; computes low-carbon% (ren+nuc); identifies peak renewable year and first-majority-renewable year. Key insights: UK grid went from 24.6% renewable (2016) to 55.0% (2025); low-carbon% improved 45.5%→68.5%; 2025 first year with renewable majority (>50%). Ofgem FMD published under Electricity Act 1989 s.4(1)(b). Epistemic verifier: PASS.

**Phase BW (2026-06-30):** Missed Retention Opportunity Analysis Section -- 12 new tests (5,777 total). saas/reporting/annual_report.py: _section_missed_retention_analysis(): reads no_offer_churn_log + company_gas_churn_log; electricity no-offer events with churn estimate (≥10% flagged); gas renewal events with ≥15% churn estimate flagged; totals margin at risk from high-churn no-offer events. Key insight: C6 (SME electricity) had 24.7% churn estimate but received no retention offer at 2024 renewal — £2,853 margin at risk. 3 gas reprices with >15% churn estimate. Epistemic verifier: PASS.

**Phase BV (2026-06-30):** Retention Decision Economics Section -- 12 new tests (5,765 total). saas/reporting/annual_report.py: _section_retention_decision_economics(): reads retention_log; shows per-offer retention cost / expected margin protected / ROI (margin÷cost) / discount % / outcome; totals at bottom. Key insights: 18 retention offers placed, 17/18 retained; portfolio ROI ~6.7× (£118k spent protects £885k+ margin); best single ROI = 12.6× (C_IC1 2020, low cost, high expected margin); worst ROI 1.9× (C_IC3 2020, margin already compressed). Epistemic verifier: PASS.

**Phase BU (2026-06-30):** Gas Exit Decision Section -- 12 new tests (5,753 total). saas/reporting/annual_report.py: _section_gas_exit_decision(): calls GasExitDecisionBook (company/finance/gas_exit_analysis.py); presents 3-scenario board analysis: Status Quo / Exit Gas / Reprice to Breakeven; shows loss-making accounts and delta vs SQ; board recommendation. Key insights: gas drag -£47,674 in dual-fuel portfolio; reprice to breakeven = +£134,662 vs SQ; exit gas = +£99,103 (but risks losing electricity contract via cross-product churn). Connects Phase AR (GasExitDecisionBook). Epistemic verifier: PASS.

**Phase BT (2026-06-30):** Portfolio Hedge Fraction Evolution Section -- 12 new tests (5,741 total). saas/reporting/annual_report.py: _section_hedge_fraction_evolution(): reads hedge_fractions per year (per-customer avg_hf); computes portfolio avg / min / max / naked-count (hf < 5%); identifies lowest-avg year and first-naked year. Key insights: naked positions first appeared in 2019 when C_IC3g (gas I&C) was added with zero hedge; portfolio avg dropped from 89.6% (2017) to 79.3% (2024) — regime-change blindness in action; mirrors strategy that destroyed 28 real UK suppliers 2021-22. Epistemic verifier: PASS.

**Phase BS (2026-06-30):** Risk Committee Intervention Pattern Section -- 12 new tests (5,729 total). saas/reporting/annual_report.py: _section_committee_intervention_pattern(): shows per-year committee wakeups (triggered by VaR threshold breach), total customer adjustments, avg customers per event, and max VaR stressed. Key insights: 2016 had peak 13 wakeups (early book calibration); 2018-2021 were quiet (stable hedging); 2022 resurgence with 9 wakeups (crisis onset) — 62 customer adjustments. Total 38 events across run. Years with zero wakeups skipped from table. Epistemic verifier: PASS.

**Phase BR (2026-06-30):** Worst Half-Hourly Settlement Period by Year -- 12 new tests (5,717 total). saas/reporting/annual_report.py: _section_worst_settlement_periods(): shows worst HH settlement (date / SP / customer / net margin) per year; identifies single worst period across all years. Key insights: C_IC3g (large gas I&C) dominates worst periods from 2020 onwards; 2023 single worst period = -£3,475 on 2023-12-31 SP1 (gas spot price elevated at year-end). 2016-2019 worst periods small (C6, C_IC1, -£0.36 to -£20). Epistemic verifier: PASS.

**Phase BQ (2026-06-30):** BSC Credit Obligation and Regulatory Levy Breakdown -- 12 new tests (5,705 total). saas/reporting/annual_report.py: _section_bsc_regulatory_levies(): BSC credit required / CM levy / mutualization levy / CCL / gas network cost by year; identifies peak BSC credit year; flags first mutualization year. Key insights: BSC credit grew from £30 (2016) to £10,210 (2022) — a 340× increase driven by portfolio volume growth + crisis price levels. Mutualization levy first appeared 2021 (£42k) reflecting costs of failing suppliers passed through Elexon settlement. Epistemic verifier: PASS.

**Phase BP (2026-06-30):** Customer Cohort Revenue Analysis Section -- 12 new tests (5,693 total). saas/reporting/annual_report.py: _section_cohort_revenue_analysis(): groups customers by acquisition year (cohort); reads per_customer_lifetime.acquisition_date + per_cid_pnl; table shows total revenue / gross margin / net margin / revenue-per-customer per cohort; identifies best rev/customer cohort and best net margin cohort; flags loss cohorts. Key insights: 2017 cohort (C_IC1) best (£3.16M rev, £837k net); 2019 cohort (C_IC3 + C_IC3g) loss-making (£6.5M rev but -£49k net due to gas anchor drag). Epistemic verifier: PASS.

**Phase BO (2026-06-30):** CfD Levy, Bad Debt & Treasury Drawdowns Section -- 12 new tests (5,681 total). saas/reporting/annual_report.py: _section_cfd_and_treasury(): year-by-year CfD levy / RO levy / bad debt / treasury drawdown count / bills count; identifies CfD credit years (negative levy); flags treasury drawdown years (credit facility used); peak bad debt year. Key insight: 2022 CfD went CREDIT (-£50,342) as wholesale >> strike price and CfD generators had to repay the system — this reduced supplier cost; treasury drawn in 2022-2024 (crisis stress + recovery). Epistemic verifier: PASS.

**Phase BN (2026-06-30):** Segment Margin Attribution Section -- 12 new tests (5,669 total). saas/reporting/annual_report.py: _section_segment_margin_attribution(): reads segment_split per year; table showing all 5 segments (resi electricity / resi gas / SME electricity / I&C electricity / I&C gas) with gross margin £ + year total; identifies best/worst total GM year; flags loss-making segment-years. Key insights: 2022 resi gas first loss (-£742); I&C electricity peak £964k (2022) and £1.16M (2024); resi+SME together <1% of total gross margin. Epistemic verifier: PASS.

**Phase BM (2026-06-30):** Price Cap Headroom Section -- 12 new tests (5,657 total). saas/reporting/annual_report.py: _section_price_cap_headroom(): reads churn_basis_risk.rate_vs_svt_pct per term; year-by-year table showing avg vs SVT% / above-cap count / min / max; identifies best headroom year and largest above-SVT year. Key insights: 2021 (5/9 terms above SVT at avg +9.2%) and 2022 (4/7 at +11.5%) — crisis-era I&C tariffs exceeded residential SVT; I&C/SME exempt from Ofgem price cap; 2020 best headroom (-30% avg). Epistemic verifier: PASS.

**Phase BL (2026-06-30):** Portfolio Stress Test History Section -- 12 new tests (5,645 total). saas/reporting/annual_report.py: _section_stress_test_history(): for each year, runs all 5 StressTestBook scenarios (MARKET_SPIKE, CREDIT_DEFAULT, DEMAND_SHOCK, LIQUIDITY_CRISIS, COMBINED_CRISIS) against year-end treasury and best available VaR; outputs RAG table (GREEN/AMBER/RED per year per scenario); identifies most-stressed year and all-GREEN years. Credit facility assumption: £2M; weekly burn = max(1% treasury, £25k). First time existing StressTestBook (Phase 303) is connected to annual report retrospective analysis. Epistemic verifier: PASS.

**Phase BK (2026-06-30):** Financial Ratios Section -- 12 new tests (5,633 total). saas/reporting/annual_report.py: _section_financial_ratios(): year-by-year EBIT margin % / revenue per customer / gross margin per customer / bad debt rate %; uses management_accounts income_statement + years active_customer_ids; best/worst EBIT year; peak revenue-per-customer year. Key insights: 2016 best EBIT (45.2%, early portfolio before I&C dominance); 2022 worst EBIT (21.3%, crisis peak); 2022 peak revenue-per-customer £306k (I&C crisis-year billing); 2024 EBIT recovery to 38.4%. Epistemic verifier: PASS.

**Phase BJ (2026-06-30):** Churn Prediction Calibration Section -- 12 new tests (5,621 total). saas/reporting/annual_report.py: _section_churn_prediction_calibration(): filters company_event_log for churn events; table shows customer / date / sim_churn_probability / company_estimate / delta (pp) / UNDERESTIMATED/ACCURATE/OVERESTIMATED verdict (±10pp threshold); summary with MAE and systematic bias flag. Key insight: 5 of 6 actual churns were underestimated by the company — the epistemic blindfold (company cannot see sim churn parameters) creates systematic under-prediction, exactly as real small suppliers experience. Epistemic verifier: PASS.

**Phase BI (2026-06-30):** Tariff Estimation Accuracy Section -- 12 new tests (5,609 total). saas/reporting/annual_report.py: _section_tariff_estimation_accuracy(): reads company_divergence.tariff_error_by_year; table shows observation count / mean absolute error % / max absolute error % / accuracy band (GOOD <10% / MODERATE 10-15% / POOR ≥15%); identifies best and worst accuracy years (n≥5 filter); epistemic blindfold note. Key insights: 2024 best accuracy (9.75% mean error, market normalised); 2023 worst non-trivial year (19.89%, crisis aftermath lag in forward curves); 2025 outlier (n=2, 32.85%, insufficient data). Epistemic verifier: PASS.

**Phase BH (2026-06-30):** Dynamic Pricing Activity Section -- 12 new tests (5,597 total). saas/reporting/annual_report.py: _section_dynamic_pricing_activity(): groups dynamic_pricing_log and margin_feedback_log by year; table shows adjustment count / avg delta (£/MWh) / up count / down count / emergency reprice count; identifies peak-avg-delta year and total emergency reprices. Key insights: 2022 crisis peak avg adjustment +18.1 £/MWh; 29 total emergency reprices 2016-2025 (8 in crisis years 2021-2022); 2023 post-crisis lag shows 8 emergency reprices (delayed contract renewals still exposed). Epistemic verifier: PASS.

**Phase BG (2026-06-30):** Portfolio CLV Evolution Section -- 12 new tests (5,585 total). saas/reporting/annual_report.py: _section_clv_evolution(): year-end CLV snapshots aggregated by year (gas accounts excluded via trailing 'g' filter); table shows total portfolio CLV / account count / average CLV / YoY delta; identifies peak, earliest/lowest, biggest YoY gain and drop. Key insight: 2018 I&C step-change (CLV jumped £37k→£1M when major I&C customers joined); 2025 peak at £3.46M forward portfolio value. Epistemic verifier: PASS.

**Phase BF (2026-06-30):** Acquisition Strategy Intelligence Book -- 15 new tests (5,573 total). company/crm/acquisition_strategy_book.py (new): ChannelROIAnalysis (frozen; is_viable = CLV ≥ 3×CAC; net_value_gbp); PortfolioGrowthScenario (frozen; required_attempts from win_rate; total_cac_spend/expected_total_clv/net_value); AcquisitionStrategyBook (analyse_channel / rank_channels / model_growth_scenario / minimum_viable_clv / strategy_summary). Channel benchmarks: PCW £55, direct £30, broker £160, referral £20, winback £37. Tenure: I&C 4.5yr, resi 3.2yr, SME 2.8yr. Epistemic verifier: PASS.

**Phase BE (2026-06-30):** Gross Margin Bridge (Year-over-Year Attribution) -- 12 new tests (5,558 total). annual_report.py: _section_gross_margin_bridge(): year-by-year table showing revenue / wholesale_cost / non_commodity_cost / gross_margin / GM% with delta columns (ΔRevenue / ΔWholesale / ΔNon-Commodity / ΔGM); first year shows — for deltas; best/worst GM% years highlighted. Key findings: 2022 worst GM% = 24.8% (revenue +£1.84M but wholesale cost +£1.43M consumed most of it); 2024 recovery to 42.4% (wholesale cost fell £717k on normalising market); 2016 nominal best (51.2%) but tiny portfolio. Epistemic verifier: PASS.

**Phase BD (2026-06-30):** Renewal Pricing Engine -- 15 new tests (5,546 total). company/pricing/renewal_pricing_engine.py: RenewalPricingRecommendation (FULL_MARGIN/COMPETITIVE/COST_PLUS/NO_OFFER); RenewalPricingResult (frozen; total_cost_gbp_per_mwh / margin_per_mwh / vs_svt_pct / is_viable); RenewalPricingEngine (base_conversion_pct 85%; risk_premium_pct 5%; price_renewal computes cost floor from wholesale + non-commodity + CTS/MWh, applies risk premium, caps at SVT×1.02; NO_OFFER when cost_floor > SVT; I&C segment 0.3× conversion decay rate for relationship selling; portfolio_renewal_plan; pricing_summary). 15 tests first pass. Connects Phase BA (price elasticity), Phase M (renewal conversion), Phase K (break-even). Epistemic verifier: PASS.

**Phase BC (2026-06-30):** Risk Committee Activity Section -- 12 new tests (5,531 total). annual_report.py: _section_risk_committee_activity(): year-by-year table of session count / peak VaR current & stressed / accounts touched; busiest year / peak VaR year callouts; most-frequently-adjusted accounts ranking; non-list wake-up values handled gracefully. Key finding: 2016 busiest (13 sessions, VaR £28 — early framework calibration); 2023 peak VaR (£130k despite only 4 sessions — reduced committee oversight at highest stress). C1 adjusted 22 times across all years. Connects to Phase BB RiskCommitteeDecisionLedger. Epistemic verifier: PASS.

**Phase BB (2026-06-30):** Risk Committee Decision Ledger -- 15 new tests (5,519 total). company/risk/risk_committee_ledger.py: InterventionTrigger (VAR_THRESHOLD/TREASURY_STRESS/PRICE_SPIKE/MARGIN_DETERIORATION/SCHEDULED_REVIEW); InterventionOutcome (EFFECTIVE/NEUTRAL/COUNTERPRODUCTIVE/PENDING); CommitteeSession (frozen; var_ratio property; outcome property using ±£1k treasury delta threshold; treasury_delta_gbp); RiskCommitteeDecisionLedger (record_session; sessions_for_year; sessions_by_trigger; effective_interventions; counterproductive_interventions; intervention_effectiveness_rate; most_active_trigger; busiest_year; peak_stressed_var_gbp; governance_summary). Company-observable: records own committee decisions and treasury outcomes. Connects to var_monitor (Ph282), hedge_effectiveness (Ph319), financial_resilience (Ph318). Epistemic verifier: PASS.

**Phase BA (2026-06-30):** Price Elasticity Estimator -- 15 new tests (5,504 total). company/pricing/price_elasticity.py: ElasticityBand (LOW/MODERATE/HIGH); PriceChangeImpact (frozen; extra_churn_rate_pct / total_churn_rate_pct / expected_lost_customers / expected_lost_revenue_gbp / expected_retained_revenue_gbp / is_viable / revenue_delta_gbp / elasticity_band); PortfolioImpact (frozen; net_revenue_delta_gbp / retention_rate_pct); PriceElasticityBook (is_crisis_year multiplies elasticity ×1.5; estimate_churn_impact; model_portfolio_impact; optimal_tariff_change gradient search over user-specified range; elasticity_summary). Calibration: CMA 2016 / Ofgem 2019-2023 — resi=-0.18 (1.8% extra churn per 10% price rise); SME=-0.12; I&C=-0.05 (very inelastic — long contracts). Connects Phase AC (repricing actions), Phase M (renewal conversion). Epistemic verifier: PASS.

**Phase AZ (2026-06-30):** I&C Triad Notification Book -- 15 new tests (5,489 total). company/market/triad_notification_book.py: AlertStatus (ISSUED/RESPONDED/NO_RESPONSE); TriadAlert (frozen; demand_reduction_kw = 70% × estimated_demand if RESPONDED, else 0); CustomerTriadProfile (frozen; triad_charge_gbp/avoided_charge_gbp using _TNUOS_TRIAD_RATE_GBP_PER_KW 2022=£60.40/kW); TriadSavingsRecord (frozen; response_rate_pct/saving_pct); TriadNotificationBook (enrol; issue_alert: requires enrolled profile — raises KeyError/ValueError; is_triad_season Nov-Feb; is_triad_risk_period SP 33-39; savings_for_account_year; total_portfolio_saving_gbp; triad_notification_summary). Calibration: C_IC3 at 1,000 kW peak demand → £42,280 estimated saving at 70% response. Connects to tnuos_ledger.py (Phase 29a). Closes I&C Triad management gap in backlog.

**Phase AY (2026-06-30):** Customer Strategic Value Matrix -- 12 new tests (5,474 total). annual_report.py: _section_customer_strategic_value(): 2x2 CLV×churn-probability quadrant matrix using by_billing_account data; PROTECT (high CLV, low churn)/CRITICAL (high CLV, high churn)/MONITOR (low CLV, low churn)/EXIT (low CLV, high churn); median CLV and median churn as quadrant boundaries; gas accounts excluded (no trailing-g keys); per-quadrant CLV total and % of portfolio; board action note if CRITICAL non-empty. Key finding: I&C accounts (C_IC1/IC2/IC3/IC4) in PROTECT = 99% of portfolio CLV £5.97M; resi accounts in CRITICAL/MONITOR/EXIT with collectively negligible CLV. Annual report deduplication fix: removed duplicate _section_management_accounts call introduced in Phase AT; report now renders single management accounts section. Epistemic verifier: PASS.

**Phase AX (2026-06-30):** Customer Experience & Service Quality -- 12 new tests (5,462 total). annual_report.py: _section_customer_experience(): year-by-year billing clarity (0-1 scale) and complaint probability; LOW CLARITY flag (<0.80); HIGH COMPLAINTS flag (>5.5%); service quality score; acquisition performance summary (5 attempts, 0 wins, 0% win rate). Key finding: 2025=0.777 (worst clarity, end-of-portfolio billing complexity); 2022=0.791 LOW CLARITY (crisis). Epistemic verifier: PASS.

**Phase AW (2026-06-30):** Bill Shock Analysis -- 12 new tests (5,438 total). annual_report.py: _section_bill_shock_analysis(): year-by-year avg shock %, event count, bills count, shock rate %; HIGH flag (>=30%), ELEVATED (>=20%); crisis peak note with SLC 21 reference. Key finding: 2022=33.8% avg shock (HIGH) vs 14-17% normal years; 2025=23.6% (ELEVATED, likely final-term renewal spike). Epistemic verifier: PASS.

**Phase AV (2026-06-30):** Policy Cost & Levy Breakdown -- 12 new tests (5,426 total). annual_report.py: _section_policy_cost_breakdown(): RO/CfD/CCL/CM/FiT/total-policy/network by year; negative CfD levy in 2022 bolded with rebate note (crisis: spot > strike → generators repay via CfD mechanism); policy cost CAGR computation. Key finding: policy costs £1,701 (2016) → £285,999 (2025), CAGR 76.7%/yr. 2022: CfD levy = -£50,342 (unique negative year). Epistemic verifier: PASS.

**Phase AU (2026-06-30):** Commodity Split (Electricity vs Gas P&L) -- 12 new tests (5,414 total). annual_report.py: _section_commodity_split(): year-by-year elec/gas net margin and revenue; YES/NO profitable flag; gas share of revenue %; 'gas loss-making since X' note; cross-subsidy callout. Key finding: gas profitable 2016-2020, loss-making every year 2021-2025 (5 consecutive years). Electricity cross-subsidises gas supply. Connects Phase AR (Gas Exit). Epistemic verifier: PASS.

**Phase AT (2026-06-30):** Management Accounts P&L Section -- 12 new tests (5,402 total). annual_report.py: _section_management_accounts(): year-by-year income statement from management_accounts; revenue/wholesale/non-commodity/gross/bad-debt/opex/net columns; net margin %; best/worst year notes; balance sheet (cash/receivables/total assets/opening capital/profit). Wired first in generate_annual_report. 12/12 tests first run. Epistemic verifier: PASS.

**Phase AS (2026-06-30):** Gas Exit Analysis Annual Report Section -- 10 new tests (5,390 total). annual_report.py: _section_gas_exit_analysis() renders scenario comparison table (STATUS_QUO/EXIT_GAS/REPRICE_GAS); loss-making accounts with ROC + breakeven uplift %; accretive accounts; board decision note. Wired into generate_annual_report before _section_segment_capital_efficiency. Connects Phase AR (GasExitDecisionBook), Phase AP (gas capital ROC). Epistemic verifier: PASS.

**Phase AR (2026-06-30):** Gas Exit Decision Book -- 14 new tests (5,380 total). company/finance/gas_exit_analysis.py: GasAccountProfile (frozen; is_gas_accretive/gas_roc/breakeven_revenue_uplift_pct); GasScenarioResult (frozen; total_net_gbp/gas_net_gbp/elec_net_gbp/customers_retained/accounts_exited); GasExitDecisionBook (pairs inferred from per_cid_comm_pnl trailing-g keys; status_quo/exit_gas/reprice_gas scenarios; loss_making_accounts/accretive_accounts/scenario_comparison/gas_exit_summary). Exit gas: I&C 40% churn risk / resi 20% churn risk on electricity leg. Reprice gas: loss-making accounts repriced to break-even (net=0). Board finding: REPRICE_GAS recommended (+£134k vs SQ) vs EXIT_GAS (+£99k vs SQ). C_IC3g needs 7.2% revenue uplift; C4g needs 18.8%. Epistemic verifier: PASS (267 company files).

**Phase AQ (2026-06-30):** Board Risk Summary -- 12 new tests (5,366 total). saas/reporting/annual_report.py: _section_board_risk_summary() synthesises 6 RAG indicators from all preceding phase data: (1) Revenue concentration HHI (AMBER); (2) Gas segment ROC (RED=-0.7x); (3) Churn blind miss rate (RED=67%); (4) Demand estimation error peak (RED=3.3%/15.6%); (5) Pricing basis risk worst year (RED=+32.8%); (6) Net margin % (GREEN=32.9%). Renders RAG table with Board Action Required note when REDs present. Wired as second section in generate_annual_report after executive summary. Fixed early-exit condition and basis_risk key names. Epistemic verifier: PASS.

**Phase AP (2026-06-30):** Segment Capital Efficiency -- 12 new tests (5,354 total). saas/reporting/annual_report.py: _section_segment_capital_efficiency() aggregates segment_split per year into lifetime gross/capital/net; ROC = net/capital; CAPITAL DESTROYER when ROC<0; gas finding when lifetime gas net < 0. Key finding: I&C gas ROC=-0.7x (-£132k net on £185k capital); resi gas ROC=-0.9x; I&C electricity ROC=27.1x cross-subsidises both gas segments. Board: gas supply is a capital destroyer justified only if CLV of dual-fuel retention exceeds loss. Epistemic verifier: PASS. Connects segment_split, Phase 331 (dual-fuel account).

**Phase AO (2026-06-30):** Demand Estimation Error Trend -- 12 new tests (5,342 total). saas/reporting/annual_report.py: _section_company_divergence() extended with demand_error_by_year subsection; year-by-year mean/max EAC prediction error; HIGH/MODERATE/Low signals; trend note (0.07% in 2016 → 3.26% mean / 15.56% max in 2024 as customers acquire EVs/solar/heat pumps the company cannot directly observe); smart meter action note. Early-exit condition updated to include demand data. Epistemic verifier: PASS. Root cause: Phase B life events create temporary estimation gap until company observes a full billing cycle with new device. Connects demand_error_by_year (company_divergence), Phase B, Phase 23a.

**Phase AN (2026-06-30):** Portfolio Concentration Risk -- 12 new tests (5,330 total). saas/reporting/annual_report.py: _section_portfolio_concentration_risk() computes HHI on per_customer_lifetime net_margin_after_cost_to_serve_gbp; segment margin share (I&C 98.7%, resi 0.9%, SME 0.5%); top-5 accounts by margin contribution + latest sim churn probability + churn-weighted margin-at-risk; concentration warning when I&C >95%. HHI=2,249 (MODERATE). Board finding: a single I&C departure removes 14-29% of all portfolio margin; resi/SME are effectively margin-neutral. Tests: 12/12 passing. Epistemic verifier: PASS. Connects per_customer_lifetime, churn_basis_risk.

**Phase AM (2026-06-30):** Pricing Basis Risk Attribution -- 12 new tests (5,318 total). saas/reporting/annual_report.py: _section_pricing_basis_risk() uses basis_risk_terms (149 per-contract forward-rate comparisons) to show year-by-year accuracy of the company forward curve: tariff_error_pct = (company_fwd - sim_fwd) / sim_fwd. Labels: HIGH OVER-PRICE (mean >+15%), moderate over, on target, UNDER-PRICE (mean <-5%). Post-crisis board warning when >=1 HIGH OVER-PRICE year in 2023+. Key finding: 2023 (+18.4%) and 2025 (+32.8%) are HIGH OVER-PRICE -- company locked in expensive crisis-era forwards after market normalised, mirroring the mechanism that eroded real UK supplier margins 2022-24. Tests: 12/12 passing. Epistemic verifier: PASS. Connects basis_risk_terms output, Phase 37b (forward curve).

**Phase AL (2026-06-30):** Counterfactual Retention Value -- 12 new tests (5,306 total). saas/reporting/annual_report.py: _section_counterfactual_retention() uses no_offer_churn_log + retention_log (calibrates P(retain|offer) from actuals = 94%) + per_customer_lifetime; computes counterfactual net benefit for each positive-ETM no-offer churn (5% discount resi, 8% SME/I&C); flags net-neg ETM churns as CORRECT PASS; root cause note when missed opportunities exist. Simulation finding: £3,621 net recoverable value from 4 missed opportunities (C3, C2, C6, C4) at £293 retention cost. C1 churn correctly declined (net-neg ETM). Tests: 12/12 passing. Epistemic verifier: PASS. Connects no_offer_churn_log (sim output), Phase AE (retention offers), Phase AK (churn root cause).

**Phase AK (2026-06-30):** Churn Root Cause Attribution -- 14 new tests (5,294 total). saas/reporting/annual_report.py: _section_churn_root_cause() cross-references customer_events (event_type=churned) with dynamic_pricing_log (last rate change), churn_basis_risk (rate-vs-SVT, company vs sim estimate), and per_customer_lifetime (segment, tenure, lifetime margin). Shows per-departed-account table; root cause summary (blind misses/warned/crisis-era/overpriced-at-departure). 6 simulation churns: £39,706 total lifetime margin lost; 3 company blind misses (sim 32%, company 0%); 3 crisis-era churns (2021-22). Tests: 14/14 passing. Epistemic verifier: PASS. Connects Phase AD (churn), Phase 11b (basis risk), Phase 15b (dynamic pricing).

**Phase AJ (2026-06-30):** CRM Risk Triage Section -- 14 new tests (5,280 total). saas/reporting/annual_report.py: _section_crm_intelligence() uses churn_basis_risk latest-renewal-per-customer + per_customer_lifetime to classify CRITICAL/HIGH/MEDIUM/LOW churn risk bands, show rate-vs-SVT positioning, compute lifetime margin at risk (CRITICAL+HIGH band), identify company blind spots (HIGH sim risk + <10% company estimate). Wired after _section_portfolio_intelligence_pack. No run_phase2b.py changes. Tests: 14/14 passing. Epistemic verifier: PASS. Connects Phases AD (churn bands), AC (repricing), 11b (churn basis risk).

**Phase AI (2026-06-30):** EAC Drift Snapshot -- 10 new tests (5,266 total). saas/reporting/annual_report.py: _section_eac_drift_snapshot() groups demand_estimation_log (Phase 23a/25a) by customer_id, computes first-to-latest EAC drift, classifies as significant (≥15%)/moderate (5-15%)/stable (<5%), infers likely cause (>50% drift: likely EV acquisition; >20%: EV or ASHP; <-15%: solar/efficiency upgrade), shows notable-drift table sorted by absolute drift magnitude, portfolio demand trend (N increasing / M decreasing / mean drift %). Silent when no demand_estimation_log. Observable billing data only — epistemic-compliant. Tests: 10/10. Epistemic verifier: PASS. Connects Phases 23a, 25a (demand estimation).

**Phase AH (2026-06-30):** Board Intelligence Pack -- 12 new tests (5,256 total). saas/reporting/annual_report.py: _section_portfolio_intelligence_pack() synthesises four sections from observable pipeline data: (1) Retention Intelligence — coverage rate (offers/at-risk), acceptance rate, margin protected, blind-miss avoidable loss; (2) Flexibility Revenue Intelligence — total revenue, revenue-per-enrolled-customer-year, enrollment CAGR, DFS CAGR since launch; (3) Churn Pattern Analysis — total churns, peak year, net book movement, portfolio trend; (4) Board Recommendations — up to 4 actionable recommendations derived from retention gap, offer fail rate, flexibility enrollment, crisis-year churn. Silent when no retention or churn data. Wired after _section_flexibility_revenue. Data sources: retention_log, no_offer_churn_log, company_event_log, flexibility_revenue_summary. Tests: 12/12 passing. Epistemic verifier: PASS. Connects Phases AG, AE, AD, AF.

**Phase AF (2026-06-30):** DSR/Flexibility Revenue Integration -- 15 new tests (5,232 total). company/market/flexibility_revenue_book.py (new): FlexibilityRevenueRecord (frozen; customer_id/year/has_ev/has_ashp/has_battery/flex_kw/capacity_market_revenue_gbp/dfs_revenue_gbp/total_revenue_gbp); FlexibilityRevenueBook (compute_year uses HouseholdDemandRegister.dynamic_assets to identify enrolled customers; CM revenue from 2016 onwards at T-4 rate £75/kW/yr; DFS revenue from 2022 onwards at £4.5/MWh x 20 events/yr; records_for_year/total_revenue_for_year/total_cm_revenue/total_dfs_revenue/flexibility_summary with per_year breakdown). Wired into simulation/run_phase2b.py (compute_year for all elec customers per year; returned in flexibility_revenue_summary + flexibility_revenue_by_year). Wired into saas/reporting/annual_report.py (flexibility_revenue_gbp per year in yearly dict; total_flexibility_revenue_gbp in report). Key finding: EV customer earns £555/yr CM + £666/yr DFS (2022+) = £1,221/yr; battery adds £375/yr CM + £450/yr DFS = £825/yr additional. Connects Phase AA (potential assessment), Phase N/Q (EV/battery asset wiring).

**Phase AE (2026-06-29):** Customer Retention Offer Book -- 21 new tests (5,217 total). company/crm/customer_retention.py (new): OfferType (LOYALTY_DISCOUNT/TOU_REFERRAL/DUAL_FUEL_BUNDLE/PRICE_MATCH/ACCOUNT_REVIEW/NO_OFFER); OfferDeclineReason (NET_NEGATIVE/INSUFFICIENT_MARGIN); RetentionOffer (frozen; max_spend=50% of net margin; is_affordable/expected_retention_value_gbp); CustomerRetentionBook (generate_offer selects by dominant driver: EV+RATE_SHOCK→TOU_REFERRAL zero-cost; RATE_SHOCK→PRICE_MATCH 8%; TENURE_SHORT/BASELINE→LOYALTY_DISCOUNT 5%; BILL_STRESS→ACCOUNT_REVIEW; net-neg→NO_OFFER; total_retention_spend_gbp/retention_summary). Completes retention trilogy: Phase AB (drift) → Phase AC (reprice) → Phase AD (churn risk) → Phase AE (retention offer).

**Phase AD (2026-06-29):** Portfolio Churn Risk Book -- 34 new tests (5,196 total). company/crm/portfolio_churn_risk.py (new): ChurnRiskBand (CRITICAL≥50%/HIGH≥30%/MEDIUM≥15%/LOW); ChurnRiskDriver (RATE_SHOCK/BILL_STRESS/TENURE_SHORT/BASELINE); CustomerChurnRisk (frozen; expected_loss_gbp/is_at_risk); PortfolioChurnRiskBook (assess wraps churn_model.py with full segment/fuel/hedge support; at_risk_customers/by_band/by_driver/total_revenue_at_risk_gbp/total_expected_loss_gbp/portfolio_churn_rate_pct/top_n_by_expected_loss/driver_breakdown/churn_risk_summary). Connects Phase J (profitability), Phase M (renewal conversion), Phase AC (repricing trigger → churn driver).

**Phase AC (2026-06-29):** Portfolio Repricing Action Book -- 24 new tests (5,162 total). company/crm/portfolio_repricing.py (new): RepricingPriority (CRITICAL/HIGH/MEDIUM/MONITOR); RepricingAction (frozen; tariff_delta_gbp_pa/estimated_margin_recovery_gbp_pa at 70% retention; is_urgent/is_actionable); PortfolioRepricingBook (plan_reprice recomputes recommended tariff at existing unit rate on new AQ; critical_actions/actionable_actions/by_priority/total_margin_at_risk_gbp/total_expected_recovery_gbp/top_n_by_margin_recovery/portfolio_reprice_summary). Priority logic: CRITICAL=urgent_drift+<=60d renewal; HIGH=urgent+<=180d or reprice+upcoming; MEDIUM=material drift+far renewal. Connects Phase AB (EAC drift), Phase M (renewal timing), Phase K (break-even assessor).

**Phase AB (2026-06-29):** EAC Drift Assessor -- 35 new tests (5,138 total). company/crm/eac_drift_assessor.py (new): DriftDirection/RenewalAction enums; EACDriftAssessment (frozen; drift_kwh/drift_pct/drift_direction/likely_cause/renewal_action/is_material); EACDriftBook (significant_increases/significant_decreases/renewal_reprice_candidates/urgent_reprice_candidates/mean_drift_pct/drift_summary). Thresholds: +15% = INCREASED, -10% = DECREASED, +30% = URGENT_REPRICE. Likely-cause inference: ev_acquired/ashp_installed/solar_installed/ev_and_ashp_acquired from CRM asset flags. Connects Phase C (billing-derived EAC), Phase H (AQ at signing), Phase M (renewal engine). First module to flag customers for repricing based on life-event-driven consumption drift.

**Phase AA (2026-06-29):** Demand Flexibility Potential Assessor -- 23 new tests (5,103 total). company/market/flexibility_potential.py (new): FlexibilityAssetType (EV/ASHP/BATTERY/EV_AND_BATTERY); FlexibilityEstimate (frozen; flex_kw/flex_kwh_per_event/dfs_revenue_gbp_pa/capacity_market_revenue_gbp_pa/total_annual_revenue_gbp/is_dfs_eligible/flex_mwh_per_event); FlexibilityPotentialBook (assess returns None if no assets; dfs_eligible/top_by_flex_kw/total_portfolio_flex_kw/total_portfolio_revenue_gbp_pa/by_asset_type/flexibility_summary). Calibrated: EV 7.4kW/ASHP 3kW/battery 5kW (UK typical). DFS £4.5/MWh × 20 events/yr × 1h; Capacity Market £75/kW/yr (T-4 2023). Key finding: EV+battery customer generates £2,046/yr flexibility revenue vs EV-only £930/yr. Connects to dsr_book.py for enrollment. Leverages Phases P (EV shape), I (ASHP), Q (battery) physical models.
**Phase Z (2026-06-29):** Smart Meter Consumption Reconciliation Book -- 23 new tests (5,080 total). company/billing/smart_meter_reconciliation.py (new): ReconciliationType (OVERBILLED/UNDERBILLED/NO_ADJUSTMENT); ReconciliationAdjustment (frozen; adjustment_kwh/credit_debit_gbp/is_back_billing_protected using SLC31A 12-month cap on domestic undercharges/recoverable_gbp=0 when protected/is_material £5 threshold); SmartMeterReconciliationBook (reconcile/adjustments_for/credits_owed_to_customers/charges_owed_by_customers/back_billing_protected_adjustments/total_credit_exposure_gbp/total_recoverable_gbp/total_unrecoverable_gbp/material_adjustments/reconciliation_summary). SLC 31A: domestic suppliers cannot recover undercharges for consumption >12 months before billing date (May 2018 rule); ~GBP90M sector write-off 2018-2022. I&C always recoverable. Connects to back_billing.py (Ph314), smart_meter_analytics.py.
**Phase Y (2026-06-29):** ToU Rate Card Optimiser -- 29 new tests (5,057 total). company/pricing/tou_rate_card.py (new): ToURateCandidate (frozen; overnight<standard<peak validation; octopus_go_style/aggressive_ev/conservative_ev classmethod factories; to_tou_rate_structure() conversion); RateCardEvaluation (frozen; margin_delta_gbp/is_margin_positive/is_customer_positive/viability_reason); ToURateCardOptimiser (evaluate/viable_rates/optimal_rate/best_customer_rate/optimiser_summary). Viability = customer_saving > 0 AND supplier_margin_tou > 0 AND margin_loss_pct <= threshold. Key finding: Octopus Go-style 7.5p overnight fails 20% threshold (74% margin reduction for overnight-heavy EV customers) but is viable at 80% threshold (supplier still earns £516 margin vs £1,989 flat). Conservative 10p overnight: £712 margin, 64% loss. Supplier must accept 60-75% margin reduction to offer meaningful overnight EV discount. Completes T-U-V-X-Y ToU analytics-to-product chain.
**Phase X (2026-06-29):** ToU Product Launch Decision Engine -- 25 new tests (5,028 total). company/pricing/tou_product_launch.py (new): LaunchReadinessSignal (LAUNCH/HOLD/MONITOR); ToULaunchThreshold (default_for: min 5% EV penetration, £500 max margin loss); ToULaunchAssessment (frozen; ev_penetration_pct/margin_at_risk_gbp/is_launch_viable/is_market_ready/signal/worst_case_margin_delta_gbp); ToUProductLaunchBook (assess/launch_history/readiness_trend/years_until_viable/launch_summary). Signal logic: MONITOR when EV penetration < threshold; HOLD when margin-at-risk > max loss; LAUNCH otherwise. Key finding: for EV-heavy portfolio with high cross-subsidy, HOLD is board recommendation (toU launch would cost more than the at-risk subsidy is worth). years_until_viable() extrapolates EV penetration trajectory to estimate when ToU becomes viable product. Also: test_warm_factor_reduces_consumption → test_warm_factor_reduces_consumption_ic + test_resi_consumption_uses_hdd_not_weather_factor (Phase W test fix: resi now uses HDD not weather_factor). Completes T-U-V-X analytics chain.
**Phase W (2026-06-29):** Gas Boiler Daily HDD Shape -- 13 new tests (5,003 total). simulation/gas_settlement.py: replaces static GAS_CONSUMPTION_MONTHLY_PROFILE × term-level weather_factor for resi/SME with per-day HDD-weighted shape (_GAS_BOILER_HEATING_FRACTION=0.70, _HDD_REF_ANNUAL from sim.weather_hdd). Daily heating = AQ × 0.70 × (hdd_today / hdd_ref_annual); DHW flat = AQ × 0.30 / 365. I&C keeps monthly profile (Phase 60). run_phase2b.py: removes weather_factor_for_term computation (was term-level scalar, now internal to settlement). Mirrors Phase I ASHP electricity pattern exactly. Annual total conserved with reference HDD; actual cold years add heating demand. Three existing tests updated: test_gas_seasonality.py, test_ic_gas_profile.py, test_phase30b_gas_policy_costs.py. Closes last major settlement accuracy gap: gas consumption now responds to daily weather, not just monthly averages.
**Phase V (2026-06-29):** ToU Migration Impact Scenario -- 16 new tests (4,990 total). company/pricing/tou_migration_scenario.py (new): MigrationScenario (frozen; migrated_count/retained_count/baseline_margin_gbp/post_migration_margin_gbp/margin_delta_gbp/revenue_delta_gbp/avg_customer_saving_gbp/is_margin_positive); ToUMigrationScenarioBook (run_scenario/compare_rates/best_supplier_scenario/portfolio_summary). Customers migrate in order of lowest cross-subsidy first. Key finding: for EV-heavy portfolio 0% migration is always best for supplier (flat-rate cross-subsidy never recovered under ToU). company/pricing/ev_cross_subsidy.py gains flat_revenue_gbp/tou_revenue_gbp/customer_saving_gbp properties on CrossSubsidyRecord. Closes T-U-V ToU chain.
**Phase U (2026-06-29):** EV Cross-Subsidy Register -- 16 new tests (4,974 total). company/pricing/ev_cross_subsidy.py (new): CrossSubsidyRecord (frozen; flat_margin_gbp/tou_margin_gbp/cross_subsidy_gbp=flat-tou/is_at_risk/years_with_ev); CrossSubsidyRegister (record via Phase T OVERNIGHT_HEAVY shape/top_n_by_cross_subsidy/at_risk_if_tou_launched/total_cross_subsidy_gbp/average_cross_subsidy_gbp/portfolio_summary with top_account_id). cross_subsidy proportional to annual_kwh; crisis year still positive. Operational complement to Phase T: supplier can rank all EV customers by cross-subsidy value for flat-tariff retention.
**Phase T (2026-06-29):** ToU Tariff Profitability Assessor -- 16 new tests (4,958 total). company/pricing/tou_tariff_assessor.py (new): DemandShapeClass (OVERNIGHT_HEAVY/STANDARD_FLAT/PEAK_HEAVY/WINTER_HEAVY); WholesaleBandRates.normal()/.crisis(); ToURateStructure.default() Octopus-Go style (7.5p/28.5p/45p); ToUProfitabilityComparison frozen (flat/tou revenue, shared wholesale_cost, margin_delta_gbp, is_tou_beneficial_for_supplier, customer_saving_gbp, supplier_preferred_tariff); ToUTariffAssessorBook (assess/flat_preferred_accounts/tou_preferred_accounts/overnight_heavy_assessments/portfolio_summary). Key finding: EV at 3,000 kWh normal market earns supplier GBP 746 flat vs GBP 189 ToU -- GBP 557 cross-subsidy under flat. Peak-heavy on ToU: supplier margin improves. ASHP (WINTER_HEAVY): modest delta. Closes ToU economics gap: Phase P made EV overnight shape accurate; Phase T makes flat vs ToU supplier profitability comparison concrete.
**Phase P (2026-06-29):** EV Smart Charging Shape (Overnight-Weighted) -- 12 new tests (4,942 total). simulation/run_phase2b.py: _EV_OVERNIGHT_PERIODS frozenset ({1..14, 47, 48} = 23:00-07:00, 16 periods); _EV_OVERNIGHT_FRACTION=0.90, _EV_DAYTIME_FRACTION=0.10. _weather_adjusted_shape_fn Phase N flat adder replaced with overnight-weighted distribution: ev_overnight_per_hh = ev_daily * 0.90 / 16; ev_daytime_per_hh = ev_daily * 0.10 / 32; conservation check: 90% + 10% = 100% daily. Triad periods (33-38 = 16:00-19:00) now correctly get the low daytime fraction — not inflated by EV (was unrealistic in Phase N). Overnight periods carry 9x more charge than daytime per HH period. UK Smart Charge Point Regulations 2021 mandate off-peak as default; ~85-90% home EV charging is overnight (NGESO). Annual total unchanged. Enables accurate ToU tariff economics (Phase T precondition): supplier sees EV customer wholesale cost overnight-heavy, flat-rate billing cross-subsidy now correctly modelled.
**Phase S (2026-06-29):** Unified Dual-Fuel Billing Engine + Payment Ledger -- 44 new tests (4,930 total). company/billing/dual_fuel_bill.py (new): FuelBillSection (frozen; fuel/period_start/period_end/days_in_period/consumption_kwh/unit_rate_pence/standing_charge_pence_per_day/standing_charge_gbp/energy_charge_gbp/levies_gbp/subtotal/vat_rate/vat_gbp/total/is_paid/effective_rate_pence), DualFuelBill (frozen; electricity/gas sections; balance_gbp/amount_owing_gbp/in_credit/billing_calendar/all_paid), DualFuelBillBook (gas_account_id C1g convention; build_bills groups elec+gas invoices by month bucket; cumulative_balance_gbp; outstanding_invoices). VAT by market: resi=5%, I&C=20%, SME=20% if >33kWh/day. company/billing/payment_ledger.py (new): PaymentMethodType (DD/PPM/BACS/Card/Cheque/Cash/CHAPS), PaymentOutcome (SUCCESS/FAILED/PENDING/REVERSED), PaymentRecord (frozen; is_successful/is_failed/is_pending), PaymentLedger (record/payments_for_account/successful_total_gbp/failed_payments/payment_method_breakdown/ledger_summary/portfolio_summary). Portal: /account/{id}/billing (new) -- unified dual-fuel billing page with per-fuel sections showing standing charges, consumption kWh, unit rate p/kWh, levies, VAT, total, payment status, pay buttons; account balance bar (credit/owing/zero). /account/{id}/consumption updated to split electricity + gas monthly tables for dual-fuel customers. Response to Rich: "billing is the heart of a supplier, currently very basic."
**Phase R (2026-06-29):** SEG Export Estimator — 21 new tests (4,886 total). company/regulatory/seg_export_estimator.py (new): AnnualExportEstimate (frozen; generation_kwh/self_consumed_kwh/exported_kwh/seg_rate_p_per_kwh/seg_payment_gbp), SEGExportEstimator (annual_yield_kwh/self_consumption_fraction/export_fraction/estimate_annual_export_kwh/estimate_and_record/portfolio_summary). company/regulatory/seg_book.py: SEGContract gains capacity_kwp field (default 0.0, backward-compatible). Constants: ANNUAL_YIELD_KWH_PER_KWP=850 (SAP 10.2); SELF_CONSUMPTION_STANDARD=0.50/WITH_BATTERY=0.70 (BEIS 2022); SEG_START_YEAR=2020. estimate_and_record() raises ValueError pre-2020 (FIT era); records SEGPayment in SEGBook; 2022 crisis rate (7.5p) inflates payment vs 2020 (4.0p). portfolio_summary() dedups by customer_id. Closes the SEG gap: SEGBook (Phase 310) was unconnected; estimator wires capacity-based export estimation for solar customers registered post-2020.
**Phase Q (2026-06-29):** Battery Home Energy Storage Settlement Wiring -- 14 new tests (4,865 total). simulation/household_demand.py: dynamic_assets() now returns battery/battery_kwh (was missing -- battery acquired via life events but invisible to settlement). simulation/run_phase2b.py: _BATTERY_EVENING_PEAK frozenset (periods 33-40 = 16:00-20:00); _battery_daily_dispatch() helper (charge from excess solar outside evening peak, SOC tracking, discharge in evening peak, 90% roundtrip efficiency); _weather_adjusted_shape_fn battery-aware path: when has_battery+has_solar+irradiance available, computes gross_load via build_demand_shape(solar=False) + solar_gen via solar_generation_shape(irradiance), then calls _battery_daily_dispatch in place of standard solar-clamped reduction. Non-battery path unchanged. Effect: battery-equipped solar homes now show reduced evening peak import (16:00-20:00) and correctly-modelled midday self-consumption (excess solar charges battery rather than being exported and discarded). Closes the last household asset gap: solar, EV, ASHP, and battery all now affect the HH settlement shape.
**Phase O (2026-06-29):** Solar Dynamic Settlement Wiring -- 12 new tests (4,851 total). simulation/run_phase2b.py: (1) _weather_adjusted_shape_fn now updates assets["solar"] from dynamic_assets alongside assets["ev"] (was missing -- life-event solar never applied irradiance reduction); (2) cloud_cover and latitude always passed for all profile-class customers (removed has_solar gate); (3) cloud_cover_by_customer built for all elec customers not just static-solar C4. Customers acquiring solar via life events (Phase B) now get correct half-hourly import reduction: summer midday ~30-40% reduction, night periods unchanged, import clamped >= 0. Phase 25a (static C4 solar customer) unaffected -- irradiance was already applied there.
**Phase N (2026-06-29):** EV Settlement Wiring + Physical Suitability Constraints -- 26 new tests (4,861 total). simulation/household.py: has_driveway (off-street parking gate), roof_aspect (south/east_west/north/na), hp_eligible property. simulation/life_events.py: EV blocked for no-driveway; solar blocked for north/na aspect; HP blocked for flats/1-bed. simulation/run_phase2b.py: EV flat demand shape wired into _weather_adjusted_shape_fn (ev_annual_kwh/365.25/48, from ev_acquired date). background/session_watchdog.py: 3 usage-limit NTFY sends suppressed (Rich flagged as spam). EV now fully settled like ASHP Phase G. All permutations supported for eligible homes.
**Phase M (2026-06-29):** Renewal Conversion Rate Book -- 21 new tests (4,835 total). company/crm/renewal_conversion.py (new): RenewalOutcome (ACCEPTED/SWITCHED/LAPSED/PENDING), RenewalChannel (DIRECT_PHONE/ONLINE/BROKER/AUTOMATIC), RenewalRecord (frozen; days_to_decision/days_notice_before_term_end/met_notice_obligation SLC22 42-day/is_retained), RenewalConversionBook (outcomes_for/conversion_rate_pct/avg_days_to_decision/notice_obligation_breaches/pending_decisions/best_converting_segment/conversion_summary). Fills CRM gap: acquisition→tenure→renewal→churn loop now complete. SLC 22 minimum 42-day notice before term end.
**Phase L (2026-06-29):** Tariff Segment Profitability Book -- 19 new tests (4,814 total). company/pricing/segment_profitability.py (new): SEGMENT_RESI_CREDIT/RESI_PPM/SME/IC constants; SegmentProfitabilityRecord (frozen; total_net_contribution_gbp/is_net_negative/average_net_contribution_gbp/net_margin_pct/average_revenue_per_account_gbp); SegmentProfitabilityBook (record/aggregate_from_customers by segment+year/latest_for_segment/net_negative_segments/most_profitable_segment/segment_summary). Portfolio-level complement to Phase J (per-customer) and Phase K (cap constraints). Observable inputs only: revenue/wholesale/levy/operating cost breakdowns from billing data.
**Fix (2026-06-29):** Phase 44a stale import + Phase G test updates -- 13 previously-broken tests now passing (4,795 total). company/crm/customer_profitability.py: estimate_prior_term_net_margin() groups settlement records by term_start, returns prior-term net margin for the most recent completed term (MIN_RECORDS_FOR_JUDGEMENT=3); compute_profitability_uplift() returns NET_NEGATIVE_UPLIFT_GBP_PER_MWH=5 GBP/MWh when net-negative, 0 otherwise. tests/simulation/test_phase_g_ashp_settlement.py: 3 tests updated for Phase I HDD-weighted ASHP shape (flat assertions replaced with HDD-aware assertions).
**Phase K (2026-06-29):** Break-Even Tariff Assessor -- 21 new tests (4,782 total). company/pricing/break_even_assessor.py: BreakEvenAssessment (frozen; break_even_p_per_kwh=total_cost+minimum_margin; is_cap_constrained when cap<break_even; headroom_p_per_kwh/uncovered_loss_gbp/minimum_viable_tariff_gbp_pa), BreakEvenAssessorBook (record/latest_for/cap_constrained/total_uncovered_loss_gbp/cap_constrained_rate_pct/assessor_summary). Connects Phase J (profitability detection) with Ph295 (price cap) and Ph294 (CTS). Key test: 2022-Q4 cap tight -- ASHP customer at 8,600 kWh with high levies is structurally constrained (company cannot price profitably within regulatory ceiling). None cap = uncapped I&C/SME segments. Closes "flat margin" loop: detection (PhJ) + structural diagnosis (PhK).
**Phase J (2026-06-29):** Customer Profitability Register -- 25 new tests (4,761 total). company/crm/customer_profitability.py: CustomerProfitabilityRecord (frozen; gross_margin_gbp/net_contribution_gbp/is_net_negative/gross_margin_pct/net_margin_pct), CustomerProfitabilityBook (record/latest_for/history_for/net_negative_accounts/top_n_by_contribution/total_net_contribution_gbp/net_negative_rate_pct/profitability_summary). Observable inputs only: annual_revenue_gbp/wholesale_cost_gbp/levy_cost_gbp/operating_cost_gbp. Test includes ASHP-customer-drives-net-negative scenario: 8,600 kWh @ standard tariff, volume-driven levies (CM/CfD/RO/BSUoS) exceed margin. Addresses CLAUDE.md "flat margin makes some customers net-negative" concern. Connects to cost_to_serve (Ph294), clv_calculator, dual_fuel_account (Ph331).
**Phase I (2026-06-29):** ASHP Seasonal Electricity Shape (HDD-Weighted) -- 10 new tests (4,736 total). simulation/run_phase2b.py: _weather_adjusted_shape_fn Phase G flat ASHP adder replaced with HDD-weighted seasonal profile. 70% of ASHP annual kWh scaled by daily HDD / REFERENCE_MONTHLY_HDD sum (same basis as gas boiler gas consumption); 30% DHW component flat year-round. Uses existing get_hdd() and REFERENCE_MONTHLY_HDD from sim/weather_hdd.py. Annual total conserved (~5,500 kWh over a reference year, within 3%). In warm 2020 actual HDD ~81% of reference, giving ~4,800 kWh -- correct weather-responsive behaviour. Winter peak ~2x flat-average daily load; July trough ~0.03x flat-average. First time ASHP electricity demand is weather-responsive. Replaces Phase G comment "first approximation".
**Phase H (2026-06-29):** Electricity EAC Multiplier at Term Signing -- 12 new tests (4,726 total). simulation/run_phase2b.py: _company_eac_estimate() gains base_eac_override kwarg (falls back to it on first term, ignores on renewal terms where billing history is used). At electricity term signing: eac_multiplier_for_date() called on household_demand_register, declared EAC multiplied by EPC*(1+ev_fraction+ashp_fraction)*(1-solar_fraction), result used as override. EV customers: first-term EAC correctly higher; solar customers: correctly lower; ASHP customers: matches Phase G settlement uplift. No double-counting on renewal terms (billing history already reflects actual consumption). Mirrors Phase D gas_eac_multiplier_for_date wiring. Tests: first-term uses override, renewal-term ignores override, EV uplift, solar reduction, ASHP >1, solar < no-solar, adjusted-base identity.
**Phase G (2026-06-29):** ASHP Electricity Settlement Wiring -- 12 new tests (4,714 total). simulation/household.py: ASHP_BASE_ELECTRICITY_KWH=5_500.0 module-level constant. simulation/run_phase2b.py: _weather_adjusted_shape_fn gains Phase G block after EPC multiplier: household_at_date() for date + ashp_annual_kwh()/365.25/48 per half-hour, additive flat load for heat pump homes. Phase F built eac_multiplier_for_date() but never called it in settlement (eac_multiplier_for_date has 0 production call sites). Gas side (gas_eac_multiplier_for_date, Phase D) was wired; electricity side was not. Phase G closes the gap: from ASHP install date, demand shape +5,500 kWh/yr + gas AQ -88% (Phase D). Tests: uplift amount ≈5,500 kWh/yr; uplift absent before install date; EPC + ASHP independent; district heat zero uplift; I&C zero uplift; ground-source same as air-source; pre/post timing via life event injection.
**Phase F (2026-06-29):** Heat Pump Electricity Uplift -- 14 new tests (4,702 total). simulation/household.py: ashp_annual_kwh() -> 5,500 kWh/yr for ASHP homes (BEIS Electrification of Heat trial 2021-22; DESNZ 2023 Roadmap median 5,200 kWh/yr for pre-2000 stock; 5,500 kWh as calibrated midpoint for EPC C-D portfolio mix). simulation/household_demand.py: eac_multiplier_for_date() extended from EPC*(1+EV)*(1-solar) to EPC*(1+EV+ASHP)*(1-solar); _cid_hash() replaces hash(cid) with deterministic md5-based hash (fixes PYTHONHASHSEED non-reproducibility). Tests in test_phase_c/d_*.py updated for new invariant (non-increasing rather than stable). Fidelity: from ASHP install date, electricity EAC rises +5,500 kWh AND gas AQ drops to 12% residual (Phase D) — first time single heat_pump_installed life event produces correct dual-fuel effects. Connects to household.py (A), life_events.py (B), household_demand.py (C/D/E), gas_settlement.py.

**Phase E (2026-06-29):** EPC Band Evolution via Insulation Upgrades -- 19 new tests (4,688 total). simulation/household.py: epc_consumption_multiplier() now applies insulation-level caps: FULL insulation caps at 1.00 (EPC-C equivalent), PARTIAL caps at 1.25 (EPC-D equivalent). Caps apply only upward (A/B homes at 0.75 are unaffected). Effect: an EPC-E home (1.55x) with PARTIAL insulation upgrade bills at EPC-D rates (1.25x) from the upgrade date — flowing through electricity EAC (Phase C) and gas AQ (Phase D) settlement. First time ECO-scheme insulation events (Phase B life events) affect P&L. Connects to household.py (Phase A), life_events.py (Phase B), household_demand.py (Phase C), gas_settlement.py (Phase D).

**Phase D (2026-06-27):** Gas EAC Integration with Household Demand Register -- 16 new tests (4,669 total). simulation/household_demand.py: GAS_HEAT_PUMP_RESIDUAL_FRACTION = 0.12; HouseholdDemandRegister.gas_eac_multiplier_for_date(cid, date) -> float: returns epc_consumption_multiplier() for gas-boiler resi/SME (EPC-D=1.25, EPC-E=1.55), GAS_HEAT_PUMP_RESIDUAL_FRACTION for heat-pump homes, 1.0 for I&C/non-residential. simulation/run_phase2b.py: 3-line change applies multiplier to aq_kwh at gas term signing. Effect on declared AQs: C1g 12,000->15,000 kWh (+25%), C2g 15,000->18,750 kWh (+25%), C3g 14,000->21,700 kWh (+55%), C4g 22,000->34,100 kWh (+55%), C_IC3g unchanged. Total resi gas volume +42%; gas P&L magnitude increases proportionally. First time EPC band affects gas consumption. Connects household.py (Phase A), life_events.py (Phase B), household_demand.py (Phase C) to gas_settlement.py.

**Phase C (2026-06-27):** Household-Driven EAC Integration -- 26 new tests (4,652 total). simulation/household_demand.py (new): HouseholdDemandRegister: builds household register for all 18 customers; generates life events per customer 2016-2025 (seeded RNG); epc_multiplier(cid, date) -> float; eac_multiplier_for_date(cid, date) -> composite float (EPC * (1+EV_fraction) * max(0, 1-solar_fraction)); dynamic_assets(cid, date) -> {ev/solar/smart_meter}. simulation/run_phase2b.py: instantiates HouseholdDemandRegister at startup; passes dynamic_assets to demand model and epc_multiplier to settlement shape. Effect: EPC-D homes draw 1.25x segment EAC; EPC-E 1.55x; EV acquisition adds ~2,143 kWh/yr from acquisition date; solar install reduces net import from install date. First time household physical model (Phase A) and life events engine (Phase B) affect actual simulation P&L. Connects to household.py (Phase A), life_events.py (Phase B), run_phase2b.py.

**Phase B (2026-06-27):** Life Events Engine -- 32 new tests (4,626 total). simulation/life_events.py (new): LifeEvent frozen dataclass (customer_id/event_date/event_type/payload); generate_life_events() -- Bernoulli trials per year on calibrated UK probability tables (solar 3%→5.7% 2016-2025 DESNZ REPD; EV 0.3%→7% DfT; ASHP 0.1%→0.6%; boiler replacement by age OLD=9%/MID=4%/NEW=1%; insulation upgrade POOR=3%/PARTIAL=1% ECO4); apply_events() reconstructs Household state by replaying event log; household_at_date() for point-in-time reconstruction. Constraints: no flat roof solar, no I&C EVs, battery conditional on solar install, no duplicate acquisitions. All 18 real customers generate events without error. Connects to household.py (Phase A).

**Phase A (2026-06-27):** Household Physical Model -- 36 new tests (4,594 total). simulation/household.py (new): PropertyType/BuildEra/HeatingSystem/BoilerAge/InsulationLevel enums; Household frozen dataclass; epc_consumption_multiplier() calibrated to EHS 2022-23 AT1_6 (C=1.0 baseline; 50% prebound-effect adjustment; A/B=0.75x → G=2.20x); seasonal_flatness_factor(); ev_annual_kwh() (7,500 miles @ 3.5 MPkWh = 2,143 kWh/yr); solar_annual_generation_kwh() (850 kWh/kWp/yr SAP10.2). make_household() maps existing customer records to representative UK profiles (home_type → PropertyType/BuildEra/HeatingSystem/InsulationLevel); build_household_register() covers all 18 customers. Baseline 2016: 2.8% solar, no EVs, no heat pumps, gas-heated resi.

**Phase 332 (2026-06-27):** Risk Committee Deterministic Engine + File API Fix -- 21 new tests (4,559 total). sim/risk_committee_rules.py: parse_handshake (hf/VaR ratio/sigma_recent/triggered_customers from structured handshake context), should_escalate (sigma > 1.5 or all triggered at hf=1.0), apply_rules (step: 0.25/0.20/0.15 by VaR ratio), decide (returns escalate_to_llm flag + adjustments dict). Updated sim/risk_committee_agent.py: rule engine by default; escalates to Ollama only for crisis sigma or maxed-out portfolio. background/file_api.py: auto-loads .env.file-api if FILE_API_KEY not in env (fixes 403 on restart). background/start_worker.sh: sources .env.file-api before starting file-api session. Expected: removes ~95% of Ollama committee calls; LLM reserved for genuine crisis events.

**Phase 331 (2026-06-27):** Dual-Fuel Account Consolidator -- 25 new tests (4,538 total). company/crm/dual_fuel_account.py: FuelType (ELECTRICITY/GAS), FuelLeg (frozen; supply_point_ref MPAN/MPRN; estimated_annual_cost_gbp from EAC/AQ + unit_rate + standing; active flag), DualFuelAccount (frozen; is_dual_fuel/is_electricity_only/is_gas_only/has_any_supply/combined_annual_cost_gbp/active_fuels), DualFuelAccountBook (register_electricity_leg/register_gas_leg raises ValueError on wrong fuel/get_account/all_accounts/dual_fuel_accounts/electricity_only/gas_only/total_combined_annual_cost_gbp/dual_fuel_summary). Electricity settled via BSC/MPAN; gas via UNC/MPRN; same customer account, separate settlement. Connects to supply_point_register (Ph299), customer_registry, tariff_engine.

**Phase 330 (2026-06-27):** Payment Method Register -- 22 new tests (4,513 total). company/billing/payment_method_register.py: PaymentMethod (DIRECT_DEBIT/PREPAYMENT_METER/BACS_TRANSFER/CHEQUE/CASH), PaymentMethodSource (VOLUNTARY/DEBT_MANDATED/VULNERABILITY_PROTECTION/DEFAULT), PaymentMethodRecord (frozen; is_prepayment/is_direct_debit/is_debt_mandated), PaymentMethodRegister (set_method/current/history_for/accounts_by_method/ppm_accounts/dd_accounts/debt_mandated_ppm/method_breakdown/payment_method_summary). UK: ~70% DD, ~15% PPM; debt-mandated PPM monitored by Ofgem; SLC 27 PPM install rules; 2023 forced-fitting scandal. Connects to direct_debit, prepayment, ppm_debt_loading (Ph313), debt_collection (Ph311).

**Phase 329 (2026-06-27):** Fuel Poverty Indicator Book -- 21 new tests (4,491 total). company/regulatory/fuel_poverty.py: FuelPovertyDefinition (CLASSIC >10% income / LIHC post-2013 England / AFFORDABLE_WARMTH Scotland), FuelPovertyRisk (LOW/MODERATE/HIGH/FUEL_POOR), FuelPovertyAssessment (frozen; energy_as_pct_income/income_after_energy_gbp/risk/is_fuel_poor -- LIHC: below 60% median after costs AND >10%), FuelPovertyBook (latest_for/fuel_poor_accounts uses only latest per account/high_risk_accounts/fuel_poverty_rate_pct/fuel_poverty_summary). Real: 6.5M UK households fuel poor 2023; Ofgem Consumer Duty: must identify and act. Connects to whd_book (Ph281), debt_collection (Ph311), consumer_duty (Ph283).

**Phase 328 (2026-06-27):** Disconnection Warning Register -- 17 new tests (4,470 total). company/billing/disconnection_warning.py: WarningStep (WARNING_1/2/3/DISCONNECTION_NOTICE), WarningStatus (PENDING/SENT/RESOLVED/OVERRIDDEN), DisconnectionWarning (frozen; earliest_next_action_date/can_escalate), DisconnectionWarningRegister (mark_sent/resolve/override/can_disconnect requires full sequence + 28-day notice/outstanding_warnings/warning_summary). SLC 27/SoP Regs: 4-contact minimum; 28-day formal notice; 2023 Ofgem investigated suppliers threatening disconnection without completing sequence. Connects to debt_collection (Ph311), winter_moratorium (Ph325).

**Phase 327 (2026-06-27):** Third Party Authority (TPA) Register -- 19 new tests (4,453 total). company/crm/tpa_register.py: TPAScope (VIEW_ONLY/BILLING_MANAGEMENT/FULL_AUTHORITY), TPARelationship (CARER/FAMILY_MEMBER/ENERGY_ADVISOR/DEBT_CHARITY/SOLICITOR/POWER_OF_ATTORNEY/LANDLORD), TPARecord (frozen; is_active/has_billing_access/has_full_authority), TPARegister (grant/revoke/expire/active_tpas_for_account/expiring_soon/power_of_attorney_accounts/tpa_summary). Ofgem Consumer Duty/SLC: must respect designated TPAs; POA legally binding; GDPR Article 6 lawful basis for TPA data sharing. Connects to consumer_duty (Ph283), priority_services, billing.

**Phase 326 (2026-06-27):** DD Indemnity Claim Register -- 23 new tests (4,434 total). company/billing/dd_indemnity.py: DDIndemnityReason (NOT_AUTHORISED/AMOUNT_INCORRECT/TIMING_INCORRECT/DUPLICATE_PAYMENT/FRAUDULENT), DDIndemnityStatus (RECEIVED/INVESTIGATING/UPHELD/REJECTED/WRITTEN_OFF), DDIndemnityClaim (frozen; is_active/creates_debt/is_investigation_overdue 10-WD), DDIndemnityRegister (receive_claim/start_investigation/uphold/reject/write_off/overdue_investigations/total_exposure_gbp/total_upheld_gbp/dd_indemnity_summary). BACS DD Guarantee: bank refunds immediately; supplier investigates within 10 WD; upheld = debt on account; ~2-3% of DD customers raise annually. Connects to direct_debit, billing_dispute, debt_collection (Ph311).

**Phase 325 (2026-06-27):** Winter Disconnection Moratorium Register -- 25 new tests (4,411 total). company/billing/winter_moratorium.py: MoratoriumType (WINTER_DOMESTIC/VULNERABLE_YEAR_ROUND/DEBT_MORATORIUM), DisconnectionRisk (NO_RISK/PROTECTED/AT_RISK), MoratoriumRecord (frozen; is_active/protection_status), is_winter_period() (Nov-Mar), WinterMoratoriumRegister (register/end_moratorium/is_protected/can_disconnect/vulnerable_protections/winter_protections/moratorium_summary). SLC 27/Gas SoP Regs: domestic Nov-Mar disconnection ban; vulnerable customers year-round; 2022-23 PPM-forcing scandal breached these rules. Connects to debt_collection (Ph311), consumer_duty (Ph283), priority_services.

**Phase 324 (2026-06-27):** MHHS Readiness Tracker -- 22 new tests (4,386 total). company/market/mhhs_tracker.py: MHHSMilestone (8: DCC_CONNECTIVITY/HH_DATA_INGESTION/NHH_PROFILE_MIGRATION/SETTLEMENT_SYSTEM_UPGRADE/CUSTOMER_COMMUNICATION/ELEXON_REGISTRATION/GO_LIVE_SHADOW/GO_LIVE_PRODUCTION), MHHSMilestoneStatus (NOT_STARTED/IN_PROGRESS/COMPLETE/AT_RISK/FAILED), MHHSMilestoneRecord (frozen; is_overdue/days_to_target), MHHSReadinessSnapshot (frozen; migration_completion_pct/is_on_track), MHHSReadinessTracker (record_milestone/update_milestone/record_snapshot/overdue_milestones/complete_milestones/at_risk_milestones/readiness_rag/mhhs_summary). Ofgem SCR 2020/BSC P272: shadow running Nov 2024; production June 2025; DCC central infrastructure for SMETS2 HH data. Connects to smart_meter_rollout (Ph284), settlement_reconciler.

**Phase 323 (2026-06-27):** Energy Theft Reporting Book -- 21 new tests (4,364 total). company/billing/energy_theft_book.py: TheftCaseStatus (SUSPECTED/UNDER_INVESTIGATION/CONFIRMED/DNO_NOTIFIED/ESTIMATED_BILL_RAISED/CLOSED_*), TheftType (METER_TAMPERING/BYPASSED/FRAUDULENT_READS/COMMUNICATION_INTERFERENCE), TheftCase (frozen; is_dno_notification_overdue 2-WD from confirmation/is_active), EnergyTheftBook (raise_case/start_investigation/confirm_theft/notify_dno/raise_estimated_bill/close/active_cases/confirmed_cases/overdue_dno_notifications/total_estimated_loss_kwh/theft_summary). GS(SS)5: 2-WD DNO notification post-confirmation; 3-year back-bill exception to 12-month SLC 31A rule; 2.6 TWh stolen annually UK. Connects to theft_indicator (billing), supply_point_register (Ph299).

**Phase 322 (2026-06-27):** Deemed Contract Register -- 22 new tests (4,343 total). company/billing/deemed_contract.py: DeemedSupplyReason (NEW_TENANT/VOID_PERIOD_ENDED/ACQUISITION_DEFAULT/SUPPLIER_SWITCH_FAIL), DeemedContractStatus (ACTIVE_DEEMED/NOTIFIED/CONVERTED/VACATED), DeemedContractRecord (frozen; is_notification_overdue 5 working-day deadline/months_on_deemed/is_extended_deemed after 12m), DeemedContractRegister (register/notify/convert/vacate/active_deemed/overdue_notifications/extended_deemed/records_by_reason/deemed_summary). Ofgem SLC 2B: 5 working-day notification; after 12 months extra obligations + right to switch without exit fee. Connects to cot.py (deemed_rate_gbp_per_kwh), supply_point_register (Ph299), cos_process (Ph298).

**Phase 321 (2026-06-27):** Supplier of Last Resort (SoLR) Register -- 24 new tests (4,321 total). company/crm/solr_register.py: SoLRStatus (TRANSFERRED/NOTIFIED/CONTRACT_OFFERED/CONTRACT_ACCEPTED/INTEGRATED), SoLRTransferRecord (frozen; is_notification_overdue/is_contract_offer_overdue/is_in_solr_billing_period), SoLRDesignation (frozen), SoLRRegister (record_designation/transfer/notify/offer_contract/accept/integrate/active_transfers/overdue_notifications/overdue_contract_offers/in_solr_billing_period/total_credit_claimed_gbp/solr_summary). 5-day notification/30-day contract offer/90-day SVT billing periods. 2021-22: 28 supplier failures, 4M+ customers via SoLR. Connects to supply_point_register (Ph299), account_closure (Ph312), credit_refund (Ph320).

**Phase 320 (2026-06-27):** Credit Refund Book -- 26 new tests (4,297 total). company/billing/credit_refund.py: RefundTrigger (CUSTOMER_REQUEST/ACCOUNT_CLOSURE/ANNUAL_CREDIT_REVIEW/DECEASED_ESTATE), RefundStatus (PENDING/APPROVED/PAID/REJECTED/HELD), CreditRefundRecord (frozen; working_days_to_pay/is_overdue/breached_deadline), CreditRefundBook (raise_refund/approve/pay/reject/hold/pending_refunds/overdue_refunds/deadline_breaches/total_outstanding_gbp/refund_summary). Ofgem SLC 14: credit balance refund within 10 working days (tightened from 28 calendar days in 2019); 2022 crisis: multiple enforcement notices for suppliers withholding customer credit balances. Connects to account_closure (Ph312), invoice (billing).

**Phase 319 (2026-06-27):** Hedge Effectiveness Assessment Book -- 29 new tests (4,271 total). company/risk/hedge_effectiveness.py: HedgeRelationshipType (FAIR_VALUE/CASH_FLOW), EffectivenessOutcome (HIGHLY_EFFECTIVE/INEFFECTIVE/PROSPECTIVE_ONLY), EffectivenessTest (frozen; effectiveness_ratio_pct/outcome/is_effective/ineffectiveness_gbp), HedgeEffectivenessBook (tests_for_hedge/tests_for_period/failed_tests/effective_tests/de_designated_hedges/total_ineffectiveness_gbp/effectiveness_summary). IFRS 9 80-125% retrospective test; de-designation triggers P&L recognition of all gains/losses; 2022 crisis caused widespread de-designation as customer volumes shrank vs hedged quantities. Connects to forward_book (Ph307), hedge_policy (Ph22b), var_monitor (Ph282).

**Phase 318 (2026-06-27):** Financial Resilience Assessment Book -- 27 new tests (4,242 total). company/risk/financial_resilience.py: FRAStatus (RESILIENT/ADEQUATE/BORDERLINE/INADEQUATE), FRATrigger (ROUTINE_QUARTERLY/MARKET_STRESS_EVENT/REGULATOR_DIRECTED), FRAAssessment (frozen; total_liquidity_gbp/months_of_liquidity/status/is_compliant/period_label), FinancialResilienceBook (record/assessments_for_year/latest_assessment/inadequate_quarters/borderline_or_worse/trend_is_deteriorating/fra_summary). Ofgem FRA Framework post-2022: 28 supplier failures; mandatory quarterly board sign-off; 12m liquidity minimum; stress+VaR must pass. Connects to stress_test (Ph303), var_monitor (Ph282), margin_call_book (Ph289), corporation_tax (Ph316).

**Phase 317 (2026-06-27):** VAT Book -- 20 new tests (4,215 total). company/finance/vat_book.py: VATRateCategory (DOMESTIC_REDUCED 5%/STANDARD 20%/ZERO/EXEMPT), classify_vat_category (residential->5%; SME <=33kWh/day elec or <=145kWh/day gas -> 5%; I&C->20%), VATTransaction (frozen; vat_rate/vat_gbp/gross_amount_gbp), VATQuarterlyReturn (frozen; net_vat_due/is_repayment), VATBook (record_transaction/transactions_for_period/quarterly_return with 8% input VAT estimate/total_output_vat_gbp by year/vat_summary). Real data: UK domestic energy 5% since Finance Act 1994; business 20%; SME qualifying threshold HMRC concession; quarterly HMRC returns within 1m+7d of quarter end; 2022 billing errors caused wrong VAT rate misapplication. Connects to billing/invoice, ccl_ledger (Ph304), company_pl, corporation_tax (Ph316).
**Phase 316 (2026-06-27):** Corporation Tax Provision Book -- 24 new tests (4,195 total). company/finance/corporation_tax.py: _ct_rate_for_year 2016-2025 (20% 2016, 19% 2017-2022, 25% 2023+), TaxProvision (frozen; taxable_profit=PBT-loss_relief; current_tax_gbp=taxable*rate; profit_after_tax/effective_rate_pct/is_loss_year), CorporationTaxBook (provision_for_year with automatic loss-carry-forward relief; total_tax_paid/loss_years/accumulated_losses_gbp/tax_summary). Real data: UK CT rate rises from 19% to 25% April 2023 (largest rise since 1974, Finance Act 2021); Energy Profits Levy (EPL) applies to producers only, NOT energy suppliers; loss relief: trading losses carried forward indefinitely. For a GBP1M net profit supplier: +GBP60k/yr tax from 2023. Connects to company_pl (Ph?), pnl.py, management_accounts.
**Phase 315 (2026-06-27):** Payment Plan Adequacy Checker -- 19 new tests (4,171 total). company/billing/payment_plan_adequacy.py: ATPCompliance (AFFORDABLE/BORDERLINE/UNAFFORDABLE/UNKNOWN), PaymentPlanAdequacyCheck (frozen; disposable_income_gbp=income-essentials; plan_as_pct_disposable; compliance: <=15% AFFORDABLE, 15-25% BORDERLINE, >25%/residual<GBP50 UNAFFORDABLE; is_compliant), PaymentPlanAdequacyBook (record_check/latest_for/non_compliant_plans/borderline_plans/vulnerable_non_compliant/total_at_risk_gbp/adequacy_summary). Ofgem SLC 27A Ability to Pay guidance: plan ideally <15% disposable income; 2022-23: energy bills tripled, 40% of plans became unaffordable (Citizens Advice 2023); unaffordable plans -> PPM installation -> self-rationing -> fuel poverty. Connects to payment_plan.py, ppm_debt_loading (Ph313), debt_collection (Ph311), vulnerability_index, warm_home_discount (Ph281).
**Phase 314 (2026-06-27):** Back-billing Compliance Book -- 16 new tests (4,152 total). company/billing/back_billing.py: BackBillingReason (ESTIMATED_READ_CORRECTED/SMART_METER_INSTALL_REVEALED/BILLING_SYSTEM_ERROR/SUPPLIER_ERROR), BackBillingAssessment (frozen; billing_date/consumption_period_start-end/billed_amount_gbp/is_domestic; cap_applies: domestic+post-2018-05+period_start<12m_ago; capped_amount_gbp pro-rata allowed days; written_off_gbp=billed-capped), BackBillingBook (record/assessments_for/capped_assessments/non_compliant_if_charged_full/total_written_off_gbp/total_billed_gbp/back_billing_summary). Ofgem SLC 31A effective 01 May 2018: domestic only; triggered most after SMETS2 install reveals years of estimated reads; sector wrote off ~GBP90M 2018-2022; non-domestic excluded (commercial terms). Connects to billing/invoice, meter_read_validation, smart_meter_rollout (Ph284), hh_consumption.
**Phase 313 (2026-06-27):** PPM Debt Loading Tracker -- 19 new tests (4,136 total). company/billing/ppm_debt_loading.py: PPMDebtLoadStatus (ACTIVE/SUSPENDED/COMPLETED), PPMDebtLoad (frozen; debt_amount_gbp/recovery_rate_pct/is_domestic/is_smart_meter/customer_consented; max_load_gbp GBP250 domestic; is_compliant [>250 fails/rate>5% fails/smart-no-consent fails]; expected_recovery_days(monthly_spend)), PPMDebtLoadingBook (record_load/suspend/complete/active_loads/non_compliant_loads/smart_meter_consents_missing/total_loaded_gbp/loading_summary). Real calibration: Ofgem PPM Rules 2019 max GBP250/fuel domestic; 5% recovery rate cap per top-up; smart PPM requires customer consent (2019); British Gas 2023 forced-fitting scandal: warrants used to install PPMs on vulnerable customers -- Ofgem banned forced-fitting April 2023. Connects to debt_collection (Ph311), account_closure (Ph312), prepayment.py, smart_meter_rollout (Ph284).
**Phase 312 (2026-06-27):** Account Closure Book -- 23 new tests (4,117 total). company/billing/account_closure.py: ClosureReason (CUSTOMER_SWITCH/VACANT_PROPERTY/CUSTOMER_DECEASED/BUSINESS_CLOSURE), ClosureStatus (INITIATED/FINAL_READ_RECEIVED/FINAL_BILL_ISSUED/DEPOSIT_RETURNED/DEPOSIT_APPLIED/DEBT_REFERRED/CLOSED), AccountClosure (frozen; net_balance_gbp=final_bill+debt-deposit; requires_debt_referral/days_since_closure/is_final_bill_overdue), AccountClosureBook (initiate/receive_final_read/issue_final_bill/return_deposit/apply_deposit_to_debt/refer_to_debt_collection/close/active_closures/overdue_final_bills/deposits_to_return/debt_referrals/requiring_debt_referral/closure_summary). Real calibration: Ofgem SLC 21B 42-day final bill deadline; deposit return within 14 days (SLC 12); ~8-12% closures have net debt balance; 2022 final bill delays were #1 switch complaint category. Connects to cos_process (Ph298), supply_point_register (Ph299), billing/invoice, debt_collection (Ph311).
**Phase 311 (2026-06-27):** Debt Collection Process Book -- 26 new tests (4,094 total). company/finance/debt_collection.py: DebtStage (INITIAL_REMINDER/WARNING_LETTER/PRE_LEGAL/DEBT_AGENCY/LEGAL_ACTION/WRITE_OFF), DebtRecord (frozen; account_id/amount_gbp/stage/stage_date/initial_date/is_vulnerable_customer; days_in_stage/is_statute_barred >6yr England-Wales/recovery_probability 0.95->0.0 by stage/expected_recovery_gbp), DebtCollectionBook (record_debt/escalate [preserves initial_date+amount]/write_off/active_debts/debts_by_stage/total_outstanding_gbp/expected_recovery_gbp/vulnerable_accounts/statute_barred_check/debt_summary). Real calibration: UK avg arrears 2022 GBP380/customer (Ofgem Retail State of Market); write-off rate 1.5-2.5% revenue in 2022-23 crisis; agency recovery 60-75p/GBP energy debts; avg 90-120 days to legal from first reminder; Ofgem: vulnerable customers must not go to agency without welfare check first. Connects to bad_debt_provision (Ph?? -- aging buckets), billing/debt_referral (SLC 27A referrals), warm_home_discount (Ph281 -- vulnerable flag), consumer_duty (Ph283), stress_test (Ph303 -- credit default scenario).
**Phase 310 (2026-06-27):** Smart Export Guarantee (SEG) Book -- 20 new tests (4,068 total). company/regulatory/seg_book.py: SEGTechnology (SOLAR_PV/WIND/MICRO_CHP/HYDRO), SEGContract (frozen; is_active=contract_end is None), SEGPayment (frozen; payment_gbp=export_kwh*rate/100), SEGBook (seg_rate_for_year 2020-2025 competitive rates; register_contract/terminate_contract via dataclass replace/record_payment/active_contracts/payments_for_customer/payments_for_year/total_paid_gbp/total_export_kwh/seg_summary). Illustrative competitive rates 2020-2025: 4.0->7.5->4.5 p/kWh; 2022 crisis peak when wholesale >50p/kWh made micro-generation valuable. SEG mandatory for suppliers >150k domestic customers from Jan 2020; NOT recoverable via levelisation (unlike FIT, Ph286) -- direct P&L cost. Connects to fit_book (Ph286 -- predecessor ended 2019-03-31), property_improvement, eep_book (SEG scheme type), decarbonisation_score (Ph279).
**Phase 309 (2026-06-27):** Gas Procurement Policy Book -- 23 new tests (4,048 total). company/risk/gas_procurement_policy.py: GasProcurementStatus (COMPLIANT/SHORT_COVER/OVER_HEDGED/STOP_LOSS_ALERT), GasCoverTarget (frozen; year/min_cover_pct/max_cover_pct), GasProcurementCheck (frozen; supply_obligation_mwh/forward_cover_mwh/nbp_sbp_gbp_per_mwh; cover_pct/is_crisis_alert(SBP>100)/status(target)/shortfall_mwh(target)), GasProcurementPolicyBook (cover_target_for_year 2016-2025 w/ real-year min covers; check_cover/checks_for_year/non_compliant_checks/crisis_alerts/mean_cover_pct/policy_summary). Real calibration: post-2022 Ofgem guidance mandates 80% minimum forward cover; suppliers with <40% cover when NBP spiked 10x in 2021-22 faced ruinous spot purchases (Igloo, People's Energy, etc). 2022 target raised to 85%. STOP_LOSS_ALERT overrides cover status when SBP>100 GBP/MWh. Closes the gas hedging governance gap: electricity side has hedge_policy.py (Ph22b) and hedge_decision.py (Ph43b); gas now has equivalent procurement policy. Connects to gas_otc_book (Ph253), gas_nominations, gas_imbalance_ledger (Ph306), stress_test (Ph303).
**Phase 308 (2026-06-27):** Coverage Sprint — Billing, CRM, Finance, Pricing -- 55 new tests (4,025 total). Closes zero-coverage gap on 5 untested company modules: billing/consumption.py (11 tests: consumption_history missing DB/filter/keys/year-month/sort/unknown; monthly_totals aggregate/separate/sorted/empty), billing/hh_consumption.py (14 tests: get_hh_consumption missing/filter/sort/unknown; recent_hh_periods last-n/default-48/fewer-than-n; is_feed_available true/false), crm/customer_profitability.py (10 tests: estimate_prior_term_net_margin no-records/insufficient/sum/filter-cid/electricity-only/before-term/negative; compute_profitability_uplift no-history/negative/positive), finance/budget.py (13 tests: get_annual_budget known/copy/unknown/keys; traffic_light green/amber/red/boundary; variance_report empty/keys/positive/custom; monthly_variance empty/keys/evenly-split), pricing/ofgem_price_cap.py (8 tests: pre-2019 none/elec-2022/gas-2022/elec>gas-all-years/2022>2020/unknown-fuel/fallback/2019-not-none). All modules had 0 tests before this phase.
**Phase 307 (2026-06-27):** Trading Book & Hedge Decision Coverage -- 36 new tests (3,970 total). tests/company/trading/test_forward_book.py: ForwardContract (frozen, bid_ask default), TradingBook (open_hedge/settle_period profit+loss/settle returns 0 on miss/pnl+mwh accumulate/open+closed contracts/amend_hedge old+new fraction/close_position realised P&L/mark_to_market in/out-of-money/portfolio_mtm aggregation+missing price skip/summary keys/multi-customer independence). tests/company/trading/test_hedge_decision.py: estimate_price_volatility (<5 records floor/bounds/noise ordering/constant price floor/zero-price filter/missing-date filter), compute_bid_ask_cost (base pct/long tenor cap/price-proportional), decide_hedge_fraction (>= floor/>= 1.0/zero eac/zero fwd/zero term/no records/high vol pushes near 1.0/returns float). Closes zero-coverage gap on company/trading/forward_book.py (252 lines) and company/trading/hedge_decision.py (139 lines) -- the core electricity hedging decision engine used in every simulation run.
**Phase 306 (2026-06-27):** Gas Shipper Imbalance Ledger -- 28 new tests (3,934 total). company/market/gas_imbalance_ledger.py: GasImbalanceDirection (LONG/SHORT/FLAT), GasImbalanceRecord (frozen; mprn/trade_date/nominated_mwh/metered_mwh/sbp_gbp_per_mwh/ssp_gbp_per_mwh; imbalance_mwh=metered-nominated; direction with 1% linepack tolerance; imbalance_charge_gbp: SHORT=-imbalance*SBP cost, LONG=+surplus*SSP revenue; is_crisis_price SBP>100 GBP/MWh; cashout_spread), GasImbalanceLedger (nbp_annual_rate/nbp_sbp_for_month/nbp_ssp_for_month with seasonal factors; record/records_for_date/records_for_mprn/net_imbalance_cost_gbp/crisis_periods/short_periods/mean_cashout_spread/gas_imbalance_summary). Real NBP data 2016-2025: 12->180->30 GBP/MWh; 2022 crisis SBP exceeded 100 GBP/MWh threshold consistently; SBP=NBP+5%, SSP=NBP-5%; winter premium/summer discount via seasonal factors. 2021-22 NBP spike (10x) caused ruinous cashout costs for shippers caught short -- killed Igloo, People's Energy, etc. Connects to gas_nominations (nominations vs metered), gas_network_ledger (Ph305), imbalance_ledger (Ph297 -- electricity parallel), cost_to_serve (Ph294).
**Phase 305 (2026-06-27):** Gas Network Charge Ledger -- 20 new tests (3,906 total). company/market/gas_network_ledger.py: GasTransporterZone (8 UK zones: CADENT_NW/NG/WM, NORTHERN, SOUTHERN, WALES_WEST, SGN_SCOTLAND/SOUTH), GasNetworkCharge (frozen; mprn/settlement_date/consumption_mwh/aq_kwh/zone/nts_rate_gbp_per_mwh/ldz_rate_gbp_per_mwh/ggl_rate_gbp_per_meter_year/days_in_period; nts_charge_gbp/ldz_charge_gbp/ggl_charge_gbp/total_charge_gbp/unit_cost_p_per_kwh), GasNetworkLedger (nts_rate_for_year/ldz_rate_for_year/ggl_rate_for_year; record_charge/charges_for_mprn/charges_for_year/total_nts_gbp/total_ldz_gbp/total_ggl_gbp/annual_cost_breakdown/cost_trend/gas_network_summary). Real rate data: NTS+LDZ 2016-2025 (1.40->1.43 p/kWh, peak 1.95 in 2022 crisis); GGL introduced Nov 2021 (GBP2.10/meter/yr), fell to GBP0.45 by 2023 as biomethane uptake disappointed. RIIO-GD2 stable post-crisis normalisation. Connects to gas_nominations, mprn_register, bsuos_ledger (Ph293), cost_to_serve (Ph294), ccl_ledger (Ph304).
**Phase 304 (2026-06-27):** CCL Ledger -- 16 new tests (3,886 total). company/regulatory/ccl_ledger.py: CCLFuel (ELECTRICITY/GAS), CCLExemptReason (RESIDENTIAL/LEC_COVERED), CCLCharge (frozen; charge_gbp=0 if exempt), CCLQuarterlyReturn (frozen; total_due_gbp/is_nil_return), CCLLedger (rate_for_year/record_charge/charges_for_account/charges_for_year/total_due_gbp/quarterly_return/ccl_summary). Real HMRC rates 2016-2025: elec 0.554->0.775 p/kWh; gas 0.195->0.465 p/kWh. 2019 spike: elec +45% (0.583->0.847), gas +67% (0.203->0.339) -- Budget 2018 NIC->CCL tax-shift policy. Residential fully exempt; LEC holders (renewable electricity with Levy Exemption Certificate) exempt. Closes CCL gap across all business customer segments (SME/I&C). Connects to cost_to_serve (Ph294).
**Phase 303 (2026-06-27):** Stress Test Framework -- 20 new tests (3,870 total). company/risk/stress_test.py: StressScenario (5: MARKET_SPIKE/CREDIT_DEFAULT/DEMAND_SHOCK/LIQUIDITY_CRISIS/COMBINED_CRISIS), StressAssumption (frozen; default_for() loads 2022-calibrated params; COMBINED_CRISIS: elec 5x/gas 4x/margin GBP500k/counterparty GBP1M), StressResult (frozen; drawdown_pct/is_severe <GBP250k/severity_rag GREEN-AMBER-RED/weeks_to_cash_concern Optional[int]), StressTestBook (run_stress/results_for_scenario/worst_case/probability_weighted_loss_gbp/scenarios_survived/scenarios_failed/all_red/stress_summary). Ofgem Financial Resilience Assessment Framework (introduced post-2022): quarterly stress tests mandatory; 28 supplier failures 2021-22 partly from failure to stress-test credit facility adequacy against margin call cascades. Connects to var_monitor (Ph282), margin_call_book (Ph289), credit_limit_book (Ph290), bsuos_ledger (Ph293), imbalance_ledger (Ph297). Closes largest gap in company/risk/ (previously 3 modules/305 lines).
**Phase 302 (2026-06-27):** GSoP Payments Tracker -- 16 new tests (3,887 total). company/regulatory/gsop_tracker.py: GSoPStandard (10: BILLING_DELAY/COMPLAINT_NO_RESPONSE/COMPLAINT_UNRESOLVED/RECONNECTION_DELAY/APPOINTMENT_MISSED/FINAL_BILL_DELAY/METER_READ_DISPUTE/DIRECT_DEBIT_ERROR/SWITCHING_DELAY/DEBT_QUERY_DELAY), GSoPBreachStatus (4: OPEN/COMPENSATED/WAIVED/DISPUTED), frozen GSoPBreach (breach_id/account_id/standard/breach_date/resolution_date/compensation_gbp=30.0/status/notes; is_open/is_compensated/working_days_open Mon-Fri count), GSoPTracker (record_breach/compensate_breach/waive_breach/open_breaches/breaches_for_standard/total_compensation_paid_gbp/total_compensation_outstanding_gbp/breach_rate_per_100_customers/breaches_by_standard/is_systemic >5 breaches/gsop_summary). UK Electricity/Gas Standards of Performance Regulations 2015: GBP30 auto-compensation; >3 breaches/100 customers triggers Ofgem supervisory action; GBP21.3M paid sector-wide 2022-23. Connects to ET register (Ph301), consumer_duty (Ph283), regulatory_dashboard (Ph300).
**Phase 301 (2026-06-26):** Erroneous Transfer Register -- 19 new tests (3,871 total). company/market/erroneous_transfer.py: ETStatus (OPEN/INVESTIGATING/RESOLVED_CORRECTED/RESOLVED_ACCEPTED/COMPENSATION_DUE/CLOSED), ETResolutionType (RETURNED_TO_ORIGINAL/CUSTOMER_ACCEPTED_GAIN/WITHDRAWN), frozen ETClaim (working_days_open [Mon-Fri loop]/is_overdue [>20 days]/compensation_gbp [GBP30 if overdue+unresolved]), ErroneousTransferRegister (raise_claim/update_status/resolve_claim/open_claims/overdue_claims/et_rate_pct/compensation_outstanding_gbp/claims_by_status/et_summary). Under Ofgem SLC P14 / REC, ETs must be resolved within 20 working days; GBP30 auto-compensation if overdue. ET rate >0.1% triggers Ofgem compliance review. Connects to cos_process (Ph298) and supply_point_register (Ph299).
**Phase 300 (2026-06-26):** MILESTONE — Regulatory Compliance Dashboard -- 12 new tests (3,852 total). company/regulatory/regulatory_dashboard.py: FilingStatus (4), ComplianceArea (8: SFR/REMIT/PRICE_CAP/ENVIRONMENTAL/SOCIAL/CONSUMER_DUTY/TRADE_REPORTING/FUEL_MIX), frozen ComplianceObligation (is_breach, needs_attention), RegulatoryDashboard (overall_rag, filed_on_time_rate, area_rag by all 8 areas, dashboard_summary). Aggregates SFR/REMIT/Price Cap/RO/FIT/FMD/ECO/WHD/EBSS/Consumer Duty into single board-level status.

**Phase 299 (2026-06-26):** Supply Point Register -- 11 new tests (3,840 total). company/crm/supply_point_register.py: ProfileClass (PC1-PC8 settlement classes), frozen SupplyPointRecord (is_hh PC5-8, is_domestic PC1-2, is_active), SupplyPointRegister (deregister via replace, active_points, hh_points, profile_class_breakdown, total_aq_kwh). MPAN/MPRN registry -- the legal foundation of supplier-customer supply point registration.

**Phase 298 (2026-06-26):** Change of Supplier Process -- 9 new tests (3,829 total). company/crm/cos_process.py: CoSStage (7), ObjectionReason (4), frozen CoSEvent, CoSProcess (stateful pipeline; object_to_switch for debt/contract objections, receive_final_read), CoSRegister (summary with in_progress/completed/objected). Closes the supply transfer loop: retention offer -> declined -> CoS process -> final read -> switch complete.

**Phase 297 (2026-06-26):** Imbalance Charge Ledger -- 12 new tests (3,820 total). company/market/imbalance_ledger.py: ImbalanceDirection (LONG/SHORT/FLAT), frozen ImbalanceRecord (imbalance_charge_gbp: long=SSP positive receivable, short=SBP negative cost; is_crisis_price >£500/MWh; cashout_spread), ImbalanceLedger (net cost, crisis period tracking). Closes the settlement loop from forwards -> DA -> intraday -> BM imbalance.

**Phase 296 (2026-06-26):** REMIT Reporting Book -- 10 new tests (3,808 total). company/regulatory/remit_book.py: REMITProductType (6 product types), frozen REMITReport (notional_value_gbp, is_large_trade>=100MWh), REMITReportingBook (submit/acknowledge lifecycle, compliance_rate, pending_reports). T+1 trade reporting obligation to FCA/ACER.

**Phase 295 (2026-06-26):** Ofgem Price Cap Book -- 10 new tests (3,798 total). company/regulatory/price_cap.py: 26 quarters real data Q1-2019 to Q1-2025; CapStatus (4), frozen CapComplianceCheck (headroom/is_compliant), PriceCapBook (elec/gas cap rates, typical annual bill, breach tracking). Peak Q3-2022: £3,549 vs £1,137 baseline = 3.12x. Connects to TariffSmoothing (Ph277) and CostToServe (Ph294).

**Phase 294 (2026-06-26):** Cost-to-Serve Calculator -- 10 new tests (3,788 total). company/pricing/cost_to_serve.py: CustomerSegment (4), frozen CostToServeBreakdown (all 7 levy components + ops; levy_pct_of_total), CostToServeCalculator (acquisition_cost_gbp, mean_total_cost, high_cost_accounts). Connects all 7 non-commodity cost ledgers into a unified per-unit economics view. Activity-based pricing foundation (CLAUDE.md principle).

**Phase 293 (2026-06-26):** BSUoS Charge Ledger -- 11 new tests (3,778 total). company/market/bsuos_ledger.py: frozen BSUoSCharge (is_crisis_period 2021-22), BSUoSLedger (rate_for_year, crisis_uplift_multiple=3.26x, annual_rate_trend, bsuos_summary; peak_rate_year=2022 at £6.85/MWh). COMPLETES 7-of-7 major non-commodity electricity cost ledgers alongside CM/CfD/RO/FIT/DUoS/TNUoS.

**Phase 292 (2026-06-26):** TNUoS Charge Ledger -- 10 new tests (3,767 total). company/market/tnuos_ledger.py: TriadStatus (TRIAD/NEAR_MISS/NORMAL), frozen TNUoSCharge (residual + triad charges), frozen TriadHalfHour, TNUoSLedger (zone_factor, confirmed_triads). North zones pay 40% more (locational signal to shift load south). Triad demand drives capacity charges. Completes 5 of 7 non-commodity cost ledgers.

**Phase 291 (2026-06-26):** DUoS Charge Ledger -- 11 new tests (3,757 total). company/market/duos_ledger.py: DNOArea (14 UK areas), VoltageLevel (HV/LV), frozen DUoSCharge (unit_charge_gbp/total_charge_gbp), DUoSLedger (unit_rate_for_year; charges by account/year; annual_unit_cost_p_per_kwh; hv_customer_count). HV customers pay 60% of LV rate. Real 2016-2025 DUoS rates (1.85-2.75 p/kWh). One of 7 major non-commodity electricity costs alongside CM/CfD/RO/FIT/BSUoS/TNUoS.

**Phase 290 (2026-06-26):** Counterparty Credit Limit Book -- 12 new tests (3,746 total). company/finance/credit_limit_book.py: CounterpartyType (5 types), frozen CreditLimit (is_material>=£1M), frozen ExposureRecord (total_exposure = MTM + PFE; is_stress_exposure when PFE>2xMTM), CreditLimitBook (utilisation_pct, is_breach, breaches, limit_summary with portfolio_utilisation_pct). Connects to MarginCallBook — breach triggers escalation to credit committee.

**Phase 289 (2026-06-26):** Margin Call Book -- 11 new tests (3,734 total). company/finance/margin_call_book.py: MarginCallStatus (RECEIVED/SETTLED/DISPUTED/DEFAULTED), frozen MarginCallEvent (is_stress_event >£500k variation margin), MarginCallBook (credit_facility_gbp, settle_call, total_outstanding, headroom_gbp, is_liquidity_stressed at 80% utilisation, stress_events). Models the 2022 crisis mechanism that triggered administration in 29 UK suppliers when margin calls exceeded credit facility headroom.

**Phase 288 (2026-06-26):** ECO Obligation Tracker -- 10 new tests (3,723 total). company/regulatory/eco_obligation.py: ECOPhase (ECO2/ECO3/ECO4), MeasureCategory (4), frozen ECODelivery (cost_per_tonne_co2), ECOObligationBook (estimated_annual_obligation_gbp, fuel_poor_delivery_pct, eco_summary). Obligation costs: ECO2 £3.20/MWh, ECO3 £4.50/MWh, ECO4 £6.80/MWh. Connects to PropertyImprovementBook. Models supplier home efficiency delivery obligation.

**Phase 287 (2026-06-26):** Fuel Mix Disclosure (FMD) -- 12 new tests (3,713 total). company/regulatory/fuel_mix_disclosure.py: FuelMixDisclosure (6 fuel source %, rego_covered_mwh, total_retail_mwh; total_pct, rego_coverage_pct, is_100pct_renewable, vs_uk_average()), FuelMixDisclosureBook (file_disclosure, renewable_trend, fmd_summary). Real UK avg fuel mix 2016-2023: coal 9.1%->0.5%, renewables 24.7%->45.3%. Suppliers claiming 100% renewable must have matching REGO coverage.

**Phase 286 (2026-06-26):** Feed-in Tariff (FIT) Book -- 11 new tests (3,701 total). company/regulatory/fit_book.py: FITTechnology (5 types), frozen FITInstallation (is_active), frozen FITPayment (generation/export payments), FITBook (register/record/levelisation_charge_gbp/fit_summary). Real 2012-2019 generation rates (16.0p/kWh 2012 to 3.68p 2019). FIT scheme closed March 2019. Levelisation levy 2016-2019: £8.36-£9.45/MWh passed through to all suppliers.

**Phase 285 (2026-06-26):** Renewable Obligation (RO) Tracker -- 10 new tests (3,690 total). company/regulatory/renewable_obligation.py: ROSettlementMethod (SURRENDER_ROC/BUYOUT/MIXED), frozen ROAnnualReturn (obligation_rocs/shortfall_rocs/buyout_cost_gbp/is_compliant), RenewableObligationBook (compliance_record/non_compliant_years/ro_summary). Real ROC obligation levels and buyout prices 2016-2025. Distinct from REGO (disclosure) -- RO is the financial obligation where suppliers surrender ROCs or pay Ofgem buyout price.

**Phase 284 (2026-06-26):** Smart Meter Rollout Book -- 12 new tests (3,667 total). company/market/smart_meter_rollout.py: MeterGeneration (SMETS1/SMETS2/TRADITIONAL), RolloutStatus (ON_TRACK/BEHIND/SIGNIFICANTLY_BEHIND), frozen MeterPortfolioSnapshot (smart_penetration_pct/remote_reads_pct/annual_manual_read_cost_gbp), SmartMeterRolloutBook (rollout_status/annual_progress/rollout_summary). Ofgem SMIP annual targets (10% 2016 to 85% 2025). SMETS1: 75% remote read rate; SMETS2: 95%. Manual read cost: £15/visit.

**Phase 283 (2026-06-26):** Consumer Duty Compliance Register -- 12 new tests (3,655 total). company/compliance/consumer_duty.py: DutyOutcome (4 Ofgem-mandated outcomes), OutcomeRAG (GREEN/AMBER/RED), frozen OutcomeAssessment (is_compliant), ConsumerDutyRegister (latest_for_outcome/overall_rag/outcomes_summary). Also fixed: warm_home_discount.py now exports whd_summary() and whd_eligible_customers() module-level functions required by portal/app.py -- resolved 23 test collection errors unblocking 226 previously-hidden tests.

**Phase 282 (2026-06-26):** VaR Monitor Book -- 13 new tests (3,630 total). company/risk/var_monitor.py: VaRBreachLevel (WITHIN_LIMIT/AMBER/RED), frozen VaRObservation (current_var_gbp/stressed_var_gbp/treasury_gbp; var_as_pct_treasury/stress_uplift_pct), VaRMonitorBook (configurable amber/red limits; record_observation/breach_count/peak_var/mean_var_gbp/var_trend/var_summary). Tracks company-observable VaR from risk committee wake-up outputs. Fills key gap in company/risk/ (previously just 2 test files).

**Phase 281 (2026-06-26):** Warm Home Discount (WHD) Tracker -- 11 new tests (3,617 total). company/regulatory/warm_home_discount.py: WHDEligibilityBasis (CORE_GROUP/BROADER_GROUP), frozen WHDRecord, WHDBook (record_discount/has_received_whd/levy_recoverable_gbp/mark_levy_recovered/whd_summary). Rates: £140 (2015-21), £150 (2022+). Annual scheme; levy recovered from Ofgem post-payment. Core Group via DWP (pension credit), Broader Group via self-application. Connects to VulnerabilityIndex for eligibility assessment.

**Phase 280 (2026-06-26):** EBSS Tracker -- 11 new tests (3,606 total). company/regulatory/energy_bill_support.py: EBSSCreditType (STANDARD/ALT_FUEL), frozen EBSSCredit, EBSSBook (record_credit/credits_for_account/govt_receivable_gbp/mark_claimed/ebss_summary). Scheme months Oct 2022-Mar 2023; £66.67/month x 6 = £400/household; alt fuel £100 one-off. mark_claimed() reduces govt receivable balance. Real 2022-23 UK government intervention captured as balance sheet item.

**Phase 279 (2026-06-26):** Decarbonisation Score -- 13 new tests (3,595 total). company/sustainability/ (new directory): DScoreBand (A/B/C/D at 80/60/40/<40), frozen DScoreBreakdown with 4 dimension scores, DecarbScorer computes REGO coverage (25pts)/EPC improvement (25pts)/heat pump adoption (25pts, 20% = full)/carbon reduction (25pts, 20%/yr = full), DScoreBook (annual records, trend, improving flag, summary). Synthesizes HomeRegistry, PropertyImprovementBook, and RegoPortfolio observations into a single ESG scorecard.

**Phase 278 (2026-06-26):** Monthly Ops Dashboard Tab -- 11 new tests (3,582 total). extract_monthly_ops() in generate_dashboard_data.py aggregates bill_shock_events, committee_wake_ups, and retention_log by calendar month into 103-row timeline (2016-2025). Monthly tab on poesys.net: 4 KPI cards, Chart.js bar+line chart (shocks red/blue by crisis, committee overlay), full operational timeline table with CRISIS annotation. Closes Dashboard Phase E.

**Phase 277 (2026-06-26):** Tariff Smoothing Book -- 11 new tests (3,571 total). company/pricing/tariff_smoothing.py: SmoothedRateStatus (BELOW_COST/AT_COST/MARGINAL/PROFITABLE), frozen TariffDecision (unit_rate vs wholesale_cost vs smoothing_reserve; gross_margin/is_loss_making/status computed), TariffSmoothingBook (record_decision/decisions_for_commodity/loss_making_years/max_bill_shock_pct/smoothing_summary). Models the pricing decision that spreads wholesale spikes. Crisis 2022 scenario: 30p/kWh rate vs 35p/kWh cost = loss-making. Closes tariff smoothing backlog item.

**Phase 276 (2026-06-26):** BM Settlement tab on /sim/ -- 10 new tests (3,560 total). tools/generate_sim_data.py: _bm_monthly_aggregation() extracts monthly BM settlement stats (mean_ssp, mean_niv_mwh, short_pct, is_crisis) from existing Elexon SSP cache -- SBP and NIV data already present in 168k records. site/sim/index.html: BM Settlement 3rd tab with monthly Short% bar chart (crisis red), dual-axis SSP+Short% combo chart, annual table with NET LONG/NET SHORT classification, 4 KPI cards. Closes /sim/ balancing mechanism backlog item.

**Phase 275 (2026-06-26):** Green Claims Audit test coverage -- 12 new tests (3,550 total). Closed zero-coverage gap in company/compliance/green_claims_audit.py (GreenClaimsAuditor audits REGO coverage vs green product consumption). tests/company/compliance/ directory created. Tests cover COMPLIANT/AT_RISK/NON_COMPLIANT paths, wrong-year REGO exclusion, coverage_pct cap at 100, penalty_estimate_gbp when shortfall, non-green product codes ignored, empty consumption edge case.

**Phase 274 (2026-06-26):** Life Event Impact Assessor -- 12 new tests (3,538 total). company/crm/life_event_impact.py: ImpactSeverity (LOW/MODERATE/HIGH/CRITICAL), LifeEventImpact (frozen dataclass), LifeEventImpactAssessor (assess/batch_assess/urgent_impacts/psr_candidates/summary). Maps all 11 LifeEventTypes to severity + consumption_delta_pct + PSR trigger + vulnerability flag + recommended_actions. Connects life_events + priority_services + vulnerability_index into unified impact assessment layer.

**Phase 273 (2026-06-26):** Management Accounts Dashboard Tab -- 10 new tests (3,526 total). tools/generate_dashboard_data.py: extract_management_accounts() extracts 10-year P&L waterfall (revenue/wholesale/non_commodity/gross_margin/capital/bad_debt/cost_to_serve/fixed/acquisition/net_margin + net_margin_pct) from management_accounts key in run output. Wired into generate() as management_accounts key in dashboard.json. site/index.html: Accounts tab with stacked cost-vs-revenue Chart.js bar+line chart and annual P&L waterfall table; 2021/2022 crisis years highlighted amber; net margin % column added.

**Phase 272 (2026-06-26): Physical Home Registry -- 12 new tests (3,516 total). company/crm/home_registry.py: HomeRegistry class managing customer->property mappings. register/upgrade_epc/get_profile; portfolio slices: profiles_by_epc, profiles_by_type, eco4_eligible_accounts, fuel_poor_accounts, psr_priority_accounts; aggregates: epc_distribution, fuel_distribution, tenure_distribution, total_estimated_elec/gas_kwh, registry_summary. Wraps existing frozen Property dataclass from property_model.py (no new enums needed).**

**Phase 271 (2026-06-26):** Weather Engine & HDD tab on /sim/ -- 10 new tests (3,504 total). tools/fetch_weather_data.py: fetches London daily temps from Open-Meteo 2016-2025, computes monthly HDD (base 15.5C National Grid). site/sim/index.html: Prices/Weather tabs; Weather tab has 10-yr monthly temp chart, monthly HDD bar chart with avg overlay, annual table with COLD WINTER badge, crisis narrative. process_run_complete.py: weather fetch wired in on every run. Critical NTFY spam fix: generate_insights stored ledger headline gross (~6.3M) in run_history; maybe_ntfy compared total_net (~1.3M) against that; every run triggered NEW LOW. Fixed to use total_net_gbp throughout.

**Phase 270 (2026-06-26):** Local NL query via Qwen3/Ollama — 7 new tests (3,494 total). `background/file_api.py`: `POST /query` endpoint calls Ollama qwen3:14b with `/no_think` prefix for fast responses (no API cost, stays local on Tailscale). `site/index.html`: fetch URL changed from Cloudflare Pages Function to `https://skynet-1.taila062fa.ts.net:8765/query` directly. `background/start_worker.sh`: file-api added as managed tmux session. Also fixed JS syntax errors in supplier dashboard (Ph266 onkeydown) and customer portal login (Ph263 double-quote nesting). Also fixed process_run_complete.py race condition + relative path bug.

---
**12 new tests (3,373 total).**

---


---
### Phase 254 -- Ofgem Market Compliance Scorecard (2026-06-26)
**Files:** `company/regulatory/compliance_scorecard.py` (new), `tests/company/regulatory/test_compliance_scorecard.py` (new)

**What was built:**
- RAGStatus: GREEN / AMBER / RED.
- ComplianceDomain: 10 domains (GOVERNANCE / BILLING_METERING / PAYMENT_DEBT / INFORMATION_TRANSPARENCY / COMPLAINTS / VULNERABLE_CUSTOMERS / TARIFF_PRICE_CAP / ENVIRONMENTAL / NETWORK_BALANCING / FINANCIAL_RESILIENCE).
- ComplianceCheck frozen: domain, check_date, status, metric_value, threshold (both optional), notes; slc_reference (maps domain to SLC clusters), is_breach.
- ComplianceScorecard mutable: record_check(), latest_status(domain), overall_rag(as_of_date), breaches(as_of_date), scorecard_summary(). Temporal logic: excludes future checks from as_of_date assessments.

**Fidelity delta:** A real UK energy supplier's Compliance Director presents exactly this RAG dashboard to the Risk Committee monthly. Ofgem expects every licenced supplier to maintain a live compliance monitoring function (post-crisis 2022 enforcement action). The 10 domains map to SLC obligation clusters — any RED triggers an internal audit and may require notification to Ofgem under the material breach provisions of SLC 0. Integrates across all regulatory modules: SFRBook (Ph250), ComplaintRegister (Ph218), VulnerabilityIndex (Ph243), EEObligationTracker (Ph219), LicenceHealthMonitor (Ph206).

**12 new tests (3,361 total).**

---


---
### Phase 253 -- Wholesale gas OTC trading book (NBP) (2026-06-26)
**Files:** `company/market/gas_otc_book.py` (new), `tests/company/market/test_gas_otc_book.py` (new)

**What was built:**
- GasTenor: WITHIN_DAY / DAY_AHEAD / MONTH_AHEAD / SEASON_AHEAD.
- GasTradeDirection: BUY / SELL.
- Season: SUMMER (Apr-Sep) / WINTER (Oct-Mar).
- GasOTCTrade frozen: trade_date, delivery_date, tenor, direction, volume_therms, price_p_per_therm; volume_mwh (×0.02931), trade_value_gbp (buy=cost, sell=revenue), is_crisis_price (>200p/th), delivery_season.
- GasOTCBook mutable: record_trade(), trades_by_delivery_month(), net_position_therms(), average_buy_price_p_th() (VWAP), crisis_trades(), seasonal_exposure_therms(), gas_book_summary().

**Fidelity delta:** The NBP gas OTC market is where UK suppliers hedge their gas procurement obligations. A supplier with 1 billion therms of annual supply obligation must buy forward on NBP — typically summer cheap (storage injection) and winter expensive (peak demand). The 2022 crisis: within-day gas hit 600+ p/th vs the 50-70 p/th historical normal. Suppliers who had bought season-ahead winter gas in early 2022 at 200+ p/th locked in losses when they had to sell forward positions; unhedged suppliers faced catastrophic spot costs. seasonal_exposure_therms() shows the net summer/winter position, directly modelling the seasonal risk that destroyed over-leveraged suppliers. Connects to GasStorageBook (Ph246) and GasNominationBook (Ph144).

**13 new tests (3,349 total).**

---


---
### Phase 252 -- Customer behaviour segmentation model (2026-06-26)
**Files:** `company/crm/behaviour_segment.py` (new), `tests/company/crm/test_behaviour_segment.py` (new)

**What was built:**
- PaymentBehaviour: EXEMPLARY (≥95%) / RELIABLE (80-95%) / OCCASIONAL_MISS (60-80%) / CHRONIC_LATE (<60%).
- EngagementLevel: HIGHLY_ENGAGED (paper-free or >4 logins/mo) / ENGAGED / PASSIVE / DISENGAGED (0 logins 6m+).
- SwitchingRisk: HIGH (<12m since switch) / MEDIUM (12-24m) / LOW (none/3y+).
- CustomerSegment: CHAMPION / LOYAL / AT_RISK / STRUGGLING / DISENGAGED_STABLE / CHURNER + recommended_intervention map.
- BehaviourProfile frozen: derived from observable data only (on-time rate, portal logins, contact frequency, switching history, paper-free flag).
- BehaviourSegmentBook mutable: record_profile(), latest_profile(), segment_counts(), at_risk_customers(), segment_summary().

**Fidelity delta:** Real CRM platforms (Salesforce Energy & Utilities, SAP IS-U) segment domestic customers by exactly these observable behavioural signals. A CHAMPION customer (exemplary payer, paper-free, loyal) gets a loyalty reward; a CHURNER (chronic late, recently switched) gets a win-back offer (or write-off). The AT_RISK segment (reliable payer but recently shopped around) is the most commercially valuable: these customers have high creditworthiness AND are actively considering leaving. Targeting them with retention outreach is higher ROI than chasing STRUGGLING accounts. Connects to AcquisitionCohortCLV (Ph235), RetentionRisk (Ph~170), and ContactJourney (Ph244).

**14 new tests (3,336 total).**

---


---
### Phase 251 -- Property improvement event tracker (2026-06-26)
**Files:** `company/crm/property_improvement.py` (new), `tests/company/crm/test_property_improvement.py` (new)

**What was built:**
- MeasureType: 10 measures (CAVITY_WALL/SOLID_WALL/LOFT/HEAT_PUMP_ASH/HEAT_PUMP_GSH/SOLAR_PV/SMART_METER/BOILER_REPLACEMENT/DOUBLE_GLAZING/DRAUGHT_PROOFING).
- FundingScheme: ECO4 / BUS / HUG2 / SEG / PRIVATE / GBIS.
- PropertyImprovement frozen: customer_id, uprn, measure, installation_date, funding_scheme, cost_gbp, epc_before/after; grant_gbp (scheme/measure lookup), customer_cost_gbp, annual_elec/gas_saving_kwh, epc_points_gained, simple_payback_years (at UK avg price £0.28/kWh elec, £0.07/kWh gas).
- PropertyImprovementBook mutable: record_improvement(), for_customer(), annual_improvements(), total_grant_gbp(), customers_upgraded_epc(rating), improvement_summary().

**Fidelity delta:** Closes the EPC improvement feedback loop Rich asked about. A real supplier tracks every ECO4 referral → installation → EPC certificate upgrade. BUS heat pump installation (£7,500 grant) moves a customer from EPC D to B: ~8,000 kWh gas saving, ~20 EPC points, 5-year payback (if customer pays the £4,500 balance). customers_upgraded_epc() connects to VulnerabilityIndex (Ph243): a customer who upgrades from F to D is no longer fuel-poor — that's a statutory change in their support entitlement. Total grant disbursed also feeds the ECO4 obligation tracker (Ph219).

**12 new tests (3,322 total).**

---


---
### Phase 250 -- Supplier Financial Resilience (SFR) book (2026-06-26)
**Files:** `company/regulatory/sfr_book.py` (new), `tests/company/regulatory/test_sfr_book.py` (new)

**What was built:**
- SFRStatus: PASS / WATCH / BREACH / INVESTIGATION.
- SFRMetric: LIQUIDITY / CREDIT_BALANCE_COVER / HEDGE_RATIO / QUARTERLY_RETURN_FILED.
- SFRAssessment frozen: quarter_end, liquidity_days, credit_balance_cover_pct, hedge_ratio_pct, return_filed; liquidity_status/hedge_status/credit_cover_status (GREEN/AMBER/RED), overall_status, breach_metrics.
- SFRBook mutable: record_assessment(), file_return(), latest_assessment(), breach_quarters(), sfr_summary().

**Fidelity delta:** Ofgem's March 2023 SFR Decision Document imposed mandatory liquidity requirements (30-day minimum) and credit balance ringfencing after 29 suppliers failed in 2021-22. Pre-crisis suppliers legally held customer credit balances as working capital, then couldn't return them when the wholesale cost surge hit. The Minimum Liquidity Requirement directly models the lesson: a supplier at 22 days liquidity (BREACH) vs 38 days (WATCH) vs 55 days (PASS) has meaningfully different regulatory standing. breach_quarters() would reveal a supplier running below the MLR — exactly the early-warning signal Ofgem now requires before a licence review. Connects to WorkingCapitalMonitor (Ph225) and CreditFacility (Ph198).

**11 new tests (3,310 total).**

---


---
### Phase 249 -- Intraday electricity trading book (2026-06-26)
**Files:** `company/market/intraday_book.py` (new), `tests/company/market/test_intraday_book.py` (new)

**What was built:**
- TradeDirection: BUY / SELL.
- TradeReason: POSITION_BALANCING / DEMAND_FORECAST_REVISION / GENERATION_SHORTFALL / EMERGENCY_COVER / OPTIMISATION.
- IntradayTrade frozen: trade_id, settlement_date, settlement_period (1-48), direction, volume_mw, price_gbp_per_mwh, traded_at, reason; volume_mwh (×0.5 hours), trade_value_gbp (buy=cost, sell=revenue), is_crisis_price (>£500/MWh).
- IntradayBook mutable: record_trade() (validates period 1-48), trades_for_date(), net_position_mwh() (by date or period), daily_pnl_gbp(), crisis_trades(), average_buy_price(), intraday_summary().

**Fidelity delta:** After forward hedging, suppliers must balance their position in real-time on the N2EX intraday platform before gate closure (1h before each 30-min settlement period). A supplier with a 50 MW portfolio might execute 50-100 intraday trades per day. Poor intraday management creates residual imbalance that goes to Elexon cashout at punitive prices (£2,000+/MWh in the 2022 crisis). daily_pnl_gbp() measures the spread capture (sell minus buy) — positive means the trader is profiting from balancing activity, negative means they're paying a premium to cover. Connects to ImbalanceAnalytics (Ph233) for any residual position that survives to cashout.

**12 new tests (3,299 total).**

---


---
### Phase 248 -- CfD (Contracts for Difference) levy book (2026-06-26)
**Files:** `company/market/cfd_levy.py` (new), `tests/company/market/test_cfd_levy.py` (new)

**What was built:**
- LevyDirection: POSITIVE / NEGATIVE / ZERO.
- CfDLevyCharge frozen: account_id, charge_date, year, quarter, consumption_mwh, rate_gbp_per_mwh; levy_gbp (negative = credit), direction, is_credit.
- get_levy_rate(year, quarter): historical quarterly CfD levy rates 2016-2025. 2022 Q2-Q4 are negative (crisis peak Q4 2022: -£12.3/MWh).
- CfDLevyBook mutable: record_charge(), charges_for_account(), annual_levy_gbp(), quarterly_levy_gbp(), total_credit_quarters(), levy_summary().

**Fidelity delta:** The CfD levy is the mechanism that funds UK renewable generators with long-term revenue stability. Suppliers collect the levy from customers as a non-commodity cost and remit to LCCC. The crisis reversal is the most consequential feature: in 2022 Q2-Q4, wholesale electricity prices far exceeded most CfD strike prices (typical offshore wind £50-80/MWh vs market £200-500/MWh), so generators owed the surplus to LCCC, which then distributed it back to suppliers as a credit. This reduced supplier non-commodity bills by £8-12/MWh in Q3-Q4 2022 — a partial offset to the catastrophic commodity cost rise. Connects to NetworkChargeLedger (Ph216) for the non-commodity cost picture and REGOPortfolio (Ph148) for renewable sourcing.

**12 new tests (3,287 total).**

---


---
### Phase 247 -- Power Purchase Agreement (PPA) book (2026-06-26)
**Files:** `company/market/ppa_book.py` (new), `tests/company/market/test_ppa_book.py` (new)

**What was built:**
- PPATechnology: ONSHORE_WIND / OFFSHORE_WIND / SOLAR / HYDRO / BIOMASS.
- PPAPricingType: FIXED / INDEXED / FLOOR (floor = min guaranteed, tracks market above floor).
- PPAContract frozen: contract_id, generator_id, technology, start/end date, capacity_mw, annual_generation_mwh, price_gbp_per_mwh; term_years, annual_cost_gbp, is_active(date), effective_price(market_price), vs_market_gbp(market_price).
- PPABook mutable: add_contract(), active_contracts(date), total_contracted_mwh(date), total_annual_cost_gbp(date), total_vs_market_gbp(date, market_price), ppa_summary(date, market_price).

**Fidelity delta:** PPAs are how UK renewable generators secure long-term revenue (typically 10-15 year fixed-price contracts). Suppliers use them to source green electricity below wholesale while providing REGOs for green tariffs. The vs_market_gbp() method quantifies whether the PPA was a good deal in hindsight: in 2022, pre-crisis fixed-price PPAs at £45/MWh were enormously beneficial vs spot at £200+/MWh. Connects to REGOPortfolio (Ph148) for green claims and CommodityHedgeSchedule (Ph207) for overall supply position.

**11 new tests (3,275 total).**

---


---
### Phase 246 -- Gas seasonal storage book (2026-06-26)
**Files:** `company/market/gas_storage.py` (new), `tests/company/market/test_gas_storage.py` (new)

**What was built:**
- StorageFacility (5): ROUGH (3,300 mcm — mothballed May 2017) / STUBLACH (390 mcm) / HOLFORD (40 mcm) / HUMBLY_GROVE (320 mcm) / HORNSEA (140 mcm).
- StorageOperation: INJECT / WITHDRAW.
- StorageTransaction frozen: facility, date, operation, volume_mcm, price_gbp_per_therm; cost_gbp (positive=inject/outflow, negative=withdraw/inflow); therms_per_mcm = 3,412.14; is_winter_operation (Oct-Mar).
- GasStorageBook mutable: inject(), withdraw() — updates _inventory_mcm dict; inventory_mcm(facility), total_injected_mcm(year), net_storage_cost_gbp(year), spread_gbp_per_therm(facility, year), storage_summary(year).

**Fidelity delta:** The Rough field closure in May 2017 reduced UK seasonal storage capacity by ~70% (from 4.4 BCm to 1.2 BCm). This is widely cited as a reason UK consumers were most exposed to the 2021-22 gas price spike — less buffer stock meant immediate passthrough of NBP spot prices. The storage spread (withdraw price minus inject price) is the P&L of a "buy summer/sell winter" gas trading strategy: 2022 spread of ~£120/therm was the highest on record. spread_gbp_per_therm() connects to GasNominationBook (Ph144) imbalance analysis: well-managed storage reduces nomination error and cashout costs.

**9 new tests (3,264 total).**

---
### Phase 245 -- Capacity Market participation book (2026-06-26)
**Files:** `company/market/capacity_market.py` (new), `tests/company/market/test_capacity_market.py` (new)

**What was built:**
- CMUnitType: CCGT / OCGT / BATTERY / DEMAND_RESPONSE / INTERCONNECTOR / PUMP_STORAGE.
- AuctionType: T4 (4 years ahead) / T1 (1 year ahead).
- _CM_CLEARING_PRICE_GBP_PER_KW_PER_YEAR: 2016 £18 → 2020 £6.44 → 2022 £75 (crisis) → 2025 £60.
- CMUnit frozen: unit_id, unit_type, derated_capacity_kw, registered_date.
- CMObligation mutable: unit, delivery_year, auction_type, clearing_price; annual_revenue_gbp (derated_kw × price), net_revenue_gbp (after penalties), apply_penalty().
- CapacityMarketBook: register_unit(), add_obligation(unit, year, type, optional_price), obligations_for_year(), total_revenue_gbp(year), total_derated_kw(year), cm_summary(year).

**Fidelity delta:** The Capacity Market is a government mechanism paying generators (and demand-side assets) to guarantee availability during winter stress events. A 100 MW battery with 2022 CM obligation earned £7.5M/year in CM revenue alone. The 2022 spike from £6.44 to £75/kW (12x increase) reflects the energy security panic following Russian gas supply disruption. T4 auctions are held 4 years in advance for new build; T1 for shorter-term reliability. DSR assets can participate at lower build costs than generation. Connects to FlexibleAsset (Ph239) and DSRPortfolio (Ph224): BM dispatch revenue + CM revenue + Triad avoidance is the "stacked revenue" model for flexible assets.

**9 new tests (3,255 total).**

---
### Phase 244 -- Customer contact preferences and channel management (2026-06-26)
**Files:** `company/crm/contact_journey.py` (new), `tests/company/crm/test_contact_journey.py` (new)

**What was built:**
- ContactChannel (6): EMAIL / SMS / POST / PHONE / IN_APP / WEB_PORTAL.
- ContactPurpose (7): BILL / TARIFF_CHANGE / MARKETING / DEBT_CHASE / RENEWAL_OFFER / SERVICE_UPDATE / COMPLAINT_UPDATE.
- ContactOutcome: DELIVERED / OPENED / CLICKED / BOUNCED / OPTED_OUT / NO_ANSWER / COMPLETED.
- _CHANNEL_COST_PENCE: EMAIL 0.2p / SMS 4p / POST 80p / PHONE 350p / IN_APP 0p.
- CustomerContactPrefs frozen: paper_free_discount_eligible (paper_free=True and not bill_by_post).
- ContactAttempt frozen: attempt_id, channel, purpose, sent_at, outcome, cost_pence; was_successful (DELIVERED/OPENED/CLICKED/COMPLETED).
- ContactJourney: set_prefs(), get_prefs(), log_attempt(), delivery_rate_pct(channel, year), total_contact_cost_gbp(year), opted_out_customers(), contact_summary(year).

**Fidelity delta:** Paper-free billing was a major driver of cost reduction for energy suppliers (2016-2022). A customer with 12 paper bills costs £9.60/yr to send; email costs £0.24/yr. With 100,000 domestic customers, moving 80% to paper-free saves ~£750k/yr. total_contact_cost_gbp() is a real operational cost; phone contacts at 350p (£3.50 per call handling) are the most expensive touchpoint. opted_out_customers() feeds the GDPR privacy_register (Ph240): opting out of a contact channel must be reflected in future campaign targeting. Delivery_rate by channel guides the channel selection in outbound_contact_campaign (Ph203).

**9 new tests (3,246 total).**

---
### Phase 243 -- Fuel poverty vulnerability index (2026-06-26)
**Files:** `company/crm/vulnerability_index.py` (new), `tests/company/crm/test_vulnerability_index.py` (new)

**What was built:**
- VulnerabilityBand: LOW (0-14) / MEDIUM (15-34) / HIGH (35-59) / CRITICAL (60+).
- FuelPovertyIndicator (6) with scores: BENEFITS 20, DISABILITY 25, CHILD_HOUSEHOLD 10, ELDERLY_75 20, CANCER_TREATMENT 30, HOME_OXYGEN 60.
- VulnerabilityAssessment frozen: customer_id, assessment_date, indicator_score, arrears_gbp, has_prepayment_meter, annual_income_band, fuel_spend_pct_income; arrears_score (0/5/10/20 by threshold), fuel_poverty_score (0/10/20), ppm_score (0/10); total_score, band, is_priority_services (HIGH+CRITICAL), disconnection_protected (CRITICAL only).
- assess_vulnerability() factory taking a list of FuelPovertyIndicator.

**Fidelity delta:** Ofgem requires suppliers to maintain a Priority Services Register (PSR) for vulnerable customers and prohibits disconnection of CRITICAL customers between Oct-Mar or at any time if life-support equipment is present. HOME_OXYGEN = 60 points ensures medical equipment users always reach CRITICAL band regardless of other factors. The vulnerability index feeds PPMBook (Ph145) — a HIGH/CRITICAL customer gets emergency credit of £10 (not £5), and fuel_spend_pct_income ≥10% is the statutory definition of fuel poverty. Arrears >£500 triggers an income-based repayment plan (Ofgem non-disconnection protection).

**9 new tests (3,237 total).**

---
### Phase 242 -- Metering services contracts (MOP/DC) (2026-06-26)
**Files:** `company/market/metering_contracts.py` (new), `tests/company/market/test_metering_contracts.py` (new)

**What was built:**
- MeteringServiceType: MOP / DC / DA / MAM.
- MeterType: CREDIT / PREPAYMENT / SMART (SMETS2) / HH (half-hourly).
- ServiceCallType (6): METER_READ / METER_INSTALL / METER_EXCHANGE / METER_REMOVAL / FAULT_REPAIR / SMART_COMMISSIONING.
- _MOP_RATE (£/meter/year): CREDIT £18 / PPM £22 / SMART £28 / HH £45.
- _DC_RATE (£/meter/year): CREDIT £12 / PPM £14 / SMART £16 / HH £30.
- MeteringContract frozen: provider_id, service_type, meter_type, start_date, end_date, mpan; annual_cost_gbp, is_active(as_of), cost_for_period_gbp(from, to).
- MeteringContractManager: register_contract(), log_service_call(), active_contracts(as_of, service_type), annual_contract_cost_gbp(year), service_call_cost_gbp(year), metering_summary(year).

**Fidelity delta:** Every supply point has a MOP and a DC contract — two separate third-party agreements that are a real cost of supply independent of commodity prices. For a domestic credit meter: £18 MOP + £12 DC = £30/year = 2.5p/kWh on a 1,200 kWh/yr user. For a half-hourly I&C meter: £45 + £30 = £75/year. Smart meter commissioning (service_call: SMART_COMMISSIONING) is a one-off £100-£150 cost that the government partially subsidised through the smart meter programme. When suppliers exit (SoLR), MOP/DC contracts transfer to the incoming supplier — they don't terminate, which is a legal and operational guarantee.

**8 new tests (3,228 total).**

---
### Phase 241 -- Renewables Obligation compliance ledger (2026-06-26)
**Files:** `company/regulatory/roc_ledger.py` (new), `tests/company/regulatory/test_roc_ledger.py` (new)

**What was built:**
- ROCTechnology (7): ONSHORE_WIND / OFFSHORE_WIND / SOLAR_PV / HYDRO / ANAEROBIC_DIGESTION / BIOMASS / LANDFILL_GAS.
- _BUYOUT_PRICE_GBP_PER_ROC: 2016 £44.33 → 2025 £63.80 (indexed by Ofgem annually).
- _RO_LEVEL_ROC_PER_MWH: 2016 0.341 → 2025 0.223 (declining as renewables capacity increases).
- ROCPurchase frozen: technology, rocs, price_gbp_per_roc, purchase_date; total_cost_gbp.
- ROCompliancePeriod: year, supplied_mwh; obligation_rocs (= mwh × RO level), rocs_surrendered, shortfall_rocs, buyout_cost_gbp (= shortfall × buyout price), compliance_pct, is_compliant.
- ROCLedger: buy_rocs(), open_period(year, mwh), surrender_rocs(year, rocs), get_period(), total_roc_spend_gbp(year), roc_summary(year).

**Fidelity delta:** The Renewables Obligation is the pre-CfD mechanism for larger renewables (pre-2017 commissioned). Suppliers must surrender ROCs for their share of electricity supply or pay the buyout price. The buyout pool is redistributed to suppliers who did surrender ROCs (mutualisation), so "buyout" is a transfer not a loss — but complex to model. The RO level declines each year as more renewables are built, reducing the per-MWh obligation cost over time. A 2016 supplier with 100 GWh owed 34,100 ROCs; by 2025 only 22,300. The gap between roc_spend and buyout_cost reveals the ROC market premium (ROCs trade above buyout in normal years).

**9 new tests (3,220 total).**

---
### Phase 240 -- GDPR privacy consent register (2026-06-26)
**Files:** `company/regulatory/privacy_register.py` (new), `tests/company/regulatory/test_privacy_register.py` (new)

**What was built:**
- ConsentPurpose (6): BILLING / MARKETING_EMAIL / MARKETING_SMS / THIRD_PARTY_SHARING / ANALYTICS / SMART_METER_DATA.
- DSRType: ACCESS / ERASURE / PORTABILITY / RECTIFICATION / RESTRICTION.
- DSRStatus: RECEIVED / IN_PROGRESS / COMPLETED / EXTENDED / REFUSED.
- ConsentRecord frozen: customer_id, purpose, granted, consent_date, withdrawal_date; is_active (granted and not withdrawn).
- DataSubjectRequest mutable: request_id, customer_id, dsr_type, received_date; deadline() = +30 days (standard) or +60 days (extended); is_overdue(as_of); complete(date); extend().
- PrivacyConsentRegister: record_consent(), has_active_consent(customer_id, purpose), raise_dsr(), get_dsr(), overdue_requests(as_of), customers_without_consent(purpose, list), privacy_summary(as_of).

**Fidelity delta:** UK GDPR (retained after Brexit) requires DSARs completed within 30 calendar days, extensible to 3 months for complex/numerous requests (controller must notify within first 30 days). Energy suppliers must track consent separately for smart meter data (SMIP purposes) vs marketing. Marketing email without an opt-in record is an Ofcom/ICO violation carrying fines up to 4% of global turnover. customers_without_consent(MARKETING_EMAIL) feeds the contact_campaign_tracker (Ph203): campaigns must only target opted-in customers.

**10 new tests (3,211 total).**

---
### Phase 239 -- Flexible asset dispatch model (2026-06-26)
**Files:** `company/market/flexible_asset.py` (new), `tests/company/market/test_flexible_asset.py` (new)

**What was built:**
- AssetType: BATTERY_STORAGE / PUMP_STORAGE / FLYWHEEL / DEMAND_RESPONSE.
- DispatchMode: CHARGE / DISCHARGE / STANDBY.
- AssetDispatchInterval frozen: settlement_date, period, mode, power_mw, price_achieved; energy_mwh = power × 0.5, revenue_gbp (negative on charge, positive on discharge, 0 on standby), is_evening_peak (SP 33-40).
- FlexibleAsset mutable: asset_id, type, capacity_mw, storage_mwh, roundtrip_efficiency_pct (default 85%), current_soc_mwh; soc_pct, can_charge, can_discharge; dispatch(date, period, mode, power, price) updates SoC with efficiency loss on charge; total_revenue_gbp(year), cycles_in_year(year), asset_summary(year).

**Fidelity delta:** Battery storage is the fastest-growing flexible asset in GB. A 10MW/20MWh battery with 85% roundtrip efficiency and 300 cycles/year earns arbitrage revenue by charging at ~£50/MWh (overnight/midday solar) and discharging at ~£200/MWh (evening peak) or BM prices. SoC tracking is the key state variable — the battery can't be dispatched if empty, can't charge if full. cycles_in_year() drives battery degradation modelling. Connects to DSR portfolio (Ph224) and BM unit log (Ph237): triad avoidance is the most valuable use case — discharging during the 3 settlement periods that set the Triad saves ~£7.50/kW/yr in TNUoS.

**9 new tests (3,201 total).**

---
### Phase 238 -- MPAS supply point registry (2026-06-26)
**Files:** `company/market/mpas_registry.py` (new), `tests/company/market/test_mpas_registry.py` (new)

**What was built:**
- RegistrationStatus: REGISTERED / IN_TRANSFER / OBJECTED / WITHDRAWN / LOST.
- Commodity: ELECTRICITY / GAS.
- SupplyPoint mutable: supply_point_id, commodity, customer_id, registration_date, annual_consumption_kwh, status, transfer_effective_date, objection_raised, objection_reason, losing_supplier; is_active, annual_mwh, raise_objection(reason), resolve_objection(allow_transfer), complete_transfer(date).
- MPASRegistry: register(), get(), active_supply_points(commodity), total_registered_mwh(commodity), objected_points(), registrations_in_period(from, to), mpas_summary().

**Fidelity delta:** MPAS (Meter Point Administration Service) is the central registry where supply points are registered to suppliers. The objection process — introduced to prevent erroneous or "slamming" switches — allows a current supplier to object within 5 business days. Valid objection reasons include customer still in a fixed-term contract, an existing complaint not resolved, or incorrect MPAN. Objections resolved in favour of the gaining supplier → IN_TRANSFER; rejected → WITHDRAWN (customer stays). total_registered_mwh(ELECTRICITY) feeds the hedging_schedule (Ph207) and seasonal_demand_model (Ph234) as the company's actual portfolio volume for forward buying.

**9 new tests (3,192 total).**

---
### Phase 237 -- Balancing Mechanism (BM) unit log (2026-06-26)
**Files:** `company/market/bm_unit_log.py` (new), `tests/company/market/test_bm_unit_log.py` (new)

**What was built:**
- BMActionType: OFFER (increase output / decrease demand) / BID (decrease output / increase demand).
- BMDispatchStatus: SUBMITTED / ACCEPTED / DISPATCHED / PART_DISPATCHED / DECLINED.
- BMOffer frozen: bmu_id, settlement_date, settlement_period, action_type, offered_mw, price_gbp_per_mwh, submission_time; offered_mwh = mw × 0.5 (one SP), is_expensive (>£500/MWh).
- BMDispatch mutable: offer, dispatched_mw, dispatch_time; dispatched_mwh, revenue_gbp, utilisation_pct; PART_DISPATCHED if dispatched_mw < 99% of offered.
- BMUnitLog: bmu_id, capacity_mw; submit_offer(), record_dispatch(), total_revenue_gbp(year), dispatch_count(year), avg_dispatch_price(year), bm_summary(year).

**Fidelity delta:** The Balancing Mechanism is the real-time tool National Grid ESO uses to balance generation and demand second-by-second, via dispatch of accepted offers/bids. Suppliers with flexible demand (DSR customers from Ph224) can submit demand-reduction offers at attractive BM prices. During 2022 crisis, BM clearing prices routinely exceeded £500/MWh (is_expensive=True), giving flexible demand customers 10-20x their normal off-peak rate. BMUnitLog connects to ImbalanceAnalytics (Ph233): a company with well-run BM participation can reduce its imbalance cash-out costs by deliberately taking positions. avg_dispatch_price() feeds the risk reporting dashboard.

**9 new tests (3,183 total).**

---
### Phase 236 -- Smart Export Guarantee (SEG) portfolio (2026-06-26)
**Files:** `company/billing/seg_portfolio.py` (new), `tests/company/billing/test_seg_portfolio.py` (new)

**What was built:**
- SEGTariffTier: FIXED / FLEXIBLE.
- `get_seg_rate(year)`: history 2020-2025 (5.5p, 6p, 12p, 15p, 12p, 10p).
- SEGCustomer frozen: customer_id, mpan, solar_capacity_kwp, registration_date, tariff_tier, battery_capacity_kwh; has_battery, estimated_annual_export_kwh(year), annual_seg_income_gbp(year). Without battery: 50% self-consumption; with battery: 70% self-consumption.
- SEGPortfolio: register(), record_export(customer_id, period, kwh), total_export_kwh(year), total_seg_payments_gbp(year), customers_with_battery(), total_solar_capacity_kwp(), seg_summary(year).

**Fidelity delta:** SEG (Smart Export Guarantee) replaced FiT export tariff from Jan 2020 — suppliers with >150k customers are obligated to offer. A 4kWp panel generates ~900 kWh/yr net (UK average), exporting 450 kWh without battery (~£27/yr at 2020 rates, £68/yr at 2023 peak). With a 10kWh home battery, exports drop to 270 kWh (battery charges from midday peak, reduces export) but customer's own bill savings rise. Suppliers pay out but recover via wholesale energy they don't need to procure at that moment. total_seg_payments_gbp() feeds working_capital_monitor (Ph225) as a real outflow. High-solar customers during 2022-2023 crisis received 15p/kWh export — more than SVT import rates in some half-hour periods.

**10 new tests (3,174 total).**

---
### Phase 235 -- Customer acquisition cohort CLV (2026-06-26)
**Files:** `company/crm/acquisition_cohort.py` (new), `tests/company/crm/test_acquisition_cohort.py` (new)

**What was built:**
- AcquisitionChannel (6): PRICE_COMPARISON / DIRECT_ONLINE / REFERRAL / RETENTION / DOOR_TO_DOOR / TPI.
- CohortCustomer mutable: acquisition_date, acquisition_cost_gbp, annual_revenue_gbp, churn_date; is_active, lifetime_months(as_of), lifetime_revenue_gbp(as_of), net_clv_gbp(as_of).
- AcquisitionCohort: cohort_id, year, month, channel; add_customer(), churn_customer(), initial_size, active_count(), retention_rate_pct(), total_acquisition_cost_gbp(), avg_net_clv_gbp(as_of), payback_months(as_of), cohort_summary(as_of).

**Fidelity delta:** Cohort CLV analysis is the standard VC/CFO metric for energy supplier unit economics. PCW acquisitions (MoneySupermarket, uSwitch) have CaC of £60-120 but churn in 12-18 months (price-sensitive), giving payback of 8-14 months. Referral acquisitions cost £20-40 and have 40% lower churn, giving payback of 4-6 months. D2D (door-to-door) has the highest CaC (£150-200) but also highest first-year revenue due to customer stickiness. TPI cohorts are I&C only and have 3-5 year tenures. payback_months() feeds the marketing_budget (company/crm/) channel ROI decision: channels with payback > 24 months should be cut unless there are secondary benefits.

**8 new tests (3,164 total).**

---
### Phase 234 -- Seasonal demand forecast model (2026-06-26)
**Files:** `company/market/seasonal_demand.py` (new), `tests/company/market/test_seasonal_demand.py` (new)

**What was built:**
- Season: WINTER (Nov-Mar) / SUMMER (Apr-Oct).
- DemandScenario: BASE (1.0x) / HIGH (1.15x) / LOW (0.85x).
- _SEASONAL_INDEX by month (1-12): Jan 1.35 / Jul-Aug 0.80 / Dec 1.30.
- MonthlyDemandForecast frozen: year, month, commodity, base_mwh, scenario; season, seasonal_index, forecast_mwh (= base × index × scenario).
- SeasonalDemandModel: set_monthly_forecast(), get_month(), annual_demand_mwh(year, commodity), seasonal_demand_mwh(year, commodity, season), peak_month(year, commodity), winter_summer_ratio(year, commodity), demand_summary(year).

**Fidelity delta:** Seasonal demand forecasting is the foundation of the forward purchasing calendar. January peak = 35% above annual average; suppliers use this to set the "S1" (Season 1 winter) forward hedge — the largest single trade of the year. winter_summer_ratio (typically 1.6-1.8 for residential gas, 1.2-1.4 for electricity) determines the hedge curve shape. HIGH scenario (15% uplift) is used for cold-year risk; LOW scenario (15% below) for mild-year risk. The difference between seasonal_demand_mwh(base) and actual consumption in Ph144 gas_nominations is the primary imbalance driver. Connects to hedging_schedule (Ph207): forecasts feed the forward contract set.

**10 new tests (3,156 total).**

---
### Phase 233 -- Settlement imbalance analytics (2026-06-26)
**Files:** `company/market/imbalance_analytics.py` (new), `tests/company/market/test_imbalance_analytics.py` (new)

**What was built:**
- ImbalanceDirection: LONG (> +0.01 MWh) / SHORT (< -0.01 MWh) / FLAT (otherwise).
- ImbalanceRecord frozen: settlement_date, period (1-48), commodity, imbalance_mwh, cash_out_price; direction, cash_out_cost_gbp (abs(mwh) × price).
- ImbalanceAnalytics: record(), total_cash_out_gbp(year, commodity), net_imbalance_mwh(year), systematic_bias(year), worst_period(year), short_count(year), avg_cash_out_per_mwh(year), imbalance_summary(year).

**Fidelity delta:** Elexon BSC settlement runs (SF, R1, R2, RF) calculate each supplier's net imbalance per settlement period. systematic_bias(year) is the key metric: if a supplier is consistently SHORT (under-nominated), it means their consumption forecasting is biased low — possibly due to not modelling EV demand correctly. During 2022, cash-out prices hit £350-450/MWh (vs. £40-60 in 2016) making short imbalances enormously expensive. worst_period() identifies which market event caused the largest single-period cash-out — often a Triad event or extreme cold snap. avg_cash_out_per_mwh tracks whether imbalance cost is rising (methodology problem) or falling (improving nomination accuracy).

**9 new tests (3,146 total).**

---
### Phase 232 -- Counterparty credit rating book (2026-06-26)
**Files:** `company/trading/credit_rating_book.py` (new), `tests/company/trading/test_credit_rating_book.py` (new)

**What was built:**
- CreditRating enum (9): AAA / AA / A / BBB / BB / B / CCC / D / NR.
- _RATING_SCORE (0-10): AAA=10, BBB=7 (investment grade floor), D=0.
- _PROBABILITY_OF_DEFAULT_PCT: AAA 0.01% to CCC 22% to D 100%.
- is_investment_grade(): rating score ≥ 7 (BBB and above).
- CounterpartyCreditProfile frozen: score, pd_pct, is_investment_grade, exposure_limit_gbp.
- CreditExposure mutable: counterparty_id, trade_date, exposure_gbp, trade_type.
- CreditRatingBook: register(), record_exposure(), total_exposure_gbp(), is_within_limit(new_exposure), sub_investment_grade_counterparties(), credit_summary().

**Fidelity delta:** All UK wholesale energy trading is subject to credit limits under the BSC and ISDA Master Agreement framework. Shell, BP, and EDF are typically BBB-AA rated counterparties who trade large volumes. Sub-investment-grade (BB-) counterparties require bilateral credit support annexes (CSA) or LOC posting before trading. is_within_limit() is the pre-trade credit check: a trade that would breach the counterparty's limit must be rejected or collateral increased. During the 2022 crisis, many energy company ratings were downgraded (Centrica was briefly at BB+), reducing their ability to trade on standard credit terms.

**8 new tests (3,137 total).**

---
### Phase 231 -- Gas supply interruption risk model (2026-06-26)
**Files:** `company/market/gas_interruption.py` (new), `tests/company/market/test_gas_interruption.py` (new)

**What was built:**
- InterruptClass: FIRM (0% discount) / INTERRUPTIBLE (8%) / EMERGENCY_ONLY (15%).
- InterruptionReason: SUPPLY_EMERGENCY / NETWORK_CONSTRAINT / PLANNED_MAINTENANCE / NON_PAYMENT / HEALTH_SAFETY.
- GasInterruption mutable: notice_date, start/expected_end, is_vulnerable; notice_days, expected_duration_days, actual_duration_days, restore().
- InterruptibilityContract frozen: interrupt_class, max_interruptions_per_year, min_notice_hours; discount_pct.
- GasInterruptionManager: register_contract(), issue_interruption(), active_interruptions(), interruptions_for_customer(), vulnerable_customers_affected(), interruption_summary(year).

**Fidelity delta:** Gas interruptibility is a formal contractual status (IGEM UP/9). Interruptible customers accept controlled gas reduction during supply emergencies in exchange for a tariff discount (typically 8-15%). Xoserve manages the mprn register and coordinates interruptions via National Gas. During Feb 2022, UK underground gas storage was at 3% of capacity (vs EU average 30%), putting GB within days of a supply emergency. vulnerable_customers_affected() is critical: Ofgem SLC 4A strictly prohibits disconnecting vulnerable gas customers in winter (1 Oct - 31 Mar). Interruptible discounts appear as cost reduction in gas_nominations (Ph144) but the model must track when interruptions are actually invoked.

**8 new tests (3,129 total).**

---
### Phase 230 -- Integrated board KPI dashboard (2026-06-26)
**Files:** `company/finance/board_dashboard.py` (new), `tests/company/finance/test_board_dashboard.py` (new)

**What was built:**
- KPIStatus: GREEN / AMBER (≤10% miss) / RED (>10% miss) / NOT_SET.
- KPIMetric frozen: name, value, target, unit, lower_is_better; vs_target_pct, status, is_on_target.
- BoardDashboard: period, customer_count, net_margin/gross_margin/treasury/enterprise_value, churn_rate, complaints_per_100, bad_debt_ratio, cash_runway_weeks, hedge_ratio; kpis(targets) → list of 10 KPIMetric; rag_summary(targets) → {green/amber/red/overall/at_risk_metrics}.
- 10 KPIs: Customer Count / Net Margin / Gross Margin / Treasury / Enterprise Value / Churn Rate / Complaints/100 / Bad Debt Ratio / Cash Runway / Hedge Ratio.

**Fidelity delta:** UK energy supplier board packs contain exactly these 10 metrics, colour-coded RAG. The board decides whether to raise a credit facility drawdown (Ph198) if treasury goes amber. They trigger risk_appetite review (company/risk/) if hedge_ratio goes RED. complaints/100 > 3 triggers an emergency customer service review. The RAG summary's at_risk_metrics is what the CEO focuses on first: if it's empty, the session is brief; if it has 3+ entries in 2022, they discuss whether to apply for administration. Connects all company-layer modules into a single synthesised view.

**8 new tests (3,121 total).**

---
### Phase 229 -- Customer switching gain/loss report (2026-06-26)
**Files:** `company/crm/switching_report.py` (new), `tests/company/crm/test_switching_report.py` (new)

**What was built:**
- SwitchDirection: GAIN / LOSS.
- SwitchReason (8): PRICE / SERVICE / GREEN_TARIFF / SMART_METER / DEAL / COMPLAINT_DISSATISFACTION / MOVING_HOME / UNKNOWN.
- SwitchRecord frozen: switch_date, direction, from/to_supplier, annual_kwh, reason; annual_mwh, is_gain.
- SwitchingReport: record() (auto-sets from/to based on direction), gains(year), losses(year), net_customer_movement(year), net_mwh_movement(year), churn_rate_pct(year, avg_customers), loss_reasons(year), top_gaining_from(year), switching_summary(year, avg_customers).

**Fidelity delta:** Switching data is published weekly by Energy UK and monthly by Ofgem. UK market had 5% monthly switching rate at peak (2019). In 2022, switching collapsed to near zero as all suppliers were on SVT — there was no point switching since everyone had the same Ofgem price cap. top_gaining_from() is the weekly MD question: "which of our competitors are leaking customers most?" It drives acquisition targeting. loss_reasons breakdown feeds the churn_model (Ph~30s) root cause analysis. MOVING_HOME losses are inevitable (COT); PRICE losses are preventable through retention.

**9 new tests (3,113 total).**

---
### Phase 228 -- Tariff change notification log (2026-06-26)
**Files:** `company/crm/tariff_notification.py` (new), `tests/company/crm/test_tariff_notification.py` (new)

**What was built:**
- ADVANCE_NOTICE_DAYS = 42 (Ofgem SLC 25B requirement).
- NotificationChannel: EMAIL / POST / SMS / IN_APP.
- TariffChangeReason: MARKET_PRICE_CHANGE / PRICE_CAP_CHANGE / CONTRACT_RENEWAL / REGULATORY_CHANGE / PRODUCT_RESTRUCTURE.
- TariffNotification mutable: sent_date, effective_date, old/new unit_rate + standing_charge; notice_days (effective - sent), meets_advance_notice (≥42d), unit_rate_change_pct, is_price_increase.
- TariffNotificationLog: send(), get(), mark_confirmed(), compliance_breaches(), customer_notifications(), price_increases(year), notification_summary(year).

**Fidelity delta:** Ofgem SLC 25B requires 42 days advance notice for tariff changes to fixed-price contract customers. This is the same 42 days as the contract notice period in Ph215 — both stem from the same regulation. A breach (< 42 days) means the price change is unenforceable and the customer can keep the old rate. Oct 2022 was the largest notification event in UK energy history: ~10 million customers notified simultaneously that prices were rising to the EPG ceiling (£2,500) from 1 Oct 2022, following the mini-Budget cap. Notification compliance is audited by Ofgem annually. IN_APP replaces POST for smart meter customers.

**8 new tests (3,104 total).**

---
### Phase 227 -- UK ETS emission allowance registry (2026-06-26)
**Files:** `company/regulatory/ets_registry.py` (new), `tests/company/regulatory/test_ets_registry.py` (new)

**What was built:**
- _UKETS_PRICE_GBP_PER_TONNE (2021-2025): £50 → £72 (2022 peak, ~£80+ in March) → £45 (2024).
- _FREE_ALLOCATION_TONNE_PER_MWH: gas 0.06t/MWh / coal 0 / biomass 0.01.
- get_ukets_price(year): year-indexed with fallback.
- AllowanceSource: AUCTION / FREE_ALLOCATION / SECONDARY_MARKET / FORWARD_PURCHASE.
- AllowancePurchase frozen: purchase_id, year, purchase_date, tonnes_co2, price; total_cost_gbp.
- ComplianceObligation frozen: generation_mwh, emission_factor_tonne_per_mwh, free_allocation; gross/net_obligation_tonnes (net clamped at 0).
- ETSRegistry: purchase(), record_obligation(), surrender(year, tonnes), holding_tonnes(year), total_spend_gbp(year), compliance_position(year) → {obligation/holdings/surplus_deficit/is_compliant/spend}.

**Fidelity delta:** UK ETS launched January 2021, replacing EU ETS for UK-based installations. Energy suppliers that own gas-fired generation (e.g., OVO with Luminae, EDF with nuclear + gas mix) must surrender allowances by April 30 each year for prior-year emissions. Gas receives free allocation (0.06t/MWh benchmark), reducing net compliance cost. Forward_purchase of ETS allowances is a hedging strategy: buy at £50 in Jan vs paying £72 at auction in March — exactly the kind of compliance hedging decision that falls within the company layer's permitted information. Net obligation clamped at zero because free allocation can exceed actual emissions during part-load operation.

**9 new tests (3,096 total).**

---
### Phase 226 -- Multisite I&C account management (2026-06-26)
**Files:** `company/crm/multisite_account.py` (new), `tests/company/crm/test_multisite_account.py` (new)

**What was built:**
- SiteCategory enum (6): HEAD_OFFICE / MANUFACTURING / WAREHOUSE / RETAIL_UNIT / DATA_CENTRE / REMOTE_OFFICE.
- BillingFrequency: MONTHLY / QUARTERLY / CONSOLIDATED (single invoice for all sites).
- SupplyPoint frozen: mpan, site_name, postcode, category, annual_kwh, max_demand_kva, connection_voltage_kv; is_hv (≥ 11kV), annual_mwh.
- MultisiteAccount mutable: add_site(), remove_site(), site_count, total_annual_kwh/mwh, peak_site, sites_by_category(), hv_sites(), account_summary().
- MultisitePortfolio: create_account(), get(), total_portfolio_mwh(), accounts_by_manager(), largest_accounts(n=5).

**Fidelity delta:** Large I&C customers (supermarkets, manufacturers, data centres) have 10-500 supply points under a single account. Consolidated billing is mandatory for FTSE 250 customers: one invoice, one credit limit, one account manager. is_hv (≥ 11kV) distinguishes direct DNO connections (no LV distribution charge) from LV-connected sites — HV discount is £5-8/MWh on DUoS charges. Data centres (>1 MW load) have 100% load factor (constant draw) vs warehouses (50-70%), making them the highest-value I&C customer type. largest_accounts() drives the key account management prioritisation.

**9 new tests (3,087 total).**

---
### Phase 225 -- Working capital daily cash position (2026-06-26)
**Files:** `company/finance/working_capital.py` (new), `tests/company/finance/test_working_capital.py` (new)

**What was built:**
- CashFlowType (9): CUSTOMER_COLLECTIONS / WHOLESALE_SETTLEMENT / NETWORK_CHARGES / PAYROLL / VAT_PAYMENT / CREDIT_FACILITY_DRAWDOWN / CREDIT_FACILITY_REPAYMENT / DSR_REVENUE / REGO_PURCHASE.
- CashFlowDirection: INFLOW / OUTFLOW; signed_amount (positive for inflow, negative for outflow).
- DailyCashPosition mutable: opening_balance, entries; net_cash_flow, closing_balance, total_inflows, total_outflows.
- WorkingCapitalMonitor: opening_balance + _minimum_operating_balance (default £50k); post_day(date, [(type, direction, amount, ref)]), current_balance(), is_below_minimum(), headroom_gbp(), positions_in_period(), lowest_balance_in_period(), total_inflows_gbp(), cash_summary().

**Fidelity delta:** Working capital management is existential for energy suppliers. BSC wholesale settlement has a 28-day payment window with daily obligation swings — during Feb 2022, a medium supplier's daily settlement obligation could swing ±£500k. The "death spiral": low cash → miss settlement → BSC suspension → loss of licence. lowest_balance_in_period identifies stress dates when the operator must draw on the credit facility (Ph198) to avoid minimum breach. Connects to bsc_credit.py (Ph53) which sets the minimum credit cover that compounds the cash drain.

**9 new tests (3,078 total).**

---
### Phase 224 -- Demand Side Response (DSR) portfolio (2026-06-26)
**Files:** `company/market/dsr_portfolio.py` (new), `tests/company/market/test_dsr_portfolio.py` (new)

**What was built:**
- DSREventType (5): GRID_STRESS / FREQUENCY_RESPONSE / TRIAD_AVOIDANCE / CAPACITY_MARKET_DISPATCH / VOLUNTARY.
- CurtailmentStatus: NOTIFIED / COMPLIED / PARTIAL / NON_COMPLIANT / EXEMPTED.
- DSREvent mutable: start/end_datetime, target_mw_reduction, notice_minutes; duration_hours, target_mwh, is_short_notice (< 30 min).
- CustomerCurtailment mutable: contracted_reduction_kw, actual_reduction_kw, revenue_gbp; compliance_pct; auto-status (COMPLIED ≥ 95%, PARTIAL > 0, else NON_COMPLIANT).
- DSRPortfolio: create_event(), record_curtailment(), total_mwh_delivered(event_id), compliance_rate_pct(event_id), annual_revenue_gbp(year), dsr_summary(year).

**Fidelity delta:** Flexibility markets are a major I&C revenue stream: large consumers can earn £50-200/MWh for voluntary curtailment during grid stress events (National Grid ESO EMR auctions). Triad avoidance events (3 peak demand half-hours Nov-Feb 16-19:00) save £15-20/MWh of annual TNUoS charges for HH-settled customers — a significant cost reduction incentive. Capacity Market (CM) participants receive £40-60/kW/year for availability. compliance_rate feeds Ofgem reporting (DSR providers must maintain ≥ 85% compliance or face CM penalties). DSR revenue supplements commodity margin — a hidden differentiator for I&C suppliers.

**9 new tests (3,069 total).**

---
### Phase 223 -- Period-end financial reconciliation ledger (2026-06-26)
**Files:** `company/finance/period_reconciliation.py` (new), `tests/company/finance/test_period_reconciliation.py` (new)

**What was built:**
- ReconciliationStatus: OPEN / RECONCILED / DISPUTED / WRITTEN_OFF.
- VarianceType (5): REVENUE_SHORTFALL / COST_OVERRUN / SETTLEMENT_DIFFERENCE / ACCRUAL_REVERSAL / METER_READ_ERROR.
- ReconciliationVariance frozen: period, variance_type, amount_gbp; is_adverse (< 0), abs_amount_gbp.
- PeriodReconciliation mutable: billed/accrued revenue + wholesale/network/policy/operating cost breakdown; total_revenue, total_cost, gross_margin, total_variance, adjusted_margin (margin + variances); add_variance(), close().
- ReconciliationLedger: open_period(), get(), open_periods(), annual_gross_margin_gbp(year), variances_by_type(year), reconciliation_summary(year).

**Fidelity delta:** UK energy supplier month-close process: Revenue (billed) booked in arrears; accruals bridge the 42-day billing lag. Settlement differences arise because Elexon runs 3 Settlement Runs (SF, R1, R2) that may revise volumes 28 days later. Accrual reversal is required when a billed quarter is finally settled at a different volume. The ReconciliationLedger is the mechanism by which the CFO signs off P&L each month: adjusted_margin = gross_margin + net_variances is the bottom line they approve. Connects to revenue_accruals (Ph202) and bad_debt_provision (Ph201).

**9 new tests (3,060 total).**

---
### Phase 222 -- Interconnector cross-border price exposure (2026-06-26)
**Files:** `company/market/interconnector_monitor.py` (new), `tests/company/market/test_interconnector_monitor.py` (new)

**What was built:**
- Interconnector enum (7): IFA1 2000MW / IFA2 1000MW / BritNed 1000MW / NEMO 1000MW / NSL 1400MW / VikingLink 1400MW / ElecLink 1000MW.
- FlowDirection: IMPORT / EXPORT / CONSTRAINED.
- _INTERCONNECTOR_CAPACITY_MW: registry by interconnector.
- InterconnectorObservation frozen: flow_mw, gb/foreign price; price_differential, capacity_mw, utilisation_pct.
- InterconnectorPriceMonitor: record(), observations_for(), avg_price_differential(), highest_differential(), import_days(), total_import_mwh(interconnector), monitor_summary(date).

**Fidelity delta:** Interconnectors now supply ~10% of GB electricity; during 2022 NordStream disruption, French nuclear outages meant IFA/ElecLink reversed direction from import to export, and GB prices decoupled from European prices. price_differential peaks (£500+/MWh across IFA1, Jan 2022 cold snap) represent arbitrage opportunities for large I&C customers with flexibility. utilisation_pct tracks interconnector constraint risk: at >95%, any outage on the link disrupts the market instantly. monitor_summary feeds the annual market risk report.

**8 new tests (3,051 total).**

---
### Phase 221 -- SoLR exposure model (2026-06-26)
**Files:** `company/regulatory/solr_exposure.py` (new), `tests/company/regulatory/test_solr_exposure.py` (new)

**What was built:**
- _SOLR_LEVY_HISTORY_GBP_PER_MWH (2016-2025): 2016 £0.50 → 2022 £10.00 → 2025 £2.50.
- get_solr_levy_gbp_per_mwh(year): year-indexed lookup with fallback to most recent.
- SoLREvent mutable: event_id, failed_supplier, announcement_date, customer_count, avg_annual_kwh, legacy_credit_gbp; total_annual_mwh, levy_cost_gbp(year).
- SoLRAcquisitionPrice frozen: offered_unit_rate_pence, offered_standing_pence, acquisition_premium_pct, is_above_svt.
- SoLRBook: record_event(), complete_transfer(appointed_solr), annual_levy_cost_gbp(year), total_legacy_credit_gbp(), events_summary(year).

**Fidelity delta:** From Sep 2021 to Apr 2022, 29 UK energy suppliers failed, including Bulb (1.7m customers) which entered SAR (Special Administration Regime). The SoLR process costs are recovered through the Supplier of Last Resort Levy and the BSC Balancing Mechanism charges — these are already in the mutualization_levy (Ph54) rate table (same £10.0/MWh peak). Legacy credit_gbp is the customer credit balance that was transferred and must be honoured: the SoLR is compensated via a Levy pooled across all remaining suppliers (Ofgem SLC 14A.3). SoLR appointment has strategic value: it delivers a large customer tranche instantly, typically priced above SVT to recover the credit debt.

**8 new tests (3,043 total).**

---
### Phase 220 -- Smart meter HH consumption analytics (2026-06-26)
**Files:** `company/billing/smart_meter_analytics.py` (new), `tests/company/billing/test_smart_meter_analytics.py` (new)

**What was built:**
- PERIODS_PER_DAY = 48 / PERIOD_MINUTES = 30 (Ofgem standard HH settlement).
- HHReading frozen: customer_id, read_datetime, kwh; settlement_period (1-48), is_evening_peak (SP 33-40 = 16:00-20:00), is_morning_peak (SP 15-18 = 07:00-09:00).
- build_consumption_profile(): aggregates readings into ConsumptionProfile (total_kwh, peak_kwh, off_peak_kwh, avg_daily_kwh, max_demand_kw = peak_kWh × 2, load_factor_pct = avg_kw/max_kw, peak_share_pct, days_covered).
- SmartMeterAnalytics: ingest(customer_id, datetime, kwh), profile(customer_id), customers_with_data(), evening_peak_customers(threshold_pct=35%), high_demand_customers(threshold_kw).

**Fidelity delta:** HH metered customers (I&C and smart meter resi) submit Actual Metered Data (AMD) in 48 half-hourly periods per Elexon BSC. evening_peak_customers() identifies ToU candidates for peak-shifting incentive (Ph52 demand response). max_demand_kw is used for TNUoS Triad demand assessment (winter peaks 16-19:00 on weekdays Nov-Feb). load_factor is a credit quality signal: low load_factor (< 30%) with high max_demand = large, sporadic consumer — higher credit risk. ConsumptionProfile integrates with billing engine for accurate HH bill calculation vs profile-class estimation.

**9 new tests (3,035 total).**

---
### Phase 219 -- Energy efficiency obligation tracker (2026-06-26)
**Files:** `company/regulatory/ee_obligation_tracker.py` (new), `tests/company/regulatory/test_ee_obligation_tracker.py` (new)

**What was built:**
- EEScheme enum (5): ECO4 / GBIS / WHD / BUS / HUG2.
- MeasureType enum (8): LOFT_INSULATION / CAVITY_WALL / SOLID_WALL / HEAT_PUMP / BOILER_UPGRADE / SOLAR_PV / SMART_HEATING / GLAZING.
- _TYPICAL_SAVINGS_KWH_PER_YEAR: 600 (loft) to 3000 (heat pump) kWh/year.
- EEReferral mutable: referral_id, customer_id, scheme, measure_type, referral_date, is_vulnerable; typical_annual_saving_kwh, is_completed, install(date, installer, cost_gbp).
- EEObligationTracker: refer(), get(), completed_measures(year), total_savings_kwh(year), obligation_mwh_delivered(scheme, year), vulnerable_customer_count(scheme), portfolio_summary(year).

**Fidelity delta:** Suppliers with ≥150k customers have ECO4 obligations set by Ofgem each year (2022-2026). Obligation is denominated in MWh of lifetime energy savings delivered through qualifying measures. Heat pump is highest-value (3,000 kWh/yr) but lowest volume; loft insulation is lowest-value but easiest to deliver. obligation_mwh_delivered(ECO4, year) feeds build_obligations_report() (Ph199) eco4_delivered_mwh argument. GBIS (Great British Insulation Scheme, 2023+) targets EPC D-G properties and fuel poor households. HUG2 (Home Upgrade Grant) is grant-funded for off-gas-grid homes.

**8 new tests (3,026 total).**

---
### Phase 218 -- Complaint register and SLC 27 compliance (2026-06-26)
**Files:** `company/crm/complaint_register.py` (new), `tests/company/crm/test_complaint_register.py` (new)

**What was built:**
- ComplaintCategory enum (8): BILLING / METER_READS / SUPPLY_FAILURE / SWITCH / DEBT_COLLECTION / CUSTOMER_SERVICE / SMART_METER / TARIFF.
- ComplaintStatus: OPEN / UNDER_INVESTIGATION / AWAITING_CUSTOMER / RESOLVED / UPHELD / NOT_UPHELD / OMBUDSMAN_REFERRED.
- RESOLUTION_DEADLINE_DAYS = 56 (8 calendar weeks, SLC 27).
- Complaint mutable: deadline(), days_open(as_of), is_overdue(as_of), is_ombudsman_eligible(as_of) (at 56d), resolve(date, upheld, goodwill_gbp), refer_to_ombudsman(date).
- ComplaintRegister: raise_complaint(), get(), open_complaints(), overdue_complaints(as_of), complaints_per_100_customers(count, year), upheld_rate_pct(year), total_goodwill_gbp(year), complaints_summary(as_of, customer_count).

**Fidelity delta:** Ofgem SLC 27 requires complaints to be resolved or acknowledged within 8 weeks (56 days); after that, the customer may refer to the Energy Ombudsman and the supplier must cooperate. complaints_per_100 feeds licence_health.py (Ph206) WATCH/BREACH check (threshold 3/100). Upheld rate of >50% suggests systematic billing or service quality issues — a trigger for Ofgem review. Goodwill payments are P&L cost: 2022 saw industry-wide surge in billing complaints as suppliers issued large catch-up bills post-freeze.

**9 new tests (3,018 total).**

---
### Phase 217 -- Trade finance instrument registry (2026-06-26)
**Files:** `company/finance/trade_finance.py` (new), `tests/company/finance/test_trade_finance.py` (new)

**What was built:**
- InstrumentType enum (5): LETTER_OF_CREDIT / BANK_GUARANTEE / PARENT_GUARANTEE / SURETY_BOND / CASH_DEPOSIT.
- InstrumentStatus enum: ACTIVE / EXPIRING_SOON (<= 30 days) / EXPIRED / CALLED / CANCELLED.
- CreditInstrument mutable: instrument_id, customer_id, type, issuer, face_value_gbp, issue/expiry_date; days_to_expiry(as_of), refresh_status(as_of), call(date, amount).
- TradeFinanceLedger: register(), get(), call_instrument(), total_credit_support_gbp(customer, as_of) excludes expired/called, expiring_within(as_of, days), instruments_by_type(as_of), portfolio_summary(as_of).

**Fidelity delta:** I&C customers (industrial and commercial sites) routinely post Letters of Credit (LOC) or bank guarantees instead of cash deposits to meet BSC credit cover and supplier security requirements. A £500k LOC from HSBC covers both BSC margin and supplier credit risk. During the 2022 crisis, LC fees rose ~3x as banks priced in credit deterioration of energy companies. Expiry tracking is mission-critical: an expired LOC leaves the supplier unsecured and the customer in technical default, triggering a right to restrict supply under SLC 22B. Portfolio-level total_coverage_gbp feeds the BSC credit cover model (Ph53).

**8 new tests (3,009 total).**

---
### Phase 216 -- Network charge pass-through ledger (2026-06-26) ★ 3,001 TESTS
**Files:** `company/market/network_charge_ledger.py` (new), `tests/company/market/test_network_charge_ledger.py` (new)

**What was built:**
- NetworkChargeType enum (5): TNUOS / DUOS / BSUOS / CMSUOS / METERING.
- NetworkChargeRate frozen: year, charge_type, commodity, rate_gbp_per_mwh, notes.
- NetworkChargeRecord frozen: customer_id, mpan, period, charge_type, consumption_mwh, rate; charge_gbp property.
- NetworkChargeLedger: set_rate(), get_rate(year, type, commodity), post_charge(), total_charges_gbp(customer, period), charges_by_type(year), portfolio_total_gbp(year), annual_summary(year).

**Fidelity delta:** UK electricity bills comprise ~30% network costs (TNUoS + DUoS + BSUoS) at ~£38-50/MWh combined. TNUoS (National Grid transmission) is charged to large suppliers who participate in the settlement; DUoS (distribution) is charged by DNOs regionally and varies significantly (London = £15/MWh, rural Scotland = £40/MWh). BSUoS doubled in 2022 to ~£20/MWh as the GB system had to take exceptional balancing actions during gas supply constraints. These are genuine pass-through costs — suppliers don't profit from them, but tracking misallocation is a significant billing error source. Feeds company_pl (Ph181) network_cost_gbp line.

**★ 3,001 TESTS — project milestone reached.**

---
### Phase 215 -- Supply contract lifecycle manager (2026-06-26)
**Files:** `company/billing/contract_manager.py` (new), `tests/company/billing/test_contract_manager.py` (new)

**What was built:**
- ContractStatus enum: ACTIVE / IN_NOTICE / EXPIRED / CANCELLED / RENEWED.
- ContractType enum: FIXED_TERM / VARIABLE / DEEMED / EVERGREEN.
- _NOTICE_PERIOD_DAYS: FIXED_TERM 42d / VARIABLE 28d / DEEMED 14d / EVERGREEN 90d.
- SupplyContract mutable: contract_id, customer_id, mpan, type, start/end_date, rates, aq; notice_period_days, term_months, notice_deadline() (end - notice), is_in_notice_window(as_of), days_to_expiry(as_of), annual_cost_estimate_gbp().
- ContractManager: register(), serve_notice() (sets IN_NOTICE + date), expire_contract(), contracts_for_customer(), active_contracts(), expiring_within(as_of, days), contracts_in_notice_window(as_of), portfolio_summary(as_of).

**Fidelity delta:** UK fixed-price contracts must be notified 42 days before expiry per Ofgem SLC 25B. Failure to notify means the customer auto-rolls to SVT — the most common source of customer complaints. The 90-day evergreen notice is standard for I&C multi-site contracts. is_in_notice_window() feeds renewals_book (Ph194) outreach: only customers in the notice window should be called for renewal. expiring_within() drives the renewal_chase campaign (Ph203): call list generated 50 days before expiry.

**9 new tests (2,993 total).**

---
### Phase 214 -- Ancillary product bundle tracker (2026-06-26)
**Files:** `company/crm/ancillary_products.py` (new), `tests/company/crm/test_ancillary_products.py` (new)

**What was built:**
- AncillaryProduct enum (7): BOILER_COVER / EV_TARIFF / SMART_HOME_CONTROLS / HOME_INSURANCE / BROADBAND / CARBON_OFFSET / SOLAR_MONITORING.
- _MONTHLY_REVENUE_GBP defaults: £18 boiler, £0 EV tariff (margin from commodity), £5 smart controls, £32 insurance, £28 broadband, £3 carbon, £4 solar monitoring.
- ProductSubscription mutable: customer_id, product, start_date, end_date, monthly_price_gbp (defaults from table); is_active, annual_revenue_gbp(year) (prorated to period within year).
- AncillaryRevenueTracker: subscribe(), cancel(), active_subscriptions(), products_per_customer(), total_annual_revenue_gbp(), revenue_by_product(), avg_products_per_customer(), portfolio_summary(year).

**Fidelity delta:** Product bundling has become a key differentiation and margin strategy for UK energy retailers. Octopus Energy achieved 2.8 products/customer average in 2024 (energy + EV tariff + smart controls + Intelligent Octopus), generating ~£50/customer/year ancillary revenue. OVO bundled Kaluza smart controls + carbon offset + boiler cover. avg_products_per_customer is the NPS-equivalent metric that predicts churn: multi-product customers churn 60% less than commodity-only. EV_TARIFF earns £0 direct revenue but locks in commodity consumption as EVs represent 1.5-4 MWh/year additional load.

**8 new tests (2,984 total).**

---
### Phase 213 -- Meter read validation engine (2026-06-26)
**Files:** `company/billing/meter_read_validation.py` (new), `tests/company/billing/test_meter_read_validation.py` (new)

**What was built:**
- ReadSource enum: CUSTOMER / ESTIMATED / SMART_METER / ENGINEER_VISIT.
- ValidationFlag enum: REVERSAL / EXCESSIVE_DAILY_RATE (>3x expected) / LOW_DAILY_RATE (<0.2x expected) / TRANSPOSITION_LIKELY / METER_ADVANCE_ZERO (zero advance > 7 days).
- ValidationResult enum: ACCEPTED / QUERIED / REJECTED.
- MeterReadValidation frozen: read_date, read_value, previous_read, previous_read_date, expected_daily_kwh, source; days_elapsed, advance_kwh, implied_daily_kwh, flags (list), result (REVERSAL/EXCESSIVE -> REJECTED; other flags -> QUERIED; else ACCEPTED), _check_transposition() (rotates last digit and checks if closer to expected), summary().

**Fidelity delta:** UK suppliers must validate all customer-submitted reads before billing. A transposed read (12456 entered as 12465) can create a £500 billing error. Industry benchmarks: >5% of reads require query; <0.5% are reversed (meter running backwards = fault). Smart meter reads bypass customer validation but still check for zero-advance (clock error or tamper). Engineer visits are ground truth — they override all other reads. This module feeds meter_dispute.py (Ph154) when a validated read contradicts a customer claim.

**7 new tests (2,976 total).**

---
### Phase 212 -- Wholesale price monitor (2026-06-26)
**Files:** `company/market/price_monitor.py` (new), `tests/company/market/test_price_monitor.py` (new)

**What was built:**
- PriceAlertLevel enum: NORMAL / ELEVATED / HIGH / EXTREME.
- Commodity enum: ELECTRICITY / GAS.
- PriceObservation frozen: spot/month_ahead/quarter_ahead prices; term_structure_slope (M1-spot), is_backwardation (<-2), is_contango (>+2).
- PriceTrigger: trigger_id, commodity, level, threshold_gbp_per_mwh, description.
- WholesalePriceMonitor: add_trigger(), record_observation(), latest_observation(), active_alerts() (sorted by threshold desc), highest_alert_level(), price_history(days), monitor_summary().

**Fidelity delta:** Energy supplier trading desks typically set 4 alert tiers for spot prices. For electricity: ELEVATED >=£80/MWh (2x pre-crisis avg), HIGH >=£200/MWh (4x), EXTREME >=£400/MWh (8x). During August 2022, Day-Ahead electricity hit £900/MWh — every trigger breached simultaneously. is_backwardation (spot > forward) is a key signal: it means the market expects supply relief, so locking in forward buys is advisable; contango (forward > spot) means carry cost of being long. Term structure slope directly feeds hedge_decision.py (existing Ph43a). This module is the company-layer price observatory — it reads from market_data feeds, not SIM internals.

**8 new tests (2,969 total). 150 company/ files milestone.**

---
### Phase 211 -- Customer payment behaviour analytics (2026-06-26)
**Files:** `company/billing/payment_behaviour.py` (new), `tests/company/billing/test_payment_behaviour.py` (new)

**What was built:**
- PaymentResult enum: ON_TIME / LATE / DD_FAILED / PARTIAL / MISSED.
- PaymentBehaviour enum: EXCELLENT (0% failures) / GOOD (<10%) / FAIR (<25%) / POOR (<50%) / CRITICAL (>=50%).
- PaymentRecord frozen: customer_id, due_date, amount_due/paid, payment_date, result; days_late (None if missed), shortfall_gbp.
- PaymentBehaviourAnalytics: record(), records_for_customer(), on_time_rate(), dd_failure_rate(), avg_days_late(), behaviour_score(), total_shortfall_gbp(), portfolio_summary() with by_behaviour breakdown.

**Fidelity delta:** UK energy suppliers track payment behaviour at the individual customer level as an operational risk metric. DD failure rate > 20% is a red flag for the credit team; behaviour_score drives arrears escalation priority (CRITICAL customers get immediate outbound call, POOR get SMS, EXCELLENT get digital self-serve). The behaviour score feeds credit_scoring (Ph135) at renewal — repeat DD failures can downgrade a PRIME customer to SUBPRIME, triggering deposit requirement. 2022 crisis: DD_FAILED rates doubled industry-wide as customers hit by energy bill shock cancelled DDs.

**9 new tests (2,961 total).**

---
### Phase 210 -- Regulatory reporting calendar (2026-06-26)
**Files:** `company/regulatory/reporting_calendar.py` (new), `tests/company/regulatory/test_reporting_calendar.py` (new)

**What was built:**
- ReportingFrequency enum: MONTHLY / QUARTERLY / ANNUAL / AD_HOC.
- DeadlineStatus enum: PENDING / SUBMITTED / OVERDUE / WAIVED.
- RegulatoryDeadline frozen: status(as_of), is_submitted, days_until_due(as_of).
- RegulatoryCalendar: add_deadline(), mark_submitted() (replaces frozen dataclass), overdue(as_of), due_within_days(as_of, days), by_regulator(regulator), calendar_summary(as_of) with due_within_14_days count.

**Fidelity delta:** UK energy suppliers face ~15-20 mandatory regulatory submissions per year: Ofgem Annual Return (April), WHD Core Group (Dec), DESNZ ECO4 quarterly reports, BSC monthly settlement data, MPAS quarterly reconciliation, Elexon half-hourly data, DESNZ SECR (Streamlined Energy and Carbon Reporting), FMD (Fuel Mix Disclosure), capacity market quarterly, RO quarterly, CfD quarterly. Missing a submission is a licence breach (SLC 21). A compliance manager tracks all deadlines on a rolling calendar — overdue detection triggers board escalation. Feeds licence_health.py (Ph206) compliance check.

**8 new tests (2,952 total).**

---
### Phase 209 -- Carbon emissions per customer (Scope 2) (2026-06-26)
**Files:** `company/regulatory/carbon_emissions.py` (new), `tests/company/regulatory/test_carbon_emissions.py` (new)

**What was built:**
- _EMISSION_FACTORS_G_CO2_PER_KWH dict: 8 fuel types (coal 820 / gas 490 / nuclear 12 / wind 11 / solar 41 / hydro 24 / biomass 230 / imports 300). IPCC 2014 lifecycle figures.
- FuelMixRecord frozen: year + 8 percentage fields; total_pct, renewable_pct (wind+solar+hydro), low_carbon_pct (renewable+nuclear+biomass), emission_intensity_g_per_kwh (VWAP of fuels).
- CustomerCarbonFootprint frozen: electricity_kwh, gas_kwh, electricity_intensity_g_per_kwh; electricity_co2_kg (intensity*kwh/1000), gas_co2_kg (183g/kWh fixed), total_co2_kg, total_co2_tonnes, summary().
- build_customer_footprint(customer_id, year, electricity_kwh, gas_kwh, fuel_mix) -> CustomerCarbonFootprint.

**Fidelity delta:** Ofgem mandates Fuel Mix Disclosure for all licensed suppliers (SLC 21). Every customer bill must state the fuel mix and associated CO2 emission rate for their tariff. Green tariff suppliers must match REGOs to their consumption and can report near-zero electricity emissions. A typical 2024 UK household uses 3,000 kWh electricity (140g/kWh → 420 kg CO2) + 11,000 kWh gas (183g → 2,013 kg) = 2.4 tonnes/year. This closes the Scope 2 reporting gap: fuel_mix.py (Ph billing) handles disclosure; this module computes the actual per-customer footprint for ESG reporting.

**8 new tests (2,944 total).**

---
### Phase 208 -- Staff headcount and payroll model (2026-06-26)
**Files:** `company/finance/payroll.py` (new), `tests/company/finance/test_payroll.py` (new)

**What was built:**
- Department enum (8): OPERATIONS / CUSTOMER_SERVICES / TRADING / FINANCE / TECHNOLOGY / REGULATORY / SALES / SENIOR_MANAGEMENT.
- EmploymentType enum: PERMANENT / CONTRACT / PART_TIME.
- HeadcountRole frozen: role_id, title, department, employment_type, annual_salary_gbp, headcount, fte; total_annual_salary_gbp, employer_ni_gbp (13.8% on salary above £9,100), pension_cost_gbp (5% of salary), total_employment_cost_gbp.
- HeadcountPlan: add_role(), total_headcount, total_fte, total_payroll_cost_gbp, cost_by_department(), headcount_by_department(), cost_per_customer_gbp(active_customers), summary().

**Fidelity delta:** A UK energy supplier's opex is 65-75% people costs. A 5,000-customer supplier needs ~30 FTE (18 CS agents, 4 operations, 3 finance, 3 trading, 2 regulatory), costing ~£1.5M/year (£300/customer). A 50,000-customer supplier needs ~120 FTE but achieves scale efficiency at £70-80/customer. During the 2022 crisis, customer_services headcount spiked 40% as call volumes tripled — opex soared before companies could reduce customer base. cost_per_customer_gbp feeds directly into company_pl (Ph181) operating_cost_gbp and activity-based pricing.

**8 new tests (2,936 total).**

---
### Phase 207 -- Commodity hedging schedule (2026-06-26)
**Files:** `company/market/hedging_schedule.py` (new), `tests/company/market/test_hedging_schedule.py` (new)

**What was built:**
- HedgeTenor enum: MONTH_AHEAD / QUARTER_AHEAD / SEASON_AHEAD / YEAR_AHEAD.
- Commodity enum: ELECTRICITY / GAS.
- ForwardContractDelivery frozen: contract_id, commodity, delivery_month, volume_mwh, contracted_price_gbp_per_mwh, tenor, traded_date; contract_value_gbp property.
- DeliveryMonthPosition mutable: forecast_mwh, _contracts list; hedged_mwh, open_position_mwh, hedge_ratio_pct, is_over_hedged, avg_contracted_price (VWAP).
- HedgingSchedule: set_forecast(), add_contract() [raises KeyError if no forecast], get_position(), over_hedged_months(), portfolio_hedge_ratio(), schedule_summary().

**Fidelity delta:** A UK electricity supplier typically hedges 80-95% of forecast consumption 12-18 months out (season-ahead and year-ahead), tapering to month-ahead top-ups. The avg_contracted_price is the VWAP of all forward contracts for a delivery month — this is what the trading desk uses to benchmark whether current spot pricing makes remaining open position buyable or worth deferring. 2022: suppliers who hedged 80% at £80/MWh year-ahead saw avg_contracted_price of £104 at delivery even with 20% bought at £200 spot — survivors. Naked suppliers paid £200 full stop.

**8 new tests (2,928 total).**

---
### Phase 206 -- Supply licence health monitor (2026-06-26)
**Files:** `company/regulatory/licence_health.py` (new), `tests/company/regulatory/test_licence_health.py` (new)

**What was built:**
- LicenceCheckStatus enum: PASS / WATCH / BREACH.
- LicenceCheck frozen: name, description, value, threshold, status, notes; headroom property.
- LicenceHealthReport frozen: checks tuple; pass/watch/breach_count, overall_status (worst), is_going_concern (zero breaches), get(name), summary().
- build_licence_health_report(as_of, active_customer_count, net_assets_gbp, treasury_gbp, weeks_cash_runway, bad_debt_ratio_pct, complaints_per_100) -> LicenceHealthReport.
- 6 checks: customer_count (>=50; watch at <75), net_assets_gbp (>= 0; balance sheet insolvency), treasury_gbp (>=£100k), cash_runway_weeks (>=8w; SoLR at <4w), bad_debt_ratio (PASS<3%/WATCH<5%/BREACH>=5%), complaints_per_100 (PASS<1/WATCH<3/BREACH>=3).

**Fidelity delta:** Ofgem requires SLC 28 net assets to be positive at all times; breach = mandatory board notification within 5 business days. Cash runway < 8 weeks triggers the internal Going Concern escalation protocol; < 4 weeks triggers Ofgem to consider appointing a SoLR. The supplier board is required to self-certify quarterly against all SLC conditions. is_going_concern = False means the auditors would add a "material uncertainty" note — triggering immediate investor scrutiny. This is the "will the business survive?" question that all the other financial modules (company_pl, cash_flow_forecast, credit_facility) ultimately feed.

**7 new tests (2,920 total).**

---
### Phase 205 -- Capacity-to-Pay (CtP) affordability assessment (2026-06-26)
**Files:** `company/billing/capacity_to_pay.py` (new), `tests/company/billing/test_capacity_to_pay.py` (new)

**What was built:**
- AffordabilityOutcome enum: CAN_PAY_IN_FULL / CAN_PAY_PARTIAL / CANNOT_PAY / FUEL_POVERTY.
- RecommendedAction enum (6): STANDARD_PLAN (12m) / EXTENDED_PLAN (24m) / MINIMUM_PLAN / PPM_CONVERSION / DEBT_ADVICE_REFERRAL / WRITE_OFF_CONSIDERATION.
- CtPAssessment frozen: monthly_income_gbp, monthly_essential_outgoings_gbp, total_debt_gbp, is_vulnerable; disposable_income_gbp (income-outgoings), energy_share_of_income_pct (debt/(income*12)*100), affordable_monthly_repayment_gbp (10% of disposable), outcome, recommended_action, estimated_plan_months, summary().
- Logic: fuel_poverty if energy_share >= 10%; cannot_pay if disposable=0; can_pay_in_full if 10%*disposable clears debt in 12m; partial otherwise. Vulnerable+fuel_poverty -> PPM_CONVERSION.

**Fidelity delta:** Ofgem SLC 27A requires suppliers to assess ability to pay before referring to external debt collectors. The 10% of income threshold aligns with the UK government's fuel poverty definition. CtP outputs feed directly into arrears_book (Ph174) stage transitions: PLAN_OFFERED uses affordable_monthly_repayment_gbp; CANNOT_PAY customers must be referred to debt advice (not straight to enforcement). The 2022 crisis: customers on SVT with unaffordable bills after cap removal → mass FUEL_POVERTY outcomes, mass PPM_CONVERSION requests.

**7 new tests (2,913 total).**

---
### Phase 204 -- Switching cooling-off and objection management (2026-06-26)
**Files:** `company/market/switch_governance.py` (new), `tests/company/market/test_switch_governance.py` (new)

**What was built:**
- Constants: COOLING_OFF_DAYS=14 (Consumer Contracts Regs 2013), OBJECTION_WINDOW_DAYS=15 (BSC).
- ObjectionReason enum: DEBT / CONTRACT_IN_TERM / CUSTOMER_REQUEST / IDENTITY_MISMATCH.
- ObjectionOutcome enum: UPHELD / REJECTED / WITHDRAWN.
- ErroneousTransferStatus enum: REPORTED / UNDER_INVESTIGATION / CUSTOMER_RETURNED / CLOSED_NO_ACTION.
- CoolingOffCancellation frozen: days_after_sale, within_cooling_off.
- SwitchObjection mutable: within_objection_window (<=15 days of switch request), is_resolved.
- ErroneousTransfer mutable: days_to_report, is_resolved.
- SwitchGovernanceBook: record_cancellation(), raise_objection(), resolve_objection(), report_et(), resolve_et(), cancellations_in_cooling_off(), open_objections(), open_ets(), annual_summary(year).

**Fidelity delta:** Ofgem monitors supplier performance on: cooling-off rate (>5% suggests mis-selling), erroneous transfer rate (<0.1% of switches), objection uphold rate (debt objections 80% upheld; contract-in-term varies). A losing supplier can raise a debt objection within 15 days to block the switch; the gaining supplier must respond. High ET rates trigger mandatory Ofgem remedial action and customer compensation. This closes the switching governance gap between switch_analytics (Ph186) and MPAN register (Ph185).

**7 new tests (2,906 total).**

---
### Phase 203 -- Outbound contact campaign tracker (2026-06-26)
**Files:** `company/crm/campaign_tracker.py` (new), `tests/company/crm/test_campaign_tracker.py` (new)

**What was built:**
- CampaignType enum (7): RENEWAL_CHASE / RETENTION_WINBACK / DEBT_COLLECTION / SMART_METER_INSTALL / EEP_REFERRAL / WHD_OUTREACH / SURVEY.
- ContactOutcome enum (6): CONVERTED / NO_ANSWER / REFUSED / CALLBACK_ARRANGED / WRONG_NUMBER / UNCONTACTABLE.
- ContactChannel enum (4): PHONE / EMAIL / SMS / POST.
- CampaignContact frozen: is_converted (outcome==CONVERTED), is_reached (not NO_ANSWER/WRONG_NUMBER/UNCONTACTABLE).
- Campaign mutable: target_count, _contacts; is_active (no end_date), contacts_made, conversion_rate (converted/reached*100), contact_rate (reached/total*100), summary().
- CampaignTracker: create_campaign(), record_contact() (auto-IDs CTT-NNNN), close_campaign(), get(), active_campaigns(), campaigns_by_type().

**Fidelity delta:** UK supplier outbound contact centres run ~6 concurrent campaigns: Oct-Nov renewal chase (fixed tariff expiry), debt collection (arrears > 60d), WHD outreach (Oct-Dec), smart meter install book (rolling), EEP referral (vulnerable customers). Conversion rate differs by channel: phone 15-25%, email 3-8%, SMS 5-12%, post <1% for collections. Outbound lift metric (Ph194 renewals_book) is the aggregate of these campaign conversions minus natural renewal rate.

**8 new tests (2,899 total).**

---
### Phase 202 -- Revenue accruals ledger (2026-06-26)
**Files:** `company/finance/revenue_accruals.py` (new), `tests/company/finance/test_revenue_accruals.py` (new)

**What was built:**
- RevenueType enum: COMMODITY / STANDING_CHARGE / EXIT_FEE / LATE_PAYMENT_FEE / RECONNECTION_FEE.
- RecognitionBasis enum: BILLED / ACCRUED.
- RevenueEntry frozen dataclass: customer_id, period_start/end, revenue_type, basis, amount_gbp, commodity; period_days and daily_revenue_gbp properties.
- RevenueAccrualsLedger: post(), entries_in_period(), billed_revenue_gbp(), accrued_revenue_gbp(), total_revenue_gbp(), by_type(), accrual_ratio() (accrued/total*100), monthly_summary(year, month).

**Fidelity delta:** UK energy suppliers recognise revenue under IFRS 15 ("when performance obligation satisfied"). For energy, this means revenue accrues daily as gas/electricity flows — even if the bill hasn't been issued yet. A high accrual_ratio indicates a long billing cycle: the company has supplied energy but not collected cash (receivables risk). During the 2022 crisis, suppliers with quarterly billing had accrual ratios of 60-70% — meaning most "revenue" was a promise, not cash. The ledger bridges company_pl (Ph181) REVENUE line with cash_flow_forecast (Ph183) RECEIPTS line.

**7 new tests (2,891 total).**

---
### Phase 201 -- Bad debt provisioning model (2026-06-26)
**Files:** `company/finance/bad_debt_provision.py` (new), `tests/company/finance/test_bad_debt_provision.py` (new)

**What was built:**
- AgingBucket enum: CURRENT (0-30d) / DAYS_30 (31-60d) / DAYS_60 (61-90d) / DAYS_90 (91-180d) / DAYS_180_PLUS.
- _PROVISION_RATES: 0.5% / 5% / 20% / 50% / 90% (standard UK ECL approach).
- classify_age(days_outstanding) -> AgingBucket.
- ArrearsLedgerItem frozen: customer_id, outstanding_gbp, days_outstanding, is_vulnerable; aging_bucket, provision_rate, provision_gbp properties.
- BadDebtProvision frozen: items tuple; total_arrears_gbp, total_provision_gbp, provision_coverage_pct, by_bucket() dict, vulnerable_provision_gbp(), summary().
- build_provision(as_of, items) -> BadDebtProvision.

**Fidelity delta:** Under IFRS 9 (adopted 2018), UK suppliers must hold an "expected credit loss" (ECL) provision against their arrears book, staged by days overdue. A mid-sized supplier with £1M in arrears might hold £200-400k in provision; during the 2022 crisis the provision rate doubled as 180-day balances surged. The CFO uses provision_coverage_pct as a health indicator — below 25% = aggressive; above 60% = stress signal. Bridges arrears_book (Ph174), vulnerability_register (Ph169), company_pl (Ph181), and bad_debt field in BoardKPIDashboard (Ph182).

**8 new tests (2,884 total).**

---
### Phase 200 -- Customer lifecycle stage tracker (2026-06-26)
**Files:** `company/crm/lifecycle_tracker.py` (new), `tests/company/crm/test_lifecycle_tracker.py` (new)

**What was built:**
- LifecycleStage enum (10 states): PROSPECT → PENDING_SWITCH → ACTIVE → AT_RISK / IN_ARREARS / IN_DEFERRAL / RENEWAL_DUE → CHURNED / MOVED_OUT / DECEASED.
- _ON_SUPPLY_STAGES set: PENDING_SWITCH, ACTIVE, AT_RISK, IN_ARREARS, IN_DEFERRAL, RENEWAL_DUE (not CHURNED/MOVED_OUT/DECEASED).
- LifecycleEvent dataclass: customer_id, from_stage, to_stage, event_date, reason.
- CustomerLifecycle mutable: stage, acquisition_date, _history; is_on_supply, is_active_customer, transition(), tenure_days(as_of), stage_history().
- CustomerLifecycleTracker: register(), get(), transition(), customers_in_stage(), active_customers(), on_supply_count(), portfolio_summary(as_of).

**Fidelity delta:** UK supplier CRM systems track each customer's commercial status as a state machine. portfolio_summary() gives the CMO an at-a-glance split: 850 active / 40 at-risk / 12 in-arrears / 6 renewal-due / 28 churned. The tracker is the hub that connects renewals_book (Ph194), arrears_book (Ph174), payment_deferral (Ph170), vulnerability_register (Ph169) — real suppliers segment on exactly these lifecycle states for outbound contact prioritisation.

**8 new tests (2,876 total).**

---
### Phase 199 -- Annual regulatory obligations report (2026-06-26)
**Files:** `company/regulatory/annual_obligations.py` (new), `tests/company/regulatory/test_annual_obligations.py` (new)

**What was built:**
- ObligationStatus enum: MET / AT_RISK / BREACHED / NOT_APPLICABLE.
- ObligationLineItem frozen dataclass: name/obligation_value/delivered_value/unit/status/penalty_estimate_gbp; delivery_pct, shortfall properties.
- AnnualObligationsReport frozen dataclass: year/report_date/obligations tuple; met_count/at_risk_count/breached_count/overall_status (worst wins)/total_penalty_estimate_gbp/get(name)/summary().
- build_obligations_report(): assembles WHD (£150/customer shortfall), ECO4 (£10/MWh shortfall), GSOP (breach count + payments), Ofgem Annual Return (overdue if submitted=False and past due_date), REGO (£50/MWh shortfall).

**Fidelity delta:** UK energy suppliers face a cascade of statutory obligations each year. Missing WHD rebates triggers Ofgem investigation (£150/customer missed); ECO4 shortfall means buying "traded carbon" credits at premium; GSOP payments are small (£30/SLA breach) but signal service failures; an overdue Ofgem Annual Return is a licence breach. board_kpis.py (Ph182) surfaces the aggregate; this report provides the line-item breakdown behind it. Bridges Ph167 (WHD register), Ph197 (EEP book), Ph143 (REGO audit), Ph190 (Ofgem supply return).

**8 new tests (2,868 total).**

---
### Phase 198 -- Revolving credit facility model (2026-06-26)
**Files:** `company/finance/credit_facility.py` (new), `tests/company/finance/test_credit_facility.py` (new)

**What was built:**
- DrawdownReason enum: WHOLESALE_SETTLEMENT / WORKING_CAPITAL / BSC_CREDIT_COVER / SEASONAL_CASHFLOW / EMERGENCY.
- CreditFacility frozen dataclass: facility_id, lender, limit_gbp, interest_rate_pct, commitment_fee_pct, maturity_date; daily_commitment_fee_gbp.
- FacilityDrawdown mutable dataclass: drawdown_id, facility_id, amount_gbp, drawdown_date, reason, repaid_date/amount; is_outstanding, interest_accrued_gbp(as_of, rate_pct).
- CreditFacilityBook: register_facility(), drawdown() [raises if would breach limit], repay(), outstanding_balance(facility_id), total_interest_accrued_gbp(as_of), utilisation_pct(facility_id).

**Fidelity delta:** UK mid-sized energy suppliers maintain a revolving credit facility (RCF) of £5-20M with a clearing bank. The 2022 crisis: wholesale settlement cash calls hit simultaneously with customer receipt delays → RCF drawn to 90% → lender covenant breach → administrator called in. utilis_pct >80% typically triggers a board-level liquidity alert. Interest at SONIA + 200-350bps; commitment fee ~0.5% pa on undrawn portion. Completes the treasury stack: 13w cashflow (Ph183) + RCF (Ph198) + BSC credit cover (Ph53).

**7 new tests (2,860 total).**

---
### Phase 197 -- Energy efficiency programme (EEP) book (2026-06-26)
**Files:** `company/crm/eep_book.py` (new), `tests/company/crm/test_eep_book.py` (new)

**What was built:**
- EEPMeasure enum: 8 measures (CAVITY_WALL / SOLID_WALL / LOFT_INSULATION / HEAT_PUMP / SOLAR_PV / SMART_CONTROLS / DOUBLE_GLAZING / BOILER_UPGRADE).
- EEPScheme enum: ECO4 / BUS / SEG / SELF_FUNDED.
- EEPInstallation frozen dataclass: customer_id, mpan, measure, scheme, install_date, estimated_annual_saving_gbp, cost_gbp, subsidy_gbp; customer_cost_gbp (cost-subsidy), simple_payback_years.
- EEPBook: record(), installs_for_customer(), total_subsidy_gbp(scheme=None, year=None), estimated_savings_portfolio_gbp(year=None), annual_summary(year) with by_measure.

**Fidelity delta:** UK suppliers report ECO4 annual obligation delivery to DESNZ and Ofgem. BUS (Boiler Upgrade Scheme) offers £7,500 grant toward heat pump installation, capped per year. ECO4 funding is allocated to obligated suppliers based on market share. A full-subsidy ECO4 loft insulation (zero customer cost) closes the payback question completely. Tracks the actual delivery book versus decarb_recommender.py (Ph168) which is the recommendation engine.

**7 new tests (2,853 total).**

---
### Phase 196 -- Digital portal analytics (2026-06-26)
**Files:** `company/crm/portal_analytics.py` (new), `tests/company/crm/test_portal_analytics.py` (new)

**What was built:**
- PortalAction enum: 11 actions (LOGIN, VIEW_BILL, DOWNLOAD_BILL, SUBMIT_METER_READ, CHANGE_DIRECT_DEBIT, UPDATE_CONTACT_DETAILS, VIEW_TARIFF, INITIATE_SWITCH, RAISE_COMPLAINT, VIEW_CONSUMPTION, ENROL_PAPERLESS).
- Self-serve actions: SUBMIT_METER_READ, CHANGE_DIRECT_DEBIT, UPDATE_CONTACT_DETAILS, ENROL_PAPERLESS.
- PortalEvent frozen dataclass: event_id, customer_id, action, event_datetime, session_id; is_self_serve.
- PortalAnalytics: record(), events_in_period(from_dt, to_dt, action=None), unique_users(), self_serve_rate(), action_counts(), monthly_summary(year, month).

**Fidelity delta:** UK suppliers track digital self-serve rate as a key cost metric. A 1% increase in portal self-serve reduces inbound call volume by ~800 calls/year per 100k customers. Post-2021 portal investments: meter read submission (reduces estimated billing errors), DD change (reduces call centre costs), paperless billing (reduces paper cost £2/customer/year). INITIATE_SWITCH spiked dramatically in Oct-Nov 2022 as customers tried to escape price cap rises. Tracks with contact_centre_metrics.py (Ph189) to show deflection impact.

**7 new tests (2,846 total).**

---
### Phase 195 -- NPS cohort tracker (2026-06-26)
**Files:** `company/crm/nps_tracker.py` (new), `tests/company/crm/test_nps_tracker.py` (new)

**What was built:**
- classify_nps(score) utility: promoter (9-10) / passive (7-8) / detractor (0-6).
- NPSResponse frozen dataclass: customer_id, score (0-10), surveyed_date, segment, channel, verbatim; category, is_promoter, is_detractor.
- NPSTracker: record() (raises if score not 0-10), nps_in_period(from_date, to_date, segment=None), monthly_nps(year) → 12-month dict, by_segment(year) → segment-keyed NPS dict, annual_summary(year) with responses/nps/promoter_pct/detractor_pct/by_segment.
- NPS = (promoters - detractors) / n × 100.

**Fidelity delta:** UK supplier NPS benchmarks: >30 excellent, 0-30 good, <0 poor. 2022 crisis: industry-wide NPS dropped from +25 to -15 in Q4 2022 as bills doubled. detractor_pct doubled from ~15% to ~30%. Tracking monthly NPS trends lets the ops team see emerging service problems before they hit complaints; post_call channel typically shows lowest NPS (customers call when unhappy). Complements conversation_log avg_nps() (Ph171) with cohort-level analytics.

**9 new tests (2,839 total).**

---
### Phase 194 -- Customer renewals analytics book (2026-06-26)
**Files:** `company/crm/renewals_book.py` (new), `tests/company/crm/test_renewals_book.py` (new)

**What was built:**
- RenewalOutcome enum: RENEWED / LAPSED / SWITCHED_AWAY / MOVED_OUT / DECEASED.
- OfferType enum: SAME_TARIFF / BETTER_TARIFF / PRICE_MATCH / LOYALTY_DISCOUNT / AUTO_ROLLOVER.
- RenewalRecord frozen dataclass: customer_id, segment, term_end_date, outcome, offer_type, offered_rate_ppm, new_term_months, days_notice_given, was_outbound_contact; accepted property.
- RenewalsBook: add(), renewal_rate(year, segment) [MOVED_OUT/DECEASED excluded from denominator], lapse_rate(), outbound_lift() [uplift in renewal rate from outbound contact], by_offer_type(year) [renewal rate per offer type], annual_summary(year).

**Fidelity delta:** UK supplier renewal rates are the #1 commercial metric. Typical renewal rate: 60-70% on fixed-term. Outbound contact lift is typically 8-15 percentage points — a customer who picks up the phone has 75% chance of renewal vs 65% without contact. LOYALTY_DISCOUNT offer type gets the highest renewal rate (85%+) but worst margin. 2022: many customers lapsed onto SVT (cheaper short-term) or switched away entirely as fixed rates rose above cap.

**8 new tests (2,830 total).**

---
### Phase 193 -- Demand-Side Response (DSR) programme book (2026-06-26)
**Files:** `company/market/dsr_book.py` (new), `tests/company/market/test_dsr_book.py` (new)

**What was built:**
- DSRStatus enum: ENROLLED / ACTIVE / SUSPENDED / WITHDRAWN.
- DispatchResult enum: DELIVERED (>=95% of requested) / PARTIAL / NON_DELIVERY / CANCELLED.
- DSRParticipant frozen dataclass: customer_id, mpan, contracted_mw, enrolled_date, status, payment_per_mwh_gbp.
- DispatchEvent frozen dataclass: event_id, customer_id, requested_mw, delivered_mw, dispatch_start/end, result, payment_gbp; duration_hours, delivered_mwh, delivery_rate computed.
- DSRBook: enroll(), dispatch() (raises if not ACTIVE; auto-classifies result; computes payment), events_for_customer(), total_contracted_mw(), total_payments_gbp(year), delivery_rate_year(year), annual_summary(year).

**Fidelity delta:** UK I&C customers can enroll in DSR programmes where they agree to reduce load on instruction from their supplier (who can offer them to NESO Balancing Services). Payment is typically £50-100/MWh delivered; non-delivery incurs reputational penalties. A 2MW I&C customer dispatched for 2 hours = 4 MWh = £240 payment. During the 2021-22 winter stress events, DSR was critical to avoiding demand disconnection.

**7 new tests (2,822 total).**

---
### Phase 192 -- Gas MPRN supply point register (2026-06-26)
**Files:** `company/market/mprn_register.py` (new), `tests/company/market/test_mprn_register.py` (new)

**What was built:**
- GasConsumptionBand enum: DOMESTIC (<=73,200 kWh AQ) / SMALL_NON_DOMESTIC (<=293k) / MEDIUM_NON_DOMESTIC (<=732k) / LARGE_NON_DOMESTIC (>732k).
- classify_gas_band(annual_quantity_kwh) utility.
- MPRNStatus enum: REGISTERED / DEREGISTERED / PENDING_REGISTRATION / PENDING_SWITCH / DISCONNECTED / OBJECTED.
- MPRNRecord frozen dataclass: mprn, status, annual_quantity_kwh, registered_date, current_supplier_id, deregistered_date, pending_switch_date; consumption_band, is_active (not DEREGISTERED/DISCONNECTED).
- MPRNRegister: register(), initiate_switch(), complete_switch(), deregister(), get(mprn), active_mprns(), by_band(band), portfolio_summary() with total_aq_kwh.

**Fidelity delta:** Xoserve manages the gas MPRN equivalent of MPAS. The AQ (Annual Quantity) banding matters commercially: large non-domestic customers have bespoke contracts and transportation charges; domestic have standard commodity charges. total_aq_kwh in portfolio_summary gives the gas-book total load — the CFO's gas supply exposure number, paired with GasNominationBook (Ph144) and hedge portfolio for gas risk.

**9 new tests (2,815 total).**

---
### Phase 191 -- Risk appetite framework (2026-06-26)
**Files:** `company/risk/risk_appetite.py` (new), `tests/company/risk/test_risk_appetite.py` (new)

**What was built:**
- RiskCategory enum: MARKET / CREDIT / LIQUIDITY / OPERATIONAL / REGULATORY.
- RiskRAG enum: WITHIN_APPETITE / APPROACHING_LIMIT / LIMIT_BREACH.
- RiskLimit frozen dataclass: limit_id, category, description, limit_value, unit, warning_threshold_pct (default 80%); warning_value property.
- RiskMeasurement frozen dataclass: limit_id, measured_value, measured_date, limit ref; utilisation_pct, rag (breach if > limit; approaching if >= 80% of limit; green otherwise), is_breach.
- RiskAppetiteFramework: approved_date, add_limit(), record_measurement(), latest_measurement(), active_breaches() (latest per limit), risk_dashboard(as_of) with items + breach count.

**Fidelity delta:** Every UK licensed supplier's board must approve a Risk Appetite Framework annually. The CRO (or FD in smaller suppliers) tracks limit utilisation monthly. In 2022: open gas position approaching 5,000 MWh limit as hedging became unaffordable → approaching; bad_debt 5% vs 3% limit → breach; both flagged to the board at the same time the P&L turned negative. This is the governance layer that failed at multiple UK suppliers in 2021-2022.

**8 new tests (2,806 total).**

---
### Phase 190 -- Ofgem annual supply data return (2026-06-26)
**Files:** `company/regulatory/ofgem_supply_return.py` (new), `tests/company/regulatory/test_ofgem_supply_return.py` (new)

**What was built:**
- OfgemSupplyReturn frozen dataclass: year, submitted_date, residential/SME/IC customer counts, elec/gas supplied (GWh), residential_complaints, average_debt_per_customer_gbp, whd_customers_supported, gsop_payments_gbp, solr_events, bad_debt_written_off_gbp; total_customers, complaints_per_100_customers, is_submitted, whd_penetration_pct, summary().
- OfgemReturnBook: file_return(), get(year), missing_years(from_year, to_year), all_returns() sorted.

**Fidelity delta:** Every UK licensed supplier must submit an annual supply data return to Ofgem by 31 March each year. The return is a statutory obligation; failure to file is an SLC breach. In 2022, the data was shocking: complaints_per_100 hit 10x normal at some suppliers; avg_debt_per_customer breached £200; WHD coverage dropped below the Ofgem target 70% penetration of eligible customers. missing_years() flags compliance gaps — the exact type of issue that triggers an Ofgem investigation.

**8 new tests (2,798 total).**

---
### Phase 189 -- Contact centre performance metrics (2026-06-26)
**Files:** `company/crm/contact_centre_metrics.py` (new), `tests/company/crm/test_contact_centre_metrics.py` (new)

**What was built:**
- AgentPerformancePeriod frozen dataclass: agent_id, period dates, calls_handled, total_handle_time_seconds, first_contact_resolutions, escalations, complaints_raised, avg_csat; computed: avg_handle_time_seconds, first_contact_resolution_rate, escalation_rate, complaint_rate (all None if zero calls).
- ContactCentreMetrics frozen dataclass: period dates, total_calls, answered_within_sla_seconds, abandoned_calls, total_handle_time_seconds, agents_on_duty; computed: abandonment_rate (abandoned/offered), sla_answer_rate, avg_handle_time_seconds, calls_per_agent, summary().

**Fidelity delta:** Ofgem monitors contact centre performance through SLC metrics. The 2022 crisis saw UK suppliers' average abandonment rates hit 25-30% (vs Ofgem target of <8%) and SLA answer rates (answering within 60 seconds) drop to 40% nationally. This directly caused complaint volumes to spike. Complements conversation_log.py (Ph171) with aggregate operational metrics that the COO reviews weekly.

**9 new tests (2,790 total).**

---
### Phase 188 -- Supplier of Last Resort (SoLR) intake (2026-06-26)
**Files:** `company/crm/solr_intake.py` (new), `tests/company/crm/test_solr_intake.py` (new)

**What was built:**
- SoLRIntakeStatus enum: NOTIFIED / CONTACTED / ONBOARDED / SWITCHED_AWAY / UNRESPONSIVE.
- SoLRBatch frozen dataclass: batch_id, failed_supplier, appointment_date, customer_count, deemed_tariff_rate_pct_above_cap; is_priced_above_cap flag.
- SoLRCustomer mutable dataclass: customer_id, batch_id, mpan, segment, status, contacted_date, onboarded_date, switched_away_date; is_retained (ONBOARDED).
- SoLRBook: register_batch(), add_customer(), mark_contacted(), mark_onboarded(), mark_switched_away(), customers_in_batch(), retention_rate(batch_id), contact_rate(batch_id), batch_summary().

**Fidelity delta:** 29 UK energy suppliers failed in 2021-22; each triggered a SoLR appointment. The SoLR receives stranded customers at a Ofgem-set "deemed" contract price (often above cap, as SoLRs were compensated). SoLR contact rate target is 85% in 30 days; retention of 50-60% is typical (rest switch to preferred tariff elsewhere). This is a genuinely UK-specific business event that no other retail sector has an equivalent to — and surviving suppliers must model the liability and operational cost of being a potential SoLR appointee.

**8 new tests (2,781 total).**

---
### Phase 187 -- CLV cohort analysis book (2026-06-26)
**Files:** `company/crm/clv_cohort_book.py` (new), `tests/company/crm/test_clv_cohort_book.py` (new)

**What was built:**
- CustomerCLVRecord frozen dataclass: customer_id, acquisition_year, channel, segment, clv_gbp, annual_margin_gbp, tenure_years.
- CohortSummary frozen dataclass: key, customer_count, avg_clv_gbp, median_clv_gbp, total_clv_gbp, avg_annual_margin_gbp, avg_tenure_years, profitable_pct, is_profitable_cohort.
- CLVCohortBook: add(), by_acquisition_year(year), by_channel(channel), by_segment(segment), all_cohorts_by_year() dict, best_cohort_by_year() / worst_cohort_by_year(), portfolio_summary().
- Median uses standard two-element average for even-n lists.

**Fidelity delta:** The board answer that matters: "which acquisition year cohort was most valuable?" PCW-acquired 2022 cohorts are the worst in history — high CAC, negative CLV because customers left the moment prices normalised. Direct-web 2019 cohorts are typically best: low CAC, long tenure, sticky SVT customers. best/worst_cohort_by_year lets the CFO see at a glance that PCW spend in 2021-2022 destroyed value. Extends clv_calculator.py (individual) to portfolio cohort view.

**9 new tests (2,773 total).**

---
### Phase 186 -- Supplier switching analytics (2026-06-26)
**Files:** `company/crm/switch_analytics.py` (new), `tests/company/crm/test_switch_analytics.py` (new)

**What was built:**
- SwitchDirection enum: GAIN / LOSS.
- SwitchStatus enum: INITIATED / COMPLETED / OBJECTED / CANCELLED / ERRONEOUS.
- SwitchEvent frozen dataclass: event_id, mpan, customer_id, direction, losing_supplier, gaining_supplier, initiation_date, completion_date, status, erroneous_transfer; days_to_complete, is_completed properties.
- SwitchAnalytics: record(), complete(), object(), mark_erroneous(), gains_in_year(year), losses_in_year(year), erroneous_transfers_in_year(year), avg_days_to_complete(year), net_customer_change(year), annual_summary(year).

**Fidelity delta:** The 5-day switching guarantee (formerly 21 days) is a key Ofgem target. In 2022, mass exodus from SVT price cap suppliers drove weeks-to-complete from 5 to 15+ days as MPAS was overwhelmed. Erroneous transfers (switching the wrong MPAN) peaked at ~0.4% of all switches nationally. avg_days_to_complete tracks process health. net_customer_change is the single metric the MD watches weekly. Complements MPAN register (Ph185) and TPI book (Ph184) for the full switching picture.

**8 new tests (2,764 total).**

---
### Phase 185 -- MPAN supply point register (2026-06-26)
**Files:** `company/market/mpan_register.py` (new), `tests/company/market/test_mpan_register.py` (new)

**What was built:**
- MPANStatus enum: REGISTERED / DEREGISTERED / PENDING_REGISTRATION / PENDING_SWITCH / ENERGISED / DE_ENERGISED / OBJECTED.
- ProfileClass enum: PC1-PC8 with Ofgem standard descriptions (Domestic/Non-Domestic/HH-settled tiers).
- MPANRecord frozen dataclass: mpan, status, profile_class, measurement_class, registered_date, current_supplier_id, deregistered_date, pending_switch_date; is_active (not DEREGISTERED or DE_ENERGISED), profile_class_description.
- MPANRegister: register(), initiate_switch() (→ PENDING_SWITCH), complete_switch() (new supplier, new registered_date), object_to_switch() (→ OBJECTED), deregister(), get(mpan), active_mpans(), pending_switches(), by_profile_class(pc), portfolio_summary().

**Fidelity delta:** Every electricity supply point in GB is identified by an MPAN. Suppliers register/de-register supply points with MPAS (Xoserve/DCC equivalent for electricity). The switch flow — initiate → complete OR object — matches real-world ERO (Electricity Registration and Change of Supplier) flow. Objection right lasts 15 working days from switch notification; grounds include active debt. PC1-PC8 classification determines whether a customer is settled as HH (PC5-PC8 P272/P415 mandate) or non-HH (PC1-PC4).

**9 new tests (2,756 total).**

---
### Phase 184 -- Third-party intermediary (TPI/broker) book (2026-06-26)
**Files:** `company/crm/tpi_book.py` (new), `tests/company/crm/test_tpi_book.py` (new)

**What was built:**
- TPITier enum: PREFERRED / STANDARD / PROBATION / SUSPENDED.
- TPICommissionBasis enum: FIXED_PER_CUSTOMER / PCT_OF_ANNUAL_REVENUE / PCT_OF_ANNUAL_CONSUMPTION.
- TPI frozen dataclass: tpi_id, name, tier, commission_basis, commission_rate, registered_date, accredited flag.
- TPIDeal frozen dataclass: deal_id, tpi_id, customer_id, annual_consumption_mwh, annual_revenue_gbp, deal_date; commission_gbp derived from basis (fixed / % revenue / £ per MWh).
- TPIBook: register(), suspend() (replaces TPI with SUSPENDED tier), record_deal() (raises if TPI suspended), deals_for_tpi(), total_commission_gbp(tpi_id=None), active_tpis(), annual_summary(year).

**Fidelity delta:** ~40% of UK SME/I&C customers are acquired through brokers/TPIs. Commission is typically 1.5-3% of annual revenue for I&C, or £60-120 fixed for SME. After the 2022 crisis, several brokers were suspended/de-accredited after mis-selling fixed-price contracts that suppliers then refused to honour. The suspension mechanism — blocking future deals from a bad actor — is a real regulatory tool. Complements channel_roi.py (Ph175) and marketing_budget.py (Ph180).

**9 new tests (2,747 total).**

---
### Phase 183 -- 13-week rolling cash flow forecast (2026-06-26)
**Files:** `company/finance/cash_flow_forecast.py` (new), `tests/company/finance/test_cash_flow_forecast.py` (new)

**What was built:**
- WeeklyCashFlow frozen dataclass: week_start, customer_receipts, wholesale_settlements, network_charges, policy_levies, operating_costs, other_outflows; total_inflows/total_outflows/net_cash/is_net_positive.
- CashFlowForecast frozen dataclass: as_of, opening_cash, weeks (13-week tuple); closing_cash_gbp, minimum_weekly_balance_gbp (minimum running balance), weeks_to_cash_concern (first week balance goes <=0; None if solvent), is_solvent_throughout, summary().
- build_cash_flow_forecast(): factory for steady-state weekly inputs; optional per-week other_outflows spike support.

**Fidelity delta:** Every UK energy supplier CFO reviews a 13-week rolling cash view weekly. The 2022 crisis: weekly wholesale settlements jumped from £70k to £100k+ while customer receipts stayed flat — no operational breathing room. weeks_to_cash_concern=1 means administration by next Monday without emergency liquidity. minimum_weekly_balance_gbp shows the tightest point, often around the BSC credit cover drawdown week. Complements board_kpis.py (Ph182) and company_pl.py (Ph181).

**9 new tests (2,738 total).**

---
### Phase 182 -- Board KPI dashboard (RAG status) (2026-06-26)
**Files:** `company/finance/board_kpis.py` (new), `tests/company/finance/test_board_kpis.py` (new)

**What was built:**
- KPIStatus enum: GREEN / AMBER / RED.
- KPIValue frozen dataclass: name, value, unit, target, lower_is_better; vs_target_pct, status (GREEN within -5%, AMBER -5 to -20%, RED below -20%).
- BoardKPIDashboard frozen dataclass: 7 KPIs, green/amber/red_count, overall_status (worst single KPI determines overall), get_kpi(name), summary() with kpis list.
- build_board_dashboard(): 7 standard UK energy supplier KPIs: customer_count, gross_margin_pct, ebitda_margin_pct, bad_debt_pct, complaint_resolution_days, csat_score, gsop_compliance_pct.

**Fidelity delta:** Every UK energy supplier board reviews a RAG dashboard quarterly. The 2022 crisis: bad_debt_pct=5% against a 1.5% target triggers RED (>3x overshoot), cascading the overall_status to RED even if all other KPIs are green. This pattern — a single financial risk metric dragging the whole board pack to red — was exactly how Bulb and others reported to their boards before administration. GSOP compliance <100% = Ofgem breach risk, separate from customer satisfaction.

**9 new tests (2,729 total).**

---
### Phase 181 -- Company-level P&L income statement (2026-06-26)
**Files:** `company/finance/company_pl.py` (new), `tests/company/finance/test_company_pl.py` (new)

**What was built:**
- CompanyPL frozen dataclass: 10 input fields (revenue, wholesale_cost, policy_cost, network_cost, operating_cost, marketing_cost, bad_debt, whd_rebates, gsop_payments).
- Computed properties: gross_margin_gbp (revenue - wholesale - policy - network), total_operating_cost_gbp (opex + marketing + bad_debt + WHD + GSOP), ebitda_gbp (gross - total_opex), gross_margin_pct, ebitda_margin_pct, bad_debt_as_pct_revenue, is_profitable, summary() dict.
- build_company_pl(): factory with most fields optional (defaults to 0).

**Fidelity delta:** This is the CFO's income statement. WHD rebates (£150 per eligible customer, Phase 167) and GSOP payments (Phase 147) are mandatory regulatory costs that flow directly into the company P&L. Bad debt write-offs (Phase 174/170) are also expensed here. A UK supplier with 30% bad debt (2022 crisis context) and high WHD obligation can be EBITDA-negative even on healthy gross margins. Ties together: billing revenue, wholesale hedge PnL (Ph179), marketing spend (Ph180), regulatory costs.

**9 new tests (2,720 total).**

---
### Phase 180 -- Sales and marketing budget tracker (2026-06-26)
**Files:** `company/crm/marketing_budget.py` (new), `tests/company/crm/test_marketing_budget.py` (new)

**What was built:**
- MarketingCategory enum: 7 categories (PCW commission, digital advertising, telesales commission, brand advertising, partner commission, retention outbound, referral reward).
- MarketingSpend frozen dataclass: cost_per_customer_gbp derived.
- AnnualMarketingBudget frozen dataclass: total_spent_gbp, budget_utilisation_pct, blended_cac_gbp, total_customers_acquired, summary() with by_category breakdown.
- MarketingBudgetTracker: set_budget(year), record_spend(), annual_budget(year), total_spend_all_years(), cac_by_category(year).

**Fidelity delta:** Marketing spend is a major cost line for UK suppliers. PCW commission is typically the largest single marketing cost at £50-70 per customer, while brand advertising drives zero directly-measurable acquisitions. Combined with channel_roi.py (Phase 175), a company can now track both the ROI it expects per channel and the actual spend/CAC it achieves. Budget utilisation tracks whether marketing headroom is being used efficiently.

**8 new tests (2,711 total).**

---
### Phase 179 -- Hedge performance tracker (2026-06-26)
**Files:** `company/market/hedge_performance.py` (new), `tests/company/market/test_hedge_performance.py` (new)

**What was built:**
- HedgeOutcome enum: PROFITABLE (hedge price < spot) / NEUTRAL (within 5%) / COSTLY (hedge price > spot).
- HedgeDelivery frozen dataclass: contracted_price, spot_price_at_delivery, price_differential, pnl_gbp, outcome, hedge_effectiveness_pct.
- HedgePerformanceBook: record_delivery(), total_pnl_gbp(year), profitable_trades(), costly_trades(), avg_effectiveness_pct(year), annual_summary(year).

**Fidelity delta:** The 2022 crisis separated survivors from victims purely on hedge effectiveness. An electricity forward at GBP80/MWh vs GBP200 spot = GBP120k saved per 1,000 MWh. Suppliers who hedged 70%+ at pre-crisis prices survived; those at <30% (converted to naked exposure by low margins) failed. This tracker is the company's view: it knows what prices it traded at (from trade blotter, Phase 131) and what spot delivered (from market data, observable). It does not need to read simulation internals.

**8 new tests (2,703 total).**

---
### Phase 178 -- Customer portfolio load forecast (2026-06-26)
**Files:** `company/market/load_forecast.py` (new), `tests/company/market/test_load_forecast.py` (new)

**What was built:**
- UK average consumption benchmarks: RESI elec 3,100 kWh, RESI gas 12,000 kWh, SME elec 25,000 kWh, IC elec 500,000 kWh.
- Seasonal factors: electricity Q1 1.18x, Q3 0.82x; gas Q1 1.55x, Q3 0.55x (gas has a 3:1 winter-to-summer ratio).
- SegmentLoadForecast frozen dataclass: per-segment quarterly and annual MWh, monthly_avg_mwh.
- PortfolioLoadForecast frozen dataclass: total_elec_mwh, total_gas_mwh, quarterly_elec/gas_mwh(), summary() dict.
- build_portfolio_forecast(year, resi_accounts, sme_accounts, ic_accounts, include_gas).

**Fidelity delta:** The trading desk needs to know what it must hedge from the company's own forecast built from account counts and market-standard consumption averages. Combined with Phase 177, a company-layer trading model can now say: "I forecast 5,000 MWh and have hedged 4,200 MWh = 84% covered = SHORT by 16%." Gas seasonality 3:1 winter:summer causes systematic over-hedging in summer and under-hedging in winter if ignored.

**9 new tests (2,695 total).**

---
### Phase 177 -- Customer portfolio energy position (2026-06-26)
**Files:** `company/market/portfolio_position.py` (new), `tests/company/market/test_portfolio_position.py` (new)

**What was built:**
- `PositionDirection` enum: SHORT (<95% hedged) / FLAT (95–105%) / LONG (>105%).
- `EnergyPosition` frozen dataclass: forecast_customer_load_mwh, hedged_mwh, hedge_ratio_pct, net_position_mwh, direction, is_within_policy.
- `PortfolioEnergyPosition` frozen dataclass: electricity + gas combined; is_fully_hedged (both FLAT), summary() dict.
- `compute_energy_position()`: factory computing hedge ratio from load/hedged volumes.
- ±5% flat tolerance — reflects standard 'hedge within 5% of volume' trading policy.

**Fidelity delta:** A real trading desk measures its position every day as (forecasted customer load) vs (hedged volume). Being 20% short when prices spike is exactly how real suppliers went insolvent in 2022. This is the company's observable view: it knows what it has hedged (from trades logged in the trade blotter, Phase 131) and what it forecasts customers will consume (from meter read patterns). It cannot see the simulation's hedge effectiveness calculation.

**9 new tests (2,686 total).**

---
### Phase 176 -- Invoice / billing dispute resolution (2026-06-26)
**Files:** `company/billing/billing_dispute.py` (new), `tests/company/billing/test_billing_dispute.py` (new)

**What was built:**
- `BillingDisputeType` enum: 7 types (wrong_tariff_applied, incorrect_unit_rate, missing_discount, duplicate_invoice, direct_debit_error, standing_charge_error, exit_fee_dispute).
- `BillingDisputeStatus` enum: OPEN / UNDER_REVIEW / RESOLVED_CREDIT / RESOLVED_NO_CHANGE / ESCALATED.
- `BillingDispute` frozen dataclass: is_open, days_to_resolution, credit_applied_gbp, closed_date.
- `BillingDisputeBook`: raise_dispute(), update_status(), resolve_with_credit(), resolve_no_change(), open_disputes(), disputes_for_customer(), total_credits_issued_gbp(), annual_summary() with avg_days_to_resolution.

**Fidelity delta:** Billing disputes are distinct from meter disputes (Phase 154). A wrong tariff applied after a switch is a billing error, not a meter read error; an exit fee dispute is contractual. UK suppliers must respond to all billing disputes within 8 weeks (SLC 2.7) or the customer gains automatic Ombudsman eligibility (Phase 155). Average days to resolution is an Ofgem-reported metric.

**8 new tests (2,677 total).**

---
### Phase 175 -- Acquisition channel ROI model (2026-06-26)
**Files:** `company/crm/channel_roi.py` (new), `tests/company/crm/test_channel_roi.py` (new)

**What was built:**
- `AcquisitionChannel` enum: 7 channels — PCW (MoneySupermarket/uSwitch), DIRECT_WEB, TELESALES, PARTNER_REFERRAL, SMART_METER_INSTALL, EXISTING_CUSTOMER_REFERRAL, OUTBOUND_RETENTION.
- `_BASE_CAC_GBP`: £12 (retention) to £90 (telesales); PCW £65.
- `_CHANNEL_CHURN_FACTOR`: PCW 1.45x (switcher behaviour); smart meter installs 0.70x (captive); referrals 0.65x (loyalty).
- `compute_channel_roi()`: DCF CLV model (same 10% discount rate as Phase 141), effective_churn = base × churn_factor, tenure = 1/churn, ROI = CLV / CAC.
- `ChannelROIResult` (frozen): all fields, is_profitable (roi ≥ 1.0).
- `channel_roi_ranking()`: sorted all-channel comparison.

**Fidelity delta:** PCW acquisition is the dominant source for UK domestic customers but delivers the lowest ROI — compare-site switchers churn at 1.45x average rate because they are by definition price-optimising. Smart meter installs produce the best ROI because the SMETS2 install creates a data relationship that reduces churn. A real CFO uses exactly this matrix to set acquisition budget allocations by channel.

**9 new tests (2,669 total).**

---
### Phase 174 -- Arrears escalation workflow (2026-06-26)
**Files:** `company/billing/arrears_book.py` (new), `tests/company/billing/test_arrears_book.py` (new)

**What was built:**
- `ArrearsStage` enum: 10 stages — CURRENT → DD_FAILED → FIRST_NOTICE → SECOND_NOTICE → PAYMENT_PLAN_OFFERED → PAYMENT_PLAN_ACCEPTED → PAYMENT_PLAN_DEFAULTED → REFERRED_TO_DEBT → WRITTEN_OFF + RESOLVED.
- `ArrearsCase` dataclass: arrears_amount, amount_recovered, outstanding_gbp, is_open, days_open; is_vulnerable flag; terminal stage guard (raises if advance attempted after resolution/write-off).
- `ArrearsBook`: open_case(), advance_stage(), record_recovery(), resolve(), write_off(), open_cases(), cases_for_customer(), cases_at_stage(), total_arrears_outstanding_gbp(), annual_summary() with by_stage counts.

**Fidelity delta:** UK energy debt enforcement has a legally mandated escalation sequence. The 2022 energy crisis saw UK households accumulate ~£3.9bn in arrears — more than double pre-crisis levels. Suppliers must follow SLC 27 (ability to pay) at each stage and cannot disconnect domestic customers (only PPM self-disconnection is indirect). This workflow is the counterpart to Phase 170 (voluntary deferral): involuntary arrears from DD failure escalating through the debt recovery chain.

**9 new tests (2,660 total).**

---
### Phase 173 -- Neighbourhood energy comparison (social proof) (2026-06-26)
**Files:** `company/crm/neighbourhood_comparison.py` (new), `tests/company/crm/test_neighbourhood_comparison.py` (new)

**What was built:**
- `ConsumptionRating` enum: MUCH_LOWER (≤-20%) / LOWER (≤-5%) / SIMILAR (≤+10%) / HIGHER (≤+30%) / MUCH_HIGHER (>+30%) — vs neighbourhood median.
- `NeighbourhoodComparison` frozen dataclass: customer_annual_kwh, neighbour_median_kwh, neighbour_efficient_kwh (top 20% efficiency), vs_median_pct, vs_efficient_pct, consumption_rating, potential_saving_kwh (if above efficient threshold), summary() dict.
- `build_neighbourhood_comparison()`: takes a list of comparable consumption figures, computes median (n//2 index) and efficient (n//5 index = top 20% quartile).

**Fidelity delta:** Social proof is one of the most cost-effective demand reduction tools. Real UK suppliers (OVO, Octopus) send monthly neighbour comparison reports that have been shown to reduce consumption 1-4%. The potential_saving_kwh is the actionable output: a customer using 40% more than efficient neighbours could save ~800 kWh/yr at £160 savings, which a supplier can use to trigger decarb recommendations (Phase 168) or TOU tariff offers.

**10 new tests (2,651 total).**

---
### Phase 172 -- Premises occupancy history register (2026-06-26)
**Files:** `company/crm/occupancy_register.py` (new), `tests/company/crm/test_occupancy_register.py` (new)

**What was built:**
- `TenancyEndReason` enum: MOVED_OUT / DECEASED / SWITCHED_SUPPLIER / EVICTED / VOID.
- `OccupancyPeriod` dataclass: mpan, customer_id, move_in_date, move_out_date, end_reason; is_current, duration_days.
- `PremisesOccupancyRegister`: record_move_in() (raises if MPAN already occupied), record_move_out(), current_occupant(mpan), occupancy_at_date(mpan, as_of) — point-in-time query, void_mpans(), history_for_mpan(), history_for_customer(), portfolio_summary().

**Fidelity delta:** Every meter point in the UK has a chain of occupants. When a customer moves out, the MPAN becomes void until a new customer is registered. Erroneous transfer disputes arise when the wrong customer is associated with an MPAN. The occupancy_at_date() method enables point-in-time attribution — e.g., who was responsible for energy at MPAN X on date Y — which underpins both billing resolution and COT investigation.

**9 new tests (2,641 total).**

---
### Phase 171 -- Customer conversation transcript model (2026-06-26)
**Files:** `company/crm/conversation_log.py` (new), `tests/company/crm/test_conversation_log.py` (new)

**What was built:**
- `ConversationOutcome` enum: RESOLVED / ESCALATED / PENDING_CALLBACK / ABANDONED / TRANSFERRED.
- `ConversationTurn` frozen dataclass: speaker (agent/customer), text, timestamp.
- `CustomerConversation` dataclass: channel, agent_id, started_at, turns list, add_turn(), close() with CSAT (1-5 validated) and NPS (0-10 validated), duration_seconds, is_open.
- `ConversationLog`: start(), get(), conversations_for_customer(), open_conversations(), avg_csat(), avg_nps(), resolution_rate(), annual_summary() with by_outcome counts.

**Fidelity delta:** Closes the human conversation simulation gap Rich asked about. A real supplier logs every customer interaction at this granularity — call centre recordings are transcribed, NPS surveys sent post-call. Combined with ContactLog (Phase 164) the CRM layer now has: metadata (channel/reason/handle time) AND the actual dialogue transcript with satisfaction scores. Resolution rate and NPS are key Ofgem-reported customer service metrics.

**9 new tests (2,632 total).**

---
### Phase 170 -- Payment deferral / holiday scheme (2026-06-26)
**Files:** `company/billing/payment_deferral.py` (new), `tests/company/billing/test_payment_deferral.py` (new)

**What was built:**
- `DeferralReason` enum: FINANCIAL_HARDSHIP / COVID_19 / JOB_LOSS / ILLNESS / BEREAVEMENT / BENEFIT_DELAY.
- `DeferralStatus` enum: ACTIVE / COMPLETED / DEFAULTED / CANCELLED.
- `PaymentDeferral` dataclass: deferred_amount, repayment_plan_monthly, outstanding_gbp, deferral_days, is_active; auto-completes when amount_repaid >= deferred_amount.
- `PaymentDeferralBook`: create(), record_repayment(), mark_defaulted(), cancel(), active_deferrals(), overdue_deferrals(as_of), deferrals_for_customer(), total_deferred_outstanding_gbp(), annual_summary() with by_reason counts.

**Fidelity delta:** Ofgem SLC 27A (Ability to Pay) requires suppliers to offer customers in payment difficulty a repayment plan proportionate to their means. During the 2022 energy crisis, £billions of deferred debt accumulated across UK supplier books — the Covid deferral reason alone covered 2020-21 when Ofgem mandated no-disconnection. Overdue deferrals list exposes credit risk for suppliers that granted holidays without follow-through.

**9 new tests (2,623 total).**

---
### Phase 169 -- Customer vulnerability register (2026-06-26)
**Files:** `company/crm/vulnerability_register.py` (new), `tests/company/crm/test_vulnerability_register.py` (new)

**What was built:**
- `VulnerabilityFlag` enum: 12 flags (medical_equipment, ppm_self_disconnected, serious_illness, mental_health, fuel_poverty, payment_difficulty, bereavement, elderly, disabled, child_dependent, job_loss, language_barrier).
- Severity weights: medical_equipment/PPM=5, illness/mental=4, fuel_poverty/payment/bereavement=3, elderly/disabled/child/job_loss=2, language=1.
- Required actions per flag: PSR, no_disconnect, debt_advice, ECO4/WHD referral, payment plan, bereavement handler, translation service.
- `VulnerabilityRecord` frozen dataclass: severity_score (sum of weights), required_actions (deduplicated), psr_required, no_disconnect_required.
- `VulnerabilityRegister`: register(), get(), update_flags(), remove(), psr_customers(), no_disconnect_customers(), high_severity(threshold=5), annual_summary() with flag_counts.

**Fidelity delta:** Ofgem SLC 31B requires suppliers to maintain a vulnerability register and ensure appropriate actions. The register synthesises signals from life events (Ph162), fuel poverty (Ph166), PPM self-disconnection (Ph145), PSR (Ph120/121) into a single per-customer severity score and required-action list. medical_equipment and PPM self-disconnection are the highest severity because disconnection means immediate physical danger or loss of energy in cold conditions.

**11 new tests (2,614 total).**

---
### Phase 168 -- Decarbonisation recommendation engine (2026-06-26)
**Files:** `company/crm/decarb_recommender.py` (new), `tests/company/crm/test_decarb_recommender.py` (new)

**What was built:**
- `Measure` enum: 9 measures (cavity/solid-wall/loft insulation, heat pump, solar PV, smart controls, double glazing, LED lighting, battery storage).
- `FundingScheme` enum: ECO4 / BUS (Boiler Upgrade Scheme, £7,500 grant) / SEG / GHG (Great British Insulation) / SELF_FUNDED.
- `MeasureRecommendation` frozen dataclass: estimated savings/cost, funding schemes tuple, priority, simple_payback_years.
- `DecarbonisationPlan` frozen dataclass: ordered recommendations, total_potential_savings_gbp, top_measure, summary().
- `recommend_measures()`: EPC F/G → insulation (cavity if terraced/semi/detached, solid wall otherwise); ECO4 eligible → zero-cost; EPC D+ + gas/oil boiler → heat pump (BUS); no solar → solar PV (SEG); always → smart controls.
- Connects to: Property (Ph161), FuelPovertyAssessment (Ph166), WHDRegister (Ph167), ECO4 tracker (Ph130).

**Fidelity delta:** UK net-zero mandates suppliers to help customers decarbonise. This closes the gap between knowing a customer is fuel-poor with an EPC F property (Ph161/166) and generating the actual measures they should receive. BUS, ECO4, GHG, and SEG funding chains are all represented. Payback years gives an advisory view suppliers can show customers.

**11 new tests (2,603 total).**

---
### Phase 167 -- Warm Home Discount (WHD) register (2026-06-26)
**Files:** `company/billing/whd_register.py` (new), `tests/company/billing/test_whd_register.py` (new)

**What was built:**
- `WHDEligibilityReason` enum: CORE_GROUP (pension credit, automatic) / BROADER_GROUP_LIHC / BROADER_GROUP_PSR / INDUSTRY_INITIATIVE.
- `WHDStatus` enum: ELIGIBLE / APPLIED / REBATED / INELIGIBLE.
- `WHDApplication` frozen dataclass; status derived from rebated_date.
- `WHDRegister`: apply() with duplicate-year guard, mark_rebated(), pending_rebates(), total_rebated_gbp(scheme_year), applications_for_customer(), annual_summary() with by_eligibility_reason breakdown.
- WHD_REBATE_GBP = £150 (Ofgem-mandated constant).

**Fidelity delta:** Every UK energy supplier above a customer threshold must participate in WHD. The £150 rebate appears on electricity bills, and suppliers must file annual returns to Ofgem. Connected to Phase 166 fuel_poverty: LIHC customers qualify for broader group, PSR + low income for broader group PSR track. Industry initiative track covers supplier discretion. Pending rebates list flags regulatory exposure if not paid before scheme deadline.

**11 new tests (2,592 total).**

---
### Phase 166 -- Fuel poverty income assessment (2026-06-26)
**Files:** `company/crm/fuel_poverty.py` (new), `tests/company/crm/test_fuel_poverty.py` (new)

**What was built:**
- `FuelPovertyBand` enum: NOT_FUEL_POOR / BORDERLINE (8–10%) / FUEL_POOR (>10%) / SEVERELY_FUEL_POOR (>20% of income on energy).
- `LIHCStatus` enum: NOT_LIHC / LIHC / LIHC_SEVERE — Low Income High Cost (post-2012 UK definition: income <60% median AND costs above median).
- `FuelPovertyAssessment` frozen dataclass: energy_spend_pct, fuel_poverty_band, lihc_status, is_fuel_poor, whd_eligible (LIHC → Warm Home Discount priority), eco4_priority.
- `assess_fuel_poverty(customer_id, income, energy_cost)`: factory function.
- Calibrated to UK medians: household income £34,963, energy cost £2,074/yr.

**Fidelity delta:** UK fuel poverty affects 14% of households. Suppliers must identify and prioritise fuel-poor customers for WHD rebates, ECO4 measures, and debt hardship provisions. Previously there was no income-based fuel poverty assessment — only the property-based proxy from Phase 161 (EPC F/G + tenure). Phase 166 closes this: the full UK fuel poverty assessment (both the 10%-of-income criterion and the LIHC criterion) is now computable from observable household data.

**10 new tests (2,581 total).**

---
### Phase 165 -- Customer energy profile: 360-degree view (2026-06-26)
**Files:** `company/crm/energy_profile.py` (new), `tests/company/crm/test_energy_profile.py` (new)

**What was built:**
- `CustomerEnergyProfile` frozen dataclass: composes a `Property` (Phase 161) with a `HouseholdBehaviourProfile` (Phase 163) into a single observable record per customer.
- Properties derived from composition: estimated_annual_elec/gas_kwh, is_fuel_poor, eco4_eligible, tou_candidate (medium/high sensitivity), heat_pump_candidate (gas boiler + EPC A–D), decarbonisation_priority_score (0–1 weighted by EPC/heat pump/solar gaps).
- summary() dict: all key fields for CRM dashboard display.

**Fidelity delta:** A real supplier's CRM "360 view" shows property efficiency, consumption profile, vulnerability flags, eligibility for programmes (ECO4, heat pump grants), and decarbonisation priority — all observable from the company's own data. This synthesises the premises/behaviour theme opened in Phase 161: property (161) + behaviour (163) + life events (162) + contacts (164) + 360 profile (165) form a coherent customer picture that drives product targeting, vulnerability triage, and compliance reporting.

**10 new tests (2,571 total).**

---
### Phase 164 -- Inbound contact and call centre interaction model (2026-06-26)
**Files:** `company/crm/contact_log.py` (new), `tests/company/crm/test_contact_log.py` (new)

**What was built:**
- `ContactChannel` enum: PHONE / WEBCHAT / EMAIL / LETTER / PORTAL.
- `ContactReason` enum: 12 reasons (billing_query, meter_read, payment_difficulty, complaint, debt_advice, bereavement, etc.).
- `ContactInteraction` dataclass: interaction_id, customer_id, channel, reason, contact_date, handle_minutes, resolved, escalated, notes.
- `ContactLog`: record() (auto avg_handle_minutes if not specified), contacts_for_customer(), avg_handle_minutes_for_reason(), annual_summary() with by_reason breakdown.
- Calibrated handle times: bereavement 25 min, complaint 18 min, debt advice 20 min, meter read 5 min.

**Fidelity delta:** Call centre cost is a major P&L line for UK suppliers — Ofgem regularly reviews cost-to-serve per contact. Previously there was no model of customer contact volume or reason mix. Phase 164 closes this: every inbound interaction is logged with channel, reason, handle time, and escalation flag, enabling cost-to-serve computation at interaction level and feeding into the company's annual reporting.

**9 new tests (2,561 total).**

---
### Phase 163 -- Household behaviour profile (2026-06-26)
**Files:** `company/crm/household_profile.py` (new), `tests/company/crm/test_household_profile.py` (new)

**What was built:**
- `HouseholdType` enum: 7 types (single/couple/family/retired/student/WFH).
- `HeatingSystem` enum: 7 heating types including heat pump and storage heater.
- `HouseholdBehaviourProfile` frozen dataclass: peak_load_factor (family=1.35×, retired=1.20×, student=0.75×); daytime_consumption_pct (retired=72%, student=40%; WFH days boost both); evening_consumption_pct (complement); tou_price_sensitivity (high/medium/low drives ToU tariff uptake); smart_meter_benefit_score (price-sensitive + evening-heavy households gain most); heat_pump_eligible.

**Fidelity delta:** Energy consumption patterns differ dramatically by household type — a retired couple at home all day has a very different half-hourly shape from a working single occupant. ToU tariff uptake and smart meter benefit also vary systematically. Previously all customers used the same profile shape regardless of household type. Phase 163 provides the behavioural layer that connects household demographics to consumption shape, ToU sensitivity, and decarbonisation eligibility.

**11 new tests (2,552 total).**

---
### Phase 162 -- Customer life events lifecycle (2026-06-26)
**Files:** `company/crm/life_events.py` (new), `tests/company/crm/test_life_events.py` (new)

**What was built:**
- `LifeEventType` enum: 11 events covering household changes, financial shocks, health events, and property moves.
- `LifeEvent` dataclass: customer_id, event_type, event_date, notes, occupancy_delta; trigger properties (triggers_vulnerability_review, triggers_occupancy_change, triggers_cot, triggers_psr_review).
- `LifeEventLog`: record(), events_for_customer(), pending_vulnerability_reviews(since), pending_cot_triggers(since), pending_psr_reviews(since), annual_summary() with by_type breakdown.

**Fidelity delta:** A customer's energy behaviour and risk profile change with life circumstances — job loss increases debt risk; retirement changes occupancy patterns; serious illness may require PSR registration; a move triggers COT. Previously customers were static profiles from first contract. Phase 162 closes this: life events now flow from customer record into the operational modules that need to respond (COT, PSR, vulnerability review, debt management). Opens the human behaviour simulation theme per Rich's direction.

**11 new tests (2,541 total).**

---
### Phase 161 -- Property model: premises attributes and consumption estimation (2026-06-26)
**Files:** `company/crm/property_model.py` (new), `tests/company/crm/test_property_model.py` (new)

**What was built:**
- `PropertyType` enum: DETACHED / SEMI_DETACHED / TERRACED / FLAT / BUNGALOW / MOBILE_HOME / COMMERCIAL.
- `TenureType` enum: OWNER_OCCUPIED / PRIVATE_RENTED / SOCIAL_RENTED / SHARED_OWNERSHIP.
- `EPCRating` enum: A–G.
- `Property` frozen dataclass: uprn, property_type, tenure, epc_rating, floor_area_m2, bedrooms, occupants, has_gas, has_solar_pv, electric_vehicle.
  - consumption_multiplier: A=0.60× through G=1.75× (relative to D-baseline).
  - estimated_annual_elec_kwh: area-scaled, occupant-adjusted, EV uplift +2500 kWh, solar offset −2000 kWh.
  - estimated_annual_gas_kwh: area-scaled; 0 if no_gas.
  - is_fuel_poor: EPC F/G + private/social rented tenure.
  - eco4_eligible: EPC D–G.
  - psr_priority_property: EPC F/G.

**Fidelity delta:** A real supplier holds property attributes (via EPC register, UPRN lookup) to estimate consumption, identify fuel-poor customers, and target ECO4 measures. Previously customers had no physical property context — consumption was assigned without any structural explanation. Phase 161 opens the premises simulation theme (Rich direction 07:35 UTC): property type and efficiency now drive consumption estimates, fuel poverty flags, and eligibility gates.

**12 new tests (2,530 total).**

---
### Phase 160 -- Smart Export Guarantee (SEG) tariff management (2026-06-26)
**Files:** `company/billing/smart_export.py` (new), `tests/company/billing/test_smart_export.py` (new)

**What was built:**
- `seg_rate_ppm(year)`: year-indexed export rates 2020–2025 (5.5p→7p→15p→12p→8.5p→7p; 2022 crisis peak).
- `seg_valid_rate(rate)`: enforces Ofgem SEG minimum (>0p, conventionally ≥1p).
- `SEGAccount`: record_export(year_month, kwh), payment_for_period(), total_export_kwh(), annual_summary().
- `SEGBook`: register() (rejects sub-minimum rates), record_export(), get_account(), portfolio_summary().

**Fidelity delta:** The Smart Export Guarantee (SEG), effective 1 January 2020, requires UK suppliers with >150k customers to offer export tariffs to solar/battery customers. Smaller suppliers may opt in. Previously all generation was uncompensated — solar PV customers received no export income. Phase 160 closes this: prosumer customers can register for SEG, record monthly export volumes, and receive payment. The 2022 crisis dynamic shows exports more than doubling in value (5.5p→15p/kWh).

**12 new tests (2,518 total).**

---
### Phase 159 -- Economy 7 off-peak tariff billing (2026-06-26)
**Files:** `company/billing/economy7.py` (new), `tests/company/billing/test_economy7.py` (new)

**What was built:**
- `TariffRegister` enum: DAY / NIGHT.
- `e7_unit_rate_ppm(year, register)`: year-indexed rates 2016–2025 for day and night registers.
- `E7MeterRead` frozen dataclass: customer_id, read_date, day_kwh, night_kwh; total_kwh, night_pct.
- `E7Bill` frozen dataclass: day_charge_gbp, night_charge_gbp, total_gbp, blended_rate_ppm.
- `generate_e7_bill(customer_id, period_start, period_end, day_kwh, night_kwh)`: factory using period year for rates.

**Fidelity delta:** Economy 7 is used by ~3 million UK households with storage heaters or immersion tanks. The dual-register meter (day/night) receives separate unit rates — the night rate is substantially cheaper to incentivise overnight use of cheap overnight grid electricity. Previously all billed customers used a single register. Phase 159 closes this: dual-register billing with year-indexed day/night rates, showing the crisis-era spike (34p day / 19p night in 2022 vs 12p / 6.5p in 2016).

**11 new tests (2,506 total).**

---
### Phase 158 -- Customer acquisition journey funnel (2026-06-26)
**Files:** `company/crm/acquisition_journey.py` (new), `tests/company/crm/test_acquisition_journey.py` (new)

**What was built:**
- `AcquisitionStage` enum: QUOTE_REQUESTED / APPLICATION_SUBMITTED / CREDIT_CHECK / CREDIT_APPROVED / CREDIT_DECLINED / SIGNED_UP / FIRST_BILL_SENT / ONBOARDED. Terminal stages: CREDIT_DECLINED, ONBOARDED.
- `AcquisitionJourney`: advance(stage, date), current_stage (latest by date), is_complete, converted, days_to_stage(stage).
- `AcquisitionFunnel`: start_journey(customer_id, channel, quote_date), advance(customer_id, stage, date), conversion_rate(from, to), drop_off_at(stage) (open journeys stalled at that stage), channel_summary() (total/converted/rate by channel).

**Fidelity delta:** A UK supplier tracks where prospects drop out of the acquisition funnel — quote-to-application, credit decline rate, sign-up-to-onboarding gaps all inform CAC and channel ROI. Previously customers appeared instantaneously in the registry at sign-up with no journey model. Phase 158 closes this: the full acquisition funnel is tracked from first quote through credit check, contract sign, and onboarding.

**12 new tests (2,495 total).**

---
### Phase 157 -- Microbusiness customer classification (2026-06-26)
**Files:** `company/crm/microbusiness.py` (new), `tests/company/crm/test_microbusiness.py` (new)

**What was built:**
- `MicrobusinessStatus` enum: MICRO / NON_MICRO / UNCLASSIFIED.
- `MicrobusinessProfile` frozen dataclass: customer_id, annual_elec_kwh, annual_gas_kwh, staff_count, annual_turnover_gbp, as_of_date; `status` property (all criteria must pass); `eligible_protections()` (5 Ofgem rights for micro customers).
- `classify_customer()`: factory function returning a MicrobusinessProfile.
- Thresholds: electricity <100 MWh/yr, gas <293 MWh/yr, staff ≤10, turnover ≤£2M. Any single breach → NON_MICRO.
- Unclassified if no consumption data provided.

**Fidelity delta:** Ofgem grants microbusinesses domestic-equivalent protections: 42-day notice on contract renewals, prohibition on rollover without consent, access to the Energy Ombudsman, and right to exit deemed contracts. Previously all SME customers were treated identically regardless of size. Phase 157 closes this: micro vs non-micro status is computed from observable attributes and drives which protections apply.

**12 new tests (2,483 total).**

---
### Phase 156 -- Tariff variation notice management (2026-06-26)
**Files:** `company/billing/tariff_variation.py` (new), `tests/company/billing/test_tariff_variation.py` (new)

**What was built:**
- `VariationReason` enum: PRICE_CAP_CHANGE / POLICY_COST_CHANGE / NETWORK_COST_CHANGE / TARIFF_RESTRUCTURE / COMMERCIAL_DECISION.
- `VariationOutcome` enum: PENDING / ACCEPTED / REJECTED_SWITCHED_AWAY / REJECTED_STAYED.
- `TariffVariation` dataclass: notice_period_days, is_adequate_notice() (>=30 days), has_no_exit_fee_window(as_of) (notice_sent ≤ as_of ≤ effective_date), rate_change_pct.
- `TariffVariationBook`: issue_notice(), record_response(), pending_variations(as_of), variations_for_customer(), inadequate_notice_violations() (compliance flag), annual_summary() (total/accepted/switched_away/violations).

**Fidelity delta:** Ofgem SLC 23.1 requires suppliers to give at least 30 days notice before changing a tariff unit rate for an existing customer. During the notice window the customer can switch away without an exit fee. Previously tariff changes were applied without any notice-period model. Phase 156 closes this: variation notices are issued, tracked through the notice window, and compliance violations are flagged.

**13 new tests (2,471 total).**

---
### Phase 155 -- Customer complaint management and Ombudsman escalation (2026-06-26)
**Files:** `company/crm/complaints.py` (new), `tests/company/crm/test_complaints.py` (new)

**What was built:**
- `ComplaintCategory` enum: BILLING / METERING / SUPPLY_INTERRUPTION / SWITCHING / CUSTOMER_SERVICE / DEBT_HANDLING / PPM / OTHER.
- `ComplaintStatus` enum: OPEN / UNDER_INVESTIGATION / RESOLVED / DEADLOCKED / ESCALATED_TO_OMBUDSMAN / OMBUDSMAN_CLOSED.
- `Complaint` dataclass: days_open(as_of), is_open, eligible_for_ombudsman (>=56 days open, not yet resolved/escalated).
- `ComplaintBook`: raise_complaint(), update_status(), resolve() (with optional redress_gbp), escalate_to_ombudsman() (gated: only if eligible), overdue_for_ombudsman(as_of), complaints_for_customer(), annual_summary() with by_category breakdown.

**Fidelity delta:** Ofgem SLC 2.7 requires suppliers to have a formal complaints process; any complaint unresolved after 8 weeks becomes eligible for the Energy Ombudsman. Previously complaints had no formal lifecycle. Phase 155 closes this: complaints are raised, investigated, resolved with redress, or escalated to the Ombudsman when the 56-day window expires.

**12 new tests (2,458 total).**

---
### Phase 154 -- Meter read dispute management (2026-06-26)
**Files:** `company/billing/meter_dispute.py` (new), `tests/company/billing/test_meter_dispute.py` (new)

**What was built:**
- `DisputeType` enum: ESTIMATED_READ / ACTUAL_TOO_HIGH / METER_FAULT / PRIOR_READING_ERROR.
- `DisputeStatus` enum: OPEN / UNDER_REVIEW / RESOLVED_ACCEPTED / RESOLVED_REJECTED.
- `MeterDispute` dataclass: dispute_id, customer_id, bill_reference, dispute_type, billed/claimed_read_kwh, opened_date, status, credit_applied_gbp; `disputed_kwh` property; `is_open` covers both OPEN and UNDER_REVIEW.
- `MeterDisputeBook`: open_dispute() (auto-increment ID), update_status(), resolve() (accepted/rejected, credit, notes), outstanding_disputes(), disputes_for_customer(), annual_summary() (total/accepted/rejected/outstanding/credit_gbp).

**Fidelity delta:** When a customer believes a meter read is wrong (estimated read, meter fault, prior error), UK suppliers must follow a formal dispute process that may result in a rebill and credit. Previously billing had no dispute resolution path — incorrect bills could not be formally contested or corrected. Phase 154 closes this: disputes are tracked from opening through review to resolution with credit application.

**12 new tests (2,446 total).**

---
### Phase 153 -- Fixed-term contract exit fee (2026-06-26)
**Files:** `company/billing/exit_fee.py` (new), `tests/company/billing/test_exit_fee.py` (new)

**What was built:**
- `ExitFeeWaiveReason` enum: WITHIN_NOTICE_PERIOD / CONTRACT_EXPIRED / SUPPLIER_BREACH / CUSTOMER_DEATH / PROPERTY_EMERGENCY.
- `ExitFeeResult` frozen dataclass: customer_id, contract_end_date, exit_date, days_remaining, fee_gbp, waived, waive_reason.
- `calculate_exit_fee(customer_id, contract_end_date, exit_date, annual_kwh, commodity, waive_reason=None)`: fee = days_remaining/365 × annual_kwh × rate_ppm / 100. Auto-waive within 42 days of end or if expired. Manual waive_reason overrides (death, emergency, breach).
- Rates: electricity 1.5p/kWh, gas 1.0p/kWh (typical UK market schedule).

**Fidelity delta:** Fixed-term tariff contracts include an Early Termination Charge (ETC) to compensate the supplier for forward-purchased energy that can no longer be recovered. Ofgem prohibits exit fees in the final 42 days (notice period) and after expiry. Previously there was no model for ETCs — switching (Phase 115) treated exits as cost-free. Phase 153 closes this: calculate_exit_fee() computes the ETC before a switch is processed, with auto-waive for the notice-period window.

**10 new tests (2,434 total).**

---
### Phase 152 -- Payment plan management (2026-06-26)
**Files:** `company/billing/payment_plan.py` (new), `tests/company/billing/test_payment_plan.py` (new)

**What was built:**
- `PaymentPlanStatus` enum: ACTIVE / COMPLETED / DEFAULTED / CANCELLED.
- `PaymentPlan` dataclass: plan_id, customer_id, original_debt_gbp, installment_gbp, start_date, status, payments_made, total_paid_gbp, missed_payments. Properties: expected_months (ceil), remaining_debt_gbp (max(0, original - paid)), is_complete.
- `PaymentPlanBook`: create_plan(), record_payment() (applies min(installment, remaining); completes plan when debt cleared), record_missed() (increments counter; defaults at threshold=2), cancel_plan(), active_plans(), defaulted_plans(), plans_for_customer(), portfolio_summary().
- Default threshold: 2 missed payments → DEFAULTED (industry standard trigger for PPM recommendation or debt sale).

**Fidelity delta:** UK suppliers must offer affordable repayment plans under Ofgem SLC 27A (Ability to Pay). A plan that defaults (≥2 missed payments) triggers escalation: PPM installation (if customer accepts) or referral to debt collector. Previously there was no model for structured repayment between debt incurrence and write-off. Phase 152 closes this: the full debt-management lifecycle is now modelled — arrears → referral (Phase 151) → payment plan (Phase 152) → PPM (Phase 145) or write-off.

**12 new tests (2,424 total).**

---
### Phase 151 -- Debt advice referral tracking (2026-06-26)
**Files:** `company/billing/debt_referral.py` (new), `tests/company/billing/test_debt_referral.py` (new)

**What was built:**
- `DebtAdviceOrg` enum: STEP_CHANGE / CITIZENS_ADVICE / NATIONAL_DEBTLINE / MONEY_ADVICE_SERVICE.
- `ReferralStatus` enum: REFERRED / ACCEPTED / DECLINED / COMPLETED / NO_RESPONSE.
- `DebtReferral` dataclass: referral_id, customer_id, total_debt_gbp, referral_date, org, status, response_date, outcome_notes. Property: is_resolved.
- `DebtReferralBook`: refer() (creates with default StepChange), update_status(), outstanding_referrals(), eligible_for_referral(debt, threshold=£200), referrals_for_customer(), annual_summary(year).
- `REFERRAL_THRESHOLD_GBP = 200.0` (Ofgem SLC 27A Ability to Pay threshold).

**Fidelity delta:** UK suppliers must refer domestic customers in significant arrears (≥£200) to free debt advice services under Ofgem SLC 27A (Ability to Pay condition). They must also track referral outcomes (accepted/declined/completed/no response) for Ofgem reporting. Previously bad debt was modelled as a percentage write-off but there was no referral process. Phase 151 closes this: the company can now trigger and track debt advice referrals, distinguishing the 2022 crisis surge (elevated referral rates) from normal years.

**11 new tests (2,412 total).**

---
### Phase 150 -- Priority Services Register (PSR) (2026-06-26)
**Files:** `company/crm/priority_services.py` (new), `tests/company/crm/test_priority_services.py` (new)

**What was built:**
- `PSRNeed` enum (10 types): LARGE_PRINT_BILLS, BRAILLE_BILLS, AUDIO_BILLS, ADVANCE_NOTICE, NOMINEE_BILLING, MEDICALLY_DEPENDENT, HEARING_IMPAIRED, VISUALLY_IMPAIRED, CHRONIC_ILLNESS, OTHER.
- `PSREntry` dataclass: customer_id, needs (list), added_date, review_due_date (365 days after registration), nominee_name, nominee_contact. Methods: is_due_for_review(), is_medically_dependent(), requires_nominee_contact().
- `PSRBook`: register(), update_needs(), is_registered(), get(), due_for_review(as_of), medically_dependent_customers() (DNO priority for power outages), nominee_contacts(), portfolio_summary() (total/medical_dep/with_nominee/need_breakdown).

**Fidelity delta:** All licensed UK energy suppliers must maintain a Priority Services Register (PSR) of customers with specialist needs. The PSR is distinct from the financial vulnerability register: it tracks service ACCESS needs (alternative bill formats, advance notice, nominee billing). Annual review is mandatory. MEDICALLY_DEPENDENT customers are shared with DNOs for priority restoration in power outages. Previously only financial vulnerability was modelled (ServiceLog Phase 69). Phase 150 closes this: the company now maintains a full PSR with annual review tracking.

**12 new tests (2,401 total).**

---
### Phase 149 -- Annual Energy Statement (AES) (2026-06-26)
**Files:** `company/billing/annual_statement.py` (new), `tests/company/billing/test_annual_statement.py` (new)

**What was built:**
- `AnnualStatement` frozen dataclass: customer_id, year, consumption_kwh, total_cost_gbp, effective_unit_rate_ppm, sc_ppd, tariff_name, tariff_type, prev_year_consumption_kwh, consumption_change_pct, market_avg_cost_gbp, estimated_saving_gbp.
- `AnnualStatementBook`: generate() (computes consumption_change_pct from prev year; estimated_saving = market_avg - actual; None if no market data), get(customer_id, year), statements_for_customer(), issued_for_year(year), overdue(as_of, all_customer_ids) (missing prior-year statements), summary(year).

**Fidelity delta:** Ofgem SLC 31B requires domestic suppliers to issue an Annual Energy Statement to every customer showing: annual consumption, total cost, effective unit rate, standing charge, comparison to previous year, and estimated saving from switching. This is a mandatory regulatory document that drives informed switching decisions in the UK market. Previously the company had no model for AES generation or compliance tracking. Phase 149 closes this: AnnualStatementBook generates and tracks AES across the portfolio, with overdue() identifying compliance gaps.

**12 new tests (2,389 total).**

---
### Phase 148 -- Annual Direct Debit Review (ADDR) (2026-06-26)
**Files:** `company/billing/dd_review.py` (new), `tests/company/billing/test_dd_review.py` (new)

**What was built:**
- `DDAction` enum: INCREASE / DECREASE / MAINTAIN.
- `DDReviewResult` frozen dataclass: customer_id, review_date, current_dd_gbp, actual_annual_spend_gbp, recommended_monthly_gbp, variance_pct, action.
- `review()`: computes ADDR outcome. Variance = (actual - implied_annual) / implied_annual * 100. ±5% threshold triggers action. Recommended monthly = ceiling-rounded annual/12.
- `DDReviewBook`: run_review() (records result), latest_review(customer_id), overdue_for_review(as_of, last_review_dates, months=12), summary() -> counts by action + avg_variance_pct.

**Fidelity delta:** Ofgem SLC 27B requires suppliers to review all domestic DD amounts at least annually and adjust if the payment materially diverges from expected spend. Persistent underpaying leads to accumulated debt (bad debt risk); overpaying leads to credit positions that must be refunded. Previously DD management (Phase 88/113) tracked mandate status but had no annual review cycle. Phase 148 closes this: the company can now run systematic ADDR across the portfolio and track compliance.

**12 new tests (2,377 total).**

---
### Phase 147 -- Guaranteed Standards of Performance (GSOPs) (2026-06-26)
**Files:** `company/regulatory/gsop.py` (new), `tests/company/regulatory/test_gsop.py` (new)

**What was built:**
- `GSOPType` enum: MISSED_APPOINTMENT / ERRONEOUS_TRANSFER / WRONGFUL_DISCONNECT / FINAL_BILL_DELAY / REFUND_DELAY.
- `GSOPPayment` dataclass: payment_id, customer_id, gsop_type, trigger_date, payment_due_date, amount_gbp, paid_date. Properties: is_paid, is_overdue(as_of).
- `GSOPBook`: record_trigger() (auto-calculates due_date via _add_working_days()), pay(), overdue(as_of), total_liability_gbp(year=None), annual_report(year) -> triggers/paid/auto_pay_rate_pct/overdue_count/by_type.
- `_add_working_days()`: advances n working days (Mon-Fri), used for payment deadlines.

**Fidelity delta:** UK suppliers must make automatic GSOP payments to domestic customers when service standards are missed. This is a statutory obligation — failure to auto-pay is itself a breach of SLC 2.7. Previously the company had no model for these mandatory compensation flows. Phase 147 closes this: GSOPBook tracks every trigger event, computes due dates by working-day window (10-20 days by type), and reports annual auto-pay compliance rate for Ofgem filing.

**12 new tests (2,365 total).**

---
### Phase 146 -- Change of Tenancy (COT) management (2026-06-26)
**Files:** `company/billing/cot.py` (new), `tests/company/billing/test_cot.py` (new)

**What was built:**
- `COTType` enum: MOVE_OUT / MOVE_IN.
- `COTEvent` dataclass: customer_id, meter_point, cot_type, date, meter_read_kwh, new_occupant_id.
- `COTBook`: record_move_out() (triggers void), record_move_in() (clears void), void_properties(), void_days(meter_point, as_of), overdue_for_nomination(as_of) (voids >28 days -> regulatory trigger to place on named SVT), portfolio_summary() (total_voids/avg_void_days/overdue_count), events_for(meter_point).
- `deemed_rate_gbp_per_kwh(date)`: SVT + 20% uplift, capped at Ofgem domestic price cap. 2022: 28p SVT -> 33.6p deemed (capped at 34p). 2019: 15.5p SVT -> capped at 16p.

**Fidelity delta:** ~3% of UK electricity meter points change occupancy each year. When a customer vacates, the property enters a "void" state -- the supplier must still meter it, bill "The Occupier" at deemed rates, and place it on a named SVT contract within 28 days. There was previously no model for this: customers persisted indefinitely at the same meter point. Phase 146 closes this: the company now tracks meter-point lifecycle from move-out through void period to new-occupant move-in.

**13 new tests (2,353 total).**

---
### Phase 145 -- Prepayment meter (PPM) management (2026-06-26)
**Files:** `company/billing/prepayment.py` (new), `tests/company/billing/test_prepayment.py` (new)

**What was built:**
- `PPMAccount` dataclass: customer_id, meter_id, balance_gbp, debt_gbp, emergency_credit_limit_gbp (GBP5 standard / GBP10 vulnerable), debt_recovery_rate (0.50 standard / 0.25 vulnerable), is_vulnerable. Properties: in_emergency_credit, emergency_credit_used_gbp, emergency_credit_remaining_gbp.
- `PPMBook`: register(), top_up() (debt recovery withheld first; remainder to balance; capped at outstanding debt), consume_daily() (deducts cost; triggers emergency credit draw when balance hits zero), is_friendly_hours() (Ofgem rule: no disconnect 10pm-6am or weekends), is_self_disconnected() (balance < -limit AND not friendly hours), portfolio_summary() (self_disconnected/in_emergency_credit/avg_balance/total_debt counts).
- `_is_friendly_hours()`: weekday 10pm-6am or weekend -> True.

**Fidelity delta:** ~4M UK residential customers are on prepayment meters. PPM was referenced as a recommended outcome in credit_scoring.py (HIGH_RISK -> PPM) and as a meter type in meter_assets.py, but no operational model existed. Phase 145 closes this: the company now models the full PPM lifecycle -- top-up debt recovery, emergency credit draw-down, and Ofgem-mandated friendly hours protection. The 2022 crisis is captured: at 3x pre-crisis unit rates, emergency credit exhausts in ~2 days vs ~2 weeks, directly modelling the self-disconnection surge that drove Ofgem's 2023 PPM installation rule changes.

**19 new tests (2,340 total).**

---
### Phase 144 -- Gas daily balancing and nomination model (2026-06-26)
**Files:** `company/market/gas_nominations.py` (new), `tests/company/market/test_gas_nominations.py` (new)

**What was built:**
- `DailyNomination` dataclass: date, gas_account_id, nominated_kwh, actual_kwh, nbp_spot_gbp_per_therm.
- `GasNominationBook`: nominate(), imbalance_kwh(), cash_out_cost_gbp() (short pays NBP spot; long receives 0.85x haircut credit), nomination_accuracy_pct() (% days within +-5% tolerance), monthly_cashout_gbp(), annual_cashout_gbp(), worst_imbalance_periods(n=5), balancing_summary().
- Short position cost: imbalance_kwh / 29.31 * nbp_spot_gbp_per_therm. 2022 crisis: 1,000 kWh short at GBP 3.50/therm = GBP 119 vs GBP 12 in 2016.

**Fidelity delta:** Every UK gas shipper must nominate daily gas quantities to Xoserve under UNC. Imbalance against nomination is settled at within-day NBP spot. This process drove multiple supplier failures in 2021-22 when NBP spot hit GBP 10/therm intraday. The current gas billing model calculates rates but never modeled procurement/balancing. Phase 144 closes this: the company now tracks nomination accuracy as a KPI and computes daily cash-out costs. Explains operationally why under-forecasting demand in a crisis is fatal.

**13 new tests (2,321 total).**

---
### Phase 143 -- Green tariff REGO compliance audit (2026-06-26)
**Files:** `company/compliance/green_claims_audit.py` (new), `tests/test_phase143_green_claims_audit.py` (new)

**What was built:**
- `GreenClaimsAuditResult` (dataclass): year, obligation_mwh, rego_held_mwh, coverage_pct, status (COMPLIANT / AT_RISK / NON_COMPLIANT), shortfall_mwh, green_products_active, penalty_estimate_gbp.
- `GreenClaimsAuditor`: `compute_obligation(product_consumption_kwh, date_str)` sums REGO obligations across all active green products with billed consumption; `audit(year, product_consumption_kwh)` runs the full check; `summary_lines()` returns annual report lines. Thresholds: COMPLIANT >=100%, AT_RISK 90-99%, NON_COMPLIANT <90%. Penalty: shortfall x £50/MWh.
- `portfolio_held_mwh()` includes both available and already-retired REGOs (both count toward compliance).

**Fidelity delta:** Ofgem enforces Fuel Mix Disclosure: suppliers marketing "100% renewable" products must hold REGOs equal to 100% of that supply. Phase 143 is the compliance gate that connects TariffCatalogue (Ph 142) to RegoPortfolio (Ph 139) -- the company can now verify REGO coverage before publishing green claims. Withdrawn products (e.g. IC_GREEN_CERT post-2023) correctly excluded from obligation after withdrawal date.

**13 new tests (2,320 total).**

---
### Phase 142 -- Green tariff product catalogue (2026-06-26)
**Files:** `company/billing/tariff_products.py` (new), `tests/company/billing/test_tariff_products.py` (new)

**What was built:**
- `TariffProduct` (frozen dataclass): code, name, commodity, segment, term, is_green, rego_required_pct, unit_rate_premium_pct, launch_date, withdrawal_date.
- `TariffCatalogue`: 9 realistic UK products spanning 2016-2025 (Standard Fix 1yr/2yr/Variable SVT, Green Fix 1yr/2yr, SME Fixed/Green, I&C Baseload/Green Certified). `active_products(date_str)` (launch/withdrawal window), `products_for_segment(segment)`, `green_products()`, `get_by_code(code)`, `rego_requirement_mwh(consumption_kwh, product_code)`, `summary()`.
- IC_GREEN_CERT withdrawn 2023-12-31 (REGO prices post-crisis made it uneconomic to offer); correctly excluded from active set.

**Fidelity delta:** UK energy suppliers maintain named tariff products on comparison sites (Ofgem, USwitch, MoneySuperMarket). Green products require REGO backing before making '100% renewable' claims under the Fuel Mix Disclosure Regulations 2005. `rego_requirement_mwh()` is the audit gate that feeds into `RegoPortfolio.coverage_check()` (Phase 139) before publishing marketing claims. Connects to renewal engine (Phase 136) -- product codes give named tariff options in renewal packs.

**20 new tests (2,307 total).**

### Phase 141 -- Customer lifetime value (CLV) calculator (2026-06-27)
**Files:** `company/crm/clv_calculator.py` (new), `tests/company/crm/test_clv_calculator.py` (new)

**What was built:**
- `compute_clv()`: DCF model using 10% discount rate and tenure = 1/churn_rate. CLV = annual_net_margin * ((1-(1+r)^-n)/r). Margin tiers: PREMIUM (>=200), STANDARD (50-200), LOW (0-50), NET_NEGATIVE (<0).
- `clv_to_cac_ratio()`: compares CLV to CAC (Phase 123). HEALTHY (>=3x) / MARGINAL (>=1.5x) / BREAK_EVEN (>=1x) / LOSS_MAKING.
- `portfolio_clv_summary()`: total/mean CLV, tier distribution.

**Fidelity delta:** CLV:CAC ratio is the primary metric for evaluating whether acquisition spend is justified. A ratio below 1.0 means the company loses money on every customer acquired through that channel. Connects to CAC model (Phase 123) and churn analytics (Phase 124) for a full customer economics picture.

**9 new tests (2,287 total).**

---
### Phase 140 -- MOA charge management (2026-06-27)
**Files:** `company/billing/moa_charges.py` (new), `tests/company/billing/test_moa_charges.py` (new)

**What was built:**
- `_MOA_ANNUAL_GBP`: rate schedule for 5 meter types (TRAD/PPM/SMETS1/SMETS2/AMR) at 2016/2018/2020/2022/2024 anchor points.
- `get_moa_annual_charge(meter_type, year)`: interpolated annual rate. `get_moa_daily_charge()`: daily pro-rated equivalent.
- `calculate_moa_charges(meter_points, year)`: returns `MoaInvoiceLine` per point (daily * days_in_period). `moa_portfolio_cost()` aggregates total.

**Fidelity delta:** MOA charges are a real supplier cost (~0.3-1.5p/kWh equivalent depending on meter type) that appears in every supplier P&L but is rarely modelled in energy market simulations. SMETS2 costs are materially higher than TRAD due to DCC (Data Communications Company) communications overhead.

**9 new tests (2,278 total).**

---
### Phase 139 -- REGO procurement and retirement (2026-06-27)
**Files:** `company/market/rego_portfolio.py` (new), `tests/company/market/test_rego_portfolio.py` (new)

**What was built:**
- `RegoPurchase`: purchase_id, scheme_year, mwh, price_per_mwh, generator, technology (wind_onshore/offshore/solar/hydro/biomass), retired flag. Computed: cost_gbp.
- `RegoPortfolio`: buy(), retire(), by_scheme_year(), retired_mwh(), available_mwh(), coverage_check() (shortfall vs consumption), by_technology(), summary().
- `get_rego_price(year)`: published market price 2016-2025 (2022 peak £6.50/MWh during crisis when renewable demand surged).

**Fidelity delta:** Ofgem's Fuel Mix Disclosure rules require REGOs to back any "100% renewable" claim. Shortfall means the claim cannot be substantiated. The coverage_check() function is the audit gate before publishing marketing claims. The 2022 REGO price spike (£6.50 vs £0.80 in 2016) is a hidden cost that caught some suppliers out during the energy crisis.

**10 new tests (2,269 total).**

---
### Phase 138 -- Forward curve anomaly detection (2026-06-27)
**Files:** `company/market/curve_monitor.py` (new), `tests/company/market/test_curve_monitor.py` (new)

**What was built:**
- `PricePoint` dataclass: period, price_gbp_mwh, commodity.
- `ForwardCurveMonitor(window=30)`: add() computes rolling z-score against window-1 prior points (excludes current from mean/std). Returns `AnomalyResult` once ≥10 data points available. Severity thresholds: normal <2.5σ, watch 2.5-3.5σ, alert 3.5-5.0σ, critical >5.0σ.
- `screen_series()`: batch process historical series; `summary()` counts by severity.

**Fidelity delta:** Market teams at UK suppliers use statistical anomaly detection on inbound price feeds to distinguish data errors from genuine market events. Critical alerts (>5σ) trigger automatic feed suspension and manual review before the price is used in trading or billing calculations.

**9 new tests (2,259 total).**

---
### Phase 137 -- Ofgem reporting obligations tracker (2026-06-27)
**Files:** `company/regulatory/ofgem_obligations.py` (new), `tests/company/regulatory/test_ofgem_obligations.py` (new)

**What was built:**
- 6 mandatory `ReportingObligation` entries: price_cap_compliance (monthly, SLC 21C, £250k max), billing_accuracy_audit (monthly, SLC 7, £100k), complaint_report (quarterly, SLC 14C, £500k), annual_business_report (annual, SLC 36D, £10M), smart_meter_progress (annual, SLC 22, £1M), debt_difficulty_report (annual, SLC 27, £500k).
- `ObligationSubmission`: submission vs deadline date, is_on_time, days_late.
- `OfgemObligationsTracker`: record_submission(), late_submissions(), on_time_rate_pct(), total_potential_penalty_gbp(), summary().

**Fidelity delta:** Ofgem conducts routine compliance monitoring across these SLCs and can issue enforcement orders or impose financial penalties for non-submission or late filing. total_potential_penalty_gbp() surfaces the financial exposure from outstanding late filings.

**9 new tests (2,250 total).**

---
### Phase 136 -- Renewal pricing engine (2026-06-27)
**Files:** `company/billing/renewal_engine.py` (new), `tests/company/billing/test_renewal_engine.py` (new)

**What was built:**
- `generate_renewal_pack()`: builds a `RenewalPack` with 3 quotes — fixed_1yr, fixed_2yr (+0.5p/kWh term premium), variable_svt (+2.5p/kWh risk premium). Unit rate = spot + segment margin (RESI 2.5p, SME 3.0p, IC 1.8p) + term premium.
- `RenewalPack`: quotes list, cheapest, recommended (default: fixed_1yr), days_to_expiry, spot_price_p_kwh.
- `RenewalQuote`: unit_rate, standing_charge, annual_est_cost_gbp, valid_until, recommended flag, term_label (human-readable).

**Fidelity delta:** Renewal offers are sent 42 days before fixed-term expiry (SLC 22A). The company prices from observable market data (price feed, Phase 76) not simulation internals. Customers who don't renew roll onto SVT. The renewal engine feeds the acquisition/churn analytics (Phase 124).

**9 new tests (2,241 total).**

---
### Phase 135 -- Customer credit scoring (2026-06-27)
**Files:** `company/crm/credit_scoring.py` (new), `tests/company/crm/test_credit_scoring.py` (new)

**What was built:**
- `assess_credit()`: derives credit tier from observable signals — dd_active, missed_payments, account_age_days, has_bad_debt_history, arrears_gbp. Score 0-100; PRIME ≥80, STANDARD ≥60, SUBPRIME ≥35, HIGH_RISK <35.
- `CreditAssessment` dataclass: tier, score, deposit_gbp (0/1/2× monthly bill est), ppm_recommended (HIGH_RISK only), flags (contributing signals), tier_label.

**Fidelity delta:** UK suppliers use credit scoring at onboarding to set deposit requirements and determine whether a PPM is appropriate. Scoring must be based on observable data only (not simulation internals). The SUBPRIME deposit (1× monthly bill) and HIGH_RISK deposit (2× monthly) align with Ofgem's guidance on credit checks for domestic customers.

**9 new tests (2,232 total).**

---
### Phase 134 -- Tariff change notification (TCN) management (2026-06-27)
**Files:** `company/billing/tariff_change_log.py` (new), `tests/company/billing/test_tariff_change_log.py` (new)

**What was built:**
- `TariffChangeNotice`: notice_id, change_type (svt_price_change/fixed_term_expiry/cap_reset/whd_change/other), notification_date, effective_date. Computed: notice_days, required_notice_days (30 SVT, 42 fixed term), is_compliant, rate_change_pct.
- `TariffChangeLog`: record(), for_customer(), non_compliant(), pending_effective(), by_change_type(), unacknowledged(), summary() with compliance_rate_pct.

**Fidelity delta:** Ofgem SLC 22 requires minimum notice periods for tariff changes. Non-compliance can result in fines up to 10% of annual turnover. The non_compliant() filter gates the compliance team's pre-change review.

**9 new tests (2,223 total).**

---
### Phase 133 -- DESNZ supplier data returns (2026-06-27)
**Files:** `company/regulatory/desnz_returns.py` (new), `tests/company/regulatory/test_desnz_returns.py` (new)

**What was built:**
- `SupplierDataReturn`: monthly SDR — customer counts by fuel/meter/tariff type, smart_meter_pct computed from total_customers (electricity + gas - dual_fuel).
- `FuelPovertyDeclaration`: annual estimate under LILEE (Low Income Low Energy Efficiency, England 2023+) definition with fuel_poverty_rate_pct.
- `CarbonIntensityReturn`: annual CO₂ g/kWh weighted by IPCC lifecycle emission factors (gas 490, coal 820, nuclear 12, renewable 15). renewable_pct accessor.
- `estimate_fuel_poor_customers()`: linear scaling from annual bill vs 10%-of-income threshold (£2,500 at £25k median income).

**Fidelity delta:** The SDR is submitted monthly to DESNZ for market monitoring. Fuel poverty declarations feed Ofgem's annual Supplier Performance Report. Carbon intensity is required for the Fuel Mix Disclosure Regulations 2005.

**9 new tests (2,214 total).**

---
### Phase 132 -- Counterparty credit limit management (2026-06-27)
**Files:** `company/trading/credit_limits.py` (new), `tests/company/trading/test_credit_limits.py` (new)

**What was built:**
- `CounterpartyLimit` dataclass: counterparty_id, name, credit_rating, limit_gbp, category (CCGT_generator/bank/aggregator/retail).
- `CounterpartyCreditManager`: set_limit(), update_exposure(), check_trade() (GREEN <70% / AMBER 70-90% / RED ≥90% / NO_LIMIT; RED and NO_LIMIT block trades), breached_limits(), summary().

**Fidelity delta:** Pre-trade credit checks are mandatory under ISDA/CSA master agreements used in wholesale energy trading. Most UK suppliers use a pre-trade screen against approved counterparty lists with rated limits. Trading above the limit requires risk committee sign-off. Phase 131 blotter + Phase 132 credit limits constitute the core trading control framework.

**9 new tests (2,205 total).**

---
### Phase 131 -- Wholesale trade blotter (2026-06-27)
**Files:** `company/trading/trade_blotter.py` (new), `tests/company/trading/test_trade_blotter.py` (new)

**What was built:**
- `TradeEntry` dataclass: trade_id, direction (buy/sell), commodity, volume_mwh, price_gbp_per_mwh, counterparty, delivery_period, desk, reported_to_remit. Computed: notional_gbp, is_remit_reportable.
- `TradeBlotter`: record(), get(), buys()/sells(), by_counterparty(), by_desk(), unreported_remit(), mark_reported(), net_position_mwh(), counterparty_exposure(), summary().

**Fidelity delta:** REMIT (Regulation on Energy Market Integrity and Transparency) requires reporting of all wholesale energy trades to ACER within 1 working day. unreported_remit() identifies trades breaching the reporting deadline. The blotter is also the primary record for counterparty credit exposure management.

**10 new tests (2,196 total).**

---
### Phase 130 -- ECO4 obligation tracker (2026-06-27)
**Files:** `company/regulatory/eco_tracker.py` (new), `tests/company/regulatory/test_eco_tracker.py` (new)

**What was built:**
- `EcoTracker(account_count, scheme_year)`: three-tier eligibility — exempt (<150k), contribution fee (150k-250k), direct delivery (>250k).
- `annual_obligation_twhd`: rate 0.042 TWhd/1k accounts. `record_measure()`, `delivered_twhd()` (verified only), `shortfall_twhd()`, `completion_pct()`, `status()` (EXEMPT/ON_TRACK/AT_RISK/BREACH).
- `measure_scores()`: catalogue of 9 ECO4 measure types with TWhd scores (cavity wall £95, ASHP £350, solid wall external £290 etc).

**Fidelity delta:** ECO4 (2022-2026) is a material cost obligation for large UK suppliers. Non-delivery triggers Ofgem enforcement action. The simulation's 18-customer book is too small to trigger the obligation, but the module gates correctly on the account count so it would activate as the book grows.

**10 new tests (2,186 total).**

---
### Phase 129 -- Customer notification preferences (2026-06-27)
**Files:** `company/crm/notification_prefs.py` (new), `tests/company/crm/test_notification_prefs.py` (new)

**What was built:**
- `CommPreference` dataclass: customer_id, channel (email/sms/post/phone/portal), pref_type (service/marketing/paper_bills), enabled, updated_date, source.
- `NotificationPreferences`: set(), get(), can_contact() with PECR-compliant defaults (service email/post always allowed if no explicit pref; marketing requires explicit opt-in), opted_out_marketing(), paper_bill_customers(), summary().

**Fidelity delta:** Ofgem SLC 14B requires a supplier to communicate with customers via at least one channel. PECR requires opt-in for electronic marketing. The module enforces both constraints via defaults and can_contact() validation.

**11 new tests (2,176 total).**

---
### Phase 128 -- Meter asset management (2026-06-27)
**Files:** `company/billing/meter_assets.py` (new), `tests/company/billing/test_meter_assets.py` (new)

**What was built:**
- `MeterAsset` dataclass: asset_id, customer_id, meter_type (SMETS1/SMETS2/TRAD/PPM/AMR), installed_date, manufacturer, serial_number, status. Computed: cert_due_date (type-specific 7-15yr periods), cert_overdue, cert_due_soon.
- `MeterAssetRegister`: register(), get(), for_customer(), operational(), faulty(), cert_overdue(), cert_due_soon(), by_type(), summary() with smart_pct.

**Fidelity delta:** UK suppliers must maintain a meter asset register per MOA (Meter Operator Agent) obligations. Certification periods are set by the relevant standards body (BS 5685 for traditional meters). Smart meter percentage is an Ofgem KPI (target 75%+ of domestic customers by 2025).

**9 new tests (2,165 total).**

---
### Phase 127 -- HH meter data quality checker (2026-06-27)
**Files:** `company/market/hh_data_quality.py` (new), `tests/company/market/test_hh_data_quality.py` (new)

**What was built:**
- `HHRecord` dataclass: period_id, kwh, data_type (actual/estimated/substituted), flag.
- `HHDataQualityChecker.check_record()`: negative consumption (error), zero actual read (warning), implausibly high vs EAC (warning), estimated (info), substituted (warning).
- `check_day(records)`: validates 48-period completeness; quality_ok=False if any errors; total_kwh, estimated_kwh, errors/warnings/infos counts.

**Fidelity delta:** BSCP505 (BSC Procedure for HH data quality) defines the quality flags that settlement agents must apply. HH data quality failures are the primary upstream cause of billing disputes — a quality_ok gate prevents billing on bad data.

**9 new tests (2,156 total).**

---
### Phase 126 -- Imbalance price risk model (2026-06-27)
**Files:** `company/market/imbalance.py` (new), `tests/company/market/test_imbalance.py` (new)

**What was built:**
- `compute_imbalance(period_id, metered_mwh, contracted_mwh, spot_price_gbp_mwh, stress)`: short (metered > contracted) charged at SSP = spot × 1.18 (normal) or spot × 2.2 (stress); long (metered < contracted) receives SBP = spot × 0.95; balanced = zero charge.
- `imbalance_summary(exposures)`: aggregates total charge, short/long/balanced period counts, net MWh per direction, cost/receipt flag.

**Fidelity delta:** Imbalance charges under the BSC (Balancing and Settlement Code) are the most dangerous P&L exposure for unsophisticated UK suppliers. SSP reached £9,999/MWh during 2021 stress events. The stress mode toggle models this tail risk explicitly.

**9 new tests (2,147 total).**

---
### Phase 125 -- Ofgem market benchmark data (2026-06-27)
**Files:** `company/market/market_report.py` (new), `tests/company/market/test_market_report.py` (new)

**What was built:**
- `_UK_AVG_ELEC_UNIT_RATE_P_KWH` 2016-2025 (13.6→22.3 p/kWh, crisis peak 34.0 in 2022).
- `_UK_AVG_GAS_UNIT_RATE_P_KWH` 2016-2025 (3.5→5.2 p/kWh, crisis peak 10.3 in 2022).
- `_UK_SWITCHING_RATE_PCT` 2016-2025 (17%→2.8% crisis crash→recovery to 13%).
- `market_benchmark(year)`, `compare_to_market(elec, gas, year)` — positioning (BELOW/AT/ABOVE_MARKET at ±3% threshold).

**Fidelity delta:** Ofgem's quarterly domestic market report is the standard reference for pricing benchmarking. The switching rate collapse in 2022 (2.8%) vs 2016 (17%) directly reflects the crisis — customers couldn't switch because there was nowhere cheaper to go.

**9 new tests (2,138 total).**

---
### Phase 124 -- Churn waterfall + reason code analysis (2026-06-27)
**Files:** `company/crm/churn_analytics.py` (new), `tests/company/crm/test_churn_analytics.py` (new)

**What was built:**
- `ChurnEvent`: customer_id, direction (gain/loss), year, reason (8 codes: price/service/moving_home/switching_broker/auto_renewal/going_green/consolidation/unknown), retention_attempted/succeeded flags.
- `ChurnWaterfall`: opening_book, gains, losses, closing_book, churn_rate, growth_rate.
- `ChurnAnalytics`: record(), losses_by_year/gains_by_year(), reason_breakdown() (sorted by count), retention_rate(), waterfall(), summary().

**Fidelity delta:** The churn waterfall is standard management reporting for UK energy suppliers. Reason codes allow the business to distinguish structural churn (price) from preventable churn (service) and lifecycle churn (moving home). Retention rate measures effectiveness of save-a-sale calls — a key KPI for customer management teams.

**10 new tests (2,129 total).**

---
### Phase 123 -- Customer Acquisition Cost (CAC) model (2026-06-27)
**Files:** `company/crm/acquisition_cost.py` (new), `tests/company/crm/test_acquisition_cost.py` (new)

**What was built:**
- `_CAC_BY_CHANNEL_YEAR` 2016-2025: PCW £45-72, direct £28-33, broker £140-200, referral £15-25, winback £35-42.
- `get_cac(channel, year)`, `cac_summary(year)` (all channels).
- `clv_vs_cac(annual_margin, tenure, channel, year)`: CLV = margin × tenure; ratio ≥3.0 = HEALTHY, ≥1.5 = MARGINAL, else LOSS_MAKING.

**Fidelity delta:** PCW fees have been a major source of pressure on small UK suppliers — the CMA found that PCW-acquired customers had shorter tenures and lower margins than direct-acquired customers, making PCW-heavy books structurally less viable.

**10 new tests (2,119 total).**

---
### Phase 122 -- Network Use of System (UoS) charges (2026-06-26)
**Files:** `company/market/network_charges.py` (new), `tests/company/market/test_network_charges.py` (new)

**What was built:**
- `_DUOS_PENCE_PER_KWH` 2016-2025: DUoS rates by segment (resi 2.1→3.5, SME 2.8→4.5, I&C 1.4→2.3 p/kWh). I&C lower due to direct connection; SME highest per kWh.
- `_TNUOS_PENCE_PER_KWH` 2016-2025: TNUoS residual charge (0.45→0.70 p/kWh).
- `get_duos_rate()`, `get_tnuos_rate()`, `network_cost_per_mwh()` (combined GBP/MWh), `annual_network_cost(year, segment, consumption_mwh)`.

**Fidelity delta:** DUoS/TNUoS are typically the largest non-commodity cost for UK suppliers after wholesale energy. Correct segment differentiation (I&C < resi < SME per kWh) is essential for accurate margin analysis and customer-level profitability.

**10 new tests (2,109 total).**

---
### Phase 121 -- Capacity Market obligation management (2026-06-26)
**Files:** `company/regulatory/capacity_market.py` (new), `tests/company/regulatory/test_capacity_market.py` (new)

**What was built:**
- `_CM_OBLIGATION_RATE_BY_YEAR` 2016-2025: NESO auction clearing prices (£0.77/kW in 2021 Covid year → £75/kW in 2022 crisis).
- `compute_cm_obligation(year, total_demand_mwh, firm_capacity_kw)`: derives obligation_kw from peak demand estimate (1.8x average x 0.92 de-rating), annual charge, DELIVERED/PARTIAL/FAILED delivery status, and penalty.
- `cm_charge_per_mwh(year, demand)`: pass-through cost per MWh.

**Fidelity delta:** The Capacity Market charge is a material and volatile cost for UK suppliers (visible in the 100x swing 2021→2022). Suppliers who failed to manage CM obligations during the crisis incurred significant penalties on top of their wholesale losses.

**10 new tests (2,099 total).**

---
### Phase 120 -- Wholesale risk limits + position governor (2026-06-26)
**Files:** `company/trading/risk_limits.py` (new), `tests/company/trading/test_risk_limits.py` (new)

**What was built:**
- `RiskLimit` dataclass: limit_name, value, unit, effective_year, set_by, notes.
- `RiskGovernor`: set_limit(), get_limit(), check() (OK/WARNING >80%/BREACH >=100%), check_all(current_values), governance_summary() with overall RAG, new_position_allowed().
- Standard limits: max_open_position_mwh, max_single_contract_mwh, var_limit_gbp, stop_loss_gbp.

**Fidelity delta:** Real energy trading desks operate under hard position limits set by the risk committee. The stop-loss trigger suspends new buying when MTM losses breach the limit — this is the mechanism that should have triggered earlier at suppliers who accumulated naked positions during 2021. This module provides that governance layer.

**11 new tests (2,089 total).**

---
### Phase 119 -- Standard Licence Condition (SLC) monitoring (2026-06-26)
**Files:** `company/regulatory/licence_monitor.py` (new), `tests/company/regulatory/test_licence_monitor.py` (new)

**What was built:**
- `SLCStatus` dataclass: slc_number, description, status (COMPLIANT/MONITOR/BREACH/NOT_ASSESSED), evidence, last_checked.
- `LicenceMonitor`: set_status(), get(), all_statuses(), breaches(), under_monitor(), catalogue(), compliance_summary() with RAG (GREEN/AMBER/RED).
- `_SLC_CATALOGUE`: 9 key SLCs (billing SLC 7, complaints SLC 14, price cap SLC 21C, smart meters SLC 22/27/27A, capital SLC 36, PSR SLC 47, SEG SLC 55).

**Fidelity delta:** UK suppliers hold an Ofgem Standard Licence with ~60 conditions. Non-compliance triggers enforcement action and potential licence revocation. This module provides the compliance skeleton — the RAG summary maps directly to what a compliance officer would report to the board.

**10 new tests (2,078 total).** CLAUDE.md trimmed 172→161 lines.

---
### Phase 118 -- DTN message log (2026-06-26)
**Files:** `company/market/dtn_log.py` (new), `tests/company/market/test_dtn_log.py` (new)

**What was built:**
- `DtnMessage` dataclass: flow_id, direction (inbound/outbound), timestamp, mpan_or_mprn, customer_id, status (received/processed/rejected/pending), flow_description property.
- `DtnLog`: record(), inbound(), outbound(), by_flow(), for_customer(), rejected(), summary() with by_flow Counter, known_flows().
- Known flows: D0001 (meter read), D0010 (EAC update), D0150 (registration), D0301Z (switch), D0052/D0055 (aggregation), D0205 (query); gas 806/814/816/826.

**Fidelity delta:** The DTN is the operational communications backbone for all UK energy market participants. Every meter read, switch request, EAC update, and registration arrives as a structured D-series message. This module gives the company observability into its market communications — essential for operational reconciliation.

**10 new tests (2,068 total).**

---
### Phase 117 -- Supplier of Last Resort (SoLR) risk assessment (2026-06-26)
**Files:** `company/regulatory/solr.py` (new), `tests/company/regulatory/test_solr.py` (new)

**What was built:**
- `solr_capital_requirement(transfer_size, treasury_gbp)`: BSC shortfall levy + bad debt risk vs treasury; SUSTAINABLE/MARGINAL/UNSUSTAINABLE status.
- `solr_revenue_upside(transfer_size)`: retained book (after 12% 3-month SVT churn) x SVT revenue per customer.
- `solr_scenario(scenario, treasury_gbp)`: named scenarios (small 5k / medium 50k / large 200k / bulb_scale 1.7M).
- Calibrated to 2021-22 energy crisis (28 supplier failures, ~£85/customer BSC levy).

**Fidelity delta:** SoLR is a board-level capital risk for UK suppliers. The 2021-22 crisis demonstrated that mid-sized suppliers can be forced to absorb books they cannot capitalise, triggering their own failure. This module quantifies that risk before appointment.

**10 new tests (2,058 total).**

---
### Phase 116 -- Energy theft / loss indicator (2026-06-26)
**Files:** `company/billing/theft_indicator.py` (new), `tests/company/billing/test_theft_indicator.py` (new)

**What was built:**
- `classify_anomaly(actual_kwh, eac_kwh)`: ok / watch (<65% EAC) / investigate (<40% EAC) / no_data.
- `screen_portfolio(customers_with_actuals)`: batch classification sorted by ratio, with aggregate counts.
- Investigate message explicitly flags Ofgem reporting duty.

**Fidelity delta:** Ofgem requires suppliers to report suspected energy theft (meter tampering). Consumption materially below EAC is the primary observable signal — this module provides the first-line screening that would trigger a field investigation.

**10 new tests (2,048 total).**

---
### Phase 115 -- Supplier switching request tracking (2026-06-26)
**Files:** `company/billing/switching.py` (new), `tests/company/billing/test_switching.py` (new)

**What was built:**
- `SwitchRequest` dataclass: reference, commodity, direction (gain/loss), submitted_date, transfer date, status (pending/completed/objected/withdrawn), objection_deadline (14 days), is_objectable.
- `SwitchingBook`: record(), complete(), object_to() (within window), withdraw(), pending_losses(), switching_summary() with net_completed.

**Fidelity delta:** Supplier switching via DTN is the primary churn mechanism for UK energy customers. The 10-working-day objection window (implemented as 14 calendar days) is the standard Ofgem/BSC framework — it gives the current supplier a retention window. Net_completed tracks portfolio growth/shrinkage from switching activity.

**11 new tests (2,038 total).**

---
### Phase 114 -- MPAN/MPRN meter point registry (2026-06-26)
**Files:** `company/billing/meter_points.py` (new), `tests/company/billing/test_meter_points.py` (new)

**What was built:**
- `MeterPoint` dataclass: customer_id, commodity, MPAN/MPRN, profile_class (1-8), GSP group, registered flag.
- `MeterPointRegistry`: register(), get()/electricity()/gas(), all_for_customer(), unregistered(), summary().
- `validate_mpan()` (13-digit regex), `validate_mprn()` (6-10 digit Xoserve format).
- `infer_profile_class()`: PC1=resi unrestricted, PC2=E7, PC3=SME, PC5=I&C HH.

**Fidelity delta:** Every UK supply point has a DNO-issued MPAN (electricity) or Xoserve-issued MPRN (gas). These are the primary identifiers in Elexon DTN and Xoserve switching/reconciliation flows. Profile class (embedded in MPAN structure) determines settlement treatment — critical for BSC compliance.

**17 new tests (2,027 total).**

---
### Phase 113 -- Direct Debit mandate management (2026-06-26)
**Files:** `company/billing/direct_debit.py` (new), `tests/company/billing/test_direct_debit.py` (new)

**What was built:**
- `DirectDebitMandate` dataclass: mandate reference, masked bank details, monthly amount, status, next collection date, failed attempts.
- `DDPaymentAttempt` dataclass: mandate_reference, outcome (collected/failed/cancelled), failure_reason.
- `DirectDebitBook`: create_mandate (28-day BACS cycle), record_attempt (2-strike suspension rule), cancel_mandate, reinstate_mandate, failed_mandates(), dd_summary().

**Fidelity delta:** UK energy suppliers use BACS Direct Debit as the primary recurring collection mechanism. Failed DDs are the primary upstream trigger of debt escalation. This completes the billing lifecycle: invoice → DD collection → failed DD → debt aging → bad debt.

**12 new tests (2,010 total).** CLAUDE.md trimmed 179→166 lines.

---
### Phase 112 -- Vulnerability register admin view (2026-06-26)
**Files:** `company/portal/app.py` (extended), `company/portal/templates/admin_vulnerability.html` (new), `company/portal/templates/admin.html` (extended), `tests/company/portal/test_admin_vulnerability.py` (new)

**What was built:**
- `GET /admin/vulnerability`: shows full vulnerability register (active + historical resolved), cross-referenced against WHD eligible customers, with a Contact button per row.
- Admin nav: Vulnerability link (amber-brown button).

**Fidelity delta:** UK suppliers are required to maintain a Priority Service Register (PSR) for vulnerable customers. This admin view provides the required operational view of the register.

**8 new tests (1,998 total).**

---
### Phase 111 -- Fuel mix disclosure (2026-06-26)
**Files:** `company/billing/fuel_mix.py` (new), `company/portal/app.py` (extended), `company/portal/templates/regulatory.html` (extended), `tests/company/billing/test_fuel_mix.py` (new)

**What was built:**
- `fuel_mix.py`: `_FUEL_MIX_BY_YEAR` 2016-2025 (DESNZ Fuel Mix Disclosure); `get_fuel_mix(year)` per-source percentages; `fuel_mix_summary(year)` with derived fields (low_carbon_pct, fossil_pct, renewable_trend, trend_direction).
- Regulatory dashboard: Fuel Mix Disclosure table with trend arrow.

**Fidelity delta:** UK suppliers are legally required to publish annual fuel mix under Ofgem Standard Licence Conditions (SLC). Regulatory page now meets this disclosure requirement.

**9 new tests (1,990 total).**

---
### Phase 110 -- Carbon footprint tracking (2026-06-26)
**Files:** `company/billing/carbon_footprint.py` (new), `company/portal/app.py` (extended), `company/portal/templates/consumption.html` (extended), `tests/company/billing/test_carbon_footprint.py` (new)

**What was built:**
- `electricity_intensity(year)`: DESNZ grid CO2e intensity 2016-2025 (266→115 gCO2e/kWh, -57%).
- `estimate_carbon(eac_kwh, commodity, year)`: annual CO2e in kg + tonnes for electricity/gas.
- `carbon_trend(eac_kwh, commodity, years)`: year-series for decarbonisation progress.
- Consumption portal: green footprint widget showing annual kg/tonnes CO2e + grid intensity.

**Fidelity delta:** UK suppliers must provide fuel mix and CO2 intensity data under Ofgem rules. Customers can now see their annual carbon footprint declining as the grid decarbonises — the same data British Gas, Octopus, and E.ON Next show in their apps.

**10 new tests (1,981 total).**

---
### Phase 109 -- Admin retention dashboard (2026-06-26)
**Files:** `company/portal/app.py` (extended), `company/portal/templates/admin_retention.html` (new), `company/portal/templates/admin.html` (extended), `tests/company/portal/test_admin_retention.py` (new)

**What was built:**
- `GET /admin/retention`: loads `portfolio_risk_summary()` across all customers, renders tier summary cards (HIGH/MEDIUM/LOW counts) and a sortable customer risk table (score, tier, signals).
- Admin nav: pink Retention button added.

**Fidelity delta:** Closes the loop from Phase 108's scoring engine to a management view. Ops teams can now prioritise retention outreach by risk tier.

**7 new tests (1,971 total).**

---
### Phase 108 -- Retention risk scoring (2026-06-26)
**Files:** `company/crm/retention_risk.py` (new), `tests/company/crm/test_retention_risk.py` (new)

**What was built:**
- `retention_risk(customer, invoices, contacts, renewal_info, rate_cmp)`: scores 0-5 from observable signals: overdue invoice (+2), recent complaint (+1), renewal notice window (+1), rate significantly above market (+1). Tier: LOW/MEDIUM/HIGH.
- `portfolio_risk_summary()`: aggregate tier counts for all customers.

**Fidelity delta:** UK suppliers run retention models to identify at-risk customers. This rule-based version uses only company-observable data (no SIM internals), mirroring what a real ops team would flag in their CRM.

**8 new tests (1,964 total).**

---
### Phase 107 -- Usage benchmarking (2026-06-26)
**Files:** `company/billing/usage_benchmark.py` (new), `company/portal/app.py` (extended), `company/portal/templates/consumption.html` (extended), `tests/company/billing/test_usage_benchmark.py` (new)

**What was built:**
- `_peer_group(customer, all_customers)`: peers = same home_type AND EPC band group (A-C=high, D-E=mid, F-G=low).
- `compute_percentile(value, peers)`: rank 0-100 (lower = more efficient).
- `usage_benchmark()`: returns peer_count, customer_eac, peer_median, percentile, rating, plain-text label.
- Consumption portal: colour-coded comparison widget (green=efficient, amber=heavy, blue=average).

**Fidelity delta:** Customers see how their usage compares to similar homes — the same feature used by major UK suppliers (British Gas Energy Monitor, EDF Smart Usage). Epistemically valid: all data from customer records, no SIM internals.

**10 new tests (1,956 total).**

---
### Phase 106 -- CSAT admin reporting (2026-06-26)
**Files:** `company/portal/app.py` (extended), `company/portal/templates/admin.html` (extended), `tests/company/portal/test_admin_csat.py` (new)

**What was built:**
- `_load_admin_data()` now includes `csat` dict from `_SERVICE_LOG.csat_summary()`.
- Admin overview: 5th summary card showing mean CSAT score and count of rated contacts.
- Shows `—` gracefully when no ratings exist.

**Fidelity delta:** Closes the CSAT feedback loop: per-interaction star ratings (Phase 105) now surface as an aggregate KPI for management in the admin overview.

**7 new tests (1,946 total).**

---
### Phase 105 -- CSAT score tracking (2026-06-26)
**Files:** `company/crm/service_log.py` (extended), `company/portal/app.py` (extended), `company/portal/templates/contact.html` (extended), `tests/company/crm/test_csat.py` (new)

**What was built:**
- `ServiceEvent.csat_score`: optional 1-5 INT field.
- Auto-migration: `ALTER TABLE ADD COLUMN csat_score` if missing (safe upgrade for existing DBs).
- `ServiceLog.csat_summary()`: count, mean score, promoter_pct (% rated 4-5 stars).
- `rate_contact(event_id, score)`: update score for a specific contact row.
- `latest_contact_id(customer_id)`: return most recent row ID for a customer.
- Contact portal: 5-star widget on success page; `POST /account/{id}/contact/rate` stores the score.

**Fidelity delta:** Suppliers measure CSAT per interaction to track service quality. The company now captures this data through the portal, enabling aggregate reporting.

**9 new tests (1,939 total).**

---
### Phase 104 -- Ombudsman referral tracking (2026-06-26)
**Files:** `company/crm/service_log.py` (extended), `company/portal/app.py` (extended), `company/portal/templates/admin_complaints.html` (extended), `company/portal/templates/regulatory.html` (extended), `tests/company/crm/test_ombudsman.py` (new)

**What was built:**
- `ServiceLog.ombudsman_eligible()`: complaints where `resolve_overdue=True` (unresolved >8 weeks).
- `ServiceLog.ombudsman_count()`: count of eligible cases.
- Admin/complaints: red alert box listing each case with deadlock letter + Ombudsman Services signposting.
- Regulatory dashboard: Ombudsman section — green confirmation if 0, red count with link if >0.

**Fidelity delta:** UK suppliers are legally required to issue a deadlock letter and signpost the Energy Ombudsman after 8 weeks. The company layer now tracks and surfaces this obligation.

**10 new tests (1,930 total).**

---
### Phase 103 -- Smart meter upgrade request flow (2026-06-26)
**Files:** `company/portal/app.py` (extended), `company/portal/templates/smart_meter.html` (new), `company/portal/templates/dashboard.html` (extended), `tests/company/portal/test_smart_meter.py` (new)

**What was built:**
- `GET /account/{id}/smart-meter`: if already HH, shows confirmation; if profile-class, shows upgrade request form.
- `POST /account/{id}/smart-meter`: records `ServiceEvent(contact_reason='smart_meter', outcome='upgrade_requested', agent_type='self_service')` in CRM. Shows success with reference number.
- Dashboard: prompt with link for non-HH customers.

**Fidelity delta:** Customers can request a smart meter through the self-service portal, which creates a traceable CRM record — exactly how UK suppliers like E.ON Next and Octopus handle upgrade requests.

**8 new tests (1,920 total).**

---
### Phase 102 -- Admin navigation hub (2026-06-26)
**Files:** `company/portal/templates/admin.html` (extended), `tests/company/portal/test_admin_nav.py` (new)

**What was built:**
- Admin overview page: quick-link buttons to all major staff views (Complaints, Collections, Renewals, Regulatory, Trading) in colour-coded pill style.
- All 22 portal routes reachable from /admin in ≤2 clicks.

**Fidelity delta:** Operational completeness — every admin sub-view now has a one-click entry point from the overview page.

**10 new tests (1,912 total).**

---
### Phase 101 -- EPC energy efficiency advice (2026-06-26)
**Files:** `company/billing/efficiency_advice.py` (new), `company/portal/app.py` (extended), `company/portal/templates/dashboard.html` (extended), `tests/company/billing/test_efficiency_advice.py` (new)

**What was built:**
- `efficiency_advice.py`: `epc_advice(rating)` — 3+ tailored tips per EPC band (A-G); `available_schemes(customer)` — maps EPC rating to applicable UK schemes (ECO4, GBIS, SEG, BUS, WHD, LAFE); `efficiency_summary(customer)` — combined dict including is_high_efficiency flag.
- Dashboard: collapsible `<details>` panel showing EPC band, tips, and available schemes.

**Fidelity delta:** Customers see EPC-tailored energy efficiency advice and applicable government schemes — the same guidance major UK suppliers like British Gas and E.ON Next provide through their portals.

**11 new tests (1,902 total).**

---
### Phase 100 -- Switching recommendation engine (2026-06-26)
**Files:** `company/pricing/switching_recommendation.py` (new), `company/portal/app.py` (extended), `company/portal/templates/dashboard.html` (extended), `tests/company/pricing/test_switching_recommendation.py` (new)

**What was built:**
- `switching_recommendation(customer, rate_cmp, as_of)`: synthesises:
  - Contract type (fixed/variable/SVT)
  - Days until renewal + notice window status
  - Protected/exposed vs current market (from rate_cmp)
  - Price cap applicability (domestic only)
  - → Returns `action` (switch/stay/consider_switching/not_applicable), `urgency` (high/medium/low/none), `reason` (plain English)
- Dashboard: tariff advice widget (red=switch now, green=stay, blue=consider).

**Fidelity delta:** The portal now gives customers personalised switching advice — the same kind of intelligence real UK suppliers provide through their digital channels. Synthesises 5 prior phases into a single actionable recommendation.

**11 new tests (1,891 total) — Phase 100 milestone.**

---
### Phase 99 -- Market rate comparison widget (2026-06-26)
**Files:** `company/market/rate_comparison.py` (new), `company/portal/app.py` (extended), `company/portal/templates/consumption.html` (extended), `tests/company/market/test_rate_comparison.py` (new)

**What was built:**
- `rate_comparison.py`: `market_rate_comparison()` — gets forward estimate from `PriceFeed` (£/MWh ÷ 10 = p/kWh, +5% risk premium); `_effective_rate_p_per_kwh()` derives contracted rate from most recent invoice (total_gbp/consumption_kwh×100). Returns delta, protected flag, and human-readable message.
- Consumption page: widget shown above cost forecast. Green if protected (locked in below market); amber/red if exposed.
- Returns `None` gracefully if feed unavailable or no invoice history.

**Fidelity delta:** Customers can now see whether their fixed contract is protecting them vs the forward market — the most impactful insight for customers deciding whether to switch or renew.

**8 new tests (1,880 total).**

---
### Phase 98 -- Admin upcoming renewals (2026-06-26)
**Files:** `company/portal/app.py` (extended), `company/portal/templates/admin_renewals.html` (new), `tests/company/portal/test_admin_renewals.py` (new)

**What was built:**
- `GET /admin/renewals`: iterates all customers, filters to those with `days_until_renewal() <= 90`; sorts by days remaining ascending (most urgent first).
- `admin_renewals.html`: urgency colour-coding: ≤14 days = red (urgent), ≤30 days = amber (notice window), ≤90 days = green.
- Account links to customer portal; handles empty state.

**Fidelity delta:** Retention team can now see which customers are approaching contract end and prioritise outreach. Customers in the ≤30-day notice window are flagged for proactive tariff comparison.

**8 new tests (1,872 total).**

---
### Phase 97 -- Annual cost forecast (2026-06-26)
**Files:** `company/billing/consumption_forecast.py` (new), `company/portal/app.py` (extended), `company/portal/templates/consumption.html` (extended), `tests/company/billing/test_consumption_forecast.py` (new)

**What was built:**
- `forecast_annual_cost(account_id, unit_rate_p, standing_charge_p, db)`: derives EAC from invoice history, projects annual cost = `(EAC × rate / 100) + (SC × 365 / 100)`. UK seasonal quarterly split: Q1=30%, Q2=22%, Q3=18%, Q4=30% (heating profile).
- Returns `None` if insufficient history (graceful fallback in template).
- Consumption page: green banner with annual estimate and quarterly breakdown.

**Fidelity delta:** Customers now see a forward-looking annual cost estimate — the key feature of every major UK supplier's online portal.

**8 new tests (1,864 total).**

---
### Phase 96 -- Collections queue (2026-06-26)
**Files:** `company/billing/collections.py` (new), `company/portal/app.py` (extended), `company/portal/templates/admin_collections.html` (new), `tests/company/billing/test_collections.py` (new)

**What was built:**
- `collections.py`: `get_overdue_invoices(db, as_of)` — queries invoices with `payment_status in ('unpaid','partially_paid')` and `due_date < today`. `get_collections_queue()` — aggregates per-customer (overdue count, total £, oldest due, max days overdue, tier). `_aging_tier()` — 0-30/30-60/60-90/90+ buckets.
- `GET /admin/collections`: collections queue sorted worst-first with tier colour-coding.

**Fidelity delta:** Admin staff can now see exactly which customers are overdue, by how much, and how long. Worst-case (90+ days) customers are highlighted in red — the natural next step is collections escalation or Ombudsman referral.

**10 new tests (1,856 total).**

---
### Phase 95 -- Contract renewal countdown (2026-06-26)
**Files:** `company/billing/contract.py` (new), `company/portal/app.py` (extended), `company/portal/templates/dashboard.html` (extended), `tests/company/billing/test_contract.py` (new)

**What was built:**
- `contract.py`: `contract_end_date(customer, as_of)` — advances acquisition date by term-year steps until past `as_of`; `days_until_renewal()`; `is_in_notice_window(window_days=30)`; `renewal_summary()`.
- `variable`/`svt`/`flex`/`hh` return `None` (rolling contract, no fixed end date).
- Dashboard: renewal date + days countdown shown for fixed-term customers; within 30-day window: amber alert with link to tariff comparison.

**Fidelity delta:** Customers can now see when their contract ends and take action. Fixed-term customers approaching renewal get a prompt to compare tariffs — mirroring real supplier retention workflows.

**11 new tests (1,846 total).**

---
### Phase 94 -- Complaint deadline tracker (2026-06-26)
**Files:** `company/crm/service_log.py` (extended), `company/portal/app.py` (extended), `company/portal/templates/admin_complaints.html` (new), `tests/company/crm/test_complaint_deadlines.py` (new)

**What was built:**
- `_add_working_days(start, n)`: module-level helper, skips Sat/Sun.
- `ServiceLog.complaint_deadlines()`: for every complaint event, computes `acknowledge_by` (contact + 2 working days), `resolve_by` (contact + 8 weeks), `resolved` flag, `ack_overdue` / `resolve_overdue` (vs today).
- `GET /admin/complaints`: table of all complaints with deadline dates and overdue highlighting.

**Fidelity delta:** Ofgem complaint SLAs now enforced in the portal. Staff can see at a glance which complaints are approaching or past deadline.

**10 new tests (1,835 total).**

---
### Phase 93 -- Warm Home Discount (WHD) (2026-06-26)
**Files:** `company/regulatory/warm_home_discount.py` (new), `company/portal/app.py` (extended), `company/portal/templates/regulatory.html` (extended), `company/portal/templates/dashboard.html` (extended), `tests/company/regulatory/test_warm_home_discount.py` (new)

**What was built:**
- `warm_home_discount.py`: `WHD_REBATE_BY_YEAR` 2017-2025 (real Ofgem amounts: £135-£150); `whd_eligible_customers(service_log)` from `vulnerability_register()`; `compute_whd_liability()`; `whd_summary()`.
- Regulatory dashboard: WHD scheme year, eligible count, rebate per customer, total WHD liability.
- Account dashboard: vulnerability badge shown if customer is in vulnerability register.

**Fidelity delta:** WHD scheme modelled as a real cost obligation. Vulnerable customers flagged in CRM automatically generate WHD liability in the regulatory view.

**11 new tests (1,825 total).**

---
### Phase 92 -- Peak/off-peak band overlay on HH consumption (2026-06-26)
**Files:** `company/portal/app.py` (extended), `company/portal/templates/consumption.html` (extended), `tests/company/portal/test_tou_band.py` (new)

**What was built:**
- `_tou_band(date_str, hour)` helper: weekends always Off-Peak; weekdays Peak 07:00-19:00 (product definition, not SIM internals).
- Consumption route: `is_tou = smart_meter OR metering==HH`; each `hh_data` record enriched with `band` field.
- `consumption.html`: Band column added to HH table; rows colour-coded (amber=Peak, blue=Off-Peak); peak/off-peak legend above table.

**Fidelity delta:** Destinationvision explicit test now met — C7 (HH smart meter customer) sees their half-hourly consumption with peak/off-peak pricing overlaid. The simulation stops being abstract.

**10 new tests (1,814 total).**

---
### Phase 91 -- CSS filing wired to persistent ServiceLog (2026-06-26)
**Files:** `company/portal/app.py` (extended), `company/portal/templates/regulatory.html` (extended), `tests/company/portal/test_portal_regulatory_css.py` (new)

**What was built:**
- `_load_regulatory_data()`: calls `generate_css_filing(_SERVICE_LOG.as_dicts(), css_year)` where `css_year = datetime.now().year`.
- Regulatory dashboard: new CSS Annual Filing table showing total contacts, complaints, resolution rate, target met (80%+), vulnerable customers contacted.
- CSS year is operational (current year), not simulation `latest_year` — portal contacts are real-time.

**Fidelity delta:** Portal→CRM→CSS regulatory filing loop fully closed. A customer complaint submitted via Contact Us form is immediately visible in the Regulatory dashboard's CSS Annual Filing.

**9 new tests (1,804 total).**

---
### Phase 90 -- Contact Us portal form (2026-06-26)
**Files:** `company/portal/app.py` (extended), `company/portal/templates/contact.html` (new), `company/portal/templates/dashboard.html` (nav), `tests/company/portal/test_portal_contact.py` (new)

**What was built:**
- `GET /contact`: displays contact form (reason dropdown, notes textarea, formal complaint checkbox).
- `POST /contact`: creates `ServiceEvent(channel='portal')` and records it in `_SERVICE_LOG` (persistent SQLite). Shows confirmation; notes Ofgem 8-week complaint response requirement.
- `_SERVICE_LOG` instantiated once at app startup with `DEFAULT_DB_PATH`.
- Dashboard nav: Contact Us link added.

**Fidelity delta:** Customer portal interactions now flow into the CRM service log. CSS filing can now have real complaint history: a customer submits a complaint via portal → ServiceEvent persisted → complaint_stats(year) returns real data → generate_css_filing() uses it.

**11 new tests (1,795 total).**

---
### Phase 89 -- ServiceLog SQLite persistence (2026-06-26)
**Files:** `company/crm/service_log.py` (rewritten), `tests/company/crm/test_service_log_persistent.py` (new)

**What was built:**
- `ServiceLog(db_path=None)`: in-memory SQLite (`:memory:`) — ephemeral, independent per instance, backwards-compatible with all existing tests.
- `ServiceLog(db_path=Path(...))`: file-backed SQLite — events/complaints/vulnerabilities persist across restarts.
- Persistent connection held on instance to avoid `:memory:` isolation issue (each `sqlite3.connect(':memory:')` is a fresh empty DB).
- All 12 prior CRM tests pass unchanged. `DEFAULT_DB_PATH = company/data/service_log.db`.

**Fidelity delta:** CRM data now persists between simulation runs. CSS filing (`generate_css_filing()`) can be passed a persistent ServiceLog with real complaint history rather than empty in-memory data.

**8 new tests (1,784 total).**

---
### Phase 88 -- Direct Debit Mandate (2026-06-26)
**Files:** `company/billing/direct_debit.py` (new), `company/portal/app.py` (extended), `company/portal/templates/direct_debit.html` (new), `company/portal/templates/dashboard.html` (nav), `tests/company/billing/test_direct_debit.py` (new), `tests/company/portal/test_portal_dd.py` (new)

**What was built:**
- `DDMandate` dataclass; SQLite schema at `company/data/direct_debit.db`.
- `set_mandate()` (UPSERT), `get_mandate()`, `cancel_mandate()` (soft-delete), `is_dd_customer()`, `list_mandates()`. Payment day validated 1-28.
- Portal: GET `/account/{id}/direct-debit` (shows active mandate or setup form); POST saves mandate; POST `/cancel` deactivates. Success/cancelled banners.
- Dashboard nav: Direct Debit link added.

**Fidelity delta:** A real UK energy supplier stores DD mandates and uses them to determine collection vs manual payment. The portal now supports the full DD lifecycle: setup, view, cancel.

**21 new tests (1,776 total).**

---
### Phase 87 -- EAC Calibration from billing history (2026-06-26)
**Files:** `company/billing/eac_calibration.py` (new), `company/portal/app.py` (extended), `company/portal/templates/consumption.html` (EAC section), `tests/company/billing/test_eac_calibration.py` (new)

**What was built:**
- `calibrate_eac(account_id, db_path, lookback_years=2)`: sums consumption_kwh from invoices in lookback window, annualises by days covered. Returns None if no data.
- `calibrate_all_customers()`: batch calibration; `eac_drift()`: drift_pct + direction (up/down/flat, 0.5% deadband).
- Consumption portal: calibrated EAC vs original shown with colour-coded drift indicator.

**Fidelity delta:** UK suppliers recalibrate EAC annually from meter reads. After 10 years of demand response and weather effects, the portal now shows how far actual consumption drifted from acquisition EAC — the signal a real supplier uses to reprice renewals.

**12 new tests (1,755 total).**

---
### Phase 86 -- Account Statement (print-ready) (2026-06-26)
**Files:** `company/portal/app.py` (extended), `company/portal/templates/statement.html` (new), `company/portal/templates/bills.html` (nav updated), `company/portal/templates/dashboard.html` (nav updated), `tests/company/portal/test_portal_statement.py` (new)

**What was built:**
- `GET /account/{id}/statement`: renders full invoice history + balance summary (billed, paid, bad debt, outstanding). Print-optimised via `@media print` CSS (hides nav).
- `statement.html`: invoice table + summary section with account balance breakdown.
- Dashboard + bills nav: Statement link added.
- No new modules — reads from existing invoice DB via `invoices_for_account()`.

**Fidelity delta:** A customer or account manager can now open /statement and get a printable snapshot of the full billing relationship — the kind of document a real supplier produces on request.

**11 new tests (1,743 total).**

---
### Phase 85 -- Admin Portfolio Overview (2026-06-26)
**Files:** `company/portal/app.py` (extended), `company/portal/templates/admin.html` (new), `tests/company/portal/test_portal_admin.py` (new)

**What was built:**
- `_load_admin_data()`: aggregates per-customer invoice summary (outstanding, paid, invoice count) + smart meter flag + portfolio totals (billed, paid, outstanding, bad debt).
- `GET /admin`: Admin Overview dashboard listing all customers with segment, commodity, EAC, smart meter status, and financial summary. Summary cards for top-level metrics.
- `admin.html`: responsive grid summary cards + full customer table with account links.

**Fidelity delta:** An MD or operations manager can now open /admin and see the full book — all 18+ customers, their payment status, and portfolio-wide financial exposure — without logging in as each individual customer.

**11 new tests (1,732 total).**

---
### Phase 84 -- Regulatory Compliance Dashboard (2026-06-26)
**Files:** `company/portal/app.py` (extended), `company/portal/templates/regulatory.html` (new), `company/portal/templates/dashboard.html` (nav link added), `tests/company/portal/test_portal_regulatory.py` (new)

**What was built:**
- `_load_regulatory_data()`: computes smart meter penetration from customer DB (count smart_meter=True / HH metered resi), MCR solvency from run output treasury + customer count, Ofgem annual turnover fee.
- `GET /regulatory`: Regulatory Compliance Dashboard route — smart meter compliance (COMPLIANT/AT_RISK/BREACH badge), MCR capital adequacy (OK/Watch/STRESS badge), annual fee table.
- `regulatory.html`: three sections — Smart Meter Rollout, Capital Adequacy, Annual Fees.
- Dashboard nav: Regulatory link added.
- Uses company.regulatory.compliance + saas.capital.solvency; no simulation internals.

**Fidelity delta:** Rich can now click Regulatory from the portal and see compliance status for both smart meter mandate and capital adequacy — the same view an MD would check before a quarterly board report.

**13 new tests (1,721 total).**

---
### Phase 83 -- Portal payment submission (2026-06-26)
**Files:** `company/portal/app.py` (extended), `company/portal/templates/payment_confirm.html` (new), `company/portal/templates/bills.html` (updated), `company/billing/invoice.py` (get_invoice: create_schema added), `tests/company/portal/test_portal_payment.py` (new)

**What was built:**
- `POST /account/{id}/pay`: accepts invoice_number + amount_gbp from form; looks up invoice; calls `reconcile_payment()`; returns confirmation page.
- `payment_confirm.html`: shows paid/partially_paid/no_match with invoice detail and return link.
- `bills.html`: "Pay £X.XX" button on each unpaid/partially_paid invoice row.
- `get_invoice()`: now calls `create_schema()` to ensure schema exists before querying.
- Customer journey complete: login → dashboard → bills → **pay** → confirmation.

**Fidelity delta:** A customer logged in to the portal can now submit a payment against an outstanding invoice and see the reconciliation result — closing the billing lifecycle within the portal (bill issued → customer pays → status updated).

**12 new tests (1,708 total).**

---
### Phase 82 -- HH consumption feed + portal half-hourly view (2026-06-26)
**Files:** `simulation/publish_consumption_data.py` (new), `company/billing/hh_consumption.py` (new), `company/portal/app.py` (extended), `company/portal/templates/consumption.html` (extended), `background/process_run_complete.py` (extended), `docs/market_data/consumption_feed.json` (created), `tests/company/portal/test_hh_consumption_feed.py` (new)

**What was built:**
- `read_hh_data(customer_id, n_days=2)`: reads C7/C8/C9 half-hourly profiles from `sim/hh_data/{id}.csv` (48 periods/day × n_days).
- `publish_consumption(hh_customers, output_path)`: writes `docs/market_data/consumption_feed.json` — 288 records (3 customers × 2 days × 48 periods).
- `process_run_complete.py`: calls `publish_consumption()` after each sim run.
- `company/billing/hh_consumption.py`: `get_hh_consumption()` + `recent_hh_periods()` — reads feed, no SIM imports.
- Portal consumption route: if HH customer + feed available, passes last 48 periods to template.
- `consumption.html`: HH table (date / period / time / kWh) for C7-C9; graceful if feed absent.

**Fidelity delta:** When Rich logs in as C7 and navigates to Consumption, they now see a half-hourly table showing real consumption patterns (e.g. morning peak at 07:00, evening peak at 18:30). This is the Destinationvision's "key test" — the simulation stops being abstract.

**13 new tests (1,696 total).**

---
### Phase 81 -- Trading desk: live spot prices from M3 feed (2026-06-26)
**Files:** `company/portal/app.py` (extended), `company/portal/templates/trading.html` (extended), `tests/company/portal/test_trading_spot_feed.py` (new)

**What was built:**
- `_load_spot_prices()`: reads from `PriceFeed(_PRICE_FEED_PATH)`; returns elec/gas spot + forward estimates; empty dict if feed unavailable.
- Trading route now passes `{"data": ..., "spot": _load_spot_prices()}` to template.
- `trading.html`: Market Data Feed section shows elec/gas spot + forward price estimate; stale-feed warning if >24h old; gracefully omitted if feed unavailable.

**Fidelity delta:** The trading desk now shows live market prices from the M3 feed alongside hedge portfolio performance. A trader logging in sees today's spot (£100.58/MWh elec, £32.79/MWh gas) and 5% risk-premium forward estimates alongside 10-year P&L history. This completes the M3 end-to-end loop: SIM writes → feed file → company reads → trading desk displays.

**8 new tests (1,683 total).**

---
### Phase 80 -- M3 price feed live: publish on every sim run (2026-06-26)
**Files:** `simulation/publish_market_feed.py` (new), `background/process_run_complete.py` (extended), `tests/simulation/test_publish_market_feed.py` (new), `docs/market_data/price_feed.json` (created)

**What was built:**
- `build_feed_prices(n_elec_periods=48, n_gas_days=10)`: extracts last 24h of Elexon SSP half-hourly prices + last 10 days of NBP gas daily prices from SIM data sources.
- `publish(output_path)`: calls `build_feed_prices()` then `publish_feed()` from the company's market interface.
- `process_run_complete.py`: calls `publish()` after report generation on every sim run.
- `docs/market_data/price_feed.json`: live feed now populated (48 electricity + 10 gas records, latest elec £100.58/MWh from 2025-06-07).

**Fidelity delta:** Phase 76 defined the M3 market data seam but `publish_feed()` was never called — the feed file didn't exist and `PriceFeed.is_available()` returned False. Phase 80 closes this gap: the M3 interface is now truly live. Every simulation run updates the price feed. The company's `PriceFeed` can now read current spot prices without any SIM imports.

**11 new tests (1,675 total).**

---
### Phase 79 -- Portal: Consumption history page (2026-06-26)
**Files:** `company/billing/consumption.py` (new), `company/portal/app.py` (extended),
`company/portal/templates/consumption.html` (new), `company/portal/templates/dashboard.html`
(minor: nav link), `tests/company/portal/test_consumption.py` (new)

**What was built:**
- `consumption_history(account_id, db_path)`: reads per-invoice kWh from invoice DB, returns list with year/month fields.
- `monthly_totals(records)`: aggregates by (year, month), sorted chronologically.
- Portal GET `/account/{id}/consumption`: reads consumption history, detects HH customers via `metering=="HH"`, renders table.
- `consumption.html`: monthly table; HH smart meter banner ("half-hourly resolution available"); nav links to dashboard/bills/tariff-compare.
- Dashboard nav: added Consumption link.

**Fidelity delta:** The Destinationvision Portal MVP requirement is now complete. C7/C8/C9 customers (HH metered, `metering=="HH"`) see a smart meter banner when viewing their consumption. The customer journey is: login → dashboard → bills → consumption history → tariff comparison → switch tariff. When Rich logs in as C7, the portal now shows all five views.

**11 new tests (1,664 total).**

---
### Phase 78 -- Year-indexed non-commodity billing rates (2026-06-26)
**Files:** `saas/non_commodity.py` (extended), `saas/bill_generator.py` (extended), `tests/saas/test_non_commodity_year_indexed.py` (new)

**What was built:**
- `_NON_COMMODITY_ELEC_RESI_BY_YEAR`: year-indexed electricity non-commodity rate 2016–2024 (resi), from Ofgem Retail Market Monitoring / Cornwall Insight data.
- `_NON_COMMODITY_GAS_RESI_BY_YEAR`: year-indexed gas non-commodity rate 2016–2024 (resi).
- SME multipliers: 0.77 (elec), 0.80 (gas) applied to resi base rate.
- `non_commodity_rate(commodity, segment, year=None)`: accepts optional `year`; returns year-indexed rate when provided, falls back to flat 2019 baseline for backward compat.
- `bill_generator.generate_bill()`: extracts billing year from `dates[0]` and passes to `non_commodity_rate`.

**Fidelity delta:** Customer bills now reflect actual UK network charge evolution 2016–2024. In 2022, resi electricity non-commodity rises from the flat £55/MWh baseline to £73/MWh — correctly capturing the DUoS/TNUoS spike during the energy crisis. Gas non-commodity rises from £10 to £15/MWh. This closes the explicit gap flagged in Section 9: "flat pass-through in non_commodity.py rather than year-indexed actuals."

**14 new tests (1,653 total).**

---
### Phase 77 -- Portal Phase 2: Tariff Comparison (2026-06-26)
**Files:** `company/pricing/tariff_comparison.py` (new), `company/portal/app.py` (extended), `company/portal/templates/tariff_compare.html` (new), `company/portal/templates/tariff_switch_confirm.html` (new), `tests/company/pricing/test_tariff_comparison.py` (new), `tests/company/portal/test_tariff_compare.py` (new)

**What was built:**
- `unit_rate_from_forward(forward_gbp_mwh, markup_pct, vat_rate)`: converts observable forward price to customer unit rate in p/kWh (inc VAT).
- `annual_cost_gbp(unit_rate_p, sc_p, eac_kwh)`: estimated annual cost from unit rate + standing charge.
- `compare_tariffs(eac_kwh, sim_interface, as_of_date, segment)`: returns 3 options (Fixed 1yr, Fixed 2yr, Variable SVT) sorted cheapest first. Segment-aware: I&C has no standing charge, domestic uses published Ofgem rate.
- Portal GET `/account/{id}/tariff-compare`: renders comparison table with switch buttons.
- Portal POST `/account/{id}/switch-tariff`: logs request, generates SW- reference, renders confirmation.

**Fidelity delta:** Rich can now log in as C1 and see competing tariff options with estimated annual costs, then request a tariff switch. The portal now completes the customer journey from bill review to renewal decision. This is the most user-visible demonstration that the company is real.

**17 new tests (1,639 total).**

---
### Phase 76 -- M3 Market Data Feed (2026-06-26)
**Files:** `company/market/price_feed.py` (new), `tests/company/market/test_price_feed.py` (new)

**What was built:**
- `SpotPrice` frozen dataclass: fuel, period, price_gbp_per_mwh.
- `PriceFeed(feed_path)`: reads from published JSON feed file only — zero SIM module imports.
  - `is_available()`: checks feed file exists.
  - `spot_prices(fuel)`: returns list of SpotPrice from feed.
  - `get_latest_spot(fuel)`: most recent spot price by period sort.
  - `get_forward_price_estimate(fuel, lookback_periods=48, premium_pct=5%)`: mean of recent spots + risk premium.
  - `is_stale(max_age_hours=24)`: compares published_at to now.
  - `summary()`: structured dict for reporting.
- `publish_feed(prices, output_path, published_at)`: SIM pipeline calls this after each run to write the feed file.

**Fidelity delta:** The company now reads market prices from a published data file rather than calling SIM functions. This closes the last architectural gap: the market data seam is now properly defined. Swapping to live Elexon/ICE data requires only pointing `PriceFeed` at a different feed file — no company code changes needed. **All Destinationvision gaps (C1-C4, FI1-FI3, T1-T3, M1-M3) are now CLOSED.**

**10 new tests (1,622 total).**

---
### Phase 75 -- M1 Elexon Settlement Interface (2026-06-26)
**Files:** `company/market/settlement_reconciler.py` (new), `tests/company/market/test_settlement_reconciler.py` (new)

**What was built:**
- `SettlementStatement` dataclass: period, customer_id, volume_kwh, ssp_gbp_per_mwh, net_settlement_cost_gbp, hedge_pnl_gbp.
- `receive_settlement()`: pure constructor for settlement receipts.
- `reconcile_against_bill(statement, billed_revenue, threshold_pct=5%)`: imbalance = billed - settled. Flagged when >5% of settlement cost OR >£10 absolute.
- `reconcile_period_batch(statements, revenues)`: batch reconciliation with total imbalance, flagged count, checked count.
- `imbalance_summary(batch_result)`: favourable/unfavourable counts, net_position (favourable/unfavourable).

**Fidelity delta:** The company can now receive Elexon settlement statements and reconcile them against its own billing records. An imbalance flagging system catches cases where billed tariff revenue diverges significantly from wholesale settlement cost -- a key operational risk in energy retail (BSC imbalance charges). M1 closed -- full market infrastructure stack complete.

**10 new tests (1,612 total).**

---
### Phase 74 -- M2 Regulatory Reporting (2026-06-26)
**Files:** `company/regulatory/compliance.py` (new), `tests/company/regulatory/test_compliance.py` (new)

**What was built:**
- `smart_meter_target(year, segment)`: Ofgem SMETS2 targets 2019-2025 (resi: 53%-86%; SME: 75% of resi; I&C: 100% always).
- `smart_meter_compliance_status(actual, year, segment)`: COMPLIANT / AT_RISK (>5pp gap) / BREACH (>10pp gap).
- `check_price_cap_compliance(records, cap_unit, cap_sc)`: flags any tariff record exceeding Ofgem domestic cap on unit rate or standing charge.
- `generate_css_filing(service_log_data, year)`: annual CSS return -- total contacts, complaints, resolved count, resolution rate, vulnerable customers. `resolution_target_met` flag (Ofgem SLC37: 80% within 56 days).
- `annual_turnover_fee(revenue_gbp)`: Ofgem annual fee at 0.07% of turnover.

**Fidelity delta:** The company can now self-assess against Ofgem licence conditions before the regulator does. Smart meter compliance status, price cap breach detection, and CSS filing are the three most common regulatory enforcement triggers in UK energy retail. M2 closed.

**13 new tests (1,602 total).**

---
### Phase 73 -- T1 Trading Desk Interface (2026-06-26)
**Files:** `company/portal/app.py` (extended), `company/portal/templates/trading.html` (new), `tests/company/portal/test_trading_route.py` (new)

**What was built:**
- `GET /trading` route in portal: loads `hedge_effectiveness_total` and per-year breakdown from `run_output_latest.json` via `_load_trading_data()`. Renders portfolio summary (actual vs naked vs value-add), best/worst hedging decisions (customer_id, term_start, P&L, HF), and year-by-year P&L table.
- `trading.html` template: coloured P&L (green/red), graceful fallback when no run data.
- Reads published run output only -- no simulation internals.

**Fidelity delta:** The trading desk now has a browser view. Rich can navigate to /trading and see the full hedging P&L record: the 2022 energy crisis shows the book deeply negative (hedged at £50-70/MWh, settled at £200+), while 2016-2019 shows hedging as a drag on returns (naked would have won). That tension is the point of the trading book. T1 closed -- all three trading capabilities complete.

**7 new tests (1,589 total).**

---
### Phase 72 -- T2 Position Management (2026-06-25)
**Files:** `company/trading/forward_book.py` (extended), `tests/company/trading/test_position_management.py` (new)

**What was built:**
- `HedgeAmendment` dataclass: customer_id, term_start, amendment_date, old/new hedge fraction, reason. Immutable audit record.
- `PositionClosure` dataclass: customer_id, term_start, close_date, close_price, realised_pnl_gbp.
- `TradingBook.amend_hedge()`: records fraction change with sequential old-fraction tracking (so two amendments correctly chain old->new->newer).
- `TradingBook.close_position()`: computes realised P&L = (close_price - agreed) x notional; removes from open book.
- `open_contracts()` now filters out closed positions; `portfolio_mtm()` likewise.
- `amendments()`, `closures()`, `closed_contracts()` accessors.

**Fidelity delta:** The trading book now has a full lifecycle: open (Phase 43a), mark-to-market (Phase 71), amend, close. The audit trail means every position change is dated and attributed. This is the structure a real energy supplier's trading desk uses for mandate compliance review. T2 closed.

**10 new tests (1,582 total).**

---
### Phase 71 -- T3 Mark-to-Market Valuation (2026-06-25)
**Files:** `company/trading/forward_book.py` (extended), `tests/company/trading/test_mtm.py` (new)

**What was built:**
- `TradingBook.mark_to_market(contract, current_price)`: MTM value of one contract. MTM P&L = (market_price - agreed_price) x notional_mwh. Returns {customer_id, term_start, notional_mwh, agreed_price, market_price, mtm_pnl_gbp, in_the_money}.
- `TradingBook.portfolio_mtm(current_prices_by_customer)`: portfolio rollup. Accepts {customer_id: price} dict; skips contracts with no price. Returns {total_mtm_pnl_gbp, positions_priced, positions_in_the_money, positions_out_of_money, positions[]}.
- Current market prices injected as a parameter (company's observable forward price from tariff engine -- no SIM internals).

**Fidelity delta:** The trading book now has daily valuation. Pre-crisis 2021 Q4: forwards agreed at £50-70/MWh, market now £150+, portfolio deeply in-the-money. Post-crisis 2023: some short-duration hedges locked in at peak; deeply out-of-the-money. The MTM signal is the risk committee's most important daily number. T3 closed.

**10 new tests (1,572 total).**

---
### Phase 70 -- FI3 Treasury Management (2026-06-25)
**Files:** `company/finance/treasury.py` (new), `tests/company/finance/test_treasury.py` (new)

**What was built:**
- `company/finance/treasury.py`: `working_capital(balance_sheet)` -- current assets minus current liabilities. `cash_flow_by_year(pack)` -- cash balance per year from management accounts. `annual_cash_changes(pack)` -- year-over-year delta. `project_treasury(pack, base_year, horizon=3)` -- 3-year forward projection using average of last 3 actual cash changes. `treasury_health(pack, year, customer_count)` -- MCR requirement (£130/account), headroom, status (OK >1x / WATCH 0-1x / CRITICAL <0x).
- All data from management accounts balance sheets; no simulation internals.

**Fidelity delta:** Treasury is now managed, not just tracked. The company has a 3-year cash forecast and a formal MCR headroom signal. Combined with Phase 55 solvency signal and Phase 53 BSC credit cover, the company now has a complete capital adequacy stack: spot check (MCR), credit cover (BSC), and forward view (FI3). FI3 closed -- financial infrastructure complete.

**12 new tests (1,562 total).**

---
### Phase 69 -- C4 CRM Service Interaction Log (2026-06-25)
**Files:** `company/crm/service_log.py` (new), `tests/company/crm/test_service_log.py` (new)

**What was built:**
- `company/crm/service_log.py`: `ServiceEvent` dataclass (customer_id, event_date, channel, contact_reason, outcome, agent_type, complaint_flag, vulnerability_flag, notes). `VulnerabilityFlag` dataclass (customer, flagged_date, flag_type, active, resolved_date). `ServiceLog`: `record_contact()`, `contacts_for_customer()`, `complaints()`, `complaint_rate()`, `complaint_stats(year)`, `vulnerability_register()`, `resolve_vulnerability()`, `as_dicts()`.
- Complaint stats filterable by year. Vulnerability flags auto-created on contact; resolvable with a dated closure. Independent from lifecycle event log (`CompanyEventLog`).

**Fidelity delta:** CRM now has two tracks: lifecycle events (churn/retention/acquisition, existing) and service interactions (contacts, complaints, vulnerabilities — new). Complaint rate and vulnerability register are the two most scrutinised customer service KPIs in UK energy retail (Ofgem CRM requirements). C4 closed.

**12 new tests (1,550 total).**

---
### Phase 68 -- C2 Customer Portal MVP (2026-06-25)
**Files:** `company/portal/app.py` (new), `company/portal/templates/` (3 HTML templates), `tests/company/portal/test_portal.py` (new)

**What was built:**
- `company/portal/app.py`: FastAPI app with 4 routes: `GET /` (login page), `POST /login` (account-number auth, case-insensitive), `GET /account/{id}` (dashboard: profile + billing summary), `GET /account/{id}/bills` (invoice list from SQLite).
- Jinja2 templates: `login.html`, `dashboard.html`, `bills.html`. Reads company layer only: `saas/customers.py` for profile, `company/billing/invoice.py` for invoices. No simulation internals.
- `_invoice_summary()`: aggregates billed/paid/outstanding from invoice DB for dashboard display.

**Fidelity delta:** Rich can now log in as C1 and see account profile (segment, contract, EAC), billing summary (total billed, paid, outstanding), and invoice history with payment status. The customer experience is real. C2 closed.

**14 new tests (1,538 total).**

---
### Phase 67 -- C3 Payment Processing and Debt Aging (2026-06-25)
**Files:** `company/billing/payments.py` (new), `tests/company/billing/test_payments.py` (new)

**What was built:**
- `company/billing/payments.py`: `reconcile_payment()` -- matches `payment_received_event` to invoice by customer_id + billing_period_end; returns new status (paid/partially_paid/no_match). `reconcile_payments()` -- batch reconciliation with outcome counts. `age_debt()` -- flags invoices unpaid >90 days as bad_debt. `debt_aging_summary()` -- current/late/overdue/bad_debt aging buckets.
- Reconciliation uses 0.1% tolerance (total * 0.999) to absorb rounding; idempotent on already-paid invoices.

**Fidelity delta:** Billing lifecycle complete: bill -> invoice artefact -> payment -> reconciliation -> bad debt. Invoices age through four buckets: current/late/overdue/bad_debt. Foundation for DSO metric. C3 closed.

**10 new tests (1,524 total).**

---
### Phase 65 — FI2 Budget vs Actual (2026-06-25)
**Files:** `company/finance/budget.py` (new), `tests/company/finance/test_budget_vs_actual.py` (new), `saas/reporting/annual_report.py` (extended)

**What was built:**
- `company/finance/budget.py`: `_BUDGET_BY_YEAR` (2016-2025 static constants from prior-year actuals * growth factors: revenue * 1.10, opex * 1.05), `variance_report()`, `monthly_variance()`, `traffic_light()' (GREEN <5%, AMBER 5-15%, RED >=15%).
- Annual report: 10-year variance table (Budget Revenue, Actual Revenue, Rev%, Budget Net, Actual Net, Net%, RAG).
- 2021: AMBER (-13.7% net miss); 2022: RED (+18.3% crisis outperformance); 2023: RED (-21.1% post-crisis miss).

**Fidelity delta:** Company now has a budget model. Management reporting moves from observation to control. FI2 closed.

**12 new tests (1,505 total).**

---

### Phase 62 — Standing Charges: Electricity and Gas (2026-06-25)
**Files:** `simulation/policy_costs.py` (extended), `simulation/hedged_settlement.py` (updated), `simulation/gas_settlement.py` (updated), `tests/simulation/test_phase62_standing_charges.py` (new)

**What was built:**
- `simulation/policy_costs.py`: `get_electricity_standing_charge_per_day()` and `get_gas_standing_charge_per_day()`, year-indexed from Ofgem tariff tracker data 2016–2024. Resi electricity: 24p/day (2016) → 61p/day (2024); gas: 22p → 31p/day. SME: 1.5× multiplier. I&C: 0.0 (capacity charges via BSC settlement).
- `simulation/hedged_settlement.py`: SC prorated per half-hour period, added to customer revenue and supplier margin; `standing_charge_gbp` field in settlement records.
- `simulation/gas_settlement.py`: daily SC added as `gas_standing_charge_gbp` field.

**Fidelity delta:** Standing charges were missing from all tariffs. Resi customers pay ~£350/yr (electricity) + £120/yr (gas) in standing charges; this is a real fixed-revenue stream for the supplier. Post-2022, the Ofgem price cap applies ceiling values to standing charges just as it does to unit rates.

**12 new tests (1,456 total).**

---

### Phase 61 — Flex Tariff Policy Pass-Through Fix (2026-06-25)
**Files:** `simulation/hedged_settlement.py`, `tests/simulation/test_phase41a_flex.py` (updated), `tests/simulation/test_phase61_flex_passthrough.py` (new)

**What was built:**
- `simulation/hedged_settlement.py` `run_flex_term()`: Fixed revenue calculation to include policy and network costs as pass-through (matching `run_hedged_term` pass-through logic). Revenue = (ref_price + markup + policy + network) × consumption; net = markup × consumption. Previously: revenue = (ref + markup) × consumption; net = markup - policy - network (supplier absorbed all policy/network costs).
- `tests/simulation/test_phase41a_flex.py`: Updated 3 test assertions — margin and revenue tests now verify pass-through semantics; `net_margin_gbp` rather than `margin_gbp` is the key invariant.
- `tests/simulation/test_phase61_flex_passthrough.py` (new): 8 tests for pass-through correctness (net = markup, revenue includes passthrough, policy non-zero but doesn't reduce net, unit_rate reflects full customer bill, net stable across 2018 vs 2022 policy levels).

**Fidelity delta:** C_IC4 (3 GWh/year supermarket chain, flex tariff) was showing ~£175k annual losses and -£1.06M total — an artefact of incorrectly charging the supplier for policy and network costs that the customer actually pays. In a real UK I&C flex contract (spot-indexed, week-ahead calling), policy costs (RO, CfD, CCL, CM, FiT, mutualization levy) and network charges are billed to the customer as pass-through items. The supplier's margin is the trading markup only (£2/MWh). After the fix: C_IC4 net margin ≈ £6k/year (markup × volume), and total business net margin improves by ~£1.1M from previously incorrect losses.

**8 new tests (1,444 total).**

### Phase 60 — I&C Gas Flat Seasonal Profile (2026-06-25)
**Files:** `simulation/gas_settlement.py`, `tests/sim/test_ic_gas_profile.py` (new), `tests/sim/test_gas_seasonality.py` (updated)

**What was built:**
- `simulation/gas_settlement.py`: `GAS_IC_CONSUMPTION_MONTHLY_PROFILE` — I&C process gas monthly factors. Jan=1.075, Jul=0.913, 1.18× ratio (vs 5.3× resi). Source: UK DUKES industrial gas monthly shares, normalised.
- `run_gas_term()`: selects profile by `segment` — `"I&C"` → IC profile, all others → resi profile. Prior Phase 59 applied the residential 5.3× seasonal swing to C_IC3g (AQ=5M kWh), creating £1,048/day Jan-Jul billing delta — incorrect for process-heat-dominated industrial demand.

**Fidelity delta:** I&C gas consumption is now near-flat across months (~1.18× Jan:Jul), matching UK industrial gas demand patterns. Resi gas retains the 5.3× seasonal heating demand swing. C_IC3g annual billing distribution is now physically realistic.

**8 new tests (1,436 total).**

---

### Phase 59 — Monthly Gas Consumption Seasonality (2026-06-25)
**Files:** `simulation/gas_settlement.py`, `tests/sim/test_gas_seasonality.py` (new)

**What was built:**
- `simulation/gas_settlement.py`: `GAS_CONSUMPTION_MONTHLY_PROFILE` — monthly daily-consumption factors from UK DUKES Table 4.3 resi gas monthly shares (2016-2020 avg). Jan=1.884, Jul=0.353, 5.3× ratio. Normalized so a full non-leap year sums to 365 kWh per unit of AQ/365.
- `run_gas_term()`: `base_daily_kwh = AQ/365`; per-day `daily_kwh = base × GAS_CONSUMPTION_MONTHLY_PROFILE[month] × weather_factor`. Previously flat at AQ/365 every day.
- Settlement records include `seasonal_factor` field per record.

**Fidelity delta:** Residential gas billing now reflects the real winter/summer consumption ratio (~5:1). January bills are ~5× higher than July (as in reality), not flat. Combined with Phase 58 weather factor, gas P&L now has both within-year seasonal shape AND year-to-year weather deviation. Prior model was flat AQ/365 per day — unrealistic for heating-dominated demand.

**10 new tests (1,436 total).**

---

### Phase 58 — Weather-Adjusted Gas Consumption: HDD Model (2026-06-25)
**Files:** `sim/weather_hdd.py` (new), `simulation/gas_settlement.py`, `simulation/run_phase2b.py`, `tests/sim/test_weather_hdd.py` (new)

**What was built:**
- `sim/weather_hdd.py`: `get_hdd(date_str, customer_id)` — HDD = max(0, 15.5°C − mean_temp). `get_monthly_hdd()`, `get_weather_factor(year, month, customer_id)` — actual/reference HDD ratio, clipped [0.3, 2.0]. `weather_factor_for_term()` — day-weighted average over a contract term. `REFERENCE_MONTHLY_HDD`: UK Met Office 1991–2020 climate normals (Jan 350 HDD → Jul 5 HDD).
- `simulation/gas_settlement.py`: `weather_factor: float = 1.0` param on `run_gas_term()`. `daily_kwh = AQ/365 × weather_factor`. Factor appears in every settlement record.
- `simulation/run_phase2b.py`: for each resi/SME gas term, compute `weather_factor_for_term(term_start, term_end, cid)` and pass to `run_gas_term()`. I&C process gas (`C_IC3g`) unchanged (industrial load, not space-heating-dominated).

**Fidelity delta:** Gas consumption now varies with actual UK weather. The 2019–2020 warm winter (warmest on record) reduces resi gas consumption and cost; a January cold snap increases demand. Resi gas customers see weather-driven bill variance. Fixed-rate supplier margin improves in warm years (billed at fixed tariff, less gas actually consumed = lower wholesale cost).

**15 new tests (1,418 total).**

---

### Phase 57 — Year-Varying Bad Debt (2026-06-25)
**Files:** `saas/cost_to_serve.py`, `simulation/run_phase2b.py`, `saas/reporting/annual_report.py`, `tests/saas/test_bad_debt.py` (new)

**What was built:**
- `saas/cost_to_serve.py`: `get_bad_debt_rate(year, segment)` — year-varying lookup replacing flat `BAD_DEBT_RATE`. Resi: 2.0% (stable), 4.0% (2021), 8.0% (2022 peak — Ofgem 2.4M households in arrears), 5.0% (2023), 3.0% (2024). SME: 1.0%→3.0%→2.0%. I&C: 0.5% (stable through crisis — long-term contracts, direct debit mandates).
- `simulation/run_phase2b.py`: `bad_debt_gbp` computed each settlement record and deducted from `net_margin_gbp` + treasury. Previously `bad_debt_provision_gbp` existed in reporting but was not deducted. `total_bad_debt` added to run output.
- `saas/reporting/annual_report.py`: `bad_debt_gbp` now sourced from per-record data (not `payment_behaviour`). Also fixed solvency dedup bug: `_section_solvency_signal()` now uses billing-account-deduped count (C1+C1g = 1, not 2).
- Fixed 2 pre-existing Phase 54 test failures in `test_phase27b_ccl.py` and `test_phase31a_fit_levy.py` — expected policy cost was missing `mutualization_levy_gbp`.

**Fidelity delta:** Bad debt was a paper provision that didn't touch the treasury. Now the crisis years bite: 2022 resi customers default at 8% of revenue — mirroring the Ofgem 2.4M-households-in-arrears figure. Crisis-year treasury depletion is more realistic. Solvency MCR ratio also corrected for dual-fuel account deduplication.

**9 new tests (1,403 total).**

---

### Phase 55 — Ofgem MCR Solvency Signal (2026-06-25)
**Files:** `saas/capital/solvency.py` (new), `saas/reporting/annual_report.py`, `tests/saas/capital/test_solvency.py` (new)

**What was built:**
- `saas/capital/solvency.py`: `compute_solvency_signal(treasury_gbp, active_customer_count)` → `{per_customer_net_assets_gbp, mcr_floor_gbp, solvency_ratio, status}`. `MCR_FLOOR_GBP_PER_CUSTOMER = 130.0` (Ofgem MCR target for dual-fuel); `Watch < 2×`, `STRESS < 1×` (account below floor). `compute_solvency_by_year(years_data)` aggregates per report year.
- `saas/reporting/annual_report.py`: `_section_solvency_signal()` updated (Phase 21b/55) to use `compute_solvency_by_year`; table now shows Solvency Ratio and Status columns. Import added for `compute_solvency_by_year`.
- `docs/market_research/ASSUMPTIONS.md`: Rows 38 and 41 updated — gas and electricity price cap rows were falsely marked "NOT MODELLED"; Phase 47a applies both.

**Fidelity delta:** Ofgem's supply licence Standard Condition 27 requires licensed suppliers to maintain sufficient net assets per customer. The MCR (Minimum Capital Requirement) target is approximately £130/dual-fuel account. When treasury per account falls below the floor (ratio < 1×), the supplier is in regulatory breach — this is how Ofgem triggered Special Administration Regime for Bulb (when its per-customer net assets turned negative). The simulation now tracks this per year and flags Watch/STRESS conditions.

**12 new tests (1,389 total).**

---

### Phase 52 — ToU Demand Response Model (2026-06-25)
**Files:** `saas/demand_response.py` (new), `simulation/run_phase2b.py`, `tests/saas/test_phase52_demand_response.py` (new), `tests/background/test_session_watchdog.py`, `background/session_watchdog.py`

**What was built:**
- `saas/demand_response.py`: `PEAK_PERIODS` = SP 32-38 (16:00-18:30 UK); `OFFPEAK_PERIODS` = SP 1-14 + SP 47-48. `compute_shift_fraction(assets)` — base 15% peak-to-offpeak shift + EV +12% + heat_pump +8%, capped at 100%. `apply_demand_shift(hh_profile, shift_fraction)` — redistributes shifted_kwh uniformly across offpeak periods; energy conserved. `make_shifted_shape_fn(base_shape_fn, shift_fraction)` — wraps existing shape callable for use in `run_hedged_term()`.
- `simulation/run_phase2b.py`: ToU-eligible customers use `make_shifted_shape_fn()` to produce a modified consumption shape; passed to `run_hedged_term()` as `effective_shape_fn`. `demand_response_log` per term written to run output (customer_id, shift_fraction, has_ev, has_heat_pump).
- `background/session_watchdog.py`: API connectivity check (`check_api_reachable()`), exponential backoff on failure (1m/2m/5m then 10min indefinitely), NTFY Rich on first failure and every hour while still down. Pre-start curl check before each restart.

**Fidelity delta:** ToU-eligible customers (smart-meter or HH-metered) now shift peak consumption in response to price signals. A customer with an EV and heat pump shifts 35% of their 16:00-18:30 load to overnight/early morning periods. This changes actual settlement-period consumption fed into `run_hedged_term()`, affecting imbalance exposure and hedge effectiveness. The pattern mirrors how UK Agile and Economy 7 customers respond to price differentials in practice.

**24 new tests (1,355 total).**

---

### Phase 51 — ToU Eligibility Gate Broadened (2026-06-24)
**Files:** `saas/smart_meter_rollout.py`, `simulation/run_phase2b.py`, `tests/saas/test_phase51_tou_eligibility.py` (new)

**What was built:**
- `is_tou_eligible(customer: dict)` added to `saas/smart_meter_rollout.py`: returns True if `customer.get("metering") == "HH"` (original HH-metered customers) OR `customer.get("smart_meter", False) is True` (acquired customers with Phase 50 rollout-stamped smart meter).
- `simulation/run_phase2b.py`: ToU pricing gate at line 1115 upgraded from `is_hh_customer(customer)` to `is_tou_eligible(customer)`. The HH consumption shape path (line 1061) remains gated on `is_hh_customer` — HH reads only apply to customers with actual HH data files.

**Fidelity delta:** Smart-meter acquired customers now receive peak/off-peak Time-of-Use pricing on their electricity contract. In 2024, ~72% of acquired resi customers have smart meters and pay ToU rates. This is how UK suppliers run Agile/Economy 7 tariffs in practice: smart meter enables ToU pricing even before true HH settlement is available. The Phase 5 smart tariff infrastructure is now complete for resi customers.

**9 new tests (1,330 total).**

---

### Phase 50 — Smart Meter Rollout Model (2026-06-24)
**Files:** `saas/smart_meter_rollout.py` (new), `saas/property_model.py`, `saas/customers.py`, `tests/saas/test_smart_meter_rollout.py` (new), `tests/saas/test_phase50_smart_meter_integration.py` (new)

**What was built:**
- `saas/smart_meter_rollout.py`: `get_penetration(year, segment)` — UK smart meter stock penetration by segment (resi 10%→75% 2016-2025, SME 5%→57%, I&C 100% per BSC P272/P322 mandate). `get_new_install_probability(year, segment)` — annual probability a NHH customer gets a smart meter (derived from penetration delta / remaining NHH base). `should_upgrade_to_hh(year, segment, rng_value)` — deterministic Boolean roll. `is_hh_eligible(metering)` — ToU gate.
- `saas/property_model.py`: `get_smart_meter_status(customer_id, year, segment)` — time-aware flag. Static profile for known customers (ASSET_PROFILE_BY_CUSTOMER); for acquired customers, uses `get_penetration()` with deterministic RNG seeded by `customer_id`. Same customer always gets the same answer for a given year; monotonic (if True in year Y, True in Y+1).
- `saas/customers.py`: `make_acquired_customer()` stamps `smart_meter: bool` based on rollout penetration at acquisition year. Earlier acquisitions have lower probability; I&C always True.

**Fidelity delta:** The simulation now tracks smart meter adoption over the 2016-2025 UK rollout. Acquired customers in 2016 have ~10% probability of a smart meter; by 2024 that's ~72%. This gates Phase 51 (Time-of-Use tariffs): only HH-metered/smart-meter customers are eligible. The company can observe its own smart meter penetration and know what fraction of its portfolio can be offered ToU products.

**30 new tests (1,321 total).**

---

### Phase 49 — EWMA Base + Dynamic Term Structure Slope (2026-06-24)
**Files:** `company/pricing/tariff_engine.py`, `tests/company/pricing/test_phase49_term_structure.py` (new)

**What was built:**
- `_compute_ewma(daily_means, half_life_days=30)`: exponentially weighted mean with 30-day half-life, replaces simple rolling mean as the base price estimate in `get_forward_price()`. Faster regime adaptation — recent prices weighted more than older prices.
- `_estimate_term_structure_slope(delivery_date, price_records)`: compares 30-day EWMA vs 90-day EWMA to derive an annualised contango/backwardation slope. Positive in rising markets (contango), negative in falling markets (backwardation). Capped to `[TERM_SLOPE_FLOOR=-8%, TERM_SLOPE_CAP=+15%]` per year.
- `get_forward_price()` applies `slope × tenor_years` as a dynamic premium on top of the Phase 48a structural term premium. In the 2021-22 crisis (strongly rising spot), long-dated I&C contracts now price higher; in falling markets they price lower.

**Fidelity delta:** The company's forward price now reflects observable market direction. In a contango market a 2-year contract is priced above a 1-year contract by more than the fixed structural premium alone — matching how N2EX/NBP markets actually behave. The EWMA base (vs 120-day simple mean) adapts faster to regime changes, reducing the systematic underpricing lag during the 2021-22 price spike.

**15 new tests (1,291 total).**

---

### Phase 48a — Forward Curve Term-Length Premium (2026-06-24)
**Files:** `company/pricing/tariff_engine.py`, `company/interfaces/sim_interface.py`, `tests/company/pricing/test_phase48a_term_premium.py` (new)

**What was built:**
- `TERM_LENGTH_PREMIUM_PCT_PER_YEAR = 0.02` in `tariff_engine.py`: 2% per year of contract duration beyond 12 months.
- `get_forward_price()` gains `term_months: int = 12` parameter. `term_premium = max(0, (term_months/12 - 1)) × 0.02` added to the risk premium in the final price: `base × (1 + risk_premium + term_premium)`.
- Applied additively: a 2-year contract gets +2% on the base, a 3-year gets +4%. Sub-12-month terms get no premium (floor at 0). All existing callers default to 12 months — no change to current simulation outputs.
- `SimInterface.get_forward_price()` and `LiveSimInterface.get_forward_price()` updated with `term_months` parameter.

**Fidelity delta:** UK forward markets (NBP/EPEX) price CAL+2 1–4% above CAL+1 (Bloomberg/Refinitiv). Real I&C contracts reflect this term structure: a 2-year fixed deal commands a premium over a 1-year deal because the supplier locks in more price risk. The SIM forward curve now models this term structure, making multi-year I&C pricing realistic.

**7 new tests (1,276 total).**

---

### Phase 46a — Gas Risk Premium Further Reduced (2026-06-23)
**Files:** `company/pricing/tariff_engine.py`, `tests/company/pricing/test_phase45c_risk_premium.py`, `tests/company/pricing/test_tariff_engine.py`

**What was built:**
- `GAS_RISK_PREMIUM_FRACTION`: 10% → 5%. UK resi gas fixed tariffs: suppliers price at NBP + thin service margin only. Pass-through gas already bills at spot + £2/MWh (Phase 45b), so this premium applies only to fixed-term gas customers.
- With 5% premium in stable markets (120-day mean ≈ EWMA): company_fwd ≈ SIM_fwd → near-zero gas margin. Positive margins emerge when 120-day mean > EWMA (falling markets), where the company's lagged pricing gives it an advantage.
- Electricity (8%) now higher than gas (5%) — justified because I&C electricity contracts have more competitive pricing pressure and higher spot volatility exposure in the SIM.
- Updated tests: `test_gas_risk_premium_higher_than_electricity` renamed and semantics corrected; Phase 45c gas test updated.

**Fidelity delta:** UK resi gas suppliers earn near-zero margins in stable years (confirmed by Cornwall Insight 2020 analysis showing resi gas at ~1-2% in that period). Phase 46a brings the SIM into line.

**0 new tests (1,250+ total, tests updated for new constants).**

---

### Phase 45c — Forward Curve Risk Premium Recalibration (2026-06-23)
**Files:** `company/pricing/tariff_engine.py`, `tests/company/pricing/test_phase45c_risk_premium.py` (new)

**What was built:**
- `COMPANY_RISK_PREMIUM_FRACTION` reduced 15% → 8% (electricity): aligns with UK I&C competitive market (5–8% above NAP/baseload). Original 15% drove C_IC1/C_IC2 to ~33% cumulative net margin vs 3–8% industry benchmark.
- `GAS_RISK_PREMIUM_FRACTION` reduced 20% → 10% (gas): gas market more volatile than electricity, but pass-through gas is now billed at spot (Phase 45b) so the premium only affects fixed gas tariffs where the company takes price risk.
- 8 new unit tests in `test_phase45c_risk_premium.py`: constants at correct values, gas > electricity, both below prior levels, forward price uses new premiums.

**Fidelity delta:** Company forward pricing matches UK I&C competitive market norms; systematic overpricing artefact eliminated. Churn model naturally handles under-competitive pricing at renewal.

**8 new tests (1,250+ total).**

---

### Phase 45b — Gas Pass-Through Bills at Spot Price (2026-06-23)
**Files:** `simulation/gas_settlement.py`, `tests/simulation/test_phase45b_gas_pass_through_spot.py` (new)

**What was built:**
- `GAS_PASS_THROUGH_SERVICE_FEE_GBP_PER_MWH = 2.0`: thin handling margin company earns on pass-through gas.
- `settle_gas_period()` (pass-through branch): billing now uses `daily_mwh × (spot_price + £2/MWh)` instead of `billed_gbp` (which used `unit_rate = company_fwd × 1.20 + £2`). Policy/network costs still added on top.
- `unit_rate` parameter stored in schedule for reference but bypassed in billing calculation for pass-through.
- 6 tests verify: energy billing = spot + fee, net ≈ service fee when spot == forward, net strictly lower than old model, constant at £2.0, fixed gas unaffected, crisis spot passes through to customer.

**Fidelity delta:** Gas pass-through tariffs now correctly transfer wholesale price risk to the customer; company earns only the thin service margin (£2/MWh), eliminating the artifical 19.9% I&C/gas net vs 2–6% industry benchmark.

**6 new tests (1,242+ total).**

---

### Phase 45a — Revenue & Margin Sanity Check (2026-06-23)
**Files:** `tools/revenue_sanity_check.py` (new), `saas/reporting/annual_report.py`, `background/process_run_complete.py`, `site/snapshots/DASHBOARD_20260623_120151.json` (new)

**What was built:**
- `tools/revenue_sanity_check.py`: post-run P&L waterfall + per-segment net margin vs Ofgem/CMA benchmarks (resi 2–5%, SME 3–8%, I&C 3–15%). Flags anomalies; exits 1 on fail.
- `saas/reporting/annual_report.py`: `_section_revenue_sanity()` wired in after Customer P&L Ranking. Runs every annual report, silent if tool unavailable.
- `background/process_run_complete.py`: sanity check logged after dashboard generation on every run_complete pipeline execution.
- Snapshot JSON companion: standalone `DASHBOARD_*.json` at same URL as HTML snapshot — strategy advisor fetches without JS.
- Anomalies detected: I&C/gas 19.9% (bench 2–6%, root cause: company_fwd overestimates actual NBP forward on gas pass-through), resi 12.2%/11.8% (CCL-exempt + forward bias).

**Fidelity delta:** Every full run now auto-checks margin realism against UK industry benchmarks.

**0 new tests (1,290+ total).**

### Phase 44a — Customer Profitability Feedback into Renewal Pricing (2026-06-23)
**Files:** `company/crm/customer_profitability.py` (new), `saas/tariff_pricing.py`, `simulation/run_phase2b.py`, `tests/company/test_customer_profitability.py` (new)

**What was built:**
- `estimate_prior_term_net_margin()`: reads company's own billing records (net_margin_gbp) for a customer's most recent completed term. Returns total net margin in £, or None if insufficient history (< 48 records = 1 month of HH data).
- `compute_profitability_uplift()`: returns £3/MWh if prior term was net-negative, 0.0 otherwise.
- `saas/tariff_pricing.py`: `profitability_uplift_per_mwh` parameter (additive, default 0.0 — backward compatible).
- `simulation/run_phase2b.py`: uplift applied at renewal for electricity fixed/pass-through terms only. Logged in `profitability_uplift_log` in run output. Churn model handles consequence naturally (higher rate → higher churn probability → unprofitable customers tend to leave).
- Epistemic compliance: company only uses its own billing records — observable accounting data, not simulation parameters.

**Fidelity delta:** The company now acts like a real supplier: identifies loss-making accounts at renewal and quotes them higher. Regime where this matters most is post-crisis (2021+) when some customers' consumption patterns made them net-negative despite "on-target" margin.

**Closes:** "Pricing actions not implemented (tariff uplift for NET_NEGATIVE customers)" from ASSUMPTIONS.md Known Gaps.

**13 new tests (1,290+ total).**

### Phase 43b — Adaptive Trading Desk, VaR-Constrained (2026-06-23)
**Files:** `company/trading/hedge_decision.py` (new), `company/trading/forward_book.py`, `simulation/run_phase2b.py`, `saas/reporting/annual_report.py`, `tests/company/test_hedge_decision.py` (new)

**What was built:**
- `estimate_price_volatility()`: 90-day EWMA realized vol from observable spot prices (Elexon SSP). λ=0.94, annualized.
- `decide_hedge_fraction()`: 95% VaR constraint — max unhedged position = 15% of term revenue at risk. High-vol regimes force higher hedge fractions automatically.
- `compute_bid_ask_cost()`: OTC execution cost model — 0.5% + 0.2%/year tenor, capped 1.5% (N2EX calibrated).
- `ForwardContract` extended with `bid_ask_cost_gbp`; `TradingBook.summary()` now includes bid-ask total.
- `_section_trading_pnl()` in annual report: year-by-year hedge P&L vs gross margin with direction signal.
- Epistemic compliance: all inputs observable (published spot prices, company's own demand/price estimates).

**Fidelity delta:** The trading desk now adapts hedge fractions to market conditions. In calm 2016-2020 regime, VaR allows low hedges; in crisis it forces higher coverage — modelling the regime-change blindness trap that killed real UK suppliers.

**15 new tests (1,257+ total).**

### Architecture Stages 0-4 (2026-06-23)
**Files:** `docs/claude/best-practice-audit.md`, `background/agent_status.py`, `site/index.html` (System tab), `.claude/agents/discovery-agent.md`, `.claude/agents/epistemic-verifier.md`, `background/agent_protocol.py`, `tools/epistemic_verifier.py`, `CLAUDE.md` (restructured)

**What was built:** See Section 12 (Agent Architecture). CLAUDE.md reduced from 494 lines to 151 lines. Epistemic verifier added to phase-close checklist. 18 new protocol tests.

### Phase 42 — Gas Forward Curve Seasonal Calibration (2026-06-22)
**Files:** `sim/forward_curve.py`, `simulation/run_phase2b.py`, `simulation/run_segments.py`, `tests/sim/test_forward_curve.py`

**What was built:**
- Gas-specific seasonal multiplier table (`GAS_MONTH_SEASONAL_MULTIPLIER`): Q1 peak 1.22×, Q3 trough 0.80× — vs electricity Q1 1.12×, Q3 0.88×. UK space-heating demand creates 2-3× steeper winter/summer spread for NBP vs N2EX.
- `fuel` parameter on `generate_forward_price()` and `_seasonal_shape()`. Backward-compatible — electricity remains the default.
- `GAS_BASE_TERM_PREMIUM = 0.05` (vs electricity 0.06) — gas NBP forward market is more liquid.
- Weather adjustment (Phase 4c-3) correctly guarded to electricity only.
- Gas bootstrap and gas path in `run_segments.py` all use `fuel="gas"`. 8 new tests (23 total in test_forward_curve.py).

**What this fixed:** Gas forward prices were being calculated with electricity seasonal multipliers. Gas customers (C1g-C4g, C_IC3g) were systematically mispriced — winter gas terms underpriced, summer terms overpriced — because electricity's winter demand shape is much flatter than gas space-heating demand.


### Phase 26 — Industrial HH Demand Profile + Risk Committee EAC Consistency
**Files:** `sim/hh_data/C_IC1.csv`, `saas/customers.py`, `simulation/run_phase2b.py` (risk committee block), `tests/simulation/test_phase26a_industrial_profile.py`

**What was built:**
- **Industrial warehouse HH profile** for C_IC1: replaced scaled residential C7 shape with deterministic warehouse profile — Mon-Fri 08:00-18:00 core hours at 273 kWh/period, overnight standby 14 kWh/period, Saturday 40%, Sunday 15% of weekday; no seasonal variation; annual total ~2 GWh/year
- **Weekday:Sunday ratio** 6.7× (vs near-flat residential before) — correctly models large-site industrial demand
- **Risk committee block**: EAC now from `_company_eac_estimate()` for all active electricity customers including C_IC1 — consistent with Phase 25a settlement-derived EAC; eliminates last `EFFECTIVE_EAC_KWH` oracle read from risk committee path

**What this fixed:** C_IC1 was modelled with a residential demand shape scaled to I&C volume — flat evenings and weekends. Industrial warehouses have strong weekday/weekend structure. Fidelity fix ensures risk committee sees the correct demand pattern for hedging decisions. 6 new tests (860 total).


---

## 4b. Institutional Knowledge System

All R&D findings and market intelligence are stored in a structured knowledge system:

| Directory | Purpose |
|---|---|
| `docs/institutional/` | Curated, distilled knowledge (tracked in `knowledge_map.md`) |
| `docs/market_research/` | Raw timestamped research files |
| `docs/institutional/knowledge_map.md` | Domain × topic × confidence H/M/L index |
| `docs/institutional/research_methodology.md` | How research was conducted; session logs |
| `docs/institutional/source_guide.md` | Authoritative data sources for each domain |

**Knowledge domains covered:** Elexon SSP/AGWS, Ofgem price cap & capital floor, Renewables Obligation, CfD levy, BSC credit cover, NBP/TTF gas markets, EPC consumption data, supplier P&L structures, energy crisis anatomy (2021-22), novel scenario generation (negative prices, Dunkelflaute, BESS saturation, gas network death spiral).

---

## 5. Autonomous Stack

The system runs autonomously between sessions. All background processes are systemd user units with self-healing cron (every 30 minutes):

| Process | File | Role |
|---|---|---|
| `sim_runner` | `background/sim_runner.py` | Continuously re-runs the full simulation; writes `run_complete_*.md` staging markers |
| `autonomous_runner` | `background/autonomous_runner.py` | Runs Claude `--print` turns on each completed sim run; publishes reports |
| `ntfy_responder` | `background/ntfy_responder.py` | Receives Rich's NTFY messages; writes `from_rich_*.md` to staging; acks with reply |
| `staging_watcher` | `background/staging_watcher.py` | Monitors `docs/staging/` for new files; notifies when new instructions arrive |
| `health_check` | `background/health_check.py` | Verifies all processes alive; logs to `docs/observability/health-check-log.md` |
| `session_watchdog` | `background/session_watchdog.py` | Detects Claude Code usage-limit pauses; resumes session automatically |
| `dispatcher` | `background/dispatcher.py` | Routes inbound NTFY messages by urgency (urgent → wake session, normal → queue) |
| `file_api` | `background/file_api.py` | FastAPI server on Tailscale Funnel — serves status and reports to Rich's phone |
| `discovery_agent` | `background/discovery_agent.py` | Background research agent; updates `ASSUMPTIONS.md` with market data |

**NTFY protocol:** Rich sends a phone notification → `ntfy_responder` acks → writes `from_rich_*.md` → orchestrator picks it up at next startup → acts → sends result back via NTFY.

---

## 6. File Inventory

### `sim/` — Market & Physics Layer

| File | What it does |
|---|---|
| `price_engine.py` | Forward price generation: lookback mean × seasonal multiplier + volatility premium |
| `forward_curve.py` | Forward curve from SSP lookback; pstdev from daily means (not raw HH) |
| `hedging_strategy.py` | Hedge fraction evolution rule; `MIN_HEDGE_FLOOR = 0.85` mandate |
| `risk_engine.py` | VaR assessment per term: dual-window (recent σ vs stressed σ), capital cost, collateral |
| `risk_committee.py` | `RiskCommitteeMonitor`: tracks cooldown, fires when VaR threshold exceeded |
| `risk_committee_agent.py` | Ollama/LLM agent that reads portfolio state and suggests hedge adjustments |
| `profile_class_1.py` | UK residential electricity demand shape (48 HH values/day, seasonal variation) |
| `profile_class_3.py` | UK SME electricity demand shape (PC3) |
| `weather_engine.py` | Regime-switching AR(1) temperature model, Cholesky cross-location correlation |
| `weather_price_sensitivity.py` | Temperature-to-forward-price sensitivity multiplier |
| `weather_ingestor.py` | Fetches Open-Meteo hourly temperature data |
| `system_prices.py` | Live Elexon SSP fetch via Insights API |
| `system_prices_history.py` | Historical SSP range queries against cached data |
| `gas_prices_history.py` | NBP daily price history (3,446 records, 2016–2025) |
| `generation_demand_history.py` | Elexon AGWS/demand history queries |
| `hedging.py` | Hedge position accounting: hedged vs spot volume, mark-to-market |
| `hedging_strategy.py` | `decide_initial_hedge_fraction()`, `evolve_hedge_fraction()`, mandate floor |
| `cache_store.py` | SSP cache read/write; `get_cached_prices()`, `log_cache_access()` |
| `prefetch_demand_generation.py` | Pre-fetch demand/generation data for offline use |

### `simulation/` — Simulation Engine

| File | What it does |
|---|---|
| `run_phase2b.py` | **Primary named-customer simulation loop.** 9 customers × 9.5 years. Annual terms. |
| `run_segments.py` | **Segment simulation loop.** 5 segments × 9.5 years. Headcount evolves annually. |
| `segments.py` | `CustomerSegment` dataclass; 5 segment definitions; `apply_annual_headcount_changes()` |
| `run_phase4c_on_phase2b.py` | Combined Phase 2b + Phase 4c pipeline (billing, payment, contact, CLV, enterprise value) |
| `hedged_settlement.py` | `run_hedged_term()`: settles one annual electricity term. Records include `ro_levy_gbp`, `cfd_levy_gbp`, `policy_cost_gbp`. |
| `gas_settlement.py` | `run_gas_term()`: settles one annual gas term. NBP-priced monthly. |
| `policy_costs.py` | RO and CfD levy lookup tables (2016–2024); `get_electricity_policy_cost_per_mwh()` |
| `settlement.py` | Shared constants: `CONTRACT_LENGTH_DAYS = 365`, settlement period helpers |
| `customer_events.py` | Churn events, home-move events, acquisition events with timestamps |
| `renewals.py` | Contract renewal decision: churn roll, home-move, bill-shock check; policy cost pass-through at term build |
| `demand_model.py` | Demand shape dispatch: PC1/PC3 for non-HH, actual data for HH customers |
| `hh_consumption.py` | Half-hourly consumption reader for C7–C9 smart-meter customers |
| `tou_periods.py` | Time-of-use period classifier: peak (07:00-11:00, 16:00-20:00 weekdays), off-peak |
| `weather_inputs.py` | `weather_means_for_customer()`, `lookback_mean_temps()` — weather data adapters |
| `portfolio_pnl.py` | Portfolio-level P&L aggregation helpers |
| `run_phase0b.py` ... `run_phase3c_calibration.py` | Phase exploration runs (historical artefacts; not used in current pipeline) |

### `saas/` — Company Layer

| File | What it does |
|---|---|
| `customers.py` | Named customer roster: C1–C9 (electricity), C1g–C4g (gas). EAC, location, segment. |
| `tariff_pricing.py` | Fixed-tariff pricing: unit rate calculation from forward price + margin target |
| `bill_generator.py` | Itemised bill: unit rate × consumption + standing charge + non-commodity + VAT |
| `non_commodity.py` | Network charges + levies by segment: DUoS, TNUoS, BSUoS, RO, FiT, CfD, CM |
| `ledger.py` | Transaction journal: every financial event as a typed ledger entry |
| `payment_behaviour.py` | Payment timing, late payment, bad-debt provision (2% resi, 1% SME) |
| `contact_model.py` | Complaint probability from bill clarity score |
| `churn_model.py` | Bill-shock churn model (>20% YoY increase) with renewal probability |
| `clv_model.py` | Shifted-BG CLV via PyMC-Marketing; per-billing-account expected lifetime revenue |
| `clv_seed.py` | CLV prior seeding from initial acquisition data |
| `home_move_win_rate.py` | Probability of retaining a moving customer |
| `cost_to_serve.py` | Annual cost-to-serve: overhead per customer + bad-debt provision |
| `enterprise_value.py` | Portfolio enterprise value: sum of CLV across all billing accounts |
| `growth_mandate.py` | Growth mandate config: `flat`/`growth`; fixed cost monthly; acquisition spend |
| `customer_reaction.py` | Customer reaction to billing events: complaint, churn signal |
| `property_model.py` | Property characteristics for weather correlation (home type, bedrooms, EPC) |
| `reporting/annual_report.py` | Named-customer annual report generator (2,500+ lines) |
| `reporting/segment_report.py` | Segment portfolio annual report generator |

### `company/` — Company/SIM Boundary
- `billing/invoice.py`: invoice data type
- `crm/customer_registry.py`: customer lookup interface
- `crm/event_log.py`: `CompanyEventLog` with `ChurnEvent`, `AcquisitionEvent`, `RetentionEvent`
- `crm/churn_model.py`: company churn estimator — bill-shock + bill-burden + hedge-fraction signals
- `finance/pnl.py`: P&L aggregation (reads from ledger)
- `interfaces/sim_interface.py`: the seam between company and simulation. Company reads settlement records via this interface; cannot access raw simulation internals.
- `pricing/tariff_engine.py`: company-only forward price estimator — 120d lookback, adaptive window, seasonal adjustment, regime detection, portfolio premium
- `pricing/margin_feedback.py`: per-customer recovery surcharge when prior term lost >5% of revenue

### `background/` — Autonomous Stack
See Section 5 above.

### `tools/`
- `publish_report_gist.py`: commits report to main → Pages live in ~2 min; also posts Gist
- `generate_hh_data.py`: generates synthetic HH CSV files for C7–C9
- `delegate_ollama.py`: wrapper for Qwen3 code generation calls via Ollama
- `stamp_latest_md.py`: updates timestamp in LATEST.md

### `tests/` — 787 tests across 35+ test modules
```
saas/          ~280 tests (bill_generator, churn, CLV, contact, CTS, customers,
                           enterprise_value, growth_mandate, home_move, ledger,
                           payment_behaviour, property_model, tariff_pricing,
                           annual_report, segment_report)
background/    126 tests  (autonomous_runner, dispatcher, file_api, health_check,
                           ntfy_responder, ntfy_utils, session_watchdog, sim_runner,
                           staging_watcher)
simulation/    ~130 tests (customer_events, customer_events_basis_risk, demand_model,
                           hh_consumption, policy_costs, renewals, run_phase2b,
                           run_phase3b_regression, run_phase4c, segments, weather_inputs)
sim/            51 tests  (forward_curve, generation_demand_history, hedging_strategy,
                           price_engine, risk_committee_agent, risk_engine,
                           weather_engine, weather_price_sensitivity)
company/       ~170 tests (invoice, customer_registry, pnl, sim_interface, churn_model,
                           event_log, tariff_engine, margin_feedback, churn_via_live)
tools/           2 tests
```

---

## 7. Key Documents

| Document | Location | Purpose |
|---|---|---|
| `CLAUDE.md` | repo root | Primary agent anchor: architecture, principles, key learnings, current state |
| `STATUS.md` | repo root | Expanded current state including all five hollow gaps |
| `docs/status/LATEST.md` | also GitHub Pages | Mobile snapshot: current phase, latest results, stack status |
| `docs/reports/ANNUAL_REPORT.md` | also GitHub Pages | Operator-facing annual report (latest named-customer run) |
| `docs/reports/REPORTING_BACKLOG.md` | repo | Prioritised reporting improvement queue; all 15 items tracked (11 closed) |
| `docs/market_research/ASSUMPTIONS.md` | also GitHub Pages | Living log of simulation assumptions vs real UK benchmarks |
| `docs/simulation-strategy.md` | repo | Detailed phase-by-phase narrative of hedging strategy evolution |
| `docs/calibration/price-engine.md` | repo | Forward price calibration methodology and findings |
| `docs/calibration/weather-engine.md` | repo | Weather model calibration and fitting notes |
| `docs/instructions/MASTER_BACKLOG.md` | repo | Phase execution instructions (internal to agent) |
| `docs/instructions/NTFY_TWO_WAY_PROTOCOL.md` | repo | NTFY communication protocol specification |
| `docs/staging/` | repo | Active instruction queue (Rich's staged instructions + run_complete markers) |
| `docs/observability/PHASE_10a_SUMMARY.md` | repo | Phase 10a design decisions, findings, open questions |

---

## 8. The Five Hollow Gaps (Progress)

These were identified early as the things that make the simulation feel like a *model* rather than an *operating company*:

| Gap | Status | Phase closed |
|---|---|---|
| 1. No customer events actually firing | **CLOSED** | Phase 6b/7e: churn events, replacement onboarding, event log |
| 2. No ledger | **CLOSED** | Phase 7a/7b: 2.2M transaction events, waterfall, bad-debt posting |
| 3. SIM/company barrier structural not functional | **DEEPENED** | Phase 11a+11b+12a–22b: company has own tariff engine, churn model, event log, retention, margin feedback, portfolio premium, regime detection, hedging policy (Phase 22b). Level 2 (decision boundary) now closed for all major decisions. |
| 4. HH smart meter data path never built | **CLOSED** | Phase 6a: C7–C9 on real HH consumption, demand model dispatches both paths. ToU tariffs active (Phase 13a). |
| 5. Reporting only recently added | **CLOSED** | Phase 5a/5b: full annual report pipeline, GitHub Pages, NTFY digest. 2,500+ line annual report with 20+ analytical sections. |

---

## 9. Known Gaps & Open Questions

### Consumption calibration
~~C1 2,800→2,500 kWh/yr and C5 25,000→15,000 kWh/yr~~ — **done (Phase 21c)**. Subsequent terms auto-correct via settlement-derived EAC (Phase 25a). Remaining: C2/C3/C4 resi EAC not yet benchmarked against Ofgem TDCV segmented by dwelling type.

### Policy costs still use settlement-date lookup only
Phase 21a adds RO + CfD. Network charges (DUoS ~£15–20/MWh, TNUoS ~£5–8/MWh) still modeled as flat pass-through in `non_commodity.py` rather than year-indexed actuals. Future phase target.

### ~~BSC credit cover not modeled as working capital~~ — CLOSED Phase 53
`saas/capital/bsc_credit.py` computes peak daily wholesale × 1.2 buffer; 2022 crisis shows 363× increase vs 2016.

### ~~Solvency / per-customer net assets~~ — CLOSED Phase 55
`saas/capital/solvency.py`: `compute_solvency_signal(treasury, customers)` → OK/Watch/STRESS. MCR floor £130/dual-fuel account; Watch < 2×, STRESS < 1×. MCR ratio column in annual report.

### Company layer full operational independence
The `company/` layer has own models (tariff engine, churn model, event log, retention decisions, margin feedback). But it still shares code-execution paths with SIM — it is not a fully independent runtime. True operational independence (company runs its own end-to-end simulation against observable market data only) is the long-horizon goal.

### Smart meter customers on PC shapes (segments)
C7–C9 named customers have synthetic HH data. The segment model's "smart" segments (resi_smart, sme_smart) still use PC1/PC3 shapes. True half-hourly shapes for smart segments are deferred.

### EPC-calibrated consumption distributions
29.2M EPC records available via GOV.UK (requires One Login for bulk). Would calibrate consumption to actual property stock distribution. Future phase target.

---

## 10. The Numbers at a Glance

**Codebase:**
- 303+ Python modules (company layer), ~47,500 lines total
- 420+ git commits
- 5,623 tests (fast / ~10s; simulation integration ~8 min per run)

**Data:**
- 168,026 real Elexon SSP records (2015–2025, 123 MB)
- 3,446 NBP daily gas prices (2016–2025)
- 9 HH smart meter profiles (C7–C9 residential, C_IC1–C_IC4 I&C at 1–4 GWh/year)

**Latest full run (Phase AG, 2026-06-30):**
- Net margin £1,243,337 (treasury change) | Gross £6,462,146 | EV £6,037,509 | SURVIVED
- 5,623 tests. Phase DG: Consumer Vulnerability Register (23). Phase DF: SAR Register (32). Phase DE: EBSS (28). Phase DD: EBRS (28). Phase DC: EMIR (29). Phase DB: ICO Breach (33).

**Simulation complexity:**
- 165,000+ settlement periods (9.5 years × 48 HH/day)
- Full cost stack: wholesale (SSP) + network (DUoS+TNUoS, Phase 29b) + policy (RO+CfD+CCL+CM+FiT+Mutualization, Phase 21a/27b/30a/31a/54) + Ofgem cap (resi, Phase 47a)
- Risk committee Ollama calls per run (each ~7s) — 95% of runtime

---

## 11. Why PROJECT_OVERVIEW.md Didn't Auto-Update

**Investigation (2026-06-21 — response to Rich's NTFY):**

This document was dated 2026-06-20 at 543 tests while we were actually at Phase 21a with 787 tests. Here is why, and what the right fix is.

**What the run-complete pipeline does:**
`background/process_run_complete.py` regenerates `ANNUAL_REPORT.md` and updates `LATEST.md` on every completed simulation run. Those are **run output documents** — they change every run because simulation results change every run.

**Why PROJECT_OVERVIEW.md should NOT be in the run-complete pipeline:**
This document is a **project state document** — it describes architecture, build history, design decisions, and phase milestones. These don't change when a new simulation run completes; they change when new code phases ship. Updating PROJECT_OVERVIEW.md on every run would:
1. Overwrite meaningful narrative with auto-generated stubs
2. Update test counts and financials but not architecture changes (which is what makes it stale)
3. Create spurious commits on every run (~5 times per day)

**The real problem:** PROJECT_OVERVIEW.md should be updated at phase close, not at run complete. The phase commit is the right trigger. The document fell behind because phase close didn't include a step to update it.

**The fix:**
- Add `docs/PROJECT_OVERVIEW.md` to the phase-close checklist in `CLAUDE.md`
- Specifically: update test count, latest run figures, and add a build history entry at the end of each phase
- LATEST.md and ANNUAL_REPORT.md: auto-updated by run-complete pipeline (correct)
- PROJECT_OVERVIEW.md: updated manually at phase close by the orchestrator (correct)

This distinction also applies to CLAUDE.md's "Current state" section, which serves a similar function for the agent itself.

---

## 12. Agent Architecture (as of 2026-06-23)

The project runs a multi-layer agent architecture. This section describes it as it now exists after Architecture Stages 0-4.

### Layer 1 — Orchestrator

**Claude Code (Sonnet 4.6)** is the lead orchestrator. It reads staged instructions, designs solutions, delegates implementation to Qwen, reviews outputs, runs tests, and manages the build. All frontier token spend goes here — reasoning, design, review, and delegation.

### Layer 2 — Code-Domain Subagents (.claude/agents/)

Defined in `.claude/agents/`. These are Claude Code subagents with scoped tools and domain-specific instructions.

| Agent | Definition | Scope |
|---|---|---|
| `sim-engineer` | `.claude/agents/sim-engineer.md` | `sim/` — historical data, forward curves |
| `saas-engineer` | `.claude/agents/saas-engineer.md` | `saas/` — billing, CLV, churn, CRM |
| `interface-steward` | `.claude/agents/interface-steward.md` | `company/interfaces/` — SIM/company seam |
| `discovery-agent` | `.claude/agents/discovery-agent.md` | `docs/market_research/` — assumption validation |
| `epistemic-verifier` | `.claude/agents/epistemic-verifier.md` | Read-only — scans diffs for barrier violations |

### Layer 3 — Background Daemons (background/)

Long-running systemd user processes. All emit structured status to `docs/observability/agent_status.json` (schema v1) and appear on the poesys.net System health panel.

| Daemon | Role | Produces |
|---|---|---|
| `sim_runner` | Continuously re-runs full simulation | `run_complete_*.md` staging markers |
| `autonomous_runner` | Runs Claude `--print` turns | Published reports, LATEST.md updates |
| `ntfy_responder` | Receives Rich's NTFY messages | `from_rich_*.md` staging files |
| `staging_watcher` | Monitors `docs/staging/` | Alerts when new instructions arrive |
| `session_watchdog` | Detects Claude usage-limit pauses | Session resume signals |
| `dispatcher` | Routes NTFY by urgency | Urgent → wake session, normal → queue |
| `discovery_agent` | Background market research | ASSUMPTIONS.md updates |
| `background_worker` | General background task queue | Varies |

### Layer 4 — Execution Engine

**qwen3:14b via Ollama** handles all code generation. Receives edits, specs, and file content from the orchestrator; returns implementations. No frontier token spend.

**Risk committee agent** runs during simulation via Ollama. Local only — no frontier API spend in simulation runs.

### Observability Layer

`docs/observability/agent_status.json`: structured JSON updated by all 8 daemons (schema v1).
Fields per agent: `name`, `role`, `status`, `last_heartbeat`, `last_action`, `last_action_ts`, `anomaly`, `produces`.

`site/data/agent_status.json`: mirrored to Cloudflare Pages, rendered on poesys.net System tab.
Green = heartbeat <1h, Amber = 1-6h, Red = >6h or status=error.

### Inter-Agent Message Protocol

`background/agent_protocol.py`: `AgentMessage` dataclass with `IntentType` enum (9 known intents).
Additive — does not replace NTFY or staging file formats. Used for new structured communication going forward.
First live usage: `sim_runner.py` emits `AgentMessage(intent="run_complete")` on each successful run.

### Epistemic Barrier

`company/interfaces/sim_interface.py` is the only approved crossing point between company layer and simulation.
`tools/epistemic_verifier.py` scans company/ code for barrier violations at phase close.
Any direct import from `sim/` or `simulation/` in company code is a violation.

