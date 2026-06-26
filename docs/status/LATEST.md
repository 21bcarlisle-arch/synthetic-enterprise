# Latest Status (mobile snapshot)

This file is served by `/ui/status` on the file API for quick mobile checks.
For full detail see `STATUS.md` at the repo root.

**Share with Claude.ai**: paste this URL into a claude.ai chat and Claude
will fetch the live content directly — no copy/paste needed, always
up to date with the latest push to `main`:
https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/docs/status/LATEST.md

Last updated: 2026-06-26T04:19:38Z


**Sim run 2026-06-26T03:12Z (git=453140d):** Total net £1,330,126 | Revenue £14.2M | Final treasury £3,796,762 | 10-yr gross margin 46%. 2022 net £276k (crisis peak), 2024 net £337k (recovery).
**Phase 133 COMPLETE (2026-06-27):** DESNZ supplier data returns -- 9 new tests (2,214 total).
- company/regulatory/desnz_returns.py: monthly SDR, annual fuel poverty declaration (LILEE)
- CarbonIntensityReturn: CO₂ g/kWh weighted by IPCC lifecycle factors (gas 490, coal 820)
- Fidelity: SDR submission and fuel poverty data are mandatory annual regulatory obligations

**Phase 132 COMPLETE (2026-06-27):** Counterparty credit limits -- 9 new tests (2,205 total).
- company/trading/credit_limits.py: pre-trade credit check (GREEN/AMBER/RED/NO_LIMIT)
- check_trade() blocks RED (≥90%) and NO_LIMIT trades; approves AMBER with monitoring
- Fidelity: pre-trade credit checks are mandatory under ISDA/CSA agreements

**Phase 131 COMPLETE (2026-06-27):** Wholesale trade blotter -- 10 new tests (2,196 total).
- company/trading/trade_blotter.py: REMIT-aware trade journal (buy/sell, counterparty, delivery_period)
- unreported_remit() gates ACER reporting obligation (1 working day deadline)
- net_position_mwh() and counterparty_exposure() for risk aggregation
- Fidelity: REMIT non-reporting is an enforcement risk; blotter is the primary record

**Phase 130 COMPLETE (2026-06-27):** ECO4 obligation tracker -- 10 new tests (2,186 total).
- company/regulatory/eco_tracker.py: ECO4 tiers (exempt/contribution/direct delivery)
- annual_obligation_twhd scaled to account count; EXEMPT/ON_TRACK/AT_RISK/BREACH status
- Fidelity: ECO4 non-delivery triggers Ofgem enforcement; material cost for large suppliers

**Phase 129 COMPLETE (2026-06-27):** Customer notification preferences -- 11 new tests (2,176 total).
- company/crm/notification_prefs.py: PECR/GDPR channel preferences (email/sms/post/phone/portal)
- can_contact() defaults: service email always on; marketing requires explicit opt-in
- paper_bill_customers() roster for paper dispatch
- Fidelity: SLC 14B requires at least one service comms channel per customer

**Phase 128 COMPLETE (2026-06-27):** Meter asset management -- 9 new tests (2,165 total).
- company/billing/meter_assets.py: MeterAsset (5 types, cert_due_date, overdue/due_soon)
- MeterAssetRegister: operational/faulty/cert_overdue tracking, smart_pct summary
- Fidelity: meter asset register is a mandatory compliance record for UK suppliers

**Phase 127 COMPLETE (2026-06-27):** HH data quality checker -- 9 new tests (2,156 total).
- company/market/hh_data_quality.py: BSCP505-aligned quality flags (negative/zero/high/estimated)
- check_day() validates 48-period completeness; quality_ok flag gates billing
- Fidelity: HH data quality failures are the primary cause of billing disputes

**Phase 126 COMPLETE (2026-06-27):** Imbalance price risk model -- 9 new tests (2,147 total).
- company/market/imbalance.py: compute_imbalance() SSP/SBP pricing, stress mode toggle
- imbalance_summary() with net cost/receipt, short/long/balanced period counts
- Fidelity: imbalance charge is the most volatile P&L line for unsophisticated suppliers

**Phase 125 COMPLETE (2026-06-27):** Ofgem market benchmark data -- 9 new tests (2,138 total).
- company/market/market_report.py: UK avg elec/gas rates 2016-2025, switching rate
- market_benchmark(), compare_to_market() with BELOW/AT/ABOVE_MARKET ±3% positioning
- Fidelity: Ofgem quarterly domestic market report is standard market intelligence input

