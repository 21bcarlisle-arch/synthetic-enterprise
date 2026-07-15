# DIRECTOR ANSWERS — Appendix C.7, all six (signed, relayed by advisor)

**Staged:** 2026-07-15. **Director-ratified in live conversation ("GO").** These
are DECISIONS, not proposals — R13/one-way-door items are signed here; execute
against them. They incorporate the STAGING_PULL_LOOP_RESCOPE: the pull loop is
the main transport; H17-headless is re-aimed at fan-out + Epoch-4 substrate.

## 1. Budget (TurnBudget)
**No token cap beyond the plan's own windows.** Tokens are not the constraint;
a tight cap re-invents goal-seeking. **Turns: 20/hour ceiling as a DIAGNOSTIC,
not a throttle.** The real guard is a churn alarm: **sustained turns with zero
level-transitions is the runaway signature** — alarm on that ratio, not on
count. The old MAX_TURNS_PER_HOUR=2 stays rejected. Director-set, versioned;
never agent-tuned.

## 2. Activation
**Pull loop: live TODAY, immediately after its instrumented proof passes**
(three consecutive turn boundaries drawing + executing with zero pane writes),
during the director's waking hours — he will flip the enable flag himself at the
console (see #6). **H17-headless: stays dark** until its re-scoped need arises
(fan-out beyond subagent limits; Epoch-4 tournament). Build can complete dark.

## 3. Concurrency
**Main loop is 1-wide by construction** (one session, one turn at a time).
Width lives INSIDE turns via worktree subagents, governed by the **RAM-aware
cap the OOM incident set (currently 2)** — raised only when the guard shows
headroom, never by preference. Tournament concurrency is an Epoch-4 decision.

## 4. A8 — ABSORB
**H10/H17 ABSORBS A8's substrate.** Building the turn-substrate twice is the
file-scope collision the question predicts. **A8 survives as the METRIC-BEARING
atom**: cycle-time profiling, fast-mode guardrails (fast-mode may never
publish — mechanical, fail-closed), and the Epoch-4 feasibility number, all on
H17's substrate. Adjust file_scope and L3 sequencing accordingly.

## 5. Model tier
**Main-loop turns: Opus** — the standing Monday decision, made because the
judgment failures were main-session failures, and the pull loop IS the main
session. Per-atom routing inside turns follows the existing CLAUDE.md table
(build=Opus, swarm=Sonnet, supervisor micro=Haiku, Qwen local). Haiku
micro-turns for tournament lives: DEFERRED to Epoch-4 framing.

## 6. Kill switch — confirmed, with three hardenings
Path/name confirmed: `docs/observability/.build_executor_enabled`. Hardenings:
(a) **ONE switch governs ALL autonomous execution** — pull loop and any future
headless executor; no second flag. (b) **Fail-closed:** file missing/malformed
= DISABLED. (c) **Console-only to flip** — director-reserved, same class as
security profiles; no agent, twin, or staged doc may create or modify it.
**Mutation test required (R15):** with the flag off, the very next turn
boundary must REFUSE to continue — a kill switch never proven to kill is a
theatre control per the kill-list doctrine.

## Standing note
The through-line of all six: generous where the cost is tokens, hard-edged
where the cost is control. Report each answer's implementation in the next
digest; the activation step (#2/#6 flag-flip) waits for the director's console.
