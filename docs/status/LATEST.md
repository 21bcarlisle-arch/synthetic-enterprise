## Phase RR COMPLETE -- WEBSITE_AS_SHOWCASE.md tab 4 case-study recommender CLOSED, staging hygiene
Last updated: 2026-07-06T23:27:53Z

**Status:** COMPLETE. 15,856 tests collected. Epistemic: PASS.

**Phase RR:** housekeeping first -- archived 4 staged docs (CUSTOMER_360_REDESIGN.md,
SUPPLIER_TAB_OVERHAUL.md, NAV_STORY_PLATFORM_METHOD.md, PROJECT_TAB_OVERHAUL.md) to
docs/staging/done/ that PRIORITIES.md/PROJECT_OVERVIEW.md had already declared CLOSED IN FULL
(Phases RL/RP, RM, RQ, RG) but were never moved out of the active queue. Main work: new
tools/generate_case_study_recommender.py auto-curates 5 "interesting customers" (most eventful
journey, largest company-vs-SIM churn divergence, retention-save-then-churned-anyway, heaviest
arrears cascade, notable life event) by ranking real per-household signals already computed by
generate_customer_reaction_chain.py/generate_customer_sample.py -- nobody hand-picked by account
id. Live run picked C2/C_IC2/C5/C3/C7, each figure real (e.g. C_IC2's 2489% churn-estimate error,
sim 4% vs company 95%, a live instance of the documented I&C 0.95-ceiling behaviour). Output
site/data/case_studies.json, wired into process_run_complete.py, rendered as a new panel on
site/customers/index.html's login page linking into each household's Timeline.

**This closes WEBSITE_AS_SHOWCASE.md tab 4** (case-study recommender). Tabs 2 (frozen-policy
baseline) and 3 (learning ledger) remain gated behind Rich's visual confirmation of P1a-c, per the
priority-reset rule, not started.

**Gate cleared (2026-07-06 21:05 BST):** Rich confirmed via NTFY -- "I like the live site a lot.
It's a big improvement." This satisfies the P1a-c visual-confirmation gate. PRIORITIES.md P2 is
now ACTIVE (CTS £0/£91,780 reconciliation first, per docs/staging/drafts/NEXT_PHASE.md option B;
then frozen-policy baseline, FEEDBACK_AND_REPUTATION.md, NUDGE_PHYSICS.md, SAAS_COVERAGE_MAP.md).

**Prior:** Phase RQ (2026-07-06) -- NAV_STORY_PLATFORM_METHOD.md CLOSED IN FULL, Method section +
Project tab slim-down (closes PRIORITIES.md's entire P1a-c PRIORITY RESET). Phase RP --
BILLING_AND_PAYMENTS_LEDGER.md, per-account payment ledger + Statement/Cashflow views. Phase RO --
NAV_STORY_PLATFORM_METHOD.md P1, Home/Story landing + Platform section. Phases RF-RQ: see
docs/claude/phase-history.md and docs/PROJECT_OVERVIEW.md Section 4.


**Latest simulation results (2016–2025)** — auto-processed (525s / 9 min):
- Net margin: £1,535,307.74 | Gross: £6,467,308.57 | Capital: £51,433
- Treasury: £2,466,636 → £3,911,894 | 38 committee interventions | 1605 bills issued
- Enterprise value: £8,930,210.95 | Net after CTS: £6,433,343
- Retention: 14 offers, 14/14 retained | 6 no-offer churns | 6 total churned accounts