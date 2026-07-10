# Bill shock definition — real domain-sense gap, not yet fixed

**Found:** 2026-07-10, director page comment (NTFY): *"Expected seasonality isn't a bill shock
is it really? It's when it jumps at the end of a contract or the DD jumps up when consumption
increases carried through. Things like that. Did you or it research energy bill shock?"*

## Was this researched? No.

Checked `docs/market_research/ASSUMPTIONS.md` and every other market-research doc for a "bill
shock" entry: **none exists.** The ≥20% threshold and the month-on-month comparison basis
(`saas/bill_generator.py::generate_bill()`'s `bill_shock_pct`) have no external citation anywhere
in this codebase. This was an invented convention, not a researched one — a genuine gap, not a
nitpick.

## The mechanism, exactly as it exists today

`simulation/run_phase4c_on_phase2b.py::build_monthly_bills()` groups settlement records into one
bill per customer per **calendar month**, in chronological order, and passes each bill's own
immediately-prior bill as `previous_bill_total_gbp`. `bill_shock_pct = abs(total - previous) /
previous` — a raw month-N-vs-month-(N-1) percentage change, with:

- **No seasonal/year-over-year adjustment.** A resi customer's real December bill vs. November
  bill will show a large, entirely expected jump from winter heating demand alone — this
  mechanism cannot distinguish that from a genuine surprise.
- **No contract-end/tariff-reversion detection.** The real UK phenomenon Rich names — a fixed
  deal ending and reverting to a much higher SVT/deemed rate — is exactly the kind of "shock" a
  real supplier's customer-service function cares about, and this mechanism has no way to flag it
  specifically; it would only show up if it happened to also cross the raw 20% threshold that
  month, indistinguishable from any other cause.
- **No Direct Debit recalculation/catch-up detection.** Real DD accounts are billed a smoothed
  monthly amount that periodically gets recalculated against actual consumption/price
  (a genuine, well-known "DD jumped" complaint driver in UK energy retail) — not modelled as its
  own event type at all in this codebase (checked: no `dd_recalculation` or equivalent concept
  exists).

## What the real run data shows (checked, not assumed)

494 total bill-shock events across the 2016-2025 run. Month distribution does **not** cleanly
match a pure heating-seasonality hypothesis (which would predict a sharp Nov-Feb peak) — April,
May, June, September, and October all show comparable or higher counts than the deep-winter
months, for both gas and electricity legs separately. This is inconclusive rather than
confirming or ruling out any single cause: it's plausibly a mix of staggered contract-renewal
dates (spread across the year by each customer's own acquisition anniversary, not clustered by
calendar season) and the UK Ofgem price cap's own quarterly reset months (Jan/Apr/Jul/Oct), on
top of whatever genuine seasonal consumption swing exists. **Properly separating these requires
the fix below, not eyeballing the aggregate distribution** — flagged honestly as inconclusive,
not stretched into a confirmed finding either way.

## Research landed (2026-07-10, same session, later): `docs/market_research/BILL_SHOCK_EVENT_TYPES_ANCHORS.md`

Dispatched real web research (WebSearch/WebFetch, available in this interactive session) into
the two named event types before attempting any redesign, matching this project's "research
first, don't invent the anchor" discipline. Real, sourced findings:

- **Contract-end reversion magnitude:** SVT/price-cap rate currently ~8-14% (£150-£260/yr)
  above the cheapest fixed deals (July 2026 market) -- real, sourced, but explicitly
  **time-varying**, not a fixed constant (the 2021-22 crisis produced much larger gaps
  industry-wide). Any redesign must not hardcode one number.
- **Reversion timing:** Ofgem SLC 7A requires 30 days' notice on deemed-contract terms, no exit
  fees; exiting a fixed deal within 49 days of its own end date is also fee-free. **Could not
  source** a single universal "reversion happens on day X" rule -- practice varies by supplier
  (some roll to a deemed/OOC rate, others to their own SVT).
- **DD recalculation frequency:** Ofgem's own 2022-onward Direct Debit Market Compliance Review
  exists BECAUSE review frequency and price-change handling are inconsistent across the
  industry -- a regulator-acknowledged fact, not a research gap on this pass. Ofgem's Credit
  Balances decision (2022) does require suppliers to notify customers before a DD change and
  glide credit balances back over ~12 months (not an instant snap), but **no clean "maximum
  legitimate single jump %"** exists to cite.
- **No formal Ofgem "bill shock" definition exists at all**, confirmed by targeted search --
  any redesign must define its own working threshold, not borrow a regulatory one.
- **A real, structural, non-seasonal cause for part of the observed pattern**: Ofgem reviews the
  price cap quarterly (Jan/Apr/Jul/Oct) -- this plausibly explains part of the parent finding's
  April/October elevated shock counts as a genuine industry-wide event, not pure noise, though
  still not conclusively separated from seasonal consumption effects without the actual redesign.

## Year-over-year comparison BUILT (2026-07-10, same session, later)

The seasonality half of the redesign (comparing against the same calendar month a year prior)
was built: `simulation/run_phase4c_on_phase2b.py::build_monthly_bills()` gained additive
`bill_shock_yoy_pct`/`bill_shock_likely_seasonal` fields, and `saas/reporting/annual_report.py`
threads them through to `shock_events` so a real business surface (Operations tab) shows the
split. **Self-caught via a fresh-context `phase-close-evaluator` review** (HARNESS_BEST_PRACTICE_
ADOPTION.md item 2): the feature initially shipped with zero test coverage on the new fields
(the pre-existing 18 phase4c tests tested none of it), and the evaluator's own manual smoke-test
found a real semantic bug -- a month immediately following a genuine anomaly (reverting to
baseline) was mislabelled `likely_seasonal`, since its own month-on-month swing is large and its
year-over-year comparison is small, the same signature real seasonality produces, for the wrong
reason. Fixed by excluding a month from the seasonal label if its own immediately-prior calendar
month was itself flagged as a month-on-month shock (`_prior_calendar_month()`); the exact bug is
now a named regression test. 8 new tests, all passing (`tests/simulation/
test_run_phase4c_on_phase2b.py`).

## Still not built

Explicit event-type detection (contract-end tariff reversion; DD recalculation) remains separate,
bigger work needing new SIM state -- the anchors from the research above are in hand, but two
genuine design choices remain open (a time-varying not fixed reversion differential; no citable
"max DD jump" figure to bound an invented one). Registered in PRIORITIES.md as backlog, not
rushed.
