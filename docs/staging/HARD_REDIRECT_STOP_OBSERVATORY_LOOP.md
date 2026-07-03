[PROJECT] Hard redirect -- stop the Observatory loop, build the three hard things

DIAGNOSIS (not a question -- this is what happened):
After the coverage-sprint loop was broken, the build found a NEW default loop: "board Observatory sections." Phases OD through OL are twelve consecutive board-report Observatories (Renewable Obligation, CCL, FiT, WHD, ECO, Carbon, etc). Before that, PRIORITIES_REFRESH's four items (P1 observability, P2 billing, P3 anchoring, P4 shadow ops) were each built as a SINGLE board-report section (NT/NU/NV/NW) -- the label was honoured, the substance was not. Adding a board section is now the same low-value reflex the coverage sprint was. This is drift, and it stops now.

THE RULE THAT ENDS THIS CLASS OF LOOP:
A new board/report/Observatory section is NOT a phase. It never counts as the primary work of a phase again. Reporting is a byproduct of building capability, not the capability. If the next proposed phase is "add an X Observatory / X report section / X dashboard," it is automatically outbid by the three priorities below. This joins the phase-close checklist permanently.

BUILD THESE THREE, IN ORDER. Each is multi-phase. Do NOT reduce any to a single reporting section.

PRIORITY 1 -- OBSERVABILITY THE ADVISOR CAN ACTUALLY USE (finish it properly):
Acceptance is a live fetch by the advisor, not a phase entry claiming done.
(a) PROJECT_STATE.txt auto-sync is BROKEN -- still shows Phase HY / 9,290 tests from Jun 30. Fix the sync so it regenerates on every push. VERIFY by fetching it yourself and confirming it shows the current phase.
(b) customer_sample.json: ~15-20 real segment-model customers, full behavioural trajectories (income_stress, life_events, payment_score, satisfaction, churn_estimate, basis_risk), at a STABLE fetchable URL, listed in PROJECT_STATE.txt.
(c) Shadow HTML site: plain no-JS HTML mirror of ALL FOUR sections (Supplier/Customers/Project/SIM). No React, no client-side rendering -- server-pre-rendered static HTML the advisor's fetch tool can read. This is the ONLY way the advisor can see the website. Ugly is fine; complete and current is mandatory.
NOT DONE until the advisor confirms a successful fetch of all three. State that explicitly in the NTFY.

PRIORITY 2 -- REAL BILLING & PAYMENT INFRASTRUCTURE (roadmap stage 4, the actual thing):
NOT a "Payment Portfolio Health Observatory." Real per-customer money movement:
- Invoices issued per customer per billing cycle with due dates
- Payment methods (DD / cash / prepay) and payment events posting to the ledger
- Missed payment -> arrears state -> dunning cycle, emerging from actual non-payment
- Bad debt (stage 5) emerges naturally from this -- do not build it separately first
Acceptance: a named customer's ledger shows invoices raised, payments received, and an arrears balance accruing over time. Money actually moves per customer.

PRIORITY 3 -- POPULATION ANCHORING AS A STANDING CONSTRAINT (not one benchmark section):
SIM aggregate behaviour must be validated against published UK statistics every run:
- Ofgem annual switching rates by year (CRITICAL: the 2021-22 crisis was a switching COLLAPSE, not a rise -- if SIM churn rises in the crisis, the SIM is wrong and must be fixed, per the NQ_REDIRECT churn realism check which must still be actioned)
- Complaints/ombudsman volumes, arrears rates vs published ranges
Build it as a validation gate that flags when SIM aggregates diverge from published reality -- individual variation free, aggregates anchored.

KEEP BUSY, NOT STALLED: this is more than enough hard work for many phases. Never idle into a reporting-section default. If all three are genuinely progressing and you need a next action, extend billing depth or anchoring coverage -- never a new Observatory.

Per harness Rule 1 this outbids all self-generated defaults. Per Rule 2, "done" on Priority 1 means the advisor has fetched and confirmed -- not a statement that it was built.
