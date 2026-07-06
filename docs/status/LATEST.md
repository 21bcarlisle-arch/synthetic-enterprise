## Phase RK COMPLETE -- Customer 360 v4 item 2: real bill equation, fabrication debt closed
Last updated: 2026-07-06T14:10:18Z

**Status:** COMPLETE. 15,785 tests collected, fast suite (15,661) clean. Epistemic: PASS.

**Phase RK:** replaced a real fabrication debt Phase RJ surfaced -- tools/generate_invoice_data.py
used to synthesise invoice amounts from a hand-picked seasonal weight curve, unrelated to actual
consumption, even though site/state/billing_ledger.json already carried the real per-invoice
usage/rate/standing-charge breakdown from the sim's own bills. Rewritten to map real ledger data
through directly; process_run_complete.py reordered so the ledger generates before the invoice
step needs it. Billing tab is now click-to-expand per bill: the equation (usage x rate + standing
charge + non-commodity + VAT = total) and a why-different waterfall vs the previous bill and same
month last year (usage effect / price effect / other), verified against live data.

**Prior:** Phase RJ (2026-07-06) -- Customer 360 tabbed household IA + per-fuel MPAN/MPRN
separation. Phases RF-RI: Company/Regulatory tab dedup, Project tab elevation, concurrency fix,
Supplier IA regroup, Customer 360 v3 usage-chart rendering. Earlier: docs/claude/phase-history.md
and docs/PROJECT_OVERVIEW.md Section 4.

**Front of queue next:** CUSTOMER_360_REDESIGN.md v4 items 3 (event downstream effects on
Timeline) and 4 (reaction-loop rendering) per PRIORITIES.md P1a -- company/crm/ already has the
complaint/service-ticket/satisfaction infrastructure, needs joining into the portal JSON.


**Latest simulation results (2016–2025)** — auto-processed (509s / 8 min):
- Net margin: £1,535,307.74 | Gross: £6,467,308.57 | Capital: £51,433
- Treasury: £2,466,636 → £3,911,894 | 38 committee interventions | 1605 bills issued
- Enterprise value: £8,826,938.57 | Net after CTS: £6,360,822
- Retention: 14 offers, 14/14 retained | 6 no-offer churns | 6 total churned accounts