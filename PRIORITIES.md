# PRIORITIES.md -- Synthetic Enterprise
# Last refreshed: 2026-07-04 (advisor steer: churn model recalibration is P1; correlated-generator work returned to backlog)

## COMPLETED
- P1a: PROJECT_STATE.txt auto-sync -- FIXED (Phase PT; GH Pages fix 2026-07-04)
- P1b: customer_sample.json + customers.json + supplier.json at stable fetchable paths -- DONE (Phase PT)
- P1c: Shadow HTML site (4 sections) -- DONE (site/shadow/* auto-regenerating on every run)
- P2 (billing): Billing & Payment Infrastructure -- DONE (Phases PP/MW/MX/MY/NH)
- P2 (network): Network Charge Year-Indexed Actuals -- DONE (Phase 78; PROJECT_OVERVIEW.md Sec 9 gap closed)
- P3: Population Anchoring -- DONE (Phases NS/PQ/PR/PS: switching, churn, complaints, arrears)
- P4: Shadow Live Operation -- DONE (Phases PU/PV: live decisions + market adapter)
- Correlated market generator: Correlated Synthetic Market Generator -- DONE (Phase PX: bivariate OU adapter; Phase PY: equivalence gate PASS)
- Scenario stress testing: Phase PZ -- 4 scenarios; QUANTIFIES residual regime-change exposure for the board
  (correction 2026-07-04: PZ does NOT close regime-change blindness -- the 85% hedge floor closed it
  historically; PZ adds board-facing visibility into residual exposure. Claims must match artifacts.)

## ORDERING NOTE (2026-07-04, advisor steer)
Phase PZ (scenario stress testing) jumped the queue: ADVISOR_CONFIRM_STATE_FRESH.md released the
correlated-generator hold WITH explicit conditions -- it stays BACKLOG behind P1-P3 below until those
are DELIVERED, not just listed. No further generator/scenario phases until P1-P3 below are complete.

## PRIORITY 1 -- CHURN MODEL RECALIBRATION
Evidence in customer_sample.json: company estimate floored at ~5% while sim crisis churn ran
0.38-0.41; churn_estimate_error_pct shows the same -0.82 to -0.88 error at renewal after renewal,
across nearly every customer; and where the model DOES fire it overshoots (C_IC1: +1478%). The
company is effectively blind on its single most commercially important estimate -- it drives
retention offers, CLV, pricing.
Approach: diagnose why estimates pin at the floor during sustained-crisis periods (the 24-month
reference window from the NQ redirect -- was it built?); validate against the per-customer
basis-risk data now published; measure with the NJ/NK recall/precision/F1 framework; target
improvement on BOTH crisis and calm years. The sim ground-truth side was already realism-checked
via population anchoring -- this is the company-model side.

## PRIORITY 2 -- BILLING DEPTH
Arrears states and dunning cycles emerging from the 1,605-invoice base; missed payment -> arrears
-> escalation, per customer. Bad debt emerges from this; do not build it separately.

## PRIORITY 3 -- SHADOW-LIVE HARDENING
Daily decision log persistence, timestamped decisions building the falsifiable track record, on
the swappable-adapter interface per the PU_ADAPTER instruction.

## Backlog (after P1-P3 delivered)
- Further correlated-generator scenarios, extended stress suites, shadow-live index page
- C2/C3/C4 resi EAC benchmarking vs Ofgem TDCV by dwelling type
- Smart meter customers on real HH shapes for segment model
- EPC-calibrated consumption distributions (requires GOV.UK data access)
- BSUoS year-indexed actuals
