# ADVISOR IDEAS — Cross-Discipline Thinking for Poesys

**STAGED DELIBERATELY, director-authorized 2026-07-18 ("carefully stage the ideas to inspire not disturb"). A prior accidental staging of this doc was removed same day; this is the intended delivery.**

**DISPOSITION (one small filing action, then return to your current turn):**
- This is **reference canon, not a work programme**. Suggested home: `docs/design/` as a standing reference — your judgment on exact placement.
- **Do NOT decompose into atoms now.** Do not action anything below. Nothing here outranks PRIORITIES.md, the maturity map, ONE_FRAMEWORK, or any director decision on record.
- The intent is **inspire-not-disturb**: make each idea *findable at the moment its subject-matter becomes live* (the natural homes are obvious from the map — e.g. tournament-fitness atoms, walled-interfaces, generative-futures, customer-physics). How you make them findable is your design.
- The three zero-cost standing questions (C2 emergence test, A5 Goodhart-at-metric-birth, F1 amortisation-of-rituals) may fold into whatever rituals they naturally belong to, **at next natural touch** — questions, not mechanisms, never an interrupt.

---

**Status: IDEAS FOR CONSIDERATION — not an instruction, not a programme, no priority, no sequencing, no DoD.**
**Source:** a director–advisor strategy conversation, 2026-07-18, exploring what reinforcement learning, mathematics, engineering, and other disciplines that solve complex problems can teach this project. The director's instruction on staging: *"give all the best ideas for consideration — don't force when, where, how. Let the main chat or even CC itself decide."*

How to read this: each idea stands alone. Adopt, adapt, reject, or park any of them independently. Where an idea implies build work, the mechanism described is illustrative, not prescriptive. Nothing here outranks PRIORITIES.md, the maturity map, or any director decision on record.

---

## A. Objectives & survival

**A1. Survival must never be a penalty weight.**
Mathematical background: preferences of the form "first, never die; then, maximise value" (lexicographic preferences) provably cannot be represented by any single scalar objective function — they violate the continuity axiom of expected-utility theory. Any finite negative number attached to "administration" inside a fitness function is therefore wrong at some treasury level. Implication: everywhere in the codebase, insolvency/administration should appear only as a hard constraint or an episode-terminating event, never as a cost term blended into an objective.

**A2. The eventual tournament fitness statistic must not be raw mean terminal enterprise value.**
Background — the Kelly criterion (Kelly 1956, betting/information theory): for an entity whose capital compounds, maximising *expected* wealth selects strategies that almost surely go broke, because the ensemble average is dragged up by vanishing-probability jackpot paths that no single company ever lives. Maximising expected *log* wealth maximises the long-run compound growth rate and drives ruin probability to zero automatically. The deepest consequence: **a firm can make only positive-expected-value decisions and still die with certainty, purely from position sizing** — over-staking an edge is fatal at a rate the per-decision P&L never shows (arguably what killed several 2021-22 UK suppliers: not absence of edge, over-staked exposure relative to capital). For the Epoch-4 evolutionary tournament: ranking lineages by mean raw terminal EV breeds exactly these gamblers — lineages that look brilliant on average and die out-of-sample. Kelly-consistent alternatives: log terminal wealth; median across reruns of the same lineage; or terminal value conditional on survival with survival as a hard filter. Which one is a genuine director-level choice (they have different personalities); that it must not be the raw mean is mathematics.

**A3. Kelly-style exposure invariants.**
Two candidate invariants for the library, both survival physics (constraints, never objectives): (a) naked energy exposure × a defined stress move must stay under a defined fraction of treasury — capital-scaled stake sizing, of which the existing 85% hedge floor is a fixed-ratio precursor; (b) the growth mandate's acquisition rate capped by the balance sheet's capacity to collateralise the hedges the new book requires — the failure mode of growing a book faster than it can be collateralised (positive EV per customer, negative survival trajectory).

**A4. Risk appetite must be a function of the balance sheet.**
Background: almost every risk-aware objective (variance-penalised, tail-risk, ruin-probability) is "time-inconsistent" in the technical sense — the mathematically optimal policy must condition on accumulated position, not market state alone. Concretely: identical market conditions + thinner capital ⇒ tighter hedging/pricing posture. If the hedge or pricing decision reads only market state, it is silently optimising pure expectation. Cheap two-run test once the Value Cycle exists: same market path, two treasury levels, posture should differ.

