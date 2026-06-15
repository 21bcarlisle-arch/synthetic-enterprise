# Phase 5c: Hedging Mandate Redesign

## Objective

Redesign the hedging philosophy from "speculative book with a risk governor"
to "supply obligation first, active position second." This is a fundamental
change to how the simulation models a real energy supplier's hedging
behaviour.

## Context

The current model starts from a low hedge fraction and the risk committee
reacts upward when VaR breaches thresholds. This is backwards — it models
a speculative position with a safety valve, not a supply business managing
its purchase obligation.

The result: capital costs running at ~41% of gross margin because the book
carries significant unhedged exposure. In 2021 the risk committee added
value vs naked, but the business still lost money. A properly mandated
supplier would have been largely hedged before the crisis hit.

Rich's industry experience: EDF and similar suppliers operated a minimum
hedge mandate. The default is fully hedged. The active position (typically
~10%) handles weather window uncertainty and genuine asymmetric
fundamentals plays. Speculation is not the base case — supply obligation
management is.

## The New Mandate

**Minimum hedge floor: 0.85** (85% of volume hedged forward by default)

**Active position buffer: up to 0.15** (15% unhedged for weather window,
short-term demand uncertainty, and fundamentals-driven positions)

**Risk committee role changes:** Instead of deciding whether to hedge,
it manages the active position within the 0.15 buffer. It may:
- Recommend increasing hedge fraction toward 1.0 if downside risk is
  asymmetric (e.g. pre-winter with storage concerns)
- Recommend holding at 0.85 floor if fundamentals suggest spot will be
  below forward (backwardation expected)
- Never recommend below 0.85 — that breaches mandate

**Capital cost changes:** Collateral requirement should reflect only the
active unhedged position (max 15% of volume), not the full naked exposure.
This should significantly reduce capital cost as a share of gross margin
in normal years.

## What to build

1. Add `MIN_HEDGE_FLOOR = 0.85` as a simulation constant, applied at
   contract term inception — all new terms start at 0.85 minimum

2. Modify the risk committee logic: it operates within [0.85, 1.0] range
   only. It cannot recommend below 0.85. Its decision space is now whether
   to move toward 1.0 (more hedged) based on VaR and fundamentals signals,
   or hold at floor.

3. Recalculate capital cost to reflect only the active unhedged fraction
   (1 - hedge_fraction), not the full portfolio VaR. The collateral buffer
   is on the active position, not the notional book.

4. Re-run the full 9.5yr simulation with the new mandate.

5. Regenerate ANNUAL_REPORT.md and publish to GitHub Pages.

6. In the hedge effectiveness section, add a new comparison:
   - Actual (mandate-hedged) vs naked vs old model (reactive hedging)
   - What did the mandate cost vs the old approach in calm years?
   - What did it save in 2021-2022?
   - What is capital cost as % of gross margin under the new mandate?

## Fidelity delta

After this phase the simulation models a real supplier's hedging behaviour
rather than a speculative trading book. The 2021-2022 crisis section should
show a business that was largely protected by its forward purchases, not one
that scrambled to hedge after the fact.

## Constraints

- Delegate all implementation to local Qwen
- Do not change the settlement engine, weather model, or customer book
- The Historical Ground Truth law applies — the simulation cannot see
  future prices when deciding hedge fractions
- Document the mandate clearly in a new section of CLAUDE.md under
  "Simulation Design Decisions"

## Gate

**[REVIEW_GATE]** — Rich reviews the regenerated annual report, specifically:
- Capital cost as % of gross margin (expect significant reduction)
- 2021 net margin (expect improvement vs current £-1,096)
- Hedge effectiveness comparison: mandate vs old reactive vs naked
- Whether the business behaviour now looks credible to a domain expert

## NTFY

On completion:
1. "Phase 5c complete. Mandate-hedged simulation re-run finished."
2. "Capital cost ratio: [new %] vs 41% under old model."
3. "2021 net margin: [new figure] vs £-1,096 under old model."
4. Report URL for review.
