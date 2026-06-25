# Synthetic Enterprise — Destination Vision & Build Backlog

## The Destination

Synthetic Enterprise is not a simulation of an energy company.
It is an energy company that operates against a simulated market.

The distinction is fundamental. A simulation describes what a company
would do. An autonomous company actually does it — issues invoices,
opens trading positions, posts ledger entries, responds to customers,
submits to market systems. The outputs are real artefacts, not model
outputs.

When the company is ready to transact in the real market, the
transition is: swap the simulated market interfaces for real ones.
The company infrastructure does not change. Only the data source
changes.

This document defines what "company infrastructure" means, what
"simulated market interfaces" means, and the backlog to get there.

---

## The Two Systems

### The Market Simulator (SIM)

The SIM is a high-fidelity proxy of the UK energy market. It provides:

- **Wholesale price feed** — half-hourly spot prices, forward curve
  by tenor, bid-ask spread. Equivalent to N2EX/ICE real-time feed.
- **Settlement system** — Elexon-equivalent: accepts meter reads,
  runs imbalance settlement, issues settlement statements.
- **Weather and demand** — half-hourly demand forecasts and actuals
  by region, correlated with weather.
- **Customer behaviour engine** — simulates customer decisions:
  renewal, churn, home move, payment. The company cannot see inside
  this engine — it only sees outcomes (customer renewed, customer left,
  payment received).
- **Regulatory environment** — Ofgem price cap by quarter, levy rates
  by year, licence condition triggers.

The SIM exposes all of this through defined interfaces — APIs that
mirror real UK market systems as closely as practical. The company
connects to these interfaces. It never reads the SIM's internals.

**The real-world equivalents of each SIM interface:**

| SIM Interface | Real-World Equivalent |
|---|---|
| Wholesale price feed | N2EX, ICE, Trayport |
| Settlement system | Elexon BSC portal, ECOES |
| Weather/demand | National Grid ESO, Met Office |
| Customer behaviour | Real customers (portal, phone, email) |
| Regulatory environment | Ofgem, BEIS publications |

When the company is ready to go live, each SIM interface is replaced
by its real-world equivalent. The company code doesn't change.

### The Company

The company is an autonomous energy supplier. It has:

**Trading infrastructure**
- Forward book: positions opened at term signing, marked daily
- VaR engine: portfolio risk measured against stressed floor
- Hedging mandate: 85% minimum floor, active position managed
- Trading desk interface: positions, P&L, exposure by customer and tenor

**Financial infrastructure**
- Double-entry ledger: every financial event posted as DR/CR pairs
- Trial balance: reconciles daily
- P&L statement: emerges from ledger, not from formula
- Balance sheet: cash, receivables, forward book MTM, VAT liability
- Cash flow statement: operating, investing, financing
- Management accounts: monthly close, variance vs budget

**Customer infrastructure**
- Customer registry: every account with full history
- Contract management: terms, rates, start/end dates, renewal calendar
- Invoice engine: generates real invoice documents (PDF) per term
- Payment processing: records payments, ages debt, posts to ledger
- Bad debt management: provision, escalation, write-off
- Customer portal: customers log in, view bills, consumption, account

**Market infrastructure**
- Elexon interface: submits meter reads, receives settlement statements
- Reconciles settlement against own records
- Imbalance management: tracks unhedged exposure vs actual consumption
- Licence compliance: tracks obligations, files required reports

**Operations**
- CRM: customer interactions, cases, service history
- Complaints handling: intake, resolution, regulatory reporting
- Vulnerability management: identifies and flags at-risk customers
- Collections: payment plans, escalation, referral

---

## The Backlog

Ordered by dependency. Each item is a genuine capability gap — the
company cannot do this today.

### Foundation (do first — everything else depends on these)

**F1 — Double-entry ledger**
Every financial event posted as proper DR/CR pairs with account codes.
Trial balance reconciles. P&L and balance sheet emerge from it.
Currently: margin tracker with event log. Not a real ledger.

**F2 — Ofgem price cap model**
Quarterly price cap applied to domestic tariffs 2019-present.
Currently: no cap, domestic margins 12% vs real 1-4%. Phase 47a
addresses this — ensure it covers the full cap history 2019-2025.

**F3 — Full SIM/company operational independence**
Company runs end-to-end on its own models with no shared code paths
to SIM internals. Currently: shared code paths remain.
Test: can the company module be imported and run without importing
anything from sim/ or simulation/?

**F4 — Market interface definitions**
Formal API definitions for every SIM→company data feed. Versioned,
typed, documented. Currently: function calls, not interfaces.
These become the swap points when going live.

### Customer Infrastructure

