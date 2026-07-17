# PARALLEL-RUNG HARNESS-PRUNING EVALUATION — adopt first-party, keep governance
**Staged:** 2026-07-17 by advisor, director-decided. **HELD — DO NOT ACTION DURING OPS1.**
**Trigger:** the parallel rung opening — after OPS1 sub-steps 5–7 land verified AND serial
autonomy has run boring for a sustained stretch. Until then this doc just sits here.
**Place in arc:** Lane H (harness). The ladder is stable → serial → parallel → prioritise;
this is the gate work AT the parallel rung. It extends the standing harness-pruning ritual
(memory: re-check first-party practice at every epoch boundary / major release).

## Why (director-ratified reasoning, 2026-07-17)
The sub-step-4 lesson generalises: systemd beat the hand-rolled watchdog because ADOPT
boring first-party plumbing > BUILD bespoke, and the bespoke layer that remains must be
justified against that baseline. Boris Cherny's "Steps of AI Adoption" (2026-07-16)
confirms the same ladder independently (our stable/serial/parallel = his steps 1/2/3) and
names the step-3 trap we lived: "scaling agent count before the loop has earned trust."
His step-2/3 tooling list contains first-party versions of several things we hand-rolled.
Before opening parallel, run the pruning evaluation so we scale on maintained primitives,
not bespoke machinery.

## The evaluation (problem statement — the builder designs the method)
For EACH hand-rolled mechanism below, decide ADOPT (first-party replaces ours) / ADAPT
(first-party under our governance wrapper) / REJECT (bespoke justified — say why against
the first-party baseline), with a small bounded pilot where adoption is plausible:
1. tree_lock / parallel-lane isolation  ↔  Claude Code worktree isolation (CLI/Desktop)
2. pull-loop Stop-hook transport / self-refill  ↔  routines, /loop, /batch, /goal
3. hand-rolled parallel lanes  ↔  dynamic workflows + ULTRACODE (already held in advisor
   memory: bounded pilot only — cap agents via prompt ("use at most 5 agents") or /config
   "Dynamic workflow size"; any size default committed in-repo (.claude/settings), never
   hand-set; watch token cost; high effort stays the session default)
4. NTFY dispatcher / channel-watching  ↔  Claude Tag (monitor a channel, kick off tasks)
5. Any remaining bespoke session/process machinery  ↔  agent sandboxing, Agent view,
   auto-mode classifier tuning, subagent primitives
Also fold in: automatic code review / security review defaults (Cherny step-2 guardrails)
— do we get these for free now, and do they replace any bespoke skeptic-pass mechanics?

## What is NOT up for adoption (the governance layer — no first-party equivalent exists)
Console sanctity contract · HELD/dark/enabled manifest semantics + reconcile · gated
advance (director gates between rungs/sub-steps) · escalation walls & one-way-door
predicate · the epistemic wall · seed-must-not-auto-advance. These ride ABOVE whatever
plumbing wins. The IP is this layer; the plumbing below should be as boring and
first-party as possible (relatable-IP principle).

## Standard for the verdicts
Same honesty as sub-step 4: argue each REJECT against the first-party baseline, not
alongside it; pilots bounded and verified; every adoption deletes the bespoke path it
replaces (no parallel old path); config changes land in-repo per IaC.
