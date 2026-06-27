# Human Simulation Layer — Vision and Build Requirements

## Read First: The Founding Vision

Before reading this document, read `docs/vision/pitch.md` in the
repo. It contains the complete articulation of why this layer exists:
- Section 2c: The hyper-personalised human simulation
- Section 2d: The observability gap — edge cases are the business
- Section 2e: Hyper-personalised CLV — every customer gets the same rigour

This document translates that vision into build requirements.

## Context

This document extends FOUR_SECTION_VISION.md (the SIM section,
"Customer World" tab) and DESTINATION_VISION.md. Do not duplicate
what is in those documents. This document has one job: specify what
the human simulation layer should be and how to build it.

This is the most distinctive part of the project. Everything else —
the trading book, the ledger, the regulatory stack — a well-funded
team could build. The hyper-personalised human simulation is what
no one else has, because no one else has run the full population of
UK energy customers through enough life scenarios to know what
actually drives behaviour.

---

## The Problem with Current Customer Models

Current energy supplier software treats customers as consumption
profiles attached to payment methods. CRM systems hold transactional
data. Segmentation models group customers into archetypes. Risk
models assign probability scores.

None of these hold what actually determines how a customer behaves:
their physical circumstances, their economic trajectory, their life
events, and their emotional state.

The simulation currently has 295 customers across 5 segments. That
is better than 9 named customers. It is not the human simulation.

---

## The Vision: Not a Segment. A Person.

Every simulated customer should have four interacting dimensions:

### Dimension 1 — Physical

The home:
- Property type: terraced, semi-detached, detached, flat
- Build era: pre-1919, 1919-1944, 1945-1964, 1965-1980, post-1980
- EPC rating: A-G
- Heating system: gas boiler (combi/system), heat pump, electric
- Boiler age: new (0-5yr), mid (5-12yr), old (12yr+), replacement due
- Solar panels: yes/no, capacity (kWp), install year
- Battery storage: yes/no, capacity (kWh)
- Electric vehicle: yes/no, charger type (3.7kW/7kW/22kW)
- Smart meter: yes/no, install year
- Insulation: loft (yes/no/partial), cavity wall (yes/no), solid wall

All of this is observable from real data sources:
- EPC register (Domestic Energy Performance Certificates — public API)
- Smart meter HH reads (via DCC)
- Census 2021 (household composition by LSOA)
- DVLA (EV registrations by postcode)

All of it changes how energy is consumed, what the bill looks like,
and what the customer's risk profile is.

### Dimension 2 — Economic

- Disposable income band: <£500/mo, £500-1500, £1500-3000, £3000+
- Income stability: PAYE stable, self-employed variable, benefits,
  pension
- Credit score trajectory: improving, stable, deteriorating
- Payment timing history: always on time, occasional late, frequent late
- Sensitivity to price changes: high (switches on small increases),
  medium, low (loyal regardless of price)
- Debt level: none, manageable, stressed, crisis

The economic dimension evolves with life events and with the energy
market. A large bill in a cold winter changes the financial picture
for a cash-constrained household in ways that ripple forward for
months. The simulation should model this forward propagation.

### Dimension 3 — Life Events

The events that change a person's relationship to their energy supplier:

| Event | Effect on energy behaviour |
|---|---|
| New baby | Consumption up (house warmer), attention down, payment timing slips |
| House move | Triggers switch, new tariff, opportunity or loss |
| Job loss | Income drop, payment stress, bad debt risk |
| Retirement | Home all day for first time, consumption pattern changes |
| EV acquisition | Overnight charging, consumption up 20-30%, ToU opportunity |
| Solar install | Export tariff needed, self-consumption changes bill |
| Heat pump install | Electricity up, gas down or zero, tariff restructure needed |
| Chronic illness | Home more, consumption up, vulnerability flag |
| Divorce | Two households from one, both need new supply |
| Death | Estate supply, sensitive handling required |

Each event has:
- A probability per household archetype per year
- A timing distribution (when in the year it tends to happen)
- An effect duration (how long the behaviour change lasts)
- A company response requirement (what the supplier should do)

### Dimension 4 — Emotional

- Stress level: low / moderate / high / crisis
- Attention available: full / distracted / overwhelmed
- Complaint propensity: low / medium / high
- Loyalty vs switching intention: loyal / passive / actively shopping
- Trust in supplier: high / medium / low / broken

