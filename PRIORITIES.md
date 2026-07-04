# PRIORITIES.md -- Synthetic Enterprise
# Last refreshed: 2026-07-04 (P1 billing depth DELIVERED via Phase QD; P2 shadow-live hardening promoted to P1)

## COMPLETED
- P1 (billing depth): Arrears states + dunning cycles + emergent bad debt -- DONE (Phase QD).
  simulation/arrears_engine.py: arrears_stages()/ic_arrears_stages() model the full missed-payment
  -> FIRST_NOTICE -> SECOND_NOTICE -> RESOLVED|WRITTEN_OFF cascade per customer (resi + I&C dispute
  variant); compute_emergent_bad_debt()/apply_emergent_bad_debt() replace the flat get_bad_debt_rate()
  formula with real written-off arrears. KEY FINDING: flat-rate bad debt was £92,550.88; real emergent
  figure is £3,051.07 -- confirms the PP/PW/NU infrastructure PRIORITY 1's note flagged was already
  most of the way there; QD closed the remaining "bad debt emerges from arrears, not a formula" gap.
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
correlated-generator hold WITH explicit conditions -- it stays BACKLOG behind P1-P2 below until those
are DELIVERED, not just listed. No further generator/scenario phases until P1-P2 below are complete.

## PRIORITY 1 -- SHADOW-LIVE HARDENING (promoted from P2, 2026-07-04)
Daily decision log persistence, timestamped decisions building the falsifiable track record, on
the swappable-adapter interface per the PU_ADAPTER instruction.

## PRIORITY 2 -- WEBSITE INTEGRITY PARTS B+C
Professional design system across all four shadow sections + customer portal (per-fuel legs,
never combined-only); permanent per-run wiring of the consistency gate (Phase QC only fixed the
ordering bug + one net-margin check, Part A item 3 asked for ALL headline numbers compared across
ALL surfaces). See docs/staging/done/ once archived for the full staged instruction.

## Backlog (after P1-P2 delivered)
- Further correlated-generator scenarios, extended stress suites, shadow-live index page
- C2/C3/C4 resi EAC benchmarking vs Ofgem TDCV by dwelling type
- Smart meter customers on real HH shapes for segment model
- EPC-calibrated consumption distributions (requires GOV.UK data access)
- BSUoS year-indexed actuals
