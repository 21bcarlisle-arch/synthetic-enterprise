# Autonomous Build-Executor — Spec (scoped 2026-07-14; BUILD = tomorrow's P1)

## Why it exists — the gap, with evidence
2026-07-14 22:03→23:26: the map only moves when an EXECUTOR consumes the Rule-0
supervisor draw. The interactive session was the only executor; it went quiet and
the map froze ~83 min while auto-process re-ran **flat** (£1,521,070 every cycle).
The Rule-0 draw *identifies* work; it does not *do* it. Rule 0's "default state is
WORKING" therefore needs an autonomous executor. Until it exists, the human-tier
session is a single point of idle.

## Req 1 — exhume WHY autonomous_runner was retired → resurrect-vs-rebuild ON EVIDENCE
Evidence: `docs/staging/done/AUTONOMOUS_RUNNER_TRUE_RETIREMENT.md` (2026-07-08). It was
**NOT** retired because autonomous execution is wrong. It was retired because it was a
**hidden, unmonitored, respawning, budget-burning** spawner: the 07-07 "console kill"
was non-durable — `start_worker.sh` respawned it on every stack restart — so it kept
launching `claude -p` turns invisibly ("hidden + still spawning + still burning budget…
worse than either state"). The durable fix was to comment it out of the launcher,
enumerate its children, director-kill them, and restore alerting as truly-retired.

**Decision (evidence, not nostalgia): REBUILD, not resurrect.** The old runner's fatal
flaws were pure operational governance (hidden / non-durable-kill / unmonitored /
uncapped budget) — exactly what this spec now mandates. Resurrecting its code inherits
its ungoverned shape. Caveat: FIRST read the old `autonomous_runner.py` turn-loop +
return handling for reusable primitives — reuse *code*, never its *governance*.

## Req 2 — headless turns, machine-checkable returns; REPLACES keystroke injection
- Turns are HEADLESS (`claude -p`/SDK), each returning a **machine-checkable structured
  value** (the schema-forced return my build workflows already use).
- It is the **replacement for keystroke/tmux send-keys injection**, which **STAYS BANNED**
  (safety control; the `/usage`-write incident, one-way-door cat 5/8). The executor NEVER
  types into any interactive pane.
- The **interactive pane is the director's console ONLY** — no automated write to it, ever.
- A turn "succeeded" ONLY when its RETURN VALUE proves work **landed** (origin commit SHA,
  map level bumped, green gate) — never "a turn was submitted" (see the theatre finding
  below). Submit-consumed ≠ write-landed is a build-time invariant here.

## Req 3 — inherits ALL governance unchanged
- **Walls/dials + Rule 0:** consumes the same `_self_refill_draw` incl. the Rule-0 harden
  tier; never crosses a wall; yields dials in reverse priority per Rule 0.
- **One-way doors → the director** (never self-decides); **twin answers the reversible rest**
  (BUILD-open within the open epoch, etc.).
- **Gate-verified pushes:** every executor push runs blast-radius suite + epistemic verifier
  + sole-map-writer discipline — identical to the manual waves.
- **Tripwires over the top:** hard budget cap (tokens/turns per window), concurrency cap
  (the 15Gi OOM lesson → 2-wide default, RAM-aware), a **visible heartbeat** the director
  sees (never hidden — the exact failure that retired the old one), health-check up/down/
  loop alerting, and a **durable kill switch** (launcher edit, not a non-durable process-kill).
  Budget + activity surface on the Director door.

## Req 4 — this IS the Epoch-4 tournament substrate (one build, two payoffs)
The Epoch-4 evolutionary tournament (10k independent sim-lives) and the build-executor are
the SAME primitive: a **governed fan-out of headless units across cores with machine-checkable
returns, a budget/concurrency governor, and monitoring.** A8's `tournament_runner.py`
(parallel, memory-capped, fail-closed-publish, structured-return-per-life) is already a
special case of it.

**A8 re-sequencing case:** do NOT finish A8→L3 as a standalone parallel runner. Build the
**shared executor substrate** (governed headless fan-out + return-gating + budget/concurrency
governor + monitoring); A8's tournament and the nightly build-executor become two frontends
on it, and ARCH1's low-memory `RecordedSimInterface` feeds BOTH. One build, two payoffs.

## Verification standard (from tonight's theatre findings — see the two answers)
The executor's own success-check must be **write-landed, not submit-consumed**: no tautology
markers (a self-touched file the checker reads), no "submitted a turn" = "did work". Success
= an independent artifact. **Mutation-test the success-check**: a turn that submitted but
produced nothing must be caught as FAILED, and the check must fail-closed if its evidence
source is unavailable.

## Build plan (tomorrow, P1)
1. Read old `autonomous_runner.py` for reusable turn-loop/return primitives (not governance).
2. Core: governed headless-turn executor (draw → dispatch → **gate the return** → next), with
   budget/concurrency/heartbeat/kill-switch tripwires + monitoring + Director-door visibility.
3. Wire to `_self_refill_draw` (Rule-0 tier included); one-way-door→director, twin→rest.
4. Fold A8's `tournament_runner` in as a frontend on the same substrate.
5. Mutation-test the return-gating (submit ≠ landed) and every tripwire (each fires on its defect).
