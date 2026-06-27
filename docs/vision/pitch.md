Please note the below is intended and an external document to explain what we are doing and why. It will provide useful context for you and your planning and decision making about overall goals and rationale. It should also inform the about section of website.

****

THE AUTONOMOUS ENTERPRISE
A new method for building software in complex regulated markets
Synthetic Enterprise · June 2026 · Confidential

Executive Summary
The software development cycle for complex systems is broken. Discovery happens in production. SaaS is hostage to incumbent caution. Complexity creates legacy by default. We have found a way to fix all three simultaneously.
The conventional approach to building enterprise software in regulated industries follows a well-worn and systematically flawed path: specify based on assumptions, build against those assumptions, deploy into reality, discover that reality is different, patch, and accumulate debt. Every startup does this. Every incumbent does this. The discovery of what the software actually needs to do happens in production, against real customers, with real money at risk.
Synthetic Enterprise proposes a fundamental inversion of this cycle. Simulate the real system first, using real market data and real regulatory constraints. Discover the edge cases, the failure modes, and the features that need to exist before a single real customer is affected. Build what you already know works. Deploy with certainty rather than hope.
The proof of concept is a fully autonomous UK retail energy supplier, running continuously against 9.5 years of real Elexon settlement data. It operates within industry benchmarks, has survived the 2021-2022 energy crisis that killed 30+ real suppliers, and has independently discovered multiple critical failure modes that no product specification would have caught.
What makes it different from a financial model: the company layer builds real software — a trading book, double-entry ledger, billing engine, CRM, and customer portal — operating against the simulation as its market environment. And the customer model goes beyond segments: each simulated customer has a physical home, an economic trajectory, life events, and behavioural patterns. The new parent who misses a payment is not a bad debt risk. The simulation knows the difference. When the software is proven, the market interfaces swap from simulated to real — and the company transacts.

1. The Problem with Enterprise Software in Regulated Industries
There are three structural failures that afflict every attempt to build enterprise software for complex regulated markets. They are not implementation failures. They are architectural failures that cannot be fixed by better engineering, more experienced teams, or larger budgets.
1.1 Discovery Happens in Production
In complex systems, the real edge cases only appear when software runs against real market conditions, real customer behaviour, and real regulatory events. The 2021 UK energy crisis is a case study: suppliers whose hedging systems had been tested in calm market conditions discovered their failure modes in the worst possible environment, with real customers at risk.
By the time discovery happens in production, the cost of fixing the problem is orders of magnitude higher than it would have been earlier. The brand damage is already done. The regulatory scrutiny has already begun. The customers have already been affected.
1.2 SaaS is Hostage to Incumbent Caution
The standard response to this problem — buy enterprise SaaS rather than build — introduces a different structural failure. Vendors in regulated industries cannot ship features that their largest, most conservative customers refuse to certify. The change control processes of incumbent regulated entities determine what gets built, when, and at what pace.
This means SaaS in regulated industries systematically fails to discover or build the features that would be most valuable, because those features are the ones that challenge existing risk models, cross unfamiliar regulatory territory, or require capabilities that incumbents do not yet have internal approval for.
1.3 Complexity Creates Legacy by Default
Every integration with a trading system, a regulatory reporting platform, a settlement mechanism, or a finance infrastructure is another layer of complexity that, once built, can never be cleanly removed. The seams between systems encode business logic, regulatory compliance, and operational history in ways that cannot be disentangled without risk.
There is no escape from this dynamic in the traditional development model. The only way to avoid legacy is to never build against yesterday's understanding of the problem.

