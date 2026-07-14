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

---

## Appendix A — REQ-1 exhumation: old `autonomous_runner.py` (discharges the Req-1 caveat)
DISCOVER pass, 2026-07-14/15, doc-only. Source read: `git show 400ef3692:background/autonomous_runner.py`
— the **last live version** (commit `400ef3692`, 2026-07-11 12:16 "Close DISABLE_AUTOUPDATER
permanence gap", 271 lines), the one that was subsequently commented out of `start_worker.sh` per
`docs/staging/done/AUTONOMOUS_RUNNER_TRUE_RETIREMENT.md`. History enumerated via
`git log --all --oneline -- background/autonomous_runner.py` (14 commits, `58bcfbe4e` first →
`400ef3692` last). **All line numbers below are into that `400ef3692` blob**, not any live file.

**Verdict stands: REBUILD (§Req 1), reuse the mechanical primitives below, inherit NONE of the
governance. The two lists are deliberately exhaustive so tomorrow's build can cite/lift or reject
each item by line.**

### A.1 — REUSABLE PRIMITIVES (reuse *code/shape*, re-governed)
1. **Headless `claude -p` subprocess launch (the core primitive).** L207–L215:
   `subprocess.Popen([CLAUDE_BIN, "-p", "--model", AUTONOMOUS_TURN_MODEL, "--dangerously-skip-permissions", PROMPT], cwd=PROJECT_DIR, stdout=outfile, stderr=outfile, text=True, env=env)`.
   This is exactly the "headless turn" of Req 2 — non-interactive, no TTY, output redirected to a
   file, never types into a pane. Lift the invocation shape; replace the free-text prompt with the
   schema-forced structured-return prompt (Req 2's machine-checkable return).
2. **Model routing to the cheap tier.** L58–L63 rationale + L63 `AUTONOMOUS_TURN_MODEL = "claude-haiku-4-5-20251001"`,
   threaded into the launch at L208. Matches CLAUDE.md's current routing (`AUTONOMOUS_TURN_MODEL` =
   Haiku for supervisor micro-turns). Reuse the constant + the "fastest/cheapest for volume micro-turns"
   decision; keep it a named constant, not a literal.
3. **Absolute `CLAUDE_BIN` path + existence guard.** L55–L56 (`/home/rich/.nvm/.../bin/claude`,
   full path "since nvm isn't active in subprocess env") and L168–L170 (skip + log if the binary is
   missing). Real operational lesson — nvm shims are not on the subprocess PATH; keep both.
4. **Rate-cap via a sliding-window deque.** L90 `_turn_times: deque`, L103–L107 `turns_in_last_hour()`
   (pop entries older than 3600s), enforced at L176–L178 against `MAX_TURNS_PER_HOUR`. This is the
   skeleton of Req 3's "hard budget cap (turns per window)" — reuse the deque/window mechanic, but
   drive it off the real budget/turn governor, not a hard-coded `2`.
5. **Single-flight guard (no overlapping turns).** L172–L174: if `_active_proc.poll() is None`, skip
   the cycle. This is the seed of Req 3's concurrency cap — generalise from 1-wide to the RAM-aware
   N-wide (2-wide default) governor, but the "don't launch while one is in flight" check is correct.
6. **Turn reaping + return-code capture.** L235–L254: `poll()` the child, read `returncode`, log
   completion, reset `_active_proc`. This is where Req 2's **return-gating** must be injected — the
   old code trusts `rc==0` and does nothing with the *content* of the turn; keep the reap loop, but
   replace "rc captured → done" with "parse the structured return → prove work landed (origin SHA /
   map level / green gate) → only then count success" (see §Verification standard).
7. **Connectivity-aware rate-cap refund.** L239–L251: on `rc != 0`, tail the output file for
   `ConnectionRefused` / `Unable to connect` and, if found, pop the slot back off `_turn_times` so
   API downtime doesn't burn the budget window. Sound idea (don't charge the cap for infra failures)
   — reuse, but make the classifier structured (exit-code / typed error) rather than substring-grep
   of a redirected log tail (fragile: `rsplit("---\n", 1)[-1]`, L241).