**Phase 124 COMPLETE (2026-06-27):** Churn waterfall + reason code analysis -- 10 new tests (2,129 total).
- company/crm/churn_analytics.py: ChurnEvent (8 reason codes), ChurnWaterfall, ChurnAnalytics
- reason_breakdown() sorted by count, retention_rate(), summary() with churn/growth rate pct
- Fidelity: churn waterfall + reason codes are standard MO reporting for UK energy suppliers

**Phase 123 COMPLETE (2026-06-27):** Customer Acquisition Cost (CAC) model -- 10 new tests (2,119 total).
- company/crm/acquisition_cost.py: CAC by channel 2016-2025 (PCW GBP 48-72, broker GBP 140-200)
- clv_vs_cac(): HEALTHY/MARGINAL/LOSS_MAKING at ratio 3.0/1.5 thresholds
- Fidelity: CAC is the denominator in the CLV/CAC health check

**Phase 122 COMPLETE (2026-06-26):** Network UoS charges -- 10 new tests (2,109 total).
- company/market/network_charges.py: DUoS + TNUoS rates 2016-2025 (resi/sme/ic segments)
- network_cost_per_mwh(), annual_network_cost(); resi<ic<sme ordering maintained
- Fidelity: DUoS/TNUoS are the largest non-commodity cost for most UK suppliers

**Phase 121 COMPLETE (2026-06-26):** Capacity Market obligation management -- 10 new tests (2,099 total).
- company/regulatory/capacity_market.py: CM obligation rates 2016-2025 (£0.77→£75 crisis)
- compute_cm_obligation(): obligation_kw, annual_charge, delivery status, penalty
- Fidelity: CM pass-through is a material cost for all UK suppliers

**Phase 120 COMPLETE (2026-06-26):** Wholesale risk limits + position governor -- 11 new tests (2,089 total).
- company/trading/risk_limits.py: RiskGovernor with OK/WARNING/BREACH thresholds
- Four limits: max_open_position_mwh, max_single_contract_mwh, var_limit_gbp, stop_loss_gbp
- new_position_allowed() gates new buys; governance_summary() for risk committee

**Phase 119 COMPLETE (2026-06-26):** Licence condition monitoring -- 10 new tests (2,078 total).
- company/regulatory/licence_monitor.py: LicenceMonitor tracks SLCs (7/14/21C/22/27/27A/36/47/55)
- compliance_summary() with RAG status (GREEN/AMBER/RED)
- Fidelity: Ofgem SLC compliance is the regulatory backbone for all UK suppliers

**Phase 118 COMPLETE (2026-06-26):** DTN message log -- 10 new tests (2,068 total).
- company/market/dtn_log.py: DtnMessage/DtnLog; D-series electricity + gas 806/814/826 flows
- inbound/outbound/by_flow/rejected/summary(); flow_description from known_flows dict
- Fidelity: DTN is the operational backbone for all UK market participant comms

**Phase 117 COMPLETE (2026-06-26):** SoLR risk assessment -- 10 new tests (2,058 total).
- company/regulatory/solr.py: solr_capital_requirement() (levy+bad_debt vs treasury)
- solr_revenue_upside() (SVT retained book after 12% churn), solr_scenario() (4 scenarios)
- Calibrated to 2021-22 crisis (28 failures, ~£85/customer BSC levy)

**Phase 116 COMPLETE (2026-06-26):** Energy theft / loss indicator -- 10 new tests (2,048 total).
- company/billing/theft_indicator.py: classify_anomaly() (ok/watch/investigate vs EAC), screen_portfolio()
- Thresholds: <65% of EAC = watch, <40% = investigate + Ofgem reporting duty flagged
- Fidelity: Ofgem requires suppliers to report suspected meter tampering

**Phase 115 COMPLETE (2026-06-26):** Supplier switching request tracking -- 11 new tests (2,038 total).
- company/billing/switching.py: SwitchRequest (gain/loss, 14-day objection window), SwitchingBook
- complete/object_to/withdraw, pending_losses(), switching_summary() with net_completed
- Fidelity: DTN switching flow with 10-working-day objection window (primary churn driver)

**Phase 114 COMPLETE (2026-06-26):** MPAN/MPRN meter point registry -- 17 new tests (2,027 total).
- company/billing/meter_points.py: MeterPoint dataclass, MeterPointRegistry
- validate_mpan/validate_mprn, infer_profile_class (PC1-8), registered tracking
- Fidelity: MPAN/MPRN are the identifiers used in all Elexon/Xoserve flows