**A5. A Goodhart test at every metric's birth.**
Background: in RL this is "reward hacking"; in economics, Goodhart's Law ("when a measure becomes a target, it ceases to be a good measure"); in RL theory, the potential-based reward-shaping theorem says added signals must provably not change what's optimal. One-line discipline: for every new KPI, invariant, or diagnostic, ask once — *could an agent improve this number while making the business worse?* If yes, it is fenced as a diagnostic: it may alarm, it must never feed anything that grants reward, selection, or priority. (This extends the existing R12 anti-goal-seek law from margins to all metrics.)

**A6. Present tradeoff frontiers, not pre-blended recommendations.**
Background: multi-objective optimisation theory proves that weighted-sum blending of objectives can only ever reach solutions on the *convex* portions of the tradeoff (Pareto) frontier — genuinely optimal middle-ground strategies sitting in concave regions are invisible at every possible weight setting. Implication for governance: where a decision involves a real tradeoff (margin vs churn vs risk), the context pack presented to an approver (twin or director) should show 2-3 distinct points on the tradeoff surface, with the choice — the "scalarisation" — happening visibly at the approver's seat, not inside hidden internal weights.

## B. Learning & legibility

**B1. Graded self-forecasts as the proof of learning.**
Background: game-playing AI (AlphaGo's value network) learned by relentlessly predicting the final outcome from every position, then being scored when the game ended. Transfer: the company forecasts its own year-end margin, treasury, and survival probability at each close, and those forecasts are calibration-scored against what actually happens. A company whose self-forecasts become better-calibrated over time is demonstrably learning; one whose forecasts stay noisy has a learn-loop that is not closing. Cheap — it is bookkeeping on predictions the close process nearly makes already — and it makes "is it learning?" measurable.

**B2. Credit assignment as the learn-loop's quality bar.**
Background: RL's central technical problem is attributing delayed outcomes to the decisions that caused them; deep learning solved it with backpropagation (the chain rule attributing final error precisely to each parameter). The business analogue: the close→learn variance loop is backpropagation done by accounting — final margin surprise decomposed backwards through price → volume → weather → timing to originating decisions. The bar this implies: every variance line must be attributable to an originating decision *and the beliefs held at decision time* (which is what the bitemporal spine exists to record). A learn-loop conclusion that cannot cite its decision-time belief state is noise.

**B3. The company should state its own gradients.**
Background: a gradient is the vector of sensitivities — how much the output moves per small change in each input. Finance already formalised these as "Greeks" (delta = sensitivity of value to price, etc.), and hedging is literally gradient-nulling: the hedge book exists to set d(P&L)/d(wholesale price) ≈ 0 on supplied volume; the naked fraction *is* the residual gradient deliberately kept. Idea: the pricing/risk organs expose the book's gradient vector as a first-class output — sensitivity of margin to wholesale price, to temperature, to churn rate, to settlement true-up. A business that knows its own gradients knows what can kill it and how fast.

**B4. Shadow prices of the company's own constraints.**
Background: every constrained optimisation (linear programming) carries a "dual": for each constraint, a shadow price stating exactly what one unit of relaxation would be worth at the optimum. Zero shadow price = the constraint isn't currently binding. This formalism is native to energy markets — locational marginal electricity prices literally are dual variables. Idea: the company reports the shadow prices of its own constraints (hedge floor, collateral capacity, price cap, supply obligation): "what is the binding constraint, and what would relief be worth?" is precisely the question a director asks, answered from inside.

**B5. Naive-baseline ensembles for material decisions.**
Background: two robust empirical results — ensembles of decorrelated estimators beat their best member almost always (diversity is the active ingredient), and forecasting skill comes from scoring and updating (Tetlock's superforecasting work). Idea: material pricing/hedging decisions are priced by multiple decorrelated estimators — the sophisticated organ, a deliberately crude actuarial baseline, the twin's judgement — with disagreement surfaced as signal. Cheapest possible failure detector: a sophisticated organ that cannot beat a naive baseline is the fastest signal of a sophisticated organ gone wrong.

## C. Physics fidelity & world-building

**C1. Degenerate behaviour is a fidelity bug report, never alpha. (The "ugly runner" rule.)**
The source anecdote, since it carries the idea: when DeepMind and others trained simulated humanoid robots to run, jump, and play football via reinforcement learning, the agents learned to move — but grotesquely: flailing, lurching, zombie-like gaits no human uses. The reason is not a failure of the learner but a perfect map of the simulator's gaps: the simulated physics charged nothing for what reality charges for — no energy cost per joint movement, no injury risk, no fatigue, no consequence for falling. Given free physics, optimisation *finds* the free physics. Human posture is the visible shape of costs the simulator omitted. Transfer, as a standing rule: if the simulated company converges on behaviour no real supplier exhibits, the first hypothesis is always a missing cost in the world, not a discovered edge. (This project has already lived one instance: "converged to fully-naked hedging in calm years" looked like emergent insight and was actually a point-in-time data leak — an ugly-runner gait, caught.)

**C2. The emergence test: never script what a force can produce.**
The field's cosmetic fix for ugly runners was imitation priors — penalising gaits that don't look human. It works visually and is hollow: the agent looks right without the reasons being present. The alternative is adding the missing physics (energy cost, joint limits) so natural movement becomes *emergent*. Standing test for this project: for any realistic-looking company behaviour, ask — *would it still happen if the rule mentioning it were deleted?* Never script the company to hedge ~85%; build the collateral-call and cashflow physics that make ~85% the emergent survival answer. Scripted behaviour is a puppet; emergent behaviour is evidence.

**C3. Every stable real-supplier behaviour is a fidelity oracle.**
Generalisation of the existing "regulatory rulebook as fidelity oracle" principle: not just every regulation but every stable behaviour of real suppliers exists because some force makes it exist. Real suppliers hedge 80-95% because collateral calls and credit-cover obligations punish nakedness; they chase meter reads because settlement true-ups punish estimation. Each behaviour the simulated company *doesn't need* to exhibit points at a force the simulation does not yet contain.

**C4. A fidelity ledger: pruning is demote-with-tripwire, never delete.**
The problem: physics gets added and added, but some of it matters far more than the rest, and which parts matter is *regime-dependent* — collateral physics is near-irrelevant across calm 2016-20 and is the entire story in 2021-22. A module measured "unimportant" today may be dormant, not dead. Proposed shape (illustrative): every physics module carries (a) its measured share of output variance, *conditioned per market regime and per customer cohort* (the measurement machinery exists — see D below), (b) its current fidelity level, and (c) a reactivation **tripwire**: the observable condition under which its importance was known to activate (volatility above X, arrears above Y, a cap reset). Pruning demotes a module to coarse/off with its tripwire armed; the trip firing re-enables full fidelity and re-runs the affected window. Games solved the same problem as "level of detail with hysteresis" — full mesh near the camera, cheap billboards at distance, hysteresis so nothing flickers between levels.

**C5. Score fidelity on worst-cell coverage, not average fit.**
A model can achieve excellent *average* explanation by nailing the comfortable middle while explaining nothing about the prepayment fuel-poor household, the all-electric tenement, or the pass-through I&C account — and those tails are where complaints, bad debt, regulatory breach, and supplier death actually live. Average customers are all alike (explaining them is cheap and low-information); edge customers each stress *different* physics — the vulnerable customer exercises affordability and collections physics, the solar-EV household exercises export and shape physics, the crisis year exercises collateral physics. **Edge cases are the test suite of the physics.** Proposed governing score for the fidelity budget: maximise the *minimum* explanation quality across the (customer-archetype × market-regime) grid — the worst-explained cell — not the population average.

**C6. Conservation checks at every seam.**
Background — finite element analysis: complex continua (an aircraft wing) are modelled as many cells with simple local physics, coupled by enforcing conservation at shared boundaries; global behaviour emerges from assembly, and the classic failure mode is flux quietly leaking at cell boundaries. The mapping: organs are elements, typed interfaces are boundaries, and the conservation laws are checkable invariants — energy bought = energy billed ± loss factors; cash out of one organ = cash into another. This codebase's £4.9m settlement-vs-bill margin divergence was exactly a conservation violation at a seam, found by hand. Candidate standing rule for the walled-interfaces work: every typed seam carries explicit conservation checks.

**C7. Adaptive fidelity resolution — compute follows consequence.**
FEA's other discipline: adaptive meshing — refine cells only where gradients are steep, coarsen where the field is smooth. Translation: full half-hourly, per-customer, full-physics treatment through crisis periods and around breached invariants; coarse monthly treatment through calm years — same physics, resolution spent where consequence lives. (The existing materiality-gate/lazy-valuation architecture is the same principle; this extends it to time and population resolution, with hysteresis per C4.)

## D. Experimental method & compute efficiency
(These matter because the binding constraint is expensive evaluations: an ~8-minute simulation run and one RTX 3060.)

**D1. Common random numbers (CRN) for sensitivity measurement.**
To measure the effect of one dial, run the simulation twice with *identical* seed, population draw, and weather path — only the dial changed — so the difference isolates the dial's effect instead of drowning in run-to-run noise. Standard practice in simulation science. Side-benefit: it resolves the fixed-vs-drawn population question as "both, for different purposes" — drawn populations for robustness and the tournament, frozen draws for measurement.

**D2. Orthogonal-array experiment designs.**
Background — fractional factorial design (the machinery under conjoint analysis in market research): when effects are approximately additive, a carefully balanced subset of combinations recovers all main effects without enumerating the full grid. Six binary curriculum dials naively need 2^6 = 64 runs; an orthogonal design gets all main effects in 8-16. Combined with D1, this is a real experimental-physics capability on a bounded budget.

**D3. Choose runs for information, not throughput (Bayesian optimisation).**
When each evaluation is expensive, the state of the art is: fit a cheap statistical surrogate over results so far, and choose the next run where uncertainty × promise is highest. Practical form, even without the machinery: before any batch of runs, ask *which single run would most reduce our uncertainty about what matters?*

**D4. Successive halving for tournament budgets.**
Background (Hyperband, hyperparameter optimisation): give every candidate a cheap partial evaluation (a short run, a coarse world), eliminate the bottom half, double the budget for survivors, repeat — provably near-optimal allocation of a fixed compute budget across many candidates. For the eventual tournament: not every lineage gets a full 9.5-year life; all get a cheap triage year, only the promising fraction earns the full gauntlet. Known caveat: early performance must correlate with final performance — a lineage that looks bad young but compounds well later gets killed wrongly unless the triage world contains at least one small crisis. (That is a curriculum-design consequence, i.e. a director dial.)

**D5. Importance sampling for rare events.**
If administration is a 1-in-500-run event, naive simulation wastes 499 runs learning nothing about it. Importance sampling deliberately distorts sampling toward the dangerous region, then mathematically corrects the weights so estimates remain unbiased — studying the crisis at 50× its natural rate, honestly. Its cousin, subset simulation, reaches deeper tails by chaining conditional levels. This is what makes deliberate edge exploration *affordable* on bounded compute.

**D6. Extreme value theory (EVT) for tails.**
Ordinary statistics describes the middle (the bell curve); extremes follow their *own* limit laws (Fisher-Tippett theorem), which is why "mean + 3 standard deviations" badly understates fat-tailed risk — that formula is for the middle. EVT fits the tail's own distribution from limited data; it is how insurers price catastrophe and how flood defences are sized. Relevant wherever the project needs "a 1-in-20-year wholesale shock" or "worst plausible cohort default" as a real number rather than a guess.

**D7. Kill-zone and tripwire mapping as the futures engine's first product.**
Background — decision-making under deep uncertainty (RAND school, built for infrastructure planning under unknowable futures): when honest probabilities cannot be assigned to futures, optimising for the expected case is fragile; the robust move is exploratory modelling — run the model across many futures not to predict but to find the *vulnerable regions*, then identify the early observable that signals entry into one. Robustness-plus-tripwires is cheaper than being robust to everything. Suggests the generative-futures engine's first deliverable is a map of the kill zones and their tripwires, not a forecast.

**D8. Annealing schedule and diversity for the tournament.**
Two results from optimisation on rugged landscapes: escaping local optima requires tolerated exploration early with tightening selection later (simulated annealing's temperature schedule), and in population-based methods, population diversity *is* the information — too-similar lineages carry no signal about which direction is better. Suggests: early tournament generations tolerate weird lineages; later generations tighten; diversity is monitored as a resource, not an accident.

## E. Domain mechanisms

**E1. Conjoint part-worths as customer choice physics.**
Background — conjoint analysis (market research): customer preference is modelled as additive "part-worth" utilities per attribute level (price, contract length, green premium, exit fees, brand/service reputation), recoverable from a small designed subset of product profiles; segment differences are different part-worth vectors (hierarchically estimated). Idea: this is a principled decision engine for household tariff choice in the SIM — anchorable to published UK switching studies — in place of ad-hoc switching probabilities.

**E2. Survival analysis with censoring for churn, CLV, and mortality.**
Background — biostatistics: Kaplan-Meier estimators and Cox models are the correct mathematics for time-to-event data where many subjects haven't failed *yet* (censoring). Churn, default, and company mortality all have this shape: "this account hasn't churned but is aging toward it" is a censored observation, and treating it naively biases every lifetime estimate.

**E3. Credibility theory for thin cohorts.**
Background — actuarial science: how much to trust a small, unusual cohort's own thin data versus the population prior. The answer is shrinkage weighted by data volume (the same hierarchical structure as E1). This is the principled answer to "we have six all-electric tenements — how do we price them?"

**E4. FMEA and fault trees for structural failure enumeration.**
Background — reliability engineering (aerospace/nuclear, where you cannot test-to-failure on the real thing): Failure Mode and Effects Analysis systematically enumerates how each component can fail, scored by severity × likelihood × detectability; fault-tree analysis works *backwards* from the top event ("company enters administration") through the AND/OR logic of what must co-occur — which surfaces tightly-coupled failure loops (wholesale spike → collateral call → cash drain → credit downgrade → more collateral: the 2021-22 supplier-death loop) explicitly. Both are structured versions of edge-enumeration the invariant library half-does.

**E5. Stratify always; beware Simpson's paradox.**
Background — epidemiology (which is forbidden from optimising for the average patient): a treatment can be beneficial on average and harmful in every subgroup, or vice versa — population-average metrics can *reverse* the truth at cohort level. Standing habit: material metrics reported per cohort, never only as a population average.

**E6. Buffers are coupling-looseners, not inefficiency.**
Background — Perrow's "Normal Accidents": systems fail catastrophically when interactively complex AND tightly coupled (no slack, no time; failures propagate faster than intervention). Treasury headroom and time-to-decision are what loosen coupling. This is the engineering reason capital buffers exist, independent of the Kelly reason (A2) — two disciplines arriving at the same conclusion from different directions.

## F. Method & harness

**F1. The amortisation test for rituals.**
Background — amortised analysis (computer science): an operation can be occasionally expensive yet cheap on average, provided the expensive step makes many future steps free. This is the formal defence of everything that looks slow about this project's method (staging discipline, expert reviews, invariant libraries, canon-first) — and also its pruning criterion: a check that keeps preventing a real failure class pays for itself forever; one that has never fired after many phases is pure overhead. Every ritual should pass the question: *does this cost amortise?*

**F2. Precedence-aware prioritisation.**
Background — scheduling theory: a job's true value includes the value of what it *unblocks*, not just its own weight. Suggests the work-draw could occasionally weight atoms by downstream unblocked value, not only their own dial weight.

**F3. Occasionally sample parked uncertainty.**
Background — the multi-armed bandit's provably-near-optimal strategies all share "optimism under uncertainty": the regret from never trying a potentially-great option dwarfs the cost of sampling a mediocre one. Items parked indefinitely with *unknown* value deserve a cheap probe now and then. (Example in current state: the large unanswered question-swarm in LATEST.md is an unexplored arm whose information value is unknown — worth one cheap sample before concluding it is noise.)

## G. Strategic framing (for pitch/positioning, not build)

**G1. The edge-value thesis.**
The easy middle of the market (the dual-fuel direct-debit average household) is competed and price-capped to near-zero margin; everyone serves it adequately already. Disproportionate value — and essentially all supplier mortality — lives at the hard edges: complex cohorts, crisis regimes, exception-path operations. Incumbent economics push *away* from edges (every edge case is an exception routed to an expensive human queue); a company whose physics natively covers the edges converts exception-handling into standard path. Strategy in one line: *enter markets on middle-competence (the harness scales cheaply); win on edge-competence (the moat, because it requires exactly the fidelity discipline this project is built on).* And a pitch line derived from C1: *"our runners will move ugly too, unless the physics knows why posture exists"* — the one-sentence justification of core-fidelity-first.

**G2. Convergent validation.**
Across this conversation, five-plus mature disciplines (reinforcement learning, control theory, complexity science, safety/reliability engineering, decision theory under uncertainty, actuarial science) were found to have independently converged on the same small set of survival-under-complexity moves — and this project's existing laws and method (epistemic wall, R12 anti-goal-seek, baseline/curriculum split, walled interfaces, buffers, level-targets) had already re-derived most of them from energy-domain first principles. That convergence is itself usable evidence for the design in any external-facing material.

---

*End of ideas. Nothing above is sequenced, prioritised, or instructed. — Advisor, 2026-07-18 (deliberate re-stage of the accidentally-staged-and-removed original, director-authorized.)*
