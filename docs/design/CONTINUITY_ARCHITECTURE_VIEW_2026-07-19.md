# Continuity architecture — a reasoned view (2026-07-19)

**Requested by:** DIRECTOR_DIRECTIVE_SEAT_WORK_AND_CONTINUITY_PROOF_2026-07-19, standing note.
**Question:** is keeping ONE Claude Code session alive indefinitely via stop-hook rearm working
*with* the grain of the tool, or *against* it? A view is asked for before anyone builds a fifth fix.

## Verdict

**Against the grain. Move to scheduled bounded invocations.** Four fixes on this one class in a
single day (RC1, RC3, the rest-heartbeat, the identity fix) is well past R3's redesign threshold —
and R3 says redesign the *mechanism*, not patch it a fifth time. The mechanism to change is the
*persistent seat itself*, not another guard bolted onto it.

## Why the persistent seat fights the tool

1. **The Stop hook is EDGE-triggered.** It fires when a turn *ends*. A drained/rested loop that
   never receives a turn never fires it — "detection is not wake". We have been manufacturing a
   level-triggered "stay alive forever" primitive out of an edge-triggered rearm. That gap is the
   root of the whole class; every fix so far has papered a different corner of the same mismatch.
2. **Identity cannot be pinned across restarts the tool doesn't guarantee.** The drift bug (a seat
   resumed under a live session id != WORKER_SESSION_ID, so the transport rejects every Stop as
   non-worker) is a direct symptom of insisting one long-lived identity survive process churn the
   tool owns, not us. The deterministic `--session-id` seed is a workaround for a requirement we
   imposed, not one the tool offers.
3. **systemd owns processes; a Claude *turn* is not a process we own.** worker_seat.py's own header
   says it: the tmux server holding the session is "the one thing systemd cannot own". The whole
   seat-manager exists to bridge that gap — i.e. to fake process-liveness semantics for a thing that
   doesn't have them. That bridge is the accretion OPS1 was written to forbid.

## Why scheduled bounded invocations work *with* the grain

Each unit of work = one `claude -p` invocation that reads disk/ledger state, does one bounded thing,
and **exits cleanly**. A scheduler (cron / systemd timer) fires the next one.

- **Fresh process, clean lifecycle every time.** No identity to preserve, no rearm to keep alive,
  no edge-vs-level trigger gap. The failure class *cannot recur* because the thing that fails
  (a long-lived seat) no longer exists.
- **Liveness becomes "did the schedule fire?"** — a solved, level-triggered problem — instead of
  "is the one seat still breathing?", which we have now failed to answer robustly four times.
- **IaC-native (OPS1's core).** The schedule is committed; reconstruct-from-repo holds; no
  hand-held tmux state determines behaviour. This is the transferability that is the product.
- **Already the project's other model.** `autonomous_runner.py` and the `claude -p` turn path
  already work this way; state already lives on disk (staged docs, the map, the ledgers). The
  pull-loop's own inputs are all disk-resident — nothing genuinely requires a resident process.

## The one real tradeoff, and why it's acceptable

The resident seat's only genuine advantage is sub-minute reactivity to a staged doc without polling.
But the rest-heartbeat already bounded that to ≤60s, and a 60s timer delivers the same reactivity
with nothing to keep alive. Per-invocation cold-start latency is real but immaterial at this cadence.

## Evidence update (2026-07-19 evening) — the incident that moves this from reasoning to proof

`DIRECTOR_FINDING_HEARTBEAT_BLOCKED_INPUT_2026-07-19`: after the bring-up turn the seat entered the
rest-heartbeat and the director typed a work-granting instruction into the pane. It was **queued for
~27 minutes, not delivered** — recovery required the director pressing Escape to interrupt the hook.
A mechanism built to make waking *possible* made the most direct wake path — the human typing —
**impossible**.

**Root cause, with evidence.** The heartbeat sleeps in-hook (`pull_next_work.py`:
`time.sleep(60)` in a loop up to `HEARTBEAT_HOLD_SECONDS = 480`, then re-arms). The per-beat bound
*held* (480 < the 600s hook timeout); the 27 minutes was cumulative re-arming across beats. While the
hook subprocess runs, the session is occupied and cannot process input.

**Is input-blocking intrinsic to in-hook polling? Yes** (confirmed against Claude Code's documented
behaviour, not assumed): a running Stop hook cannot detect that input is pending, there is **no
documented mechanism for a hook to yield to pending input** or to run short beats and let the session
process input between invocations, and `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` is orthogonal (it caps block
*count*, not input handling). Shortening the beat would reduce the worst-case block but **cannot
deliver the "never block input" hard property** — as long as the wake mechanism is "keep the hook
busy to hold the chain open," the hook being busy *is* what blocks the human. The property and the
mechanism are in direct contradiction within the in-hook model.

**This is the decisive point.** The persistent-seat model cannot simultaneously (a) stay alive by
occupying the hook and (b) remain instantly steerable — they are the same resource. Scheduled bounded
invocations dissolve the contradiction: between invocations the session is *not running*, so a human
(or a timer, or a staged doc) reaches it immediately; nothing is held hostage. The "never block
director input" requirement is therefore not a patchable bug in the current heartbeat — it is a
**property only the scheduled-invocation architecture can satisfy**. Requirement 4 of the finding,
answered plainly: input-blocking is intrinsic; this strengthens the case for scheduled invocations
and against a fifth patch to the persistent seat.

## What I am NOT doing

This is a view, per the director's request — not the fifth fix. I have **not** changed any
scheduling infrastructure, systemd unit, or the seat model, and — deliberately — **have not patched
the live Stop-hook wake path overnight** to chase the "never block input" property. The finding
itself warns not to destabilise the working wake path (load-bearing, only just proven), and the
analysis above shows the property is unreachable by a hook-timing tweak anyway: a partial change
would carry real risk (stranding the seat) for no guarantee. Shortening the beat is the only
in-model mitigation and it is a palliative, not the fix.

Building the scheduled-invocation shape (and retiring the seat) is an operational-layer redesign
(OPS1) and touches scheduling/platform-administration — the director's to open. If he agrees, the
next step is a small OPS1 design pass: define the bounded work-unit, the timer, and the disk-state
contract, carry the R15 property **"director input during any active state is acted on promptly,
never queued indefinitely"** as an acceptance test, then migrate behind a dark flag with the seat as
fallback until proven.
