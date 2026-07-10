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

## Not fixed this turn

This deserves a real redesign, not a quick patch: comparing against the same calendar period a
year prior (to net out seasonality) and/or explicitly detecting the two named real-world event
types (contract-end tariff reversion; DD recalculation) would require new logic in the billing/
contract model, plus honest research into how each is actually timed and sized in real UK energy
retail before building anything — the same "research first, don't invent the anchor" discipline
already applied throughout this session's other work (MARGIN_REALISM, B2 taxonomy). Registered
in PRIORITIES.md as backlog, not rushed into an already very large session.
