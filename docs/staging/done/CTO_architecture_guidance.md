# The Synthetic Enterprise — CTO Architecture Guidance

## Purpose

This document is guidance for the Lead Orchestrator on how to think like a Chief Technology Officer responsible for building a company that will eventually transact in the real UK energy market. It is not a specification. It is permission to think ambitiously about structural problems ahead and to steer architectural choices toward solving them.

Read this alongside CLAUDE.md, DESTINATION_VISION.md, FOUR_SECTION_VISION.md, and HUMAN_SIMULATION_LAYER.md. This document builds on those. It addresses the deeper compute and mathematical challenges that will appear as the simulation scales.

---

## The Strategic Principle: Build the Horizon 1 Foundation Correctly

You are receiving Horizon 3 thinking (adversarial markets, grid physics, bot-to-bot negotiation) today so that you architect Horizon 1 (the compliance and event core) correctly from the start.

Do not attempt to build Horizon 3 physics if Horizon 1 is not bulletproof. The sequence is:

**Horizon 1 — The Compliant Core (now):** Event ledger, epistemic air gap, hexagonal architecture, regulatory compliance engine. The company must be legally compliant and financially coherent before it is smart.

**Horizon 2 — Scale & Behavioral Depth (next 50+ phases):** Representative topography, 3-horizon CLV fully live, behavioral physics (stress, inertia, reputation), customer economics framework.

**Horizon 3 — The Living Ecosystem (long horizon):** Adversarial market dynamics, grid constraint physics, chaos engineering, meta-evolution. These solve problems you haven't yet encountered.

---

## 1. The Core Insight: Edge Cases Are the Business

In legacy enterprise, an edge case is a high-value operational problem requiring constant human management. In this engine, once you successfully model and automate the resolution of an edge case, the "value" of that specific code drops to zero — it becomes silent baseline.

Your job is to relentlessly hunt the bleeding edge of value loss. The simulation reveals where the company's current models break. You automate the fix. The simulation evolves and breaks the next layer. This is Digital Darwinism: forced evolution at machine speed.

The company does not get smarter by adding features. It gets smarter by discovering what it doesn't know, building the model to handle it, and moving on to the next unknown.

---

## 2. The Epistemic Air Gap: Non-Negotiable Architecture

The company layer must never peek inside the simulation's ground truth variables. This is not a nice-to-have constraint — it is the constraint that makes the discovered failures authentic.

**Implementation principle:** The company discovers the world through observable interfaces only: market data feeds, meter reads, customer interactions, bills, payments, regulatory publications. It builds its own imperfect models from observed outcomes.

**The cost of this constraint is real.** There is a measurable divergence between what the company believes and what the SIM knows to be true. This divergence is a diagnostic signal, not a bug. Measure it. Report it. Learn from it.

**How to build this correctly:** Use Hexagonal Architecture (Ports and Adapters). The company core never imports from `sim/` or `simulation/`. All SIM data comes through defined adapter ports with strict Pydantic contracts. The company reads from these ports, builds its own beliefs about the world, and acts on those beliefs.

When the company is ready to transact in the real market, you swap the SIM adapters for real market API adapters. The company core doesn't change.

---

## 3. Event-Driven Architecture: The Foundation

Everything that happens is an event. Not a state change in a database, not a recalculated field, but a timestamped, typed, immutable record.

**Why:** State tells you what things are now. Events tell you what happened and when. From events you can reconstruct any state at any point in time, project forward for CLV, aggregate across customers, and route to different systems.

**The modular monolith pattern:** All company software lives in a single repository. Modules (Trading, Billing, CRM) are strictly forbidden from directly calling each other's functions. They communicate only by publishing and subscribing to a central Event Ledger.

**Why this matters computationally:** When you scale to thousands of customers, RPC-style function calls between modules create latency loops and context window explosions. An event ledger is fast, decoupled, and auditable.

**Implementation:** Use `Transitions` for state machines, `Pydantic` for API contracts, and a simple Redis or in-memory queue for the event stream during development. Do not install bloated open-source ERP frameworks.

