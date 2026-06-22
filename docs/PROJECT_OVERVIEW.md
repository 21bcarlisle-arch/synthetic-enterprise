# Synthetic Enterprise — Project Overview & Audit

*Last updated: 2026-06-22. 320+ commits. 867 tests (~853 in SIM_FAST_MODE=1). Codebase: ~17,450 lines across 184+ Python modules.*

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
| 3. SIM/company barrier structural not functional | **DEEPENED** | Phase 11a+11b+12a–21a: company has own tariff engine, churn model, event log, retention decisions, margin feedback, portfolio premium, regime detection. Divergence from SIM ground truth formally measured (Phase 12e). |
| 4. HH smart meter data path never built | **CLOSED** | Phase 6a: C7–C9 on real HH consumption, demand model dispatches both paths. ToU tariffs active (Phase 13a). |
| 5. Reporting only recently added | **CLOSED** | Phase 5a/5b: full annual report pipeline, GitHub Pages, NTFY digest. 2,500+ line annual report with 20+ analytical sections. |

---

## 9. Known Gaps & Open Questions

### Consumption calibration
Current C1 residential electricity EAC is 2,800 kWh/yr; Ofgem TDCV medium is 2,500 kWh/yr. SME C5 is 15,000 kWh/yr vs real 8,500–25,000 kWh/yr microbiz range. Recalibration planned (Phase 21c).

### Policy costs still use settlement-date lookup only
Phase 21a adds RO + CfD. Network charges (DUoS ~£15–20/MWh, TNUoS ~£5–8/MWh) still modeled as flat pass-through in `non_commodity.py` rather than year-indexed actuals. Future phase target.

### BSC credit cover not modeled as working capital
Real suppliers hold BSC credit cover as a working capital requirement (~£8–15/MWh × peak exposure). Not yet in treasury model. Future phase target.

### Solvency / per-customer net assets
Ofgem licence requires positive net assets per customer (floor: £0; target: £130/dual-fuel customer). Not yet computed or tracked in reporting. Future phase target.

### Company layer full operational independence
The `company/` layer has own models (tariff engine, churn model, event log, retention decisions, margin feedback). But it still shares code-execution paths with SIM — it is not a fully independent runtime. True operational independence (company runs its own end-to-end simulation against observable market data only) is the long-horizon goal.

### Smart meter customers on PC shapes (segments)
C7–C9 named customers have synthetic HH data. The segment model's "smart" segments (resi_smart, sme_smart) still use PC1/PC3 shapes. True half-hourly shapes for smart segments are deferred.

### EPC-calibrated consumption distributions
29.2M EPC records available via GOV.UK (requires One Login for bulk). Would calibrate consumption to actual property stock distribution. Future phase target.

---

## 10. The Numbers at a Glance

**Codebase:**
- 177 Python modules, ~16,000 lines
- 306 git commits
- 867 tests (all green); ~853 in SIM_FAST_MODE=1; 867 in full suite (~40 min with Ollama)

**Data:**
- 168,026 real Elexon SSP records (2015–2025, 123 MB)
- 3,446 NBP daily gas prices (2016–2025)
- 4 HH smart meter profiles (C7–C9 residential, C_IC1 I&C at 2 GWh/year)

**Latest named-customer run (git 2f380ac, 10 customers incl C_IC1, 2016–2025):**
- Revenue undisclosed in run_output_latest.json aggregate | Net margin £225,920 (ledger)
- Gross margin £235,160 | Capital charges £9,240
- Treasury £463,166 → £465,105 | 236 risk committee interventions | 1,165 bills
- Enterprise value: £309,282 | 23 retention offers / 19 retained | 7 accounts ever churned

**Simulation complexity:**
- 165,000+ settlement periods (9.5 years × 48 HH/day)
- 323 risk committee Ollama calls per run (each ~7s) — 95% of 38-min runtime
- Full test suite: 867 tests, ~16s with SIM_FAST_MODE=1

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