The emotional dimension is the hardest to model and the most
important for customer-facing interactions. An agent that cannot
distinguish a distressed customer from an angry one — or a confused
customer from a disengaged one — will consistently produce the
wrong interaction.

---

## The Canonical Example (from the investor thesis)

A person living in a 1960s semi-detached house in Stockport, EPC
rating D, with a 15-year-old combi boiler, solar panels installed
in 2019, an electric vehicle on the drive, and two teenagers.

In February 2023, they have a new baby and their partner has reduced
working hours. Their disposable income has dropped. Their energy
consumption has increased — the house is always warm, the baby needs
a consistent temperature. Their stress levels are high. Their
attention is limited.

This person is not a bad debt risk in the conventional sense. They
have always paid on time. But in the three months following the
birth, their payment timing will slip. They will not open the bill
immediately. They will not engage with a payment reminder in the way
they normally would. They are not defaulting. They are overwhelmed.

A company that treats this person the same as a genuinely high-risk
debtor — applying the same collections script, the same escalation
timeline, the same tone — will generate a complaint. Possibly a
regulatory referral. Certainly a churn event when their circumstances
normalise.

A company that knows who this person is responds differently. It
gives them space. It offers a payment plan before they ask for one.
It checks in with a human touch rather than an automated reminder.

**The simulation should make this scenario happen.** The life event
fires. The consumption changes. The payment timing slips. The company's
service layer sees the signals. The question is: does it respond
correctly?

---

## What to Build

### Phase A — Household Model

Extend the customer data model to include physical home attributes:

`simulation/household.py` — `Household` dataclass:
- property_type, build_era, epc_rating
- heating_system, boiler_age
- has_solar, solar_kwp, solar_install_year
- has_battery, battery_kwh
- has_ev, ev_charger_kw
- has_smart_meter, smart_meter_install_year
- insulation_profile

Seed each existing customer segment with representative household
profiles drawn from real UK data:
- EPC register distributions by property type and build era
- Census 2021 household composition by region
- BEIS heat pump and solar uptake data

The household profile drives:
- Base consumption (calibrated to EPC rating and property type)
- Seasonal shape (better-insulated homes have flatter seasonal curves)
- ToU eligibility (smart meter required)
- EV charging load (if has_ev)
- Solar export (if has_solar)

### Phase B — Life Events Engine

`simulation/life_events.py` — event generator:

For each customer, each year, roll life events based on:
- Household archetype probabilities (young family vs retired couple
  vs single professional vs multi-occupancy)
- Current life stage
- Regional factors (employment rates, housing market activity)

When an event fires:
- Record in the customer's event log with date
- Apply the behavioural effect (consumption change, payment timing
  change, stress level change, attention change)
- Set the duration of the effect
- Flag the appropriate company response

The company layer sees only the observable consequences — not the
event itself. It sees: consumption changed, payment timing slipped,
contact frequency increased. It has to infer the underlying cause.
That inference is the epistemic gap.

### Phase C — Emotional State Model

`simulation/emotional_state.py`:

Each customer has a current emotional state that updates based on:
- Recent life events (new baby → stress high, attention low)
- Recent bill shock (>30% increase → complaint propensity rises)
- Recent company interactions (complaint resolved well → trust up)
- Time since last interaction (long silence → disengagement risk)
- Economic stress (income drop → stress high)

The emotional state determines:
- How the customer responds to outbound contact
- Whether a retention offer is likely to be received well
- Whether a complaint is likely if a problem occurs
- The appropriate contact channel and tone

The company layer should have a simplified version of this model —
built from observable signals (contact frequency, payment timing,
bill shock history) — that approximates the true emotional state
without reading it from the simulation.

### Phase D — CLV at Individual Level

Once household and life events are modelled, CLV becomes
genuinely individual rather than segment-based:

`saas/clv_individual.py`:

For each customer, calculate expected future value as a function of:
- Their specific household (EPC rating drives consumption stability)
- Their life stage (retired couple has predictable tenure,
  young family has high home-move risk)
- Their economic trajectory (improving income → lower churn risk)
- Their emotional state (stressed + high bill → churn imminent)
- Their next likely life event (new EV in next 12 months →
  ToU tariff opportunity worth £X)

The 80/20 insight from the pitch: not all personalisation dimensions
drive equal value variance. Run the full population, vary dimensions
systematically, measure outcome difference. The 20% of dimensions
that drive 80% of value variance become the design brief.

