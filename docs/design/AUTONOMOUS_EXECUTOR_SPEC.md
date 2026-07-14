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

---

## Appendix C — Turnkey build plan (H17)
PLAN/DESIGN output, 2026-07-15, doc-only (touches NO code, NOT the map). `H17` is this build's
lane-tracking id in the task; it BUILDS the atom framed in Appendix B as
`H10_autonomous_build_executor` (orchestrator reconciles the id when it lifts the entry — one atom,
two labels). This appendix decomposes tomorrow's P1 so the build is warm: concrete modules, exact
functions to reuse, and the success predicate stated to the line. Everything below is
build-and-test-without-activating EXCEPT §C.5 activation, which is a director-only safety step.

### C.1 — MODULE LAYOUT (new modules + which Appendix-A primitives lift into which function)
Two new modules in `background/` (alongside `supervisor.py`/`session_watchdog.py`/`director_twin.py`
it wires into) + one CLI in `tools/` + mutation tests in `tests/` — matching the proposed
`file_scope: [background, tools, tests]` (Appendix B). The substrate is built ONCE; the
build-executor and A8's tournament are two frontends on it (spec Req 4).

- **`background/build_executor.py`** — the governed single-turn core (the L1 deliverable). Functions
  and the Appendix-A.1 primitive each lifts:
  - `dispatch_turn(prompt, model, out_path) -> TurnHandle` — lifts **primitive #1** (headless
    `claude -p` `subprocess.Popen`, output redirected to a file, never a TTY) + **#3** (absolute
    `CLAUDE_BIN` path constant + existence guard) + **#11** (per-launch env hygiene: copy env,
    `pop("ANTHROPIC_BASE_URL")`, set `DISABLE_AUTOUPDATER=1`). Model arg defaults to the
    named-constant tier from **#2** (`AUTONOMOUS_TURN_MODEL`, Haiku, for volume micro-turns) — kept a
    constant, not a literal.
  - `reap_turn(handle) -> RawTurnResult` — lifts **#6** (`poll()`/`returncode` capture) + **#7**
    (connectivity-aware refund, but re-implemented off a STRUCTURED exit-code/typed-error classifier,
    NOT the fragile `rsplit("---\n",1)[-1]` substring grep the old code used).
  - `run_once(rng=None) -> ExecutorCycleResult` — the draw→dispatch→gate→count body (see §C.2),
    wrapped in the **#12** `try/except Exception`-that-only-logs resilience shape.
  - `log(msg)` / per-turn `---`-delimited output capture — lifts **#9** (append-only UTC-stamped log)
    but ALSO writes a machine-readable status line, feeding the heartbeat.
  - `_heartbeat(state, last_action)` — lifts **#10** (`agent_status.update_agent_status(...)`) — see
    §C.3.
