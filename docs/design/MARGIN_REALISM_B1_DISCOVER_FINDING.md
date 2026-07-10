# B1 (margin bridge, Maturity Map DISCOVER stage) finding: two live report sections disagree

**Status:** DISCOVER-stage finding, not a build (per MATURITY_MAP.md Section 2: DISCOVER
output is "distilled findings + named references + anchors", BUILD is a separate,
later stage). No code changed. Filed from the second dial-weighted maturity-map
self-refill draw (`B1_margin_bridge`, level 2->3).

## What was checked

`saas/reporting/margin_attribution.py::build_margin_bridge_series()` is real, working
code: its own residual reconciles to ~£0 for every year transition (verified against
`docs/reports/run_output_latest.json`), so it is internally self-consistent on its own
terms. Auditing its real_world_twin ("FP&A margin bridge deck") and how it's actually
surfaced turned up something more concrete than a missing feature.

## The finding: two adjacent report sections, two different pipelines, disagreeing numbers

`saas/reporting/annual_report.py` appends TWO separately-named margin-bridge sections
back to back (lines 8872-8873): `_section_gross_margin_bridge()` ("Phase BE", built
straight from `management_accounts[yr].income_statement.*` -- the real double-entry
ledger) and `_section_net_margin_bridge()` ("Phase NT", built from
`data["margin_bridge_series"]`, which is `years[yr].*`-based -- the SIM-side aggregate,
same pipeline flagged in the E2 finding). **They render one directly after the other
in the actual generated `docs/reports/ANNUAL_REPORT.md`, both claiming to show
gross-margin movement, with no label explaining they use different data sources --
and their numbers disagree.**

Live evidence, 2016->2017 transition, both tables read directly from the current
`ANNUAL_REPORT.md`:
- "Gross Margin Bridge" (ledger-based) table: `ΔGM £` = **+£116,919.31**
- "Net Margin Bridge" (years[]-based) table, same transition: `Gross Δ` = **+£116,417**

A real FP&A veteran reading these two tables in sequence -- exactly the Expert Hour test
this map is built around -- would immediately ask "these are both labelled as the
gross-margin change for the same year, why do they disagree, and which one is real?"
This fails BOTH halves of the Expert Hour bar at once: **substance** (the two numbers
for "the same thing" are not the same number) and **legibility** (nothing on the page
tells the reader they are reading two different pipelines).

## Root cause: the same unresolved question as the E2 finding, now with a visible symptom

This is not a new root cause -- it is the SAME structural divergence documented in
`docs/design/MARGIN_REALISM_E2_TWO_PIPELINES_FINDING.md` (years[].net_gbp vs
management_accounts income_statement.net_margin_gbp disagreeing on how policy/network
pass-through interacts with margin), now shown to have a second, LIVE, user-visible
manifestation on the actual generated report, not just an internal data inconsistency
found by comparing raw JSON. This raises the priority of resolving the E2 root cause:
it is not only a "which denominator" question for one dashboard figure any more, it is
actively producing two contradictory numbers on the one document a real board member
would read.

## Other, smaller DISCOVER-stage gaps noted (not investigated further this pass)

- `gross_delta_gbp` in the bridge is a single lump figure -- a genuine FP&A margin
  bridge commonly separates a rate/price effect from a volume effect within gross
  margin movement (a "price-cost-volume bridge"). Whether this convention is standard
  specifically for UK energy-supplier reporting (vs a generic FP&A convention) is being
  checked via a dispatched discovery-agent task against real UK supplier reporting
  practice; findings will land in `docs/market_research/ASSUMPTIONS.md` under a
  "B1 margin bridge (Maturity Map DISCOVER)" heading once complete.
- `portfolio_change` (active customer count delta) is tracked as an informational
  figure only -- not an attributed £ driver, not part of the residual reconciliation.
  A real customer-growth/churn margin contribution (new-customer vs lost-customer £
  effect) may be a real, missing driver category; same discovery-agent task is checking
  whether this is standard in real supplier reporting.
- No opex/cost-to-serve driver line exists yet in either bridge -- expected and
  correctly NOT a gap to fix here, since MARGIN_REALISM Step 3 (opex mechanism,
  currently in progress) is the dependency that would feed it.

## Next step (not this turn)

Once the E2 root cause (why `non_commodity_cost_gbp` and `policy_cost_gbp +
network_cost_gbp` disagree, and why the ledger nets it at gross while `years[]`
deducts it again post-gross) is traced and resolved, both bridge sections should
either converge onto one pipeline or be explicitly, visibly labelled as answering
different questions -- registered in PRIORITIES.md alongside the E2 finding rather
than as a separate, disconnected task.