This analysis should run automatically after each simulation run and
appear in the Supplier MI → Customers section as:
"Top 3 personalisation dimensions by value impact this run."

---

## How This Drives the Company Build

Every dimension of the human simulation creates pressure on the
company software:

**Household model** → company needs to know property characteristics.
Forces: EPC data integration, premises model in CRM, consumption
calibration per property.

**Life events** → company needs to detect and respond to them.
Forces: pattern detection in usage and payment data, life event
inference model, appropriate response workflows in CRM.

**Emotional state** → company needs to adapt contact strategy.
Forces: sentiment detection in interactions, contact strategy rules
that vary by inferred state, conversation tone guidance.

**Individual CLV** → company needs to price and retain individually.
Forces: individual renewal pricing engine, personalised retention
offer sizing, proactive outreach timing based on CLV trajectory.

Each of these is a feature the company has to build — not because it
was specified, but because the simulation makes it necessary.

---

## Connection to the Customer Portal

When a customer logs in to poesys.net/customers/, their household
profile should be visible:

- Property: 1960s semi-detached, EPC D, gas boiler (14yr)
- Devices: Solar 3.8kWp (2019), EV 7kW charger
- Household: 2 adults, 2 children + new baby (Feb 2023)
- Current state: payment timing slipped (inferred), stress elevated

This is what makes the portal real. Not just bills and consumption —
the company's model of who this customer actually is, and what it's
doing about it.

The gap between the SIM's ground truth (dimension 4 emotional state:
OVERWHELMED) and the company's inferred state (payment timing +2
weeks, contact frequency down, estimated: STRESSED) is the epistemic
gap made visible in a customer record.

---

## Event-Driven Architecture

Every meaningful thing that happens — in the SIM and in the company
— must be an event. Not a state change in a database, not a
recalculated field, but a timestamped, typed, immutable record that
something happened at a specific point in time.

**Why events, not state:**

State tells you what things are now. Events tell you what happened
and when. From events you can reconstruct any state at any point in
time, project forward for CLV, aggregate across customers for
portfolio analytics, and route different events to different systems.

The CRM, the ledger, account profitability — all of these are
projections from the event stream, not independently maintained
states. When you open a customer record you see their event history.
The current state is derived from that history.

**The event taxonomy:**

Customer events (produced by SIM customer behaviour engine):
- BillIssued, PaymentReceived, PaymentLate, PaymentMissed
- PaymentPlanAgreed, DebtWrittenOff
- ContactMade, ContactAttempted, ContactIgnored
- ComplaintRaised, ComplaintResolved, OmbudsmanReferral
- RenewalOffered, RenewalAccepted, RenewalDeclined, ChurnNotified
- HomeMoveFiled, TariffChanged, SmartMeterInstalled
- LifeEventFired (SIM internal — not visible to company)
- LifeEventSignalObserved (what company can infer)
- VulnerabilityFlagged, VulnerabilityResolved
- SentimentScoreUpdated (from interaction analysis)

Market events (produced by SIM market engine):
- SettlementPeriodClosed, ImbalanceSettled
- ForwardPricePublished, PriceCapChanged, LevyRateUpdated
- HedgeContractOpened, HedgeContractClosed, HedgeContractSettled

Company events (produced by company layer):
- TariffPriced, RenewalOfferGenerated
- RiskCommitteeConvened, HedgeDecisionMade
- InvoiceGenerated, LedgerPosted
- RetentionOfferMade, RetentionOutcomeRecorded
- AcquisitionAttempted, AcquisitionSucceeded

**Account-level profitability from events:**

Every cost and revenue event carries an account_id. Profitability
at any level (account, segment, portfolio) is a real-time aggregation:

Revenue events → BillIssued, ExportPaymentMade
Cost events → WholesaleCost, NetworkCharge, LevyCost,
              CostToServe, BadDebt, AcquisitionCost

Account P&L = sum(revenue events) - sum(cost events) for that account

This works at any time granularity: this period, this contract term,
year-to-date, lifetime. And it's auditable — every pound of margin
traces back to the events that produced it.

**CRM as event consumer:**

The CRM does not hold state — it projects state from the customer
event stream. The customer portal shows the event history, not a
snapshot. Account profitability in the Supplier MI is a live
aggregation from events.

This is what makes the platform extensible. Add a new event type
and every downstream system (CRM, ledger, portal, dashboard)
automatically gets the new data without schema changes.

