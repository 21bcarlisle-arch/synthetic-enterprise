# CLAUDE.md — Synthetic Enterprise

## What this project is

A high-fidelity simulation of a fully autonomous UK energy supply business, operating against
real Elexon/NESO half-hourly settlement data. The business layer cannot see future data
(Point-in-Time Blindfold, strictly enforced). Goal: detailed enough to say "that is how a
real UK energy supplier works."

→ Architecture, module inventory, build history: `docs/PROJECT_OVERVIEW.md`

---

## Who does what

- **Rich** — MD/board. Stages instructions in `docs/staging/`. Staging = approval. Does not write code.
- **Claude Code** — lead orchestrator. Designs, delegates, reviews, manages build.
- **qwen3:14b (Ollama)** — all code generation and mechanical execution. Frontier tokens for reasoning only.
- **Risk committee** — local Ollama only. No frontier API spend in simulation runs.

---

## How to operate autonomously

**NTFY is the primary communication channel.** Rich uses it for steering and quick direction changes.
- `background/ntfy_responder.py` writes inbound messages (>25 chars) to `docs/staging/from_rich_TIMESTAMP.md`
- After acting on a `from_rich_*.md` message, reply via `background.ntfy_utils.send_ntfy`.
- Move actioned files to `docs/staging/done/` after processing.

**At startup and after every completed task:** poll `docs/staging/` and action unread files immediately.
- `run_complete_*.md` — publish results (regenerate report, LATEST.md, dashboard.json), commit, push,
  archive. **Do NOT send NTFY for routine sim run completions.** Only NTFY for notable exceptions
  (admin event, all-time high/low margin). Batch silently if multiple queued.
- `run_pending_*.md` — check if finished and act accordingly.
- `from_rich_*.md` — action it, reply via NTFY, archive.

**At every REVIEW_GATE:**
1. Complete phase and commit all outputs.
2. NTFY Rich with what was done and what's next.
3. Proceed immediately to the next phase — do not hold for confirmation.
4. Rich redirects via NTFY if he wants a different direction.

**Always update and commit LATEST.md before sending NTFY.** If stale, fix the root cause.

**When budget is available between tasks:** check backlog, fix known issues, improve coverage. Don't sit idle.

---

## Phase-close checklist (in order)

1. Update test count + latest run figures in PROJECT_OVERVIEW.md Section 10.
2. Add build history entry in PROJECT_OVERVIEW.md Section 4.
3. **Run epistemic verifier:** `python3 -m tools.epistemic_verifier` — must PASS before committing.
   If FAIL: fix violations before committing any phase-close output.
4. **`wc -c CLAUDE.md` — hard limit 35,000 chars / 200 lines.** If over: move phase details to
   `docs/claude/phase-history.md`. Never accumulate phase details in CLAUDE.md.
5. Add one-line phase completion entry to CLAUDE.md "Current state".
6. Commit and push.

PROJECT_OVERVIEW.md is updated at phase close. Run-complete pipeline does NOT update it.

---

## Current state

