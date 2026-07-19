# Retro — worker-seat identity drift: the doorbell rang at a stale address (2026-07-19)

## One-line
The whole 2026-07-19 continuity class (RC1, RC3, the REST HEARTBEAT) targeted the **draw**, while the
real fault was that the **worker seat wasn't recognised as the worker at all** — the transport was
delivering to a session id no live seat was running under. Fixing the message while the address was stale.

## Timeline (observed unless marked inferred)
- Pre-13:14 — worker seat took turns normally (pull-loop-log: worker-recognised `drained-and-gated → allow stop`).
- 13:14 — last worker-recognised Stop; chain rested.
- ~13:14–15:xx — the seat's live session id changed to `da80a780…` (**inferred:** this Claude Code build reassigns the session id when launched with `--resume`; the seat was seeded `--resume 22080be5…`).
- 15:13 / 15:19 — Stop hook logs `non-worker session (session_id=da80a780…) → allow stop`. The seat is now **invisible to the transport** (`da80a780… ≠ WORKER_SESSION_ID 22080be5…`), so it never gets work — and `worker_seat.py` sees `tmux "claude"` alive and never re-seeds. **Deadlock: alive-but-wrong-identity, neither fed nor healed.**
- Earlier the same session: RC1 (starved draw), RC3 (origin-blind `find_work`), and the REST HEARTBEAT (drained chain dies at rest) were each diagnosed and fixed — all real gaps, all in the **draw/transport-cadence** layer, none of which could help while the seat was unrecognised.

## Root cause (the director's framing, adopted)
**Identity drift.** The seat was running under a session id different from `WORKER_SESSION_ID`, so the
pull-loop's worker-seat guard rejected every Stop as non-worker. RC1/RC3/heartbeat all "fixed the draw
while the doorbell was ringing at a stale address." Two enabling defects:
1. **Seeding was non-deterministic** — `--resume` reassigned the live id on this CC build.
2. **Keep-alive checked liveness, not identity** — `_session_alive()` was `tmux has-session -t claude`; it
   could not tell "the *right* seat is up" from "*a* session named claude is up." A fail-silent liveness
   signal, same class as the 6h-blackout watchdog whose liveness beat was one it could refresh itself.

## Fixes
- **`worker_seat.py` (this retro's atom):** seed **deterministically** with `--session-id WORKER_SESSION_ID`
  (never `--resume`; archive any stale transcript first), and make keep-alive **identity-aware** —
  `_classify_seat` returns `drift` when the live id ≠ `WORKER_SESSION_ID` and REPORTS it loud (the
  reconciler/deadman pages) rather than resting it as healthy. **No-reap invariant preserved:** the manager
  never kills; the actual bounce is the director's console-authorized `bounce_worker_seat.sh`. R15 mutation
  tests: deterministic-not-resume, drift-detected-not-healthy, unknown-id-not-a-false-drift, drift-never-reaps.
- **REST HEARTBEAT (`pull_next_work.py`, kept):** still correct and necessary — once the seat is recognised,
  a drained chain must heartbeat rather than die. It was simply downstream of the identity guard, so it
  couldn't engage on the drifted seat.
- **The bounce (`bounce_worker_seat.sh`, director-run, from outside the seat):** deploys the fix + re-seeds a
  clean recognised seat, which then arms the heartbeat.

## Lessons / candidate rules
- **L1 — verify the address before fixing the message.** Before diagnosing the *draw*, confirm the work is
  reaching a *recognised* consumer. The end-to-end delivery path (seat identity → transport recognition →
  draw → wake) must be checked whole; I fixed three draw-layer gaps before checking whether the seat was even
  identified. Extends **R4** (name the working analogue; here: "was the doorbell wired to a live address?").
- **L2 — a liveness check must verify IDENTITY, not mere existence.** "Something is up" ≠ "the right thing is
  up." A keep-alive/health signal that can't distinguish the correct instance from any instance is
  fail-silent by construction. Generalises [[feedback_fail_silent_control_patterns]].
- **L3 — verify your own session before any process action.** I was one step from `kill 2195894` to "restart
  the worker" — which was **my own PID**. An ancestry check caught it. Any restart/kill of a seat must first
  prove the target PID/session is not the actor. (Near-miss, not an incident — averted by verification.)
- **L4 — evidence must settle the CLAIM, not just kill the scary narrative (R9, applied twice).** I first
  asserted "no re-arm exists," retracted it on the supervisor log, then over-corrected into "the supervisor
  IS the re-arm" — also wrong. Two wrong conclusions from partial reads. Read enough to decide the claim, not
  just enough to abandon the first guess.
