# PULL, NOT PUSH — staging was never broken; the doorbell was (P0, director-decided)

**Staged:** 2026-07-15 by advisor. **Director's question, verbatim:** *"Isn't the
point of staging to give instruction? Why can't we just use staging?"* He is
right, and this re-scopes the transport fix accordingly. Disposition: INTERRUPT
(the transport is the live defect class).

## The decomposition the question exposes
- **Instruction channel = staging.** Track record: 100%. Every staged doc landed,
  was read, was actioned. Nothing here changes.
- **Attention channel = keystroke injection.** Track record: five deaths. This is
  the ONLY broken link, and it is banned.
We were about to rebuild both when only one is broken.

## The fix: the session PULLS work at every turn boundary (verify against
## current official docs before building — Finding 1 applies)
Claude Code's **Stop hook** runs inside the session's own lifecycle when a turn
ends, with a machine-checkable protocol for continuing the session with new
input (the documented block-stop/continue mechanism; the community "self-
continuing loop" pattern is built on exactly this). Therefore:
- **Turn ends -> Stop hook calls the EXISTING supervisor draw (find_work /
  Rule-0 non-empty draw) -> feeds the drawn work back as the next input.** The
  session never idles while atoms exist, and NOTHING EVER TYPES INTO THE PANE.
- The draw logic already exists and is tested. This is GLUE, not a new system:
  wire draw -> Stop hook, delete the injection path.
- Staged docs, from_rich files, twin answers: all become items the draw serves
  at the next boundary. Staging remains the single instruction channel.

## What must hold (requirements, not mechanisms)
1. **No robotic pane writes, ever again.** The interactive pane is the
   director's console ONLY. Enforce structurally (the existing grep-guard on raw
   send-keys extends to ALL writers, including the watchdog and any dispatcher).
2. **Steering binds at turn boundaries** (already decided). INTERRUPT-class
   items are served first at the next boundary; encourage shorter turns /
   checkpoint commits so boundaries come often.
3. **Watchdog becomes process-level only:** it may RESTART a dead session
   (spawn/respawn is a process operation, not a keystroke); it may never type
   into a live one. /usage polling stays eliminated.
4. **Deadman + H15 + health checks unchanged** — they key on external clocks
   (commits) and remain the tripwires over the top.
5. **Context hygiene:** one long session accumulates context; state-on-disk is
   the real memory (proven by every /clear). Define the compaction/clear cadence
   inside the loop so it never depends on a human noticing 700k tokens.
6. **PIN-authenticated ntfy remains the only machine-ingested human channel**
   (per SECURITY ADDENDUM); it feeds staging; the loop serves it.

## H17 re-scope (do not discard — re-aim)
The pull-loop is the MAIN transport. H17's headless-turn foundation
(mutation-proven last night) is re-scoped to what genuinely needs
process-per-turn semantics: **parallel fan-out beyond subagent limits and the
Epoch-4 tournament substrate** (many short lives, structured returns, separate
metering pool). One foundation, right-sized target. Reconcile the 12 primitives
and the build plan against this split; report what changes.

## Sequencing
1. Build + prove the pull loop (test: with N atoms below target and an idle
   session, three consecutive turn boundaries each draw and execute work with
   zero pane writes — instrumented, not asserted).
2. Migrate: injection path deleted, grep-guard extended, watchdog demoted to
   process-level.
3. Then resume the morning triage order (echo-loop quarantine, publish-gate
   regression, archive-on-answer) ON the new transport — its first real workload.

## The casebook line (record it)
The director's naive question — "why can't we just use staging?" — collapsed a
full orchestrator rebuild into a wiring change, by noticing that the channel
with a perfect record and the channel with five deaths had been treated as one
thing. Vantage, not capability. Again.
