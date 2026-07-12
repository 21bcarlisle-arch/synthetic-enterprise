# Escalation reversibility audit (PROCEED_BY_DEFAULT.md / MAKE_IT_STICK.md DoD)

**Both docs ask for an audit of "the last 20 escalations" — how many were actually reversible.**
Honest finding: this project's ENTIRE history contains only **7 formal Tier-1 review-gate
escalations** (`docs/review_gates/done/`), not 20 — smaller than either doc anticipated. No padding
to reach 20; this is the full population, not a sample.

## Classification against the NEW one-way-door list (7 categories: real money, real-world
commitment, irretractable public claim, irrecoverable data loss, security/safety-control, values
decision, real customer/market)

| Gate | Old-model reason | New-model verdict |
|---|---|---|
| `SKIP_PERMISSIONS_TIER1.md` | Tier 1: safety-control mod | **Genuine one-way door** (category 5) |
| `SKIP_PERMISSIONS_ALL_LAUNCHERS.md` | Tier 1: safety-control mod | **Genuine one-way door** (category 5) |
| `EPISTEMIC_VERIFIER_TIMING_DETECTION_TIER1.md` | Tier 1: safety-control mod | **Genuine one-way door** (category 5 — modifying the verifier itself) |
| `POESYS_ROUTINE_SCOPE_TIER1.md` | Tier 1: safety-control mod | **Genuine one-way door** (category 5 — live external cloud Routine, real credentials/connectors) |
| `HEDGE_VOLATILITY_LOOKBACK_FORESIGHT_BUG.md` | Tier 1: epistemic law | **Borderline** — the live site headline figures were not yet PROVISIONAL-labelled at the time, so publishing corrected figures was arguably category 3 (irretractable public claim); weaker than the other four, and would likely not need a full stop-the-world gate once figures carry the PROVISIONAL badge (now standard, R14) |
| `POINT_IN_TIME_SNAPSHOT_TIER1.md` | Tier 1: epistemic law | **Would NOT need to block under the new model** — this was a design/registration decision ("register, don't build now"), not a code change to the wall's enforcement itself. "Touching the epistemic law" is not one of the new 7 categories on its own; the epistemic verifier gate (run before every commit) is the real, mechanical enforcement — a design discussion about the wall's architecture is ordinary reversible work |
| `AUTONOMOUS_RUNNER_STILL_RUNNING.md` | Tier 1 (ambiguous — not cleanly one of the old two categories even at the time) | **Would NOT need to block** — killing a stray process is trivially reversible (restart it if wrong); this reads as an operational judgement call escalated out of caution, not a real one-way door |

## Result

- **4 of 7 (57%) were genuine one-way doors even under the new, narrower model** — all four are
  safety-control modifications (category 5): skip-permissions (twice), the epistemic verifier
  itself, and a live external cloud Routine's tool/connector scope. This is a real, structural
  signal: nearly every genuine escalation in this project's history has been a safety-control
  change, not a business/build decision — exactly the category PROCEED_BY_DEFAULT.md's own
  authentication convention (CLAUDE.md) still gates hardest, correctly.
- **2 of 7 (29%) would NOT need to have blocked** under the new model (`POINT_IN_TIME_SNAPSHOT_TIER1`,
  `AUTONOMOUS_RUNNER_STILL_RUNNING`) — both were epistemic-law-adjacent or operational judgement
  calls, reversible in practice, escalated under the OLD model's broader "anything touching the
  epistemic law" category (now narrowed away — the epistemic verifier's own automated gate is the
  real enforcement, not a human stop).
- **1 of 7 (14%) is borderline** (`HEDGE_VOLATILITY_LOOKBACK_FORESIGHT_BUG`) — plausibly avoidable
  now that PROVISIONAL labelling (R14) exists, but wasn't standard practice at the time.

**Honest framing, not the director's own prior expectation forced to fit:** the doc anticipated
finding "nearly all" of the last 20 were reversible. The real number is smaller (29% clearly
reversible, up to 43% including the borderline case) — the true population is 7, not 20, and a
majority (57%) were genuine safety-control changes that would correctly escalate under either
model. The measured error is real but more modest than "nearly all" — reported as measured, not
adjusted to match the expected narrative (R9).