**Phase 113 COMPLETE (2026-06-26):** Direct Debit mandate management -- 12 new tests (2,010 total).
- company/billing/direct_debit.py: DirectDebitBook with BACS 28-day cycle, 2-strike suspension
- Mandate lifecycle: active/suspended/cancelled; dd_summary() for admin overview
- CLAUDE.md trimmed from 179→166 lines (phases 80-99 archived to phase-history.md)

**Phase 112 COMPLETE (2026-06-26):** Vulnerability register admin view -- 8 new tests (1,998 total).
- GET /admin/vulnerability: full register (active + resolved), WHD badge, Contact button per row
- Admin nav: Vulnerability button (amber/brown)
- whd_eligible_customers() cross-referenced for WHD badge display

**Phase 111 COMPLETE (2026-06-26):** Fuel mix disclosure -- 9 new tests (1,990 total).
- company/billing/fuel_mix.py: DESNZ fuel mix 2016-2025 (renewable 24.6%→55%)
- get_fuel_mix(), fuel_mix_summary() with low-carbon %, fossil %, trend direction
- Regulatory dashboard: Fuel Mix Disclosure section (Ofgem licence requirement)

**Phase 110 COMPLETE (2026-06-26):** Carbon footprint tracking -- 10 new tests (1,981 total).
- company/billing/carbon_footprint.py: DESNZ grid intensity 2016-2025 (266→115 gCO2e/kWh), estimate_carbon() for elec+gas
- Consumption portal: green footprint widget (kg CO2e/yr + tonnes)
- Grid decarbonisation visible: 2016 EAC 3500kWh = 931kg CO2e; 2025 = 403kg (-57%)

**Phase 109 COMPLETE (2026-06-26):** Admin retention dashboard -- 7 new tests (1,971 total).
- GET /admin/retention: tier summary cards + sortable customer risk table
- Admin nav: Retention button links to dashboard
- Closes loop from Phase 108 scoring engine to management view

**Phase 108 COMPLETE (2026-06-26):** Retention risk scoring -- 8 new tests (1,964 total).
- company/crm/retention_risk.py: rule-based churn signal scoring (overdue/complaint/notice window/rate exposure)
- Score 0-5 -> LOW/MEDIUM/HIGH tier; portfolio_risk_summary() aggregates
- Foundation for admin retention dashboard (Phase 109)

**Phase 107 COMPLETE (2026-06-26):** Usage benchmarking -- 10 new tests (1,956 total).
- company/billing/usage_benchmark.py: peer group by home_type + EPC band, percentile rank, efficient/average/heavy label
- Consumption portal: colour-coded benchmark widget vs peer median

**Phase 106 COMPLETE (2026-06-26):** CSAT admin reporting -- 7 new tests (1,946 total).
- _load_admin_data() adds csat dict from ServiceLog.csat_summary()
- Admin overview: 5th summary card shows mean CSAT score + rated count
- Closes feedback loop: portal capture (Phase 105) → admin view (Phase 106)

**Phase 105 COMPLETE (2026-06-26):** CSAT score tracking -- 9 new tests (1,939 total).
- ServiceLog: csat_score INT column (with auto-migration), csat_summary(), rate_contact(), latest_contact_id()
- Contact portal: 1-5 star rating widget on success page; POST /contact/rate stores score
- Foundation for CSAT reporting in admin dashboard

**Phase 104 COMPLETE (2026-06-26):** Ombudsman referral tracking -- 10 new tests (1,930 total).
- ServiceLog.ombudsman_eligible(): complaints unresolved >8 weeks (resolve_overdue=True + not resolved)
- admin/complaints: red alert box listing each eligible case with deadlock letter prompt
- regulatory dashboard: Ombudsman section (green if 0; red with count + link if >0)

**Phase 103 COMPLETE (2026-06-26):** Smart meter upgrade request flow -- 8 new tests (1,920 total).
- GET/POST /account/{id}/smart-meter portal flow
- HH customers: already-active confirmation; non-HH: request form
- POST records ServiceEvent to CRM (reason=smart_meter, outcome=upgrade_requested)
- Dashboard: one-click link for non-HH customers

**Phase 102 COMPLETE (2026-06-26):** Admin navigation hub -- 10 new tests (1,912 total).
- admin.html: coloured quick-link buttons to Complaints/Collections/Renewals/Regulatory/Trading
- All 22 portal routes now reachable from admin in ≤2 clicks