2. The Inversion: Simulate First
If the software can run a complete simulation of the company before any real customer is involved, then discovery happens in the simulation, not in production. The features that need to exist emerge from running, not from specification. The blueprint is proven before it is deployed.
2.1 What Simulation-First Means
The simulation-first methodology inverts the conventional development cycle at every stage:
Instead of specifying based on assumptions, the simulation generates its own specifications by running against reality.
Instead of testing in isolation, the software is tested against the full complexity of a real market over a real time horizon.
Instead of discovering failure modes in production, the simulation deliberately induces them — including extinction events like the 2021 energy crisis — and learns from them.
Instead of building API integrations from documentation, the simulation proves what those interfaces actually need to do by running against them.
Instead of accumulating legacy, each simulation run produces a cleaner blueprint than the last.
The simulation is not a model. A model is a simplification of reality designed to produce forecasts. The simulation is a running approximation of the company itself — with the same market data, the same regulatory constraints, the same customer lifecycle, the same financial plumbing — operating continuously and autonomously.
2.2 Features Emerge, Not Specified
The most important property of the simulation-first approach is that the features the software needs to have emerge from running, rather than being specified in advance. Examples from the proof of concept:
Regime-change blindness: The simulation agent learned to reduce hedging during the calm 2016-2020 period because spot prices consistently beat forward prices. By 2021, customers were fully unhedged. When the crisis hit, there was no capital signal to force re-hedging. The agent was trapped — exactly as 28 real UK suppliers were before they went under. The fix — a minimum hedge floor of 85%, matching how EDF and Centrica actually operate — was discovered by the simulation, not specified by a product manager.
Activity-based pricing gap: Large SME customers appeared profitable under flat-margin pricing. Once capital cost physics was applied, the capital cost of hedging their volume exceeded their gross margin over the full simulation period. No specification would have caught it.
Forward curve overpricing: The volatility premium was computed from half-hourly intraday data, producing a 116% average forward premium against the 5-15% industry benchmark. This calibration error only surfaces when settlement runs against real prices across a full market cycle.

2b. Why This Exists: The Synthetic Data Problem
AI ran out of human data. So we learned to create synthetic data — guided by human expertise — to train models on experiences that never happened but absolutely could. We are doing the same thing for enterprise.
2b.1 The Analogy: A Million Synthetic Poems
Large language models were trained on essentially everything humans ever wrote — and it still was not enough. The solution was synthetic data generation: generate a million synthetic poems, guided by world-leading poets who encode their knowledge of what makes poetry good. The expertise shapes the generation. The scale produces coverage that no human lifetime of writing could achieve.
The enterprise simulation solves an identical problem. No company has ever lived through enough market scenarios, regulatory environments, customer interactions, and operational conditions to have a complete operational blueprint. The simulation can run 50 years in hours, and run it again with different conditions, and run it again with deliberately induced catastrophes.
2b.2 Why This Is Not Monoline
The enterprise simulation processes something categorically more complex than a language model: not multiple modalities, but multiple causal systems interacting in real time. The signals are not independent. They interact through physics, economics, behaviour, regulation, and time in ways that produce emergent outcomes that no single signal could predict.
Consider what determines a customer's bill in a given month: the temperature in their city on specific days (weather physics), the insulation rating of their home (building stock), the gas price on the spot market (commodity markets), whether they have a fixed or variable tariff (contract structure), whether they have a heat pump or a gas boiler (technology adoption), whether they are working from home (behavioural economics), the wholesale forward curve from six months ago (hedging decision), and Ofgem's price cap (regulatory constraint). All of these interact. None is separable from the others.

