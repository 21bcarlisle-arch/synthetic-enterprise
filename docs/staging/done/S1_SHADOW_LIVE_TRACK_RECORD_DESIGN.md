[DESIGN NOTE] S1 -- Shadow-Live Proof-First Track Record -- Tier 3, proceeding in 4h unless redirected

## The ask (STRATEGIC_HORIZON_DECISIONS.md, S1 + Decision 2, adopted PRIORITIES.md 2026-07-07)

"PROOF FIRST -- shadow-live track record. QE's immutable daily decision log + PV's swappable
adapter are the plumbing; remaining work: live/near-live feed behind the adapter, daily
pre-registered decisions (hedge fraction, renewal pricing, retention EVs), predicted-vs-realised
scorecard. START THE CLOCK EARLY: track-record length cannot be bought later." Decision 2: the
track record is public from day one, misses included. PRIORITIES.md flags this design note as
needing the same caution as FROZEN_POLICY_BASELINE_DESIGN.md -- a visible, one-way-door-adjacent
public surface.

## What exists today

Phase QE + PV already built most of the plumbing: `tools/run_live_decisions.py` produces a daily
decision (hedge recommendation, renewal-price flags, acquisition prices) from `live_portfolio.json`
via a swappable `MarketDataPort` (`tools/market_adapters/`, frozen_2025 or synthetic).
`append_decision_log()` writes one immutable entry per UTC calendar day to
`site/state/live_decisions_log.jsonl`, first-write-wins, never overwritten. This already runs
daily (background_worker.py invokes it via process_run_complete.py's pipeline; confirmed on this
tree by four real log entries spanning 2026-07-04 to 2026-07-07).

## Key finding: the loop as built cannot ever be graded

Pulled the four most recent real log entries on this tree:

```
decision_run_at          market_as_of_date  elec_spot  days_to_renewal (C9)
2026-07-04T16:50:52Z     2025-06-07         70.31      22
2026-07-05T00:02:33Z     2025-06-07         70.31      22
2026-07-06T00:05:12Z     2025-06-07         70.31      22
2026-07-07T00:01:07Z     2025-06-07         70.31      22
```

Four days of real wall-clock elapsed time, and every field is byte-identical except the run
timestamp. Root cause: `tools/live_market.py::_effective_as_of()` falls back to the latest date
present in the SSP cache whenever the requested as-of date exceeds it, and
`run_live_decisions.py` never passes an explicit as-of -- so `market_as_of_date` is permanently
pinned to whatever the cache's last date is. That cache (`sim/cache/elexon_ssp_full.json`) stops
at 2025-06-07 because `background/prefetch_elexon_ssp.py::FETCH_END` is a hardcoded constant
matching `run_phase2b.py`'s designed historical-decade boundary (2015-11-07 to 2025-06-07) -- it
was never meant to be a rolling window, it was meant to bound the one-off historical fetch for
the sim's fixed 2016-2025 book.

The `days_to_renewal` figure is computed from that same frozen `as_of_date`
(`_renewal_flags(customers, as_of_date, ...)`), so it doesn't count down either. A "daily
pre-registered decision" log that never changes is not a track record -- it is one decision,
timestamped four times. Nothing in it can ever be marked realised or missed, because the
reference clock it is computed against never advances. This is the actual gap S1 has to close,
not the append-only logging mechanism (which already works correctly).

Could not verify from this session whether Elexon's real API now publishes settlement data past
2025-06-07 -- network access (curl/WebFetch) requires interactive approval not available in this
autonomous run. This is the one open factual question the recommendation below is contingent on;
flagging it explicitly rather than guessing.

## Two decoupled clocks, one bug

There are two different "as of" concepts wearing one variable:
1. **Market price freshness** -- genuinely bounded by what real Elexon data exists.
2. **Wall-clock elapsed time** -- what a renewal countdown and a realised/predicted grading
   mechanism actually need, and what has nothing to do with whether new settlement prices exist.
   `days_to_renewal` and "has this decision's horizon since passed" should be computed against
   real today, not against the market data's as-of date.

## Options

A. Extend the real Elexon fetch forward from 2025-06-07 on a rolling basis (new cache-refresh
   job, decoupled from `prefetch_elexon_ssp.py`'s one-off historical constant), so
   `market_as_of_date` genuinely advances as real settlement data is published. Correct in the
   limit, but contingent on the open question above (does real data past 2025-06-07 exist / is it
   fetchable) -- cannot be sized or committed to until that's answered.
B. Decouple the two clocks now, independent of A. `get_market_summary()` keeps reporting the last
   real known settlement price, but labelled honestly with its true age (e.g. "market data N days
   stale" surfaced on the public page, never hidden). `run_live_decisions.py` computes
   `days_to_renewal` and all future grading against real wall-clock today, not
   `market["as_of_date"]`. This alone makes renewal windows count down for real and lets the
   scorecard mark decisions realised/missed as their horizons pass in real time, even before A
   lands.
C. Point the live decision engine at the `synthetic` correlated-generator adapter instead, so
   prices move daily regardless of real data availability. Rejected -- Decision 2's public claim
   is proof against reality; grading recommendations against a generator seeded by this project
   would gut the "proof" and could read as misleading once published.

Recommendation: **B now**, cheap and immediately unlocks a genuine track record without waiting
on an unresolved external fact; **A as a fast-follow**, sized only once the open question is
answered (flag for Rich or a discovery-agent research pass: confirm whether data.elexon.co.uk
currently serves settlement prices beyond 2025-06-07).

## Scorecard design (once B lands)

New `tools/generate_track_record_scorecard.py` walks `live_decisions_log.jsonl`; for each entry
whose forecast horizon has since elapsed (per the wall-clock fix), join against what actually
happened:
- **Renewal-price flags**: did the customer renew at/near `proposed_rate_gbp_per_mwh` (compare
  against the realised rate recorded once the renewal executes)?
- **Hedge recommendation**: did INCREASE/HOLD/REDUCE turn out right against the commodity move
  that followed (once A lands and prices actually move; until then, honestly reported as
  "ungraded -- market data has not advanced")?
- **Retention EVs**: not currently in the logged decision at all -- `run_live_decisions.py` has no
  retention-offer branch today. Adding one (EV estimate at time of flag, using the existing
  counterfactual-lift machinery from Phase QQ) is required to satisfy S1's own stated scope
  ("hedge fraction, renewal pricing, retention EVs"), not optional polish.

First real scorecard entries won't exist until real elapsed time passes after the wall-clock fix
ships -- that IS the point of "start the clock early." Record the cutover date once implemented
so track-record length is auditable from a fixed, stated start, and publish the page from day one
per Decision 2 even while it shows zero graded decisions -- an honest "0 graded so far, clock
started <date>" is the correct first state, not something to wait out before publishing.

## Tier classification

Tier 3 per PRIORITIES.md's own framing -- once a public track-record page exists and starts
accumulating graded predictions, it becomes evidence a stranger can point to; walking it back or
quietly re-founding it later would read badly against the project's radical-honesty identity.
4h opt-out window applies; proceeding with Option B (wall-clock decoupling + scorecard scaffold,
`retention EV` field added to the daily decision log) unless redirected. Option A stays open,
gated on the real-data question above.
