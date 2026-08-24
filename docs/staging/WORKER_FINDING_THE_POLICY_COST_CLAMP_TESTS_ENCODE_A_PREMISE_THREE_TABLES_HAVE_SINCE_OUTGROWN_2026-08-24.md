# The policy-cost clamp tests encode a premise three of their thirteen tables have since outgrown

**Severity:** LATENT
**Lane:** D_billing_metering
**Rank:** backlog (below the director's named set; nothing published is wrong today)
**Status:** QUEUED, not fixed on sight (SELF_INTERRUPT_DISCIPLINE — this is my own finding, and the
supply of these is infinite)
**Class:** a finding's own premise going stale between the mint and the build

## What is on disk

`tests/simulation/test_policy_cost_coverage.py` is **UNTRACKED** and 6 of its 20 tests fail. It was
written against `WORKER_FINDING_THE_COST_STACK_CLAMPS_SILENTLY_INSIDE_ITS_OWN_RUN_WINDOW`
(2026-08-14), whose headline is *"all 13 year-keyed policy/network tables end at 2024"*.

**That is no longer true, and I measured it rather than inheriting it.** At `2025-04-05`:

| | tables |
|---|---|
| **Clamped (10)** | `_NETWORK_COST_RESI_SME_BY_YEAR`, `_DUOS_IC_BY_YEAR`, `_CM_LEVY_BY_YEAR`, `_FIT_LEVY_BY_YEAR`, `_GAS_NETWORK_COST_BY_YEAR`, `_GGL_RATE_GBP_PER_METER_YEAR`, `_CFD_LEVY_BY_YEAR`, `_MUTUALIZATION_LEVY_BY_YEAR`, `_ELEC_SC_PENCE_PER_DAY_BY_YEAR`, `_GAS_SC_PENCE_PER_DAY_BY_YEAR` |
| **Since extended to 2025, i.e. covered (3)** | `_RO_COST_BY_OY_START`, `_CCL_ELECTRICITY_RATE_BY_YEAR`, `_GAS_CCL_RATE_BY_YEAR` |

So `test_the_2025_clamp_the_finding_measured` fails `assert 10 == 13`. The test is wrong, not the
code: it pinned the finding's *count* instead of deriving it.

## What is genuinely unbuilt

The instrument exists — `YEAR_KEY_BASIS` (13), `table_coverage`, `is_extrapolated`,
`extrapolated_tables`, `coverage_report` all pass their own tests. Missing is the **disclosure
path**, which is the half that matters:

1. `simulation/policy_costs.py::coverage_note` — absent.
2. `saas/reporting/annual_report.py::_extrapolation_note` — absent (3 tests ImportError on it).
3. `run_phase4c_on_phase2b` never emits `policy_cost_coverage` into the run output, so
   `annual_report` has nothing to render and the disclosure silently disappears.

The substantive claim still stands: a share of the published 2025 stack is priced on at least one
clamped table and **nothing on the page says so**. That is the R14 family — a figure without its
basis — and it is why this is worth finishing rather than deleting.

## Why it is queued and not done

It is not on the director's named set, it touches `simulation/` and `saas/reporting/` (both in the
live sim runner's import graph, so a multi-file signature change there has a crash window), and its
own premise needed re-measuring before a line could be written — which is the finding.

## Repair instruction, when drawn

Do **not** re-pin 13. Derive the expected clamped set from `table_coverage` inside the test so it
self-corrects as tables are extended, and keep the non-vacuity leg
(`test_a_date_inside_the_window_is_not_extrapolated`) as the control that stops the derivation
becoming a mirror of itself. Then build the three missing disclosure symbols above and assert the
note reaches the **rendered** report, not the run output (R11).
