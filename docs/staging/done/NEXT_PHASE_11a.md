# Phase 11a: Company Pricing Autonomy — Close the SIM/Company Functional Gap

## What this phase closes

**Hollow gap 3**: "SIM/company barrier is structural, not functional."

Currently the company's tariffs are derived directly from the SIM's internal
forward curve (`sim/forward_curve.py`). A real energy supplier never sees its
forward curve's internal parameters — it sees published spot prices, broker
indices, and its own historical purchase data, then builds its own estimate.

After this phase: the company sets tariffs from its own observable-data forward
price model. The SIM runs against those tariffs. The difference between the
company's estimate and the SIM's ground truth is **basis risk** — visible in
the P&L for the first time.

## Epistemic contract

The company is allowed to observe:
- Historical spot electricity prices (already in `sim/system_prices_history.py`)
- Historical gas prices (already in `sim/gas_prices_history.py`)
- Its own past bills and wholesale settlement costs (from ledger events)

The company is NOT allowed to see:
- `sim/forward_curve.py` internals
- The SIM's volatility parameters or seasonal multipliers
- The weather engine's forward demand forecasts

## Deliverables

### 1. `company/pricing/tariff_engine.py`

Observable-data forward price estimator. Algorithm:
- For each contract term start, look back at the last 4 quarters of spot
  prices (observable market data the company could access)
- Compute rolling mean + standard deviation of recent spot prices
- Apply a company risk premium (a fixed markup, e.g. 15% above rolling mean)
- Return the company's forward price estimate

This will systematically differ from `sim/forward_curve.py` — sometimes
higher (company over-estimates → too expensive → profitable per unit),
sometimes lower (company under-estimates → margin squeeze). The 2021-2022
crisis should show the company's estimate lagging badly as prices spike —
the same failure mode that killed real suppliers.

### 2. `company/interfaces/sim_interface.py` — `LiveSimInterface`

Implement the live class:
- `get_forward_price(fuel, delivery_date)` → calls `company/pricing/tariff_engine.py`
  (reads spot history, NOT forward_curve.py internals)
- `get_settlement_data(mpan, period)` → reads from ledger events
- `get_customer_status(account_id)` → reads from CRM registry
- `notify_churn()` / `notify_acquisition()` → updates CRM registry

`build_sim_interface(live=True)` now works.

### 3. `simulation/run_phase2b.py` modification

At each contract pricing step, instead of:
```python
fwd = generate_forward_price(term_start, elec_records, ...)
unit_rate = price_fixed_tariff(fwd, ...)
```

Use:
```python
iface = build_sim_interface(live=True)
company_fwd = iface.get_forward_price('electricity', term_start)
unit_rate = price_fixed_tariff(company_fwd, ...)
# store both: company_fwd (what company used) and sim_true_fwd (ground truth)
```

The `sim_true_fwd` is still computed (for P&L reconciliation and risk
committee analysis) but the company's tariff is what actually gets charged.

### 4. Basis risk reporting

New JSON output fields:
- `company_fwd_gbp_per_mwh` and `sim_fwd_gbp_per_mwh` per contract term
- `tariff_error_pct` = (company_fwd - sim_fwd) / sim_fwd per term

New annual report section: "Tariff Basis Risk" — table by year showing
company forecast error, direction (over/under), and margin impact in £.

## Test scope

- `tests/test_company_tariff_engine.py` — unit tests for the observable
  forward price model (output is plausible, differs from sim ground truth)
- `tests/test_live_sim_interface.py` — LiveSimInterface integration
- Existing financial figures will shift slightly (company tariffs ≠ SIM
  ground truth tariffs); update assertions accordingly

## What this unlocks

- The company now makes a consequential decision (tariff pricing) using only
  information it's allowed to see
- The simulation shows the financial consequences of imperfect company
  forecasting — the same mechanism that caused real supplier failures in 2021-22
- Foundation for company's own churn model (Phase 11b) — same pattern: company
  estimates from observables, results differ from SIM ground truth

## Commit message

"Phase 11a: company pricing autonomy — close SIM/company functional gap"
