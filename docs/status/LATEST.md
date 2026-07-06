## Phase RP COMPLETE -- BILLING_AND_PAYMENTS_LEDGER.md CLOSED IN FULL (PRIORITIES.md P1a reopened)
Last updated: 2026-07-06T16:20:32Z

**Status:** COMPLETE. 15,836 tests collected, fast suite (15,712) clean. Epistemic: PASS.

**Phase RP:** recovered a second interrupted prior session's uncommitted work (a new
tools/generate_payment_ledger_data.py + its tests, matching edits already made to
simulation/arrears_engine.py, site/customers/index.html, tests/tools/test_billing_tab_fix.py, and
process_run_complete.py) -- verified complete against docs/staging/BILLING_AND_PAYMENTS_LEDGER.md's
four items and closed it out. Per-account chronological ledger (invoice/payment/notice/write-off/
recovery, running balance) built from real billing_ledger.json data, patched onto each customer
JSON. Billing tab renamed BILLING & PAYMENTS with Bills/Statement/Cashflow sub-views on
site/customers/index.html, each carrying a page-level reconciliation line (Collected + Outstanding
+ Written off == Billed). arrears_engine.py's RECOVERED/SOLD stages gained a structured amount_gbp
field (previously only inside a prose note string). Verified against the full live book:
reconciliation identity holds for every household (both fuel legs), at least one real write-off
case and one real open-balance case confirmed -- not fabricated.

**Prior:** Phase RO (2026-07-06) -- NAV_STORY_PLATFORM_METHOD.md P1, Home/Story landing + Platform
section. Phase RN -- Billing tab regression fix + closed-account UX. Phase RM -- Supplier tab
portfolio event stream + Recommended Actions elevation + heatmap click-through (CLOSES P1b). Phase
RL -- Customer 360 v4 items 3-4, real event effects + reaction chain (CLOSES P1a v4 scope). Phases
RF-RK: see docs/claude/phase-history.md and docs/PROJECT_OVERVIEW.md Section 4.

**Front of queue next:** PRIORITIES.md P1c (NAV_STORY_PLATFORM_METHOD.md) -- Method section
(operating-model diagram, R1-R6 rules with forging incidents, live staging-loop view, retro
library) + the Project tab slim-down (Company sub-tab -> Method, Capabilities sub-tab -> Platform).
Not yet started.


**Latest simulation results (2016–2025)** — auto-processed (511s / 9 min):
- Net margin: £1,535,307.74 | Gross: £6,467,308.57 | Capital: £51,433
- Treasury: £2,466,636 → £3,911,894 | 38 committee interventions | 1605 bills issued
- Enterprise value: £8,826,938.57 | Net after CTS: £6,360,822
- Retention: 14 offers, 14/14 retained | 6 no-offer churns | 6 total churned accounts