**Implementation requirement:**

All four phases of the human simulation (household, life events,
emotional state, individual CLV) must produce typed events that
flow into the event store. The company layer consumes observable
events only — never the SIM's internal events (LifeEventFired
is SIM-internal; LifeEventSignalObserved is what the company sees).

The event store is the single source of truth. Everything else
is a projection from it.

## Probabilistic Architecture

The human simulation does not model every customer the same way.
Each customer has their own response function — a set of probability
distributions that determine how they behave at each decision point.
The aggregate P&L is the sum of 295 individual stories, not a formula
applied to a segment average.

**Key principle: behaviour is probabilistic at decision points only.**

Between decision points, behaviour is deterministic — consumption
follows the household profile, the calendar advances, the ledger
posts. At decision points, behaviour is drawn from the customer's
individual distribution shaped by their current state.

Decision points (when probabilistic draws happen):
- Bill receipt — will they read it? when will they pay?
- Payment due date — will they pay on time, late, or not at all?
- Renewal — will they accept, negotiate, or churn?
- Contact event — will they respond? how?
- Life event fires — what is the downstream behavioural effect?

This keeps the simulation computationally tractable. Each customer
has roughly 10-20 state updates per year — trivially fast even at
thousands of customers. Never update state at settlement period
(half-hourly) frequency — that would be 48 × 365 = 17,520 updates
per customer per year and would balloon compute.

**The right probabilistic tools:**

**Payment timing** — survival/hazard model. "How long until payment?"
Each customer has a baseline hazard rate modified by current state.
Stressed customer → slower payment. Comfortable → faster.
Use Weibull or log-normal distribution for time-to-payment.

**Payment default** — competing risks. Customer who hasn't paid faces
competing outcomes: pays eventually, pays with one reminder, pays
with two reminders, goes to collections. Each has a probability and
a time distribution drawn from customer state.

**Churn at renewal** — discrete-time hazard. Probability of churning
at this renewal is a function of bill shock magnitude, price
sensitivity, tenure, emotional state, competitor price signal.
Shifted-Beta-Geometric (already in codebase) is correct for
contractual settings.

**Bill shock response** — not binary. A distribution of responses:
ignore, note dissatisfaction, query contact, formal complaint,
immediate switch. Probabilities depend on complaint propensity
and stress level.

**Contact propensity** — Poisson process. Contacts arrive at a rate
that varies by state. Stressed customer in bill shock month: 3x
baseline contact rate. Inter-arrival time between contacts:
exponentially distributed.

**Life event timing** — Poisson process for rare events (job loss,
new baby, house move). Background rate per year varies by household
archetype. Young family: high new-baby rate. Retired couple: high
chronic illness rate.

**Scaling properties:**

