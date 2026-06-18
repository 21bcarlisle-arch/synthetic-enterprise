# Company Layer Foundation (Parallel Workstream)

## Context

The simulation is maturing but some rules are still changing — tariff
structure, ToU pricing, forward curves. Building the full company layer
now risks rework. However some pieces are stable enough to build
immediately because they don't depend on rules that are still in flux.

This is a parallel workstream to Phase 8a. It can be built concurrently
by a specialist agent or in between simulation runs when the GPU is busy.

## What this is

The beginning of a real company layer — not simulation objects, but
persistent company artefacts that will eventually be driven by real
customer and market interactions. The simulation is the environment. The
company operates against it.

The goal is not to replicate what the simulation already does. It is to
build the foundation that a real autonomous energy supplier would need —
starting with the pieces that are stable regardless of how the SIM rules
evolve.

## What to build

### 1 — Customer Registry (CRM foundation)

A persistent customer record store, separate from the simulation's
in-memory customer objects.

`company/crm/customer_registry.py`

Each customer record contains:
- Account ID (maps to simulation customer ID)
- Customer type: residential / SME
- Fuel type: electricity / gas / dual
- Supply start date
- Current status: active / churned / pending
- Tariff type: fixed / variable (ToU field reserved for later)
- Contact details: name, address, email (synthetic but structured)
- Meter point references: MPAN (electricity), MPRN (gas)
- Smart meter flag: True for C7/C8/C9

This is a SQLite database, not an in-memory dict. Records persist between
runs. The simulation updates status (churn, acquisition) by writing to
this registry, not just changing internal state.

Seed it with the current customer book (C1-C9 plus C2_2).

### 2 — Billing Artefact Engine

Bills currently exist as calculations. Make them documents.

`company/billing/invoice.py`

Each invoice is a structured record with:
- Invoice number (sequential, persistent across runs)
- Account ID
- Billing period: start date, end date
- Line items: consumption (kWh), unit rate (p/kWh), standing charge
- Subtotal, VAT (20%), total due
- Due date (14 days from issue)
- Payment status: unpaid / paid / partially paid / bad debt
- Issue date

Store invoices in SQLite: `company/billing/invoices.db`

The simulation's existing bill calculation feeds into this — the invoice
engine wraps the calculation in a real artefact. Every bill the simulation
issues becomes a retrievable invoice record.

### 3 — Company P&L from Ledger

The ledger (Phase 7b) already exists. Build a P&L view that reads from
it as a company would — not as a simulation output but as an accounting
statement.

`company/finance/pnl.py`

Produce a simple income statement from ledger events:
- Revenue: sum of payment_received events
- Bad debt: sum of bad_debt events  
- Wholesale cost: sum of settlement events
- Gross margin: revenue minus wholesale
- Operating costs: acquisition spend + fixed costs + cost to serve
- Net margin: gross minus operating costs

This should agree with the simulation's own P&L figures. If it doesn't,
that's a bug worth finding.

### 4 — Company/SIM Interface Seam

Define the formal boundary between the SIM and the company layer.

`company/interfaces/sim_interface.py`

The company layer should only access simulation data through this seam.
It cannot read simulation internals directly. The interface exposes:
- `get_settlement_data(mpan, period)` — what did this meter consume?
- `get_forward_price(fuel, delivery_date)` — what is the forward price?
- `get_customer_status(account_id)` — is this customer still on supply?
- `notify_churn(account_id, date)` — customer has left
- `notify_acquisition(account_id, date)` — new customer activated

This seam doesn't need to be fully functional yet — define the interface
and stub the implementations. The point is to establish the boundary so
future company-layer work always goes through it.

## What NOT to build yet

- Customer portal (depends on tariff structure settling — ToU coming)
- Market submission interfaces (depends on SIM/company separation design)
- Payment processing (Phase 7b handles this for now)
- Direct debit / payment method selection (depends on billing artefacts
  being stable first)

## Fidelity delta

After this workstream the company has a persistent identity separate from
the simulation. Customers exist as records. Bills exist as documents.
The P&L is an accounting statement, not a model output. The seam between
SIM and company is defined even if not yet enforced.

## Constraints

- Use SQLite for persistence — simple, no infrastructure, queryable
- Company layer lives under `company/` — entirely separate from
  `simulation/` and `saas/`
- No simulation internals accessed directly — only through the interface
  seam
- Delegate all implementation to local Qwen
- This workstream does not require a full simulation re-run — it can be
  built and tested against existing run output JSON

## Tests

At minimum:
- Customer registry: seed, query, update status
- Invoice engine: generate invoice from bill data, retrieve by account
- P&L: agrees with simulation net margin from existing run output
- Seam: all interface methods callable, stubs return sensible defaults

## NTFY

On completion:
1. "Company layer foundation complete."
2. "Customer registry: [n] accounts seeded."
3. "Invoice engine: [n] invoices generated from existing run."
4. "Company P&L agrees with simulation: [yes/no — and if no, the gap]"
5. "SIM/company seam defined at company/interfaces/sim_interface.py"
