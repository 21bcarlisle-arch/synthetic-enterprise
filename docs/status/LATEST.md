## Wake-doorbell third-strike fix + BILL_CORRECTNESS_ADDENDUM Defect 1 CLOSED
Last updated: 2026-07-09T00:06:37Z

**Status:** COMPLETE. 16,012 tests pass (full suite minus known-slow simulation integration suites).
Epistemic: PASS.

**Wake-doorbell fix (R3, director-direct):** two staged P1 docs sat unactioned 2+ hours despite
staging_watcher logging "delivered (confirmed)" wakes, because session_watchdog.py's autoloop
nudge and REVIEW_GATE reply relay were still raw, unguarded tmux send-keys -- a gap an earlier
same-day fix (commit cc2d741c) explicitly flagged as deferred and never closed, racing
staging_watcher's now-safe wake into the same pane with no coordination. Per R3, eliminated the
duplicate mechanism: tmux_relay.py gains relay_lock() (fcntl cross-process lock, mirrors
tree_lock.py) making send_keys_when_idle() atomic across daemons; session_watchdog.py's two call
sites now route through it like every other daemon. session_watchdog restarted live, verified.
Full evidence chain in docs/retrospectives/2026-07-08-wake-doorbell-third-strike.md.

**BILL_CORRECTNESS_ADDENDUM.md Defect 1 CLOSED:** C6's 20% VAT and ~28MWh/yr were already correct
for its true SME segment -- the director-found mislabel ("Household / Residential" on the portal)
was a pure render-layer bug in site/customers/index.html's badge/label logic, which only
special-cased I&C and silently collapsed every other segment into Residential. Fixed with an
explicit per-segment lookup. Sweeping for the same class found a second, independent instance:
saas/non_commodity.py's VAT_RATE dict was missing an "I&C" key, silently charging I&C accounts
domestic-rate (5%) VAT instead of the legally-required 20% business rate -- fixed, with a
regression test guarding the class. Defects 2-4 (bill period/reads/MPAN, ToU-ready line structure,
portal-vs-ledger-vs-sample reconciliation) next; Defect 5 (I&C billing model) registered to
backlog. DOMAIN_SENSE_AND_COMPLIANCE.md (P1 compliance programme) queued behind Phase 4 per its
own sequencing; harness-side pieces background-lane eligible now.

**Prior:** Phase RX (2026-07-08) -- S1 shadow-live track record CLOSED (Options B + A). Phase RW
(2026-07-07) -- SAAS_COVERAGE_MAP.md CLOSED, P2 queue fully closed. Phases RF-RX: see
docs/claude/phase-history.md and docs/PROJECT_OVERVIEW.md Section 4.

**Latest simulation results (2016–2025)** — auto-processed (468s / 8 min):
- Net margin: £1,526,516.74 | Gross: £6,447,283.33 | Capital: £51,210
- Treasury: £2,466,636 → £3,903,143 | 38 committee interventions | 1550 bills issued
- Enterprise value: £8,220,970.68 | Net after CTS: £6,414,742
- Retention: 12 offers, 12/12 retained | 6 no-offer churns | 6 total churned accounts