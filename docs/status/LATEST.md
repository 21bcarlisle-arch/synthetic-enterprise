## Phase RJ COMPLETE -- Customer 360 tabbed household IA + per-fuel MPAN/MPRN separation
Last updated: 2026-07-06T09:33:23Z

**Status:** COMPLETE. 15,791 tests collected, fast suite (15,667) clean. Epistemic: PASS.

**Phase RJ (recovered an interrupted prior-session's uncommitted work):** site/customers/index.html
rebuilt from a single-account view into a 6-tab household IA (Overview/Accounts/Consumption/
Billing/Timeline/Risk) with per-fuel selectors on every tab that carries one -- closes
CUSTOMER_360_REDESIGN.md v4's "gas/elec separated at every stage" ask. Accounts tab gains real
MPAN (Elexon modulus-11 check digit) + MPRN per fuel; Timeline tab assembles real renewal/churn +
life events, merged and sorted. KEY FINDING while surveying remaining v4 scope: billing_ledger.json
already has real per-invoice usage/rate/standing-charge data from actual sim bills, but the
customer-facing JSON's own invoices are still a fabricated seasonal-weight approximation --
flagged as the next fix (closes both the bill-equation item and a real fabrication debt).

**Prior:** Phases RF-RI (2026-07-05/06) -- Company/Regulatory tab dedup, Project tab Timeline/
Capabilities/System elevation, concurrency race fix, Supplier IA regroup (grouped nav + Query
FAB), Customer 360 v3 usage-chart rendering. Phases QR-QE and earlier: docs/claude/phase-history.md
and docs/PROJECT_OVERVIEW.md Section 4.

**Front of queue next:** CUSTOMER_360_REDESIGN.md v4 items 2 (bill equation + why-different
waterfall, wiring real billing_ledger.json data into the customer JSON), 3 (event downstream
effects), 4 (reaction-loop rendering) -- per PRIORITIES.md P1a.


**Latest simulation results (2016–2025)** — auto-processed (491s / 8 min):
- Net margin: £1,535,307.74 | Gross: £6,467,308.57 | Capital: £51,433
- Treasury: £2,466,636 → £3,911,894 | 38 committee interventions | 1605 bills issued
- Enterprise value: £8,826,938.57 | Net after CTS: £6,360,822
- Retention: 14 offers, 14/14 retained | 6 no-offer churns | 6 total churned accounts