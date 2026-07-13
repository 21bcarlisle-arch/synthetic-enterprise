## Background-worker NTFY fix (root-caused recurring pipeline failures) + wide DISCOVER batch
Last updated: 2026-07-13T07:13:57Z

**Status:** self-refill cycle (idle-tier DISCOVER/FRAME), latest sim run processed successfully.
Epistemic PASS throughout. All commits pushed.

**Infra fix (real, root-caused, R4):** found and fixed the cause of repeated
"Failed to process run_complete_*.md (rc=1)" entries in background-worker-log.md. The
`background-worker` tmux session's own `start_worker.sh` launch was missing the
`${NTFY_ENV_FLAGS[@]}` pass-through every sibling NTFY-touching session correctly has --
so `process_run_complete.py` (spawned as a subprocess) crashed at import time whenever a real
headline change reached its notification step, silently dropping the run and leaving the marker to
retry indefinitely. Fixed the script, restarted the actual tmux session, and verified the running
process's own environment now carries the NTFY vars. Confirmed working end-to-end: the next real
run (`git=5a7e470f`, net margin £1,524,058) processed cleanly -- 17,117 tests passed, report
regenerated, committed, pushed.

**DISCOVER batch (BUILD stays gated per epoch sequencing throughout; no code written except the
infra fix above and one earlier full E2 BUILD+live-verify already reported):**
- **W1_2_generate_futures / W2_6_sme_distress_twin / W2_4_household_budget / W2_5_life_event_stream
  / W2_8_self_rationing / W2_9_segment_debt_tnc / W2_2_population_draw:** each grounded in real,
  current (2026) external data (NESO scenario practice vs. quant stochastic-generation methods;
  UK insolvency sector concentration; ONS income deciles + JRF essential-cost floor; UK life-event
  rates; National Energy Action self-disconnection polling; Ofgem DD compliance review; population-
  synthesis/IPF methodology). One real correction found and flagged, not glossed over: the
  household-budget atom's own registered debt-priority ordering ("food before energy") isn't well
  supported -- real Citizens Advice/StepChange guidance treats energy as a PRIORITY debt alongside
  rent/council tax, not ranked below them.
- **W2_3_competitor_field / C2_discovery_through_interfaces:** mis-registration corrections on
  existing evidence (same class as earlier D2/G2/E2 corrections this session) -- W2_3 was entirely
  blank despite real, already-wired, DESNZ-anchored competitor-savings code
  (`simulation/market_switching_propensity.py`) existing and driving real churn calculations; C2's
  independently-actionable onboarding-wiring gap was re-verified still open, not stale.

**Prior (same session, already reported):** E2_revenue_reconciliation reached its L3 target
(live-verified on poesys.net); W1_reveal_over_time's first Expert Hour passed with one low-severity
finding; W2_7_willingness_classification's initial DISCOVER pass landed.

**Latest simulation results (2016–2025)** — auto-processed (463s / 8 min):
- Net margin: £1,505,286.33 | Gross: £6,455,406.22 | Capital: £51,273
- Treasury: £2,466,636 → £3,883,451 | 38 committee interventions | 1575 bills issued
- Enterprise value: £7,281,815.13 | Net after CTS: £6,385,545
- Retention: 12 offers, 12/12 retained | 4 no-offer churns | 4 total churned accounts