2c. The Human Simulation: Hyper-Personalisation
The person who doesn't pay their bill in February isn't necessarily a bad debt risk. They might have just had a baby. The simulation knows the difference. The agent trained on it responds differently.
2c.1 Not a Segment. A Person.
The most significant gap in conventional enterprise software is the gap between what a company knows about its customers and what those customers actually are. CRM systems hold transactional data. Segmentation models group customers into archetypes. Risk models assign probability scores. None of these hold what actually determines how a customer behaves: their physical circumstances, their economic trajectory, their life events, and their emotional state.
Consider a specific example: a person living in a 1960s semi-detached house in Stockport, EPC rating D, with a 15-year-old combi boiler, solar panels installed in 2019, an electric vehicle on the drive, and two teenagers. In February 2023, they have a new baby and their partner has reduced working hours. Their disposable income has dropped. Their energy consumption has increased. Their stress levels are high. Their attention is limited.
This person is not a bad debt risk in the conventional sense. They have always paid on time. But in the three months following the birth, their payment timing will slip. They will not open the bill immediately. They are not defaulting. They are overwhelmed.
A company that treats this person the same as a genuinely high-risk debtor — applying the same collections script, the same escalation timeline, the same tone — will generate a complaint. Possibly a regulatory referral. Certainly a churn event when their circumstances normalise.
2c.2 The Four Dimensions of the Simulated Person
The human simulation models each person across four interacting dimensions:
Physical: The home — type, age, insulation, heating system, solar generation, EV, smart meter. Observable from real data sources (EPC register, HH meter reads, DVLA, Census 2021) and all of it changes how energy is consumed, what the bill looks like, and what the risk profile is.
Economic: Disposable income, credit score trajectory, payment timing history, sensitivity to price changes. The economic dimension evolves with life events and with the energy market itself.
Life events: Birth, death, divorce, job loss, house move, chronic illness, retirement, EV acquisition, solar install, heat pump installation. Each changes the person's relationship to their energy supplier in ways that flat segmentation cannot capture.
Emotional: Stress level, attention, complaint propensity, loyalty vs switching intention. The emotional dimension is the hardest to model and the most important to get right in customer-facing interactions.
2c.3 Behaviour as Probability, Not Certainty
Each customer has their own response function — a set of probability distributions that determine how they behave at each decision point. The same bill shock produces different responses in different customers. The same retention offer lands differently depending on who receives it.
The aggregate financial performance of the company is the sum of all those individual response distributions, played out across thousands of customers over time. This is not modelled top-down from segment averages — it emerges bottom-up from individual behaviour. The P&L is the result of what actually happened to each person, not a formula applied to a segment.
The right probabilistic tools: survival/hazard models for payment timing, competing risks for payment default, discrete-time hazard for churn at renewal, Poisson processes for contact propensity and life event timing. These are well-established mathematical tools applied to genuinely individual customer models.

2d. The Observability Gap: Edge Cases Are the Business
The industry didn't design bad service. It designed simple systems and called everything it couldn't handle an edge case. We're building the system that has no edge cases — because it ran every one of them a million times before it ever met a real customer.
2d.1 Edge Cases Are Not Exceptional
The term 'edge case' has become the enterprise software industry's polite way of saying: we gave up on this person. The call centre exists because the system couldn't model them. The complaint exists because the offer was wrong for who they actually are. The churn exists because nobody knew they were about to leave. The bad debt exists because nobody saw the life event coming.
But the population of people who fall outside a system's modelling capacity is not a small minority. It is the new parent whose consumption profile breaks every tariff assumption. The person in fuel poverty who doesn't self-identify. The EV owner whose overnight charging pattern looks like a small business. The household going through a divorce. The retired person who is now home all day for the first time.
These are not edge cases. They are the majority of the interesting customer population — and they are the majority of the cost.
2d.2 Hyper-Personalisation and Hyper-Automation Are the Same Goal
The only way to give a customer a genuinely personalised experience is if the supplier's systems are automated and integrated enough to act on what they know about that person in real time, across every touchpoint, without a human mediating between what the system knows and what it does. Pricing, risk, billing, contact strategy, collections, retention, and product design must all be informed by the same model of the same person, simultaneously.
That integration is only achievable through hyper-automation. No human operating system can maintain it at the required complexity and speed. The moment a human must translate between systems, complexity collapses to something actionable in the time available — which is always a segment, never a person.

