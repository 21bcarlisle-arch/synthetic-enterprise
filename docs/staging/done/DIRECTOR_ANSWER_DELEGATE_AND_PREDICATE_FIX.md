# DIRECTOR ANSWER — DELEGATE (forever) + escalation fires IFF the predicate is true (P1, signed)

**Staged:** 2026-07-16 by advisor, **director-decided ("Delegate — fix forever")**.
Answers the executor-wall escalation on SITE1 review-gating AND fixes the class
that produced it. Two parts: a decision (part 1) and a harness defect fix (part 2).

## PART 1 — DELEGATE, permanently. Taste is a TWO-WAY DOOR.
**Cold-eyes personas gate visible surfaces to their target level autonomously.
The director does NOT gate visible surfaces — not as a blocker, not as a periodic
review.**

Principle (director, verbatim intent): **taste is a two-way door.** If the
machine's aesthetic/visual choice is wrong, the director changes it freely, later
— an L3 demotes on a word. Reversibility already gives him the only thing he
needs (the power to correct), so there is NO reason to gate on taste up front.
Gating visible surfaces on the director's eyes just makes him the bottleneck on
every visual atom (Theory of Constraints: do not put the director in the critical
path of high-frequency work).

**Rule reconciliation (resolve the conflict PERMANENTLY, don't re-ask per atom):**
- CLAUDE.md Expert-Hour "cold-eyes personas review; director spot-checks, never
  gates" → THIS governs visible surfaces.
- P-4 "Rich-flagged visible surface flips to done only on Rich's visual
  confirmation" → **REPEALED/NARROWED**: visible surfaces reach their level on
  cold-eyes verification; the director may review and freely demote at his
  cadence, but his review is NEVER a gate and the loop NEVER waits for it.
- SITE1 specifically: cold-eyes gates it to L3 autonomously. Its "pixel-pending
  the director's eyes" residual is DISSOLVED — it was the bottleneck this repeals.

Net: visible surfaces progress at machine speed; the director corrects taste
whenever he chooses, reversibly, without ever being a blocker.

## PART 2 — HARNESS FIX: escalation fires IFF the one-way-door predicate is true
The executor mislabelled a REVIEW-GATE (SITE1 L3, which demotes freely = fully
reversible) as a one-way door and stopped on it. Root cause (the turn's own
honest finding): it escalated on gate_status='escalate' JUDGEMENT, not because
one_way_door.py's predicate fired — the predicate wouldn't fire on a reversible
level-up. **This is exactly the ACTION_NEEDED_REDESIGN failure: escalation must
fire if-and-only-if the predicate is true.**

**Requirement (class fix, not instance):**
- An escalation to the director fires **IFF** the one-way-door predicate matches
  (real money, legal/real-world commitment, unretractable public claim,
  irrecoverable data loss, security/safety-control, values/curriculum, real
  customer/market, platform-admin). 
- A **reversible review-gate is NEVER a one-way door.** If the only question is
  "is this good enough?" and a wrong answer demotes freely, it is NOT escalated
  as a door — cold-eyes (or the relevant reviewer) decides it autonomously, per
  Part 1.
- The executor may not escalate on free-floating "judgement/uncertainty" — if
  uncertain AND reversible, it PROCEEDS (per ONE_WAY_DOOR_DEFAULTS_TO_ACT and
  ROUTE_AROUND_BEFORE_STOPPING) and logs; it escalates ONLY on a true predicate
  match, and then via a self-contained NTFY (per ESCALATIONS_MUST_BE_SELF_CONTAINED).
- Mutation test: a reversible review-gate must NOT produce an escalation; a true
  one-way door MUST. Revert-to-break fails it.

## Why this is "fix forever"
Part 1 removes the director from the critical path of visible-surface review
permanently (taste = two-way door). Part 2 stops the loop mislabelling reversible
gates as doors permanently (predicate-gated escalation). Together: the loop stops
manufacturing director-decisions out of reversible work, and the one class of
decision the director actually reserved (true one-way doors) still reaches him —
self-contained, on his phone.

## DoD
P-4 narrowed/repealed for visible surfaces (cold-eyes gates, director never
blocks); SITE1 L3 reachable autonomously, its pixel-pending residual dissolved;
escalation wired to fire IFF the one-way-door predicate matches; reversible
review-gates never escalated; the judgement-based escalation path removed;
mutation test proving a review-gate produces no escalation and a true door does;
folded with ACTION_NEEDED_REDESIGN, ONE_WAY_DOOR_DEFAULTS_TO_ACT, and H19.
