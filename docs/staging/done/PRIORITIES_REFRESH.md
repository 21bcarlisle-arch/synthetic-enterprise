[PROJECT] PRIORITIES.md refresh -- queue the big things, in this order

The current work stream (churn model fine-tuning at n=6) is real but is polish on roadmap stage 3 while bigger items sit unqueued. Refresh PRIORITIES.md so the default queue serves these, in order:

PRIORITY 1 -- OBSERVABILITY COMPLETION (finish permanent_observability -- this is trust infrastructure, everything else depends on it):
(a) Fix PROJECT_STATE.txt auto-sync -- dead since Jun 30, still showing Phase HY / 9,290 tests. Must regenerate on every push.
(b) customer_sample.json at a stable fetchable URL, listed in PROJECT_STATE.txt Key Files section.
(c) Shadow HTML site: plain no-JS HTML mirror of ALL FOUR site sections (Supplier / Customers / Project / SIM) showing the same underlying data as the live SPAs. The strategy advisor cannot execute JavaScript -- this is the only way the website is visible to it. Ugly is fine; complete and current is mandatory. Publish under a stable path (e.g. poesys.net/shadow/) and list it in PROJECT_STATE.txt.
NON-NEGOTIABLE ACCEPTANCE: the strategy advisor can fetch and verify every section of the website without JS, without copy-paste, and the artifacts regenerate automatically on every run/push. Rule 2 applies: done means the advisor has confirmed a successful fetch, not a statement.

PRIORITY 2 -- BILLING & PAYMENT INFRASTRUCTURE (roadmap stage 4):
Real per-customer invoices with payment due dates, payment methods (DD / cash / prepay), actual payment events posting to the ledger, arrears states emerging from missed payments. Money moves per customer per month. Bad debt (stage 5) then emerges from this naturally -- do not build bad debt separately first.

PRIORITY 3 -- POPULATION ANCHORING (standing constraint, applies from now on, not a one-off phase):
SIM aggregate behaviour must match published UK statistics: Ofgem annual switching rates by year (including the crisis-period switching collapse), complaints/ombudsman volumes, arrears rates. Individual variation is free; aggregates are anchored. The NQ redirect churn realism check is the first application. Add an anchoring section to the annual report showing SIM aggregate vs published benchmark with RAG flags.

PRIORITY 4 -- SHADOW LIVE OPERATION (design after Priority 2 lands):
Paper-trading mode against current real market data: daily decisions logged and timestamped, zero capital at risk. Converts the sim from retrodiction to falsifiable live prediction. Design proposal first via drafts/ -- this is a one-way-door architecture decision, Rich reviews before build.

Update PRIORITIES.md now, confirm via NTFY with the new Now/Next queue. Per harness Rule 1, this refresh outbids any self-generated default work.
