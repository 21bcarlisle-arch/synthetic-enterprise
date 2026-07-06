[PROJECT] PRIORITY RESET -- the public website is now P1, ahead of further backend depth. Rich's direct verdict after reviewing the live site: still far below target, tab order unchanged, gas and electricity still bundled everywhere he looks.

WHY THIS RESET: the SIM tab (QY-RC), Project tab generators (RD/RG), and customer-PORTAL design tokens (QO) shipped -- but the FOUR PUBLIC TABS Rich actually looks at (poesys.net Overview/Supplier/Customers/SIM top-level + the six-section nav) are still structurally pre-overhaul. The big morning directive set (SUPPLIER_TAB_OVERHAUL, CUSTOMER_360_REDESIGN v4, NAV_STORY_PLATFORM_METHOD, WEBSITE_AS_SHOWCASE) is staged and acknowledged but NOT executed. Backend depth (CTS reconciliation, frozen-policy baseline, IA plumbing) is real work but must now YIELD to the front-end until the public site matches the vision.

DEFINITION OF "OVERHAUL" (so this doesn't get met with a palette flip again): it means STRUCTURE, NAVIGATION, TAB ORDER, LAYOUT, and PER-FUEL SEPARATION -- on the REAL public site (site/{index,sim,customers,project} + the portal Rich reaches by clicking a customer), NOT the shadow mirror, NOT just CSS colours. A white version of the same flat layout does NOT count as done.

NEW PRIORITY ORDER (work top-down; each is Tier 2, pre-approved; single-writer only -- do not start until SERIALIZE_WORKERS.md lock is in place):

P1a. CUSTOMER 360 (CUSTOMER_360_REDESIGN.md, v4 -- the reference implementation). The live C1 page must become: household with TWO first-class accounts (elec MPAN + gas MPRN each with own tariff/meter/consumption/bills/P&L), combined as an optional roll-up ONLY; tabbed IA (Overview/Accounts/Consumption/Billing/Timeline/Risk); usage charts (volume + shape + weather overlay); the bill equation visible (usage x price, why-different waterfall); the QP event ledger as the customer timeline; progressive disclosure inline, no popups; light + UK lens (MPAN/MPRN, p/kWh, EAC, PSR). GAS AND ELEC SEPARATED AT EVERY STAGE -- this is the specific thing Rich keeps flagging.

P1b. SUPPLIER TAB IA (SUPPLIER_TAB_OVERHAUL.md). 11 flat tabs -> grouped nav (Performance/Commercial/Trading&Market/Operations/Governance); Query persistent not a tab; Capabilities MOVED to Project; portfolio event stream as the spine; in-world rule (no test counts/phase letters on company surfaces); heatmap click-through; Recommended Actions elevated to Overview.

P1c. SIX-SECTION NAV + STORY (NAV_STORY_PLATFORM_METHOD.md). Home/Story landing; add Platform (CTO/CPO view) and Method (the harness) sections; the tab REORDER Rich specifically noted is unchanged.

P2 (resumes after P1a-c land + Rich confirms visually): CTS £0/£91,780 reconciliation (NEXT_PHASE.md -- already flagged as margin-shifting, keep the careful approach), frozen-policy baseline (FROZEN_POLICY_BASELINE_DESIGN.md), FEEDBACK_AND_REPUTATION, NUDGE_PHYSICS, SAAS_COVERAGE_MAP.

ACCEPTANCE for every P1 item: Rich opens the live public page and it reads like a professional SaaS product with gas/elec separated -- not white-flat. Report "awaiting Rich's visual review", never "done". Update PRIORITIES.md to this order now.

Also action the already-staged infra fixes first if not yet done: SERIALIZE_WORKERS.md (single-writer lock), FLAG_ALL_LAUNCHERS.md (autonomous-runner flag), PAGES_CONCURRENCY_FIX.md (stop the deploy-failure emails). These unblock clean single-writer front-end work.
