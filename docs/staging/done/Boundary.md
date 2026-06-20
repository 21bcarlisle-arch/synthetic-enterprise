# Design Principle: Epistemic Honesty — The Company Cannot See Inside the SIM

## The Principle

The most important architectural rule in this project, after Historical
Ground Truth, is this:

**The company cannot know what the simulation knows.**

The SIM is ground truth. It knows the real churn probability distributions,
the real forward curve dynamics, the real weather, the real customer
behaviour parameters. The company never has direct access to any of this.

A real energy supplier doesn't know:
- The true probability that a customer will churn
- The true forward price dynamics and risk premiums
- The true demand elasticity of its customers
- The true cost structure of its competitors
- What the weather will actually do

It discovers these things through observation, over time, imperfectly.
It reads market data feeds. It talks to customers. It analyses its own
bills and payments. It monitors meter reads. It builds models from
observed outcomes — and those models will always be approximations,
sometimes wrong ones.

The company's models being imperfect is not a bug. It is the point.
Real suppliers make systematic mistakes in their churn models, their
forward curve assumptions, their demand forecasts. Those mistakes have
consequences. The simulation should allow — and produce — those
consequences.

## What this means in practice

**The company reads from interfaces, not from simulation internals:**
- Market prices: read from a market data feed interface, not from
  forward_curve.py directly
- Customer behaviour: inferred from observed renewals, churns, and
  complaints — not from churn_model.py parameters
- Weather and demand: read from weather forecast feeds and meter reads —
  not from the weather engine internals
- Risk and VaR: calculated by the company's own risk models from
  observable market data — not from the simulation's VaR engine

**The company builds its own models:**
- Its churn model is trained on observed customer outcomes, not on
  the simulation's ground truth parameters
- Its forward curve is constructed from market observations, not from
  the simulation's pricing engine
- Its demand forecast is built from meter reads and weather forecasts,
  not from the simulation's consumption model

**The SIM/company seam is epistemic, not just architectural:**
- `company/interfaces/sim_interface.py` defines what the company is
  allowed to observe
- Anything not exposed through this interface is invisible to the company
- The interface exposes outcomes and observables, never parameters or
  internals

**The assumption library (docs/market_research/ASSUMPTIONS.md) is the
company's knowledge base** — built from what it has discovered through
observation and research, not from reading the simulation's source code.

## The test

Before any piece of company-layer code is written, ask:
"Could a real UK energy supplier know this?"

If yes — it can be in the company layer.
If no — it must come through the interface seam as an observable,
or be estimated by the company's own models from observable data.

If the answer is "only by reading the simulation's internals" —
it is a violation of this principle.

## Add to CLAUDE.md

Add the following section to CLAUDE.md immediately after "Architectural
laws" (or create that section if it doesn't exist):

---

### Epistemic Honesty — The Company Cannot See Inside the SIM

The company layer operates under the same information constraints as a
real energy supplier. It cannot see simulation internals — churn model
parameters, forward curve construction, weather engine outputs, VaR
model internals. It discovers the world through observable interfaces:
market data feeds, meter reads, customer interactions, its own bills
and payments, regulatory publications.

The company's models (churn, demand, forward curve) are approximations
built from observed outcomes — not reads from simulation ground truth.
Those approximations will be imperfect. That imperfection is the point.

Before writing any company-layer code, ask: "Could a real UK energy
supplier know this?" If the answer requires reading simulation internals,
it is a violation of this principle.

The SIM/company seam (company/interfaces/sim_interface.py) enforces
this boundary. It exposes observables and outcomes. It never exposes
parameters or internals.

---

## Commit message

"Add epistemic honesty principle: company cannot see inside the SIM"
