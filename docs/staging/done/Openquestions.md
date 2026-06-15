# Open Questions & Proactive Improvement

## Context

Phase 6a (HH smart meter customers) is in progress. While that runs or
after it completes, the following questions and concerns have been raised
by Rich and his strategy advisor. You have better visibility into the
codebase and data than we do — investigate each one, form your own view,
and propose or implement fixes where you judge them appropriate. Be
proactive: don't wait for further instruction on items you can resolve
yourself.

## Open Questions

### 1 — Revenue not captured

Gross margin, capital cost, and net margin are stored in the run JSON but
total revenue (consumption x tariff rate) is not. Without revenue we
cannot calculate net margin as a percentage of revenue, which is the
industry standard profitability benchmark (expect 2-5% for a retail energy
supplier). 

Concern: we don't know if the simulation is producing credible margin
percentages or not.

### 2 — Forward curve realism

The simulation uses synthetic forward curves derived from historical spot
prices. Real UK power and gas forward markets have distinct term structure
dynamics — seasonal contango/backwardation patterns, risk premiums that
vary by tenor, and liquidity constraints that compress during crises (when
everyone wants to buy protection simultaneously). 

Concern: if the forwards don't reflect real market term structure, the
hedging cost/benefit figures are wrong, and the mandate redesign (Phase 5c)
may be optimised against an unrealistic price environment. There are likely
patterns in when the market is contango vs backwardated that a real
supplier's risk committee would exploit.

### 3 — Cost to serve model is thin

Current model: fixed overhead (£55/yr residential, £120/yr SME) plus bad
debt provision (2% revenue residential, 1% SME). This is a skeleton.

Concern: a real supplier's cost to serve includes customer acquisition
cost, metering and data costs, regulatory levies, system charges, contact
centre costs, and debt collection. The current model probably understates
true cost to serve significantly, which means net margin after cost to
serve is overstated.

### 4 — Idle detector false positives

The session watchdog triggers on pane silence, but long "Cogitating"
stretches produce no output for 5+ minutes. This causes false-positive
nudges and the autoloop cap firing unnecessarily.

Concern: wasted frontier tokens on unnecessary restarts, and misleading
signals about session health.

### 5 — Report clarity across runs

Now that Phase 5c introduced a mandate-hedged model alongside the original
reactive model, the report needs to clearly attribute every figure to its
source run. The executive summary should show net margin as % of revenue
for both models once revenue is captured.

### 6 — CLAUDE.md gaps

Two things not yet captured in CLAUDE.md:
- Non-blocking concurrency: if blocked on one task, move to the next
  independent item rather than waiting
- Session window is ~5 hours not 4 hours

## What we're asking

Investigate these concerns using your direct access to the codebase and
run data. Form your own view on severity and fix priority. Implement
whatever you judge to be straightforward fixes autonomously. For larger
items (e.g. forward curve realism) propose an approach via NTFY before
building.

Be proactive. Drive the project forward. Rich is available all day and
will respond to NTFY messages.