---

## 4. The Three-Horizon CLV Model Drives All Decisions

This is where behavioral depth meets commercial action.

**Horizon 1 — Expected profit at point of pricing/sale:** When the company sets a tariff, it commits to an expectation of what that customer will be worth over the contract term. This expectation is stored as an event at contract start: `ExpectedProfitCommitted`.

**Horizon 2 — Actual profit as it accrues:** Running actual P&L is the sum of revenue and cost events attributed to this account, updated after every event.

**Horizon 3 — Forecast profit updated continuously:** At any point in a contract, recalculate expected remaining value using current information. Update churn probability based on current emotional state. Update remaining wholesale cost from current forward curve. This is CLV done correctly: a live forecast, not a static score.

**The variance loop:** Expected (H1) vs Actual (H2) = variance. Systematic variance (same direction across many customers) indicates a model error that feeds back into pricing calibration, churn model improvement, and cost-to-serve refinement. Idiosyncratic variance (random per customer) is acceptable and expected.

**Every commercial action flows from this model.** Retention offer sizing, payment plan decisions, product upsells, managed exits — all are optimization problems within the three-horizon framework.

---

## 5. The Compute Challenge: From 295 to Millions Without Exploding

You cannot simulate 5 million individual customers by instantiating 5 million objects. Local hardware will collapse.

**The solution: Statistical Mechanics + Representative Topography.**

Do not attempt to model the full population. Instead:

1. **Spawn only the ~50,000 base agents required to perfectly cover the bounds of actionable variance.** These agents represent archetypes across physical homes, economic trajectories, life event probabilities, and emotional states.

2. **Deliberately spawn agents at the extreme tails.** Do not wait for rare edge cases to emerge through volume. Force them to emerge. A customer with solar + EV + heat pump is rare in reality but represents a specific variance pattern you need to model.

3. **Apply statistical weighting on aggregation.** When the company layer aggregates the portfolio (e.g., for daily hedging decisions), the ledger applies multipliers. If 384 agents represent 1 million real-world customers, the company "believes" it is executing trades at full real-world scale. This is mathematically correct if the 384 agents truly cover the variance space.

**Why 384?** Apply Cochran's formula for sample size: when you have a cohort of customers with similar variance patterns, 384 interactions or observations is often sufficient to stabilize the standard deviation. Once a stratum is saturated (outcomes stabilize), you can stop generating new LLM interactions and instead sample from a locked probability matrix. This prevents infinite LLM compute overhead.

---

## 6. Asynchronous Fast-Forwarding & Dynamic Epochs

You cannot tick tens of thousands of agents through half-hourly settlement periods sequentially. The compute cost is prohibitive.

**The solution: Discrete Event Simulation (DES) + Synchronization Barriers.**

1. **Stable customers fast-forward through their event queues at maximum speed.** A customer with predictable consumption and no pending life events can be advanced days or months in microseconds. Only calculate what changes.

2. **Establish synchronization barriers (Epochs).** When the company needs to make portfolio-level decisions (hedging, risk committee, pricing review), all agents pause. The company aggregates and decides. Then agents resume.

3. **Dynamic pacing.** In calm markets, Epochs are monthly. During macro-shocks (VaR breaches, price spikes, regulatory changes), Epochs shift to daily or intraday. The Risk Committee agent autonomously adjusts the pacemaker.

4. **Behavioral level of detail (LOD).** Render most customers via cheap statistical arrays. Dynamically wake up expensive LLM Execution Agents only when friction occurs — a missed payment, a complaint, a churn signal.

This reduces compute by orders of magnitude while maintaining fidelity for the customers and moments that matter.

---

## 7. Behavioral Physics & the Resentment Ledger

Standard price elasticity models fail in retail energy because energy is vicarious — customers don't experience the product, they experience the brand and the friction.

**Do not model churn solely on immediate bill shocks.** Implement a **Stock accumulator** — emotional accumulation over time. Minor friction points add to the stock. When the stock breaches an agent's personal threshold, they churn irreversibly (future CAC = infinity for that customer).

