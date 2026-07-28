# DIRECTOR-CANON — Poesys PITCH v7 (adopted verbatim, 2026-07-28)

**Status: DIRECTOR-AUTHORED CANON for PURPOSE and ARGUMENT.** Adopted verbatim from
`docs/staging/DIRECTOR_CANON_PITCH_V7_2026-07-28.md`, superseding v6. The pitch body below
is the director's text — **do NOT edit, condense or "correct" it.** Any factual claim that is
stale, overturned or unverifiable is a *finding for the director*, proposed for ruling in
`docs/design/PITCH_V7_RECONCILIATION_2026-07-28.md`, never a self-edit here (including the
known "Draft v5" footer error — retained verbatim, correction proposed in the reconciliation).

**Layer division (coherence ruling):** this document is canon for PURPOSE/ARGUMENT;
`THE_MODEL_ON_A_PAGE.md` is canon for STATE (what exists/is planned); the site derives from
both. Where they disagree that is a finding for the director, not an edit.

*Everything above this line is adoption metadata (not the director's text). Everything below it
is the director's verbatim pitch.*

---

# THE ENTERPRISE SIMULATOR

**Poesys — personal energy at near-zero marginal cost, and the cheapest tonne of carbon left**

*Draft v7 · For review — not yet published*

*Supersedes draft v6. By the Director's decision (28 July 2026), customer money-saving is declared the engine of abatement: bills cut by reducing or time-shifting usage, never by discounting, so the customer's motive and the carbon mission are served by the same action. The customer-savings ledger counts usage-side savings only — price transfers never count. Carbon remains the mission; this decision states why customers will let it happen.*

*v6 note retained: Supersedes draft v5. By the Director's decision (21 July 2026), the venture's purpose is now declared settled — non-commercial, carbon saving as the goal, public domain as the plan — which supersedes the v3-era Board requirement to declare and rank alternative purposes. The other four Board corrections are retained: the regulatory contingency on autonomous supply, future states in the conditional, the volunteer programme coupled to the security posture review, and the mission's status as chosen rather than derived. Durable claims stay in this document; current status lives in the register on the site.*

## In one paragraph

Almost every field that got dramatically better did it the same way: stop building expensive prototypes, simulate them instead. Wind tunnels became computational fluid dynamics. Crash tests became models. Chip design, drug discovery, aerodynamics, motorsport — high-fidelity synthetic data plus serious compute, with only the refined, high-confidence answers built for real. Business never got that. Companies still prototype in production, on real customers, with real money, and pay for the failures in capital, brand and regulatory scrutiny. Poesys is the simulator for an energy company. It lives its whole life against real market data, repeatedly, and takes only proven answers into the real world. It runs to a deliberate budget — limited people, cost, tokens and carbon — because constraint is what forces invention. And that budget is what unlocks the prize. Every company serving millions built one platform and averaged its customers, because software was expensive to write; the average was never what anyone wanted, it was what everyone could afford. When creating software is marginal cost, the average stops being necessary. Every customer gets their own plan, their own cost and carbon path — a bill cut by using less, not by discounting — and a message on the channel they prefer, in the tone that suits the moment. That is the cheapest tonne of CO₂ left in the system. Energy, anywhere — geography is one of the variables we sample, not a market we expand into.

## What this is, plainly

Poesys is an energy company built and operated by AI. The software that runs it — trading, hedging, billing, credit and collections, customer service, regulatory compliance, the monthly accounts — is written, tested, deployed and improved by AI agents working continuously. Human direction is deliberately capped: one person sets the strategy and approves the decisions that genuinely require a human, and does not write code or run the machine.

One thing to be clear about, because it bounds everything. A fully autonomous licensed energy supplier is not something the regulator will permit. Holding a supply licence requires named, accountable human beings, and that will not change because the software got good. The capped-human design is a research condition, not a licensing plan. Whatever operates in a real market will have people accountable for it, and the autonomy will show up as cost, speed and reach rather than as an absence of humans.

It runs today: a company operating continuously against a decade of real UK market data, publishing what it decided and why, and correcting itself in public when it gets something wrong. It has no customers, no licence and no revenue. Exactly what is built, what is designed, and what is unproven changes week to week; the honest answer at any moment is the **live maturity register published on the site**, and this document deliberately does not duplicate it.

And what it is for is settled. The aim is carbon, not commerce: to discover how each household can best be helped to play its part in the solution, and to place what is built and learned in the public domain — including, if it fails, exactly why it failed. There are many simulations of climate change. There are very few simulations of how each of us can best be helped to act on it. This is one. It is not built to become a token-burning exercise: compute is spent only where it buys learning, and funding is welcome for one purpose — to make that learning faster and better, through real volunteers and a disciplined carbon proof. Human direction is capped at one person today; it could widen to a small number of expert volunteers without changing what it is. The mission — carbon abatement through personalisation — is a direction the Director has chosen, to be judged as argument.

## 1. The pattern nobody disputes

The expensive part of engineering was never the successful prototype. It was the failed ones.

Aerospace stopped building airframes to discover they were wrong and moved the discovery into CFD. Automotive crash-tested in simulation long before it crash-tested in steel. Semiconductor design has been verification-first for decades — nobody tapes out a chip to find out whether it works. Pharmaceutical discovery narrows an enormous candidate space computationally before anything reaches a bench, let alone a patient. Formula One teams are limited by regulation in how much wind-tunnel time they may buy, and compete on simulation quality instead.

The shift happens when two things cross a threshold: fidelity — the synthetic environment becomes faithful enough that what you learn there transfers — and compute — enough of it to run the space rather than sample it thinly. Simulation never replaced real-world testing. It changed what real-world testing is for. Failures move to where they cost nothing; the real world is reserved for confirming refined, high-confidence answers.

## 2. Business never got a simulator

A company gets one life. It learns in production, against real customers, with real money on the table, and pays for its lessons in churn, capital, complaints and regulatory scrutiny. Every failure mode it discovers, it discovers the expensive way. Every assumption made at the specification stage is tested by reality after the code is written, the process is embedded and the debt is accrued.

Financial models are not simulators — a model is a simplification designed to produce a forecast. What has been missing is an environment: a running approximation of the company itself, with the same market data, the same regulatory constraints, the same customer lifecycle and the same financial plumbing, operating continuously so that behaviour emerges rather than being specified.

This matters most where complexity is highest and the cost of learning in production is worst: regulated markets. UK retail energy is a good place to prove it precisely because it is unforgiving. Real settlement data. Real price caps. Real licence conditions. Real consequences — thirty suppliers left the market in 2021–22.

## 3. What already exists, and where we differ

This idea is not ours alone, and the people who got there first deserve credit.

Power TAC has run since 2012: an open-source simulation of a retail electricity market in which autonomous trading agents compete, offering tariffs to customers and covering their positions in wholesale and balancing markets. It has an annual international competition and a research community around it. It was ahead of its time and it remains the closest thing to what we are building. Agent-based modelling of electricity markets is a mature academic field going back two decades, and rate-design work in the United States now evaluates thousands of heterogeneous households to test how tariff structures land on affordability and fairness.

The idea was right. What has changed is what can now be built on it.

| | The field today | Poesys |
|---|---|---|
| **The customer** | A load shape and a tariff choice — typically a rational agent balancing cost against inconvenience, aggregated into usage bands. Individual tariffs are often not even expressible. | A household: home physics, finances, life events, capability, willingness, attention — and the states that move week to week. Individual by construction. |
| **The firm** | Tariff strategy and trading, to the P&L line. | The operating interior as well: billing, credit, arrears, collections, complaints, the ledger, regulatory compliance — where real suppliers actually fail. |
| **What the firm can see** | The modeller sees everything; the simulation is built to be analysed. | The company is blindfolded — it infers its own book from meter reads, payments and contacts, exactly as a real supplier must. |
| **Data** | Often stylised or limited by what was available when the platform was designed. | A decade of real settlement prices, the national building stock, linked household panels, published service-quality statistics. |
| **How it is built** | Research teams, grant cycles, publication rhythm. Human-paced, episodic. | Built and improved continuously by AI, in parallel, self-testing, self-correcting, with human direction capped. |
| **What comes out** | Findings, papers, competition results. | Working software intended to run a company, plus the evidence for whether it is trustworthy. |

Speed and cost are the honest advantage, not brilliance. The bottleneck was never the idea; it was that building and maintaining something this large used to require a team and a budget. A system that builds itself continuously, runs on a single machine and reserves expensive reasoning for design rather than typing changes that arithmetic. Wider scope, deeper detail, faster iteration, lower cost — those are the four claims, and none of them requires anyone else to have been wrong.

The build is uneven by design — some dimensions are hardened, some are designed and unbuilt — and the live register records which is which at any moment, including the defects the system has declared against itself.

## 4. Building one honestly

A simulator that flatters is worse than none, because it produces confident answers that transfer to nothing. Three disciplines make the difference, and each is a constraint on ourselves.

**Anchored.** The world is built on real observable data — a decade of real half-hourly settlement prices, real gas prices, real building stock, real regulation — not invented physics. Every assumption is registered against an external source, and where the simulation diverges from a published benchmark, the divergence is recorded rather than tuned away. Every figure published carries its exact cut and derivation.

*The data, in two layers.* Underneath, real, and available in volume across every category that matters: markets (decades of half-hourly settlement prices and daily gas prices); homes (the national building stock at property level — age, construction, heating, insulation, efficiency); consumption (half-hourly metered demand and published load profiles by customer class); people (national longitudinal surveys covering income, expenditure, life events, health, attitudes and energy hardship); service reality (published statistics on complaints, debt, switching and supplier performance); business (full public financial records for every UK company, plus non-domestic building performance and sector consumption data).

On top, synthetic and effectively unlimited: households and firms generated from those real distributions, living years of consumption, bills, payments, contacts and life events — every one traceable back to a real anchor.

The linkage question is the important one, and the honest answer is layered. Some datasets are genuinely joined at household level — smart meter reads linked to survey responses and building records, longitudinal panels following the same households for years — but those are thousands of households, not millions. Population-scale data links statistically rather than record to record, and some of it, complaints and service quality in particular, exists only as published rates attached to no individual home. That is enough, because the small linked datasets supply the thing that actually matters: the correlation structure. How house physics relates to income; how income relates to payment behaviour; how attitudes relate — or fail to relate — to what people actually do. Learn the joint structure where it is observable, then generate populations at any scale that reproduce it — including the awkward combinations, which is where the value is.

That combination is the whole point. Any competent analyst can model a factor. What no company has been able to do is run the permutations: this kind of house, with this kind of household, at this point in their financial year, hit by this kind of weather, on this kind of tariff, with kit that half-works, contacted this way at this moment. The space is far too large to observe directly and far too large to test on real customers. Generated faithfully, it can be explored exhaustively — and the intersections that matter found before anyone builds anything for them. This is the move that unlocked modern AI: when you run out of real examples, generate faithful ones from what you know, and learn from experiences that never happened but absolutely could. Real data sets the physics; synthetic data provides the volume; the fidelity work exists to keep the second honest to the first.

**Blindfolded.** The company inside the simulator cannot see the simulator's workings. It discovers its world the way a real supplier would — through meter reads, market feeds, bills, payments and regulatory publications. The test applied to every piece of information is: could a real UK energy supplier have known this, at that moment? Without that wall, a simulated company learns to cheat, and everything it teaches you is worthless.

**Validated against reality.** Simulation narrows the search; real people confirm it. The design: consenting volunteers keep their own supplier and share their data, we run a parallel personalised bill against their actual consumption, and publish the difference — including where we were wrong. Where prediction fails, that is discovery: a missing factor located in a real household and fed back into the model. This programme opens only after a security posture review has completed — the moment real household data is involved, the standard changes — and the live register records where it stands.

## 5. The budget is the design

Human input, money, tokens and carbon are all deliberately capped. An unconstrained system builds bloat: more headcount, more features, more compute, because nothing forces a choice. A constrained one invents. Each cap acts as selection pressure on a different axis — capped human input forces genuine autonomy rather than an assistant with a person behind it; capped cost forces architectural efficiency; capped tokens force the work onto small local models wherever a large one is not genuinely needed; capped carbon forces the delivery mechanism to be as light as the outcome it claims.

The four scarcities are also the product. They are what makes cost-to-serve approach zero — the premise everything after this depends on.

## 6. The end of economies of scope

Economies of scope were the whole game, and they are ending.

Because software was expensive to create, the winning move was to build one platform and spread it across as many customers, markets and use cases as possible. Everything followed from that: configuration flags instead of different products; roadmaps set by the largest and most conservative customer; vendors in regulated industries unable to ship anything their most cautious client will not certify; an experience that is the average of everyone and the preference of no one.

The monolith is not a design failure. It is the rational response to a cost that no longer exists.

When creating software is marginal cost, the compromise stops being necessary. You do not configure one system for a new market — you generate the instance that market needs. And the same logic runs all the way down to the individual customer, because the two costs that used to be fused come apart: learning a pattern is genuinely expensive and is paid once — this kind of household, at this kind of moment, responds to this — while applying it to the next matching household costs tokens. Architecture per customer; economics at the pattern level.

## 7. What personalisation actually means here

Not a segment. Not a name in a mail-merge.

**Their own plan and their own path.** Every household has a cost and carbon trajectory — what they spend, what they emit, and how both move when the boiler ages, a baby arrives, an EV lands, a fixed term expires. The company holds that trajectory rather than a segment average, so every intervention is judged against it: did this household's cost and carbon actually bend, or did we merely send a message?

**Timing, not just targeting.** Slow-moving traits — the physics of the home, the household, what they care about — set the range of what is possible. Fast-moving states move within it: a house move, a bill shock, a cold snap, the week before payday. Habits reset at moments of change, and an intervention timed to one of those windows outperforms the same intervention sent at random. The biggest savings of all — insulation, a replacement boiler, a heat pump, an EV's charging schedule — are only ever taken at moments like these: a move, a new car, a boiler that finally fails. Moments of action, not campaigns. Conventional segmentation sees the traits and misses the states, and the states are where behaviour actually changes.

**Channel and tone.** Personalisation is not only what a customer is offered — it is how they are met: channel, timing, register, length, how much explanation. The same message that helps one household lands as harassment in another, and the same household wants a different tone in different weeks. A monolith settles on one voice, tested against the average, and that voice is the reason most people ignore their energy supplier. Here the voice is generated per person, per moment — brisk when they are busy, gentle when they are struggling, technical when they want the detail — and it costs nothing extra.

It matters most exactly where it is hardest. When someone is behind on a bill, the difference between a competent nudge and a threatening one determines whether they act or hide.

## 8. Real homes, real reluctance

Households are not showrooms. They are accumulations of technology acquired over decades, by different people, for different reasons, with no plan. A boiler from 2011. Solar panels whose inverter predates the assumption that everything has wifi. A smart meter that lost its signal two years ago and nobody chased it. A smart thermostat someone unpaired because it kept doing things they had not asked for. Almost nothing integrates cleanly, and much of it never will.

Most of the energy transition is designed for a house that barely exists: fully connected, fully instrumented, occupied by someone who enjoys optimising things. That house belongs to the early adopter — and the early adopter has already acted. The carbon that remains is in the other homes, with older kit, patchier connectivity and people who are not interested in a project.

Which leads to the point the industry keeps getting wrong. Inertia and reluctance are treated as obstacles: barriers to be overcome with better apps, louder messaging, more persuasion. They are not obstacles. They are the operating conditions. Most people do not want to engage with their energy supply. They want the house warm, the bill lower, and to think about it as little as possible — and that preference is entirely reasonable.

So we treat it as the design brief. Work with whatever a home can actually do rather than what it ought to have. Ask for the smallest change that produces the result. Never require enthusiasm, and never require the same thing twice from someone who has already declined. A product that only works for people who are keen has excluded the majority of the remaining carbon by construction.

This is where the simulator earns its place twice over. A synthetic population can be built to be as awkward as the real one — real building stock, real technology vintages, kit that half-works, people who ignore, refuse, or agree and then never act — so what works for reluctant households is discovered before anything is built for them. And it is where the argument against one-size-fits-all lands hardest: a single platform must be designed for the average home, which means designing for a home nobody lives in. Generating per household means meeting each one where it actually is.

## 9. Why carbon is the mission

Behaviour change is the cheapest abatement left. No capital works, no supply chain, no installation, no waiting list. It fails commercially for one reason: personal attention has always been priced per head, so it went to wealth management and never to a household paying an energy bill. Remove that cost and the economics invert.

And it is the same move the customer is already paying for. The only durable way to cut a bill is to cut the energy behind it — use less, and use it when it is cheap. That is also, and identically, the abatement. Discounting, the industry's current paradigm, moves margin between supplier and customer and saves nothing; usage-side saving pays the customer and the climate from the same action. Money is why the household acts; carbon is why Poesys exists; one intervention serves both, counted on two ledgers. This is what value creation should mean for a supplier: a smaller bill because less energy was needed, not because a loss-leading discount bought a switch.

The clearest example is one nobody sells. Most UK condensing boilers never actually condense: they are left at a flow temperature that keeps the return water too hot for the second heat exchanger to recover any latent heat, so an appliance rated A runs at C-to-E efficiency for its entire life. Turning that temperature down costs nothing, needs no equipment and changes no habit, and the published trial evidence puts the saving at roughly a tenth of a household's gas. No discount comes close, and nobody in the industry has a reason to mention it. That is the shape of the opportunity: savings that are invisible, unglamorous, specific to one house, and worth finding only when attention costs nothing.

Getting tone and timing right is not customer service. It is abatement. The barrier to domestic behaviour change is rarely information — people broadly know. It is the message arriving wrong, at the wrong moment, in a voice that triggers avoidance rather than action.

The UK government's own appraisal benchmark gives the yardstick: a central carbon value of £273 per tonne of CO₂e for 2025 (2022 prices, ±50% sensitivity), derived from the marginal abatement cost of meeting legally binding targets. Anything delivered below that line pays for itself in policy terms. The metric we intend to be judged on:

**£ per tonne of CO₂e saved = (cost to serve + cost to persuade, including compute) ÷ (carbon abated)**

Autonomy drives the numerator down. Personalisation drives the denominator up.

Two disciplines keep this honest. First, it is a diagnostic, not a target — the moment a number becomes something to optimise, it stops measuring anything. Second, three ledgers, all reported: carbon saved for customers; carbon spent serving them — people, compute, tokens; and the net position. A carbon claim that counts only one side is not a claim. Third, the customer-savings ledger counts only savings from reduced or time-shifted usage — never price transfers or discounts — because a discount can be gamed and a kilowatt-hour cannot.

## 10. The same argument for business customers

Business energy divides on one line: whether a procurement function exists. Above it — large industrial and commercial — behaviour is genuinely rational: tender cycles, risk mandates, budget certainty. Modelling that needs an optimiser and a contract calendar rather than psychology, and it is where carbon stops being a preference and becomes a purchase: larger companies face mandatory carbon reporting and supply-chain pressure, so a supplier that hands them audited, granular carbon data — and demonstrably reduces it — is supplying something they are already obliged to produce. The three-ledger discipline becomes a product feature.

Below the line — the publican, the corner shop, the care home — the residential argument transfers almost unchanged: one busy owner, no procurement, heavy reliance on brokers, contracts that roll over because nobody had time. Regulators protect these customers specifically because the market does not behave rationally for them. The inertia is the same inertia, and the reason they have never been served well is the same reason: individual attention cost individual headcount. The natural second population, not a different product.

## 11. Global by design

Energy is the domain, globally — not as an expansion story, but as a property of the design. Market structure, regulator, climate, tariff regime, building stock and payment culture are variables the simulator samples, not architecture it must rebuild; the core — supply and demand mechanics, hedging and risk, the customer lifecycle, the billing waterfall, the decision architecture — stays constant. Because an attempt costs almost nothing, you can run many attempts, and many attempts is how anything gets good. Britain first, because it is one of the hardest and best-instrumented retail energy markets in the world. If it works here it is unlikely to be defeated by somewhere easier.

## 12. Why believe any of it

The most valuable output so far is not a profit figure. It is the errors the system has caught in itself. Among them, as a permanent public record:

- A forward premium an order of magnitude above the industry benchmark, traced to its own volatility mathematics — a calibration error that only surfaces when settlement runs against real prices across a full market cycle.
- A price engine whose extreme-spike tail was an order of magnitude too small — found by its own fidelity instrument and declared publicly as the blocking defect rather than smoothed over.
- Published figures on its own website that had silently drifted from the underlying data — caught by a rule that every published number must be derived from source rather than copied.
- A flagship discovery publicly retracted when its evidence turned out to be leaked by a subtle look-ahead in the system's own inputs. The retraction was narrated, not quietly deleted.
- A measured blind spot it reported on itself — a class of payment failures it structurally cannot observe — published as a limitation to live with rather than adjusted away.

The current defect register, with each finding's derivation and status, lives on the site and is always more up to date than any document.

None of these is a triumph. Together they are the argument. A system that audits itself this hard is the only kind whose efficiency and carbon claims are worth anything — and the machinery that produces them is itself the asset: it holds itself against a deliberately naive benchmark, removes one factor at a time to see whether that factor was doing any work, and runs the same simulated household twice — once contacted, once not — to isolate what genuinely caused what. Very few real companies can measure the quality of their own learning. This one is built to.

## 13. What is not proven

The load-bearing claims are hypotheses with designed tests, and they stay in this section until real-world evidence moves them out:

- **That personalisation keeps paying as it gets finer.** That value keeps rising past broad groups into the fine-grained combinations most companies never reach is the load-bearing claim.
- **That timing beats messaging by enough to matter.** The least well-anchored part of the model: nothing in linked real data connects a household's attention to its meter. Disposition does leave observable traces — the kit a household owns and how they run it says more about their tolerance for effort than any survey answer — but attention and mood do not, and that gap is where this claim is exposed. The thesis rests on behavioural trial evidence, and it is the idea most likely to be wrong.
- **That any real tonne has been abated, or real pound saved.** In-simulation counterfactuals prove the mechanism is coherent; only real households save money and carbon.
- **That the blueprint transfers to another market** without more work than the argument implies.

All of these need the real world, and the path there is deliberately small: volunteers who keep their own supplier, a parallel personalised bill run alongside their real one, and the difference published both ways.

## 14. The cost of finding out

The most unusual thing about this venture is how little it costs to run. The same constraints that make the product work make the enterprise cheap: no office, no sales function, no platform to maintain, the heavy work on small local models on a single machine. The burn is closer to a research project than a startup.

That changes the shape of the proposition. This does not need venture capital to survive — it needs sponsorship to go faster, and it can continue either way. The scale of money that would materially change the trajectory is the scale routinely available to carbon and net-zero innovation programmes in the UK: enough to run a real volunteer cohort, prove abatement against a disciplined counterfactual, and take the blueprint into a second market. Not enough to interest a growth fund, which is rather the point. The bet is asymmetric: the cost of finding out is small, the failure is cheap and instructive, and the upside — behavioural abatement delivered below the government's own appraisal value, replicable across markets — is not.

What we are looking for, in order:

1. **Domain stress-testing.** The most valuable thing an energy practitioner can do is try to break it. Every decision the system makes is published in readable form, so an expert can see what it chose, why, and on what evidence — and argue with it without touching any code.
2. **Volunteers**, once the security posture review completes: households who keep their existing supplier and let us run a personalised bill alongside their real one, with the difference published both ways.
3. **Routes to real households** — via suppliers, intermediaries or innovation-funded programmes — where results are measured against the standards the regulator already holds suppliers to, rather than asserted.
4. **Sponsorship for the carbon proof.** Modest and specific: the volunteer cohort and the measurement discipline that turns a simulated mechanism into a proven tonne.

## Note on claims

Every figure this project publishes carries a status — *observed with evidence*, *external benchmark*, *chosen*, *hypothesis with a designed test*, or *retracted and not relied upon* — and the current register of claims, with each figure's derivation and exact data cut, is maintained on the site rather than frozen into this document. Two entries are permanent. The mission stated here — carbon abatement through personalisation — is **chosen, not derived**: a direction the Director has selected, argued above, to be judged as argument. And financial results are published only with their basis and their uncertainty, and never while a declared defect could move them materially — or not at all.

*Poesys · Draft v5*
