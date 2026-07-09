# EPOCH2_EVIDENCE_PASS — R9 desk work before the next epoch is framed (P2)

**Staged:** 2026-07-09 by advisor, director-approved.
**Place in the arc:** Epoch 1 (core fidelity) is running and unaffected. This pass
gathers evidence about the CURRENT architecture so Epoch 2 ("The Value Cycle" —
the commercial brain: wholesale+NEC→price, price→bill, meter→cash, close→learn)
can be framed as evolution or rebuild on facts, not suspicion. Desk work only:
read code, answer questions with evidence, change nothing. Background-lane
eligible; must not slow Phase 4 / DOMAIN_SENSE work.

## Three questions — answer each with file/line evidence, R9 labels
(observed-with-evidence vs inferred), and a one-paragraph verdict.

### Q1. How are retail tariffs actually set today?
Trace the mechanism end-to-end: where do tariff values come from, per fuel and
segment, per year? Specifically test the director's suspicion: are prices
BACK-CALCULATED (derived from historical market levels / known outcomes /
tuned to hit plausible bills) or DECIDED (an ex-ante cost stack — wholesale,
losses, network, policy, cost-to-serve, bad debt, capital — plus an explicit
margin decision, positioned against something)? If there is any pricing
decision logic, name its inputs, owner, cadence, and audit trail. If there is
none, say so plainly.

### Q2. What is the event model, and could truth arrive late?
Describe the current simulation state model: tick structure, what a "step"
does, how state is written. Then the critical property: can a value, once
computed (a bill, a consumption figure, a cost, a margin), be lawfully WRONG
and later RESTATED — or does the architecture assume single-pass truth
resolved atomically within a period? Assess concretely what it would take to
carry two timestamps per fact (when-it-happened vs when-we-learned-it,
append-only corrections) — locally contained change, or foundational rework?

### Q3. What do compute and storage actually scale with?
Profile a representative full run: where does wall-time go, what does storage
grow with (customers x ticks? events? artefacts?), and what are the top 3 cost
drivers. Then estimate directionally: under (a) population scale-up 10-100x,
and (b) repeated full-history reruns (the future evolutionary tournament),
which components break first? Identify anything computed eagerly per-tick that
could be computed lazily at decision points.

## Output
docs/design/EPOCH2_EVIDENCE.md — three sections, evidence-cited, each ending
with a verdict line: "Epoch 2 implication: evolution / partial rebuild /
foundational rework" plus the single biggest risk. One NTFY with the three
verdict lines only.

## Explicitly out of scope
No fixes, no refactors, no new mechanisms, no ASSUMPTIONS changes. Evidence
only. The director and advisor frame Epoch 2 from your answers.
