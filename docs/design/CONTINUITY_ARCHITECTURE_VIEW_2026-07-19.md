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

## What I am NOT doing

This is a view, per the director's request — not the fifth fix. I have **not** changed any
scheduling infrastructure, systemd unit, or the seat model. Building the scheduled-invocation shape
(and retiring the seat) is an operational-layer redesign (OPS1) and touches
scheduling/platform-administration — the director's to open. If he agrees, the next step is a small
OPS1 design pass: define the bounded work-unit, the timer, and the disk-state contract, then migrate
behind a dark flag with the seat as fallback until proven.
