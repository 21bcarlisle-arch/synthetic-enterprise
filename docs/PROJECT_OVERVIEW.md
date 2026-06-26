# Synthetic Enterprise — Project Overview & Audit

*Last updated: 2026-06-26. 400+ commits. 2,156 tests (1,728 non-simulation, 428 simulation). Codebase: ~31,700 lines across 241+ Python modules.*

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
- 200+ Python modules, ~22,500 lines
- 400+ git commits
- 2,156 tests (1,728 fast / ~10s; simulation integration ~8 min per run)

**Data:**
- 168,026 real Elexon SSP records (2015–2025, 123 MB)
- 3,446 NBP daily gas prices (2016–2025)
- 9 HH smart meter profiles (C7–C9 residential, C_IC1–C_IC4 I&C at 1–4 GWh/year)

**Latest full run (Phase 127, 2026-06-27):**
- Net margin £1,330,126 | Gross £6,546,003 | Revenue £14,215,256 | Treasury £3,796,762 | SURVIVED
- 17 new tests: Portal Phase 2 tariff comparison (3 tariff options sorted by cost, switch request flow).

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