**Phase 101 COMPLETE (2026-06-26):** EPC energy efficiency advice -- 11 new tests (1,902 total).
- company/billing/efficiency_advice.py: epc_advice() tips for bands A-G; available_schemes() maps EPC to gov schemes
- Dashboard: collapsible EPC advice panel showing tailored tips + schemes
- Available schemes: ECO4, Great British Insulation Scheme, SEG, Boiler Upgrade, WHD

**Phase 100 COMPLETE (2026-06-26):** Switching recommendation engine -- 11 new tests (1,891 total).
- company/pricing/switching_recommendation.py: action logic (switch/stay/consider/N-A) based on fixed/variable, renewal window, market rate delta
- Dashboard: tariff advice widget (red=switch urgently, green=stay, blue=consider)
- Synthesises Phase 95 (contract), 99 (market rate), 47a (price cap) intelligence

**Phase 99 COMPLETE (2026-06-26):** Market rate comparison widget -- 8 new tests (1,880 total).
- company/market/rate_comparison.py: forward estimate vs effective invoice rate; delta + protected flag + message
- Consumption page: market rate comparison widget (green if protected, amber/red if exposed)
- Returns None gracefully if feed unavailable or no invoice history

**Phase 98 COMPLETE (2026-06-26):** Admin upcoming renewals -- 8 new tests (1,872 total).
- GET /admin/renewals: contracts ending in next 90 days, sorted by urgency
- Colour-coded: ≤14d red (urgent), ≤30d amber (notice window), ≤90d green
- admin_renewals.html; account links; "no renewals" empty state

**Phase 97 COMPLETE (2026-06-26):** Annual cost forecast -- 8 new tests (1,864 total).
- company/billing/consumption_forecast.py: forecast_annual_cost() = EAC × rate + 365 × SC; quarterly split by UK heating profile
- Consumption page: estimated annual cost + per-quarter breakdown
- Returns None if insufficient invoice history (falls back gracefully)

**Phase 96 COMPLETE (2026-06-26):** Collections queue -- 10 new tests (1,856 total).
- company/billing/collections.py: overdue invoice query, per-customer aggregation, 4-tier aging
- GET /admin/collections: collections queue sorted by severity (worst first)
- admin_collections.html: tier colour-coded table with account links

**Phase 95 COMPLETE (2026-06-26):** Contract renewal countdown -- 11 new tests (1,846 total).
- company/billing/contract.py: contract_end_date(), days_until_renewal(), is_in_notice_window(), renewal_summary()
- Dashboard: renewal date + days countdown; in-window CTA to compare tariffs
- Fixed_1yr/2yr advance from acquisition by term steps; variable returns None

**Phase 94 COMPLETE (2026-06-26):** Complaint deadline tracker -- 10 new tests (1,835 total).
- ServiceLog.complaint_deadlines(): 2-working-day ack deadline, 8-week resolve deadline per complaint
- _add_working_days() helper skips weekends; overdue flags computed vs today
- GET /admin/complaints: all open complaints with deadline status; admin_complaints.html

**Phase 93 COMPLETE (2026-06-26):** Warm Home Discount -- 11 new tests (1,825 total).
- company/regulatory/warm_home_discount.py: rebate amounts 2017-2025, eligibility from vulnerability_register, liability calculation
- Regulatory dashboard: WHD scheme year, eligible count, rebate/customer, total liability
- Dashboard: vulnerability badge if customer in vulnerability register

**Phase 92 COMPLETE (2026-06-26):** Peak/off-peak band overlay on HH consumption -- 10 new tests (1,814 total).
- _tou_band(): weekends off-peak; weekdays peak 07:00-19:00
- Consumption route: hh_data enriched with band field; is_tou passed to template
- consumption.html: Band column, amber peak rows, blue off-peak rows, legend
- Destinationvision test met: C7 (HH smart meter) sees peak/off-peak pricing overlaid

**Phase 91 COMPLETE (2026-06-26):** CSS filing wired to persistent ServiceLog -- 9 new tests (1,804 total).
- Regulatory dashboard CSS section: total contacts, complaint rate, resolution rate, target met, vulnerable count
- generate_css_filing() called with _SERVICE_LOG.as_dicts() and datetime.now().year
- Portal→CRM→CSS filing loop now fully closed