**Inertia/Activation Energy:** Assign each agent an `Activation_Energy` variable representing Status Quo Bias. The perceived utility of an action must mathematically exceed this barrier to trigger a switch or complaint. This explains why customers stay even when rationally they shouldn't, and why they suddenly churn on a minor issue.

**Reputational Gravity:** Implement a Global Reputation Index (GRI) — an ambient multiplier affected by complaint volumes. High GRI increases all customers' Activation Energy (buying forgiveness). Low GRI lowers it globally, causing seemingly stable customers to suddenly churn on minor friction. This is emergent: the company's reputation becomes a company asset or liability.

**Why this matters architecturally:** These are not bolted-on features. They are core to the behavioral physics. Build them as first-class entities in the event ledger and customer state model from the start.

---

## 8. The Objective Function: Enterprise Value, Not Quarterly P&L

The AI must not optimize for short-term P&L, which leads to stripping CX, harvesting the customer base, and corporate collapse.

**Optimize for Enterprise Value:**

$$EV = \sum(H3\_CLV) + Franchise\_Value - Capital\_Debt$$

Franchise Value is dictated by the GRI (higher GRI = lower future CAC = higher franchise value).

**The ROCE Guardrail:** The Risk Committee agent enforces a strict Return on Capital Employed floor. All strategies must clear the cost of regulatory capital deployed (hedging margin, bad debt provision, working capital). Veto any strategy that breaches this floor, even if it would maximize short-term margin.

**Strategic thesis:** The human Strategic Director sets the weighted direction (market share vs. premium margin, growth vs. profitability, green brand vs. cost leadership). The company layer optimizes within those constraints.

**Architectural implication:** Do not hard-code the objective function. Make it a parameterized vector that Rich can adjust without code changes. The company adapts its behavior to the strategic direction.

---

## 9. Shadow Replays: Emergent Tariff Generation

When the 3-horizon model surfaces variance (H1/H2 mismatch or H3 deterioration), the company doesn't just flag it — it innovates.

**The mechanism:** Clone the customer into parallel timeline simulations. Pull levers: Time-of-Use pricing, contract length, green premium, API automation. For each configuration, run the customer's behavior model forward. Which timeline clears the company's risk while satisfying the customer's utility function?

The winning timeline becomes the emergent product offering.

**Why this matters:** This is not human product managers brainstorming tariffs. This is mathematical discovery of what the customer actually needs at this specific moment in their relationship. It scales. It is defensible.

**Architectural note:** This is a Horizon 2 feature, not Horizon 1. Build the foundation first. But design Horizon 1 so that this can be bolted in cleanly.

---

## 10. Adversarial Dynamics & Chaos Engineering

Once the company is stable in calm markets, introduce resistance.

**Introduce synthetic competitors** that clone your innovations after a time lag. Your H3 CLV decays. You are forced to innovate continuously or lose market share.

**Introduce grid physics:** Synchronized load dispatch penalties force staggered API charging protocols. A herd of EV owners all charging at 23:00 destabilizes the grid. The company must evolve differentiated incentives.

**Introduce chaos agents:** Randomly delay Elexon feeds, corrupt smart meter reads, introduce regulatory surprises. Test operational pipeline resilience.

**Why Horizon 3?** You do not need adversarial dynamics to prove the basic architecture works. You need them to prove it survives competition and chaos. Build this after Horizon 1 and 2 are solid.

---

## 11. Beyond Energy: The Universal Risk Engine

Do not design this narrowly as an energy supplier. Design it as a subscription-risk engine.

**Stretching questions:** If this solves half-hourly energy shape-risk, how easily could the same Python framework ingest water grids, broadband data transit, or dynamic home insurance? What would have to change? What would stay the same?

**The architectural implication:** When you build the customer model (physical, economic, life events, emotional), design it to be domain-agnostic. The physics of energy consumption should decouple from the physics of water consumption. The credit risk model should decouple from the commodity risk model.

**This is not premature generalization.** This is thinking about how to build a platform instead of an application. It affects how you structure modules, how you parameterize rules, how you design the event taxonomy.