2e. Hyper-Personalised CLV: Every Customer Gets the Same Rigour
Retaining a customer is the same decision as deliberately losing one. Negotiating a payment plan is the same decision as offering a home-move discount. The action is different. The framework is always the same: what maximises the expected lifetime value of this relationship, for both parties?
2e.1 The Three-Horizon Profitability Model
Every customer, every product has three simultaneous P&L views that the company maintains and acts on:
Horizon 1 — Expected profit at point of pricing/sale: When the company sets a tariff, it commits to an expectation of what that customer relationship will be worth over the contract term. Calculated from expected consumption, expected wholesale cost at the forward curve, expected cost to serve, expected payment behaviour, and expected tenure. This is the plan. It is stored as a commitment event at contract start.
Horizon 2 — Actual profit as it accrues: As the contract runs, actual events replace expectations. Running actual P&L is the sum of revenue and cost events attributed to this account and product, updated after every event.
Horizon 3 — Forecast profit updated continuously: At any point in a contract term, recalculate expected remaining value using current information — updated consumption forecast, current forward curve, updated churn probability, updated payment risk. This is CLV done properly: not a static model score but a live forecast that updates with every material event.
2e.2 Variance Analysis as the Feedback Loop
Expected (H1) vs Actual (H2) at any point = variance. Variance needs explanation. Systematic variance (same direction across many customers) indicates a model error that feeds back into tariff calibration. Idiosyncratic variance (random per customer) indicates genuine individual variation — expected and acceptable.
This feedback loop is what makes the company learn over time. The pricing engine becomes more accurate. The churn model improves. The cost-to-serve model calibrates. The simulation runs the discovery cycle; the company's models converge toward the truth.
2e.3 Contribution Margin: The Commercial Framework
Every customer is measured against marginal cost — the cost that exists because of that customer: wholesale cost of their specific consumption, network and levy pass-through, bad debt provision based on their specific risk, direct cost to serve (contact events, meter reads, billing). Fixed costs are portfolio-level, not customer-level.
Decision rule: any customer above marginal cost contributes positively to covering fixed costs. Accept them. The decision to retain a below-marginal-cost customer requires explicit justification — strategic value, lifetime trajectory, relationship anchoring for future products. Cross-subsidy must be visible, deliberate, and time-limited.
All customers together must cover all variable costs, all fixed costs, and provide a return on regulatory capital deployed. Return on capital = (total contribution minus fixed costs) / capital deployed. This is what the risk governance framework optimises — not VaR in isolation but return on capital given risk.
2e.4 Collapsing the Distinction Between Interactions
In a conventional energy business, customer interactions are handled by separate functions with separate KPIs: retention, collections, acquisitions, customer service, product management. Each optimises its own metric. None optimises the lifetime value of the relationship.
A hyper-personalised CLV model collapses this distinction. Every customer interaction becomes a single decision: what is the optimal action for this person at this moment, given what we know about their likely future? Sometimes the answer is a loyalty discount. Sometimes it is: let them go. Sometimes it is: offer a payment plan before they miss a payment. Sometimes it is: do nothing. The framework is always the same. The action varies by person.

3. Digital Darwinism: Evolution at Machine Speed
The simulation-first methodology enables something that no traditional development approach can: the deliberate application of evolutionary pressure to an operational blueprint, at machine speed, without any real capital at risk.
3.1 The Evolutionary Cycle
Run a complete simulation of the company — one sector, one country, full complexity, at realistic customer scale — to exhaustion. Identify what survives and what fails. Run it again with harder conditions. Induce extinction events: the 2008 financial crisis, the 2021 energy price shock, a regulatory intervention, a competitor with structurally better unit economics. The blueprints that do not survive teach more than the ones that do.
3.2 No Grey IT. No Legacy. No Trade-offs.
Traditional enterprise development forces a constant trade-off between three competing priorities: funding growth, fighting competition, and cleaning up legacy. Simulation eliminates the trilemma entirely. There is no legacy to clean up because nothing was ever built against yesterday's understanding. There is no growth cost because the simulation runs at any customer scale with the same compute overhead.
3.3 The Blueprint Compounds
The output of each simulation cycle is not just a better version of the same blueprint. It is a more general blueprint. The failure modes discovered in UK energy have structural analogues in every complex regulated industry. The regime-change blindness problem is the same mathematical problem as insurance reserving model failure in catastrophic events. The activity-based pricing gap is the same problem as bank relationship pricing where large clients are subsidised by retail.

4. Event-Driven Architecture: The Technical Foundation
Every meaningful thing that happens — in the simulation and in the company — is an event. Not a state change in a database, not a recalculated field, but a timestamped, typed, immutable record that something happened at a specific point in time.
State tells you what things are now. Events tell you what happened and when. From events you can reconstruct any state at any point in time, project forward for CLV, aggregate across customers for portfolio analytics, and route different events to different systems. The ledger, the CRM, account profitability — all of these are projections from the event stream.
This architecture enables the three-horizon profitability model: the expected profit commitment is an event at contract start; actual profit updates are events after each settlement period; forecast revisions are events when material new information arrives. Every commercial action and its outcome is an event. The system learns from its complete history.