**Phase 90 COMPLETE (2026-06-26):** Contact Us portal form -- 11 new tests (1,795 total).
- GET/POST /account/{id}/contact: reason dropdown, notes textarea, formal complaint checkbox
- ServiceEvent recorded in persistent _SERVICE_LOG on submit; complaint_flag set if formal complaint
- contact.html (new); dashboard Contact Us link; closes the portal→CRM data flow

**Phase 89 COMPLETE (2026-06-26):** ServiceLog SQLite persistence -- 8 new tests (1,784 total).
- ServiceLog() rewritten: in-memory SQLite (:memory:) by default; ServiceLog(db_path=...) for file persistence
- Events/complaints/vulnerabilities survive reconnect; all 12 prior CRM tests pass unchanged
- Foundation for CSS filing with real CRM data; DEFAULT_DB_PATH = company/data/service_log.db

**Phase 88 COMPLETE (2026-06-26):** Direct Debit Mandate -- 21 new tests (1,776 total).
- company/billing/direct_debit.py (new): DDMandate dataclass, SQLite persistence, set/get/cancel/list/is_dd_customer
- Portal: GET/POST /account/{id}/direct-debit (setup form) + POST /cancel; direct_debit.html
- Dashboard nav: Direct Debit link; payment_day 1-28 validated

**Phase 87 COMPLETE (2026-06-26):** EAC Calibration from billing history -- 12 new tests (1,755 total).
- company/billing/eac_calibration.py (new): calibrate_eac() annualises from invoice consumption_kwh (2yr lookback)
- calibrate_all_customers() batch; eac_drift() returns drift_pct + direction (up/down/flat)
- Consumption portal: calibrated EAC vs original with drift indicator

**Phase 86 COMPLETE (2026-06-26):** Account Statement -- 11 new tests (1,743 total).
- GET /account/{id}/statement: full invoice table + balance summary (billed/paid/bad debt/outstanding)
- Print-optimised: @media print CSS hides nav; Print button in corner
- Statement link added to dashboard + bills nav

**Phase 85 COMPLETE (2026-06-26):** Admin Portfolio Overview -- 11 new tests (1,732 total).
- GET /admin: customer portfolio table — segment, commodity, EAC, smart meter, outstanding, paid
- Summary cards: active accounts, total billed, outstanding, bad debt
- Per-customer account links; _load_admin_data() aggregates invoice DB across all accounts

**Phase 84 COMPLETE (2026-06-26):** Regulatory Compliance Dashboard -- 13 new tests (1,721 total).
- `GET /regulatory`: smart meter penetration vs Ofgem target (COMPLIANT/AT_RISK/BREACH badge)
- MCR capital adequacy section: treasury vs £130/account floor, ratio, OK/Watch/STRESS badge
- Ofgem annual turnover fee from total revenue
- `regulatory.html` (new); Dashboard nav updated with Regulatory link
- Uses company.regulatory.compliance + saas.capital.solvency — no SIM internals

**Phase 83 COMPLETE (2026-06-26):** Portal payment submission -- 12 new tests (1,708 total).
- `POST /account/{id}/pay`: invoice_number + amount from form → reconcile_payment() → confirmation
- `company/portal/templates/payment_confirm.html` (new): shows paid/partially_paid/no_match with detail
- `bills.html` updated: Pay button on each unpaid/partially_paid invoice row
- `get_invoice()` now calls create_schema() — no crash on empty DB
- Customer journey fully closed: login → dashboard → bills → pay → confirmation

**Phase 82 COMPLETE (2026-06-26):** HH consumption feed + portal half-hourly view -- 13 new tests (1,696 total).
- `simulation/publish_consumption_data.py` (new): reads real HH profiles from sim/hh_data/{C7,C8,C9}.csv; 288-record JSON feed (2 days × 48 periods × 3 customers)
- `company/billing/hh_consumption.py` (new): get_hh_consumption() + recent_hh_periods() — reads feed, no SIM imports
- Portal: HH customers (C7-C9) see live half-hourly consumption table (last 24h, 48 periods) on /consumption
- process_run_complete.py: calls publish_consumption() after each sim run (auto-refreshed)

**Phase 81 COMPLETE (2026-06-26):** Trading desk: live spot prices from M3 feed -- 8 new tests (1,683 total).
- `company/portal/app.py`: _load_spot_prices() reads PriceFeed → elec/gas spot + forward estimates
- `trading.html`: Market Data Feed section (spot, forward, stale warning); graceful if feed absent
- M3 end-to-end: SIM writes feed → company reads → trading desk displays £100.58/MWh elec spot

