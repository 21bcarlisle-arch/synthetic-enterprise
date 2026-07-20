# Scheduled Bounded Invocations — the continuity transport, redesigned (2026-07-20)

**Status:** DESIGN + OFFLINE BUILD. Dark (not live). Cutover is director-gated and director-run
(it retires the seat this session runs in — see §8).
**Authorizes-from:** director console 2026-07-20 ("Do the migration properly and prove all three
properties together: cheap at rest, wakes on a staged doc, never blocks input").
**Supersedes the transport of:** the persistent stop-hook-rearm worker seat + its rest-heartbeat.
**Evidence trail (why, not preference):** `CONTINUITY_ARCHITECTURE_VIEW_2026-07-19.md`,
`REST_HEARTBEAT_TOKEN_BURN_ANALYSIS_2026-07-20.md`, and the two director findings
(`DIRECTOR_FINDING_HEARTBEAT_BLOCKED_INPUT_2026-07-19.md`,
`DIRECTOR_FINDING_HEARTBEAT_TOKEN_BURN_2026-07-20.md`).
**OPS1 mandate this serves:** `OPERATIONAL_LAYER_DESIGN.md` — no operational mechanism without a
stated purpose/guarantee/why; IaC (reconstruct-from-repo); simplicity guard.

---

## 1. PURPOSE (the north-star this traces to)

The company must keep working autonomously without a human holding a session open, AND the director
must be able to steer it and read it at any moment. The continuity transport is the mechanism that
delivers "keep working" between director touches. It must be **cheap when there is nothing to do,
promptly awake when there is, and never in the way of the human.**

## 2. WHY THE PERSISTENT SEAT IS THE WRONG SHAPE (three production failures, one root)

One long-lived `claude` session, kept alive by a Stop hook that re-arms itself, failed three
independent ways in ~30 hours — all traceable to *a resident turn-chain that must pay inference to
stay alive*:

1. **Input-blocking (27 min).** The in-hook rest poll (`pull_next_work.py::_rest_heartbeat`,
   `time.sleep` up to `HOLD=480s`, then re-arm) occupies the session; a running Stop hook cannot
   yield to pending input. The director typed a work grant; it queued 27 min until he pressed Escape.
2. **Death on a transient API error (~6 h).** The seat died mid-response at 23:51 and stayed dead all
   night. The re-arm mechanism *is* the dead process — a hook only runs when a turn ends, and a dead
   process ends no turns. Detection fired (transport frozen, deadman, publish gate wedged 16×);
   nothing external could restart it.
3. **Token burn at rest (~128.7k tok/h).** Each keep-alive beat is a full model turn re-reading the
   whole (growing) context. Resting *cost more the longer it rested* — the opposite of rest.

These are not three bugs to patch. They are one architectural mismatch: **a level-triggered
"stay-alive" requirement built out of an edge-triggered (turn-ends) primitive.** R3 says redesign the
mechanism, not patch it a fifth time. The mechanism is the persistent seat itself.

## 3. THE SHAPE — scheduled bounded invocations

Replace the *resident, self-holding* chain with a *transient, externally-triggered* one.

```
  systemd .timer (every 60s) ─┐
                              ├─▶ worker-tick.service (oneshot) ─▶ background/worker_tick.py
  systemd .path (staging/) ───┘        │
                                       │  cheap Python, NO model:
                                       │   1. autonomy enabled?          (.build_executor_enabled)
                                       │   2. an invocation already live? (lockfile)   → exit 0
                                       │   3. sync origin-staged (RC3) + find_work()
                                       │        └─ no work  → exit 0        ◀── ZERO tokens (rest)
                                       │        └─ work     → spawn ONE:
                                       ▼
                          claude -p "<doorbell>"   (headless, env SE_SBI_WORKER=1)
                                       │  runs its natural agentic session: reads disk state,
                                       │  acts, commits — then EXITS. No self-re-arm.
                                       ▼
                                     exits ─▶ next .timer/.path tick starts a FRESH one if work remains
```

- **At rest**: the tick is a few ms of Python and **spawns nothing** → literally zero inference.
  Idle cost is O(0), not O(context)·(beats). *(P1)*
- **A new local staged doc**: the `.path` unit fires the tick within ~seconds. An origin-staged doc:
  the 60s `.timer` tick runs `_sync_origin_staging()` then `find_work()` and catches it. *(P2)*
- **The human**: nothing resident holds a session. The director's interactive session (§7) is a
  *different* process the tick never touches; it is always immediately responsive. *(P3)*
- **Death of an invocation**: it ends one process; the next tick starts a fresh one from disk state.
  A crash is a skipped tick, not an outage. *(kills failure class 2 by construction)*

### Why one invocation = one bounded work session (not a re-armed chain)

`claude -p "<prompt>"` already runs a *full* agentic session (many internal turns: read, edit, test,
commit) until the model naturally stops, then exits. The old Stop-hook `block+continue` existed only
to *artificially chain a second atom into the same session*. We do not want that: we want a clean
exit and let the **external** scheduler start the next one. So in scheduled mode the Stop hook does
**nothing but allow-stop** — no draw, no block, no heartbeat. The timer/path own re-arming. This is
the whole point: the unreliable thing (an in-process self-re-arm) is replaced by a reliable external
one (a systemd timer), which is a *solved, level-triggered* problem.

## 4. THE IDENTITY SIMPLIFICATION (this deletes the drift-bug class)

The persistent seat had to pin one `WORKER_SESSION_ID` across process churn the tool owns; a resume
reassigned the live id and the Stop-hook worker-guard rejected the seat as "non-worker" — the
2026-07-19 deadlock. Scheduled invocations get a **fresh session id every time** and never need one
pinned. The Stop hook discriminates the worker not by a fragile fixed id but by an **environment
variable the tick sets on the invocation it spawns** (`SE_SBI_WORKER=1`), which the Stop-hook
subprocess inherits. The director's interactive session has no such env → it is never the worker →
never pulled. **There is no identity to drift.** (`worker_seat.py`'s `_live_session_id`/`_classify_seat`
drift machinery is retired at cutover — flagged for the rebuild pile, not kept as an anchor.)

## 5. GUARANTEES (and how each is proven — R15)

| # | Property | Mechanism | Proof (mutation / offline) |
|---|----------|-----------|----------------------------|
| P1 | Cheap at rest (~0 tok) | tick spawns `claude -p` **only** when `find_work` returns work | `test`: drained-and-gated draw → `_should_spawn` is False → no subprocess. Mutation: force a work draw → it *would* spawn. |
| P2 | Wakes on a staged doc | `.timer` (60s, origin-sync+draw) **and** `.path` (local, immediate) both fire the tick | `test`: a staged doc present → `find_work` non-None → tick spawns. R15: disable `.timer` → `.path` still wakes; disable `.path` → `.timer` still wakes (two independent triggers). |
| P3 | Never blocks input | no resident session held by a hook; Stop hook allow-stops always in scheduled mode; worker is headless | `test`: Stop hook in scheduled mode with a non-worker payload → allow-stop; with SE_SBI_WORKER but scheduled-mode → allow-stop (no heartbeat). Structural: no `time.sleep` on the rest path. |
| — | Autonomy kill-switch honoured | tick checks `.build_executor_enabled` (fail-closed) first | `test`: flag absent → tick spawns nothing. |
| — | No stacking / runaway bound | lockfile with a live-pid check; only one invocation at a time | `test`: lock held by a live pid → tick exits without spawning; stale lock (dead pid) → reclaimed. |
| — | No silent dead chain | both triggers are systemd-owned; loss of one is reconcile-visible | reconcile-watch already alarms on a declared-but-missing unit. |

## 6. WHAT CHANGES, WHAT STAYS (blast radius)

**New (all dark until cutover):**
- `background/worker_tick.py` — the cheap tick + bounded spawn + lock.
- `background/worker-tick.service` / `.timer` / `.path` — systemd IaC (installed *held*: not started).
- `background/director_console.sh` — the deliberate interactive path (§7).
- `background/cutover_to_scheduled.sh` — the director-run, from-outside cutover (§8).

**Modified (behind a flag — the live seat is UNAFFECTED until the flag flips):**
- `.claude/hooks/pull_next_work.py` — adds scheduled-mode: when
  `docs/observability/.scheduled_invocations_enabled` exists, `decide()` allow-stops always (no draw,
  no heartbeat); the worker discriminator becomes `SE_SBI_WORKER`. When the flag is absent, behaviour
  is byte-for-byte the current persistent-seat heartbeat (fallback preserved).
- `background/schedule_manifest.yaml` — declares the three new units (held), so reconcile sees them.
- `.claude/settings.json` — at cutover, `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` reverts to default (no more
  keep-alive blocks to cap). Not before.

**Unchanged / retired at cutover:** `worker_seat.py` + `worker-seat-manager.service` (retired — no
resident seat to manage). `supervisor.py::find_work` stays the sole draw authority. `deadmans-switch`,
`reconcile-watch`, `file-api` unchanged.

**`staging_watcher.py` is NOT superseded (corrected 2026-07-20):** its tmux send-keys wake was already
DELETED at the 2026-07-15 pull-loop migration; its remaining roles — NTFY the *director* on a new
staged doc, surface `[ADVISOR-STAGED]` origin commits, and housekeeping sweeps — are director-facing
and independent of the worker wake. The `.path` unit wakes the *worker*; staging_watcher notifies the
*director*. Both stay. (A pre-existing, migration-independent drift was found while checking this: the
staging-watcher daemon had died with nothing to restart it — the same no-external-restarter class —
alarming since 09:14Z, ~2h before this migration's first commit. Restarted via its systemd unit
2026-07-20; both reconcilers back to 0 drift.)

**Reconcile done-gate:** `cutover_to_scheduled.sh` asserts BOTH reconcilers (schedule units + process
daemons) show 0 drift before cutover counts as done — a migration that leaves the reconciler alarming
is not done. Pre-cutover the worker-tick units are declared dark and installed inert (0 drift); at
cutover the manifest enable/active flip is committed atomically with the systemctl enable+start so the
declaration never lags reality (avoiding the transient declare-before-install drift seen at 11:00Z).

## 7. THE DELIBERATE INTERACTIVE PATH (director requirement, 2026-07-20)

> *"After cutover there is no persistent seat to attach to. Preserve a deliberate path for me to
> interact directly when I need it."*

**`background/director_console.sh`** launches an on-demand interactive Claude Code session in the
repo (`claude --dangerously-skip-permissions --model claude-opus-4-8`, fresh session, no
`SE_SBI_WORKER`). Properties, by construction:
- It is **never the worker** (no `SE_SBI_WORKER` env) → the Stop hook allow-stops it; the timer never
  delivers work into it; it is never held open by a heartbeat.
- It is **always immediately available and responsive** — because nothing resident holds a lock or a
  session, there is no queue to wait behind (the exact failure of the old seat). The director types,
  it acts, he closes it or leaves it; when he leaves, it simply idles at ~0 cost (allow-stop) and the
  scheduled worker keeps running headless underneath.
- It **coexists with the worker**: worker `claude -p` invocations run headless; commits from either
  are serialized by the existing `tree_lock`. Concurrent writers are already handled.

So the director's channels after cutover are: (a) staging (async, as now), (b) NTFY (as now), and
(c) `director_console.sh` — a live interactive seat on demand, which the migration makes *more*
reliable than the old shared seat, not less.

## 8. CUTOVER (director-gated, director-run, from OUTSIDE the seat)

The cutover **retires the persistent seat — which is the session this design was written in.** A
process cannot cleanly kill itself mid-turn, so cutover is a script the director runs from a separate
shell (same pattern as `bounce_worker_seat.sh`):

`background/cutover_to_scheduled.sh` (idempotent, ordered, each step reconcile-checked):
1. Create `docs/observability/.scheduled_invocations_enabled` (Stop hook stops heartbeating; any live
   seat now allow-stops cleanly at its next rest instead of burning tokens).
2. `install_schedule.sh` installs + **starts** `worker-tick.timer` and `worker-tick.path`; flips their
   manifest declaration to enabled/active.
3. Stop + disable `worker-seat-manager.service`; retire the tmux `claude` seat (the old seat exits at
   its next allow-stop, or the director kills the tmux session by id).
4. Revert `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` to default in settings.json.
5. Reconcile → expect 0 drift; NTFY one cutover-complete summary.

**Rollback** (if the scheduled path misbehaves live): delete `.scheduled_invocations_enabled`, stop
the two units, re-enable `worker-seat-manager.service`. The persistent-seat heartbeat is byte-for-byte
intact behind the flag — fallback is a flag flip, not a rebuild.

## 9. WHAT THIS DELIBERATELY DOES NOT DO

- **Not the resource-aware fan budget** (`DIRECTOR_STEER_RESOURCE_AWARE_SCHEDULING`). The director
  sequenced that separately ("do NOT change the draw and the fan cap in one turn"). This migration is
  the continuity *transport* only; the parallel-fan budget is a distinct follow-up.
- **No new metadata, no cathedral.** Two systemd unit types + one ~150-line Python tick + one env-var
  discriminator. The disk-state contract (`find_work`, staged docs, ledgers) already exists; this
  re-points the *trigger*, it does not rebuild the *draw*. (Simplicity guard.)

## 10. LIVE CUTOVER OUTCOME (2026-07-20) — done, and how it differs from the §8 plan

Cut over live from inside the seat (the old pull-loop transport had frozen at 11:45; the deadman
fired — the failing transport *was* the argument to finish, not defer). What happened:

1. **Scheduled flag set** → the Stop hook allow-stops every session (worker `decide()` → `None`).
   The rest-heartbeat / token-burn is **dead immediately**, for all sessions.
2. **`worker-tick.timer` + `.path` enabled + started** (manifest flipped enabled/active; committed IaC).
   Both `active/enabled`; the timer fired within seconds.
3. **PROVEN LIVE, in production, on the director's real work:** the first tick drew the staged
   `DIRECTOR_STEER_POPULATION_COVERAGE_DESIGN` doc and spawned a bounded `claude -p` worker
   (SE_SBI_WORKER=1) to consume it — P2 (wake-on-staged-doc → bounded invocation) demonstrated end
   to end, not just in tests.
4. **Both reconcilers 0 drift.**

**Deliberate deviation from §8 — the seat and its manager are KEPT, not retired.** Retiring the
`claude` seat entry while this session runs *in* it would either self-kill (killing the tmux session
is killing this process) or trip a `RETIRED_RUNNING` alarm until the seat closes — a persistent
alarm, which the director forbade. And it turns out retirement isn't needed to kill the class:
**scheduled mode neuters the resident seat.** It can no longer heartbeat (→ can't block input, can't
burn tokens), and its death no longer causes a work outage because work continuity is now the
external timer, wholly independent of the seat. So the resident `claude` session becomes a harmless,
~0-cost **idle director console** (kept alive by worker-seat-manager, whose role is redefined from
"keep the autonomous worker alive" to "keep the director's console available") plus the on-demand
`director_console.sh`. All three failure MODES are eliminated even though the seat OBJECT remains.
Full retirement of the seat + manager is now **optional future cleanup** (do it when a session is
*not* running in the seat), not a required, self-kill-adjacent handoff. The `CLAUDE_CODE_STOP_HOOK_
BLOCK_CAP` in settings.json is left as-is (harmless in scheduled mode; settings is director-owned).

**Rollback** unchanged: delete `.scheduled_invocations_enabled` (hook → heartbeat fallback), stop the
two units. The persistent-seat path is byte-for-byte intact behind the flag.