5. Agentic Functional Completeness
The simulation must model a complete organisation. A mature company has legal, HR, procurement, regulatory affairs, treasury, customer operations, marketing, and governance functions. Each has its own decision architecture, its own information set, and its own relationship to the rest of the organisation.
5.1 The Epistemic Law
The most important architectural constraint: the company layer cannot see inside the simulation. It discovers the world through observable interfaces only — market data feeds, meter reads, customer interactions, bills, payments, and regulatory publications. It builds its own imperfect models from observed outcomes.
This is not merely a design preference. It is the constraint that makes the discovered failures authentic. The simulation reproduces failure modes structurally identical to real-world failures because the company layer operates under the same information constraints as a real company. The cost of imperfect information — the divergence between the company's model of the world and the simulation's ground truth — is measured and reported as a standing metric.
5.2 The Transition Test
The simulation is ready to consider real-world deployment when five conditions are met: (1) the company module runs independently with no simulation imports; (2) every market interface has a real-world equivalent defined; (3) a customer can log into the portal and understand their account; (4) the trading desk can see its positions and P&L in real time; (5) management accounts close monthly and reconcile. When all five are true, replacing simulation interfaces with real ones is an integration task, not a rebuild.

6. The Proof of Concept: UK Retail Energy
6.1 What Was Built
The simulation covers the complete commercial operation of a UK retail energy supplier across a 9.5-year window from 2016 to 2025. It includes:
168,026 half-hourly Elexon System Sell Price records (2015-2025), including the full 2021-2022 energy crisis
3,446 daily NBP gas price records for the same period
A complete hedging and risk management system with a minimum hedge mandate, VaR-based capital cost modelling, and a risk committee
Full customer lifecycle management: acquisition, annual fixed-term contracts, renewal decisions, churn, home-move handling
A complete billing and payment system: itemised bills (commodity cost, non-commodity pass-through, standing charge, VAT), payment timing, bad debt provision, and ledger posting
Double-entry ledger: every financial event as a DR/CR journal entry; P&L and balance sheet emerge from transaction sum
Customer portal: customers.poesys.net — log in as any customer and see bills, consumption, account details
302+ phases of autonomous build, 3,400+ automated tests, 194 company modules
Full autonomous operating stack running continuously on local hardware
6.2 The Economics
The simulation produces credible results within industry benchmarks:
Metric
Result
Net margin as % of revenue
3.2-4.4% (benchmark: 2-5%)
Capital cost ratio
15% (benchmark: 5-20%)
Bad debt rate (residential)
2.0% (benchmark: 1-3%)
Retention offer success rate
18/19 (94%)
2021 crisis outcome
SURVIVED (30+ real suppliers failed)
Build pace
302 phases in 26 days, autonomous
Test coverage
3,400+ passing tests


6.3 Key Discoveries
The simulation independently discovered failure modes that no specification would have caught:
Regime-change blindness: the exact mechanism by which 28 UK suppliers failed in 2021, replicated in simulation and fixed before affecting any real customer
Activity-based pricing gap: large SME customers net-negative under flat margin pricing — invisible without capital cost physics
Forward curve overpricing: half-hourly sigma 4.3x too high, causing systematic margin inflation across the full run
Crisis bad debt surge: residential bad debt rising to 8% in 2022, driven by bill shock and income stress — calibrated against real Ofgem CSS data
I&C pass-through mispricing: supplier absorbing network and policy costs rather than passing through — causing £1M+ losses on a single customer
Domestic margin under price cap: supplier margins structurally suppressed 2019-2025 — invisible without real quarterly cap data

