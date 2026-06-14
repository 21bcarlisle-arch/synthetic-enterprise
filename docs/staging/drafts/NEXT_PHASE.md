# Proposed next phase: HH smart meter customers (Phase 6a)

Status: DRAFT — proposed by Claude Code under the opt-out REVIEW_GATE
process in CLAUDE.md ("How to operate autonomously"). Will be actioned in
4 hours from the second NTFY unless Rich stages a different instruction in
docs/staging/.

## Why this, why now

Phase 5b (report data pipeline) is complete and pushed (`05d4156`).
CLAUDE.md's "Decisions made 14 June 2026" names HH smart meter customers as
the next priority, ahead of I&C (deferred) and event-driven customer
lifecycle (depends on this). This is also "hollow gap #4" — every customer
today is on a profile-class shape; no half-hourly consumption data exists
anywhere in the simulation, which blocks ToU tariffs, demand flexibility,
EV/solar/battery work, and the rest of the smart-energy value chain.

`saas/customers.py` already anticipates this: `eac_kwh` is documented as
"may be `None` for future smart-meter customers", but no customer currently
has `eac_kwh=None` and no HH consumption path exists in
`simulation/settlement.py` or `simulation/demand_model.py`.

## Two-way-door check

This phase only *adds* customers and a new consumption-data path; it does
not change existing profile-class customers or their settlement logic. It is
fully reversible — if HH data integration proves too disruptive, the new
customers can be removed or left dormant without touching C1-C6/C1g-C4g.

## Proposed scope

1. **Source HH data**: 2-3 residential customers using a public dataset
   (e.g. a UKPN/Ofgem smart meter trial extract, or — if licensing/availability
   is unclear — Open-Meteo-correlated synthetic HH profiles generated the same
   way as the existing weather-driven demand shapes in
   `simulation/weather_inputs.py` / `simulation/demand_model.py`). Decide
   data source first; this gates everything else.
2. **Add 2-3 new customers** (e.g. C7, C8, C9) to `saas/customers.py` with
   `eac_kwh=None` and a new field indicating HH metering (exact field TBD by
   whichever Qwen delegation designs the schema change).
3. **HH consumption path**: extend `simulation/demand_model.py` /
   `simulation/settlement.py` so HH customers' settlement uses real
   half-hourly consumption directly instead of a profile-class shape ×
   annual estimate. Profile-class customers (C1-C6, C1g-C4g) must be
   unaffected — same outputs as today, verified by the existing 252 tests
   continuing to pass unchanged.
4. **Run + verify**: a full 2016-2025 run with the new customers included,
   confirming the simulation still produces a coherent settlement record set
   and the existing report pipeline (`run_phase4c_on_phase2b
   --save-json` -> `annual_report.py`) handles the mixed profile-class/HH
   portfolio without errors (new customers will show "Not available" for any
   4b/4c metrics not yet computed for them — document explicitly, as Phase 5b
   did for other gaps).
5. **Tests**: new tests for the HH data loader and HH consumption path; no
   regressions in the 252 existing tests.

## Explicitly out of scope for this phase

- ToU tariffs (depends on this, not concurrent with it)
- Event-driven customer lifecycle (separate phase, also next-in-line per
  CLAUDE.md roadmap)
- Any change to C1-C6/C1g-C4g's existing behaviour or figures

## Delegation

As always: design and review stay with this agent; HH data-loading code,
schema additions, and demand-model extension are delegated to local Qwen.

## Gate

At completion: commit, NTFY with results, write the next draft (likely
event-driven customer lifecycle per the roadmap), second NTFY, 4-hour
opt-out window — same pattern as this one.