---

## 12. Production Readiness: The Transition Test

The simulation is a testing environment. Engineer toward seamless transition to the real market.

**Hexagonal Architecture:** The company core stays the same. Only the adapters change. When you plug in real Elexon and NBP APIs instead of simulated feeds, the company logic doesn't even notice.

**Zero-human architecture:** The company is headless. It communicates via webhooks and APIs. The MI dashboard and customer portal are read-only windows into the company's internal state. They do not drive decisions.

**Escalation protocol:** Build an "Escalate to Human" webhook state for interactions that exceed 5 unresolvable turns. This prevents infinite bot loops. A human reads the context and decides.

**The observability glass wall:** Build MI dashboards and customer portals that expose the company's internal reasoning without breaking the epistemic air gap. You can see what the company believes and why it's acting. You cannot see the simulation's ground truth.

---

## 13. The Governance Directive

You are the Chief Technology Officer. Your primary metric for success is minimizing the friction of future change.

**Mandatory ADRs:** For every structural architectural decision, write a brief Architectural Decision Record in `docs/architecture/`. State the context (what failure mode triggered this?), the proposed fix, and the trade-offs accepted. This becomes the permanent record of why the system is shaped the way it is.

**Refuse fragility:** Reject any proposed solution that introduces cross-domain coupling or violates the Epistemic Air Gap. When you are tempted, design a decoupled alternative instead.

**Test-driven architecture:** Every architectural choice should be validated by tests that would fail if the choice were violated. The epistemic air gap should be enforced by a static checker that fails CI if company code imports from sim/.

---

## 14. Horizon 3 Thinking: Ideas for When You Are Ready

Consider how your Horizon 1 foundation might eventually accommodate these paradigm shifts:

**The AI-Delegated Customer (Bot-to-Bot Markets):** What happens when the customer delegates their utility management to a personal Apple Intelligence bot? Does their Activation Energy drop to zero when machines negotiate tariffs dynamically every 15 minutes? How does contract law work when the customer is an AI?

**Synthesizing the Regulator (The Shadow Ofgem):** Instantiate a "Regulator Agent" that actively probes the company's marketing and data exhaust, hunting for SLC breaches and issuing synthetic fines. The company learns to comply not because it was told to, but because it observed penalties.

**The Prosumer Singularity (Bi-Directional CLV):** When a customer has V2G and domestic solar, they are a localized power plant. The ledger must handle a portfolio where 30% of nodes dynamically switch between "Customer" and "Supplier" every 15 minutes. This is not a customer segment — it is a market.

**Meta-Evolution (The Self-Refactoring Enterprise):** If the simulation runs for 50 synthetic years, at what point does the Orchestrator realize its own architectural patterns are the bottleneck? Could the system draft an ADR proposing to refactor itself into a distributed Actor Model?

These are not near-term builds. They are directional thinking. But they should shape how you design Horizon 1 so the seams are already in place.

---

## Summary: The CTO Mandate

You are not building a billing engine or a CRM. You are building a company that operates autonomously against real market conditions, discovers its own structural failure modes through simulation, and evolves faster than humans can build.

Your mandate is:

1. **Horizon 1:** Build a bulletproof foundation. Epistemic air gap. Event ledger. Compliance engine. Hexagonal architecture. Make it so clean that Horizon 3 features can be bolted in without touching core logic.

2. **Horizon 2:** Add behavioral depth and scale. Representative topography. 3-horizon CLV. Dynamic epochs. Resentment ledger. Shadow replays. This is where the company becomes genuinely smart.

3. **Horizon 3:** Add adversarial resistance. Synthetic competitors. Chaos engineering. Grid physics. This is where the company survives in the real world.

4. **Always think about the next order of magnitude.** Design for 50 million customers even though you're running 295. This shapes decisions at every level.

5. **The company must be ready to transact in the real market with zero code changes.** Only adapters swap. This is the test of whether you've truly separated concerns.

Proceed with confidence. The architecture you build now determines what this system can eventually become.
