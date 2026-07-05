## Phase RD COMPLETE -- phases.json generator + Project tab Sim-runs counter fix
Last updated: 2026-07-05T21:12:32Z

**Status:** COMPLETE. 15,732 tests collected, fast suite (14,470) clean. Epistemic: PASS.

**Phase RD (PROJECT_TAB_OVERHAUL.md R-A/consistency scope, WEBSITE_INTEGRITY_AND_DESIGN QW Part 2 CLOSED):**
- site/data/phases.json was hand-curated and stale since 2026-07-03 (latest_phase frozen at OL)
  -- a direct R-A violation causing the Project tab's stale Timeline, frozen Capabilities cards,
  and corrupted Test Progression/Phases-per-day charts (duplicate x-axis labels, one absurd bar)
- New tools/generate_phases_json.py parses PROJECT_OVERVIEW.md Section 4's 433 phase headers
  (reusing generate_project_state.py's proven phase/test parser), wired into
  background/process_run_complete.py so it self-regenerates every run -- latest_phase now
  correctly RD
- Fixed the Project tab's "Sim runs" dead counter (always showed 10, the truncated run_history
  list length) via new count_run_history_total() reading the full run_history.json (now 100)

**Front of queue next:** WEBSITE_AS_SHOWCASE.md Part 0 / PROJECT_TAB_OVERHAUL.md /
SUPPLIER_TAB_OVERHAUL.md -- the four site/shadow/*.html mirror pages are still on the pre-v4
dark terminal-monospace theme.

**Prior milestones:** Phases QR-QZ/RA-RC (acquisition funnel, debt-branch, event-frequency,
correlation panels, Prices/Weather/BM rebuilds, freshness stamps) -- docs/claude/phase-history.md
and docs/PROJECT_OVERVIEW.md Section 4.


**Latest simulation results (2016–2025)** — auto-processed (525s / 9 min):
- Net margin: £1,535,307.74 | Gross: £6,467,308.57 | Capital: £51,433
- Treasury: £2,466,636 → £3,911,894 | 38 committee interventions | 1605 bills issued
- Enterprise value: £8,826,938.57 | Net after CTS: £6,360,822
- Retention: 14 offers, 14/14 retained | 6 no-offer churns | 6 total churned accounts