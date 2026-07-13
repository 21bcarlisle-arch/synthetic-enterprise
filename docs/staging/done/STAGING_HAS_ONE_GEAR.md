# STAGING HAS ONE GEAR — fix it (P0, and then the advisor goes quiet)

**Staged:** 2026-07-13 by advisor. **Director-raised:** *"Am I constantly
distracting it? Do we need to more clearly state things into epochs or the
queue?"* Yes, and yes. The evidence and the fix:

## The evidence
- Atoms below target: **31 -> 24 overnight, with ZERO staged docs and zero
  director input.** The machine drew and closed its own work.
- **24 -> 24 this morning, while the advisor staged four docs.** The backlog
  stops moving when we feed it.
- Shape of the interference: ~20 advisor-staged docs in 48 hours, almost ALL
  harness/governance/method — the FACTORY. The actual company work (affordability
  physics, the bill/ledger disconnect, three clocks, M2 rails) came mostly from
  the machine's OWN draw or the director's domain instincts. We have been tuning
  the factory while the product advanced when we weren't looking.

## The structural flaw
**The staging channel has exactly one priority: NOW.** CLAUDE.md treats staging
as pre-approval, action-immediately, don't-wait. So EVERY staged doc preempts
the map by construction — whether or not it is urgent. There is no way to say
"important, not urgent, put it in the queue." Result: P0 inflation (six P0s in a
day) and a machine that never gets to run its own plan.

## The fix — staged docs get a DISPOSITION, and the default is QUEUE
Every staged doc must declare one of:
- **`QUEUE` (DEFAULT):** register as one or more atoms on the maturity map —
  lane, epoch, dial, file_scope, level definitions — and then **let the normal
  dial-weighted draw pick it up in its own priority order.** Do NOT preempt
  current work. If a staged doc arrives without a disposition, treat it as QUEUE.
- **`EPOCH-DEFER`:** register against a future epoch; not workable now (thinking
  work still allowed per EPOCH_GATING).
- **`INTERRUPT`:** act now, preempt. **Rare and must be justified in one line.**
  Legitimate only for: a live defect harming published output, a safety/security
  issue, a one-way door needing the director, or something blocking the whole
  machine (e.g. the draw being broken).

**The agent is explicitly authorised — required, in fact — to say "queued, not
urgent; I will draw it per the dial" and continue its current work.** Deferring
a QUEUE doc is correct behaviour, not disobedience. Advisor docs are INPUTS TO
THE MAP, not commands to the attention.

## Consequences
1. Update CLAUDE.md's staging protocol: staging = pre-approved CONTENT, not
   pre-approved URGENCY. Disposition governs when.
2. The director re-ranks dials at boundaries; that is how priority is expressed
   — not by whoever staged most recently.
3. **The advisor commits to batch-not-stream** (its own standing rule, violated
   all weekend): ideas get held and staged as ONE batch per boundary/digest,
   unless genuinely INTERRUPT-class.
4. Retro-classify what is currently in flight: anything not meeting the
   INTERRUPT bar becomes QUEUE and goes on the map, to be drawn in dial order.

## DoD
Disposition field honoured in the staging protocol + CLAUDE.md; QUEUE is the
default; the agent demonstrably defers a QUEUE doc while finishing map work and
says so in a digest; P0 count stops inflating. Then: **draw down the 24. The map
is the plan; the advisor is not the plan.**