8. **Usage-limit detection to yield to the watchdog.** L138–L162 `_usage_limit_active()` +
   L180–L182 skip. Recognises a usage-limit pane and stays out of the way so `session_watchdog`
   owns the wait/resume. Keep the *intent* (don't fire into a known-dead limit); the pane-scrape
   implementation is a governance anti-pattern (see B.5) — read the limit from a durable status
   signal, not `tmux capture-pane`.
9. **Append-only structured logging + turn-output capture.** L94–L100 `log()` (UTC-stamped,
   mkdir-safe append) and L187–L191 (per-turn `---`-delimited header written to
   `autonomous-turn-output.md`). Reuse the append-only, timestamped, per-turn-delimited log shape;
   it feeds the visible heartbeat (Req 3) once it also writes a machine-readable status, not only prose.
10. **`agent_status.json` heartbeat wiring.** L88 import, L223–L228 startup registration
    (role/produces), L253/L256/L258 per-state `update_agent_status(...)` (idle/working). This is the
    hook the Director-door heartbeat (Req 3) already consumes — reuse the wiring; the *defect* was
    that nothing forced it to stay visible (see B.3).
11. **`DISABLE_AUTOUPDATER=1` + `ANTHROPIC_BASE_URL` scrub on the child env.** L195–L206 & L206:
    copy env, `pop("ANTHROPIC_BASE_URL")` (go direct, no token-proxy SPOF — L192–L194), set
    `DISABLE_AUTOUPDATER=1` explicitly per-launch rather than trusting tmux inheritance (the whole
    point of commit `400ef3692`). Both are hard-won per-launch env-hygiene fixes — reuse verbatim.
12. **Reaper wrapped so one bad turn can't kill the loop.** L266–L267: the per-cycle body is inside
    `try/except Exception` that only logs. Correct resilience shape (cf. CLAUDE.md "sim_runner
    TimeoutExpired must be caught") — keep it.

### A.2 — GOVERNANCE ANTI-PATTERNS (do NOT reuse — these are exactly what retired it)
1. **Respawn-on-restart / non-durable kill.** The fatal one. The runner was a `while True`
   long-lived daemon (L230–L264) launched from `start_worker.sh`; a console process-kill was
   non-durable because the launcher re-spawned it on every stack restart
   (`AUTONOMOUS_RUNNER_TRUE_RETIREMENT.md`: "hidden + still spawning + still burning budget").
   New executor's kill switch MUST be a **launcher/config edit (durable)**, not a process-kill —
   Req 3's "durable kill switch (launcher edit)".
2. **No real budget cap — only a hard-coded turns/hour.** L67 `MAX_TURNS_PER_HOUR = 2`, a literal
   with no token accounting and no coupling to any actual budget window (L22 comment even calls it
   "conservative"). No hard *token* cap anywhere. Req 3 mandates a real budget cap (tokens AND turns
   per window) driven by the governor, fail-closed.
3. **No visible heartbeat / unmonitored.** Though it wrote `agent_status.json`, nothing surfaced the
   runner to the director and nothing alarmed on up/down/stuck — so it ran *invisibly* for 6+ hours
   ("hidden, unmonitored"). Req 3: a **visible heartbeat the director sees on the Director door** +
   health-check up/down/loop alerting. Invisibility, not autonomy, is what got it retired.
4. **Idle/liveness inferred by scraping the interactive pane.** L110–L135 `idle_seconds()` +
   L118 `_pane_content()` = `tmux capture-pane -t claude -p`, with L262 firing a turn after 30 min of
   a "static pane". This couples the executor to the **director's console pane** (Req 2: the
   interactive pane is the director's console ONLY) and is fragile (a static pane ≠ idle work).
   The new executor draws from `_self_refill_draw` (Rule 0), not from pane-staleness.
5. **Usage-limit detection also by pane-scrape.** L145–L162 `_usage_limit_active()` reads the pane
   text and pattern-matches UI strings (`"usage limit reached"`, etc.), with an ad-hoc `|[]`` -skip
   heuristic (L157) to dodge code-context false positives. Same console-coupling anti-pattern as #4
   and inherently brittle — read a durable limit signal instead.
6. **`--dangerously-skip-permissions` on an unattended, ungoverned spawner.** L27–L33 / L185 / L208.
   The flag itself is authorised (SKIP_PERMISSIONS_TIER1, console-confirmed for every launcher) — the
   anti-pattern is pairing full skip-permissions with *no* budget cap, *no* concurrency governor, *no*
   visible heartbeat, and a *non-durable* kill. Full autonomy is only safe **behind** the Req 3
   tripwires; the flag is a given, the governor around it was missing.
7. **Free-text prompt, return trusted on exit code alone.** L69–L85 prompt is prose ("ADVANCE THE
   PROJECT", "pick the highest-priority gap", "NTFY Rich") and success is judged only by `rc`
   (L252) — the textbook **submit-consumed ≠ write-landed** theatre this spec bans (Req 2 /
   §Verification standard). Not reusable: replace with a schema-forced structured return that must
   prove an independent landed artifact.
8. **Self-directing scope (chose its own work + messaged the director).** The prompt let the turn
   pick priorities and even NTFY the director with proposals (L78–L80). The new executor consumes the
   governed `_self_refill_draw` (one-way-door→director, twin→reversible rest); it does not free-choose
   scope or write to the director's channel on its own initiative.

---

## Appendix B — Atom framing (proposal for the orchestrator to register)
DISCOVER/FRAME output, doc-only. **This section does NOT edit `docs/design/maturity_map.yaml`** —
the sole-writer guard (THREE_LANES: orchestrator is the sole map writer until
`H9_map_write_serialisation`) owns that file. The orchestrator lifts the block below into the map.
Schema mirrors the live `A8_experiment_loop_speed` entry; `provenance: proposal` per
EPOCH_GATING_AND_ATOM_AUTHORSHIP (author-and-frame allowed now, BUILD-open is DIRECTOR_TWIN's call).

### Proposed map entry (lift verbatim, orchestrator adjusts id-collision/rank)
```yaml
- id: H10_autonomous_build_executor
  name: "Autonomous build-executor: a governed headless-turn executor that CONSUMES the Rule-0 self-refill draw and lands work, so the map moves without the interactive session as sole executor — and IS the Epoch-4 tournament substrate (governed headless fan-out + return-gating + budget/concurrency governor + monitoring)"
  lane: H_harness
  value_stream: close_to_learn
  epoch: 2
  level_current: 0
  level_target: 3
  loop_stage: build
  dial_inherited: 3
  provenance: proposal
  evidence: ["docs/design/AUTONOMOUS_EXECUTOR_SPEC.md", "docs/staging/done/AUTONOMOUS_RUNNER_TRUE_RETIREMENT.md", "docs/observability/autonomous-runner-log.md"]
  file_scope: [background, tools, tests]
  simplifications: ["2026-07-15 FRAMED (doc-only DISCOVER pass, AUTONOMOUS_EXECUTOR_SPEC.md). Rebuild-not-resurrect (spec Req 1); reuses the 12 mechanical primitives exhumed from old autonomous_runner.py @400ef3692 (Appendix A.1), inherits NONE of the 8 governance anti-patterns (A.2). Shared substrate with A8's tournament_runner and ARCH1's RecordedSimInterface (spec Req 4): build the governed headless fan-out ONCE, A8's tournament and the nightly build-executor are two frontends on it. Success = write-landed (origin SHA / map-level bump / green gate), never submit-consumed; return-gating and every tripwire (budget cap, concurrency cap, visible heartbeat, durable kill switch) mutation-tested to fire on their own named defect (R15). Interactive pane stays director-console-only; keystroke/tmux injection STAYS BANNED (one-way-door cat 5/8)."]
  expert_hour: {status: not_attempted, last: null, findings: []}
  real_world_twin: "an operations team that can identify the next job automatically but still needs a person physically present to press go — until it builds a governed dispatcher that does the pressing under hard budget, concurrency, and kill controls"
  depends_on: [A8_experiment_loop_speed, ARCH1_internal_seams]
```

### Field rationale (for the orchestrator's review, not part of the map entry)
- **id `H10_autonomous_build_executor`** — proposed; orchestrator resolves any collision with the
  live H-series before registering.
- **lane `H_harness`** — it is harness/experiment-loop infrastructure (measures and moves the map),
  same lane as A8 and the tiered-test/experiment-speed work it shares a substrate with.
- **epoch 2** — matches A8 (its co-substrate) and honours COMPOUNDING_WORK_FIRST: this shortens the
  feedback loop (the map moves without a human executor), so it sequences with the other
  compounding-return work regardless of the narrative epoch arc. It is tomorrow's P1.
- **file_scope `[background, tools, tests]`** — executor core + tripwires live in `background/`
  (alongside `supervisor.py`/`session_watchdog.py`/`director_twin.py` it wires into), the
  tournament/fan-out frontend + any CLI in `tools/` (matching A8's own `[tools, background, tests]`),
  mutation tests in `tests/`. **Overlaps A8's file_scope** → NOT disjoint → these two do not draw
  concurrently under the multi-atom-draw file_scope gate; serialise, or build H10's substrate first
  and land A8 as a frontend on it (spec Req 4's "one build, two payoffs" sequencing).
- **depends_on `[A8_experiment_loop_speed, ARCH1_internal_seams]`** — spec Req 4 names both: A8's
  tournament folds in as a frontend, ARCH1's low-memory `RecordedSimInterface` feeds both frontends.
  Orchestrator confirms whether H10 should instead ABSORB A8 (build the shared substrate under H10,
  demote A8 to a frontend milestone) rather than depend on it — a re-sequencing call the spec flags
  ("do NOT finish A8→L3 as a standalone parallel runner").

### Proposed exit tests (L1 / L2 / L3)
- **L1 — governed single-turn executor (the core loop lands one real unit).**
  Draws one atom from `_self_refill_draw` (Rule-0 tier included), dispatches ONE headless
  `claude -p` turn with a schema-forced structured return, and gates on **write-landed**: the turn
  counts as success only when its return proves an independent artifact (origin commit SHA / map
  level bumped / green gate), never on submit/`rc==0`. One-way-door→director, twin→reversible rest.
  Interactive pane never written to. Exit test: a live turn lands a real commit whose SHA the gate
  reads back from origin; a **mutation test** proves a turn that submitted-but-produced-nothing is
  caught as FAILED, and the check **fails closed** when its evidence source is unavailable (R15:
  no tautology / fail-open / fail-silent).
- **L2 — full tripwire governor + visible monitoring, running unattended.**
  Every Req-3 tripwire enforced and each **mutation-tested to fire on its own named defect** (R15):
  hard budget cap (tokens + turns/window), concurrency cap (RAM-aware, 2-wide default — the 15Gi
  OOM lesson), visible heartbeat on the Director door (budget + activity), health-check
  up/down/loop alerting, and a **durable kill switch (launcher/config edit, not a process-kill** —
  the exact failure that retired the predecessor; a non-durable kill must be provably insufficient
  in test). Gate-verified pushes: every executor push runs the blast-radius suite + epistemic
  verifier + sole-map-writer discipline, identical to the manual waves. Exit test: runs a
  multi-turn unattended session that respects every cap, surfaces a live heartbeat a fetch confirms,
  and is durably stoppable via the launcher edit with the process-kill shown to be resurrected by a
  stack restart (proving durability is required).
- **L3 — shared Epoch-4 substrate: two frontends, one governed fan-out.**
  A8's `tournament_runner` (parallel, memory-capped, fail-closed-publish, structured-return-per-life)
  and the nightly build-executor both run as frontends on the SAME governed headless-fan-out +
  return-gating + budget/concurrency governor + monitoring, both fed by ARCH1's low-memory
  `RecordedSimInterface`. A fast/mock/tournament run may NEVER publish, promote an atom, or feed the
  board pack (fail-closed, mechanical — inherited from A8). Exit test: a governed N-wide fan-out
  runs both a build sweep and a tournament batch under one budget/concurrency governor with per-unit
  machine-checkable returns; the fail-closed publish barrier is mutation-tested (a mock/tournament
  unit attempting to publish/promote is blocked); COUPLED-TRIAD gap reported. C-S5 time-scale
  invariance stated for the fan-out logic.
