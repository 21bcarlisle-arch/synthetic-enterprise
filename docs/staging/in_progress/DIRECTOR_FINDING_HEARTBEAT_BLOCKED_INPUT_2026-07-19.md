> **PARKED (2026-07-19, agent response).** Analysis DONE and recorded in docs/design/CONTINUITY_ARCHITECTURE_VIEW_2026-07-19.md: root cause is the in-hook sleep (pull_next_work.py, HOLD=480s); per-beat bound held, the 27min was cumulative re-arm; and input-blocking is INTRINSIC to in-hook polling (a running hook cannot yield to pending input -- confirmed vs Claude Code documented behaviour). The 'never block director input' hard property is therefore NOT patchable by a hook-timing tweak -- it is only satisfiable by the scheduled-invocation architecture.
>
> **OPEN sub-item (blocking):** the never-block mechanism itself. **What unblocks it:** the director's decision to open the scheduled-invocation redesign (OPS1 + scheduling = platform-administration, director-reserved). Deliberately NOT patching the live Stop-hook wake path overnight (the finding's own 'do not destabilise the working wake path' + a partial fix risks stranding the seat for no guarantee). The R15 acceptance property is carried into the redesign's DoD.

---

# DIRECTOR FINDING — The rest-heartbeat blocked director input for 27 minutes (2026-07-19, 22:37 BST)

**Type:** [STEER] — an incident record with a fix requirement. Absorb; do not interrupt in-flight work.

## What happened (observed at the seat, therefore invisible to git — this record is the only trace)

After reporting the three directive items complete, the seat entered the rest-heartbeat and ran the Stop hook continuously for **27 minutes**. During that time the director typed a work-granting instruction into the seat. It was **queued, not delivered** — the interface showed "Press up to edit queued messages" while the hook kept running. The seat did not act on it. Recovery required the director pressing Escape to interrupt the hook, at which point the queued instruction was released and work began.

## Why this matters

1. **A mechanism built to make waking possible made waking impossible.** The rest-heartbeat exists so a rested loop can be woken by a staged doc. In this instance it prevented the most direct wake path there is — the director typing into the seat. That is a worse failure than the one it was built to fix, because the fallback channel is the one it broke.
2. **27 minutes exceeds the design bound.** The heartbeat was specified as a bounded in-hook poll *below* the 600s hook timeout. Sustained 27-minute occupancy is either the bound not holding, repeated re-arming with no yield between beats, or no interrupt point for pending input. Determine which, with evidence.
3. **It is direct evidence for your own architectural view.** `CONTINUITY_ARCHITECTURE_VIEW_2026-07-19.md` argues the persistent stop-hook-rearm seat works against the grain of the tool. This is a concrete instance: a seat that must poll to stay alive holds the seat hostage between turns. Cite this incident in that document — it moves the view from reasoning to evidence.

## Requirements (mechanism yours)

- **The heartbeat must never block director input.** Pending input must interrupt or pre-empt the beat promptly — a rested seat must remain immediately steerable by the human at all times. Treat this as a hard property, not a tuning preference.
- **Honour the stated bound**, and make a breach observable rather than silent: a beat that overruns should be loud, since a silent overrun is indistinguishable from a healthy rest from outside.
- **R15:** prove the property — input delivered during an active beat is acted on promptly, not queued indefinitely.
- **Consider whether this changes the recommendation.** If input-blocking is intrinsic to in-hook polling rather than a bug in this implementation, say so plainly: it strengthens the case for scheduled bounded invocations and against a fifth patch to the persistent seat.

**Risk & proportionality:** touches the Stop-hook path (blast radius: the whole continuity mechanism, which is currently load-bearing and only just proven). Do not destabilise the working wake path while fixing the blocking behaviour — sequence it, own commit, prove both properties (wakes on staged doc AND never blocks input) before landing. Tag: **contract-touching — implement with named mitigations.**

— Advisor, recording the director's observation, 2026-07-19.
