# Proposed Phase 9b — Functional SIM/Company Separation

## Context

Phase 9a built the company layer skeleton: SQLite CRM, invoice engine, P&L
module, and a formal `SimInterface` seam in `company/interfaces/sim_interface.py`.
The seam exists but it's all stubs — `invoice.py` and `pnl.py` still receive
simulation internals (bill dicts, ledger events) directly. The company layer
has no operational independence.

This closes hollow gap #3: *"SIM/company barrier is architectural, not
functional. The seam exists in code structure but the company layer has no
operational independence. It doesn't make decisions based only on what it's
allowed to see."*

## What "functional" means in practice

The test is simple: after a full run, the company layer should be able to
produce its P&L and CRM state using **only** data accessed through
`SimInterface` — with no direct imports of simulation modules
(`saas/billing.py`, `saas/ledger.py`, `simulation/run_phase2b.py`, etc.).
The company acts as if the simulation is a black box it can query.

## Proposed scope

### 1. `LiveSimInterface` — real data through the formal seam

Implement `LiveSimInterface(SimInterface)` in
`company/interfaces/sim_interface.py`. It reads from
`docs/reports/run_output_latest.json` (already written after every full run
by `sim_runner.py`) and fulfils all four interface methods with real data:

- `get_settlement_data(mpan, period)` — look up the customer's settlement
  records for the period from the JSON (indexed by `customer_id` / billing
  period)
- `get_forward_price(fuel, delivery_date)` — return the forward curve price
  for that date from the run's `forward_curve` section
- `get_customer_status(account_id)` — derive from the run's lifecycle events:
  if the customer has a `churned` event before today's date, return `'churned'`;
  otherwise `'active'`
- `notify_churn` / `notify_acquisition` — write events to the CRM
  (`company/crm/customer_registry.py`) so the registry stays in sync

`build_sim_interface(live=True)` returns `LiveSimInterface` instead of
raising `NotImplementedError`.

### 2. Lifecycle event wiring

At the end of `simulation/run_phase2b.py` (or in
`simulation/run_phase4c_on_phase2b.py`), after the run completes, iterate
the lifecycle events and call `SimInterface.notify_churn()` /
`notify_acquisition()` for each. This is a post-run sync, not real-time —
the simulation still runs first, the company layer updates from the output.

This is the minimum viable version of functional separation: the company
learns about events through the interface, not by reading simulation globals.

### 3. Post-run reconciliation script

New `company/run_reconciliation.py`:

1. Load `LiveSimInterface` (reads `run_output_latest.json`)
2. Sync CRM: call `notify_churn` / `notify_acquisition` for all lifecycle events
3. Generate invoices: for each billing period × customer, call
   `SimInterface.get_settlement_data()` and feed the result to `invoice.py`
4. Build company P&L from those invoices via `pnl.py`
5. Reconcile: `reconcile_with_sim(company_pnl, sim_net_margin)` — expect
   agreement within £0.01
6. Print/write a reconciliation report

This script is the proof of functional separation: it produces the right
answer using only the interface, not simulation imports.

### 4. Annual report section

New `_company_reconciliation_section()` in `saas/reporting/annual_report.py`:

- CRM summary: how many customers active vs churned at run end
- Company P&L vs simulation P&L — agree/disagree flag
- Invoice count, total billed, payment status breakdown

Replaces the placeholder "Company Layer: not yet integrated" in the report.

### 5. Tests

- `LiveSimInterface` returns real data for a known customer/period from a
  fixture JSON
- `notify_churn` updates CRM status (existing `StubSimInterface` test pattern)
- `run_reconciliation` script produces P&L that agrees with simulation to
  within £0.01 (integration test using `run_output_latest.json` if present,
  else skip with `pytest.mark.skipif`)
- Reconciliation section renders correctly in annual report fixture tests

## Out of scope

- Real-time event streaming (simulation notifying company *during* a run,
  not just after)
- Company-layer decisions feeding back into the simulation (e.g. company
  decides to acquire a customer, simulation creates them)
- Any UI or API for the company layer

Both of those are the *next* level of separation — Phase 9c territory.

## Gate

Per CLAUDE.md opt-out REVIEW_GATE pattern: proceeding in 4 hours unless
Rich redirects via staging or NTFY.
