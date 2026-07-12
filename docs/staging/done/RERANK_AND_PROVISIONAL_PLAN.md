# RE-RANK + PROVISIONAL PLAN (P1, director-decided 2026-07-12)

## Part 1 — Re-rank of your two authored proposals (both ACCEPTED)
Good decomposition; both name real gaps nobody had mapped. Verdicts:

**F5_ofgem_licence_readiness — ACCEPT. DISCOVER now.**
High immediate value: the licence path IS the gate between "simulation" and
"company" (capital adequacy, systems/process requirements, fit-and-proper
persons, reporting duties). What it turns up may CONSTRAIN Epoch-3 design, so
discovering it late is expensive. Discover now, build gated to Epoch 5.

**A5_tournament_fitness_mortality — ACCEPT, but FRAME OPTIONS ONLY.**
Frame the candidate fitness functions, mortality rules and their consequences;
present them as options with trade-offs. **You may NOT choose the fitness
function.** That is a values decision reserved to the director, and the reason
is exact: a tournament optimising purely for enterprise value will evolve a
company toward whatever maximises EV — including customer exploitation and
regulatory gaming — with only mortality rules and constraints standing in the
way. This is the alignment problem reproduced inside the simulation, and the
principal must choose what the company is FOR. Frame it; he decides.

## Part 2 — Build a PROVISIONAL PLAN (compute it; do not guess)
We now have the ingredients, so derive rather than estimate:

1. **Empirical cycle times:** mine the git history of maturity_map.yaml for
   every level transition with timestamps. Report the actual distribution
   (median/spread) per level-step, per lane, per loop stage. Weekend actuals
   exist (D3 L2->L3 overnight; W5_1 L0->L2 in a day; W1, W3_1 a level each).
2. **Critical path:** dependency graph + epoch exit tests -> the longest chain
   to each epoch's exit. Name the chain explicitly; it is the thing that
   determines when go-live analysis can begin.
3. **Concurrency, computed:** use file_scope disjointness to derive the
   MAXIMUM USEFUL WIDTH at each phase. This settles the "how parallel should
   we be" question with arithmetic instead of opinion. State the number.
4. **Model the true bottleneck — the director.** Review, ratification, Expert
   Hours and Tier-1 approvals are the scarce resource, not compute. Use the
   decision-effort/elapsed model from the governance work: forecast the
   DIRECTOR-HOURS each phase needs. If he is the critical path, say so and
   quantify it — that is a finding, not an embarrassment (and it is the same
   FTE model, pointed at the project itself).
5. **Confidence tiers:** HIGH for Epoch 2 (decomposed), MEDIUM for Epoch 3,
   COARSE for 4-5 (undecomposed — the estimate improves as DISCOVER lands).
   Re-forecast at every epoch boundary and after every ~10 level transitions.

## LAW A GUARDRAIL (non-negotiable, add to CLAUDE.md)
**The plan is a diagnostic and a tie-breaker, NEVER a target.** Dates are
forecasts; exit tests remain the ONLY gate. No atom may be promoted, and no
verification shortened, to hit a forecast. If a date and a test conflict, the
date is wrong. Deviation from the plan is ALLOWED and expected — re-rank on
evidence — but must be logged with a reason.

## Use
When the self-refill draw is ambiguous, follow the plan's critical path.
Publish it on the Journey door with confidence bands (honest forecasting is
itself an investor artefact).

## DoD
Both proposals ranked in PRIORITIES.md as above; plan computed from real data
(not estimated); critical path named; max-useful-width stated per phase;
director-hours forecast; confidence tiers + re-forecast cadence; Law A
guardrail in CLAUDE.md; plan published on the Journey door; Monday pack
includes it. One digest line.
