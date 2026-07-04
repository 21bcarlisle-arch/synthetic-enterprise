# PRIORITIES.md -- Synthetic Enterprise
# Last refreshed: 2026-07-04 (P1 shadow-live hardening DELIVERED via Phase QE; Website Integrity Part C
# DELIVERED via Phase QF; Part B (design system + customer portal per-fuel legs) is now the sole P1)

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
- Website data integrity Part A: DONE (Phase QC, staged WEBSITE_INTEGRITY_AND_DESIGN.md) -- fixed the
  step-ordering bug that put a stale Executive Summary next to correct 10-Year Totals on the same page, and
  replaced the hardcoded phase/test-count site header with docs/observability/build_info.json.
- Shadow-live decision log persistence: DONE (Phase QE) -- append_decision_log() writes
  site/state/live_decisions_log.jsonl, one immutable entry per UTC calendar day, closing the gap where
  run_decisions() silently overwrote the same dated snapshot every cycle and no track record accumulated.
- Website data integrity Part C (permanent per-run wiring): DONE (Phase QF) -- widened the Part A
  consistency gate from a single net-margin check to 8 headline metrics (net/gross margin, enterprise
  value, bills, committee interventions, retention offers/retained, churn count) compared across the
  dashboard totals vs run_insights.json exec-summary source; a mismatch now NTFYs Rich immediately instead
  of only printing to a log nobody watches in real time (generate() propagates the gate result instead of
  discarding it). Freshness stamps (git commit + phase, not just a timestamp) added to every shadow page
  footer. KEY FINDING: the widened gate immediately caught a real, pre-existing gross-margin discrepancy
  (dashboard £6,452,603 vs exec-summary £6,467,309, ~£14.7k / 0.2%) caused by tools/generate_insights.py
  preferring the _ledger_headline subtotal over total_gross_gbp -- the same class of bug Part A fixed for
  net margin, just never applied to gross. Fixed at root (precedence flipped to match net margin's and
  extract_portfolio's convention). Part B (design system + customer portal per-fuel legs) is the only
  remaining scope from the staged instruction.

## ORDERING NOTE (2026-07-04, advisor steer)
Phase PZ (scenario stress testing) jumped the queue: ADVISOR_CONFIRM_STATE_FRESH.md released the
correlated-generator hold WITH explicit conditions -- it stays BACKLOG behind P1 below until it's
DELIVERED, not just listed. No further generator/scenario phases until P1 below is complete.

## PRIORITY 1 -- WEBSITE INTEGRITY PART B (PROFESSIONAL DESIGN SYSTEM)
One coherent design system across all four shadow sections + customer portal: consistent nav,
typography, spacing, palette, components (KPI cards, tables, RAG chips), responsive. Customer portal
to proper billing/CRM standard -- per-fuel legs everywhere (electricity and gas as SEPARATE accounts,
e.g. C4 and C4g each with own consumption/tariff/invoices/P&L), combined view as an optional roll-up,
never the only view; invoice/payment/arrears history per account from billing_ledger.json. Shadow
mirror stays in lockstep (same canonical data, same generator pass, plain HTML). See
docs/staging/done/WEBSITE_INTEGRITY_AND_DESIGN_PARTA_DONE.md for the full original staged instruction
(Part B, item 6-8).

## Backlog (after P1 delivered)
- Further correlated-generator scenarios, extended stress suites, shadow-live index page
- C2/C3/C4 resi EAC benchmarking vs Ofgem TDCV by dwelling type
- Smart meter customers on real HH shapes for segment model
- EPC-calibrated consumption distributions (requires GOV.UK data access)
- BSUoS year-indexed actuals
