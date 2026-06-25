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