**Phase 80 COMPLETE (2026-06-26):** M3 price feed live: publish on every sim run -- 11 new tests (1,675 total).
- `simulation/publish_market_feed.py` (new): build_feed_prices() reads last 48 SSP HH + 10 NBP daily prices
- `process_run_complete.py`: calls publish() after report gen; feed auto-updated on every sim run
- `docs/market_data/price_feed.json` created: 58 records, latest elec spot £100.58/MWh (2025-06-07)
- PriceFeed.is_available() now True; Phase 76 M3 architectural gap fully closed

**Phase 79 COMPLETE (2026-06-26):** Portal: Consumption history page -- 11 new tests (1,664 total).
- `company/billing/consumption.py` (new): consumption_history() + monthly_totals() reads from invoice DB
- Portal: GET /account/{id}/consumption; HH customers (C7-C9) see smart meter banner
- Dashboard nav updated with Consumption link; Portal MVP now complete (all 5 customer views)

**Phase 78 COMPLETE (2026-06-26):** Year-indexed non-commodity billing rates -- 14 new tests (1,653 total).
- `saas/non_commodity.py`: year-indexed tables 2016-2024 for resi elec (£52→£80/MWh) and gas (£9→£16/MWh)
- SME multipliers: 0.77 elec / 0.80 gas applied to resi base; backward-compat year=None → 2019 flat baseline
- `bill_generator.py`: billing year extracted from dates[0], passed to non_commodity_rate
- 2022 crisis: resi elec non-commodity £55→£73/MWh; closes Section 9 known gap

**Phase 77 COMPLETE (2026-06-26):** Portal Phase 2: Tariff Comparison -- 17 new tests (1,639 total).
- `company/pricing/tariff_comparison.py` (new): compare_tariffs() returns Fixed 1yr/2yr/Variable sorted by annual cost
- Portal: GET tariff-compare + POST switch-tariff (generates SW- reference, renders confirmation)
- Rich can now log in as C1 and request a tariff switch via the portal

**Phase 76 COMPLETE (2026-06-26):** M3 Market Data Feed -- 10 new tests (1,622 total).
- `company/market/price_feed.py` (new): PriceFeed reads published JSON feed, is_stale(), summary()
- publish_feed() for SIM pipeline; forward estimate = recent spot mean + risk premium
- M3 closed -- all Destinationvision gaps are now CLOSED

**Phase 75 COMPLETE (2026-06-26):** M1 Elexon Settlement Interface -- 10 new tests (1,612 total).
- `company/market/settlement_reconciler.py` (new): SettlementStatement, reconcile_against_bill(), batch reconciliation
- Imbalance flagged if >5% of settlement cost or >£10; M1 closed

**Phase 74 COMPLETE (2026-06-26):** M2 Regulatory Reporting -- 13 new tests (1,602 total).
- `company/regulatory/compliance.py` (new): price cap compliance, smart meter COMPLIANT/AT_RISK/BREACH, CSS annual return
- Ofgem SLC37 complaint resolution tracking; annual turnover fee computation
- M2 closed

**Phase 73 COMPLETE (2026-06-26):** T1 Trading Desk Interface -- 7 new tests (1,589 total).
- Portal: GET /trading route shows hedge portfolio summary, best/worst decisions, P&L by year
- Reads hedge_effectiveness from run_output_latest.json; T1 closed

**Phase 72 COMPLETE (2026-06-25):** T2 Position Management -- 10 new tests (1,582 total).
- HedgeAmendment + PositionClosure dataclasses; amend_hedge() + close_position() with audit trail
- open_contracts() + portfolio_mtm() now exclude closed positions
- T2 closed -- full trade lifecycle: open -> amend -> close

**Phase 71 COMPLETE (2026-06-25):** T3 Mark-to-Market -- 10 new tests (1,572 total).
- `company/trading/forward_book.py`: mark_to_market() + portfolio_mtm() methods added to TradingBook
- MTM = (market_price - agreed_price) x notional_mwh per contract; portfolio rollup
- T3 closed -- trading book now has daily valuation capability

**Phase 70 COMPLETE (2026-06-25):** FI3 Treasury Management -- 12 new tests (1,562 total).
- `company/finance/treasury.py` (new): working capital, cash trend, project_treasury(), treasury_health()
- MCR headroom (OK/WATCH/CRITICAL), 3-year cash flow projection from management accounts
- FI3 closed -- financial infrastructure stack complete

