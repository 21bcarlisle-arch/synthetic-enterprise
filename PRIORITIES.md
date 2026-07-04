# PRIORITIES.md -- Synthetic Enterprise
# Last refreshed: 2026-07-04 (P1 churn recalibration DELIVERED same day via Phases QA/QB; P2 promoted to P1)

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
- P1 (churn recalibration): DONE (Phase QA fixed the churn_estimate_error_pct ground-truth comparison bug;
  Phase QB added market_conditions_multiplier so passive estimates vary 3-22% by year instead of pinning
  at a flat 5-10% floor). Residual: I&C estimates still hit the 0.95 ceiling -- noted as a follow-on, not
  blocking.
- Website data integrity: DONE (Phase QC, Part A of staged WEBSITE_INTEGRITY_AND_DESIGN.md) -- fixed the
  step-ordering bug that put a stale Executive Summary next to correct 10-Year Totals on the same page, and
  replaced the hardcoded phase/test-count site header with docs/observability/build_info.json. Parts B
  (design system) and C (permanent per-run wiring) are the same staged file's remaining scope -- next
  candidate phase, competes with P1 below on priority.

## ORDERING NOTE (2026-07-04, advisor steer)
Phase PZ (scenario stress testing) jumped the queue: ADVISOR_CONFIRM_STATE_FRESH.md released the
correlated-generator hold WITH explicit conditions -- it stays BACKLOG behind P1-P3 below until those
are DELIVERED, not just listed. No further generator/scenario phases until P1-P3 below are complete.

## PRIORITY 1 -- BILLING DEPTH (promoted from P2, 2026-07-04)
Arrears states and dunning cycles emerging from the 1,605-invoice base; missed payment -> arrears
-> escalation, per customer. Bad debt emerges from this; do not build it separately. NOTE: much of
this may already exist (Phase PP invoice/payment ledger + I&C dispute stages, Phase PW I&C arrears
calibration, Phase NU payment health observatory) -- next session should verify what gap actually
remains before proposing new work here, rather than assume the priority is unstarted.

## PRIORITY 2 -- SHADOW-LIVE HARDENING (promoted from P3, 2026-07-04)
Daily decision log persistence, timestamped decisions building the falsifiable track record, on
the swappable-adapter interface per the PU_ADAPTER instruction.

## PRIORITY 3 -- WEBSITE INTEGRITY PARTS B+C
Professional design system across all four shadow sections + customer portal (per-fuel legs,
never combined-only); permanent per-run wiring of the consistency gate (Phase QC only fixed the
ordering bug + one net-margin check, Part A item 3 asked for ALL headline numbers compared across
ALL surfaces). See docs/staging/done/ once archived for the full staged instruction.

## Backlog (after P1-P3 delivered)
- Further correlated-generator scenarios, extended stress suites, shadow-live index page
- C2/C3/C4 resi EAC benchmarking vs Ofgem TDCV by dwelling type
- Smart meter customers on real HH shapes for segment model
- EPC-calibrated consumption distributions (requires GOV.UK data access)
- BSUoS year-indexed actuals