**Phase 278 COMPLETE (2026-06-26):** Dashboard Monthly Ops tab -- 11 new tests (3,582 passing). tools/generate_dashboard_data.py: extract_monthly_ops() aggregates bill_shock_events/committee_wake_ups/retention_log by calendar month; fields: shock_count/avg_shock_pct/max_shock_pct/committee_interventions/retention_offers/retained/is_crisis. site/index.html: Monthly tab with 4 KPI cards (total shocks/crisis shocks/worst month/committee meetings), Chart.js bar+line chart (shocks in red/blue by crisis, committee as overlay line), full 103-month operational timeline table. dashboard.json: monthly_ops key injected. Closes Dashboard Phase E.
**Phase 277 COMPLETE (2026-06-26):** Tariff Smoothing Book -- 11 new tests (3,571 passing). company/pricing/tariff_smoothing.py: SmoothedRateStatus (BELOW_COST/AT_COST/MARGINAL/PROFITABLE), TariffDecision (frozen: year/commodity/unit_rate/wholesale_cost/smoothing_reserve; gross_margin_p_per_kwh/is_loss_making/status), TariffSmoothingBook (record_decision/decisions_for_commodity/loss_making_years/max_bill_shock_pct/smoothing_summary). Crisis 2022 scenario: rate=30p/kWh vs cost=35p/kWh = loss-making year. Closes tariff smoothing backlog item.
**Phase 276 COMPLETE (2026-06-26):** BM Settlement tab on /sim/ -- 10 new tests (3,560 passing). tools/generate_sim_data.py: _bm_monthly_aggregation() extracts monthly mean_ssp/mean_sbp/spread/max_ssp/mean_niv_mwh/short_pct/is_crisis from existing SSP cache (SBP and NIV already in 168k-record Elexon dump). site/sim/index.html: BM Settlement 3rd tab; 4 KPI cards (2022 avg short%, 10-yr avg short%, highest short% month, peak BM price); monthly Short% bar chart (crisis red/normal blue); dual-axis SSP+Short% chart; annual NIV direction table with NET LONG/SHORT status.
**Phase 275 COMPLETE (2026-06-26):** Green Claims Audit test coverage -- 12 new tests (3,550 passing). company/compliance/green_claims_audit.py (existing): REGO compliance auditor cross-checking green product consumption vs REGO portfolio. Added tests/company/compliance/test_green_claims_audit.py (new, zero-coverage gap closed): COMPLIANT/AT_RISK/NON_COMPLIANT status paths; wrong-year REGO exclusion; coverage cap at 100%; summary_lines format; penalty_estimate_gbp when shortfall; non-green product codes correctly ignored.
**Phase 274 COMPLETE (2026-06-26):** Life Event Impact Assessor -- 12 new tests (3,538 passing). company/crm/life_event_impact.py: ImpactSeverity (LOW/MODERATE/HIGH/CRITICAL), LifeEventImpact (frozen: severity/consumption_delta_pct/triggers_psr_review/vulnerability_flag/recommended_actions/is_urgent/to_dict), LifeEventImpactAssessor (assess/batch_assess/urgent_impacts/psr_candidates/summary). All 11 LifeEventTypes mapped: SERIOUS_ILLNESS=CRITICAL+PSR, JOB_LOSS=HIGH+15% consumption, RETIREMENT=PSR+12%, BIRTH=+8%, JOB_GAIN=-10%. Connects life_events (base) + priority_services (Ph) + vulnerability_index (Ph243).
**Phase 273 COMPLETE (2026-06-26):** Management Accounts Dashboard Tab -- 10 new tests (3,526 passing). tools/generate_dashboard_data.py: extract_management_accounts() extracts 10-year P&L waterfall from management_accounts key in run output (revenue/wholesale/non_commodity/gross_margin/capital/bad_debt/cost_to_serve/fixed/acquisition/total_opex/net_margin + net_margin_pct); wired into generate() as management_accounts key in dashboard.json. site/index.html: Accounts tab with stacked cost-vs-revenue bar+line chart and full P&L waterfall table; 2021/2022 crisis rows highlighted amber.
**Phase 272 COMPLETE (2026-06-26):** Physical Home Registry -- 12 new tests (3,516 passing). company/crm/home_registry.py: HomeRegistry class wrapping existing Property dataclass; register/upgrade_epc/get_profile/profiles_by_epc/profiles_by_type/eco4_eligible_accounts/fuel_poor_accounts/psr_priority_accounts/epc_distribution/fuel_distribution/tenure_distribution/registry_summary. Connects property_model (Ph base) + property_improvement (Ph251) + vulnerability_index (Ph243) into unified home portfolio view.
**Phase 271 COMPLETE (2026-06-26):** Weather Engine & HDD tab on /sim/ -- 10 new tests (3,504 passing). tools/fetch_weather_data.py: Open-Meteo 2016-2025 London temps, monthly HDD (base 15.5C National Grid). site/sim/index.html: Prices/Weather tabs; 10-yr monthly temp chart + HDD bar chart + annual table with COLD WINTER badge + crisis narrative. Critical NTFY spam fix: generate_insights stored ledger gross (~6.3M) vs total_net (~1.3M) in run_history, every run triggered [NEW LOW]; fixed to use total_net_gbp consistently + cleared history.
**Phase 270 COMPLETE (2026-06-26):** Local NL Query via Qwen3/Ollama -- 7 new tests (3,494 passing). POST /query added to background/file_api.py: calls qwen3:14b via Ollama with /no_think prefix (fast, zero API cost, Tailscale-only). site/index.html: fetch URL changed to https://skynet-1.taila062fa.ts.net:8765/query. start_worker.sh: file-api added as managed tmux session. Also fixed: supplier dashboard onkeydown JS syntax error (Ph266), customer portal login double-quote JS bug (Ph263), process_run_complete.py race condition + relative path.
**Phase 269 COMPLETE (2026-06-26):** Customer Portal Billing Year Filter -- 8 new tests (3,487 passing). Year selector buttons (2016-2025 + All) on the Bills section. renderBills() function shows filtered invoices most-recent-first, total spend KPI, and outstanding (UNPAID) amount in amber. BILL_YEAR state + filterBillYear() for re-render.
**Phase 268 COMPLETE (2026-06-26):** /sim/ Section: Wholesale Price Explorer -- 10 new tests (3,479 passing). generate_sim_data.py processes 168,026 HH Elexon SSP records into monthly/annual aggregates + peak records. site/sim/index.html: Chart.js monthly price chart (mean + P95 + crisis zone overlay), 6 KPI cards, annual table with CRISIS badges, top-10 peak SSP table. Peak: 4,037/MWh (Sep 2021); 2022 mean 199.50 vs 2016 39.41 = 5x crisis multiple. Nav /sim/ link un-dimmed across all 5 pages. generate_sim_data wired into process_run_complete.
**Phase 267 COMPLETE (2026-06-26):** Dashboard Phase B Completion: Year filter on Financial/Trading/Customers tabs -- 8 new tests (3,469 passing). yearBtnsHtml() helper (reusable year selector bar). mkChart() now destroys existing Chart.js instances before re-creating (required for tab re-render). selectYear() clears rendered cache for the three filterable tabs and re-renders if active. Financial tab: filters annual P&L data + charts to selected year. Trading tab: filters spot_monthly by month prefix + hedge_annual by year. Customers tab: filters book_annual, heatmap shows only selected year column, events + retention filtered. All tabs degrade to full 10-year view on All.
**Phase 266 COMPLETE (2026-06-26):** Dashboard Phase D: "Talk to the Data" NL query interface -- 9 new tests (3,461 passing). extract_query_context() in generate_dashboard_data.py builds a compact 2.6k char text summary (portfolio totals, annual P&L, customer lifetime margins, retention/operations) stored as query_context in dashboard.json. functions/api/query.js (new): Cloudflare Pages Function proxying NL questions to claude-haiku-4-5-20251001 (ANTHROPIC_API_KEY env var). "Query" tab added to poesys.net with question input, 5 example queries, chat-style answer history. Context auto-loads from dashboard.json.
**Phase 265 COMPLETE (2026-06-26):** NTFY notable-exception digest -- 6 new tests (3,452 passing). background/process_run_complete.py: _run_history_max_net() reads run_history to find prior best; maybe_ntfy(data, net, insights=None): sends NTFY only for admin events, new all-time-high (>1% over prev best), or new all-time-low (<50% of prev best when prev_best>1M); digest includes executive_summary + top recommended_action. Normal runs remain silent (CLAUDE.md standing policy). tests/tools/test_ntfy_digest.py (new).
**Phase 264 COMPLETE (2026-06-26):** Invoice generation for customer portal -- 9 new tests (3,446 passing). tools/generate_invoice_data.py (new): synthetic monthly invoice records from per-customer lifetime revenue; seasonal weighting (gas winter-heavy, elec mild peak); standing charge added; last invoice UNPAID, all prior PAID; I&C uses higher daily standing charge (£1.20/day vs £0.28). Customer JSONs updated: C1 = 120 invoices @ ~£43/month; C_IC1 = 108 invoices @ ~£35k/month. process_run_complete.py: generate_invoice_data called on every run. Portal /customers/ now shows full billing history for all 19 accounts.
**Phase 263 COMPLETE (2026-06-26):** Four-section site restructure (poesys.net) -- 13 new tests (3,437 passing). site/customers/index.html (new): static customer portal with login (account ID only), account summary, lifetime P&L; site/project/index.html (new): about, investor summary card, 4 key discoveries, test/phase velocity charts, roadmap; site/data/customers/{id}.json (new, 19 accounts): per-customer static JSON from run output; site/data/phases.json (new): phase/test progression for velocity charts; tools/generate_customer_data.py (new): generates per-customer JSON; Nav bar added to all pages (site/index.html, timeline, staging-status); process_run_complete.py: customer JSON regenerated on every run; Gate: poesys.net/customers/ (log in as C1), poesys.net/project/ (investor summary + charts), nav visible on all pages.
**Phase 262 COMPLETE (2026-06-26):** Run History table (Dashboard Phase B) -- 6 new tests (3,424 passing). tools/generate_insights.append_run_history(): guards blocking non-hex hashes and non-positive net margins (prevents test artifacts). tools/generate_dashboard_data.extract_run_history(): max_entries=10 slice, empty on missing. dashboard.json: run_history key. site/index.html renderInsights(): Run History table (hash/net margin/date) below recommended actions.
**Phase 261 COMPLETE (2026-06-26):** Year Spotlight (Dashboard Phase B partial) -- 5 new tests (3,418 passing). site/index.html: YEAR_FILTER state + year-btn CSS + selectYear()/renderSpotlight() JS functions; Overview tab: year selector buttons (2016-2025 + All) + spotlight card (net margin, gross, revenue, treasury, bill shocks, worst shock, active elec, avg hedge %) with CRISIS YEAR badge for 2021/2022. tests/tools/test_year_spotlight.py (new): all years present, crisis years in book_annual, bill_shock_count, hedge_annual, 2022 shocks >= 2020.
**Phase 260 COMPLETE (2026-06-26):** Strategic Coherence Infrastructure -- 0 new tests (3,413 passing). docs/PRIORITIES.md (new): living priority file, updated each session; seed with Ph 259-260 in Now, dashboard B/D in Next. site/staging-status/index.html (new): staged/actioned/done visibility at poesys.net/staging-status/. site/timeline/index.html (new): 299-phase git-log-extracted table + 2 velocity charts (phases-over-time, tests-over-time) + investor summary card at poesys.net/timeline/. Archives Coherence_and_velocity.md staging instruction.
**Phase 259 COMPLETE (2026-06-26):** Level 3 Coherence Executive Summary -- 6 new tests (3,413 passing). tools/generate_insights.py: RunInsights extended with coherence_narrative/recommended_actions; _generate_coherence() cross-area narrative (dominant theme, hedge/crisis/IC synthesis); 3 recommended actions always generated; PCL segment fix (net_gbp fallback, segment=="I&C" detection). Dashboard Insights tab: coherence card (teal border) + Recommended Actions card (amber border, numbered). Dashboardvision.md Phase C backbone.
**Phase 258 COMPLETE (2026-06-26):** Dashboard Insights tab -- 4 new tests (3,407 passing). site/index.html: Insights tab button + div + renderInsights() JS function. tools/generate_dashboard_data.py: extract_insights() loads run_insights.json into dashboard.json. tests/tools/test_generate_dashboard_insights.py (new): extract_insights absent/present/invalid-json/5-areas. Surfaces executive summary + 5 area narrative cards on poesys.net. Dashboardvision.md Phase A frontend complete.
**Phase 257 COMPLETE (2026-06-26):** Run Insight Generator ("so what" layer) -- 15 new tests (3,403 passing). tools/generate_insights.py (new): InsightArea (TRADING/CUSTOMERS/RISK/FINANCIAL/OPERATIONS), AreaInsight (frozen: area/headline/narrative/key_metrics), RunInsights (frozen: git_hash/generated_at/net_margin_gbp/executive_summary/insights). generate_insights()/save_insights()/append_run_history(). Integrated into process_run_complete.py: auto-generates structured narratives after every sim run. Stores run_insights.json (current) and run_history.json (cumulative). Dashboardvision.md Phase A: Level 2 insight layer.
**Phase 256 COMPLETE (2026-06-26):** Day-ahead electricity trading book (N2EX/EPEX SPOT UK) -- 15 new tests (3,388 passing). company/market/day_ahead_book.py (new): DayAheadDirection (BUY/SELL), DayAheadAuction (frozen: delivery_date/direction/volume_mwh/bid_price/cleared_price/auctioned_at; cost_gbp/vs_forward_spread_gbp_per_mwh/is_crisis_price >300), DayAheadBook (submit_auction/auctions_for_month/net_position_mwh/total_volume_mwh/total_cost_gbp/average_clearing_price/crisis_auctions/monthly_summary/day_ahead_summary). Closes trading timeline gap: forwards -> day-ahead -> intraday -> BM. 2022 crisis: DA cleared 400-600/MWh at winter peaks.
**Phase 255 COMPLETE (2026-06-26):** Customer Satisfaction Survey (CSS) tracker -- 12 new tests (3,373 passing). company/crm/css_tracker.py (new): CSSPerformanceBand (TOP >=7.8 / MID / BOTTOM <6.0), CSSResponse (frozen: 6 dimensions 1-10; composite_score weighted 30%/14%; would_recommend >=7.0; validation), CSSBook (record_response/annual_responses/avg_score/performance_band/vs_industry_avg/recommend_rate/css_summary). 2022 crisis: industry avg dropped to 5.2/10 -- highest volume of dissatisfied customers on record. Addresses Rich's request for "conversations" simulation.
**Phase 254 COMPLETE (2026-06-26):** Ofgem Market Compliance Scorecard -- 12 new tests (3,361 passing). company/regulatory/compliance_scorecard.py (new): RAGStatus (GREEN/AMBER/RED), ComplianceDomain (10: GOVERNANCE/BILLING_METERING/PAYMENT_DEBT/INFO_TRANSPARENCY/COMPLAINTS/VULNERABLE_CUSTOMERS/TARIFF_PRICE_CAP/ENVIRONMENTAL/NETWORK_BALANCING/FINANCIAL_RESILIENCE), ComplianceCheck (frozen: domain/status/metric_value/threshold; slc_reference/is_breach), ComplianceScorecard (record_check/latest_status/overall_rag/breaches/scorecard_summary). Temporal filtering: future checks excluded from as_of_date summary. Maps to SLC cluster references per domain.
**Phase 253 COMPLETE (2026-06-26):** Wholesale gas OTC trading book (NBP) -- 13 new tests (3,349 passing). company/market/gas_otc_book.py (new): GasTenor (WITHIN_DAY/DAY_AHEAD/MONTH_AHEAD/SEASON_AHEAD), GasTradeDirection (BUY/SELL), Season (SUMMER Apr-Sep/WINTER Oct-Mar), GasOTCTrade (frozen: volume_mwh=therms*0.02931/trade_value_gbp/is_crisis_price >200p/th/delivery_season), GasOTCBook (record_trade/trades_by_delivery_month/net_position_therms/average_buy_price_p_th/crisis_trades/seasonal_exposure_therms/gas_book_summary). 2022 crisis: NBP hit 600+ p/th vs 50-70 normal.
**Phase 252 COMPLETE (2026-06-26):** Customer behaviour segmentation model -- 14 new tests (3,336 passing). company/crm/behaviour_segment.py (new): PaymentBehaviour (EXEMPLARY/RELIABLE/OCCASIONAL_MISS/CHRONIC_LATE), EngagementLevel (HIGHLY_ENGAGED/ENGAGED/PASSIVE/DISENGAGED), SwitchingRisk (HIGH/MEDIUM/LOW), CustomerSegment (CHAMPION/LOYAL/AT_RISK/STRUGGLING/DISENGAGED_STABLE/CHURNER + recommended_intervention), BehaviourProfile (frozen: derived from payment_on_time_rate/portal_logins_per_month/months_since_last_switch/paper_free), BehaviourSegmentBook (record_profile/latest_profile/segment_counts/at_risk_customers/segment_summary). Addresses Rich's request for behaviour simulation.
**Phase 251 COMPLETE (2026-06-26):** Property improvement event tracker -- 12 new tests (3,322 passing). company/crm/property_improvement.py (new): MeasureType (10: CAVITY_WALL/SOLID_WALL/LOFT/HEAT_PUMP_ASH/HEAT_PUMP_GSH/SOLAR_PV/SMART_METER/BOILER/DOUBLE_GLAZING/DRAUGHT_PROOFING), FundingScheme (6: ECO4/BUS/HUG2/SEG/PRIVATE/GBIS), PropertyImprovement (frozen: grant_gbp/customer_cost_gbp/annual_elec_saving_kwh/annual_gas_saving_kwh/epc_points_gained/simple_payback_years), PropertyImprovementBook (record_improvement/for_customer/annual_improvements/total_grant_gbp/customers_upgraded_epc/improvement_summary). BUS grant £7,500 for heat pump; ECO4 cavity wall £2,500. Closes EPC improvement loop connecting decarb_recommender (Ph) to fuel poverty (Ph243).
**Phase 250 COMPLETE (2026-06-26):** Supplier Financial Resilience (SFR) book -- 11 new tests (3,310 passing). company/regulatory/sfr_book.py (new): SFRStatus (PASS/WATCH/BREACH/INVESTIGATION), SFRMetric (4: LIQUIDITY/CREDIT_BALANCE_COVER/HEDGE_RATIO/QUARTERLY_RETURN_FILED), SFRAssessment (frozen: liquidity_days/credit_balance_cover_pct/hedge_ratio_pct/return_filed; liquidity_status/hedge_status/credit_cover_status/overall_status/breach_metrics), SFRBook (record_assessment/file_return/latest_assessment/breach_quarters/sfr_summary). Thresholds: MLR >=30d (AMBER=30-40d, GREEN=40d+); hedge>=60% (AMBER=60-70%, GREEN=70%+). Post-2022 Ofgem requirement following 29 supplier failures.
**Phase 249 COMPLETE (2026-06-26):** Intraday electricity trading book -- 12 new tests (3,299 passing). company/market/intraday_book.py (new): TradeDirection (BUY/SELL), TradeReason (5: POSITION_BALANCING/DEMAND_FORECAST_REVISION/GENERATION_SHORTFALL/EMERGENCY_COVER/OPTIMISATION), IntradayTrade (frozen: settlement_period 1-48/volume_mw/price_gbp_per_mwh/traded_at; volume_mwh=volume*0.5/trade_value_gbp/is_crisis_price >£500/MWh), IntradayBook (record_trade/trades_for_date/net_position_mwh/daily_pnl_gbp/crisis_trades/average_buy_price/intraday_summary). 2022 crisis: intraday prices hit £4,000+/MWh at winter peaks.
**Phase 248 COMPLETE (2026-06-26):** CfD (Contracts for Difference) levy book -- 12 new tests (3,287 passing). company/market/cfd_levy.py (new): LevyDirection (POSITIVE/NEGATIVE/ZERO), CfDLevyCharge (frozen: account_id/charge_date/year/quarter/consumption_mwh/rate_gbp_per_mwh; levy_gbp/direction/is_credit), CfDLevyBook (record_charge/charges_for_account/annual_levy_gbp/quarterly_levy_gbp/total_credit_quarters/levy_summary), get_levy_rate() with 2016-2025 quarterly rates. 2022 crisis: levy went NEGATIVE Q2-Q4 (peak -£12.3/MWh Q4) -- generators repaid LCCC, reducing supplier bills. Connects to network_charge_ledger (Ph216).
**Phase 247 COMPLETE (2026-06-26):** Power Purchase Agreement (PPA) book -- 11 new tests (3,275 passing). company/market/ppa_book.py (new): PPATechnology (5: ONSHORE_WIND/OFFSHORE_WIND/SOLAR/HYDRO/BIOMASS), PPAPricingType (FIXED/INDEXED/FLOOR), PPAContract (frozen: capacity_mw/annual_generation_mwh/price_gbp_per_mwh; term_years/annual_cost_gbp/is_active/effective_price/vs_market_gbp), PPABook (add_contract/active_contracts/total_contracted_mwh/total_annual_cost_gbp/total_vs_market_gbp/ppa_summary). FLOOR pricing tracks market when above floor; fixed-price PPAs at £45/MWh were enormously valuable in 2022 (spot £200+/MWh).
**Phase 246 COMPLETE (2026-06-26):** Gas seasonal storage book -- 9 new tests (3,264 passing). company/market/gas_storage.py (new): StorageFacility (5: ROUGH 3,300 mcm mothballed May 2017 / STUBLACH / HOLFORD / HUMBLY_GROVE / HORNSEA), StorageOperation (INJECT/WITHDRAW), StorageTransaction (frozen: volume_mcm/price_gbp_per_therm/cost_gbp/is_winter_operation), GasStorageBook (inject/withdraw/inventory_mcm/total_injected_mcm/net_storage_cost_gbp/spread_gbp_per_therm/storage_summary). Rough closure cut UK seasonal capacity 70%; key cause of 2021-22 crisis exposure.
**Phase 245 COMPLETE (2026-06-26):** Capacity Market (CM) participation book -- 9 new tests (3,255 passing). company/market/capacity_market.py (new): CMUnitType (6: CCGT/OCGT/BATTERY/DSR/INTERCONNECTOR/PUMP), AuctionType (T4/T1), _CM_CLEARING_PRICE 2016-2025 (£18-£75 crisis peak), CMUnit (frozen: derated_capacity_kw), CMObligation (mutable: annual_revenue/apply_penalty/net_revenue), CapacityMarketBook (register/add_obligation/total_revenue/total_derated_kw/cm_summary). 2022 crisis: clearing price £75/kW vs £6.44 in 2020.
**Phase 244 COMPLETE (2026-06-26):** Customer contact preferences and channel management -- 9 new tests (3,246 passing). company/crm/contact_journey.py (new): ContactChannel (6: EMAIL/SMS/POST/PHONE/IN_APP/WEB), ContactPurpose (7: BILL/TARIFF_CHANGE/MARKETING/DEBT_CHASE/RENEWAL/SERVICE_UPDATE/COMPLAINT_UPDATE), ContactOutcome (7), _CHANNEL_COST_PENCE (email 0.2p / SMS 4p / post 80p / phone 350p), CustomerContactPrefs (frozen: paper_free_discount_eligible), ContactAttempt (frozen: was_successful), ContactJourney (log_attempt/delivery_rate_pct/total_contact_cost/opted_out_customers).
**Phase 243 COMPLETE (2026-06-26):** Fuel poverty vulnerability index -- 9 new tests (3,237 passing). company/crm/vulnerability_index.py (new): VulnerabilityBand (LOW/MEDIUM/HIGH/CRITICAL at 0/15/35/60), FuelPovertyIndicator (6: BENEFITS/DISABILITY/CHILD/ELDERLY_75/CANCER/HOME_OXYGEN; scores 10-60), VulnerabilityAssessment (frozen: indicator_score + arrears_score + fuel_poverty_score + ppm_score = total; band/is_priority_services/disconnection_protected), assess_vulnerability() factory. HOME_OXYGEN=60 → always CRITICAL. Connects to PPMBook (Ph145) and credit_scoring (Ph135).
**Phase 242 COMPLETE (2026-06-26):** Metering services contracts (MOP/DC) -- 8 new tests (3,228 passing). company/market/metering_contracts.py (new): MeteringServiceType (MOP/DC/DA/MAM), MeterType (CREDIT/PPM/SMART/HH), ServiceCallType (6), _MOP_RATE (£18-£45/meter/yr by type), _DC_RATE (£12-£30/meter/yr), MeteringContract (frozen: annual_cost/is_active/cost_for_period), ServiceCall (frozen), MeteringContractManager (register/log_service_call/active_contracts/annual_contract_cost/service_call_cost/metering_summary). HH meters cost 3× credit for MOP services.