**Phase 69 COMPLETE (2026-06-25):** C4 CRM Service Interaction Log -- 12 new tests (1,550 total).
- `company/crm/service_log.py` (new): ServiceEvent + ServiceLog with complaint/vulnerability tracking
- complaint_stats(year), vulnerability_register(), resolve_vulnerability()
- CRM moves from lifecycle-only events to full service history; C4 closed

**Phase 68 COMPLETE (2026-06-25):** C2 Customer Portal MVP -- 14 new tests (1,538 total).
- `company/portal/app.py` (new): FastAPI app, 4 routes (login + dashboard + bills)
- Jinja2 HTML templates; account number auth; reads company layer only
- Rich can log in as C1 and view profile, billing summary, invoice history; C2 closed

**Phase 67 COMPLETE (2026-06-25):** C3 Payment Processing + Debt Aging -- 10 new tests (1,524 total).

**Phase 66 COMPLETE (2026-06-25):** C1 Invoice Line Items + Text Format -- 9 new tests (1,514 total).
- `company/billing/invoice.py`: schema extended with commodity/non-commodity columns; create_invoice() stores full line items; format_invoice_text() renders structured text invoice
- C1 invoice documents now show energy charge, network & levies, standing charge, VAT breakdown

**Phase 65 COMPLETE (2026-06-25):** FI2 Budget vs Actual -- 12 new tests (1,505 total).
- `company/finance/budget.py` (new): budget constants (2016-2025, prior-year actuals * growth factors), variance_report(), traffic_light()
- Annual report: 10-year RAG variance table; 2021 AMBER (-13.7% net miss), 2022 RED (+18.3% crisis outperformance), 2023 RED (-21.1% post-crisis); FI2 closed

**Phase 64 COMPLETE (2026-06-25):** FI1 Management Accounts from double-entry journal -- 13 new tests (1,493 total).
- company/finance/management_accounts.py (new): build_monthly_accounts(), annual_management_pack(), cross_check()
- P&L now emerges from account codes (4001=revenue, 5001+5100=COGS, 5200=capital, 6xxx=opex) not formulas; FI1 closed
- Annual report: 10-year management accounts table + final-year balance sheet + cross-check vs simulation net

**Phase 63 COMPLETE (2026-06-25):** F1 Double-entry ledger — 24 new tests (1,480 total).
- `company/finance/double_entry.py` (new): 13 account codes (1xxx–6xxx), `to_journal_entry()` for all 9 ledger event types
- `trial_balance()`, `income_statement()`, `balance_sheet()` — Assets = Liabilities + Equity verified
- Foundation for FI1 management accounts and C1 customer invoices (Destinationvision.md F1)

**Phase 62 COMPLETE (2026-06-25):** Standing charges (electricity + gas, resi/SME) -- 12 new tests (1,456 total).
- `simulation/policy_costs.py`: Ofgem tariff tracker year-indexed SC tables; resi elec 24p/day (2016) -> 61p/day (2024), gas 22p->31p; SME 1.5x; I&C=0
- `hedged_settlement.py`: SC prorated per half-hour, added to revenue+margin; `standing_charge_gbp` field per record
- `gas_settlement.py`: daily SC in `gas_standing_charge_gbp` field

**Phase 61 COMPLETE (2026-06-25):** Flex tariff policy pass-through fix — 8 new tests (1,444 total).
- `run_flex_term()` in `hedged_settlement.py`: revenue now includes policy+network recovery (pass-through to customer)
- C_IC4 total net swings from -£1.06M to +£33k; prior model had supplier absorbing all policy costs

**Phase 60 COMPLETE (2026-06-25):** I&C gas flat seasonal profile — 8 new tests (1,436 total).
- `GAS_IC_CONSUMPTION_MONTHLY_PROFILE`: Jan=1.075, Jul=0.913, 1.18× ratio vs resi 5.3×
- `run_gas_term()` selects profile by segment; Phase 59 was applying resi heating swing to 5M kWh I&C

**Phase 59 COMPLETE (2026-06-25):** Monthly gas consumption seasonality — 10 new tests (1,428 total).
- `GAS_CONSUMPTION_MONTHLY_PROFILE` in `gas_settlement.py`: Jan=1.884, Jul=0.353, 5.3× winter/summer ratio (DUKES Table 4.3)
- Per-day `daily_kwh = AQ/365 × seasonal × weather_factor`; prior model was flat AQ/365 every day
- Combined with Phase 58 HDD factor: resi gas has both within-year shape AND year-to-year deviation