**C1 — Real invoice documents**
PDF invoices per customer per term. Line items: consumption, unit
rate, standing charge, non-commodity pass-through (itemised by levy),
VAT. Invoice number, issue date, due date, payment status.
Currently: bill records in database, no document.

**C2 — Customer portal (MVP)**
Web interface at customers.poesys.net (or similar subdomain).
Log in as any customer. See: current tariff, recent bills (PDF),
consumption chart, payment history, account status.
Rich should be able to log in as C1 and experience what C1 sees.
Currently: nothing.

**C3 — Payment processing**
Record payments against invoices. Age debt. Trigger bad debt
provision at 90 days. Post to ledger. Currently: payment events
exist in ledger but not linked to specific invoices.

**C4 — CRM and interaction log**
Every customer interaction recorded: contact reason, channel,
outcome, agent (AI or human). Complaint flag. Vulnerability flag.
Currently: event log for lifecycle events only, no service history.

### Trading Infrastructure

**T1 — Trading desk interface**
View on poesys.net showing: open positions by customer and tenor,
portfolio P&L, VaR current vs stressed, mandate compliance.
Updates after every settlement run. Currently: trading book exists
but only visible in annual report.

**T2 — Position management**
Open, amend, close forward positions. Track against mandate.
Audit trail. Currently: positions created at term signing only,
no amendment capability.

**T3 — Real-time mark-to-market**
Forward positions marked daily against current forward curve.
MTM P&L posted to ledger. Currently: settled at term end only.

### Financial Infrastructure

**FI1 — Management accounts**
Monthly P&L, balance sheet, cash flow — formatted as a real
management pack. Revenue recognition, accruals, provisions.
Currently: annual report with margin figures. Not accounts.

**FI2 — Budget vs actual**
Annual budget set at start of year. Monthly variance reported.
Drives management decisions. Currently: no budget model.

**FI3 — Treasury management**
Cash forecasting, working capital management, credit facility
headroom. Currently: treasury is a running balance, not managed.

### Market Infrastructure

**M1 — Elexon settlement interface**
Company submits meter reads, receives settlement statements,
reconciles against own records. Imbalance flagged and managed.
Currently: settlement runs inside the SIM, company reads results.

**M2 — Regulatory reporting**
Licence condition compliance tracking. CSS filing (annual).
Currently: nothing.

**M3 — Market data feed**
Company receives forward prices through a defined feed interface,
not by calling SIM functions. This is the swap point for live data.
Currently: SIM functions called directly.

### The Customer Portal (detailed)

This deserves its own section because it's the most important
single thing for demonstrating the company is real.

**Portal MVP (phase 1):**
- URL: customers.poesys.net
- Login: account number + postcode (simulated auth)
- Dashboard: current tariff, next bill date, last payment
- Bills: list of all invoices, download as PDF
- Consumption: half-hourly chart for HH customers, monthly for others
- Contact: raise a query (goes to CRM)

**Portal phase 2:**
- Tariff comparison: what would I pay on other available tariffs?
- Switch tariff: request a tariff change at next renewal
- Direct debit: set up / amend payment method
- Smart meter: view real-time consumption (for HH customers)

**Why this matters:**
When Rich logs in as C7 (HH smart meter customer) and sees their
half-hourly consumption chart with peak/off-peak pricing overlaid,
the simulation stops being abstract. The customer experience is
real. That's the test.

---

## The Transition Test

The simulation is ready to consider real-world deployment when:

1. The company module runs independently — no SIM imports
2. Every market interface has a real-world equivalent defined
3. A customer can log into the portal and understand their account
4. The trading desk can see its positions and P&L in real time
5. Management accounts close monthly and reconcile
6. The epistemic verifier passes on every phase

When all five are true, replacing SIM interfaces with real ones
is an integration task, not a rebuild.

---

## Instructions for the Agent

This document is the destination. Every phase proposal should be
evaluated against it.

Before proposing a new phase, ask:
1. Does this close a gap in the company infrastructure above?
2. Does this make a SIM interface more like its real-world equivalent?
3. Does this move the company closer to operational independence?

If the answer to all three is no, the phase adds simulation depth
but not company reality. That may still be justified — calibration
matters — but it should be a conscious choice, not a default.

The backlog items above (F1-F4, C1-C4, T1-T3, FI1-FI3, M1-M3)
are the priority work. Simulation depth phases (forward curve
calibration, price cap model, segment expansion) are also important
but secondary to building the company infrastructure.

When proposing phases, propose from this backlog first. If a
simulation depth phase is more urgent, explain why before proposing it.

**The customer portal (C2) is the single highest-priority item
not yet started.** Build it as soon as the invoice engine (C1)
exists. These two together make the company real in a way that
no amount of simulation sophistication can.
