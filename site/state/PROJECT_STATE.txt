# PROJECT STATE — Synthetic Enterprise
Generated: 2026-06-30T20:06:26Z

## Summary
- Current Phase: HY (Coverage Expansion Sprint IX)
- Test Suite: 9,290 tests passing (unit / fast suite)
- Company Modules: 406 Python modules
- Simulation Window: 2016-2025 (Elexon HH settlement data)
- Architecture: sim/ (market + settlement engine) | company/ (business layer) | site/ (dashboard)

## Latest Simulation Results (auto-processed)
- Net Margin: £1,243,337 (treasury change after CTS)
- Gross Margin: £6,462,146
- Enterprise Value: £6,037,509
- Treasury: £2,466,636 → £3,709,973
- Risk Committee Interventions: 38
- Bills Issued: 1,531
- Retention: 17/18 offers accepted | 5 no-offer churns | 6 total churned accounts

## Module Inventory by Domain

| Domain | Module Count | Primary Purpose |
|--------|-------------|-----------------|
| billing/ | 69 | Customer billing: invoices, payments, meter reads, PPM, refunds, arrears |
| compliance/ | 5 | Consumer Duty, board reporting, fair value assessments |
| core/ | 7 | Account intelligence, event ledger, reputation, CLV foundations |
| crm/ | 79 | Customer lifecycle: acquisition, churn, retention, switching, TPI, complaints |
| finance/ | 28 | P&L, treasury, budgets, VAT, bad debt, sensitivity analysis |
| interfaces/ | 1 | SIM/company seam (sim_interface.py) — observables only |
| market/ | 79 | Settlement, metering, network charges, capacity, DSR, flexibility, gas |
| portal/ | 1 | Customer self-service portal (app.py) |
| pricing/ | 19 | Tariff engine, renewal pricing, elasticity, NCC forecasting, price cap |
| regulatory/ | 62 | SLC compliance, ECO4/WHD/REGO/REMIT/EMIR/GGL/CCA obligations, PSR |
| risk/ | 13 | FRA, VaR, stress tests, credit rating, hedge effectiveness, liquidity |
| sustainability/ | 4 | Carbon intensity, TCFD, decarbonisation scoring |
| trading/ | 25 | Forward book, OTC/exchange margin, EMIR, BM, imbalance, credit limits |

Total: 392 modules

## Phase History (recent — GW onwards)

