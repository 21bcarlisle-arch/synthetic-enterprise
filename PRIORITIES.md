# PRIORITIES.md — Synthetic Enterprise
# Last refreshed: 2026-07-03 per advisor PRIORITIES_REFRESH staging file

## PRIORITY 1 — OBSERVABILITY COMPLETION (non-negotiable trust infrastructure)

### 1a. Fix PROJECT_STATE.txt auto-sync (dead since Jun 30)
PROJECT_STATE.txt at poesys.net/state/PROJECT_STATE.txt still shows Phase HY / 9,290 tests.
Must regenerate on every push. Root cause: auto-sync hook not firing since Jun 30.
Acceptance: advisor fetches and confirms current state without copy-paste.

### 1b. Stable fetchable URL for customer_sample.json
customer_sample.json must be at a stable URL listed in PROJECT_STATE.txt Key Files section.

### 1c. Shadow HTML site (all 4 sections, no JS required)
Plain HTML mirror of Supplier / Customers / Project / SIM sections at poesys.net/shadow/.
Strategy advisor cannot execute JavaScript -- shadow site is the only way website is visible.
Ugly is fine; complete and current is mandatory. Listed in PROJECT_STATE.txt.
NON-NEGOTIABLE: advisor can fetch and verify every section without JS or copy-paste.
Artifacts regenerate automatically on every run/push.

## PRIORITY 2 — BILLING & PAYMENT INFRASTRUCTURE (roadmap stage 4)

Real per-customer invoices with payment due dates, payment methods (DD / cash / prepay),
actual payment events posting to the ledger, arrears states from missed payments.
Money moves per customer per month. Bad debt (stage 5) emerges from this naturally.
Do NOT build bad debt separately first.

## PRIORITY 3 — POPULATION ANCHORING (standing constraint, applies from now on)

SIM aggregate behaviour must match published UK statistics:
- Annual switching rates by year including crisis-period collapse
- Complaints/ombudsman volumes
- Arrears rates
Individual variation is free; aggregates are anchored.
Add anchoring section to annual report: SIM aggregate vs. published benchmark with RAG flags.
Phase NS addressed switching rate anchoring. This generalises the approach.

## PRIORITY 4 — SHADOW LIVE OPERATION (design after Priority 2 lands)

Paper-trading mode against current real market data: daily decisions logged and timestamped,
zero capital at risk. Converts sim from retrodiction to falsifiable live prediction.
Design proposal first via drafts/ -- one-way-door architecture decision, Rich reviews.

---
## Backlog (not queued)

- **NT**: SVT Positioning Intelligence -- company uses Ofgem public SVT rates to compute
  rate-vs-SVT differential as observable churn signal.
- **NU**: Crisis Tariff Strategy -- no fixed deals when cap below wholesale cost (2022 scenario).
- **NV**: Gas Market Churn Alignment -- independent gas churn propensity model.
