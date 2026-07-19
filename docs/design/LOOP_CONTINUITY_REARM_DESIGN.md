# Loop-continuity re-arm — the redesign (R3, second attempt at this class)

**Provenance:** director, 2026-07-19 console: *"RC3 did not achieve origin-wake … detection is not
wake … Diagnose the layer distinction before patching … R3 applies: redesign rather than patch, and
prove it by leaving a staged doc and showing it consumed with no console input."*
**Supersedes the RC3 patch's continuity claim** (`9ada5f245`, `_sync_origin_staging`). RC3 stays as a
*visibility* helper; it was never the wake. See `LOOP_CONTINUITY_FAILURE_DIAGNOSIS.md` for RC1/RC3.

---

## 0. Purpose / guarantee / why (OPS1 — state these FIRST)

- **Purpose:** the autonomous worker seat must resume drawing work on its own after it comes to rest,
  when — and only when — real work appears, with no human input and no keystroke injection.
- **Guarantee (the invariant to prove):** *while autonomy is enabled, the worker's turn-chain is never
  in a terminal dead state from which only external input can revive it.* A rested seat re-checks
  `find_work()` on a bounded clock and continues the moment work exists.
- **Why it broke:** the pull-loop migration (2026-07-15) deleted keystroke injection (banned; five
  deaths) and demoted the supervisor to a mute watchdog, making the **Stop hook the sole transport**.
  A Stop hook is *edge-triggered* — it fires only when a turn ends. Nothing re-fires it at rest. The
  one component that used to cold-start a rested pane on a timer, `autonomous_runner.py`, was retired
  in the same migration and never replaced. Continuity has had no heartbeat since.

---

## 1. The layer distinction (the director's question, answered)

There are **two callers of `find_work()`**, and they live in different layers with opposite properties:

| | Stop hook `pull_next_work.py` | Supervisor `supervisor.py` |
|---|---|---|
| Trigger | **edge** — only when a turn ends | **level** — `while True: sleep(120)` |
| Can it deliver a turn to the pane? | **YES** (block+continue → next turn's input) | **NO** — `grant_turn()` does zero pane writes since the pull-loop migration; it only logs "work identified for the pull-loop to deliver at the next turn boundary" |
| Runs at rest (no turn in flight)? | **NO** — no turn boundary → never invoked | **YES** — every 120s |

The two are **severed**: the layer with the clock (supervisor) *cannot act*; the layer that *can act*
(Stop hook) *has no clock*. `find_work()` runs every 120s in the supervisor — and after RC3 even pulls
the origin-staged doc into the local tree — but that layer is a mute observer. The layer that could put
a turn into the pane is only invoked at a turn boundary, and **at rest there are no turn boundaries.**

**Why RC3 changed nothing.** RC3 made `find_work()` origin-aware. `find_work()` *is* invoked every
120s — by the supervisor, the layer that cannot deliver. So the doc became *visible* within 2 min and
was *seen* every cycle (supervisor-log: "Work identified … DIRECTOR_STEER_CONTEXT_AS_MANAGED_RESOURCE
…" repeated 14:34→14:45) — and *never delivered*. RC3 fixed visibility; the missing half was always
re-arm. The director's framing is exact: *"making `find_work` origin-aware only helps if something
INVOKES find_work"* — in the layer that can act, on a clock. Nothing does.

**Why the earlier "RC2 retracted — supervisor IS the re-arm" was wrong.** The supervisor *cycles*
fine, but cycling ≠ re-arming. It was stripped of turn-delivery in the migration. "The level loop is
alive" was mistaken for "the level loop can wake the worker." It can't. That *is* the continuity gap.

### Evidence (observed, not inferred — R9)
- `pull-loop-log.md`: last Stop-hook action **13:14:42 UTC**, `drained-and-gated -> allow stop`. The
  chain died there. Health file: `ALLOW_STOP_QUIET_WAIT`.
- `supervisor-log.md`: from **14:34 UTC** every 120s cycle logs the staged doc "identified … to deliver
  at the next turn boundary" — a boundary that never came — until **14:47 "Session busy"** (a turn
  finally began, because the **director typed into the pane** — the very console input RC3 was meant to
  make unnecessary).
- So ~13:14 → 14:47 the seat sat idle with an unprocessed staged doc detected every cycle, undelivered.

### The absorbing-state trap
`drained-and-gated → allow stop` was introduced (ADVISOR_STEER 2026-07-18 item 1) as a *legitimate
resting state* to stop the at-target HARDEN re-verification treadmill. Its own comment claims: *"a
staged doc … wakes the loop on the next turn — responsiveness intact."* **That claim is false at rest:**
it wakes on *the next turn*, but an allow-stop *is the end of the chain* — there is no next turn. So
drained-and-gated is not a resting state; it is a **terminal absorbing state**, reachable only by
killing the sole wake path.

---

## 2. Why patching `find_work` again cannot work (R3 → redesign)

The defect is not in `find_work` (it draws correctly and, post-RC3, sees origin docs). The defect is
that **nothing invokes the transport at rest.** Any further change *inside* `find_work` — more
origin-awareness, faster rate-limit, a new signal — is invisible until something calls it in a layer
that can deliver a turn. This is the second attempt at "wake on staged work" (RC3 was the first), same
class, so R3 forbids another patch. The redesign must **restore a clock to the transport itself.**

---

## 3. Design constraints (what any fix must respect)

- **W1 — no keystroke/`send-keys` injection into the pane.** Banned; five deaths. Non-negotiable wall.
- **W2 — console sanctity (G-L1).** The mechanism acts on the *worker seat only* (session-id filtered,
  exactly as the Stop hook already does), never the director's console.
- **W3 — no accretion (OPS1).** Reuse the existing sole transport; do not revive a second parallel
  turn-launcher (the retired `autonomous_runner`) or add a new bespoke process. One mechanism, designed.
- **W4 — the kill switch still kills.** Autonomy-off (`.build_executor_enabled` absent) must still lead
  to a real, terminal stop. The immortality applies *only while autonomy is enabled*.
- **W5 — don't reintroduce the treadmill.** The 2026-07-18 steer's intent (stop burning tokens
  re-verifying finished atoms) must hold: resting must not *do HARDEN work*; it may only *wait and
  re-check* at near-zero cost.
- **W6 — R15.** Prove the re-arm fires by a mutation test: reverting the change must make a
  "wakes-on-new-work-while-at-rest" test FAIL.

---

## 4. Acceptance test (the director's proof — "staged doc consumed with no console input")

A closed-loop, no-console test, run live:
1. Bring the seat to rest (end this turn; the chain enters the heartbeat).
2. A **background process** (systemd/`sleep`-scheduled, *not* the console, *not* me typing) drops a
   test file into `docs/staging/` after the seat is at rest.
3. Within one heartbeat interval, the seat begins a new turn whose input is the staged-doc doorbell —
   with **no console input between rest and wake**.
4. Evidence: the pull-loop-log shows `…-> allow stop`/heartbeat, then a `BLOCK+continue … unprocessed
   staging -- <testfile>` with a timestamp after the drop; the transcript shows the consuming turn; the
   director-input log shows no human input in the window. Then the test file is archived.

This test is *inherently cross-turn* (the wake must be performed by the mechanism, not by the turn that
built it) and is the definition of done for this atom — no completion claim before it is shown green.

---

## 5. The mechanism — heartbeat the transport (in-hook bounded poll)

**Reconnect the clock to the transport by making the Stop hook self-clock while resting**, instead of
allow-stopping into death. This keeps everything inside the existing sole transport (W3), needs no
send-keys (W1) and no console contact (W2).

Change is confined to `pull_next_work.py::decide()`'s **drained-and-gated branch only** (and the Stop
hook's `timeout` in `settings.json`). Every other branch is unchanged:
- kill-switch-off → allow-stop (die) — **unchanged** (W4).
- non-worker/console session → allow-stop — **unchanged** (W2).
- real work found → block+continue immediately — **unchanged**.
- `DRAW_EMPTY_UNEXPECTED` (map broken under Rule 0) → allow-stop + loud alarm — **unchanged**.

**New drained-and-gated behaviour (worker seat, autonomy ON):** enter a bounded in-hook poll instead of
allow-stopping:

```
elapsed = 0
while elapsed < HEARTBEAT_HOLD_SECONDS:      # bounded well under the hook timeout
    sleep(HEARTBEAT_POLL_SECONDS)            # e.g. 60s
    elapsed += HEARTBEAT_POLL_SECONDS
    reason, exhausted = find_work(...)       # re-runs the RC3 origin-sync + staging scan + draw
    if reason and not <still-drained-and-gated>:
        return block+continue(reason)        # WAKE — real work appeared, deliver it
# no work within the hold window: emit ONE minimal re-arm continuation so the Stop
# cycle refreshes and the poll resumes next boundary (keeps the chain immortal at
# ~one trivial turn per hold window — near-zero tokens, honours W5)
return block+continue("[REST HEARTBEAT] drained-and-gated; no new work in the last "
                      "<hold>s. Do nothing and stop immediately — you are correctly resting.")
```

- **Answer to "what invokes `find_work` at rest":** the resting Stop hook itself, on its own
  `HEARTBEAT_POLL_SECONDS` clock. The transport becomes level-triggered by holding its own boundary
  open and polling — no second process, no keystrokes.
- **Latency:** ≤ `HEARTBEAT_POLL_SECONDS` (target 60s) — as responsive as, and independent of, the
  supervisor's 120s.
- **Cost:** while resting, the hook sleeps (near-zero); at most **one trivial "resting, stop" turn per
  `HEARTBEAT_HOLD_SECONDS` window** — it does no HARDEN work (W5).
- **Crash path is already covered:** if the seat *process* dies, `worker_seat.py` re-seeds it; the
  bring-up turn ends → Stop fires → this hook continues on any available work (or heartbeats). No
  separate cold-starter needed (W3).
- **Health signal:** a new typed outcome `HEARTBEAT_REARM` (distinct from `ALLOW_STOP_QUIET_WAIT`) so
  the deadman/reconciler can tell "resting-but-alive" from "stopped". A drained seat that is *no longer*
  heartbeating is now itself an alarmable condition (a rested seat must show a fresh heartbeat stamp).

**Numeric params (`HEARTBEAT_POLL_SECONDS`, `HEARTBEAT_HOLD_SECONDS`, Stop-hook `timeout`) are set from
the confirmed Claude Code Stop-hook timeout semantics** — the hold window sits safely under the
configured hook timeout; the timeout is raised in `settings.json` to accommodate it. If long-held Stop
hooks prove unsafe, the fallback is the *near-empty heartbeat-turn* variant (block+continue a trivial
"resting" turn immediately, delay enforced by the turn running a bounded `sleep` poller) — same
guarantee, delay moved from the hook into the turn. Chosen variant and final numbers recorded in §6 on
build.

---

## 6. Build log (filled as sub-steps land — one verified step at a time; no premature "done")

- [ ] Confirm Stop-hook timeout semantics; fix numeric params + variant. → §5
- [ ] Implement drained-and-gated heartbeat in `pull_next_work.py`; raise Stop-hook `timeout`.
- [ ] R15 mutation test (revert heartbeat → "wakes-at-rest" test FAILs). Fast gate green.
- [ ] Arm live; commit+push via `tree_lock`.
- [ ] Run the §4 acceptance test (no-console staged-doc drop) and paste the evidence here.
- [ ] Only then: mark the continuity atom re-armed; NTFY the conflict resolved.
