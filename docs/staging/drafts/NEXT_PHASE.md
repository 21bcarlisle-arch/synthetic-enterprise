# NEXT_PHASE proposal — Phase RY: Reputation Feedback Loop (FEEDBACK_AND_REPUTATION Layer 2)

**Filed:** 2026-07-08 (autonomous session, after processing run_complete_20260708T072800Z).
**Tier:** 3 (novel/self-generated). The ranked queue is exhausted at its front — S1 (shadow-live
track record) was CLOSED by Phase RX (Options A **and** B), and its fast-follows (hedge-outcome
grading, live NBP gas) are unranked backlog and both currently un-actionable autonomously (grading
is premature until live entries accumulate; a gas source is network + endpoint-verification blocked).
Layer 2 is a *named, staged* scope item (docs/staging/FEEDBACK_AND_REPUTATION.md, carved out as
"still open" when the P2 queue closed), but it was never ranked into the current queue, so I am
classifying UP to Tier 3 and giving the standard 4h opt-out rather than claiming pre-approval.
**Opt-out window: 4h from the NTFY timestamp — will proceed unless redirected.**

## The gap this closes (roadmap item + real-world fidelity gained)
Roadmap item: **FEEDBACK_AND_REPUTATION.md Layer 2 — Public Reputation & the reputation loops.**
Layer 1 (Phase RU) gave the company a *private* view of satisfaction: CSAT/NPS surveys, complaint
occurrence/resolution against the real 56-day Ombudsman SLC window, discovered empirically off the
SIM's hidden true satisfaction. But today reputation is a dead-end read: nothing *consumes* it.

Real UK suppliers live and die by public reputation. A Trustpilot score and the quarterly Citizens
Advice star-rating are visible to everyone, owned by no one, and they **feed back into the book**:
bad press raises in-market shopping propensity and depresses acquisition-funnel conversion; good
service recovery and review responses are real spend decisions weighed against reputation-mediated
CLV. Right now the sim has an acquisition funnel (`simulation/acquisition_funnel.py`) and a
reputation index (`company/core/reputation_index.py`) that never touch each other. **The missing
fidelity is the loop** — reputation as an emergent, consequential state, not a vanity metric. This
is a structural gain (a closed feedback loop), explicitly NOT "another board section" (rule 0a/R6).

## Scope (one phase)
1. **Public review generation (SIM-side).** Customers post Trustpilot-class public reviews with
   propensity driven by satisfaction *extremes* (delight/anger, not the silent middle) and event
   triggers (billing error, great service recovery, switching friction). Rolling public score +
   review volume. Grounded to a real benchmark distribution in
   docs/market_research/ (extend NUDGE/FEEDBACK benchmark note — no network needed; use published
   figures already cited, or file a discovery-agent task if a fresh anchor is wanted).
2. **Regulator-style quarterly star-rating** (Citizens Advice analogue) computed from complaints
   volume + contact performance + billing accuracy, **population-anchored** to the real published
   supplier-rating distribution (so a "4-star" means what it means in the market).
3. **THE LOOPS (the point of the phase):**
   - reputation → acquisition-funnel conversion (a funnel-stage multiplier in acquisition_funnel.py);
   - reputation → in-market entry probability in the churn journey (bad press ⇒ customers shop).
   Both consume only company-*observable* reputation (the public score), never SIM-internal truth —
   epistemic wall preserved and, per 0b, *shown* on both sides.
4. **Company levers as EV decisions** (decision_policy.py): service recovery, review responses,
   complaint-handling investment — each a cost-vs-reputation-mediated-CLV choice in the decision loop.

## Evidence rule (0b — must land on business surfaces, from the latest run)
- **Customers tab:** a named account leaving a public review after a real service event — real dates,
  real trigger, review text template keyed to the event. (Extends the existing Reaction Chain.)
- **Sim tab:** reputation trend vs SIM true-satisfaction (correlation panel) + the funnel-conversion
  response to a reputation swing over time.
- **Supplier tab:** the company's public score & star-rating dashboard vs SIM truth divergence, and
  the reputation→acquisition figure the decision loop now acts on. (Extends RU's Reputation section.)
- **Project tab:** spec/archive only.

## Why not the alternatives
- *S1 fast-follows* — hedge-outcome grading is premature (no accumulated live entries yet); live NBP
  gas is network/endpoint-verification blocked (Tier-1-adjacent external data decision, needs Rich).
- *NUDGE_PHYSICS remaining mechanisms* — additive breadth (more behavioural levers of the same kind);
  Layer 2 closes a *loop*, which is the higher-fidelity structural gain. NUDGE stays a good follow-on.

## Sizing / risk
Mostly SIM + company modelling with a bounded frontend extension to three existing surfaces. Fully
autonomous (no network on the critical path). Reversible (new modules + additive wiring; funnel/churn
multipliers default to 1.0 so a mis-calibration is a no-op, same defensive pattern as RX's rolling
fetch). Not a one-way door — no data-model rewrite, no epistemic-law change, no external/live-site
structural change. Epistemic verifier must PASS on the reputation→funnel seam before commit.