→ Phases 1–245: `docs/claude/phase-history.md` | Earlier: `CLAUDE_HISTORY.md`
---

## Architectural Laws

### Epistemic Honesty — The Company Cannot See Inside the SIM

The company layer operates under the same information constraints as a real energy supplier.
It cannot see simulation internals — churn parameters, forward curve construction, weather
engine outputs, VaR internals. It discovers the world through observable interfaces: market
data feeds, meter reads, customer interactions, its own bills and payments, regulatory
publications.

The company's models are approximations built from observed outcomes — not reads from ground
truth. That imperfection is the point.

**Before writing any company-layer code:** ask "Could a real UK energy supplier know this?"
If the answer requires reading simulation internals, it is a violation.

The SIM/company seam (`company/interfaces/sim_interface.py`) enforces this boundary —
exposes observables and outcomes only, never parameters or internals.

---

## Sequencing principles

**Two-way-door filter:** don't build something that depends on an unresolved upstream question.

**Build efficiency:** tests passing + capabilities added per frontier session (hard metric).
Fidelity delta — one sentence per phase on what the sim can now do (soft metric, Rich assesses).
CLV is not a stable measuring stick — it evolves with business rules.

**Reversibility** governs data architecture and agent governance. Prefer designs that can be unwound.

**Regime-change blindness** is a known failure mode. The sim converged to near-naked hedging during
calm 2016–2020 data, directly before the crisis — mirroring what killed real suppliers. All
hedging/risk models must account for this.

