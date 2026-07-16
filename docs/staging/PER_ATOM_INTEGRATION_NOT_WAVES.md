# STREAM, DON'T BATCH — per-atom integration, no wave boundaries (P1, director-decided)

**Staged:** 2026-07-16 by advisor, **director-decided**. Disposition: QUEUE-high
(pure velocity multiplier; not new scope — removes a throughput bug). This is the
first concrete finding of G6_method_lens_audit (Kanban/flow), surfaced by the
director watching four verified forks idle while waiting on a fifth.

## The bug the director caught
The executor currently integrates WAVE-SYNCHRONOUSLY: draw N forks -> wait for
ALL N to finish -> fold inboxes -> ONE integration suite -> ONE merge. Observed
live: SITE1, C13, W1_9 finished in 3-5 min and sat IDLE while A8 (loop-speed
build) ran long. **The whole wave moves at the speed of its slowest / most
problematic fork.** That is a batch boundary, and batch boundaries are the
classic flow killer — exactly what Kanban/flow discipline (G6) exists to remove.
We want a machine that STREAMS, not one that PULSES.

## The fix: integrate at the smallest independently-verifiable unit (usually one atom)
- Each fork, on completion, **rebases -> runs its own gate -> merges
  independently** the moment IT is green — not when its slowest sibling is green.
- A slow or failing fork **blocks ONLY ITSELF**. The others have already landed
  and the draw has already pulled the next work. A stuck fork escalates (per the
  door rule: proceed-and-log if reversible, escalate only at a true wall) without
  freezing everything behind it.
- **This is why F1 mattered and why it comes first.** Atomic in-commit map-write
  (F1, just landed) is precisely what makes INDEPENDENT merges safe — without it,
  concurrent level-writes race and corrupt the map; with it, per-atom integration
  is safe. The enabler prioritised this morning unlocks the flow asked for now —
  same insight, arriving twice.
- The external-truth gate (verifier + suite + write-landed) runs on **every
  individual merge**, not once per wave. Verification per atom, not per batch.

## The guardrail (do not over-rotate into "always maximally parallel")
Per-atom integration is right for INDEPENDENT atoms. **Genuinely coupled changes
still land together** — the discipline is "integrate at the smallest unit that is
independently verifiable," which is USUALLY one atom and OCCASIONALLY a coupled
pair. The judgment is *how small is safely independent*, not *maximise forks*.
The area-interfaces (ARCH1) make more things independent over time, so the
coupled exceptions shrink — but they are real and must be respected now.

And the standing concurrency guardrail holds: **maximise parallelism THAT STAYS
VERIFIED.** Throughput is bounded by verification, not by fork count — the
constraint to watch as it widens is verification throughput, never raw lanes.
Do NOT drop a gate to go wider.

## Consequence for the loop
Combined with F1 + the self-continuing headless loop, the steady state becomes:
draw continuously -> each atom integrates the instant it is individually verified
-> slow/failing forks block only themselves -> external-truth gate on every merge.
No wave boundaries. Never moving at the speed of the slowest. This is genuine
flow, and it compounds — every future wave stops waiting on its slowest member.

## DoD
Executor integration step changed from wave-synchronous to **per-atom
rebase-gate-merge**; a slow/failing fork blocks only itself and escalates per the
door rule without freezing siblings; the external-truth gate runs on every
individual merge; the "smallest independently-verifiable unit" rule recorded
(coupled changes may still land together); folded into G6 as its first adopted
flow pattern. A check: with N forks where one runs long, the N-1 completed forks
must LAND without waiting on the slow one.
