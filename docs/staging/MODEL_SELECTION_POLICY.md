# MODEL_SELECTION_POLICY — match the model to the work (P1, mechanised)

**Staged:** 2026-07-12 by advisor, director-raised ("should we not move it up to
Opus from Sonnet? did we stage a 'use the right model' instruction?"). Answer:
no such rule existed — a real gap. The project has a LOCAL tiering policy
(Qwen for in-sim risk calls) but nothing governing which FRONTIER model does
which work. Fix that, in config, not in memory.

## Principle
Model choice is a per-ROLE decision, not a per-session preference. Two
different failure modes need two different tiers:
- **Judgment work** (noticing subtle wrongness) -> the strongest model.
- **Execution volume** (producing correct mechanical output at scale) -> the
  efficient model.

## Assignment
**OPUS-tier (judgment):**
- **DIRECTOR_TWIN — mandatory, non-negotiable.** Its entire value is fidelity
  to the principal's judgement. A cheaper model that approximates the director
  BADLY is worse than no twin: it answers confidently, as him, wrongly, and the
  error only surfaces at overturn. If the twin runs on anything, it runs on the
  strongest model available.
- Cold-eyes / skeptic passes, Expert-Hour walks, C-suite persona reviews.
- FRAME and DISCOVER loop stages; architectural design; epoch framing.
- Root-cause investigations of the class that found the bill/ledger disconnect
  and the granting-model defect.
- Adjudications of findings; the internal-audit organ.

**SONNET-tier (volume):**
- BUILD execution: writing code and tests to a settled design.
- HARDEN sweeps, mechanical refactors, doc updates.
- Wide discovery fan-out (breadth beats depth; many agents, cheap each).
- The auto-process pipeline.

**LOCAL (Qwen) — unchanged:** high-frequency in-sim calls (risk committee),
where cost per call dominates and the decision is bounded.

## Mechanise it (MAKE_IT_STICK applies)
Encode the assignment in the harness config — subagent definitions, hook
config, session defaults — so the right model is used BY CONSTRUCTION, not by
the agent remembering to switch. A model policy that depends on memory is a
model policy with an expiry date. Record it in CLAUDE.md as well (two places
or not at all).

## Measure it (the honest test)
This is a hypothesis, so test it: tag each turn/atom with the model that did
it, and track by model tier — evaluator NEEDS_WORK rate, defects caught,
rework rate, level transitions per token. Report at the next epoch boundary.
If the Opus premium buys nothing measurable on judgment work, say so plainly
and revert — that is the evidence culture applied to ourselves.

## Budget note
Weekly usage sits ~36% on a Sunday with a Monday reset, and the director's
standing complaint has been UNDER-use, not over. There is headroom to spend on
the turns that think. Tokens are the fuel gauge, never the score.

## DoD
Model assignment live in config (state which model each role now uses); twin
pinned to the strongest tier; CLAUDE.md updated; per-turn model tagging + the
comparison metrics collecting; one digest line reporting the current model of
the main session (the director cannot see it from his end — tell him).