**Activity-based pricing:** flat margin makes some customers net-negative. Any pricing model must
account for cost-to-serve at the customer level.

---

## Key learnings — do not repeat these mistakes

- **Local models confabulate endpoints.** Pre-load ground-truth API context before any local model touches external sources.
- **LATEST.md must be committed before NTFY**, not after. If stale, fix root cause.
- **REVIEW_GATE must only match on actual pane idleness** — not on prose mentioning the string "REVIEW_GATE".
- **Staging-watcher notifies Rich, not the agent.** Poll `docs/staging/` yourself.
- **The simulation is not the company.** Company makes decisions based on what it's allowed to see.
- **Non-blocking concurrency.** If blocked on a long run, move to the next staging item and return.
- **Session usage window is ~5 hours**, not 4. Don't under-estimate available budget.
- **CLAUDE.md hard limit: 35k chars / 200 lines.** Stop and trim before anything else if exceeded.
- **Committee cooldown must be date-based**, not record-count. With 18+ customers, 1440 records ≠ 30 days.
- **sim_runner TimeoutExpired must be caught.** Uncaught exception kills the `while True` loop.

---

## Technical environment

**Hardware (Skynet):** Intel i5-13400F, 32GB DDR4, RTX 3060 12GB VRAM. Windows 11 Pro + WSL2/Ubuntu.
**Networking:** Tailscale WSL2 `100.69.81.59` | File API `https://skynet-1.taila062fa.ts.net:8765`
**AI stack:** Claude Code (orchestrator) → qwen3:14b/Ollama (code gen) → risk committee (local Ollama)
**Key paths:** `docs/staging/` (instructions) | `docs/status/LATEST.md` | `docs/reports/ANNUAL_REPORT.md`
**Data:** Elexon `data.elexon.co.uk` (key-free) | NESO CKAN | Open-Meteo | synthetic forward curves
**Elexon note:** API migrated to Insights Solution. Legacy wrappers partly stale — verify before use.
