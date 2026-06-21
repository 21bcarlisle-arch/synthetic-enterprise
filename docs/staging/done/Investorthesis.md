# Add Investor Thesis — Long-Horizon Goals to CLAUDE.md

## Instruction

Add the following new section to CLAUDE.md, after the "Roadmap from here"
section and before "Technical environment". This captures the long-horizon
vision from the investor thesis document. It is context for future roadmap
decisions, not an immediate build target. Do not start building any of
these things now — just encode them as the north star.

## Section to add

---

## Investor Thesis — Long-Horizon Vision

The following goals are not immediate build targets. They are the
destination the simulation is working toward. Every phase decision
should be evaluated against whether it moves toward or away from
these goals.

### Digital Darwinism at Machine Speed

The simulation currently runs one continuous timeline (2016–2025).
The long-horizon goal is to run the same company through multiple
alternative timelines simultaneously — deliberately inducing extinction
events (the 2021 crisis, regulatory interventions, competitor shocks,
demand collapses) and evolving the operational blueprint through them.

Each run produces a blueprint stronger than the last — not by small
iterative margin, but fundamentally stronger because each run discovers
failure modes invisible in the previous one. The 2021 crisis revealed
regime-change blindness. The next stress test will reveal something else.

The build should move toward: configurable extinction events, parallel
scenario runs, blueprint comparison across runs. The current single-
timeline run is the foundation. Scenario branching is the destination.

### Bot-to-Bot Protocol Discovery

As AI deployment matures, a new category of interaction emerges: two
AI agents negotiating directly with no human in the loop on either
side. When the company's procurement agent negotiates with a supplier's
sales agent, the failure modes — commitment boundaries, hallucination
risks, adversarial dynamics, contractual implications — are qualitatively
different from anything in human-to-human or human-to-AI interaction.

The simulation is the only safe environment to discover and test these
protocols before they result in real contractual commitments or legal
exposure. This is not a future problem — it is an immediate one for any
company deploying AI agents in commercial roles.

The build should move toward: agent-to-agent interaction scenarios,
commitment boundary testing, adversarial negotiation discovery. The
company layer agents (tariff engine, churn model, retention offers)
are the starting point. Inter-agent negotiation is the destination.

### The Translation Thesis — Geography and Industry as Parameters

Every failure mode discovered in UK energy has a structural analogue
in other complex regulated industries:

- Regime-change blindness → insurance reserving models trained on
  benign history; credit scoring trained on expansion
- Activity-based pricing gap → corporate insurance policies profitable
  until claims capital is loaded; large bank clients subsidised by retail
- Forward curve overpricing → specialty lines premia wrong vs loss
  emergence; bid-offer calibrated to recent vol, blind to tail risk

The simulation should eventually be re-parameterisable: change the
regulatory framework, market structure, currency, and cultural behaviour
parameters — and the same core physics runs in German energy, UK
insurance, or retail banking. The blueprint compounds across sectors
and geographies without a full rebuild.

The build should move toward: clean separation of market-specific
parameters from core physics, documented parameter interfaces for
each layer, proof-of-concept re-parameterisation for one new market.
UK energy is the first blueprint. It is not the last.

### The Real Company Transition

The simulation becomes a real company when it starts transacting.
That transition requires:
- The SIM/company barrier fully enforced — the company operating
  entirely on its own models with no shared code paths to SIM internals
- Real customer-facing interfaces — a portal where simulated customers
  interact, and eventually real ones
- Real market interfaces — the company submitting to Elexon, not just
  reading from it
- Capital — at the point when the blueprint is proven, not before

The simulation is not there yet. But every phase should be evaluated
against: does this move us closer to a company that could actually
transact? If not, why are we building it?

---

## Commit message

"CLAUDE.md: add investor thesis long-horizon vision section"
