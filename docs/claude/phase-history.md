# Phase History — Phases 30a–46a

Phase completion details. Earlier phases (1–29) in CLAUDE_HISTORY.md.

---

## Model evaluation (2026-06-21)

gemma4:12b vs qwen3:14b — **keep qwen3:14b**.
- Same accuracy on all 3 tasks (dispatcher 10/10, discovery 5/5, risk committee valid)
- qwen3:14b 4× faster: 4.5s/call vs 20.9s/call (dispatcher), 11s vs 34.6s (risk committee)
- gemma4:12b 7.6GB but slower inference on RTX 3060 12GB. Switching → sim ~3 hrs, not 38 min.

---

## The five hollow gaps (status as of 2026-06-22)

1. **Customer events firing — DEEPENED (Phase 12b).** Six customers have actually churned with
   specific dates. Company CRM has `CompanyEventLog` with dated Churn/Acquisition/RetentionEvent
   artefacts. Company churn estimate >30% triggers retention offer reducing SIM churn by 20%.

2. **Ledger — CLOSED.** 2.2M ledger events: billing, settlement, capital charges, VAT, bad debt,
   acquisition. P&L is the sum of transactions, not a formula.

3. **SIM/company barrier — DIVERGENCE NOW MEASURED (Phase 12e).** Company has own tariff engine
   (observable forward prices only) and churn estimator. Divergence from SIM ground truth measured
   year-by-year in annual report. Full operational independence is the long-horizon goal.

4. **HH smart meter path — CLOSED.** `simulation/hh_consumption.py` — C7-C9 on real HH shapes.

5. **Reporting — CLOSED.** Annual report, CTS, CLV, churn/pricing basis risk on GitHub Pages.

---

## Simulation Design Decisions

### Minimum hedge mandate (Phase 5c, 14 June 2026)

Redesigned from "speculative book with risk governor" to "supply obligation first, active position
second" — matching how real suppliers (e.g. EDF) actually operate.

- `sim/hedging_strategy.MIN_HEDGE_FLOOR = 0.85` — every term starts at least 85% hedged.
- Active position (≤15% unhedged) is what the risk committee manages. `evolve_hedge_fraction()`
  can raise toward 1.0 but never drops below the floor.
- Capital cost charged only on unhedged (naked) portion — raising the floor to 0.85 caps naked
  exposure at 15% by construction.
- Old reactive model preserved as `docs/reports/run_output_old_reactive_model_pre5c.json`.

---

## Phase 46a COMPLETE (2026-06-23) — Gas Risk Premium Further Reduced 10%→5%

0 new tests (1,250+, existing tests updated). Constants change only.
- `company/pricing/tariff_engine.py`: `GAS_RISK_PREMIUM_FRACTION` 10% → 5%.
- With 5% gas and 8% electricity premiums: in stable markets, company_fwd (gas) ≈ SIM_fwd (gas) → near-zero margin.
  UK resi gas suppliers DO report near-zero/thin margins in stable years (Cornwall Insight 2020: ~1-2%).
  Margins emerge when 120-day mean lags below falling EWMA (company advantages from lagged pricing).
- Electricity premium stays at 8% (higher spot volatility exposure + I&C competitive pricing pressure).
- Sanity check expectation: resi/gas ~0-2% net in stable markets, potentially negative in 2021-22 crisis years.
  9-year cumulative should fall within -5% to +5% range.
- Tests updated: `test_gas_risk_premium_higher_than_electricity` renamed since elec > gas now.

---

## Phase 45c COMPLETE (2026-06-23) — Forward Curve Risk Premium Recalibration

8 new tests (1,250+ total). Calibration fix, no interface change.
- `company/pricing/tariff_engine.py`: `COMPANY_RISK_PREMIUM_FRACTION` 15% → 8%, `GAS_RISK_PREMIUM_FRACTION` 20% → 10%.
- Root cause: original 15%/20% created systematic overpricing vs SIM's EWMA-based forward. C_IC1/C_IC2 showed
  33% cumulative net margin over 9 years (industry I&C benchmark: 3–8%). Gas pass-through already fixed in Phase 45b;
  this fixes fixed-tariff electricity and gas.
- UK I&C competitive market: brokers price at 5–8% above NAP/baseload. Gas has higher basis risk so premium > elec.
- 8 unit tests confirm constants, forward price calculation, and that gas > elec premium still holds.

---

## Phase 45b COMPLETE (2026-06-23) — Gas Pass-Through Bills at Spot Price

6 new tests (1,242+ total). Settlement change for pass-through gas.
- `simulation/gas_settlement.py`: `GAS_PASS_THROUGH_SERVICE_FEE_GBP_PER_MWH = 2.0`.
  Pass-through customers now billed at `daily_mwh × (spot + £2/MWh)` instead of `unit_rate = company_fwd × 1.20 + £2`.
- Prior model applied a 20% risk premium (gas_risk_premium_fraction) to a 120-day rolling mean even for pass-through
  customers, creating 15–20% net margin on gas where industry benchmark is 2–6% (pass-through ≈ 0%).
- Fixed tariffs unaffected. Policy + network costs still added on top of spot billing.
- Discovered from Phase 45a sanity check: I&C/gas segment showing 19.9% net (bench 2–6%).

---

## Phase 45a COMPLETE (2026-06-23) — Revenue & Margin Sanity Check

0 new tests (1,290+ total). Standing post-run calibration guard.
- `tools/revenue_sanity_check.py`: P&L waterfall (supply revenue → wholesale → gross → policy+network → capital → net)
  + per-segment net% vs Ofgem/CMA benchmarks (resi 2–5%, SME 3–8%, I&C 3–15%). Exits 1 on anomaly.
- `saas/reporting/annual_report.py`: `_section_revenue_sanity()` after Customer P&L Ranking — embedded in every report.
- `background/process_run_complete.py`: sanity check logged post-dashboard on every run_complete.
- `site/snapshots/DASHBOARD_*.json`: standalone companion JSON for strategy advisor (no JavaScript needed).
- Ledger clarification: `_ledger_headline.net_margin_gbp` = gross − capital only (policy/network cancel as
  billed to customer ≈ paid by company). True economic net = record-sum `net_margin_gbp` (deducts all costs).
- Anomalies flagged: I&C/gas 19.9% (bench 2–6%), resi/elec 12.2% (bench 2–5%), resi/gas 11.8% (bench 2–4%).
  Root cause: company_fwd overestimates actual forward on pass-through customers; resi CCL-exempt. Calibration
  investigation deferred to Phase 45b or discovery agent.

## Phase 44a COMPLETE (2026-06-23) — Customer Profitability Feedback

13 new tests (1,290+ total). Closes "Pricing actions not implemented" Known Gap in ASSUMPTIONS.md.
- `company/crm/customer_profitability.py`: `estimate_prior_term_net_margin()` — reads company's own
  net_margin_gbp fields from prior billing records, returns total £ for most recent prior term.
  `compute_profitability_uplift()` — returns £3/MWh (NET_NEGATIVE_UPLIFT) if net < 0, else 0.
  Minimum 48 records required before making judgement (first term always gets base pricing).
- `saas/tariff_pricing.py`: `profitability_uplift_per_mwh` parameter (default 0.0, backward compatible).
- `simulation/run_phase2b.py`: uplift applied for electricity fixed/pass-through terms at term_index >= 1.
  Logged in `profitability_uplift_log`. Churn model handles outcome naturally (higher rate → higher churn).
- Epistemic compliance: company uses only its own billing records — observable accounting data only.
- Uplift doesn't fire in 1-year test (no prior-term history); fires from year 2+ as expected.

## Phase 43b COMPLETE (2026-06-23) — Adaptive Trading Desk, VaR-Constrained

15 new tests (1,257+ total). Per-term VaR-constrained hedge decision replaces static RESET_HEDGE_FRACTION.
- `company/trading/hedge_decision.py`: `estimate_price_volatility()` — 90-day EWMA (λ=0.94) of
  squared log returns, annualized × √252, floored at 10% / capped at 250%.
  `decide_hedge_fraction()` — solves `hf = 1 − max_var / (fwd × eac_mwh_term × vol_term × 1.6449)`,
  clamped to `[COMPANY_MIN_HEDGE_FLOOR, 1.0]`. High vol → VaR constraint binds → higher hf.
  `compute_bid_ask_cost()` — 0.5% + 0.2%/year of tenor, capped at 1.5% (N2EX OTC calibration).
- `company/trading/forward_book.py`: `bid_ask_cost_gbp` field; `total_bid_ask_cost_gbp` property;
  `summary()` now includes bid-ask cost.
- `simulation/run_phase2b.py`: per-term VaR decision before `naked_kwh =` in else-branch (fixed/pass-through);
  `compute_bid_ask_cost()` wired into ForwardContract opening.
- `saas/reporting/annual_report.py`: `_section_trading_pnl()` — year-by-year hedge P&L vs gross margin %.
- Integration result: 93 contracts, 46,345 MWh hedged, £463k hedge P&L, £35k bid-ask cost.

## Phase 43a COMPLETE (2026-06-23) — Company Trading Book

14 new tests (1,242+ total). First SIM/company full independence for hedging decisions.
- `company/trading/forward_book.py`: `ForwardContract(customer_id, term_start, term_end, notional_mwh,
  agreed_price_gbp_per_mwh, hedge_fraction)` — frozen dataclass; `TradingBook.open_hedge()` registers
  at tariff signing; `TradingBook.settle_period()` computes hedge P&L per half-hour period.
- Epistemic compliance: `agreed_price = company_fwd` (company's own tariff engine output only; uses
  published forward market data — no SIM internals).
- `simulation/run_phase2b.py`: for each fixed/pass-through electricity term, opens a `ForwardContract`
  and calls `settle_period()` for each record, adding `hedge_pnl_gbp` field. `trading_book.summary()`
  added to run output (contract_count, total_hedged_mwh, total_hedge_pnl_gbp).
- 1-year fast run: 93 contracts, 44,196 MWh hedged, £406k hedge P&L. Net margin unchanged —
  hedge P&L is now decomposed from supply margin, not added to it.
- Fixed stale test: `test_pass_through_customer_in_fast_run` used wrong key `all_settlement_records`
  (correct: `all_records`).

## Phase 42 COMPLETE (2026-06-22) — Gas-specific seasonal forward curve

8 new tests. `sim/forward_curve.py`:
- `GAS_MONTH_SEASONAL_MULTIPLIER`: steeper winter premium (Jan: 1.22) and deeper summer discount
  (Jul: 0.80) vs electricity (Jan: 1.12, Jul: 0.88). UK gas seasonality 2-3× more extreme.
- `GAS_BASE_TERM_PREMIUM = 0.05` (vs electricity 0.06 — gas forward market more liquid).
- `generate_forward_price()`: `fuel` param added (`"electricity"` default, backward-compat).
- `_seasonal_shape()`: `fuel` param selects correct multiplier table.
- Weather adjustment NOT applied to gas (uses calibrated seasonal shape instead).
- `simulation/run_phase2b.py`, `simulation/run_segments.py`: pass `fuel="gas"` on gas calls.

## Phase 41a COMPLETE (2026-06-22) — Flex/trading tariff

