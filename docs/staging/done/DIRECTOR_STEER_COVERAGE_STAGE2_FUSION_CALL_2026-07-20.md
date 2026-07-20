# DIRECTOR STEER — Stage 2 of the coverage loop: the fusion call (2026-07-20)

**Type:** [STEER] — answers the decision raised in `POPULATION_COVERAGE_SOURCE_LANDSCAPE.md` §5 and authorises stage 2. Method remains yours.

**First: the stage-1 landscape is good work.** The coverage matrix (§2) is the load-bearing finding and it is honestly drawn — no row is `●` across the board, the two richest joint sources are precisely the gated ones, and you named the two gaps that matter rather than papering over them: household-level EV×PV×battery co-ownership is not openly observable, and attitudes are never jointly observed with fabric or tech. That those gaps sit exactly where the value and the mortality live is the finding, not an inconvenience.

## The fusion decision (§5) — the director's call, with reasoning

**Ruling: conservative crossing by default; fusion only where there is evidence for the conditional structure; every cell tagged with its provenance; and every fusion assumption recorded as a scheduled test rather than a settled fact.**

The reasoning, because it should govern similar calls later:

**1. The two errors are not symmetric.** Cross conservatively and you generate some households that do not exist — the cost is wasted N and a few implausible cells, and crucially *you know you do not know*. Fuse under a false conditional-independence assumption and you get a population that **systematically misrepresents** the joint structure, with the distortion concentrated in the tails, and everything downstream — pricing, segmentation, the fidelity grid, the carbon claims — learns from it as though it were true. An honest gap is recoverable; a confident error is not.

**2. Therefore, per cross-group pair, use your own §5 taxonomy and default to (c) over (b):**
   - (a) observed jointly → use it;
   - (b) fused under stated conditional independence → **only where there is positive evidence for the conditional structure**, never as a convenience;
   - (c) no basis → cross it and pay the N cost.
   Where (b) is used, the assumption is a **declared fidelity risk**, visible in the fidelity ledger.

**3. Provenance tagging is mandatory.** Every cell/dimension-pair in the committed structure carries its status — **observed / fused / assumed** — exactly as the ratified pitch requires every published figure to carry its claim status. Same discipline, applied to the population.

**4. The addition the director wants (this is the point, not a caveat): treat fusion assumptions as TESTABLE HYPOTHESES, not permanent choices.** Record each assumption explicitly and in a form that can later be checked against real households — the shadow-billing volunteer track is the natural first test bed, and the counterfactual-twin machinery already exists for controlled comparison. This converts an unavoidable weakness into a *scheduled experiment*: the proof engine turned on the population model itself. Design so this is cheap later — the assumptions register should be machine-readable and each entry should state what observation would refute it.

## Stage 2 authorisation

Proceed with §7 step 1 as written: **fetch the ungated open sources** (Census 2021 cross-tabs, MCS dashboard, DfT EV stats, solar/FIT, smart-meter stats, PAT and Ofgem aggregate tables, fuel-poverty tables, NEED anonymised sample), plus **published cross-tabs from the gated sources' report pages**. Cache raw outside the repo.

**Hard boundary, restated: no personal microdata.** Do not apply for, obtain, or hold unit records from EHS, Understanding Society, FRS or Census microdata. Published aggregates and cross-tabs only. The ratified pitch stakes a public claim that no household data has entered the system; that must stay true.

## Method note

Your §6 evaluation is accepted: covering arrays for the categorical dimensions, space-filling layered on for the genuinely continuous ones, worst-cell as the objective, and greedy-incremental construction to satisfy nesting. The observation that fractional-factorial fits the *curriculum dials* better than the population itself — because in the population the interactions are the point — is a good one and worth keeping in the record.

**Risk & proportionality:** stage 2 is fetch-and-cache plus published tables; no generator change, no personal data. Tag: **narrow/reversible — proceed by default.** Report in prose plus committed structure before stage 3, per the loop.

— Advisor, carrying the director's ruling, 2026-07-20.
