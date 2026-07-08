# TURN_CONTINUATION_AND_PHASE3_GO — close the last harness gap, then build (P1)

**Staged:** 2026-07-08 ~18:00 BST by advisor. **Tier:** 2 — proceed now.
This stage exists partly to BE the doorbell: an urgent from_rich instruction
(Phase 3 go + staging housekeeping) is sitting in your queue with no wake class.
Process it first.

## The gap (director-repeat x3 today = P1 by rule)
Turns end; nothing grants the next one. The runner's retirement removed idle-turn
coverage; the wake covers only new staged files; from_rich is excluded entirely.
Result: three stalls today — Phase 3 "started" then sat; urgent director
instruction queued deaf; hardening waited on coincidence. The director's operating
contract is: he steers via advisor and NTFY, nothing requires console paste, and
work CONTINUES between steers.

## Deliverable 1 (before Phase 3 code): minimal turn-continuation
Design constraints (hard):
- Same session only; no second worker; no claude -p spawning; single-writer holds.
- Event/state-driven, not periodic polling for its own sake.
- All injected text HMAC-signed; zero content authority (R7) — a nudge says only
  "open agenda / queued item exists, read state from disk".
Suggested shape (yours to refine — you know the harness best):
a) **Open-agenda continuation:** maintain a small on-disk agenda marker (current
   phase, open items). Watchdog/watcher, on its existing cycle, if agenda has open
   items AND session idle → inject one signed continue-nudge. Agenda cleared =
   silence. No open work = no turns = no burn.
b) **Urgent from_rich promotion:** dispatcher already classifies urgency. URGENT
   verdict → signed wake (read the queued file from disk). Routine from_rich stays
   queued for the next natural turn — loop-prevention preserved.
Test both live (isolation guard: injection refuses any session name not matching
the env-configured target — this also closes today's test-residue hole). One NTFY
when live.

## Deliverable 2: execute the queued instruction
Phase 3 of CORE_FIDELITY_PHASES.md — unhappy-path physics, meter reads first —
plus the housekeeping already queued (archive the 3 never-archived staging docs;
advisor verified their only commit is the original 4-5 Jul stage).

## Then: continuous build under the standing rules
Bounded-silence NTFYs; 0b observable evidence on surfaces per scope item; steers
may arrive by NTFY or staging mid-phase — absorb without stopping unless a P1
redirect says stop. The director's success test for this week: meter reads that
fail, bills that run late, visible on the portal — fidelity delta, not activity.