8 new tests. All 4 UK I&C tariff types now implemented.
- `saas/customers.py`: `C_IC4` — 3 GWh supermarket, Manchester, `tariff_type: "flex"`.
- `sim/hh_data/C_IC4.csv`: opening-hours peak + base refrigeration, 3 GWh/year.
- `simulation/hedged_settlement.py`: `run_flex_term()` — reference = 7-day rolling spot (PIT safe);
  revenue = (ref + £2/MWh markup) × consumption; capital_cost = 0; hedge_fraction = 1.0.
- `simulation/run_phase2b.py`: dispatches to `run_flex_term()`. Skips risk assessment for flex.

## Phase 41-prep COMPLETE (2026-06-22) — Forward curve reform (EWMA + term structure)

10 new tests. `sim/forward_curve.py` rewritten:
- `forward = spot_EWMA × seasonal_shape × (1 + term_premium)`
- EWMA half-life 30 days (vs 90-day SMA). Monthly seasonal multipliers. Term premium 6% for 1yr.
- Research: `docs/market_research/uk_power_forward_curves_2016_2025.md`

## Phase 40c COMPLETE (2026-06-22) — Deemed rate (out-of-contract I&C)

8 new tests.
- `C_IC1`/`C_IC2`: `deemed_gap_days: 30` — 30-day out-of-contract window on each renewal.
- `run_deemed_term()`: billed at spot × (1 + 0.20 premium). Capital cost = 0.

## Phase 40b COMPLETE (2026-06-22) — Gas pass-through tariff + tariff column in report

7 new tests.
- `C_IC3g`: 5 GWh industrial gas, Teesside, `tariff_type: "pass_through"`.
- `run_gas_term(pass_through=True)`: actual gas network + CCL + GGL billed at settlement.

## Phase 40a COMPLETE (2026-06-22) — I&C pass-through tariff

9 new tests + 2 stale fixes.
- `C_IC3`: 4 GWh chemical plant, Teesside, `tariff_type: "pass_through"`.
- `run_hedged_term(pass_through=True)`: actual policy + network passed through. Company bears only
  wholesale spread risk.

## Phase 39a COMPLETE (2026-06-22) — SVT comparative pricing for passive renewers

18 new tests (1,127 total).
- `simulation/svt_rates.py`: Ofgem Default Tariff Cap rates 2016–2029 (£/MWh).
- SVT comparison table in annual report: at-risk (above SVT) vs protected (below SVT).

## Phase 38a COMPLETE (2026-06-22) — Scenario comparison runner

12 new tests (1,109 total).
- `simulation/scenario_comparison.py`: runs all 5 scenarios, returns sorted KPI comparison.
- `format_comparison_table()`: markdown table — all scenarios side-by-side.

## Phase 37a COMPLETE (2026-06-22) — Forward scenario metadata banner in annual report

7 new tests (1,097 total).
- `_section_scenario_metadata(data)`: banner when `scenario_name` is set. Silent for historical runs.

## Phase 36a COMPLETE (2026-06-22) — Scenario integration runner

9 new tests (1,090 total).
- `simulation/run_scenario.py`: `run_forward_scenario()` — monkey-patches price feeds transparently.

## Phase 35b COMPLETE (2026-06-22) — Gas forward scenario generator

