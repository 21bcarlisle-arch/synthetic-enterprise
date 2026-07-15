# METHOD LENS — audit our harness against the PROCESS disciplines, not just the AI ones (QUEUE, director-raised)

**Staged:** 2026-07-15 by advisor, **director-raised**. Disposition: QUEUE.
This is a LENS / standing audit, not a feature. Register it, draw it for
DISCOVER, and let it generate proposal-atoms for the map.

## The diagnosis (why we kept rediscovering old knowledge by injury)
Every best-practice review this week scoped itself to "best practice for **AI
agent harnesses**" — worktrees, hooks, headless orchestration, context
management. That is the TOOLING layer. But most of what bit us lives in the
PROCESS layer — sizing, decomposition, WIP limits, flow, estimate-vs-actual,
readiness/done gates — which is decades old and INDEPENDENT of what does the
work. **We scoped our search to the novel-AI universe and skipped the mature
software-delivery universe, for a problem that is mostly a delivery problem
with AI as the executor.** The executor is new; the delivery problem is not.

**Finding 1 was itself scoped too narrowly.** "Search published practice when
you hit a wall" has meant "search published AGENT practice." It must mean
"search published practice INCLUDING the process disciplines that predate AI."
Amend Finding 1 accordingly.

## Evidence: our hard-won "discoveries" are named patterns we could have read
- "Oversized item must be split before starting" = story sizing / INVEST.
  We learned it by watching ARCH1 and the executor stall as unsplit monsters.
- "Limit WIP; flow beats utilization" = Kanban's founding insight.
  We learned it as "GPU at 2% isn't the constraint" and "don't force width onto
  the build lane."
- "The real constraint is invisible until you remove the fake ones" = Theory of
  Constraints, the Five Focusing Steps. We wrote it as "bottlenecks are onions."
- "Estimate vs actual is a calibration signal, not a stick" = the
  capacity-planning / #NoEstimates debate. Raised from first principles tonight.
- "Definition of Ready / Definition of Done" = we've been building ad-hoc level
  gates that are exactly this, unnamed.
- "Blameless post-mortem + a register that spots repeat causes" = classic SRE
  incident practice. Our unified failure register (G4) is re-deriving it.

## The task
A deliberate pass mapping our incident-lessons and current mechanisms against
the established delivery/process disciplines, to (a) NAME what we have, (b)
adopt the refinements those fields already worked out, and (c) surface the
things those fields solved that we HAVEN'T hit yet — so we stop paying tuition
for lessons that are in a textbook.

**Disciplines to draw from (not exhaustive):**
- SDLC / PDLC (product & software lifecycle: discovery, readiness, phase gates)
- Lean / Lean software (waste, flow, pull, build-measure-learn)
- Kanban (WIP limits, flow metrics, cycle time, classes of service)
- Scaled Agile / general Agile (sizing, INVEST, DoR/DoD, backlog refinement)
- Theory of Constraints (identify/exploit/subordinate the constraint)
- SRE / incident practice (blameless post-mortems, error budgets, toil)
- Queue theory / flow (why utilization != throughput — the thing we kept hitting)

## Two questions it must answer
1. **What does mature delivery do that we don't?** (the gaps we haven't reached
   yet — proactively, not by the next injury)
2. **Which of our "novel" findings are named patterns with known refinements?**
   (so we adopt the mature version, not our injured first draft)

## Guardrails (so this doesn't import ceremony we don't need)
- We are ONE director + AI executors, not many human teams. **Adopt the
  PRINCIPLE, reject the CEREMONY.** Most of Scaled Agile's apparatus exists for
  human-team coordination we don't have — take the flow/sizing/constraint
  insights, leave the stand-ups, story-points-as-currency, and ritual.
- Everything adopted is a DIAL, not a target (anti-goal-seek stands — velocity,
  cycle time, size, estimates are all diagnostics, never things to optimise
  toward or gate completion on).
- Output is PROPOSAL-atoms for the director to rank, not unilateral process
  imposition.

## Relationship to what's already staged
This is the META-fix behind EFFORT_SIZING_DISCIPLINE (c872f2f3) — sizing is one
instance; this lens finds the rest. It also strengthens G4 (failure register)
and the naive organ (both currently pointed only at AI-shaped failure modes).

## The point (record it in the casebook)
It turns REACTIVE discovery (learn by injury) into PROACTIVE adoption (learn by
reading) — which is itself exactly what a Lean practitioner would tell you to
do. The highest-leverage process work left is to stop being surprised by
things that are already written down.

## DoD
The audit run as a DISCOVER pass; a mapping table (our lesson/mechanism <->
established pattern <-> refinement-we're-missing) produced and surfaced on the
Method door; proposal-atoms generated for genuine gaps and queued for director
rank; Finding 1 amended in CLAUDE.md to include non-AI delivery disciplines;
the reject-ceremony / adopt-principle and dial-not-target guardrails recorded.
