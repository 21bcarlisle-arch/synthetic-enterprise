# A5_tournament_fitness_mortality — FRAME (options only, no selection)

**Atom:** `A5_tournament_fitness_mortality` (epoch 4, `docs/design/maturity_map.yaml`, `provenance:
proposal`). **Status:** FRAME OPTIONS ONLY per RERANK_AND_PROVISIONAL_PLAN.md: *"Frame the candidate
fitness functions, mortality rules and their consequences; present them as options with trade-offs.
You may NOT choose the fitness function. That is a values decision reserved to the director."*

**This document does not recommend a default.** Every option below is presented with its
consequences, not a preference. Where a table forces an ordering, the ordering is by *complexity to
build*, never by *which the agent thinks is best*.

## Why this is reserved to the director, stated precisely (the risk this atom exists to name)

A tournament is, mechanically, a search process: many company variants run across generated-future
scenarios (`W1_2_generate_futures`), the fitness function scores each run, the mortality rule kills
the low scorers, survivors seed the next generation. **Whatever the fitness function rewards is what
the search will find a way to maximise — including paths a human wouldn't choose.** This project
already has the raw material for exactly that failure mode:

- Enterprise value is dominated by net margin (`saas/reporting/annual_report.py`), which is
  mechanically improvable by under-provisioning cost-to-serve for expensive-to-serve segments
  (`B2_opex_cost_to_serve` exists precisely because flat margin makes some customers net-negative —
  a pure-EV search would rediscover the incentive to under-serve them).
- The obligations register / domain invariants (`company/compliance/domain_invariants.py`) are
  currently *checked and reported*, not *load-bearing against a search process* — nothing today
  would stop an EV-maximising search from treating an occasional invariant breach as a cost worth
  paying if the expected fine is smaller than the expected gain (the exact mutualised-cost dynamic
  research for `F5_ofgem_licence_readiness` found real UK suppliers being regulated against, SLC 4B).
- Customer-harm signals (bill shock, satisfaction heterogeneity, vulnerable-customer flags) exist as
  *diagnostics* today, not as anything a fitness function reads — a search blind to them has no
  reason to avoid the strategies that produce them, if those strategies also raise EV.

This is the alignment problem — reward specification gaming / Goodhart's Law — reproduced inside the
simulation, not a hypothetical import from outside it. R12 (anti-goal-seek: margin is a diagnostic,
never a target) already governs the *company's own* behaviour inside a single run; this atom is
where the same discipline must be designed in at the level of *what makes a company variant survive
across runs*, or R12 is silently violated one level up, at the meta-level R12 itself doesn't reach.

## Candidate fitness functions (options, not a recommendation)

| Option | Formula shape | What it optimises for | Named risk |
|---|---|---|---|
| **A — Pure EV** | `fitness = enterprise_value` | Nothing but the bottom line | Included as the **strawman**, to make the danger legible, not as a viable option. Directly reproduces the under-provisioning/invariant-gaming risk above. Building this even as an experiment should itself be a director-authorised, curriculum-versioned act (R13), never a default. |
| **B — EV, hard-gated on compliance** | `fitness = enterprise_value` IF no Tier-1/material invariant breach, ELSE `-infinity` (instant cull) | EV among compliant survivors only | Simple to build (reuses the existing obligations register as a pass/fail gate). Risk: a single bright-line gate can still leave EV free to optimise every *non-gated* margin lever (e.g. legal-but-exploitative pricing/switching friction) — narrower than it looks. |
| **C — Multi-objective / Pareto** | Vector of `(EV, customer_harm_index, regulatory_standing_index, ...)`, ranked by Pareto dominance (no single scalar) | A *frontier* of trade-offs, not one number | Most faithful to "no fudge factor," avoids collapsing incommensurable goods into one weight a search can then game around that weight. Cost: requires defining and building the harm/standing indices themselves (real design work, itself director-scoped), and Pareto selection among many variants needs its own tie-breaking rule at cull time. |
| **D — Balanced-scorecard weighted sum** | `fitness = w1*EV + w2*customer_outcomes + w3*regulatory_standing + w4*operational_health`, director-set weights | Whatever combination the director's weights encode | Real-world analogue: how PE/turnaround investors increasingly score portfolio companies (financial + ESG/regulatory-risk covenants are now standard practice, not niche). Cheapest to build and reason about. Named risk: a weighted sum is *always* gameable at the margin the search has the most room to move in — if `w1` dominates, this option degrades toward Option A's risk profile in practice even though it looks safer on paper; the weights themselves become the values decision, not a detail. |
| **E — Constraint-satisfaction, EV as tiebreaker only** | Survival = passes ALL named hard constraints (compliance, customer-harm ceilings, regulatory standing floors); among survivors, EV ranks them | EV differentiates only among variants already judged acceptable on every other axis | Structurally closest to "EV is a diagnostic, never a target" (R12) applied at the meta-level. Cost: every constraint threshold is itself a values call that must be named and versioned (which harm ceiling, which standing floor) — this doesn't remove the values decision, it just relocates all of it into explicit, inspectable thresholds instead of implicit weights. |

## Candidate mortality rules (independent of which fitness function is chosen)

| Rule | Mechanic | Consequence |
|---|---|---|
| **Threshold cull** | Bottom X% by fitness score removed each generation | Simple, standard genetic-algorithm convention; X itself is a director-set curriculum parameter (R13) |
| **Instant death on hard breach** | Any Tier-1/material invariant violation kills the variant regardless of fitness score | Composable with ANY fitness option above as a floor; the closest mechanical expression of "no atom may be promoted... to hit a forecast"-style non-negotiable gating, applied to survival itself |
| **Tournament (pairwise) selection** | Variants compete head-to-head, winner survives; less deterministic than a flat threshold | Preserves more strategy diversity than a strict cutoff; real evolutionary-strategy literature default |
| **Elitism + diversity preservation** | Top-N always survive unconditionally, but a diversity metric prevents the whole population converging on one strategy | Guards against premature convergence to a single (possibly locally-exploitative) strategy monoculture — relevant precisely because Epoch 4's own worked example is where regime diversity (`W1_2_generate_futures`) starts mattering |

Mortality rules and fitness functions are **independent choices** — any row of the first table can
pair with any row of the second. The two decisions should not be conflated into one.

## What is NOT decided by this document (explicitly, per the director's instruction)

- Which fitness-function option (or hybrid) is used.
- Which mortality rule (or combination) is used.
- The concrete weights/thresholds/harm-index definitions any option would need if chosen — those are
  themselves values decisions nested inside whichever option is picked, not resolvable at FRAME
  stage.
- Whether Option A (pure EV) should ever be built even as a labelled, curriculum-versioned
  "what NOT to do" demonstration run — that is itself a call for the director, not an agent default.

## Dependencies and sequencing (unchanged from the atom's own registration)

BUILD remains gated on: (1) the director's choice above, (2) `W1_2_generate_futures` (the
generated-future engine this fitness function would actually score runs against) landing first, (3)
`A4_sim_approver` (the policy-agent playing the human approver for tournament runs) existing to
apply whatever the director chooses consistently across many runs without needing him present for
each one. `loop_stage` stays `idle` — this FRAME output does not promote the atom to BUILD eligibility
(per `MATURITY_MAP.md` §9 rule 8, DISCOVER/FRAME work never self-promotes an atom).