9 new tests (1,081 total).
- `sim/scenario/gas_scenario_generator.py`: regime-conditioned NBP prices, correlated with electricity.
- 5 matching scenario presets. Floor: £5/MWh (gas doesn't go negative).

## Phase 35a COMPLETE (2026-06-22) — Bimodal electricity forward scenario price generator

16 new tests.
- `sim/scenario/bimodal_generator.py`: 5 named scenarios (baseline_2025, central_2027,
  stress_dunkelflaute_2027, low_renewables_2027, battery_saturation_2029).
- Two-regime Markov: lower mode £38-60/MWh ↔ upper mode £100-130/MWh. Negative price injection.

## Phase 34a COMPLETE (2026-06-22) — 42-day renewal notice period

9 new tests.
- `NOTICE_DAYS = 42`. Company prices tariff using data from 42 days before term start.
- Effect in crisis: company priced pre-spike → amplifies basis risk.

## Phase 33b COMPLETE (2026-06-22) — Active/passive split in annual report

6 new tests (1,047 total).
- `_section_active_passive_renewal(data)`: active/passive counts, error tables. Backward compatible.

## Phase 33a COMPLETE (2026-06-22) — Active/passive renewal split

10 new tests (1,041 total).
- `PASSIVE_BASE_CHURN_RATE=0.05`, cap 10%. 65% passive (SVT rollers), 35% active.
- 2022 crisis: all renewals forced passive (no fixed deals available).

## Phase 32a COMPLETE (2026-06-22) — Gas book year-by-year P&L in annual report

11 new tests (1,031 total).
- `_section_gas_pl(data)`: 8-column table Year | Revenue | Wholesale | Gross | Policy | Network | Capital | Net.

## Phase 31a COMPLETE (2026-06-22) — Feed-in Tariff (FiT) levy

20 new tests (943 total).
- `_FIT_LEVY_BY_YEAR` (£4.10–8.47/MWh, 2016–2024). Applies to ALL demand (no domestic exemption).
- `policy_cost_gbp = RO + CfD + CCL + CM + FiT`

## Phase 30b COMPLETE (2026-06-22) — Gas policy costs (CCL, network, GGL)

33 new tests.
- Gas CCL (resi exempt), gas network (£9-18/MWh), Green Gas Levy (per-MPRN, from Nov 2021).

## Phase 30a COMPLETE (2026-06-22) — Capacity Market (CM) levy

16 new tests (923 total).
- `_CM_LEVY_BY_YEAR` (£0.5–7.27/MWh, 2016–2024). Applies to ALL demand.

For Phases 12–29, see CLAUDE_HISTORY.md.

## Architecture Stages 2-4 COMPLETE (2026-06-23) — Agent infrastructure

- Stage 2: `.claude/agents/discovery-agent.md` — market research agent, scoped to `docs/market_research/`, structured findings format.
- Stage 3: `.claude/agents/epistemic-verifier.md` + `tools/epistemic_verifier.py` — SIM/company barrier scanner, in phase-close checklist.
- Stage 4: `background/agent_protocol.py` — `AgentMessage` + `IntentType`, 18 tests, live in sim_runner.

## Phase 43a COMPLETE (2026-06-23) — Company trading book

14 new tests (1,242+ total).
- `company/trading/forward_book.py`: `ForwardContract` + `TradingBook`. On each fixed/pass-through term signing, company opens a forward contract (agreed_price = company_fwd, notional = EAC × hf).
- `settle_period()` decomposes hedge P&L from supply margin each half-hour. `trading_book.summary()` in run output.

## Phase 44a COMPLETE (2026-06-23) — Customer profitability feedback

13 new tests (1,290+ total). Closes "Pricing actions not implemented" Known Gap.
- `company/crm/customer_profitability.py`: `estimate_prior_term_net_margin()` + `compute_profitability_uplift()`.
- Net-negative electricity customers receive £3/MWh uplift at renewal. Churn model handles consequence.

## Phase 44b COMPLETE (2026-06-23) — VaR-constrained hedging extended to gas

No new tests. `simulation/run_phase2b.py`: gas fixed terms now call `decide_hedge_fraction()`.
- Same EWMA vol model, 95% VaR ≤ 15% term revenue. Pass-through skipped. Committee overrides take precedence.

## Phase 45a COMPLETE (2026-06-23) — Revenue & margin sanity check

0 new tests (1,236+ total).
- `tools/revenue_sanity_check.py`: P&L waterfall + per-segment net% vs Ofgem/CMA benchmarks.
- Anomalies detected: I&C/gas 19.9% (forward bias), resi 12.2%/11.8% (CCL-exempt + forward bias). Drove 45b/45c fixes.

## Phase 45b COMPLETE (2026-06-23) — Gas pass-through billed at spot

6 new tests (1,242+ total).
- `simulation/gas_settlement.py`: pass-through customers billed at daily spot + £2/MWh service fee.
- Eliminates artificial 19.9% I&C/gas net margin from 20% risk premium on non-risk-bearing billing.

## Phase 45c COMPLETE (2026-06-23) — Forward curve risk premium recalibration

8 new tests (1,250+ total).
- `company/pricing/tariff_engine.py`: `COMPANY_RISK_PREMIUM_FRACTION` 15%→8%, `GAS_RISK_PREMIUM_FRACTION` 20%→10%.
- UK I&C benchmark: 5-8% above NAP. Original 15%/20% drove C_IC1/C_IC2 to 33% net vs 3-8% industry.

## Phase 46a COMPLETE (2026-06-23) — Gas risk premium 10%→5%

0 new tests (1,250+ total).
- `GAS_RISK_PREMIUM_FRACTION` 10%→5% in `tariff_engine.py`. UK resi gas margins near-zero in stable markets.
- Electricity (8%) now higher than gas (5%).

## Phase 47a COMPLETE (2026-06-24) — Ofgem domestic price cap

10 new tests. `company/pricing/ofgem_price_cap.py`: `get_cap_unit_rate_gbp_per_mwh(fuel, year)`.
- Applied in `run_phase2b.py` after all uplifts for resi fixed customers. Cap bites 2021+, resi margins compress.

## Phase 47b COMPLETE (2026-06-24) — Cap-aware acquisition gate

10 new tests (1,270+ total).
- `saas/growth_mandate.py`: `should_attempt_acquisition()` — gate fires when Ofgem cap < company_fwd.
- Applied before `roll_acquisition()`. Crisis-year pause emerges from economics, not hard-coded years.


## Phase 62 COMPLETE (2026-06-25) -- Standing charges (electricity + gas, resi/SME)

12 new tests (1,456 total).
- simulation/policy_costs.py: get_electricity_standing_charge_per_day() and get_gas_standing_charge_per_day() -- year-indexed tables (2016-2024) from Ofgem quarterly tariff tracker. Resi elec 24p/day (2016) to 61p/day (2024); gas 22p to 31p. SME 1.5x resi multiplier. I&C = 0.0 (capacity charges in BSC settlement).
- simulation/hedged_settlement.py: SC prorated per half-hour period (daily/48). Added to revenue_gbp and margin_gbp; standing_charge_gbp field in every electricity record.
- simulation/gas_settlement.py: daily gas SC added to revenue_gbp; gas_standing_charge_gbp field in every gas record.
- Prior model: no standing charge. Fixed-rate customers implicitly underpriced vs real market where SC adds ~100-200 GBP/yr additional supplier income.


---

## Phases 55–65 (archived from CLAUDE.md Current State)

**Phase 55 COMPLETE (2026-06-25):** Ofgem MCR solvency signal — 12 new tests (1,389 passing). `saas/capital/solvency.py` (new): `compute_solvency_signal(treasury, customers)` → status OK/Watch/STRESS. MCR floor £130/dual-fuel account; Watch < 2×, STRESS < 1×. `_section_solvency_signal()` updated; formal ratio column in annual report.
**Phase 56 COMPLETE (2026-06-25):** Gas pass-through hedge zero-locked — 5 new tests (1,394 passing). `simulation/run_phase2b.py`: pass-through gas `hf` forced to 0.0 (was 0.85). Wrong-way risk eliminated: C_IC3g had +42% gas margin 2021 (hedge windfall) and -86% 2023 (hedge loss on reversion). Cost now = spot × vol; margin = service_fee + network + policy only.
**Phase 57 COMPLETE (2026-06-25):** Year-varying bad debt (crisis surge) — 9 new tests (1,403 passing). `saas/cost_to_serve.py`: `get_bad_debt_rate(year, segment)` — 2021 resi 4%, 2022 8% (Ofgem 2.4M arrears), 2023 5%. `run_phase2b.py`: bad_debt_gbp deducted from net_margin_gbp + treasury each settlement period.
**Phase 58 COMPLETE (2026-06-25):** Weather-adjusted gas consumption (HDD model) — 15 new tests (1,418 passing). `sim/weather_hdd.py` (new): `get_weather_factor(year, month, cid)` — actual/reference HDD ratio [0.3, 2.0]; UK 1991–2020 climate normals. `gas_settlement.py`: `weather_factor` param scales `daily_kwh`; field in every record. `run_phase2b.py`: resi/SME gas gets term-averaged factor; I&C process gas unchanged.
**Phase 59 COMPLETE (2026-06-25):** Monthly gas consumption seasonality — 10 new tests (1,428 passing).. `simulation/gas_settlement.py`: `GAS_CONSUMPTION_MONTHLY_PROFILE` (Jan=1.884, Jul=0.353, 5.3× ratio). Per-day `daily_kwh = AQ/365 × seasonal × weather`. Prior model: flat AQ/365 every day.
**Phase 60 COMPLETE (2026-06-25):** I&C gas flat seasonal profile — 8 new tests (1,436 passing). `GAS_IC_CONSUMPTION_MONTHLY_PROFILE` in `gas_settlement.py`: Jan=1.075, Jul=0.913, 1.18× ratio. `run_gas_term()` selects resi vs I&C profile by `segment`. Prior: resi 5.3× swing on 5M kWh I&C = £1k/day distortion.
**Phase 61 COMPLETE (2026-06-25):** Flex tariff policy pass-through fix — 8 new tests (1,444 passing). `run_flex_term()` in `hedged_settlement.py`: revenue now includes policy+network recovery (pass-through to customer). Prior: supplier absorbed all policy costs, creating £175k/yr artificial losses for C_IC4. Net = markup x volume only; C_IC4 total net swings from -£1.06M to +£33k.
**Phase 62 COMPLETE (2026-06-25):** Standing charges (electricity + gas, resi/SME) -- 12 new tests (1,456 passing). simulation/policy_costs.py: get_electricity_standing_charge_per_day() and get_gas_standing_charge_per_day(), year-indexed Ofgem tariff tracker data 2016-2024. Resi elec 24p/day->61p/day, gas 22p->31p; SME 1.5x multiplier; I&C=0. hedged_settlement.py: SC prorated per half-hour period, added to revenue+margin, standing_charge_gbp field. gas_settlement.py: daily SC in gas_standing_charge_gbp field.
**Phase 63 COMPLETE (2026-06-25):** F1 Double-entry ledger — 24 new tests (1,480 passing). `company/finance/double_entry.py` (new): chart of accounts (13 codes, 1xxx–6xxx), `to_journal_entry()` for all 9 ledger event types, `trial_balance()`, `income_statement()`, `balance_sheet()`. P&L and balance sheet now emerge from accounts; Assets = Liabilities + Equity verified. Foundation for FI1 management accounts and C1 invoices. (Destinationvision.md F1)
**Phase 64 COMPLETE (2026-06-25):** FI1 Management Accounts -- 13 new tests (1,493 passing). company/finance/management_accounts.py (new): build_monthly_accounts(), annual_management_pack(), cross_check(). Annual report _section_management_accounts(): 10-year P&L table (Revenue/COGS/Gross/OpEx/Net/Cash/Equity all from account codes 4xxx/5xxx/6xxx), cross-check vs simulation net (<=5% variance), final-year balance sheet with A=L+E. FI1 closed.
**Phase 65 COMPLETE (2026-06-25):** FI2 Budget vs Actual -- 12 new tests (1,505 passing). company/finance/budget.py (new): _BUDGET_BY_YEAR (2016-2025, prior-year-actuals * 1.10 revenue / * 1.05 opex), variance_report(), monthly_variance(), traffic_light() (GREEN/AMBER/RED). Annual report: _section_budget_vs_actual() 10-year RAG table. 2021 AMBER (-13.7%), 2022 RED (+18.3%), 2023 RED (-21.1%). FI2 closed.


## Phases 66–88 (archived from CLAUDE.md 2026-06-26)

**Phase 66 COMPLETE (2026-06-25):** C1 Invoice Line Items + Text Format -- 9 new tests (1,514 passing). company/billing/invoice.py: schema extended with commodity_amount_gbp/non_commodity_amount_gbp columns; create_invoice() uses bill line items (standing charge, non-commodity, VAT) directly; format_invoice_text() renders structured text invoice with energy/levies/standing/VAT/total. C1 line-item invoice documents now working.
**Phase 67 COMPLETE (2026-06-25):** C3 Payment Processing + Debt Aging -- 10 new tests (1,524 passing). company/billing/payments.py (new): reconcile_payment() by customer_id+billing_period_end (paid/partially_paid/no_match), reconcile_payments() batch counts, age_debt() bad_debt after 90 days, debt_aging_summary() four aging buckets. Billing lifecycle complete: bill->invoice->payment->reconciliation->bad_debt. C3 closed.
**Phase 68 COMPLETE (2026-06-25):** C2 Customer Portal MVP -- 14 new tests (1,538 passing). company/portal/app.py (new): FastAPI app with routes GET /, POST /login (account number auth), GET /account/{id} (dashboard), GET /account/{id}/bills (invoice list). Jinja2 HTML templates (login/dashboard/bills). Reads company layer only: saas/customers.py + invoice DB. Rich can now log in as C1 and see account profile, billing summary, and invoice history. C2 closed.
**Phase 69 COMPLETE (2026-06-25):** C4 CRM Service Interaction Log -- 12 new tests (1,550 passing). company/crm/service_log.py (new): ServiceEvent dataclass (channel/reason/outcome/agent_type/complaint_flag/vulnerability_flag), ServiceLog with record_contact(), contacts_for_customer(), complaints(), complaint_rate(), complaint_stats(year), vulnerability_register(), resolve_vulnerability(), as_dicts(). CRM moves from lifecycle-only to full service history. C4 closed.
**Phase 70 COMPLETE (2026-06-25):** FI3 Treasury Management -- 12 new tests (1,562 passing). company/finance/treasury.py (new): working_capital(balance_sheet), cash_flow_by_year(pack), annual_cash_changes(pack), project_treasury(pack, base_year, horizon=3) -- 3-yr trend extrapolation, treasury_health(pack, year, customer_count) -- MCR headroom + OK/WATCH/CRITICAL status. Uses management accounts balance sheets only. FI3 closed.
**Phase 71 COMPLETE (2026-06-25):** T3 Mark-to-Market Valuation -- 10 new tests (1,572 passing). company/trading/forward_book.py: mark_to_market(contract, current_price) -> {mtm_pnl_gbp, in_the_money, ...}, portfolio_mtm(current_prices_by_customer) -> {total_mtm_pnl_gbp, positions_priced, in/out counts, positions[]}. MTM = (market - agreed) x notional_mwh. Skips positions with no current price. T3 closed.
**Phase 72 COMPLETE (2026-06-25):** T2 Position Management -- 10 new tests (1,582 passing). company/trading/forward_book.py: HedgeAmendment + PositionClosure dataclasses; amend_hedge() records old->new fraction with dated audit trail; close_position() records realised P&L (close_price-agreed)*notional; closed_contracts(), amendments(), closures() accessors. open_contracts() now excludes closed; portfolio_mtm() likewise. T2 closed.
**Phase 73 COMPLETE (2026-06-26):** T1 Trading Desk Interface -- 7 new tests (1,589 passing). company/portal/app.py: GET /trading route + _load_trading_data() reads hedge_effectiveness from run_output_latest.json; templates/trading.html: hedge portfolio summary, best/worst decisions, P&L by year table. T1 closed -- trading desk view live on portal.
**Phase 74 COMPLETE (2026-06-26):** M2 Regulatory Reporting -- 13 new tests (1,602 passing). company/regulatory/compliance.py (new): smart_meter_target(year, segment), smart_meter_compliance_status() COMPLIANT/AT_RISK/BREACH (Ofgem SMETS2 mandate), check_price_cap_compliance() (SLC breach detection), generate_css_filing(service_log, year) (annual CSS return: complaints, resolution rate, vulnerable contacts), annual_turnover_fee(). M2 closed.
**Phase 75 COMPLETE (2026-06-26):** M1 Elexon Settlement Interface -- 10 new tests (1,612 passing). company/market/settlement_reconciler.py (new): SettlementStatement dataclass, receive_settlement(), reconcile_against_bill() (imbalance = billed - settled, flagged if >5% or >£10), reconcile_period_batch() (batch reconciliation with counts), imbalance_summary() (favourable/unfavourable/flagged/net_position). M1 closed.
**Phase 76 COMPLETE (2026-06-26):** M3 Market Data Feed -- 10 new tests (1,622 passing). company/market/price_feed.py (new): PriceFeed class reads published JSON feed file (no SIM module imports), SpotPrice dataclass, get_latest_spot(), get_forward_price_estimate() (mean + risk premium), is_stale() (configurable max age), summary(); publish_feed() for SIM pipeline to write feed. M3 closed -- all Destinationvision gaps now closed.
**Phase 77 COMPLETE (2026-06-26):** Portal Phase 2: Tariff Comparison -- 17 new tests (1,639 passing). company/pricing/tariff_comparison.py (new): unit_rate_from_forward(), annual_cost_gbp(), compare_tariffs() (3 options: Fixed 1yr/2yr/Variable SVT, sorted by est. annual cost, segment-aware VAT+SC). Portal: GET /account/{id}/tariff-compare + POST /account/{id}/switch-tariff (generates reference, renders confirm page). templates: tariff_compare.html + tariff_switch_confirm.html.
**Phase 82 COMPLETE (2026-06-26):** HH consumption feed + portal half-hourly view -- 13 new tests (1,696 passing). `simulation/publish_consumption_data.py` (new): reads sim/hh_data/{C7,C8,C9}.csv, writes 288-record JSON feed (2 days × 48 periods × 3 customers). `company/billing/hh_consumption.py` (new): get_hh_consumption() + recent_hh_periods() reads feed. Portal consumption route: HH customers see live half-hourly table (last 24h). process_run_complete.py: calls publish_consumption() after each sim run.
**Phase 83 COMPLETE (2026-06-26):** Portal payment submission -- 12 new tests (1,708 passing). `POST /account/{id}/pay`: accepts invoice_number+amount from bills page, calls reconcile_payment(), returns payment_confirm.html (paid/partially_paid/no_match). `bills.html`: Pay button on unpaid rows. Customer journey complete: login→dashboard→bills→pay→confirmation.
**Phase 84 COMPLETE (2026-06-26):** Regulatory Compliance Dashboard -- 13 new tests (1,721 passing). GET /regulatory: smart meter penetration vs Ofgem SMETS2 target (COMPLIANT/AT_RISK/BREACH), MCR capital adequacy (OK/Watch/STRESS), annual turnover fee. regulatory.html (new). Dashboard nav: Regulatory link. Uses company/regulatory/compliance.py + saas/capital/solvency.py.
**Phase 85 COMPLETE (2026-06-26):** Admin Portfolio Overview -- 11 new tests (1,732 passing). GET /admin: full customer portfolio table (segment/commodity/EAC/smart meter/outstanding/paid) + summary cards (accounts, billed, outstanding, bad debt). _load_admin_data() aggregates invoice summaries across all accounts.
**Phase 86 COMPLETE (2026-06-26):** Account Statement -- 11 new tests (1,743 passing). GET /account/{id}/statement: all invoices + balance summary (billed/paid/bad debt/outstanding), print-optimised (@media print CSS, Print button). statement.html (new). Nav: Statement link on dashboard + bills page.
**Phase 87 COMPLETE (2026-06-26):** EAC Calibration from billing history -- 12 new tests (1,755 passing). company/billing/eac_calibration.py (new): calibrate_eac() lookback window annualised from invoice DB, calibrate_all_customers(), eac_drift() drift_pct + direction. Consumption portal: calibrated EAC vs original with % drift.
**Phase 88 COMPLETE (2026-06-26):** Direct Debit Mandate -- 21 new tests (1,776 passing). company/billing/direct_debit.py (new): DDMandate dataclass, set_mandate(), get_mandate(), cancel_mandate(), is_dd_customer(), list_mandates() with SQLite persistence. Portal: GET/POST /account/{id}/direct-debit + POST /cancel; direct_debit.html; Dashboard DD link.


## Phases 80-81, 89-99 (archived from CLAUDE.md 2026-06-26)

**Phase 80 COMPLETE (2026-06-26):** M3 price feed live: publish on every sim run -- 11 new tests (1,675 passing). simulation/publish_market_feed.py (new): build_feed_prices() (last 48 SSP HH periods + 10 NBP daily prices), publish() writes to docs/market_data/price_feed.json. process_run_complete.py: calls publish() after report gen. PriceFeed.is_available() now True; latest elec spot £100.58/MWh. Phase 76 M3 gap fully closed.
**Phase 81 COMPLETE (2026-06-26):** Trading desk: live spot prices from M3 feed -- 8 new tests (1,683 passing). company/portal/app.py: _load_spot_prices() reads PriceFeed, returns elec/gas spot + forward estimates. Trading route passes spot to template. trading.html: Market Data Feed section with spot/forward prices; stale warning. M3 end-to-end loop complete: SIM writes → feed file → company reads → trading desk displays.
**Phase 89 COMPLETE (2026-06-26):** ServiceLog SQLite persistence -- 8 new tests (1,784 passing). company/crm/service_log.py rewritten: ServiceLog(db_path=None) uses in-memory SQLite; ServiceLog(db_path=...) persists to file. All 12 existing CRM tests pass unchanged. Events, complaint stats, vulnerability register survive reconnect.
**Phase 90 COMPLETE (2026-06-26):** Contact Us portal form -- 11 new tests (1,795 passing). GET/POST /account/{id}/contact: reason dropdown (billing/payment/smart_meter/switch/complaint/general), notes textarea, formal complaint checkbox. ServiceEvent recorded in persistent _SERVICE_LOG on submit. contact.html (new). Dashboard Contact Us link.
**Phase 91 COMPLETE (2026-06-26):** CSS filing wired to persistent ServiceLog -- 9 new tests (1,804 passing). _load_regulatory_data() calls generate_css_filing(_SERVICE_LOG.as_dicts(), current_year); regulatory.html: CSS Annual Filing table (contacts/complaints/resolution rate/target met/vulnerable). CSS year = datetime.now().year not simulation latest_year.
**Phase 92 COMPLETE (2026-06-26):** Peak/off-peak band overlay on HH consumption -- 10 new tests (1,814 passing). _tou_band(date, hour): weekends always off-peak; weekdays peak 07:00-19:00. consumption route enriches hh_data with band field + is_tou flag. consumption.html: Band column, colour-coded rows, Peak/Off-Peak legend. Destinationvision C7 test now met.
**Phase 93 COMPLETE (2026-06-26):** Warm Home Discount (WHD) -- 11 new tests (1,825 passing). company/regulatory/warm_home_discount.py (new): WHD_REBATE_BY_YEAR 2017-2025, whd_eligible_customers() from vulnerability_register(), compute_whd_liability(), whd_summary(). Regulatory page WHD section; dashboard vulnerability badge.
**Phase 94 COMPLETE (2026-06-26):** Complaint deadline tracker -- 10 new tests (1,835 passing). _add_working_days() helper; ServiceLog.complaint_deadlines(): ack-by (2 working days) + resolve-by (8 weeks) per complaint, overdue flags. GET /admin/complaints + admin_complaints.html.
**Phase 95 COMPLETE (2026-06-26):** Contract renewal countdown -- 11 new tests (1,846 passing). company/billing/contract.py (new): contract_end_date() advances acquisition date by N-year steps (fixed_1yr/2yr), days_until_renewal(), is_in_notice_window(), renewal_summary(). Dashboard: renewal date + days countdown; notice window CTA → tariff compare.
**Phase 96 COMPLETE (2026-06-26):** Collections queue -- 10 new tests (1,856 passing). company/billing/collections.py (new): get_overdue_invoices() (unpaid/partially_paid past due), get_collections_queue() (per-customer aggregation, sorted by severity), _aging_tier() (0-30/30-60/60-90/90+ days). GET /admin/collections + admin_collections.html.
**Phase 97 COMPLETE (2026-06-26):** Annual cost forecast -- 8 new tests (1,864 passing). company/billing/consumption_forecast.py (new): forecast_annual_cost() uses calibrated EAC × unit_rate + SC × 365; UK seasonal quarterly split (Q1 30%/Q2 22%/Q3 18%/Q4 30%). Consumption page: estimated annual cost + quarterly breakdown.
**Phase 98 COMPLETE (2026-06-26):** Admin upcoming renewals -- 8 new tests (1,872 passing). GET /admin/renewals lists customers with contracts ending ≤90 days; colour-coded by urgency (≤14d red/≤30d amber/≤90d green). admin_renewals.html. Extends contract.py from Phase 95.
**Phase 99 COMPLETE (2026-06-26):** Market rate comparison widget -- 8 new tests (1,880 passing). company/market/rate_comparison.py (new): market_rate_comparison() compares PriceFeed forward estimate (£/MWh → p/kWh) vs effective contracted rate from last invoice; returns delta, protected flag, and human message. Consumption page: rate comparison widget.


## Phases 100-110 (archived from CLAUDE.md 2026-06-26)

**Phase 100 COMPLETE (2026-06-26):** Switching recommendation engine -- 11 new tests (1,891 passing). company/pricing/switching_recommendation.py (new): synthesises contract type, renewal window, market rate delta, and price cap into action (switch/stay/consider/N/A) + urgency (high/medium/low/none) + plain-text reason. Dashboard tariff advice widget.
**Phase 101 COMPLETE (2026-06-26):** EPC energy efficiency advice -- 11 new tests (1,902 passing). company/billing/efficiency_advice.py (new): epc_advice() (7 bands A-G, tailored tips), available_schemes() (ECO4/GBIS/SEG/BUS/WHD by rating), efficiency_summary(). Dashboard: collapsible EPC advice panel with scheme list.
**Phase 102 COMPLETE (2026-06-26):** Admin navigation hub -- 10 new tests (1,912 passing). admin.html: coloured quick-link buttons to Complaints/Collections/Renewals/Regulatory/Trading. All 22 portal routes reachable from admin in ≤2 clicks.
**Phase 103 COMPLETE (2026-06-26):** Smart meter upgrade request flow -- 8 new tests (1,920 passing). GET/POST /account/{id}/smart-meter. HH customers see confirmation; non-HH get request form (contact pref + notes). POST records CRM ServiceEvent (contact_reason=smart_meter, outcome=upgrade_requested, agent_type=self_service). Dashboard: non-HH prompt with link.
**Phase 104 COMPLETE (2026-06-26):** Ombudsman referral tracking -- 10 new tests (1,930 passing). ServiceLog.ombudsman_eligible() + ombudsman_count(): complaints unresolved >8 weeks. admin/complaints: red alert box listing eligible cases + deadlock letter prompt. regulatory dashboard: Ombudsman section (0 = green / >0 = red alert + link).
**Phase 105 COMPLETE (2026-06-26):** CSAT score tracking -- 9 new tests (1,939 passing). ServiceLog: csat_score INT column (with migration), csat_summary() (count/mean/promoter_pct), rate_contact(), latest_contact_id(). Contact portal: star rating widget on success page + POST /contact/rate. Admin: csat_summary() available for reporting.
**Phase 106 COMPLETE (2026-06-26):** CSAT admin reporting -- 7 new tests (1,946 passing). _load_admin_data() adds csat dict from _SERVICE_LOG.csat_summary(). Admin overview: 5th summary card (mean score / rated count). Closes CSAT feedback loop from portal capture to management view.
**Phase 107 COMPLETE (2026-06-26):** Usage benchmarking -- 10 new tests (1,956 passing). company/billing/usage_benchmark.py (new): _peer_group() (same home_type + EPC band), compute_percentile(), usage_benchmark() -> efficient/average/heavy + label. Consumption portal: peer comparison widget (colour-coded, peer count + median kWh).
**Phase 108 COMPLETE (2026-06-26):** Retention risk scoring -- 8 new tests (1,964 passing). company/crm/retention_risk.py (new): retention_risk() scores 0-5 from observable signals (overdue invoice +2, complaint +1, notice window +1, rate exposed +1) -> LOW/MEDIUM/HIGH tier. portfolio_risk_summary() aggregates by tier.
**Phase 109 COMPLETE (2026-06-26):** Admin retention dashboard -- 7 new tests (1,971 passing). GET /admin/retention: tier breakdown cards (HIGH/MEDIUM/LOW counts), sortable customer table (score/tier/signals). portfolio_risk_summary() aggregates all customers. Admin nav: Retention button.
**Phase 110 COMPLETE (2026-06-26):** Carbon footprint tracking -- 10 new tests (1,981 passing). company/billing/carbon_footprint.py (new): electricity_intensity() DESNZ grid gCO2e/kWh 2016-2025 (266→115, -57%), estimate_carbon() (elec + gas), carbon_trend(). Consumption portal: annual CO2e footprint widget with Ofgem fuel mix intensity.


## Phases 111-118 (archived from CLAUDE.md 2026-06-27)

**Phase 111 COMPLETE (2026-06-26):** Fuel mix disclosure -- 9 new tests (1,990 passing). company/billing/fuel_mix.py (new): _FUEL_MIX_BY_YEAR 2016-2025 (24.6%→55% renewable), get_fuel_mix(), fuel_mix_summary() (renewable/low-carbon/fossil pct + trend direction). Regulatory page: Fuel Mix Disclosure table.
**Phase 112 COMPLETE (2026-06-26):** Vulnerability register admin view -- 8 new tests (1,998 passing). GET /admin/vulnerability: full register (active + resolved), WHD badge if eligible, Contact button per row. Admin nav: Vulnerability button. whd_eligible_customers() wired in.
**Phase 113 COMPLETE (2026-06-26):** Direct Debit mandate management -- 12 new tests (2,010 passing). company/billing/direct_debit.py (new): DirectDebitMandate + DDPaymentAttempt dataclasses, DirectDebitBook (create_mandate, record_attempt, cancel, reinstate, failed_mandates, dd_summary). 2-strike suspension rule (BACS standard). CLAUDE.md trimmed 179→166 lines (phases 80-99 archived).
**Phase 114 COMPLETE (2026-06-26):** MPAN/MPRN meter point registry -- 17 new tests (2,027 passing). company/billing/meter_points.py (new): MeterPoint + MeterPointRegistry; validate_mpan() (13-digit), validate_mprn() (6-10 digit Xoserve); infer_profile_class() (PC1-5 from segment/metering); registered/unregistered tracking; summary().
**Phase 115 COMPLETE (2026-06-26):** Supplier switching request tracking -- 11 new tests (2,038 passing). company/billing/switching.py (new): SwitchRequest dataclass (gain/loss, 14-day objection window, is_objectable), SwitchingBook (record/complete/object_to/withdraw, pending_losses, switching_summary with net_completed).
**Phase 116 COMPLETE (2026-06-26):** Energy theft / loss indicator -- 10 new tests (2,048 passing). company/billing/theft_indicator.py (new): classify_anomaly() (ok/watch/investigate thresholds: <65%/<40% of EAC), screen_portfolio() (sorted by ratio). Ofgem reporting duty flagged in message.
**Phase 117 COMPLETE (2026-06-26):** SoLR risk assessment -- 10 new tests (2,058 passing). company/regulatory/solr.py (new): solr_capital_requirement() (levy + bad_debt_risk vs treasury, SUSTAINABLE/MARGINAL/UNSUSTAINABLE), solr_revenue_upside() (SVT retained book), solr_scenario() (small/medium/large/bulb_scale). 2021-22 crisis calibrated.
**Phase 118 COMPLETE (2026-06-26):** DTN message log -- 10 new tests (2,068 passing). company/market/dtn_log.py (new): DtnMessage + DtnLog; D-series electricity flows (D0001/D0010/D0150/D0301Z etc) + gas 806/814/826; inbound/outbound/by_flow/rejected, summary() with by_flow counts.


## Phases 119-126 (archived from CLAUDE.md 2026-06-27)

**Phase 119 COMPLETE (2026-06-26):** Licence condition monitoring -- 10 new tests (2,078 passing). company/regulatory/licence_monitor.py (new): LicenceMonitor.set_status()/get()/breaches()/under_monitor()/compliance_summary() (RAG: GREEN/AMBER/RED). _SLC_CATALOGUE: SLC 7/14/21C/22/27/27A/36/47/55.
**Phase 120 COMPLETE (2026-06-26):** Wholesale risk limits + position governor -- 11 new tests (2,089 passing). company/trading/risk_limits.py (new): RiskLimit + RiskGovernor; check() OK/WARNING(>80%)/BREACH(>=100%); check_all(), governance_summary() (overall RAG), new_position_allowed(). Four limits: open position/single contract/VaR/stop-loss.
**Phase 121 COMPLETE (2026-06-26):** Capacity Market obligation management -- 10 new tests (2,099 passing). company/regulatory/capacity_market.py (new): _CM_OBLIGATION_RATE_BY_YEAR 2016-2025 (£0.77-£75 crisis spike), compute_cm_obligation() (obligation_kw, charge, DELIVERED/PARTIAL/FAILED, penalty), cm_charge_per_mwh().
**Phase 122 COMPLETE (2026-06-26):** Network Use of System (UoS) charges -- 10 new tests (2,109 passing). company/market/network_charges.py (new): _DUOS_PENCE_PER_KWH 2016-2025 (resi/sme/ic), _TNUOS_PENCE_PER_KWH; network_cost_per_mwh() (DUoS+TNUoS p/kWh + GBP/MWh), annual_network_cost().
**Phase 123 COMPLETE (2026-06-27):** Customer Acquisition Cost (CAC) model -- 10 new tests (2,119 passing). company/crm/acquisition_cost.py (new): _CAC_BY_CHANNEL_YEAR 2016-2025 (pcw/direct/broker/referral/winback); get_cac(), cac_summary(), clv_vs_cac() (HEALTHY/MARGINAL/LOSS_MAKING, ratio>=3/>=1.5).
**Phase 124 COMPLETE (2026-06-27):** Churn waterfall + reason code analysis -- 10 new tests (2,129 passing). company/crm/churn_analytics.py (new): ChurnEvent (gain/loss, 8 reason codes, retention flags), ChurnWaterfall (opening/gains/losses/closing/churn_rate/growth_rate), ChurnAnalytics (reason_breakdown, retention_rate, summary).
**Phase 125 COMPLETE (2026-06-27):** Ofgem market benchmark data -- 9 new tests (2,138 passing). company/market/market_report.py (new): UK avg elec/gas unit rates + switching rates 2016-2025 (Ofgem domestic market report); market_benchmark(), compare_to_market() (BELOW/AT/ABOVE_MARKET ±3% threshold).
**Phase 126 COMPLETE (2026-06-27):** Imbalance price risk model -- 9 new tests (2,147 passing). company/market/imbalance.py (new): compute_imbalance() (short→SSP 18% premium/stress 120%; long→SBP 5% discount; balanced→zero), imbalance_summary() (cost/receipt counts + net). BSC imbalance mechanism modelled.


## Phases 127-134 (archived from CLAUDE.md 2026-06-27)

**Phase 127 COMPLETE (2026-06-27):** HH data quality checker -- 9 new tests (2,156 passing). company/market/hh_data_quality.py (new): HHRecord (actual/estimated/substituted), HHDataQualityChecker.check_record() (negative/zero/high/estimated flags), check_day() (48-period completeness + total_kwh + quality_ok).
**Phase 128 COMPLETE (2026-06-27):** Meter asset management -- 9 new tests (2,165 passing). company/billing/meter_assets.py (new): MeterAsset (SMETS1/SMETS2/TRAD/PPM/AMR, cert_due_date/cert_overdue/cert_due_soon), MeterAssetRegister (operational/faulty/cert_overdue/cert_due_soon/by_type/smart_pct).
**Phase 129 COMPLETE (2026-06-27):** Customer notification preferences -- 11 new tests (2,176 passing). company/crm/notification_prefs.py (new): CommPreference (channel/pref_type/source), NotificationPreferences: set/get/can_contact() (default service email allowed; marketing requires explicit opt-in), opted_out_marketing(), paper_bill_customers(), summary().
**Phase 130 COMPLETE (2026-06-27):** ECO4 obligation tracker -- 10 new tests (2,186 passing). company/regulatory/eco_tracker.py (new): EcoTracker (exempt/<150k; contribution/150-250k; direct/>250k), annual_obligation_twhd (rate×accounts), record_measure()/delivered_twhd()/shortfall/completion_pct/status (EXEMPT/ON_TRACK/AT_RISK/BREACH), measure_scores() catalogue.
**Phase 131 COMPLETE (2026-06-27):** Wholesale trade blotter -- 10 new tests (2,196 passing). company/trading/trade_blotter.py (new): TradeEntry (buy/sell, notional_gbp, is_remit_reportable), TradeBlotter (record/get/buys/sells, net_position_mwh, unreported_remit, mark_reported, counterparty_exposure).
**Phase 132 COMPLETE (2026-06-27):** Counterparty credit limits -- 9 new tests (2,205 passing). company/trading/credit_limits.py (new): CounterpartyLimit (rating/limit_gbp/category), CounterpartyCreditManager: check_trade() (GREEN<70%/AMBER<90%/RED≥90%/NO_LIMIT), update_exposure(), breached_limits(), summary().
**Phase 133 COMPLETE (2026-06-27):** DESNZ supplier data returns -- 9 new tests (2,214 passing). company/regulatory/desnz_returns.py (new): SupplierDataReturn (SDR monthly: customer counts by type, smart_meter_pct), FuelPovertyDeclaration (LILEE, fuel_poverty_rate_pct), CarbonIntensityReturn (CO₂ g/kWh lifecycle weighted), estimate_fuel_poor_customers().
**Phase 134 COMPLETE (2026-06-27):** Tariff change notification (TCN) -- 9 new tests (2,223 passing). company/billing/tariff_change_log.py (new): TariffChangeNotice (notice_days, required_notice 30/42d, is_compliant, rate_change_pct), TariffChangeLog (non_compliant, pending_effective, compliance_rate_pct).


## Phases 135-140 (archived from CLAUDE.md 2026-06-27)

**Phase 135 COMPLETE (2026-06-27):** Customer credit scoring -- 9 new tests (2,232 passing). company/crm/credit_scoring.py (new): assess_credit() (dd_active/missed_payments/arrears/bad_debt -> PRIME/STANDARD/SUBPRIME/HIGH_RISK), deposit_gbp (0/1/2x monthly), ppm_recommended for HIGH_RISK.
**Phase 136 COMPLETE (2026-06-27):** Renewal pricing engine -- 9 new tests (2,241 passing). company/billing/renewal_engine.py (new): generate_renewal_pack() builds fixed_1yr/fixed_2yr/variable_svt quotes (spot+margin+term_premium), RenewalPack.cheapest/recommended, segment-aware margin (RESI 2.5p/SME 3.0p/IC 1.8p).
**Phase 137 COMPLETE (2026-06-27):** Ofgem reporting obligations tracker -- 9 new tests (2,250 passing). company/regulatory/ofgem_obligations.py (new): 6 mandatory obligations (price_cap/billing_audit/complaint_report/annual_business/smart_meter/debt_difficulty); ObligationSubmission.is_on_time/days_late; on_time_rate_pct(), penalty accrual.
**Phase 138 COMPLETE (2026-06-27):** Forward curve anomaly detection -- 9 new tests (2,259 passing). company/market/curve_monitor.py (new): ForwardCurveMonitor (rolling z-score, window=30), AnomalyResult (normal/watch/alert/critical at 2.5/3.5/5.0sigma), screen_series(), summary().
**Phase 139 COMPLETE (2026-06-27):** REGO procurement and retirement -- 10 new tests (2,269 passing). company/market/rego_portfolio.py (new): RegoPurchase (5 tech types, cost_gbp), RegoPortfolio (buy/retire/available_mwh/coverage_check/by_technology), get_rego_price() 2016-2025 (2022 peak 6.50).
**Phase 140 COMPLETE (2026-06-27):** MOA charge management -- 9 new tests (2,278 passing). company/billing/moa_charges.py (new): _MOA_ANNUAL_GBP 2016-2025 (TRAD/PPM/SMETS1/SMETS2/AMR), get_moa_annual_charge() interpolated, calculate_moa_charges() per meter-point, moa_portfolio_cost().


## Phases 141-145 (archived from CLAUDE.md 2026-06-26)

**Phase 141 COMPLETE (2026-06-27):** Customer lifetime value (CLV) calculator -- 15 new tests (2,287 passing). company/crm/clv_calculator.py (new): compute_clv() DCF model (10% discount rate, tenure=1/churn_rate), clv_to_cac_ratio() (HEALTHY/MARGINAL/BREAK_EVEN/LOSS_MAKING), portfolio_clv_summary().
**Phase 142 COMPLETE (2026-06-26):** Green tariff product catalogue -- 20 new tests (2,307 passing). company/billing/tariff_products.py (new): TariffProduct (frozen dataclass: code/name/commodity/segment/term/is_green/rego_required_pct/premium/launch/withdrawal), TariffCatalogue (9 UK products 2016-2025: Standard/Green Fix 1yr/2yr, Variable SVT, SME Fixed/Green, IC Baseload/GreenCert). active_products(date), products_for_segment(), green_products(), get_by_code(), rego_requirement_mwh(). IC_GREEN_CERT withdrawn 2023-12-31.
**Phase 143 COMPLETE (2026-06-26):** Green tariff REGO compliance audit -- 13 new tests (2,320 passing). company/compliance/green_claims_audit.py (new): GreenClaimsAuditResult (year/obligation_mwh/rego_held_mwh/coverage_pct/status/shortfall_mwh/green_products_active/penalty_estimate_gbp), GreenClaimsAuditor. COMPLIANT >=100% / AT_RISK 90-99% / NON_COMPLIANT <90%. Penalty 50/MWh shortfall.
**Phase 144 COMPLETE (2026-06-26):** Gas daily balancing and nomination model -- 13 new tests (2,321 passing). company/market/gas_nominations.py (new): DailyNomination, GasNominationBook (nominate/imbalance_kwh/cash_out_cost_gbp/nomination_accuracy_pct/monthly_cashout_gbp/annual_cashout_gbp/worst_imbalance_periods/balancing_summary). Short position buys shortfall at NBP spot/therm; long gets 0.85x credit. 2022 crisis: 10x more expensive than 2016.
**Phase 145 COMPLETE (2026-06-26):** Prepayment meter (PPM) management -- 19 new tests (2,340 passing). company/billing/prepayment.py (new): PPMAccount (balance/debt/emergency_credit_limit/debt_recovery_rate/is_vulnerable), PPMBook (register/top_up/consume_daily/is_friendly_hours/is_self_disconnected/portfolio_summary). Debt recovery: 50% of top-up withheld (25% vulnerable). Emergency credit GBP5 standard (GBP10 vulnerable). Friendly hours 10pm-6am/weekends block disconnect.


## Phases 146-165 (archived from CLAUDE.md 2026-06-26)

**Phase 146 COMPLETE (2026-06-26):** Change of Tenancy (COT) management -- 13 new tests (2,353 passing). company/billing/cot.py (new): COTEvent (move_out/move_in/new_occupant_id), COTBook (record_move_out/record_move_in/void_properties/void_days/overdue_for_nomination/portfolio_summary/events_for). deemed_rate_gbp_per_kwh(): SVT+20% uplift capped at Ofgem domestic price cap (2022: 33.6p vs 28p SVT). 28-day void -> regulatory trigger to place on named SVT.
**Phase 147 COMPLETE (2026-06-26):** Guaranteed Standards of Performance (GSOPs) -- 12 new tests (2,365 passing). company/regulatory/gsop.py (new): GSOPType enum (5 types), GSOPPayment dataclass (trigger/due/paid dates, amount_gbp), GSOPBook (record_trigger/pay/overdue/total_liability_gbp/annual_report). _add_working_days() skips weekends. 30-second amounts per Ofgem GSOP regs. Auto-pay rate <100% = Ofgem breach risk.
**Phase 148 COMPLETE (2026-06-26):** Annual Direct Debit Review (ADDR) -- 12 new tests (2,377 passing). company/billing/dd_review.py (new): DDAction (INCREASE/DECREASE/MAINTAIN), DDReviewResult (frozen: customer_id/review_date/current_dd/actual_spend/recommended_monthly/variance_pct/action), review() (+-5% threshold), DDReviewBook (run_review/latest_review/overdue_for_review/summary). Ofgem SLC 27B.
**Phase 149 COMPLETE (2026-06-26):** Annual Energy Statement (AES) -- 12 new tests (2,389 passing). company/billing/annual_statement.py (new): AnnualStatement (frozen: consumption_kwh/total_cost_gbp/effective_unit_rate_ppm/sc_ppd/tariff_name/prev_year_consumption_kwh/consumption_change_pct/market_avg_cost_gbp/estimated_saving_gbp), AnnualStatementBook. Ofgem SLC 31B: every domestic customer must receive annual statement.
**Phase 150 COMPLETE (2026-06-26):** Priority Services Register (PSR) -- 12 new tests (2,401 passing). company/crm/priority_services.py (new): PSRNeed enum (10 types), PSREntry (needs/added_date/review_due_date/nominee), PSRBook (register/update_needs/is_registered/get/due_for_review/medically_dependent_customers/nominee_contacts/portfolio_summary). Annual review 365-day cycle. PSR = service ACCESS needs, not financial vulnerability.
**Phase 151 COMPLETE (2026-06-26):** Debt advice referral tracking -- 11 new tests (2,412 passing). company/billing/debt_referral.py (new): DebtAdviceOrg enum (StepChange/CAB/National Debtline/MAS), ReferralStatus, DebtReferral, DebtReferralBook (refer/update_status/outstanding_referrals/eligible_for_referral/annual_summary). Ofgem SLC 27A mandatory referral threshold GBP200.
**Phase 152 COMPLETE (2026-06-26):** Payment plan management -- 12 new tests (2,424 passing). company/billing/payment_plan.py (new): PaymentPlanStatus, PaymentPlan (original_debt_gbp/installment/expected_months/remaining_debt/is_complete; 2 missed = DEFAULTED), PaymentPlanBook. Bridges debt referral (Ph151) -> repayment -> PPM (Ph145).
**Phase 153 COMPLETE (2026-06-26):** Fixed-term contract exit fee -- 10 new tests (2,434 passing). company/billing/exit_fee.py (new): ExitFeeWaiveReason (WITHIN_NOTICE_PERIOD/CONTRACT_EXPIRED/SUPPLIER_BREACH/CUSTOMER_DEATH/PROPERTY_EMERGENCY), ExitFeeResult (days_remaining/fee_gbp/waived), calculate_exit_fee(). Auto-waived within 42-day notice period or after contract expiry.
**Phase 154 COMPLETE (2026-06-26):** Meter read dispute management -- 12 new tests (2,446 passing). company/billing/meter_dispute.py (new): DisputeType (ESTIMATED_READ/ACTUAL_TOO_HIGH/METER_FAULT/PRIOR_READING_ERROR), MeterDispute, MeterDisputeBook (open_dispute/update_status/resolve/outstanding_disputes/disputes_for_customer/annual_summary).
**Phase 155 COMPLETE (2026-06-26):** Customer complaint management and Ombudsman escalation -- 12 new tests (2,458 passing). company/crm/complaints.py (new): ComplaintCategory (8 types), ComplaintStatus (6 statuses), ComplaintBook. OMBUDSMAN_ESCALATION_DAYS=56 (Ofgem SLC 2.7: 8 weeks).
**Phase 156 COMPLETE (2026-06-26):** Tariff variation notice management -- 13 new tests (2,471 passing). company/billing/tariff_variation.py (new): VariationReason/VariationOutcome, TariffVariation (is_adequate_notice/has_no_exit_fee_window/rate_change_pct), TariffVariationBook. NOTICE_DAYS=30 per Ofgem SLC 23.1.
**Phase 157 COMPLETE (2026-06-26):** Microbusiness customer classification -- 12 new tests (2,483 passing). company/crm/microbusiness.py (new): MicrobusinessProfile (frozen), classify_customer(). Thresholds: elec <100 MWh, gas <293 MWh, staff <=10, turnover <=GBP2M. eligible_protections() returns 5 Ofgem SME protections.
**Phase 158 COMPLETE (2026-06-26):** Customer acquisition journey funnel -- 12 new tests (2,495 passing). company/crm/acquisition_journey.py (new): AcquisitionStage enum (8 stages), AcquisitionJourney (advance/converted/days_to_stage), AcquisitionFunnel (conversion_rate/drop_off_at/channel_summary). Terminal stages: CREDIT_DECLINED, ONBOARDED.
**Phase 159 COMPLETE (2026-06-26):** Economy 7 / off-peak tariff billing -- 11 new tests (2,506 passing). company/billing/economy7.py (new): e7_unit_rate_ppm() 2016-2025 day/night rates, E7MeterRead, E7Bill (day_charge/night_charge/blended_rate_ppm), generate_e7_bill(). 2022: day 34p (vs 12p 2016); night 19p (vs 6.5p).
**Phase 160 COMPLETE (2026-06-26):** Smart Export Guarantee (SEG) -- 12 new tests (2,518 passing). company/billing/smart_export.py (new): seg_rate_ppm() 2020-2025 (2022 peak 15p/kWh), SEGAccount/SEGBook. Zero-rate registration rejected (Ofgem SEG >= 1p min).
**Phase 161 COMPLETE (2026-06-26):** Property model -- 12 new tests (2,530 passing). company/crm/property_model.py (new): PropertyType/TenureType/EPCRating, Property frozen dataclass. consumption_multiplier (A=0.60x to G=1.75x). is_fuel_poor/eco4_eligible/psr_priority_property. Opens premises simulation theme.
**Phase 162 COMPLETE (2026-06-26):** Customer life events lifecycle -- 11 new tests (2,541 passing). company/crm/life_events.py (new): LifeEventType (11 events), LifeEvent (triggers_vulnerability_review/triggers_cot/triggers_psr_review), LifeEventLog. Links to COT/PSR/vulnerability workflows.
**Phase 163 COMPLETE (2026-06-26):** Household behaviour profile -- 11 new tests (2,552 passing). company/crm/household_profile.py (new): HouseholdType/HeatingSystem, HouseholdBehaviourProfile frozen (peak_load_factor/daytime_consumption_pct/tou_price_sensitivity/smart_meter_benefit_score/heat_pump_eligible).
**Phase 164 COMPLETE (2026-06-26):** Inbound contact and call centre model -- 9 new tests (2,561 passing). company/crm/contact_log.py (new): ContactChannel/ContactReason (12 reasons), ContactLog (avg_handle_minutes_for_reason/annual_summary). Bereavement 25 min, complaint 18 min, meter read 5 min.
**Phase 165 COMPLETE (2026-06-26):** Customer energy profile 360 view -- 10 new tests (2,571 passing). company/crm/energy_profile.py (new): CustomerEnergyProfile frozen composing Property (Ph161) + HouseholdBehaviourProfile (Ph163). tou_candidate/heat_pump_candidate/decarbonisation_priority_score. Closes premises/behaviour theme.


## Phases 166-198

**Phase 198 COMPLETE (2026-06-26):** Revolving credit facility model -- 7 new tests (2,860 passing). company/finance/credit_facility.py (new): DrawdownReason (WHOLESALE_SETTLEMENT/WORKING_CAPITAL/BSC_CREDIT_COVER/SEASONAL_CASHFLOW/EMERGENCY), CreditFacility (frozen: daily_commitment_fee_gbp), FacilityDrawdown (mutable: is_outstanding/interest_accrued_gbp), CreditFacilityBook (register_facility/drawdown raises if limit breached/repay/outstanding_balance/total_interest_accrued_gbp/utilisation_pct). 2022: 80% RCF utilisation = breach of banking covenant.
**Phase 197 COMPLETE (2026-06-26):** Energy efficiency programme (EEP) book -- 7 new tests (2,853 passing). company/crm/eep_book.py (new): EEPMeasure (8: CAVITY_WALL/SOLID_WALL/LOFT/HEAT_PUMP/SOLAR_PV/SMART_CONTROLS/DOUBLE_GLAZING/BOILER_UPGRADE), EEPScheme (ECO4/BUS/SEG/SELF_FUNDED), EEPInstallation (frozen: customer_cost_gbp=cost-subsidy/simple_payback_years), EEPBook (record/installs_for_customer/total_subsidy_gbp/estimated_savings_portfolio_gbp/annual_summary). BUS grant: £7,500 subsidy on £14k heat pump. Extends decarb_recommender.py (Ph168) with installed actuals.
**Phase 196 COMPLETE (2026-06-26):** Digital portal analytics -- 7 new tests (2,846 passing). company/crm/portal_analytics.py (new): PortalAction enum (11: LOGIN/VIEW_BILL/DOWNLOAD/SUBMIT_METER_READ/CHANGE_DD/UPDATE_CONTACT/VIEW_TARIFF/INITIATE_SWITCH/RAISE_COMPLAINT/VIEW_CONSUMPTION/ENROL_PAPERLESS), PortalEvent (frozen: is_self_serve for 4 self-service actions), PortalAnalytics (record/events_in_period/unique_users/self_serve_rate/action_counts/monthly_summary). Self-serve rate reduces call centre contact cost.
**Phase 195 COMPLETE (2026-06-26):** NPS cohort tracker -- 9 new tests (2,839 passing). company/crm/nps_tracker.py (new): classify_nps() (promoter>=9/passive 7-8/detractor<=6), NPSResponse (frozen: category/is_promoter/is_detractor), NPSTracker (record with 0-10 validation/nps_in_period/monthly_nps/by_segment/annual_summary with promoter_pct/detractor_pct). NPS = (promoters-detractors)/n*100. 2022 crisis: detractor_pct typically doubled from ~15% to ~30% industry-wide.
**Phase 194 COMPLETE (2026-06-26):** Customer renewals analytics book -- 8 new tests (2,830 passing). company/crm/renewals_book.py (new): RenewalOutcome (RENEWED/LAPSED/SWITCHED_AWAY/MOVED_OUT/DECEASED), OfferType (SAME_TARIFF/BETTER_TARIFF/PRICE_MATCH/LOYALTY_DISCOUNT/AUTO_ROLLOVER), RenewalRecord (frozen: accepted property), RenewalsBook (add/renewal_rate/lapse_rate/outbound_lift/by_offer_type/annual_summary). MOVED_OUT/DECEASED excluded from renewal_rate denominator. Outbound contact lift = outbound_rate - inbound_rate.
**Phase 193 COMPLETE (2026-06-26):** Demand-Side Response (DSR) programme book -- 7 new tests (2,822 passing). company/market/dsr_book.py (new): DSRStatus (ENROLLED/ACTIVE/SUSPENDED/WITHDRAWN), DispatchResult (DELIVERED>=95%/PARTIAL/NON_DELIVERY/CANCELLED), DSRParticipant (frozen: contracted_mw/payment_per_mwh_gbp), DispatchEvent (frozen: duration_hours/delivered_mwh/delivery_rate/payment_gbp), DSRBook (enroll/dispatch/events_for_customer/total_contracted_mw/total_payments_gbp/delivery_rate_year/annual_summary). I&C customers can earn £50-100/MWh dispatched.
**Phase 192 COMPLETE (2026-06-26):** Gas MPRN supply point register -- 9 new tests (2,815 passing). company/market/mprn_register.py (new): GasConsumptionBand (DOMESTIC <=73.2 MWh / SMALL_NON_DOMESTIC <=293 MWh / MEDIUM_NON_DOMESTIC <=732 MWh / LARGE), classify_gas_band(), MPRNStatus (REGISTERED/DEREGISTERED/PENDING_REGISTRATION/PENDING_SWITCH/DISCONNECTED/OBJECTED), MPRNRecord (frozen: consumption_band/is_active), MPRNRegister (register/initiate_switch/complete_switch/deregister/active_mprns/by_band/portfolio_summary with total_aq_kwh). Xoserve MPRN management (gas equivalent of MPAS).
**Phase 191 COMPLETE (2026-06-26):** Risk appetite framework -- 8 new tests (2,806 passing). company/risk/risk_appetite.py (new): RiskCategory (MARKET/CREDIT/LIQUIDITY/OPERATIONAL/REGULATORY), RiskRAG (WITHIN_APPETITE/APPROACHING_LIMIT/LIMIT_BREACH), RiskLimit (frozen: warning_value at 80% of limit), RiskMeasurement (frozen: utilisation_pct/rag/is_breach), RiskAppetiteFramework (add_limit/record_measurement/latest_measurement/active_breaches/risk_dashboard). 2022: bad_debt_pct 5% vs 3% limit -> LIMIT_BREACH; open_position 5,500 MWh vs 5,000 -> BREACH.
**Phase 190 COMPLETE (2026-06-26):** Ofgem annual supply data return -- 8 new tests (2,798 passing). company/regulatory/ofgem_supply_return.py (new): OfgemSupplyReturn (frozen: total_customers/complaints_per_100/is_submitted/whd_penetration_pct/summary()), OfgemReturnBook (file_return/get/missing_years/all_returns sorted by year). 2022 crisis: avg_debt_per_customer £180, bad_debt_written_off £900k, complaints_per_100=10 (3x Ofgem benchmark). Missing years signal compliance gap before Ofgem enforcement.
**Phase 189 COMPLETE (2026-06-26):** Contact centre performance metrics -- 9 new tests (2,790 passing). company/crm/contact_centre_metrics.py (new): AgentPerformancePeriod (frozen: calls_handled/fcr/escalations/complaints/csat; avg_handle_time_seconds/fcr_rate/escalation_rate/complaint_rate), ContactCentreMetrics (frozen: total_calls/answered_sla/abandoned/handle_time/agents; abandonment_rate/sla_answer_rate/avg_handle_time/calls_per_agent/summary()). 2022 crisis: call volumes 3x normal, abandonment_rate peaked at 25%, SLA answer rate dropped to 40%.
**Phase 188 COMPLETE (2026-06-26):** Supplier of Last Resort (SoLR) intake management -- 8 new tests (2,781 passing). company/crm/solr_intake.py (new): SoLRIntakeStatus (NOTIFIED/CONTACTED/ONBOARDED/SWITCHED_AWAY/UNRESPONSIVE), SoLRBatch (frozen: failed_supplier/appointment_date/customer_count/deemed_tariff_rate_pct_above_cap/is_priced_above_cap), SoLRCustomer (mutable: mark_contacted/onboarded/switched_away), SoLRBook (register_batch/add_customer/retention_rate/contact_rate/batch_summary). 2021: Bulb SAR -> SoLR-appointed suppliers received 1,700 stranded customers each.
**Phase 187 COMPLETE (2026-06-26):** CLV cohort analysis book -- 9 new tests (2,773 passing). company/crm/clv_cohort_book.py (new): CustomerCLVRecord (frozen: acquisition_year/channel/segment/clv/annual_margin/tenure), CohortSummary (frozen: avg/median/total CLV, avg_margin/tenure, profitable_pct, is_profitable_cohort), CLVCohortBook (add/by_acquisition_year/by_channel/by_segment/all_cohorts_by_year/best_cohort_by_year/worst_cohort_by_year/portfolio_summary). 2022 cohort: profitable_pct=0% when crisis-acquired customers churn immediately with negative CLV.
**Phase 186 COMPLETE (2026-06-26):** Supplier switching analytics -- 8 new tests (2,764 passing). company/crm/switch_analytics.py (new): SwitchDirection (GAIN/LOSS), SwitchStatus (INITIATED/COMPLETED/OBJECTED/CANCELLED/ERRONEOUS), SwitchEvent (frozen: days_to_complete/is_completed), SwitchAnalytics (record/complete/object/mark_erroneous/gains_in_year/losses_in_year/erroneous_transfers_in_year/avg_days_to_complete/net_customer_change/annual_summary). 2022 crisis: mass switching out on SVT price cap rises; high erroneous transfer rate.
**Phase 185 COMPLETE (2026-06-26):** MPAN supply point register -- 9 new tests (2,756 passing). company/market/mpan_register.py (new): MPANStatus (REGISTERED/DEREGISTERED/PENDING_REGISTRATION/PENDING_SWITCH/ENERGISED/DE_ENERGISED/OBJECTED), ProfileClass (PC1-PC8 with Ofgem descriptions), MPANRecord (frozen: is_active/profile_class_description), MPANRegister (register/initiate_switch/complete_switch changes supplier/object_to_switch/deregister/active_mpans/pending_switches/by_profile_class/portfolio_summary). Foundation for MPAS interactions.
**Phase 184 COMPLETE (2026-06-26):** Third-party intermediary (TPI/broker) book -- 9 new tests (2,747 passing). company/crm/tpi_book.py (new): TPITier (PREFERRED/STANDARD/PROBATION/SUSPENDED), TPICommissionBasis (FIXED_PER_CUSTOMER/PCT_OF_ANNUAL_REVENUE/PCT_OF_ANNUAL_CONSUMPTION), TPI (frozen), TPIDeal (frozen: commission_gbp derived from basis), TPIBook (register/suspend/record_deal raises if suspended/deals_for_tpi/total_commission_gbp/active_tpis/annual_summary). Suspension blocks new deals. 2022 context: some brokers mis-sold fixed-price contracts not honoured.
**Phase 183 COMPLETE (2026-06-26):** 13-week rolling cash flow forecast -- 9 new tests (2,738 passing). company/finance/cash_flow_forecast.py (new): WeeklyCashFlow (frozen: total_inflows/total_outflows/net_cash/is_net_positive), CashFlowForecast (frozen: closing_cash/minimum_weekly_balance/weeks_to_cash_concern/is_solvent_throughout/total_net_cash/summary()), build_cash_flow_forecast(). Other outflows support per-week spike payments (e.g. BSC credit cover drawdown). 2022 crisis: weekly wholesale £100k vs receipts £100k leaves opex/network uncovered from week 1 -> weeks_to_cash_concern=1.
**Phase 182 COMPLETE (2026-06-26):** Board KPI dashboard (RAG status) -- 9 new tests (2,729 passing). company/finance/board_kpis.py (new): KPIStatus (GREEN/AMBER/RED), KPIValue (frozen: vs_target_pct/status; lower_is_better flag; GREEN=within -5%, AMBER=-5 to -20%, RED<-20%), BoardKPIDashboard (frozen: green/amber/red_count/overall_status/get_kpi/summary()), build_board_dashboard(7 standard KPIs: customer_count/gross_margin/EBITDA/bad_debt/complaint_days/CSAT/GSOP_compliance). 2022 crisis: bad_debt_pct=5% on 1.5% target -> RED; cascades to overall_status=RED.
**Phase 181 COMPLETE (2026-06-26):** Company-level P&L income statement -- 9 new tests (2,720 passing). company/finance/company_pl.py (new): CompanyPL frozen dataclass (revenue/wholesale/policy/network/operating/marketing/bad_debt/whd_rebates/gsop_payments; gross_margin_gbp/gross_margin_pct/total_operating_cost_gbp/ebitda_gbp/ebitda_margin_pct/bad_debt_as_pct_revenue/is_profitable/summary()), build_company_pl(). WHD rebates and GSOP payments included in opex as regulatory obligations. New company/finance/ sub-package for company-layer financial models.
**Phase 180 COMPLETE (2026-06-26):** Sales and marketing budget tracker -- 8 new tests (2,711 passing). company/crm/marketing_budget.py (new): MarketingCategory enum (7: PCW_commission/digital_adv/telesales_commission/brand_adv/partner_commission/retention_outbound/referral_reward), MarketingSpend (frozen: cost_per_customer_gbp), AnnualMarketingBudget (frozen: total_spent/budget_utilisation_pct/blended_cac_gbp/total_customers_acquired/summary()), MarketingBudgetTracker (set_budget/record_spend/annual_budget/total_spend_all_years/cac_by_category). Brand advertising has zero customers_acquired (awareness); PCW has highest CPC. Complements channel_roi.py (Ph175).
**Phase 179 COMPLETE (2026-06-26):** Hedge performance tracker -- 8 new tests (2,703 passing). company/market/hedge_performance.py (new): HedgeOutcome (PROFITABLE/NEUTRAL/COSTLY; neutral=within 5% of spot), HedgeDelivery (frozen: pnl_gbp/price_differential/outcome/hedge_effectiveness_pct), HedgePerformanceBook (record_delivery/total_pnl_gbp/profitable_trades/costly_trades/avg_effectiveness_pct/annual_summary). 2022 crisis: forward hedge at £80/MWh vs £200 spot delivery = +£120k on 1,000 MWh -- exactly what saved hedged UK suppliers while unhedged ones went insolvent.
**Phase 178 COMPLETE (2026-06-26):** Customer portfolio load forecast -- 9 new tests (2,695 passing). company/market/load_forecast.py (new): SegmentLoadForecast (frozen: segment/commodity/account_count/annual_mwh/q1-q4_mwh/monthly_avg_mwh), PortfolioLoadForecast (frozen: total_elec/gas_mwh/quarterly_mwh/summary()), build_portfolio_forecast(resi/sme/ic/include_gas). Seasonal factors: elec Q1=1.18x/Q3=0.82x; gas Q1=1.55x/Q3=0.55x (3:1 winter:summer). Trading desk input for hedging decisions.
**Phase 177 COMPLETE (2026-06-26):** Customer portfolio energy position -- 9 new tests (2,686 passing). company/market/portfolio_position.py (new): CommodityType (ELECTRICITY/GAS), PositionDirection (LONG/SHORT/FLAT ±5% tolerance), EnergyPosition (frozen: hedge_ratio_pct/net_position_mwh/direction/is_within_policy), PortfolioEnergyPosition (elec+gas combined; is_fully_hedged/summary()), compute_energy_position(). Company-layer view of hedged-vs-forecast position; does not read simulation hedge internals.
**Phase 176 COMPLETE (2026-06-26):** Invoice / billing dispute resolution -- 8 new tests (2,677 passing). company/billing/billing_dispute.py (new): BillingDisputeType enum (7: wrong_tariff/incorrect_unit_rate/missing_discount/duplicate_invoice/dd_error/standing_charge/exit_fee), BillingDisputeStatus (OPEN/UNDER_REVIEW/RESOLVED_CREDIT/RESOLVED_NO_CHANGE/ESCALATED), BillingDispute (frozen: is_open/days_to_resolution), BillingDisputeBook (raise/update_status/resolve_with_credit/resolve_no_change/open_disputes/total_credits/annual_summary). Complementary to meter_dispute.py (Ph154): billing errors vs meter-read errors.
**Phase 175 COMPLETE (2026-06-26):** Acquisition channel ROI model -- 9 new tests (2,669 passing). company/crm/channel_roi.py (new): AcquisitionChannel enum (7 channels: PCW/direct_web/telesales/partner/smart_meter_install/referral/outbound_retention), _BASE_CAC_GBP (£12-£90) + _CHANNEL_CHURN_FACTOR (0.65-1.45x), ChannelROIResult (frozen: effective_churn/tenure/roi_ratio/is_profitable), compute_channel_roi() DCF-based, channel_roi_ranking() sorts all channels by roi_ratio. PCW has highest churn multiplier (1.45x); smart meter installs and referrals have lowest.
**Phase 174 COMPLETE (2026-06-26):** Arrears escalation workflow -- 9 new tests (2,660 passing). company/billing/arrears_book.py (new): ArrearsStage enum (10 stages: CURRENT->DD_FAILED->FIRST_NOTICE->SECOND_NOTICE->PLAN_OFFERED->PLAN_ACCEPTED->PLAN_DEFAULTED->REFERRED_TO_DEBT->WRITTEN_OFF / RESOLVED), ArrearsCase (outstanding_gbp/is_open/days_open; terminal stage guard), ArrearsBook (open_case/advance_stage/record_recovery/resolve/write_off/open_cases/total_arrears_outstanding/annual_summary). Vulnerable customer flag. Terminal stage guard prevents spurious transitions post-resolution.
**Phase 173 COMPLETE (2026-06-26):** Neighbourhood energy comparison (social proof) -- 10 new tests (2,651 passing). company/crm/neighbourhood_comparison.py (new): ConsumptionRating enum (MUCH_LOWER/LOWER/SIMILAR/HIGHER/MUCH_HIGHER at -20%/-5%/+10%/+30% vs median), NeighbourhoodComparison (frozen: vs_median_pct/vs_efficient_pct/consumption_rating/potential_saving_kwh/summary()), build_neighbourhood_comparison(sample -> median=n//2/efficient=n//5). Real UK suppliers (OVO, Octopus) send neighbour comparison reports to drive demand reduction behaviour.
**Phase 172 COMPLETE (2026-06-26):** Premises occupancy history register -- 9 new tests (2,641 passing). company/crm/occupancy_register.py (new): TenancyEndReason enum (MOVED_OUT/DECEASED/SWITCHED_SUPPLIER/EVICTED/VOID), OccupancyPeriod (mpan/customer_id/move_in/move_out/end_reason; is_current/duration_days), PremisesOccupancyRegister (record_move_in/record_move_out/current_occupant/occupancy_at_date/void_mpans/history_for_mpan/history_for_customer/portfolio_summary). Duplicate-occupancy guard. occupancy_at_date() resolves who was at a meter point on any historical date.
**Phase 171 COMPLETE (2026-06-26):** Customer conversation transcript model -- 9 new tests (2,632 passing). company/crm/conversation_log.py (new): ConversationOutcome enum (RESOLVED/ESCALATED/PENDING_CALLBACK/ABANDONED/TRANSFERRED), ConversationTurn (frozen: speaker/text/timestamp), CustomerConversation (add_turn/close/duration_seconds/is_open; CSAT 1-5 / NPS 0-10 validation), ConversationLog (start/get/conversations_for_customer/open_conversations/avg_csat/avg_nps/resolution_rate/annual_summary). Closes the human-conversation simulation gap raised by Rich.
**Phase 170 COMPLETE (2026-06-26):** Payment deferral/holiday scheme -- 9 new tests (2,623 passing). company/billing/payment_deferral.py (new): DeferralStatus (ACTIVE/COMPLETED/DEFAULTED/CANCELLED), DeferralReason (FINANCIAL_HARDSHIP/COVID_19/JOB_LOSS/ILLNESS/BEREAVEMENT/BENEFIT_DELAY), PaymentDeferral (deferred_amount/repayment_plan/outstanding_gbp/deferral_days/is_active), PaymentDeferralBook (create/record_repayment/mark_defaulted/cancel/active_deferrals/overdue_deferrals/total_deferred_outstanding_gbp/annual_summary). Auto-completes when repaid in full. Ofgem SLC 27A: suppliers must offer repayment plans to customers in difficulty.
**Phase 169 COMPLETE (2026-06-26):** Customer vulnerability register -- 11 new tests (2,614 passing). company/crm/vulnerability_register.py (new): VulnerabilityFlag enum (12 flags: fuel_poverty/serious_illness/elderly/disabled/mental_health/bereavement/job_loss/language_barrier/payment_difficulty/ppm_self_disconnected/child_dependent/medical_equipment), severity weights (medical_equipment=5, PPM=5, illness=4, mental=4 down to language=1), required_actions by flag (PSR/no_disconnect/debt_advice/ECO4/WHD etc), VulnerabilityRecord (frozen: severity_score, required_actions, psr_required, no_disconnect_required), VulnerabilityRegister (register/update_flags/remove/psr_customers/no_disconnect_customers/high_severity/annual_summary).
**Phase 168 COMPLETE (2026-06-26):** Decarbonisation recommendation engine -- 11 new tests (2,603 passing). company/crm/decarb_recommender.py (new): Measure enum (9 measures: cavity/solid-wall/loft insulation, heat_pump, solar_pv, smart_controls, double_glazing, LED, battery_storage), FundingScheme enum (ECO4/BUS/SEG/GHG/self_funded), MeasureRecommendation (frozen: savings/cost/funding/priority, simple_payback_years), DecarbonisationPlan (total_potential_savings_gbp, top_measure, summary()). recommend_measures(): EPC + property_type -> insulation; EPC D+ + gas boiler -> heat pump (BUS grant); no solar -> solar PV (SEG); always -> smart controls. ECO4 eligibles get zero-cost insulation.
**Phase 167 COMPLETE (2026-06-26):** Warm Home Discount (WHD) register -- 11 new tests (2,592 passing). company/billing/whd_register.py (new): WHDEligibilityReason (CORE_GROUP/BROADER_GROUP_LIHC/BROADER_GROUP_PSR/INDUSTRY_INITIATIVE), WHDStatus, WHDApplication (frozen: status property), WHDRegister (apply/mark_rebated/pending_rebates/total_rebated_gbp/applications_for_customer/annual_summary). Duplicate-year guard. WHD_REBATE_GBP=150.0 (Ofgem-mandated). Connects to fuel_poverty.py (Ph166): LIHC->broader group; PSR->broader group. Annual summary by eligibility reason feeds Ofgem WHD returns.
**Phase 166 COMPLETE (2026-06-26):** Fuel poverty income assessment -- 10 new tests (2,581 passing). company/crm/fuel_poverty.py (new): FuelPovertyBand (NOT_FUEL_POOR/BORDERLINE/FUEL_POOR/SEVERELY_FUEL_POOR at 0-8%/8-10%/10-20%/>20% income), LIHCStatus (NOT_LIHC/LIHC/LIHC_SEVERE per post-2012 Low Income High Cost definition), FuelPovertyAssessment (frozen: energy_spend_pct/fuel_poverty_band/lihc_status/is_fuel_poor/whd_eligible/eco4_priority), assess_fuel_poverty(). LIHC threshold: income <60% of median AND cost above median. UK median income GBP34,963 / cost GBP2,074.