Phase A (2026-06-27): Household physical model -- 36 tests (4,594).
Phase AA (2026-06-29): Demand Flexibility Potential Assessor -- 23 tests (5,103).
Phase AB (2026-06-29): EAC Drift Assessor -- 35 tests (5,138).
Phase AC (2026-06-29): Portfolio Repricing Action Book -- 24 tests (5,162).
Phase AD (2026-06-29): Portfolio Churn Risk Book -- 34 tests (5,196).
Phase AE (2026-06-29): Customer Retention Offer Book -- 21 tests (5,217).
Phase AF (2026-06-30): DSR/Flexibility Revenue Integration -- 15 tests (5,232).
Phase AG (2026-06-30): Annual Report Flex Revenue Section -- 12 tests (5,244).
Phase AH (2026-06-30): Board Intelligence Pack -- 12 tests (5,256).
Phase AI (2026-06-30): EAC Drift Snapshot -- 10 tests (5,266).
Phase AJ (2026-06-30): CRM Risk Triage -- 14 tests (5,280).
Phase AK (2026-06-30): Churn Root Cause Attribution -- 14 tests (5,294).
Phase AL (2026-06-30): Counterfactual Retention -- 12 tests (5,306).
Phase AM (2026-06-30): Pricing Basis Risk -- 12 tests (5,318).
Phase AN (2026-06-30): Portfolio Concentration Risk -- 12 tests (5,330).
Phase AO (2026-06-30): Demand Estimation Error Trend -- 12 tests (5,342).
Phase AP (2026-06-30): Segment Capital Efficiency -- 12 tests (5,354).
Phase AQ (2026-06-30): Board Risk Summary -- 12 tests (5,366).
Phase AR (2026-06-30): Gas Exit Decision Book -- 14 tests (5,380).
Phase AS (2026-06-30): Gas Exit Analysis Report Section -- 10 tests (5,390).
Phase AT (2026-06-30): Management Accounts P&L Section -- 12 tests (5,402).
Phase AU (2026-06-30): Commodity Split -- 12 tests (5,414).
Phase AV (2026-06-30): Policy Cost & Levy Breakdown -- 12 tests (5,426).
Phase AW (2026-06-30): Bill Shock Analysis -- 12 tests (5,438).
Phase AX (2026-06-30): Customer Experience & Service Quality -- 12 tests (5,462).
Phase AY (2026-06-30): Customer Strategic Value Matrix -- 12 tests (5,474).
Phase AZ (2026-06-30): I&C Triad Notification Book -- 15 tests (5,489).
Phase B (2026-06-27): Life events engine -- 32 tests (4,626).
Phase BA (2026-06-30): Price Elasticity Estimator -- 15 tests (5,504).
Phase BB (2026-06-30): Risk Committee Decision Ledger -- 15 tests (5,519).
Phase BC (2026-06-30): Risk Committee Activity Section -- 12 tests (5,531).
Phase BD (2026-06-30): Renewal Pricing Engine -- 15 tests (5,546).
Phase BE (2026-06-30): Gross Margin Bridge -- 12 tests (5,558).
Phase BF (2026-06-30): Acquisition Strategy Intelligence -- 15 tests (5,573).
Phase BG (2026-06-30): CLV Evolution -- 12 tests (5,585).
Phase BH (2026-06-30): Dynamic Pricing -- 12 tests (5,597).
Phase BI (2026-06-30): Tariff Accuracy -- 12 tests (5,609).
Phase BJ (2026-06-30): Churn Calibration -- 12 tests (5,621).
Phase BK (2026-06-30): Financial Ratios -- 12 tests (5,633).
Phase BL (2026-06-30): Stress Test History -- 12 tests (5,645).
Phase BM (2026-06-30): Price Cap Headroom -- 12 tests (5,657).
Phase BN (2026-06-30): Segment Attribution -- 12 tests (5,669).
Phase BO (2026-06-30): CfD & Treasury -- 12 tests (5,681).
Phase BP (2026-06-30): Cohort Revenue -- 12 tests (5,693).
Phase BQ (2026-06-30): BSC & Levies -- 12 tests (5,705).
Phase BR (2026-06-30): Worst Settlement Period -- 12 tests (5,717).
Phase BS (2026-06-30): Committee -- 12 tests (5,729).
Phase BT (2026-06-30): Hedge Fraction -- 12 tests (5,741).
Phase BU (2026-06-30): Gas Exit -- 12 tests (5,753).
Phase BV (2026-06-30): Retention ROI -- 12 tests (5,765).
Phase BW (2026-06-30): Missed Retention -- 12 tests (5,777).
Phase BX (2026-06-30): Fuel Mix -- 12 tests (5,789).
Phase BY (2026-06-30): VaR & Treasury -- 12 tests (5,801).
Phase BZ (2026-06-30): Portfolio Margin Sensitivity Analyser -- 12 tests (5,813).
Phase C (2026-06-27): Household-Driven EAC Integration -- 26 tests (4,653 passing).
Phase CA (2026-06-30): Service Quality Monitor -- 12 tests (5,825).
Phase CB (2026-06-30): Hedge Value-Add Analysis -- 12 tests (5,837).
Phase CC (2026-06-30): OTC Margin Call Book -- 12 tests (5,849).
Phase CD (2026-06-30): Customer Commodity P&L section -- 12 tests (5,861).
Phase CE (2026-06-30): SLC Compliance Tracker -- 12 tests (5,873).
Phase CF (2026-06-30): TPI Commission Book -- 12 tests (5,885).
Phase CG (2026-06-30): Supplier Resilience Scorecard -- 12 tests (5,897).
Phase CH (2026-06-30): Net Open Position Register -- 12 tests (5,909).
Phase CI (2026-06-30): Annual Board Pack Synthesiser -- 12 tests (5,921).
Phase CJ (2026-06-30): Initial Margin Register -- 12 tests (5,933).
Phase CK (2026-06-30): Liquidity Stress Test Book -- 12 tests (5,945).
Phase CL (2026-06-30): Fuel Mix Disclosure Book -- 12 tests (5,957).
Phase CM (2026-06-30): Market Share Estimator -- 12 tests (5,969).
Phase CN (2026-06-30): Unit Economics Annual Report Section -- 12 tests (5,981).
Phase CO (2026-06-30): Contract Exposure Register -- 12 tests (5,993).
Phase CP (2026-06-30): BSC Settlement Exposure Section -- 12 tests (6,005).
Phase CQ (2026-06-30): Environmental Impact Register -- 12 tests (6,017).
Phase CR (2026-06-30): Priority Services Register -- 12 tests (6,029).
Phase CS (2026-06-30): Gas Nomination Register -- 12 tests (6,041).
Phase CT (2026-06-30): Shipper Code Register -- 13 tests (6,054).
Phase CU (2026-06-30): Interruptible Gas Supply Register -- 13 tests (6,067).
Phase CV (2026-06-30): DA/DC Contract Register -- 12 tests (6,079).
Phase CW (2026-06-30): Licence Application Register -- 12 tests (6,091).
Phase CX (2026-06-30): Regulatory Breach Log -- 12 tests (6,103).
Phase CY (2026-06-30): Supplier Fitness Register -- 13 tests (6,116).
Phase CZ (2026-06-30): Revenue Protection Register -- 12 tests (6,128).
Phase DA (2026-06-30): Customer Comm Preferences -- 12 tests (6,140).
Phase DB (2026-06-30): ICO Data Breach Notification Register (UK GDPR) -- 33 tests (5,483).
Phase DC (2026-06-30): EMIR Trade Repository Reporting Register -- 29 tests (5,512).
Phase DD (2026-06-30): Energy Bill Relief Scheme (EBRS) Register -- 28 tests (5,540).
Phase DE (2026-06-30): Energy Bills Support Scheme (EBSS) Register -- 28 tests (5,568).
Phase DF (2026-06-30): Data Subject Access Request Register (UK GDPR Art.15) -- 32 tests (5,600 total)
Phase DG (2026-06-30): Consumer Vulnerability Duty Action Register -- 23 tests (5,623 total)
Phase DH (2026-06-30): BSC Settlement Run Tracking Register -- 25 tests (5,648 total)
Phase DI (2026-06-30): Social Obligation Spend Register -- 24 tests (5,672 total)
Phase DJ (2026-06-30): Statutory Annual Accounts Register -- 30 tests (5,702 total)
Phase DK (2026-06-30): Switching Cost Model -- 20 tests (5,722 total)
Phase DL (2026-06-30): Price Transparency Publication Register -- 22 tests (5,744 total)
Phase DM (2026-06-30): Priority Services Register (PSR) -- 25 tests (5,769 total)
Phase DN (2026-06-30): SLC Compliance Tracker tests -- 21 tests (5,790 total)
Phase DO (2026-06-30): Embedded Network Supply Register -- 23 tests (5,813 total)
Phase DP (2026-06-30): Interconnector Monitor Register -- 23 tests (5,836 total)
Phase DQ (2026-06-30): Renewal Notice Register (SLC 22) -- 19 tests (5,855 total)
Phase DR (2026-06-30): Board Meeting Minutes Register -- 21 tests (5,876 total)
Phase DS (2026-06-30): Complaint Root Cause Analyser -- 19 tests (5,895 total)
Phase DT (2026-06-30): Marketing Campaign Register -- 20 tests (5,915 total)
Phase DU (2026-06-30): Customer Credit Assessment Register -- 18 tests (5,933 total)
Phase DV (2026-06-30): Wholesale Market Position Monthly Report -- 23 tests (5,956 total)
Phase DW (2026-06-30): CLV Sensitivity Model -- 19 tests (5,975 total)
Phase DX (2026-06-30): TCFD Climate Risk Financial Assessment -- 16 tests (5,991 total)
Phase DY (2026-06-30): Wholesale Credit Exposure Register -- 21 tests (6,012 total -- milestone!).
Phase DZ (2026-06-30): Event Ledger Core -- 18 tests (6,030 total)
Phase EP (2026-06-30): Supplier Licence Renewal Tracker -- 17 tests (6,319 total)
Phase EQ (2026-06-30): Portfolio Concentration Risk Monitor -- 17 tests (6,336 total)
Phase ER (2026-06-30): SoLR Levy Reconciliation Register -- 13 tests (6,349 total)
Phase ES (2026-06-30): Customer Segment Profitability Analysis -- 18 tests (6,367 total)
Phase ET (2026-06-30): Forward Curve Confidence Band -- 22 tests (6,389 total)
Phase EU (2026-06-30): Annualised Customer Revenue Report -- 16 tests (6,405 total)
Phase EV (2026-06-30): Regulatory Capital Adequacy Assessment -- 18 tests (6,423 total)
Phase EW (2026-06-30): Customer Service Ticket Book -- 23 tests (6,446 total)
Phase EX (2026-06-30): Capacity Market Revenue Register -- 12 tests (6,458 total)
Phase EY (2026-06-30): Metering Data Exception Handler -- 17 tests (6,475 total)
Phase EZ (2026-06-30): Tariff Benchmarking Register -- 15 tests (6,490 total)
Phase FA (2026-06-30): Vulnerable Customer Register -- 17 tests (6,507 total)
Phase FB (2026-06-30): Ombudsman Register -- 15 tests (6,522 total)
Phase FC (2026-06-30): Billing Dispute Resolution Book -- 17 tests (6,539 total)
Phase FD (2026-06-30): Carbon Intensity Register -- 13 tests (6,552 total)
Phase FE (2026-06-30): Customer Onboarding Journey Tracker -- 15 tests (6,567 total)
Phase FF (2026-06-30): Wholesale Gas Market Monitor -- 13 tests (6,580 total)
Phase FG (2026-06-30): Triad Exposure Register -- 12 tests (6,592 total)
Phase FH (2026-06-30): ROC Ledger -- 13 tests (6,605 total)
Phase FI (2026-06-30): BSC Credit Assurance Register -- 13 tests (6,618 total)
Phase FJ (2026-06-30): CfD Levy Register -- 14 tests (6,632 total)
Phase FT (2026-06-30): Imbalance Cash Flow Register -- 22 tests (7,450 total)
Phase FU (2026-06-30): Triad Demand Response Book -- 25 tests (7,475 total)
Phase FV (2026-06-30): Green Gas Levy (GGL) Register -- 31 tests (7,506 total)
Phase FW (2026-06-30): Consumer Duty Annual Board Report Register -- 38 tests (7,544 total)
Phase FX (2026-06-30): PPM Installation Warrant Register -- 32 tests (7,576 total)
Phase FY (2026-06-30): Debt Respite (Breathing Space) Register -- 29 tests (7,605 total)
Phase FZ (2026-06-30): Ofgem Redress Payment Register -- 27 tests (7,632 total)
Phase GA (2026-06-30): CSS Performance Register -- 34 tests (7,666 total)
Phase GB (2026-06-30): DCC Meter Registration Register -- 34 tests (7,700 total)
Phase GP (2026-06-30): Consumer Duty Fair Value Assessment Register -- 29 tests (8,119 total)
Phase GQ (2026-06-30): DNO Network Charge Dispute Register -- 32 tests (8,151 total)
Phase GR (2026-06-30): Trade Confirmation Register -- 33 tests (8,184 total)
Phase GS (2026-06-30): Agreed Capacity Register (I&C DUoS) -- 31 tests (8,215 total)
Phase GT (2026-06-30): CCA Verification Register -- 32 tests (8,247 total)
Phase GU (2026-06-30): Network Code Modification Register -- 32 tests (8,279 total)
Phase GV (2026-06-30): RGGO Register -- 30 tests (8,309 total)
Phase GW (2026-06-30): Non-Commodity Cost (NCC) Forecast Register -- 21 tests (8,330 total)
Phase GX (2026-06-30): Customer Account Adjustment Register -- 29 tests (8,359 total)
Phase GY (2026-06-30): TPI Conduct Compliance Register -- 29 tests (8,388 total)
Phase GZ (2026-06-30): Meter Technical Investigation Register -- 42 tests (8,430 total)
Phase HA (2026-06-30): Revenue Protection Visit Register -- 38 tests (8,468 total)
Phase HB (2026-06-30): MPAS Standing Data Correction Register -- 40 tests (8,508 total)
Phase HC (2026-06-30): Gas Safety Incident Register -- 36 tests (8,544 total)
Phase HD (2026-06-30): DSO Flexibility Tender Register -- 38 tests (8,582 total)
Phase HE (2026-06-30): Smart Export Guarantee Register -- 37 tests (8,619 total)
Phase HF (2026-06-30): Grid Connection Queue Register -- 33 tests (8,652 total)
Phase HG (2026-06-30): FiT Legacy Register -- 32 tests (8,684 total)
Phase HH (2026-06-30): Wholesale Trading Mandate Register -- 34 tests (8,718 total)
Phase HI (2026-06-30): BSC Settlement Dispute Register -- 33 tests (8,751 total)
Phase HJ (2026-06-30): MOP Appointment Register -- 26 tests (8,777 total)
Phase HK (2026-06-30): BSC Performance Assurance Register -- 49 tests (8,826 total)
Phase HL (2026-06-30): Net Open Position Register -- 29 tests (8,855 total)
Phase HM (2026-06-30): Service Quality Monitor -- 30 tests (8,885 total)
Phase HN (2026-06-30): Risk Committee Decision Ledger -- 23 tests (8,908 total)
Phase HO (2026-06-30): Supplier Resilience Scorecard -- 28 tests (8,936 total)
Phase HP (2026-06-30): Renewal Pricing Engine -- 28 tests (8,964 total)
Phase HQ (2026-06-30): Coverage Expansion Sprint -- 74 tests (9,038 total)
Phase HR (2026-06-30): Coverage Expansion Sprint II -- 42 tests (9,080 total)
Phase HS (2026-06-30): Coverage Expansion Sprint III -- 30 tests (9,110 total)
Phase HT (2026-06-30): Coverage Expansion Sprint IV -- 30 tests (9,140 total)
Phase HU (2026-06-30): Coverage Expansion Sprint V -- 30 tests (9,170 total)
Phase HV (2026-06-30): Coverage Expansion Sprint VI -- 30 tests (9,200 total)
Phase HW (2026-06-30): Coverage Expansion Sprint VII -- 30 tests (9,230 total)
Phase HX (2026-06-30): Coverage Expansion Sprint VIII -- 30 tests (9,260 total)
Phase HY (2026-06-30): Coverage Expansion Sprint IX -- 30 tests (9,290 total)
Phase M (2026-06-29): Renewal Conversion Rate Book -- 21 tests (4,835).
Phase N (2026-06-29): EV Settlement Wiring + Physical Suitability -- 26 tests (4,861).
Phase O (2026-06-29): Solar Dynamic Settlement Wiring -- 12 tests (4,851).
Phase P (2026-06-29): EV Smart Charging Shape (Overnight-Weighted) -- 12 tests (4,942).
Phase Q (2026-06-29): Battery Settlement Wiring -- 14 tests (4,865).
Phase R (2026-06-29): SEG Export Estimator -- 21 tests (4,886).
Phase S (2026-06-29): Dual-Fuel Billing Engine + Payment Ledger -- 44 tests (4,930).
Phase T (2026-06-29): ToU Tariff Profitability Assessor -- 16 tests (4,958).
Phase U (2026-06-29): EV Cross-Subsidy Register -- 16 tests (4,974).
Phase V (2026-06-29): ToU Migration Impact Scenario -- 16 tests (4,990).
Phase W (2026-06-29): Gas Boiler Daily HDD Shape -- 13 tests (5,003).
Phase X (2026-06-29): ToU Product Launch Decision Engine -- 25 tests (5,028).
Phase Y (2026-06-29): ToU Rate Card Optimiser -- 29 tests (5,057).
Phase Z (2026-06-29): Smart Meter Reconciliation Book -- 23 tests (5,080).

## Website Sections

- / (index.html) — LIVE: dashboard with sim run metrics, auto-updated
- /staging-status/ — LIVE: pending and actioned staging files
- /timeline/ — LIVE: build phase timeline
- /snapshots/ — LIVE: historical run dashboards
- /customers/ — STUB: placeholder, customer data not exposed
- /project/ — STUB: placeholder with docs links
- /sim/ — STUB: placeholder, sim detail not rendered as HTML

## Key Files

- docs/status/LATEST.md — always-current one-page status (plain text)
- docs/BUILD_STATE.md — full phase + module inventory (Markdown)
- docs/PROJECT_OVERVIEW.md — authoritative architecture and build history
- CLAUDE.md — agent instructions + current phase state
- docs/claude/phase-history.md — archived phase details (GA-GZ)
- CLAUDE_HISTORY.md — earliest phase details (pre-GA)
- docs/market_data/price_feed.json — live Elexon price data
- site/data/sim_data.json — dashboard JSON (parseable without JS)
- site/data/agent_status.json — background agent health