**Phase 58 COMPLETE (2026-06-25):** Weather-adjusted gas consumption (HDD model) — 15 new tests (1,418 total).
- `sim/weather_hdd.py` (new): HDD = max(0, 15.5°C - mean_temp); UK 1991-2020 climate normals; `get_weather_factor()` [0.3, 2.0]
- `simulation/gas_settlement.py`: `weather_factor` param scales daily_kwh; resi/SME only — I&C process gas unchanged
- 2019-2020 warm winter reduces resi gas demand; Jan 2021 cold snap increases it

**Phase 57 COMPLETE (2026-06-25):** Year-varying bad debt (crisis surge) — 9 new tests (1,403 total).
- `saas/cost_to_serve.py`: `get_bad_debt_rate(year, segment)` — 2021 resi 4%, 2022 resi 8% (Ofgem 2.4M in arrears), 2023 5%
- `simulation/run_phase2b.py`: bad_debt_gbp deducted from net_margin_gbp + treasury each settlement record
- Solvency dedup fix: MCR ratio now uses billing-account count (C1+C1g = 1, not 2)

**Phase 56 COMPLETE (2026-06-25):** Gas pass-through hedge zero-lock — 5 new tests (1,394 total).
- `simulation/run_phase2b.py`: gas pass-through customers now `hf=0.0` (was 0.85 from RESET default)
- Wrong-way risk eliminated: C_IC3g showed +42% gas margin in 2021 (hedge windfall) and -86% in 2023 (loss on reversion)
- Margin now = service_fee + network + policy only; no forward price exposure for spot-indexed contracts

**Phase 55 COMPLETE (2026-06-25):** Ofgem MCR solvency signal — 12 new tests (1,389 total).
- `saas/capital/solvency.py` (new): `compute_solvency_signal()` → Watch < 2×, STRESS < 1× (below £130/account floor)
- `_section_solvency_signal()` upgraded with formal MCR ratio and status columns in annual report
- ASSUMPTIONS.md: price cap rows (38/41) updated — gas+electricity cap IS applied since Phase 47a

**Phase 54 COMPLETE (2026-06-25):** Supplier mutualization levy — 8 new tests (1,377 total).
- `simulation/policy_costs.py`: `_MUTUALIZATION_LEVY_BY_YEAR` + `get_mutualization_levy_per_mwh()`
- 2021: £4.14/MWh (17 SoLR events); 2022: £10.00/MWh (Bulb SAR + BSC shortfall recovery)
- Applied in all 3 electricity settlement paths; annual report policy table extended

**Phase 53 COMPLETE (2026-06-25):** BSC credit cover — 14 new tests (1,369 total).
- `saas/capital/bsc_credit.py` (new): peak daily electricity wholesale cost × 1.2 buffer
- Annual report: per-year BSC credit cover vs treasury table; 2022 crisis = £10k cover (363× 2016)
- Coverage ratio < 5× flagged Watch; < 2× flagged STRESS; realistic capital stress signal

**Phase 52 COMPLETE (2026-06-25):** ToU demand response — 24 new tests (1,355 total).
- `saas/demand_response.py` (new): peak→off-peak load shift (base 15% + EV +12% + heat_pump +8%)
- `make_shifted_shape_fn()` wraps consumption shape for ToU-eligible customers
- Watchdog: exponential API backoff (1m/2m/5m/10m), NTFY on failure + hourly while down

**Phase 51 COMPLETE (2026-06-24):** ToU eligibility gate — 9 new tests (1,330 total).
- `is_tou_eligible(customer)` in `saas/smart_meter_rollout.py`: True if HH-metered OR smart_meter=True
- Acquired customers with smart meters (from Phase 50 rollout model) now get peak/off-peak pricing

**Test suite: 2,214 total (all tests passing)**

**Latest simulation results (2016–2025)** — auto-processed (479s / 8 min):
- Net margin: £6,322,835.71 | Gross: £6,559,770.69 | Capital: £236,935
- Treasury: £2,466,636 → £3,796,762 | 38 committee interventions | 1531 bills issued
- Enterprise value: £6,124,100.98 | Net after CTS: £6,454,351
- Retention: 18 offers, 17/18 retained | 5 no-offer churns | 6 total churned accounts