At 295 customers — no performance concern. All customer response
functions are independent (Customer C1's decision doesn't affect C7's)
so they can be computed in parallel or sequentially with no interaction.

At 2,950 customers — still fast. Probabilistic draws are microseconds.
The bottleneck remains the risk committee LLM calls, not customer simulation.

At 29,500+ customers — customer simulation still scales linearly.
Risk committee becomes the bottleneck again. That's when parallel
settlement execution (Stage 5, deliberately deferred) becomes necessary.

The risk committee is the expensive component, not the customer
simulation. Keep customer behaviour probabilistic and decision-point-only
and scaling is not a concern.

## Research Ownership

This document is a starting point, not a specification. The agent
should own the design of the human simulation layer — researching,
challenging, and improving on what is described here before building.

Before implementing any phase, the agent should:

**Research the real data sources:**
- EPC register API (api.ratings.energy.gov.uk) — what data is
  actually available, at what granularity, with what coverage gaps
- Census 2021 (ONS) — household composition, tenure, occupancy by
  LSOA — what's queryable and how
- BEIS heat pump and solar uptake statistics — real adoption curves
  by region and property type
- DVLA EV registration data — real adoption rates by postcode
- Academic literature on energy consumption behaviour and life events
  — what's actually been measured vs assumed

**Challenge the design:**
- Are the four dimensions (physical, economic, life events, emotional)
  the right decomposition, or does research suggest a better one?
- Which life events actually have measurable effects on energy
  consumption and payment behaviour — and how large are those effects?
- What does the behavioural economics literature say about how
  people respond to bill shocks, payment difficulty, and supplier
  interactions?
- Are there better proxy signals for emotional state than contact
  frequency and payment timing?

**Validate against real supplier data:**
- Ofgem Consumer Confidence Survey data — what do customers actually
  report about their energy experience?
- Citizens Advice data on complaint types and drivers
- Vulnerability register data published by suppliers (anonymised)

**Propose improvements:**
After research, propose any changes to the model design via NTFY
before building. The research findings go to
docs/market_research/HUMAN_SIMULATION_RESEARCH.md and
ASSUMPTIONS.md. The model design that emerges from research is
better than the starting point in this document.

The discovery agent should be tasked with this research in parallel
with the build phases. It has web access and the structured finding
schema. This is exactly the kind of assumption validation it exists
to do.

## Customer Economics Framework

This is the commercial engine that makes the human simulation
actionable. Without it, rich customer models produce interesting
data but no decisions. With it, every customer insight drives a
specific commercial action.

### The Three Horizons

Every customer, every product has three simultaneous P&L views:

**Horizon 1 — Expected profit at point of pricing/sale**

When the company sets a tariff and makes an offer, it commits to
an expectation of what that customer relationship will be worth
over the contract term. Calculated at contract start from:
- Expected consumption (from household profile and season)
- Expected wholesale cost (forward curve at time of pricing)
- Expected non-commodity costs (known levy rates)
- Expected cost to serve (from customer archetype and history)
- Expected payment behaviour (from customer state and history)
- Expected tenure (from churn model at this renewal)

This is the "plan." It is stored as an event at contract start:
`ExpectedProfitCommitted(account_id, product, term, amount, assumptions)`

**Horizon 2 — Actual profit as it accrues**

As the contract runs, actual events replace expectations:
- Actual consumption vs expected (weather, life events)
- Actual wholesale settlement vs hedged cost (imbalance exposure)
- Actual payment behaviour (on time, late, missed)
- Actual cost to serve events (contacts, complaints, collections)

Running actual P&L is the sum of revenue and cost events attributed
to this account and product. Updated after every event.

**Horizon 3 — Forecast profit updated continuously**

At any point in a contract term, recalculate expected remaining
value using current information:
- Remaining consumption forecast (updated with actuals so far)
- Remaining wholesale cost (current forward curve, not pricing-time curve)
- Updated churn probability (current emotional state, bill shock history)
- Updated payment risk (current payment behaviour trend)
- Remaining expected life events (updated probabilities)

This is CLV done properly — not a static model score but a live
forecast that updates with every material event. Recalculate when:
- A life event fires
- Bill shock exceeds 20%
- Payment timing changes significantly
- A renewal decision point approaches
- Wholesale prices move materially

### Variance Analysis — The Feedback Loop

Expected (H1) vs Actual (H2) at any point = variance.
Variance needs explanation. Variance categories:

- **Consumption variance**: customer used more/less than expected
  → feeds back into household model calibration
- **Wholesale variance**: hedged cost vs settlement
  → feeds back into hedging strategy
- **Payment variance**: customer paid differently than expected
  → feeds back into payment behaviour model and individual credit risk
- **Churn variance**: customer churned earlier/later than expected
  → feeds back into churn model calibration
- **Cost to serve variance**: more/fewer contacts than expected
  → feeds back into segment cost model

Variance analysis runs after every contract term closes. Systematic
variance (same direction across many customers) indicates a model
error. Idiosyncratic variance (random per customer) indicates
genuine individual variation — expected and acceptable.

The variance report appears in Supplier MI → Financial as:
"Pricing accuracy: expected vs actual by cohort, by segment, by year."

### Contribution Margin Framework

Every customer is measured against **marginal cost** — the cost
that exists because of that customer:

**Variable costs (customer-specific):**
- Wholesale cost of their specific consumption
- Network and levy pass-through (metered to their MPAN/MPRN)
- Bad debt provision (customer-specific risk score)
- Direct cost to serve (contact events, meter reads, billing engine)
- Imbalance cost (their specific deviation from contracted profile)

**Fixed costs (portfolio-level, not customer-level):**
- Regulatory licence fees
- Core IT infrastructure
- Minimum staffing equivalent
- Insurance, legal, compliance overhead

**Decision rule:**
Any customer above marginal cost contributes positively to covering
fixed costs. Accept them. The decision to retain a below-marginal-cost
customer requires explicit justification (strategic value, lifetime
trajectory, relationship anchoring).

All customers together must:
1. Cover all variable costs
2. Cover all fixed costs
3. Provide a return on regulatory capital deployed

Return on capital = (total contribution - fixed costs) / capital deployed
Capital deployed = hedging margin requirements + bad debt provision +
working capital (receivables - payables)

This is what the risk committee should actually optimise — not VaR
in isolation but return on capital given risk.

### Product Portfolio View Per Customer

A dual-fuel customer has an electricity leg and a gas leg.
Each has its own three-horizon P&L.

**Per-product view:**
- Electricity: expected £X, actual £Y, forecast remaining £Z
- Gas: expected £A, actual £B, forecast remaining £C
- Combined: total relationship value and trend

**Cross-subsidy visibility:**
If gas is below marginal cost but electricity compensates, the
cross-subsidy is explicit and managed:
- How large is the subsidy?
- Is it narrowing or widening?
- At what point does the combined relationship become marginal?
- What action (gas price uplift, retention offer, managed exit) is optimal?

Accepting cross-subsidy is a deliberate strategic decision with a
time horizon — not a silent accounting treatment.

**Product upsell opportunities from the portfolio view:**
- Single-fuel electricity customer with an EV → ToU tariff upsell
  (quantified: expected additional margin from peak/off-peak shaping)
- Gas-only customer → electricity acquisition opportunity
- Basic tariff customer approaching renewal → smart tariff upsell
  (quantified: expected reduction in churn risk + margin improvement)

Each opportunity is sized in expected lifetime value terms before
the action is taken. The decision to make the offer is based on
whether the expected value improvement exceeds the cost of the offer.

### Commercial Actions Driven by the Framework

Every insight from the three-horizon model drives a specific action:

| Signal | Action |
|---|---|
| H3 forecast deteriorating, churn probability rising | Retention offer sized to expected value at risk |
| H2 actual below H1 expected (consumption variance) | Update household model, adjust renewal pricing |
| H2 actual above H1 expected (customer more valuable than thought) | Protect relationship, prioritise service |
| Payment behaviour trending worse | Proactive payment plan offer before miss |
| Product cross-subsidy widening | Gas price uplift at next renewal or managed exit |
| EV detected in consumption pattern | ToU tariff offer quantified |
| Life event inferred (consumption spike + payment slip) | Reduce contact pressure, offer payment flexibility |
| H1 systematically wrong for a segment | Repricing of that segment's tariff |

The company does not apply rules. It applies expected value
calculations. Every action is compared against the counterfactual
(do nothing) and the alternative actions available. The optimal
action maximises the forecast lifetime value of the relationship,
net of action cost.

This is what section 2e of the pitch deck calls "collapsing the
distinction between interactions." Retention, collections,
acquisitions, product management — all become one decision:
what is the optimal action for this person at this moment?

### Implementation

The three-horizon P&L model is built on top of the event-driven
architecture already described. Additional events:

`ExpectedProfitCommitted` — fired at contract start, stores H1
`ActualProfitUpdated` — fired after each settlement period, updates H2
`ForecastProfitRevised` — fired when material new information arrives, updates H3
`VarianceExplained` — fired at contract end, attributes variance to causes
`CommercialActionProposed` — fired when the framework identifies an action
`CommercialActionOutcomeRecorded` — fired when outcome is known

These events feed:
- CRM: customer record shows all three horizons and history of actions
- Supplier MI: portfolio view of expected vs actual vs forecast
- Pricing engine: variance feeds back into tariff calibration
- Renewal engine: H3 forecast at renewal drives offer sizing
- Risk committee: return on capital view across portfolio

## Do Not Duplicate

This document adds to:
- FOUR_SECTION_VISION.md: the Customer World tab in the SIM section
- DESTINATION_VISION.md: customer infrastructure backlog

It does not replace either. The build sequence from DESTINATION_VISION
(C1-C4) remains valid. This adds the household and life event model
as the SIM-side foundation that makes those company-layer features
meaningful.

---

## NTFY on completion of each phase

Phase A: "Household model live. [N] customers with property profiles.
Consumption now calibrated to EPC rating."

Phase B: "Life events engine live. First life event fired: [customer],
[event], [date]. Observable consequences in company layer: [list]."

Phase C: "Emotional state model live. Current state distribution:
[N] LOW / [N] MODERATE / [N] HIGH / [N] CRISIS."

Phase D: "Individual CLV live. Top personalisation dimension by value
impact: [dimension] (£[X] variance across population)."