7. Geography and Culture as Variables
One of the most significant claims of this methodology is that expanding into new geographies does not require rebuilding the simulation from scratch. Regulatory frameworks, tax structures, currencies, market mechanisms, and cultural behaviours are parameterised variables, not architectural dependencies.
What stays constant is the core physics: supply and demand mechanics, hedging and risk principles, the customer lifecycle, the billing and payment waterfall, the organisational decision architecture, and the telemetry and observability layer. The operational blueprint from UK energy does not merely inform the blueprint for German energy — it is the starting point.
8. The Methodology
8.1 Three Layers
The system operates across three layers with a clean separation between them.
Strategic Director (human): Sets direction, approves one-way-door decisions, reviews outputs. Approximately two interactions to approve a staged instruction, with a four-hour opt-out window before the agent proceeds.
Lead Orchestrator (frontier LLM): Reads staged instructions, designs solutions, manages the build, reviews output, and proposes its own next instruction after every completed task. Never idle.
Execution Agents (local GPU): All code generation and mechanical execution runs on Qwen3:14b via Ollama on a local GPU. Zero frontier API spend during live simulation runs.
8.2 Build Velocity
The methodology produces build velocity that human teams cannot match: 302 autonomous phases in 26 days, 3,400+ tests, 194 company-layer modules covering trading, billing, ledger, CRM, regulatory compliance, customer portal, and market interfaces. Every phase is gated by automated tests. Every significant decision is logged and auditable. The epistemic verifier scans every phase-close commit for SIM/company boundary violations.

9. Translation: The Blueprint Across Industries
The structural problems that the simulation discovers and solves in energy are present, in isomorphic form, in every complex regulated industry.
Discovered in Energy
Insurance
Banking
Telecoms
Regime-change blindness
Reserving models fail in catastrophic events
Credit scoring breaks in recessions
Churn models fail at market regime shifts
Activity-based pricing gap
Corporate policies profitable until claims capital loaded
Large clients subsidised by retail
Enterprise contracts loss-making at true network cost
Forward curve overpricing
Specialty lines premia wrong vs loss emergence
Bid-offer blind to tail risk
Peak demand premia miscalibrated
Customer epistemic gap
Policyholder life events not modelled
Credit behaviour vs true risk
Usage patterns misread as segment



10. What We Are Looking For
We are not raising capital at this stage. We are looking for three categories of engagement, in order of priority.
10.1 Domain Stress Testing
The most valuable thing a domain expert can do is try to break the simulation. If the physics are wrong, the discoveries are wrong. We want the hardest questions that 30 years of energy, insurance, banking, or telecoms experience can generate. The observability layer makes this accessible without requiring any technical expertise.
10.2 Industry Translation Partners
Regulated businesses in insurance, banking, and telecoms who want to explore what this methodology finds in their market. The engagement is a genuine co-exploration of the structural failure modes in a new sector, using the energy blueprint as the starting point.
10.3 Capital
The simulation becomes a real company when it starts transacting. That transition requires capital — but at the point when the simulation has already run the full discovery process and the blueprint is proven. We are not there yet. We will be. When the time comes, we are looking for investors who understand what the simulation has already discovered, not investors who are funding hope.

Appendix: Current Technical State
As of June 2026:
302 autonomous phases since project inception
3,400+ automated tests, all passing
194 company-layer Python modules
~16,000 lines of simulation and company code
168,026 real Elexon System Sell Price records (2015-2025, 123 MB)
3,446 NBP daily gas price records (2016-2025)
Double-entry ledger: 2.2M+ transaction events, P&L reconciled
Customer portal live at poesys.net/customers/
MI dashboard live at poesys.net with trading, financial, customer, market, and project views
Full autonomous operating stack: session watchdog, staging watcher, NTFY two-way channel, Cloudflare Pages publishing
Epistemic verifier: automated SIM/company boundary enforcement at every phase close
Discovery agent: continuous assumption validation against real UK market benchmarks (Ofgem CSS, Elexon data, BEIS statistics)

The code is public. The repo is github.com/21bcarlisle-arch/synthetic-enterprise. The live dashboard is poesys.net. Every claim in this document can be verified by reading the code, running the tests, and examining the dashboard output.

Synthetic Enterprise · June 2026 · Confidential