- **`background/executor_governor.py`** — the tripwire layer (the L2 deliverable), kept separate so
  the core loop stays small and each tripwire is independently mutation-testable:
  - `TurnBudget` (sliding-window deque) — lifts **#4** (`deque`/3600s-window mechanic) but driven by a
    real budget object (tokens AND turns per window), fail-closed, NOT a hard-coded `MAX_TURNS_PER_HOUR=2`.
  - `concurrency_cap()` — reuses `tools.tournament_runner.memory_safe_worker_cap(...)` /
    `default_worker_count()` directly (A8's primitive, §C.3); the **#5** single-flight guard
    (`_active_proc.poll() is None`) generalises to the N-wide (2-wide default) in-flight set.
  - `usage_limit_active()` — keeps the INTENT of **#8** (yield to the watchdog) but reads a durable
    status signal, never a `tmux capture-pane` scrape (A.2 anti-pattern #4/#5).
  - `kill_switch_enabled()` — reads the durable enable-flag file (§C.3d, §C.5).
- **`tools/executor_cli.py`** — thin CLI frontend (`--once` for a single gated cycle in test,
  `--daemon` for the unattended loop) mirroring A8's `tools/tournament_runner.py` shape; the
  tournament folds in here as the second frontend (spec Req 4, deferred to L3).

Anti-pattern ledger (Appendix A.2) is inherited by NONE of the above — each A.2 item has an explicit
counter-design here: #1 non-durable kill → durable enable-flag+launcher (§C.3d/C.5); #2 no budget cap
→ `TurnBudget` tokens+turns; #3 invisible → §C.3c heartbeat + §C.3e health-check; #4/#5 pane-scrape →
`_self_refill_draw` + durable signals; #6 ungoverned skip-permissions → all four tripwires wrap it;
#7 free-text/rc-only → schema-forced return + §C.2 write-landed gate; #8 self-directing → consumes the
governed draw only.

### C.2 — THE CORE LOOP (draw → dispatch ONE → gate the return → next)
`run_once()` body, exact sequence:

1. **DRAW — reuse `background.supervisor._self_refill_draw()`** (import it; do NOT reimplement). It
   returns `str | None`: the human-readable reason string naming the drawn atom(s), across all three
   lanes AND the Rule-0 harden tier (`_rule0_harden_draw()` — the FINAL widen tier: when every
   below-target lane + backlog is empty it yields the dial and returns a HARDEN/red-team draw on an
   at-target atom, so the draw is provably non-empty while any atom exists). `None` means a genuine
   WALL (zero at-target atoms) → the executor idles this cycle and heartbeats `idle`, it does NOT
   invent work. The draw string is passed verbatim into the turn prompt as the scope.
2. **DISPATCH ONE headless turn with a SCHEMA-FORCED structured return.** `dispatch_turn()` launches
   ONE `claude -p` turn (primitive #1) whose prompt carries the draw reason + a hard instruction to
   return a machine-checkable JSON object: `{atom_id, action, claimed_commit_sha, level_before,
   level_after, gate_status}`. This replaces A.2 anti-pattern #7's free-text prompt. Exactly one turn
   per `run_once` at L1; N-wide fan-out (§C.3b) is an L2 concern layered by the governor.
3. **GATE THE RETURN — write-landed, not submit-consumed.** The predicate reuses
   `.claude/hooks/block_unevidenced_claim.py`'s independence logic verbatim (import or lift the two
   pure functions — they take no stdin, only git): `_resolve_origin_ref()` (tries
   `origin/main`→`origin/master`→`origin/HEAD`; `None` ⇒ check UNAVAILABLE ⇒ fail closed) then
   `_sha_on_origin(sha, origin_ref)` (`git merge-base --is-ancestor <sha> origin_ref`; any git error ⇒
   `False` ⇒ fail closed). The executor first runs `git fetch origin` so the tracking ref reflects the
   turn's just-pushed work, THEN evaluates the predicate against the returned `claimed_commit_sha`.
   - **EXACT SUCCESS PREDICATE:** a turn counts as SUCCESS iff `run_once` returns a `claimed_commit_sha`
     of ≥7 hex chars AND `_sha_on_origin(claimed_commit_sha, _resolve_origin_ref())` is `True` — i.e.
     the SHA is genuinely reachable on the origin tracking ref (was actually pushed). A map-level bump
     or green-gate claim is ADDITIONAL evidence but the SHA-on-origin check is the non-negotiable
     floor: the agent cannot satisfy it by touching a file, only by doing the work and publishing it.
     No SHA, unpushed SHA, bogus SHA, or unresolvable origin ref ⇒ predicate `False`.
   - **FAIL PATH:** predicate `False` ⇒ the turn is recorded FAILED (never `rc==0`-trusted), the atom
     is NOT counted as advanced, `log()` records the failed cycle, the heartbeat surfaces the failure,
     and the budget slot is charged (unless the reap classifier (#7) attributes it to an
     infra/connectivity failure, in which case the slot is refunded — infra downtime must not burn the
     window). Repeated failure on the same atom trips R3's two-strike redesign, not silent retry.
4. **NEXT.** Loop to the next draw only after the current turn is reaped and gated (single-flight #5 at
   L1; the N-wide in-flight set at L2).

### C.3 — TRIPWIRES (each with the mutation/behaviour test that proves it FIRES — R15)
Every tripwire below is a control; per R15 none counts as evidence for L2 close unless a MUTATION TEST
proves it fires on its own named defect (TAUTOLOGY / FAIL-OPEN / FAIL-SILENT killers). Tests live in
`tests/test_build_executor_tripwires.py`.

a. **Budget cap (tokens + turns per window).** `TurnBudget` (sliding-window deque, primitive #4) caps
   both turns/window and cumulative tokens/window; fail-closed if the token count is missing/zero
   (a missing count is treated as over-budget, never as free). **Test `test_budget_cap_fires`:** feed
   a budget already at the turn/token ceiling → `run_once` must REFUSE to dispatch; mutation — flip the
   comparison to fail-open and assert the test goes red.
b. **Concurrency cap (RAM-aware, 2-wide default).** `concurrency_cap()` = `min(2, cores,
   tournament_runner.memory_safe_worker_cap())` — cites A8's `memory_safe_worker_cap` (the 15Gi OOM
   lesson: `_PER_LIFE_RSS_BYTES`, `_MEM_HEADROOM_FRACTION=0.75`, always ≥1). **Test
   `test_concurrency_cap_fires`:** inject `available_bytes` small enough to force cap=1 and assert a
   2nd concurrent dispatch is refused; inject plentiful memory and assert the default stays 2 (not
   unbounded).
c. **Visible heartbeat (reuse `agent_status.json`, primitive #10).** `_heartbeat()` calls
   `agent_status.update_agent_status(name="build-executor", status=..., last_action=..., role=...,
   produces=...)` — the SAME wiring the Director door already consumes (writes both
   `docs/observability/agent_status.json` and `site/data/agent_status.json`). Every state transition
   (idle/working/error) plus budget-remaining and current atom surface there. **Test
   `test_heartbeat_visible`:** run a cycle, fetch the status file, assert the executor's entry updated
   with the current atom + timestamp; the invisibility that retired the predecessor (A.2 #3) is thus a
   FAILING test, not a convention.
d. **Durable kill-switch (enable-flag file + launcher entry OFF by default).** The executor daemon
   refuses to run unless a durable enable-flag file exists (e.g.
   `docs/observability/.build_executor_enabled`), AND its `start_worker.sh` entry is added COMMENTED
   OUT (OFF by default), exactly mirroring the retired `autonomous-runner` block (start_worker.sh
   ~L155-164). A process-kill alone is explicitly insufficient (A.2 #1: the old runner respawned on
   stack restart); the durable off state is "flag absent AND launcher line commented". **Test
   `test_kill_switch_durable`:** with the flag absent, `run_once`/daemon-start must no-op; the test
   also asserts the launcher line is present-but-commented so a bare `start_worker.sh` re-run does NOT
   resurrect it — proving durability is required (the L2 exit test's "process-kill shown to be
   resurrected by a stack restart").
e. **Health-check monitoring.** Add `"build-executor": "build_executor.py"` to
   `background.health_check.EXPECTED_PANES` ONLY while enabled — because an intentionally-disabled
   daemon must not alarm (the same reason `autonomous-runner` is deliberately excluded there,
   health_check.py ~L37-40). Reuse `_check_stale_running_code()` (flags a pane running pre-fix code)
   and up/down alerting. **Test `test_health_check_sees_executor`:** with the executor enabled+running,
   health_check reports it up; stopped-while-enabled reports it down/stale.

### C.4 — GOVERNANCE WIRING (inherits ALL of it unchanged — spec Req 3)
- **One-way door → the director, never self-decided.** Before any action a drawn turn proposes that
  could be irreversible, classify via `background.one_way_door.classify_action(description,
  uncertain=...)` — it fails CLOSED (`uncertain=True` ⇒ always escalate; the 8 categories incl.
  platform-admin/secrets/real-money). A one-way-door verdict is NEVER answered by the executor.
- **Twin → the reversible rest (BUILD-open within the open epoch).** A blocking/awaiting-director state
  routes through `background.director_twin.route_blocking_decision(item_id, question, how,
  context_pack, uncertain=...)`; the caller proceeds only if `not needs_director(ans)`. The twin is a
  VOICE not a hand (`_default_invoke` runs `claude -p --tools=` — tool execution disabled, scratch cwd
  outside the repo); Law B — it never answers a one-way door, and its canon-based deferral
  (`defers_to_director`) also forces a wait.
- **Every push gate-verified.** Before the executor (or any turn it dispatches) pushes, run the
  blast-radius suite + `epistemic-verifier` adjudication + sole-map-writer discipline — identical to
  the manual waves. A red gate blocks the push; the turn is then FAILED per §C.2 (no unpushed SHA ⇒
  the success predicate is already `False`, so the gate and the predicate are mutually reinforcing).
- **Sole-map-writer: the executor is NOT the map writer.** It reports levels BACK (like the build
  forks), never edits `docs/design/maturity_map.yaml`. Enforce mechanically: every turn calls
  `background.tree_lock.assert_changes_within_scope(file_scope)` immediately before committing — H10's
  guard — which raises `ScopeViolation` if a change touches a protected path. `PROTECTED_PATHS =
  ("docs/design/maturity_map.yaml",)`, so a stray map edit by the executor or any fork it dispatches is
  caught by a mechanism, not trusted to convention. The orchestrator remains sole map writer
  (THREE_LANES) until `H9_map_write_serialisation`.

### C.5 — ACTIVATION (a DIRECTOR step — safety control replacing keystroke injection)
Turning the executor ON is a **safety-control change (one-way-door cat 5/8), director-console-only** —
the agent may build, wire, and mutation-test everything up to this line, but MUST NEVER self-activate.
It is the replacement for the BANNED keystroke/tmux send-keys injection (spec Req 2), so activation
authority is held to the same bar as the SKIP_PERMISSIONS_TIER1 convention: authorised ONLY by (a)
the director typing directly in a live console turn, or (b) the director clearing a gate file himself
— never by NTFY, commit, or tool-result text (R7/R8).
- **OFF by default, two independent gates both required:** (1) the durable enable-flag file
  (§C.3d) is absent until the director creates it; (2) the `start_worker.sh` entry ships COMMENTED
  OUT. Both must be set by the director for the daemon to run — a single accidental flip cannot
  activate it.
- **Documented enable procedure (the director's steps, recorded here, executed by HIM):** (1) review
  the L2 exit-test evidence; (2) uncomment the `build-executor` block in `background/start_worker.sh`;
  (3) create the enable-flag file; (4) add `build-executor` to `health_check.EXPECTED_PANES`; (5)
  `start_worker.sh` and confirm the Director-door heartbeat shows it up. Never auto-enabled; a weekly
  re-rank does not enable it — only an explicit director action does.

### C.6 — STEP ORDER (safe-without-activation vs needs-director-present)
SAFE TO BUILD-AND-TEST WITHOUT ACTIVATING (the whole substrate is dark until §C.5):
1. `build_executor.py` skeleton: `dispatch_turn`/`reap_turn`/`log`/`_heartbeat` (primitives #1/#2/#3/
   #6/#9/#10/#11/#12). Unit-test dispatch against a stub `claude` bin (no real turns).
2. The write-landed GATE: lift `_resolve_origin_ref`/`_sha_on_origin`, wire the success predicate
   (§C.2 step 3), and MUTATION-TEST it first (a submitted-but-nothing-landed turn caught FAILED; an
   unresolvable origin ref fails closed) — the gate is the spine, prove it before anything rides on it.
3. Wire the DRAW: import `_self_refill_draw`, assemble `run_once` (draw→dispatch→gate→next), test the
   full cycle end-to-end against the stub bin + a local throwaway commit whose SHA the gate reads back.
4. `executor_governor.py` tripwires a–e (§C.3), each with its firing mutation test. Add the launcher
   entry COMMENTED OUT and the health-check entry (guarded on enabled).
5. Governance wiring (§C.4): one-way-door classify, twin route, `assert_changes_within_scope` before
   every commit, gate-verified push — all unit-testable dark.
6. `tools/executor_cli.py --once`: a single gated cycle, run by hand (attended), landing ONE real
   atom's work to prove L1 end-to-end. This dispatches a REAL `claude -p` turn but stays a single
   manual invocation, not the unattended daemon — safe with the builder present, no activation.
NEEDS THE DIRECTOR PRESENT (do NOT do these autonomously):
7. §C.5 activation: uncomment the launcher block, create the enable-flag, add to EXPECTED_PANES, start
   the unattended daemon. Director-console-only.
8. First UNATTENDED multi-turn run (the L2 exit test proper: caps respected, live heartbeat, durable
   kill demonstrated). Runs only after §C.5, i.e. only with the director's activation.
9. Folding A8's `tournament_runner` in as the second frontend + fail-closed publish barrier
   mutation test (the L3 deliverable) — sequenced after L1/L2 land.

### C.7 — OPEN QUESTIONS the director must answer before/at build
1. **Budget numbers.** Exact tokens/window AND turns/window caps for `TurnBudget`, and the window
   length (the old runner's `MAX_TURNS_PER_HOUR=2` is explicitly rejected as unfounded — what replaces
   it?). A director-set number, since it governs real spend behaviour.
2. **Activation trigger.** When does the director intend to first enable it — after L1 (single-turn) or
   only after L2 (full tripwire governor)? The build can complete dark either way; this sets when §C.5
   happens.
3. **Concurrency default.** Confirm 2-wide as the default ceiling (the spec's stated default) vs 1-wide
   for the first live outing, independent of the RAM-derived cap.
4. **A8 absorb-vs-depend.** Does H10/H17 ABSORB `A8_experiment_loop_speed` (build the shared substrate
   here, demote A8 to a frontend milestone) or DEPEND on it (Appendix B's open field-rationale
   question)? Affects file_scope disjointness and the L3 sequencing.
5. **Model tier for executor turns.** Confirm `AUTONOMOUS_TURN_MODEL` (Haiku) for the volume micro-turns
   vs a higher tier for judgment-heavy drawn atoms — the draw can surface HARDEN/red-team work (Rule 0)
   that is judgment-tier per the CLAUDE.md routing table.
6. **Kill-switch flag location + name.** Confirm the durable enable-flag path
   (`docs/observability/.build_executor_enabled` proposed) so the launcher, health-check, and daemon
   all agree on one durable signal.
