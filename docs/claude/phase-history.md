# Phase History — Phases 30a–42

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
