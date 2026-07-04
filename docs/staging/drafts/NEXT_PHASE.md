# NEXT PHASE PROPOSAL: Phase PZ -- Scenario Stress Testing via Synthetic Market

**Status:** Awaiting advisor confirmation that PROJECT_STATE.txt is fresh at
21bcarlisle-arch.github.io/synthetic-enterprise/status/PROJECT_STATE.txt (fix deployed
2026-07-04T05:35Z). Will proceed once confirmed by external fetch OR after 4h opt-out window
(expires 2026-07-04T09:35Z UTC) unless redirected.

## Gap addressed

Phase PX built CorrelatedGeneratorAdapter (bivariate OU). Phase PY validated it (equivalence
gate PASS, endgame gate UNLOCKED). The gap: the company's live decision tools (run_live_decisions.py)
still only run against a single frozen 2025 snapshot. The adapter exists but the company has
never exercised it for scenario analysis. A real UK energy supplier stress-tests renewal and
hedging decisions across base/bull/bear/crisis market scenarios before committing.

## What real fidelity is gained

1. Company can run renewal decisions under 4 scenarios: base (normal OU), bull (persistent
   backwardation, low vol), bear (persistent contango, moderate vol), crisis (high-vol regime).
2. Scenario output table: proposed renewal rates, hedge recommendations, margin impact --
   across all 4 scenarios for the active renewal window customers.
3. Board section in annual report: Scenario Sensitivity table -- per-scenario margin delta
   vs base case.
4. Closes the final CLAUDE.md known failure (regime-change blindness).

## Architecture

tools/run_live_decisions.py: run_scenario_analysis(scenarios) -> dict per scenario.
saas/reporting/annual_report.py: _section_scenario_sensitivity.
background/process_run_complete.py: calls run_scenario_analysis(); commits scenario_analysis_latest.json.

## Epistemic: PASS (company's own model, public statistics)

## ~15 tests target

## Expected outcome
Board can answer: what would our renewal rates and hedge positions look like if 2021-22 happened
again? Regime-change blindness (CLAUDE.md known failure) fully closed.
